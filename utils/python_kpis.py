from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


_PRIMARY = "#FFB020"
_BG = "#0B0F17"
_SURFACE = "#141C2B"
_GRID = "#25324A"
_TEXT = "#EAF0FF"
_MUTED = "#A7B3CC"
_SUCCESS = "#2BD576"
_DANGER = "#FF3B3B"


KPI_ID = Literal["kpi_prefs", "kpi_1", "kpi_3", "kpi_4", "kpi_5", "kpi_6"]


def _empty_figure(title: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        height=420,
        paper_bgcolor=_BG,
        plot_bgcolor=_SURFACE,
        font=dict(family="Inter", color=_TEXT),
        title=dict(text=title, x=0.5, font=dict(size=22)),
        margin=dict(t=80, l=60, r=60, b=60),
    )
    fig.add_annotation(
        text="Aucune donnée",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=18, color=_MUTED),
    )
    return fig


def _apply_wildflix_layout(fig: go.Figure, title: str, height: int) -> go.Figure:
    fig.update_layout(
        height=int(height),
        paper_bgcolor=_BG,
        plot_bgcolor=_SURFACE,
        font=dict(family="Inter", color=_TEXT),
        title=dict(text=title, x=0.5, font=dict(size=26)),
        showlegend=False,
        margin=dict(t=100, l=80, r=80, b=80),
    )
    fig.update_annotations(font=dict(family="Inter", size=18, color=_TEXT))
    fig.update_xaxes(
        color=_MUTED,
        gridcolor=_GRID,
        title_font=dict(size=16, family="Inter", color=_MUTED),
        tickfont=dict(size=14, family="Inter", color=_MUTED),
    )
    fig.update_yaxes(
        color=_MUTED,
        gridcolor=_GRID,
        title_font=dict(size=16, family="Inter", color=_MUTED),
        tickfont=dict(size=14, family="Inter", color=_MUTED),
    )
    return fig


def _dedupe_movies(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df.iloc[0:0].copy()
    if "imdb_key" in df.columns:
        return df.drop_duplicates(subset=["imdb_key"], keep="first").copy()
    return df.drop_duplicates(keep="first").copy()


def _explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if "genres" not in df.columns:
        return df.assign(genre_name="")

    out = df.copy()
    out["genre_name"] = out["genres"].fillna("").astype(str).str.split("|")
    out = out.explode("genre_name", ignore_index=True)
    out["genre_name"] = out["genre_name"].fillna("").astype(str).str.strip()
    out = out[out["genre_name"] != ""]
    return out


def _explode_actors(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    cols = []
    for i in (1, 2, 3):
        name_col = f"actor_{i}_name"
        like_col = f"actor_{i}_facebook_likes"
        if name_col in df.columns:
            cols.append((name_col, like_col if like_col in df.columns else None))

    if not cols:
        return df.assign(actor_name="", actor_facebook_likes=np.nan)

    frames = []
    for name_col, like_col in cols:
        tmp = df.copy()
        tmp = tmp.rename(columns={name_col: "actor_name"})
        if like_col:
            tmp = tmp.rename(columns={like_col: "actor_facebook_likes"})
        else:
            tmp["actor_facebook_likes"] = np.nan
        tmp["actor_name"] = tmp["actor_name"].fillna("").astype(str).str.strip()
        tmp = tmp[tmp["actor_name"] != ""]
        frames.append(tmp)

    if not frames:
        return df.assign(actor_name="", actor_facebook_likes=np.nan)
    return pd.concat(frames, ignore_index=True)


def kpi_prefs(df_movies: pd.DataFrame) -> go.Figure:
    """
    Preferences KPI: likes by genre and by language.

    Expects a "likes" dataset (one row per like) already merged with movies metadata.
    """
    if df_movies is None or df_movies.empty:
        return _empty_figure("Préférences utilisateurs du site")

    work = df_movies.copy()

    genre_counts = pd.DataFrame(columns=["genre_main", "likes"])
    if "genre_main" in work.columns:
        genre_counts = (
            work.groupby("genre_main", dropna=False)
            .size()
            .reset_index(name="likes")
            .assign(genre_main=lambda d: d["genre_main"].fillna("Unknown").astype(str))
            .sort_values("likes", ascending=False)
            .head(12)
        )

    lang_counts = pd.DataFrame(columns=["language", "likes"])
    if "language" in work.columns:
        lang_counts = (
            work.groupby("language", dropna=False)
            .size()
            .reset_index(name="likes")
            .assign(language=lambda d: d["language"].fillna("Unknown").astype(str))
            .sort_values("likes", ascending=False)
            .head(12)
        )

    if genre_counts.empty and lang_counts.empty:
        return _empty_figure("Préférences utilisateurs du site")

    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "bar"}, {"type": "bar"}]],
        subplot_titles=("Likes par genre", "Likes par langue"),
        horizontal_spacing=0.12,
    )

    if not genre_counts.empty:
        fig.add_trace(
            go.Bar(
                x=genre_counts["genre_main"],
                y=genre_counts["likes"],
                marker_color=_PRIMARY,
                text=genre_counts["likes"],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Likes: %{y}<extra></extra>",
            ),
            row=1,
            col=1,
        )

    if not lang_counts.empty:
        fig.add_trace(
            go.Bar(
                x=lang_counts["language"],
                y=lang_counts["likes"],
                marker_color=_PRIMARY,
                text=lang_counts["likes"],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Likes: %{y}<extra></extra>",
            ),
            row=1,
            col=2,
        )

    fig.update_yaxes(title_text="Likes", row=1, col=1)
    fig.update_yaxes(title_text="Likes", row=1, col=2)
    fig.update_xaxes(tickangle=45, row=1, col=1)
    fig.update_xaxes(tickangle=45, row=1, col=2)

    return _apply_wildflix_layout(fig, "Préférences utilisateurs du site", height=520)


