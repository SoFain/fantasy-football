from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd

from src.compat_flags import COMPAT_FLAG_NAMES, compat_flag_enabled
from src.ui_data_guards import (
    attach_trade_pick_scores_to_assets,
    attach_trade_scores_to_assets,
    collect_selected_trade_assets,
    ensure_player_profile_display_columns,
    ensure_sleeper_watch_display_columns,
    is_trade_pick_asset,
    summarize_trade_pick_score_side,
    summarize_trade_score_side,
    trade_asset_selector_count_with_blank,
    trade_pick_slot_display,
    trade_pick_warning_labels,
    trade_side_has_mixed_player_and_pick_assets,
    unresolved_trade_asset_labels,
)


class StagingUiWarningFixTests(unittest.TestCase):
    def test_player_profiles_backfills_missing_depth_position_from_position(self):
        df = pd.DataFrame(
            {
                "player_display_name": ["A.J. Brown", "Bijan Robinson"],
                "position": ["WR", "RB"],
            }
        )

        out = ensure_player_profile_display_columns(df)

        self.assertEqual(out["depth_position"].tolist(), ["WR", "RB"])

    def test_versus_finder_profile_rows_fill_blank_depth_position(self):
        df = pd.DataFrame(
            {
                "player_display_name": ["Ja'Marr Chase", "Brock Bowers"],
                "position": ["WR", "TE"],
                "depth_position": ["", None],
            }
        )

        out = ensure_player_profile_display_columns(df)

        self.assertEqual(out["depth_position"].tolist(), ["WR", "TE"])

    def test_sleeper_watch_derives_missing_rolling_three_week_ppr(self):
        df = pd.DataFrame(
            {
                "player_name": ["Late Round Dart", "Empty Box Score"],
                "fantasy_points_last_3": [30.0, None],
            }
        )

        out = ensure_sleeper_watch_display_columns(df)

        self.assertEqual(out["rolling_3_week_ppr"].tolist(), [10.0, 0.0])
        self.assertIn("sleeper_score", out.columns)
        self.assertEqual(out["sleeper_score"].tolist(), [0.0, 0.0])

    def test_sleeper_watch_preserves_existing_rolling_three_week_ppr(self):
        df = pd.DataFrame({"rolling_3_week_ppr": ["12.5", None]})

        out = ensure_sleeper_watch_display_columns(df)

        self.assertEqual(out["rolling_3_week_ppr"].tolist(), [12.5, 0.0])

    def test_trade_lab_side_b_selection_collects_expected_asset(self):
        empty_label = "-- Select Player / Pick --"
        chase_label = "🏃 Ja'Marr Chase (WR - CIN) (Value: 9999)"
        player_map = {
            chase_label: {
                "player_display_name": "Ja'Marr Chase",
                "position": "WR",
                "team": "CIN",
                "market_value": 9999,
            }
        }

        assets = collect_selected_trade_assets(
            [empty_label, chase_label],
            player_map,
            empty_label,
        )

        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0]["player_display_name"], "Ja'Marr Chase")
        self.assertEqual(assets[0]["market_value"], 9999)

    def test_trade_lab_side_a_selection_collects_expected_asset(self):
        empty_label = "-- Select Player / Pick --"
        brown_label = "🏃 A.J. Brown (WR - PHI) (Value: 3821)"
        player_map = {
            brown_label: {
                "player_display_name": "A.J. Brown",
                "position": "WR",
                "team": "PHI",
                "market_value": 3821,
            }
        }

        assets = collect_selected_trade_assets([brown_label], player_map, empty_label)

        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0]["player_display_name"], "A.J. Brown")
        self.assertEqual(assets[0]["team"], "PHI")

    def test_trade_score_rows_attach_by_name_or_identity(self):
        assets = [
            {"player_display_name": "A.J. Brown", "player_id_internal": "p1"},
            {"player_display_name": "Ja'Marr Chase"},
        ]
        score_rows = [
            {"player_id": "p1", "player_name": "A.J. Brown", "trade_score": 81.5},
            {"player_id": "p2", "player_name": "Ja'Marr Chase", "trade_score": 89.0},
        ]

        attached = attach_trade_scores_to_assets(assets, score_rows)
        summary = summarize_trade_score_side(attached)

        self.assertEqual(attached[0]["score"]["trade_score"], 81.5)
        self.assertEqual(attached[1]["score"]["trade_score"], 89.0)
        self.assertEqual(summary["scored_count"], 2)
        self.assertEqual(summary["missing_count"], 0)
        self.assertEqual(summary["total_trade_score"], 170.5)

    def test_player_score_rows_do_not_attach_to_pick_assets(self):
        assets = [
            {"player_display_name": "2026 Pick 1.01", "position": "PICK", "source_pick_key": "sleeper:PICK:2026:1:1"},
        ]
        score_rows = [{"player_name": "2026 Pick 1.01", "trade_score": 96.7}]

        attached = attach_trade_scores_to_assets(assets, score_rows)

        self.assertIsNone(attached[0]["score"])

    def test_pick_score_rows_attach_by_source_key_or_label(self):
        assets = [
            {"player_display_name": "2026 Pick 1.01", "position": "PICK", "source_pick_key": "sleeper:PICK:2026:1:1"},
            {"player_display_name": "2026 1st", "position": "PICK"},
        ]
        score_rows = [
            {
                "source_pick_key": "sleeper:PICK:2026:1:1",
                "pick_label": "2026 Pick 1.01",
                "pick_score": 96.7,
                "score_tier": "elite",
                "model_version": "trade_pick_score_v0_2026_001",
            },
            {
                "source_pick_key": "sleeper:PICK:2026:1",
                "pick_label": "2026 1st",
                "pick_score": 86.2,
                "score_tier": "premium",
                "model_version": "trade_pick_score_v0_2026_001",
            },
        ]

        attached = attach_trade_pick_scores_to_assets(assets, score_rows)
        summary = summarize_trade_pick_score_side(attached)

        self.assertEqual(attached[0]["score"]["pick_score"], 96.7)
        self.assertEqual(attached[1]["score"]["score_tier"], "premium")
        self.assertEqual(summary["scored_count"], 2)
        self.assertEqual(summary["missing_count"], 0)
        self.assertEqual(summary["total_pick_score"], 182.9)

    def test_missing_pick_score_rows_are_reported_without_breaking_summary(self):
        assets = [
            {"player_display_name": "2026 Pick 1.01", "position": "PICK", "source_pick_key": "sleeper:PICK:2026:1:1"},
            {"player_display_name": "2027 3rd", "position": "PICK", "source_pick_key": "sleeper:PICK:2027:3"},
        ]
        score_rows = [{"source_pick_key": "sleeper:PICK:2026:1:1", "pick_label": "2026 Pick 1.01", "pick_score": 96.7}]

        attached = attach_trade_pick_scores_to_assets(assets, score_rows)
        summary = summarize_trade_pick_score_side(attached)

        self.assertIsNone(attached[1]["score"])
        self.assertEqual(summary["scored_count"], 1)
        self.assertEqual(summary["missing_count"], 1)
        self.assertEqual(summary["total_pick_score"], 96.7)

    def test_trade_side_mixed_asset_detection_keeps_scores_separate(self):
        assets = [
            {"player_display_name": "A.J. Brown", "position": "WR"},
            {"player_display_name": "2026 Pick 1.01", "position": "PICK"},
        ]

        self.assertTrue(is_trade_pick_asset(assets[1]))
        self.assertTrue(trade_side_has_mixed_player_and_pick_assets(assets))

    def test_trade_lab_selector_count_keeps_blank_after_filled_side(self):
        self.assertEqual(trade_asset_selector_count_with_blank(1, 0), 1)
        self.assertEqual(trade_asset_selector_count_with_blank(1, 1), 2)
        self.assertEqual(trade_asset_selector_count_with_blank(2, 1), 2)
        self.assertEqual(trade_asset_selector_count_with_blank(2, 2), 3)

    def test_trade_lab_renders_extra_side_a_selector_in_same_rerun(self):
        app_source = Path("app.py").read_text(encoding="utf-8")

        self.assertIn("next_num_a = trade_asset_selector_count_with_blank", app_source)
        self.assertIn('f"Select Asset A {i+1}"', app_source)
        self.assertIn("range(st.session_state.num_a, next_num_a)", app_source)

    def test_trade_lab_renders_extra_side_b_selector_in_same_rerun(self):
        app_source = Path("app.py").read_text(encoding="utf-8")

        self.assertIn("next_num_b = trade_asset_selector_count_with_blank", app_source)
        self.assertIn('f"Select Asset B {i+1}"', app_source)
        self.assertIn("range(st.session_state.num_b, next_num_b)", app_source)

    def test_trade_pick_slot_display_is_clear_for_exact_and_round_only(self):
        self.assertEqual(trade_pick_slot_display({"pick_class": "exact_slot", "pick_slot": 1.0}), "1")
        self.assertEqual(trade_pick_slot_display({"pick_class": "round_only", "pick_slot": None}), "round-only")

    def test_trade_pick_warning_labels_are_browser_readable(self):
        labels = trade_pick_warning_labels(
            [
                "college_context_unavailable",
                "draft_outcome_prior_insufficient",
                "pick_market_source_only",
                "pick_score_staging_only",
                "pick_round_only_uncertainty",
            ]
        )

        self.assertIn("college context unavailable", labels)
        self.assertIn("pick score staging only", labels)
        self.assertIn("pick round only uncertainty", labels)

    def test_non_ppr_missing_pick_score_remains_explicitly_unavailable(self):
        assets = [
            {"player_display_name": "2026 Pick 1.01", "position": "PICK", "source_pick_key": "sleeper:PICK:2026:1:1"},
        ]

        attached = attach_trade_pick_scores_to_assets(assets, [])
        summary = summarize_trade_pick_score_side(attached)

        self.assertIsNone(attached[0]["score"])
        self.assertEqual(summary["asset_count"], 1)
        self.assertEqual(summary["scored_count"], 0)
        self.assertEqual(summary["missing_count"], 1)

    def test_pick_score_component_and_warning_text_is_browser_visible(self):
        app_source = Path("app.py").read_text(encoding="utf-8")

        self.assertIn("Components: market, slot capital, time discount, liquidity, college context, uncertainty.", app_source)
        self.assertIn("Warnings: {warning_label_text}", app_source)

    def test_missing_trade_score_rows_are_reported_without_breaking_summary(self):
        assets = [
            {"player_display_name": "A.J. Brown", "player_id_internal": "p1"},
            {"player_display_name": "Unknown Asset", "player_id_internal": "missing"},
        ]
        score_rows = [{"player_id": "p1", "player_name": "A.J. Brown", "trade_score": 81.5}]

        attached = attach_trade_scores_to_assets(assets, score_rows)
        summary = summarize_trade_score_side(attached)

        self.assertIsNone(attached[1]["score"])
        self.assertEqual(summary["scored_count"], 1)
        self.assertEqual(summary["missing_count"], 1)
        self.assertEqual(summary["total_trade_score"], 81.5)

    def test_trade_lab_resolves_aj_brown_label_without_leading_icon(self):
        empty_label = "-- Select Player / Pick --"
        mapped_label = "🏃 A.J. Brown (WR - PHI) (Value: 3821)"
        selected_label = "A.J. Brown (WR - PHI) (Value: 3821)"
        player_map = {
            mapped_label: {
                "player_display_name": "A.J. Brown",
                "position": "WR",
                "team": "PHI",
                "market_value": 3821,
            }
        }

        assets = collect_selected_trade_assets([selected_label], player_map, empty_label)

        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0]["player_display_name"], "A.J. Brown")

    def test_trade_lab_resolves_jamarr_chase_curly_apostrophe_label(self):
        empty_label = "-- Select Player / Pick --"
        mapped_label = "🏃 Ja'Marr Chase (WR - CIN) (Value: 9888)"
        selected_label = "🏃 Ja’Marr Chase (WR - CIN) (Value: 9888)"
        player_map = {
            mapped_label: {
                "player_display_name": "Ja'Marr Chase",
                "position": "WR",
                "team": "CIN",
                "market_value": 9888,
            }
        }

        assets = collect_selected_trade_assets([selected_label], player_map, empty_label)

        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0]["player_display_name"], "Ja'Marr Chase")

    def test_trade_lab_unresolved_selection_is_reported(self):
        empty_label = "-- Select Player / Pick --"
        player_map = {}

        unresolved = unresolved_trade_asset_labels(
            ["Mystery Player (WR - FA) (Value: 1)"],
            player_map,
            empty_label,
        )

        self.assertEqual(unresolved, ["Mystery Player (WR - FA) (Value: 1)"])

    def test_trade_lab_side_state_keys_do_not_collide(self):
        app_source = Path("app.py").read_text(encoding="utf-8")

        self.assertIn('key=f"sel_a_{i}"', app_source)
        self.assertIn('key=f"sel_b_{i}"', app_source)

    def test_feature_flags_still_default_false(self):
        for flag_name in COMPAT_FLAG_NAMES:
            self.assertFalse(compat_flag_enabled(flag_name, {}))


if __name__ == "__main__":
    unittest.main()
