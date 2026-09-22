-- Validation helper. Render placeholders before running manually.
-- triggers_news_check must be true for exactly the news-trigger fields.
-- Expected result: zero rows

SELECT field_name, triggers_news_check, COUNT(*) AS row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_status_changes`
WHERE triggers_news_check
  != (field_name IN ('injury_status', 'team', 'depth_chart_order'))
GROUP BY field_name, triggers_news_check;
