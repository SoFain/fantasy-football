-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_metadata_column_count = 0

WITH expected_tables AS (
    SELECT table_name
    FROM UNNEST([
        'raw_nflverse_pbp',
        'raw_nflverse_weekly',
        'raw_nflverse_rosters',
        'raw_nflverse_rosters_weekly',
        'raw_nflverse_players',
        'raw_nflverse_ff_playerids',
        'raw_nflverse_schedules',
        'raw_nflverse_teams',
        'raw_nflverse_team_stats',
        'raw_nflverse_injuries',
        'raw_nflverse_depth_charts',
        'raw_nflverse_snap_counts',
        'raw_nflverse_participation',
        'raw_nflverse_ngs_passing',
        'raw_nflverse_ngs_rushing',
        'raw_nflverse_ngs_receiving',
        'raw_nflverse_ftn_charting',
        'raw_nflverse_draft_picks'
    ]) AS table_name
),
expected_columns AS (
    SELECT column_name
    FROM UNNEST([
        'source_system',
        'source_loader',
        'source_version',
        'source_season',
        'source_week',
        'source_refresh_id',
        'loaded_at',
        'loaded_by',
        'row_hash'
    ]) AS column_name
)
SELECT COUNT(*) AS missing_metadata_column_count
FROM expected_tables
CROSS JOIN expected_columns
WHERE NOT EXISTS (
    SELECT 1
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.COLUMNS` c
    WHERE c.table_name = expected_tables.table_name
        AND LOWER(c.column_name) = expected_columns.column_name
);
