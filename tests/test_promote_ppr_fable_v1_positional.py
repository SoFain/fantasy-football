import unittest
from scripts.promote_ppr_fable_v1_positional import WRITE_GATE,build_sql,reception_candidates_sql

class PromotePprFableV1PositionalTest(unittest.TestCase):
    def test_scope_and_archive(self):
        sql=build_sql("p","d","ppr")
        self.assertIn("scoring_profile_id='ppr'",sql)
        self.assertIn("INSERT INTO `p.d.analytics_pigskin_rankings_history`",sql)
        self.assertIn("WHEN 'RB' THEN 80 WHEN 'WR' THEN 100 WHEN 'TE' THEN 35",sql)
        self.assertIn("v_ranking_post_formula_safety",sql)
        self.assertIn("formula_score + context.post_formula_adjustment",sql)
        self.assertIn("Selected Fable rows contain missing Sleeper identity context",sql)
        self.assertIn("context.current_board_rank_eligible",sql)
        self.assertIn("AND COALESCE(context.current_board_rank_eligible,FALSE)",sql)
        self.assertIn("candidate.formula_rank <= CASE candidate.position",sql)
        self.assertIn("c.formula_rank-c.new_rank AS llm_rank_delta",sql)
        self.assertIn("COALESCE(context.ranking_eligibility,'current_roster_review_required')",sql)
        self.assertIn("NOT EXISTS(SELECT 1 FROM reception_candidates c",sql)
        self.assertNotIn("position='QB'",sql)

    def test_candidates_come_from_current_formula_views_without_decisions(self):
        sql=build_sql("p","d","ppr","m")
        self.assertIn("CREATE TEMP TABLE reception_candidates AS",sql)
        self.assertLess(sql.index("CREATE TEMP TABLE reception_candidates"),sql.index("Selected Fable rows contain"))
        for removed in ("ppr_fable_rankings_current","recommended_rank","promotion_eligible","decision_code","decision_note","FORMULA_DEFAULT","EXCLUDE_UNSIGNED"):
            self.assertNotIn(removed,sql)
        self.assertIn("adjusted_formula_rank AS new_rank",sql)
        self.assertIn("Eligible Fable candidate has no ranking row template",sql)

    def test_reception_candidate_formula_matches_runbook(self):
        sql=reception_candidates_sql("p","m")
        self.assertIn("rb_fable_01_score + 0.02*z_target_share - 0.02*z_ngt_tpg AS formula_score",sql)
        self.assertIn("`p.m.v_wr_fable_v1_current_candidates`",sql)
        self.assertIn("`p.m.v_te_fable_v1a_scored_seasons`",sql)
        self.assertIn("PARTITION BY position ORDER BY formula_score DESC, player_name",sql)
        self.assertEqual(build_sql("p","d","ppr","m").count(sql),1)
        self.assertEqual(build_sql("p","d","half_ppr","m").count(sql),1)

    def test_rostered_injury_context_is_review_only(self):
        sql=build_sql("p","d","ppr","m")
        self.assertIn("AND context.gsis_id IS NULL",sql)
        self.assertIn("injury status is review-only with no estimated games missed",sql)
        self.assertIn("current_team IS NULL OR ranking_eligibility = 'teamless_unranked'",sql)
        self.assertNotIn("context.current_board_rank_eligible AND context.sleeper_hard_review",sql)
    def test_gate(self): self.assertEqual(WRITE_GATE,"ALLOW_PPR_FABLE_POSITIONAL_PROMOTION")

    def test_reception_profiles_normalize_scores_and_build_metric_verdicts(self):
        sql=build_sql("p","d","ppr","m")
        self.assertIn("MIN(ranking_score) OVER(PARTITION BY position)",sql)
        self.assertIn("ROUND(50+49*SAFE_DIVIDE",sql)
        self.assertIn("v_rb_fable_01_scored_seasons",sql)
        self.assertIn("v_wr_fable_v1_current_candidates",sql)
        self.assertIn("v_te_fable_v1a_scored_seasons",sql)
        self.assertIn("non-garbage-time touches per game",sql)
        self.assertIn("WOPR",sql)
        self.assertIn("targets per route",sql)
        self.assertIn("rank-only Pigskin verdicts",sql)
        self.assertIn("normalized to 50-99",sql)
        self.assertIn("receives veteran coverage",sql)

    def test_wr_repair_provenance_survives_future_promotions(self):
        sql=build_sql("p","d","ppr","m")
        self.assertIn("wr.prior_v1_score",sql)
        self.assertIn("current two-year availability component",sql)
        self.assertIn("MARVIN_HARRISON_JR_SOURCE_ID",sql)
        self.assertIn("formula weights unchanged",sql)

    def test_half_ppr_verdict_identifies_profile(self):
        sql=build_sql("p","d","half_ppr","m")
        self.assertIn("in Half-PPR",sql)

if __name__=="__main__": unittest.main()
