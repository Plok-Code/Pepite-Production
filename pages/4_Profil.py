from datetime import date

import streamlit as st

from utils.auth import (
    change_password,
    update_profile,
)
from utils.user_repo import get_user
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

            email_for_lookup = st.session_state.get("user_email")
            try:
                current_user = get_user(str(email_for_lookup)) if email_for_lookup else None
            except Exception:
                current_user = None

            dob_default = None
            dob_str = (current_user or {}).get("date_of_birth")
            if dob_str:
                try:
                    dob_default = date.fromisoformat(str(dob_str)[:10])
                except Exception:
                    dob_default = None

            current_gender = (current_user or {}).get("gender")
            current_in_creuse = (current_user or {}).get("in_creuse")
            current_cinema_last_12m = (current_user or {}).get("cinema_last_12m")

            with st.form("wf_profile_form"):
                current_pseudo = st.session_state.get("pseudo") or ""
                current_email = st.session_state.get("user_email") or ""

                pseudo = st.text_input(t("pseudo_label"), value=current_pseudo)
                email = st.text_input(t("email_label"), value=current_email)

                date_of_birth = st.date_input(
                    t("dob_label"),
                    value=dob_default,
                    format="YYYY-MM-DD",
                    key="wf_profile_dob",
                )

                gender_options = ["", "male", "female", "other"]
                gender_choice = st.selectbox(
                    t("gender_label"),
                    options=gender_options,
                    index=(gender_options.index(current_gender) if current_gender in gender_options else 0),
                    format_func=lambda v: t("optional_placeholder") if v == "" else t(f"gender_{v}"),
                    key="wf_profile_gender",
                )
                gender = None if gender_choice == "" else gender_choice

                yes_no_options = ["", "yes", "no"]
                in_creuse_choice = st.selectbox(
                    t("in_creuse_label"),
                    options=yes_no_options,
                    index=(
                        1
                        if current_in_creuse is True
                        else 2
                        if current_in_creuse is False
                        else 0
                    ),
                    format_func=lambda v: (
                        t("optional_placeholder")
                        if v == ""
                        else t("yes")
                        if v == "yes"
                        else t("no")
                    ),
                    key="wf_profile_in_creuse",
                )
                in_creuse = None if in_creuse_choice == "" else in_creuse_choice == "yes"

                cinema_choice = st.selectbox(
                    t("cinema_12m_label"),
                    options=yes_no_options,
                    index=(
                        1
                        if current_cinema_last_12m is True
                        else 2
                        if current_cinema_last_12m is False
                        else 0
                    ),
                    format_func=lambda v: (
                        t("optional_placeholder")
                        if v == ""
                        else t("yes")
                        if v == "yes"
                        else t("no")
                    ),
                    key="wf_profile_cinema_12m",
                )
                cinema_last_12m = None if cinema_choice == "" else cinema_choice == "yes"

                submitted = st.form_submit_button(
                    t("save_button"), type="primary")
                if submitted:
                    ok, message = update_profile(
                        new_email=email,
                        new_pseudo=pseudo,
                        date_of_birth=(date_of_birth.isoformat() if date_of_birth else None),
                        gender=gender,
                        in_creuse=in_creuse,
                        cinema_last_12m=cinema_last_12m,
                    )
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
