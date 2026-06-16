-- Validation helper. Render placeholders before running manually.
-- Expected result: raw_source_reference_count = 0 for the compatibility view.

SELECT
    'compat_sleeper_watch_candidates_no_raw_ui_dependency' AS validation_name,
    COUNTIF(REGEXP_CONTAINS(LOWER(view_definition), r'\bweekly_metrics\b|\bsleeper_rosters\b|\bsleeper_roster_players\b')) AS raw_source_reference_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.VIEWS`
WHERE table_name = 'compat_sleeper_watch_candidates';
