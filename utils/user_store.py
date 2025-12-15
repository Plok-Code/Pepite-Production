import base64
import hashlib
import json
import secrets
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_PATH = DATA_DIR / "users.json"


SEED_USERS: dict[str, dict] = {
    "user@wildflix.com": {"password": "user123", "role": "user", "pseudo": "user"},
    "admin@wildflix.com": {"password": "admin123", "role": "admin", "pseudo": "admin"},
}


def _hash_password(password: str, salt_b64: str | None = None) -> tuple[str, str]:
    if salt_b64 is None:
        salt = secrets.token_bytes(16)
        salt_b64 = base64.b64encode(salt).decode("utf-8")
    else:
        salt = base64.b64decode(salt_b64.encode("utf-8"))

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    digest_b64 = base64.b64encode(digest).decode("utf-8")
    return salt_b64, digest_b64


def _ensure_user_store():
    if USERS_PATH.exists():
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    users: dict[str, dict] = {}
    for email, info in SEED_USERS.items():
        salt_b64, digest_b64 = _hash_password(str(info["password"]))
        users[email] = {
            "role": info.get("role", "user"),
            "pseudo": info.get("pseudo", email.split("@")[0]),
            "salt": salt_b64,
            "password_hash": digest_b64,
            "favorites": [],
        }

    USERS_PATH.write_text(json.dumps(users, indent=2, ensure_ascii=False), encoding="utf-8")


def load_users() -> dict[str, dict]:
    _ensure_user_store()
    return json.loads(USERS_PATH.read_text(encoding="utf-8"))


def save_users(users: dict[str, dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    USERS_PATH.write_text(json.dumps(users, indent=2, ensure_ascii=False), encoding="utf-8")


def verify_password(user: dict, password: str) -> bool:
    salt_b64 = user.get("salt")
    expected = user.get("password_hash")
    if not salt_b64 or not expected:
        return False

    _, digest_b64 = _hash_password(password, salt_b64=salt_b64)
    return secrets.compare_digest(str(expected), str(digest_b64))


def set_password(user: dict, new_password: str) -> None:
    salt_b64, digest_b64 = _hash_password(new_password)
    user["salt"] = salt_b64
    user["password_hash"] = digest_b64

