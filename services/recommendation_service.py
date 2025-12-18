from __future__ import annotations

import math
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from utils.settings import get_recommender_model
from utils.text import normalize_text


_KNN_MODELS_DIR = Path(__file__).resolve().parent.parent / "ml"


def _get_knn_model_path() -> Path:
    model = get_recommender_model()
    return _KNN_MODELS_DIR / f"KNN_{model}.pkl"


@lru_cache(maxsize=3)
def _load_knn_model(path: str) -> Any | None:
    model_path = Path(path)
    if not model_path.exists():
        return None

    try:
        import joblib  # type: ignore
    except Exception:
        return None

    try:
        return joblib.load(model_path)
    except Exception:
        return None


def _build_key_to_index(df: pd.DataFrame) -> dict[str, int]:
    if "imdb_key" not in df.columns:
        return {}

    mapping: dict[str, int] = {}
    for idx, raw in zip(df.index.tolist(), df["imdb_key"].tolist()):
        if pd.isna(raw):
            continue
        key = str(raw).strip()
        if not key or key in mapping:
            continue
        mapping[key] = int(idx)
    return mapping


def _tokenize_movie_row(row: pd.Series) -> list[str]:
    tokens: list[str] = []

    kw = row.get("plot_keywords_final")
    if pd.notna(kw) and str(kw).strip():
        for part in str(kw).split("|"):
            tok = normalize_text(part).replace(" ", "_")
            if tok:
                tokens.append(tok)

    genre_main = row.get("genre_main")
    if pd.notna(genre_main) and str(genre_main).strip():
        tok = normalize_text(str(genre_main)).replace(" ", "_")
        if tok:
            tokens.append(f"genre_{tok}")

    language = row.get("language")
    if pd.notna(language) and str(language).strip():
        tok = normalize_text(str(language)).replace(" ", "_")
        if tok:
            tokens.append(f"lang_{tok}")

    return tokens


def _recommend_with_cosine_keywords(
    df: pd.DataFrame, favorites: set[str], n: int
) -> pd.DataFrame:
    if not favorites or "imdb_key" not in df.columns:
        return df.head(0)

    fav_mask = df["imdb_key"].astype(str).isin(set(map(str, favorites)))
    fav_df = df[fav_mask].copy()
    if fav_df.empty:
        return df.head(0)

    user_vec = Counter()
    for _, row in fav_df.iterrows():
        user_vec.update(_tokenize_movie_row(row))

    if not user_vec:
        return df.head(0)

    user_norm = math.sqrt(sum(v * v for v in user_vec.values()))
    if user_norm <= 0:
        return df.head(0)

    candidates = df[~fav_mask].copy()
    if candidates.empty:
        return df.head(0)

    scores: list[float] = []
    for _, row in candidates.iterrows():
        toks = _tokenize_movie_row(row)
        if not toks:
            scores.append(0.0)
            continue
        dot = sum(user_vec.get(t, 0) for t in set(toks))
        denom = user_norm * math.sqrt(len(set(toks)))
        scores.append((dot / denom) if denom else 0.0)

    candidates["wf_reco_score"] = scores

    sort_cols = ["wf_reco_score"]
    for col in ("score_global", "popularity", "num_voted_users"):
        if col in candidates.columns:
            sort_cols.append(col)

    candidates = candidates.sort_values(sort_cols, ascending=[False] * len(sort_cols))
    if "imdb_key" in candidates.columns:
        candidates = candidates.drop_duplicates(subset=["imdb_key"], keep="first")
    return candidates.head(int(n))


def get_recommendations_from_favorites(df: pd.DataFrame, favorites: set[str], n: int = 10) -> pd.DataFrame:
    """
    Generates recommendations based on user favorites.
    Preferred logic: use ML KNN cosine model (ml/KNN_cosine.pkl) when dependencies are available.
    Fallback logic: cosine similarity on keyword/genre/language tokens.
    """
    if not favorites or "imdb_key" not in df.columns or df.empty:
        return df.head(0)

    model = _load_knn_model(str(_get_knn_model_path()))
    if model is not None and hasattr(model, "kneighbors") and hasattr(model, "_fit_X"):
        key_to_index = _build_key_to_index(df)
        fav_indices = [key_to_index.get(str(k)) for k in set(map(str, favorites))]
        fav_indices = [i for i in fav_indices if i is not None]
        if fav_indices:
            k = max(int(n) + 20, 30)
            k = min(k, len(df))

            scores: dict[int, float] = {}
            for i in fav_indices:
                try:
                    distances, indices = model.kneighbors(model._fit_X[int(i)], n_neighbors=k)
                except Exception:
                    scores = {}
                    break

                idxs = list(indices[0])
                dists = list(distances[0])
                for j, dist in zip(idxs, dists):
                    if j in fav_indices:
                        continue
                    # For cosine metric, sklearn returns cosine distance in [0,2]. Similarity ~ 1 - distance.
                    sim = 1.0 - float(dist)
                    prev = scores.get(int(j))
                    if prev is None or sim > prev:
                        scores[int(j)] = sim

            if scores:
                ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
                top_idx = [idx for idx, _ in ranked[: int(n) * 3]]
                out = df.loc[top_idx].copy()
                out["wf_reco_score"] = [scores.get(int(i), 0.0) for i in out.index.tolist()]

                sort_cols = ["wf_reco_score"]
                for col in ("score_global", "popularity", "num_voted_users"):
                    if col in out.columns:
                        sort_cols.append(col)

                out = out.sort_values(sort_cols, ascending=[False] * len(sort_cols))
                out = out[~out["imdb_key"].astype(str).isin(set(map(str, favorites)))].copy()
                if "imdb_key" in out.columns:
                    out = out.drop_duplicates(subset=["imdb_key"], keep="first")
                    indices_retenus = []
                    premiers_mots = []
                    for row in out.itertuples():
                        titre = row.movie_title
                        mots = str(titre).split()
                        if not mots:
                            continue
                        premier_mot = mots[0]
                        if premier_mot not in premiers_mots:
                            indices_retenus.append(row.Index)
                            premiers_mots.append(premier_mot)
                        if len(indices_retenus) == int(n):
                            break
                return out.loc[indices_retenus]
                #return out.head(int(n))

    return _recommend_with_cosine_keywords(df, favorites, n=int(n))


def get_similar_movies(df: pd.DataFrame, imdb_key: str, n: int = 10) -> pd.DataFrame:
    imdb_key = str(imdb_key).strip()
    if not imdb_key:
        return df.head(0)
    return get_recommendations_from_favorites(df, {imdb_key}, n=int(n))


def get_recommender_info() -> tuple[str, str | None]:
    """
    Returns (backend, reason).

    backend:
      - "knn_cosine": the ML model is loaded and used.
      - "fallback": keyword-based cosine fallback is used.
    """
    model_path = _get_knn_model_path()
    if not model_path.exists():
        return "fallback", f"Modèle introuvable: {model_path.name}"

    model = _load_knn_model(str(model_path))
    if model is not None:
        return "knn_cosine", None

    try:
        import joblib  # noqa: F401
    except Exception:
        return "fallback", "Dépendance manquante: joblib"

    try:
        import sklearn  # noqa: F401
    except Exception:
        return "fallback", "Dépendance manquante: scikit-learn"

    try:
        import scipy  # noqa: F401
    except Exception:
        return "fallback", "Dépendance manquante: scipy"

    return "fallback", "Impossible de charger le modèle (versions incompatibles ?)"
