from utils.mysql_store import mysql_conn
from utils.user_repo import get_user, create_user, update_user_password, backend_name
import streamlit as st
import os
import toml
from pathlib import Path
import sys

# Debug imports
try:
    import pymysql
    print(f"DEBUG: pymysql version: {pymysql.__version__}")
except ImportError:
    print("DEBUG: pymysql NOT INSTALLED")

# Be verbose
print(f"DEBUG: CWD is {os.getcwd()}")


def load_secrets():
    secrets_path = Path.cwd() / ".streamlit" / "secrets.toml"
    print(f"DEBUG: Looking for secrets at {secrets_path}")

    if secrets_path.exists():
        try:
            data = toml.load(secrets_path)
            if "mysql" in data:
                print("DEBUG: Found [mysql] in secrets.")
                mysql = data["mysql"]
                os.environ["MYSQL_HOST"] = str(mysql.get("host", ""))
                os.environ["MYSQL_PORT"] = str(mysql.get("port", "3306"))
                os.environ["MYSQL_USER"] = str(mysql.get("user", ""))
                os.environ["MYSQL_PASSWORD"] = str(mysql.get("password", ""))
                os.environ["MYSQL_DATABASE"] = str(mysql.get("database", ""))
                print(f"DEBUG: Set MYSQL_HOST={os.environ['MYSQL_HOST']}")
            else:
                print("DEBUG: [mysql] section NOT found in secrets.")
        except Exception as e:
            print(f"DEBUG: Failed to load secrets.toml: {e}")
    else:
        print("DEBUG: secrets.toml does not exist at that path.")


load_secrets()


def reset_admin():
    email = "admin@wildflix.com"
    password = "admin123456"
    pseudo = "Admin"

    bn = backend_name()
    print(f"Backend detected: {bn}")

    if bn == "local":
        print("WARNING: Using LOCAL backend. If you expect MySQL, check PyMySQL installation and secrets.")

    # Check if user exists
    try:
        user = get_user(email)
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return

    if not user:
        print(f"User {email} not found. Creating...")
        ok, msg = create_user(email, pseudo, password, role="admin")
        if ok:
            print("SUCCESS: Admin user created.")
        else:
            print(f"ERROR: Failed to create admin. {msg}")
    else:
        print(f"User {email} found. Resetting password...")
        ok, msg = update_user_password(email, password)
        if ok:
            print("SUCCESS: Password updated.")
        else:
            print(f"ERROR: Failed to update password. {msg}")

        # Ensure role is admin
        if bn == "mysql":
            try:
                with mysql_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "UPDATE users SET role='admin' WHERE email=%s", (email,))
                    conn.commit()
                print("SUCCESS: Role ensured as 'admin'.")
            except Exception as e:
                print(f"WARNING: Could not force role update: {e}")


if __name__ == "__main__":
    reset_admin()
