"""Command-line entry point: ``netflix-insights data/netflix_titles.csv``."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import analysis, plots
from .cleaning import clean, load_raw


def build_report(df, out_dir: Path) -> Path:
    """Write a Markdown report with tables and chart links."""
    s = analysis.summary(df)
    lines = [
        "# Netflix catalogue report",
        "",
        f"- **{s['titles']:,}** titles from **{s['countries']}** countries",
        f"- {s['movies_pct']:.1f}% movies, {s['shows_pct']:.1f}% TV shows",
        f"- Added between {s['first_year_added']} and {s['last_year_added']}",
        f"- Median movie length: {s['median_movie_minutes']:.0f} minutes",
        "",
        "## Titles added per year",
        "",
        analysis.additions_per_year(df).to_markdown(),
        "",
        "![additions](additions_per_year.png)",
        "",
        "## Top countries",
        "",
        analysis.top_values(df, "country").to_frame("titles").to_markdown(),
        "",
        "![countries](top_countries.png)",
        "",
        "## Top genres",
        "",
        analysis.top_values(df, "listed_in", 12).to_frame("titles").to_markdown(),
        "",
        "![genres](top_genres.png)",
        "",
        "## Median years from release to Netflix",
        "",
        analysis.time_to_platform(df).to_frame("years").to_markdown(),
        "",
        "![length](movie_length.png)",
        "",
    ]
    path = out_dir / "REPORT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="path to netflix_titles.csv")
    parser.add_argument("-o", "--out", type=Path, default=Path("reports"), help="output folder")
    parser.add_argument("--json", action="store_true", help="print the summary as JSON only")
    args = parser.parse_args(argv)

    df = clean(load_raw(args.csv))
    if args.json:
        print(json.dumps(analysis.summary(df), indent=2))
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    charts = plots.all_charts(df, args.out)
    report = build_report(df, args.out)
    print(f"Cleaned {len(df):,} titles")
    for c in charts:
        print(f"  chart  {c}")
    print(f"  report {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
