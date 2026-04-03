"""MCP server exposing ANF Scripture citation data for open-ended AI queries.

Run with:
    python -m mcp_server.server

The server expects the SQLite database at the path given by the environment
variable ANF_DB_PATH, defaulting to outputs/anf_references.sqlite.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

DB_PATH = Path(os.environ.get("ANF_DB_PATH", "outputs/anf_references.sqlite"))

server = Server("anf-citations")


def _connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found at {DB_PATH}. "
            "Run the pipeline first: python data_processer.py"
        )
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_citations",
            description=(
                "Search Scripture citations from the Ante-Nicene Fathers. "
                "Filter by any combination of biblical book, author, testament group, "
                "volume, or quote confidence. Returns matching citation records."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "book": {
                        "type": "string",
                        "description": "OSIS book code (e.g. 'Matt', 'Ps', 'John', 'Tob'). "
                        "Use rank_books to discover valid codes.",
                    },
                    "author": {
                        "type": "string",
                        "description": "Author ID substring (e.g. 'origen', 'tertullian', 'clement'). Case-insensitive.",
                    },
                    "testament_group": {
                        "type": "string",
                        "enum": ["new_testament", "old_testament_or_other", "deuterocanonical"],
                        "description": "Filter by testament group.",
                    },
                    "volume": {
                        "type": "string",
                        "description": "Volume label (e.g. 'volume_1' through 'volume_9').",
                    },
                    "quote_confidence": {
                        "type": "string",
                        "enum": ["exact_citation", "probable_allusion"],
                        "description": "Filter by whether the citation is explicit or an allusion.",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 50,
                        "description": "Maximum number of results to return.",
                    },
                },
            },
        ),
        types.Tool(
            name="rank_books",
            description=(
                "Rank biblical books by citation frequency across the Ante-Nicene Fathers. "
                "Optionally filter by testament group or restrict to a single author."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "testament_group": {
                        "type": "string",
                        "enum": ["new_testament", "old_testament_or_other", "deuterocanonical"],
                        "description": "Only rank books in this testament group.",
                    },
                    "author": {
                        "type": "string",
                        "description": "Restrict ranking to citations by this author (substring match).",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "description": "Number of top books to return.",
                    },
                },
            },
        ),
        types.Tool(
            name="rank_authors",
            description=(
                "Rank Church Fathers by total citation count or by coverage breadth "
                "(number of unique books cited). Optionally filter by testament group."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "by": {
                        "type": "string",
                        "enum": ["total_citations", "unique_books"],
                        "default": "total_citations",
                        "description": "Ranking metric.",
                    },
                    "testament_group": {
                        "type": "string",
                        "enum": ["new_testament", "old_testament_or_other", "deuterocanonical"],
                        "description": "Restrict to citations from this testament group.",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "description": "Number of top authors to return.",
                    },
                },
            },
        ),
        types.Tool(
            name="rank_psalms",
            description=(
                "Rank individual Psalms by citation frequency. "
                "Optionally restrict to a specific author."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "author": {
                        "type": "string",
                        "description": "Restrict to citations by this author (substring match).",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 30,
                        "description": "Number of top Psalms to return.",
                    },
                },
            },
        ),
        types.Tool(
            name="get_author_coverage",
            description=(
                "For one or more Church Fathers, show which biblical books they cited, "
                "including deuterocanonical usage. If no author is specified, returns "
                "coverage for all authors."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "author": {
                        "type": "string",
                        "description": "Author ID substring (e.g. 'origen'). Omit for all authors.",
                    },
                },
            },
        ),
        types.Tool(
            name="find_unquoted_books",
            description=(
                "Return the list of canonical (and deuterocanonical) biblical books "
                "that were never cited anywhere in the Ante-Nicene Fathers corpus. "
                "Optionally restrict to a specific author to find gaps in their citations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "author": {
                        "type": "string",
                        "description": "Author ID (exact). Omit to check the entire corpus.",
                    },
                },
            },
        ),
        types.Tool(
            name="citations_by_century",
            description=(
                "Summarize citation patterns grouped by the approximate century of each "
                "Church Father (1st, 2nd, 3rd, or early 4th century). Useful for "
                "questions like 'which Psalm was most quoted in the 2nd century?'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "century": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4],
                        "description": "Filter to a specific century CE.",
                    },
                    "book": {
                        "type": "string",
                        "description": "Restrict to citations of this biblical book.",
                    },
                    "group_by": {
                        "type": "string",
                        "enum": ["century", "book", "author"],
                        "default": "century",
                        "description": "Dimension to group results by.",
                    },
                },
            },
        ),
        types.Tool(
            name="run_query",
            description=(
                "Execute a read-only SQL SELECT query directly against the ANF references "
                "database. The table is 'bible_references' with columns: "
                "id, volume, author_id, work_id, osis_ref, passage, book, "
                "testament_group, books_in_osis, chapter_start, verse_start, quote_confidence. "
                "Use this for custom or complex questions not covered by other tools."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "A SQL SELECT statement.",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 100,
                        "description": "Maximum rows to return.",
                    },
                },
                "required": ["sql"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    try:
        result = _dispatch(name, arguments)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    except FileNotFoundError as exc:
        return [types.TextContent(type="text", text=f"Error: {exc}")]
    except Exception as exc:
        return [types.TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


def _dispatch(name: str, args: dict[str, Any]) -> Any:
    if name == "search_citations":
        return _search_citations(args)
    if name == "rank_books":
        return _rank_books(args)
    if name == "rank_authors":
        return _rank_authors(args)
    if name == "rank_psalms":
        return _rank_psalms(args)
    if name == "get_author_coverage":
        return _get_author_coverage(args)
    if name == "find_unquoted_books":
        return _find_unquoted_books(args)
    if name == "citations_by_century":
        return _citations_by_century(args)
    if name == "run_query":
        return _run_query(args)
    raise ValueError(f"Unknown tool: {name}")


def _search_citations(args: dict[str, Any]) -> list[dict[str, Any]]:
    clauses = []
    params: list[Any] = []

    if book := args.get("book"):
        clauses.append("book = ?")
        params.append(book)
    if author := args.get("author"):
        clauses.append("author_id LIKE ?")
        params.append(f"%{author}%")
    if tg := args.get("testament_group"):
        clauses.append("testament_group = ?")
        params.append(tg)
    if volume := args.get("volume"):
        clauses.append("volume = ?")
        params.append(volume)
    if confidence := args.get("quote_confidence"):
        clauses.append("quote_confidence = ?")
        params.append(confidence)

    limit = int(args.get("limit", 50))
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT volume, author_id, work_id, book, chapter_start, verse_start, quote_confidence, testament_group, osis_ref, passage FROM bible_references {where} LIMIT ?"
    params.append(limit)

    with _connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return _rows_to_dicts(rows)


def _rank_books(args: dict[str, Any]) -> list[dict[str, Any]]:
    clauses = []
    params: list[Any] = []

    if tg := args.get("testament_group"):
        clauses.append("testament_group = ?")
        params.append(tg)
    if author := args.get("author"):
        clauses.append("author_id LIKE ?")
        params.append(f"%{author}%")

    limit = int(args.get("limit", 20))
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT book, COUNT(*) AS citation_count FROM bible_references {where} GROUP BY book ORDER BY citation_count DESC LIMIT ?"
    params.append(limit)

    with _connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return _rows_to_dicts(rows)


def _rank_authors(args: dict[str, Any]) -> list[dict[str, Any]]:
    by = args.get("by", "total_citations")
    clauses = []
    params: list[Any] = []

    if tg := args.get("testament_group"):
        clauses.append("testament_group = ?")
        params.append(tg)

    limit = int(args.get("limit", 20))
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    if by == "unique_books":
        sql = f"SELECT author_id, COUNT(DISTINCT book) AS unique_books FROM bible_references {where} GROUP BY author_id ORDER BY unique_books DESC LIMIT ?"
    else:
        sql = f"SELECT author_id, COUNT(*) AS total_citations FROM bible_references {where} GROUP BY author_id ORDER BY total_citations DESC LIMIT ?"

    params.append(limit)

    with _connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return _rows_to_dicts(rows)


def _rank_psalms(args: dict[str, Any]) -> list[dict[str, Any]]:
    clauses = ["book = 'Ps'", "chapter_start != ''"]
    params: list[Any] = []

    if author := args.get("author"):
        clauses.append("author_id LIKE ?")
        params.append(f"%{author}%")

    limit = int(args.get("limit", 30))
    where = "WHERE " + " AND ".join(clauses)
    sql = f"SELECT chapter_start AS psalm, COUNT(*) AS citation_count FROM bible_references {where} GROUP BY chapter_start ORDER BY citation_count DESC LIMIT ?"
    params.append(limit)

    with _connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return _rows_to_dicts(rows)


def _get_author_coverage(args: dict[str, Any]) -> list[dict[str, Any]]:
    clauses = []
    params: list[Any] = []

    if author := args.get("author"):
        clauses.append("author_id LIKE ?")
        params.append(f"%{author}%")

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"""
        SELECT
            author_id,
            COUNT(DISTINCT book) AS unique_books,
            COUNT(DISTINCT CASE WHEN testament_group='deuterocanonical' THEN book END) AS deuterocanonical_books,
            COUNT(*) AS total_citations
        FROM bible_references
        {where}
        GROUP BY author_id
        ORDER BY total_citations DESC
    """

    with _connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return _rows_to_dicts(rows)


def _find_unquoted_books(args: dict[str, Any]) -> dict[str, Any]:
    from .constants import CANONICAL_BOOK_ORDER  # local import to avoid circular at module level

    clauses = []
    params: list[Any] = []

    if author := args.get("author"):
        clauses.append("author_id = ?")
        params.append(author)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT DISTINCT book FROM bible_references {where}"

    with _connect() as conn:
        cited = {row["book"] for row in conn.execute(sql, params).fetchall()}

    unquoted = [b for b in CANONICAL_BOOK_ORDER if b not in cited]
    return {"unquoted_books": unquoted, "count": len(unquoted)}


def _citations_by_century(args: dict[str, Any]) -> list[dict[str, Any]]:
    from .constants import AUTHOR_METADATA  # local import

    century_filter = args.get("century")
    book_filter = args.get("book")
    group_by = args.get("group_by", "century")

    # Build a mapping author_id -> century from metadata
    author_centuries: dict[str, int | None] = {
        aid: meta.get("century")  # type: ignore[assignment]
        for aid, meta in AUTHOR_METADATA.items()
    }

    clauses = []
    params: list[Any] = []

    if book_filter:
        clauses.append("book = ?")
        params.append(book_filter)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT author_id, book, chapter_start, COUNT(*) AS cnt FROM bible_references {where} GROUP BY author_id, book, chapter_start"

    with _connect() as conn:
        rows = _rows_to_dicts(conn.execute(sql, params).fetchall())

    # Annotate each row with century
    for row in rows:
        row["century"] = author_centuries.get(row["author_id"])

    # Apply century filter
    if century_filter is not None:
        rows = [r for r in rows if r.get("century") == century_filter]

    # Group results
    from collections import defaultdict

    if group_by == "century":
        grouped: dict[Any, int] = defaultdict(int)
        for row in rows:
            grouped[row["century"]] += row["cnt"]
        return [{"century": k, "citation_count": v} for k, v in sorted(grouped.items(), key=lambda x: (x[0] is None, x[0]))]

    if group_by == "book":
        grouped = defaultdict(int)
        for row in rows:
            grouped[row["book"]] += row["cnt"]
        return [{"book": k, "citation_count": v} for k, v in sorted(grouped.items(), key=lambda x: -x[1])]

    if group_by == "author":
        grouped = defaultdict(int)
        for row in rows:
            grouped[row["author_id"]] += row["cnt"]
        return [{"author_id": k, "citation_count": v} for k, v in sorted(grouped.items(), key=lambda x: -x[1])]

    return rows


def _run_query(args: dict[str, Any]) -> list[dict[str, Any]]:
    sql = args["sql"].strip()
    if not sql.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")
    limit = int(args.get("limit", 100))
    # Apply limit if not already present
    if "LIMIT" not in sql.upper():
        sql = f"{sql} LIMIT {limit}"

    with _connect() as conn:
        rows = conn.execute(sql).fetchmany(limit)
    return _rows_to_dicts(rows)


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
