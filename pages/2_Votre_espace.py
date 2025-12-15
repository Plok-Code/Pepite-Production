import streamlit as st

from utils.auth import (
    change_password,
    init_auth_state,
    login_form,
    logout_button,
    update_profile,
    show_flash_toast,
    sidebar_navigation,
)
from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.theme import apply_wildflix_theme
from utils.ui_components import inject_wildflix_styles, render_movie_row, section_title


def get_recommendations_from_favorites(df, favorites: set[str], n: int = 10):
    if not favorites or "imdb_key" not in df.columns:
        return df.head(0)

    fav_df = df[df["imdb_key"].astype(str).isin(set(map(str, favorites)))].copy()
    if fav_df.empty or "genre_main" not in fav_df.columns:
        return df.head(0)

    genres = [g for g in fav_df["genre_main"].dropna().tolist() if str(g).strip()]
    if not genres:
        return df.head(0)

    candidates = df[
        (df["genre_main"].isin(genres)) & (~df["imdb_key"].astype(str).isin(set(map(str, favorites))))
    ].copy()

    sort_cols = [c for c in ["score_global", "popularity", "num_voted_users"] if c in candidates.columns]
    if sort_cols:
        candidates = candidates.sort_values(sort_cols, ascending=[False] * len(sort_cols))

    if "imdb_key" in candidates.columns:
        candidates = candidates.drop_duplicates(subset=["imdb_key"], keep="first")
    return candidates.head(n)


def main():
    st.set_page_config(page_title="Votre espace", page_icon="U", layout="wide")
    apply_wildflix_theme()
    init_auth_state()
    sidebar_navigation()
    login_form()
    logout_button()
    show_flash_toast()
    inject_wildflix_styles()

    if not st.session_state.get("is_authenticated", False):
        st.error("Vous devez etre connecte pour acceder a votre espace.")
        st.stop()

    df = load_movies()
    render_global_search(df, source_page="pages/2_Votre_espace.py")

    st.title("Votre espace")
    tabs = st.tabs(["Profil", "Vos favoris", "Recommandations"])

    favorites = st.session_state.setdefault("favorites", set())

    with tabs[0]:
        section_title("Profil", "Modifiez vos informations.")

        with st.form("wf_profile_form"):
            pseudo = st.text_input("Pseudo", value=st.session_state.get("pseudo") or "")
            email = st.text_input("Email", value=st.session_state.get("user_email") or "")
            submitted = st.form_submit_button("Enregistrer", type="primary")
            if submitted:
                ok, message = update_profile(new_email=email, new_pseudo=pseudo)
                if ok:
                    st.session_state["flash_message"] = message
                    st.rerun()
                st.error(message)

        st.markdown("---")
        section_title("Mot de passe", "Changez votre mot de passe.")
        with st.form("wf_password_form"):
            current_password = st.text_input("Mot de passe actuel", type="password")
            new_password = st.text_input("Nouveau mot de passe", type="password")
            confirm_password = st.text_input("Confirmer le nouveau mot de passe", type="password")
            submitted = st.form_submit_button("Mettre a jour", type="secondary")
            if submitted:
                if new_password != confirm_password:
                    st.error("Les mots de passe ne correspondent pas.")
                else:
                    ok, message = change_password(current_password, new_password)
                    if ok:
                        st.session_state["flash_message"] = message
                        st.rerun()
                    st.error(message)

    with tabs[1]:
        section_title("Vos favoris", "Films que vous avez aimes.")

        if not favorites:
            st.info("Vous n'avez pas encore de favoris.")
        else:
            fav_df = df[df["imdb_key"].astype(str).isin(set(map(str, favorites)))].copy()
            sort_cols = [c for c in ["score_global", "popularity", "num_voted_users"] if c in fav_df.columns]
            if sort_cols:
                fav_df = fav_df.sort_values(sort_cols, ascending=[False] * len(sort_cols))

            fav_df = fav_df.reset_index(drop=True)
            for start in range(0, len(fav_df), 5):
                render_movie_row(
                    fav_df.iloc[start : start + 5],
                    key=f"user_favs_{start}",
                    max_items=5,
                    source_page="pages/2_Votre_espace.py",
                )

    with tabs[2]:
        section_title("Recommandations", "Basees sur vos favoris.")

        if not favorites:
            st.info("Pour commencer, ajoutez des films a vos favoris (bouton coeur).")
        else:
            recos = get_recommendations_from_favorites(df, favorites, n=10)
            if recos.empty:
                st.info("Ajoutez quelques favoris pour debloquer des recommandations.")
            else:
                for start in range(0, len(recos), 5):
                    render_movie_row(
                        recos.iloc[start : start + 5],
                        key=f"user_recos_{start}",
                        max_items=5,
                        source_page="pages/2_Votre_espace.py",
                    )


if __name__ == "__main__":
    main()
