-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_claim_player_rows = 0

WITH grain AS (
    SELECT
        claim_id,
        COALESCE(player_id_internal, source_player_key, display_name) AS player_key,
        player_role_in_claim,
        COALESCE(side, '') AS side,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.fantasy_claim_players`
    GROUP BY 1, 2, 3, 4
)
SELECT COUNTIF(row_count > 1) AS duplicate_claim_player_rows
FROM grain;
