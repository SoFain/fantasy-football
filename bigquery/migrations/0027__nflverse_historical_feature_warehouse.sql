-- nflverse historical feature warehouse scaffold.
-- Additive schema-only migration. It creates empty contracts and compatibility views.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_pbp` (
    season INT64,
    week INT64,
    game_id STRING,
    play_id INT64,
    posteam STRING,
    defteam STRING,
    play_type STRING,
    passer_player_id STRING,
    receiver_player_id STRING,
    rusher_player_id STRING,
    epa FLOAT64,
    success FLOAT64,
    cpoe FLOAT64,
    air_yards FLOAT64,
    yards_gained FLOAT64,
    yardline_100 FLOAT64,
    game_seconds_remaining INT64,
    score_differential FLOAT64,
    red_zone_flag BOOL,
    inside_10_flag BOOL,
    inside_5_flag BOOL,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, game_id, posteam, defteam;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_weekly` (
    season INT64,
    week INT64,
    player_id STRING,
    player_name STRING,
    team STRING,
    opponent_team STRING,
    position STRING,
    targets FLOAT64,
    carries FLOAT64,
    air_yards FLOAT64,
    receiving_yards FLOAT64,
    rushing_yards FLOAT64,
    passing_yards FLOAT64,
    receptions FLOAT64,
    receiving_tds FLOAT64,
    rushing_tds FLOAT64,
    passing_tds FLOAT64,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, player_id, team, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_rosters` (
    season INT64,
    player_id STRING,
    gsis_id STRING,
    player_name STRING,
    team STRING,
    position STRING,
    status STRING,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY player_id, gsis_id, team, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_rosters_weekly` (
    season INT64,
    week INT64,
    player_id STRING,
    gsis_id STRING,
    player_name STRING,
    team STRING,
    position STRING,
    status STRING,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, player_id, team, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_players` (
    nflverse_player_id STRING,
    gsis_id STRING,
    sleeper_player_id STRING,
    fantasy_player_id STRING,
    player_name STRING,
    normalized_player_name STRING,
    position STRING,
    latest_team STRING,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
CLUSTER BY nflverse_player_id, gsis_id, sleeper_player_id, normalized_player_name;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_ff_playerids` (
    nflverse_player_id STRING,
    gsis_id STRING,
    sleeper_player_id STRING,
    fantasy_player_id STRING,
    platform STRING,
    platform_player_id STRING,
    player_name STRING,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
CLUSTER BY nflverse_player_id, gsis_id, sleeper_player_id, platform_player_id;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_schedules` (
    season INT64,
    week INT64,
    game_id STRING,
    game_date TIMESTAMP,
    home_team STRING,
    away_team STRING,
    stadium STRING,
    roof STRING,
    surface STRING,
    temp FLOAT64,
    wind FLOAT64,
    total_line FLOAT64,
    spread_line FLOAT64,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, game_id, home_team, away_team;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_teams` (
    team STRING,
    team_name STRING,
    conference STRING,
    division STRING,
    aliases_json STRING,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
CLUSTER BY team;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_team_stats` (
    season INT64,
    week INT64,
    team STRING,
    plays FLOAT64,
    pass_attempts FLOAT64,
    rush_attempts FLOAT64,
    yards FLOAT64,
    turnovers FLOAT64,
    epa_total FLOAT64,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, team;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_injuries` (
    season INT64,
    week INT64,
    team STRING,
    gsis_id STRING,
    player_name STRING,
    position STRING,
    report_status STRING,
    practice_status STRING,
    game_status STRING,
    injury_notes STRING,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, team, gsis_id;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_depth_charts` (
    season INT64,
    week INT64,
    team STRING,
    gsis_id STRING,
    player_name STRING,
    position STRING,
    depth_rank INT64,
    depth_role STRING,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY team, gsis_id, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_snap_counts` (
    season INT64,
    week INT64,
    game_id STRING,
    player_id STRING,
    gsis_id STRING,
    player_name STRING,
    team STRING,
    position STRING,
    offense_snaps FLOAT64,
    offense_pct FLOAT64,
    defense_snaps FLOAT64,
    st_snaps FLOAT64,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, player_id, team, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_participation` (
    season INT64,
    week INT64,
    game_id STRING,
    player_id STRING,
    gsis_id STRING,
    player_name STRING,
    team STRING,
    participation_json STRING,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, game_id, player_id, team;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_ngs_passing` (
    season INT64,
    week INT64,
    player_gsis_id STRING,
    player_name STRING,
    team STRING,
    attempts FLOAT64,
    cpoe FLOAT64,
    avg_time_to_throw FLOAT64,
    avg_air_yards FLOAT64,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, player_gsis_id, team;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_ngs_rushing` (
    season INT64,
    week INT64,
    player_gsis_id STRING,
    player_name STRING,
    team STRING,
    attempts FLOAT64,
    expected_yards FLOAT64,
    rush_yards_over_expected FLOAT64,
    stacked_box_rate FLOAT64,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, player_gsis_id, team;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_ngs_receiving` (
    season INT64,
    week INT64,
    player_gsis_id STRING,
    player_name STRING,
    team STRING,
    targets FLOAT64,
    avg_separation FLOAT64,
    avg_intended_air_yards FLOAT64,
    expected_yac FLOAT64,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, player_gsis_id, team;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_ftn_charting` (
    season INT64,
    week INT64,
    game_id STRING,
    play_id INT64,
    player_id STRING,
    team STRING,
    charting_flags_json STRING,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, game_id, play_id;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_draft_picks` (
    season INT64,
    team STRING,
    player_id STRING,
    player_name STRING,
    position STRING,
    draft_round INT64,
    draft_pick INT64,
    college STRING,
    source_system STRING,
    source_loader STRING,
    source_version STRING,
    source_season INT64,
    source_week INT64,
    source_refresh_id STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING,
    raw_payload_json STRING
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY player_id, team, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.stg_player_identity` (
    player_id_internal STRING,
    nflverse_player_id STRING,
    gsis_id STRING,
    sleeper_player_id STRING,
    fantasy_player_id STRING,
    player_name STRING,
    normalized_player_name STRING,
    position STRING,
    team STRING,
    season INT64,
    week INT64,
    identity_confidence FLOAT64,
    identity_source_json STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    source_refresh_id STRING,
    created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, player_id_internal, team, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.stg_game_context` (
    season INT64,
    week INT64,
    game_id STRING,
    game_date TIMESTAMP,
    home_team STRING,
    away_team STRING,
    stadium STRING,
    roof STRING,
    surface STRING,
    temp FLOAT64,
    wind FLOAT64,
    total_line FLOAT64,
    spread_line FLOAT64,
    source_freshness_json STRING,
    missing_data_flags STRING,
    source_refresh_id STRING,
    created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, game_id, home_team, away_team;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.stg_player_week_stats` (
    season INT64,
    week INT64,
    player_id_internal STRING,
    nflverse_player_id STRING,
    gsis_id STRING,
    player_name STRING,
    position STRING,
    team STRING,
    opponent_team STRING,
    targets FLOAT64,
    carries FLOAT64,
    air_yards FLOAT64,
    receiving_yards FLOAT64,
    rushing_yards FLOAT64,
    passing_yards FLOAT64,
    receptions FLOAT64,
    passing_tds FLOAT64,
    rushing_tds FLOAT64,
    receiving_tds FLOAT64,
    source_freshness_json STRING,
    missing_data_flags STRING,
    source_refresh_id STRING,
    created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, player_id_internal, team, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.stg_team_week_stats` (
    season INT64,
    week INT64,
    team STRING,
    opponent_team STRING,
    plays FLOAT64,
    pass_attempts FLOAT64,
    rush_attempts FLOAT64,
    team_targets FLOAT64,
    team_air_yards FLOAT64,
    epa_total FLOAT64,
    epa_per_play FLOAT64,
    success_rate FLOAT64,
    neutral_pass_rate FLOAT64,
    pass_rate_over_expected FLOAT64,
    red_zone_pass_rate FLOAT64,
    red_zone_rush_rate FLOAT64,
    opponent_epa_allowed FLOAT64,
    opponent_pass_epa_allowed FLOAT64,
    opponent_rush_epa_allowed FLOAT64,
    source_freshness_json STRING,
    missing_data_flags STRING,
    source_refresh_id STRING,
    created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, team, opponent_team;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.stg_play_player_events` (
    season INT64,
    week INT64,
    game_id STRING,
    play_id INT64,
    event_type STRING,
    player_id_internal STRING,
    nflverse_player_id STRING,
    gsis_id STRING,
    team STRING,
    opponent_team STRING,
    posteam STRING,
    defteam STRING,
    yardline_100 FLOAT64,
    game_seconds_remaining INT64,
    score_differential FLOAT64,
    epa FLOAT64,
    success FLOAT64,
    cpoe FLOAT64,
    air_yards FLOAT64,
    yards_gained FLOAT64,
    pass_attempt BOOL,
    rush_attempt BOOL,
    target BOOL,
    reception BOOL,
    touchdown BOOL,
    red_zone_flag BOOL,
    inside_10_flag BOOL,
    inside_5_flag BOOL,
    source_freshness_json STRING,
    missing_data_flags STRING,
    source_refresh_id STRING,
    created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, game_id, player_id_internal, event_type;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.stg_participation_context` (
    season INT64,
    week INT64,
    game_id STRING,
    player_id_internal STRING,
    player_name STRING,
    position STRING,
    team STRING,
    offense_snaps FLOAT64,
    offense_pct FLOAT64,
    defense_snaps FLOAT64,
    st_snaps FLOAT64,
    participation_json STRING,
    has_true_route_source BOOL,
    route_share FLOAT64,
    source_freshness_json STRING,
    missing_data_flags STRING,
    source_refresh_id STRING,
    created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, game_id, player_id_internal, team;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_advanced_metrics` (
    metric_version STRING,
    feature_run_id STRING,
    season INT64,
    week INT64,
    player_id_internal STRING,
    player_name STRING,
    position STRING,
    team STRING,
    opponent_team STRING,
    scoring_profile_id STRING,
    league_type_id STRING,
    roster_format_id STRING,
    targets FLOAT64,
    carries FLOAT64,
    opportunities FLOAT64,
    target_share FLOAT64,
    air_yards_share FLOAT64,
    wopr FLOAT64,
    adot FLOAT64,
    racr FLOAT64,
    weighted_opportunity FLOAT64,
    carry_share FLOAT64,
    opportunity_share FLOAT64,
    red_zone_targets FLOAT64,
    red_zone_carries FLOAT64,
    red_zone_touches FLOAT64,
    inside_10_carries FLOAT64,
    inside_5_carries FLOAT64,
    high_value_touches FLOAT64,
    epa_total FLOAT64,
    epa_per_opportunity FLOAT64,
    success_rate FLOAT64,
    cpoe FLOAT64,
    explosive_rush_rate FLOAT64,
    explosive_reception_rate FLOAT64,
    snap_share FLOAT64,
    injury_status STRING,
    depth_chart_role STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, player_id_internal, scoring_profile_id, position;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.team_week_context_metrics` (
    metric_version STRING,
    feature_run_id STRING,
    season INT64,
    week INT64,
    team STRING,
    opponent_team STRING,
    plays FLOAT64,
    seconds_per_play FLOAT64,
    neutral_pass_rate FLOAT64,
    pass_rate_over_expected FLOAT64,
    team_epa_per_play FLOAT64,
    pass_epa_per_play FLOAT64,
    rush_epa_per_play FLOAT64,
    team_success_rate FLOAT64,
    red_zone_pass_rate FLOAT64,
    red_zone_rush_rate FLOAT64,
    opponent_epa_allowed FLOAT64,
    opponent_pass_epa_allowed FLOAT64,
    opponent_rush_epa_allowed FLOAT64,
    opponent_funnel_label STRING,
    game_environment_json STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, team, opponent_team;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.qb_week_environment_metrics` (
    metric_version STRING,
    feature_run_id STRING,
    season INT64,
    week INT64,
    qb_player_id_internal STRING,
    player_name STRING,
    team STRING,
    opponent_team STRING,
    dropbacks FLOAT64,
    pass_attempts FLOAT64,
    sacks FLOAT64,
    scrambles FLOAT64,
    designed_rushes FLOAT64,
    epa_per_dropback FLOAT64,
    passing_epa FLOAT64,
    cpoe FLOAT64,
    adot FLOAT64,
    deep_attempt_rate FLOAT64,
    sack_rate FLOAT64,
    scramble_rate FLOAT64,
    pass_rate_over_expected_context FLOAT64,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY week, qb_player_id_internal, team;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.pigskin_player_context_packet_current` (
    packet_version STRING,
    feature_run_id STRING,
    as_of_season INT64,
    as_of_week INT64,
    player_id_internal STRING,
    player_name STRING,
    position STRING,
    team STRING,
    scoring_profile_id STRING,
    league_type_id STRING,
    roster_format_id STRING,
    identity_json STRING,
    advanced_metrics_json STRING,
    recent_form_json STRING,
    team_context_json STRING,
    ranking_context_json STRING,
    projection_context_json STRING,
    trade_context_json STRING,
    risk_context_json STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    packet_text STRING,
    packet_json STRING,
    created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(as_of_season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY as_of_week, player_id_internal, scoring_profile_id, position;

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.player_recent_advanced_metrics_current` AS
SELECT
    metric_version,
    feature_run_id,
    season AS as_of_season,
    week AS as_of_week,
    player_id_internal,
    player_name,
    position,
    team,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    TO_JSON_STRING(STRUCT(target_share, air_yards_share, wopr, weighted_opportunity)) AS season_to_date_metrics_json,
    TO_JSON_STRING(STRUCT(target_share, air_yards_share, wopr, weighted_opportunity)) AS last_3_metrics_json,
    TO_JSON_STRING(STRUCT(target_share, air_yards_share, wopr, weighted_opportunity)) AS last_5_metrics_json,
    TO_JSON_STRING(STRUCT(target_share, air_yards_share, wopr, weighted_opportunity)) AS last_8_metrics_json,
    'needs_history' AS trend_label,
    missing_data_flags AS sample_size_flags,
    source_freshness_json,
    missing_data_flags,
    created_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_advanced_metrics`
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY player_id_internal, scoring_profile_id, league_type_id, roster_format_id
    ORDER BY season DESC, week DESC, created_at DESC
) = 1;

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.player_role_usage_metrics_current` AS
SELECT
    metric_version,
    feature_run_id,
    season AS as_of_season,
    week AS as_of_week,
    player_id_internal,
    player_name,
    position,
    team,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    snap_share,
    CAST(NULL AS FLOAT64) AS route_share,
    target_share,
    air_yards_share,
    wopr,
    carry_share,
    opportunity_share,
    TO_JSON_STRING(STRUCT(red_zone_targets, red_zone_carries, red_zone_touches)) AS red_zone_role,
    high_value_touches,
    'needs_history' AS trend_direction,
    CAST(NULL AS FLOAT64) AS role_volatility,
    injury_status AS injury_summary,
    depth_chart_role AS depth_summary,
    source_freshness_json,
    CONCAT(COALESCE(missing_data_flags, '[]'), ';route_share_requires_true_route_source') AS missing_data_flags,
    created_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_advanced_metrics`
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY player_id_internal, scoring_profile_id, league_type_id, roster_format_id
    ORDER BY season DESC, week DESC, created_at DESC
) = 1;

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.compat_pigskin_player_context_current` AS
SELECT
    as_of_season,
    as_of_week,
    player_id_internal,
    player_name,
    position,
    team,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    packet_version,
    feature_run_id,
    packet_text,
    packet_json,
    source_freshness_json,
    missing_data_flags,
    created_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.pigskin_player_context_packet_current`;
