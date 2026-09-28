-- Validation helper. Render placeholders before running manually.
-- Expected result: player_identity_warning_rows = 0

WITH coverage AS (
    SELECT
        COUNT(*) AS total_rows,
        COUNTIF(UPPER(position) IN ('QB', 'RB', 'WR', 'TE', 'K', 'DEF')) AS player_rows,
        COUNTIF(UPPER(position) NOT IN ('QB', 'RB', 'WR', 'TE', 'K', 'DEF') OR position IS NULL) AS non_player_asset_rows,
        COUNTIF(player_id_internal IS NULL) AS rows_missing_player_id_internal,
        COUNTIF(player_id_internal IS NULL AND UPPER(position) IN ('QB', 'RB', 'WR', 'TE', 'K', 'DEF')) AS unresolved_player_rows,
        COUNTIF(player_id_internal IS NULL AND (UPPER(position) NOT IN ('QB', 'RB', 'WR', 'TE', 'K', 'DEF') OR position IS NULL)) AS unresolved_non_player_asset_rows,
        SAFE_DIVIDE(
            COUNTIF(player_id_internal IS NULL AND UPPER(position) IN ('QB', 'RB', 'WR', 'TE', 'K', 'DEF')),
            NULLIF(COUNTIF(UPPER(position) IN ('QB', 'RB', 'WR', 'TE', 'K', 'DEF')), 0)
        ) AS player_identity_missing_rate,
        SAFE_DIVIDE(COUNTIF(player_id_internal IS NULL), NULLIF(COUNT(*), 0)) AS overall_identity_missing_rate,
        ARRAY_AGG(
            IF(
                player_id_internal IS NULL AND UPPER(position) IN ('QB', 'RB', 'WR', 'TE', 'K', 'DEF'),
                STRUCT(
                    source_id,
                    source_player_key,
                    display_name,
                    position,
                    team,
                    rank_overall,
                    rank_position,
                    market_value,
                    missing_data_flags
                ),
                NULL
            )
            IGNORE NULLS
            ORDER BY rank_overall ASC
            LIMIT 20
        ) AS top_unresolved_players
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.market_consensus_baseline_current`
)
SELECT
    IF(player_identity_missing_rate > 0.05, 1, 0) AS player_identity_warning_rows,
    total_rows,
    player_rows,
    non_player_asset_rows,
    rows_missing_player_id_internal,
    unresolved_player_rows,
    unresolved_non_player_asset_rows,
    player_identity_missing_rate,
    overall_identity_missing_rate,
    0.05 AS warning_threshold,
    0.20 AS failure_threshold,
    0.05 AS target_threshold,
    top_unresolved_players
FROM coverage;
