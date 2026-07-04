from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from src import ranking_formula_backtests as rfb


class _Done:
    def __init__(self, rows=None):
        self._rows = rows or []

    def result(self):
        return self._rows


class _FakeClient:
    def __init__(self, rows=None):
        self.loaded = []
        self.queries = []
        self.rows = rows or []

    def load_table_from_json(self, rows, table):
        self.loaded.append((rows, table))
        return _Done()

    def query(self, sql, job_config=None):
        self.queries.append((sql, job_config))
        return _Done(self.rows)


class _SequencedFakeClient:
    def __init__(self, row_batches):
        self.row_batches = list(row_batches)
        self.queries = []

    def query(self, sql, job_config=None):
        self.queries.append((sql, job_config))
        if not self.row_batches:
            return _Done([])
        return _Done(self.row_batches.pop(0))


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
        joined_sql = "\n".join(sql for sql, _ in fake.queries)
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

    def test_seeded_candidate_loader_uses_parameterized_query(self):
        candidate = rfb.build_candidate_row(
            rfb.default_formula("QB"),
            formula_name="QB Seed",
            candidate_id="candidate-qb",
            formula_set_id="set-1",
        )
        fake = _FakeClient(rows=[candidate])

        loaded = rfb.load_ranking_formula_candidates(
            client=fake,
            position="QB",
            candidate_ids=["candidate-qb"],
            status="draft",
        )

        self.assertEqual(loaded[0]["candidate_id"], "candidate-qb")
        sql, job_config = fake.queries[0]
        self.assertIn("@status", sql)
        self.assertIn("@candidate_ids", sql)
        parameter_names = {param.name for param in job_config.query_parameters}
        self.assertIn("status", parameter_names)
        self.assertIn("candidate_ids", parameter_names)

    def test_loader_validates_returned_formula_json(self):
        candidate = rfb.build_candidate_row(
            rfb.default_formula("QB"),
            formula_name="QB Seed",
            candidate_id="candidate-qb",
            formula_set_id="set-1",
        )
        candidate["formula_json"] = json.dumps(
            {
                "version": "x",
                "position": "QB",
                "score_expression": "weighted_linear",
                "features": ["weekly_metrics"],
                "weights": {"weekly_metrics": 1},
                "normalization": {"method": "position_percentile"},
            }
        )
        fake = _FakeClient(rows=[candidate])

        with self.assertRaisesRegex(rfb.FormulaValidationError, "SQL or executable code"):
            rfb.load_ranking_formula_candidates(client=fake, position="QB")

    def test_formula_set_loader_returns_candidate_references(self):
        formula_set = {
            "formula_set_id": "set-1",
            "formula_set_name": "Set",
            "formula_set_version": "v1",
            "qb_candidate_id": "qb",
            "rb_candidate_id": "rb",
            "wr_candidate_id": "wr",
            "te_candidate_id": "te",
            "status": "draft",
            "description": None,
            "created_by": "test",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": None,
            "notes": None,
        }
        fake = _FakeClient(rows=[formula_set])

        loaded = rfb.load_ranking_formula_set(client=fake, formula_set_id="set-1")

        self.assertEqual(loaded["qb_candidate_id"], "qb")
        self.assertEqual(loaded["te_candidate_id"], "te")

    def test_all_position_candidates_for_formula_set_loads_three_draft_rows(self):
        formula_set = {
            "formula_set_id": "set-1",
            "formula_set_name": "Set",
            "formula_set_version": "v1",
            "qb_candidate_id": "qb-balanced",
            "rb_candidate_id": "rb-balanced",
            "wr_candidate_id": "wr-balanced",
            "te_candidate_id": "te-balanced",
            "status": "draft",
            "description": None,
            "created_by": "test",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": None,
            "notes": None,
        }
        candidates = [
            rfb.build_candidate_row(
                rfb.default_formula("TE"),
                formula_name=f"TE {index}",
                candidate_id=f"te-{index}",
                formula_set_id="set-1",
            )
            for index in range(3)
        ]
        fake = _SequencedFakeClient([ [formula_set], candidates ])

        loaded = rfb.load_all_position_candidates_for_formula_set(
            client=fake,
            formula_set_id="set-1",
            position="TE",
        )

        self.assertEqual(len(loaded), 3)
        candidate_sql, candidate_job_config = fake.queries[1]
        self.assertIn("formula_set_id = @formula_set_id", candidate_sql)
        parameter_names = {param.name for param in candidate_job_config.query_parameters}
        self.assertIn("formula_set_id", parameter_names)

    def test_invalid_status_rejected(self):
        with self.assertRaisesRegex(rfb.FormulaValidationError, "Unsupported candidate status"):
            rfb.load_ranking_formula_candidates(client=_FakeClient(), status="archived")

    def test_unbounded_real_data_dry_run_rejected(self):
        with self.assertRaisesRegex(rfb.FormulaValidationError, "season span"):
            rfb.load_bounded_feature_rows(
                client=_FakeClient(),
                position="QB",
                season_start=2014,
                season_end=2016,
                week_start=1,
                week_end=4,
                scoring_profile_id="ppr",
                league_type_id="redraft",
                roster_format_id="one_qb",
                limit=100,
            )

    def test_result_shape_and_missing_feature_flags(self):
        candidate = rfb.build_candidate_row(
            rfb.default_formula("QB"),
            formula_name="QB Seed",
            candidate_id="candidate-qb",
            formula_set_id="set-1",
        )
        feature_rows = [
            {
                "season": 2014,
                "week": 1,
                "player_id_internal": "00-1",
                "player_name": "QB One",
                "position": "QB",
                "team": "ABC",
                "actual_points": 20.0,
                "passing_epa_per_play": None,
                "passing_success_rate": None,
                "cpoe": 0.05,
            }
        ]

        result_rows = rfb.build_result_rows_for_candidates(
            candidates=[candidate],
            feature_rows=feature_rows,
            backtest_run_id="run-1",
            formula_set_id="set-1",
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
            target_name="top_12_position",
        )

        row = result_rows[0]
        self.assertEqual(row["candidate_id"], "candidate-qb")
        self.assertEqual(row["season"], 2014)
        self.assertIn("feature_values_json", row)
        missing = json.loads(row["missing_flags_json"])["missing_features"]
        self.assertIn("passing_epa_per_play", missing)
        self.assertIn("pigskin_context_score", missing)

    def test_summary_shape_includes_candidate_level_metrics(self):
        candidate = rfb.build_candidate_row(
            rfb.default_formula("RB"),
            formula_name="RB Seed",
            candidate_id="candidate-rb",
            formula_set_id="set-1",
        )
        result_rows = [
            {
                "candidate_id": "candidate-rb",
                "predicted_score": 50.0,
                "predicted_rank_position": 1,
                "actual_rank_position": 1,
                "target_hit": True,
                "missing_flags_json": json.dumps({"missing_features": ["pigskin_context_score"]}),
            }
        ]

        summary = rfb.build_summary_from_results(
            candidate_row=candidate,
            result_rows=result_rows,
            backtest_run_id="run-1",
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
            target_name="top_12_position",
        )

        self.assertEqual(summary["sample_size"], 1)
        self.assertEqual(summary["top_n_hit_rate"], 1.0)
        self.assertIn("missing_input_rate", summary)
        metric_payload = json.loads(summary["metric_json"])
        missing_payload = json.loads(summary["missing_flags_json"])
        self.assertEqual(metric_payload["expected_feature_count"], 4)
        self.assertEqual(metric_payload["available_feature_count"], 3)
        self.assertEqual(metric_payload["missing_feature_count"], 1)
        self.assertEqual(missing_payload["missing_feature_names"], ["pigskin_context_score"])

    def test_air_yards_share_proxy_scores_as_percentage(self):
        self.assertEqual(rfb._feature_value_to_score("air_yards", 0.42), 42.0)

    def test_unavailable_supported_feature_stays_missing_not_zero_filled(self):
        formula = {
            "version": "ranking_formula_v0_2026_001",
            "position": "WR",
            "score_expression": "weighted_linear",
            "features": ["targets", "receiving_yards"],
            "weights": {"targets": 0.5, "receiving_yards": 0.5},
            "normalization": {"method": "position_percentile"},
            "source_flags": {},
        }
        result = rfb.evaluate_formula_for_feature_row(
            rfb.validate_formula(formula),
            {"targets": 8, "receiving_yards": None},
        )

        self.assertIn("receiving_yards", result["missing_features"])
        self.assertNotIn("receiving_yards", result["feature_values"])

    def test_feature_and_target_availability_reports_missing_inputs(self):
        candidate = rfb.build_candidate_row(
            {
                "version": "ranking_formula_v0_2026_001",
                "position": "TE",
                "score_expression": "weighted_linear",
                "features": ["targets", "receiving_yards", "pigskin_context_score"],
                "weights": {"targets": 0.4, "receiving_yards": 0.4, "pigskin_context_score": 0.2},
                "normalization": {"method": "position_percentile"},
                "source_flags": {},
            },
            formula_name="TE Seed",
            candidate_id="candidate-te",
            formula_set_id="set-1",
        )
        feature_rows = [
            {
                "season": 2025,
                "week": 18,
                "player_id_internal": "00-0037744",
                "player_name": "Trey McBride",
                "position": "TE",
                "targets": 8,
                "receiving_yards": 50,
                "actual_points": 16.2,
            }
        ]

        feature_report = rfb.build_feature_availability_report([candidate], feature_rows)
        target_report = rfb.build_target_availability_report(feature_rows)

        candidate_report = feature_report["candidate-te"]
        self.assertEqual(candidate_report["targets"]["available_count"], 1)
        self.assertEqual(candidate_report["pigskin_context_score"]["available_count"], 0)
        self.assertTrue(target_report["target_available"])
        self.assertEqual(target_report["target_row_count"], 1)

    def test_no_lookahead_backtest_requires_future_target_season(self):
        with self.assertRaisesRegex(rfb.FormulaValidationError, "avoid lookahead"):
            rfb.run_no_lookahead_backtest(
                client=_FakeClient(),
                formula_set_id="set-1",
                source_season=2025,
                target_season=2025,
                target_week_start=1,
                target_week_end=18,
                scoring_profile_ids=["ppr"],
                positions=["QB"],
            )

    def test_no_lookahead_backtest_evaluates_three_candidates_for_profile(self):
        formula_set = self._formula_set()
        candidates = [
            rfb.build_candidate_row(
                rfb.default_formula("QB"),
                formula_name=f"QB {index}",
                candidate_id=f"qb-{index}",
                formula_set_id="set-1",
            )
            for index in range(3)
        ]
        feature_rows = [
            self._feature_row("00-1", "QB One", 28.0, 0.22),
            self._feature_row("00-2", "QB Two", 18.0, 0.10),
        ]
        fake = _SequencedFakeClient([[formula_set], candidates, feature_rows])

        result = rfb.run_no_lookahead_backtest(
            client=fake,
            formula_set_id="set-1",
            source_season=2024,
            target_season=2025,
            target_week_start=1,
            target_week_end=18,
            scoring_profile_ids=["ppr"],
            positions=["QB"],
            dry_run=True,
        )

        self.assertTrue(result["dry_run"])
        self.assertEqual(result["candidate_count"], 3)
        self.assertEqual(len(result["backtest_run_rows"]), 1)
        self.assertEqual(len(result["result_rows"]), 6)
        self.assertEqual(len(result["candidate_summary_rows"]), 3)
        self.assertEqual(result["backtest_run_rows"][0]["backtest_run_id"], "ranking_backtest_v0_2024_to_2025_ppr")
        self.assertEqual(result["result_rows"][0]["season"], 2025)
        self.assertEqual(result["result_rows"][0]["scoring_profile_id"], "ppr")

    def test_no_lookahead_backtest_version_controls_run_ids(self):
        formula_set = self._formula_set()
        candidates = [
            rfb.build_candidate_row(
                rfb.default_formula("QB"),
                formula_name=f"QB {index}",
                candidate_id=f"qb-{index}",
                formula_set_id="set-1",
            )
            for index in range(3)
        ]
        fake = _SequencedFakeClient([[formula_set], candidates, []])

        result = rfb.run_no_lookahead_backtest(
            client=fake,
            formula_set_id="set-1",
            source_season=2024,
            target_season=2025,
            target_week_start=1,
            target_week_end=18,
            scoring_profile_ids=["ppr"],
            positions=["QB"],
            backtest_version="v1",
            dry_run=True,
        )

        self.assertEqual(result["backtest_version"], "v1")
        self.assertEqual(result["backtest_run_rows"][0]["backtest_run_id"], "ranking_backtest_v1_2024_to_2025_ppr")

    def test_no_lookahead_feature_query_uses_safe_v1_source_mappings(self):
        fake = _FakeClient(rows=[])

        rfb.load_no_lookahead_feature_rows(
            client=fake,
            position="WR",
            source_season=2024,
            target_season=2025,
            target_week_start=1,
            target_week_end=18,
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
        )

        sql, _ = fake.queries[0]
        self.assertIn("pigskin_player_context_packet_current", sql)
        self.assertIn("packet_team_epa_per_play", sql)
        self.assertIn("scoring_profile_id = 'ppr'", sql)
        self.assertIn("$.neutral_pass_rate", sql)
        self.assertIn("AVG(metrics.carries) AS rushing_attempts", sql)
        self.assertIn("AVG(metrics.air_yards_share) AS air_yards", sql)

    def test_no_lookahead_dry_run_writes_nothing(self):
        formula_set = self._formula_set()
        candidates = [
            rfb.build_candidate_row(
                rfb.default_formula("QB"),
                formula_name=f"QB {index}",
                candidate_id=f"qb-{index}",
                formula_set_id="set-1",
            )
            for index in range(3)
        ]
        fake = _SequencedFakeClient([[formula_set], candidates, []])

        rfb.run_no_lookahead_backtest(
            client=fake,
            formula_set_id="set-1",
            source_season=2024,
            target_season=2025,
            target_week_start=1,
            target_week_end=18,
            scoring_profile_ids=["ppr"],
            positions=["QB"],
            dry_run=True,
        )

        self.assertFalse(hasattr(fake, "loaded"))

    def test_no_lookahead_write_fails_closed_without_gate(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(PermissionError, rfb.WRITE_GATE):
                rfb.run_no_lookahead_backtest(
                    client=_FakeClient(),
                    formula_set_id="set-1",
                    source_season=2024,
                    target_season=2025,
                    target_week_start=1,
                    target_week_end=18,
                    scoring_profile_ids=["ppr"],
                    positions=["QB"],
                    dry_run=False,
                    write=True,
                )

    def test_save_executed_backtest_writes_only_allowed_backtest_tables(self):
        run_row = rfb.build_backtest_run_row(
            candidate_count=1,
            formula_set_id="set-1",
            formula_version="v1",
            season_start=2024,
            season_end=2025,
            week_start=1,
            week_end=18,
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
            target_name="position_default_top_n",
            dry_run=False,
            status="complete",
            backtest_run_id="run-1",
        )
        result_row = {
            "backtest_run_id": "run-1",
            "candidate_id": "candidate-qb",
            "formula_set_id": "set-1",
            "formula_version": "v1",
            "position": "QB",
            "season": 2025,
            "week": 1,
            "player_id_internal": "00-1",
            "player_name": "QB One",
            "team": "ABC",
            "scoring_profile_id": "ppr",
            "league_type_id": "redraft",
            "roster_format_id": "one_qb",
            "predicted_score": 88.0,
            "predicted_rank_position": 1,
            "actual_points": 30.0,
            "actual_rank_position": 1,
            "target_name": "top_12_position",
            "target_hit": True,
            "win_rate": 1.0,
            "feature_values_json": "{}",
            "result_json": "{}",
            "missing_flags_json": "{\"missing_features\":[]}",
            "source_freshness_json": "{}",
            "created_at": "2026-01-01T00:00:00+00:00",
        }
        summary_row = rfb.build_summary_from_results(
            candidate_row=rfb.build_candidate_row(
                rfb.default_formula("QB"),
                formula_name="QB",
                candidate_id="candidate-qb",
                formula_set_id="set-1",
            ),
            result_rows=[result_row],
            backtest_run_id="run-1",
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
            target_name="top_12_position",
        )
        fake = _FakeClient()

        summary = rfb.save_executed_backtest(
            {
                "backtest_run_rows": [run_row],
                "result_rows": [result_row],
                "candidate_summary_rows": [summary_row],
            },
            project_id="p",
            dataset_id="d",
            client=fake,
        )

        self.assertEqual(summary["target_tables"], [
            "ranking_backtest_runs",
            "ranking_backtest_results",
            "ranking_backtest_candidate_summaries",
        ])
        loaded_tables = [table for _, table in fake.loaded]
        self.assertIn("p.d.ranking_backtest_runs", loaded_tables)
        self.assertIn("p.d.ranking_backtest_results", loaded_tables)
        self.assertIn("p.d.ranking_backtest_candidate_summaries", loaded_tables)
        self.assertNotIn("p.d.ranking_formula_candidates", loaded_tables)
        self.assertNotIn("p.d.ranking_formula_champions", loaded_tables)

    def test_champion_recommendations_are_not_active_champion_rows(self):
        candidates = [
            {"candidate_id": "a", "formula_name": "A", "position": "QB"},
            {"candidate_id": "b", "formula_name": "B", "position": "QB"},
        ]
        summaries = [
            {
                "scoring_profile_id": "ppr",
                "position": "QB",
                "candidate_id": "a",
                "pairwise_win_rate": 0.55,
                "actual_points_captured_rate": 0.95,
                "top_n_hit_rate": 0.50,
                "missing_input_rate": 0.10,
            },
            {
                "scoring_profile_id": "ppr",
                "position": "QB",
                "candidate_id": "b",
                "pairwise_win_rate": 0.60,
                "actual_points_captured_rate": 0.90,
                "top_n_hit_rate": 0.45,
                "missing_input_rate": 0.20,
            },
        ]

        recommendations = rfb.recommend_champions(summaries, candidates)

        self.assertEqual(recommendations[0]["candidate_id"], "b")
        self.assertNotIn("active", recommendations[0])

    def _formula_set(self):
        return {
            "formula_set_id": "set-1",
            "formula_set_name": "Set",
            "formula_set_version": "v1",
            "qb_candidate_id": "qb-balanced",
            "rb_candidate_id": "rb-balanced",
            "wr_candidate_id": "wr-balanced",
            "te_candidate_id": "te-balanced",
            "status": "draft",
            "description": None,
            "created_by": "test",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": None,
            "notes": None,
        }

    def _feature_row(self, player_id, name, actual_points, passing_epa_per_play):
        return {
            "season": 2025,
            "week": 1,
            "player_id_internal": player_id,
            "player_name": name,
            "position": "QB",
            "team": "ABC",
            "actual_points": actual_points,
            "recent_points_avg": actual_points - 2,
            "passing_epa_per_play": passing_epa_per_play,
            "passing_success_rate": 0.52,
            "cpoe": 0.04,
        }


if __name__ == "__main__":
    unittest.main()
