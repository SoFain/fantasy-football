-- Validation helper. Render placeholders before running manually.
-- Expected result: draft_claims_missing_review_fields should be reviewed

SELECT COUNT(*) AS draft_claims_missing_review_fields
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.fantasy_claims`
WHERE review_status = 'draft'
  AND (
      claim_direction IS NULL
      OR (player_ids_json IS NULL OR player_ids_json = '[]')
      OR claim_source_type IS NULL
      OR scoring_profile_id IS NULL
      OR league_type_id IS NULL
      OR roster_format_id IS NULL
  );
