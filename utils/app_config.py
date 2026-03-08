import streamlit as st
import os

# Weights for "Featured" score calculation
W_QUALITY = 0.4
W_POPULARITY = 0.2
W_GLOBAL = 0.4


def _secret_str(key: str) -> str:
    try:
        value = st.secrets.get(str(key))
    except Exception:
        value = None
    return str(value or "").strip()


def get_secret_key() -> str:
    """
    Retrieves the SECRET_KEY from st.secrets or environment variables.
    Falls back to a dev key if not found (with a warning in logs).
    """
    # 1. Try Streamlit Secrets
    try:
        if "SECRET_KEY" in st.secrets:
            return st.secrets["SECRET_KEY"]
    except Exception:
        pass

    # 2. Try Environment Variable
    env_key = os.getenv("WILDFLIX_SECRET_KEY")
    if env_key:
        return env_key

    # 3. Fallback (Development only)
    # console warning could be added here if needed
    return "wildflix_dev_secret_key_fallback_do_not_use_in_prod"


def get_bootstrap_admin_config() -> dict[str, str] | None:
    email = _secret_str("WILDFLIX_ADMIN_EMAIL")
    password = _secret_str("WILDFLIX_ADMIN_PASSWORD")
    pseudo = _secret_str("WILDFLIX_ADMIN_PSEUDO")

    if not email or not password:
        try:
            section = st.secrets.get("admin_bootstrap", {})
        except Exception:
            section = {}
        if isinstance(section, dict):
            email = email or str(section.get("email") or "").strip()
            password = password or str(section.get("password") or "").strip()
            pseudo = pseudo or str(section.get("pseudo") or "").strip()

    email = email or os.getenv("WILDFLIX_ADMIN_EMAIL", "").strip()
    password = password or os.getenv("WILDFLIX_ADMIN_PASSWORD", "").strip()
    pseudo = pseudo or os.getenv("WILDFLIX_ADMIN_PSEUDO", "").strip()

    if not email or not password:
        return None

    return {
        "email": email,
        "password": password,
        "pseudo": pseudo or "Admin",
    }
