"""Parsing routines for CCEL ThML volumes."""

from __future__ import annotations

import re
from pathlib import Path

from .constants import DEUTEROCANONICAL_BOOKS, KNOWN_BOOK_IDS, NEW_TESTAMENT_BOOKS
from .models import ParseReport, Reference

ATTR_RE = re.compile(r"(\w+)\s*=\s*['\"]([^'\"]*)['\"]")
EVENT_RE = re.compile(
    r"<authorID>([^<]+)</authorID>|<workID>([^<]+)</workID>|<(scripRef|scripCom)\b([^>]*)>(.*?)</\3>",
    re.IGNORECASE | re.DOTALL,
)
OSIS_TAG_RE = re.compile(r"<([a-zA-Z0-9:_-]+)\b[^>]*\bosisRef\s*=", re.IGNORECASE)
BIBLE_OSIS_BOOK_RE = re.compile(r"Bible:([^.:\s]+)")
OSIS_SEGMENT_RE = re.compile(r"Bible:([^.\s:]+)\.([0-9]+)(?:\.([0-9]+))?")


def classify_book(book: str) -> str:
    if book in NEW_TESTAMENT_BOOKS:
        return "new_testament"
    if book in DEUTEROCANONICAL_BOOKS:
        return "deuterocanonical"
    return "old_testament_or_other"


def volume_label_from_path(input_file: Path) -> str:
    volume_match = re.search(r"Volume(\d+)", input_file.stem)
    return f"volume_{volume_match.group(1)}" if volume_match else input_file.stem.lower()


def parse_references(thml_file: Path) -> tuple[list[Reference], ParseReport]:
    references: list[Reference] = []
    current_author = "unknown_author"
    current_work = "unknown_work"
    total_reference_tags = 0
    non_bible_reference_tags = 0
    multi_book_osis_tags = 0
    duplicate_rows_removed = 0
    malformed_osis_references = 0
    ambiguous_book_ids = 0
    exact_quote_references = 0
    probable_allusion_references = 0

    text = thml_file.read_text(encoding="utf-8")
    volume_label = volume_label_from_path(thml_file)

    osis_tags = [match.group(1).lower() for match in OSIS_TAG_RE.finditer(text)]
    other_osis_tags = sum(1 for tag_name in osis_tags if tag_name not in {"scripref", "scripcom"})

    for match in EVENT_RE.finditer(text):
        author_text, work_text, tag_name, attrs, passage = match.groups()
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

        books = tuple(BIBLE_OSIS_BOOK_RE.findall(osis_ref))
        if not books:
            non_bible_reference_tags += 1
            continue

        if len(set(books)) > 1:
            multi_book_osis_tags += 1
            ambiguous_book_ids += 1

        if any(book not in KNOWN_BOOK_IDS for book in books):
            ambiguous_book_ids += 1

        chapter_start, verse_start = "", ""
        segment_match = OSIS_SEGMENT_RE.search(osis_ref)
        if segment_match:
            _, chapter_start, verse_start = segment_match.groups()
            verse_start = verse_start or ""
        else:
            malformed_osis_references += 1

        quote_confidence = "exact_citation" if (tag_name or "").lower() == "scripref" else "probable_allusion"
        if quote_confidence == "exact_citation":
            exact_quote_references += 1
        else:
            probable_allusion_references += 1

        references.append(
            Reference(
                volume=volume_label,
                author_id=current_author,
                work_id=current_work,
                osis_ref=osis_ref,
                passage=passage.strip(),
                book=books[0],
                testament_group=classify_book(books[0]),
                books_in_osis=books,
                chapter_start=chapter_start,
                verse_start=verse_start,
                quote_confidence=quote_confidence,
            )
        )

    deduped_references: list[Reference] = []
    seen: set[tuple[str, str, str, str, str, str]] = set()
    for ref in references:
        key = (ref.volume, ref.author_id, ref.work_id, ref.book, ref.osis_ref, ref.passage)
        if key in seen:
            duplicate_rows_removed += 1
            continue
        seen.add(key)
        deduped_references.append(ref)

    report = ParseReport(
        input_file=str(thml_file),
        total_reference_tags=total_reference_tags,
        bible_reference_tags=len(deduped_references),
        non_bible_reference_tags=non_bible_reference_tags,
        multi_book_osis_tags=multi_book_osis_tags,
        other_osis_tags=other_osis_tags,
        duplicate_rows_removed=duplicate_rows_removed,
        malformed_osis_references=malformed_osis_references,
        ambiguous_book_ids=ambiguous_book_ids,
        exact_quote_references=exact_quote_references,
        probable_allusion_references=probable_allusion_references,
        duplicate_reference_rationale=(
            "Exact duplicate removed by tuple(volume, author_id, work_id, book, osis_ref, passage)."
            if duplicate_rows_removed
            else ""
        ),
    )
    return deduped_references, report
