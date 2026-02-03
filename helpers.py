import re
from urllib.parse import urlparse

SPOTIFY_ID_PATTERN = re.compile(r"[A-Za-z0-9]+")


def extract_playlist_id(value):
    """
    Extracts the Spotify playlist ID from supported inputs.

    Supported formats:
    - https://open.spotify.com/playlist/{playlist_id}
    - https://open.spotify.com/user/{user_id}/playlist/{playlist_id}
    - spotify:playlist:{playlist_id}
    """
    if not value:
        return None

    cleaned_value = value.strip()
    if not cleaned_value:
        return None

    spotify_uri_match = re.search(r"spotify:playlist:([A-Za-z0-9]+)", cleaned_value)
    if spotify_uri_match:
        return spotify_uri_match.group(1)

    parsed = urlparse(cleaned_value)
    if parsed.netloc != "open.spotify.com" and not parsed.netloc.endswith(".spotify.com"):
        return None

    path_parts = [part for part in parsed.path.split("/") if part]
    if "playlist" not in path_parts:
        return None

    playlist_index = path_parts.index("playlist") + 1
    if playlist_index >= len(path_parts):
        return None

    playlist_id = path_parts[playlist_index]
    return playlist_id if SPOTIFY_ID_PATTERN.fullmatch(playlist_id) else None


def sanitize_filename(name):
    """Sanitizes a string to be a valid filename."""
    name = name.strip()
    # Remove invalid characters that are common across OSes
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace spaces with underscores for better compatibility
    name = name.replace(' ', '_')
    # Limit length to avoid filesystem errors
    name = name[:150]
    # If the name ends up empty after sanitization, provide a default
    if not name:
        return "playlist.csv"
    if not name.lower().endswith(".csv"):
        return f"{name}.csv"
    return name


def format_duration(duration_ms):
    """Convert milliseconds into a human-friendly timecode."""
    if duration_ms is None:
        return ""
    total_seconds = max(int(duration_ms / 1000), 0)
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"
