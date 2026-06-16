-- Validation helper. Render placeholders before running manually.
-- Expected result: orphan_claim_grade_rows = 0

SELECT COUNT(*) AS orphan_claim_grade_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.claim_grades` grades
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.fantasy_claims` claims
    ON grades.claim_id = claims.claim_id
WHERE claims.claim_id IS NULL;
