from google.cloud import bigquery

from src.load import get_bigquery_project


def get_existing_tables(client, dataset_id):
    rows = client.query(f"""
        SELECT table_name
        FROM `{client.project}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
    """).result()
    return {row.table_name for row in rows}


def build_game_environment_sql(project_id, dataset_id):
    return f"""
    CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.analytics_game_environment`
    PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2000, 2050, 1))
    CLUSTER BY home_team, away_team, roof_category, surface_category AS
    WITH game_rows AS (
        SELECT
            season,
            week,
            game_id,
            ARRAY_AGG(game_date IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS game_date,
            ARRAY_AGG(home_team IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS home_team,
            ARRAY_AGG(away_team IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS away_team,
            ARRAY_AGG(stadium IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS stadium,
            ARRAY_AGG(game_stadium IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS historical_stadium_name,
            ARRAY_AGG(stadium_id IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS stadium_id,
            LOWER(TRIM(ARRAY_AGG(roof IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)])) AS roof,
            LOWER(TRIM(ARRAY_AGG(surface IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)])) AS surface,
            ARRAY_AGG(temp IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS temp_f,
            ARRAY_AGG(wind IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS wind_mph,
            ARRAY_AGG(weather IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS weather_text
        FROM `{project_id}.{dataset_id}.play_by_play`
        WHERE season_type = 'REG'
        GROUP BY season, week, game_id
    ),
    classified AS (
        SELECT
            *,
            CASE
                WHEN roof IN ('dome', 'closed') THEN TRUE
                WHEN roof IN ('open', 'outdoors', 'outdoor') THEN FALSE
                ELSE NULL
            END AS is_indoor_or_closed,
            CASE
                WHEN roof = 'dome' THEN 'dome'
                WHEN roof = 'closed' THEN 'closed_roof'
                WHEN roof = 'open' THEN 'open_roof'
                WHEN roof IN ('outdoors', 'outdoor') THEN 'outdoors'
                ELSE 'unknown_roof'
            END AS roof_category,
            CASE
                WHEN surface LIKE '%grass%' THEN 'grass'
                WHEN surface LIKE '%turf%'
                    OR surface LIKE '%fieldturf%'
                    OR surface LIKE '%sportturf%'
                    OR surface LIKE '%matrixturf%'
                    OR surface LIKE '%a_turf%'
                    OR surface LIKE '%astro%' THEN 'synthetic'
                WHEN surface IS NULL OR surface = '' THEN 'unknown_surface'
                ELSE 'other_surface'
            END AS surface_category,
            REGEXP_CONTAINS(LOWER(COALESCE(weather_text, '')), r'\\b(rain|snow|sleet|freezing|storm|thunder)\\b') AS precipitation_or_storm_flag,
            REGEXP_CONTAINS(LOWER(COALESCE(weather_text, '')), r'\\bsnow\\b|freezing') AS snow_or_freezing_flag
        FROM game_rows
    )
    SELECT
        *,
        CASE
            WHEN is_indoor_or_closed THEN 'controlled_indoor'
            WHEN temp_f IS NULL THEN 'unknown_temp'
            WHEN temp_f < 32 THEN 'freezing'
            WHEN temp_f < 45 THEN 'cold'
            WHEN temp_f > 85 THEN 'hot'
            ELSE 'moderate'
        END AS temperature_bucket,
        CASE
            WHEN is_indoor_or_closed THEN 'controlled_indoor'
            WHEN wind_mph IS NULL THEN 'unknown_wind'
            WHEN wind_mph >= 20 THEN 'severe_wind'
            WHEN wind_mph >= 15 THEN 'high_wind'
            WHEN wind_mph >= 10 THEN 'moderate_wind'
            ELSE 'calm_low_wind'
        END AS wind_bucket,
        CASE
            WHEN is_indoor_or_closed THEN 'low'
            WHEN wind_mph >= 20 OR snow_or_freezing_flag THEN 'high'
            WHEN wind_mph >= 15 OR precipitation_or_storm_flag OR temp_f < 32 THEN 'medium'
            ELSE 'low'
        END AS environment_risk_level,
        CASE
            WHEN is_indoor_or_closed THEN 'Indoor or closed-roof environment. Weather should not materially change projection unless field surface or unusual venue context matters.'
            WHEN wind_mph >= 20 THEN 'Severe wind environment. Downgrade deep passing, long field goals, and fragile pass volume assumptions.'
            WHEN wind_mph >= 15 THEN 'High wind environment. Treat downfield passing efficiency and kicker projections with caution.'
            WHEN snow_or_freezing_flag THEN 'Snow or freezing condition signal. Recheck current forecast and consider offensive efficiency downside.'
            WHEN precipitation_or_storm_flag THEN 'Precipitation signal. Recheck current forecast and consider ball-security and efficiency downside.'
            WHEN temp_f > 85 THEN 'Hot outdoor environment. Watch pace, fatigue, and humidity context.'
            ELSE 'No major environment penalty from historical game conditions.'
        END AS fantasy_environment_note
    FROM classified
    """


