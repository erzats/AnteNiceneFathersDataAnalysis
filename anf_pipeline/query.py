"""In-memory query helper for exploration and future MCP integration."""

from __future__ import annotations

from dataclasses import asdict

from .models import Reference


class ReferenceQueryEngine:
    """Provides composable filtering over parsed references."""

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
    ) -> list[Reference]:
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
        return records

    @staticmethod
    def to_dicts(records: list[Reference]) -> list[dict[str, str]]:
        normalized: list[dict[str, str]] = []
        for record in records:
            row = asdict(record)
            row["books_in_osis"] = "|".join(record.books_in_osis)
            normalized.append({k: str(v) for k, v in row.items()})
        return normalized
