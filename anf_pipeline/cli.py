"""CLI orchestration for ANF parsing and analytics outputs."""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

from .aggregation import (
    build_author_book_counts,
    write_count_csv,
    write_long_csv,
    write_overall_csv,
    write_parse_diagnostics_csv,
    write_structured_csv,
    write_volume_comparison_csv,
)
from .parsing import parse_references, volume_label_from_path
from .query import ReferenceQueryEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract Bible references from ANF ThML files.")
    parser.add_argument(
        "--input",
        dest="inputs",
        action="append",
        type=Path,
        help="Path to a ThML/HTML input file (repeat for multiple volumes).",
    )
    parser.add_argument("--out-dir", type=Path, default=Path("outputs"), help="Directory for generated CSV files.")
    parser.add_argument("--query-author", type=str, help="Optional author filter for query preview output.")
    parser.add_argument("--query-work", type=str, help="Optional work filter for query preview output.")
    parser.add_argument("--query-book", type=str, help="Optional exact Bible book filter for query preview output.")
    parser.add_argument("--query-volume", type=str, help="Optional volume label filter (e.g., volume_1).")
    parser.add_argument("--query-limit", type=int, default=10, help="Maximum number of query preview rows to print.")
    return parser.parse_args()


def run_pipeline() -> None:
    args = parse_args()
    inputs = args.inputs or [
        Path("texts/AnteNiceneVolume1.html"),
        Path("texts/AnteNiceneVolume2.html"),
        Path("texts/AnteNiceneVolume3.html"),
    ]

    args.out_dir.mkdir(parents=True, exist_ok=True)

    all_references = []
    per_volume_counts: dict[str, Counter[str]] = {}
    diagnostics = []

    for input_file in inputs:
        references, report = parse_references(input_file)
        all_references.extend(references)
        diagnostics.append(report)

        volume_label = volume_label_from_path(input_file)
        per_volume_counts[volume_label] = Counter(ref.book for ref in references)

        long_csv = args.out_dir / f"references_long_{volume_label}.csv"
        author_counts_csv = args.out_dir / f"book_counts_by_author_{volume_label}.csv"
        overall_counts_csv = args.out_dir / f"book_counts_overall_{volume_label}.csv"

        write_long_csv(long_csv, references)
        write_count_csv(author_counts_csv, build_author_book_counts(references))
        write_overall_csv(overall_counts_csv, Counter(ref.book for ref in references))

        print(f"Parsed {len(references)} Bible references from {input_file}.")
        print(f"Wrote: {long_csv}, {author_counts_csv}, {overall_counts_csv}")
        print(
            "Diagnostics: "
            f"total_reference_tags={report.total_reference_tags}, "
            f"bible_reference_tags={report.bible_reference_tags}, "
            f"non_bible_reference_tags={report.non_bible_reference_tags}, "
            f"multi_book_osis_tags={report.multi_book_osis_tags}, "
            f"other_osis_tags={report.other_osis_tags}, "
            f"duplicate_rows_removed={report.duplicate_rows_removed}"
        )

    combined_long_csv = args.out_dir / "references_long.csv"
    combined_structured_csv = args.out_dir / "references_structured.csv"
    combined_author_counts_csv = args.out_dir / "book_counts_by_author.csv"
    combined_overall_counts_csv = args.out_dir / "book_counts_overall.csv"
    volume_comparison_csv = args.out_dir / "book_counts_volume_comparison.csv"
    parse_diagnostics_csv = args.out_dir / "parse_diagnostics.csv"

    write_long_csv(combined_long_csv, all_references)
    write_structured_csv(combined_structured_csv, all_references)
    write_count_csv(combined_author_counts_csv, build_author_book_counts(all_references))
    write_overall_csv(combined_overall_counts_csv, Counter(ref.book for ref in all_references))
    write_volume_comparison_csv(volume_comparison_csv, per_volume_counts)
    write_parse_diagnostics_csv(parse_diagnostics_csv, diagnostics)

    print(f"Parsed {len(all_references)} Bible references across {len(inputs)} volume(s).")
    print(
        "Wrote combined files: "
        f"{combined_long_csv}, {combined_structured_csv}, {combined_author_counts_csv}, "
        f"{combined_overall_counts_csv}, {volume_comparison_csv}, {parse_diagnostics_csv}"
    )

    if any([args.query_author, args.query_work, args.query_book, args.query_volume]):
        engine = ReferenceQueryEngine(all_references)
        query_rows = engine.filter(
            author=args.query_author,
            work=args.query_work,
            book=args.query_book,
            volume=args.query_volume,
        )
        preview_rows = engine.to_dicts(query_rows[: args.query_limit])
        print(f"\nQuery matched {len(query_rows)} row(s). Showing first {len(preview_rows)}:")
        if not preview_rows:
            return

        fieldnames = list(preview_rows[0].keys())
        writer = csv.DictWriter(
            f=__import__("sys").stdout,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(preview_rows)
