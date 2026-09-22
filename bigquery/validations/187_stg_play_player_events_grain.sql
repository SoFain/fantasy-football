-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_play_event_rows = 0

SELECT COUNT(*) AS duplicate_play_event_rows
FROM (
    SELECT season, week, game_id, play_id, event_type, player_id_internal, team, COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.stg_play_player_events`
    GROUP BY 1, 2, 3, 4, 5, 6, 7
    HAVING row_count > 1
);
