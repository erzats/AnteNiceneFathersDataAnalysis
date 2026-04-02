"""Higher-level research outputs for ANF Scripture-citation questions."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from .constants import CANONICAL_BOOK_ORDER, DEUTEROCANONICAL_BOOKS
from .models import Reference


def write_tobit_reference_csv(path: Path, references: list[Reference]) -> None:
    tobit_refs = [ref for ref in references if ref.book == "Tob"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "author_id",
                "work_id",
                "volume",
                "osis_ref",
                "chapter_start",
                "verse_start",
                "passage",
            ]
        )
        for ref in tobit_refs:
            writer.writerow(
                [
                    ref.author_id,
                    ref.work_id,
                    ref.volume,
                    ref.osis_ref,
                    ref.chapter_start,
                    ref.verse_start,
                    ref.passage,
                ]
            )


def write_psalm_popularity_csv(path: Path, references: list[Reference]) -> None:
    psalm_counts: Counter[str] = Counter()
    for ref in references:
        if ref.book != "Ps":
            continue
        chapter = ref.chapter_start or "unknown"
        psalm_counts[chapter] += 1

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["psalm", "count"])
        for chapter, count in sorted(psalm_counts.items(), key=lambda row: (-row[1], row[0])):
            writer.writerow([chapter, count])


def write_unquoted_books_csv(path: Path, references: list[Reference]) -> None:
    quoted = {ref.book for ref in references}
    unquoted = [book for book in CANONICAL_BOOK_ORDER if book not in quoted]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["book"])
        for book in unquoted:
            writer.writerow([book])


def write_author_coverage_csv(path: Path, references: list[Reference]) -> None:
    by_author: dict[str, set[str]] = defaultdict(set)
    by_author_deut: dict[str, set[str]] = defaultdict(set)
    by_author_non_deut: dict[str, set[str]] = defaultdict(set)

    for ref in references:
        by_author[ref.author_id].add(ref.book)
        if ref.book in DEUTEROCANONICAL_BOOKS:
            by_author_deut[ref.author_id].add(ref.book)
        else:
            by_author_non_deut[ref.author_id].add(ref.book)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "author_id",
                "unique_books_total",
                "unique_books_non_deut",
                "unique_books_deut",
                "quoted_deuterocanonical",
            ]
        )
        for author in sorted(by_author):
            total_books = len(by_author[author])
            non_deut = len(by_author_non_deut[author])
            deut = len(by_author_deut[author])
            writer.writerow([author, total_books, non_deut, deut, "yes" if deut else "no"])

