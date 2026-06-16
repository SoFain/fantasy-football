-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_profile_rows = 0 once scoring_profiles is applied.

SELECT
    'compat_sleeper_watch_candidates_scoring_profiles_exist' AS validation_name,
    COUNTIF(sp.scoring_profile_id IS NULL) AS missing_profile_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_sleeper_watch_candidates` c
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.scoring_profiles` sp
    ON c.scoring_profile_id = sp.scoring_profile_id;