def build_player_weekly_truth_sql(project_id, dataset_id, existing_tables):
    has_snap_counts = "weekly_snap_counts" in existing_tables
    has_ngs_receiving = "ngs_receiving" in existing_tables
    has_injuries = "injury_reports" in existing_tables
    has_news = "realtime_player_news" in existing_tables
    has_player_rosters = "player_rosters" in existing_tables
    has_qb_weekly = "analytics_player_qb_weekly" in existing_tables

    snap_counts_cte = f"""
    snap_counts AS (
        SELECT
            season,
            week,
            player AS player_name,
            team,
            SUM(offense_snaps) AS offense_snaps,
            AVG(offense_pct) AS offense_pct
        FROM `{project_id}.{dataset_id}.weekly_snap_counts`
        GROUP BY season, week, player_name, team
    )
    """ if has_snap_counts else """
    snap_counts AS (
        SELECT
            CAST(NULL AS INT64) AS season,
            CAST(NULL AS INT64) AS week,
            CAST(NULL AS STRING) AS player_name,
            CAST(NULL AS STRING) AS team,
            CAST(NULL AS FLOAT64) AS offense_snaps,
            CAST(NULL AS FLOAT64) AS offense_pct
        FROM UNNEST([])
        WHERE FALSE
    )
    """

    ngs_receiving_cte = f"""
    ngs_receiving AS (
        SELECT
            season,
            week,
            player_display_name AS player_name,
            team_abbr AS team,
            AVG(avg_cushion) AS avg_cushion,
            AVG(avg_separation) AS avg_separation,
            AVG(avg_yac_above_expectation) AS avg_yac_above_expectation
        FROM `{project_id}.{dataset_id}.ngs_receiving`
        GROUP BY season, week, player_name, team
    )
    """ if has_ngs_receiving else """
    ngs_receiving AS (
        SELECT
            CAST(NULL AS INT64) AS season,
            CAST(NULL AS INT64) AS week,
            CAST(NULL AS STRING) AS player_name,
            CAST(NULL AS STRING) AS team,
            CAST(NULL AS FLOAT64) AS avg_cushion,
            CAST(NULL AS FLOAT64) AS avg_separation,
            CAST(NULL AS FLOAT64) AS avg_yac_above_expectation
        FROM UNNEST([])
        WHERE FALSE
    )
    """

    injuries_cte = f"""
    injuries AS (
        SELECT
            season,
            week,
            full_name AS player_name,
            team,
            MAX(report_status) AS injury_status,
            MAX(report_primary_injury) AS primary_injury
        FROM `{project_id}.{dataset_id}.injury_reports`
        GROUP BY season, week, player_name, team
    )
    """ if has_injuries else """
    injuries AS (
        SELECT
            CAST(NULL AS INT64) AS season,
            CAST(NULL AS INT64) AS week,
            CAST(NULL AS STRING) AS player_name,
            CAST(NULL AS STRING) AS team,
            CAST(NULL AS STRING) AS injury_status,
            CAST(NULL AS STRING) AS primary_injury
        FROM UNNEST([])
        WHERE FALSE
    )
    """

    news_cte = f"""
    sleeper_trends AS (
        SELECT
            player_name,
            team,
            SUM(IF(trend_type = 'ADD', trend_count, 0)) AS sleeper_add_count,
            SUM(IF(trend_type = 'DROP', trend_count, 0)) AS sleeper_drop_count
        FROM `{project_id}.{dataset_id}.realtime_player_news`
        GROUP BY player_name, team
    )
    """ if has_news else """
    sleeper_trends AS (
        SELECT
            CAST(NULL AS STRING) AS player_name,
            CAST(NULL AS STRING) AS team,
            CAST(NULL AS INT64) AS sleeper_add_count,
            CAST(NULL AS INT64) AS sleeper_drop_count
        FROM UNNEST([])
        WHERE FALSE
    )
    """

    current_rosters_cte = f"""
    current_rosters AS (
        SELECT
            gsis_id AS player_id,
            ARRAY_AGG(display_name IGNORE NULLS ORDER BY season DESC LIMIT 1)[SAFE_OFFSET(0)] AS player_full_name,
            ARRAY_AGG(latest_team IGNORE NULLS ORDER BY season DESC LIMIT 1)[SAFE_OFFSET(0)] AS current_team,
            ARRAY_AGG(status IGNORE NULLS ORDER BY season DESC LIMIT 1)[SAFE_OFFSET(0)] AS roster_status,
            ARRAY_AGG(espn_id IGNORE NULLS ORDER BY season DESC LIMIT 1)[SAFE_OFFSET(0)] AS espn_id
        FROM `{project_id}.{dataset_id}.player_rosters`
        WHERE gsis_id IS NOT NULL
        GROUP BY player_id
    )
    """ if has_player_rosters else """
    current_rosters AS (
        SELECT
            CAST(NULL AS STRING) AS player_id,
            CAST(NULL AS STRING) AS player_full_name,
            CAST(NULL AS STRING) AS current_team,
            CAST(NULL AS STRING) AS roster_status,
            CAST(NULL AS STRING) AS espn_id
        FROM UNNEST([])
        WHERE FALSE
    )
    """

    qb_week_context_cte = f"""
    qb_week_context AS (
        SELECT
            season,
            week,
            player_id,
            ARRAY_AGG(qb_name ORDER BY targets DESC LIMIT 1)[SAFE_OFFSET(0)] AS primary_qb_name,
            ARRAY_AGG(qb_id ORDER BY targets DESC LIMIT 1)[SAFE_OFFSET(0)] AS primary_qb_id,
            ARRAY_AGG(targets ORDER BY targets DESC LIMIT 1)[SAFE_OFFSET(0)] AS primary_qb_targets,
            ARRAY_AGG(epa_per_target ORDER BY targets DESC LIMIT 1)[SAFE_OFFSET(0)] AS primary_qb_epa_per_target,
            ARRAY_AGG(target_share_from_qb ORDER BY targets DESC LIMIT 1)[SAFE_OFFSET(0)] AS primary_qb_target_share,
            STRING_AGG(qb_name, ', ' ORDER BY targets DESC) AS qbs_targeted_by
        FROM `{project_id}.{dataset_id}.analytics_player_qb_weekly`
        GROUP BY season, week, player_id
    )
    """ if has_qb_weekly else """
    qb_week_context AS (
        SELECT
            CAST(NULL AS INT64) AS season,
            CAST(NULL AS INT64) AS week,
            CAST(NULL AS STRING) AS player_id,
            CAST(NULL AS STRING) AS primary_qb_name,
            CAST(NULL AS STRING) AS primary_qb_id,
            CAST(NULL AS INT64) AS primary_qb_targets,
            CAST(NULL AS FLOAT64) AS primary_qb_epa_per_target,
            CAST(NULL AS FLOAT64) AS primary_qb_target_share,
            CAST(NULL AS STRING) AS qbs_targeted_by
        FROM UNNEST([])
        WHERE FALSE
    )
    """

    return f"""
    CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.analytics_player_weekly_truth`
    PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2000, 2050, 1))
    CLUSTER BY position, team, player_name AS
    WITH
    weekly_source AS (
        SELECT DISTINCT *
        FROM `{project_id}.{dataset_id}.weekly_metrics`
        WHERE season_type = 'REG'
    ),
    play_by_play_source AS (
        SELECT DISTINCT
            season,
            week,
            posteam,
            yardline_100,
            pass_attempt,
            rush_attempt,
            receiver_player_name,
            rusher_player_name
        FROM `{project_id}.{dataset_id}.play_by_play`
    ),
    weekly AS (
        SELECT
            season,
            week,
            player_id,
            player_name,
            player_display_name,
            position,
            position_group,
            team,
            opponent_team,
            season_type,
            SUM(COALESCE(fantasy_points, 0)) AS fantasy_points,
            SUM(COALESCE(fantasy_points_ppr, 0)) AS fantasy_points_ppr,
            SUM(COALESCE(targets, 0)) AS targets,
            SUM(COALESCE(receptions, 0)) AS receptions,
            SUM(COALESCE(receiving_yards, 0)) AS receiving_yards,
            SUM(COALESCE(receiving_tds, 0)) AS receiving_tds,
            SUM(COALESCE(receiving_air_yards, 0)) AS receiving_air_yards,
            SUM(COALESCE(carries, 0)) AS carries,
            SUM(COALESCE(rushing_yards, 0)) AS rushing_yards,
            SUM(COALESCE(rushing_tds, 0)) AS rushing_tds,
            SUM(COALESCE(attempts, 0)) AS pass_attempts,
            SUM(COALESCE(passing_yards, 0)) AS passing_yards,
            SUM(COALESCE(passing_tds, 0)) AS passing_tds,
            AVG(target_share) AS target_share,
            AVG(air_yards_share) AS air_yards_share,
            AVG(wopr) AS wopr,
            SUM(COALESCE(passing_epa, 0)) AS passing_epa,
            SUM(COALESCE(rushing_epa, 0)) AS rushing_epa,
            SUM(COALESCE(receiving_epa, 0)) AS receiving_epa,
            SUM(
                COALESCE(passing_epa, 0)
                + COALESCE(rushing_epa, 0)
                + COALESCE(receiving_epa, 0)
            ) AS total_epa,
            SUM(SUM(COALESCE(carries, 0))) OVER(PARTITION BY season, week, team) AS team_carries,
            SUM(SUM(COALESCE(attempts, 0))) OVER(PARTITION BY season, week, team) AS team_pass_attempts,
            SAFE_DIVIDE(SUM(COALESCE(carries, 0)), SUM(SUM(COALESCE(carries, 0))) OVER(PARTITION BY season, week, team)) AS carry_share,
            CASE 
                WHEN position = 'QB' THEN SAFE_DIVIDE(SUM(COALESCE(carries, 0)), NULLIF(SUM(COALESCE(carries, 0)) + SUM(COALESCE(attempts, 0)), 0))
                ELSE SAFE_DIVIDE(SUM(COALESCE(carries, 0)), NULLIF(SUM(COALESCE(carries, 0)) + SUM(COALESCE(targets, 0)), 0))
            END AS player_run_opportunity_pct,
            CASE 
                WHEN position = 'QB' THEN SAFE_DIVIDE(SUM(COALESCE(attempts, 0)), NULLIF(SUM(COALESCE(carries, 0)) + SUM(COALESCE(attempts, 0)), 0))
                ELSE SAFE_DIVIDE(SUM(COALESCE(targets, 0)), NULLIF(SUM(COALESCE(carries, 0)) + SUM(COALESCE(targets, 0)), 0))
            END AS player_pass_opportunity_pct
        FROM weekly_source
        GROUP BY
            season,
            week,
            player_id,
            player_name,
            player_display_name,
            position,
            position_group,
            team,
            opponent_team,
            season_type
    ),
    red_zone AS (
        SELECT
            season,
            week,
            player_name,
            team,
            SUM(red_zone_targets) AS red_zone_targets,
            SUM(red_zone_carries) AS red_zone_carries,
            SUM(red_zone_touches) AS red_zone_touches
        FROM (
            SELECT
                season,
                week,
                receiver_player_name AS player_name,
                posteam AS team,
                COUNT(1) AS red_zone_targets,
                0 AS red_zone_carries,
                COUNT(1) AS red_zone_touches
            FROM play_by_play_source
            WHERE yardline_100 <= 20
                AND receiver_player_name IS NOT NULL
                AND pass_attempt = 1
            GROUP BY season, week, player_name, team

            UNION ALL

            SELECT
                season,
                week,
                rusher_player_name AS player_name,
                posteam AS team,
                0 AS red_zone_targets,
                COUNT(1) AS red_zone_carries,
                COUNT(1) AS red_zone_touches
            FROM play_by_play_source
            WHERE yardline_100 <= 20
                AND rusher_player_name IS NOT NULL
                AND rush_attempt = 1
            GROUP BY season, week, player_name, team
        )
        GROUP BY season, week, player_name, team
    ),
    {snap_counts_cte},
    {ngs_receiving_cte},
    {injuries_cte},
    {news_cte},
    {current_rosters_cte},
    {qb_week_context_cte},
    joined AS (
        SELECT
            w.*,
            COALESCE(cr.player_full_name, w.player_display_name, w.player_name) AS player_full_name,
            COALESCE(cr.current_team, w.team) AS current_team,
            cr.roster_status,
            cr.espn_id,
            COALESCE(cr.current_team, w.team) != w.team AS team_changed_since_stats,
            qbc.primary_qb_name,
            qbc.primary_qb_id,
            qbc.primary_qb_targets,
            qbc.primary_qb_epa_per_target,
            qbc.primary_qb_target_share,
            qbc.qbs_targeted_by,
            COALESCE(r.red_zone_targets, 0) AS red_zone_targets,
            COALESCE(r.red_zone_carries, 0) AS red_zone_carries,
            COALESCE(r.red_zone_touches, 0) AS red_zone_touches,
            s.offense_snaps,
            s.offense_pct,
            n.avg_cushion,
            n.avg_separation,
            n.avg_yac_above_expectation,
            i.injury_status,
            i.primary_injury,
            COALESCE(t.sleeper_add_count, 0) AS sleeper_add_count,
            COALESCE(t.sleeper_drop_count, 0) AS sleeper_drop_count,
            COALESCE(w.targets, 0) + COALESCE(w.carries, 0) AS skill_player_opportunities,
            COALESCE(w.receiving_tds, 0) + COALESCE(w.rushing_tds, 0) + COALESCE(w.passing_tds, 0) AS touchdowns,
            SAFE_DIVIDE(w.fantasy_points_ppr, NULLIF(COALESCE(w.targets, 0) + COALESCE(w.carries, 0), 0)) AS fantasy_points_per_opportunity,
            SAFE_DIVIDE(w.total_epa, NULLIF(COALESCE(w.pass_attempts, 0) + COALESCE(w.targets, 0) + COALESCE(w.carries, 0), 0)) AS epa_per_opportunity
        FROM weekly w
        LEFT JOIN red_zone r
            ON w.season = r.season
            AND w.week = r.week
            AND LOWER(w.player_name) = LOWER(r.player_name)
            AND w.team = r.team
        LEFT JOIN snap_counts s
            ON w.season = s.season
            AND w.week = s.week
            AND LOWER(w.player_display_name) = LOWER(s.player_name)
            AND w.team = s.team
        LEFT JOIN ngs_receiving n
            ON w.season = n.season
            AND w.week = n.week
            AND LOWER(w.player_display_name) = LOWER(n.player_name)
            AND w.team = n.team
        LEFT JOIN injuries i
            ON w.season = i.season
            AND w.week = i.week
            AND LOWER(w.player_display_name) = LOWER(i.player_name)
            AND w.team = i.team
        LEFT JOIN sleeper_trends t
            ON LOWER(w.player_display_name) = LOWER(t.player_name)
            AND w.team = t.team
        LEFT JOIN current_rosters cr
            ON w.player_id = cr.player_id
        LEFT JOIN qb_week_context qbc
            ON w.season = qbc.season
            AND w.week = qbc.week
            AND w.player_id = qbc.player_id
    ),
    scored AS (
        SELECT
            *,
            LAG(fantasy_points_ppr) OVER player_weeks AS prior_week_ppr,
            fantasy_points_ppr - LAG(fantasy_points_ppr) OVER player_weeks AS ppr_delta,
            AVG(fantasy_points_ppr) OVER recent_player_weeks AS rolling_3_week_ppr,
            AVG(targets) OVER recent_player_weeks AS rolling_3_week_targets,
            AVG(carries) OVER recent_player_weeks AS rolling_3_week_carries,
            AVG(skill_player_opportunities) OVER recent_player_weeks AS rolling_3_week_opportunities,
            ROUND(
                COALESCE(target_share, 0) * 35
                + COALESCE(air_yards_share, 0) * 20
                + COALESCE(wopr, 0) * 12
                + LEAST(COALESCE(targets, 0) * 1.6, 18)
                + LEAST(COALESCE(carries, 0) * 1.1, 16)
                + LEAST(COALESCE(red_zone_touches, 0) * 4, 16)
                + COALESCE(offense_pct, 0) * 12,
                2
            ) AS opportunity_score,
            LEAST(
                GREATEST(
                    ROUND(
                        COALESCE(epa_per_opportunity, 0) * 8
                        + COALESCE(fantasy_points_per_opportunity, 0) * 2
                        + COALESCE(avg_yac_above_expectation, 0),
                        2
                    ),
                    -20
                ),
                35
            ) AS efficiency_score,
            SAFE_DIVIDE(touchdowns * 6, NULLIF(fantasy_points_ppr, 0)) AS touchdown_dependency_rate
        FROM joined
        WINDOW
            player_weeks AS (
                PARTITION BY player_id, season
                ORDER BY week
            ),
            recent_player_weeks AS (
                PARTITION BY player_id, season
                ORDER BY week
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            )
    ),
    truth AS (
        SELECT
            *,
            ROUND(opportunity_score + efficiency_score, 2) AS analytical_grade,
            ROUND(
                COALESCE(opportunity_score, 0)
                + LEAST(COALESCE(rolling_3_week_opportunities, 0) * 1.2, 18)
                + COALESCE(offense_pct, 0) * 10,
                2
            ) AS role_quality_score,
            ROUND(fantasy_points_ppr - SAFE_DIVIDE(opportunity_score, 3.5), 2) AS points_over_role_score,
            LEAST(
                GREATEST(
                    ROUND(
                        IF(fantasy_points_ppr >= 14, 10, 0)
                        + IF(skill_player_opportunities < 8, 20, 0)
                        + IF(skill_player_opportunities < 10 AND COALESCE(rolling_3_week_opportunities, 0) < 10, 15, 0)
                        + IF(touchdown_dependency_rate >= 0.45 AND touchdowns > 0, 25, 0)
                        + IF(fantasy_points_per_opportunity >= 2.5 AND skill_player_opportunities < 10, 15, 0)
                        + IF(offense_pct IS NOT NULL AND offense_pct < 0.65, 10, 0)
                        + IF(position IN ('WR', 'TE') AND COALESCE(target_share, 0) < 0.18, 10, 0)
                        + IF(position IN ('WR', 'TE') AND COALESCE(wopr, 0) < 0.45, 8, 0)
                        - IF(target_share >= 0.22 OR wopr >= 0.55, 15, 0)
                        - IF(skill_player_opportunities >= 12, 15, 0)
                        - IF(red_zone_touches >= 3, 5, 0),
                        2
                    ),
                    0
                ),
                100
            ) AS role_fragility_score
        FROM scored
    )
    SELECT
        *,
        touchdown_dependency_rate >= 0.45 AND touchdowns > 0 AS touchdown_dependent,
        role_fragility_score >= 55
            AND fantasy_points_ppr >= 12 AS box_score_trap,
        target_share >= 0.22 OR wopr >= 0.55 AS target_earner,
        skill_player_opportunities >= 12
            AND fantasy_points_ppr < 10 AS empty_volume,
        skill_player_opportunities < 8
            AND fantasy_points_ppr >= 12 AS usage_warning,
        fantasy_points_ppr >= 14
            AND points_over_role_score >= 8
            AND role_fragility_score >= 45 AS points_outran_role,
        fantasy_points_ppr >= 12
            AND skill_player_opportunities < 8 AS thin_role_big_week,
        role_fragility_score >= 55 AS fragile_role,
        fantasy_points_ppr >= 14
            AND role_quality_score >= 45
            AND role_fragility_score < 35 AS role_backed_production,
        CASE
            WHEN fantasy_points_ppr >= 18
                AND role_fragility_score >= 55
                THEN 'Box-score trap: points beat role'
            WHEN fantasy_points_ppr >= 14
                AND touchdown_dependency_rate >= 0.45
                AND touchdowns > 0
                THEN 'Touchdown-dependent spike'
            WHEN fantasy_points_ppr >= 12
                AND skill_player_opportunities < 8
                THEN 'Thin role, loud box score'
            WHEN skill_player_opportunities >= 14
                AND fantasy_points_ppr < 10
                THEN 'Volume survived, box score failed'
            WHEN target_share >= 0.25
                OR wopr >= 0.65
                THEN 'Earned target profile'
            WHEN red_zone_touches >= 3
                AND fantasy_points_ppr < 12
                THEN 'Role is better than the result'
            WHEN skill_player_opportunities < 6
                AND fantasy_points_ppr < 8
                THEN 'Thin role, no excuse'
            ELSE 'Needs context'
        END AS analytical_verdict
    FROM truth
    """


