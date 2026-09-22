-- Additive injury-context feature columns for ranking research.

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_role_context_metrics`
ADD COLUMN IF NOT EXISTS injury_status_score FLOAT64,
ADD COLUMN IF NOT EXISTS injury_burden_score FLOAT64,
ADD COLUMN IF NOT EXISTS missed_time_risk_score FLOAT64,
ADD COLUMN IF NOT EXISTS availability_score FLOAT64,
ADD COLUMN IF NOT EXISTS injury_context_missing_flags_json STRING,
ADD COLUMN IF NOT EXISTS identity_mapping_method STRING,
ADD COLUMN IF NOT EXISTS identity_mapping_confidence FLOAT64;

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
ADD COLUMN IF NOT EXISTS injury_status_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS injury_burden_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS missed_time_risk_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS availability_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS injury_context_missing_flags_json STRING;
