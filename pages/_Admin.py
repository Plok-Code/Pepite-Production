import streamlit as st
from utils.data_loader import load_movies
from utils.auth import init_auth_state, login_form, logout_button, show_flash_toast, sidebar_navigation
from utils.header import render_global_search
from utils.theme import apply_wildflix_theme
from utils.ui_components import section_title


def main():
    st.set_page_config(page_title="Admin", page_icon="A", layout="wide")
    apply_wildflix_theme()
    init_auth_state()
    sidebar_navigation()
    login_form()
    logout_button()
    show_flash_toast()

    if st.session_state.role != "admin":
        st.error("Acces reserve aux administrateurs.")
        st.stop()

    df = load_movies()
    render_global_search(df, source_page="pages/_Admin.py")

    st.title("Espace admin - Dashboards")

    col1, col2 = st.columns(2)

    with col1:
        section_title("Dashboard Python")
        st.info("Placeholders pour les graphiques Streamlit/Plotly.")
        import plotly.express as px
        import plotly.io as pio

        pio.templates.default = "plotly_dark"

        top_directors = (
            df.groupby("director_name")["score_global"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        fig = px.bar(
            top_directors,
            x="director_name",
            y="score_global",
            title="Top 10 realisateurs",
            color_discrete_sequence=["#FFB020"],
        )
        fig.update_layout(
            paper_bgcolor="#0B0F17",
            plot_bgcolor="#141C2B",
            font=dict(color="#EAF0FF", family="Inter"),
            title_font=dict(color="#EAF0FF", size=16),
        )
        fig.update_xaxes(color="#A7B3CC", gridcolor="#25324A")
        fig.update_yaxes(color="#A7B3CC", gridcolor="#25324A")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Dashboard Power BI")
        st.info("Integrez ici une iframe ou un lien securise vers Power BI.")

        powerbi_url = st.text_input("URL du rapport Power BI :")
        if powerbi_url:
            st.markdown(
                f"""
                <iframe
                    width="100%" height="500"
                    src="{powerbi_url}"
                    frameborder="0" allowFullScreen="true">
                </iframe>
                """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
