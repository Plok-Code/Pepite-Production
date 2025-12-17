import os

import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from utils.admin_analytics import (
    apply_user_filters,
    favorites_for_users,
    load_favorites_df,
    load_users_df,
)
from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.i18n import t
from utils.layout import common_page_setup
from utils.ui_components import render_movie_row, section_title


def _get_powerbi_embed_url() -> str | None:
    # Hardcoded for testing as requested
    return "https://app.powerbi.com/reportEmbed?reportId=76c1a151-a7e7-48a8-9210-d53ebec79519&autoAuth=true&ctid=a2e466aa-4f86-4545-b5b8-97da7c8febf3"

    # url = str(os.getenv("POWERBI_EMBED_URL", "")).strip()
    # if url:
    #     return url

    # try:
    #     raw = st.secrets.get("POWERBI_EMBED_URL") or st.secrets.get("powerbi_embed_url")
    # except StreamlitSecretNotFoundError:
    #     return None

    # if raw is None:
    #     return None
    # return str(raw).strip() or None


def _render_admin_filters() -> dict:
    with st.container(border=True):
        section_title(t("admin_filters_title"))

        c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1.5])

        with c1:
            age_range = st.slider(t("admin_age_filter"),
                                  0, 120, (0, 120), key="wf_admin_age")
            include_unknown_age = st.checkbox(
                t("admin_include_unknown"),
                value=True,
                key="wf_admin_age_unknown",
            )

        with c2:
            gender_raw = st.selectbox(
                t("admin_gender_filter"),
                options=["all", "male", "female", "other", "unknown"],
                format_func=lambda v: (
                    t("admin_all")
                    if v == "all"
                    else t("admin_unknown")
                    if v == "unknown"
                    else t(f"gender_{v}")
                ),
                key="wf_admin_gender",
            )

        with c3:
            in_creuse_raw = st.selectbox(
                t("admin_in_creuse_filter"),
                options=["all", "yes", "no", "unknown"],
                format_func=lambda v: (
                    t("admin_all")
                    if v == "all"
                    else t("admin_unknown")
                    if v == "unknown"
                    else t("yes")
                    if v == "yes"
                    else t("no")
                ),
                key="wf_admin_creuse",
            )

        with c4:
            cinema_raw = st.selectbox(
                t("admin_cinema_filter"),
                options=["all", "yes", "no", "unknown"],
                format_func=lambda v: (
                    t("admin_all")
                    if v == "all"
                    else t("admin_unknown")
                    if v == "unknown"
                    else t("yes")
                    if v == "yes"
                    else t("no")
                ),
                key="wf_admin_cinema",
            )

    gender = None if gender_raw == "all" else gender_raw
    in_creuse = (
        None
        if in_creuse_raw == "all"
        else "unknown"
        if in_creuse_raw == "unknown"
        else True
        if in_creuse_raw == "yes"
        else False
    )
    cinema_last_12m = (
        None
        if cinema_raw == "all"
        else "unknown"
        if cinema_raw == "unknown"
        else True
        if cinema_raw == "yes"
        else False
    )

    return {
        "age_range": age_range,
        "include_unknown_age": include_unknown_age,
        "gender": gender,
        "in_creuse": in_creuse,
        "cinema_last_12m": cinema_last_12m,
    }


