from __future__ import annotations

from pathlib import Path
import json
import unittest

from src import pigskin_packet_retrieval as retrieval


class FakeJob:
    def __init__(self, rows):
        self._rows = rows

    def result(self):
        return self._rows


class FakeClient:
    project = "fantasy-football-498121"

    def __init__(self, rows=None):
        self.rows = rows or []
        self.calls = []

    def query(self, sql, job_config=None):
        self.calls.append((sql, job_config))
        return FakeJob(self.rows)


def packet_row(**overrides):
    base = {
        "as_of_season": 2025,
        "as_of_week": 18,
        "player_id_internal": "00-0032764",
        "player_name": "T.Hill",
        "position": "WR",
        "team": "MIA",
        "scoring_profile_id": "ppr",
        "league_type_id": "redraft",
        "roster_format_id": "one_qb",
        "packet_version": "pigskin_packet_v0",
        "feature_run_id": "feature_2025",
        "packet_text": "Historical Miami usage context.",
        "packet_json": json.dumps(
            {
                "warnings": ["sample size warning"],
                "blocked_metrics": ["route_share", "pressure_rate"],
                "source_metric_version": "nflverse_advanced_metrics_v0",
            }
        ),
        "source_freshness_json": json.dumps({"role": {"max_week": 18}}),
        "missing_data_flags": json.dumps({"blocked_metric_flags": ["route_share"]}),
        "created_at": "2026-06-30T00:00:00",
    }
    base.update(overrides)
    return base


def params_by_name(job_config):
    return {param.name: param for param in job_config.query_parameters}


class PigskinPacketRetrievalTests(unittest.TestCase):
    def test_rejects_request_without_explicit_season_or_window(self):
        result = retrieval.retrieve_historical_pigskin_packets()

        self.assertEqual(result["status"], "validation_error")
        self.assertIn("explicit season", result["error"])

    def test_builds_parameterized_query_against_compat_view(self):
        sql, job_config = retrieval.build_historical_packet_query(
            project_id="fantasy-football-498121",
            dataset_id="fantasy_football_brain",
            season_start=2025,
            season_end=2025,
            player_name_variants=["t.hill"],
        )

        rendered = sql.lower()
        self.assertIn("compat_pigskin_player_context_current", rendered)
        self.assertNotIn("raw_nflverse_", rendered)
        self.assertNotIn("stg_", rendered)
        self.assertNotIn("pigskin_player_context_packet_current", rendered)
        self.assertIn("@season_start", rendered)
        self.assertIn("@player_name_variants", rendered)
        self.assertEqual(
            job_config.maximum_bytes_billed,
            retrieval.DEFAULT_MAX_BYTES_BILLED,
        )

    def test_injected_player_name_is_not_rendered_into_sql(self):
        client = FakeClient([packet_row()])

        retrieval.retrieve_historical_pigskin_packets(
            season=2025,
            player_name="T.Hill'; SELECT * FROM raw_nflverse_pbp --",
            client=client,
            dataset_id="fantasy_football_brain",
        )

        sql, _ = client.calls[0]
        self.assertNotIn("SELECT *", sql)
        self.assertNotIn("raw_nflverse_pbp", sql)

    def test_player_id_lookup_is_deterministic_and_historical_only(self):
        client = FakeClient([packet_row()])

        result = retrieval.retrieve_historical_pigskin_packets(
            season=2025,
            player_id_internal="00-0032764",
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["status"], "ok")
        packet = result["packet"]
        self.assertEqual(packet["historical_team"], "MIA")
        self.assertEqual(packet["historical_position"], "WR")
        self.assertNotIn("current_team", packet)
        self.assertTrue(packet["current_roster_status_source_required"])

    def test_ambiguous_compact_name_returns_candidates_not_packet(self):
        client = FakeClient(
            [
                packet_row(player_id_internal="00-0032764", team="MIA", position="WR"),
                packet_row(player_id_internal="00-0027854", team="NO", position="TE"),
            ]
        )

        result = retrieval.retrieve_historical_pigskin_packets(
            season=2025,
            player_name="T.Hill",
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["status"], "ambiguous")
        self.assertFalse(result["found"])
        self.assertEqual(result["candidate_count"], 2)
        self.assertNotIn("packet", result)

    def test_full_name_variant_does_not_claim_current_roster_status(self):
        client = FakeClient(
            [
                packet_row(player_id_internal="00-0032764", team="MIA", position="WR"),
                packet_row(player_id_internal="00-0027854", team="NO", position="TE"),
            ]
        )

        result = retrieval.retrieve_historical_pigskin_packets(
            season=2025,
            player_name="Tyreek Hill",
            client=client,
            dataset_id="fantasy_football_brain",
        )
        _, job_config = client.calls[0]
        variants = params_by_name(job_config)["player_name_variants"].values

        self.assertIn("t.hill", variants)
        self.assertEqual(result["status"], "ambiguous")
        self.assertIn("Sleeper/current roster", result["current_roster_status_policy"])

    def test_team_and_position_can_disambiguate_compact_name(self):
        client = FakeClient([packet_row(player_id_internal="00-0032764")])

        result = retrieval.retrieve_historical_pigskin_packets(
            season=2025,
            player_name="T.Hill",
            team="MIA",
            position="WR",
            client=client,
            dataset_id="fantasy_football_brain",
        )
        _, job_config = client.calls[0]
        params = params_by_name(job_config)

        self.assertEqual(params["team"].value, "MIA")
        self.assertEqual(params["position"].value, "WR")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["packet"]["historical_team"], "MIA")

    def test_regular_season_mode_excludes_postseason_by_cutoff(self):
        sql, job_config = retrieval.build_historical_packet_query(
            project_id="fantasy-football-498121",
            dataset_id="fantasy_football_brain",
            season_start=2025,
            season_end=2025,
            include_postseason=False,
        )
        params = params_by_name(job_config)

        self.assertIn("as_of_week <= IF(as_of_season <= 2020, 17, 18)", sql)
        self.assertFalse(params["include_postseason"].value)

    def test_include_postseason_true_allows_week_22_result(self):
        client = FakeClient([packet_row(as_of_week=22)])

        result = retrieval.retrieve_historical_pigskin_packets(
            season=2025,
            week=22,
            include_postseason=True,
            player_id_internal="00-0032764",
            client=client,
            dataset_id="fantasy_football_brain",
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["packet"]["as_of_week"], 22)

    def test_blocked_metrics_are_preserved_as_unavailable(self):
        packet = retrieval.normalize_historical_packet(packet_row())

        self.assertIn("route_share", packet["blocked_metrics"])
        self.assertEqual(packet["blocked_metric_policy"], "blocked metrics are unavailable, not zero")
        self.assertIn("sample size warning", packet["warnings"])

    def test_malformed_packet_json_does_not_crash(self):
        packet = retrieval.normalize_historical_packet(
            packet_row(packet_json="{bad json")
        )

        self.assertEqual(packet["packet_json"], {})
        self.assertIn("packet_json could not be parsed", packet["warnings"])

    def test_module_does_not_import_sleeper_llm_or_pigskin_prompt_tools(self):
        source = Path("src/pigskin_packet_retrieval.py").read_text(encoding="utf-8").lower()

        self.assertNotIn("ingest_sleeper", source)
        self.assertNotIn("google.generativeai", source)
        self.assertNotIn("execute_pigskin_context_tool", source)


if __name__ == "__main__":
    unittest.main()
