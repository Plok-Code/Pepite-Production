import streamlit as st
from utils.auth import (
    init_auth_state,
    login_form,
    logout_button,
    show_flash_toast,
    sidebar_navigation,
)
from utils.theme import apply_wildflix_theme
from utils.i18n import render_sidebar_flags


def common_page_setup(page_title: str, page_icon: str = "🎬", layout: str = "wide"):
    """
    Handles standard page configuration and initialization steps.
    """
    st.set_page_config(page_title=page_title,
                       page_icon=page_icon, layout=layout)

    apply_wildflix_theme()
    # Note: inject_wildflix_styles from ui_components is no longer needed
    # as apply_wildflix_theme now handles it.

    init_auth_state()

    sidebar_navigation()
    login_form()
    logout_button()
    render_sidebar_flags()

    show_flash_toast()
