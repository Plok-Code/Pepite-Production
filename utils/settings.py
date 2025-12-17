from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SETTINGS_PATH = Path(__file__).resolve().parent.parent / "data" / "settings.json"

VALID_RECO_MODELS = {"cosine", "euclidean", "manhattan"}

DEFAULT_SETTINGS: dict[str, Any] = {
    "recommender_model": "cosine",
}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_settings() -> dict[str, Any]:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not SETTINGS_PATH.exists():
        SETTINGS_PATH.write_text(
            json.dumps(DEFAULT_SETTINGS, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return dict(DEFAULT_SETTINGS)

    data = _read_json(SETTINGS_PATH)
    merged = dict(DEFAULT_SETTINGS)
    merged.update({k: v for k, v in data.items() if v is not None})
    return merged


def save_settings(settings: dict[str, Any]) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_recommender_model() -> str:
    model = str(load_settings().get("recommender_model", "cosine")).strip().lower()
    return model if model in VALID_RECO_MODELS else "cosine"


def set_recommender_model(model: str) -> None:
    model = str(model).strip().lower()
    if model not in VALID_RECO_MODELS:
        model = "cosine"
    settings = load_settings()
    settings["recommender_model"] = model
    save_settings(settings)

