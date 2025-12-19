from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd

from utils.mysql_store import ensure_schema, is_mysql_ready, mysql_conn
from utils.user_repo import backend_name
from utils.user_store import load_users


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except Exception:
        return None


def _age_from_dob(dob: date | None) -> int | None:
    if dob is None:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def load_users_df() -> pd.DataFrame:
    if backend_name() == "mysql" and is_mysql_ready():
        ensure_schema()
        with mysql_conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                        SELECT email, pseudo, role, date_of_birth, gender, in_creuse, cinema_last_12m
                        FROM users
                        """
                    )
                except Exception:
                    cur.execute("SELECT email, pseudo, role FROM users")
                rows = cur.fetchall() or []
            conn.commit()
        df = pd.DataFrame(rows)
    else:
        users = load_users()
        rows: list[dict[str, Any]] = []
        for email, info in users.items():
            rows.append(
                {
                    "email": str(email),
                    "pseudo": info.get("pseudo"),
                    "role": info.get("role"),
                    "date_of_birth": info.get("date_of_birth"),
                    "gender": info.get("gender"),
                    "in_creuse": info.get("in_creuse"),
                    "cinema_last_12m": info.get("cinema_last_12m"),
                }
            )
        df = pd.DataFrame(rows)

    if df.empty:
        return pd.DataFrame(
            columns=[
                "email",
                "pseudo",
                "role",
                "date_of_birth",
                "age",
                "gender",
                "in_creuse",
                "cinema_last_12m",
            ]
        )

    for col in ("date_of_birth", "gender", "in_creuse", "cinema_last_12m"):
        if col not in df.columns:
            df[col] = None

    dob = df["date_of_birth"].map(_parse_date)
    df["date_of_birth"] = dob.map(lambda d: d.isoformat() if d else None)
    df["age"] = dob.map(_age_from_dob)

    def _bool_or_none(v: Any) -> bool | None:
        if v is None:
            return None
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)) and not pd.isna(v):
            return bool(int(v))
        s = str(v).strip().lower()
        if s in ("1", "true", "yes", "oui"):
            return True
        if s in ("0", "false", "no", "non"):
            return False
        return None

    df["in_creuse"] = df["in_creuse"].map(_bool_or_none)
    df["cinema_last_12m"] = df["cinema_last_12m"].map(_bool_or_none)
    df["gender"] = df["gender"].map(lambda v: (str(v).strip().lower() or None) if v is not None else None)
    df["role"] = df["role"].map(lambda v: (str(v).strip().lower() or None) if v is not None else None)
    df["email"] = df["email"].astype(str)
    return df


def load_favorites_df() -> pd.DataFrame:
    if backend_name() == "mysql" and is_mysql_ready():
        ensure_schema()
        with mysql_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT u.email AS email, f.imdb_key AS imdb_key
                    FROM favorites f
                    JOIN users u ON u.id = f.user_id
                    """
                )
                rows = cur.fetchall() or []
            conn.commit()
        df = pd.DataFrame(rows)
    else:
        users = load_users()
        rows: list[dict[str, Any]] = []
        for email, info in users.items():
            for imdb_key in (info.get("favorites") or []):
                rows.append({"email": str(email), "imdb_key": str(imdb_key)})
        df = pd.DataFrame(rows)

    if df.empty:
        return pd.DataFrame(columns=["email", "imdb_key"])

    df["email"] = df["email"].astype(str)
    df["imdb_key"] = df["imdb_key"].astype(str)
    return df


def apply_user_filters(
    users_df: pd.DataFrame,
    age_range: tuple[int, int] = (0, 120),
    include_unknown_age: bool = True,
    gender: list[str] | None = None,
    in_creuse: list[str] | None = None,
    cinema_last_12m: list[str] | None = None,
) -> pd.DataFrame:
    if users_df.empty:
        return users_df

    df = users_df.copy()

    age_min, age_max = int(age_range[0]), int(age_range[1])
    if (age_min, age_max) != (0, 120) or not include_unknown_age:
        age = df["age"]
        if include_unknown_age:
            df = df[age.isna() | age.between(age_min, age_max)]
        else:
            df = df[age.between(age_min, age_max)]

    if gender is not None:
        allowed = {str(v).strip().lower() for v in gender if str(v).strip()}
        all_values = {"male", "female", "other", "unknown"}
        if allowed and allowed != all_values:
            mask = pd.Series(False, index=df.index)
            if "unknown" in allowed:
                mask |= df["gender"].isna()
            known = sorted(v for v in allowed if v != "unknown")
            if known:
                mask |= df["gender"].isin(known)
            df = df[mask]

    def _apply_multi_bool_filter(col: str, selected: list[str] | None) -> None:
        nonlocal df
        if selected is None:
            return
        allowed = {str(v).strip().lower() for v in selected if str(v).strip()}
        all_values = {"yes", "no", "unknown"}
        if not allowed or allowed == all_values:
            return
        mask = pd.Series(False, index=df.index)
        if "unknown" in allowed:
            mask |= df[col].isna()
        if "yes" in allowed:
            mask |= df[col] == True
        if "no" in allowed:
            mask |= df[col] == False
        df = df[mask]

    _apply_multi_bool_filter("in_creuse", in_creuse)
    _apply_multi_bool_filter("cinema_last_12m", cinema_last_12m)
    return df


def favorites_for_users(favorites_df: pd.DataFrame, users_df: pd.DataFrame) -> pd.DataFrame:
    if favorites_df.empty or users_df.empty:
        return favorites_df.iloc[0:0].copy()
    return favorites_df.merge(users_df[["email"]], on="email", how="inner")
