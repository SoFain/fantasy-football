from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from google.cloud import bigquery

from src import trade_player_scores as scores


RAW_SOURCE_OBJECTS = (
    "weekly_metrics",
    "play_by_play",
    "market_values",
    "ngs_passing",
    "ngs_rushing",
    "ngs_receiving",
    "ftn_charting",
    "weekly_snap_counts",
    "injury_reports",
    "player_rosters",
    "player_contracts",
    "depth_charts",
    "sleeper_viewer_team_snapshots",
    "sleeper_roster_players",
    "sleeper_lineups",
    "sleeper_available_players",
)


class FakeJob:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.errors = None

    def result(self):
        return self.rows


class FakeClient:
    project = "fantasy-football-498121"

    def __init__(self, rows=None):
        self.rows = rows or []
        self.query_calls = []
        self.load_calls = []
        self.delete_calls = []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        if "MERGE" in sql:
            return FakeJob([])
        return FakeJob(self.rows)

    def load_table_from_json(self, rows, table_id, job_config=None):
        self.load_calls.append((rows, table_id, job_config))
        return FakeJob([])

    def delete_table(self, table_id, not_found_ok=False):
        self.delete_calls.append((table_id, not_found_ok))


def player_row(**overrides):
    row = {
        "player_id_internal": "player-1",
        "source_player_key": "src-1",
        "gsis_id": "src-1",
        "player_name": "A.J. Brown",
        "normalized_name": "aj brown",
        "position": "WR",
        "team": "PHI",
        "current_market_value": 8000,
        "projected_3_year_value": 9000,
        "risk_adjusted_trade_value": 7800,
        "asset_position_scarcity_score": 0.5,
        "recent_points_per_game": 18.0,
        "history_snap_share": 0.82,
        "history_target_share": 0.28,
        "history_rush_share": 0.0,
        "high_value_touches": 4.0,
        "yards_per_target": 10.0,
        "yards_per_reception": 14.0,
        "catch_rate": 0.68,
        "history_sample_size": 4,
        "source_fraud_score": 12.0,
        "projection_model_run_id": "model-1",
        "projection_as_of_season": 2025,
        "projection_as_of_week": 6,
        "projection_raw_as_of_season": 2025,
        "projection_raw_as_of_week": 6,
        "projection_team": "PHI",
        "projection_confidence_score": 90.0,
        "projection_risk_score": 8.0,
        "ranking_version": "rank-v1",
        "history_teams": ["PHI"],
        "truth_teams": ["PHI"],
        "truth_current_teams": ["PHI"],
        "fantasy_teams": ["PHI"],
        "fraud_team": "PHI",
        "fraud_current_team": "PHI",
        "asset_source_freshness_json": json.dumps({"assets": "fresh"}),
        "history_source_freshness_json": json.dumps({"history": "fresh"}),
        "fantasy_source_freshness_json": json.dumps({"fantasy": "fresh"}),
        "asset_missing_data_flags": "[]",
        "history_missing_data_flags": "[]",
        "fantasy_missing_data_flags": "[]",
    }
    row.update(overrides)
    return row


def score_output_row(**overrides):
    row = {
        "player_id": "player-1",
        "player_name": "A.J. Brown",
        "position": "WR",
        "team": "PHI",
        "model_run_id": "model-1",
        "trade_score": 50.0,
        "confidence_score": 65.0,
        "missing_flags_json": "[]",
    }
    row.update(overrides)
    return row


