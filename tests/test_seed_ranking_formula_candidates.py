from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from scripts import seed_ranking_formula_candidates as seed
from src import ranking_formula_backtests as rfb


class _Done:
    def result(self):
        return None


class _FakeClient:
    def __init__(self):
        self.queries = []

    def query(self, sql, job_config=None):
        self.queries.append((sql, job_config))
        return _Done()


class RankingFormulaSeedTests(unittest.TestCase):
    def test_seed_payload_validates_with_expected_position_counts(self):
        payload = seed.build_seed_payload()
        candidates = payload["candidate_rows"]

        self.assertEqual(len(candidates), 12)
        self.assertEqual(
            {position: sum(1 for row in candidates if row["position"] == position) for position in rfb.POSITIONS},
            {"QB": 3, "RB": 3, "WR": 3, "TE": 3},
        )
        for row in candidates:
            self.assertEqual(row["status"], "draft")
            formula = json.loads(row["formula_json"])
            self.assertEqual(formula["score_expression"], "weighted_linear")
            rfb.validate_formula(formula)

    def test_formula_set_references_seeded_baseline_candidates(self):
        payload = seed.build_seed_payload()
        candidate_ids = {row["candidate_id"] for row in payload["candidate_rows"]}
        formula_set = payload["formula_set_row"]

        self.assertEqual(formula_set["status"], "draft")
        self.assertIn(formula_set["qb_candidate_id"], candidate_ids)
        self.assertIn(formula_set["rb_candidate_id"], candidate_ids)
        self.assertIn(formula_set["wr_candidate_id"], candidate_ids)
        self.assertIn(formula_set["te_candidate_id"], candidate_ids)

    def test_dry_run_summary_does_not_write(self):
        payload = seed.build_seed_payload()
        summary = seed.summarize_payload(payload, wrote=False)

        self.assertTrue(summary["dry_run"])
        self.assertFalse(summary["wrote"])
        self.assertEqual(summary["candidate_count"], 12)
        self.assertEqual(summary["target_tables"], ["ranking_formula_candidates", "ranking_formula_sets"])

    def test_apply_without_gate_fails_closed(self):
        fake = _FakeClient()
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(PermissionError, rfb.WRITE_GATE):
                seed.apply_seed(client=fake)

        self.assertEqual(fake.queries, [])

    def test_apply_targets_only_candidates_and_formula_sets(self):
        fake = _FakeClient()
        with patch.dict("os.environ", {rfb.WRITE_GATE: "true"}, clear=True):
            result = seed.apply_seed(client=fake)

        self.assertTrue(result["wrote"])
        self.assertEqual(result["candidate_count"], 12)
        self.assertEqual(result["formula_set_count"], 1)
        self.assertEqual(len(fake.queries), 13)
        joined_sql = "\n".join(sql for sql, _ in fake.queries)
        self.assertIn("ranking_formula_candidates", joined_sql)
        self.assertIn("ranking_formula_sets", joined_sql)
        self.assertNotIn("ranking_backtest_runs", joined_sql)
        self.assertNotIn("ranking_backtest_results", joined_sql)
        self.assertNotIn("ranking_backtest_candidate_summaries", joined_sql)
        self.assertNotIn("ranking_formula_champions", joined_sql)

    def test_seed_formulas_have_no_blocked_metrics_or_table_names(self):
        payload = seed.build_seed_payload()

        for row in payload["candidate_rows"]:
            formula_text = row["formula_json"]
            self.assertNotIn("weekly_metrics", formula_text)
            formula = json.loads(formula_text)
            self.assertFalse(set(formula["features"]) & set(rfb.BLOCKED_METRIC_FEATURES))


if __name__ == "__main__":
    unittest.main()
