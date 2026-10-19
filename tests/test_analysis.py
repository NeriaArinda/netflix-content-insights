from pathlib import Path

from netflix_insights import analysis
from netflix_insights.cli import main


def test_type_split_sums_to_one(df):
    split = analysis.type_split(df)
    assert abs(split.sum() - 1) < 1e-9
    assert split["Movie"] == 0.6


def test_additions_per_year(df):
    table = analysis.additions_per_year(df)
    assert list(table.index) == [2017, 2019, 2021]
    assert table.loc[2021, "TV Show"] == 1


def test_top_countries_counts_co_productions(df):
    top = analysis.top_values(df, "country")
    assert top["United States"] == 3
    assert top["India"] == 2


def test_genre_by_country_percentages(df):
    table = analysis.genre_by_country(df, ["United States"])
    assert table.loc["United States", "Dramas"] == round(2 / 3 * 100, 1)


def test_summary_keys(df):
    s = analysis.summary(df)
    assert s["titles"] == 5
    assert s["countries"] == 2
    assert s["median_movie_minutes"] == 90


def test_cli_writes_report(sample_csv: Path, tmp_path: Path):
    out = tmp_path / "out"
    assert main([str(sample_csv), "-o", str(out)]) == 0
    assert (out / "REPORT.md").exists()
    assert len(list(out.glob("*.png"))) == 4
