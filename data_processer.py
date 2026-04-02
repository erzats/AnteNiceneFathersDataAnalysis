"""Extract and aggregate biblical references from CCEL ThML volumes."""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

AUTHOR_RE = re.compile(r"<authorID>([^<]+)</authorID>", re.IGNORECASE | re.DOTALL)
WORK_RE = re.compile(r"<workID>([^<]+)</workID>", re.IGNORECASE | re.DOTALL)
ATTR_RE = re.compile(r"(\w+)\s*=\s*['\"]([^'\"]*)['\"]")
OSIS_BOOK_RE = re.compile(r"Bible:([^.:\s]+)")
EVENT_RE = re.compile(
    r"<authorID>([^<]+)</authorID>|<workID>([^<]+)</workID>|<(scripRef|scripCom)\b([^>]*)>(.*?)</\3>",
    re.IGNORECASE | re.DOTALL,
)
OSIS_TAG_RE = re.compile(r"<([a-zA-Z0-9:_-]+)\b[^>]*\bosisRef\s*=", re.IGNORECASE)


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

CANONICAL_BOOK_ORDER = [
    "Gen",
    "Exod",
    "Lev",
    "Num",
    "Deut",
    "Josh",
    "Judg",
    "Ruth",
    "1Sam",
    "2Sam",
    "1Kgs",
    "2Kgs",
    "1Chr",
    "2Chr",
    "Ezra",
    "Neh",
    "Tob",
    "Jdt",
    "Esth",
    "AddEsth",
    "1Macc",
    "2Macc",
    "Job",
    "Ps",
    "Prov",
    "Eccl",
    "Song",
    "Wis",
    "Sir",
    "Isa",
    "Jer",
    "Lam",
    "Bar",
    "EpJer",
    "Ezek",
    "Dan",
    "AddDan",
    "PrAzar",
    "Sus",
    "Bel",
    "Hos",
    "Joel",
    "Amos",
    "Obad",
    "Jonah",
    "Mic",
    "Nah",
    "Hab",
    "Zeph",
    "Hag",
    "Zech",
    "Mal",
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
]


@dataclass(frozen=True)
class Reference:
    author_id: str
    work_id: str
    osis_ref: str
    passage: str
    book: str
    testament_group: str


@dataclass(frozen=True)
class ParseReport:
    input_file: str
    total_reference_tags: int
    bible_reference_tags: int
    non_bible_reference_tags: int
    multi_book_osis_tags: int
    other_osis_tags: int
    duplicate_rows_removed: int


def parse_references(thml_file: Path) -> tuple[list[Reference], ParseReport]:
    references: list[Reference] = []
    current_author = "unknown_author"
    current_work = "unknown_work"
    total_reference_tags = 0
    bible_reference_tags = 0
    non_bible_reference_tags = 0
    multi_book_osis_tags = 0
    duplicate_rows_removed = 0

    text = thml_file.read_text(encoding="utf-8")

    osis_tags = [match.group(1).lower() for match in OSIS_TAG_RE.finditer(text)]
    other_osis_tags = sum(1 for tag_name in osis_tags if tag_name not in {"scripref", "scripcom"})

    for match in EVENT_RE.finditer(text):
        author_text, work_text, _, attrs, passage = match.groups()
        if author_text is not None:
            current_author = author_text.strip()
            continue
        if work_text is not None:
            current_work = work_text.strip()
            continue

        total_reference_tags += 1
        attr_dict = dict(ATTR_RE.findall(attrs))
        osis_ref = attr_dict.get("osisRef", "") or attr_dict.get("osisref", "")
        if not osis_ref.startswith("Bible:"):
            non_bible_reference_tags += 1
            continue

        books = OSIS_BOOK_RE.findall(osis_ref)
        if not books:
            non_bible_reference_tags += 1
            continue

        bible_reference_tags += 1
        if len(set(books)) > 1:
            multi_book_osis_tags += 1

        references.append(
            Reference(
                author_id=current_author,
                work_id=current_work,
                osis_ref=osis_ref,
                passage=passage.strip(),
                book=books[0],
                testament_group=classify_book(books[0]),
            )
        )

    deduped_references: list[Reference] = []
    seen: set[tuple[str, str, str, str, str]] = set()
    for ref in references:
        key = (ref.author_id, ref.work_id, ref.book, ref.osis_ref, ref.passage)
        if key in seen:
            duplicate_rows_removed += 1
            continue
        seen.add(key)
        deduped_references.append(ref)

    return deduped_references, ParseReport(
        input_file=str(thml_file),
        total_reference_tags=total_reference_tags,
        bible_reference_tags=len(deduped_references),
        non_bible_reference_tags=non_bible_reference_tags,
        multi_book_osis_tags=multi_book_osis_tags,
        other_osis_tags=other_osis_tags,
        duplicate_rows_removed=duplicate_rows_removed,
    )


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


def write_volume_comparison_csv(path: Path, per_volume_counts: dict[str, Counter[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["book", "total_count", "volume_1_count", "volume_2_count", "volume_3_count"])
        v1 = per_volume_counts.get("volume_1", Counter())
        v2 = per_volume_counts.get("volume_2", Counter())
        v3 = per_volume_counts.get("volume_3", Counter())

        for book in CANONICAL_BOOK_ORDER:
            volume_1_count = v1.get(book, 0)
            volume_2_count = v2.get(book, 0)
            volume_3_count = v3.get(book, 0)
            writer.writerow(
                [book, volume_1_count + volume_2_count + volume_3_count, volume_1_count, volume_2_count, volume_3_count]
            )


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract Bible references from ANF ThML files.")
    parser.add_argument(
        "--input",
        dest="inputs",
        action="append",
        type=Path,
        help="Path to a ThML/HTML input file (repeat for multiple volumes).",
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
    inputs = args.inputs or [
        Path("texts/AnteNiceneVolume1.html"),
        Path("texts/AnteNiceneVolume2.html"),
        Path("texts/AnteNiceneVolume3.html"),
    ]

    args.out_dir.mkdir(parents=True, exist_ok=True)

    all_references: list[Reference] = []
    per_volume_counts: dict[str, Counter[str]] = {}
    diagnostics: list[ParseReport] = []

    for input_file in inputs:
        references, report = parse_references(input_file)
        all_references.extend(references)
        diagnostics.append(report)

        volume_match = re.search(r"Volume(\d+)", input_file.stem)
        volume_label = f"volume_{volume_match.group(1)}" if volume_match else input_file.stem.lower()
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
    combined_author_counts_csv = args.out_dir / "book_counts_by_author.csv"
    combined_overall_counts_csv = args.out_dir / "book_counts_overall.csv"
    volume_comparison_csv = args.out_dir / "book_counts_volume_comparison.csv"
    parse_diagnostics_csv = args.out_dir / "parse_diagnostics.csv"

    write_long_csv(combined_long_csv, all_references)
    write_count_csv(combined_author_counts_csv, build_author_book_counts(all_references))
    write_overall_csv(combined_overall_counts_csv, Counter(ref.book for ref in all_references))
    write_volume_comparison_csv(volume_comparison_csv, per_volume_counts)
    write_parse_diagnostics_csv(parse_diagnostics_csv, diagnostics)

    print(f"Parsed {len(all_references)} Bible references across {len(inputs)} volume(s).")
    print(
        "Wrote combined files: "
        f"{combined_long_csv}, {combined_author_counts_csv}, {combined_overall_counts_csv}, "
        f"{volume_comparison_csv}, {parse_diagnostics_csv}"
    )


if __name__ == "__main__":
    main()
