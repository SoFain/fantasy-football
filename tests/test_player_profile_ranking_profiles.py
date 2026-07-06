from __future__ import annotations

import unittest

from src import player_profile_ranking_profiles as profiles


class PlayerProfileRankingProfileTests(unittest.TestCase):
    def test_dropdown_options_are_limited_to_requested_profiles(self):
        options = profiles.get_player_profile_scoring_profile_options()

        self.assertEqual([option["label"] for option in options], ["PPR", "Half PPR", "Standard", "GNG Keeper"])
        self.assertEqual([option["scoring_profile_id"] for option in options], ["ppr", "half_ppr", "standard", "gng_keeper"])

    def test_default_profile_is_ppr(self):
        resolved = profiles.resolve_player_profile_scoring_profile(None)

        self.assertEqual(profiles.PLAYER_PROFILE_SCORING_PROFILE_DEFAULT, "ppr")
        self.assertEqual(resolved["label"], "PPR")
        self.assertEqual(resolved["scoring_profile_id"], "ppr")

    def test_selected_profile_maps_to_internal_id(self):
        resolved = profiles.resolve_player_profile_scoring_profile("GNG Keeper")

        self.assertEqual(resolved["scoring_profile_id"], "gng_keeper")

    def test_half_ppr_profile_maps_to_internal_id(self):
        resolved = profiles.resolve_player_profile_scoring_profile("Half PPR")

        self.assertEqual(resolved["scoring_profile_id"], "half_ppr")

    def test_rankings_query_filters_selected_scoring_profile(self):
        sql, job_config = profiles.build_pigskin_rankings_query(
            "test-project",
            "test_dataset",
            "standard",
        )

        self.assertIn("analytics_pigskin_rankings", sql)
        self.assertIn("scoring_profile_id = @scoring_profile_id", sql)
        self.assertNotIn("ranking_formula_candidates", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["scoring_profile_id"], "standard")

    def test_rankings_query_caps_position_depths_for_player_profiles(self):
        sql, _ = profiles.build_pigskin_rankings_query(
            "test-project",
            "test_dataset",
            "ppr",
        )

        self.assertIn("WHEN 'QB' THEN 45", sql)
        self.assertIn("WHEN 'RB' THEN 80", sql)
        self.assertIn("WHEN 'WR' THEN 100", sql)
        self.assertIn("WHEN 'TE' THEN 35", sql)
        self.assertNotIn("WHEN 'TE' THEN 60", sql)

    def test_rankings_query_filters_half_ppr_without_fallback(self):
        sql, job_config = profiles.build_pigskin_rankings_query(
            "test-project",
            "test_dataset",
            "half_ppr",
        )

        self.assertIn("scoring_profile_id = @scoring_profile_id", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["scoring_profile_id"], "half_ppr")
        self.assertNotEqual(params["scoring_profile_id"], "ppr")

    def test_missing_profile_board_message_is_explicit(self):
        self.assertEqual(
            profiles.PLAYER_PROFILE_RANKINGS_MISSING_MESSAGE,
            "Rankings for this scoring system have not been generated yet.",
        )


if __name__ == "__main__":
    unittest.main()
