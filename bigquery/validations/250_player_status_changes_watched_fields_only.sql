-- Validation helper. Render placeholders before running manually.
-- Rows outside the watched set mean the detector and this contract disagree.
-- Expected result: zero rows

SELECT field_name, COUNT(*) AS row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_status_changes`
WHERE field_name NOT IN (
    'team', 'status', 'injury_status',
    'depth_chart_position', 'depth_chart_order'
)
GROUP BY field_name;
