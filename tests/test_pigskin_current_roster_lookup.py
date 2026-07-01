from __future__ import annotations

from pathlib import Path
import unittest

from src import pigskin_current_roster_lookup as lookup


class FakeJob:
    def __init__(self, result_rows):
        self._result_rows = result_rows

    def result(self):
        return self._result_rows


class FakeClient:
    project = "fantasy-football-498121"

    def __init__(self, result_rows=None):
        self.result_rows = result_rows or []
        self.calls = []

    def query(self, sql, job_config=None):
        self.calls.append((sql, job_config))
        return FakeJob(self.result_rows)


def candidate_row(**overrides):
    row = {
        "source_name": "sleeper_players_current",
        "source_priority": 30,
        "source_role": "global_current",
        "player_id_internal": "00-0032764",
        "gsis_id": "00-0032764",
        "sleeper_player_id": "1166",
        "full_name": "Tyreek Hill",
        "display_name": "Tyreek Hill",
        "normalized_name": "tyreek hill",
        "position": "WR",
        "current_team": "MIA",
        "current_roster_status": "active",
        "league_id": None,
        "roster_id": None,
        "source_freshness_json": '{"snapshot_at":"2026-06-30T00:00:00Z"}',
        "missing_data_flags": '{"flags":[]}',
        "current_roster_as_of": "2026-06-30T00:00:00Z",
        "fantasy_availability": None,
        "free_agent": False,
    }
    row.update(overrides)
    return row


def params_by_name(job_config):
    return {param.name: param for param in job_config.query_parameters}


