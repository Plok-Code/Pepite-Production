from __future__ import annotations

import os

import streamlit as st


def get_powerbi_iframe_url() -> str | None:
    """
    Returns a Power BI "reportEmbed" URL for iframe rendering (User owns data).

    Configure in `.streamlit/secrets.toml` (ignored by git):

    [powerbi]
    SIMPLE_URL = "https://app.powerbi.com/reportEmbed?..."

    Or via env var (useful for deployments):
      - `WILDFLIX_POWERBI_SIMPLE_URL`
      - `POWERBI_SIMPLE_URL`
      - `POWERBI_REPORT_EMBED_URL`
      - `POWERBI_URL`
    """
    for env_key in (
        "WILDFLIX_POWERBI_SIMPLE_URL",
        "POWERBI_SIMPLE_URL",
        "POWERBI_REPORT_EMBED_URL",
        "POWERBI_URL",
        "POWERBI_IFRAME_URL",
    ):
        raw = os.getenv(env_key)
        if raw:
            url = str(raw).strip()
            if url:
                return url

    secrets = st.secrets.get("powerbi", st.secrets)
    for key in (
        "SIMPLE_URL",
        "simple_url",
        "REPORT_EMBED_URL",
        "report_embed_url",
        "IFRAME_URL",
        "iframe_url",
        "URL",
        "url",
    ):
        raw = secrets.get(key)
        if raw is None:
            continue
        url = str(raw).strip()
        if url:
            return url
    return None
