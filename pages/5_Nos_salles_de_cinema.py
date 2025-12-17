import streamlit as st

from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.i18n import t
from utils.layout import common_page_setup
from utils.ui_components import section_title


def main():
    common_page_setup(page_title=t("cinemas_title"))

    df = load_movies()
    render_global_search(df, source_page="pages/5_Nos_salles_de_cinema.py")

    st.title(t("cinemas_title"))

    section_title(t("cinemas_context_title"))
    st.write(t("cinemas_context_body"))

    st.markdown("---")
    section_title(t("cinemas_construction_title"))
    st.info(t("cinemas_construction_body"))

    st.markdown("---")
    section_title(t("contact_title"))
    st.caption(t("contact_disclaimer"))
    with st.form("wf_contact_form"):
        st.text_input(t("contact_name_label"), key="wf_contact_name")
        st.text_input(t("email_label"), key="wf_contact_email")
        st.text_area(t("contact_message_label"), key="wf_contact_message")
        if st.form_submit_button(t("contact_send"), type="primary"):
            st.success(t("contact_sent"))


if __name__ == "__main__":
    main()

