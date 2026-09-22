-- Phase 32.18 addendum: additive RB weighted-opportunity diagnostic columns.
-- No destructive DDL. No live rankings, champions, or detail backtest rows are modified.

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
ADD COLUMN IF NOT EXISTS red_zone_carries FLOAT64,
ADD COLUMN IF NOT EXISTS outside_red_zone_targets FLOAT64,
ADD COLUMN IF NOT EXISTS outside_red_zone_carries FLOAT64,
ADD COLUMN IF NOT EXISTS gemini31_rb_weighted_opportunity_ppr FLOAT64;
