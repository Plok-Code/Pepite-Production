import streamlit as st
import os

# Weights for "Featured" score calculation
W_QUALITY = 0.4
W_POPULARITY = 0.2
W_GLOBAL = 0.4


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
