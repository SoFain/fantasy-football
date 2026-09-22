-- Validation helper. Render placeholders before running manually.
-- is_vacant must agree with coach_name: vacant iff no name.
-- Expected result: zero rows

SELECT team_abbr, role, coach_name, is_vacant
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.coaching_staff_current`
WHERE is_vacant != (coach_name IS NULL)
LIMIT 100;
