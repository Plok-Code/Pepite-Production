from __future__ import annotations

import numpy as np
import pandas as pd


_RATING_CANDIDATES = [
    "imdb_score",
    "vote_average",
    "rating",
    "score",
    "average_rating",
    "mean_rating",
]
_COUNT_CANDIDATES = [
    "num_voted_users",
    "vote_count",
    "rating_count",
    "num_ratings",
    "votes",
    "n_votes",
]


def _pick_first_existing(cols: list[str], candidates: list[str]) -> str | None:
    for c in candidates:
        if c in cols:
            return c
    return None


def categorize_movies(
    df: pd.DataFrame,
    *,
    min_votes: int = 5,
) -> tuple[pd.DataFrame, str | None, str | None]:
    """
    Adds 2 columns:
      - `vote_decile` (1..10 when computable)
      - `category`: Blockbuster / Pépite / Niche / Navet / Autre

    The rules follow the snippet provided by the user:
      - Navet: rating < 4
      - Blockbuster: rating > 8 and vote_decile in (9, 10)
      - Pépite: rating > 8 and vote_decile between 3 and 7
      - Niche: rating > 7 and vote_decile in (1, 2)

    Returns (df_with_categories, rating_col, count_col).
    """
    if df is None or df.empty:
        out = (df if df is not None else pd.DataFrame()).copy()
        out["vote_decile"] = np.nan
        out["category"] = "Autre"
        return out, None, None

    rating_col = _pick_first_existing(list(df.columns), _RATING_CANDIDATES)
    count_col = _pick_first_existing(list(df.columns), _COUNT_CANDIDATES)

    out = df.copy()
    out["vote_decile"] = np.nan
    out["category"] = "Autre"

    if rating_col is None or count_col is None:
        return out, rating_col, count_col

    out[rating_col] = pd.to_numeric(out[rating_col], errors="coerce")
    out[count_col] = pd.to_numeric(out[count_col], errors="coerce")

    eligible = out[rating_col].notna() & out[count_col].notna() & (out[count_col] >= int(min_votes))
    if not eligible.any():
        return out, rating_col, count_col

    work = out.loc[eligible, [rating_col, count_col]].copy()
    # qcut can return fewer than 10 bins when duplicates are present.
    work["vote_decile"] = pd.qcut(work[count_col], q=10, labels=False, duplicates="drop").astype(float) + 1
    work["category"] = "Autre"
    work.loc[work[rating_col] < 4, "category"] = "Navet"
    work.loc[(work[rating_col] > 8) & (work["vote_decile"].isin([9, 10])), "category"] = "Blockbuster"
    work.loc[
        (work[rating_col] > 8) & (work["vote_decile"].between(3, 7)),
        "category",
    ] = "Pépite"
    work.loc[(work[rating_col] > 7) & (work["vote_decile"].isin([1, 2])), "category"] = "Niche"

    out.loc[work.index, "vote_decile"] = work["vote_decile"]
    out.loc[work.index, "category"] = work["category"]

    return out, rating_col, count_col


def sample_rows(df: pd.DataFrame, *, n: int, seed: int) -> pd.DataFrame:
    if df is None or df.empty or n <= 0:
        return df.iloc[0:0].copy() if df is not None else pd.DataFrame()
    n = min(int(n), int(len(df)))
    return df.sample(n=n, random_state=int(seed)).reset_index(drop=True)

