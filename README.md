# Glowhaven Media Orchestrator

> **Turn media platforms into one clean, local-first export workflow.**

[![CI](https://github.com/GlowhavenIndustries/Glowhaven-Media-Orchestrator/actions/workflows/ci.yml/badge.svg)](https://github.com/GlowhavenIndustries/Glowhaven-Media-Orchestrator/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-111827.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-web%20app-000000.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

Glowhaven Media Orchestrator is a self-hosted Flask application for exporting playlist metadata from connected media services into clean, analytics-ready files.

The project currently ships with a **Spotify connector** and a plugin architecture for adding additional services.

**Credentials stay on the server or local machine. Playlist data is fetched on demand and the application does not maintain a playlist database.**

---

## ✨ What it does

Give Glowhaven a playlist URL and it handles the repetitive work:

1. Validates the submitted Spotify URL.
2. Connects to Spotify using server-side credentials.
3. Follows Spotify pagination for large playlists.
4. Normalizes track metadata into a consistent schema.
5. Generates a CSV export in memory.
6. Returns the file directly to the user.

### Current export fields

| Field | Description |
| --- | --- |
| Track # | Export order |
| Name | Track name |
| Artists | Artist names |
| Album | Album title |
| Duration (ms) | Original duration value |
| Duration | Human-readable duration |
| Added At | Playlist timestamp when available |

---

## 🔌 Plugin architecture

Media sources are isolated behind a small plugin contract.

~~~text
                    Glowhaven Orchestrator
                             |
                    +--------+--------+
                    | Plugin Registry |
                    +--------+--------+
                             |
                 +-----------+-----------+
                 |                       |
                 v                       v
        SpotifyServicePlugin       Future plugins
                 |
                 v
          Spotify Web API
~~~

Adding a service does not require rewriting the export pipeline. A plugin provides availability information and an export operation, while the shared export layer handles normalization and CSV generation.

### Current status

| Connector | Status |
| --- | --- |
| Spotify | Available |
| YouTube | Architecture ready, connector not shipped |
| Apple Music | Architecture ready, connector not shipped |
| JSON export | Not currently shipped |
| Data warehouse export | Not currently shipped |
| Scheduled exports | Not currently shipped |

That distinction is intentional. The README describes what is actually in the repository today.

---

## 🔐 Security

Glowhaven is designed for local and self-hosted use, with security controls implemented in the application rather than relying only on deployment conventions.

### Credentials

- Spotify credentials are read from environment variables or an optional local Glowhaven Core configuration file.
- Credentials are not sent to the browser.
- .env files are ignored by Git.
- Production requires an explicit Flask secret key.

### Request protection

- CSRF tokens protect export POST requests.
- Requests are rate limited in memory.
- Form payloads have strict size and part limits.
- Spotify playlist URLs must use HTTPS and the canonical open.spotify.com hostname.
- Playlist URL length is bounded.

### Browser protections

Responses include:

- Content Security Policy
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Strict referrer policy
- Permissions Policy
- HSTS when running in production

### Export safety

CSV text fields are protected against spreadsheet formula injection by neutralizing formula-prefixed values before they are written to exports.

### Container safety

The Docker image:

- Runs as a non-root user.
- Includes a health check.
- Excludes Git metadata, environments, caches, and local secrets through .dockerignore.

### Dependency security

GitHub Actions runs pip-audit against the repository dependency set on pushes and pull requests.

Security reports and fixes are welcome through GitHub Issues and pull requests.

---

## 🚀 Quick start

### Windows

Install Python 3.10 or newer, then run:

~~~bat
start.bat
~~~

The launcher creates a virtual environment, installs dependencies, creates .env when needed, and starts the application.

Open:

~~~text
http://127.0.0.1:5000
~~~

### macOS, Linux, or manual Windows setup

~~~bash
git clone https://github.com/GlowhavenIndustries/Glowhaven-Media-Orchestrator.git
cd Glowhaven-Media-Orchestrator
python -m venv venv
~~~

Activate the environment:

~~~bash
# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
~~~

Install dependencies:

~~~bash
pip install -r requirements.txt
~~~

Start the application:

~~~bash
python app.py
~~~

Then open http://127.0.0.1:5000.

---

## 🎵 Spotify configuration

Create a Spotify application and provide its credentials through environment variables.

~~~ini
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
FLASK_SECRET_KEY=replace_with_a_long_random_secret
~~~

Optional Glowhaven Core configuration:

~~~ini
GLOWHAVEN_CORE_CONFIG=/path/to/glowhaven-core.json
~~~

The Core configuration file can provide the same application secrets when your deployment already has a centralized secret workflow.

### Production

Set a strong secret before starting the application:

~~~bash
export FLASK_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
~~~

For a production deployment behind a reverse proxy, bind the application explicitly:

~~~bash
export ORCHESTRATOR_BIND_HOST=127.0.0.1
export PORT=5000
~~~

Terminate TLS at your reverse proxy and keep the Flask application off the public internet.

---

## 🐳 Docker

Build and run:

~~~bash
docker compose up -d --build
~~~

The included Compose configuration uses production Flask settings and binds the container listener correctly for port publishing.

For a serious deployment, put HTTPS in front of the container and provide secrets through your deployment platform rather than committing them to files.

---

## 🧪 Development

Install dependencies:

~~~bash
pip install -r requirements.txt
~~~

Run tests:

~~~bash
pytest -q
~~~

The test suite covers:

- Playlist URL validation
- Filename sanitization
- Duration formatting
- CSV generation
- Flask page rendering
- Successful export flow
- Spotify API error handling
- CSRF enforcement
- Security response headers

### CI

Every push to main and every pull request runs:

~~~text
pytest
pip-audit
~~~

This gives contributors a fast signal for both regressions and known dependency vulnerabilities.

---

## 🗂️ Project structure

~~~text
.
├── app.py
├── helpers.py
├── orchestrator/
│   ├── config.py
│   ├── exports.py
│   └── plugins.py
├── templates/
│   └── index.html
├── static/
│   ├── app.js
│   ├── styles.css
│   └── glowhaven-emblem.svg
├── tests/
│   ├── test_app.py
│   └── test_helpers.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── start.bat
├── .env.example
├── .dockerignore
└── .github/
    └── workflows/
        └── ci.yml
~~~

---

## 🧠 Design principles

### Local first

Your media credentials and exported data should stay within infrastructure you control.

### Small core

The application keeps the orchestration layer compact so new connectors can be added without introducing a large framework.

### Explicit capabilities

The UI and README distinguish shipped functionality from planned integrations.

### Secure defaults

Input validation, CSRF protection, browser security headers, bounded requests, safe CSV generation, and dependency auditing are part of the application workflow.

### Extensible connectors

Services should be isolated behind the plugin interface rather than coupled to the UI.

---

## 🤝 Contributing

Pull requests are welcome.

A good connector contribution should:

1. Implement the existing plugin contract.
2. Keep credentials server-side.
3. Include tests for normal and failure paths.
4. Avoid adding unnecessary dependencies.
5. Preserve the shared export schema where possible.
6. Pass the full CI suite.

For security-sensitive issues, avoid publishing credentials or private data in a public issue.

---

## 🗺️ Roadmap

Potential future work includes:

- Additional media connectors
- JSON exports
- Data warehouse destinations
- Scheduled exports
- Larger service-specific test suites
- Optional integration with Glowhaven Dashboard
- More granular connector permissions
- Expanded operational telemetry

Roadmap items are proposals, not current product capabilities.

---

## 📄 License

Glowhaven Media Orchestrator is released under the **MIT License**.

See [LICENSE](LICENSE) for the complete license text.

---

## Glowhaven

**Building the future, on our terms.**

Glowhaven Media Orchestrator is one piece of the broader Glowhaven ecosystem: focused, self-hosted software designed to connect real systems without hiding the important parts behind unnecessary complexity.

⭐ If this project is useful to you, consider starring the repository and sharing what you build with it.