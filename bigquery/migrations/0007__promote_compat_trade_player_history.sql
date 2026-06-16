-- Promote Trade Lab player history compatibility view.
-- This view hides raw weekly_metrics behind curated scoring, identity, and evidence marts.

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_player_history` AS
WITH scoring_rows AS (
    SELECT
        fp.*
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_fantasy_points_by_profile` fp
),
profile_points AS (
    SELECT
        COALESCE(player_id_internal, '') AS player_id_internal_key,
        source_player_key,
        season,
        week,
        MAX(IF(scoring_profile_id = 'standard', total_fantasy_points, NULL)) AS fantasy_points_standard,
        MAX(IF(scoring_profile_id = 'half_ppr', total_fantasy_points, NULL)) AS fantasy_points_half_ppr,
        MAX(IF(scoring_profile_id = 'ppr', total_fantasy_points, NULL)) AS fantasy_points_ppr_profile
    FROM scoring_rows
    GROUP BY player_id_internal_key, source_player_key, season, week
),
identity AS (
    SELECT
        player_id_internal,
        gsis_id,
        sleeper_player_id,
        normalized_name,
        display_name,
        position,
        current_team,
        source_confidence,
        match_method
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_identity_bridge`
),
truth AS (
    SELECT
        player_id,
        player_display_name,
        player_full_name,
        position,
        team,
        current_team,
        opponent_team,
        season,
        week,
        fantasy_points_ppr,
        targets,
        receptions,
        carries,
        target_share,
        carry_share,
        air_yards_share,
        receiving_air_yards,
        red_zone_targets,
        red_zone_carries,
        red_zone_touches,
        offense_pct,
        passing_yards,
        passing_tds,
        rushing_yards,
        rushing_tds,
        receiving_yards,
        receiving_tds,
        passing_epa,
        rushing_epa,
        receiving_epa,
        total_epa,
        primary_qb_name,
        primary_qb_epa_per_target,
        primary_qb_target_share,
        qbs_targeted_by,
        wopr,
        opportunity_score,
        efficiency_score,
        role_quality_score,
        role_fragility_score
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_weekly_truth`
    WHERE season_type = 'REG'
),
rankings AS (
    SELECT *
    FROM (
        SELECT
            player_id,
            sleeper_player_id,
            player_name,
            position,
            current_team,
            model_run_id,
            ranking_version,
            rank AS pigskin_rank_position,
            tier AS pigskin_tier,
            ROW_NUMBER() OVER(
                PARTITION BY COALESCE(player_id, sleeper_player_id, player_name), position
                ORDER BY generated_at DESC, rank ASC
            ) AS rn
        FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings`
        WHERE COALESCE(is_active, TRUE)
    )
    WHERE rn = 1
),
game_environment AS (
    SELECT
        season,
        week,
        game_id,
        home_team,
        away_team,
        stadium,
        roof,
        surface,
        temp_f,
        wind_mph,
        weather_text,
        environment_risk_level,
        fantasy_environment_note
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_game_environment`
)
SELECT
    COALESCE(sr.player_id_internal, id.player_id_internal) AS player_id_internal,
    sr.source_player_key,
    COALESCE(id.display_name, sr.player_display_name, truth.player_full_name, truth.player_display_name) AS player_display_name,
    COALESCE(
        id.normalized_name,
        REGEXP_REPLACE(
            REGEXP_REPLACE(LOWER(COALESCE(sr.player_display_name, truth.player_full_name, truth.player_display_name, '')), r'\s+(jr|sr|ii|iii|iv|v)\.?$', ''),
            r'[^a-z0-9]+',
            ''
        )
    ) AS normalized_name,
    COALESCE(sr.position, truth.position, id.position) AS position,
    COALESCE(sr.team, truth.current_team, truth.team, id.current_team) AS team,
    COALESCE(sr.opponent, truth.opponent_team) AS opponent,
    sr.season,
    sr.week,
    sr.scoring_profile_id,
    sr.total_fantasy_points,
    sr.passing_points,
    sr.rushing_points,
    sr.receiving_points,
    sr.reception_points,
    sr.turnover_points,
    sr.bonus_points,
    profile_points.fantasy_points_ppr_profile AS fantasy_points_ppr,
    profile_points.fantasy_points_half_ppr,
    profile_points.fantasy_points_standard,
    CAST(NULL AS FLOAT64) AS snaps,
    truth.offense_pct AS snap_share,
    truth.targets,
    truth.receptions,
    truth.carries,
    CAST(NULL AS FLOAT64) AS routes_proxy,
    truth.target_share,
    truth.carry_share AS rush_share,
    truth.receiving_air_yards AS air_yards,
    truth.air_yards_share AS air_yard_share,
    truth.red_zone_touches AS red_zone_opportunities,
    COALESCE(truth.receptions, 0) + COALESCE(truth.red_zone_touches, 0) AS high_value_touches,
    truth.passing_yards,
    truth.passing_tds,
    CAST(NULL AS FLOAT64) AS interceptions,
    truth.rushing_yards,
    truth.rushing_tds,
    truth.receiving_yards,
    truth.receiving_tds,
    SAFE_DIVIDE(truth.rushing_yards, NULLIF(truth.carries, 0)) AS yards_per_carry,
    SAFE_DIVIDE(truth.receiving_yards, NULLIF(truth.targets, 0)) AS yards_per_target,
    SAFE_DIVIDE(truth.receiving_yards, NULLIF(truth.receptions, 0)) AS yards_per_reception,
    SAFE_DIVIDE(truth.receptions, NULLIF(truth.targets, 0)) AS catch_rate,
    TO_JSON_STRING(STRUCT(
        truth.passing_epa AS passing_epa,
        truth.rushing_epa AS rushing_epa,
        truth.receiving_epa AS receiving_epa,
        truth.total_epa AS total_epa,
        truth.opportunity_score AS opportunity_score,
        truth.efficiency_score AS efficiency_score,
        truth.role_quality_score AS role_quality_score,
        truth.role_fragility_score AS role_fragility_score,
        truth.wopr AS wopr
    )) AS epa_summary_json,
    TO_JSON_STRING(STRUCT(
        truth.primary_qb_name AS primary_qb_name,
        truth.primary_qb_epa_per_target AS primary_qb_epa_per_target,
        truth.primary_qb_target_share AS primary_qb_target_share,
        truth.qbs_targeted_by AS qbs_targeted_by
    )) AS qb_split_json,
    ge.game_id,
    CASE
        WHEN COALESCE(sr.team, truth.current_team, truth.team) = ge.home_team THEN 'home'
        WHEN COALESCE(sr.team, truth.current_team, truth.team) = ge.away_team THEN 'away'
        ELSE NULL
    END AS home_away,
    TO_JSON_STRING(STRUCT(
        ge.game_id AS game_id,
        ge.stadium AS stadium,
        ge.roof AS roof,
        ge.surface AS surface,
        ge.temp_f AS temp_f,
        ge.wind_mph AS wind_mph,
        ge.weather_text AS weather_text,
        ge.environment_risk_level AS environment_risk_level,
        ge.fantasy_environment_note AS fantasy_environment_note
    )) AS game_environment_json,
    CAST(NULL AS STRING) AS opponent_context_json,
    rankings.model_run_id,
    rankings.ranking_version,
    CAST(NULL AS INT64) AS pigskin_rank_overall,
    rankings.pigskin_rank_position,
    rankings.pigskin_tier,
    ROW_NUMBER() OVER(
        PARTITION BY COALESCE(sr.player_id_internal, id.player_id_internal, sr.source_player_key), sr.scoring_profile_id
        ORDER BY sr.season DESC, sr.week DESC
    ) AS recency_order,
    TO_JSON_STRING(STRUCT(
        'analytics_player_fantasy_points_by_profile' AS scoring_source,
        'analytics_player_weekly_truth' AS evidence_source,
        'player_identity_bridge' AS identity_source,
        'analytics_pigskin_rankings' AS ranking_source,
        'analytics_game_environment' AS environment_source,
        sr.updated_at AS scoring_refreshed_at,
        sr.scoring_profile_id AS scoring_profile_id
    )) AS source_freshness_json,
    TO_JSON_STRING(ARRAY(
        SELECT DISTINCT flag
        FROM UNNEST(ARRAY_CONCAT(
            IF(COALESCE(sr.player_id_internal, id.player_id_internal) IS NULL, ['missing_player_id_internal'], []),
            IF(truth.player_id IS NULL, ['missing_truth_row'], []),
            IF(truth.offense_pct IS NULL, ['missing_snap_share'], []),
            IF(truth.receiving_air_yards IS NULL, ['missing_air_yards'], []),
            IF(truth.red_zone_touches IS NULL, ['missing_red_zone_opportunities'], []),
            IF(ge.game_id IS NULL, ['missing_game_environment'], []),
            IF(rankings.ranking_version IS NULL, ['missing_pigskin_ranking_context'], []),
            IF(sr.missing_data_flags IS NOT NULL AND sr.missing_data_flags != '[]', ['scoring_missing_data_flags_present'], []),
            ['missing_routes_proxy', 'missing_snaps']
        )) AS flag
        WHERE flag IS NOT NULL
        ORDER BY flag
    )) AS missing_data_flags,
    sr.updated_at AS refreshed_at
FROM scoring_rows sr
LEFT JOIN profile_points
    ON COALESCE(sr.player_id_internal, '') = profile_points.player_id_internal_key
    AND sr.source_player_key = profile_points.source_player_key
    AND sr.season = profile_points.season
    AND sr.week = profile_points.week
LEFT JOIN identity id
    ON (sr.player_id_internal IS NOT NULL AND sr.player_id_internal = id.player_id_internal)
    OR (sr.source_player_key IS NOT NULL AND sr.source_player_key = id.gsis_id)
    OR (sr.source_player_key IS NOT NULL AND sr.source_player_key = id.sleeper_player_id)
LEFT JOIN truth
    ON sr.source_player_key = truth.player_id
    AND sr.season = truth.season
    AND sr.week = truth.week
LEFT JOIN rankings
    ON (
        truth.player_id IS NOT NULL
        AND rankings.player_id = truth.player_id
        AND rankings.position = truth.position
    )
    OR (
        id.sleeper_player_id IS NOT NULL
        AND rankings.sleeper_player_id = id.sleeper_player_id
        AND rankings.position = COALESCE(sr.position, truth.position, id.position)
    )
LEFT JOIN game_environment ge
    ON sr.season = ge.season
    AND sr.week = ge.week
    AND (
        (
            COALESCE(sr.team, truth.current_team, truth.team) = ge.home_team
            AND COALESCE(sr.opponent, truth.opponent_team) = ge.away_team
        )
        OR (
            COALESCE(sr.team, truth.current_team, truth.team) = ge.away_team
            AND COALESCE(sr.opponent, truth.opponent_team) = ge.home_team
        )
    );