def build_fraud_watch_sql(project_id, dataset_id):
    return f"""
    CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.analytics_fraud_watch`
    PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2000, 2050, 1))
    CLUSTER BY fraud_label, position, player_name AS
    WITH candidates AS (
        SELECT
            season,
            week,
            player_id,
            player_name,
            player_display_name,
            position,
            team,
            current_team,
            opponent_team,
            fantasy_points_ppr,
            targets,
            receptions,
            carries,
            target_share,
            air_yards_share,
            wopr,
            offense_snaps,
            offense_pct,
            red_zone_touches,
            touchdowns,
            skill_player_opportunities,
            rolling_3_week_opportunities,
            fantasy_points_per_opportunity,
            opportunity_score,
            role_quality_score,
            points_over_role_score,
            role_fragility_score,
            touchdown_dependency_rate,
            total_epa,
            analytical_grade,
            analytical_verdict,
            primary_qb_name,
            primary_qb_epa_per_target,
            qbs_targeted_by,
            injury_status,
            primary_injury,
            sleeper_add_count,
            sleeper_drop_count,
            thin_role_big_week,
            points_outran_role,
            role_backed_production,
            ROUND(
                role_fragility_score
                + IF(points_outran_role, 15, 0)
                + IF(thin_role_big_week, 15, 0)
                + IF(touchdown_dependency_rate >= 0.45 AND touchdowns > 0, 15, 0)
                + IF(fantasy_points_per_opportunity >= 2.5 AND skill_player_opportunities < 10, 10, 0)
                - IF(role_backed_production, 35, 0),
                2
            ) AS fraud_score
        FROM `{project_id}.{dataset_id}.analytics_player_weekly_truth`
        WHERE position IN ('QB', 'RB', 'WR', 'TE')
            AND season_type = 'REG'
            AND fantasy_points_ppr >= 8
    )
    SELECT
        *,
        CASE
            WHEN role_backed_production THEN 'Not fraud: role backed it up'
            WHEN touchdown_dependency_rate >= 0.45
                AND touchdowns > 0
                AND skill_player_opportunities < 12
                THEN 'TD merchant'
            WHEN thin_role_big_week THEN 'Thin role, loud box score'
            WHEN offense_pct IS NOT NULL
                AND offense_pct < 0.65
                AND fantasy_points_ppr >= 12
                THEN 'Snap-count fraud watch'
            WHEN points_outran_role THEN 'Points outran role'
            WHEN role_fragility_score >= 55 THEN 'Fragile role'
            ELSE 'Monitor only'
        END AS fraud_label,
        CASE
            WHEN role_backed_production
                THEN 'The production has enough role support. Do not force a fraud take just because the points were high.'
            WHEN touchdown_dependency_rate >= 0.45
                AND touchdowns > 0
                AND skill_player_opportunities < 12
                THEN 'The fantasy week leaned too hard on touchdown points without a sturdy weekly workload.'
            WHEN thin_role_big_week
                THEN 'The box score was louder than the actual touch or target base.'
            WHEN offense_pct IS NOT NULL
                AND offense_pct < 0.65
                AND fantasy_points_ppr >= 12
                THEN 'Useful points came from a player who was not living on the field enough to trust blindly.'
            WHEN points_outran_role
                THEN 'The scoring result materially beat the role score. Treat it as repeatability risk until usage confirms it.'
            WHEN role_fragility_score >= 55
                THEN 'The role profile is fragile enough that the next ranking bump needs proof, not vibes.'
            ELSE 'The profile is not clean enough to trust or loud enough to roast without more context.'
        END AS fraud_case,
        CASE
            WHEN position IN ('WR', 'TE')
                THEN 'Rising target share, WOPR, routes or snap share would make the box score more believable.'
            WHEN position = 'RB'
                THEN 'A stable carry base, pass-game role, and goal-line work would make the production more repeatable.'
            WHEN position = 'QB'
                THEN 'Repeatable rushing volume, pass volume, and EPA would separate signal from one-week noise.'
            ELSE 'Better weekly role evidence would soften the fraud read.'
        END AS what_would_change_mind
    FROM candidates
    WHERE fraud_score >= 25
    """


