-- Validation helper. Render placeholders before running manually.
-- Expected result: zero rows for latest loaded Sleeper roster snapshot.

WITH latest_snapshot AS (
    SELECT MAX(snapshot_at) AS snapshot_at
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_roster_players`
),
latest_roster_players AS (
    SELECT rp.*
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_roster_players` rp
    JOIN latest_snapshot
        USING (snapshot_at)
),
matched AS (
    SELECT
        rp.league_id,
        rp.roster_id,
        rp.player_name,
        rp.position,
        rp.team,
        rp.sleeper_player_id,
        rp.gsis_id,
        b.player_id_internal
    FROM latest_roster_players rp
    LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.player_identity_bridge` b
        ON (rp.gsis_id IS NOT NULL AND rp.gsis_id = b.gsis_id)
        OR (rp.sleeper_player_id IS NOT NULL AND rp.sleeper_player_id = b.sleeper_player_id)
        OR (
            REGEXP_REPLACE(REGEXP_REPLACE(LOWER(rp.player_name), r'\s+(jr|sr|ii|iii|iv|v)\.?$', ''), r'[^a-z0-9]+', '') = b.normalized_name
            AND rp.position = b.position
            AND rp.team = b.current_team
        )
)
SELECT
    'sleeper_roster_players_missing_bridge_rows' AS validation_name,
    league_id,
    roster_id,
    player_name,
    position,
    team,
    sleeper_player_id,
    gsis_id
FROM matched
WHERE player_id_internal IS NULL
ORDER BY league_id, roster_id, position, player_name;
