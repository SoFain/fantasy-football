-- Validation helper. Render placeholders before running manually.
-- Expected result: unknown_scoring_profile_count = 0.

SELECT
    'compat_trade_assets_current_scoring_profiles_exist' AS validation_name,
    COUNTIF(sp.scoring_profile_id IS NULL) AS unknown_scoring_profile_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_assets_current` a
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.scoring_profiles` sp
    ON a.scoring_profile_id = sp.scoring_profile_id
    AND COALESCE(sp.active, TRUE);
