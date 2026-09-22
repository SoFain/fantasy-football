import unittest

from scripts.promote_te_fable_v1a_standard_te import build_statements


class PromoteTeFableV1aTest(unittest.TestCase):
    def setUp(self):
        self.statements = dict(build_statements("project", "brain", "metrics", "version", "run"))
        self.sql = "\n".join(self.statements.values())

    def test_scope_is_standard_te_only(self):
        self.assertIn("position = 'TE'", self.sql)
        self.assertIn("scoring_profile_id = 'standard'", self.sql)
        self.assertNotIn("position = 'RB'", self.sql)

    def test_board_uses_no_man_formula_and_te35(self):
        insert = self.statements["insert_fable_board"]
        self.assertIn("te_fable_v1a_no_man_score", insert)
        self.assertIn("QUALIFY board_rank <= 35", insert)
        self.assertIn("'te_fable_v1a_no_man_formula'", insert)

    def test_prior_board_is_archived(self):
        self.assertIn("analytics_pigskin_rankings_history", self.statements["archive_prior_board"])
        self.assertIn("is_active", self.statements["archive_prior_board"])

    def test_deterministic_board_has_no_llm_movement(self):
        insert = self.statements["insert_fable_board"]
        self.assertIn("'NO_ADJUSTMENT'", insert)
        self.assertIn("'deterministic-no-llm'", insert)
        self.assertNotIn("GEMINI", insert.upper())


if __name__ == "__main__":
    unittest.main()
