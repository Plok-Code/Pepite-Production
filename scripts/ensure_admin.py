from __future__ import annotations

import argparse
import os
import secrets
import string

from utils.user_repo import backend_name, create_user, get_user, update_user_password


def _generate_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(int(length)))


def ensure_admin(email: str, password: str, pseudo: str) -> tuple[bool, str]:
    email = str(email).strip().lower()
    pseudo = str(pseudo).strip() or email.split("@")[0]

    if not email or "@" not in email:
        return False, "Email invalide."
    if len(str(password)) < 4:
        return False, "Mot de passe trop court."

    user = get_user(email)
    if not user:
        return create_user(email, pseudo, str(password), role="admin")

    ok, msg = update_user_password(email, str(password))
    if not ok:
        return ok, msg

    backend = backend_name()
    if backend == "mysql":
        try:
            from utils.mysql_store import ensure_schema, mysql_conn

            ensure_schema()
            with mysql_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE users SET role='admin' WHERE email=%s", (email,))
                conn.commit()
        except Exception as exc:
            return True, f"{msg} (role non mis à jour: {exc})"
        return True, "Admin mis à jour (mot de passe + rôle)."

    try:
        from utils.user_store import load_users, save_users

        users = load_users()
        if email in users:
            users[email]["role"] = "admin"
            save_users(users)
    except Exception:
        pass

    return True, "Admin mis à jour (mot de passe + rôle)."


def main() -> None:
    parser = argparse.ArgumentParser(description="Crée / met à jour un compte admin Wildflix.")
    parser.add_argument("--email", default=os.getenv("WILDFLIX_ADMIN_EMAIL", "admin@wildflix.com"))
    parser.add_argument("--password", default=os.getenv("WILDFLIX_ADMIN_PASSWORD"))
    parser.add_argument("--pseudo", default=os.getenv("WILDFLIX_ADMIN_PSEUDO", "Admin"))
    args = parser.parse_args()

    password = args.password or _generate_password()
    ok, msg = ensure_admin(args.email, password, args.pseudo)
    print(msg)
    if not args.password:
        print(f"Mot de passe g\u00e9n\u00e9r\u00e9: {password}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
