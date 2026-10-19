import pandas as pd
import pytest

from netflix_insights.cleaning import explode, parse_duration


def test_duplicates_removed(df):
    assert len(df) == 5
    assert (df["title"] == "Alpha").sum() == 1


def test_dates_parsed(df):
    assert df.loc[df["title"] == "Gamma", "year_added"].item() == 2019
    assert pd.isna(df.loc[df["title"] == "Epsilon", "year_added"].item())


def test_misplaced_duration_is_moved(df):
    row = df[df["title"] == "Delta"].iloc[0]
    assert row["duration_value"] == 74
    assert row["duration_unit"] == "min"
    assert row["rating"] == "Unrated"


@pytest.mark.parametrize(
    "text, expected",
    [("90 min", (90, "min")), ("2 Seasons", (2, "season")), ("1 Season", (1, "season")),
     ("", (None, None)), (None, (None, None)), ("abc", (None, None))],
)
def test_parse_duration(text, expected):
    assert parse_duration(text) == expected


def test_lists_split(df):
    gamma = df[df["title"] == "Gamma"].iloc[0]
    assert gamma["country"] == ["United States", "India"]
    assert df[df["title"] == "Epsilon"].iloc[0]["country"] == []


def test_explode_rejects_scalar_column(df):
    with pytest.raises(ValueError):
        explode(df, "title")
