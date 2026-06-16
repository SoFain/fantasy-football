-- Validation helper. Render placeholders before running manually.
-- Expected result: zero rows.

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
        b.player_id_internal
    FROM active_rankings r
    LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.player_identity_bridge` b
        ON (r.player_id IS NOT NULL AND r.player_id = b.gsis_id)
        OR (r.sleeper_player_id IS NOT NULL AND r.sleeper_player_id = b.sleeper_player_id)
        OR (
            REGEXP_REPLACE(REGEXP_REPLACE(LOWER(r.player_name), r'\s+(jr|sr|ii|iii|iv|v)\.?$', ''), r'[^a-z0-9]+', '') = b.normalized_name
            AND r.position = b.position
            AND r.current_team = b.current_team
        )
)
SELECT
    'current_pigskin_rankings_missing_bridge_rows' AS validation_name,
    position,
    rank,
    player_name,
    player_id,
    sleeper_player_id
FROM matched
WHERE player_id_internal IS NULL
ORDER BY position, rank;
