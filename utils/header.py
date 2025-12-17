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
    logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo_pepite_prodseul.png"
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
    with st.container():
        c1, c2, c3 = st.columns([2.2, 6, 1.2], vertical_alignment="center")

        with c1:
            logo_uri = _get_brand_logo_data_uri()
            if logo_uri:
                st.markdown(
                    f"""
                    <style>
                    [class*="st-key-wf_brand_home_logo"] button{{
                      background-image: url("{logo_uri}") !important;
                      background-size: contain !important;
                      background-repeat: no-repeat !important;
                      background-position: center !important;
                      background-color: transparent !important;
                      border: 0 !important;
                      padding: 0 !important;
                      height: 72px !important;
                      min-height: 72px !important;
                    }}
                    [class*="st-key-wf_brand_home_logo"] button > div{{ opacity: 0 !important; }}
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Home",
                    key="wf_brand_home_logo",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.switch_page("Home.py")
            else:
                if st.button(t("app_title"), key="wf_brand_home", type="secondary"):
                    st.switch_page("Home.py")

        with c2:
            st.text_input(
                t("search_placeholder"),
                key="wf_global_search_query",
                label_visibility="collapsed",
                placeholder=t("search_placeholder"),
                on_change=_submit_global_search,
                args=(source_page,),
            )

        with c3:
            if st.button(
                t("search_submit"),
                key="wf_global_search_submit",
                use_container_width=True,
                type="secondary",
            ):
                _submit_global_search(source_page)