def build_pigskin_rankings_sql(project_id, dataset_id):
    return f"""
    CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.analytics_pigskin_rankings_candidates`
    PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2020, 2050, 1))
    CLUSTER BY position, rank, player_name AS
    WITH run_context AS (
        SELECT
            CURRENT_TIMESTAMP() AS generated_at,
            EXTRACT(YEAR FROM CURRENT_DATE()) AS season,
            CONCAT('pigskin-', FORMAT_TIMESTAMP('%Y%m%d%H%M%S', CURRENT_TIMESTAMP())) AS ranking_version
    ),
    latest_roster_season AS (
        SELECT MAX(season) AS max_season
        FROM `{project_id}.{dataset_id}.player_rosters`
    ),
    sleeper_latest_snapshot AS (
        SELECT MAX(snapshot_at) AS max_snapshot_at
        FROM `{project_id}.{dataset_id}.sleeper_players_current`
    ),
    sleeper_current AS (
        SELECT * EXCEPT(rn)
        FROM (
            SELECT
                sp.*,
                LOWER(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(LOWER(sp.player_name), r'\s+(jr|sr|ii|iii|iv|v)\.?$', ''),
                        r'[^a-z0-9]+',
                        ''
                    )
                ) AS player_name_key,
                ROW_NUMBER() OVER(
                    PARTITION BY sp.sleeper_player_id
                    ORDER BY sp.snapshot_at DESC, COALESCE(sp.search_rank, 999999)
                ) AS rn
            FROM `{project_id}.{dataset_id}.sleeper_players_current` sp
            JOIN sleeper_latest_snapshot sls
                ON sp.snapshot_at = sls.max_snapshot_at
            WHERE sp.position IN ('QB', 'RB', 'WR', 'TE')
                AND sp.active IS TRUE
                AND sp.team IS NOT NULL
                AND (sp.status IS NULL OR sp.status IN ('Active', 'ACT'))
                AND REGEXP_CONTAINS(COALESCE(sp.fantasy_positions_json, ''), CONCAT('"', sp.position, '"'))
        )
        WHERE rn = 1
    ),
    roster_players_raw AS (
        SELECT
            r.gsis_id AS player_id,
            ARRAY_AGG(r.display_name IGNORE NULLS ORDER BY r.season DESC LIMIT 1)[SAFE_OFFSET(0)] AS player_name,
            ARRAY_AGG(r.position IGNORE NULLS ORDER BY r.season DESC LIMIT 1)[SAFE_OFFSET(0)] AS position,
            ARRAY_AGG(r.latest_team IGNORE NULLS ORDER BY r.season DESC LIMIT 1)[SAFE_OFFSET(0)] AS current_team,
            ARRAY_AGG(r.status IGNORE NULLS ORDER BY r.season DESC LIMIT 1)[SAFE_OFFSET(0)] AS roster_status
        FROM `{project_id}.{dataset_id}.player_rosters` r, latest_roster_season lrs
        WHERE r.season = lrs.max_season
            AND r.gsis_id IS NOT NULL
            AND r.position IN ('QB', 'RB', 'WR', 'TE')
            AND (r.status IS NULL OR r.status IN ('ACT', 'RES', 'PUP', 'SUS', 'NWT', 'INA'))
        GROUP BY r.gsis_id
    ),
    roster_players AS (
        SELECT
            *,
            LOWER(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(LOWER(player_name), r'\s+(jr|sr|ii|iii|iv|v)\.?$', ''),
                    r'[^a-z0-9]+',
                    ''
                )
            ) AS player_name_key
        FROM roster_players_raw
    ),
    active_roster_players AS (
        SELECT
            COALESCE(rp.player_id, sc.gsis_id, sc.sleeper_player_id) AS player_id,
            sc.sleeper_player_id,
            COALESCE(rp.player_name, sc.player_name) AS player_name,
            sc.position,
            sc.team AS current_team,
            rp.roster_status,
            sc.team AS sleeper_team,
            sc.active AS sleeper_active,
            sc.status AS sleeper_status,
            sc.injury_status AS sleeper_injury_status,
            sc.depth_chart_position AS sleeper_depth_chart_position,
            sc.depth_chart_order AS sleeper_depth_chart_order,
            sc.search_rank AS sleeper_search_rank,
            'eligible_current_sleeper_player' AS ranking_eligibility
        FROM sleeper_current sc
        LEFT JOIN roster_players rp
            ON (
                sc.gsis_id IS NOT NULL
                AND sc.gsis_id = rp.player_id
            )
            OR (
                sc.player_name_key = rp.player_name_key
                AND sc.position = rp.position
                AND sc.team = rp.current_team
            )
    ),
    latest_stat_season AS (
        SELECT
            player_id,
            MAX(season) AS max_stat_season
        FROM `{project_id}.{dataset_id}.analytics_player_weekly_truth`
        WHERE season_type = 'REG'
            AND position IN ('QB', 'RB', 'WR', 'TE')
        GROUP BY player_id
    ),
    player_weekly_agg AS (
        SELECT
            t.player_id,
            ARRAY_AGG(t.player_name IGNORE NULLS ORDER BY t.season DESC, t.week DESC LIMIT 1)[SAFE_OFFSET(0)] AS player_name,
            ARRAY_AGG(t.position IGNORE NULLS ORDER BY t.season DESC, t.week DESC LIMIT 1)[SAFE_OFFSET(0)] AS position,
            ARRAY_AGG(t.current_team IGNORE NULLS ORDER BY t.season DESC, t.week DESC LIMIT 1)[SAFE_OFFSET(0)] AS current_team,
            ARRAY_AGG(t.roster_status IGNORE NULLS ORDER BY t.season DESC, t.week DESC LIMIT 1)[SAFE_OFFSET(0)] AS roster_status,
            MAX(t.season) AS stat_season,
            COUNT(DISTINCT CONCAT(CAST(t.season AS STRING), '-', CAST(t.week AS STRING))) AS weekly_rows,
            AVG(t.fantasy_points_ppr) AS avg_ppr,
            AVG(t.opportunity_score) AS avg_opportunity,
            AVG(t.efficiency_score) AS avg_efficiency,
            AVG(t.total_epa) AS avg_total_epa,
            SUM(t.total_epa) AS season_total_epa,
            AVG(t.epa_per_opportunity) AS avg_epa_per_opportunity,
            AVG(t.passing_epa) AS avg_passing_epa,
            SUM(t.passing_epa) AS season_passing_epa,
            AVG(t.rushing_epa) AS avg_rushing_epa,
            SUM(t.rushing_epa) AS season_rushing_epa,
            AVG(t.receiving_epa) AS avg_receiving_epa,
            SUM(t.receiving_epa) AS season_receiving_epa,
            AVG(t.role_quality_score) AS avg_role_quality,
            AVG(t.role_fragility_score) AS avg_role_fragility,
            AVG(t.analytical_grade) AS avg_grade,
            AVG(t.wopr) AS avg_wopr,
            AVG(t.target_share) AS avg_target_share,
            AVG(t.carry_share) AS avg_carry_share,
            AVG(t.player_run_opportunity_pct) AS avg_player_run_opportunity_pct,
            AVG(t.player_pass_opportunity_pct) AS avg_player_pass_opportunity_pct,
            SUM(t.fantasy_points_ppr) AS total_ppr,
            SUM(t.targets) AS total_targets,
            SUM(t.carries) AS total_carries,
            SUM(t.red_zone_touches) AS total_red_zone_touches,
            SUM(t.touchdowns) AS total_touchdowns
        FROM `{project_id}.{dataset_id}.analytics_player_weekly_truth` t
        JOIN latest_stat_season lss
            ON t.player_id = lss.player_id
            AND t.season = lss.max_stat_season
        WHERE t.season_type = 'REG'
            AND t.position IN ('QB', 'RB', 'WR', 'TE')
        GROUP BY t.player_id
    ),
    player_season_agg AS (
        SELECT
            t.player_id,
            t.season,
            AVG(t.fantasy_points_ppr) AS season_avg_ppr,
            AVG(t.wopr) AS season_wopr,
            AVG(t.target_share) AS season_target_share,
            AVG(t.carry_share) AS season_carry_share,
            AVG(t.role_quality_score) AS season_role_quality,
            AVG(t.role_fragility_score) AS season_role_fragility,
            SUM(t.total_epa) AS season_total_epa,
            SUM(t.passing_epa) AS season_passing_epa,
            SUM(t.rushing_epa) AS season_rushing_epa,
            SUM(t.receiving_epa) AS season_receiving_epa
        FROM `{project_id}.{dataset_id}.analytics_player_weekly_truth` t
        WHERE t.season_type = 'REG'
            AND t.position IN ('QB', 'RB', 'WR', 'TE')
        GROUP BY t.player_id, t.season
    ),
    player_multi_season AS (
        SELECT
            player_id,
            ARRAY_AGG(season_wopr IGNORE NULLS ORDER BY season DESC LIMIT 3)[SAFE_OFFSET(0)] AS latest_season_wopr,
            ARRAY_AGG(season_wopr IGNORE NULLS ORDER BY season DESC LIMIT 3)[SAFE_OFFSET(1)] AS previous_season_wopr,
            ARRAY_AGG(season_wopr IGNORE NULLS ORDER BY season DESC LIMIT 3)[SAFE_OFFSET(2)] AS two_years_ago_wopr,
            ARRAY_AGG(season_target_share IGNORE NULLS ORDER BY season DESC LIMIT 3)[SAFE_OFFSET(0)] AS latest_season_target_share,
            ARRAY_AGG(season_target_share IGNORE NULLS ORDER BY season DESC LIMIT 3)[SAFE_OFFSET(1)] AS previous_season_target_share,
            ARRAY_AGG(season_carry_share IGNORE NULLS ORDER BY season DESC LIMIT 3)[SAFE_OFFSET(0)] AS latest_season_carry_share,
            ARRAY_AGG(season_carry_share IGNORE NULLS ORDER BY season DESC LIMIT 3)[SAFE_OFFSET(1)] AS previous_season_carry_share,
            ARRAY_AGG(season_avg_ppr IGNORE NULLS ORDER BY season DESC LIMIT 3)[SAFE_OFFSET(0)] AS latest_season_ppr,
            ARRAY_AGG(season_avg_ppr IGNORE NULLS ORDER BY season DESC LIMIT 3)[SAFE_OFFSET(1)] AS previous_season_ppr,
            ARRAY_AGG(season_total_epa IGNORE NULLS ORDER BY season DESC LIMIT 3)[SAFE_OFFSET(0)] AS latest_season_total_epa,
            ARRAY_AGG(season_total_epa IGNORE NULLS ORDER BY season DESC LIMIT 3)[SAFE_OFFSET(1)] AS previous_season_total_epa
        FROM player_season_agg
        GROUP BY player_id
    ),
    base_scored AS (
        SELECT
            rc.ranking_version,
            rc.generated_at,
            rc.season,
            'preseason' AS ranking_phase,
            'PPR' AS format,
            COALESCE(rp.position, agg.position) AS position,
            rp.player_id,
            rp.sleeper_player_id,
            COALESCE(rp.player_name, agg.player_name) AS player_name,
            COALESCE(rp.current_team, agg.current_team) AS current_team,
            COALESCE(rp.roster_status, agg.roster_status) AS roster_status,
            rp.sleeper_team,
            rp.sleeper_active,
            rp.sleeper_status,
            rp.sleeper_injury_status,
            rp.sleeper_depth_chart_position,
            rp.sleeper_depth_chart_order,
            rp.sleeper_search_rank,
            rp.ranking_eligibility,
            agg.stat_season,
            COALESCE(agg.weekly_rows, 0) AS weekly_rows,
            agg.avg_ppr,
            agg.avg_opportunity,
            agg.avg_efficiency,
            agg.avg_total_epa,
            agg.season_total_epa,
            agg.avg_epa_per_opportunity,
            agg.avg_passing_epa,
            agg.season_passing_epa,
            agg.avg_rushing_epa,
            agg.season_rushing_epa,
            agg.avg_receiving_epa,
            agg.season_receiving_epa,
            agg.avg_role_quality,
            agg.avg_role_fragility,
            agg.avg_grade,
            agg.avg_wopr,
            agg.avg_target_share,
            agg.avg_carry_share,
            ms.latest_season_wopr,
            ms.previous_season_wopr,
            ms.two_years_ago_wopr,
            ms.latest_season_target_share,
            ms.previous_season_target_share,
            ms.latest_season_carry_share,
            ms.previous_season_carry_share,
            ms.latest_season_ppr,
            ms.previous_season_ppr,
            ms.latest_season_total_epa,
            ms.previous_season_total_epa,
            agg.avg_player_run_opportunity_pct,
            agg.avg_player_pass_opportunity_pct,
            agg.total_ppr,
            agg.total_targets,
            agg.total_carries,
            agg.total_red_zone_touches,
            agg.total_touchdowns,
            ROUND(
                0.55 * COALESCE(agg.avg_grade, 0)
                + 0.15 * COALESCE(agg.avg_opportunity, 0)
                + 0.10 * COALESCE(agg.avg_efficiency, 0)
                + 0.10 * GREATEST(0, 100 - COALESCE(agg.avg_role_fragility, 50))
                + 0.10 * LEAST(100, COALESCE(agg.avg_ppr, 0) * 4),
                2
            ) AS raw_ranking_score,
            CASE
                WHEN COALESCE(rp.position, agg.position) = 'QB'
                    AND COALESCE(rp.sleeper_depth_chart_order, 99) > 1
                    THEN 18.0
                WHEN COALESCE(rp.position, agg.position) = 'QB'
                    AND rp.sleeper_depth_chart_order IS NULL
                    THEN 10.0
                WHEN COALESCE(rp.position, agg.position) IN ('RB', 'WR', 'TE')
                    AND COALESCE(rp.sleeper_depth_chart_order, 99) > 5
                    THEN 5.0
                ELSE 0.0
            END AS depth_chart_penalty,
            ROUND(
                LEAST(
                    100,
                    GREATEST(
                        0,
                        35
                        + COALESCE(agg.weekly_rows, 0) * 2
                        + IF(agg.avg_grade IS NOT NULL, 20, 0)
                        - IF(COALESCE(agg.avg_role_fragility, 0) >= 60, 10, 0)
                    )
                ),
                2
            ) AS confidence_score
        FROM active_roster_players rp
        LEFT JOIN player_weekly_agg agg
            ON rp.player_id = agg.player_id
            OR (
                LOWER(rp.player_name) = LOWER(agg.player_name)
                AND rp.position = agg.position
            )
        LEFT JOIN player_multi_season ms
            ON rp.player_id = ms.player_id
        CROSS JOIN run_context rc
    ),
    scored AS (
        SELECT
            *,
            ROUND(GREATEST(0, raw_ranking_score - depth_chart_penalty), 2) AS ranking_score
        FROM base_scored
    ),
    ranked AS (
        SELECT
            *,
            RANK() OVER(
                PARTITION BY position
                ORDER BY ranking_score DESC, COALESCE(avg_ppr, 0) DESC, player_name
            ) AS rank
        FROM scored
        WHERE position IN ('QB', 'RB', 'WR', 'TE')
    )
    SELECT
        ranking_version,
        generated_at,
        season,
        ranking_phase,
        format,
        position,
        rank,
        CASE
            WHEN position = 'QB' AND COALESCE(sleeper_depth_chart_order, 99) > 1 THEN 'backup or handcuff'
            WHEN position = 'QB' AND rank <= 3 THEN 'elite QB1'
            WHEN position = 'QB' AND rank <= 8 THEN 'QB1'
            WHEN position = 'QB' AND rank <= 18 THEN 'QB2 or streamer'
            WHEN position = 'QB' THEN 'bench or watchlist'
            WHEN rank <= 3 THEN 'elite'
            WHEN rank <= 8 THEN 'front-line starter'
            WHEN rank <= 16 THEN 'starter'
            WHEN rank <= 30 THEN 'flex or matchup'
            ELSE 'deep or watchlist'
        END AS tier,
        player_id,
        player_name,
        current_team,
        roster_status,
        sleeper_player_id,
        sleeper_team,
        sleeper_active,
        sleeper_status,
        sleeper_injury_status,
        sleeper_depth_chart_position,
        sleeper_depth_chart_order,
        sleeper_search_rank,
        ranking_eligibility,
        stat_season,
        weekly_rows,
        raw_ranking_score,
        depth_chart_penalty,
        ranking_score,
        avg_ppr,
        avg_opportunity,
        avg_efficiency,
        avg_total_epa,
        season_total_epa,
        avg_epa_per_opportunity,
        avg_passing_epa,
        season_passing_epa,
        avg_rushing_epa,
        season_rushing_epa,
        avg_receiving_epa,
        season_receiving_epa,
        avg_role_quality,
        avg_role_fragility,
        avg_grade,
        avg_wopr,
        avg_target_share,
        avg_carry_share,
        latest_season_wopr,
        previous_season_wopr,
        two_years_ago_wopr,
        latest_season_target_share,
        previous_season_target_share,
        latest_season_carry_share,
        previous_season_carry_share,
        latest_season_ppr,
        previous_season_ppr,
        latest_season_total_epa,
        previous_season_total_epa,
        avg_player_run_opportunity_pct,
        avg_player_pass_opportunity_pct,
        total_ppr,
        total_targets,
        total_carries,
        total_red_zone_touches,
        total_touchdowns,
        confidence_score,
        CASE
            WHEN avg_grade IS NULL THEN 'No recent NFL weekly sample. Pigskin is treating this as a watchlist profile, not a ranked conviction.'
            WHEN position = 'QB' AND COALESCE(sleeper_depth_chart_order, 99) > 1 THEN 'Historical production noted, but Sleeper has him as a backup. Calling that a QB1 projection would be malpractice with a spreadsheet.'
            WHEN rank <= 3 AND COALESCE(avg_role_fragility, 0) < 40 THEN 'Elite ranking with enough role support to survive the usual offseason noise.'
            WHEN COALESCE(avg_role_fragility, 0) >= 60 THEN 'Ranked, but fragile. The box score may be wearing a nicer suit than the role deserves.'
            WHEN COALESCE(avg_ppr, 0) >= 12 AND COALESCE(avg_role_quality, 0) < 45 THEN 'Useful fantasy output, questionable process. That is exactly where the vibes tax starts getting expensive.'
            WHEN COALESCE(avg_opportunity, 0) >= 60 THEN 'The volume is doing real work. Pigskin can respect that, even if the market gets weird about it.'
            ELSE 'Ranked off the blended Pigskin score: role, efficiency, opportunity, fragility, and PPR output.'
        END AS pigskin_verdict,
        CONCAT(
            'Pigskin rank #', CAST(rank AS STRING), ' at ', position,
            ' from a ', CAST(ROUND(ranking_score, 1) AS STRING), ' score. ',
            'Raw score ', CAST(ROUND(raw_ranking_score, 1) AS STRING),
            ', depth-chart penalty ', CAST(ROUND(depth_chart_penalty, 1) AS STRING),
            ', Sleeper team ', COALESCE(sleeper_team, 'none'),
            ', Sleeper depth ', COALESCE(CAST(sleeper_depth_chart_order AS STRING), 'unknown'), '. ',
            'Inputs: grade ', CAST(ROUND(COALESCE(avg_grade, 0), 1) AS STRING),
            ', opportunity ', CAST(ROUND(COALESCE(avg_opportunity, 0), 1) AS STRING),
            ', efficiency ', CAST(ROUND(COALESCE(avg_efficiency, 0), 1) AS STRING),
            ', EPA/opportunity ', CAST(ROUND(COALESCE(avg_epa_per_opportunity, 0), 3) AS STRING),
            ', role fragility ', CAST(ROUND(COALESCE(avg_role_fragility, 0), 1) AS STRING),
            ', PPR/G ', CAST(ROUND(COALESCE(avg_ppr, 0), 1) AS STRING), '.'
        ) AS rank_rationale,
        COALESCE(
            NULLIF(
                ARRAY_TO_STRING(
                    ARRAY(
                        SELECT flag
                        FROM UNNEST([
                            IF(avg_grade IS NULL, 'missing recent weekly sample', NULL),
                            IF(position = 'QB' AND COALESCE(sleeper_depth_chart_order, 99) > 1, 'not current QB1 on own NFL depth chart', NULL),
                            IF(sleeper_team IS NULL, 'not on a current Sleeper NFL team', NULL),
                            IF(COALESCE(avg_role_fragility, 0) >= 60, 'fragile role', NULL),
                            IF(COALESCE(avg_ppr, 0) >= 12 AND COALESCE(avg_role_quality, 0) < 45, 'box-score support outruns role quality', NULL),
                            IF(position IN ('WR', 'TE') AND COALESCE(avg_wopr, 0) < 0.35 AND rank <= 24, 'target profile is thin for price', NULL),
                            IF(position = 'RB' AND COALESCE(avg_carry_share, 0) < 0.35 AND rank <= 24, 'backfield share is thin for price', NULL)
                        ]) AS flag
                        WHERE flag IS NOT NULL
                    ),
                    '; '
                ),
                ''
            ),
            'no major Pigskin ranking flag'
        ) AS risk_flags,
        CASE
            WHEN position IN ('WR', 'TE') THEN 'A target-share, WOPR, route, or QB-context change can move this rank materially.'
            WHEN position = 'RB' THEN 'A backfield share, goal-line role, injury, or pass-game usage change can move this rank materially.'
            WHEN position = 'QB' THEN 'A rushing role, pass-volume, play-caller, protection, or weapons change can move this rank materially.'
            ELSE 'A meaningful role, team, or health context change can move this rank materially.'
        END AS what_would_change_mind,
        'deterministic-pigskin-v2-sleeper-eligible' AS model_name,
        'pigskin-rankings-v2-sleeper-depth' AS prompt_version,
        CONCAT(
            'stats_through_', COALESCE(CAST(stat_season AS STRING), 'none'),
            '_generated_', FORMAT_TIMESTAMP('%Y%m%d', generated_at)
        ) AS data_snapshot_label,
        TRUE AS is_active
    FROM ranked
    """


