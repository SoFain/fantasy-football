-- Additive direct nflverse Next Gen Stats metrics for ranking research.

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_ngs_receiving`
ADD COLUMN IF NOT EXISTS position STRING,
ADD COLUMN IF NOT EXISTS avg_cushion FLOAT64,
ADD COLUMN IF NOT EXISTS percent_share_of_intended_air_yards FLOAT64,
ADD COLUMN IF NOT EXISTS receptions INT64,
ADD COLUMN IF NOT EXISTS catch_percentage FLOAT64,
ADD COLUMN IF NOT EXISTS yards FLOAT64,
ADD COLUMN IF NOT EXISTS rec_touchdowns INT64,
ADD COLUMN IF NOT EXISTS avg_yac FLOAT64,
ADD COLUMN IF NOT EXISTS avg_expected_yac FLOAT64,
ADD COLUMN IF NOT EXISTS avg_yac_above_expectation FLOAT64;

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_ngs_rushing`
ADD COLUMN IF NOT EXISTS position STRING,
ADD COLUMN IF NOT EXISTS efficiency FLOAT64,
ADD COLUMN IF NOT EXISTS percent_attempts_gte_eight_defenders FLOAT64,
ADD COLUMN IF NOT EXISTS avg_time_to_los FLOAT64,
ADD COLUMN IF NOT EXISTS rush_attempts INT64,
ADD COLUMN IF NOT EXISTS rush_yards FLOAT64,
ADD COLUMN IF NOT EXISTS avg_rush_yards FLOAT64,
ADD COLUMN IF NOT EXISTS rush_touchdowns INT64,
ADD COLUMN IF NOT EXISTS rush_yards_over_expected_per_att FLOAT64,
ADD COLUMN IF NOT EXISTS rush_pct_over_expected FLOAT64;

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_ngs_passing`
ADD COLUMN IF NOT EXISTS position STRING,
ADD COLUMN IF NOT EXISTS avg_completed_air_yards FLOAT64,
ADD COLUMN IF NOT EXISTS aggressiveness FLOAT64,
ADD COLUMN IF NOT EXISTS expected_completion_percentage FLOAT64,
ADD COLUMN IF NOT EXISTS completion_percentage_above_expectation FLOAT64;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_ngs_metrics` (
  source_version STRING NOT NULL,
  season INT64 NOT NULL,
  week INT64 NOT NULL,
  player_id_internal STRING NOT NULL,
  player_gsis_id STRING,
  player_name STRING,
  position STRING,
  team STRING,
  ngs_avg_cushion FLOAT64,
  ngs_avg_separation FLOAT64,
  ngs_avg_intended_air_yards FLOAT64,
  ngs_catch_percentage FLOAT64,
  ngs_expected_catch_percentage FLOAT64,
  ngs_catch_over_expected FLOAT64,
  ngs_yards_after_catch FLOAT64,
  ngs_expected_yac FLOAT64,
  ngs_yac_over_expected FLOAT64,
  ngs_receiving_efficiency_score FLOAT64,
  ngs_receiving_role_quality_score FLOAT64,
  ngs_efficiency FLOAT64,
  ngs_percent_attempts_gte_8_defenders FLOAT64,
  ngs_avg_time_behind_line FLOAT64,
  ngs_expected_rush_yards FLOAT64,
  ngs_rush_yards_over_expected FLOAT64,
  ngs_rush_yards_over_expected_per_attempt FLOAT64,
  ngs_rush_yards_over_expected_success_rate FLOAT64,
  ngs_rushing_efficiency_score FLOAT64,
  ngs_box_resilience_score FLOAT64,
  ngs_cpoe FLOAT64,
  ngs_avg_time_to_throw FLOAT64,
  ngs_intended_air_yards FLOAT64,
  ngs_aggressiveness FLOAT64,
  ngs_expected_completion_percentage FLOAT64,
  ngs_passing_efficiency_score FLOAT64,
  ngs_missing_flags_json STRING,
  source_provenance_json STRING,
  source_updated_at TIMESTAMP,
  created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2016, 2030, 1))
CLUSTER BY position, player_id_internal;

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
ADD COLUMN IF NOT EXISTS ngs_receiving_efficiency_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS ngs_yac_over_expected_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS ngs_separation_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS ngs_catch_over_expected_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS ngs_rushing_efficiency_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS ngs_rush_yards_over_expected_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS ngs_box_resilience_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS ngs_qb_passing_efficiency_score_3yr FLOAT64,
ADD COLUMN IF NOT EXISTS ngs_missing_flags_json STRING;
