import pytest
from helpers import extract_playlist_id, format_duration, sanitize_filename

# Tests for extract_playlist_id
@pytest.mark.parametrize("url, expected_id", [
    ("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M", "37i9dQZF1DXcBWIGoYBM5M"),
    ("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M", "37i9dQZF1DXcBWIGoYBM5M"),
    ("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=some_share_id", "37i9dQZF1DXcBWIGoYBM5M"),
    ("https://open.spotify.com/user/spotify/playlist/37i9dQZF1DXcBWIGoYBM5M", "37i9dQZF1DXcBWIGoYBM5M"),
    ("https://google.com", None),
    ("", None),
    ("just a string", None),
])
def test_extract_playlist_id(url, expected_id):
    """Test that playlist IDs are extracted correctly from various URL formats."""
    assert extract_playlist_id(url) == expected_id

# Tests for sanitize_filename
@pytest.mark.parametrize("name, expected_filename", [
    ("My Awesome Playlist", "My_Awesome_Playlist.csv"),
    ("  leading/trailing spaces  ", "leadingtrailing_spaces.csv"),
    ("Playlist with /\\:*?\"<>| chars", "Playlist_with__chars.csv"),
    ("a" * 200, ("a" * 150) + ".csv"),
    ("", "playlist.csv"),
    ("<>:\"/\\|?*", "playlist.csv"), # all invalid chars
    ("  ", "playlist.csv"), # only spaces
    ("Already.csv", "Already.csv"),
])
def test_sanitize_filename(name, expected_filename):
    """Test that filenames are sanitized correctly."""
    assert sanitize_filename(name) == expected_filename


@pytest.mark.parametrize("duration_ms, expected", [
    (180000, "3:00"),
    (240000, "4:00"),
    (3601000, "1:00:01"),
    (0, "0:00"),
    (None, ""),
])
def test_format_duration(duration_ms, expected):
    """Test duration formatting to human-readable timecodes."""
    assert format_duration(duration_ms) == expected
