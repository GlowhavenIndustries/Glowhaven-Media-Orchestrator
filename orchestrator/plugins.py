from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Protocol, Tuple

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from orchestrator.exports import TrackRow, build_track_rows


@dataclass(frozen=True)
class ServiceStatus:
    key: str
    name: str
    description: str
    is_available: bool
    detail: str


class MediaServicePlugin(Protocol):
    key: str
    name: str
    description: str

    def is_available(self) -> Tuple[bool, str]:
        ...

    def export_playlist(self, playlist_id: str) -> Tuple[str, List[TrackRow]]:
        ...


class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, MediaServicePlugin] = {}

    def register(self, plugin: MediaServicePlugin):
        self._plugins[plugin.key] = plugin

    def get(self, key: str) -> Optional[MediaServicePlugin]:
        return self._plugins.get(key)

    def list_status(self) -> List[ServiceStatus]:
        statuses = []
        for plugin in self._plugins.values():
            available, detail = plugin.is_available()
            statuses.append(
                ServiceStatus(
                    key=plugin.key,
                    name=plugin.name,
                    description=plugin.description,
                    is_available=available,
                    detail=detail,
                )
            )
        return statuses


class SpotifyServicePlugin:
    key = "spotify"
    name = "Spotify"
    description = "Playlist ingestion and export via Spotify Web API."

    def __init__(self, client_id: Optional[str], client_secret: Optional[str]):
        self._client_id = client_id
        self._client_secret = client_secret
        self._client: Optional[spotipy.Spotify] = None

    def _get_client(self) -> spotipy.Spotify:
        if self._client:
            return self._client
        if not self._client_id or not self._client_secret:
            raise RuntimeError("Spotify credentials are missing.")
        credentials_manager = SpotifyClientCredentials(
            client_id=self._client_id,
            client_secret=self._client_secret,
        )
        self._client = spotipy.Spotify(client_credentials_manager=credentials_manager)
        return self._client

    def is_available(self) -> Tuple[bool, str]:
        if self._client_id and self._client_secret:
            return True, "Ready"
        return False, "Add SPOTIFY_CLIENT_ID + SPOTIFY_CLIENT_SECRET or Glowhaven Core config."

    def export_playlist(self, playlist_id: str) -> Tuple[str, List[TrackRow]]:
        client = self._get_client()
        playlist = client.playlist(playlist_id)
        tracks = playlist.get("tracks", {})
        track_rows: List[TrackRow] = []
        row_index = 1
        while tracks:
            items = tracks.get("items", [])
            track_rows.extend(build_track_rows(items, start_index=row_index))
            row_index = len(track_rows) + 1
            if tracks.get("next"):
                tracks = client.next(tracks)
            else:
                break
        playlist_name = playlist.get("name", "playlist")
        return playlist_name, track_rows