def build_pigskin_rankings_history_create_sql(project_id, dataset_id):
    return f"""
    CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.analytics_pigskin_rankings_history`
    PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2020, 2050, 1))
    CLUSTER BY position, ranking_version, rank AS
    SELECT *
    FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings`
    WHERE FALSE
    """


def build_pigskin_rankings_history_schema_update_sql(project_id, dataset_id):
    table_id = f"`{project_id}.{dataset_id}.analytics_pigskin_rankings_history`"
    new_columns = [
        ("sleeper_player_id", "STRING"),
        ("sleeper_team", "STRING"),
        ("sleeper_active", "BOOLEAN"),
        ("sleeper_status", "STRING"),
        ("sleeper_injury_status", "STRING"),
        ("sleeper_depth_chart_position", "STRING"),
        ("sleeper_depth_chart_order", "INT64"),
        ("sleeper_search_rank", "INT64"),
        ("ranking_eligibility", "STRING"),
        ("raw_ranking_score", "FLOAT64"),
        ("depth_chart_penalty", "FLOAT64"),
    ]
    return [
        f"ALTER TABLE {table_id} ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
        for column_name, column_type in new_columns
    ]


def build_pigskin_rankings_history_insert_sql(project_id, dataset_id):
    columns = [
        "ranking_version",
        "generated_at",
        "season",
        "ranking_phase",
        "format",
        "position",
        "rank",
        "tier",
        "player_id",
        "player_name",
        "current_team",
        "roster_status",
        "sleeper_player_id",
        "sleeper_team",
        "sleeper_active",
        "sleeper_status",
        "sleeper_injury_status",
        "sleeper_depth_chart_position",
        "sleeper_depth_chart_order",
        "sleeper_search_rank",
        "ranking_eligibility",
        "stat_season",
        "weekly_rows",
        "raw_ranking_score",
        "depth_chart_penalty",
        "ranking_score",
        "avg_ppr",
        "avg_opportunity",
        "avg_efficiency",
        "avg_role_quality",
        "avg_role_fragility",
        "avg_grade",
        "avg_wopr",
        "avg_target_share",
        "avg_carry_share",
        "avg_player_run_opportunity_pct",
        "avg_player_pass_opportunity_pct",
        "total_ppr",
        "total_targets",
        "total_carries",
        "total_red_zone_touches",
        "total_touchdowns",
        "confidence_score",
        "pigskin_verdict",
        "rank_rationale",
        "risk_flags",
        "what_would_change_mind",
        "model_name",
        "prompt_version",
        "data_snapshot_label",
        "is_active",
    ]
    column_csv = ",\n        ".join(columns)
    active_column_csv = ",\n        ".join(f"active.{column}" for column in columns)
    return f"""
    INSERT INTO `{project_id}.{dataset_id}.analytics_pigskin_rankings_history` (
        {column_csv}
    )
    SELECT
        {active_column_csv}
    FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings` active
    WHERE NOT EXISTS (
        SELECT 1
        FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings_history` history
        WHERE history.ranking_version = active.ranking_version
    )
    """


