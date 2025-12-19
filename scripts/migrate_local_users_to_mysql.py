from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.mysql_store import ensure_schema, mysql_conn
from utils.user_store import load_users


def _clean_email(email: str) -> str:
    return str(email).strip().lower()


def _to_int_bool_or_none(v: Any) -> int | None:
    if v is None:
        return None
    if isinstance(v, bool):
        return int(v)
    s = str(v).strip().lower()
    if s in ("1", "true", "yes", "oui"):
        return 1
    if s in ("0", "false", "no", "non"):
        return 0
    return None


def _upsert_user(cur, *, email: str, info: dict[str, Any]) -> int:
    email = _clean_email(email)
    if not email or "@" not in email:
        raise ValueError(f"Email invalide: {email!r}")

    pseudo = str(info.get("pseudo") or email.split("@")[0]).strip()[:64]
    role = str(info.get("role") or "user").strip().lower()[:16] or "user"
    salt = str(info.get("salt") or "").strip()
    password_hash = str(info.get("password_hash") or "").strip()

    date_of_birth = info.get("date_of_birth")
    if date_of_birth is not None:
        date_of_birth = str(date_of_birth).strip()[:10] or None

    gender = info.get("gender")
    if gender is not None:
        gender = str(gender).strip().lower()[:16] or None

    in_creuse = _to_int_bool_or_none(info.get("in_creuse"))
    cinema_last_12m = _to_int_bool_or_none(info.get("cinema_last_12m"))

    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
    row = cur.fetchone()
    if row:
        user_id = int(row["id"])
        cur.execute(
            """
            UPDATE users
            SET pseudo=%s, role=%s, salt=%s, password_hash=%s,
                date_of_birth=%s, gender=%s, in_creuse=%s, cinema_last_12m=%s
            WHERE id=%s
            """,
            (
                pseudo,
                role,
                salt,
                password_hash,
                date_of_birth,
                gender,
                in_creuse,
                cinema_last_12m,
                user_id,
            ),
        )
        return user_id

    cur.execute(
        """
        INSERT INTO users (email,pseudo,role,salt,password_hash,date_of_birth,gender,in_creuse,cinema_last_12m)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            email,
            pseudo,
            role,
            salt,
            password_hash,
            date_of_birth,
            gender,
            in_creuse,
            cinema_last_12m,
        ),
    )
    return int(cur.lastrowid)


def _replace_favorites(cur, *, user_id: int, favorites: list[Any]) -> None:
    cur.execute("DELETE FROM favorites WHERE user_id=%s", (int(user_id),))
    keys = sorted({str(k).strip() for k in (favorites or []) if str(k).strip()})
    if not keys:
        return
    cur.executemany(
        "INSERT INTO favorites (user_id, imdb_key) VALUES (%s,%s)",
        [(int(user_id), str(k)) for k in keys],
    )


def migrate(*, dry_run: bool = False) -> tuple[int, int]:
    users = load_users()
    if not users:
        return 0, 0

    ensure_schema()
    migrated_users = 0
    migrated_favs = 0

    with mysql_conn() as conn:
        with conn.cursor() as cur:
            for email, info in users.items():
                user_id = _upsert_user(cur, email=str(email), info=dict(info or {}))
                favorites = list((info or {}).get("favorites") or [])
                _replace_favorites(cur, user_id=user_id, favorites=favorites)
                migrated_users += 1
                migrated_favs += len({str(k).strip() for k in favorites if str(k).strip()})

        if dry_run:
            conn.rollback()
        else:
            conn.commit()

    return migrated_users, migrated_favs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migre data/users.json (stockage local) vers MySQL (Railway)."
    )
    parser.add_argument("--dry-run", action="store_true", help="Teste sans écrire dans MySQL.")
    args = parser.parse_args()

    n_users, n_favs = migrate(dry_run=bool(args.dry_run))
    suffix = " (dry-run)" if args.dry_run else ""
    print(f"OK{suffix}: {n_users} users, {n_favs} favoris migrés.")


if __name__ == "__main__":
    main()
