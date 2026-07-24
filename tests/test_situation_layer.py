import unittest

from src import situation_layer as sl


class BuildSituationSqlTest(unittest.TestCase):
    def setUp(self):
        self.sql = sl.build_situation_sql("proj", "ds")

    def test_renders_without_placeholders(self):
        self.assertNotIn("{project_id}", self.sql)
        self.assertNotIn("{dataset_id}", self.sql)

    def test_normalizes_the_prefixed_identity_scheme(self):
        # The profile mart's 2025 rows use 'gsis:'-prefixed ids while earlier
        # seasons use bare gsis; the layer must join on the normalized key or
        # the 2024->2025 transition silently vanishes (0 joins observed).
        self.assertIn("REGEXP_REPLACE(player_id_internal, r'^gsis:', '')", self.sql)
        self.assertIn("source_player_key", self.sql)

    def test_targets_both_slices(self):
        self.assertIn(f"BETWEEN {sl.FIRST_TRANSITION_SEASON} AND {sl.STATS_SEASON}", self.sql)
        self.assertIn(f"{sl.CURRENT_SEASON} AS situation_for_season", self.sql)

    def test_qb_quality_is_prior_season(self):
        # qb_to's quality must come from the stats season, never the outcome
        # season, or the training set leaks the future.
        self.assertIn("qb_next_prior.season = prev.season", self.sql)

    def test_flags_cover_the_editorial_set(self):
        for flag in ("NEW_TEAM", "QB_CHANGED", "QB_UPGRADE_MAJOR", "QB_DOWNGRADE", "AGE_CLIFF"):
            self.assertIn(flag, self.sql)

    def test_age_cliff_bands_are_position_specific(self):
        for pos, age in sl.AGE_CLIFF.items():
            self.assertIn(f"e.position = '{pos}' AND e.age_at_season >= {age}", self.sql)

    def test_current_rows_read_platform_sources(self):
        self.assertIn("sleeper_players_current", self.sql)
        self.assertIn("coaching_staff_current", self.sql)
        self.assertIn("analytics_pigskin_rankings", self.sql)

    def test_metric_basis_names_the_stats_context(self):
        self.assertIn("metric_basis", self.sql)


class JobWiringTest(unittest.TestCase):
    def test_job_registered(self):
        from src.job_runner import JOB_DISPATCHERS, VALID_JOB_NAMES

        self.assertIn("build-situation-layer", VALID_JOB_NAMES)
        self.assertIn("build-situation-layer", JOB_DISPATCHERS)

    def test_dry_run_makes_no_queries(self):
        result = sl.build_situation_layer(client=object(), dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertGreater(result["sql_bytes"], 1000)


if __name__ == "__main__":
    unittest.main()
