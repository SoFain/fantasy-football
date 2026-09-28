from pathlib import Path
import unittest


SQL_PATH = Path(__file__).resolve().parents[1] / "bigquery" / "rb_std_gpt_5_5_v1_0a_dry_run.sql"


class RbStdGpt55V10aSqlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sql = SQL_PATH.read_text(encoding="utf-8")
        cls.lower_sql = cls.sql.lower()

    def test_query_is_read_only_and_bounded(self) -> None:
        for statement in ("insert ", "update ", "delete ", "merge ", "truncate ", "create table"):
            self.assertNotIn(statement, self.lower_sql)
        self.assertIn("target_season between 2023 and 2025", self.lower_sql)
        self.assertIn("source_window_end_season < target_season", self.lower_sql)

    def test_standard_xfp_removes_expected_receptions(self) -> None:
        self.assertIn("rec_fantasy_points_exp", self.sql)
        self.assertIn("$.receptions_exp", self.sql)
        self.assertIn("receiving_xfp_standard", self.sql)

    def test_rushing_only_weights_are_exact(self) -> None:
        self.assertIn("0.4375 * ryoe_modifier", self.sql)
        self.assertIn("0.3125 * rushing_efficiency_modifier", self.sql)
        self.assertIn("0.2500 * box_resilience_modifier", self.sql)

    def test_epa_variant_uses_epa_per_target(self) -> None:
        self.assertIn("receiving_epa_per_target", self.sql)
        self.assertIn("0.20 * receiving_epa_modifier", self.sql)
        self.assertNotIn("raw yac", self.lower_sql)
        self.assertNotIn("yac_above_expectation", self.lower_sql)

    def test_blocked_inputs_are_absent(self) -> None:
        for blocked in (
            "pigskin_context_score",
            "yprr",
            "tprr",
            "first_read",
            "broken_tackle",
        ):
            self.assertNotIn(blocked, self.lower_sql)

    def test_fumble_and_availability_contracts_are_present(self) -> None:
        self.assertIn("$.fumbles_lost", self.sql)
        self.assertIn("a.carries + a.receptions as touches", self.lower_sql)
        self.assertIn("games_with_offensive_snaps", self.sql)
        self.assertIn("availability_risk_flag", self.sql)


if __name__ == "__main__":
    unittest.main()
