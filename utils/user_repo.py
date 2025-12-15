from __future__ import annotations

from typing import Any

from utils.mysql_store import (
    create_user as mysql_create_user,
    get_favorites as mysql_get_favorites,
    get_user_by_email as mysql_get_user_by_email,
    ensure_schema as mysql_ensure_schema,
    is_mysql_ready,
    set_favorites as mysql_set_favorites,
    update_email as mysql_update_email,
    update_password as mysql_update_password,
    update_pseudo as mysql_update_pseudo,
)
from utils.user_store import load_users, save_users, set_password, verify_password


_MYSQL_AVAILABLE: bool | None = None


def _is_mysql_available() -> bool:
    global _MYSQL_AVAILABLE

    if not is_mysql_ready():
        _MYSQL_AVAILABLE = False
        return False

    if _MYSQL_AVAILABLE is not None:
        return _MYSQL_AVAILABLE

    try:
        mysql_ensure_schema()
        _MYSQL_AVAILABLE = True
    except Exception:
        _MYSQL_AVAILABLE = False
    return _MYSQL_AVAILABLE


def backend_name() -> str:
    return "mysql" if _is_mysql_available() else "local"


def get_user(email: str) -> dict[str, Any] | None:
    email = str(email).strip().lower()
    if not email:
        return None

    if backend_name() == "mysql":
        user = mysql_get_user_by_email(email)
        if not user:
            return None
        favorites = mysql_get_favorites(int(user["id"]))
        return {
            "id": int(user["id"]),
            "email": str(user["email"]),
            "pseudo": str(user.get("pseudo") or user["email"].split("@")[0]),
            "role": str(user.get("role") or "user"),
            "salt": str(user.get("salt") or ""),
            "password_hash": str(user.get("password_hash") or ""),
            "favorites": sorted(favorites),
        }

    users = load_users()
    u = users.get(email)
    if not u:
        return None
    return {
        "id": None,
        "email": email,
        "pseudo": u.get("pseudo") or email.split("@")[0],
        "role": u.get("role") or "user",
        "salt": u.get("salt") or "",
        "password_hash": u.get("password_hash") or "",
        "favorites": list(u.get("favorites", [])),
    }


def verify_user_password(user: dict[str, Any], password: str) -> bool:
    return verify_password(user, password)


def create_user(email: str, pseudo: str, password: str, role: str = "user") -> tuple[bool, str]:
    email = str(email).strip().lower()
    pseudo = str(pseudo).strip() or email.split("@")[0]
    password = str(password)
    role = str(role or "user")

    if not email or "@" not in email:
        return False, "Email invalide."
    if len(password) < 4:
        return False, "Mot de passe trop court."

    if backend_name() == "mysql":
        user_tmp = {}
        set_password(user_tmp, password)
        return mysql_create_user(
            email=email,
            pseudo=pseudo,
            role=role,
            salt=str(user_tmp["salt"]),
            password_hash=str(user_tmp["password_hash"]),
        )

    users = load_users()
    if email in users:
        return False, "Cet email est deja utilise."

    user = {"role": role, "pseudo": pseudo, "favorites": []}
    set_password(user, password)
    users[email] = user
    save_users(users)
    return True, "Compte cree."


def save_favorites(email: str, favorites: set[str]) -> None:
    email = str(email).strip().lower()
    if not email:
        return

    if backend_name() == "mysql":
        user = mysql_get_user_by_email(email)
        if not user:
            return
        mysql_set_favorites(int(user["id"]), set(map(str, favorites)))
        return

    users = load_users()
    u = users.get(email)
    if not u:
        return
    u["favorites"] = sorted(set(map(str, favorites)))
    save_users(users)


def update_profile(
    current_email: str, new_email: str | None = None, new_pseudo: str | None = None
) -> tuple[bool, str, str]:
    current_email = str(current_email).strip().lower()
    if not current_email:
        return False, "Utilisateur introuvable.", current_email

    next_email = current_email
    if new_email is not None:
        cleaned = str(new_email).strip().lower()
        if not cleaned or "@" not in cleaned:
            return False, "Email invalide.", current_email
        next_email = cleaned

    if backend_name() == "mysql":
        user = mysql_get_user_by_email(current_email)
        if not user:
            return False, "Utilisateur introuvable.", current_email

        user_id = int(user["id"])
        if next_email != current_email:
            ok, msg = mysql_update_email(user_id, next_email)
            if not ok:
                return False, msg, current_email

        if new_pseudo is not None:
            pseudo = str(new_pseudo).strip()
            if pseudo:
                mysql_update_pseudo(user_id, pseudo)

        return True, "Profil mis a jour.", next_email

    users = load_users()
    user = users.get(current_email)
    if user is None:
        return False, "Utilisateur introuvable.", current_email

    if next_email != current_email:
        if next_email in users:
            return False, "Cet email est deja utilise.", current_email
        users[next_email] = user
        del users[current_email]

    if new_pseudo is not None:
        pseudo = str(new_pseudo).strip()
        if pseudo:
            user["pseudo"] = pseudo

    save_users(users)
    return True, "Profil mis a jour.", next_email


def update_user_password(email: str, new_password: str) -> tuple[bool, str]:
    email = str(email).strip().lower()
    new_password = str(new_password)
    if len(new_password) < 4:
        return False, "Mot de passe trop court."

    if backend_name() == "mysql":
        user = mysql_get_user_by_email(email)
        if not user:
            return False, "Utilisateur introuvable."
        tmp = {}
        set_password(tmp, new_password)
        return mysql_update_password(int(user["id"]), str(tmp["salt"]), str(tmp["password_hash"]))

    users = load_users()
    u = users.get(email)
    if u is None:
        return False, "Utilisateur introuvable."
    set_password(u, new_password)
    save_users(users)
    return True, "Mot de passe mis a jour."
