from __future__ import annotations

import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from utils.settings import get_recommender_model
from utils.text import normalize_text


_KNN_MODELS_DIR = Path(__file__).resolve().parent.parent / "ml"
_MAX_PER_FRANCHISE_DEFAULT = 2

_TITLE_STOPWORDS = {
    # Articles / determiners
    "the",
    "a",
    "an",
    "le",
    "la",
    "les",
    "un",
    "une",
    "des",
    "du",
    "de",
    "d",
    "l",
    # Conjunctions / prepositions (common in titles)
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "at",
    "for",
    "with",
    "from",
    "by",
    "into",
    "over",
    "under",
    "between",
    "vs",
    "versus",
    "et",
    "ou",
    "en",
    "au",
    "aux",
    "sur",
    "dans",
    "par",
    "pour",
    "avec",
    "sans",
    "chez",
}

_ROMAN_NUMERALS = {
    "ii",
    "iii",
    "iv",
    "vi",
    "vii",
    "viii",
    "ix",
    "xi",
    "xii",
    "xiii",
    "xiv",
    "xv",
    "xvi",
    "xvii",
    "xviii",
    "xix",
    "xx",
}

_SEQUEL_WORDS = {
    "part",
    "episode",
    "chapter",
    "volume",
    "vol",
    "season",
    "saison",
    "partie",
    "chapitre",
}

_SEQUEL_PREFIX_RE = re.compile(
    r"^(?:part|episode|chapter|season|saison|volume|vol|partie|chapitre)[0-9]+$"
)
_ORDINAL_RE = re.compile(r"^[0-9]+(?:st|nd|rd|th)$")

_FIRST_CORE_TOKEN_COUNTS: dict[str, int] | None = None
_FIRST_CORE_TOKEN_COUNTS_N: int | None = None
_SAFE_SINGLE_TOKEN_MAX_FREQ = 12


def _is_sequel_marker(token: str) -> bool:
    tok = (token or "").strip().lower()
    if not tok:
        return False
    if tok.isdigit():
        return True
    if tok in _ROMAN_NUMERALS:
        return True
    if tok in _SEQUEL_WORDS:
        return True
    if _SEQUEL_PREFIX_RE.match(tok) is not None:
        return True
    if _ORDINAL_RE.match(tok) is not None:
        return True
    return False


def _strip_sequel_suffix(tokens: list[str]) -> list[str]:
    if not tokens:
        return []
    out = list(tokens)
    while out and _is_sequel_marker(out[-1]):
        out.pop()
    return out or list(tokens)


def _title_norm_series(df: pd.DataFrame) -> pd.Series:
    if "title_search" in df.columns:
        return df["title_search"].fillna("").astype(str)
    if "movie_title_clean" in df.columns:
        return df["movie_title_clean"].fillna("").astype(str).map(normalize_text)
    if "movie_title" in df.columns:
        return df["movie_title"].fillna("").astype(str).map(normalize_text)
    return pd.Series([""] * len(df), index=df.index)


def _core_title_tokens(tokens: list[str]) -> list[str]:
    cleaned = [t for t in tokens if t and t not in _TITLE_STOPWORDS]
    core = [t for t in cleaned if not _is_sequel_marker(t)]
    return core or cleaned


def _first_core_token_counts(df: pd.DataFrame) -> dict[str, int]:
    global _FIRST_CORE_TOKEN_COUNTS, _FIRST_CORE_TOKEN_COUNTS_N

    n = int(len(df))
    if _FIRST_CORE_TOKEN_COUNTS is not None and _FIRST_CORE_TOKEN_COUNTS_N == n:
        return _FIRST_CORE_TOKEN_COUNTS

    title_norm = _title_norm_series(df)
    first_tokens: list[str] = []
    for raw in title_norm.tolist():
        tokens = str(raw).split()
        core = _core_title_tokens(tokens)
        first_tokens.append(core[0] if core else "")

    counts = Counter(t for t in first_tokens if t)
    _FIRST_CORE_TOKEN_COUNTS = dict(counts)
    _FIRST_CORE_TOKEN_COUNTS_N = n
    return _FIRST_CORE_TOKEN_COUNTS


