"""Tests for Phase 6 robustness hardening.

Covers:
- Three-tier confidence scoring (exact_citation / probable_allusion / echo_allusion)
- Verse-range expansion (verse_end / chapter_end fields on Reference)
- ParseReport echo_allusion_references counter
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from anf_pipeline.parsing import _ECHO_ALLUSION_WORD_THRESHOLD, parse_references


def _parse_html(content: str, filename: str = "AnteNiceneVolume1_fixture.html") -> tuple:
    with tempfile.TemporaryDirectory() as temp_dir:
        html_path = Path(temp_dir) / filename
        html_path.write_text(content, encoding="utf-8")
        return parse_references(html_path)


class TestThreeTierConfidenceScoring(unittest.TestCase):
    """scripRef → exact_citation; short scripCom → echo_allusion; long → probable_allusion."""

    def test_scrip_ref_is_exact_citation(self) -> None:
        content = (
            "<authorID>Irenaeus</authorID><workID>AH</workID>"
            "<scripRef osisRef='Bible:John.3.16'>For God so loved the world</scripRef>"
        )
        refs, report = _parse_html(content)
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].quote_confidence, "exact_citation")
        self.assertEqual(report.exact_quote_references, 1)
        self.assertEqual(report.probable_allusion_references, 0)
        self.assertEqual(report.echo_allusion_references, 0)

    def test_short_scrip_com_is_echo_allusion(self) -> None:
        # Passage below the threshold word count
        short_passage = " ".join(["word"] * (_ECHO_ALLUSION_WORD_THRESHOLD - 1))
        content = (
            f"<authorID>Origen</authorID><workID>Comm</workID>"
            f"<scripCom osisRef='Bible:Ps.22.1'>{short_passage}</scripCom>"
        )
        refs, report = _parse_html(content)
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].quote_confidence, "echo_allusion")
        self.assertEqual(report.echo_allusion_references, 1)
        self.assertEqual(report.probable_allusion_references, 0)

    def test_long_scrip_com_is_probable_allusion(self) -> None:
        # Passage at or above the threshold word count
        long_passage = " ".join(["word"] * _ECHO_ALLUSION_WORD_THRESHOLD)
        content = (
            f"<authorID>Tertullian</authorID><workID>AP</workID>"
            f"<scripCom osisRef='Bible:John.1.1'>{long_passage}</scripCom>"
        )
        refs, report = _parse_html(content)
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].quote_confidence, "probable_allusion")
        self.assertEqual(report.probable_allusion_references, 1)
        self.assertEqual(report.echo_allusion_references, 0)

    def test_empty_passage_is_echo_allusion(self) -> None:
        content = (
            "<authorID>Cyprian</authorID><workID>Unity</workID>"
            "<scripCom osisRef='Bible:Matt.16.18'></scripCom>"
        )
        refs, report = _parse_html(content)
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].quote_confidence, "echo_allusion")
        self.assertEqual(report.echo_allusion_references, 1)

    def test_mixed_confidence_tiers_counted_correctly(self) -> None:
        long_passage = " ".join(["word"] * _ECHO_ALLUSION_WORD_THRESHOLD)
        short_passage = "brief"
        content = (
            "<authorID>Justin</authorID><workID>Apol</workID>"
            f"<scripRef osisRef='Bible:John.1.14'>The Word became flesh</scripRef>"
            f"<scripCom osisRef='Bible:Ps.22.1'>{short_passage}</scripCom>"
            f"<scripCom osisRef='Bible:Rom.3.23'>{long_passage}</scripCom>"
        )
        refs, report = _parse_html(content)
        self.assertEqual(len(refs), 3)
        self.assertEqual(report.exact_quote_references, 1)
        self.assertEqual(report.echo_allusion_references, 1)
        self.assertEqual(report.probable_allusion_references, 1)

    def test_confidence_threshold_boundary_below(self) -> None:
        # Exactly (threshold - 1) words → echo_allusion
        passage = " ".join(["w"] * (_ECHO_ALLUSION_WORD_THRESHOLD - 1))
        content = (
            f"<authorID>A</authorID><workID>W</workID>"
            f"<scripCom osisRef='Bible:Gen.1.1'>{passage}</scripCom>"
        )
        refs, _ = _parse_html(content)
        self.assertEqual(refs[0].quote_confidence, "echo_allusion")

    def test_confidence_threshold_boundary_at(self) -> None:
        # Exactly threshold words → probable_allusion
        passage = " ".join(["w"] * _ECHO_ALLUSION_WORD_THRESHOLD)
        content = (
            f"<authorID>A</authorID><workID>W</workID>"
            f"<scripCom osisRef='Bible:Gen.1.1'>{passage}</scripCom>"
        )
        refs, _ = _parse_html(content)
        self.assertEqual(refs[0].quote_confidence, "probable_allusion")


class TestVerseRangeExpansion(unittest.TestCase):
    """verse_end and chapter_end are populated for range OSIS refs."""

    def test_single_verse_has_no_range(self) -> None:
        content = (
            "<authorID>A</authorID><workID>W</workID>"
            "<scripRef osisRef='Bible:Matt.5.3'>Blessed are the poor</scripRef>"
        )
        refs, _ = _parse_html(content)
        self.assertEqual(refs[0].verse_start, "3")
        self.assertEqual(refs[0].verse_end, "")
        self.assertEqual(refs[0].chapter_end, "")

    def test_verse_range_within_chapter(self) -> None:
        content = (
            "<authorID>A</authorID><workID>W</workID>"
            "<scripRef osisRef='Bible:Matt.5.3-12'>The beatitudes</scripRef>"
        )
        refs, _ = _parse_html(content)
        self.assertEqual(refs[0].chapter_start, "5")
        self.assertEqual(refs[0].verse_start, "3")
        self.assertEqual(refs[0].verse_end, "12")
        self.assertEqual(refs[0].chapter_end, "5")

    def test_verse_range_psalm(self) -> None:
        content = (
            "<authorID>A</authorID><workID>W</workID>"
            "<scripRef osisRef='Bible:Ps.119.1-8'>Blessed are those whose ways are blameless</scripRef>"
        )
        refs, _ = _parse_html(content)
        self.assertEqual(refs[0].book, "Ps")
        self.assertEqual(refs[0].verse_start, "1")
        self.assertEqual(refs[0].verse_end, "8")

    def test_verse_range_fully_qualified(self) -> None:
        # Bible:Matt.5.3-Matt.5.12
        content = (
            "<authorID>A</authorID><workID>W</workID>"
            "<scripRef osisRef='Bible:Matt.5.3-Matt.5.12'>The beatitudes passage</scripRef>"
        )
        refs, _ = _parse_html(content)
        self.assertEqual(refs[0].verse_start, "3")
        self.assertEqual(refs[0].verse_end, "12")

    def test_non_range_verse_end_empty_string(self) -> None:
        content = (
            "<authorID>A</authorID><workID>W</workID>"
            "<scripRef osisRef='Bible:John.3.16'>For God so loved</scripRef>"
        )
        refs, _ = _parse_html(content)
        self.assertIsInstance(refs[0].verse_end, str)
        self.assertEqual(refs[0].verse_end, "")

    def test_multiple_range_refs_all_parsed(self) -> None:
        content = (
            "<authorID>A</authorID><workID>W</workID>"
            "<scripRef osisRef='Bible:Matt.5.3-12'>Beatitudes text here</scripRef>"
            "<scripRef osisRef='Bible:Rom.8.1-4'>No condemnation for those in Christ Jesus</scripRef>"
        )
        refs, _ = _parse_html(content)
        self.assertEqual(len(refs), 2)
        self.assertEqual(refs[0].verse_end, "12")
        self.assertEqual(refs[1].verse_end, "4")
        self.assertEqual(refs[1].verse_start, "1")


class TestParseDiagnosticsReportNewFields(unittest.TestCase):
    """ParseReport exposes echo_allusion_references correctly."""

    def test_report_has_echo_allusion_field(self) -> None:
        content = "<authorID>A</authorID><workID>W</workID>"
        _, report = _parse_html(content)
        self.assertTrue(hasattr(report, "echo_allusion_references"))

    def test_report_echo_allusion_zero_when_no_scrip_com(self) -> None:
        content = (
            "<authorID>A</authorID><workID>W</workID>"
            "<scripRef osisRef='Bible:John.3.16'>For God so loved the world today</scripRef>"
        )
        _, report = _parse_html(content)
        self.assertEqual(report.echo_allusion_references, 0)

    def test_confidence_counts_sum_to_bible_references(self) -> None:
        long_passage = " ".join(["word"] * _ECHO_ALLUSION_WORD_THRESHOLD)
        content = (
            "<authorID>A</authorID><workID>W</workID>"
            "<scripRef osisRef='Bible:John.3.16'>For God so loved the world</scripRef>"
            f"<scripCom osisRef='Bible:Ps.22.1'>cry</scripCom>"
            f"<scripCom osisRef='Bible:Rom.3.23'>{long_passage}</scripCom>"
        )
        _, report = _parse_html(content)
        confidence_sum = (
            report.exact_quote_references
            + report.probable_allusion_references
            + report.echo_allusion_references
        )
        self.assertEqual(confidence_sum, report.bible_reference_tags)


if __name__ == "__main__":
    unittest.main()