class PigskinCurrentRosterLookupTests(unittest.TestCase):
    def test_rejects_empty_unbounded_lookup(self):
        result = lookup.lookup_current_roster_context()

        self.assertEqual(result["status"], "validation_error")
        self.assertIn("bounded identity", result["error"])

    def test_rejects_arbitrary_sql_keys(self):
        result = lookup.lookup_current_roster_context(sql_query="SELECT * FROM weekly_metrics")

        self.assertEqual(result["status"], "validation_error")
        self.assertEqual(result["blocked_reason"], "arbitrary_sql_not_allowed")
        self.assertIn("sql_query", result["unsafe_args"])

    def test_name_lookup_requires_explicit_limit(self):
        result = lookup.lookup_current_roster_context(player_name="Tyreek Hill")

        self.assertEqual(result["status"], "validation_error")
        self.assertIn("limit is required", result["error"])

    def test_query_uses_parameterized_approved_sources_only(self):
        sql, job_config = lookup.build_current_roster_lookup_query(
            project_id="fantasy-football-498121",
            dataset_id="fantasy_football_brain",
            player_name="Tyreek Hill",
            league_id="123",
            include_available_players=True,
            limit=10,
        )
        rendered = sql.lower()

        for source in lookup.APPROVED_SOURCES:
            self.assertIn(source, rendered)
        self.assertIn("@normalized_name", rendered)
        self.assertIn("@league_id", rendered)
        self.assertIn("@include_available_players", rendered)
        self.assertNotIn("raw_nflverse_", rendered)
        self.assertNotIn("weekly_metrics", rendered)
        self.assertNotIn("compat_pigskin_player_context_current", rendered)
        params = params_by_name(job_config)
        self.assertEqual(params["normalized_name"].value, "tyreek hill")
        self.assertEqual(params["limit"].value, 10)
        self.assertEqual(job_config.maximum_bytes_billed, lookup.DEFAULT_MAX_BYTES_BILLED)

    def test_stable_player_id_lookup_returns_deterministic_payload(self):
        client = FakeClient([candidate_row()])

        result = lookup.lookup_current_roster_context(
            player_id_internal="00-0032764",
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["current_team"], "MIA")
        self.assertEqual(result["current_roster_context"]["current_roster_source"], "sleeper_players_current")
        self.assertEqual(result["player_id_internal"], "00-0032764")
        self.assertEqual(len(client.calls), 1)

    def test_sleeper_player_id_lookup_is_parameterized(self):
        client = FakeClient([candidate_row()])

        lookup.lookup_current_roster_context(
            sleeper_player_id="1166",
            client=client,
            dataset_id="fantasy_football_brain",
        )
        _, job_config = client.calls[0]
        params = params_by_name(job_config)

        self.assertEqual(params["sleeper_player_id"].value, "1166")

    def test_gsis_id_lookup_is_parameterized(self):
        client = FakeClient([candidate_row()])

        lookup.lookup_current_roster_context(
            gsis_id="00-0032764",
            client=client,
            dataset_id="fantasy_football_brain",
        )
        _, job_config = client.calls[0]
        params = params_by_name(job_config)

        self.assertEqual(params["gsis_id"].value, "00-0032764")

    def test_name_lookup_with_multiple_identities_returns_ambiguity(self):
        client = FakeClient([
            candidate_row(player_id_internal="00-0032764", display_name="Tyreek Hill"),
            candidate_row(
                player_id_internal="00-0027854",
                sleeper_player_id="9999",
                gsis_id="00-0027854",
                display_name="Taysom Hill",
                position="TE",
                current_team="NO",
            ),
        ])

        result = lookup.lookup_current_roster_context(
            player_name="T.Hill",
            limit=10,
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["status"], "ambiguous")
        self.assertTrue(result["needs_identity_confirmation"])
        self.assertEqual(result["candidate_count"], 2)

    def test_team_and_position_are_parameters_for_narrowing(self):
        client = FakeClient([candidate_row()])

        lookup.lookup_current_roster_context(
            player_name="Tyreek Hill",
            team="MIA",
            position="WR",
            limit=5,
            client=client,
            dataset_id="fantasy_football_brain",
        )
        _, job_config = client.calls[0]
        params = params_by_name(job_config)

        self.assertEqual(params["team"].value, "MIA")
        self.assertEqual(params["position"].value, "WR")

    def test_available_source_sets_free_agent_status(self):
        client = FakeClient([
            candidate_row(source_name="player_identity_bridge", source_priority=10, source_role="identity"),
            candidate_row(
                source_name="sleeper_available_players",
                source_priority=50,
                source_role="league_available",
                current_roster_status="available",
                fantasy_availability="available",
                free_agent=True,
                league_id="123",
                current_team=None,
            ),
        ])

        result = lookup.lookup_current_roster_context(
            sleeper_player_id="1166",
            league_id="123",
            include_available_players=True,
            client=client,
            dataset_id="fantasy_football_brain",
        )
        context = result["current_roster_context"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(context["current_roster_status"], "available")
        self.assertTrue(context["free_agent"])
        self.assertEqual(context["availability_context"]["source"], "sleeper_available_players")

    def test_missing_current_team_returns_unknown_not_historical_team(self):
        client = FakeClient([
            candidate_row(current_team=None, current_roster_status=None),
        ])

        result = lookup.lookup_current_roster_context(
            sleeper_player_id="1166",
            client=client,
            dataset_id="fantasy_football_brain",
        )
        context = result["current_roster_context"]

        self.assertIsNone(context["current_team"])
        self.assertEqual(context["current_roster_status"], "unknown")
        self.assertIn("Current team is unknown", " ".join(result["warnings"]))

    def test_tyreek_lookup_does_not_infer_miami_from_historical_packet(self):
        client = FakeClient([
            candidate_row(current_team=None, current_roster_status="available", free_agent=True),
        ])

        result = lookup.lookup_current_roster_context(
            player_name="Tyreek Hill",
            team=None,
            limit=5,
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["status"], "ok")
        self.assertIsNone(result["current_team"])
        self.assertNotIn("historical_team", result["current_roster_context"])

    def test_lookup_payload_works_with_merge_layer(self):
        client = FakeClient([candidate_row(current_team=None, current_roster_status="available", free_agent=True)])
        historical = {
            "status": "ok",
            "packet": {
                "display_name": "T.Hill",
                "player_id_internal": "00-0032764",
                "historical_team": "MIA",
                "as_of_season": 2025,
                "as_of_week": 18,
            },
        }

        result = lookup.merge_historical_packet_with_current_lookup(
            historical,
            player_id_internal="00-0032764",
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["historical_team"], "MIA")
        self.assertIsNone(result["current_team"])
        self.assertEqual(result["current_roster_status"], "available")
        self.assertEqual(result["current_roster_lookup"]["status"], "ok")

    def test_source_metadata_is_preserved(self):
        client = FakeClient([candidate_row()])

        result = lookup.lookup_current_roster_context(
            sleeper_player_id="1166",
            client=client,
            dataset_id="fantasy_football_brain",
        )
        context = result["current_roster_context"]

        self.assertEqual(context["current_roster_as_of"], "2026-06-30T00:00:00Z")
        self.assertIn("source_freshness_json", context)
        self.assertTrue(context["provenance"])

    def test_multiple_current_candidates_require_confirmation(self):
        client = FakeClient([
            candidate_row(player_id_internal="id_1", sleeper_player_id="1166", display_name="Tyreek Hill"),
            candidate_row(player_id_internal="id_2", sleeper_player_id="2222", display_name="Tyreek Hill"),
        ])

        result = lookup.lookup_current_roster_context(
            player_name="Tyreek Hill",
            limit=10,
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["status"], "ambiguous")
        self.assertTrue(result["needs_identity_confirmation"])

    def test_source_precedence_is_deterministic_and_documents_availability(self):
        client = FakeClient([
            candidate_row(source_name="player_identity_bridge", source_priority=10, source_role="identity"),
            candidate_row(source_name="sleeper_players_current", source_priority=30, source_role="global_current"),
            candidate_row(
                source_name="sleeper_roster_players",
                source_priority=40,
                source_role="league_rostered",
                fantasy_availability="rostered",
                league_id="123",
                roster_id=4,
            ),
        ])

        result = lookup.lookup_current_roster_context(
            sleeper_player_id="1166",
            league_id="123",
            client=client,
            dataset_id="fantasy_football_brain",
        )
        context = result["current_roster_context"]

        self.assertEqual(context["current_roster_source"], "sleeper_roster_players")
        self.assertEqual(context["current_team"], "MIA")
        self.assertEqual(context["availability_context"]["fantasy_availability"], "rostered")
        self.assertIn("player_identity_bridge", context["identity_sources"])

    def test_default_and_dry_safe_mode_never_writes(self):
        client = FakeClient([candidate_row()])

        lookup.lookup_current_roster_context(
            player_id_internal="00-0032764",
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(len(client.calls), 1)
        self.assertFalse(hasattr(client, "insert_rows_json"))
        self.assertFalse(hasattr(client, "load_table_from_json"))

    def test_module_does_not_call_sleeper_pigskin_llm_or_write_paths(self):
        source = Path("src/pigskin_current_roster_lookup.py").read_text(encoding="utf-8").lower()

        self.assertNotIn("requests.", source)
        self.assertNotIn("ingest_sleeper", source)
        self.assertNotIn("execute_pigskin_context_tool", source)
        self.assertNotIn("google.generativeai", source)
        self.assertNotIn("insert_rows", source)
        self.assertNotIn("load_table", source)


if __name__ == "__main__":
    unittest.main()
