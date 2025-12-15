import pandas as pd
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


st.set_page_config(page_title="Wildflix", page_icon="W", layout="wide")

W_QUALITY = 0.4
W_POPULARITY = 0.2
W_GLOBAL = 0.4


def get_featured_movies(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    df_tmp = df.copy()
    for col in ("imdb_score_norm", "popularity_norm", "score_global_norm"):
        if col not in df_tmp.columns:
            df_tmp[col] = 0.0

    df_tmp["featured_score"] = (
        W_QUALITY * df_tmp["imdb_score_norm"]
        + W_POPULARITY * df_tmp["popularity_norm"]
        + W_GLOBAL * df_tmp["score_global_norm"]
    )
    return df_tmp.sort_values(by="featured_score", ascending=False).head(n)


def get_blockbuster(df: pd.DataFrame, n: int = 1) -> pd.DataFrame:
    if "budget" not in df.columns:
        return df.head(0)

    df_tmp = df.copy()
    if "budget_is_imputed" in df_tmp.columns:
        non_imputed = df_tmp[df_tmp["budget_is_imputed"] == 0]
        if not non_imputed.empty:
            df_tmp = non_imputed

    df_tmp = df_tmp[df_tmp["budget"].notna()]
    return df_tmp.sort_values(by="budget", ascending=False).head(n)


def get_underrated_gems(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    if "num_voted_users" not in df.columns or "score_global" not in df.columns:
        return df.head(0)

    df_tmp = df.copy()
    df_tmp = df_tmp[df_tmp["num_voted_users"] > 1000].copy()
    df_tmp["gem_score"] = df_tmp["score_global"] / df_tmp["num_voted_users"] ** 0.2
    return df_tmp.sort_values(by="gem_score", ascending=False).head(n)


def get_niche_movies(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    if "num_voted_users" not in df.columns or "score_global" not in df.columns:
        return df.head(0)

    df_tmp = df.copy()
    df_tmp = df_tmp[df_tmp["num_voted_users"].notna() & df_tmp["score_global"].notna()].copy()
    df_tmp = df_tmp[df_tmp["num_voted_users"] >= 100]

    thresholds = [1000, 2000, 5000, 10000, float("inf")]
    for threshold in thresholds:
        candidates = df_tmp[df_tmp["num_voted_users"] <= threshold]
        if len(candidates) >= n:
            df_tmp = candidates
            break

    return df_tmp.sort_values(
        by=["score_global", "num_voted_users"], ascending=[False, True]
    ).head(n)


def _exclude_keys(df: pd.DataFrame, used_keys: set[str]) -> pd.DataFrame:
    if not used_keys or "imdb_key" not in df.columns:
        return df
    return df[~df["imdb_key"].isin(used_keys)]


def main():
    init_auth_state()
    apply_wildflix_theme()
    sidebar_navigation()
    login_form()
    logout_button()
    show_flash_toast()

    inject_wildflix_styles()

    df = load_movies()
    render_global_search(df, source_page="Home.py")

    st.title("Wildflix")

    used_keys: set[str] = set()

    featured_top3 = get_featured_movies(df, n=3)
    if "imdb_key" in featured_top3.columns:
        used_keys.update(featured_top3["imdb_key"].dropna().astype(str).tolist())
    remaining = _exclude_keys(df, used_keys)

    blockbuster = get_blockbuster(remaining, n=1)
    if "imdb_key" in blockbuster.columns:
        used_keys.update(blockbuster["imdb_key"].dropna().astype(str).tolist())
    remaining = _exclude_keys(df, used_keys)

    gem_one = get_underrated_gems(remaining, n=1)
    if "imdb_key" in gem_one.columns:
        used_keys.update(gem_one["imdb_key"].dropna().astype(str).tolist())
    remaining = _exclude_keys(df, used_keys)

    section_title("Films vedettes")
    vedettes_df = pd.concat([featured_top3, blockbuster, gem_one], ignore_index=True)
    render_movie_row(vedettes_df, key="home_vedettes", max_items=5, source_page="Home.py")

    st.markdown("---")
    section_title("Pépites")
    pepites_df = get_underrated_gems(remaining, n=5)
    render_movie_row(pepites_df, key="home_pepites", max_items=5, source_page="Home.py")

    if "imdb_key" in pepites_df.columns:
        used_keys.update(pepites_df["imdb_key"].dropna().astype(str).tolist())
    remaining = _exclude_keys(df, used_keys)

    st.markdown("---")
    section_title("Niche")
    niche_df = get_niche_movies(remaining, n=5)
    render_movie_row(niche_df, key="home_niche", max_items=5, source_page="Home.py")


if __name__ == "__main__":
    main()
