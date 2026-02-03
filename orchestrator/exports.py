import csv
import io
from dataclasses import dataclass
from typing import Iterable, List, Optional

from helpers import format_duration

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
