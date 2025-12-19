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
import html
from pathlib import Path

from utils.app_config import get_secret_key

# Secret key for signing tokens
SECRET_KEY = get_secret_key()
_UNSET = object()


def is_protected_account(email: str | None) -> bool:
    """
    Protected accounts can use the app like admins but cannot change their login email nor password.

    Configure in `.streamlit/secrets.toml`:
      [auth]
      protected_accounts = ["shared.admin@wildflix.com"]
    """
    if not email:
        return False
    email_clean = str(email).strip().lower()
    # Built-in protected shared account (works even without secrets configured).
    builtin = {"shared.admin@wildflix.com"}
    try:
        auth_cfg = st.secrets.get("auth", st.secrets)
        items = auth_cfg.get("protected_accounts") or auth_cfg.get(
            "PROTECTED_ACCOUNTS") or []
        if isinstance(items, str):
            items = [items]
        protected = {str(x).strip().lower() for x in items if str(x).strip()}
        return email_clean in (protected | builtin)
    except Exception:
        return email_clean in builtin


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
            email_from_token = verify_session_token(token)

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
                    st.session_state.date_of_birth = user.get("date_of_birth")
                    st.session_state.gender = user.get("gender")
                    st.session_state.in_creuse = user.get("in_creuse")
                    st.session_state.cinema_last_12m = user.get(
                        "cinema_last_12m")
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
        st.session_state.date_of_birth = None
        st.session_state.gender = None
        st.session_state.in_creuse = None
        st.session_state.cinema_last_12m = None
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
        with st.form("login_form"):
            email = st.text_input(t("email_label"), key="wf_modal_login_email")
            password = st.text_input(
                t("password_label"), type="password", key="wf_modal_login_password")
            submitted = st.form_submit_button(
                t("login_submit"), type="primary", use_container_width=True)

        if submitted:
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
                st.session_state.date_of_birth = user.get("date_of_birth")
                st.session_state.gender = user.get("gender")
                st.session_state.in_creuse = user.get("in_creuse")
                st.session_state.cinema_last_12m = user.get("cinema_last_12m")
                st.success(t("logged_in_as", email_clean))
                token = generate_session_token(email_clean)
                st.query_params["auth_token"] = token
                st.rerun()
            else:
                st.error(t("invalid_credentials"))

    with tab_signup:
        with st.form("signup_form"):
            pseudo = st.text_input(
                t("pseudo_label"), key="wf_modal_signup_pseudo")
            email = st.text_input(
                t("email_label"), key="wf_modal_signup_email")
            password = st.text_input(
                t("password_label"), type="password", key="wf_modal_signup_password")
            confirm = st.text_input(
                t("password_confirm"), type="password", key="wf_modal_signup_password_confirm"
            )

            dob_format = "DD-MM-YYYY" if get_current_language() == "fr" else "MM-DD-YYYY"
            date_of_birth = st.date_input(
                t("dob_label"),
                value=None,
                format=dob_format,
                key="wf_modal_signup_dob",
            )
            gender = st.selectbox(
                t("gender_label"),
                options=["male", "female", "other"],
                format_func=lambda v: t(f"gender_{v}"),
                index=None,
                placeholder=t("optional_placeholder"),
                key="wf_modal_signup_gender",
            )
            in_creuse = st.selectbox(
                t("in_creuse_label"),
                options=[True, False],
                format_func=lambda v: t("yes") if v else t("no"),
                index=None,
                placeholder=t("optional_placeholder"),
                key="wf_modal_signup_in_creuse",
            )
            cinema_last_12m = st.selectbox(
                t("cinema_12m_label"),
                options=[True, False],
                format_func=lambda v: t("yes") if v else t("no"),
                index=None,
                placeholder=t("optional_placeholder"),
                key="wf_modal_signup_cinema_12m",
            )

            site_submitted = st.form_submit_button(
                t("signup_submit"), type="primary", use_container_width=True)

        if site_submitted:
            if password != confirm:
                st.error(t("passwords_mismatch"))
            else:
                try:
                    ok, msg = create_user(
                        email=email,
                        pseudo=pseudo,
                        password=password,
                        role="user",
                        date_of_birth=(
                            date_of_birth.isoformat() if date_of_birth else None
                        ),
                        gender=gender,
                        in_creuse=in_creuse,
                        cinema_last_12m=cinema_last_12m,
                    )
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
                    st.session_state.date_of_birth = (user or {}).get(
                        "date_of_birth") or (
                        date_of_birth.isoformat() if date_of_birth else None
                    )
                    st.session_state.gender = (
                        user or {}).get("gender") or gender
                    st.session_state.in_creuse = (user or {}).get(
                        "in_creuse") if user else in_creuse
                    st.session_state.cinema_last_12m = (user or {}).get(
                        "cinema_last_12m") if user else cinema_last_12m
                    st.session_state.flash_message = t("account_created")
                    token = generate_session_token(email_clean)
                    st.query_params["auth_token"] = token
                    st.rerun()


