import json
import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OrchestratorConfig:
    environment: str
    flask_secret_key: Optional[str]
    spotify_client_id: Optional[str]
    spotify_client_secret: Optional[str]
    glowhaven_core_config_path: Optional[str]

    @classmethod
    def from_env(cls):
        environment = os.environ.get("FLASK_ENV") or os.environ.get("ENV") or "production"
        core_config_path = os.environ.get("GLOWHAVEN_CORE_CONFIG")
        core_overrides = cls._load_core_config(core_config_path)
        return cls(
            environment=environment,
            flask_secret_key=os.environ.get("FLASK_SECRET_KEY") or core_overrides.get("FLASK_SECRET_KEY"),
            spotify_client_id=os.environ.get("SPOTIFY_CLIENT_ID") or core_overrides.get("SPOTIFY_CLIENT_ID"),
            spotify_client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET")
            or core_overrides.get("SPOTIFY_CLIENT_SECRET"),
            glowhaven_core_config_path=core_config_path,
        )

    @staticmethod
    def _load_core_config(path: Optional[str]):
        if not path:
            return {}
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return {}
        if isinstance(data, dict):
            return {str(key): value for key, value in data.items()}
        return {}

    @property
    def has_spotify_credentials(self):
        return bool(self.spotify_client_id and self.spotify_client_secret)

    @property
    def is_production(self):
        return self.environment.lower() == "production"