def kpi_1_directors(df_movies: pd.DataFrame) -> go.Figure:
    df = _dedupe_movies(df_movies)
    if df.empty or "director_name" not in df.columns:
        return _empty_figure("KPI 1 — Réalisateurs")

    work = df.copy()
    work["director_name"] = work["director_name"].fillna("").astype(str).str.strip()
    work = work[(work["director_name"] != "") & (work["director_name"].str.lower() != "unknown")]
    if work.empty:
        return _empty_figure("KPI 1 — Réalisateurs")

    if "director_facebook_likes" not in work.columns:
        work["director_facebook_likes"] = np.nan

    stats = (
        work.groupby(["director_name", "director_facebook_likes"], dropna=False, as_index=False)
        .agg(nb_films=("director_name", "size"), avg_score=("score_global", "mean"))
    )
    stats["single_film"] = stats["nb_films"] == 1

    stats["avg_fb_likes"] = np.where(
        pd.to_numeric(stats["director_facebook_likes"], errors="coerce").notna(),
        (pd.to_numeric(stats["director_facebook_likes"], errors="coerce") / stats["nb_films"]).round(0),
        np.nan,
    )

    df_multi = stats[stats["nb_films"] >= 2].sort_values("avg_score", ascending=False).head(10)
    df_fb_top = stats.sort_values("director_facebook_likes", ascending=False).head(10)

    kpi_names = ["Total réalisateurs", "Score moyen", "1 film", "≥ 2 films"]
    kpi_values = [
        int(len(stats)),
        float(stats["avg_score"].mean()) if not stats.empty else 0.0,
        int(stats["single_film"].sum()),
        int(len(stats) - int(stats["single_film"].sum())),
    ]
    kpi_values_fmt = [kpi_values[0], round(kpi_values[1], 2), kpi_values[2], kpi_values[3]]

    table_df = (
        work.groupby("director_name", as_index=False)
        .agg(nb_films=("director_name", "size"), avg_score=("score_global", "mean"))
        .sort_values("nb_films", ascending=False)
        .head(15)
    )

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "table"}]],
        subplot_titles=[
            "Résumé KPI",
            "Top réalisateurs (≥2 films) — Score moyen",
            "Top Facebook Likes (réalisateurs)",
            "Top 15 — Volume de films",
        ],
        column_widths=[0.5, 0.5],
        row_heights=[0.5, 0.5],
        vertical_spacing=0.15,
        horizontal_spacing=0.10,
    )

    fig.add_trace(
        go.Bar(
            x=kpi_names,
            y=kpi_values_fmt,
            text=kpi_values_fmt,
            textposition="outside",
            marker_color=[_PRIMARY, _SUCCESS, _PRIMARY, _SUCCESS],
            hovertemplate="%{x}: %{y}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    if not df_multi.empty:
        fig.add_trace(
            go.Bar(
                x=df_multi["director_name"],
                y=df_multi["avg_score"].round(2),
                text=df_multi["avg_score"].round(2),
                textposition="outside",
                marker_color=_PRIMARY,
                hovertemplate=(
                    "Réalisateur: %{x}<br>"
                    "Score moyen: %{y:.2f}<br>"
                    "Nb films: %{customdata[0]}<br>"
                    "Total FB Likes: %{customdata[1]}<br>"
                    "FB Likes/film: %{customdata[2]}<extra></extra>"
                ),
                customdata=df_multi[["nb_films", "director_facebook_likes", "avg_fb_likes"]].values,
            ),
            row=1,
            col=2,
        )

    if not df_fb_top.empty:
        fig.add_trace(
            go.Bar(
                x=df_fb_top["director_name"],
                y=df_fb_top["director_facebook_likes"],
                text=df_fb_top["director_facebook_likes"],
                textposition="outside",
                marker_color=_PRIMARY,
                hovertemplate=(
                    "Réalisateur: %{x}<br>"
                    "Total FB Likes: %{y:,.0f}<br>"
                    "Nb films: %{customdata}<extra></extra>"
                ),
                customdata=df_fb_top["nb_films"],
            ),
            row=2,
            col=1,
        )

    fig.add_trace(
        go.Table(
            columnwidth=[50, 15, 20],
            header=dict(
                values=["<b>Réalisateur</b>", "<b>Nb films</b>", "<b>Score moyen</b>"],
                fill_color=_SURFACE,
                font=dict(color=_TEXT, size=14),
                align="left",
            ),
            cells=dict(
                values=[
                    table_df["director_name"],
                    table_df["nb_films"],
                    table_df["avg_score"].round(2),
                ],
                fill_color=_BG,
                font=dict(color=_TEXT, size=13),
                align="left",
                height=30,
            ),
        ),
        row=2,
        col=2,
    )

    fig.update_yaxes(title_text="Valeurs", automargin=True, row=1, col=1)
    fig.update_yaxes(title_text="Score moyen", automargin=True, row=1, col=2)
    fig.update_yaxes(title_text="Facebook Likes", automargin=True, row=2, col=1)
    fig.update_xaxes(tickangle=45, row=1, col=2)
    fig.update_xaxes(tickangle=45, row=2, col=1)

    return _apply_wildflix_layout(fig, "KPI 1 — Réalisateurs : score & popularité Facebook", height=900)




def kpi_3_actors(df_movies: pd.DataFrame) -> go.Figure:
    df = _dedupe_movies(df_movies)
    df = _explode_actors(df)
    if df.empty or "actor_name" not in df.columns:
        return _empty_figure("KPI 3 — Acteurs")

    work = df.copy()
    work["actor_name"] = work["actor_name"].fillna("").astype(str).str.strip()
    work = work[(work["actor_name"] != "") & (work["actor_name"].str.lower() != "unknown")]
    if work.empty:
        return _empty_figure("KPI 3 — Acteurs")

    for col in ("score_global", "actor_facebook_likes"):
        if col not in work.columns:
            work[col] = np.nan

    actor_stats = (
        work.groupby("actor_name", as_index=False)
        .agg(
            nb_films=("actor_name", "size"),
            score_moyen=("score_global", "mean"),
            fb_likes_total=("actor_facebook_likes", "sum"),
        )
    )

    # Keep the KPI useful even when the dataset is small (e.g. few likes).
    min_films = 3
    try:
        if int(actor_stats["nb_films"].max()) < min_films:
            min_films = 1
    except Exception:
        min_films = 1
    actor_stats = actor_stats[actor_stats["nb_films"] >= min_films]
    if actor_stats.empty:
        return _empty_figure("KPI 3 — Acteurs")

    top_fb_actor = actor_stats.sort_values("fb_likes_total", ascending=False).iloc[0]
    top_20_fb = actor_stats.sort_values("fb_likes_total", ascending=False).head(20)
    moyenne_top_20_likes = float(top_20_fb["fb_likes_total"].mean())

    top_score_df = actor_stats.sort_values("score_moyen", ascending=False).head(10)
    top_pop_df = actor_stats.sort_values("fb_likes_total", ascending=False).head(10)
    top_15_table = actor_stats.sort_values("nb_films", ascending=False).head(15)

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{"type": "indicator"}, {"type": "bar"}], [{"type": "bar"}, {"type": "table"}]],
        subplot_titles=(
            "Acteur #1 Facebook",
            "Top 10 — Score moyen",
            "Top 10 — Facebook likes (total)",
            "Top 15 — Nb de films",
        ),
        vertical_spacing=0.18,
    )

    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=float(top_fb_actor["fb_likes_total"]),
            number={
                "font": {"size": 46, "color": _PRIMARY},
                "valueformat": ",",
                "suffix": " likes",
            },
            delta={
                "reference": moyenne_top_20_likes,
                "valueformat": ",.0f",
                "suffix": " vs moy Top 20",
                "increasing": {"color": _SUCCESS},
                "decreasing": {"color": _DANGER},
            },
            title={
                "text": (
                    "<span style='font-size:14px;color:#A7B3CC'>Acteur n°1 Facebook</span>"
                    "<br><br>"
                    f"<span style='font-size:22px;font-weight:600'>{top_fb_actor['actor_name']}</span>"
                    "<br><span style='font-size:12px;color:#A7B3CC'>Diff. avec moy Top 20</span>"
                )
            },
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=top_score_df["actor_name"],
            y=top_score_df["score_moyen"].round(2),
            marker_color=_PRIMARY,
            text=top_score_df["score_moyen"].round(2),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Score moyen: %{y:.2f}<br>Nb films: %{customdata}<extra></extra>",
            customdata=top_score_df["nb_films"],
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Bar(
            x=top_pop_df["actor_name"],
            y=top_pop_df["fb_likes_total"],
            marker_color=_PRIMARY,
            text=top_pop_df["fb_likes_total"].round(0),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Facebook likes: %{y:,.0f}<br>Nb films: %{customdata}<extra></extra>",
            customdata=top_pop_df["nb_films"],
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Table(
            columnwidth=[55, 20, 25],
            header=dict(
                values=["<b>Acteur</b>", "<b>Nb films</b>", "<b>Score moyen</b>"],
                fill_color=_SURFACE,
                font=dict(color=_TEXT, size=14),
                align="left",
            ),
            cells=dict(
                values=[
                    top_15_table["actor_name"],
                    top_15_table["nb_films"],
                    top_15_table["score_moyen"].round(2),
                ],
                fill_color=_BG,
                font=dict(color=_TEXT, size=13),
                align="left",
                height=30,
            ),
        ),
        row=2,
        col=2,
    )

    fig.update_yaxes(title_text="Score moyen", row=1, col=2)
    fig.update_xaxes(tickangle=45, row=1, col=2)
    fig.update_xaxes(tickangle=45, row=2, col=1)
    return _apply_wildflix_layout(fig, "KPI 3 — Popularité & impact des acteurs", height=900)


