import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

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
from utils.settings import get_recommender_model, set_recommender_model
from utils.ui_components import render_movie_row, section_title
from services.recommendation_service import get_recommender_info


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
            gender_raw = st.multiselect(
                t("admin_gender_filter"),
                options=["male", "female", "other", "unknown"],
                default=["male", "female", "other", "unknown"],
                format_func=lambda v: (
                    t("admin_unknown") if v == "unknown" else t(f"gender_{v}")
                ),
                key="wf_admin_gender",
            )

        with c3:
            in_creuse_raw = st.multiselect(
                t("admin_in_creuse_filter"),
                options=["yes", "no", "unknown"],
                default=["yes", "no", "unknown"],
                format_func=lambda v: (
                    t("admin_unknown") if v == "unknown" else t("yes") if v == "yes" else t("no")
                ),
                key="wf_admin_creuse",
            )

        with c4:
            cinema_raw = st.multiselect(
                t("admin_cinema_filter"),
                options=["yes", "no", "unknown"],
                default=["yes", "no", "unknown"],
                format_func=lambda v: (
                    t("admin_unknown") if v == "unknown" else t("yes") if v == "yes" else t("no")
                ),
                key="wf_admin_cinema",
            )

    return {
        "age_range": age_range,
        "include_unknown_age": include_unknown_age,
        "gender": gender_raw,
        "in_creuse": in_creuse_raw,
        "cinema_last_12m": cinema_raw,
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

    tab_home, tab_py, tab_bi, tab_settings = st.tabs(
        [t("admin_home_tab"), "Dashboard Python", "Dashboard Power BI", t("admin_settings_tab")]
    )

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
            from utils.python_kpis import build_kpi_figure

            movies = movies_df.copy()
            if "imdb_key" in movies.columns:
                movies["imdb_key"] = movies["imdb_key"].astype(str)

            merged = filtered_favs.merge(
                movies, on="imdb_key", how="left").dropna(subset=["movie_title"])

            st.subheader("KPIs (Python)")
            kpi_options = ["kpi_prefs", "kpi_1", "kpi_3", "kpi_4", "kpi_5", "kpi_6"]
            current_kpi = st.session_state.get("wf_admin_python_kpi")
            if current_kpi not in kpi_options:
                st.session_state["wf_admin_python_kpi"] = kpi_options[0]

            kpi_id = st.selectbox(
                "KPI",
                options=kpi_options,
                format_func=lambda v: {
                    "kpi_prefs": "Préférence User du site",
                    "kpi_1": "Réalisateurs",
                    "kpi_3": "Acteurs",
                    "kpi_4": "Genres & décennie",
                    "kpi_5": "Durée",
                    "kpi_6": "Classification âge",
                }.get(v, str(v)),
                key="wf_admin_python_kpi",
            )

            fig = build_kpi_figure(kpi_id, merged)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with tab_bi:
        section_title("Dashboard Power BI")
        from utils.powerbi import get_powerbi_iframe_url

        simple_url = get_powerbi_iframe_url()
        if not simple_url:
            st.warning("Power BI n'est pas configuré.")
            st.code(
                "[powerbi]\nSIMPLE_URL = \"https://app.powerbi.com/reportEmbed?...\"",
                language="toml",
            )
        else:
            st.info("Affichage Power BI (nécessite connexion Microsoft).")
            components.iframe(simple_url, height=650, scrolling=True)
            st.caption(t("admin_powerbi_note"))

    with tab_settings:
        section_title(t("admin_settings_tab"))

        current_model = get_recommender_model()
        options = ["cosine", "euclidean", "manhattan"]
        selected = st.selectbox(
            t("admin_reco_model_label"),
            options=options,
            index=(options.index(current_model) if current_model in options else 0),
            format_func=lambda v: (
                "KNN cosine" if v == "cosine" else "KNN euclidean" if v == "euclidean" else "KNN manhattan"
            ),
            help=t("admin_reco_model_help"),
            key="wf_admin_reco_model",
        )

        c1, c2 = st.columns([1, 3], vertical_alignment="center")
        with c1:
            if st.button(t("save_button"), type="primary", key="wf_admin_reco_save"):
                set_recommender_model(selected)
                st.success(t("admin_settings_saved"))
                st.rerun()
        with c2:
            backend, reason = get_recommender_info()
            mode = "ML" if backend == "knn_cosine" else "Fallback"
            details = (reason or "").strip()
            if details:
                st.caption(t("admin_reco_backend_status", mode, details))
            else:
                st.caption(f"Moteur : {mode}")


if __name__ == "__main__":
    main()
