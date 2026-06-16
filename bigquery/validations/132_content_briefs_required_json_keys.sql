-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_required_json_keys = 0

SELECT COUNT(*) AS rows_missing_required_json_keys
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.content_briefs`
WHERE JSON_VALUE(brief_json, '$.title') IS NULL
   OR JSON_VALUE(brief_json, '$.segment_objective') IS NULL
   OR JSON_VALUE(brief_json, '$.brief_type') IS NULL
   OR JSON_QUERY(brief_json, '$.llm_prompt_payload_json') IS NULL
   OR JSON_QUERY(brief_json, '$.items') IS NULL
   OR JSON_QUERY(brief_json, '$.do_not_overclaim_caveats') IS NULL;
