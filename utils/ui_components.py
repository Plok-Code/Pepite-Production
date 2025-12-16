import pandas as pd
import streamlit as st
from textwrap import dedent


def movie_card(row: pd.Series, show_add_fav: bool = False):
    col1, col2 = st.columns([1, 3])
    with col1:
        if pd.notna(row.get("Poster", None)):
            st.image(row["Poster"], width=200)
        else:
            st.write("Pas d'affiche")
    with col2:
        title_year = int(row["title_year"]) if not pd.isna(row["title_year"]) else "N/A"
        st.markdown(f"### {row['movie_title']} ({title_year})")
        st.write(f"Genre principal : {row.get('genre_main', 'N/A')}")
        st.write(f"Score global : {row.get('score_global', 'N/A')}")
        st.write(f"IMDb : {row.get('imdb_score', 'N/A')}")
        st.write(f"Popularite : {row.get('popularity', 'N/A')}")
        if show_add_fav:
            if st.button("Ajouter aux favoris", key=f"fav_{row['imdb_key']}"):
                st.session_state.favorites.add(row["imdb_key"])
                st.success("Ajoute aux favoris")


def movie_tile(row: pd.Series, show_add_fav: bool = False, key_prefix: str = ""):
    title = row.get("movie_title", "N/A")
    genre = row.get("genre_main", "N/A")
    note = row.get("score_global", None)
    director = row.get("director_name", "N/A")
    duration = row.get("duration", None)

    actors = [row.get("actor_1_name"), row.get("actor_2_name"), row.get("actor_3_name")]
    actors = [a for a in actors if pd.notna(a) and str(a).strip()]

    st.markdown(f"**{title}**")
    st.write(f"Genre principal : {genre}" if pd.notna(genre) else "Genre principal : N/A")

    if pd.notna(note):
        st.write(f"Note : {float(note):.2f}")
    else:
        st.write("Note : N/A")

    st.write(f"Realisateur : {director}" if pd.notna(director) else "Realisateur : N/A")
    st.write(f"Acteurs : {', '.join(map(str, actors))}" if actors else "Acteurs : N/A")

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
    st.markdown(
        dedent(
            """
        <style>
        /* Masque le menu multipage par defaut (on utilise notre navigation custom). */
        [data-testid="stSidebarNav"] { display: none; }

        /* Active le scroll horizontal pour les rangées de films (container key prefix wf-scroll-...). */
        div[class*="st-key-wf-scroll-"] div[data-testid="stHorizontalBlock"] {
          overflow-x: auto;
          flex-wrap: nowrap;
          gap: 14px;
          padding-bottom: 8px;
        }
        div[class*="st-key-wf-scroll-"] div[data-testid="column"] {
          min-width: 240px;
        }

        /* Cartes films */
        div[class*="st-key-wf_card_"] {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          box-shadow: var(--shadow);
          padding: 12px;
        }

        /* Affiches cliquables (boutons Streamlit styles en poster). */
        div[class*="st-key-wf_poster_"] button {
          height: 340px;
          padding: 0;
          border-radius: 12px;
          background-size: contain;
          background-position: center;
          background-repeat: no-repeat;
          background-color: var(--surface);
          border: 1px solid var(--border);
          overflow: hidden;
        }
        div[class*="st-key-wf_poster_"] button > div {
          opacity: 0;
        }

        /* Bouton coeur superpose sur les posters (cartes). */
        div[class*="st-key-wf_poster_wrap_"]{ position: relative; }
        div[class*="st-key-wf_poster_wrap_"] div[class*="st-key-wf_fav_overlay_"]{
          position:absolute;
          top:10px;
          right:10px;
          z-index:20;
          width:44px;
          height:44px;
          display:flex;
          align-items:center;
          justify-content:center;
        }
        div[class*="st-key-wf_poster_wrap_"] div[class*="st-key-wf_fav_overlay_"] button{
          width:44px !important;
          height:44px !important;
          padding:0 !important;
          border-radius:999px !important;
          background:rgba(20,28,43,.72) !important;
          border:1px solid rgba(37,50,74,.95) !important;
          display:flex !important;
          align-items:center !important;
          justify-content:center !important;
          font-size:22px !important;
          line-height:1 !important;
          color:var(--text) !important;
        }

        /* Poster + coeur (page film). */
        div[class*="st-key-wf_film_poster_wrap_"]{ position: relative; }
        div[class*="st-key-wf_film_poster_wrap_"] div[class*="st-key-wf_film_fav_"]{
          position:absolute;
          top:12px;
          right:12px;
          z-index:20;
          width:48px;
          height:48px;
          display:flex;
          align-items:center;
          justify-content:center;
        }
        div[class*="st-key-wf_film_poster_wrap_"] div[class*="st-key-wf_film_fav_"] button{
          width:48px !important;
          height:48px !important;
          padding:0 !important;
          border-radius:999px !important;
          background:rgba(20,28,43,.72) !important;
          border:1px solid rgba(37,50,74,.95) !important;
          display:flex !important;
          align-items:center !important;
          justify-content:center !important;
          font-size:24px !important;
          line-height:1 !important;
          color:var(--text) !important;
        }
        div[class*="st-key-wf_film_poster_wrap_"] div[data-testid="stImage"] img{
          border-radius:12px;
          border:1px solid var(--border);
        }

        /* Titres des films plus lisibles dans les cartes. */
        div[class*="st-key-wf-scroll-"] button[data-testid="baseButton-secondary"] {
          font-weight: 700;
          text-align: left;
          white-space: normal;
        }
        </style>
        """
        ).strip(),
        unsafe_allow_html=True,
    )


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

    inject_wildflix_styles()

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
                imdb_key = str(imdb_key_raw) if pd.notna(imdb_key_raw) else None
                title = row.get("movie_title", "N/A")
                poster = row.get("Poster", None)

                liked = bool(imdb_key) and (imdb_key in favorites)
                fav_label = "♥" if liked else "♡"

                with st.container(border=True, key=f"wf_card_{key}_{i}_{imdb_key or 'na'}"):
                    def _open_movie():
                        st.session_state["selected_imdb_key"] = imdb_key
                        if source_page:
                            st.session_state["selected_source_page"] = source_page
                        if target_page:
                            st.switch_page(target_page)
                        else:
                            st.rerun()

                    poster_url = str(poster) if pd.notna(poster) and str(poster).strip() else None
                    poster_key = f"wf_poster_{key}_{i}_{imdb_key or 'na'}"
                    fav_button_key = f"wf_fav_overlay_{key}_{i}_{imdb_key or 'na'}"
                    with st.container(key=f"wf_poster_wrap_{key}_{i}_{imdb_key or 'na'}"):
                        if poster_url and imdb_key:
                            safe_url = poster_url.replace("'", "%27")
                            st.markdown(
                                f"<style>div[class*=\"st-key-{poster_key}\"] button {{ background-image: url('{safe_url}'); }}</style>",
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

                        if st.button(
                            fav_label,
                            key=fav_button_key,
                            type="tertiary",
                            disabled=not is_authenticated or not imdb_key,
                            help=(
                                "Connectez-vous pour ajouter aux favoris."
                                if not is_authenticated
                                else None
                            ),
                        ):
                            toggle_favorite(imdb_key)
                            st.rerun()
                        if liked:
                            st.markdown(
                                f"<style>div[class*=\"st-key-{fav_button_key}\"] button{{color:var(--danger) !important;border-color:rgba(255,59,59,0.55) !important;}}</style>",
                                unsafe_allow_html=True,
                            )

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
                    director = row.get("director_name", "N/A")
                    duration = row.get("duration", None)

                    actors = [row.get("actor_1_name"), row.get("actor_2_name"), row.get("actor_3_name")]
                    actors = [a for a in actors if pd.notna(a) and str(a).strip()]
                    actors_str = ", ".join(map(str, actors)) if actors else "N/A"

                    st.caption(f"Genre principal : {genre}")
                    st.caption(f"Note : {note}")
                    st.caption(f"Realisateur : {director}")
                    st.caption(f"Acteurs : {actors_str}")
                    if pd.notna(duration):
                        st.caption(f"Duree : {int(duration)} min")
                    else:
                        st.caption("Duree : N/A")


def section_title(title: str, subtitle: str | None = None):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)
