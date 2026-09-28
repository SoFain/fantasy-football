-- Current WR Fable v1 candidate universe with a veteran-only coverage fallback.
-- Current roster context is applied later by v_ranking_post_formula_safety.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_current_candidates` AS
SELECT
  source.*,
  source.carry_forward_replacement_score AS wr_fable_v1_score,
  source.latest_blended_td_per_game AS blended_td_per_game,
  CASE
    WHEN source.baseline_v1_score_available THEN 'CURRENT_SEASON_QUALIFIED'
    ELSE 'PRIOR_QUALIFIED_VETERAN_CARRY_FORWARD'
  END AS coverage_method,
  CASE
    WHEN source.baseline_v1_score_available THEN source.season
    ELSE source.season - 1
  END AS score_source_season
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1d_scored_seasons` AS source
WHERE source.season = 2025
  AND source.variant_id = 'I4'
  AND source.carry_forward_replacement_score IS NOT NULL
  AND (
    source.baseline_v1_score_available
    OR (
      source.prior_score_carry_forward_eligible
      AND NOT source.rookie_limited_sample_flag
    )
  );
