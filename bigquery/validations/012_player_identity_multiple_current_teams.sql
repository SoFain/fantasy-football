-- Validation helper. Render placeholders before running manually.
-- Expected result: zero rows unless missing_data_flags explicitly includes multiple_current_teams.

SELECT
    'player_identity_multiple_current_teams' AS validation_name,
    player_id_internal,
    COUNT(DISTINCT current_team) AS current_team_count,
    ARRAY_AGG(DISTINCT current_team IGNORE NULLS ORDER BY current_team) AS current_team_values
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_identity_bridge`
WHERE current_team IS NOT NULL
    AND NOT REGEXP_CONTAINS(COALESCE(missing_data_flags, ''), r'"multiple_current_teams"')
GROUP BY player_id_internal
HAVING COUNT(DISTINCT current_team) > 1;
