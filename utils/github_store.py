from __future__ import annotations

import base64
import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

try:
    import streamlit as st
    from streamlit.errors import StreamlitSecretNotFoundError
except Exception:  # pragma: no cover
    st = None

    class StreamlitSecretNotFoundError(Exception):
        pass


def get_github_store_config() -> dict[str, str] | None:
    cfg: dict[str, str] = {}

    if st is not None:
        try:
            section = st.secrets["github_store"]
            cfg = {str(k): str(v) for k, v in dict(section).items()}
        except (StreamlitSecretNotFoundError, KeyError, TypeError):
            cfg = {}

    if not cfg:
        owner = os.getenv("GITHUB_DATA_OWNER", "").strip()
        repo = os.getenv("GITHUB_DATA_REPO", "").strip()
        token = os.getenv("GITHUB_DATA_TOKEN", "").strip()
        if owner and repo and token:
            cfg = {
                "owner": owner,
                "repo": repo,
                "token": token,
                "branch": os.getenv("GITHUB_DATA_BRANCH", "main").strip() or "main",
                "path": os.getenv("GITHUB_DATA_PATH", "data/users.json").strip() or "data/users.json",
            }

    owner = str(cfg.get("owner", "")).strip()
    repo = str(cfg.get("repo", "")).strip()
    token = str(cfg.get("token", "")).strip()
    path = str(cfg.get("path", "data/users.json")).strip() or "data/users.json"
    branch = str(cfg.get("branch", "main")).strip() or "main"

    if not owner or not repo or not token:
        return None

    return {
        "owner": owner,
        "repo": repo,
        "token": token,
        "branch": branch,
        "path": path.strip("/"),
    }


def is_github_store_enabled() -> bool:
    return get_github_store_config() is not None


def _copy_json_like(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _contents_url(cfg: dict[str, str]) -> str:
    path = quote(cfg["path"], safe="/")
    ref = quote(cfg["branch"], safe="")
    return f"https://api.github.com/repos/{cfg['owner']}/{cfg['repo']}/contents/{path}?ref={ref}"


def _request_json(
    *,
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any] | list[Any] | None:
    body = None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "wildflix-data-store",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = Request(url=url, data=body, headers=headers, method=method.upper())
    with urlopen(req, timeout=20) as resp:
        raw = resp.read().decode("utf-8")
    if not raw.strip():
        return None
    return json.loads(raw)


def _read_remote_file(cfg: dict[str, str]) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = _request_json(
            method="GET",
            url=_contents_url(cfg),
            token=cfg["token"],
        )
    except HTTPError as exc:
        if exc.code == 404:
            return None, None
        try:
            detail = exc.read().decode("utf-8").strip()
        except Exception:
            detail = str(exc)
        raise RuntimeError(f"GitHub API GET failed: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"GitHub API unreachable: {exc}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("GitHub API returned an unexpected payload.")

    sha = str(payload.get("sha") or "").strip() or None
    content_b64 = str(payload.get("content") or "").replace("\n", "").strip()
    if not content_b64:
        return {}, sha

    try:
        text = base64.b64decode(content_b64.encode("utf-8")).decode("utf-8")
        data = json.loads(text)
    except Exception as exc:
        raise RuntimeError("GitHub data file is not valid JSON.") from exc

    if not isinstance(data, dict):
        raise RuntimeError("GitHub data file must contain a JSON object.")

    return data, sha


def read_json_file(
    *,
    default: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], bool]:
    cfg = get_github_store_config()
    if not cfg:
        raise RuntimeError("GitHub store not configured.")

    data, sha = _read_remote_file(cfg)
    if data is None and sha is None:
        return _copy_json_like(default or {}), False
    return data or {}, True


def save_json_file(
    payload: dict[str, Any],
    *,
    commit_message: str = "Update data/users.json",
) -> None:
    if not isinstance(payload, dict):
        raise ValueError("GitHub store only accepts JSON objects at the root.")

    cfg = get_github_store_config()
    if not cfg:
        raise RuntimeError("GitHub store not configured.")

    encoded = base64.b64encode(
        json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
    ).decode("utf-8")

    last_error: Exception | None = None
    for _ in range(2):
        _, sha = _read_remote_file(cfg)
        body = {
            "message": str(commit_message).strip() or "Update data/users.json",
            "content": encoded,
            "branch": cfg["branch"],
        }
        if sha:
            body["sha"] = sha

        try:
            _request_json(
                method="PUT",
                url=_contents_url(cfg).split("?", 1)[0],
                token=cfg["token"],
                payload=body,
            )
            return
        except HTTPError as exc:
            last_error = exc
            if exc.code == 409:
                continue
            try:
                detail = exc.read().decode("utf-8").strip()
            except Exception:
                detail = str(exc)
            raise RuntimeError(f"GitHub API PUT failed: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"GitHub API unreachable: {exc}") from exc

    raise RuntimeError(f"GitHub API PUT conflicted twice: {last_error}")
