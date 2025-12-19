from __future__ import annotations

import argparse
import secrets
import string
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.user_repo import backend_name, create_user, get_user, update_user_password  # noqa: E402


def _generate_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(int(length)))


def _set_role_mysql(email: str, role: str) -> None:
    from utils.mysql_store import ensure_schema, mysql_conn

    ensure_schema()
    with mysql_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET role=%s WHERE email=%s", (str(role), str(email).strip().lower()))
        conn.commit()


def _set_role_local(email: str, role: str) -> None:
    from utils.user_store import load_users, save_users

    email = str(email).strip().lower()
    users = load_users()
    if email not in users:
        return
    users[email]["role"] = str(role)
    save_users(users)


def reset_password(email: str, password: str | None, pseudo: str | None, role: str | None) -> tuple[bool, str, str | None]:
    email = str(email).strip().lower()
    if not email or "@" not in email:
        return False, "Email invalide.", None

    generated = None
    if not password:
        generated = _generate_password()
        password = generated

    user = get_user(email)
    if not user:
        ok, msg = create_user(
            email=email,
            pseudo=(pseudo or email.split("@")[0]),
            password=str(password),
            role=(role or "user"),
        )
        return ok, msg, generated

    ok, msg = update_user_password(email, str(password))
    if not ok:
        return ok, msg, generated

    if role:
        if backend_name() == "mysql":
            _set_role_mysql(email, role)
        else:
            _set_role_local(email, role)

    return True, "Mot de passe réinitialisé.", generated


def main() -> None:
    parser = argparse.ArgumentParser(description="Réinitialise le mot de passe d'un utilisateur (local ou MySQL).")
    parser.add_argument("--email", required=True, help="Email du compte à réinitialiser.")
    parser.add_argument("--password", default=None, help="Nouveau mot de passe (sinon généré automatiquement).")
    parser.add_argument("--pseudo", default=None, help="Pseudo si création du compte (si inexistant).")
    parser.add_argument("--role", default=None, help="Optionnel: force le rôle (admin/user).")
    parser.add_argument("--password-length", type=int, default=16, help="Taille du mot de passe généré.")
    args = parser.parse_args()

    if not args.password:
        # Generate with the requested length.
        generated = _generate_password(int(args.password_length))
        args.password = generated
    else:
        generated = None

    ok, msg, _ = reset_password(args.email, args.password, args.pseudo, args.role)
    print(msg)
    if generated:
        print(f"Nouveau mot de passe: {generated}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()

