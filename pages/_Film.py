import pandas as pd
import streamlit as st

from services.recommendation_service import get_similar_movies
from utils.auth import toggle_favorite
from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.ui_components import render_movie_row
from utils.i18n import t
from utils.layout import common_page_setup


def _get_selected_imdb_key() -> str | None:
    # Check URL first/fallback
    url_id = st.query_params.get("id")
    if url_id:
        st.session_state["selected_imdb_key"] = url_id
        return str(url_id).strip()

    raw = st.session_state.get("selected_imdb_key")
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def _format_note(value) -> str:
    try:
        return f"{float(value):.2f}"
    except Exception:
        return "N/A"


def _source_label(page_path: str | None) -> str:
    if not page_path:
        return "Retour"
    if "Home" in page_path:
        return t("home_title")
    if "1_Par_genre" in page_path:
        return t("genre_title")
    if "2_Mes_favoris" in page_path:
        return t("favorites_title")
    if "3_Recommandations" in page_path:
        return t("recos_title")
    return "Retour"


def _inject_film_styles():
    st.markdown(
        """
        <style>
        [class*="st-key-wf_bc_link_"]{ overflow:hidden; }
        [class*="st-key-wf_bc_link_"] button{
          background:transparent !important;
          border:0 !important;
          box-shadow:none !important;
          border-radius:0 !important;
          padding:0 !important;
          min-height:0 !important;
          min-width:0 !important;
          max-width:100% !important;
          overflow:hidden !important;
          text-overflow:ellipsis !important;
          white-space:nowrap !important;
          color:var(--muted) !important;
          font-weight:600 !important;
          text-decoration:none !important;
        }
        [class*="st-key-wf_bc_link_"] button:focus,
        [class*="st-key-wf_bc_link_"] button:focus-visible{
            outline:none !important;
            box-shadow:none !important;
        }
        [class*="st-key-wf_bc_link_"] button:hover{
          color:var(--text) !important;
          text-decoration:underline !important;
        }

        /* Film page: heart button (match card hearts) */
        [class*="st-key-wf_film_fav_"]{ overflow: visible; }
        [class*="st-key-wf_film_fav_"] button{
          border: none !important;
          background: transparent !important;
          box-shadow: none !important;
          padding: 0 !important;
          min-height: 0 !important;
          opacity: 1 !important;
          color: var(--danger) !important;
          -webkit-text-fill-color: var(--danger) !important;
          fill: var(--danger) !important;
          font-size: 48px !important;
          font-weight: 400 !important;
          line-height: 1 !important;
          margin: 0 !important;
          text-shadow: 0 4px 10px rgba(0,0,0,0.8) !important;
          transform: scale(1.2) !important;
          transform-origin: center center !important;
          width: auto !important;
          height: auto !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
        }
        [class*="st-key-wf_film_fav_"] button:hover{
          background: transparent !important;
          transform: scale(1.3) !important;
          transition: transform 0.2s ease !important;
        }
        html body [class*="st-key-wf_film_fav_"] button p,
        html body [class*="st-key-wf_film_fav_"] button span,
        html body [class*="st-key-wf_film_fav_"] button div,
        html body [class*="st-key-wf_film_fav_"] button *{
          color: var(--danger) !important;
          -webkit-text-fill-color: var(--danger) !important;
          fill: var(--danger) !important;
          font-size: inherit !important;
          font-weight: inherit !important;
          line-height: inherit !important;
          margin: 0 !important;
          padding: 0 !important;
          text-shadow: inherit !important;
          transform: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    common_page_setup(page_title="Film", page_icon="🎬")
    _inject_film_styles()

    source_page = st.session_state.get("selected_source_page")
    back_page = source_page or "Home.py"

    df = load_movies()
    render_global_search(df, source_page=back_page, target_page=None)

    imdb_key = _get_selected_imdb_key()
    if not imdb_key:
        st.error(t("search_no_result"))
        if st.button("Retour"):
            st.switch_page("Home.py")
        return

    # Ensure ID is in URL (persistence)
    if st.query_params.get("id") != imdb_key:
        st.query_params["id"] = imdb_key

    if "imdb_key" not in df.columns:
        st.error("Dataset Error: imdb_key missing.")
        if st.button("Retour"):
            st.switch_page("Home.py")
        return

    movie = df[df["imdb_key"].astype(str) == imdb_key]
    if movie.empty:
        st.error(t("search_no_result"))
        if st.button("Retour"):
            st.switch_page("Home.py")
        return

    row = movie.iloc[0]
    title = str(row.get("movie_title", "Film"))

    # Breadcrumb Layout
    left, right = st.columns([5, 1], vertical_alignment="center")
    with left:
        if source_page and source_page != "Home.py":
            c1, c2, c3 = st.columns(
                [1.2, 2.0, 9.8], gap="small", vertical_alignment="center")
            with c1:
                if st.button(f"{t('home_title')} >", key=f"wf_bc_link_home_{imdb_key}"):
                    st.switch_page("Home.py")
            with c2:
                if st.button(f"{_source_label(source_page)} >", key=f"wf_bc_link_src_{imdb_key}"):
                    st.switch_page(source_page)
            with c3:
                st.caption(title)
        else:
            c1, c2 = st.columns([1.2, 11.8], gap="small",
                                vertical_alignment="center")
            with c1:
                if st.button(f"{t('home_title')} >", key=f"wf_bc_link_home_{imdb_key}"):
                    st.switch_page("Home.py")
            with c2:
                st.caption(title)
    with right:
        if st.button("Retour", use_container_width=True):
            st.switch_page(back_page)

    col_poster, col_info = st.columns([1, 2], gap="large")

    # --- Col Poster ---
    with col_poster:
        poster = row.get("Poster", None)
        is_authenticated = st.session_state.get("is_authenticated", False)
        favorites = st.session_state.setdefault("favorites", set())
        liked = imdb_key in favorites
        fav_label = "♥" if liked else "♡"

        if pd.notna(poster) and str(poster).strip():
            st.image(str(poster), use_container_width=True)
        else:
            st.info("Pas d'affiche.")

        # Heart button removed (moved to info column)

        if not is_authenticated:
            st.caption(t("auth_required_favs"))

    # --- Col Info ---
    with col_info:
        # Heart centered above title
        fav_key = f"wf_film_fav_{imdb_key}"
        c_left, c_fav, c_right = st.columns([1, 1, 1])
        with c_fav:
            if st.button(
                fav_label,
                type="tertiary",
                disabled=not is_authenticated,
                help=(t("auth_required_favs") if not is_authenticated else None),
                key=fav_key,
                use_container_width=True,
            ):
                toggle_favorite(imdb_key)
                st.rerun()

        st.markdown(
            f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)

        if not is_authenticated:
            st.caption(t("auth_required_favs"))

        # Meta Data
        genre = row.get("genre_main", None)
        note = _format_note(row.get("score_global", None))
        director = row.get("director_name", None)
        duration = row.get("duration", None)

        actors = [row.get("actor_1_name"), row.get(
            "actor_2_name"), row.get("actor_3_name")]
        actors = [a for a in actors if pd.notna(a) and str(a).strip()]
        actors_str = ", ".join(map(str, actors)) if actors else "N/A"

        # Labels
        lbl_genre = t("genre_label")
        lbl_note = t("rating_label")
        lbl_dir = t("director_label")
        lbl_act = t("actors_label")
        lbl_dur = t("duration_label")
        unit_min = t("minutes")

        st.write(f"{lbl_genre} {genre}" if pd.notna(
            genre) else f"{lbl_genre} N/A")
        st.write(f"{lbl_note} {note}")
        st.write(f"{lbl_dir} {director}" if pd.notna(
            director) else f"{lbl_dir} N/A")
        st.write(f"{lbl_act} {actors_str}")
        st.write(f"{lbl_dur} {int(duration)} {unit_min}" if pd.notna(
            duration) else f"{lbl_dur} N/A")

        year = row.get("title_year", None)
        rating = row.get("content_rating", None)
        country = row.get("country_main", None) or row.get(
            "country_name", None)
        language = row.get("language", None)

        st.write(f"Annee : {int(year)}" if pd.notna(year) else "Annee : N/A")
        st.write(f"Classification : {rating}" if pd.notna(
            rating) else "Classification : N/A")
        st.write(f"Pays : {country}" if pd.notna(country) else "Pays : N/A")
        st.write(f"Langue : {language}" if pd.notna(
            language) else "Langue : N/A")

        imdb_link = row.get("movie_imdb_link", None)
        if pd.notna(imdb_link) and str(imdb_link).strip():
            st.link_button("Voir sur IMDb", str(imdb_link))

    st.markdown("---")
    st.subheader("Synopsis")
    plot = row.get("Plot", None)
    if pd.notna(plot) and str(plot).strip():
        st.write(str(plot))
    else:
        st.write("Synopsis indisponible.")

    st.markdown("---")
    st.subheader(t("similar_movies_title"))
    similar_ml = get_similar_movies(df, imdb_key, n=5)
    if similar_ml.empty:
        st.info(t("no_similar_movies"))
    else:
        render_movie_row(
            similar_ml.head(5),
            key=f"film_similar_ml_{imdb_key}",
            max_items=5,
            source_page=back_page,
            target_page=None,
        )

    if pd.notna(genre) and str(genre).strip():
        st.markdown("---")
        st.subheader("Plus dans ce genre")
        similar = df[(df["genre_main"] == genre) & (
            df["imdb_key"].astype(str) != imdb_key)].copy()
        sort_cols = [c for c in ["score_global", "popularity",
                                 "num_voted_users"] if c in similar.columns]
        if sort_cols:
            similar = similar.sort_values(
                sort_cols, ascending=[False] * len(sort_cols))
        render_movie_row(
            similar.head(5),
            key=f"film_similar_{imdb_key}",
            max_items=5,
            source_page=back_page,
            target_page=None,
        )


if __name__ == "__main__":
    main()
