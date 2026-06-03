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
            SUM(
                COALESCE(passing_epa, 0)
                + COALESCE(rushing_epa, 0)
                + COALESCE(receiving_epa, 0)
            ) AS total_epa
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
            AND w.player_name = r.player_name
            AND w.team = r.team
        LEFT JOIN snap_counts s
            ON w.season = s.season
            AND w.week = s.week
            AND w.player_name = s.player_name
            AND w.team = s.team
        LEFT JOIN ngs_receiving n
            ON w.season = n.season
            AND w.week = n.week
            AND w.player_name = n.player_name
            AND w.team = n.team
        LEFT JOIN injuries i
            ON w.season = i.season
            AND w.week = i.week
            AND w.player_name = i.player_name
            AND w.team = i.team
        LEFT JOIN sleeper_trends t
            ON w.player_name = t.player_name
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
    )
    SELECT
        *,
        ROUND(opportunity_score + efficiency_score, 2) AS analytical_grade,
        touchdown_dependency_rate >= 0.45 AND touchdowns > 0 AS touchdown_dependent,
        fantasy_points_ppr >= 15
            AND skill_player_opportunities < 8
            AND touchdown_dependency_rate >= 0.45 AS box_score_trap,
        target_share >= 0.22 OR wopr >= 0.55 AS target_earner,
        skill_player_opportunities >= 12
            AND fantasy_points_ppr < 10 AS empty_volume,
        skill_player_opportunities < 8
            AND fantasy_points_ppr >= 12 AS usage_warning,
        CASE
            WHEN fantasy_points_ppr >= 18
                AND skill_player_opportunities < 8
                AND touchdown_dependency_rate >= 0.45
                THEN 'Box-score trap: points beat role'
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
    FROM scored
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
    args = parser.parse_args()

    client = bigquery.Client(project=args.project)
    print("Materializing AI vs Vibes analytics tables...")
    jobs = materialize_all(client, dataset_id=args.dataset, dry_run=args.dry_run)
    if args.dry_run:
        total_bytes = sum(job.total_bytes_processed or 0 for job in jobs)
        print(f"Dry run passed. Estimated bytes processed: {total_bytes}")
    else:
        print(f"Tables in `{client.project}.{args.dataset}` materialized successfully.")


if __name__ == "__main__":
    main()
