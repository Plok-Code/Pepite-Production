import pandas as pd
import streamlit as st
from pathlib import Path

from utils.text import normalize_text
from utils.i18n import get_current_language


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
        else (
            (Path(__file__).resolve().parent.parent / "df_pret_bis_fr.csv")
            if get_current_language() == "fr"
            and (Path(__file__).resolve().parent.parent / "df_pret_bis_fr.csv").exists()
            else (Path(__file__).resolve().parent.parent / "df_pret_bis.csv")
        )
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

    # Display-only translated fields (do not break filtering/grouping on original columns)
    if get_current_language() == "fr":
        if "Plot_fr" in df.columns and "Plot" in df.columns:
            df["Plot_display"] = df["Plot_fr"].fillna(df["Plot"])
        if "genres_fr" in df.columns and "genres" in df.columns:
            df["genres_display"] = df["genres_fr"].fillna(df["genres"])
        if "genre_main_fr" in df.columns and "genre_main" in df.columns:
            df["genre_main_display"] = df["genre_main_fr"].fillna(df["genre_main"])
        if "language_fr" in df.columns and "language" in df.columns:
            df["language_display"] = df["language_fr"].fillna(df["language"])
        if "country_name_fr" in df.columns and "country_name" in df.columns:
            df["country_display"] = df["country_name_fr"].fillna(df["country_name"])
        elif "country_main" in df.columns:
            df["country_display"] = df["country_main"]
    else:
        if "Plot" in df.columns:
            df["Plot_display"] = df["Plot"]
        if "genres" in df.columns:
            df["genres_display"] = df["genres"]
        if "genre_main" in df.columns:
            df["genre_main_display"] = df["genre_main"]
        if "language" in df.columns:
            df["language_display"] = df["language"]
        if "country_name" in df.columns:
            df["country_display"] = df["country_name"]
    return df
