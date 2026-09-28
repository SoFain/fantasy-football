-- Validation helper. Render placeholders before running manually.
-- Surfaces how much of the staff data is still pending verification. Non-zero
-- is expected while the CSV is being populated from the source page; it should
-- trend to zero as rows are confirmed.
-- Expected result: pending_rows should be low

SELECT COUNTIF(verification_status = 'pending') AS pending_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.coaching_staff_current`;