def kpi_4_genre_decade(df_movies: pd.DataFrame) -> go.Figure:
    df = _dedupe_movies(df_movies)
    df = _explode_genres(df)
    if df.empty or "decade" not in df.columns:
        return _empty_figure("KPI 4 — Genres & décennie")

    work = df.copy()
    for col in ("score_global",):
        if col not in work.columns:
            work[col] = np.nan

    work = work.dropna(subset=["score_global"])
    if work.empty:
        return _empty_figure("KPI 4 — Genres & décennie")

    work["decile_score"] = pd.qcut(
        work["score_global"],
        q=10,
        labels=False,
        duplicates="drop",
    ).astype(float) + 1

    work["categorie"] = np.select(
        [
            work["decile_score"] <= 3,
            (work["decile_score"] >= 4) & (work["decile_score"] <= 5),
            work["decile_score"] >= 6,
        ],
        ["Exclu", "Pépite", "Blockbuster"],
        default="Exclu",
    )

    analysis = work[work["categorie"] != "Exclu"].copy()
    if analysis.empty:
        return _empty_figure("KPI 4 — Genres & décennie")

    total_films_tous = (
        int(_dedupe_movies(df_movies)["imdb_key"].nunique())
        if "imdb_key" in df_movies.columns
        else int(_dedupe_movies(df_movies).shape[0])
    )
    total_films_analyse = (
        int(analysis["imdb_key"].nunique()) if "imdb_key" in analysis.columns else int(analysis.shape[0])
    )

    genre_decade_stats = (
        analysis.groupby(["decade", "genre_name", "categorie"], as_index=False)
        .agg(nb_films=("imdb_key", "nunique") if "imdb_key" in analysis.columns else ("genre_name", "size"))
    )

    pivot_blockbuster = (
        genre_decade_stats[genre_decade_stats["categorie"] == "Blockbuster"]
        .pivot_table(index="genre_name", columns="decade", values="nb_films", fill_value=0)
    )
    pivot_pepite = (
        genre_decade_stats[genre_decade_stats["categorie"] == "Pépite"]
        .pivot_table(index="genre_name", columns="decade", values="nb_films", fill_value=0)
    )

    top_genre_per_decade = (
        genre_decade_stats.groupby(["decade", "genre_name"], as_index=False)
        .agg(nb_films_total=("nb_films", "sum"))
        .sort_values(["decade", "nb_films_total"], ascending=[True, False])
        .groupby("decade", as_index=False)
        .head(5)
    )

    genre_le_plus_frequent = (
        genre_decade_stats.groupby("genre_name", as_index=True)["nb_films"].sum().idxmax()
        if not genre_decade_stats.empty
        else "-"
    )

    def _limit_heatmap(pivot: pd.DataFrame, n: int = 18) -> pd.DataFrame:
        if pivot.empty:
            return pivot
        keep = pivot.sum(axis=1).sort_values(ascending=False).head(int(n)).index
        return pivot.loc[keep]

    pivot_blockbuster = _limit_heatmap(pivot_blockbuster, n=18)
    pivot_pepite = _limit_heatmap(pivot_pepite, n=18)

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{"type": "indicator"}, {"type": "heatmap"}], [{"type": "bar"}, {"type": "heatmap"}]],
        subplot_titles=(
            "Focus Pépites & Blockbusters",
            "Blockbusters — Nb films par genre & décennie",
            "Top 5 genres par décennie (pépite + blockbuster)",
            "Pépites — Nb films par genre & décennie",
        ),
        vertical_spacing=0.18,
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=total_films_analyse,
            number={"font": {"size": 46, "color": _PRIMARY}, "suffix": " films"},
            title={
                "text": (
                    "<span style='font-size:14px;color:#A7B3CC'>Analyse sur pépites + blockbusters uniquement<br>"
                    f"(déciles 4 à 10 du score_global / total {total_films_tous} films)</span>"
                    "<br><br>"
                    f"<span style='font-size:22px;font-weight:600'>{genre_le_plus_frequent}</span>"
                    "<br><span style='font-size:12px;color:#A7B3CC'>Genre le plus fréquent</span>"
                )
            },
        ),
        row=1,
        col=1,
    )

    if not pivot_blockbuster.empty:
        fig.add_trace(
            go.Heatmap(
                z=pivot_blockbuster.values,
                x=[str(x) for x in pivot_blockbuster.columns.tolist()],
                y=pivot_blockbuster.index.tolist(),
                colorscale=[[0, _BG], [1, _PRIMARY]],
                text=pivot_blockbuster.values,
                texttemplate="%{text}",
                textfont={"size": 12},
                hovertemplate="Décennie: %{x}<br>Genre: %{y}<br>Nb blockbusters: %{z}<extra></extra>",
                colorbar=dict(
                    title=dict(text="Nb films", side="right"),
                    thickness=15,
                    len=0.45,
                    y=0.77,
                    yanchor="middle",
                ),
            ),
            row=1,
            col=2,
        )

    fig.add_trace(
        go.Bar(
            x=top_genre_per_decade["decade"].astype(str) + " — " + top_genre_per_decade["genre_name"],
            y=top_genre_per_decade["nb_films_total"],
            marker_color=_PRIMARY,
            text=top_genre_per_decade["nb_films_total"],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Nb films: %{y}<extra></extra>",
        ),
        row=2,
        col=1,
    )

    if not pivot_pepite.empty:
        fig.add_trace(
            go.Heatmap(
                z=pivot_pepite.values,
                x=[str(x) for x in pivot_pepite.columns.tolist()],
                y=pivot_pepite.index.tolist(),
                colorscale=[[0, _BG], [1, _PRIMARY]],
                text=pivot_pepite.values,
                texttemplate="%{text}",
                textfont={"size": 12},
                hovertemplate="Décennie: %{x}<br>Genre: %{y}<br>Nb pépites: %{z}<extra></extra>",
                colorbar=dict(
                    title=dict(text="Nb films", side="right"),
                    thickness=15,
                    len=0.45,
                    y=0.23,
                    yanchor="middle",
                ),
            ),
            row=2,
            col=2,
        )

    fig.update_xaxes(title_text="Décennie", row=1, col=2)
    fig.update_yaxes(title_text="Genre", row=1, col=2)
    fig.update_xaxes(title_text="Décennie — Genre", tickangle=45, row=2, col=1)
    fig.update_yaxes(title_text="Nombre de films", row=2, col=1)
    fig.update_xaxes(title_text="Décennie", row=2, col=2)
    fig.update_yaxes(title_text="Genre", row=2, col=2)

    return _apply_wildflix_layout(fig, "KPI 4 — Popularité des films par genre & décennie", height=900)