def build_player_qb_weekly_sql(project_id, dataset_id):
    return f"""
    CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.analytics_player_qb_weekly`
    PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2000, 2050, 1))
    CLUSTER BY player_name, qb_name, posteam AS
    WITH target_events AS (
        SELECT DISTINCT
            season,
            week,
            game_id,
            posteam,
            defteam,
            passer_player_id,
            passer_player_name,
            receiver_player_id,
            receiver_player_name,
            complete_pass,
            yards_gained,
            air_yards,
            yards_after_catch,
            touchdown,
            epa,
            cpoe,
            yardline_100
        FROM `{project_id}.{dataset_id}.play_by_play`
        WHERE season_type = 'REG'
            AND pass_attempt = 1
            AND passer_player_id IS NOT NULL
            AND receiver_player_id IS NOT NULL
    ),
    team_week_targets AS (
        SELECT
            season,
            week,
            posteam,
            COUNT(1) AS team_targets
        FROM target_events
        GROUP BY season, week, posteam
    ),
    qb_week_attempts AS (
        SELECT
            season,
            week,
            posteam,
            passer_player_id,
            COUNT(1) AS qb_targets
        FROM target_events
        GROUP BY season, week, posteam, passer_player_id
    )
    SELECT
        t.season,
        t.week,
        t.posteam,
        t.defteam,
        t.receiver_player_id AS player_id,
        t.receiver_player_name AS player_name,
        t.passer_player_id AS qb_id,
        t.passer_player_name AS qb_name,
        COUNT(1) AS targets,
        SUM(COALESCE(t.complete_pass, 0)) AS receptions,
        SAFE_DIVIDE(SUM(COALESCE(t.complete_pass, 0)), COUNT(1)) AS catch_rate,
        SUM(COALESCE(t.yards_gained, 0)) AS receiving_yards,
        SAFE_DIVIDE(SUM(COALESCE(t.yards_gained, 0)), COUNT(1)) AS yards_per_target,
        SUM(COALESCE(t.air_yards, 0)) AS air_yards,
        AVG(t.air_yards) AS adot,
        SUM(COALESCE(t.yards_after_catch, 0)) AS yards_after_catch,
        SAFE_DIVIDE(SUM(COALESCE(t.yards_after_catch, 0)), NULLIF(SUM(COALESCE(t.complete_pass, 0)), 0)) AS yac_per_reception,
        SUM(COALESCE(t.touchdown, 0)) AS touchdowns,
        SUM(IF(t.yardline_100 <= 20, 1, 0)) AS red_zone_targets,
        SUM(IF(t.yardline_100 <= 10, 1, 0)) AS inside_10_targets,
        SUM(COALESCE(t.epa, 0)) AS total_epa,
        SAFE_DIVIDE(SUM(COALESCE(t.epa, 0)), COUNT(1)) AS epa_per_target,
        AVG(t.cpoe) AS avg_cpoe,
        q.qb_targets,
        tw.team_targets,
        SAFE_DIVIDE(COUNT(1), q.qb_targets) AS target_share_from_qb,
        SAFE_DIVIDE(COUNT(1), tw.team_targets) AS team_target_share
    FROM target_events t
    LEFT JOIN qb_week_attempts q
        ON t.season = q.season
        AND t.week = q.week
        AND t.posteam = q.posteam
        AND t.passer_player_id = q.passer_player_id
    LEFT JOIN team_week_targets tw
        ON t.season = tw.season
        AND t.week = tw.week
        AND t.posteam = tw.posteam
    GROUP BY
        t.season,
        t.week,
        t.posteam,
        t.defteam,
        player_id,
        player_name,
        qb_id,
        qb_name,
        q.qb_targets,
        tw.team_targets
    """


