import streamlit as st
import pandas as pd

from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.ui_components import render_movie_row, section_title
from utils.i18n import t
from utils.layout import common_page_setup
from utils.text import slugify


def main():
    common_page_setup(page_title=t("genre_title"), page_icon="🎭")

    df = load_movies()
    render_global_search(df, source_page="pages/1_Par_genre.py")

    st.title(t("genre_title"))

    genres = sorted(df["genre_main"].dropna().unique()
                    ) if "genre_main" in df.columns else []
    if not genres:
        st.error("Aucun genre disponible dans le dataset.")
        return

    selected_genre = st.selectbox(t("search_choose"), genres)

    filtered = df[df["genre_main"] == selected_genre].copy()
    sort_cols = [c for c in ["score_global", "popularity",
                             "num_voted_users"] if c in filtered.columns]
    if sort_cols:
        filtered = filtered.sort_values(
            sort_cols, ascending=[False] * len(sort_cols))

    top_n = st.slider("Nombre de films à afficher :", 5, 50, 10)
    results = filtered.head(top_n).reset_index(drop=True)

    section_title(
        t("top_n_genre", min(top_n, len(results)), selected_genre),
        t("click_to_open"),
    )

    genre_key = slugify(str(selected_genre))
    for start in range(0, len(results), 5):
        render_movie_row(
            results.iloc[start: start + 5],
            key=f"genre_{genre_key}_{start}",
            max_items=5,
            source_page="pages/1_Par_genre.py",
        )


if __name__ == "__main__":
    main()
