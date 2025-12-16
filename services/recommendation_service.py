import pandas as pd


def get_recommendations_from_favorites(df: pd.DataFrame, favorites: set[str], n: int = 10) -> pd.DataFrame:
    """
    Generates recommendations based on user favorites.
    Logic: Find movies with same main genre as favorites, excluding the favorites themselves.
    """
    if not favorites or "imdb_key" not in df.columns:
        return df.head(0)

    fav_df = df[df["imdb_key"].astype(str).isin(
        set(map(str, favorites)))].copy()
    if fav_df.empty or "genre_main" not in fav_df.columns:
        return df.head(0)

    genres = [g for g in fav_df["genre_main"].dropna().tolist()
              if str(g).strip()]
    if not genres:
        return df.head(0)

    candidates = df[
        (df["genre_main"].isin(genres)) & (
            ~df["imdb_key"].astype(str).isin(set(map(str, favorites))))
    ].copy()

    sort_cols = [c for c in ["score_global", "popularity",
                             "num_voted_users"] if c in candidates.columns]
    if sort_cols:
        candidates = candidates.sort_values(
            sort_cols, ascending=[False] * len(sort_cols))

    if "imdb_key" in candidates.columns:
        candidates = candidates.drop_duplicates(
            subset=["imdb_key"], keep="first")

    return candidates.head(n)
