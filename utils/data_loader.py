import pandas as pd
import streamlit as st
from pathlib import Path

from utils.text import normalize_text


def _minmax_norm(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce")
    min_value = series.min()
    max_value = series.max()
    if pd.isna(min_value) or pd.isna(max_value) or min_value == max_value:
        return pd.Series(0.0, index=series.index)
    return (series - min_value) / (max_value - min_value)


@st.cache_data
def load_movies(path: str | Path | None = None) -> pd.DataFrame:
    csv_path = (
        Path(path)
        if path is not None
        else Path(__file__).resolve().parent.parent / "df_pret_bis.csv"
    )
    df = pd.read_csv(csv_path)

    df["movie_title_clean"] = df["movie_title"].fillna("").astype(str).str.strip()
    df["title_lower"] = df["movie_title_clean"].str.lower()
    df["title_search"] = df["movie_title_clean"].map(normalize_text)

    if "genre_main" in df.columns:
        df["genre_main_lower"] = df["genre_main"].fillna("").astype(str).str.lower()

    for col in ("imdb_score", "popularity", "score_global"):
        if col in df.columns:
            df[f"{col}_norm"] = _minmax_norm(df[col])
    return df
