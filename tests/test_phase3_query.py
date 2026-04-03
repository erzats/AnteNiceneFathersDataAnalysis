"""Tests for Phase 3 query engine extensions.

Covers:
- Deuterocanonical inclusion/exclusion toggle
- Top-N books per author aggregation
- Minimum unique-books threshold filter
- quote_confidence filter in filter()
"""

from __future__ import annotations

import unittest

from anf_pipeline.models import Reference
from anf_pipeline.query import ReferenceQueryEngine


def _make_ref(
    *,
    author_id: str = "test_author",
    work_id: str = "test_work",
    book: str = "John",
    osis_ref: str = "Bible:John.3.16",
    passage: str = "For God so loved the world",
    testament_group: str = "new_testament",
    volume: str = "volume_1",
    quote_confidence: str = "exact_citation",
    verse_start: str = "16",
    chapter_start: str = "3",
    verse_end: str = "",
    chapter_end: str = "",
) -> Reference:
    return Reference(
        volume=volume,
        author_id=author_id,
        work_id=work_id,
        osis_ref=osis_ref,
        passage=passage,
        book=book,
        testament_group=testament_group,
        books_in_osis=(book,),
        chapter_start=chapter_start,
        verse_start=verse_start,
        quote_confidence=quote_confidence,
        verse_end=verse_end,
        chapter_end=chapter_end,
    )


class TestDeuterocanonicalToggle(unittest.TestCase):
    def setUp(self) -> None:
        self.refs = [
            _make_ref(book="Tob", testament_group="deuterocanonical", author_id="origen"),
            _make_ref(book="John", testament_group="new_testament", author_id="origen"),
            _make_ref(book="Wis", testament_group="deuterocanonical", author_id="tertullian"),
            _make_ref(book="Matt", testament_group="new_testament", author_id="tertullian"),
        ]
        self.engine = ReferenceQueryEngine(self.refs)

    def test_include_deuterocanonical_by_default(self) -> None:
        result = self.engine.filter()
        self.assertEqual(len(result), 4)

    def test_exclude_deuterocanonical(self) -> None:
        result = self.engine.filter(include_deuterocanonical=False)
        self.assertEqual(len(result), 2)
        books = {r.book for r in result}
        self.assertNotIn("Tob", books)
        self.assertNotIn("Wis", books)

    def test_exclude_deuterocanonical_combined_with_author_filter(self) -> None:
        result = self.engine.filter(author="origen", include_deuterocanonical=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].book, "John")


class TestQuoteConfidenceFilter(unittest.TestCase):
    def setUp(self) -> None:
        self.refs = [
            _make_ref(quote_confidence="exact_citation"),
            _make_ref(quote_confidence="probable_allusion"),
            _make_ref(quote_confidence="echo_allusion"),
        ]
        self.engine = ReferenceQueryEngine(self.refs)

    def test_filter_exact_citation(self) -> None:
        result = self.engine.filter(quote_confidence="exact_citation")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].quote_confidence, "exact_citation")

    def test_filter_probable_allusion(self) -> None:
        result = self.engine.filter(quote_confidence="probable_allusion")
        self.assertEqual(len(result), 1)

    def test_filter_echo_allusion(self) -> None:
        result = self.engine.filter(quote_confidence="echo_allusion")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].quote_confidence, "echo_allusion")

    def test_no_confidence_filter_returns_all(self) -> None:
        result = self.engine.filter()
        self.assertEqual(len(result), 3)


