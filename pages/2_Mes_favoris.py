import streamlit as st

from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.ui_components import render_movie_row, section_title
from utils.i18n import t
from utils.layout import common_page_setup


def main():
    common_page_setup(page_title=t("favorites_title"), page_icon="♥")

    if not st.session_state.get("is_authenticated", False):
        st.error(t("auth_required_favs"))
        st.stop()

    df = load_movies()
    render_global_search(df, source_page="pages/2_Mes_favoris.py")

    st.title(t("favorites_title"))
    section_title(t("your_collection"), t("your_collection_desc"))

    favorites = st.session_state.setdefault("favorites", set())

    if not favorites:
        st.info(t("no_favorites"))
    else:
        fav_df = df[df["imdb_key"].astype(str).isin(
            set(map(str, favorites)))].copy()
        sort_cols = [c for c in ["score_global", "popularity",
                                 "num_voted_users"] if c in fav_df.columns]
        if sort_cols:
            fav_df = fav_df.sort_values(
                sort_cols, ascending=[False] * len(sort_cols))

        fav_df = fav_df.reset_index(drop=True)
        for start in range(0, len(fav_df), 5):
            render_movie_row(
                fav_df.iloc[start: start + 5],
                key=f"user_favs_{start}",
                max_items=5,
                source_page="pages/2_Mes_favoris.py",
            )


if __name__ == "__main__":
    main()
