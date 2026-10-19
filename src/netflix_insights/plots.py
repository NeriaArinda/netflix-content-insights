"""Charts saved as PNG files for the report."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from . import analysis  # noqa: E402

MOVIE = "#3B6EA8"
SHOW = "#D9822B"
GRID = "#E5E5E5"


def _style(ax: plt.Axes, title: str) -> None:
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)


def additions_chart(df: pd.DataFrame, out: Path) -> Path:
    table = analysis.additions_per_year(df)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(table.index, table.get("Movie", 0), color=MOVIE, lw=2.5, label="Movies")
    ax.plot(table.index, table.get("TV Show", 0), color=SHOW, lw=2.5, label="TV shows")
    _style(ax, "Titles added to Netflix per year")
    ax.legend(frameon=False)
    return _save(fig, out / "additions_per_year.png")


def top_countries_chart(df: pd.DataFrame, out: Path, n: int = 10) -> Path:
    top = analysis.top_values(df, "country", n).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top.index, top.values, color=MOVIE)
    _style(ax, f"Top {n} producing countries")
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    return _save(fig, out / "top_countries.png")


def top_genres_chart(df: pd.DataFrame, out: Path, n: int = 12) -> Path:
    top = analysis.top_values(df, "listed_in", n).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.barh(top.index, top.values, color=MOVIE)
    _style(ax, f"Top {n} genres")
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    return _save(fig, out / "top_genres.png")


def movie_length_chart(df: pd.DataFrame, out: Path) -> Path:
    movies = df[(df["type"] == "Movie") & (df["duration_unit"] == "min")]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(movies["duration_value"].astype(float), bins=40, color=MOVIE)
    median = float(movies["duration_value"].median())
    ax.axvline(median, color=SHOW, lw=2, ls="--")
    ax.annotate(f"median {median:.0f} min", (median, ax.get_ylim()[1] * 0.9),
                xytext=(8, 0), textcoords="offset points", color=SHOW)
    _style(ax, "Movie run time (minutes)")
    return _save(fig, out / "movie_length.png")


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def all_charts(df: pd.DataFrame, out: Path) -> list[Path]:
    return [
        additions_chart(df, out),
        top_countries_chart(df, out),
        top_genres_chart(df, out),
        movie_length_chart(df, out),
    ]
