"""Aggregation and CSV output helpers."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from .constants import CANONICAL_BOOK_ORDER
from .models import ParseReport, Reference


def write_long_csv(path: Path, references: Iterable[Reference]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["author_id", "work_id", "book", "testament_group", "osis_ref", "passage"])
        for ref in references:
            writer.writerow([ref.author_id, ref.work_id, ref.book, ref.testament_group, ref.osis_ref, ref.passage])


def write_structured_csv(path: Path, references: Iterable[Reference]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "volume",
                "author_id",
                "work_id",
                "book",
                "books_in_osis",
                "chapter_start",
                "verse_start",
                "testament_group",
                "osis_ref",
                "passage",
            ]
        )
        for ref in references:
            writer.writerow(
                [
                    ref.volume,
                    ref.author_id,
                    ref.work_id,
                    ref.book,
                    "|".join(ref.books_in_osis),
                    ref.chapter_start,
                    ref.verse_start,
                    ref.testament_group,
                    ref.osis_ref,
                    ref.passage,
                ]
            )


def write_count_csv(path: Path, rows: Iterable[tuple[str, str, int]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["author_id", "book", "count"])
        for row in rows:
            writer.writerow(row)


def write_overall_csv(path: Path, counts: Counter[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["book", "count"])
        for book, count in counts.most_common():
            writer.writerow([book, count])


def write_volume_comparison_csv(path: Path, per_volume_counts: dict[str, Counter[str]]) -> None:
    def _volume_sort_key(label: str) -> tuple[int, str]:
        suffix = label.rsplit("_", maxsplit=1)[-1]
        return (int(suffix), label) if suffix.isdigit() else (10_000, label)

    volume_labels = sorted(per_volume_counts.keys(), key=_volume_sort_key)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["book", "total_count", *[f"{label}_count" for label in volume_labels]])

        for book in CANONICAL_BOOK_ORDER:
            volume_counts = [per_volume_counts.get(label, Counter()).get(book, 0) for label in volume_labels]
            writer.writerow([book, sum(volume_counts), *volume_counts])


def write_parse_diagnostics_csv(path: Path, reports: Iterable[ParseReport]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "input_file",
                "total_reference_tags",
                "bible_reference_tags",
                "non_bible_reference_tags",
                "multi_book_osis_tags",
                "other_osis_tags",
                "duplicate_rows_removed",
            ]
        )
        for report in reports:
            writer.writerow(
                [
                    report.input_file,
                    report.total_reference_tags,
                    report.bible_reference_tags,
                    report.non_bible_reference_tags,
                    report.multi_book_osis_tags,
                    report.other_osis_tags,
                    report.duplicate_rows_removed,
                ]
            )


def build_author_book_counts(references: Iterable[Reference]) -> list[tuple[str, str, int]]:
    nested_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for ref in references:
        nested_counts[ref.author_id][ref.book] += 1

    rows: list[tuple[str, str, int]] = []
    for author_id in sorted(nested_counts):
        for book, count in nested_counts[author_id].most_common():
            rows.append((author_id, book, count))
    return rows
