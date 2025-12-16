import os
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.i18n import t
from utils.layout import common_page_setup


def _get_powerbi_embed_url() -> str | None:
    url = str(os.getenv("POWERBI_EMBED_URL", "")).strip()
    if url:
        return url

    try:
        raw = st.secrets.get("POWERBI_EMBED_URL") or st.secrets.get(
            "powerbi_embed_url")
    except StreamlitSecretNotFoundError:
        return None

    if raw is None:
        return None
    url = str(raw).strip()
    return url or None


def main():
    common_page_setup(page_title=t("admin_title"), page_icon="🔒")

    if st.session_state.get("role") != "admin":
        st.error(t("admin_access_denied"))
        st.stop()

    df = load_movies()
    render_global_search(df, source_page="pages/_Admin.py")

    st.title(t("admin_title"))

    tab_py, tab_bi = st.tabs(["Dashboard Python", "Dashboard Power BI"])

    with tab_py:
        st.subheader("Dashboard Python")
        # Python dashboard logic can be added here
        st.info("Section Dashboard Python en construction.")

    with tab_bi:
        st.subheader("Dashboard Power BI")
        powerbi_url = _get_powerbi_embed_url()
        if powerbi_url:
            st.markdown(
                f"""
                <iframe
                    width="100%" height="650"
                    src="{powerbi_url}"
                    frameborder="0" allowFullScreen="true">
                </iframe>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.error(
                "Power BI non configure. Ajoutez `POWERBI_EMBED_URL` (env ou secrets).")


if __name__ == "__main__":
    main()
