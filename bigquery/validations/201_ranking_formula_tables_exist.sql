-- Validation helper. Render placeholders before running manually.
-- Expected result: table_count = 6

SELECT COUNT(*) AS table_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.TABLES`
WHERE table_name IN (
    'ranking_formula_candidates',
    'ranking_backtest_runs',
    'ranking_backtest_results',
    'ranking_backtest_candidate_summaries',
    'ranking_formula_champions',
    'ranking_formula_sets'
);
