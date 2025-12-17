import pandas as pd
import streamlit as st

from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.ui_components import render_movie_row, section_title
from utils.i18n import t
from utils.layout import common_page_setup
from services.movie_service import (
    get_featured_movies,
    get_blockbuster,
    get_underrated_gems,
    get_niche_movies,
    exclude_keys
)


def main():
    common_page_setup(page_title="Pepite Production", page_icon="💎")

    # Load Data
    df = load_movies()
    render_global_search(df, source_page="Home.py")

    st.title(t("app_title"))

    # Logic to fetch movies
    used_keys: set[str] = set()

    # 1. Vedettes (Featured + Blockbuster + 1 Gem)
    featured_top3 = get_featured_movies(df, n=3)
    if "imdb_key" in featured_top3.columns:
        used_keys.update(
            featured_top3["imdb_key"].dropna().astype(str).tolist())

    remaining = exclude_keys(df, used_keys)

    blockbuster = get_blockbuster(remaining, n=1)
    if "imdb_key" in blockbuster.columns:
        used_keys.update(blockbuster["imdb_key"].dropna().astype(str).tolist())

    remaining = exclude_keys(df, used_keys)

    gem_one = get_underrated_gems(remaining, n=1)
    if "imdb_key" in gem_one.columns:
        used_keys.update(gem_one["imdb_key"].dropna().astype(str).tolist())

    remaining = exclude_keys(df, used_keys)

    # Render Vedettes
    section_title(t("featured_section"))
    vedettes_df = pd.concat(
        [featured_top3, blockbuster, gem_one], ignore_index=True)
    render_movie_row(vedettes_df, key="home_vedettes",
                     max_items=5, source_page="Home.py")

    st.markdown("---")

    # 2. Pépites (Gems)
    section_title(t("gems_section"))
    pepites_df = get_underrated_gems(remaining, n=5)
    render_movie_row(pepites_df, key="home_pepites",
                     max_items=5, source_page="Home.py")

    if "imdb_key" in pepites_df.columns:
        used_keys.update(pepites_df["imdb_key"].dropna().astype(str).tolist())
    remaining = exclude_keys(df, used_keys)

    st.markdown("---")

    # 3. Niche
    section_title(t("niche_section"))
    niche_df = get_niche_movies(remaining, n=5)
    render_movie_row(niche_df, key="home_niche",
                     max_items=5, source_page="Home.py")


if __name__ == "__main__":
    main()