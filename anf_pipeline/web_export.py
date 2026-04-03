"""Export pipeline data as JSON files for the Next.js web frontend."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from .constants import (
    AUTHOR_METADATA,
    BOOK_DISPLAY_NAMES,
    CANONICAL_BOOK_ORDER,
    DEUTEROCANONICAL_BOOKS,
    NEW_TESTAMENT_BOOKS,
)
from .models import Reference


def _testament_group(book: str) -> str:
    if book in NEW_TESTAMENT_BOOKS:
        return "new_testament"
    if book in DEUTEROCANONICAL_BOOKS:
        return "deuterocanonical"
    return "old_testament_or_other"


def _book_display(book: str) -> str:
    return BOOK_DISPLAY_NAMES.get(book, book)


def _author_display(author_id: str) -> str:
    meta = AUTHOR_METADATA.get(author_id)
    return meta["display_name"] if meta else author_id.replace("_", " ").title()  # type: ignore[index]


def export_web_data(out_dir: Path, references: list[Reference]) -> None:
    """Write all JSON data files consumed by the Next.js frontend."""
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_summary(out_dir / "summary.json", references)
    _write_books(out_dir / "books.json", references)
    _write_authors(out_dir / "authors.json", references)
    _write_psalms(out_dir / "psalms.json", references)
    _write_volume_comparison(out_dir / "volume_comparison.json", references)


def _write_summary(path: Path, references: list[Reference]) -> None:
    total = len(references)
    by_testament: Counter[str] = Counter(ref.testament_group for ref in references)
    book_counts: Counter[str] = Counter(ref.book for ref in references)
    author_counts: Counter[str] = Counter(ref.author_id for ref in references)
    quoted = set(ref.book for ref in references)
    unquoted = [book for book in CANONICAL_BOOK_ORDER if book not in quoted]

    top_books = [
        {"book": book, "display_name": _book_display(book), "count": count}
        for book, count in book_counts.most_common(10)
    ]
    top_authors = [
        {
            "author_id": author,
            "display_name": _author_display(author),
            "count": count,
        }
        for author, count in author_counts.most_common(10)
        if not (AUTHOR_METADATA.get(author, {}).get("is_editor", False))
    ][:10]

    data = {
        "total_references": total,
        "by_testament": {
            "new_testament": by_testament.get("new_testament", 0),
            "old_testament_or_other": by_testament.get("old_testament_or_other", 0),
            "deuterocanonical": by_testament.get("deuterocanonical", 0),
        },
        "unique_authors": len(set(ref.author_id for ref in references)),
        "unique_books": len(set(ref.book for ref in references)),
        "top_books": top_books,
        "top_authors": top_authors,
        "unquoted_books": [
            {"book": b, "display_name": _book_display(b)} for b in unquoted
        ],
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _write_books(path: Path, references: list[Reference]) -> None:
    book_counts: Counter[str] = Counter(ref.book for ref in references)
    volume_book_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for ref in references:
        volume_book_counts[ref.volume][ref.book] += 1

    volumes = sorted(volume_book_counts.keys(), key=lambda v: (int(v.rsplit("_", 1)[-1]) if v.rsplit("_", 1)[-1].isdigit() else 9999, v))

    rows = []
    for book in CANONICAL_BOOK_ORDER:
        count = book_counts.get(book, 0)
        rows.append({
            "book": book,
            "display_name": _book_display(book),
            "testament_group": _testament_group(book),
            "total_count": count,
            "volume_counts": {v: volume_book_counts[v].get(book, 0) for v in volumes},
        })

    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def _write_authors(path: Path, references: list[Reference]) -> None:
    by_author: dict[str, list[Reference]] = defaultdict(list)
    for ref in references:
        by_author[ref.author_id].append(ref)

    rows = []
    for author_id, refs in sorted(by_author.items(), key=lambda kv: -len(kv[1])):
        meta = AUTHOR_METADATA.get(author_id, {})
        unique_books = set(r.book for r in refs)
        deut_books = unique_books & DEUTEROCANONICAL_BOOKS
        rows.append({
            "author_id": author_id,
            "display_name": _author_display(author_id),
            "floruit": meta.get("floruit"),
            "century": meta.get("century"),
            "is_editor": meta.get("is_editor", False),
            "total_citations": len(refs),
            "unique_books": len(unique_books),
            "deuterocanonical_books_cited": len(deut_books),
            "quoted_deuterocanonical": len(deut_books) > 0,
            "top_books": [
                {"book": b, "display_name": _book_display(b), "count": c}
                for b, c in Counter(r.book for r in refs).most_common(5)
            ],
        })

    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def _write_psalms(path: Path, references: list[Reference]) -> None:
    psalm_counts: Counter[str] = Counter()
    for ref in references:
        if ref.book != "Ps":
            continue
        chapter = ref.chapter_start or "unknown"
        psalm_counts[chapter] += 1

    rows = [
        {"psalm": chapter, "count": count}
        for chapter, count in sorted(psalm_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def _write_volume_comparison(path: Path, references: list[Reference]) -> None:
    volume_book_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for ref in references:
        volume_book_counts[ref.volume][ref.book] += 1

    volumes = sorted(
        volume_book_counts.keys(),
        key=lambda v: (int(v.rsplit("_", 1)[-1]) if v.rsplit("_", 1)[-1].isdigit() else 9999, v),
    )
    book_totals: Counter[str] = Counter(ref.book for ref in references)

    rows = []
    for book in CANONICAL_BOOK_ORDER:
        if book_totals.get(book, 0) == 0:
            continue
        rows.append({
            "book": book,
            "display_name": _book_display(book),
            "testament_group": _testament_group(book),
            "total_count": book_totals.get(book, 0),
            "by_volume": {v: volume_book_counts[v].get(book, 0) for v in volumes},
        })

    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
