-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_identity_rows = 0

SELECT COUNT(*) AS missing_identity_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_player_scores`
WHERE player_id IS NULL
    OR TRIM(player_id) = '';
