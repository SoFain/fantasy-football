-- Validation helper. Render placeholders before running manually.
-- Expected result: orphan_item_rows = 0

SELECT COUNT(*) AS orphan_item_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.content_brief_items` items
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.content_briefs` briefs
  ON items.content_brief_id = briefs.content_brief_id
WHERE briefs.content_brief_id IS NULL;