def kpi_5_duration(df_movies: pd.DataFrame) -> go.Figure:
    df = _dedupe_movies(df_movies)
    if df.empty or "duration" not in df.columns:
        return _empty_figure("KPI 5 — Durée")

    work = df.copy()
    for col in ("score_global", "duration"):
        if col not in work.columns:
            work[col] = np.nan

    work = work.dropna(subset=["score_global", "duration"])
    if work.empty:
        return _empty_figure("KPI 5 — Durée")

    work["decile_score"] = pd.qcut(
        work["score_global"],
        q=10,
        labels=False,
        duplicates="drop",
    ).astype(float) + 1
    work["categorie"] = np.select(
        [
            work["decile_score"] <= 3,
            (work["decile_score"] >= 4) & (work["decile_score"] <= 5),
            work["decile_score"] >= 6,
        ],
        ["Exclu", "Pépite", "Blockbuster"],
        default="Exclu",
    )

    bins = [-np.inf, 59, 89, 119, np.inf]
    labels = ["< 1h", "1h - 1h29", "1h30 - 1h59", "2h et +"]
    work["duree_cat"] = pd.cut(work["duration"], bins=bins, labels=labels)

    analysis = work[work["categorie"] != "Exclu"].copy()
    if analysis.empty:
        return _empty_figure("KPI 5 — Durée")

    top_by_duration = (
        analysis.sort_values("score_global", ascending=False)
        .groupby("duree_cat", observed=True)
        .first()
        .reset_index()
    )

    top_15_blockbuster = (
        analysis[analysis["categorie"] == "Blockbuster"]
        .sort_values("score_global", ascending=False)
        .head(15)
        .reset_index(drop=True)
    )
    top_15_pepite = (
        analysis[analysis["categorie"] == "Pépite"]
        .sort_values("score_global", ascending=False)
        .head(15)
        .reset_index(drop=True)
    )

    table_empilee = (
        pd.concat(
            [
                top_15_blockbuster.assign(rank=range(1, len(top_15_blockbuster) + 1)),
                top_15_pepite.assign(rank=range(1, len(top_15_pepite) + 1)),
            ],
            ignore_index=True,
        )
        .sort_values(["rank", "categorie"], kind="stable")
        .drop(columns="rank")
    )
    table_empilee["Type"] = table_empilee["categorie"].map({"Blockbuster": "Blockbuster", "Pépite": "Pépite"})
    table_empilee = table_empilee[["Type", "duree_cat", "movie_title", "duration", "score_global"]].reset_index(
        drop=True
    )

    repartition = analysis.groupby("duree_cat", observed=False).size()

    fig = make_subplots(
        rows=2,
        cols=4,
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "table", "colspan": 2}, None, {"type": "bar", "colspan": 2}, None],
        ],
        subplot_titles=(
            "< 1h",
            "1h - 1h29",
            "1h30 - 1h59",
            "2h et +",
            "Top 30 alternés (Blockbuster / Pépite)",
            "",
            "Répartition des films analysés par durée",
            "",
        ),
        row_heights=[0.5, 0.5],
        vertical_spacing=0.06,
    )

    for i, row in top_by_duration.iterrows():
        col = int(i) + 1
        duration_val = row.get("duration")
        duration_txt = f"{int(duration_val)} min" if pd.notna(duration_val) else "N/A"
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=float(row["score_global"]),
                number={"font": {"size": 40, "color": _PRIMARY}, "suffix": " pts"},
                title={
                    "text": (
                        f"<span style='font-size:18px;font-weight:600'>{row.get('movie_title','')}</span>"
                        f"<br><span style='font-size:12px;color:#A7B3CC'>{duration_txt}</span>"
                    ),
                    "align": "center",
                },
            ),
            row=1,
            col=col,
        )

    fig.add_trace(
        go.Table(
            columnwidth=[10, 25, 45, 15, 15],
            header=dict(
                values=["Type", "Catégorie durée", "Film", "Durée (min)", "Score"],
                fill_color=_SURFACE,
                font=dict(color=_TEXT, size=14),
                align="left",
            ),
            cells=dict(
                values=[
                    table_empilee["Type"],
                    table_empilee["duree_cat"].astype(str),
                    table_empilee["movie_title"],
                    table_empilee["duration"].astype(int),
                    table_empilee["score_global"].round(2),
                ],
                fill_color=_BG,
                font=dict(color=_TEXT, size=13),
                align="left",
                height=28,
            ),
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=repartition.index.astype(str),
            y=repartition.values,
            marker_color=_PRIMARY,
            text=repartition.values,
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Nb films: %{y}<extra></extra>",
        ),
        row=2,
        col=3,
    )

    fig.update_yaxes(title_text="Nb films", row=2, col=3)
    return _apply_wildflix_layout(fig, "KPI 5 — Meilleurs films selon leur durée", height=800)


