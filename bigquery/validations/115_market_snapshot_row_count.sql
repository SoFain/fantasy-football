-- Validation helper. Render placeholders before running manually.
-- Expected result: mismatched_snapshot_row_counts = 0

WITH actual_counts AS (
    SELECT
        snapshot_id,
        source_id,
        COUNT(*) AS actual_row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.market_consensus_player_values`
    GROUP BY 1, 2
)
SELECT COUNTIF(s.row_count != COALESCE(a.actual_row_count, 0)) AS mismatched_snapshot_row_counts
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.market_consensus_snapshots` s
LEFT JOIN actual_counts a
    USING (snapshot_id, source_id);
