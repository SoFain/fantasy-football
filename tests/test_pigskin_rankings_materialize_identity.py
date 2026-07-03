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
