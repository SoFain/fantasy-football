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

    def test_trend_formula_candidates_validate_without_blocked_metrics(self):
        candidates = rfb.trend_formula_candidates("set-v2")

        self.assertEqual(len(candidates), 12)
        self.assertEqual(
            {position: sum(1 for row in candidates if row["position"] == position) for position in rfb.POSITIONS},
            {"QB": 3, "RB": 3, "WR": 3, "TE": 3},
        )
        for row in candidates:
            formula = rfb.validate_formula(json.loads(row["formula_json"]))
            self.assertEqual(formula["version"], "ranking_formula_v2_trend_2026_001")
            self.assertFalse(set(formula["features"]) & set(rfb.BLOCKED_METRIC_FEATURES))

    def test_three_year_improving_player_scores_above_declining_player(self):
        formula = rfb.validate_formula(
            {
                "version": "ranking_formula_v2_trend_2026_001",
                "position": "WR",
                "score_expression": "weighted_linear",
                "features": ["target_share_slope_3yr", "improving_3yr", "declining_3yr"],
                "weights": {"target_share_slope_3yr": 0.5, "improving_3yr": 0.25, "declining_3yr": 0.25},
                "normalization": {"method": "position_percentile"},
                "source_flags": {"trend_features_available": True},
            }
        )

        improving = rfb.evaluate_formula_for_feature_row(
            formula,
            {"target_share_slope_3yr": 0.04, "improving_3yr": 1.0, "declining_3yr": 0.0},
        )
        declining = rfb.evaluate_formula_for_feature_row(
            formula,
            {"target_share_slope_3yr": -0.04, "improving_3yr": 0.0, "declining_3yr": 1.0},
        )

        self.assertGreater(improving["predicted_score"], declining["predicted_score"])

    def test_missing_trend_history_is_explicit(self):
        formula = rfb.validate_formula(
            {
                "version": "ranking_formula_v2_trend_2026_001",
                "position": "RB",
                "score_expression": "weighted_linear",
                "features": ["opportunity_slope_3yr", "availability_rate_3yr"],
                "weights": {"opportunity_slope_3yr": 0.5, "availability_rate_3yr": 0.5},
                "normalization": {"method": "position_percentile"},
                "source_flags": {"trend_features_available": True},
            }
        )

        result = rfb.evaluate_formula_for_feature_row(formula, {"availability_rate_3yr": 0.8})

        self.assertIn("opportunity_slope_3yr", result["missing_features"])

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

    def test_no_lookahead_backtest_uses_trend_candidates_when_requested(self):
        formula_set = self._formula_set()
        fake = _SequencedFakeClient([[formula_set], [], []])

        result = rfb.run_no_lookahead_backtest(
            client=fake,
            formula_set_id="set-1",
            source_season=2024,
            target_season=2025,
            target_week_start=1,
            target_week_end=18,
            scoring_profile_ids=["ppr"],
            positions=["WR"],
            backtest_version="v2_trend_rolling",
            source_window_years=3,
            candidate_family="trend_v2",
            dry_run=True,
        )

        self.assertEqual(result["candidate_family"], "trend_v2")
        self.assertEqual(result["source_window_years"], 3)
        self.assertEqual(result["candidate_count"], 3)
        self.assertTrue(all(row["candidate_id"].endswith("_v2_trend_2026_001") for row in result["candidate_rows"]))

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

    def test_no_lookahead_feature_query_excludes_target_season_and_uses_source_window(self):
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
            source_window_years=3,
        )

        sql, job_config = fake.queries[0]
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["source_window_start"], 2022)
        self.assertEqual(params["source_season"], 2024)
        self.assertEqual(params["target_season"], 2025)
        self.assertIn("metrics.season BETWEEN @source_window_start AND @source_season", sql)
        self.assertIn("metrics.season < @target_season", sql)
        self.assertIn("points_per_game_slope_3yr", sql)
        self.assertIn("breakout_trajectory_3yr", sql)

    def test_rolling_pairs_require_target_coverage_and_exclude_target_season(self):
        pairs = rfb.build_rolling_season_pairs(
            source_seasons=[2014, 2015, 2016, 2024],
            target_seasons=[2015, 2016, 2025],
            source_window_years=3,
        )

        self.assertEqual(
            pairs,
            [
                {
                    "source_season": 2014,
                    "target_season": 2015,
                    "source_window_start": 2014,
                    "source_window_end": 2014,
                    "source_window_years": 1,
                    "source_seasons": [2014],
                },
                {
                    "source_season": 2015,
                    "target_season": 2016,
                    "source_window_start": 2014,
                    "source_window_end": 2015,
                    "source_window_years": 2,
                    "source_seasons": [2014, 2015],
                },
                {
                    "source_season": 2024,
                    "target_season": 2025,
                    "source_window_start": 2024,
                    "source_window_end": 2024,
                    "source_window_years": 1,
                    "source_seasons": [2024],
                },
            ],
        )
        self.assertTrue(all(pair["target_season"] not in pair["source_seasons"] for pair in pairs))

    def test_high_confidence_and_vor_metrics_are_in_summary_json(self):
        candidate = rfb.build_candidate_row(
            {
                "version": "ranking_formula_v2_trend_2026_001",
                "position": "QB",
                "score_expression": "weighted_linear",
                "features": ["availability_rate_3yr"],
                "weights": {"availability_rate_3yr": 1.0},
                "normalization": {"method": "position_percentile"},
                "source_flags": {"trend_features_available": True},
            },
            formula_name="QB v2",
            candidate_id="qb-v2",
        )
        result_rows = []
        for index in range(14):
            result_rows.append(
                {
                    "season": 2025,
                    "week": 1,
                    "player_id_internal": f"p{index}",
                    "predicted_score": 100 - index,
                    "predicted_rank_position": index + 1,
                    "actual_points": 30 - index,
                    "actual_rank_position": index + 1,
                    "target_hit": index < 12,
                    "missing_flags_json": json.dumps({"missing_features": []}),
                }
            )

        summary = rfb.build_summary_from_results(
            candidate_row=candidate,
            result_rows=result_rows,
            backtest_run_id="run",
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
            target_name="position_default_top_n",
        )
        metric_json = json.loads(summary["metric_json"])

        self.assertIn("high_confidence_pairwise_win_rate", metric_json)
        self.assertIn("value_over_replacement_captured_rate", metric_json)

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

    def test_tournament_family_includes_required_algorithm_ids(self):
        candidates = rfb.tournament_formula_candidates("tournament-set")
        ids = {row["candidate_id"] for row in candidates}

        self.assertIn("ranking_formula_qb_current_pigskin_candidate_score_v1_2026_001", ids)
        self.assertIn("ranking_formula_rb_equal_weight_normalized_blend_v0_2026_001", ids)
        self.assertIn("ranking_formula_wr_value_over_replacement_baseline_v0_2026_001", ids)
        self.assertIn("ranking_formula_te_scarcity_adjusted_draft_value_v0_2026_001", ids)
        self.assertIn("ranking_formula_qb_simple_projection_points_baseline_v0_2026_001", ids)
        self.assertIn("ranking_formula_qb_v1_improved_mapping_2026_001", ids)
        self.assertIn("ranking_formula_wr_trend_breakout_v2_trend_2026_001", ids)
        self.assertTrue(all(row["formula_set_id"] == "tournament-set" for row in candidates))

    def test_current_pigskin_candidate_baseline_uses_no_blocked_metrics(self):
        candidates = rfb.tournament_formula_candidates("tournament-set")
        baseline = next(
            row
            for row in candidates
            if row["candidate_id"] == "ranking_formula_qb_current_pigskin_candidate_score_v1_2026_001"
        )
        formula = rfb.validate_formula(json.loads(baseline["formula_json"]))

        self.assertEqual(formula["version"], "current_pigskin_candidate_score_v1")
        self.assertFalse(set(formula["features"]) & set(rfb.BLOCKED_METRIC_FEATURES))
        self.assertIn("profile_points_score", formula["features"])

    def test_no_lookahead_backtest_uses_tournament_candidates(self):
        formula_set = self._formula_set()
        fake = _SequencedFakeClient([[formula_set], [], []])

        result = rfb.run_no_lookahead_backtest(
            client=fake,
            formula_set_id="set-1",
            source_season=2024,
            target_season=2025,
            target_week_start=1,
            target_week_end=18,
            scoring_profile_ids=["ppr"],
            positions=["QB"],
            backtest_version="ranking_backtest_tournament_v0_rolling_2017_2025",
            source_window_years=3,
            candidate_family="tournament_v0",
            dry_run=True,
        )

        self.assertEqual(result["candidate_family"], "tournament_v0")
        self.assertGreater(result["candidate_count"], 3)
        self.assertTrue(
            any(row["candidate_id"] == "ranking_formula_qb_current_pigskin_candidate_score_v1_2026_001" for row in result["candidate_rows"])
        )
        self.assertEqual(result["candidate_summary_count"], result["candidate_count"])

    def test_tournament_feature_query_exposes_current_baseline_proxy_fields(self):
        fake = _FakeClient(rows=[])

        rfb.load_no_lookahead_feature_rows(
            client=fake,
            position="RB",
            source_season=2024,
            target_season=2025,
            target_week_start=1,
            target_week_end=18,
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
            source_window_years=3,
        )

        sql, _ = fake.queries[0]
        self.assertIn("profile_points_score", sql)
        self.assertIn("opportunity_score_proxy", sql)
        self.assertIn("efficiency_score_proxy", sql)
        self.assertIn("analytical_grade_proxy", sql)
        self.assertIn("role_stability_score", sql)

    def test_scorecard_append_preserves_previous_entries(self):
        existing = "# Scorecard\n\n## Tournament History\n\n- Phase 32.3: previous run\n"
        updated = rfb.append_scorecard_tournament_entry(existing, "- Phase 32.5: tournament run")

        self.assertIn("Phase 32.3: previous run", updated)
        self.assertIn("Phase 32.5: tournament run", updated)
        self.assertEqual(
            updated,
            rfb.append_scorecard_tournament_entry(updated, "- Phase 32.5: tournament run"),
        )

    def test_pick_band_assignment(self):
        self.assertEqual(rfb.assign_pick_band(1), "1-12")
        self.assertEqual(rfb.assign_pick_band(24), "13-24")
        self.assertEqual(rfb.assign_pick_band(36), "25-36")
        self.assertEqual(rfb.assign_pick_band(60), "37-60")
        self.assertEqual(rfb.assign_pick_band(100), "61-100")
        self.assertEqual(rfb.assign_pick_band(101), "101+")
        with self.assertRaisesRegex(ValueError, "positive"):
            rfb.assign_pick_band(0)

    def test_overall_draft_rows_add_cross_position_ranks_and_vor(self):
        draft_rows = rfb.build_overall_draft_value_rows(self._overall_result_rows())
        by_player = {row["player_id_internal"]: row for row in draft_rows}

        self.assertEqual(by_player["wr1"]["predicted_overall_rank"], 1)
        self.assertEqual(by_player["rb1"]["predicted_overall_rank"], 2)
        self.assertEqual(by_player["qb1"]["actual_overall_rank"], 1)
        self.assertEqual(by_player["wr1"]["actual_overall_rank"], 2)
        self.assertEqual(by_player["wr1"]["predicted_pick_band"], "1-12")
        self.assertEqual(by_player["wr1"]["replacement_points"], 12.0)
        self.assertEqual(by_player["wr1"]["actual_vor"], 13.0)
        self.assertEqual(by_player["qb1"]["replacement_points"], 30.0)
        self.assertEqual(by_player["qb1"]["actual_vor"], 0.0)

    def test_overall_draft_value_summary_bounds_and_regret(self):
        summary = rfb.build_overall_draft_value_summary(
            self._overall_result_rows(),
            top_ns=(2, 4),
            pairwise_rank_limit=None,
        )

        self.assertEqual(summary["source_row_count"], 4)
        self.assertEqual(summary["group_count"], 1)
        self.assertGreaterEqual(summary["overall_pairwise_draft_win_rate"], 0.0)
        self.assertLessEqual(summary["overall_pairwise_draft_win_rate"], 1.0)
        self.assertEqual(summary["top_2_overall_hit_rate"], 0.5)
        self.assertEqual(summary["top_4_overall_hit_rate"], 1.0)
        self.assertGreaterEqual(summary["value_over_replacement_captured_rate"], 0.0)
        self.assertIn("1-12", summary["regret_by_pick_band"])

    def test_overall_draft_value_sql_is_read_only_and_uses_neutral_aliases(self):
        sql = rfb.build_overall_draft_value_metrics_sql(project_id="p", dataset_id="d")
        lowered = sql.lower()

        self.assertIn("ranking_backtest_results", sql)
        self.assertIn("source_row_count", sql)
        self.assertNotIn(" as rows", lowered)
        self.assertNotIn("insert ", lowered)
        self.assertNotIn("update ", lowered)
        self.assertNotIn("delete ", lowered)
        self.assertNotIn("ranking_formula_champions", lowered)

    def test_feature_mart_insert_sql_excludes_target_season_predictors(self):
        sql = rfb.build_feature_mart_insert_sql(project_id="p", dataset_id="d")

        self.assertIn("metrics.season BETWEEN @source_window_start_season AND @source_window_end_season", sql)
        self.assertIn("metrics.season < @target_season", sql)
        self.assertNotIn("metrics.season = @target_season", sql)
        self.assertIn("target.season = @target_season", sql)

    def test_feature_mart_delete_sql_is_bounded_not_global_truncate(self):
        sql = rfb.build_feature_mart_delete_sql(project_id="p", dataset_id="d")
        lowered = sql.lower()

        self.assertIn("target_season = @target_season", sql)
        self.assertIn("scoring_profile_id IN UNNEST(@scoring_profile_ids)", sql)
        self.assertIn("position IN UNNEST(@positions)", sql)
        self.assertNotIn("truncate", lowered)
        self.assertNotIn("analytics_pigskin_rankings", lowered)
        self.assertNotIn("ranking_formula_champions", lowered)

    def test_opportunity_metrics_migration_is_additive(self):
        migration = Path("bigquery/migrations/0031__ranking_opportunity_metrics.sql").read_text(encoding="utf-8")
        lowered = migration.lower()

        self.assertIn("CREATE TABLE IF NOT EXISTS", migration)
        self.assertIn("player_week_opportunity_metrics", migration)
        self.assertIn("ADD COLUMN IF NOT EXISTS qb_rushing_leverage_index", migration)
        self.assertIn("ADD COLUMN IF NOT EXISTS rb_high_value_opportunity_score", migration)
        self.assertIn("ADD COLUMN IF NOT EXISTS receiving_role_dominance_score", migration)
        self.assertNotIn("drop ", lowered)
        self.assertNotIn("truncate", lowered)
        self.assertNotIn("delete ", lowered)
        self.assertNotIn("analytics_pigskin_rankings", lowered)

    def test_opportunity_metrics_delete_sql_is_bounded(self):
        sql = rfb.build_opportunity_metrics_delete_sql(project_id="p", dataset_id="d")
        lowered = sql.lower()

        self.assertIn("player_week_opportunity_metrics", sql)
        self.assertIn("season BETWEEN @season_start AND @season_end", sql)
        self.assertNotIn("truncate", lowered)
        self.assertNotIn("analytics_pigskin_rankings", lowered)
        self.assertNotIn("ranking_formula_champions", lowered)

    def test_opportunity_metrics_insert_sql_uses_safe_sources_and_flags_blocked_metrics(self):
        sql = rfb.build_opportunity_metrics_insert_sql(project_id="p", dataset_id="d")
        lowered = sql.lower()

        self.assertIn("player_week_advanced_metrics", sql)
        self.assertIn("stg_team_week_stats", sql)
        self.assertIn("analytics_player_fantasy_points_by_profile", sql)
        self.assertIn("profile_points.scoring_profile_id = 'ppr'", sql)
        self.assertIn("first_read_share_unavailable", sql)
        self.assertIn("yprr_unavailable", sql)
        self.assertIn("blocked metrics remain missing, never fabricated", sql)
        self.assertNotIn("trade_player_scores", lowered)
        self.assertNotIn("analytics_pigskin_rankings", lowered)
        self.assertNotIn(" as rows", lowered)

    def test_feature_mart_grain_fields_are_present(self):
        sql = rfb.build_feature_mart_insert_sql(project_id="p", dataset_id="d")
        for field in (
            "source_window_start_season",
            "source_window_end_season",
            "target_season",
            "target_week",
            "scoring_profile_id",
            "league_type_id",
            "roster_format_id",
            "position",
            "player_id_internal",
        ):
            self.assertIn(field, sql)

    def test_feature_mart_insert_sql_consumes_opportunity_metrics(self):
        sql = rfb.build_feature_mart_insert_sql(project_id="p", dataset_id="d")

        for field in (
            "qb_rushing_leverage_index",
            "rb_high_value_opportunity_score",
            "receiving_role_dominance_score",
            "red_zone_usage_score",
            "goal_line_usage_score",
            "team_environment_score",
            "spike_week_rate_3yr",
            "bust_week_rate_3yr",
            "elite_week_rate_3yr",
            "opportunity_missing_flags",
        ):
            self.assertIn(field, sql)
        self.assertIn("player_week_opportunity_metrics", sql)
        self.assertIn("opportunity_source_freshness_json", sql)

    def test_sql_native_scoring_keeps_missing_features_missing(self):
        sql = rfb.build_sql_native_scoring_prototype_sql(project_id="p", dataset_id="d")

        self.assertIn("WHEN raw_feature_value IS NULL THEN NULL", sql)
        self.assertIn("SUM(IF(scored.feature_score IS NULL, 0, weights.weight))", sql)
        self.assertIn("1.0 - SAFE_DIVIDE", sql)
        self.assertNotIn("COALESCE(raw_feature_value, 0)", sql)

    def test_sql_native_scoring_sql_is_read_only_and_not_champion_path(self):
        sql = rfb.build_sql_native_scoring_prototype_sql(project_id="p", dataset_id="d")
        lowered = sql.lower()

        self.assertIn("ranking_backtest_feature_mart", sql)
        self.assertIn("current_pigskin_candidate_score_v1", sql)
        self.assertIn("simple_projection_points_baseline", sql)
        self.assertIn("v2_trend_balanced", sql)
        self.assertNotIn("insert ", lowered)
        self.assertNotIn("update ", lowered)
        self.assertNotIn("delete ", lowered)
        self.assertNotIn("analytics_pigskin_rankings", lowered)
        self.assertNotIn("ranking_formula_champions", lowered)

    def test_sql_native_current_baseline_matches_python_fixture_formula(self):
        formula = rfb.validate_formula(
            {
                "version": "current_pigskin_candidate_score_v1",
                "position": "TE",
                "features": [
                    "analytical_grade_proxy",
                    "opportunity_score_proxy",
                    "efficiency_score_proxy",
                    "role_stability_score",
                    "profile_points_score",
                ],
                "weights": {
                    "analytical_grade_proxy": 0.55,
                    "opportunity_score_proxy": 0.15,
                    "efficiency_score_proxy": 0.10,
                    "role_stability_score": 0.10,
                    "profile_points_score": 0.10,
                },
                "score_expression": "weighted_linear",
                "normalization": {"method": "position_percentile"},
            }
        )
        feature_row = {
            "analytical_grade_proxy": 80.0,
            "opportunity_score_proxy": 60.0,
            "efficiency_score_proxy": 70.0,
            "role_stability_score": 90.0,
            "profile_points_score": 50.0,
        }

        evaluated = rfb.evaluate_formula_for_feature_row(formula, feature_row)

        self.assertAlmostEqual(evaluated["predicted_score"], 74.0)
        self.assertIn("'analytical_grade_proxy' AS feature_name, 0.55 AS weight", rfb.build_sql_native_scoring_prototype_sql(project_id="p", dataset_id="d"))

    def test_feature_mart_fields_include_overall_draft_value_outputs(self):
        migration = Path("bigquery/migrations/0030__ranking_backtest_feature_mart.sql").read_text(encoding="utf-8")

        self.assertIn("actual_overall_rank INT64", migration)
        self.assertIn("value_over_replacement FLOAT64", migration)
        self.assertIn("top_24_overall BOOL", migration)
        self.assertIn("top_50_overall BOOL", migration)
        self.assertIn("top_100_overall BOOL", migration)
        self.assertIn("actual_pick_band STRING", migration)

    def test_draft_utility_metric_contract_uses_metric_json(self):
        contract = rfb.draft_utility_metric_contract()

        for metric_name in (
            "ndcg_at_k",
            "value_captured_at_k",
            "elite_recall_at_k",
            "tier_accuracy",
            "bust_rate",
            "pick_band_regret",
            "overall_pairwise_draft_win_rate",
            "high_confidence_pairwise_win_rate",
            "value_over_replacement_captured_rate",
        ):
            self.assertIn(metric_name, contract["metrics"])
        self.assertEqual(contract["position_k_values"]["TE"], [3, 6, 12])
        self.assertEqual(contract["overall_k_values"], [24, 50, 100])
        self.assertEqual(contract["persistence"], "ranking_backtest_candidate_summaries.metric_json")

    def test_sql_native_tournament_candidates_are_backtest_only(self):
        candidates = rfb.sql_native_tournament_candidates()
        ids = {row["candidate_id"] for row in candidates}

        self.assertIn("ranking_formula_qb_current_pigskin_candidate_score_v1_2026_001", ids)
        self.assertIn("ranking_formula_te_simple_projection_points_baseline_v0_2026_001", ids)
        self.assertIn("ranking_formula_wr_scarcity_adjusted_draft_value_v0_2026_001", ids)
        self.assertIn("ranking_formula_rb_value_over_replacement_baseline_v0_2026_001", ids)
        self.assertIn("ranking_formula_qb_equal_weight_normalized_blend_v0_2026_001", ids)
        self.assertIn("ranking_formula_wr_v1_improved_mapping_2026_001", ids)
        self.assertIn("ranking_formula_te_trend_balanced_v2_trend_2026_001", ids)
        self.assertTrue(all(row["status"] == "draft" for row in candidates))

    def test_sql_native_tournament_summary_sql_is_read_only_and_bounded(self):
        sql = rfb.build_sql_native_tournament_summary_sql(
            project_id="p",
            dataset_id="d",
            target_seasons=(2024, 2025),
            scoring_profile_ids=("ppr",),
            positions=("TE",),
        )
        lowered = sql.lower()

        self.assertIn("ranking_backtest_feature_mart", sql)
        self.assertIn("target_season IN (2024, 2025)", sql)
        self.assertIn("scoring_profile_id IN ('ppr')", sql)
        self.assertIn("position IN ('TE')", sql)
        self.assertIn("source_window_end_season < target_season", sql)
        self.assertIn("ndcg_at_k", sql)
        self.assertIn("value_captured_at_k", sql)
        self.assertIn("elite_recall_at_k", sql)
        self.assertIn("bust_rate", sql)
        self.assertIn("pick_band_regret", sql)
        self.assertIn("high_confidence_pairwise_win_rate", sql)
        self.assertIn("overall_pairwise_draft_win_rate", sql)
        self.assertIn("predicted_overall_rank <= 100", sql)
        self.assertIn("actual_overall_rank <= 100", sql)
        self.assertNotIn("insert ", lowered)
        self.assertNotIn("update ", lowered)
        self.assertNotIn("delete ", lowered)
        self.assertNotIn("truncate", lowered)
        self.assertNotIn("analytics_pigskin_rankings", lowered)
        self.assertNotIn("ranking_formula_champions", lowered)
        self.assertNotIn(" as rows", lowered)

    def test_sql_native_tournament_supports_opportunity_diagnostic_candidates(self):
        candidates = rfb.opportunity_diagnostic_tournament_candidates()
        sql = rfb.build_sql_native_tournament_summary_sql(
            project_id="p",
            dataset_id="d",
            target_seasons=(2025,),
            scoring_profile_ids=("ppr",),
            candidate_rows=candidates,
        )

        self.assertEqual(len(candidates), 4)
        self.assertIn("qb_rushing_leverage_index", sql)
        self.assertIn("rb_high_value_opportunity_score", sql)
        self.assertIn("receiving_role_dominance_score", sql)
        self.assertIn("team_environment_score", sql)
        self.assertNotIn("insert ", sql.lower())

    def test_sql_native_tournament_missing_features_are_not_zero_filled(self):
        sql = rfb.build_sql_native_tournament_summary_sql(project_id="p", dataset_id="d")

        self.assertIn("WHEN raw_feature_value IS NULL THEN NULL", sql)
        self.assertIn("SUM(IF(feature_score IS NULL, 0, weight))", sql)
        self.assertIn("missing features remain null", sql)
        self.assertNotIn("COALESCE(raw_feature_value, 0)", sql)

    def test_sql_native_formula_rows_match_python_fixture_formula(self):
        sql = rfb.build_sql_native_tournament_summary_sql(
            project_id="p",
            dataset_id="d",
            candidate_rows=[
                rfb.build_candidate_row(
                    {
                        "version": "fixture",
                        "position": "TE",
                        "score_expression": "weighted_linear",
                        "features": ["profile_points_score", "targets"],
                        "weights": {"profile_points_score": 0.75, "targets": 0.25},
                        "normalization": {"method": "position_percentile"},
                    },
                    formula_name="Fixture",
                    candidate_id="fixture-te",
                )
            ],
        )

        self.assertIn("'fixture-te' AS candidate_id", sql)
        self.assertIn("'profile_points_score' AS feature_name", sql)
        self.assertIn("0.75 AS weight", sql)
        self.assertIn("'targets' AS feature_name", sql)
        self.assertIn("0.25 AS weight", sql)

    def test_draft_utility_metrics_are_bigquery_native_expressions(self):
        sql = rfb.build_sql_native_tournament_summary_sql(project_id="p", dataset_id="d")

        self.assertIn("LN(scored.predicted_rank_position + 1) / LN(2)", sql)
        self.assertIn("elite_recall_at_k", sql)
        self.assertIn("tier_accuracy", sql)
        self.assertIn("bust_rate", sql)
        self.assertIn("pick_band_regret", sql)
        self.assertIn("value_over_replacement_captured_rate", sql)

    def test_sql_native_summary_write_gate_fails_closed(self):
        with self.assertRaisesRegex(PermissionError, "ALLOW_RANKING_FORMULA_BACKTEST_WRITE"):
            rfb.write_sql_native_tournament_summaries(
                client=_FakeClient(),
                project_id="p",
                dataset_id="d",
                env={},
            )

    def test_sql_native_summary_write_script_uses_insert_select_not_python_loads(self):
        sql = rfb.build_sql_native_tournament_summary_write_sql(
            project_id="p",
            dataset_id="d",
            target_seasons=(2025,),
            scoring_profile_ids=("ppr",),
            positions=("TE",),
        )
        lowered = sql.lower()

        self.assertIn("CREATE TEMP TABLE sql_native_summary AS", sql)
        self.assertIn("INSERT INTO `p.d.ranking_backtest_runs`", sql)
        self.assertIn("INSERT INTO `p.d.ranking_backtest_candidate_summaries`", sql)
        self.assertIn("FROM sql_native_summary", sql)
        self.assertNotIn("ranking_backtest_results", lowered)
        self.assertNotIn("ranking_formula_champions", lowered)
        self.assertNotIn("analytics_pigskin_rankings", lowered)

    def test_sql_native_summary_write_submits_one_bigquery_script(self):
        fake = _FakeClient()

        rfb.write_sql_native_tournament_summaries(
            client=fake,
            project_id="p",
            dataset_id="d",
            target_seasons=(2025,),
            scoring_profile_ids=("ppr",),
            positions=("TE",),
            env={rfb.WRITE_GATE: "true"},
        )

        self.assertEqual(fake.loaded, [])
        self.assertEqual(len(fake.queries), 1)
        queried_sql = fake.queries[0][0].lower()
        self.assertIn("create temp table sql_native_summary", queried_sql)
        self.assertIn("insert into `p.d.ranking_backtest_candidate_summaries`", queried_sql)
        self.assertNotIn("ranking_backtest_results", queried_sql)
        self.assertNotIn("ranking_formula_champions", queried_sql)

    def test_bqml_training_sql_uses_chronological_split_and_no_random_split(self):
        sql = rfb.build_bqml_create_model_sql(
            project_id="p",
            dataset_id="d",
            spec=rfb.bqml_model_specs(include_boosted_tree=False)[0],
        )

        self.assertIn("data_split_method='NO_SPLIT'", sql)
        self.assertIn("target_season BETWEEN 2017 AND 2023", sql)
        self.assertNotIn("AUTO_SPLIT", sql)
        self.assertNotIn("RANDOM", sql.upper())

    def test_bqml_training_features_exclude_outcome_predictors(self):
        sql = rfb.build_bqml_training_select_sql(
            project_id="p",
            dataset_id="d",
            target_name="value_over_replacement",
        )
        select_list = sql.split("FROM `p.d.ranking_backtest_feature_mart`", 1)[0]

        self.assertIn("value_over_replacement AS label_value", select_list)
        self.assertIn("profile_points_score", select_list)
        self.assertIn("profile_points_score_missing", select_list)
        self.assertNotIn("target_fantasy_points,", select_list)
        self.assertNotIn("actual_position_rank,", select_list)
        self.assertNotIn("actual_overall_rank,", select_list)
        self.assertNotIn("top_24_overall", select_list)
        self.assertNotIn("actual_pick_band", select_list)

    def test_bqml_prediction_output_maps_to_candidate_style_rows(self):
        sql = rfb.build_bqml_prediction_union_sql(
            project_id="p",
            dataset_id="d",
            specs=rfb.bqml_model_specs(include_boosted_tree=False)[:1],
            target_seasons=(2024, 2025),
        )

        for field in (
            "candidate_id",
            "candidate_family",
            "model_name",
            "target_season",
            "scoring_profile_id",
            "position",
            "player_id_internal",
            "predicted_score",
        ):
            self.assertIn(field, sql)
        self.assertIn("ML.PREDICT", sql)
        self.assertIn("target_season BETWEEN 2024 AND 2025", sql)
        self.assertNotIn(",,", sql)

    def test_bqml_prediction_identity_columns_are_not_duplicated(self):
        sql = rfb.build_bqml_prediction_union_sql(
            project_id="p",
            dataset_id="d",
            specs=rfb.bqml_model_specs(include_boosted_tree=False)[:1],
            target_seasons=(2024,),
        )
        input_select = sql.split("FROM `p.d.ranking_backtest_feature_mart`", 1)[0]

        self.assertEqual(input_select.count("    scoring_profile_id,"), 1)
        self.assertEqual(input_select.count("    position,"), 1)

    def test_bqml_logistic_probability_uses_bigquery_prob_field(self):
        logistic_spec = [spec for spec in rfb.bqml_model_specs(include_boosted_tree=False) if spec["model_type"] == "LOGISTIC_REG"][0]
        sql = rfb.build_bqml_prediction_union_sql(
            project_id="p",
            dataset_id="d",
            specs=[logistic_spec],
            target_seasons=(2024,),
        )

        self.assertIn("SELECT prob FROM UNNEST(predicted_elite_label_probs)", sql)
        self.assertNotIn("SELECT probability FROM UNNEST(predicted_elite_label_probs)", sql)

    def test_bqml_summary_sql_is_sql_native_and_does_not_touch_live_tables(self):
        sql = rfb.build_bqml_prediction_summary_sql(
            project_id="p",
            dataset_id="d",
            specs=rfb.bqml_model_specs(include_boosted_tree=False)[:1],
        )
        lowered = sql.lower()

        self.assertIn("ML.PREDICT", sql)
        self.assertIn("ndcg_at_k", sql)
        self.assertIn("overall_pairwise_draft_win_rate", sql)
        self.assertNotIn("insert ", lowered)
        self.assertNotIn("delete ", lowered)
        self.assertNotIn("ranking_formula_champions", lowered)
        self.assertNotIn("analytics_pigskin_rankings", lowered)
        self.assertNotIn("ranking_backtest_results", lowered)
        self.assertIn("LEFT JOIN pairwise USING (candidate_id, target_season, position, scoring_profile_id, league_type_id, roster_format_id)", sql)
        self.assertIn("LEFT JOIN overall_pairwise USING (candidate_id, target_season, scoring_profile_id, league_type_id, roster_format_id)", sql)

    def test_bqml_model_specs_are_bounded_and_skip_random_forest_by_default(self):
        specs = rfb.bqml_model_specs()
        model_names = {spec["model_name"] for spec in specs}

        self.assertIn("ranking_bqml_linear_vor_v0", model_names)
        self.assertIn("ranking_bqml_linear_points_v0", model_names)
        self.assertIn("ranking_bqml_logistic_elite_v0", model_names)
        self.assertIn("ranking_bqml_boosted_tree_vor_v0", model_names)
        self.assertNotIn("ranking_bqml_random_forest_vor_v0", model_names)

    def test_ensemble_specs_are_convex_and_keep_bqml_bounded(self):
        specs = rfb.ensemble_candidate_specs()
        rfb.validate_ensemble_specs(specs)

        for spec in specs:
            weight_groups = []
            if "weights" in spec:
                weight_groups.append(spec["weights"])
            weight_groups.extend(dict(spec.get("position_weights", {})).values())
            for weights in weight_groups:
                self.assertAlmostEqual(sum(weights.values()), 1.0)
                for component_id, weight in weights.items():
                    self.assertGreaterEqual(weight, 0.0)
                    if component_id.startswith("bqml_"):
                        self.assertLessEqual(weight, 0.50)

    def test_ensemble_specs_do_not_tune_on_holdout(self):
        for spec in rfb.ensemble_candidate_specs():
            self.assertEqual(spec["holdout_season"], 2025)
            self.assertLess(spec["tuned_on_season"], spec["holdout_season"])

    def test_ensemble_validation_rejects_invalid_weights(self):
        bad_specs = [
            {
                "ensemble_id": "bad",
                "ensemble_family": "bad",
                "tuned_on_season": 2024,
                "holdout_season": 2025,
                "weights": {"current_pigskin": 0.25, "bqml_logistic_elite": 0.80},
            }
        ]

        with self.assertRaises(rfb.FormulaValidationError):
            rfb.validate_ensemble_specs(bad_specs)

    def test_ensemble_summary_sql_is_sql_native_and_safe(self):
        sql = rfb.build_ensemble_prediction_summary_sql(project_id="p", dataset_id="d")
        lowered = sql.lower()

        self.assertIn("ML.PREDICT", sql)
        self.assertIn("normalized_score", sql)
        self.assertIn("2025 holdout not used for weight tuning", sql)
        self.assertIn("ranking_backtest_feature_mart", sql)
        self.assertNotIn("insert ", lowered)
        self.assertNotIn("ranking_backtest_results", lowered)
        self.assertNotIn("ranking_formula_champions", lowered)
        self.assertNotIn("analytics_pigskin_rankings", lowered)

    def test_ensemble_summary_write_is_summary_only_and_gated(self):
        fake = _FakeClient()

        with self.assertRaisesRegex(PermissionError, rfb.WRITE_GATE):
            rfb.write_ensemble_prediction_summaries(client=fake, project_id="p", dataset_id="d", env={})

        rfb.write_ensemble_prediction_summaries(
            client=fake,
            project_id="p",
            dataset_id="d",
            env={rfb.WRITE_GATE: "true"},
        )

        queried_sql = fake.queries[0][0].lower()
        self.assertIn("insert into `p.d.ranking_backtest_runs`", queried_sql)
        self.assertIn("insert into `p.d.ranking_backtest_candidate_summaries`", queried_sql)
        self.assertNotIn("ranking_backtest_results", queried_sql)
        self.assertNotIn("ranking_formula_champions", queried_sql)
        self.assertNotIn("analytics_pigskin_rankings", queried_sql)

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

    def _overall_result_rows(self):
        base = {
            "backtest_run_id": "run-1",
            "candidate_id": "candidate-1",
            "formula_set_id": "set-1",
            "formula_version": "v1",
            "season": 2025,
            "week": 1,
            "scoring_profile_id": "ppr",
            "league_type_id": "redraft",
            "roster_format_id": "one_qb",
            "target_name": "position_default_top_n",
        }
        return [
            {**base, "player_id_internal": "wr1", "player_name": "WR One", "position": "WR", "team": "A", "predicted_score": 96.0, "actual_points": 25.0},
            {**base, "player_id_internal": "rb1", "player_name": "RB One", "position": "RB", "team": "B", "predicted_score": 94.0, "actual_points": 10.0},
            {**base, "player_id_internal": "qb1", "player_name": "QB One", "position": "QB", "team": "C", "predicted_score": 90.0, "actual_points": 30.0},
            {**base, "player_id_internal": "wr2", "player_name": "WR Two", "position": "WR", "team": "D", "predicted_score": 80.0, "actual_points": 12.0},
        ]


if __name__ == "__main__":
    unittest.main()
