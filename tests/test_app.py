import re

import pytest

from app import create_app
from orchestrator.exports import TrackRow

@pytest.fixture
def app(monkeypatch):
    """Create and configure a new app instance for each test."""
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("FLASK_SECRET_KEY", "test_secret_key")
    # Setup a test config
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key", # a fake secret key for tests
        "WTF_CSRF_ENABLED": False # Disable CSRF for form testing
    })
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_index_get(client):
    """Test that the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Glowhaven Media Orchestrator" in response.data
    assert b'tabindex="0"' in response.data
    assert b'role="region"' in response.data
    assert b'aria-labelledby="csvPreviewHeading"' in response.data
    assert b'role="status"' in response.data
    assert b'aria-label="Export in progress"' in response.data

def csrf_token(client):
    response = client.get('/')
    match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
    assert match
    return match.group(1).decode()


def test_post_valid_playlist(client, mocker):
    """Test exporting a valid playlist URL."""
    plugin = client.application.config["PLUGIN_REGISTRY"].get("spotify")
    mocker.patch.object(
        plugin,
        "export_playlist",
        return_value=(
            "Test Playlist",
            [
                TrackRow(
                    track_number=1,
                    name="Song 1",
                    artists="Artist A",
                    album="Album X",
                    duration_ms=180000,
                    duration="3:00",
                    added_at="",
                ),
                TrackRow(
                    track_number=2,
                    name="Song 2",
                    artists="Artist B",
                    album="Album Y",
                    duration_ms=240000,
                    duration="4:00",
                    added_at="",
                ),
            ],
        ),
    )

    response = client.post(
        '/',
        data={
            'playlist_url': 'https://open.spotify.com/playlist/validid123',
            'service_key': 'spotify',
            'csrf_token': csrf_token(client),
        },
    )

    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert response.headers['Content-Disposition'] == 'attachment; filename=Test_Playlist.csv'

    csv_data = response.data.decode('utf-8')
    assert "Track #,Name,Artists,Album,Duration (ms),Duration,Added At" in csv_data
    assert "1,Song 1,Artist A,Album X,180000,3:00," in csv_data
    assert "2,Song 2,Artist B,Album Y,240000,4:00," in csv_data

def test_post_invalid_playlist_url(client):
    """Test submitting an invalid Spotify URL."""
    response = client.post(
        '/',
        data={'playlist_url': 'https://not-spotify.com/playlist/invalid', 'service_key': 'spotify', 'csrf_token': csrf_token(client)},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'Invalid playlist URL.' in response.data

def test_post_spotify_api_error(client, mocker):
    """Test handling of Spotify API errors."""
    plugin = client.application.config["PLUGIN_REGISTRY"].get("spotify")
    from spotipy.exceptions import SpotifyException
    mocker.patch.object(plugin, "export_playlist", side_effect=SpotifyException(404, -1, "Not found"))

    response = client.post(
        '/',
        data={'playlist_url': 'https://open.spotify.com/playlist/notfoundid', 'service_key': 'spotify', 'csrf_token': csrf_token(client)},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'An error occurred with the Spotify API.' in response.data


def test_post_without_csrf_is_rejected(client):
    response = client.post(
        '/',
        data={'playlist_url': 'https://open.spotify.com/playlist/validid123', 'service_key': 'spotify'},
    )
    assert response.status_code == 403


def test_security_headers(client):
    response = client.get('/')
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'DENY'
    assert response.headers['Referrer-Policy'] == 'strict-origin-when-cross-origin'
    assert "frame-ancestors 'none'" in response.headers['Content-Security-Policy']


def test_csv_formula_injection_is_neutralized():
    from orchestrator.exports import TrackRow, generate_csv
    row = TrackRow(1, "=SUM(A1:A2)", "+evil", "@cmd", 1000, "0:01", "-danger")
    csv_data = generate_csv([row]).getvalue().decode("utf-8")
    assert "'=SUM(A1:A2)" in csv_data
    assert "'+evil" in csv_data
    assert "'@cmd" in csv_data
    assert "'-danger" in csv_data
