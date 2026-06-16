-- Production compatibility foundation for Sleeper Watch candidates.
-- Additive migration: creates the backing mart table and replaces the compat view.
-- Data is populated by src/materialize_sleeper_watch.py.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` (
    player_id_internal STRING,
    source_player_key STRING,
    sleeper_player_id STRING,
    display_name STRING,
    normalized_name STRING,
    position STRING,
    fantasy_positions STRING,
    team STRING,
    opponent STRING,
    age FLOAT64,
    active_status STRING,
    season INT64 NOT NULL,
    week INT64 NOT NULL,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    league_id STRING,
    model_run_id STRING,
    ranking_version STRING,
    rostered_rate FLOAT64,
    available_in_league_flag BOOL,
    rostered_in_league_flag BOOL,
    waiver_candidate_flag BOOL,
    starter_candidate_flag BOOL,
    sleeper_trending_add_count INT64,
    sleeper_trending_drop_count INT64,
    market_or_roster_context_json STRING,
    fantasy_points_last_1 FLOAT64,
    fantasy_points_last_3 FLOAT64,
    fantasy_points_last_5 FLOAT64,
    fantasy_points_per_game FLOAT64,
    snap_share_last_3 FLOAT64,
    target_share_last_3 FLOAT64,
    rush_share_last_3 FLOAT64,
    targets_last_3 FLOAT64,
    carries_last_3 FLOAT64,
    receptions_last_3 FLOAT64,
    air_yards_last_3 FLOAT64,
    red_zone_opportunities_last_3 FLOAT64,
    high_value_touches_last_3 FLOAT64,
    usage_trend_score FLOAT64,
    role_growth_score FLOAT64,
    yards_per_target FLOAT64,
    yards_per_carry FLOAT64,
    yards_per_reception FLOAT64,
    catch_rate FLOAT64,
    td_dependency_score FLOAT64,
    expected_vs_actual_signal FLOAT64,
    fraud_risk_score FLOAT64,
    breakout_score FLOAT64,
    game_id STRING,
    game_environment_json STRING,
    opponent_fantasy_points_allowed_proxy FLOAT64,
    matchup_score FLOAT64,
    streamer_score FLOAT64,
    schedule_context_json STRING,
    pigskin_rank_overall INT64,
    pigskin_rank_position INT64,
    pigskin_tier STRING,
    pigskin_projection FLOAT64,
    pigskin_confidence FLOAT64,
    rank_vs_market_gap FLOAT64,
    pigskin_summary STRING,
    candidate_reason STRING,
    evidence_json STRING,
    counterargument STRING,
    snark_hook STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY player_id_internal, position, scoring_profile_id, league_id;

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS player_id_internal STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS source_player_key STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS sleeper_player_id STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS display_name STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS normalized_name STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS fantasy_positions STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS age FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS active_status STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS season INT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS week INT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS scoring_profile_id STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS league_type_id STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS roster_format_id STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS league_id STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS model_run_id STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS ranking_version STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS rostered_rate FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS available_in_league_flag BOOL;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS rostered_in_league_flag BOOL;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS waiver_candidate_flag BOOL;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS starter_candidate_flag BOOL;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS sleeper_trending_add_count INT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS sleeper_trending_drop_count INT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS market_or_roster_context_json STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS fantasy_points_last_1 FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS fantasy_points_last_3 FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS fantasy_points_last_5 FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS fantasy_points_per_game FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS snap_share_last_3 FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS target_share_last_3 FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS rush_share_last_3 FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS targets_last_3 FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS carries_last_3 FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS receptions_last_3 FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS air_yards_last_3 FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS red_zone_opportunities_last_3 FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS high_value_touches_last_3 FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS usage_trend_score FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS role_growth_score FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS yards_per_target FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS yards_per_carry FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS yards_per_reception FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS catch_rate FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS td_dependency_score FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS expected_vs_actual_signal FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS fraud_risk_score FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS breakout_score FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS game_id STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS game_environment_json STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS opponent_fantasy_points_allowed_proxy FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS matchup_score FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS streamer_score FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS schedule_context_json STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS pigskin_rank_overall INT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS pigskin_rank_position INT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS pigskin_tier STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS pigskin_projection FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS pigskin_confidence FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS rank_vs_market_gap FLOAT64;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS pigskin_summary STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS candidate_reason STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS evidence_json STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS counterargument STRING;
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates` ADD COLUMN IF NOT EXISTS snark_hook STRING;

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.compat_sleeper_watch_candidates` AS
SELECT
    player_id_internal,
    source_player_key,
    sleeper_player_id,
    display_name,
    normalized_name,
    position,
    fantasy_positions,
    team,
    opponent,
    age,
    active_status,
    season,
    week,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    league_id,
    model_run_id,
    ranking_version,
    rostered_rate,
    available_in_league_flag,
    rostered_in_league_flag,
    waiver_candidate_flag,
    starter_candidate_flag,
    sleeper_trending_add_count,
    sleeper_trending_drop_count,
    market_or_roster_context_json,
    fantasy_points_last_1,
    fantasy_points_last_3,
    fantasy_points_last_5,
    fantasy_points_per_game,
    snap_share_last_3,
    target_share_last_3,
    rush_share_last_3,
    targets_last_3,
    carries_last_3,
    receptions_last_3,
    air_yards_last_3,
    red_zone_opportunities_last_3,
    high_value_touches_last_3,
    usage_trend_score,
    role_growth_score,
    yards_per_target,
    yards_per_carry,
    yards_per_reception,
    catch_rate,
    td_dependency_score,
    expected_vs_actual_signal,
    fraud_risk_score,
    breakout_score,
    game_id,
    game_environment_json,
    opponent_fantasy_points_allowed_proxy,
    matchup_score,
    streamer_score,
    schedule_context_json,
    pigskin_rank_overall,
    pigskin_rank_position,
    pigskin_tier,
    pigskin_projection,
    pigskin_confidence,
    rank_vs_market_gap,
    pigskin_summary,
    candidate_reason,
    evidence_json,
    counterargument,
    snark_hook,
    source_freshness_json,
    missing_data_flags,
    created_at,
    updated_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.mart_sleeper_watch_candidates`;
