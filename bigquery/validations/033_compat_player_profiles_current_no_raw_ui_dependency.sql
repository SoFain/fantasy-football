-- Validation helper. Render placeholders before running manually.
-- Expected result: raw_profile_reference_count = 0.

SELECT
    'compat_player_profiles_current_no_raw_ui_dependency' AS validation_name,
    COUNTIF(REGEXP_CONTAINS(
        LOWER(view_definition),
        r'\b(player_rosters|player_contracts|depth_charts|college_player_stats|rookie_scouting_metrics)\b'
    )) AS raw_profile_reference_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.VIEWS`
WHERE table_name = 'compat_player_profiles_current';
