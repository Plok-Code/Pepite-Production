import streamlit as st
from utils.i18n import t, set_language, get_current_language

from utils.user_repo import (
    backend_name,
    create_user,
    get_user,
    save_favorites,
    update_profile as repo_update_profile,
    update_user_password,
    verify_user_password,
)
from utils.mysql_store import is_mysql_enabled, is_mysql_ready
import hmac
import hashlib
import base64
import time
import json

from utils.app_config import get_secret_key

# Secret key for signing tokens
SECRET_KEY = get_secret_key()


def generate_session_token(email: str) -> str:
    """Generates a signed token containing email and timestamp."""
    payload = {
        "email": email,
        "exp": time.time() + 7 * 24 * 3600  # 7 days expiration
    }
    payload_str = base64.urlsafe_b64encode(
        json.dumps(payload).encode()).decode().rstrip("=")
    signature = hmac.new(
        SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256
    ).hexdigest()
    return f"{payload_str}.{signature}"


def verify_session_token(token: str) -> str | None:
    """Verifies the token and returns the email if valid."""
    try:
        payload_str, signature = token.split(".")
        expected_signature = hmac.new(
            SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(signature, expected_signature):
            # Restore padding
            padding = 4 - (len(payload_str) % 4)
            if padding != 4:
                payload_str += "=" * padding

            payload = json.loads(
                base64.urlsafe_b64decode(payload_str).decode())
            if payload["exp"] > time.time():
                return payload["email"]
    except Exception:
        pass
    return None


def init_auth_state():
    if "is_authenticated" not in st.session_state:
        # Check for token in query params
        token = st.query_params.get("auth_token")
        email_from_token = None

        if token:
            print(f"DEBUG: Found auth_token in URL: {token[:10]}...")
            email_from_token = verify_session_token(token)
            print(f"DEBUG: Token verified email: {email_from_token}")

        if email_from_token:
            # Auto-login
            try:
                user = get_user(email_from_token)
                if user:
                    st.session_state.is_authenticated = True
                    st.session_state.user_email = email_from_token
                    st.session_state.user_id = user.get("id")
                    st.session_state.role = user.get("role") or "user"
                    st.session_state.pseudo = user.get(
                        "pseudo") or email_from_token.split("@")[0]
                    st.session_state.favorites = set(
                        map(str, user.get("favorites", [])))
                    st.session_state.flash_message = f"Bon retour, {st.session_state.pseudo} !"
                    return
            except Exception:
                pass

        st.session_state.is_authenticated = False
        st.session_state.user_email = None
        st.session_state.user_id = None
        st.session_state.role = "visitor"
        st.session_state.pseudo = None
        st.session_state.favorites = set()
        st.session_state.flash_message = None

    # If already authenticated (or just auto-logged in), ensure token is in URL
    if st.session_state.get("is_authenticated", False):
        current_token = st.query_params.get("auth_token")
        email = st.session_state.get("user_email")

        # If missing or we want to rotate/refresh it, set it.
        # For simplicity, if missing, generate and set.
        if not current_token and email:
            new_token = generate_session_token(email)
            st.query_params["auth_token"] = new_token


@st.dialog(t("login_tab"))
def login_dialog():
    # FORCE CSS injection directly inside the dialog to ensure it takes precedence
    st.markdown("""
        <style>
        div[data-testid="stDialog"] button[data-testid="baseButton-primary"] * {
            color: #0B0F17 !important;
            -webkit-text-fill-color: #0B0F17 !important;
            font-weight: 800 !important;
        }
        </style>
        """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs([t("login_tab"), t("signup_tab")])

    with tab_login:
        email = st.text_input(t("email_label"), key="wf_modal_login_email")
        password = st.text_input(
            t("password_label"), type="password", key="wf_modal_login_password")
        if st.button(t("login_submit"), key="wf_modal_login_submit", type="primary", use_container_width=True):
            email_clean = str(email).strip().lower()
            try:
                user = get_user(email_clean)
            except Exception as e:
                st.error(f"Erreur SGBD: {e}")
                return
            if user and verify_user_password(user, password):
                st.session_state.is_authenticated = True
                st.session_state.user_email = email_clean
                st.session_state.user_id = user.get("id")
                st.session_state.role = user.get("role") or "user"
                st.session_state.pseudo = user.get(
                    "pseudo") or email_clean.split("@")[0]
                st.session_state.favorites = set(
                    map(str, user.get("favorites", [])))
                st.success(t("logged_in_as", email_clean))
                token = generate_session_token(email_clean)
                st.query_params["auth_token"] = token
                st.rerun()
            else:
                st.error(t("invalid_credentials"))

    with tab_signup:
        pseudo = st.text_input(t("pseudo_label"), key="wf_modal_signup_pseudo")
        email = st.text_input(t("email_label"), key="wf_modal_signup_email")
        password = st.text_input(
            t("password_label"), type="password", key="wf_modal_signup_password")
        confirm = st.text_input(
            t("password_confirm"), type="password", key="wf_modal_signup_password_confirm"
        )
        if st.button(t("signup_submit"), key="wf_modal_signup_submit", type="primary", use_container_width=True):
            if password != confirm:
                st.error(t("passwords_mismatch"))
            else:
                try:
                    ok, msg = create_user(
                        email=email, pseudo=pseudo, password=password, role="user")
                except Exception as e:
                    st.error(f"Erreur SGBD: {e}")
                    return
                if not ok:
                    st.error(msg)
                else:
                    email_clean = str(email).strip().lower()
                    try:
                        user = get_user(email_clean)
                    except Exception:
                        st.error("Erreur connexion après création.")
                        return
                    st.session_state.is_authenticated = True
                    st.session_state.user_email = email_clean
                    st.session_state.user_id = user.get("id") if user else None
                    st.session_state.role = user.get(
                        "role") if user else "user"
                    st.session_state.pseudo = user.get("pseudo") if user else (
                        pseudo or email_clean.split("@")[0])
                    st.session_state.favorites = set(
                        map(str, (user or {}).get("favorites", [])))
                    st.session_state.flash_message = t("account_created")
                    token = generate_session_token(email_clean)
                    st.query_params["auth_token"] = token
                    st.rerun()


def login_form():
    if st.session_state.get("is_authenticated", False):
        pseudo = st.session_state.get("pseudo") or "Utilisateur"
        c1, c2 = st.sidebar.columns([1, 4])
        with c1:
            st.write("👤")
        with c2:
            st.write(f"**{pseudo}**")
        return

    # Single elegant button to open modal
    if st.sidebar.button(t("login_tab"), key="btn_open_login_modal", use_container_width=True, type="secondary"):
        login_dialog()

    # st.sidebar.markdown("---") # Removed per user request


def logout_button():
    if st.session_state.get("is_authenticated", False):
        if st.sidebar.button(t("logout_button"), use_container_width=True):
            email = st.session_state.get("user_email")
            if email:
                try:
                    save_favorites(str(email), set(
                        map(str, st.session_state.get("favorites", set()))))
                except Exception:
                    pass

            st.session_state.is_authenticated = False
            st.session_state.user_email = None
            st.session_state.user_id = None
            st.session_state.role = "visitor"
            st.session_state.pseudo = None
            st.session_state.favorites = set()
            st.session_state.auth_mode = None
            if "auth_token" in st.query_params:
                del st.query_params["auth_token"]
            st.rerun()


def show_flash_toast():
    message = st.session_state.pop("flash_message", None)
    if message:
        st.toast(message)


def toggle_favorite(imdb_key: str) -> bool:
    favorites = st.session_state.setdefault("favorites", set())
    if imdb_key in favorites:
        favorites.remove(imdb_key)
        st.session_state["flash_message"] = "Retire des favoris."

        if st.session_state.get("is_authenticated", False) and st.session_state.get("user_email"):
            try:
                save_favorites(
                    str(st.session_state["user_email"]), set(map(str, favorites)))
            except Exception:
                st.session_state["flash_message"] = "Retire (non sauvegarde MySQL)."
        return False

    favorites.add(imdb_key)
    st.session_state["flash_message"] = "Ajoute aux favoris."
    if st.session_state.get("is_authenticated", False) and st.session_state.get("user_email"):
        try:
            save_favorites(
                str(st.session_state["user_email"]), set(map(str, favorites)))
        except Exception:
            st.session_state["flash_message"] = "Ajoute (non sauvegarde MySQL)."
    return True


def update_profile(new_email: str | None = None, new_pseudo: str | None = None) -> tuple[bool, str]:
    if not st.session_state.get("is_authenticated", False):
        return False, "Vous devez etre connecte."

    current_email = st.session_state.get("user_email")
    if not current_email:
        return False, "Utilisateur introuvable."

    try:
        ok, msg, next_email = repo_update_profile(
            current_email=str(current_email),
            new_email=new_email,
            new_pseudo=new_pseudo,
        )
    except Exception:
        return False, "Mise a jour impossible (MySQL)."
    if not ok:
        return False, msg

    st.session_state.user_email = next_email
    try:
        user = get_user(next_email)
    except Exception:
        user = None
    st.session_state.pseudo = (user or {}).get(
        "pseudo") or next_email.split("@")[0]
    st.session_state.role = (user or {}).get("role") or st.session_state.role
    st.session_state.user_id = (user or {}).get("id")
    try:
        save_favorites(next_email, set(
            map(str, st.session_state.get("favorites", set()))))
    except Exception:
        st.session_state["flash_message"] = "Profil mis a jour (favoris non sauvegardes MySQL)."
    return True, msg


def change_password(current_password: str, new_password: str) -> tuple[bool, str]:
    if not st.session_state.get("is_authenticated", False):
        return False, "Vous devez etre connecte."

    email = st.session_state.get("user_email")
    if not email:
        return False, "Utilisateur introuvable."

    try:
        user = get_user(str(email))
    except Exception:
        return False, "Connexion MySQL impossible."
    if not user:
        return False, "Utilisateur introuvable."

    if not verify_user_password(user, str(current_password)):
        return False, "Mot de passe actuel incorrect."

    try:
        return update_user_password(str(email), str(new_password))
    except Exception:
        return False, "Mot de passe non mis a jour (MySQL)."


def sidebar_navigation():
    # Hide default Streamlit navigation
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button(t("home_title"), key="wf_nav_home", use_container_width=True):
        st.switch_page("Home.py")

    if st.sidebar.button(t("genre_title"), key="wf_nav_genre", use_container_width=True):
        st.switch_page("pages/1_Par_genre.py")

    if st.sidebar.button(t("favorites_title"), key="wf_nav_favs", use_container_width=True):
        st.switch_page("pages/2_Mes_favoris.py")

    if st.sidebar.button(t("recos_title"), key="wf_nav_recos", use_container_width=True):
        st.switch_page("pages/3_Recommandations.py")

    if st.sidebar.button(t("profile_title"), key="wf_nav_profile", use_container_width=True):
        st.switch_page("pages/4_Profil.py")

    if st.session_state.get("role") == "admin":
        if st.sidebar.button(t("admin_title"), key="wf_nav_admin", use_container_width=True):
            st.switch_page("pages/_Admin.py")
