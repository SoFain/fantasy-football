from __future__ import annotations

import unittest
from unittest.mock import patch

from src import materialize


class PigskinRankingsMaterializeIdentityTests(unittest.TestCase):
    def test_candidate_sql_uses_identity_bridge_for_sleeper_to_gsis_metrics_join(self):
        sql = materialize.build_pigskin_rankings_sql("project-id", "dataset_id")

        self.assertIn("player_identity_bridge", sql)
        self.assertIn("COALESCE(rp.player_id, sc.gsis_id, ib.gsis_id) AS metrics_player_id", sql)
        self.assertIn("ON rp.metrics_player_id = agg.player_id", sql)
        self.assertIn("ON rp.metrics_player_id = ms.player_id", sql)
        self.assertIn("CONCAT('sleeper:', sc.sleeper_player_id)", sql)

    def test_candidate_sql_is_scoring_profile_aware(self):
        sql = materialize.build_pigskin_rankings_sql(
            "project-id",
            "dataset_id",
            scoring_profile_id="gng_keeper",
            league_type_id="keeper",
            roster_format_id="one_qb",
        )

        self.assertIn("'gng_keeper' AS scoring_profile_id", sql)
        self.assertIn("'GNG Keeper' AS scoring_profile_label", sql)
        self.assertIn("'keeper' AS league_type_id", sql)
        self.assertIn("analytics_player_fantasy_points_by_profile", sql)
        self.assertIn("avg_profile_points", sql)
        self.assertIn("missing selected scoring profile sample", sql)

    def test_candidate_sql_labels_half_ppr_profile(self):
        sql = materialize.build_pigskin_rankings_sql(
            "project-id",
            "dataset_id",
            scoring_profile_id="half_ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
        )

        self.assertIn("'half_ppr' AS scoring_profile_id", sql)
        self.assertIn("'Half PPR' AS scoring_profile_label", sql)

    def test_pigskin_rankings_materialization_requires_identity_bridge(self):
        class FakeClient:
            project = "project-id"

            def query(self, *_args, **_kwargs):
                raise AssertionError("query should not run when identity bridge is missing")

        with patch.object(materialize, "get_existing_tables", return_value={"analytics_player_weekly_truth", "player_rosters", "sleeper_players_current"}):
            with self.assertRaisesRegex(RuntimeError, "player_identity_bridge"):
                materialize.materialize_pigskin_rankings(FakeClient(), dataset_id="dataset_id", dry_run=True)


if __name__ == "__main__":
    unittest.main()
