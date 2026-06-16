-- Validation helper. Render placeholders before running manually.
-- Expected result: oversized_content_briefs = 0

SELECT COUNT(*) AS oversized_content_briefs
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.content_briefs`
WHERE token_estimate > 3500
   OR LENGTH(brief_text) > 12000;
