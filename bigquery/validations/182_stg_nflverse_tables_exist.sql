-- Validation helper. Render placeholders before running manually.
-- Expected result: table_count = 6

SELECT COUNT(*) AS table_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.TABLES`
WHERE table_name IN (
    'stg_player_identity',
    'stg_game_context',
    'stg_player_week_stats',
    'stg_team_week_stats',
    'stg_play_player_events',
    'stg_participation_context'
);
