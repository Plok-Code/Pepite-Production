import pandas as pd
import streamlit as st
from textwrap import dedent
from utils.i18n import t


def movie_card(row: pd.Series, show_add_fav: bool = False):
    col1, col2 = st.columns([1, 3])
    with col1:
        if pd.notna(row.get("Poster", None)):
            st.image(row["Poster"], width=200)
        else:
            st.write("Pas d'affiche")
    with col2:
        title_year = int(row["title_year"]) if not pd.isna(
            row["title_year"]) else "N/A"
        st.markdown(f"### {row['movie_title']} ({title_year})")
        st.write(f"Genre principal : {row.get('genre_main', 'N/A')}")
        st.write(f"Score global : {row.get('score_global', 'N/A')}")
        st.write(f"IMDb : {row.get('imdb_score', 'N/A')}")
        st.write(f"Popularite : {row.get('popularity', 'N/A')}")
        if show_add_fav:
            if st.button("Ajouter aux favoris", key=f"fav_{row['imdb_key']}"):
                st.session_state.favorites.add(row["imdb_key"])
                st.success("Ajoute aux favoris")

            # Helper to check if liked for coloring (though movie_card button is simple)
            is_fav = row["imdb_key"] in st.session_state.get(
                "favorites", set())
            if is_fav:
                st.markdown(
                    f"""<style>
                    [class*="st-key-fav_{row['imdb_key']}"] {{
                        border-color: transparent !important;
                    }}
                    [class*="st-key-fav_{row['imdb_key']}"] p,
                    [class*="st-key-fav_{row['imdb_key']}"] span {{
                        color: #FF3B3B !important;
                    }}
                    </style>""",
                    unsafe_allow_html=True,
                )


def movie_tile(row: pd.Series, show_add_fav: bool = False, key_prefix: str = ""):
    title = row.get("movie_title", "N/A")
    genre = row.get("genre_main", "N/A")
    note = row.get("score_global", None)
    director = row.get("director_name", "N/A")
    duration = row.get("duration", None)

    actors = [row.get("actor_1_name"), row.get(
        "actor_2_name"), row.get("actor_3_name")]
    actors = [a for a in actors if pd.notna(a) and str(a).strip()]

    st.markdown(f"**{title}**")
    st.write(f"Genre principal : {genre}" if pd.notna(
        genre) else "Genre principal : N/A")

    if pd.notna(note):
        st.write(f"Note : {float(note):.2f}")
    else:
        st.write("Note : N/A")

    st.write(f"Realisateur : {director}" if pd.notna(
        director) else "Realisateur : N/A")
    st.write(
        f"Acteurs : {', '.join(map(str, actors))}" if actors else "Acteurs : N/A")

    if pd.notna(duration):
        st.write(f"Duree : {int(duration)} min")
    else:
        st.write("Duree : N/A")

    if show_add_fav and pd.notna(row.get("imdb_key")):
        imdb_key = row["imdb_key"]
        if st.button("Ajouter aux favoris", key=f"{key_prefix}fav_{imdb_key}"):
            st.session_state.favorites.add(imdb_key)
            st.success("Ajoute aux favoris")


def inject_wildflix_styles():
    # Deprecated: CSS is now injected by apply_wildflix_theme()
    pass


def _format_note(value) -> str:
    try:
        return f"{float(value):.2f}"
    except Exception:
        return "N/A"


