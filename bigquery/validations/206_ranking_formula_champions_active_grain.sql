-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_active_champions = 0

SELECT COUNT(*) AS duplicate_active_champions
FROM (
    SELECT formula_set_id, position, COUNT(*) AS active_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_formula_champions`
    WHERE active IS TRUE
    GROUP BY 1, 2
    HAVING active_count > 1
);
