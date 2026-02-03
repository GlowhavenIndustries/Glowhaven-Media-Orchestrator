import csv
import io
import logging
import os
from dataclasses import dataclass
from typing import Iterable, List, Optional

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
import spotipy
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials

from helpers import extract_playlist_id, format_duration, sanitize_filename

# This will be initialized in create_app
sp = None
logger = logging.getLogger(__name__)

CSV_FIELDS = [
    "Track #",
    "Name",
    "Artists",
    "Album",
    "Duration (ms)",
    "Duration",
    "Added At",
]


@dataclass(frozen=True)
class TrackRow:
    track_number: int
    name: str
    artists: str
    album: str
    duration_ms: Optional[int]
    duration: str
    added_at: str

    def to_dict(self):
        return {
            "Track #": self.track_number,
            "Name": self.name,
            "Artists": self.artists,
            "Album": self.album,
            "Duration (ms)": self.duration_ms if self.duration_ms is not None else "",
            "Duration": self.duration,
            "Added At": self.added_at,
        }


def build_track_rows(items: Iterable[dict], start_index: int = 1) -> List[TrackRow]:
    rows = []
    track_number = start_index
    for item in items:
        track = item.get("track") if item else None
        if not track:
            continue

        artists = ", ".join(artist["name"] for artist in track.get("artists", []) if artist.get("name"))
        album = track.get("album", {}).get("name", "")
        duration_ms = track.get("duration_ms")
        rows.append(
            TrackRow(
                track_number=track_number,
                name=track.get("name", ""),
                artists=artists,
                album=album,
                duration_ms=duration_ms,
                duration=format_duration(duration_ms),
                added_at=item.get("added_at", ""),
            )
        )
        track_number += 1
    return rows


def generate_csv(track_rows: Iterable[TrackRow]):
    """Generate a CSV file (in-memory) from the track data."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for row in track_rows:
        writer.writerow(row.to_dict())
    output.seek(0)
    return io.BytesIO(output.getvalue().encode("utf-8"))


def create_spotify_client():
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("Missing Spotify credentials. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.")
    credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=credentials_manager)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    app.secret_key = os.environ.get("FLASK_SECRET_KEY")
    environment = os.environ.get("FLASK_ENV") or app.config.get("ENV", "production")
    if not app.secret_key and environment == "production":
        raise RuntimeError("Production error: FLASK_SECRET_KEY environment variable is required.")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    global sp
    sp = create_spotify_client()

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            playlist_url = request.form.get("playlist_url", "")
            if not playlist_url:
                flash("Please enter a Spotify playlist URL.", "danger")
                return redirect(url_for('index'))

            playlist_id = extract_playlist_id(playlist_url)
            if not playlist_id:
                flash("Invalid Spotify playlist URL.", "danger")
                return redirect(url_for('index'))

            try:
                playlist = sp.playlist(playlist_id)
                tracks = playlist.get("tracks", {})
                track_rows: List[TrackRow] = []
                row_index = 1
                while tracks:
                    items = tracks.get("items", [])
                    track_rows.extend(build_track_rows(items, start_index=row_index))
                    row_index = len(track_rows) + 1
                    if tracks.get("next"):
                        tracks = sp.next(tracks)
                    else:
                        break

                playlist_name = playlist.get("name", "playlist")
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

        return render_template("index.html", csv_fields=CSV_FIELDS)

    return app

if __name__ == '__main__':
    app = create_app()
    print("Server started. Go to http://localhost:5000/ in your browser.")
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
