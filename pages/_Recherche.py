import streamlit as st

from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.i18n import t
from utils.layout import common_page_setup
from utils.search import search_movies
from utils.ui_components import render_movie_row, section_title


def _get_search_query() -> str:
    raw = st.session_state.get("wf_search_query")
    if raw is None:
        return ""
    return str(raw).strip()


def main():
    common_page_setup(page_title=t("search_page_title"), page_icon="🔎")

    df = load_movies()
    render_global_search(df, source_page="pages/_Recherche.py")

    query = _get_search_query()
    if not query:
        st.info(t("search_hint"))
        return

    source_page = st.session_state.get("wf_search_source_page") or "Home.py"

    left, right = st.columns([6, 1], vertical_alignment="center")
    with left:
        section_title(t("search_results_for", query))
    with right:
        if st.button(t("back_button"), use_container_width=True):
            st.switch_page(str(source_page))

    results = search_movies(df, query=query, limit=50).df
    if results.empty:
        st.info(t("search_no_result"))
        return

    for start in range(0, len(results), 5):
        render_movie_row(
            results.iloc[start: start + 5],
            key=f"search_{start}",
            max_items=5,
            source_page="pages/_Recherche.py",
        )


if __name__ == "__main__":
    main()

