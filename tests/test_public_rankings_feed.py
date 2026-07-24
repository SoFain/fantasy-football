from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.public_rankings_feed import OVERALL_BOARD_SIZE, build_profile_payload, json_bytes, sha256_hex


def overall_rows():
    rows = []
    positions = ("QB", "RB", "WR", "TE")
    position_counts = {position: 0 for position in positions}
    for rank in range(1, OVERALL_BOARD_SIZE + 1):
        position = positions[(rank - 1) % len(positions)]
        position_counts[position] += 1
        rows.append(
            {
                "board_version": "board-v1",
                "generated_at": datetime(2026, 7, 12, tzinfo=timezone.utc),
                "overall_rank": rank,
                "player_id": f"p{rank}",
                "player_name": f"Player {rank}",
                "current_team": "BUF",
                "position": position,
                "position_rank": position_counts[position],
                "projected_ppg": 10.0,
                "vorp": 2.0,
                "adjusted_vorp": 1.8,
                "position_source_version": f"{position.lower()}-v1",
                "position_rank_source": "formula",
                "risk_flags": None,
            }
        )
    return rows


def positional_rows():
    rows = []
    for overall in overall_rows():
        rows.append(
            {
                "ranking_version": f"{overall['position'].lower()}-v1",
                "generated_at": datetime(2026, 7, 12, tzinfo=timezone.utc),
                "position": overall["position"],
                "rank": overall["position_rank"],
                "tier": "starter",
                "player_id": overall["player_id"],
                "player_name": overall["player_name"],
                "current_team": overall["current_team"],
                "ranking_score": 90.0,
                "pigskin_verdict": "Public verdict.",
                "rank_rationale": "Scientific formula rationale.",
                "rank_source": "formula",
                "model_name": "deterministic",
                "prompt_version": "none",
            }
        )
    return rows


class PublicRankingsFeedTests(unittest.TestCase):
    def test_builds_deterministic_public_profile(self):
        payload = build_profile_payload(
            project_id="project",
            dataset_id="dataset",
            scoring_profile_id="standard",
            overall_rows=overall_rows(),
            positional_rows=positional_rows(),
        )

        self.assertEqual(OVERALL_BOARD_SIZE, payload["overall"]["count"])
        self.assertEqual(38, payload["positions"]["QB"]["count"])
        self.assertEqual("Public verdict.", payload["overall"]["players"][0]["pigskin_verdict"])
        self.assertNotIn("context", payload["overall"]["players"][0])
        self.assertNotIn("context", payload["positions"]["QB"]["players"][0])
        self.assertEqual(sha256_hex(json_bytes(payload)), sha256_hex(json_bytes(payload)))

    def test_adds_gng_context_to_overall_and_position_players(self):
        rows = positional_rows()
        for row in rows:
            row["ranking_context"] = "GNG scoring fit and advanced metric context."

        payload = build_profile_payload(
            project_id="project",
            dataset_id="dataset",
            scoring_profile_id="gng_keeper",
            overall_rows=overall_rows(),
            positional_rows=rows,
        )

        expected = "GNG scoring fit and advanced metric context."
        self.assertEqual(expected, payload["overall"]["players"][0]["context"])
        self.assertEqual(expected, payload["positions"]["QB"]["players"][0]["context"])

    def test_rejects_missing_gng_context(self):
        rows = positional_rows()
        for row in rows:
            row["ranking_context"] = "GNG context."
        rows[0]["ranking_context"] = None

        with self.assertRaisesRegex(ValueError, "missing GNG context"):
            build_profile_payload(
                project_id="project",
                dataset_id="dataset",
                scoring_profile_id="gng_keeper",
                overall_rows=overall_rows(),
                positional_rows=rows,
            )

    def test_rejects_missing_scientific_rank_rationale(self):
        overall = overall_rows()
        positional = positional_rows()
        positional[0]["rank_rationale"] = ""

        with self.assertRaisesRegex(ValueError, "missing scientific rank rationale"):
            build_profile_payload(
                project_id="project",
                dataset_id="dataset",
                scoring_profile_id="standard",
                overall_rows=overall,
                positional_rows=positional,
            )

    def test_rejects_non_contiguous_overall_rank(self):
        rows = overall_rows()
        rows[-1]["overall_rank"] = OVERALL_BOARD_SIZE + 1

        with self.assertRaisesRegex(ValueError, f"not contiguous 1-{OVERALL_BOARD_SIZE}"):
            build_profile_payload(
                project_id="project",
                dataset_id="dataset",
                scoring_profile_id="standard",
                overall_rows=rows,
                positional_rows=positional_rows(),
            )

    def test_flags_missing_positional_context_without_fabricating_it(self):
        rows = positional_rows()
        rows.pop()

        payload = build_profile_payload(
            project_id="project",
            dataset_id="dataset",
            scoring_profile_id="standard",
            overall_rows=overall_rows(),
            positional_rows=rows,
        )

        self.assertEqual("missing_active_positional_context", payload["warnings"][0]["code"])
        self.assertEqual("missing", payload["overall"]["players"][-1]["positional_context_status"])
        self.assertIsNone(payload["overall"]["players"][-1]["pigskin_verdict"])

    def test_rejects_teamless_overall_player(self):
        rows = overall_rows()
        rows[0]["current_team"] = None
        with self.assertRaisesRegex(ValueError, "overall board contains teamless players"):
            build_profile_payload(
                project_id="project",
                dataset_id="dataset",
                scoring_profile_id="standard",
                overall_rows=rows,
                positional_rows=positional_rows(),
            )

    def test_rejects_teamless_positional_player(self):
        rows = positional_rows()
        rows[0]["current_team"] = None
        with self.assertRaisesRegex(ValueError, "QB board contains teamless player"):
            build_profile_payload(
                project_id="project",
                dataset_id="dataset",
                scoring_profile_id="standard",
                overall_rows=overall_rows(),
                positional_rows=rows,
            )


if __name__ == "__main__":
    unittest.main()
