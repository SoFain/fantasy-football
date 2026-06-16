-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_identity_rate should be reviewed and reduced over time.

SELECT
    'compat_trade_assets_current_identity_coverage' AS validation_name,
    COUNT(*) AS row_count,
    COUNTIF(player_id_internal IS NULL) AS missing_player_id_internal_count,
    SAFE_DIVIDE(COUNTIF(player_id_internal IS NULL), COUNT(*)) AS missing_identity_rate
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_assets_current`;
