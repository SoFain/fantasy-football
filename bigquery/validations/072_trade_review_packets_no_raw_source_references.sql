-- Validation helper. Render placeholders before running manually.
-- Expected result: raw_source_reference_count = 0

SELECT
    COUNTIF(REGEXP_CONTAINS(
        LOWER(CONCAT(COALESCE(packet_json, ''), ' ', COALESCE(source_freshness_json, ''))),
        r'(market_values|weekly_metrics|sleeper_roster_players|sleeper_available_players|sleeper_lineups)'
    )) AS raw_source_reference_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_review_packets`;
