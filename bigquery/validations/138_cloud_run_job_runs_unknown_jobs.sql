-- Validation helper. Render placeholders before running manually.
-- Expected result: unknown_job_rows = 0

SELECT COUNT(*) AS unknown_job_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.cloud_run_job_runs`
WHERE started_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
  AND job_name NOT IN (
      'ingest-nflverse',
      'ingest-sleeper-news',
      'ingest-sleeper-league',
      'ingest-context-events',
      'ingest-market-values',
      'ingest-college-stats',
      'materialize-analytics',
      'generate-pigskin-rankings',
      'generate-evidence-packets',
      'run-projections',
      'run-backtests',
      'validate-warehouse',
      'verify-external-context'
  );
