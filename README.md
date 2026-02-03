# Glowhaven Media Orchestrator

Export Spotify playlists into analytics-ready CSV files with a polished, enterprise-quality interface. The application is built with Flask and Spotipy, designed to be reliable, fast, and easy to operate for both casual users and data teams.

## Why teams love it

- **Premium UI/UX:** Modern glassmorphism design, responsive layout, and accessible typography.
- **Data-rich exports:** Track number, artists, album, duration (ms + timecode), and added-at timestamps.
- **Resilient API handling:** Pagination support and clear error feedback.
- **Secure by default:** Credentials stay local and are never stored in the app.
- **Tested backend:** Robust helper and integration tests.

## Use cases

- **Marketing & growth:** Track playlist performance and compare releases over time.
- **Analytics & BI:** Load playlist data into dashboards for reporting and attribution.
- **Operations:** Maintain audit-ready CSVs for licensing and content teams.
- **Creators:** Keep personal backups of playlists and track order.

## Quick start

### 1) Clone the repository

```bash
git clone https://github.com/Apex239/spotifyplaylistexporter
cd spotifyplaylistexporter
```

### 2) Configure environment variables

Copy the example file and add credentials from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/):

```bash
cp .env.example .env
```

```ini
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
FLASK_SECRET_KEY=your_long_random_secret
```

### 3) Start the app

- **macOS/Linux:**
  ```bash
  ./start.sh
  ```
- **Windows:**
  ```bash
  ./start.bat
  ```

Navigate to `http://127.0.0.1:5000`.

## CSV schema

| Column | Description |
| --- | --- |
| Track # | Track order in the playlist |
| Name | Track name |
| Artists | Comma-separated artist names |
| Album | Album title |
| Duration (ms) | Track length in milliseconds |
| Duration | Track length in `m:ss` or `h:mm:ss` |
| Added At | Timestamp when the track was added |

## Product highlights

- **Export accuracy:** Consistent column order and ISO timestamps for audit-ready analysis.
- **Performance:** Pagination-driven retrieval for large playlists without timeouts.
- **Privacy:** No data retention or credential storage by the app.
- **Compatibility:** Supports Spotify playlist URLs and URIs.

## Environment variables

| Variable | Description |
| --- | --- |
| `SPOTIFY_CLIENT_ID` | Spotify application client ID |
| `SPOTIFY_CLIENT_SECRET` | Spotify application client secret |
| `FLASK_SECRET_KEY` | Flask session signing key |

## Production readiness checklist

- [ ] Use a dedicated Spotify app for production environments.
- [ ] Rotate credentials routinely and use per-environment secrets.
- [ ] Terminate TLS in front of Flask (reverse proxy, platform, or load balancer).
- [ ] Pin dependencies and run `pytest` on every deploy.
- [ ] Monitor Spotify API rate limits and logs.

## Troubleshooting

| Issue | Resolution |
| --- | --- |
| `Invalid playlist URL` | Ensure the link matches `https://open.spotify.com/playlist/...` or a valid Spotify URI. |
| `Authentication failed` | Re-check the client ID/secret and confirm the app is enabled in Spotify Developer Dashboard. |
| `Empty CSV` | Make sure the playlist is public or the app has access to it. |
| `Timeout on large playlists` | Retry after a moment; pagination automatically resumes from the last page. |

## Project structure

```
.
├── app.py              # Flask app factory and routes
├── helpers.py          # URL parsing, formatting helpers
├── static/
│   ├── app.js          # UI interactions
│   └── styles.css      # Premium UI styling
├── templates/
│   └── index.html      # Main UI template
├── tests/
│   ├── test_app.py     # Integration tests
│   └── test_helpers.py # Helper unit tests
├── requirements.txt
├── start.bat
└── start.sh
```

## Testing

Run the full test suite with:

```bash
pytest
```

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Make changes and ensure tests pass (`pytest`).
4. Commit (`git commit -m "Add new feature"`).
5. Push and open a Pull Request.

## License

Licensed under the MIT License. See `LICENSE` for details.