def render_movie_row(
    rows: pd.DataFrame,
    key: str,
    max_items: int = 5,
    source_page: str | None = None,
    target_page: str | None = "pages/_Film.py",
):
    from utils.auth import toggle_favorite

    from utils.auth import toggle_favorite

    # inject_wildflix_styles()  <-- REMOVED: Now called by pages directly to avoid duplication

    is_authenticated = st.session_state.get("is_authenticated", False)
    favorites = st.session_state.setdefault("favorites", set())

    df_iter = rows.head(max_items).reset_index(drop=True)
    if df_iter.empty:
        st.info("Aucun film a afficher.")
        return

    with st.container(key=f"wf-scroll-{key}"):
        cols = st.columns(len(df_iter))
        for i, (_, row) in enumerate(df_iter.iterrows()):
            with cols[i]:
                imdb_key_raw = row.get("imdb_key")
                imdb_key = str(imdb_key_raw) if pd.notna(
                    imdb_key_raw) else None
                title = row.get("movie_title", "N/A")
                poster = row.get("Poster", None)

                liked = bool(imdb_key) and (imdb_key in favorites)
                fav_label = "♥" if liked else "♡"

                with st.container(border=True, key=f"wf_card_{key}_{i}_{imdb_key or 'na'}"):
                    def _open_movie():
                        st.session_state["selected_imdb_key"] = imdb_key
                        st.query_params["id"] = imdb_key
                        if source_page:
                            st.session_state["selected_source_page"] = source_page
                        if target_page:
                            st.switch_page(target_page)
                        else:
                            st.rerun()

                    poster_url = str(poster) if pd.notna(
                        poster) and str(poster).strip() else None
                    poster_key = f"wf_poster_btn_{key}_{i}_{imdb_key or 'na'}"
                    fav_button_key = f"wf_fav_overlay_{key}_{i}_{imdb_key or 'na'}"

                    with st.container(key=f"wf_poster_wrap_{key}_{i}_{imdb_key or 'na'}"):
                        # 1. Poster Button (Rendered FIRST so it is behind)
                        if poster_url and imdb_key:
                            safe_url = poster_url.replace("'", "%27")
                            st.markdown(
                                f"<style>[class*=\"st-key-{poster_key}\"] button {{ background-image: url('{safe_url}'); }}</style>",
                                unsafe_allow_html=True,
                            )
                            if st.button(
                                "Ouvrir",
                                key=poster_key,
                                type="secondary",
                                use_container_width=True,
                            ):
                                _open_movie()
                        elif poster_url:
                            st.image(poster_url, use_container_width=True)
                        else:
                            st.info("Pas d'affiche.")

                        # 2. Heart Overlay Wrapper (Rendered SECOND so it is ON TOP)
                        fav_key_wrapper = f"wf_fav_overlay_container_{key}_{i}_{imdb_key or 'na'}"
                        with st.container(key=fav_key_wrapper):
                            # Primary button invisible effectively, served as click target
                            if st.button(
                               fav_label,
                               key=fav_button_key,
                               type="primary",
                               help="Ajouter/Retirer des favoris",
                               disabled=not is_authenticated or not imdb_key,
                               ):
                                toggle_favorite(imdb_key)
                                st.rerun()

                    # Title / Open Button (Full Width Block)
                    if st.button(
                        str(title),
                        key=f"{key}_open_{imdb_key or 'na'}_{i}",
                        type="secondary",
                        disabled=not imdb_key,
                        help=("Fiche indisponible." if not imdb_key else None),
                        use_container_width=True,
                    ):
                        if imdb_key:
                            _open_movie()

                    genre = row.get("genre_main", "N/A")
                    note = _format_note(row.get("score_global", None))
                    director_val = row.get("director_name")
                    director = str(director_val) if pd.notna(
                        director_val) else "N/A"
                    duration_val = row.get("duration")
                    duration = f"{int(duration_val)} min" if pd.notna(
                        duration_val) else "N/A"

                    language_val = row.get("language")
                    language = str(language_val) if pd.notna(
                        language_val) and str(language_val).strip() else "N/A"

                    actors_list = [row.get("actor_1_name"), row.get(
                        "actor_2_name"), row.get("actor_3_name")]
                    actors_clean = [
                        str(a) for a in actors_list if pd.notna(a) and str(a).strip()]
                    actors_str = ", ".join(
                        actors_clean) if actors_clean else "N/A"

                    # Labels Translation
                    lbl_genre = t("genre_label")
                    lbl_note = t("rating_label")
                    lbl_dir = t("director_label")
                    lbl_act = t("actors_label")
                    lbl_lang = t("language_label")
                    lbl_dur = t("duration_label")
                    unit_min = t("minutes")

                    # Custom HTML for perfectly aligned metadata grid with Pinned Bottom
                    meta_html = f"""
                    <div class="wf-meta-container">
                        <div class="wf-meta-row">{lbl_genre} {genre}</div>
                        <div class="wf-meta-row">{lbl_note} {note}</div>
                        <div class="wf-meta-row wf-meta-text">{lbl_dir} {director}</div>
                        <div class="wf-meta-row wf-meta-text">{lbl_act} {actors_str}</div>
                        <div class="wf-meta-row">{lbl_lang} {language}</div>
                        <div class="wf-meta-row wf-meta-duration">{lbl_dur} {duration}</div>
                    </div>
                    """
                    st.markdown(meta_html, unsafe_allow_html=True)


def section_title(title: str, subtitle: str | None = None):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)
