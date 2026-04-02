"""Markdown report generation for ANF Scripture-reference analysis."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from .constants import CANONICAL_BOOK_ORDER, DEUTEROCANONICAL_BOOKS
from .models import Reference


def _section_counts(references: Iterable[Reference]) -> tuple[Counter[str], Counter[str], Counter[str]]:
    nt: Counter[str] = Counter()
    ot: Counter[str] = Counter()
    deut: Counter[str] = Counter()
    for ref in references:
        if ref.testament_group == "new_testament":
            nt[ref.book] += 1
        elif ref.testament_group == "deuterocanonical":
            deut[ref.book] += 1
        else:
            ot[ref.book] += 1
    return nt, ot, deut


def _author_counts_by_group(references: Iterable[Reference]) -> dict[str, Counter[str]]:
    grouped: dict[str, Counter[str]] = {
        "new_testament": Counter(),
        "old_testament": Counter(),
        "deuterocanonical": Counter(),
    }
    for ref in references:
        if ref.testament_group == "new_testament":
            grouped["new_testament"][ref.author_id] += 1
        elif ref.testament_group == "deuterocanonical":
            grouped["deuterocanonical"][ref.author_id] += 1
        else:
            grouped["old_testament"][ref.author_id] += 1
    return grouped


def _render_top_table(counter: Counter[str], label: str, limit: int = 15) -> list[str]:
    lines = [f"| {label} | References |", "|---|---:|"]
    for item, count in counter.most_common(limit):
        lines.append(f"| {item} | {count} |")
    if len(lines) == 2:
        lines.append("| _(none)_ | 0 |")
    return lines


def _volume_totals(references: Iterable[Reference]) -> dict[str, Counter[str]]:
    per_volume: dict[str, Counter[str]] = defaultdict(Counter)
    for ref in references:
        key = "old_testament"
        if ref.testament_group == "new_testament":
            key = "new_testament"
        elif ref.testament_group == "deuterocanonical":
            key = "deuterocanonical"
        per_volume[ref.volume][key] += 1
        per_volume[ref.volume]["all"] += 1
    return dict(per_volume)


def write_markdown_report(path: Path, references: list[Reference]) -> None:
    nt_counts, ot_counts, deut_counts = _section_counts(references)
    author_counts = _author_counts_by_group(references)
    per_volume = _volume_totals(references)

    total_refs = len(references)
    nt_total = sum(nt_counts.values())
    ot_total = sum(ot_counts.values())
    deut_total = sum(deut_counts.values())

    share_nt = (nt_total / total_refs * 100) if total_refs else 0.0
    share_ot = (ot_total / total_refs * 100) if total_refs else 0.0
    share_deut = (deut_total / total_refs * 100) if total_refs else 0.0

    most_cited_book, most_cited_count = Counter(ref.book for ref in references).most_common(1)[0]
    psalm_chapter_counts = Counter(ref.chapter_start for ref in references if ref.book == "Ps" and ref.chapter_start)
    most_cited_psalm, most_cited_psalm_count = psalm_chapter_counts.most_common(1)[0] if psalm_chapter_counts else ("n/a", 0)
    most_nt_book, most_nt_count = nt_counts.most_common(1)[0] if nt_counts else ("n/a", 0)
    most_ot_book, most_ot_count = ot_counts.most_common(1)[0] if ot_counts else ("n/a", 0)
    most_deut_book, most_deut_count = deut_counts.most_common(1)[0] if deut_counts else ("n/a", 0)

    top_deut_volume = "n/a"
    top_deut_volume_count = 0
    if per_volume:
        top_deut_volume, counts = max(per_volume.items(), key=lambda item: item[1]["deuterocanonical"])
        top_deut_volume_count = counts["deuterocanonical"]

    quoted_books = {ref.book for ref in references}
    unquoted_books = [book for book in CANONICAL_BOOK_ORDER if book not in quoted_books]
    author_books: dict[str, set[str]] = defaultdict(set)
    author_deut_books: dict[str, set[str]] = defaultdict(set)
    for ref in references:
        author_books[ref.author_id].add(ref.book)
        if ref.book in DEUTEROCANONICAL_BOOKS:
            author_deut_books[ref.author_id].add(ref.book)
    broad_non_deut_authors = sorted(
        [
            author
            for author, books in author_books.items()
            if len(books) >= 15 and len(author_deut_books[author]) == 0
        ]
    )

    lines: list[str] = [
        "# Ante-Nicene Fathers Scripture Citation Report",
        "",
        "## Overall Summary",
        "",
        f"- Total references analyzed: **{total_refs}**",
        f"- New Testament references: **{nt_total}** ({share_nt:.1f}%)",
        f"- Old Testament references (excluding deuterocanonical): **{ot_total}** ({share_ot:.1f}%)",
        f"- Deuterocanonical references: **{deut_total}** ({share_deut:.1f}%)",
        "",
        "## Notable Events",
        "",
        f"1. Most cited book overall: **{most_cited_book}** ({most_cited_count} references).",
        f"2. Most cited New Testament book: **{most_nt_book}** ({most_nt_count} references).",
        f"3. Most cited Old Testament (non-deuterocanonical) book: **{most_ot_book}** ({most_ot_count} references).",
        f"4. Most cited deuterocanonical book: **{most_deut_book}** ({most_deut_count} references).",
        f"5. Volume with the most deuterocanonical references: **{top_deut_volume}** ({top_deut_volume_count} references).",
        "",
        "## Research-Question Snapshot",
        "",
        f"- Most frequently cited Psalm chapter: **Psalm {most_cited_psalm}** ({most_cited_psalm_count} references).",
        f"- Number of canonical books with zero citations in the parsed corpus: **{len(unquoted_books)}**.",
        (
            "- Fathers with broad coverage (15+ books) but no deuterocanonical citations: "
            f"**{', '.join(broad_non_deut_authors) if broad_non_deut_authors else 'none'}**."
        ),
        "- Detailed CSVs are generated in `outputs/question_*.csv` for Tobit locations, Psalm popularity, unquoted books, and author coverage.",
        "",
        "## New Testament",
        "",
        * _render_top_table(nt_counts, "Book"),
        "",
        "### Fathers (Top by NT citations)",
        "",
        * _render_top_table(author_counts["new_testament"], "Father", limit=20),
        "",
        "## Old Testament (non-deuterocanonical)",
        "",
        * _render_top_table(ot_counts, "Book"),
        "",
        "### Fathers (Top by OT citations)",
        "",
        * _render_top_table(author_counts["old_testament"], "Father", limit=20),
        "",
        "## Old Testament Deuterocanonicals",
        "",
        * _render_top_table(deut_counts, "Book"),
        "",
        "### Fathers (Top by deuterocanonical citations)",
        "",
        * _render_top_table(author_counts["deuterocanonical"], "Father", limit=20),
        "",
        "## Volume Breakdown",
        "",
        "| Volume | Total | NT | OT | Deuterocanonical |",
        "|---|---:|---:|---:|---:|",
    ]

    def _volume_sort_key(label: str) -> tuple[int, str]:
        suffix = label.rsplit("_", maxsplit=1)[-1]
        return (int(suffix), label) if suffix.isdigit() else (10_000, label)

    for volume in sorted(per_volume.keys(), key=_volume_sort_key):
        counts = per_volume[volume]
        lines.append(
            f"| {volume} | {counts['all']} | {counts['new_testament']} | {counts['old_testament']} | {counts['deuterocanonical']} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
