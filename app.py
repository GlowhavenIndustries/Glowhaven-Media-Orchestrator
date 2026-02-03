import logging

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from spotipy.exceptions import SpotifyException

from helpers import extract_playlist_id, sanitize_filename
from orchestrator.config import OrchestratorConfig
from orchestrator.exports import CSV_FIELDS, generate_csv
from orchestrator.plugins import PluginRegistry, SpotifyServicePlugin

logger = logging.getLogger(__name__)


def build_plugin_registry(config: OrchestratorConfig) -> PluginRegistry:
    registry = PluginRegistry()
    registry.register(SpotifyServicePlugin(config.spotify_client_id, config.spotify_client_secret))
    return registry


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    config = OrchestratorConfig.from_env()
    app.secret_key = config.flask_secret_key
    if not app.secret_key and config.is_production:
        raise RuntimeError("Production error: FLASK_SECRET_KEY environment variable is required.")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    registry = build_plugin_registry(config)
    app.config["PLUGIN_REGISTRY"] = registry

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            service_key = request.form.get("service_key", "spotify")
            playlist_url = request.form.get("playlist_url", "")
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
