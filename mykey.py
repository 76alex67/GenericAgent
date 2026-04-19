import os
from pathlib import Path

_DOTENV = {}
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

proxy = None

native_oai_config = {
    "apikey": _env("OPENAI_API_KEY"),
    "apibase": _env("OPENAI_BASE_URL", "OPENAI_API_BASE", "OPENAI_API_BASE_URL", default="https://api.openai.com/v1"),
    "model": _env("OPENAI_MODEL", default="gpt-4o-mini"),
    "api_mode": "responses",
    "read_timeout": 120,
    "max_retries": 2,
}
