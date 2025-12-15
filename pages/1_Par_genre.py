import re

import streamlit as st

from utils.auth import (
    init_auth_state,
    login_form,
    logout_button,
    show_flash_toast,
    sidebar_navigation,
)
from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.theme import apply_wildflix_theme
from utils.ui_components import inject_wildflix_styles, render_movie_row, section_title


def _slug(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "genre"


def main():
    st.set_page_config(page_title="Par genre", page_icon="G", layout="wide")
    apply_wildflix_theme()
    init_auth_state()
    sidebar_navigation()
    login_form()
    logout_button()
    show_flash_toast()
    inject_wildflix_styles()

    df = load_movies()
    render_global_search(df, source_page="pages/1_Par_genre.py")

    st.title("Par genre")

    genres = sorted(df["genre_main"].dropna().unique()) if "genre_main" in df.columns else []
    if not genres:
        st.error("Aucun genre disponible dans le dataset.")
        return

    selected_genre = st.selectbox("Choisissez un genre :", genres)

    filtered = df[df["genre_main"] == selected_genre].copy()
    sort_cols = [c for c in ["score_global", "popularity", "num_voted_users"] if c in filtered.columns]
    if sort_cols:
        filtered = filtered.sort_values(sort_cols, ascending=[False] * len(sort_cols))

    top_n = st.slider("Nombre de films a afficher :", 5, 50, 10)
    results = filtered.head(top_n).reset_index(drop=True)

    section_title(
        f"Top {min(top_n, len(results))} en {selected_genre}",
        "Cliquez sur un titre pour ouvrir la fiche du film.",
    )

    genre_key = _slug(str(selected_genre))
    for start in range(0, len(results), 5):
        render_movie_row(
            results.iloc[start : start + 5],
            key=f"genre_{genre_key}_{start}",
            max_items=5,
            source_page="pages/1_Par_genre.py",
        )


if __name__ == "__main__":
    main()
