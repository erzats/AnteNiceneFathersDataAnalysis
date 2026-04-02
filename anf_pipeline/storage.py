"""Persistent storage helpers for open-ended ANF citation analysis."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import Reference


TABLE_NAME = "bible_references"

REFERENCE_SCHEMA_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    volume TEXT NOT NULL,
    author_id TEXT NOT NULL,
    work_id TEXT NOT NULL,
    osis_ref TEXT NOT NULL,
    passage TEXT NOT NULL,
    book TEXT NOT NULL,
    testament_group TEXT NOT NULL,
    books_in_osis TEXT NOT NULL,
    chapter_start TEXT NOT NULL,
    verse_start TEXT NOT NULL
);
"""

REFERENCE_INDEXES_SQL = [
    f"CREATE INDEX IF NOT EXISTS idx_references_book ON {TABLE_NAME}(book);",
    f"CREATE INDEX IF NOT EXISTS idx_references_author ON {TABLE_NAME}(author_id);",
    f"CREATE INDEX IF NOT EXISTS idx_references_work ON {TABLE_NAME}(work_id);",
    f"CREATE INDEX IF NOT EXISTS idx_references_volume ON {TABLE_NAME}(volume);",
    f"CREATE INDEX IF NOT EXISTS idx_references_group ON {TABLE_NAME}(testament_group);",
]


def rebuild_reference_database(path: Path, references: list[Reference]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(REFERENCE_SCHEMA_SQL)
        for sql in REFERENCE_INDEXES_SQL:
            conn.execute(sql)
        conn.execute(f"DELETE FROM {TABLE_NAME};")
        conn.executemany(
            f"""
            INSERT INTO {TABLE_NAME} (
                volume,
                author_id,
                work_id,
                osis_ref,
                passage,
                book,
                testament_group,
                books_in_osis,
                chapter_start,
                verse_start
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            [
                (
                    ref.volume,
                    ref.author_id,
                    ref.work_id,
                    ref.osis_ref,
                    ref.passage,
                    ref.book,
                    ref.testament_group,
                    "|".join(ref.books_in_osis),
                    ref.chapter_start,
                    ref.verse_start,
                )
                for ref in references
            ],
        )
        conn.commit()


def run_sql_query(path: Path, sql: str, limit: int) -> tuple[list[str], list[tuple[object, ...]]]:
    statements = [segment.strip() for segment in sql.split(";") if segment.strip()]
    if not statements:
        return [], []

    with sqlite3.connect(path) as conn:
        columns: list[str] = []
        rows: list[tuple[object, ...]] = []
        for index, statement in enumerate(statements):
            cursor = conn.execute(statement)
            if index == len(statements) - 1:
                rows = cursor.fetchmany(limit)
                columns = [description[0] for description in cursor.description] if cursor.description else []
    return columns, rows
