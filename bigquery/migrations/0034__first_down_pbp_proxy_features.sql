-- Phase 32.18: additive first-down PBP proxy feature columns.
-- No destructive DDL. No live rankings, champions, or detail backtest rows are modified.

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_pbp_opportunity_metrics`
ADD COLUMN IF NOT EXISTS receiving_first_down_exp_pbp FLOAT64,
ADD COLUMN IF NOT EXISTS rushing_first_down_exp_pbp FLOAT64,
ADD COLUMN IF NOT EXISTS passing_first_down_exp_pbp FLOAT64,
ADD COLUMN IF NOT EXISTS high_value_first_down_opportunity_score FLOAT64,
ADD COLUMN IF NOT EXISTS receiving_chain_mover_score FLOAT64,
ADD COLUMN IF NOT EXISTS rushing_chain_mover_score FLOAT64;

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
ADD COLUMN IF NOT EXISTS receiving_first_down_exp_pbp_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS rushing_first_down_exp_pbp_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS passing_first_down_exp_pbp_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS high_value_first_down_opportunity_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS receiving_chain_mover_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS rushing_chain_mover_score_3yr FLOAT64;
