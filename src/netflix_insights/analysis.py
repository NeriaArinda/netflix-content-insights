"""Questions we can answer about the catalogue once it is clean."""

from __future__ import annotations

import pandas as pd

from .cleaning import explode


def type_split(df: pd.DataFrame) -> pd.Series:
    """Share of Movies vs TV Shows (sums to 1)."""
    return df["type"].value_counts(normalize=True).round(4)


def additions_per_year(df: pd.DataFrame) -> pd.DataFrame:
    """How many movies and shows were added each year."""
    table = (
        df.dropna(subset=["year_added"])
        .groupby(["year_added", "type"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    table.index = table.index.astype(int)
    return table


def top_values(df: pd.DataFrame, column: str, n: int = 10) -> pd.Series:
    """Most frequent countries, genres, directors or cast members."""
    return explode(df, column)[column].value_counts().head(n)


def genre_by_country(df: pd.DataFrame, countries: list[str], n_genres: int = 8) -> pd.DataFrame:
    """Percentage of each country's titles that fall into the top genres."""
    by_country = explode(explode(df, "country"), "listed_in")
    by_country = by_country[by_country["country"].isin(countries)]
    top_genres = by_country["listed_in"].value_counts().head(n_genres).index
    counts = (
        by_country[by_country["listed_in"].isin(top_genres)]
        .groupby(["country", "listed_in"])
        .size()
        .unstack(fill_value=0)
    )
    totals = df.explode("country").groupby("country").size().reindex(counts.index)
    return (counts.div(totals, axis=0) * 100).round(1)


def movie_length_stats(df: pd.DataFrame) -> pd.Series:
    """Describe movie run times in minutes."""
    movies = df[(df["type"] == "Movie") & (df["duration_unit"] == "min")]
    return movies["duration_value"].astype(float).describe().round(1)


def time_to_platform(df: pd.DataFrame) -> pd.Series:
    """Years between release and being added to Netflix, by type (median)."""
    gap = (df["year_added"] - df["release_year"]).astype("Float64")
    return gap.groupby(df["type"]).median()


def summary(df: pd.DataFrame) -> dict[str, object]:
    """Headline numbers for the README / console output."""
    split = type_split(df)
    return {
        "titles": int(len(df)),
        "movies_pct": round(float(split.get("Movie", 0) * 100), 2),
        "shows_pct": round(float(split.get("TV Show", 0) * 100), 2),
        "countries": int(explode(df, "country")["country"].nunique()),
        "first_year_added": int(df["year_added"].min()),
        "last_year_added": int(df["year_added"].max()),
        "median_movie_minutes": float(movie_length_stats(df)["50%"]),
    }
