"""Extract and aggregate biblical references from CCEL ThML volumes.

This parser is intentionally lightweight and uses regex-based streaming so it can
handle large ThML/HTML files without additional dependencies.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

AUTHOR_RE = re.compile(r"<authorID>([^<]+)</authorID>")
WORK_RE = re.compile(r"<workID>([^<]+)</workID>")
SCRIP_REF_RE = re.compile(r"<scripRef\b([^>]*)>(.*?)</scripRef>")
ATTR_RE = re.compile(r"(\w+)\s*=\s*\"([^\"]*)\"")


DEUTEROCANONICAL_BOOKS = {
    "Tob",
    "Jdt",
    "Wis",
    "Sir",
    "Bar",
    "EpJer",
    "PrAzar",
    "Sus",
    "Bel",
    "1Macc",
    "2Macc",
    "1Esd",
    "2Esd",
    "PrMan",
    "AddEsth",
    "AddDan",
}

NEW_TESTAMENT_BOOKS = {
    "Matt",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Rom",
    "1Cor",
    "2Cor",
    "Gal",
    "Eph",
    "Phil",
    "Col",
    "1Thess",
    "2Thess",
    "1Tim",
    "2Tim",
    "Titus",
    "Phlm",
    "Heb",
    "Jas",
    "1Pet",
    "2Pet",
    "1John",
    "2John",
    "3John",
    "Jude",
    "Rev",
}


@dataclass(frozen=True)
class Reference:
    author_id: str
    work_id: str
    osis_ref: str
    passage: str
    book: str
    testament_group: str


def parse_references(thml_file: Path) -> list[Reference]:
    references: list[Reference] = []
    current_author = "unknown_author"
    current_work = "unknown_work"

    with thml_file.open("r", encoding="utf-8") as handle:
        for line in handle:
            author_match = AUTHOR_RE.search(line)
            if author_match:
                current_author = author_match.group(1).strip()

            work_match = WORK_RE.search(line)
            if work_match:
                current_work = work_match.group(1).strip()

            for scrip_ref_match in SCRIP_REF_RE.finditer(line):
                attrs, passage = scrip_ref_match.groups()
                attr_dict = dict(ATTR_RE.findall(attrs))
                osis_ref = attr_dict.get("osisRef", "")
                if not osis_ref.startswith("Bible:"):
                    continue

                book = osis_ref.split(":", 1)[1].split(".", 1)[0]
                references.append(
                    Reference(
                        author_id=current_author,
                        work_id=current_work,
                        osis_ref=osis_ref,
                        passage=passage.strip(),
                        book=book,
                        testament_group=classify_book(book),
                    )
                )

    return references


def classify_book(book: str) -> str:
    if book in NEW_TESTAMENT_BOOKS:
        return "new_testament"
    if book in DEUTEROCANONICAL_BOOKS:
        return "deuterocanonical"
    return "old_testament_or_other"


def write_long_csv(path: Path, references: Iterable[Reference]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["author_id", "work_id", "book", "testament_group", "osis_ref", "passage"])
        for ref in references:
            writer.writerow([
                ref.author_id,
                ref.work_id,
                ref.book,
                ref.testament_group,
                ref.osis_ref,
                ref.passage,
            ])


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


def build_author_book_counts(references: Iterable[Reference]) -> list[tuple[str, str, int]]:
    nested_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for ref in references:
        nested_counts[ref.author_id][ref.book] += 1

    rows: list[tuple[str, str, int]] = []
    for author_id in sorted(nested_counts):
        for book, count in nested_counts[author_id].most_common():
            rows.append((author_id, book, count))
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract Bible references from ANF ThML files.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("texts/AnteNiceneVolume1.html"),
        help="Path to ThML/HTML input file.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory for generated CSV files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    references = parse_references(args.input)

    args.out_dir.mkdir(parents=True, exist_ok=True)

    long_csv = args.out_dir / "references_long.csv"
    author_counts_csv = args.out_dir / "book_counts_by_author.csv"
    overall_counts_csv = args.out_dir / "book_counts_overall.csv"

    write_long_csv(long_csv, references)
    write_count_csv(author_counts_csv, build_author_book_counts(references))
    write_overall_csv(overall_counts_csv, Counter(ref.book for ref in references))

    print(f"Parsed {len(references)} Bible references from {args.input}.")
    print(f"Wrote: {long_csv}, {author_counts_csv}, {overall_counts_csv}")


if __name__ == "__main__":
    main()
