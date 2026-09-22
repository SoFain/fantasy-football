-- Validation helper. Render placeholders before running manually.
-- Expected result: blocked_metric_without_source_rows = 0

SELECT COUNT(*) AS blocked_metric_without_source_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_formula_candidates`
WHERE (
        LOWER(formula_json) LIKE '%route_share%'
        AND LOWER(source_requirements_json) NOT LIKE '%"route_share_available":true%'
    )
   OR (
        LOWER(formula_json) LIKE '%yprr%'
        AND LOWER(source_requirements_json) NOT LIKE '%"yprr_available":true%'
    )
   OR (
        LOWER(formula_json) LIKE '%first_read_share%'
        AND LOWER(source_requirements_json) NOT LIKE '%"first_read_share_available":true%'
    )
   OR (
        LOWER(formula_json) LIKE '%true_pressure%'
        AND LOWER(source_requirements_json) NOT LIKE '%"true_pressure_available":true%'
    )
   OR (
        LOWER(formula_json) LIKE '%contact_yards%'
        AND LOWER(source_requirements_json) NOT LIKE '%"contact_yards_available":true%'
    )
   OR (
        LOWER(formula_json) LIKE '%alignment%'
        AND LOWER(source_requirements_json) NOT LIKE '%"alignment_available":true%'
    );
