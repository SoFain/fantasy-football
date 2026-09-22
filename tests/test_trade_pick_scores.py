import json
import unittest
from datetime import datetime, timezone

from src import trade_pick_scores as picks


def pick_asset(**overrides):
    row = {
        "source_player_key": "fantasycalc:2026pick101:PICK:UNK",
        "pick_label": "2026 Pick 1.01",
        "display_name": "2026 Pick 1.01",
        "position": "PICK",
        "scoring_profile_id": "ppr",
        "league_type_id": "redraft",
        "roster_format_id": "one_qb",
        "current_market_value": 7084.0,
        "risk_adjusted_trade_value": 6729.8,
        "source_freshness_json": json.dumps({"market_snapshot_date": "2026-06-01"}),
        "missing_data_flags": "[]",
    }
    row.update(overrides)
    return row


class FakeQueryJob:
    def __init__(self, rows):
        self.rows = rows

    def result(self):
        return self.rows


class FakeClient:
    project = "fantasy-football-498121"

    def __init__(self, rows):
        self.rows = rows
        self.query_calls = []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        return FakeQueryJob(self.rows)


class FakeTable:
    schema = []


class FakeWriteClient:
    project = "fantasy-football-498121"

    def __init__(self):
        self.loaded_rows = []
        self.load_table_id = None
        self.query_calls = []
        self.deleted_tables = []

    def get_table(self, table_id):
        self.target_table_id = table_id
        return FakeTable()

    def load_table_from_json(self, rows, table_id, job_config=None):
        self.loaded_rows = list(rows)
        self.load_table_id = table_id
        self.load_job_config = job_config
        return FakeQueryJob([])

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        return FakeQueryJob([])

    def delete_table(self, table_id, not_found_ok=False):
        self.deleted_tables.append((table_id, not_found_ok))


