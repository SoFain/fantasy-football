-- Scoring-profile-aware fantasy points foundation.
-- Additive only: creates the output table and enriches default scoring profile seed JSON.
-- This migration does not backfill historical player-week rows.

MERGE `{{PROJECT_ID}}.{{DATASET_ID}}.scoring_profiles` target
USING (
    SELECT
        'standard' AS scoring_profile_id,
        'Standard' AS display_name,
        '{"passing_yards":0.04,"passing_tds":4,"interceptions":-2,"passing_2pt_conversions":2,"rushing_yards":0.1,"rushing_tds":6,"rushing_2pt_conversions":2,"receptions":0,"receiving_yards":0.1,"receiving_tds":6,"receiving_2pt_conversions":2,"fumbles_lost":-2,"return_tds":6,"bonuses":{},"kicker":{},"dst":{}}' AS scoring_json_text
    UNION ALL
    SELECT
        'half_ppr',
        'Half PPR',
        '{"passing_yards":0.04,"passing_tds":4,"interceptions":-2,"passing_2pt_conversions":2,"rushing_yards":0.1,"rushing_tds":6,"rushing_2pt_conversions":2,"receptions":0.5,"receiving_yards":0.1,"receiving_tds":6,"receiving_2pt_conversions":2,"fumbles_lost":-2,"return_tds":6,"bonuses":{},"kicker":{},"dst":{}}'
    UNION ALL
    SELECT
        'ppr',
        'PPR',
        '{"passing_yards":0.04,"passing_tds":4,"interceptions":-2,"passing_2pt_conversions":2,"rushing_yards":0.1,"rushing_tds":6,"rushing_2pt_conversions":2,"receptions":1,"receiving_yards":0.1,"receiving_tds":6,"receiving_2pt_conversions":2,"fumbles_lost":-2,"return_tds":6,"bonuses":{},"kicker":{},"dst":{}}'
) source
ON target.scoring_profile_id = source.scoring_profile_id
WHEN MATCHED AND JSON_VALUE(target.scoring_json, '$.passing_yards') IS NULL THEN
    UPDATE SET
        scoring_json = PARSE_JSON(source.scoring_json_text),
        display_name = source.display_name,
        updated_at = CURRENT_TIMESTAMP(),
        active = TRUE
WHEN NOT MATCHED THEN
    INSERT (
        scoring_profile_id,
        display_name,
        scoring_json,
        created_at,
        updated_at,
        active
    )
    VALUES (
        source.scoring_profile_id,
        source.display_name,
        PARSE_JSON(source.scoring_json_text),
        CURRENT_TIMESTAMP(),
        CURRENT_TIMESTAMP(),
        TRUE
    );

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_fantasy_points_by_profile` (
    player_id_internal STRING,
    source_player_key STRING NOT NULL,
    player_display_name STRING,
    team STRING,
    opponent STRING,
    position STRING,
    season INT64 NOT NULL,
    week INT64 NOT NULL,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING,
    roster_format_id STRING,
    passing_points FLOAT64,
    rushing_points FLOAT64,
    receiving_points FLOAT64,
    reception_points FLOAT64,
    turnover_points FLOAT64,
    bonus_points FLOAT64,
    kicker_points FLOAT64,
    dst_points FLOAT64,
    total_fantasy_points FLOAT64,
    scoring_breakdown_json STRING,
    source_stat_json STRING,
    source_freshness_json STRING,
    missing_data_flags STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))
CLUSTER BY player_id_internal, scoring_profile_id, position, team;
