"""In-memory query helper for exploration and future MCP integration."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict

from .constants import DEUTEROCANONICAL_BOOKS
from .models import Reference


class ReferenceQueryEngine:
    """Provides composable filtering and aggregation over parsed references."""

    def __init__(self, references: list[Reference]):
        self.references = references

    def filter(
        self,
        *,
        author: str | None = None,
        work: str | None = None,
        book: str | None = None,
        testament_group: str | None = None,
        volume: str | None = None,
        quote_confidence: str | None = None,
        include_deuterocanonical: bool = True,
    ) -> list[Reference]:
        """Return references matching all supplied criteria.

        Args:
            author: Case-insensitive substring match on author_id.
            work: Case-insensitive substring match on work_id.
            book: Exact (case-insensitive) OSIS book code match.
            testament_group: Exact match on testament_group field.
            volume: Exact match on volume label.
            quote_confidence: Exact match on quote_confidence tier
                (``exact_citation``, ``probable_allusion``, or ``echo_allusion``).
            include_deuterocanonical: When ``False``, exclude deuterocanonical
                books from results (default ``True``).
        """
        records = self.references
        if author:
            records = [r for r in records if author.lower() in r.author_id.lower()]
        if work:
            records = [r for r in records if work.lower() in r.work_id.lower()]
        if book:
            records = [r for r in records if r.book.lower() == book.lower()]
        if testament_group:
            records = [r for r in records if r.testament_group == testament_group]
        if volume:
            records = [r for r in records if r.volume == volume]
        if quote_confidence:
            records = [r for r in records if r.quote_confidence == quote_confidence]
        if not include_deuterocanonical:
            records = [r for r in records if r.book not in DEUTEROCANONICAL_BOOKS]
        return records

    def top_books_by_author(self, top_n: int = 10) -> dict[str, list[tuple[str, int]]]:
        """Return the top-N most cited books for each author.

        Returns:
            Mapping of author_id → list of (book, count) tuples sorted
            descending by count, truncated to *top_n* entries.
        """
        nested: defaultdict[str, Counter[str]] = defaultdict(Counter)
        for ref in self.references:
            nested[ref.author_id][ref.book] += 1
        return {
            author_id: counts.most_common(top_n)
            for author_id, counts in sorted(nested.items())
        }

    def authors_with_min_unique_books(self, min_books: int) -> list[str]:
        """Return author IDs that cite at least *min_books* distinct books.

        Returns:
            Sorted list of author_id strings meeting the threshold.
        """
        unique_books: defaultdict[str, set[str]] = defaultdict(set)
        for ref in self.references:
            unique_books[ref.author_id].add(ref.book)
        return sorted(
            author_id
            for author_id, books in unique_books.items()
            if len(books) >= min_books
        )

    @staticmethod
    def to_dicts(records: list[Reference]) -> list[dict[str, str]]:
        normalized: list[dict[str, str]] = []
        for record in records:
            row = asdict(record)
            row["books_in_osis"] = "|".join(record.books_in_osis)
            normalized.append({k: str(v) for k, v in row.items()})
        return normalized
