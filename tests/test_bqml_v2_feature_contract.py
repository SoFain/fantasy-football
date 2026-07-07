from __future__ import annotations

import unittest

from src import bqml_v2_feature_contract as contract


class BqmlV2FeatureContractTests(unittest.TestCase):
    def test_standard_is_first_and_no_global_winner(self):
        self.assertEqual(contract.SCORING_PROFILE_ORDER[0], "standard")
        self.assertTrue(contract.NO_GLOBAL_ALL_PROFILE_WINNER)

    def test_model_families_are_position_and_target_specific(self):
        self.assertEqual(
            contract.model_family_ids(),
            (
                "bqml_v2_qb_profile_points",
                "bqml_v2_qb_elite_bust",
                "bqml_v2_rb_profile_points",
                "bqml_v2_rb_elite_bust",
                "bqml_v2_wr_profile_points",
                "bqml_v2_wr_elite_bust",
                "bqml_v2_te_profile_points",
                "bqml_v2_te_elite_bust",
            ),
        )
        self.assertEqual(contract.ALLOWED_MODEL_TYPES, ("LINEAR_REG", "LOGISTIC_REG"))
        self.assertIn("BOOSTED_TREE_REGRESSOR", contract.DEFERRED_MODEL_TYPES)
        self.assertIn("GEMINI", contract.BLOCKED_MODEL_TYPES)

    def test_feature_allowlists_are_position_specific(self):
        qb_features = contract.features_for_position("QB")
        rb_features = contract.features_for_position("RB")
        wr_features = contract.features_for_position("WR")
        te_features = contract.features_for_position("TE")

        self.assertIn("passing_epa_per_play", qb_features)
        self.assertNotIn("passing_epa_per_play", rb_features)
        self.assertIn("rb_high_value_opportunity_score", rb_features)
        self.assertNotIn("rb_high_value_opportunity_score", wr_features)
        self.assertIn("receiving_first_down_exp_pbp_3yr", wr_features)
        self.assertIn("offensive_snap_share_3yr", te_features)

    def test_blocked_route_metrics_are_rejected(self):
        for blocked_feature in (
            "yprr",
            "yards_per_route_run",
            "tprr",
            "targets_per_route_run",
            "true_route_share",
            "route_share",
            "first_read_share",
        ):
            with self.subTest(blocked_feature=blocked_feature):
                with self.assertRaisesRegex(ValueError, "blocked"):
                    contract.validate_features("WR", [blocked_feature])

    def test_pigskin_context_score_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "blocked"):
            contract.validate_features("QB", ["pigskin_context_score"])

    def test_historical_depth_is_rejected_when_coverage_zero(self):
        with self.assertRaisesRegex(ValueError, "blocked"):
            contract.validate_features("RB", ["depth_chart_role_score_3yr"])

    def test_sleeper_current_context_is_rejected_as_historical_predictor(self):
        for blocked_feature in (
            "sleeper_current_team",
            "sleeper_current_status",
            "sleeper_depth_chart_position",
            "current_team",
        ):
            with self.subTest(blocked_feature=blocked_feature):
                with self.assertRaisesRegex(ValueError, "blocked"):
                    contract.validate_features("TE", [blocked_feature])

    def test_target_and_outcome_columns_are_excluded_from_predictors(self):
        for position in contract.POSITIONS:
            predictors = contract.predictor_fields_for_position(position)
            for outcome_field in contract.OUTCOME_ONLY_FIELDS:
                self.assertNotIn(outcome_field, predictors)

        with self.assertRaisesRegex(ValueError, "label or outcome"):
            contract.validate_features("QB", ["target_fantasy_points"])

    def test_standard_training_predictors_include_recovered_feature_mart_fields(self):
        predictors = contract.standard_training_predictor_fields()

        self.assertIn("passing_epa_per_play", predictors)
        self.assertIn("receiving_yards", predictors)
        self.assertIn("receiving_epa", predictors)
        self.assertIn("red_zone_targets", predictors)
        self.assertIn("red_zone_opportunities", predictors)
        self.assertIn("goal_line_opportunities", predictors)
        self.assertNotIn("ngs_catch_over_expected_score_3yr", predictors)
        self.assertEqual(contract.STANDARD_ZERO_COVERAGE_DEFERRED_FEATURES, frozenset({"ngs_catch_over_expected_score_3yr"}))

    def test_target_columns_are_allowed_only_as_labels(self):
        self.assertEqual(
            contract.target_fields_for_family("bqml_v2_qb_profile_points"),
            ("target_fantasy_points", "value_over_replacement"),
        )
        self.assertEqual(
            contract.target_fields_for_family("bqml_v2_te_elite_bust"),
            ("elite_finish_label", "starter_finish_label", "bust_label"),
        )

    def test_standard_dry_run_query_is_leakage_safe(self):
        sql = contract.build_standard_training_dataset_query("project", "dataset")

        self.assertIn("scoring_profile_id = 'standard'", sql)
        self.assertIn("source_window_end_season < target_season", sql)
        self.assertIn("WHEN target_season BETWEEN 2017 AND 2023 THEN 'train'", sql)
        self.assertIn("WHEN target_season = 2024 THEN 'validation'", sql)
        self.assertIn("WHEN target_season = 2025 THEN 'holdout'", sql)
        self.assertNotIn("2026", sql)
        contract.assert_standard_query_leakage_safe(sql)

    def test_standard_dry_run_query_does_not_include_blocked_columns(self):
        sql = contract.build_standard_training_dataset_query("project", "dataset").lower()
        for blocked_feature in contract.BLOCKED_FEATURES:
            self.assertNotIn(blocked_feature, sql)
        for deferred_feature in contract.STANDARD_ZERO_COVERAGE_DEFERRED_FEATURES:
            self.assertNotIn(deferred_feature, sql)

    def test_proxy_names_do_not_overclaim_route_metrics(self):
        self.assertEqual(contract.PROXY_LABELS["receiving_first_down_exp_pbp_3yr"], "chain-mover proxy")
        self.assertEqual(contract.PROXY_LABELS["offensive_snap_share_3yr"], "snap-role proxy")
        self.assertIn("1D/RR", contract.FORBIDDEN_PROXY_LABELS["receiving_first_down_exp_pbp_3yr"])
        self.assertIn("route participation rate", contract.FORBIDDEN_PROXY_LABELS["offensive_snap_share_3yr"])

    def test_te_review_board_limit_is_35(self):
        self.assertEqual(contract.REVIEW_POSITION_LIMITS["TE"], 35)

    def test_integrity_query_checks_grain_and_leakage(self):
        sql = contract.build_standard_integrity_query("project", "dataset")

        self.assertIn("source_window_end_season >= target_season", sql)
        self.assertIn("missing_player_id_count", sql)
        self.assertIn("missing_scoring_profile_count", sql)
        self.assertIn("missing_target_label_count", sql)
        self.assertIn("duplicate_grain_count", sql)
        self.assertNotIn(" AS rows", sql)

    def test_sample_query_is_bounded_by_position(self):
        sql = contract.build_standard_sample_query("project", "dataset", per_position_limit=5)

        self.assertIn("ROW_NUMBER() OVER", sql)
        self.assertIn("PARTITION BY position", sql)
        self.assertIn("position_sample_rank <= 5", sql)
        self.assertIn("bqml_v2_missing_flags_json", sql)

    def test_training_sql_templates_are_prepared_not_executed(self):
        templates = contract.build_standard_model_sql_templates("project", "dataset")

        self.assertEqual(len(templates), 16)
        self.assertIn("standard_qb_linear_points", templates)
        self.assertIn("standard_te_logistic_bust", templates)
        self.assertIn("ranking_bqml_v2_standard_qb_linear_points_v0", templates["standard_qb_linear_points"])
        self.assertIn("ranking_bqml_v2_standard_te_logistic_bust_v0", templates["standard_te_logistic_bust"])
        self.assertIn("data_split_method = 'NO_SPLIT'", templates["standard_qb_linear_points"])
        self.assertIn("split = 'train'", templates["standard_qb_linear_points"])
        self.assertIn("model_type = 'LINEAR_REG'", templates["standard_qb_linear_points"])
        self.assertIn("model_type = 'LOGISTIC_REG'", templates["standard_qb_logistic_elite"])
        self.assertNotIn("BOOSTED_TREE", "\n".join(templates.values()))
        self.assertNotIn("pigskin_context_score", "\n".join(templates.values()))
        self.assertNotIn("depth_chart_role_score_3yr", "\n".join(templates.values()))
        self.assertIn("passing_epa_per_play", templates["standard_qb_linear_points"])
        self.assertIn("red_zone_opportunities", templates["standard_rb_linear_points"])
        self.assertIn("goal_line_opportunities", templates["standard_rb_linear_points"])
        self.assertIn("receiving_yards", templates["standard_wr_linear_points"])
        self.assertIn("receiving_epa", templates["standard_wr_linear_points"])
        self.assertIn("red_zone_targets", templates["standard_te_linear_points"])
        self.assertNotIn("ngs_catch_over_expected_score_3yr", "\n".join(templates.values()))

    def test_standard_model_specs_are_position_specific_and_bust_is_inverse(self):
        specs = contract.standard_model_specs()
        model_names = {spec["model_name"] for spec in specs}
        candidate_ids = {spec["candidate_id"] for spec in specs}

        self.assertEqual(len(specs), 16)
        self.assertIn("ranking_bqml_v2_standard_qb_linear_points_v0", model_names)
        self.assertIn("ranking_bqml_v2_standard_wr_logistic_elite_v0", model_names)
        self.assertIn("bqml_v2_standard_te_logistic_bust_inverse_v0", candidate_ids)
        bust_specs = [spec for spec in specs if spec["candidate_family"] == "bqml_v2_standard_logistic_bust_inverse"]
        self.assertEqual(len(bust_specs), 4)
        for spec in bust_specs:
            self.assertEqual(spec["label_field"], "bust_label")
            self.assertEqual(spec["higher_is_better"], "false")
            self.assertEqual(spec["prediction_column"], "predicted_bust_label_probs")

    def test_readiness_thresholds_keep_injury_and_depth_optional(self):
        self.assertEqual(contract.STANDARD_READINESS_THRESHOLDS["baseline_pigskin_proxies"], 0.95)
        self.assertEqual(contract.STANDARD_READINESS_THRESHOLDS["opportunity"], 0.95)
        self.assertNotIn("injury_availability", contract.STANDARD_READINESS_THRESHOLDS)
        self.assertNotIn("historical_depth", contract.STANDARD_READINESS_THRESHOLDS)


if __name__ == "__main__":
    unittest.main()