class TradePickScoreTests(unittest.TestCase):
    def test_exact_slot_parser_for_first_pick(self):
        parsed = picks.parse_pick_label("2026 Pick 1.01")

        self.assertTrue(parsed.parsed)
        self.assertEqual(parsed.pick_year, 2026)
        self.assertEqual(parsed.pick_class, "exact_slot")
        self.assertEqual(parsed.pick_round, 1)
        self.assertEqual(parsed.pick_slot, 1)
        self.assertEqual(parsed.estimated_overall_pick, 1)
        self.assertEqual(parsed.pick_bucket, "exact")
        self.assertEqual(parsed.parse_confidence, "high")

    def test_exact_slot_parser_for_later_slot(self):
        parsed = picks.parse_pick_label("2026 Pick 1.12")

        self.assertTrue(parsed.parsed)
        self.assertEqual(parsed.pick_round, 1)
        self.assertEqual(parsed.pick_slot, 12)
        self.assertEqual(parsed.estimated_overall_pick, 12)

    def test_round_only_parser_for_first_round(self):
        parsed = picks.parse_pick_label("2026 1st")

        self.assertTrue(parsed.parsed)
        self.assertEqual(parsed.pick_year, 2026)
        self.assertEqual(parsed.pick_class, "round_only")
        self.assertEqual(parsed.pick_round, 1)
        self.assertIsNone(parsed.pick_slot)
        self.assertIsNone(parsed.estimated_overall_pick)
        self.assertEqual(parsed.pick_bucket, "round_only")
        self.assertEqual(parsed.parse_confidence, "medium")

    def test_round_only_parser_for_second_round(self):
        parsed = picks.parse_pick_label("2027 2nd")

        self.assertTrue(parsed.parsed)
        self.assertEqual(parsed.pick_year, 2027)
        self.assertEqual(parsed.pick_class, "round_only")
        self.assertEqual(parsed.pick_round, 2)

    def test_classifier_avoids_pick_substring_false_positives(self):
        self.assertFalse(picks.is_pick_asset({
            "display_name": "George Pickens",
            "position": "WR",
            "source_player_key": "sleeper:player:george-pickens",
        }))
        self.assertFalse(picks.is_pick_asset({
            "display_name": "Kenny Pickett",
            "position": "QB",
            "source_player_key": "sleeper:player:kenny-pickett",
        }))

    def test_malformed_label_returns_unparsed_flag(self):
        parsed = picks.parse_pick_label("2026 early pick")

        self.assertFalse(parsed.parsed)
        self.assertIn("pick_label_unparsed", parsed.missing_flags)

    def test_component_scores_and_pick_score_are_bounded(self):
        result = picks.build_trade_pick_score_dry_run([
            pick_asset(),
            pick_asset(
                source_player_key="fantasycalc:2026pick112:PICK:UNK",
                pick_label="2026 Pick 1.12",
                display_name="2026 Pick 1.12",
                current_market_value=2203.0,
            ),
            pick_asset(
                source_player_key="fantasycalc:20261st:PICK:UNK",
                pick_label="2026 1st",
                display_name="2026 1st",
                current_market_value=3073.0,
            ),
        ], now=datetime(2026, 6, 27, tzinfo=timezone.utc))

        self.assertEqual(result["parsed_pick_rows"], 3)
        for row in result["rows"]:
            for field in (
                "market_score",
                "slot_capital_score",
                "time_discount_score",
                "liquidity_certainty_score",
                "college_context_score",
                "uncertainty_risk_score",
                "confidence_score",
                "pick_score",
            ):
                self.assertGreaterEqual(row[field], 0)
                self.assertLessEqual(row[field], 100)

    def test_round_only_confidence_below_exact_slot_confidence(self):
        result = picks.build_trade_pick_score_dry_run([
            pick_asset(),
            pick_asset(
                source_player_key="fantasycalc:20261st:PICK:UNK",
                pick_label="2026 1st",
                display_name="2026 1st",
                current_market_value=3073.0,
            ),
        ], now=datetime(2026, 6, 27, tzinfo=timezone.utc))
        by_label = {row["pick_label"]: row for row in result["rows"]}

        self.assertLess(
            by_label["2026 1st"]["confidence_score"],
            by_label["2026 Pick 1.01"]["confidence_score"],
        )
        self.assertIn(
            "pick_round_only_uncertainty",
            json.loads(by_label["2026 1st"]["missing_flags_json"]),
        )

    def test_college_context_defaults_neutral_and_sets_warning(self):
        result = picks.build_trade_pick_score_dry_run([pick_asset()])
        row = result["rows"][0]
        flags = json.loads(row["missing_flags_json"])
        component = json.loads(row["component_json"])

        self.assertEqual(row["college_context_score"], 50.0)
        self.assertIn("college_context_unavailable", flags)
        self.assertEqual(component["college_context"]["status"], "neutral_unavailable")
        self.assertEqual(component["college_context"]["source_tables_used"], [])

    def test_write_mode_requires_pick_specific_gate(self):
        with self.assertRaisesRegex(PermissionError, "ALLOW_TRADE_PICK_SCORE_MATERIALIZATION must be true to write pick scores"):
            picks.build_trade_pick_scores(client=FakeClient([]), dataset_id="fantasy_football_brain", write=True)

    def test_player_score_materialization_gate_does_not_authorize_pick_writes(self):
        self.assertFalse(picks.is_pick_score_write_authorized({
            "ALLOW_TRADE_SCORE_MATERIALIZATION": "true",
        }))
        self.assertTrue(picks.is_pick_score_write_authorized({
            "ALLOW_TRADE_PICK_SCORE_MATERIALIZATION": "true",
        }))

    def test_dry_run_does_not_mutate_bigquery(self):
        client = FakeClient([pick_asset()])

        result = picks.build_trade_pick_scores(
            client=client,
            dataset_id="fantasy_football_brain",
            model_version="trade_pick_score_v0_2026_001",
            dry_run=True,
        )

        self.assertEqual(len(client.query_calls), 1)
        self.assertFalse(result["wrote"])
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["parsed_pick_rows"], 1)

    def test_default_mode_is_no_write_safe(self):
        client = FakeClient([pick_asset()])

        result = picks.build_trade_pick_scores(
            client=client,
            dataset_id="fantasy_football_brain",
            model_version="trade_pick_score_v0_2026_001",
        )

        self.assertEqual(len(client.query_calls), 1)
        self.assertFalse(result["wrote"])
        self.assertTrue(result["dry_run"])

    def test_current_pick_score_query_uses_compat_view_and_source_pick_key_filter(self):
        sql, job_config = picks.build_current_trade_pick_scores_query(
            project_id="fantasy-football-498121",
            dataset_id="fantasy_football_brain",
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
            source_pick_key="fantasycalc:2026pick101:PICK:UNK",
            limit=64,
        )

        self.assertIn("compat_trade_pick_scores_current", sql)
        self.assertIn("source_pick_key = @source_pick_key", sql)
        self.assertNotIn("draft_picks", sql)
        self.assertNotIn("college_player_stats", sql)
        self.assertNotIn("rookie_scouting_metrics", sql)
        self.assertNotIn("trade_player_scores", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["source_pick_key"], "fantasycalc:2026pick101:PICK:UNK")
        self.assertEqual(params["limit"], 64)

    def test_dry_run_row_has_contract_fields_and_json_payloads(self):
        result = picks.build_trade_pick_score_dry_run([pick_asset()])
        row = result["rows"][0]

        self.assertEqual(set(row), set(picks.TRADE_PICK_SCORE_FIELDS))
        self.assertEqual(row["created_by"], "src.trade_pick_scores")
        self.assertIsNotNone(row["created_at"])
        self.assertTrue(row["score_tier"])
        component = json.loads(row["component_json"])
        flags = json.loads(row["missing_flags_json"])
        freshness = json.loads(row["source_freshness_json"])

        self.assertIsInstance(component, dict)
        self.assertIsInstance(flags, list)
        self.assertIsInstance(freshness, dict)
        self.assertIn("college_context_unavailable", flags)

    def test_merge_sql_uses_contract_grain_and_null_safe_pick_slot(self):
        sql = picks.build_trade_pick_scores_merge_sql(
            project_id="fantasy-football-498121",
            dataset_id="fantasy_football_brain",
            staging_table_name="trade_pick_scores_staging_test",
        )

        self.assertIn("MERGE `fantasy-football-498121.fantasy_football_brain.trade_pick_scores` target", sql)
        self.assertIn("USING `fantasy-football-498121.fantasy_football_brain.trade_pick_scores_staging_test` source", sql)
        for field in picks.TRADE_PICK_SCORE_MERGE_KEY_FIELDS:
            if field == "pick_slot":
                self.assertIn("IFNULL(target.pick_slot, -1) = IFNULL(source.pick_slot, -1)", sql)
            else:
                self.assertIn(f"target.{field} = source.{field}", sql)
        self.assertNotIn("trade_player_scores", sql)

    def test_save_path_loads_staging_table_and_merges_only_pick_score_table(self):
        row = picks.build_trade_pick_score_dry_run([pick_asset()])["rows"][0]
        client = FakeWriteClient()

        result = picks.save_trade_pick_scores(
            [row],
            project_id="fantasy-football-498121",
            dataset_id="fantasy_football_brain",
            client=client,
        )

        self.assertEqual(result["written_row_count"], 1)
        self.assertEqual(len(client.loaded_rows), 1)
        self.assertIn("trade_pick_scores_staging_", client.load_table_id)
        self.assertEqual(len(client.query_calls), 1)
        merge_sql = client.query_calls[0][0]
        self.assertIn("MERGE `fantasy-football-498121.fantasy_football_brain.trade_pick_scores` target", merge_sql)
        self.assertIn("IFNULL(target.pick_slot, -1) = IFNULL(source.pick_slot, -1)", merge_sql)
        self.assertNotIn("trade_player_scores", merge_sql)
        self.assertEqual(client.deleted_tables, [(client.load_table_id, True)])

    def test_write_row_validation_rejects_player_rows_and_invalid_scores(self):
        row = picks.build_trade_pick_score_dry_run([pick_asset()])["rows"][0]
        player_row = dict(row, source_pick_key="sleeper:player:123")
        bad_score_row = dict(row, pick_score=101.0)

        with self.assertRaisesRegex(ValueError, "PICK source keys"):
            picks.prepare_trade_pick_score_write_rows([player_row])
        with self.assertRaisesRegex(ValueError, "invalid pick_score"):
            picks.prepare_trade_pick_score_write_rows([bad_score_row])

    def test_round_only_write_row_keeps_pick_slot_null(self):
        row = picks.build_trade_pick_score_dry_run([
            pick_asset(
                source_player_key="fantasycalc:20261st:PICK:UNK",
                pick_label="2026 1st",
                display_name="2026 1st",
                current_market_value=3073.0,
            )
        ])["rows"][0]
        prepared = picks.prepare_trade_pick_score_write_rows([row])[0]

        self.assertEqual(prepared["pick_class"], "round_only")
        self.assertIsNone(prepared["pick_slot"])

    def test_component_json_contains_formula_confidence_and_risk(self):
        result = picks.build_trade_pick_score_dry_run([pick_asset()])
        component = json.loads(result["rows"][0]["component_json"])

        self.assertIn("formula", component)
        self.assertIn("confidence_breakdown", component)
        self.assertIn("risk_breakdown", component)

    def test_expected_warning_flags_are_present(self):
        result = picks.build_trade_pick_score_dry_run([
            pick_asset(
                source_player_key="fantasycalc:20271st:PICK:UNK",
                pick_label="2027 1st",
                display_name="2027 1st",
                current_market_value=2843.0,
            ),
            pick_asset(
                source_player_key="fantasycalc:2026pick101:PICK:UNK",
                pick_label="2026 Pick 1.01",
                display_name="2026 Pick 1.01",
                current_market_value=7084.0,
            ),
        ], now=datetime(2026, 6, 27, tzinfo=timezone.utc))
        by_label = {row["pick_label"]: row for row in result["rows"]}
        flags = json.loads(by_label["2027 1st"]["missing_flags_json"])

        self.assertIn("pick_market_source_only", flags)
        self.assertIn("college_context_unavailable", flags)
        self.assertIn("draft_outcome_prior_insufficient", flags)
        self.assertIn("pick_future_year_discount", flags)
        self.assertIn("pick_score_staging_only", flags)


if __name__ == "__main__":
    unittest.main()
