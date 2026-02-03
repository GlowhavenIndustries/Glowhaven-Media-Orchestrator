@echo off
ECHO INFO: Starting Glowhaven Media Orchestrator setup...

REM 1. Check for Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    ECHO ERROR: Python is not installed or not in PATH. Please install Python to continue.
    exit /b 1
)

REM 2. Set up virtual environment
IF NOT EXIST venv (
    ECHO INFO: Creating Python virtual environment in '.\venv'...
    python -m venv venv
)

REM Activate virtual environment
CALL venv\Scripts\activate.bat

REM 3. Install dependencies
ECHO INFO: Installing dependencies from requirements.txt...
pip install -r requirements.txt --quiet

REM 4. Check and set up .env file
IF NOT EXIST .env (
    ECHO INFO: No .env file found. Creating one from .env.example.
    copy .env.example .env > nul
)

REM 5. Ensure FLASK_SECRET_KEY is set
set "SECRET_KEY_EXISTS="
FOR /F "tokens=1,2 delims==" %%A IN (.env) DO (
    IF "%%A"=="FLASK_SECRET_KEY" SET "SECRET_KEY_EXISTS=%%B"
)

IF NOT DEFINED SECRET_KEY_EXISTS (
    ECHO INFO: FLASK_SECRET_KEY not found or is empty. Generating a new one...
    FOR /F "delims=" %%i IN ('powershell -Command "[guid]::NewGuid().ToString().Replace('-','')"') DO SET "SECRET_KEY=%%i"
    ECHO FLASK_SECRET_KEY=%SECRET_KEY%>>.env
)

REM 6. Validate Spotify credentials (optional for local development)
FOR /F "usebackq tokens=1,2 delims==" %%A IN (.env) DO (
    IF "%%A"=="SPOTIFY_CLIENT_ID" SET "SPOTIFY_CLIENT_ID=%%B"
    IF "%%A"=="SPOTIFY_CLIENT_SECRET" SET "SPOTIFY_CLIENT_SECRET=%%B"
)

IF "%SPOTIFY_CLIENT_ID%"=="your_spotify_client_id" (
    ECHO WARN: Spotify Client ID is not set. Exports will be unavailable until credentials are added.
)

IF "%SPOTIFY_CLIENT_SECRET%"=="your_spotify_client_secret" (
    ECHO WARN: Spotify Client Secret is not set. Exports will be unavailable until credentials are added.
)

REM 7. Run the application
ECHO INFO: Setup complete. Starting the application on http://127.0.0.1:5000
python app.py
