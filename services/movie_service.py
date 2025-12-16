import pandas as pd
from utils.app_config import W_QUALITY, W_POPULARITY, W_GLOBAL


def get_featured_movies(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    df_tmp = df.copy()
    for col in ("imdb_score_norm", "popularity_norm", "score_global_norm"):
        if col not in df_tmp.columns:
            df_tmp[col] = 0.0

    df_tmp["featured_score"] = (
        W_QUALITY * df_tmp["imdb_score_norm"]
        + W_POPULARITY * df_tmp["popularity_norm"]
        + W_GLOBAL * df_tmp["score_global_norm"]
    )
    return df_tmp.sort_values(by="featured_score", ascending=False).head(n)


def get_blockbuster(df: pd.DataFrame, n: int = 1) -> pd.DataFrame:
    if "budget" not in df.columns:
        return df.head(0)

    df_tmp = df.copy()
    if "budget_is_imputed" in df_tmp.columns:
        non_imputed = df_tmp[df_tmp["budget_is_imputed"] == 0]
        if not non_imputed.empty:
            df_tmp = non_imputed

    df_tmp = df_tmp[df_tmp["budget"].notna()]
    return df_tmp.sort_values(by="budget", ascending=False).head(n)


def get_underrated_gems(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    if "num_voted_users" not in df.columns or "score_global" not in df.columns:
        return df.head(0)

    df_tmp = df.copy()
    df_tmp = df_tmp[df_tmp["num_voted_users"] > 1000].copy()
    df_tmp["gem_score"] = df_tmp["score_global"] / \
        df_tmp["num_voted_users"] ** 0.2
    return df_tmp.sort_values(by="gem_score", ascending=False).head(n)


def get_niche_movies(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    if "num_voted_users" not in df.columns or "score_global" not in df.columns:
        return df.head(0)

    df_tmp = df.copy()
    df_tmp = df_tmp[df_tmp["num_voted_users"].notna(
    ) & df_tmp["score_global"].notna()].copy()
    df_tmp = df_tmp[df_tmp["num_voted_users"] >= 100]

    thresholds = [1000, 2000, 5000, 10000, float("inf")]
    for threshold in thresholds:
        candidates = df_tmp[df_tmp["num_voted_users"] <= threshold]
        if len(candidates) >= n:
            df_tmp = candidates
            break

    return df_tmp.sort_values(
        by=["score_global", "num_voted_users"], ascending=[False, True]
    ).head(n)


def exclude_keys(df: pd.DataFrame, used_keys: set[str]) -> pd.DataFrame:
    if not used_keys or "imdb_key" not in df.columns:
        return df
    return df[~df["imdb_key"].isin(used_keys)]
