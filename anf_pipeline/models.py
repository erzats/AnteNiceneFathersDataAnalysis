"""Domain models for parsing, diagnostics, and query-ready references."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Reference:
    volume: str
    author_id: str
    work_id: str
    osis_ref: str
    passage: str
    book: str
    testament_group: str
    books_in_osis: tuple[str, ...]
    chapter_start: str
    verse_start: str
    quote_confidence: str


@dataclass(frozen=True)
class ParseReport:
    input_file: str
    total_reference_tags: int
    bible_reference_tags: int
    non_bible_reference_tags: int
    multi_book_osis_tags: int
    other_osis_tags: int
    duplicate_rows_removed: int
    malformed_osis_references: int
    ambiguous_book_ids: int
    exact_quote_references: int
    probable_allusion_references: int
    duplicate_reference_rationale: str
