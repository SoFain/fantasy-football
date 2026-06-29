-- Validation helper. Render placeholders before running manually.
-- Expected result: review

SELECT 'raw_nflverse_pbp' AS table_name, COUNT(*) AS row_count, MIN(season) AS min_season, MAX(season) AS max_season, COUNT(DISTINCT CONCAT(CAST(season AS STRING), '-', CAST(week AS STRING))) AS season_week_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_pbp`
UNION ALL
SELECT 'raw_nflverse_weekly', COUNT(*), MIN(season), MAX(season), COUNT(DISTINCT CONCAT(CAST(season AS STRING), '-', CAST(week AS STRING)))
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_weekly`
UNION ALL
SELECT 'raw_nflverse_schedules', COUNT(*), MIN(season), MAX(season), COUNT(DISTINCT CONCAT(CAST(season AS STRING), '-', CAST(week AS STRING)))
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.raw_nflverse_schedules`;
