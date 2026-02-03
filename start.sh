#!/bin/bash

# A robust script to set up and run Glowhaven Media Orchestrator.

# --- Helper Functions ---
print_info() {
    echo "INFO: $1"
}

print_error() {
    echo "ERROR: $1" >&2
}

print_warning() {
    echo "WARN: $1"
}

# --- Main Script ---
print_info "Starting Glowhaven Media Orchestrator setup..."

# 1. Check for Python 3
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 to continue."
    exit 1
fi

# 2. Set up virtual environment
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    print_info "Creating Python virtual environment in './$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# 3. Install dependencies
print_info "Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet

# 4. Check and set up .env file
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    print_info "No .env file found. Creating one from .env.example."
    cp .env.example "$ENV_FILE"
fi

# 5. Ensure FLASK_SECRET_KEY is set
# Check if the key exists and has a non-empty value
if ! grep -q "^FLASK_SECRET_KEY=" "$ENV_FILE" || [[ -z $(grep "^FLASK_SECRET_KEY=" "$ENV_FILE" | cut -d '=' -f2-) ]]; then
    print_info "FLASK_SECRET_KEY not found or is empty. Generating a new one..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(16))")

    # Create a temporary file without the old key
    grep -v "^FLASK_SECRET_KEY=" "$ENV_FILE" > "$ENV_FILE.tmp"
    # Add the new key
    echo "FLASK_SECRET_KEY=$SECRET_KEY" >> "$ENV_FILE.tmp"
    # Replace the original file
    mv "$ENV_FILE.tmp" "$ENV_FILE"
fi

# 6. Validate Spotify credentials (optional for local development)
# Load .env file to check variables. This is a safe way to load them.
if [ -f "$ENV_FILE" ]; then
  export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

if [ -z "$SPOTIFY_CLIENT_ID" ] || [ "$SPOTIFY_CLIENT_ID" == "your_spotify_client_id" ]; then
    print_warning "Spotify Client ID is not set. Exports will be unavailable until credentials are added."
fi

if [ -z "$SPOTIFY_CLIENT_SECRET" ] || [ "$SPOTIFY_CLIENT_SECRET" == "your_spotify_client_secret" ]; then
    print_warning "Spotify Client Secret is not set. Exports will be unavailable until credentials are added."
fi

# 7. Run the application
print_info "Setup complete. Starting the application on http://127.0.0.1:5000"
python3 app.py
