-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_metric_rows = 0

SELECT COUNT(*) AS invalid_metric_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_opportunity_metrics`
WHERE high_value_opportunity_score < 0
   OR high_value_opportunity_score > 100
   OR receiving_equity_score < 0
   OR receiving_equity_score > 100
   OR qb_rushing_leverage_index < 0
   OR qb_rushing_leverage_index > 100
   OR wr_dominance_score < 0
   OR wr_dominance_score > 100
   OR te_receiving_role_dominance_score < 0
   OR te_receiving_role_dominance_score > 100
   OR team_environment_score < 0
   OR team_environment_score > 100
   OR missing_flags_json IS NULL
   OR source_freshness_json IS NULL
   OR provenance_json IS NULL;
