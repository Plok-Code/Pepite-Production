from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

import pandas as pd

from utils.text import normalize_text


@dataclass(frozen=True)
class SearchResult:
    df: pd.DataFrame
    query: str
    query_norm: str


def _compact(text: str) -> str:
    return (text or "").replace(" ", "")


def _score_title(query_norm: str, title_norm: str) -> float:
    q = _compact(query_norm)
    t = _compact(title_norm)
    if not q or not t:
        return 0.0

    if q in t:
        return 1.0

    tokens = query_norm.split()
    if tokens:
        token_hits = sum(1 for tok in tokens if tok and tok in title_norm)
        token_score = token_hits / len(tokens)
    else:
        token_score = 0.0

    sm = SequenceMatcher(None, q, t)
    longest = sm.find_longest_match(0, len(q), 0, len(t)).size
    partial = longest / len(q)
    ratio = sm.ratio()

    # Heuristic mix: works well for partial titles + small typos.
    return max(0.55 * token_score + 0.45 * partial, 0.35 * ratio + 0.65 * partial)


def search_movies(df: pd.DataFrame, query: str, limit: int = 50) -> SearchResult:
    raw = "" if query is None else str(query).strip()
    q_norm = normalize_text(raw)
    if len(q_norm) < 2 or df.empty:
        return SearchResult(df=df.iloc[0:0].copy(), query=raw, query_norm=q_norm)

    title_col = "title_search" if "title_search" in df.columns else "movie_title_clean"
    titles = df[title_col].fillna("").astype(str)

    q_compact = _compact(q_norm)
    if len(q_compact) <= 3:
        # Very short queries: avoid overly fuzzy results.
        title_compact = titles.str.replace(" ", "", regex=False)
        mask = title_compact.str.contains(q_compact, na=False, regex=False)
        out = df[mask].copy()
        if out.empty:
            return SearchResult(df=out, query=raw, query_norm=q_norm)
        out["wf_search_score"] = 1.0
    else:
        scores = titles.map(lambda title: _score_title(q_norm, normalize_text(title)))
        out = df[scores >= 0.42].copy()
        if out.empty:
            # Fallback: keep best candidates even below threshold.
            out = df.copy()
        out["wf_search_score"] = scores.loc[out.index].astype(float)

    sort_cols: list[str] = ["wf_search_score"]
    for col in ("score_global", "popularity", "num_voted_users"):
        if col in out.columns:
            sort_cols.append(col)

    out = out.sort_values(sort_cols, ascending=[False] * len(sort_cols))
    out = out.reset_index(drop=True).head(int(limit))
    return SearchResult(df=out, query=raw, query_norm=q_norm)

