-- Validation helper. Render placeholders before running manually.
-- Expected result: raw_source_reference_count = 0

WITH packet_text AS (
    SELECT CONCAT(COALESCE(packet_json, ''), ' ', COALESCE(source_freshness_json, '')) AS payload
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.fraud_watch_packets`
    UNION ALL
    SELECT CONCAT(COALESCE(packet_json, ''), ' ', COALESCE(source_freshness_json, '')) AS payload
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_breakout_packets`
)
SELECT
    COUNTIF(REGEXP_CONTAINS(
        LOWER(payload),
        r'(weekly_metrics|play_by_play|ngs_passing|ngs_rushing|ngs_receiving|ftn_charting|weekly_snap_counts|injury_reports|sleeper_roster_players|sleeper_available_players|sleeper_lineups)'
    )) AS raw_source_reference_count
FROM packet_text;
