-- Validation helper. Render placeholders before running manually.
-- Expected result: zero rows returned.

SELECT
    'scoring_profiles' AS table_name,
    scoring_profile_id AS config_id,
    COUNT(*) AS active_row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.scoring_profiles`
WHERE active
GROUP BY scoring_profile_id
HAVING COUNT(*) > 1

UNION ALL

SELECT
    'league_types' AS table_name,
    league_type_id AS config_id,
    COUNT(*) AS active_row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.league_types`
WHERE active
GROUP BY league_type_id
HAVING COUNT(*) > 1

UNION ALL

SELECT
    'roster_formats' AS table_name,
    roster_format_id AS config_id,
    COUNT(*) AS active_row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.roster_formats`
WHERE active
GROUP BY roster_format_id
HAVING COUNT(*) > 1

UNION ALL

SELECT
    'feature_config_versions' AS table_name,
    feature_config_version_id AS config_id,
    COUNT(*) AS active_row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.feature_config_versions`
WHERE active
GROUP BY feature_config_version_id
HAVING COUNT(*) > 1;
