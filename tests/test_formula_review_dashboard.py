from __future__ import annotations

import unittest
from pathlib import Path

from src.compat_flags import USE_FORMULA_COMPARISON_DASHBOARD, compat_flag_enabled
from src import formula_review_dashboard


SAMPLE_MARKDOWN = """
# Live 2026 Ranking Review Boards

Review version: `phase_test`

## Profile Decision Summary
| Scoring profile | Board status | Best review-only challenger | Decision |
|---|---|---|---|
| standard | ready with warnings | ranking_bqml_enriched_logistic_elite_v1 | Current Pigskin holds. |
| half_ppr | ready with warnings | ranking_bqml_enriched_logistic_elite_v1 | Current Pigskin holds. |
| ppr | ready with warnings | ranking_bqml_enriched_logistic_elite_v1 | Current Pigskin holds. |
| gng_keeper | ready with warnings | ranking_bqml_enriched_logistic_elite_v1 | Current Pigskin holds. |

## Candidate Coverage
| Profile | Position | Candidates |
|---|---|---|
| standard | TE | 213 |

## Model Summary
| Profile | Model | Predictions | Missing % |
|---|---|---|---|
| standard | enriched_logistic | 936 | 69.0% |
| standard | enriched_linear_points | 936 | 69.0% |

# Standard Review Boards

## BQML Logistic Top 50 Overall
| Logistic rank | Player | Pos | Team | Score | Current rank | Delta | Missing % |
|---|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey | RB | SF | 99.79 | 3 | +2 | 17.2% |
| 2 | Big WR Move | WR |  | 84.00 | 80 | +30 | 85.0% |

## Side-by-Side Top 100 Overall
| Rank | Current | Pos | Logistic | Pos | Score | Linear | Pos | Score |
|---|---|---|---|---|---|---|---|---|
| 1 | Jaxon Smith-Njigba | WR | Christian McCaffrey | RB | 99.79 | Player X | WR | 200.00 |

## TE Board Top 35
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 35 | Example TE | 10.00 | Example TE | 12.00 | Example TE | 14.00 |

## Logistic Risers
| Player | Pos | Current | Logistic | Delta | Missing % |
|---|---|---|---|---|---|
| Big WR Move | WR | 80 | 20 | +60 | 85.0% |

## Logistic Fallers
| Player | Pos | Current | Logistic | Delta | Missing % |
|---|---|---|---|---|---|
| Big WR Drop | WR | 10 | 60 | -50 | 82.0% |

## Cutline Crossings
| Model | Cutline | Entered | Entered sample | Exited | Exited sample |
|---|---|---|---|---|---|
| enriched_logistic | TE12 | 1 | Example TE | 1 | Other TE |

# Half PPR Review Boards
# PPR Review Boards
# GNG Keeper Review Boards
"""


class FormulaReviewDashboardTests(unittest.TestCase):
    def test_formula_review_flag_defaults_false(self):
        self.assertFalse(compat_flag_enabled(USE_FORMULA_COMPARISON_DASHBOARD, {}))
        self.assertTrue(
            compat_flag_enabled(
                USE_FORMULA_COMPARISON_DASHBOARD,
                {USE_FORMULA_COMPARISON_DASHBOARD: "true"},
            )
        )

    def test_scoring_profile_order_is_standard_first(self):
        self.assertEqual(
            [profile["id"] for profile in formula_review_dashboard.PROFILE_OPTIONS],
            ["standard", "half_ppr", "ppr", "gng_keeper"],
        )

    def test_payload_parses_profile_decisions_and_model_summary(self):
        payload = formula_review_dashboard.build_formula_review_payload(SAMPLE_MARKDOWN)

        self.assertEqual(payload["review_version"], "phase_test")
        self.assertEqual(len(payload["profile_decisions"]), 4)
        self.assertEqual(
            formula_review_dashboard.get_profile_decision(payload, "standard")["Board status"],
            "ready with warnings",
        )
        self.assertEqual(
            formula_review_dashboard.get_profile_model_summary(
                payload,
                "standard",
                "enriched_logistic",
            )["Missing %"],
            "69.0%",
        )

    def test_profile_tables_include_te35_and_cutlines(self):
        te_rows = formula_review_dashboard.get_profile_table(
            SAMPLE_MARKDOWN,
            "standard",
            formula_review_dashboard.POSITION_TABLES["TE"],
        )
        cutline_rows = formula_review_dashboard.get_profile_table(
            SAMPLE_MARKDOWN,
            "standard",
            "Cutline Crossings",
        )

        self.assertEqual(formula_review_dashboard.POSITION_TABLES["TE"], "TE Board Top 35")
        self.assertEqual(te_rows[0]["Rank"], "35")
        self.assertEqual(cutline_rows[0]["Cutline"], "TE12")

    def test_risk_filters_are_explicit_and_non_fallback(self):
        rows = formula_review_dashboard.get_profile_table(
            SAMPLE_MARKDOWN,
            "standard",
            "BQML Logistic Top 50 Overall",
        )

        movement_rows = formula_review_dashboard.filter_formula_review_rows(
            rows,
            ["movement over 20 ranks"],
        )
        missing_rows = formula_review_dashboard.filter_formula_review_rows(
            rows,
            ["high missingness"],
        )
        null_team_rows = formula_review_dashboard.filter_formula_review_rows(
            rows,
            ["null current team"],
        )

        self.assertEqual(movement_rows[0]["Player"], "Big WR Move")
        self.assertEqual(missing_rows[0]["Player"], "Big WR Move")
        self.assertEqual(null_team_rows[0]["Player"], "Big WR Move")

    def test_helper_stays_markdown_backed_and_read_only(self):
        source = Path("src/formula_review_dashboard.py").read_text(encoding="utf-8")

        self.assertIn("live-2026-ranking-review-boards.md", source)
        self.assertNotIn("google.cloud", source)
        self.assertNotIn("generate_pigskin_rankings", source)
        self.assertNotIn("GEMINI_API_KEY", source)
        self.assertNotIn("pigskin_context_score", source)

    def test_app_wires_default_off_formula_review_tab(self):
        app_source = Path("app.py").read_text(encoding="utf-8")

        self.assertIn("USE_FORMULA_COMPARISON_DASHBOARD", app_source)
        self.assertIn("use_formula_comparison_dashboard()", app_source)
        self.assertIn("render_formula_comparison_dashboard()", app_source)
        self.assertIn("Formula Review", app_source)
        self.assertNotIn("USE_FORMULA_COMPARISON_DASHBOARD=true", app_source)

    def test_formula_review_markdown_is_packaged_in_container(self):
        dashboard_doc = Path("docs/rebuild/live-2026-ranking-review-boards.md")
        dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

        self.assertTrue(dashboard_doc.exists())
        self.assertIn(
            "COPY docs/rebuild/live-2026-ranking-review-boards.md ./docs/rebuild/live-2026-ranking-review-boards.md",
            dockerfile,
        )


if __name__ == "__main__":
    unittest.main()