def login_form():
    if st.session_state.get("is_authenticated", False):
        pseudo = str(st.session_state.get("pseudo")
                     or "").strip() or "Utilisateur"
        pseudo_html = html.escape(pseudo)
        connected_html = t(
            "logged_in_as",
            f"<span class=\"wf-connected-as__name\">{pseudo_html}</span>",
        )
        st.sidebar.markdown(
            f"<div class=\"wf-connected-as\">{connected_html}</div>",
            unsafe_allow_html=True,
        )
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
            st.session_state.date_of_birth = None
            st.session_state.gender = None
            st.session_state.in_creuse = None
            st.session_state.cinema_last_12m = None
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


def update_profile(
    new_email: str | None = None,
    new_pseudo: str | None = None,
    date_of_birth: str | None | object = _UNSET,
    gender: str | None | object = _UNSET,
    in_creuse: bool | None | object = _UNSET,
    cinema_last_12m: bool | None | object = _UNSET,
) -> tuple[bool, str]:
    if not st.session_state.get("is_authenticated", False):
        return False, "Vous devez etre connecte."

    current_email = st.session_state.get("user_email")
    if not current_email:
        return False, "Utilisateur introuvable."

    if is_protected_account(str(current_email)):
        cleaned_new = str(new_email).strip().lower(
        ) if new_email is not None else str(current_email).strip().lower()
        if cleaned_new != str(current_email).strip().lower():
            return False, "Ce compte ne peut pas modifier son email de connexion."

    try:
        updates = {
            "current_email": str(current_email),
            "new_email": new_email,
            "new_pseudo": new_pseudo,
        }
        if date_of_birth is not _UNSET:
            updates["date_of_birth"] = date_of_birth
        if gender is not _UNSET:
            updates["gender"] = gender
        if in_creuse is not _UNSET:
            updates["in_creuse"] = in_creuse
        if cinema_last_12m is not _UNSET:
            updates["cinema_last_12m"] = cinema_last_12m

        ok, msg, next_email = repo_update_profile(**updates)
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
    st.session_state.date_of_birth = (user or {}).get("date_of_birth")
    st.session_state.gender = (user or {}).get("gender")
    st.session_state.in_creuse = (user or {}).get("in_creuse")
    st.session_state.cinema_last_12m = (user or {}).get("cinema_last_12m")
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

    if is_protected_account(str(email)):
        return False, "Ce compte ne peut pas modifier son mot de passe."

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

    logo_path = Path(__file__).resolve().parent.parent / \
        "assets" / "logo_pepite_prod.png"
    if logo_path.exists():
        st.sidebar.image(str(logo_path), use_container_width=True)

    if st.sidebar.button(t("home_title"), key="wf_nav_home", use_container_width=True):
        st.switch_page("Home.py")

    if st.sidebar.button(t("cinemas_title"), key="wf_nav_cinemas", use_container_width=True):
        st.switch_page("pages/5_Nos_salles_de_cinema.py")

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
