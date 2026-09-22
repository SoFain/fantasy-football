-- RB Fable v1.2 research challenger: Phase 34.4 score plus preseason RB-room competition.
-- Target-season Week 1 rosters are knowable before outcomes. Every workload input remains
-- from the input season. This view is backtest-only and does not write rankings.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_rb_fable_v12_backtest_prep` AS
WITH base AS (
  SELECT *
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_rb_fable_01_backtest_prep`
),
week_one_rb_rosters AS (
  SELECT
    season AS target_season,
    gsis_id,
    ARRAY_AGG(CASE team
      WHEN 'LA' THEN 'LAR'
      WHEN 'HST' THEN 'HOU'
      WHEN 'BLT' THEN 'BAL'
      WHEN 'CLV' THEN 'CLE'
      WHEN 'ARZ' THEN 'ARI'
      ELSE team
    END ORDER BY week LIMIT 1)[SAFE_OFFSET(0)] AS destination_team
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.raw_nflverse_rosters_weekly`
  WHERE position = 'RB'
    AND week = 1
    AND season BETWEEN 2023 AND 2025
    AND gsis_id IS NOT NULL
  GROUP BY target_season, gsis_id
),
prior_workloads AS (
  SELECT
    season,
    candidate_internal_player_id AS gsis_id,
    CASE team
      WHEN 'LA' THEN 'LAR'
      WHEN 'HST' THEN 'HOU'
      WHEN 'BLT' THEN 'BAL'
      WHEN 'CLV' THEN 'CLE'
      WHEN 'ARZ' THEN 'ARI'
      ELSE team
    END AS source_team,
    non_garbage_time_touches
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_rb_fable_01_metric_inputs`
  WHERE season BETWEEN 2022 AND 2024
),
source_rooms AS (
  SELECT season, source_team, SUM(non_garbage_time_touches) AS source_room_touches
  FROM prior_workloads
  GROUP BY season, source_team
),
rb_rooms AS (
  SELECT
    rosters.target_season,
    rosters.destination_team,
    SUM(COALESCE(workloads.non_garbage_time_touches, 0)) AS returning_room_touches,
    COUNTIF(COALESCE(workloads.non_garbage_time_touches, 0) >= 50) AS experienced_room_backs
  FROM week_one_rb_rosters AS rosters
  LEFT JOIN prior_workloads AS workloads
    ON workloads.season = rosters.target_season - 1
   AND workloads.gsis_id = rosters.gsis_id
  GROUP BY rosters.target_season, rosters.destination_team
),
enriched AS (
  SELECT
    base.*,
    rosters.destination_team,
    CASE base.team
      WHEN 'LA' THEN 'LAR'
      WHEN 'HST' THEN 'HOU'
      WHEN 'BLT' THEN 'BAL'
      WHEN 'CLV' THEN 'CLE'
      WHEN 'ARZ' THEN 'ARI'
      ELSE base.team
    END AS source_team,
    rooms.returning_room_touches,
    rooms.experienced_room_backs,
    SAFE_DIVIDE(base.non_garbage_time_touches, rooms.returning_room_touches) AS preseason_room_touch_share,
    SAFE_DIVIDE(base.non_garbage_time_touches, source_rooms.source_room_touches) AS source_room_touch_share
  FROM base
  LEFT JOIN week_one_rb_rosters AS rosters
    ON rosters.target_season = base.target_season
   AND rosters.gsis_id = base.candidate_internal_player_id
  LEFT JOIN rb_rooms AS rooms
    ON rooms.target_season = rosters.target_season
   AND rooms.destination_team = rosters.destination_team
  LEFT JOIN source_rooms
    ON source_rooms.season = base.season
   AND source_rooms.source_team = CASE base.team
     WHEN 'LA' THEN 'LAR'
     WHEN 'HST' THEN 'HOU'
     WHEN 'BLT' THEN 'BAL'
     WHEN 'CLV' THEN 'CLE'
     WHEN 'ARZ' THEN 'ARI'
     ELSE base.team
   END
),
standardized AS (
  SELECT
    enriched.*,
    enriched.destination_team IS NOT NULL AND enriched.destination_team != enriched.source_team AS team_changed,
    CASE
      WHEN enriched.destination_team IS NOT NULL AND enriched.destination_team != enriched.source_team
        THEN preseason_room_touch_share - source_room_touch_share
      ELSE 0
    END AS projected_room_share_change,
    SAFE_DIVIDE(
      preseason_room_touch_share - AVG(preseason_room_touch_share) OVER (PARTITION BY season),
      STDDEV_POP(preseason_room_touch_share) OVER (PARTITION BY season)
    ) AS z_preseason_room_touch_share
  FROM enriched
)
SELECT
  standardized.*,
  rb_fable_01_score + 0.03 * COALESCE(z_preseason_room_touch_share, 0) AS rb_fable_v12_score_003,
  rb_fable_01_score + 0.05 * COALESCE(z_preseason_room_touch_share, 0) AS rb_fable_v12_score_005,
  rb_fable_01_score + 0.08 * COALESCE(z_preseason_room_touch_share, 0) AS rb_fable_v12_score_008,
  rb_fable_01_score + 0.10 * projected_room_share_change AS rb_fable_v12_delta_score_010,
  rb_fable_01_score + 0.20 * projected_room_share_change AS rb_fable_v12_delta_score_020,
  rb_fable_01_score + 0.30 * projected_room_share_change AS rb_fable_v12_delta_score_030
FROM standardized;
