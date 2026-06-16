-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_grain_count = 0.

SELECT
    'compat_trade_assets_current_grain' AS validation_name,
    COUNT(*) AS duplicate_grain_count
FROM (
    SELECT
        COALESCE(player_id_internal, source_player_key, market_player_id) AS asset_key,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        market_snapshot_date,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_assets_current`
    GROUP BY asset_key, scoring_profile_id, league_type_id, roster_format_id, market_snapshot_date
    HAVING row_count > 1
);
