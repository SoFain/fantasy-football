-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_ready_claims = 0

SELECT COUNT(*) AS invalid_ready_claims
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.fantasy_claims`
WHERE review_status IN ('reviewed', 'ready_to_grade', 'graded')
  AND (
      source_id IS NULL
      OR source_name IS NULL
      OR claim_text IS NULL
      OR claim_type IS NULL
      OR claim_direction IS NULL
      OR time_horizon IS NULL
      OR season IS NULL
      OR (
          (player_ids_json IS NULL OR player_ids_json = '[]')
          AND (team_ids_json IS NULL OR team_ids_json = '[]')
      )
  );
