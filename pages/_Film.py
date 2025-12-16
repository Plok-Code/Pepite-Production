import pandas as pd
import streamlit as st

from utils.auth import (
    init_auth_state,
    login_form,
    logout_button,
    show_flash_toast,
    sidebar_navigation,
    toggle_favorite,
)
from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.theme import apply_wildflix_theme
from utils.ui_components import inject_wildflix_styles, render_movie_row


def _format_note(value) -> str:
    try:
        return f"{float(value):.2f}"
    except Exception:
        return "N/A"


def _source_label(page: str | None) -> str:
    if not page:
        return "Retour"
    if page.endswith("Home.py"):
        return "Accueil"
    if page.endswith("pages/1_Par_genre.py"):
        return "Par genre"
    if page.endswith("pages/2_Votre_espace.py"):
        return "Votre espace"
    if page.endswith("pages/_Admin.py"):
        return "Admin"
    return "Retour"


def _get_selected_imdb_key() -> str | None:
    raw = st.session_state.get("selected_imdb_key")
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def main():
    st.set_page_config(page_title="Fiche film", page_icon="F", layout="wide")
    apply_wildflix_theme()
    init_auth_state()
    sidebar_navigation()
    login_form()
    logout_button()
    show_flash_toast()
    inject_wildflix_styles()

    source_page = st.session_state.get("selected_source_page")
    back_page = source_page or "Home.py"

    df = load_movies()
    render_global_search(df, source_page=back_page, target_page=None)

    imdb_key = _get_selected_imdb_key()
    if not imdb_key:
        st.error("Aucun film selectionne.")
        if st.button("Retour a l'accueil"):
            st.switch_page("Home.py")
        return

    if "imdb_key" not in df.columns:
        st.error("La colonne imdb_key est manquante dans le dataset.")
        if st.button("Retour a l'accueil"):
            st.switch_page("Home.py")
        return

    movie = df[df["imdb_key"].astype(str) == imdb_key]
    if movie.empty:
        st.error("Film introuvable.")
        if st.button("Retour a l'accueil"):
            st.switch_page("Home.py")
        return

    row = movie.iloc[0]
    title = str(row.get("movie_title", "Film"))

    source_page = st.session_state.get("selected_source_page")
    back_page = source_page or "Home.py"

    st.markdown(
        """
        <style>
        [class*="st-key-wf_bc_link_"] button{
          background:transparent !important;
          border:0 !important;
          box-shadow:none !important;
          border-radius:0 !important;
          padding:0 !important;
          min-height:0 !important;
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
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([5, 1], vertical_alignment="center")
    with left:
        if source_page and source_page != "Home.py":
            c1, c2, c3 = st.columns([0.35, 0.65, 12], gap="small", vertical_alignment="center")
            with c1:
                if st.button("Accueil ›", key=f"wf_bc_link_home_{imdb_key}"):
                    st.switch_page("Home.py")
            with c2:
                if st.button(f"{_source_label(source_page)} ›", key=f"wf_bc_link_src_{imdb_key}"):
                    st.switch_page(source_page)
            with c3:
                st.caption(title)
        else:
            c1, c2 = st.columns([0.35, 13], gap="small", vertical_alignment="center")
            with c1:
                if st.button("Accueil ›", key=f"wf_bc_link_home_{imdb_key}"):
                    st.switch_page("Home.py")
            with c2:
                st.caption(title)
    with right:
        if st.button("Retour", use_container_width=True):
            st.switch_page(back_page)

    col_poster, col_info = st.columns([1, 2], gap="large")
    with col_poster:
        poster = row.get("Poster", None)
        is_authenticated = st.session_state.get("is_authenticated", False)
        favorites = st.session_state.setdefault("favorites", set())
        liked = imdb_key in favorites
        fav_label = "♥" if liked else "♡"

        with st.container(key=f"wf_film_poster_wrap_{imdb_key}"):
            if pd.notna(poster) and str(poster).strip():
                st.image(str(poster), use_container_width=True)
            else:
                st.info("Pas d'affiche.")

            fav_key = f"wf_film_fav_{imdb_key}"
            if st.button(
                fav_label,
                type="tertiary",
                disabled=not is_authenticated,
                help=("Connectez-vous pour ajouter aux favoris." if not is_authenticated else None),
                key=fav_key,
            ):
                toggle_favorite(imdb_key)
                st.rerun()
        if liked:
            st.markdown(
                f"<style>[class*=\"st-key-{fav_key}\"] button{{color:var(--danger) !important;border-color:rgba(255,59,59,0.55) !important;}}</style>",
                unsafe_allow_html=True,
            )

    with col_info:
        st.markdown(f"# {title}")

        genre = row.get("genre_main", None)
        note = _format_note(row.get("score_global", None))
        director = row.get("director_name", None)
        duration = row.get("duration", None)

        actors = [row.get("actor_1_name"), row.get("actor_2_name"), row.get("actor_3_name")]
        actors = [a for a in actors if pd.notna(a) and str(a).strip()]
        actors_str = ", ".join(map(str, actors)) if actors else "N/A"

        st.write(f"Genre principal : {genre}" if pd.notna(genre) else "Genre principal : N/A")
        st.write(f"Note : {note}")
        st.write(f"Realisateur : {director}" if pd.notna(director) else "Realisateur : N/A")
        st.write(f"Acteurs : {actors_str}")
        st.write(f"Duree : {int(duration)} min" if pd.notna(duration) else "Duree : N/A")

        year = row.get("title_year", None)
        rating = row.get("content_rating", None)
        country = row.get("country_main", None) or row.get("country_name", None)
        language = row.get("language", None)

        st.write(f"Annee : {int(year)}" if pd.notna(year) else "Annee : N/A")
        st.write(f"Classification : {rating}" if pd.notna(rating) else "Classification : N/A")
        st.write(f"Pays : {country}" if pd.notna(country) else "Pays : N/A")
        st.write(f"Langue : {language}" if pd.notna(language) else "Langue : N/A")

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

    if pd.notna(genre) and str(genre).strip():
        st.markdown("---")
        st.subheader("Plus dans ce genre")
        similar = df[(df["genre_main"] == genre) & (df["imdb_key"].astype(str) != imdb_key)].copy()
        sort_cols = [c for c in ["score_global", "popularity", "num_voted_users"] if c in similar.columns]
        if sort_cols:
            similar = similar.sort_values(sort_cols, ascending=[False] * len(sort_cols))
        render_movie_row(
            similar.head(5),
            key=f"film_similar_{imdb_key}",
            max_items=5,
            source_page=back_page,
            target_page=None,
        )


if __name__ == "__main__":
    main()
