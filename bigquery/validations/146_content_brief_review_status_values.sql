-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_review_status_rows = 0

SELECT COUNT(*) AS invalid_review_status_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.content_briefs`
WHERE review_status IS NULL
  OR review_status NOT IN ('draft', 'reviewed', 'approved', 'archived');
