from __future__ import annotations

import unittest
from pathlib import Path

from src.pigskin_live_formula_context import load_pigskin_live_formula_context


class PigskinLiveFormulaContextTests(unittest.TestCase):
    def test_context_file_exists_and_names_current_pigskin_as_active(self):
        context_path = Path("docs/rebuild/pigskin-live-ranking-formula-context.md")
        self.assertTrue(context_path.exists())

        text = load_pigskin_live_formula_context()

        self.assertIn("Current Pigskin is the live ranking source", text)
        for profile_id in ("standard", "half_ppr", "ppr", "gng_keeper"):
            self.assertIn(profile_id, text)
        for position in ("QB top 45", "RB top 80", "WR top 100", "TE top 35"):
            self.assertIn(position, text)

    def test_context_keeps_challengers_review_only(self):
        text = load_pigskin_live_formula_context()

        self.assertIn("Enriched BQML Logistic Elite is review-only", text)
        self.assertIn("Enriched Linear Points is context only", text)
        self.assertIn("BQML NGS is context only", text)
        self.assertIn("No formula champion is active", text)
        self.assertIn("Do not claim `pigskin_context_score` exists", text)

    def test_app_prompt_and_container_include_context(self):
        app_source = Path("app.py").read_text(encoding="utf-8")
        dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

        self.assertIn("load_pigskin_live_formula_context()", app_source)
        self.assertIn("{live_formula_context}", app_source)
        self.assertIn(
            "COPY docs/rebuild/pigskin-live-ranking-formula-context.md ./docs/rebuild/pigskin-live-ranking-formula-context.md",
            dockerfile,
        )


if __name__ == "__main__":
    unittest.main()
