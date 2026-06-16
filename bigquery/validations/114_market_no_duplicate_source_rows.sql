-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_source_rows = 0

WITH source_rows AS (
    SELECT
        snapshot_id,
        source_id,
        source_player_key,
        source_player_name,
        position,
        team,
        prop_market,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.market_consensus_player_values`
    GROUP BY 1, 2, 3, 4, 5, 6, 7
)
SELECT COUNTIF(row_count > 1) AS duplicate_source_rows
FROM source_rows;