def _is_safe_single_token_franchise_key(token: str, full_df: pd.DataFrame | None) -> bool:
    tok = (token or "").strip().lower()
    if len(tok) < 4:
        return False
    if tok.isdigit():
        return False
    if full_df is None or full_df.empty:
        return True
    return _first_core_token_counts(full_df).get(tok, 0) <= _SAFE_SINGLE_TOKEN_MAX_FREQ


def _compute_franchise_keys(candidates: pd.DataFrame, full_df: pd.DataFrame | None = None) -> pd.Series:
    title_norm = _title_norm_series(candidates)

    base_keys: list[str] = []
    key2_list: list[str] = []
    key1_list: list[str] = []
    for raw in title_norm.tolist():
        tokens = str(raw).split()
        tokens = _strip_sequel_suffix(tokens)
        core = _core_title_tokens(tokens)
        base = " ".join(core).strip()
        key2 = " ".join(core[:2]).strip() if len(core) >= 2 else ""
        key1 = core[0] if core else ""
        base_keys.append(base)
        key2_list.append(key2)
        key1_list.append(key1)

    key2_counts = Counter(k for k in key2_list if k)
    key1_counts = Counter(k for k in key1_list if k)

    final_keys: list[str] = []
    for base, key2, key1 in zip(base_keys, key2_list, key1_list):
        if key2 and key2_counts.get(key2, 0) >= 2:
            final_keys.append(key2)
            continue
        if (
            key1
            and key1_counts.get(key1, 0) >= 2
            and _is_safe_single_token_franchise_key(key1, full_df)
        ):
            final_keys.append(key1)
            continue
        final_keys.append(base or key2 or key1 or "")

    return pd.Series(final_keys, index=candidates.index)


def _limit_by_franchise(
    candidates: pd.DataFrame,
    n: int,
    max_per_franchise: int = _MAX_PER_FRANCHISE_DEFAULT,
    full_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if candidates.empty:
        return candidates

    n_int = int(n)
    if n_int <= 0:
        return candidates.head(0)

    keys = _compute_franchise_keys(candidates, full_df=full_df).tolist()
    counts: dict[str, int] = {}
    selected: list[int] = []

    for idx, key in zip(candidates.index.tolist(), keys):
        bucket = key or f"__{idx}"
        if counts.get(bucket, 0) >= int(max_per_franchise):
            continue
        counts[bucket] = counts.get(bucket, 0) + 1
        selected.append(int(idx))
        if len(selected) >= n_int:
            break

    if not selected:
        return candidates.head(0)
    return candidates.loc[selected].copy()


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

    n_int = int(n)
    pool = min(len(df), max(n_int * 60, 300))

    model = _load_knn_model(str(_get_knn_model_path()))
    if model is not None and hasattr(model, "kneighbors") and hasattr(model, "_fit_X"):
        key_to_index = _build_key_to_index(df)
        fav_indices = [key_to_index.get(str(k)) for k in set(map(str, favorites))]
        fav_indices = [i for i in fav_indices if i is not None]
        if fav_indices:
            scores: dict[int, float] = {}
            k = min(len(df), max(n_int * 25, 120))
            try:
                query = model._fit_X[fav_indices]
                distances, indices = model.kneighbors(query, n_neighbors=k)
            except Exception:
                distances = None
                indices = None

            if distances is not None and indices is not None:
                fav_set = set(map(int, fav_indices))
                for row_idxs, row_dists in zip(indices, distances):
                    for j, dist in zip(list(row_idxs), list(row_dists)):
                        if int(j) in fav_set:
                            continue
                        sim = 1.0 - float(dist)
                        prev = scores.get(int(j))
                        if prev is None or sim > prev:
                            scores[int(j)] = sim

            if scores:
                ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
                top_idx = [idx for idx, _ in ranked[:pool]]
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
                return _limit_by_franchise(
                    out,
                    n=n_int,
                    max_per_franchise=_MAX_PER_FRANCHISE_DEFAULT,
                    full_df=df,
                )

    fallback = _recommend_with_cosine_keywords(df, favorites, n=int(pool))
    return _limit_by_franchise(
        fallback,
        n=n_int,
        max_per_franchise=_MAX_PER_FRANCHISE_DEFAULT,
        full_df=df,
    )


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
