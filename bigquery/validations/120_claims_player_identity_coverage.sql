-- Validation helper. Render placeholders before running manually.
-- Expected result: identity_missing_rate should be reviewed, not always zero.

SELECT
    COUNT(*) AS total_claim_player_rows,
    COUNTIF(player_id_internal IS NULL) AS rows_missing_player_id_internal,
    SAFE_DIVIDE(COUNTIF(player_id_internal IS NULL), COUNT(*)) AS identity_missing_rate
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.fantasy_claim_players`;
