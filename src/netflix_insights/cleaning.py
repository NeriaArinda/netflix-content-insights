"""Load the raw Kaggle CSV and turn it into tidy, typed tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

LIST_COLUMNS = ["director", "cast", "country", "listed_in"]


def load_raw(path: str | Path) -> pd.DataFrame:
    """Read netflix_titles.csv exactly as downloaded from Kaggle."""
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])


def _split_list(value: object) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def parse_duration(value: object) -> tuple[float | None, str | None]:
    """'90 min' -> (90, 'min'); '2 Seasons' -> (2, 'season')."""
    if not isinstance(value, str) or not value.strip():
        return None, None
    number, _, unit = value.strip().partition(" ")
    try:
        amount = float(number)
    except ValueError:
        return None, None
    unit = unit.lower().rstrip("s") if unit else None
    return amount, unit


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the catalogue.

    * strips whitespace and drops exact duplicate titles
    * parses ``date_added`` into a datetime and adds ``year_added``
    * splits ``duration`` into ``duration_value`` / ``duration_unit``
    * fixes the known data-entry error where a duration ended up in ``rating``
    * converts comma-separated columns into Python lists
    """
    df = raw.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()

    df = df.drop_duplicates(subset=["type", "title", "release_year"]).reset_index(drop=True)

    # A handful of rows have "74 min" etc. in `rating` and an empty `duration`.
    misplaced = df["rating"].fillna("").str.contains(r"\d+\s*min", regex=True)
    df.loc[misplaced & df["duration"].isna(), "duration"] = df.loc[misplaced, "rating"]
    df.loc[misplaced, "rating"] = pd.NA

    df["date_added"] = pd.to_datetime(df["date_added"], format="mixed", errors="coerce")
    df["year_added"] = df["date_added"].dt.year.astype("Int64")
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce").astype("Int64")

    parsed = df["duration"].map(parse_duration)
    df["duration_value"] = parsed.map(lambda p: p[0]).astype("Float64")
    df["duration_unit"] = parsed.map(lambda p: p[1])

    for col in LIST_COLUMNS:
        df[col] = df[col].map(_split_list)

    df["rating"] = df["rating"].fillna("Unrated")
    return df


def explode(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """One row per (title, value) for a list column such as ``country``."""
    if column not in LIST_COLUMNS:
        raise ValueError(f"{column!r} is not a list column; choose from {LIST_COLUMNS}")
    out = df.explode(column)
    return out[out[column].notna()].reset_index(drop=True)