def kpi_6_content_rating(df_movies: pd.DataFrame) -> go.Figure:
    df = _dedupe_movies(df_movies)
    if df.empty or "content_rating" not in df.columns:
        return _empty_figure("KPI 6 — Classification âge")

    work = df.copy()
    for col in ("score_global", "content_rating"):
        if col not in work.columns:
            work[col] = np.nan

    work = work.dropna(subset=["score_global"])
    if work.empty:
        return _empty_figure("KPI 6 — Classification âge")

    work["content_rating"] = work["content_rating"].fillna("Unknown").astype(str).str.strip()
    work["decile_score"] = pd.qcut(
        work["score_global"],
        q=10,
        labels=False,
        duplicates="drop",
    ).astype(float) + 1

    work["categorie"] = np.select(
        [
            work["decile_score"] <= 3,
            (work["decile_score"] >= 4) & (work["decile_score"] <= 5),
            work["decile_score"] >= 6,
        ],
        ["Exclu", "Pépite", "Blockbuster"],
        default="Exclu",
    )

    analysis = work[work["categorie"] != "Exclu"].copy()
    if analysis.empty:
        return _empty_figure("KPI 6 — Classification âge")

    nb_films_analyse = int(analysis["imdb_key"].nunique()) if "imdb_key" in analysis.columns else int(analysis.shape[0])
    nb_blockbusters = int((analysis["categorie"] == "Blockbuster").sum())
    nb_pepites = int((analysis["categorie"] == "Pépite").sum())

    repartition_rating = analysis.groupby("content_rating", observed=False).size().sort_values(ascending=False)
    score_moyen_par_rating = (
        analysis.groupby("content_rating", observed=False)["score_global"].mean().round(2).sort_values(ascending=False)
    )

    def _top3(df_sub: pd.DataFrame) -> pd.DataFrame:
        return (
            df_sub.sort_values(["content_rating", "score_global"], ascending=[True, False])
            .groupby("content_rating", observed=False)
            .head(3)
            .sort_values(["content_rating", "score_global"], ascending=[True, False])
        )

    top3_blockbuster = _top3(analysis[analysis["categorie"] == "Blockbuster"])
    top3_pepite = _top3(analysis[analysis["categorie"] == "Pépite"])

    top_films_table = pd.concat(
        [
            top3_blockbuster[["movie_title", "score_global", "content_rating"]],
            top3_pepite[["movie_title", "score_global", "content_rating"]],
        ],
        ignore_index=True,
    ).sort_values("score_global", ascending=False)

    best_unrated_title = "-"
    best_unrated_score = None
    unrated = analysis[analysis["content_rating"].str.lower() == "unrated"]
    if not unrated.empty:
        best_unrated = unrated.sort_values("score_global", ascending=False).iloc[0]
        best_unrated_title = str(best_unrated.get("movie_title", "-"))
        best_unrated_score = float(best_unrated.get("score_global", 0.0))

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{"type": "indicator"}, {"type": "bar"}], [{"type": "bar"}, {"type": "table"}]],
        subplot_titles=(
            "Focus classification âge",
            "Répartition des films analysés",
            "Score moyen par classification",
            "Top films (score global)",
        ),
        vertical_spacing=0.15,
    )

    extra_unrated = (
        f"Meilleur film Unrated (Score {best_unrated_score:.2f})"
        if best_unrated_score is not None
        else "Aucun film Unrated dans cette sélection"
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=nb_films_analyse,
            number={"font": {"size": 46, "color": _PRIMARY}, "suffix": " films"},
            title={
                "text": (
                    f"<span style='font-size:14px;color:#A7B3CC'>Pépites + Blockbusters analysés<br>"
                    f"({nb_blockbusters} blockbusters | {nb_pepites} pépites)</span>"
                    f"<br><br><span style='font-size:18px;font-weight:600'>{best_unrated_title}</span>"
                    f"<br><span style='font-size:12px;color:#A7B3CC'>{extra_unrated}</span>"
                )
            },
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=repartition_rating.index.astype(str),
            y=repartition_rating.values,
            marker_color=_PRIMARY,
            text=repartition_rating.values,
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Nb films: %{y}<extra></extra>",
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Bar(
            x=score_moyen_par_rating.index.astype(str),
            y=score_moyen_par_rating.values,
            marker_color=_PRIMARY,
            text=score_moyen_par_rating.values,
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Score moyen: %{y:.2f}<extra></extra>",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Table(
            columnwidth=[50, 20, 30],
            header=dict(
                values=["<b>Film</b>", "<b>Score global</b>", "<b>Classification</b>"],
                fill_color=_SURFACE,
                font=dict(color=_TEXT, size=14),
                align="left",
            ),
            cells=dict(
                values=[
                    top_films_table["movie_title"],
                    top_films_table["score_global"].round(2),
                    top_films_table["content_rating"],
                ],
                fill_color=_BG,
                font=dict(color=_TEXT, size=13),
                align="left",
                height=30,
            ),
        ),
        row=2,
        col=2,
    )

    fig.update_xaxes(tickangle=45, row=1, col=2)
    fig.update_xaxes(tickangle=45, row=2, col=1)
    return _apply_wildflix_layout(fig, "KPI 6 — Meilleurs films par classification âge", height=900)


def build_kpi_figure(kpi_id: KPI_ID, df_movies: pd.DataFrame) -> go.Figure:
    if kpi_id == "kpi_prefs":
        return kpi_prefs(df_movies)
    if kpi_id == "kpi_1":
        return kpi_1_directors(df_movies)
    if kpi_id == "kpi_3":
        return kpi_3_actors(df_movies)
    if kpi_id == "kpi_4":
        return kpi_4_genre_decade(df_movies)
    if kpi_id == "kpi_5":
        return kpi_5_duration(df_movies)
    if kpi_id == "kpi_6":
        return kpi_6_content_rating(df_movies)
    return _empty_figure("KPI")
