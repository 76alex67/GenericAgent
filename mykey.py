"""
GenericAgent local key config.

Priority:
1) Read from environment variables if available.
2) Read from nearby .env files if available.
3) Fall back to editable placeholders below.
"""

import os
from pathlib import Path


def _load_dotenv_candidates():
    env_map = {}
    base_dir = Path(__file__).resolve().parent
    candidates = [
        base_dir / ".env",
        base_dir.parent / "deep-research" / ".env",
    ]
    for candidate in candidates:
        if not candidate.exists():
            continue
        try:
            for raw_line in candidate.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'").strip('"')
                if key and key not in env_map:
                    env_map[key] = value
        except OSError:
            continue
    return env_map


_DOTENV = _load_dotenv_candidates()
_STREAMLIT_SECRETS = {}

try:
    import streamlit as st

    _STREAMLIT_SECRETS = dict(getattr(st, "secrets", {}))
except Exception:
    _STREAMLIT_SECRETS = {}


def _env(name, *fallback_names, default=""):
    for key in (name, *fallback_names):
        value = os.getenv(key, "").strip()
        if value:
            return value
        value = _DOTENV.get(key, "").strip()
        if value:
            return value
        secret_value = _STREAMLIT_SECRETS.get(key, "")
        if isinstance(secret_value, str) and secret_value.strip():
            return secret_value.strip()
    return default


def _bool_env(name, default=False):
    value = _env(name)
    if not value:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}

# Disable default proxy fallback in llmcore.py
proxy = None

_LOCAL_CODEX_BASE = "http://127.0.0.1:15721/v1"
_USE_LOCAL_CODEX = _bool_env("GENERICAGENT_USE_LOCAL_CODEX", default=True)
_USING_LOCAL_CODEX = False

_OPENAI_KEY = _env("OPENAI_API_KEY")
_OPENAI_BASE = _env("OPENAI_BASE_URL", "OPENAI_API_BASE", "OPENAI_API_BASE_URL", default="https://api.openai.com/v1")
_OPENAI_MODEL = _env("OPENAI_MODEL", default="gpt-4o-mini")

if not _OPENAI_KEY and _USE_LOCAL_CODEX:
    _USING_LOCAL_CODEX = True
    _OPENAI_KEY = "sk-local-codex"
    _OPENAI_BASE = _LOCAL_CODEX_BASE
    _OPENAI_MODEL = _env("GENERICAGENT_LOCAL_CODEX_MODEL", "CODEX_MODEL", default="gpt-5.4")

if _OPENAI_KEY:
    native_oai_config = {
        "apikey": _OPENAI_KEY,
        "apibase": _OPENAI_BASE,
        "model": _OPENAI_MODEL,
    }
    if _USING_LOCAL_CODEX:
        native_oai_config.update({
            "api_mode": "responses",
            "read_timeout": 120,
            "max_retries": 2,
        })
else:
    # Replace this placeholder if you do not use env vars.
    native_oai_config = {
        "apikey": "sk-your-api-key-here",
        "apibase": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
    }

_ANTHROPIC_KEY = _env("ANTHROPIC_API_KEY")
_ANTHROPIC_BASE = _env("ANTHROPIC_BASE_URL", "ANTHROPIC_API_BASE_URL", default="https://api.anthropic.com")
_ANTHROPIC_MODEL = _env("ANTHROPIC_MODEL", default="claude-sonnet-4-20250514")

# Optional second backend. It is loaded only when env vars are set.
if _ANTHROPIC_KEY:
    native_claude_config = {
        "apikey": _ANTHROPIC_KEY,
        "apibase": _ANTHROPIC_BASE,
        "model": _ANTHROPIC_MODEL,
    }
