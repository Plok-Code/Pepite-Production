import streamlit as st

from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.ui_components import render_movie_row, section_title
from utils.i18n import t
from utils.layout import common_page_setup
from services.recommendation_service import get_recommendations_from_favorites


def main():
    common_page_setup(page_title=t("recos_title"), page_icon="★")

    if not st.session_state.get("is_authenticated", False):
        st.error(t("auth_required_recos"))
        st.stop()

    df = load_movies()
    render_global_search(df, source_page="pages/3_Recommandations.py")

    st.title(t("recos_title"))
    section_title(t("for_you"), t("for_you_desc"))

    favorites = st.session_state.setdefault("favorites", set())

    if not favorites:
        st.info(t("no_favorites_hint"))
    else:
        recos = get_recommendations_from_favorites(df, favorites, n=10)
        if recos.empty:
            st.info(t("more_favorites_needed"))
        else:
            for start in range(0, len(recos), 5):
                render_movie_row(
                    recos.iloc[start: start + 5],
                    key=f"user_recos_{start}",
                    max_items=5,
                    source_page="pages/3_Recommandations.py",
                )


if __name__ == "__main__":
    main()
