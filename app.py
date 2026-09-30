import logging
import os
import secrets
import time
from collections import defaultdict

from flask import Flask, abort, flash, redirect, render_template, request, send_file, session, url_for
from spotipy.exceptions import SpotifyException

from helpers import extract_playlist_id, sanitize_filename
from orchestrator.config import OrchestratorConfig
from orchestrator.exports import CSV_FIELDS, generate_csv
from orchestrator.plugins import PluginRegistry, SpotifyServicePlugin

logger = logging.getLogger(__name__)

MAX_PLAYLIST_URL_LENGTH = 2048
RATE_WINDOW_SECONDS = 600
RATE_LIMIT = 20
_rate_limits = defaultdict(list)

def _client_key():
    return request.remote_addr or "unknown"

def _allow_request():
    now = time.monotonic()
    key = _client_key()
    recent = [stamp for stamp in _rate_limits[key] if now - stamp < RATE_WINDOW_SECONDS]
    _rate_limits[key] = recent
    if len(recent) >= RATE_LIMIT:
        return False
    recent.append(now)
    return True

def _csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token

def _validate_request():
    if not _allow_request():
        abort(429)
    token = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    if not token or not expected or not secrets.compare_digest(token, expected):
        abort(403)
    if len(request.form.get("playlist_url", "").strip()) > MAX_PLAYLIST_URL_LENGTH:
        abort(413)


def build_plugin_registry(config: OrchestratorConfig) -> PluginRegistry:
    registry = PluginRegistry()
    registry.register(SpotifyServicePlugin(config.spotify_client_id, config.spotify_client_secret))
    return registry


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_path=os.path.abspath(os.path.dirname(__file__)))

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    config = OrchestratorConfig.from_env()
    app.secret_key = config.flask_secret_key or secrets.token_hex(32)
    if not config.flask_secret_key and config.is_production:
        raise RuntimeError("Production error: FLASK_SECRET_KEY environment variable is required.")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    registry = build_plugin_registry(config)
    app.config["PLUGIN_REGISTRY"] = registry
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
    app.config["MAX_FORM_MEMORY_SIZE"] = 16 * 1024
    app.config["MAX_FORM_PARTS"] = 32

    @app.after_request
    def apply_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("Content-Security-Policy", "default-src 'self'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'; script-src 'self'; style-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'")
        if config.is_production:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            _validate_request()
            service_key = request.form.get("service_key", "spotify")
            playlist_url = request.form.get("playlist_url", "").strip()
            if not playlist_url:
                flash("Please enter a playlist URL.", "danger")
                return redirect(url_for('index'))

            plugin = app.config["PLUGIN_REGISTRY"].get(service_key)
            if not plugin:
                flash("Selected media service is not registered.", "danger")
                return redirect(url_for("index"))

            is_available, detail = plugin.is_available()
            if not is_available:
                flash(detail, "danger")
                return redirect(url_for("index"))

            playlist_id = extract_playlist_id(playlist_url)
            if not playlist_id:
                flash("Invalid playlist URL.", "danger")
                return redirect(url_for('index'))

            try:
                playlist_name, track_rows = plugin.export_playlist(playlist_id)
                download_filename = sanitize_filename(playlist_name)
                csv_file = generate_csv(track_rows)

                return send_file(
                    csv_file,
                    mimetype="text/csv",
                    as_attachment=True,
                    download_name=download_filename,
                )
            except SpotifyException as error:
                logger.error("Spotify API error: %s", error)
                flash("An error occurred with the Spotify API. The playlist might be private or invalid.", "danger")
                return redirect(url_for("index"))
            except Exception as error:
                logger.error("Error processing playlist: %s", error)
                flash("An unexpected error occurred.", "danger")
                return redirect(url_for("index"))

        services = app.config["PLUGIN_REGISTRY"].list_status()
        return render_template("index.html", csv_fields=CSV_FIELDS, services=services)

    return app

if __name__ == '__main__':
    app = create_app()
    print("Server started. Go to http://localhost:5000/ in your browser.")
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
