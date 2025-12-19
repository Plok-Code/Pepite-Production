import random
import streamlit as st

from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.ui_components import render_movie_row, section_title
from utils.i18n import t
from utils.layout import common_page_setup
from utils.movie_categories import categorize_movies, sample_rows


def main():
    common_page_setup(page_title="Pepite Production", page_icon="💎")

    # Load Data
    df = load_movies()
    render_global_search(df, source_page="Home.py")

    st.markdown(f"## {t('home_hero_title')}")
    st.markdown(f"##### {t('home_hero_subtitle')}")
    st.caption(t("home_school_note"))
    st.caption(t("home_intro"))

    # Random selections based on the categories defined in the project spec.
    categorized, _, _ = categorize_movies(df, min_votes=5)

    if "wf_home_seed" not in st.session_state:
        st.session_state["wf_home_seed"] = random.randint(0, 2_147_483_647)
    seed = int(st.session_state["wf_home_seed"])

    # 1) Vedettes / Blockbusters
    section_title(t("featured_section"))
    vedettes_pool = categorized[categorized["category"] == "Blockbuster"]
    vedettes_df = sample_rows(vedettes_pool, n=5, seed=seed + 1)
    render_movie_row(vedettes_df, key="home_vedettes",
                     max_items=5, source_page="Home.py")

    st.markdown("---")

    # 2) Pépites
    section_title(t("gems_section"))
    pepites_pool = categorized[categorized["category"] == "Pépite"]
    pepites_df = sample_rows(pepites_pool, n=5, seed=seed + 2)
    render_movie_row(pepites_df, key="home_pepites",
                     max_items=5, source_page="Home.py")

    st.markdown("---")

    # 3) Niche
    section_title(t("niche_section"))
    niche_pool = categorized[categorized["category"] == "Niche"]
    niche_df = sample_rows(niche_pool, n=5, seed=seed + 3)
    render_movie_row(niche_df, key="home_niche",
                     max_items=5, source_page="Home.py")

    st.markdown("---")

    # 4) Navets
    section_title(t("flops_section"))
    navets_pool = categorized[categorized["category"] == "Navet"]
    navets_df = sample_rows(navets_pool, n=5, seed=seed + 4)
    render_movie_row(navets_df, key="home_navets",
                     max_items=5, source_page="Home.py")


if __name__ == "__main__":
    main()
