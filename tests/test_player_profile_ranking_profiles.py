from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd

from src import player_profile_ranking_profiles as profiles


class PlayerProfileRankingProfileTests(unittest.TestCase):
    def test_dropdown_options_are_limited_to_requested_profiles(self):
        options = profiles.get_player_profile_scoring_profile_options()

        self.assertEqual([option["label"] for option in options], ["Standard", "Half PPR", "PPR", "GNG Keeper"])
        self.assertEqual([option["scoring_profile_id"] for option in options], ["standard", "half_ppr", "ppr", "gng_keeper"])

    def test_default_profile_is_standard(self):
        resolved = profiles.resolve_player_profile_scoring_profile(None)

        self.assertEqual(profiles.PLAYER_PROFILE_SCORING_PROFILE_DEFAULT, "standard")
        self.assertEqual(resolved["label"], "Standard")
        self.assertEqual(resolved["scoring_profile_id"], "standard")

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
        self.assertIn("llm_adjustment_code", sql)
        self.assertIn("llm_rank_delta", sql)
        self.assertIn("sleeper_injury_status", sql)
        self.assertIn("latest_sleeper_status", sql)
        self.assertIn("COALESCE(latest_sleeper_status.injury_status", sql)
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

    def test_app_defaults_to_all_board_and_unified_all_view(self):
        app_source = Path("app.py").read_text(encoding="utf-8")

        self.assertIn('st.session_state.selected_pos = "ALL"', app_source)
        self.assertIn('positions = ["ALL", "QB", "RB", "WR", "TE"]', app_source)
        self.assertIn('if selected_pos == "ALL":', app_source)
        self.assertIn('sort_player_profile_board(df_pos, selected_pos)', app_source)
        self.assertIn('fetch_unified_rankings_data', app_source)
        self.assertNotIn('by=["position", "display_rank_sort", "display_score_sort"]', app_source)

    def test_all_board_uses_unified_overall_rank(self):
        observed_rows = [
            ("Jaxon Smith-Njigba", "WR", 1, 99.8),
            ("Puka Nacua", "WR", 2, 98.7),
            ("Josh Allen", "QB", 1, 97.6),
            ("Christian McCaffrey", "RB", 1, 96.5),
            ("Trey McBride", "TE", 1, 95.4),
            ("Amon-Ra St. Brown", "WR", 3, 94.3),
            ("Ja'Marr Chase", "WR", 4, 93.2),
            ("Drake London", "WR", 5, 92.1),
            ("Drake Maye", "QB", 2, 91.0),
            ("Bijan Robinson", "RB", 2, 90.0),
        ]
        df = pd.DataFrame(
            [
                {
                    "player_display_name": name,
                    "position": position,
                    "display_rank": rank,
                    "display_score": score,
                    "unified_overall_rank": index,
                }
                for index, (name, position, rank, score) in enumerate(observed_rows, 1)
            ]
        ).sample(frac=1, random_state=7)

        sorted_df = profiles.sort_player_profile_board(df, "ALL")

        self.assertEqual(
            sorted_df["player_display_name"].tolist(),
            [name for name, _, _, _ in observed_rows],
        )
        self.assertEqual(sorted_df["board_rank"].tolist(), list(range(1, 11)))

    def test_unified_query_is_scoring_profile_scoped(self):
        sql, job_config = profiles.build_unified_rankings_query("project", "dataset", "standard")
        self.assertIn("unified_draft_rankings_current", sql)
        self.assertIn("overall_rank AS unified_overall_rank", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["scoring_profile_id"], "standard")

    def test_adjustment_labels_are_readable(self):
        self.assertEqual(profiles.format_adjustment_label("NO_ADJUSTMENT", 0), "Formula rank")
        self.assertEqual(profiles.format_adjustment_label(None, None), "Formula rank")
        self.assertEqual(profiles.format_adjustment_label("CURRENT_ROLE_UPGRADE", 2), "Role upgrade +2")
        self.assertEqual(profiles.format_adjustment_label("INJURY_UNCERTAIN", 0), "Injury noted, no move")
        self.assertEqual(profiles.format_adjustment_label("SUSPENSION_UNCERTAIN", 0), "Suspension review, no move")
        self.assertEqual(profiles.format_adjustment_label("SUSPENSION_3_5", -4), "Suspension adjustment -4")

    def test_live_ranking_context_query_uses_player_profile_source_and_depths(self):
        sql, job_config = profiles.build_live_ranking_context_query(
            "test-project",
            "test_dataset",
            scoring_profile_id="standard",
            board="ALL",
            limit=10,
        )

        self.assertIn("analytics_pigskin_rankings", sql)
        self.assertIn("unified_draft_rankings_current", sql)
        self.assertIn("ROW_NUMBER() OVER", sql)
        self.assertIn("CASE WHEN @position IS NULL THEN unified_overall_rank END ASC", sql)
        self.assertIn("WHEN 'TE' THEN 35", sql)
        self.assertNotIn("Formula Review", sql)
        self.assertNotIn("analytics_pigskin_rankings_candidates", sql)
        self.assertNotIn("ranking_formula_champions", sql)
        self.assertNotIn("pigskin_context_score", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["scoring_profile_id"], "standard")
        self.assertIsNone(params["position"])
        self.assertEqual(params["limit"], 10)


if __name__ == "__main__":
    unittest.main()
