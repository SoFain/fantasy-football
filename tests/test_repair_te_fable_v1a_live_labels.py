import unittest

from scripts.repair_te_fable_v1a_live_labels import build_repair_sql


class RepairTeFableLiveLabelsTests(unittest.TestCase):
    def setUp(self):
        self.sql = build_repair_sql("project", "dataset")

    def test_repair_is_scoped_to_active_standard_te_board(self):
        self.assertIn("target.position = 'TE'", self.sql)
        self.assertIn("target.scoring_profile_id = 'standard'", self.sql)
        self.assertIn("target.league_type_id = 'redraft'", self.sql)
        self.assertIn("target.roster_format_id = 'one_qb'", self.sql)
        self.assertIn("target.ranking_version = @ranking_version", self.sql)

    def test_repair_updates_only_deterministic_presentation_fields(self):
        update_clause = self.sql.split("UPDATE ", 1)[1].split("WHERE target.is_active", 1)[0]
        self.assertIn("tier = CASE", update_clause)
        self.assertIn("pigskin_verdict = CASE", update_clause)
        self.assertIn("what_would_change_mind =", update_clause)
        self.assertNotIn("rank =", update_clause)
        self.assertNotIn("ranking_score =", update_clause)
        self.assertNotIn("\n  llm_adjustment_code =", update_clause)

    def test_tiers_follow_te35_cutlines(self):
        self.assertIn("target.rank <= 5", self.sql)
        self.assertIn("target.rank <= 12", self.sql)
        self.assertIn("target.rank <= 24", self.sql)
        self.assertIn("'flex or matchup'", self.sql)

    def test_model_audit_code_is_only_read_for_injury_copy(self):
        self.assertIn("target.llm_adjustment_code = 'INJURY_UNCERTAIN'", self.sql)
        self.assertIn("has no preseason rank effect", self.sql)


if __name__ == "__main__":
    unittest.main()