def build_player_qb_splits_sql(project_id, dataset_id):
    return f"""
    CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.analytics_player_qb_splits`
    PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2000, 2050, 1))
    CLUSTER BY player_name, qb_name, posteam AS
    SELECT
        season,
        posteam,
        player_id,
        player_name,
        qb_id,
        qb_name,
        COUNT(DISTINCT week) AS weeks_with_targets,
        MIN(week) AS first_week_with_qb,
        MAX(week) AS last_week_with_qb,
        SUM(targets) AS targets,
        SUM(receptions) AS receptions,
        SAFE_DIVIDE(SUM(receptions), SUM(targets)) AS catch_rate,
        SUM(receiving_yards) AS receiving_yards,
        SAFE_DIVIDE(SUM(receiving_yards), SUM(targets)) AS yards_per_target,
        SUM(air_yards) AS air_yards,
        SAFE_DIVIDE(SUM(air_yards), SUM(targets)) AS adot,
        SUM(yards_after_catch) AS yards_after_catch,
        SAFE_DIVIDE(SUM(yards_after_catch), NULLIF(SUM(receptions), 0)) AS yac_per_reception,
        SUM(touchdowns) AS touchdowns,
        SUM(red_zone_targets) AS red_zone_targets,
        SUM(inside_10_targets) AS inside_10_targets,
        SUM(total_epa) AS total_epa,
        SAFE_DIVIDE(SUM(total_epa), SUM(targets)) AS epa_per_target,
        AVG(avg_cpoe) AS avg_cpoe,
        SUM(qb_targets) AS qb_targets,
        SUM(team_targets) AS team_targets,
        SAFE_DIVIDE(SUM(targets), SUM(qb_targets)) AS target_share_from_qb,
        SAFE_DIVIDE(SUM(targets), SUM(team_targets)) AS team_target_share,
        CASE
            WHEN SUM(targets) >= 40 THEN 'large sample'
            WHEN SUM(targets) >= 20 THEN 'usable sample'
            WHEN SUM(targets) >= 10 THEN 'thin sample'
            ELSE 'noise sample'
        END AS sample_label
    FROM `{project_id}.{dataset_id}.analytics_player_qb_weekly`
    GROUP BY
        season,
        posteam,
        player_id,
        player_name,
        qb_id,
        qb_name
    """


