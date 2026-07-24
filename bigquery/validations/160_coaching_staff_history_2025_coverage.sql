-- Validation helper. Render placeholders before running manually.
-- The 2025 head-coach baseline must cover all 32 teams exactly once.
-- Expected result: team_count = 32

SELECT COUNT(DISTINCT team_abbr) AS team_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.coaching_staff_history`
WHERE season = 2025 AND role = 'head_coach';
