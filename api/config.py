import os
from configparser import ConfigParser
from functools import lru_cache
from pathlib import Path
from typing import Dict

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.ini"
ENV_PREFIX = "APP_"


def _load_from_ini() -> Dict[str, str]:
    parser = ConfigParser()
    if CONFIG_PATH.exists():
        parser.read(CONFIG_PATH, encoding="utf-8")
    if not parser.has_section("DATABASE"):
        return {}
    section = parser["DATABASE"]
    return {
        "db_name": section.get("db_name", "").strip(),
        "db_user": section.get("db_user", "").strip(),
        "db_password": section.get("db_password", "").strip(),
        "db_host": section.get("db_host", "").strip(),
        "db_port": section.get("db_port", "").strip(),
    }


@lru_cache(maxsize=1)
def get_db_settings() -> Dict[str, str]:
    """
    Load database configuration preferring environment variables, then config.ini.
    Environment variables are expected with prefix APP_, e.g. APP_DB_NAME.
    """
    ini_values = _load_from_ini()
    env_values = {
        "db_name": os.getenv(f"{ENV_PREFIX}DB_NAME") or ini_values.get("db_name"),
        "db_user": os.getenv(f"{ENV_PREFIX}DB_USER") or ini_values.get("db_user"),
        "db_password": os.getenv(f"{ENV_PREFIX}DB_PASSWORD") or ini_values.get("db_password"),
        "db_host": os.getenv(f"{ENV_PREFIX}DB_HOST") or ini_values.get("db_host"),
        "db_port": os.getenv(f"{ENV_PREFIX}DB_PORT") or ini_values.get("db_port"),
    }
    missing = [k for k, v in env_values.items() if not v]
    if missing:
        raise RuntimeError(f"Database configuration is incomplete. Missing: {', '.join(missing)}")
    return env_values


@lru_cache(maxsize=1)
def get_api_key() -> str | None:
    """
    Returns API key if set; None when not configured (internal use).
    """
    return os.getenv(f"{ENV_PREFIX}API_KEY")


@lru_cache(maxsize=1)
def get_allowed_origins() -> list[str]:
    """
    Read allowed CORS origins from env APP_ALLOWED_ORIGINS (comma separated).
    Defaults to local dev addresses.
    """
    raw = os.getenv(f"{ENV_PREFIX}ALLOWED_ORIGINS")
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return ["http://localhost:3000", "http://127.0.0.1:3000"]
