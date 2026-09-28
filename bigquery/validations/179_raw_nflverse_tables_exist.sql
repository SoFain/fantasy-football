-- Validation helper. Render placeholders before running manually.
-- Expected result: table_count = 18

SELECT COUNT(*) AS table_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.TABLES`
WHERE table_name IN (
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
);
