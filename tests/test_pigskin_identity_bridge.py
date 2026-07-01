from __future__ import annotations

from pathlib import Path
import unittest

from src import pigskin_identity_bridge as bridge


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


def identity_row(**overrides):
    row = {
        "source_name": "player_identity_bridge",
        "source_priority": 10,
        "source_role": "identity",
        "player_id_internal": "00-0032764",
        "gsis_id": "00-0032764",
        "sleeper_player_id": "1166",
        "full_name": "Tyreek Hill",
        "display_name": "Tyreek Hill",
        "normalized_name": "tyreek hill",
        "normalized_for_match": "tyreek hill",
        "compact_display_name": "t.hill",
        "position": "WR",
        "current_team": "MIA",
        "current_roster_status": "active",
        "league_id": None,
        "roster_id": None,
        "source_freshness_json": '{"identity":"fresh"}',
        "missing_data_flags": '{"flags":[]}',
        "source_as_of": "2026-06-30T00:00:00Z",
        "fantasy_availability": None,
        "free_agent": False,
    }
    row.update(overrides)
    return row


def params_by_name(job_config):
    return {param.name: param for param in job_config.query_parameters}


class PigskinIdentityBridgeTests(unittest.TestCase):
    def test_rejects_empty_unbounded_lookup(self):
        result = bridge.resolve_player_identity()

        self.assertEqual(result["status"], "validation_error")
        self.assertIn("stable ID or name", result["error"])

    def test_team_and_position_alone_are_not_identity(self):
        result = bridge.resolve_player_identity(team="MIA", position="WR")

        self.assertEqual(result["status"], "validation_error")
        self.assertIn("not identity fields", result["error"])

    def test_rejects_arbitrary_sql_keys(self):
        result = bridge.resolve_player_identity(sql_query="SELECT * FROM weekly_metrics")

        self.assertEqual(result["status"], "validation_error")
        self.assertEqual(result["blocked_reason"], "arbitrary_sql_not_allowed")
        self.assertIn("sql_query", result["unsafe_args"])

    def test_name_lookup_requires_explicit_limit(self):
        result = bridge.resolve_player_identity(player_name="Tyreek Hill")

        self.assertEqual(result["status"], "validation_error")
        self.assertIn("limit is required", result["error"])

    def test_query_uses_parameterized_approved_sources_only(self):
        sql, job_config = bridge.build_identity_bridge_query(
            project_id="fantasy-football-498121",
            dataset_id="fantasy_football_brain",
            player_name="Tyreek Hill",
            compact_name="T.Hill",
            team="MIA",
            position="WR",
            limit=10,
        )
        rendered = sql.lower()

        for source in bridge.APPROVED_SOURCES:
            self.assertIn(source, rendered)
        for source in bridge.FORBIDDEN_SOURCES:
            self.assertNotIn(source, rendered)
        self.assertIn("@normalized_names", rendered)
        self.assertIn("@compact_names", rendered)
        self.assertIn("@team", rendered)
        self.assertIn("@position", rendered)
        params = params_by_name(job_config)
        self.assertEqual(params["limit"].value, 10)
        self.assertEqual(params["team"].value, "MIA")
        self.assertEqual(params["position"].value, "WR")
        self.assertIn("tyreek hill", params["normalized_names"].values)
        self.assertIn("t.hill", params["compact_names"].values)
        self.assertEqual(job_config.maximum_bytes_billed, bridge.DEFAULT_MAX_BYTES_BILLED)

    def test_stable_player_id_lookup_is_deterministic_when_sources_agree(self):
        client = FakeClient([
            identity_row(),
            identity_row(source_name="dim_players_current", source_priority=20),
            identity_row(source_name="sleeper_players_current", source_priority=30, source_role="global_current"),
        ])

        result = bridge.resolve_player_identity(
            player_id_internal="00-0032764",
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["stable_ids"]["player_id_internal"], "00-0032764")
        self.assertIn("player_identity_bridge", result["identity_sources"])
        self.assertEqual(result["current_team"], "MIA")

    def test_sleeper_player_id_lookup_is_parameterized(self):
        client = FakeClient([identity_row()])

        bridge.resolve_player_identity(
            sleeper_player_id="1166",
            client=client,
            dataset_id="fantasy_football_brain",
        )
        _, job_config = client.calls[0]

        self.assertEqual(params_by_name(job_config)["sleeper_player_id"].value, "1166")

    def test_gsis_id_lookup_is_parameterized(self):
        client = FakeClient([identity_row()])

        bridge.resolve_player_identity(
            gsis_id="00-0032764",
            client=client,
            dataset_id="fantasy_football_brain",
        )
        _, job_config = client.calls[0]

        self.assertEqual(params_by_name(job_config)["gsis_id"].value, "00-0032764")

    def test_full_name_lookup_returns_candidates_when_multiple_identities_match(self):
        client = FakeClient([
            identity_row(display_name="Mike Williams", full_name="Mike Williams", player_id_internal="pid_1", sleeper_player_id="1", gsis_id="g1"),
            identity_row(display_name="Mike Williams", full_name="Mike Williams", player_id_internal="pid_2", sleeper_player_id="2", gsis_id="g2"),
        ])

        result = bridge.resolve_player_identity(
            full_name="Mike Williams",
            limit=10,
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(result["candidate_count"], 2)
        self.assertIsNone(result["selected_identity"])

    def test_compact_name_lookup_returns_candidates_for_t_hill_collision(self):
        client = FakeClient([
            identity_row(display_name="Tyreek Hill", player_id_internal="00-0032764", sleeper_player_id="1166", gsis_id="00-0032764"),
            identity_row(display_name="Taysom Hill", full_name="Taysom Hill", player_id_internal="00-0027854", sleeper_player_id="234", gsis_id="00-0027854", position="TE", current_team="NO"),
        ])

        result = bridge.resolve_player_identity(
            compact_name="T.Hill",
            limit=10,
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["status"], "ambiguous")
        self.assertTrue(result["needs_identity_confirmation"])
        self.assertEqual(result["candidate_count"], 2)

    def test_compact_collisions_do_not_silently_select(self):
        for compact_name in ("A.Brown", "J.Jefferson", "D.Johnson", "J.Williams"):
            with self.subTest(compact_name=compact_name):
                client = FakeClient([
                    identity_row(display_name=compact_name, player_id_internal=f"{compact_name}-1", sleeper_player_id=f"{compact_name}-s1", gsis_id=f"{compact_name}-g1"),
                    identity_row(display_name=compact_name, player_id_internal=f"{compact_name}-2", sleeper_player_id=f"{compact_name}-s2", gsis_id=f"{compact_name}-g2"),
                ])

                result = bridge.resolve_player_identity(
                    compact_name=compact_name,
                    limit=10,
                    client=client,
                    dataset_id="fantasy_football_brain",
                )

                self.assertEqual(result["status"], "ambiguous")
                self.assertIsNone(result["selected_identity"])

    def test_stable_id_conflicts_return_needs_identity_confirmation(self):
        client = FakeClient([
            identity_row(player_id_internal="00-0033040", sleeper_player_id="1166"),
            identity_row(player_id_internal="00-0029604", sleeper_player_id="1166"),
        ])

        result = bridge.resolve_player_identity(
            sleeper_player_id="1166",
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["status"], "needs_identity_confirmation")
        self.assertTrue(result["needs_identity_confirmation"])
        self.assertIn("player_id_internal", str(result["mismatch_diagnostics"]))

    def test_tyreek_packet_id_versus_current_id_returns_confirmation_needed(self):
        packet = {
            "display_name": "T.Hill",
            "player_id_internal": "00-0033040",
            "historical_team": "MIA",
        }
        current = {
            "display_name": "Tyreek Hill",
            "player_id_internal": "00-0029604",
            "sleeper_player_id": "1166",
            "current_team": "LV",
            "current_roster_source": "sleeper_players_current",
        }

        result = bridge.reconcile_packet_and_current_identity(packet, current)

        self.assertEqual(result["status"], "needs_identity_confirmation")
        self.assertEqual(result["historical_team"], "MIA")
        self.assertEqual(result["current_team"], "LV")
        self.assertEqual(result["mismatch_diagnostics"][0]["field"], "player_id_internal")

    def test_historical_team_is_not_current_roster_status(self):
        packet = {"display_name": "T.Hill", "player_id_internal": "00-0033040", "historical_team": "MIA"}

        result = bridge.reconcile_packet_and_current_identity(packet, {"unavailable": True})

        self.assertEqual(result["status"], "current_roster_source_gap")
        self.assertIsNone(result["current_team"])
        self.assertIn("not inferred", " ".join(result["warnings"]))

    def test_mahomes_unavailable_current_source_is_source_gap(self):
        packet = {
            "display_name": "P.Mahomes",
            "player_id_internal": "00-0033873",
            "historical_team": "KC",
        }

        result = bridge.reconcile_packet_and_current_identity(packet, None)

        self.assertEqual(result["status"], "current_roster_source_gap")
        self.assertEqual(result["blocked_reason"], "approved_current_roster_source_unavailable")
        self.assertTrue(result["needs_identity_confirmation"])

    def test_source_as_of_provenance_is_preserved(self):
        client = FakeClient([identity_row(source_as_of="2026-07-01T00:00:00Z")])

        result = bridge.resolve_player_identity(
            sleeper_player_id="1166",
            client=client,
            dataset_id="fantasy_football_brain",
        )

        provenance = result["provenance"][0]
        self.assertEqual(provenance["source"], "player_identity_bridge")
        self.assertEqual(provenance["source_as_of"], "2026-07-01T00:00:00Z")

    def test_compact_variant_builder_handles_initials(self):
        variants = bridge.build_compact_display_variants("A.J. Brown", "Justin Jefferson")

        self.assertIn("a.brown", variants)
        self.assertIn("aj.brown", variants)
        self.assertIn("j.jefferson", variants)

    def test_output_can_be_consumed_by_qa_helper(self):
        packet = {"display_name": "Tyreek Hill", "player_id_internal": "00-0032764", "historical_team": "MIA"}
        current = {"display_name": "Tyreek Hill", "player_id_internal": "00-0032764", "current_team": "LV"}

        result = bridge.reconcile_packet_and_current_identity(packet, current)

        self.assertEqual(result["status"], "identity_match")
        self.assertFalse(result["needs_identity_confirmation"])
        self.assertEqual(result["historical_team"], "MIA")
        self.assertEqual(result["current_team"], "LV")

    def test_reconcile_reads_nested_stable_ids_from_bridge_selected_identity(self):
        packet = {"display_name": "T.Hill", "player_id_internal": "00-0033040", "historical_team": "MIA"}
        current = {
            "display_name": "Kirk Cousins",
            "stable_ids": {
                "player_id_internal": "gsis:00-0029604",
                "sleeper_player_id": "1166",
            },
            "current_team": "LV",
        }

        result = bridge.reconcile_packet_and_current_identity(packet, current)

        self.assertEqual(result["status"], "needs_identity_confirmation")
        self.assertEqual(result["mismatch_diagnostics"][0]["field"], "player_id_internal")

    def test_no_sleeper_api_bigquery_write_pigskin_llm_or_tool_registration_exists(self):
        source = Path("src/pigskin_identity_bridge.py").read_text(encoding="utf-8").lower()

        self.assertNotIn("requests.", source)
        self.assertNotIn("ingest_sleeper", source)
        self.assertNotIn("insert_rows", source)
        self.assertNotIn("load_table", source)
        self.assertNotIn("execute_pigskin_context_tool", source)
        self.assertNotIn("google.generativeai", source)
        self.assertNotIn("function_declarations", source)
        self.assertNotIn("get_pigskin_context_tool_declarations", source)


if __name__ == "__main__":
    unittest.main()
