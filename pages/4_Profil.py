import streamlit as st

from utils.auth import (
    change_password,
    update_profile,
)
from utils.data_loader import load_movies
from utils.header import render_global_search
from utils.ui_components import section_title
from utils.i18n import t
from utils.layout import common_page_setup


def main():
    common_page_setup(page_title=t("profile_title"), page_icon="⚙️")

    if not st.session_state.get("is_authenticated", False):
        st.error(t("auth_required_profile"))
        st.stop()

    df = load_movies()
    render_global_search(df, source_page="pages/4_Profil.py")

    st.title(t("profile_title"))

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            section_title(t("profile_info_section"), t("profile_info_desc"))
            with st.form("wf_profile_form"):
                current_pseudo = st.session_state.get("pseudo") or ""
                current_email = st.session_state.get("user_email") or ""

                pseudo = st.text_input(t("pseudo_label"), value=current_pseudo)
                email = st.text_input(t("email_label"), value=current_email)

                submitted = st.form_submit_button(
                    t("save_button"), type="primary")
                if submitted:
                    ok, message = update_profile(
                        new_email=email, new_pseudo=pseudo)
                    if ok:
                        st.session_state["flash_message"] = message
                        st.rerun()
                    st.error(message)

    with col2:
        with st.container(border=True):
            section_title(t("profile_security_section"),
                          t("profile_security_desc"))
            with st.form("wf_password_form"):
                current_password = st.text_input(
                    t("current_password"), type="password")
                new_password = st.text_input(
                    t("new_password"), type="password")
                confirm_password = st.text_input(
                    t("confirm_new_password"), type="password")

                submitted = st.form_submit_button(
                    t("update_button"), type="secondary")
                if submitted:
                    if new_password != confirm_password:
                        st.error(t("passwords_mismatch"))
                    else:
                        ok, message = change_password(
                            current_password, new_password)
                        if ok:
                            st.session_state["flash_message"] = message
                            st.rerun()
                        st.error(message)


if __name__ == "__main__":
    main()
