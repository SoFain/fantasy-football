-- Validation helper. Render placeholders before running manually.
-- Expected result: player_column_count = 0

SELECT COUNT(*) AS player_column_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'trade_pick_scores'
    AND column_name IN (
        'player_id',
        'player_id_internal',
        'player_name',
        'normalized_name',
        'position',
        'team',
        'gsis_id',
        'sleeper_player_id'
    );
