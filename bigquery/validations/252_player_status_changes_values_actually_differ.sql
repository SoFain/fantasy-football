-- Validation helper. Render placeholders before running manually.
-- A change row whose old and new value are equal is a detector bug.
-- Expected result: zero rows

SELECT sleeper_player_id, field_name, old_value, new_value
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_status_changes`
WHERE COALESCE(old_value, '') = COALESCE(new_value, '')
LIMIT 100;
