import pandas as pd
import streamlit as st

from utils.text import normalize_text


def render_global_search(
    df: pd.DataFrame, source_page: str, target_page: str | None = "pages/_Film.py"
):
    with st.container():
        left, middle, right = st.columns([1.2, 6, 1.2], vertical_alignment="center")
        with left:
            if st.button("Wildflix", key="wf_brand_home", type="secondary"):
                st.switch_page("Home.py")
        with middle:
            query = st.text_input(
                "Rechercher un film",
                key="wf_global_search_query",
                label_visibility="collapsed",
                placeholder="Rechercher un film…",
            )
        with right:
            if st.button("Effacer", key="wf_global_search_clear", use_container_width=True):
                st.session_state["wf_global_search_query"] = ""
                st.rerun()

    q = normalize_text(query)
    if len(q) < 2:
        st.session_state.pop("wf_global_search_last_query", None)
        return

    search_col = None
    for col in ("title_search", "title_lower", "movie_title_clean"):
        if col in df.columns:
            search_col = col
            break

    if not search_col:
        return

    if search_col == "title_search":
        needle = q
    else:
        needle = q.lower()

    matches = df[df[search_col].astype(str).str.contains(needle, na=False, regex=False)].copy()
    if matches.empty:
        st.info("Aucun resultat.")
        return

    sort_cols = [c for c in ["score_global", "popularity", "num_voted_users"] if c in matches.columns]
    if sort_cols:
        matches = matches.sort_values(sort_cols, ascending=[False] * len(sort_cols))

    matches = matches.reset_index(drop=True).head(20)

    options: list[str] = ["Choisir un film…"]
    option_to_key: dict[str, str] = {}
    for _, row in matches.iterrows():
        imdb_key = row.get("imdb_key")
        if pd.isna(imdb_key):
            continue
        imdb_key = str(imdb_key)

        title = str(row.get("movie_title", "Film"))
        year = row.get("title_year", None)
        if pd.notna(year):
            label = f"{title} ({int(year)})"
        else:
            label = title

        genre = row.get("genre_main", None)
        if pd.notna(genre) and str(genre).strip():
            label = f"{label} • {str(genre)}"

        label = f"{label} — {imdb_key}"
        options.append(label)
        option_to_key[label] = imdb_key

    if len(options) == 1:
        st.info("Aucun resultat.")
        return

    if st.session_state.get("wf_global_search_last_query") != q:
        st.session_state["wf_global_search_last_query"] = q
        st.session_state["wf_global_search_pick"] = options[0]
    elif st.session_state.get("wf_global_search_pick") not in options:
        st.session_state["wf_global_search_pick"] = options[0]

    picked = st.selectbox(
        "Resultats",
        options,
        key="wf_global_search_pick",
        label_visibility="collapsed",
    )
    picked_key = option_to_key.get(picked)

    if st.button(
        "Ouvrir",
        key="wf_global_search_open",
        disabled=(picked_key is None),
    ):
        st.session_state["selected_imdb_key"] = picked_key
        st.session_state["selected_source_page"] = source_page
        st.session_state["wf_global_search_query"] = ""
        if target_page:
            st.switch_page(target_page)
        else:
            st.rerun()
