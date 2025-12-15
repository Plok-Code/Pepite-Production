from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

try:
    import pymysql
    from pymysql.cursors import DictCursor
except Exception:  # pragma: no cover
    pymysql = None
    DictCursor = None


def get_mysql_config() -> dict[str, Any] | None:
    cfg: dict[str, Any] = {}

    try:
        mysql_section = st.secrets["mysql"]
        cfg = dict(mysql_section)
    except (StreamlitSecretNotFoundError, KeyError, TypeError):
        host = os.getenv("MYSQL_HOST")
        if host:
            cfg = {
                "host": host,
                "port": int(os.getenv("MYSQL_PORT", "3306")),
                "user": os.getenv("MYSQL_USER", ""),
                "password": os.getenv("MYSQL_PASSWORD", ""),
                "database": os.getenv("MYSQL_DATABASE", ""),
            }

    host = str(cfg.get("host", "")).strip()
    user = str(cfg.get("user", "")).strip()
    database = str(cfg.get("database", "")).strip()
    if not host or not user or not database:
        return None

    cfg["host"] = host
    cfg["port"] = int(cfg.get("port", 3306))
    cfg["user"] = user
    cfg["password"] = str(cfg.get("password", ""))
    cfg["database"] = database
    return cfg


def is_mysql_enabled() -> bool:
    return get_mysql_config() is not None


def is_mysql_ready() -> bool:
    return is_mysql_enabled() and (pymysql is not None)


@contextmanager
def mysql_conn():
    cfg = get_mysql_config()
    if not cfg:
        raise RuntimeError("MySQL non configure (st.secrets['mysql'] ou variables d'environnement).")
    if pymysql is None:
        raise RuntimeError("pymysql n'est pas installe (ajoutez-le a requirements.txt).")

    conn = pymysql.connect(
        host=cfg["host"],
        port=int(cfg["port"]),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )
    try:
        yield conn
    finally:
        conn.close()


def ensure_schema() -> None:
    if not is_mysql_ready():
        return

    try:
        with mysql_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                      id INT AUTO_INCREMENT PRIMARY KEY,
                      email VARCHAR(255) NOT NULL UNIQUE,
                      pseudo VARCHAR(64) NOT NULL,
                      role VARCHAR(16) NOT NULL DEFAULT 'user',
                      salt VARCHAR(64) NOT NULL,
                      password_hash VARCHAR(128) NOT NULL,
                      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS favorites (
                      user_id INT NOT NULL,
                      imdb_key VARCHAR(32) NOT NULL,
                      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      PRIMARY KEY (user_id, imdb_key),
                      CONSTRAINT fk_fav_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """
                )
            conn.commit()
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Impossible de se connecter a MySQL. Verifiez `sql/mysql_schema.sql`, "
            "puis `.streamlit/secrets.toml` (section [mysql]) et que le serveur MySQL est demarre."
        ) from exc


def get_user_by_email(email: str) -> dict[str, Any] | None:
    ensure_schema()
    with mysql_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id,email,pseudo,role,salt,password_hash FROM users WHERE email=%s LIMIT 1",
                (email,),
            )
            row = cur.fetchone()
        conn.commit()
    return row


def get_favorites(user_id: int) -> set[str]:
    ensure_schema()
    with mysql_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT imdb_key FROM favorites WHERE user_id=%s", (int(user_id),))
            rows = cur.fetchall() or []
        conn.commit()
    return {str(r["imdb_key"]) for r in rows if r.get("imdb_key")}


def create_user(email: str, pseudo: str, role: str, salt: str, password_hash: str) -> tuple[bool, str]:
    ensure_schema()
    try:
        with mysql_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (email,pseudo,role,salt,password_hash) VALUES (%s,%s,%s,%s,%s)",
                    (email, pseudo, role, salt, password_hash),
                )
            conn.commit()
        return True, "Compte cree."
    except Exception as exc:  # pragma: no cover
        msg = str(exc).lower()
        if "duplicate" in msg or "unique" in msg:
            return False, "Cet email est deja utilise."
        return False, "Impossible de creer le compte (MySQL)."


def update_email(user_id: int, new_email: str) -> tuple[bool, str]:
    ensure_schema()
    try:
        with mysql_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET email=%s WHERE id=%s", (new_email, int(user_id)))
            conn.commit()
        return True, "Email mis a jour."
    except Exception as exc:  # pragma: no cover
        msg = str(exc).lower()
        if "duplicate" in msg or "unique" in msg:
            return False, "Cet email est deja utilise."
        return False, "Impossible de mettre a jour l'email (MySQL)."


def update_pseudo(user_id: int, new_pseudo: str) -> tuple[bool, str]:
    ensure_schema()
    with mysql_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET pseudo=%s WHERE id=%s", (new_pseudo, int(user_id)))
        conn.commit()
    return True, "Pseudo mis a jour."


def update_password(user_id: int, salt: str, password_hash: str) -> tuple[bool, str]:
    ensure_schema()
    with mysql_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET salt=%s,password_hash=%s WHERE id=%s",
                (salt, password_hash, int(user_id)),
            )
        conn.commit()
    return True, "Mot de passe mis a jour."


def set_favorites(user_id: int, favorites: set[str]) -> None:
    ensure_schema()
    with mysql_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM favorites WHERE user_id=%s", (int(user_id),))
            if favorites:
                values = [(int(user_id), str(k)) for k in sorted(set(map(str, favorites)))]
                cur.executemany(
                    "INSERT INTO favorites (user_id, imdb_key) VALUES (%s,%s)",
                    values,
                )
        conn.commit()
