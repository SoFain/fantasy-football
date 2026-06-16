-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_identity_rate should stay low for recent fantasy-relevant rows.

SELECT
    'compat_trade_player_history_identity_coverage' AS validation_name,
    COUNT(*) AS row_count,
    COUNTIF(player_id_internal IS NULL) AS missing_identity_count,
    SAFE_DIVIDE(COUNTIF(player_id_internal IS NULL), COUNT(*)) AS missing_identity_rate
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_player_history`
WHERE scoring_profile_id = 'ppr'
    AND season >= EXTRACT(YEAR FROM CURRENT_DATE()) - 2
    AND total_fantasy_points >= 8;
