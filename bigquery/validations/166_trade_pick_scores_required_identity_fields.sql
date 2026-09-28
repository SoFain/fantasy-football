-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_identity_rows = 0

SELECT COUNT(*) AS missing_identity_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores`
WHERE model_version IS NULL OR TRIM(model_version) = ''
    OR score_run_id IS NULL OR TRIM(score_run_id) = ''
    OR source_pick_key IS NULL OR TRIM(source_pick_key) = ''
    OR pick_label IS NULL OR TRIM(pick_label) = ''
    OR pick_year IS NULL
    OR pick_class IS NULL OR TRIM(pick_class) = ''
    OR pick_round IS NULL
    OR pick_bucket IS NULL OR TRIM(pick_bucket) = ''
    OR parse_confidence IS NULL OR TRIM(parse_confidence) = ''
    OR scoring_profile_id IS NULL OR TRIM(scoring_profile_id) = ''
    OR league_type_id IS NULL OR TRIM(league_type_id) = ''
    OR roster_format_id IS NULL OR TRIM(roster_format_id) = '';