class TradePlayerScoreTests(unittest.TestCase):
    def test_formula_uses_documented_weights_and_clamps_confidence(self):
        out = scores.calculate_trade_score(
            market_score=80,
            projection_score=70,
            recent_production_score=60,
            role_usage_score=50,
            positional_scarcity_score=40,
            efficiency_score=30,
            normalized_risk_score=0.5,
            confidence_score=80,
        )

        self.assertAlmostEqual(out["base_score"], 65.5)
        self.assertAlmostEqual(out["risk_adjustment"], -5.0)
        self.assertAlmostEqual(out["confidence_multiplier"], 0.8)
        self.assertAlmostEqual(out["trade_score"], 48.4)
        self.assertEqual(scores.confidence_multiplier(10), 0.70)
        self.assertEqual(scores.confidence_multiplier(150), 1.00)

    def test_v1_formula_does_not_apply_old_confidence_multiplier(self):
        out = scores.calculate_trade_score_v1(
            market_score=80,
            projection_score=70,
            recent_production_score=60,
            role_usage_score=50,
            positional_scarcity_score=40,
            efficiency_score=30,
            source_stability_score=90,
            risk_adjustment=-3,
        )

        self.assertAlmostEqual(out["base_score"], 67.5)
        self.assertAlmostEqual(out["risk_adjustment"], -3.0)
        self.assertEqual(out["confidence_multiplier"], 1.0)
        self.assertAlmostEqual(out["trade_score"], 64.5)

    def test_v1_model_version_routes_to_v1_formula_and_metadata(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    projection_as_of_week=None,
                    projection_raw_as_of_season=None,
                    projection_raw_as_of_week=None,
                )
            ],
            season=2025,
            week=18,
            model_version="trade_score_v1_2025_001",
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]

        component = json.loads(row["component_json"])
        flags = set(json.loads(row["missing_flags_json"]))
        self.assertEqual(component["model_family"], "v1")
        self.assertEqual(component["confidence_multiplier"], 1.0)
        self.assertIn("source_stability_score", component)
        self.assertIn("risk_breakdown", component)
        self.assertIn("projection_freshness_metadata_missing", flags)
        self.assertGreaterEqual(component["source_stability_score"], 0)
        self.assertLessEqual(component["source_stability_score"], 100)

    def test_v1_weighted_confidence_categories_collapse_generic_scoring_flags(self):
        generic_flags = [
            "missing_fumbles_lost",
            "missing_interceptions",
            "missing_passing_2pt_conversions",
            "missing_receiving_2pt_conversions",
            "missing_return_tds",
            "missing_rushing_2pt_conversions",
            "scoring_missing_data_flags_present",
        ]
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    position="WR",
                    asset_missing_data_flags=json.dumps(generic_flags),
                    projection_as_of_week=18,
                )
            ],
            season=2025,
            week=18,
            model_version="trade_score_v1_2025_001",
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]

        component = json.loads(row["component_json"])
        categories = component["confidence_breakdown"]["penalty_categories"]
        generic = [item for item in categories if item["category"] == "generic_scoring_source_warning"]
        self.assertEqual(len(generic), 1)
        self.assertEqual(generic[0]["penalty"], 2.0)
        self.assertGreater(row["confidence_score"], 60)

    def test_v1_position_specific_scoring_penalties_are_position_aware(self):
        qb_row = scores.build_trade_player_score_rows(
            [
                player_row(
                    position="QB",
                    asset_missing_data_flags=json.dumps(["missing_interceptions"]),
                    projection_as_of_week=18,
                )
            ],
            season=2025,
            week=18,
            model_version="trade_score_v1_2025_001",
        )[0]
        wr_row = scores.build_trade_player_score_rows(
            [
                player_row(
                    position="WR",
                    asset_missing_data_flags=json.dumps(["missing_interceptions"]),
                    projection_as_of_week=18,
                )
            ],
            season=2025,
            week=18,
            model_version="trade_score_v1_2025_001",
        )[0]

        qb_categories = json.loads(qb_row["component_json"])["confidence_breakdown"]["penalty_categories"]
        wr_categories = json.loads(wr_row["component_json"])["confidence_breakdown"]["penalty_categories"]
        self.assertTrue(any(item["category"] == "position_specific_scoring_gap" for item in qb_categories))
        self.assertFalse(any(item["category"] == "position_specific_scoring_gap" for item in wr_categories))

    def test_v1_missing_fraud_context_is_warning_not_high_risk(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    source_fraud_score=None,
                    pigskin_fraud_risk_score=None,
                    projection_as_of_week=18,
                )
            ],
            season=2025,
            week=18,
            model_version="trade_score_v1_2025_001",
        )[0]

        component = json.loads(row["component_json"])
        categories = component["confidence_breakdown"]["penalty_categories"]
        fraud_category = [item for item in categories if item["category"] == "missing_fraud_context_warning"]
        self.assertEqual(fraud_category[0]["penalty"], 0.0)
        self.assertIn(
            "missing_fraud_context_treated_as_unknown_not_high_risk",
            component["risk_breakdown"]["missing_source_unknown_risk_notes"],
        )
        self.assertLess(component["risk_breakdown"]["normalized_risk_score"], 0.7)

    def test_v1_team_context_mismatch_warns_when_current_team_changed(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    team="NE",
                    history_teams=["PHI"],
                    fantasy_teams=["PHI"],
                    truth_teams=["PHI"],
                    truth_current_teams=["NE"],
                    projection_team="PHI",
                    fraud_team="PHI",
                    fraud_current_team="NE",
                )
            ],
            season=2025,
            week=18,
            model_version="trade_score_v1_2025_001",
        )[0]

        flags = set(json.loads(row["missing_flags_json"]))
        team_context = json.loads(row["component_json"])["team_context"]
        self.assertIn("team_context_mismatch_warning", flags)
        self.assertTrue(team_context["current_team_matches_asset"])
        self.assertTrue(team_context["has_mismatch"])
        self.assertGreaterEqual(len(team_context["mismatches"]), 1)

    def test_v1_team_context_alias_does_not_warn(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    team="LAR",
                    history_teams=["LA"],
                    fantasy_teams=["LA"],
                    truth_teams=["LA"],
                    truth_current_teams=["LA"],
                    projection_team="LA",
                    fraud_team="LA",
                    fraud_current_team="LA",
                )
            ],
            season=2025,
            week=18,
            model_version="trade_score_v1_2025_001",
        )[0]

        flags = set(json.loads(row["missing_flags_json"]))
        team_context = json.loads(row["component_json"])["team_context"]
        self.assertNotIn("team_context_mismatch_warning", flags)
        self.assertFalse(team_context["has_mismatch"])
        self.assertEqual(team_context["normalized_asset_team"], "LAR")

    def test_v1_role_source_gap_suppressed_by_alternate_context(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    position="WR",
                    history_missing_data_flags=json.dumps(["missing_snaps", "missing_routes_proxy"]),
                    history_snap_share=0.82,
                    history_target_share=0.28,
                    history_sample_size=4,
                )
            ],
            season=2025,
            week=18,
            model_version="trade_score_v1_2025_001",
        )[0]

        categories = json.loads(row["component_json"])["confidence_breakdown"]["penalty_categories"]
        role_gap = [item for item in categories if item["category"] == "role_source_gap"][0]
        self.assertEqual(role_gap["status"], "suppressed_due_to_alternate_context")
        self.assertEqual(role_gap["penalty"], 0.0)
        self.assertIn("target_share", role_gap["alternate_context"])

    def test_v1_role_source_gap_penalizes_missing_role_context(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    position="RB",
                    history_missing_data_flags=json.dumps(["missing_snaps_last_3"]),
                    history_snap_share=None,
                    history_target_share=None,
                    history_rush_share=None,
                    high_value_touches=None,
                    recent_points_per_game=None,
                    history_sample_size=None,
                )
            ],
            season=2025,
            week=18,
            model_version="trade_score_v1_2025_001",
        )[0]

        categories = json.loads(row["component_json"])["confidence_breakdown"]["penalty_categories"]
        role_gap = [item for item in categories if item["category"] == "role_source_gap"][0]
        self.assertEqual(role_gap["status"], "penalty")
        self.assertGreater(role_gap["penalty"], 0.0)
        self.assertEqual(role_gap["alternate_context"], [])

    def test_v1_qb_routes_gap_is_warning_only(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    position="QB",
                    history_missing_data_flags=json.dumps(["missing_routes_proxy"]),
                    history_snap_share=0.99,
                    history_target_share=None,
                    history_rush_share=None,
                    high_value_touches=None,
                    recent_points_per_game=None,
                    history_sample_size=None,
                )
            ],
            season=2025,
            week=18,
            model_version="trade_score_v1_2025_001",
        )[0]

        categories = json.loads(row["component_json"])["confidence_breakdown"]["penalty_categories"]
        role_gap = [item for item in categories if item["category"] == "role_source_gap"][0]
        self.assertEqual(role_gap["status"], "warning_only")
        self.assertEqual(role_gap["penalty"], 0.0)
        self.assertEqual(role_gap["relevant_flags"], [])

    def test_v1_projection_raw_freshness_metadata_missing_is_visible(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    projection_as_of_season=2025,
                    projection_as_of_week=18,
                    projection_raw_as_of_season=None,
                    projection_raw_as_of_week=None,
                )
            ],
            season=2025,
            week=18,
            model_version="trade_score_v1_2025_001",
        )[0]

        flags = set(json.loads(row["missing_flags_json"]))
        freshness = json.loads(row["source_freshness_json"])["sources"]["projection_rankings_current"]
        self.assertIn("projection_freshness_metadata_missing", flags)
        self.assertIsNone(freshness["raw_as_of_season"])
        self.assertIsNone(freshness["raw_as_of_week"])
        self.assertEqual(freshness["effective_as_of_season"], 2025)
        self.assertEqual(freshness["effective_as_of_week"], 18)

    def test_build_rows_outputs_required_json_and_score_bounds(self):
        rows = scores.build_trade_player_score_rows(
            [
                player_row(player_id_internal="player-1", player_name="A.J. Brown", current_market_value=9000),
                player_row(player_id_internal="player-2", player_name="Ja'Marr Chase", current_market_value=9500),
            ],
            season=2025,
            week=6,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        self.assertEqual(len(rows), 2)
        first = rows[0]
        self.assertGreaterEqual(first["trade_score"], 0)
        self.assertLessEqual(first["trade_score"], 100)
        self.assertIn(first["score_tier"], {"elite", "strong", "starter", "flex", "depth", "avoid"})

        component = json.loads(first["component_json"])
        self.assertIn("market_score", component)
        self.assertIn("source_objects", component)
        self.assertEqual(set(component["source_objects"]), set(scores.safe_source_objects()))
        freshness = json.loads(first["source_freshness_json"])
        self.assertIn("sources", freshness)
        flags = json.loads(first["missing_flags_json"])
        self.assertIsInstance(flags, list)

    def test_missing_inputs_are_flagged_and_lower_confidence(self):
        rows = scores.build_trade_player_score_rows(
            [
                {
                    "source_player_key": "unresolved-1",
                    "player_name": "Unknown Player",
                    "position": "WR",
                    "team": "FA",
                }
            ],
            season=2025,
            week=6,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        row = rows[0]
        flags = set(json.loads(row["missing_flags_json"]))
        self.assertIn("missing_player_id_internal", flags)
        self.assertIn("source_player_key_used_as_player_id", flags)
        self.assertIn("missing_market_value", flags)
        self.assertIn("missing_recent_trade_history", flags)
        self.assertLess(row["confidence_score"], 70)
        self.assertEqual(row["player_id"], "unresolved-1")

    def test_positional_scarcity_respects_roster_format(self):
        base = scores.build_trade_player_score_rows(
            [player_row(position="QB", asset_position_scarcity_score=1.0)],
            season=2025,
            week=6,
            roster_format_id="one_qb",
        )[0]
        superflex = scores.build_trade_player_score_rows(
            [player_row(position="QB", asset_position_scarcity_score=1.0)],
            season=2025,
            week=6,
            roster_format_id="superflex",
        )[0]

        self.assertGreater(superflex["positional_scarcity_score"], base["positional_scarcity_score"])

    def test_source_query_uses_only_safe_marts_and_is_parameterized(self):
        sql, job_config = scores.build_trade_player_score_source_query(
            project_id="fantasy-football-498121",
            dataset_id="fantasy_football_brain",
            season=2025,
            week=6,
        )

        for object_name in scores.safe_source_objects():
            self.assertIn(f".{object_name}`", sql)
        for object_name in RAW_SOURCE_OBJECTS:
            self.assertNotIn(f".{object_name}`", sql)
        self.assertIn("@season", sql)
        self.assertIn("@week", sql)
        self.assertIsInstance(job_config, bigquery.QueryJobConfig)

    def test_component_validation_enforces_normalized_risk_zero_to_one(self):
        validation_sql = Path("bigquery/validations/152_trade_player_scores_component_score_range.sql").read_text(
            encoding="utf-8"
        )

        self.assertIn("normalized_risk_score IS NULL", validation_sql)
        self.assertIn("normalized_risk_score < 0", validation_sql)
        self.assertIn("normalized_risk_score > 1", validation_sql)
        self.assertNotIn("normalized_risk_score > 100", validation_sql)
        self.assertIn("market_score > 100", validation_sql)
        self.assertIn("projection_score > 100", validation_sql)
        self.assertIn("fraud_score > 100", validation_sql)

    def test_fraud_context_attaches_and_affects_risk_when_identity_matches(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    player_id_internal="sleeper:9509",
                    source_player_key="00-0038542",
                    gsis_id="00-0038542",
                    source_fraud_score=75.0,
                    fraud_label="thin-role",
                )
            ],
            season=2025,
            week=18,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]

        flags = set(json.loads(row["missing_flags_json"]))
        component = json.loads(row["component_json"])
        self.assertNotIn("missing_fraud_context", flags)
        self.assertEqual(row["fraud_score"], 75.0)
        self.assertGreaterEqual(row["normalized_risk_score"], 0.75)
        self.assertEqual(component["fraud_score"], 75.0)

    def test_missing_fraud_context_remains_without_reliable_match(self):
        row = scores.build_trade_player_score_rows(
            [player_row(source_fraud_score=None, pigskin_fraud_risk_score=None)],
            season=2025,
            week=18,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]

        flags = set(json.loads(row["missing_flags_json"]))
        self.assertIn("missing_fraud_context", flags)
        self.assertEqual(row["fraud_score"], 0.0)

    def test_source_query_matches_fraud_by_stable_source_keys(self):
        sql, _ = scores.build_trade_player_score_source_query(
            project_id="fantasy-football-498121",
            dataset_id="fantasy_football_brain",
            season=2025,
            week=18,
        )

        self.assertIn("fraud_match AS", sql)
        self.assertIn("a.source_player_key = f.player_key", sql)
        self.assertIn("a.gsis_id = f.player_key", sql)
        self.assertIn("a.player_id_internal = f.player_key", sql)

    def test_source_query_matches_projection_by_stable_keys_before_name_fallback(self):
        sql, _ = scores.build_trade_player_score_source_query(
            project_id="fantasy-football-498121",
            dataset_id="fantasy_football_brain",
            season=2025,
            week=18,
        )

        self.assertIn("projection_match AS", sql)
        self.assertIn("projections_player_weekly", sql)
        self.assertIn("projection_join_strategy", sql)
        self.assertIn("a.source_player_key = p.projection_source_player_key", sql)
        self.assertIn("a.gsis_id = p.projection_source_player_key", sql)
        self.assertIn("a.player_id_internal = p.projection_player_id_internal", sql)
        self.assertIn("unique_normalized_name_position_team", sql)

    def test_projection_join_metadata_is_recorded(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    projection_join_key="src-1",
                    projection_join_strategy="source_player_key",
                    projection_model_run_id="projection-model-1",
                )
            ],
            season=2025,
            week=18,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]

        component = json.loads(row["component_json"])
        freshness = json.loads(row["source_freshness_json"])
        self.assertEqual(component["projection_join"]["join_key"], "src-1")
        self.assertEqual(component["projection_join"]["join_strategy"], "source_player_key")
        self.assertEqual(
            freshness["sources"]["projection_rankings_current"]["join_strategy"],
            "source_player_key",
        )

    def test_stable_projection_join_clears_temporary_name_identity_flag(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    asset_missing_data_flags=json.dumps(["temporary_name_join_identity"]),
                    projection_join_key="src-1",
                    projection_join_strategy="source_player_key",
                    projection_model_run_id="projection-model-1",
                )
            ],
            season=2025,
            week=18,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]

        flags = set(json.loads(row["missing_flags_json"]))
        self.assertNotIn("temporary_name_join_identity", flags)
        self.assertNotIn("missing_model_run_id", flags)

    def test_projection_name_fallback_keeps_temporary_identity_flag(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    asset_missing_data_flags=json.dumps(["temporary_name_join_identity"]),
                    projection_join_key="A.J. Brown",
                    projection_join_strategy="unique_normalized_name_position_team",
                    projection_model_run_id="projection-model-1",
                )
            ],
            season=2025,
            week=18,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]

        flags = set(json.loads(row["missing_flags_json"]))
        self.assertIn("temporary_name_join_identity", flags)
        self.assertIn("projection_name_fallback_used", flags)

    def test_missing_model_run_clears_only_when_projection_context_attaches(self):
        missing = scores.build_trade_player_score_rows(
            [player_row(projection_model_run_id=None, asset_model_run_id=None)],
            season=2025,
            week=18,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]
        attached = scores.build_trade_player_score_rows(
            [player_row(projection_model_run_id="projection-model-1", asset_model_run_id=None)],
            season=2025,
            week=18,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]

        self.assertIn("missing_model_run_id", set(json.loads(missing["missing_flags_json"])))
        self.assertNotIn("missing_model_run_id", set(json.loads(attached["missing_flags_json"])))

    def test_stale_projection_context_is_flagged(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    projection_model_run_id="model-week-1",
                    projection_as_of_week=1,
                    projection_created_at="2026-01-01T00:00:00+00:00",
                )
            ],
            season=2025,
            week=18,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]

        flags = set(json.loads(row["missing_flags_json"]))
        freshness = json.loads(row["source_freshness_json"])
        self.assertIn("stale_projection_context", flags)
        self.assertEqual(freshness["sources"]["projection_rankings_current"]["as_of_week"], 1)

    def test_confidence_breakdown_is_recorded_in_component_json(self):
        row = scores.build_trade_player_score_rows(
            [player_row(source_fraud_score=None, pigskin_fraud_risk_score=None)],
            season=2025,
            week=18,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]

        component = json.loads(row["component_json"])
        breakdown = component["confidence_breakdown"]
        self.assertEqual(breakdown["starting_confidence"], 92.0)
        self.assertGreaterEqual(breakdown["missing_flag_count"], 1)
        self.assertGreaterEqual(breakdown["missing_flag_penalty"], 4.0)
        self.assertEqual(breakdown["confidence_score"], row["confidence_score"])

    def test_draft_pick_rows_are_marked_as_pending_pick_lane(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    player_id_internal=None,
                    source_player_key="fantasycalc:2026pick101:PICK:UNK",
                    player_name="2026 Pick 1.01",
                    normalized_name="2026 pick 1.01",
                    position="PICK",
                    team=None,
                    source_fraud_score=None,
                    pigskin_fraud_risk_score=None,
                )
            ],
            season=2025,
            week=18,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]

        flags = set(json.loads(row["missing_flags_json"]))
        self.assertIn("draft_pick_asset", flags)
        self.assertIn("draft_pick_score_lane_pending", flags)
        self.assertEqual(row["player_id"], "fantasycalc:2026pick101:PICK:UNK")
        self.assertIsNone(row["team"])

    def test_materialization_policy_includes_projection_covered_player(self):
        row = scores.build_trade_player_score_rows(
            [
                player_row(
                    projection_model_run_id="projection-model-1",
                    projection_as_of_week=18,
                )
            ],
            season=2025,
            week=18,
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )[0]

        self.assertEqual(scores.materialization_exclusion_reasons(row), [])
        self.assertTrue(scores.is_materializable_trade_score_row(row))

    def test_materialization_policy_excludes_diagnostics(self):
        pick = score_output_row(
            player_id="fantasycalc:2026pick101:PICK:UNK",
            position="PICK",
            missing_flags_json=json.dumps(["draft_pick_asset", "draft_pick_score_lane_pending"]),
        )
        missing_model = score_output_row(model_run_id=None)
        stale = score_output_row(missing_flags_json=json.dumps(["stale_projection_context"]))
        unresolved = score_output_row(player_id="unresolved:abc123", missing_flags_json=json.dumps(["missing_player_id"]))

        self.assertIn("pick_row", scores.materialization_exclusion_reasons(pick))
        self.assertIn("draft_pick_score_lane_pending", scores.materialization_exclusion_reasons(pick))
        self.assertIn("missing_model_run_id", scores.materialization_exclusion_reasons(missing_model))
        self.assertIn("stale_projection_context", scores.materialization_exclusion_reasons(stale))
        self.assertIn("missing_identity", scores.materialization_exclusion_reasons(unresolved))
        self.assertFalse(scores.is_materializable_trade_score_row(pick))
        self.assertFalse(scores.is_materializable_trade_score_row(missing_model))
        self.assertFalse(scores.is_materializable_trade_score_row(stale))
        self.assertFalse(scores.is_materializable_trade_score_row(unresolved))

    def test_materialization_policy_summary_reports_exclusions_and_low_confidence(self):
        rows = [
            score_output_row(player_id="player-1", trade_score=51.0, confidence_score=65.0),
            score_output_row(player_id="player-2", model_run_id=None, trade_score=42.0, confidence_score=62.0),
            score_output_row(
                player_id="fantasycalc:2026pick101:PICK:UNK",
                position="PICK",
                model_run_id=None,
                trade_score=48.0,
                confidence_score=49.0,
                missing_flags_json=json.dumps(["draft_pick_asset", "draft_pick_score_lane_pending"]),
            ),
        ]

        summary = scores.build_materialization_policy_summary(rows)

        self.assertEqual(summary["total_candidate_rows"], 3)
        self.assertEqual(summary["materializable_rows"], 1)
        self.assertEqual(summary["excluded_rows"], 2)
        self.assertEqual(summary["excluded_pick_count"], 1)
        self.assertEqual(summary["excluded_missing_model_run_id"], 2)
        self.assertEqual(summary["excluded_reason_counts"]["draft_pick_score_lane_pending"], 1)
        self.assertEqual(summary["low_confidence_row_count"], 1)
        self.assertEqual(summary["confidence_ge_70_count"], 0)
        self.assertIn("all_materializable_rows_below_confidence_70", summary["warnings"])

    def test_trade_score_model_context_label_exposes_active_model_version(self):
        context = scores.trade_score_model_context([
            score_output_row(
                model_version="trade_score_v1_2025_001",
                model_run_id="projection-model-1",
                season=2025,
                week=18,
                scoring_profile_id="ppr",
                league_type_id="redraft",
                roster_format_id="one_qb",
            )
        ])

        label = scores.trade_score_model_context_label(context)

        self.assertIn("trade_score_v1_2025_001", label)
        self.assertIn("projection-model-1", label)
        self.assertIn("2025", label)
        self.assertIn("one_qb", label)

    def test_trade_score_warning_summary_groups_v1_warning_categories(self):
        rows = scores.trade_score_warning_summary_rows(json.dumps([
            "projection_freshness_metadata_missing",
            "team_context_mismatch_warning",
            "role_usage_fallback_used",
            "missing_fraud_context",
            "missing_player_id",
            "missing_fumbles_lost",
            "draft_pick_score_lane_pending",
        ]))
        grouped = {row["category"]: row["warnings"] for row in rows}

        self.assertIn("projection_freshness_metadata_missing", grouped["Source freshness"])
        self.assertIn("team_context_mismatch_warning", grouped["Team context"])
        self.assertIn("role_usage_fallback_used", grouped["Role/source coverage"])
        self.assertIn("missing_fraud_context", grouped["Risk/Fraud context"])
        self.assertIn("missing_player_id", grouped["Identity/context"])
        self.assertIn("missing_fumbles_lost", grouped["Scoring data"])
        self.assertIn("draft_pick_score_lane_pending", grouped["Draft pick/unavailable score"])

    def test_trade_score_source_freshness_rows_expose_projection_context(self):
        freshness = {
            "sources": {
                "projection_rankings_current": {
                    "model_run_id": "projection-model-1",
                    "created_at": "2026-01-01T00:00:00Z",
                    "effective_as_of_season": 2025,
                    "effective_as_of_week": 18,
                    "raw_as_of_season": None,
                    "raw_as_of_week": None,
                },
                "compat_trade_assets_current": {"market_snapshot_date": "2026-01-01"},
                "compat_trade_player_history": {"history_rows": 500},
                "analytics_player_fantasy_points_by_profile": {"season": 2025, "week": 18},
                "analytics_fraud_watch": {"season": 2025, "week": 18, "label": "watch"},
            }
        }
        row = score_output_row(
            model_version="trade_score_v1_2025_001",
            model_run_id="projection-model-1",
            season=2025,
            week=18,
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
            source_freshness_json=json.dumps(freshness),
        )

        rows = scores.trade_score_source_freshness_rows(row)
        by_key = {(item["source"], item["field"]): item for item in rows}

        self.assertEqual(by_key[("score_model", "model_version")]["value"], "trade_score_v1_2025_001")
        self.assertEqual(by_key[("projection_rankings_current", "model_run_id")]["value"], "projection-model-1")
        self.assertEqual(by_key[("projection_rankings_current", "raw_projection_metadata")]["status"], "warning")
        self.assertEqual(by_key[("analytics_fraud_watch", "label")]["value"], "watch")

    def test_trade_score_unavailable_reason_keeps_draft_picks_out_of_score_lane(self):
        asset = {
            "player_display_name": "2026 Pick 1.01",
            "position": "PICK",
            "source_player_key": "fantasycalc:2026pick101:PICK:UNK",
        }

        self.assertEqual(
            scores.trade_score_unavailable_reason(asset),
            "draft pick score lane pending",
        )
        self.assertEqual(
            scores.trade_score_unavailable_reason({"player_display_name": "Unknown Player"}),
            "no compatible player score row",
        )

    def test_write_excludes_non_materializable_rows_from_materialization(self):
        client = FakeClient(rows=[
            player_row(player_id_internal="player-1", player_name="A.J. Brown", projection_as_of_week=18),
            player_row(player_id_internal="player-2", player_name="No Model", projection_model_run_id=None),
            player_row(
                player_id_internal=None,
                projection_model_run_id=None,
                source_player_key="fantasycalc:2026pick101:PICK:UNK",
                player_name="2026 Pick 1.01",
                normalized_name="2026 pick 1.01",
                position="PICK",
                team=None,
            ),
        ])

        result = scores.build_trade_player_scores(
            season=2025,
            week=18,
            dry_run=False,
            write=True,
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["score_row_count"], 3)
        self.assertEqual(result["materializable_player_row_count"], 1)
        self.assertEqual(result["excluded_pick_count"], 1)
        self.assertEqual(result["excluded_row_count"], 2)
        self.assertEqual(result["materialization_policy"]["excluded_missing_model_run_id"], 2)
        self.assertEqual(result["written_row_count"], 1)
        self.assertEqual(len(client.load_calls[0][0]), 1)
        self.assertNotEqual(client.load_calls[0][0][0]["position"], "PICK")
        self.assertEqual(client.load_calls[0][0][0]["player_id"], "player-1")

    def test_dry_run_fetches_and_scores_without_writing(self):
        client = FakeClient(rows=[player_row()])

        result = scores.build_trade_player_scores(
            season=2025,
            week=6,
            dry_run=True,
            write=False,
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertTrue(result["dry_run"])
        self.assertFalse(result["wrote"])
        self.assertEqual(result["score_row_count"], 1)
        self.assertEqual(len(client.query_calls), 1)
        self.assertEqual(client.load_calls, [])

    def test_write_requires_explicit_non_dry_run_and_uses_merge(self):
        client = FakeClient(rows=[player_row()])

        with self.assertRaises(ValueError):
            scores.build_trade_player_scores(
                season=2025,
                week=6,
                dry_run=True,
                write=True,
                client=client,
                dataset_id="fantasy_football_brain",
            )

        result = scores.build_trade_player_scores(
            season=2025,
            week=6,
            dry_run=False,
            write=True,
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertTrue(result["wrote"])
        self.assertEqual(len(client.load_calls), 1)
        self.assertEqual(client.load_calls[0][2].write_disposition, bigquery.WriteDisposition.WRITE_EMPTY)
        self.assertTrue(any("MERGE" in sql for sql, _ in client.query_calls))
        self.assertTrue(client.delete_calls)

    def test_default_no_write_mode_is_non_mutating(self):
        client = FakeClient(rows=[player_row()])

        result = scores.build_trade_player_scores(
            season=2025,
            week=6,
            dry_run=False,
            write=False,
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertTrue(result["dry_run"])
        self.assertFalse(result["wrote"])
        self.assertEqual(client.load_calls, [])

    def test_module_does_not_import_llm_clients(self):
        source = Path(scores.__file__).read_text(encoding="utf-8").lower()

        self.assertNotIn("openai", source)
        self.assertNotIn("gemini", source)
        self.assertNotIn("vertexai", source)


if __name__ == "__main__":
    unittest.main()