class TestTopBooksByAuthor(unittest.TestCase):
    def setUp(self) -> None:
        self.refs = [
            # Irenaeus: John x3, Matt x2, Rom x1
            _make_ref(author_id="irenaeus", book="John"),
            _make_ref(author_id="irenaeus", book="John"),
            _make_ref(author_id="irenaeus", book="John"),
            _make_ref(author_id="irenaeus", book="Matt"),
            _make_ref(author_id="irenaeus", book="Matt"),
            _make_ref(author_id="irenaeus", book="Rom"),
            # Tertullian: Matt x4, John x1
            _make_ref(author_id="tertullian", book="Matt"),
            _make_ref(author_id="tertullian", book="Matt"),
            _make_ref(author_id="tertullian", book="Matt"),
            _make_ref(author_id="tertullian", book="Matt"),
            _make_ref(author_id="tertullian", book="John"),
        ]
        self.engine = ReferenceQueryEngine(self.refs)

    def test_top_books_returns_all_authors(self) -> None:
        result = self.engine.top_books_by_author()
        self.assertIn("irenaeus", result)
        self.assertIn("tertullian", result)

    def test_irenaeus_top_book_is_john(self) -> None:
        result = self.engine.top_books_by_author()
        top_book, top_count = result["irenaeus"][0]
        self.assertEqual(top_book, "John")
        self.assertEqual(top_count, 3)

    def test_tertullian_top_book_is_matt(self) -> None:
        result = self.engine.top_books_by_author()
        top_book, top_count = result["tertullian"][0]
        self.assertEqual(top_book, "Matt")
        self.assertEqual(top_count, 4)

    def test_top_n_truncates_results(self) -> None:
        result = self.engine.top_books_by_author(top_n=2)
        self.assertLessEqual(len(result["irenaeus"]), 2)

    def test_top_1_returns_single_book(self) -> None:
        result = self.engine.top_books_by_author(top_n=1)
        self.assertEqual(len(result["irenaeus"]), 1)
        self.assertEqual(len(result["tertullian"]), 1)

    def test_empty_references_returns_empty_dict(self) -> None:
        engine = ReferenceQueryEngine([])
        self.assertEqual(engine.top_books_by_author(), {})


class TestAuthorsWithMinUniqueBooks(unittest.TestCase):
    def setUp(self) -> None:
        self.refs = [
            # origen: 3 unique books
            _make_ref(author_id="origen", book="John"),
            _make_ref(author_id="origen", book="Matt"),
            _make_ref(author_id="origen", book="Rom"),
            # repeated John for origen — still 3 unique
            _make_ref(author_id="origen", book="John"),
            # cyprian: 1 unique book
            _make_ref(author_id="cyprian", book="Matt"),
            # hermas: 2 unique books
            _make_ref(author_id="hermas", book="Rev"),
            _make_ref(author_id="hermas", book="Jas"),
        ]
        self.engine = ReferenceQueryEngine(self.refs)

    def test_min_1_returns_all_authors(self) -> None:
        result = self.engine.authors_with_min_unique_books(1)
        self.assertEqual(sorted(result), ["cyprian", "hermas", "origen"])

    def test_min_2_excludes_single_book_author(self) -> None:
        result = self.engine.authors_with_min_unique_books(2)
        self.assertNotIn("cyprian", result)
        self.assertIn("hermas", result)
        self.assertIn("origen", result)

    def test_min_3_returns_only_origen(self) -> None:
        result = self.engine.authors_with_min_unique_books(3)
        self.assertEqual(result, ["origen"])

    def test_min_4_returns_empty(self) -> None:
        result = self.engine.authors_with_min_unique_books(4)
        self.assertEqual(result, [])

    def test_result_is_sorted(self) -> None:
        result = self.engine.authors_with_min_unique_books(1)
        self.assertEqual(result, sorted(result))

    def test_repeated_citations_do_not_inflate_unique_count(self) -> None:
        # origen has 4 citation rows but only 3 unique books
        result = self.engine.authors_with_min_unique_books(4)
        self.assertNotIn("origen", result)


class TestExistingFilterMethodUnchanged(unittest.TestCase):
    """Ensure that existing filter() parameters still work correctly after Phase 3."""

    def setUp(self) -> None:
        self.refs = [
            _make_ref(author_id="irenaeus", book="John", volume="volume_1"),
            _make_ref(author_id="tertullian", book="Matt", volume="volume_3"),
            _make_ref(author_id="irenaeus", book="Rom", volume="volume_2"),
        ]
        self.engine = ReferenceQueryEngine(self.refs)

    def test_author_filter(self) -> None:
        result = self.engine.filter(author="irenaeus")
        self.assertEqual(len(result), 2)

    def test_book_filter(self) -> None:
        result = self.engine.filter(book="John")
        self.assertEqual(len(result), 1)

    def test_volume_filter(self) -> None:
        result = self.engine.filter(volume="volume_3")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].author_id, "tertullian")

    def test_combined_filters(self) -> None:
        result = self.engine.filter(author="irenaeus", volume="volume_1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].book, "John")


if __name__ == "__main__":
    unittest.main()
