from orchestrator.exports import build_track_rows
from orchestrator.plugins import PluginRegistry, ServiceStatus, SpotifyServicePlugin


class DummyServicePlugin:
    key = "youtube"
    name = "YouTube"
    description = "Test service for integration coverage."

    def is_available(self):
        return True, "Ready"

    def export_playlist(self, playlist_id):
        return "Playlist", []


def test_plugin_registry_multi_service_status():
    registry = PluginRegistry()
    registry.register(SpotifyServicePlugin("id", "secret"))
    registry.register(DummyServicePlugin())

    statuses = registry.list_status()
    status_keys = {status.key for status in statuses}
    assert status_keys == {"spotify", "youtube"}
    assert all(isinstance(status, ServiceStatus) for status in statuses)


def test_build_track_rows_stress():
    items = []
    for index in range(5000):
        items.append(
            {
                "track": {
                    "name": f"Song {index}",
                    "artists": [{"name": "Artist"}],
                    "album": {"name": "Album"},
                    "duration_ms": 180000,
                },
                "added_at": "2024-01-01T00:00:00Z",
            }
        )

    rows = build_track_rows(items)
    assert len(rows) == 5000
    assert rows[0].track_number == 1
    assert rows[-1].track_number == 5000
