import streamlit as st

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


def init_auth_state():
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
        st.session_state.user_email = None
        st.session_state.user_id = None
        st.session_state.role = "visitor"
        st.session_state.pseudo = None
        st.session_state.favorites = set()
        st.session_state.flash_message = None


def login_form():
    if st.session_state.get("is_authenticated", False):
        pseudo = st.session_state.get("pseudo") or "Utilisateur"
        role = st.session_state.get("role") or "user"
        st.sidebar.success(f"Connecte : {pseudo} ({role})")
        return

    try:
        mysql_enabled = is_mysql_enabled()
        mysql_ready = is_mysql_ready()
    except Exception:
        mysql_enabled = False
        mysql_ready = False

    if mysql_enabled and not mysql_ready:
        st.sidebar.warning(
            "MySQL configure, mais pymysql n'est pas installe. Fallback en stockage local."
        )
    elif mysql_enabled and mysql_ready and backend_name() != "mysql":
        st.sidebar.warning("MySQL configure, mais indisponible. Fallback en stockage local.")

    tab_login, tab_signup = st.sidebar.tabs(["Connexion", "Inscription"])

    with tab_login:
        st.subheader("Connexion")
        email = st.text_input("Email", key="wf_login_email")
        password = st.text_input("Mot de passe", type="password", key="wf_login_password")
        if st.button("Se connecter", key="wf_login_submit"):
            email_clean = str(email).strip().lower()
            try:
                user = get_user(email_clean)
            except Exception:
                st.error("Connexion MySQL impossible. Verifiez la configuration et relancez l'app.")
                return
            if user and verify_user_password(user, password):
                st.session_state.is_authenticated = True
                st.session_state.user_email = email_clean
                st.session_state.user_id = user.get("id")
                st.session_state.role = user.get("role") or "user"
                st.session_state.pseudo = user.get("pseudo") or email_clean.split("@")[0]
                st.session_state.favorites = set(map(str, user.get("favorites", [])))
                st.success(f"Connecte en tant que {email_clean}")
                st.rerun()
            else:
                st.error("Identifiants invalides")

    with tab_signup:
        st.subheader("Inscription")
        pseudo = st.text_input("Pseudo", key="wf_signup_pseudo")
        email = st.text_input("Email", key="wf_signup_email")
        password = st.text_input("Mot de passe", type="password", key="wf_signup_password")
        confirm = st.text_input(
            "Confirmer le mot de passe", type="password", key="wf_signup_password_confirm"
        )
        if st.button("Creer mon compte", key="wf_signup_submit"):
            if password != confirm:
                st.error("Les mots de passe ne correspondent pas.")
            else:
                try:
                    ok, msg = create_user(email=email, pseudo=pseudo, password=password, role="user")
                except Exception:
                    st.error("Inscription impossible (MySQL). Verifiez la configuration et relancez l'app.")
                    return
                if not ok:
                    st.error(msg)
                else:
                    email_clean = str(email).strip().lower()
                    try:
                        user = get_user(email_clean)
                    except Exception:
                        st.error("Compte cree, mais connexion MySQL impossible. Relancez l'app.")
                        return
                    st.session_state.is_authenticated = True
                    st.session_state.user_email = email_clean
                    st.session_state.user_id = user.get("id") if user else None
                    st.session_state.role = user.get("role") if user else "user"
                    st.session_state.pseudo = user.get("pseudo") if user else (pseudo or email_clean.split("@")[0])
                    st.session_state.favorites = set(map(str, (user or {}).get("favorites", [])))
                    st.session_state["flash_message"] = "Compte cree. Bienvenue !"
                    st.rerun()


def logout_button():
    if st.session_state.get("is_authenticated", False):
        if st.sidebar.button("Se deconnecter"):
            email = st.session_state.get("user_email")
            if email:
                try:
                    save_favorites(str(email), set(map(str, st.session_state.get("favorites", set()))))
                except Exception:
                    st.session_state["flash_message"] = "Impossible de sauvegarder vos favoris (MySQL)."

            st.session_state.is_authenticated = False
            st.session_state.user_email = None
            st.session_state.user_id = None
            st.session_state.role = "visitor"
            st.session_state.pseudo = None
            st.session_state.favorites = set()
            st.sidebar.info("Deconnecte")


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
                save_favorites(str(st.session_state["user_email"]), set(map(str, favorites)))
            except Exception:
                st.session_state["flash_message"] = "Retire (non sauvegarde MySQL)."
        return False

    favorites.add(imdb_key)
    st.session_state["flash_message"] = "Ajoute aux favoris."
    if st.session_state.get("is_authenticated", False) and st.session_state.get("user_email"):
        try:
            save_favorites(str(st.session_state["user_email"]), set(map(str, favorites)))
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
    st.session_state.pseudo = (user or {}).get("pseudo") or next_email.split("@")[0]
    st.session_state.role = (user or {}).get("role") or st.session_state.role
    st.session_state.user_id = (user or {}).get("id")
    try:
        save_favorites(next_email, set(map(str, st.session_state.get("favorites", set()))))
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
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Navigation")
    if st.sidebar.button("Accueil", key="wf_nav_home", use_container_width=True):
        st.switch_page("Home.py")
    if st.sidebar.button("Par genre", key="wf_nav_genre", use_container_width=True):
        st.switch_page("pages/1_Par_genre.py")
    if st.sidebar.button("Votre espace", key="wf_nav_user", use_container_width=True):
        st.switch_page("pages/2_Votre_espace.py")

    if st.session_state.get("role") == "admin":
        if st.sidebar.button("Admin", key="wf_nav_admin", use_container_width=True):
            st.switch_page("pages/_Admin.py")
