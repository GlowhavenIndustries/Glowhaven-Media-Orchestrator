# Glowhaven Media Orchestrator

**Glowhaven Media Orchestrator — Structuring global media ecosystems, flawlessly.**

Glowhaven Media Orchestrator transforms a single-service exporter into an enterprise-ready platform for multi-service media
orchestration. It delivers analytics-ready exports, plugin-driven integrations, and modular deployment patterns that scale
from a single workstation to global media operations.

## Why Glowhaven teams ship with it

- **Multi-service orchestration:** Spotify today, with clear hooks for YouTube, Apple Music, and future connectors.
- **Analytics-ready exports:** CSV output now, with JSON/warehouse-ready extensions planned.
- **Operational resilience:** Pagination-first ingestion, clear error handling, and audit-friendly exports.
- **Security-first posture:** Credentials stay local; optional Glowhaven Core secrets integration for production.
- **Enterprise UX:** OLED-dark, glowing interface with Glowhaven branding and clear orchestration flows.

## Core capabilities

- Multi-service playlist aggregation and export
- Analytics-ready outputs (CSV today, JSON/DB next)
- Scheduled export readiness (Glowhaven Core scheduler hooks)
- Optional Glowhaven Dashboard integration for real-time monitoring
- Plugin architecture for new media sources

## Quick start

### Docker (dev)

```bash
docker-compose up -d
```

### Docker (Windows, one command)

Run this in PowerShell or Command Prompt after installing Docker Desktop (it also installs the app by cloning the repo):

```powershell
git clone https://github.com/GlowhavenIndustries/Glowhaven-Media-Orchestrator.git; cd spotify-playlist-exporter; docker compose up -d --build
```

### Python (dev)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`.

## Configuration

Environment variables are optional for local development. In production, secrets should be provided via environment
variables or a Glowhaven Core config JSON file.

```ini
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
FLASK_SECRET_KEY=your_long_random_secret
GLOWHAVEN_CORE_CONFIG=/path/to/glowhaven-core.json
```

The optional `GLOWHAVEN_CORE_CONFIG` file can include the same keys to centralize secrets in Glowhaven Core-managed
workflows.

## Plugin architecture

Media sources register as plugins so each service can ship as its own module or container. The core orchestrator handles
scheduling, API coordination, and analytics exports while plugins focus on ingestion logic.

Example plugin responsibilities:

- Spotify: Playlist ingestion + export
- YouTube: Playlist ingestion + export
- Apple Music: Playlist ingestion + export

## Orchestration-ready exports

| Column | Description |
| --- | --- |
| Track # | Track order in the playlist |
| Name | Track name |
| Artists | Comma-separated artist names |
| Album | Album title |
| Duration (ms) | Track length in milliseconds |
| Duration | Track length in `m:ss` or `h:mm:ss` |
| Added At | Timestamp when the track was added |

## Security & governance

- Credentials remain local by default.
- Optional Glowhaven Core secrets management for production teams.
- TLS termination and audit-ready logging support via standard reverse proxies.

## Testing & reliability

Run the test suite:

```bash
pytest
```

The suite includes:

- Unit tests for helpers and export formatting
- Integration tests for multi-service plugin registration
- Stress tests for large playlist exports

## Deployment

Glowhaven Media Orchestrator is deployment-ready with Docker Compose today and can be extended to Kubernetes by splitting
plugins into their own services.

## License

Licensed under the MIT License. See `LICENSE` for details.
