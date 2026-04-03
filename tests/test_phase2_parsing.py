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
                self.assertEqual(report.malformed_osis_references, expected["malformed_osis_references"])
                self.assertEqual(report.ambiguous_book_ids, expected["ambiguous_book_ids"])


if __name__ == "__main__":
    unittest.main()