def materialize_player_weekly_truth(client, dataset_id="fantasy_football_brain", dry_run=False):
    existing_tables = get_existing_tables(client, dataset_id)
    if "weekly_metrics" not in existing_tables:
        raise RuntimeError(f"Missing required table: {dataset_id}.weekly_metrics")
    if "play_by_play" not in existing_tables:
        raise RuntimeError(f"Missing required table: {dataset_id}.play_by_play")

    query = build_player_weekly_truth_sql(client.project, dataset_id, existing_tables)
    job_config = bigquery.QueryJobConfig(dry_run=True) if dry_run else None
    job = client.query(query, job_config=job_config)
    if not dry_run:
        job.result()
    return job


def materialize_fraud_watch(client, dataset_id="fantasy_football_brain", dry_run=False):
    existing_tables = get_existing_tables(client, dataset_id)
    if "analytics_player_weekly_truth" not in existing_tables:
        raise RuntimeError(f"Missing required table: {dataset_id}.analytics_player_weekly_truth")

    query = build_fraud_watch_sql(client.project, dataset_id)
    job_config = bigquery.QueryJobConfig(dry_run=True) if dry_run else None
    job = client.query(query, job_config=job_config)
    if not dry_run:
        job.result()
    return job


def materialize_pigskin_rankings(client, dataset_id="fantasy_football_brain", dry_run=False):
    existing_tables = get_existing_tables(client, dataset_id)
    if "analytics_player_weekly_truth" not in existing_tables:
        raise RuntimeError(f"Missing required table: {dataset_id}.analytics_player_weekly_truth")
    if "player_rosters" not in existing_tables:
        raise RuntimeError(f"Missing required table: {dataset_id}.player_rosters")
    if "sleeper_players_current" not in existing_tables:
        raise RuntimeError(
            f"Missing required table: {dataset_id}.sleeper_players_current. "
            "Run the Sleeper news/current-player ingest before materializing Pigskin rankings."
        )

    queries = [build_pigskin_rankings_sql(client.project, dataset_id)]

    job_config = bigquery.QueryJobConfig(dry_run=True) if dry_run else None
    jobs = []
    for query in queries:
        job = client.query(query, job_config=job_config)
        if not dry_run:
            job.result()
        jobs.append(job)
    return jobs


def materialize_player_qb_context(client, dataset_id="fantasy_football_brain", dry_run=False):
    existing_tables = get_existing_tables(client, dataset_id)
    if "play_by_play" not in existing_tables:
        raise RuntimeError(f"Missing required table: {dataset_id}.play_by_play")

    queries = [
        build_player_qb_weekly_sql(client.project, dataset_id),
        build_player_qb_splits_sql(client.project, dataset_id),
    ]
    job_config = bigquery.QueryJobConfig(dry_run=True) if dry_run else None
    jobs = []
    for query in queries:
        job = client.query(query, job_config=job_config)
        if not dry_run:
            job.result()
        jobs.append(job)
    return jobs


def materialize_game_environment(client, dataset_id="fantasy_football_brain", dry_run=False):
    existing_tables = get_existing_tables(client, dataset_id)
    if "play_by_play" not in existing_tables:
        raise RuntimeError(f"Missing required table: {dataset_id}.play_by_play")

    query = build_game_environment_sql(client.project, dataset_id)
    job_config = bigquery.QueryJobConfig(dry_run=True) if dry_run else None
    job = client.query(query, job_config=job_config)
    if not dry_run:
        job.result()
    return job


def materialize_all(client, dataset_id="fantasy_football_brain", dry_run=False):
    jobs = []
    jobs.append(materialize_game_environment(client, dataset_id=dataset_id, dry_run=dry_run))
    jobs.extend(materialize_player_qb_context(client, dataset_id=dataset_id, dry_run=dry_run))
    jobs.append(materialize_player_weekly_truth(client, dataset_id=dataset_id, dry_run=dry_run))
    jobs.append(materialize_fraud_watch(client, dataset_id=dataset_id, dry_run=dry_run))
    jobs.extend(materialize_pigskin_rankings(client, dataset_id=dataset_id, dry_run=dry_run))
    return jobs


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Materialize AI vs Vibes fantasy analytics tables.")
    parser.add_argument(
        "--dataset",
        default="fantasy_football_brain",
        help="BigQuery dataset name containing the fantasy warehouse tables.",
    )
    parser.add_argument(
        "--project",
        default=get_bigquery_project(),
        help="BigQuery project containing the fantasy warehouse.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the BigQuery query without creating or replacing tables.",
    )
    parser.add_argument(
        "--only",
        choices=["all", "player-weekly-truth", "pigskin-rankings"],
        default="all",
        help="Materialize all analytics tables or only one targeted table group.",
    )
    args = parser.parse_args()

    client = bigquery.Client(project=args.project)
    print("Materializing AI vs Vibes analytics tables...")
    if args.only == "player-weekly-truth":
        jobs = [materialize_player_weekly_truth(client, dataset_id=args.dataset, dry_run=args.dry_run)]
    elif args.only == "pigskin-rankings":
        jobs = materialize_pigskin_rankings(client, dataset_id=args.dataset, dry_run=args.dry_run)
    else:
        jobs = materialize_all(client, dataset_id=args.dataset, dry_run=args.dry_run)
    if args.dry_run:
        total_bytes = sum(job.total_bytes_processed or 0 for job in jobs)
        print(f"Dry run passed. Estimated bytes processed: {total_bytes}")
    else:
        print(f"Tables in `{client.project}.{args.dataset}` materialized successfully.")


if __name__ == "__main__":
    main()
