-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_score_rows = 0

SELECT COUNT(*) AS invalid_score_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.claim_grades`
WHERE verdict != 'inconclusive'
  AND (
      claim_accuracy_score IS NULL
      OR confidence_score IS NULL
      OR claim_accuracy_score < 0
      OR claim_accuracy_score > 1
      OR confidence_score < 0
      OR confidence_score > 1
  );