def main():
    common_page_setup(page_title=t("admin_title"), page_icon="🛠️")

    if st.session_state.get("role") != "admin":
        st.error(t("admin_access_denied"))
        st.stop()

    movies_df = load_movies()
    render_global_search(movies_df, source_page="pages/_Admin.py")

    st.title(t("admin_title"))

    users_df = load_users_df()
    favorites_df = load_favorites_df()

    filters = _render_admin_filters()
    filtered_users = apply_user_filters(users_df, **filters)
    filtered_favs = favorites_for_users(favorites_df, filtered_users)

    tab_home, tab_py, tab_bi = st.tabs(
        [t("admin_home_tab"), "Dashboard Python", "Dashboard Power BI"])

    with tab_home:
        section_title(t("admin_top_liked"), t("admin_top_liked_desc"))

        total_users = int(filtered_users["email"].nunique(
        )) if not filtered_users.empty else 0
        total_likes = int(len(filtered_favs)) if not filtered_favs.empty else 0
        unique_movies = int(
            filtered_favs["imdb_key"].nunique()) if not filtered_favs.empty else 0

        m1, m2, m3 = st.columns(3)
        m1.metric(t("admin_selected_users"), total_users)
        m2.metric(t("admin_total_likes"), total_likes)
        m3.metric(t("admin_unique_movies"), unique_movies)

        if filtered_favs.empty:
            st.info(t("admin_no_likes"))
        else:
            top_n = st.slider(t("admin_top_n"), 5, 50, 10, key="wf_admin_topn")
            counts = (
                filtered_favs.groupby("imdb_key")
                .size()
                .reset_index(name="likes")
                .sort_values("likes", ascending=False)
                .head(int(top_n))
            )

            movies = movies_df.copy()
            if "imdb_key" in movies.columns:
                movies["imdb_key"] = movies["imdb_key"].astype(str)

            top_movies = counts.merge(movies, on="imdb_key", how="left").dropna(
                subset=["movie_title"])
            for start in range(0, len(top_movies), 5):
                render_movie_row(
                    top_movies.iloc[start: start + 5],
                    key=f"admin_top_{start}",
                    max_items=5,
                    source_page="pages/_Admin.py",
                )

    with tab_py:
        section_title(t("admin_python_tab"))

        if filtered_favs.empty:
            st.info(t("admin_no_likes"))
        else:
            movies = movies_df.copy()
            if "imdb_key" in movies.columns:
                movies["imdb_key"] = movies["imdb_key"].astype(str)

            merged = filtered_favs.merge(
                movies, on="imdb_key", how="left").dropna(subset=["movie_title"])

            c1, c2 = st.columns(2)
            with c1:
                genre_counts = (
                    merged.groupby("genre_main")
                    .size()
                    .reset_index(name="likes")
                    .sort_values("likes", ascending=False)
                    .head(12)
                )
                if not genre_counts.empty:
                    st.subheader(t("admin_likes_by_genre"))
                    chart_df = genre_counts.set_index("genre_main")[["likes"]]
                    st.bar_chart(chart_df, height=420)

            with c2:
                lang_counts = (
                    merged.groupby("language")
                    .size()
                    .reset_index(name="likes")
                    .sort_values("likes", ascending=False)
                    .head(12)
                )
                if not lang_counts.empty:
                    st.subheader(t("admin_likes_by_language"))
                    chart_df = lang_counts.set_index("language")[["likes"]]
                    st.bar_chart(chart_df, height=420)

    with tab_bi:
        section_title("Dashboard Power BI")

        # Check if secrets are configured
        from utils.powerbi import get_powerbi_embed_info
        import streamlit.components.v1 as components
        import json

        embed_data, err = get_powerbi_embed_info()

        if err:
            # Fallback to the old simple iframe if auth fails or not configured
            st.warning(f"Mode API désactivé ou erreur : {err}")
            st.info("Affichage en mode 'Utilisateur' (Nécessite connexion Microsoft)")

            # Use the "simple" URL (User Owns Data)
            # We can keep the hardcoded for now or use the one from secrets fallback
            simple_url = "https://app.powerbi.com/reportEmbed?reportId=76c1a151-a7e7-48a8-9210-d53ebec79519&autoAuth=true&ctid=a2e466aa-4f86-4545-b5b8-97da7c8febf3"
            st.markdown(
                f"""
                <iframe
                    width="100%" height="650"
                    src="{simple_url}"
                    frameborder="0" allowFullScreen="true">
                </iframe>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Render using JS SDK for seamless "App Owns Data" experience
            st.success("Mode API Connecté (Service Principal)")

            # HTML/JS for Power BI Client
            # Uses public CDN for powerbi-client
            html_code = f"""
            <div id="embedContainer" style="height: 650px; width: 100%;"></div>
            <script src="https://microsoft.github.io/PowerBI-JavaScript/demo/node_modules/powerbi-client/dist/powerbi.js"></script>
            <script>
                var models = window['powerbi-client'].models;
                var config = {{
                    type: 'report',
                    tokenType: models.TokenType.Embed,
                    accessToken: "{embed_data['accessToken']}",
                    embedUrl: "{embed_data['embedUrl']}",
                    id: "{embed_data['id']}",
                    permissions: models.Permissions.All,
                    settings: {{
                        filterPaneEnabled: false,
                        navContentPaneEnabled: true
                    }}
                }};
                
                var embedContainer = document.getElementById('embedContainer');
                var report = powerbi.embed(embedContainer, config);
            </script>
            """
            components.html(html_code, height=650)


if __name__ == "__main__":
    main()
