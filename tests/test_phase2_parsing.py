"""Regression fixtures for Phase 2 parsing quality checks."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from anf_pipeline.parsing import parse_references


class Phase2ParsingRegressionTests(unittest.TestCase):
    def test_phase2_regression_fixtures(self) -> None:
        fixtures_path = Path("tests/fixtures/phase2_parsing_cases.json")
        fixtures = json.loads(fixtures_path.read_text(encoding="utf-8"))

        for case in fixtures:
            with self.subTest(case=case["name"]):
                with tempfile.TemporaryDirectory() as temp_dir:
                    html_path = Path(temp_dir) / case["filename"]
                    html_path.write_text(case["content"], encoding="utf-8")
                    references, report = parse_references(html_path)

                expected = case["expected"]
                self.assertEqual(len(references), expected["reference_count"])
                self.assertEqual(report.duplicate_rows_removed, expected["duplicate_rows_removed"])
                self.assertEqual(report.exact_quote_references, expected["exact_quote_references"])
                self.assertEqual(report.probable_allusion_references, expected["probable_allusion_references"])
                self.assertEqual(report.echo_allusion_references, expected["echo_allusion_references"])
                self.assertEqual(report.malformed_osis_references, expected["malformed_osis_references"])
                self.assertEqual(report.ambiguous_book_ids, expected["ambiguous_book_ids"])
                # Phase 6 verse-range fields — only checked when present in the fixture.
                if "verse_start" in expected:
                    self.assertEqual(references[0].verse_start, expected["verse_start"])
                if "verse_end" in expected:
                    self.assertEqual(references[0].verse_end, expected["verse_end"])
                if "chapter_start" in expected:
                    self.assertEqual(references[0].chapter_start, expected["chapter_start"])


if __name__ == "__main__":
    unittest.main()
