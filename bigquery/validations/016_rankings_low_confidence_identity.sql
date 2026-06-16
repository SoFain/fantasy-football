-- Validation helper. Render placeholders before running manually.
-- Expected result: rows should be reviewed or manually overridden before rankings are trusted.

WITH active_rankings AS (
    SELECT *
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings`
    WHERE COALESCE(is_active, TRUE)
),
matched AS (
    SELECT
        r.position,
        r.rank,
        r.player_name,
        r.player_id,
        r.sleeper_player_id,
        b.player_id_internal,
        b.source_confidence,
        b.match_method,
        b.missing_data_flags
    FROM active_rankings r
    JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.player_identity_bridge` b
        ON (r.player_id IS NOT NULL AND r.player_id = b.gsis_id)
        OR (r.sleeper_player_id IS NOT NULL AND r.sleeper_player_id = b.sleeper_player_id)
        OR (
            REGEXP_REPLACE(REGEXP_REPLACE(LOWER(r.player_name), r'\s+(jr|sr|ii|iii|iv|v)\.?$', ''), r'[^a-z0-9]+', '') = b.normalized_name
            AND r.position = b.position
            AND r.current_team = b.current_team
        )
)
SELECT
    'rankings_low_confidence_identity' AS validation_name,
    position,
    rank,
    player_name,
    player_id_internal,
    source_confidence,
    match_method,
    missing_data_flags
FROM matched
WHERE source_confidence < 0.8
ORDER BY position, rank;
