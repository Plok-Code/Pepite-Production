from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

from utils.i18n import t
from utils.text import normalize_text


SEARCH_RESULTS_PAGE = "pages/_Recherche.py"


@st.cache_data(show_spinner=False)
def _get_brand_logo_data_uri() -> str | None:
    logo_path = Path(__file__).resolve().parent.parent / \
        "assets" / "logo_pepite_prodseul.png"
    if not logo_path.exists():
        return None

    try:
        img = Image.open(logo_path)
        img.thumbnail((340, 110))
        buf = BytesIO()
        img.save(buf, format="PNG", optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/png;base64,{b64}"
    except Exception:
        return None


def _submit_global_search(source_page: str) -> None:
    raw = str(st.session_state.get("wf_global_search_query", "")).strip()
    q = normalize_text(raw)
    if len(q) < 2:
        return

    st.session_state["wf_search_query"] = raw
    st.session_state["wf_search_query_norm"] = q
    st.session_state["wf_search_source_page"] = source_page

    try:
        st.switch_page(SEARCH_RESULTS_PAGE)
    except Exception:
        st.rerun()


def render_global_search(
    df: pd.DataFrame, source_page: str, target_page: str | None = "pages/_Film.py"
) -> None:
    # NOTE: `df` and `target_page` kept for backward compatibility.
    with st.container(key="wf_global_header"):
        with st.form("global_search_form", border=False):
            # Search only (no logo) to avoid layout issues across browsers.
            # Centering the search bar with empty columns on sides
            _, c1, c2, _ = st.columns(
                [2, 5, 1, 2], vertical_alignment="center")
            with c1:
                st.text_input(
                    t("search_placeholder"),
                    key="wf_global_search_query",
                    label_visibility="collapsed",
                    placeholder=t("search_placeholder"),
                )

            with c2:
                submitted = st.form_submit_button(
                    t("search_submit"),
                    use_container_width=True,
                    type="secondary",
                )

            if submitted:
                _submit_global_search(source_page)
