-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_route_rows = 0

SELECT COUNT(*) AS invalid_route_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_season_advanced_metrics`
WHERE route_metrics_source_status = 'BLOCKED'
    AND (
        routes_run IS NOT NULL
        OR yprr IS NOT NULL
        OR tprr IS NOT NULL
        OR receiving_first_downs_per_route IS NOT NULL
        OR route_participation_rate IS NOT NULL
    );
