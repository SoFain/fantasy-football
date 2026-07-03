from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from src import ranking_formula_backtests as rfb


class _Done:
    def result(self):
        return None


class _FakeClient:
    def __init__(self):
        self.loaded = []
        self.queries = []

    def load_table_from_json(self, rows, table):
        self.loaded.append((rows, table))
        return _Done()

    def query(self, sql):
        self.queries.append(sql)
        return _Done()


class RankingFormulaBacktestTests(unittest.TestCase):
    def test_default_qb_formula_validates(self):
        formula = rfb.validate_formula(rfb.default_formula("QB"))

        self.assertEqual(formula["position"], "QB")
        self.assertEqual(formula["score_expression"], "weighted_linear")
        self.assertIn("passing_epa_per_play", formula["features"])

    def test_unknown_position_rejected(self):
        with self.assertRaises(rfb.FormulaValidationError):
            rfb.validate_formula({"position": "K", "score_expression": "weighted_linear", "features": ["actual_points"], "weights": {"actual_points": 1}})

    def test_unknown_feature_rejected(self):
        formula = rfb.default_formula("RB")
        formula["features"] = ["not_a_real_feature"]
        formula["weights"] = {"not_a_real_feature": 1}

        with self.assertRaisesRegex(rfb.FormulaValidationError, "not allowed"):
            rfb.validate_formula(formula)

    def test_missing_required_formula_field_rejected(self):
        formula = rfb.default_formula("QB")
        del formula["version"]

        with self.assertRaisesRegex(rfb.FormulaValidationError, "formula.version is required"):
            rfb.validate_formula(formula)

    def test_code_like_expression_rejected(self):
        formula = rfb.default_formula("QB")
        formula["normalization"] = {"method": "__import__('os').system('whoami')"}

        with self.assertRaisesRegex(rfb.FormulaValidationError, "SQL or executable code"):
            rfb.validate_formula(formula)

    def test_table_name_expression_rejected(self):
        formula = rfb.default_formula("WR")
        formula["features"] = ["weekly_metrics"]
        formula["weights"] = {"weekly_metrics": 1}

        with self.assertRaisesRegex(rfb.FormulaValidationError, "SQL or executable code"):
            rfb.validate_formula(formula)

    def test_score_range_validation(self):
        self.assertEqual(rfb.validate_score(100), 100)
        with self.assertRaisesRegex(rfb.FormulaValidationError, "between 0 and 100"):
            rfb.validate_score(101, field_name="predicted_score")

    def test_allowed_input_table_list_enforced(self):
        self.assertEqual(
            rfb.validate_input_tables(["analytics_player_weekly_truth"]),
            ["analytics_player_weekly_truth"],
        )
        with self.assertRaisesRegex(rfb.FormulaValidationError, "SQL or executable code"):
            rfb.validate_input_tables(["weekly_metrics"])

    def test_sql_like_feature_rejected(self):
        formula = rfb.default_formula("WR")
        formula["features"] = ["SELECT * FROM weekly_metrics"]
        formula["weights"] = {"SELECT * FROM weekly_metrics": 1}

        with self.assertRaisesRegex(rfb.FormulaValidationError, "SQL"):
            rfb.validate_formula(formula)

    def test_blocked_metric_requires_source_flag(self):
        formula = rfb.default_formula("WR")
        formula["features"] = ["route_share"]
        formula["weights"] = {"route_share": 1}

        with self.assertRaisesRegex(rfb.FormulaValidationError, "route_share_available"):
            rfb.validate_formula(formula)

    def test_blocked_metric_allowed_when_source_flag_true(self):
        formula = rfb.default_formula("WR")
        formula["features"] = ["route_share"]
        formula["weights"] = {"route_share": 1}
        formula["source_flags"] = {"route_share_available": True}

        validated = rfb.validate_formula(formula)

        self.assertEqual(validated["features"], ["route_share"])

    def test_build_candidate_row_has_contract_json(self):
        row = rfb.build_candidate_row(rfb.default_formula("TE"), formula_name="TE baseline")

        self.assertEqual(row["position"], "TE")
        self.assertEqual(row["status"], "draft")
        self.assertEqual(json.loads(row["formula_json"])["position"], "TE")
        self.assertIn("allowed_input_tables", json.loads(row["source_requirements_json"]))

    def test_dry_run_plan_is_non_mutating(self):
        fake = _FakeClient()
        result = rfb.run_backtest_skeleton(
            [rfb.default_formula("QB"), rfb.default_formula("RB")],
            season_start=2014,
            season_end=2014,
            dry_run=True,
            client=fake,
        )

        self.assertTrue(result["dry_run"])
        self.assertFalse(result["write"])
        self.assertEqual(result["candidate_count"], 2)
        self.assertEqual(len(result["candidate_summary_rows"]), 2)
        self.assertEqual(fake.loaded, [])
        self.assertEqual(fake.queries, [])

    def test_write_requires_ranking_formula_gate(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(PermissionError, rfb.WRITE_GATE):
                rfb.run_backtest_skeleton(
                    [rfb.default_formula("QB")],
                    season_start=2014,
                    season_end=2014,
                    write=True,
                )

    def test_unrelated_trade_score_gate_does_not_authorize_writes(self):
        with patch.dict("os.environ", {"ALLOW_TRADE_SCORE_MATERIALIZATION": "true"}, clear=True):
            with self.assertRaisesRegex(PermissionError, rfb.WRITE_GATE):
                rfb.run_backtest_skeleton(
                    [rfb.default_formula("QB")],
                    season_start=2014,
                    season_end=2014,
                    write=True,
                )

    def test_authorized_write_uses_only_ranking_tables(self):
        fake = _FakeClient()
        with patch.dict("os.environ", {rfb.WRITE_GATE: "true"}, clear=True):
            result = rfb.run_backtest_skeleton(
                [rfb.default_formula("QB")],
                season_start=2014,
                season_end=2014,
                write=True,
                dry_run=False,
                client=fake,
            )

        self.assertTrue(result["write"])
        self.assertEqual(result["write_summary"]["candidate_row_count"], 1)
        self.assertEqual(result["write_summary"]["candidate_summary_row_count"], 1)
        self.assertEqual(len(fake.loaded), 3)
        self.assertEqual(len(fake.queries), 3)
        joined_sql = "\n".join(fake.queries)
        self.assertIn("ranking_formula_candidates", joined_sql)
        self.assertIn("ranking_backtest_runs", joined_sql)
        self.assertIn("ranking_backtest_candidate_summaries", joined_sql)
        self.assertNotIn("trade_player_scores", joined_sql)
        self.assertNotIn("weekly_metrics", joined_sql)

    def test_candidate_summary_shape_includes_metrics(self):
        result = rfb.run_backtest_skeleton(
            [rfb.default_formula("TE")],
            season_start=2014,
            season_end=2014,
            dry_run=True,
        )

        summary = result["candidate_summary_rows"][0]
        self.assertEqual(summary["sample_size"], 0)
        self.assertIn("pairwise_win_rate", summary)
        self.assertIn("top_n_hit_rate", summary)
        self.assertIn("rank_correlation", summary)
        self.assertIn("missing_input_rate", summary)
        self.assertIn("metric_json", summary)
        self.assertIn("missing_flags_json", summary)

    def test_pigskin_declarations_do_not_expose_ranking_formula_tables(self):
        inspected_paths = (
            "app.py",
            "src/pigskin_context_tools.py",
            "src/pigskin_packet_guardrails.py",
        )
        combined = "\n".join(Path(path).read_text(encoding="utf-8") for path in inspected_paths)

        self.assertNotIn("ranking_formula_candidates", combined)
        self.assertNotIn("ranking_backtest_results", combined)
        self.assertNotIn("ALLOW_RANKING_FORMULA_BACKTEST_WRITE", combined)

    def test_merge_sql_uses_contract_key(self):
        sql = rfb.build_merge_sql(
            project_id="p",
            dataset_id="d",
            table_name="ranking_backtest_results",
            staging_table_name="ranking_backtest_results_staging",
            key_fields=("backtest_run_id", "candidate_id", "season", "week", "player_id_internal"),
        )

        self.assertIn("target.backtest_run_id = source.backtest_run_id", sql)
        self.assertIn("target.player_id_internal = source.player_id_internal", sql)
        self.assertIn("WHEN NOT MATCHED THEN INSERT", sql)


if __name__ == "__main__":
    unittest.main()
