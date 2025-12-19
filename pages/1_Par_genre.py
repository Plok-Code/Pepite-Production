import streamlit as st
import pandas as pd

from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.ui_components import render_movie_row, section_title
from utils.i18n import t
from utils.layout import common_page_setup
from utils.text import slugify
from utils.movie_categories import categorize_movies


def _shuffle(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    if df is None or df.empty:
        return df.iloc[0:0].copy() if df is not None else pd.DataFrame()
    return df.sample(frac=1, random_state=int(seed)).reset_index(drop=True)


def _get_relaxed_pool(
    df: pd.DataFrame, *, rating_col: str | None, count_col: str | None
) -> pd.DataFrame:
    """
    Relaxed pool to fill missing items when a genre has too few Blockbusters/Pépites.

    Rule (1 step max):
      - vote_decile between 3 and 10 (Pépite → Blockbuster range)
      - rating threshold lowered by 1 point (from >8 to >7), never more.
    """
    if df is None or df.empty or not rating_col or not count_col:
        return df.iloc[0:0].copy() if df is not None else pd.DataFrame()

    if rating_col not in df.columns or count_col not in df.columns or "vote_decile" not in df.columns:
        return df.iloc[0:0].copy()

    work = df.copy()
    work[rating_col] = pd.to_numeric(work[rating_col], errors="coerce")
    work[count_col] = pd.to_numeric(work[count_col], errors="coerce")

    work = work[
        work["vote_decile"].notna()
        & work["vote_decile"].between(3, 10)
        & (work[rating_col] > 7)
    ].copy()
    return work


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

    categorized, rating_col, count_col = categorize_movies(df, min_votes=5)

    special_keys = ["__blockbusters__", "__pepites__", "__niche__", "__navets__"]

    def _format_option(value: str) -> str:
        if value == "__blockbusters__":
            return t("featured_section")
        if value == "__pepites__":
            return t("gems_section")
        if value == "__niche__":
            return t("niche_section")
        if value == "__navets__":
            return t("flops_section")
        return str(value)

    selected = st.selectbox(
        t("search_choose"),
        options=special_keys + genres,
        format_func=_format_option,
    )

    genre_key = slugify(str(selected))
    seed_key = f"wf_genre_random_seed_{genre_key}"
    if seed_key not in st.session_state:
        st.session_state[seed_key] = 0
    seed = int(st.session_state[seed_key])

    c1, c2 = st.columns([1, 4], vertical_alignment="center")
    with c1:
        if st.button(t("refresh_button"), key=f"wf_genre_refresh_{genre_key}"):
            st.session_state[seed_key] = int(st.session_state[seed_key]) + 1
            seed = int(st.session_state[seed_key])

    target_n = 30

    if selected in special_keys:
        category_map = {
            "__blockbusters__": "Blockbuster",
            "__pepites__": "Pépite",
            "__niche__": "Niche",
            "__navets__": "Navet",
        }
        target_category = category_map[str(selected)]
        pool = categorized[categorized["category"] == target_category].copy()
        pool = _shuffle(pool, seed=seed + 10)
        results = pool.head(target_n).reset_index(drop=True)
        selected_label = _format_option(str(selected))
    else:
        selected_genre = str(selected)
        selected_label = selected_genre

        filtered = categorized[categorized["genre_main"] == selected_genre].copy()

        strict = filtered[filtered["category"].isin(["Blockbuster", "Pépite"])].copy()
        if "imdb_key" in strict.columns:
            strict["imdb_key"] = strict["imdb_key"].astype(str)
            strict = strict.drop_duplicates(subset=["imdb_key"], keep="first")
        strict = _shuffle(strict, seed=seed + 1)

        relaxed = _get_relaxed_pool(filtered, rating_col=rating_col, count_col=count_col)
        if "imdb_key" in relaxed.columns:
            relaxed["imdb_key"] = relaxed["imdb_key"].astype(str)
            relaxed = relaxed.drop_duplicates(subset=["imdb_key"], keep="first")
            if "imdb_key" in strict.columns and not strict.empty:
                relaxed = relaxed[~relaxed["imdb_key"].isin(strict["imdb_key"].astype(str))].copy()
        relaxed = _shuffle(relaxed, seed=seed + 2)

        results = strict.copy()
        if len(results) < target_n and not relaxed.empty:
            results = pd.concat([results, relaxed.head(target_n - int(len(results)))], ignore_index=True)
        results = results.head(target_n).reset_index(drop=True)

    with c2:
        st.caption(t("genre_random_caption", len(results)))

    section_title(
        t("genre_random_title", len(results), selected_label),
        t("click_to_open"),
    )

    for start in range(0, len(results), 5):
        render_movie_row(
            results.iloc[start: start + 5],
            key=f"genre_{genre_key}_{start}",
            max_items=5,
            source_page="pages/1_Par_genre.py",
        )


if __name__ == "__main__":
    main()
