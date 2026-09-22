-- Additive current Sleeper player snapshot lane for roster/status context.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.raw_sleeper_players_snapshot` (
    snapshot_id STRING NOT NULL,
    snapshot_at TIMESTAMP NOT NULL,
    snapshot_year INT64 NOT NULL,
    sleeper_player_id STRING NOT NULL,
    gsis_id STRING,
    sportradar_id STRING,
    fantasy_data_id STRING,
    player_name STRING,
    first_name STRING,
    last_name STRING,
    search_full_name STRING,
    position STRING,
    team STRING,
    active BOOL,
    status STRING,
    injury_status STRING,
    fantasy_positions_json STRING,
    depth_chart_position STRING,
    depth_chart_order INT64,
    search_rank INT64,
    years_exp INT64,
    metadata_json STRING,
    raw_payload_json STRING,
    source_system STRING,
    source_url STRING,
    source_version STRING,
    loaded_at TIMESTAMP,
    loaded_by STRING,
    row_hash STRING
)
PARTITION BY RANGE_BUCKET(snapshot_year, GENERATE_ARRAY(2020, 2035, 1))
CLUSTER BY snapshot_at, sleeper_player_id, team;

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_player_context_current` AS
WITH latest_snapshot AS (
  SELECT MAX(snapshot_at) AS latest_snapshot_at
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.raw_sleeper_players_snapshot`
),
latest_raw AS (
  SELECT raw_snapshot.*
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.raw_sleeper_players_snapshot` raw_snapshot
  JOIN latest_snapshot
    ON raw_snapshot.snapshot_at = latest_snapshot.latest_snapshot_at
),
identity_bridge AS (
  SELECT
    player_id_internal,
    gsis_id,
    sleeper_player_id,
    display_name,
    current_team
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_identity_bridge`
)
SELECT
  raw_snapshot.snapshot_id,
  raw_snapshot.snapshot_at,
  raw_snapshot.snapshot_year,
  COALESCE(identity_bridge.player_id_internal, raw_snapshot.gsis_id, raw_snapshot.sleeper_player_id) AS player_id_internal,
  raw_snapshot.sleeper_player_id,
  raw_snapshot.gsis_id,
  raw_snapshot.player_name,
  COALESCE(identity_bridge.display_name, raw_snapshot.player_name) AS display_name,
  raw_snapshot.position,
  raw_snapshot.team AS sleeper_current_team,
  identity_bridge.current_team AS identity_current_team,
  raw_snapshot.active,
  raw_snapshot.status,
  raw_snapshot.injury_status,
  raw_snapshot.fantasy_positions_json,
  raw_snapshot.depth_chart_position,
  raw_snapshot.depth_chart_order,
  raw_snapshot.search_rank,
  raw_snapshot.years_exp,
  TO_JSON_STRING(STRUCT(raw_snapshot.snapshot_at AS raw_sleeper_players_snapshot_at)) AS source_freshness_json,
  TO_JSON_STRING(ARRAY_CONCAT(
    IF(raw_snapshot.team IS NULL, ['missing_sleeper_current_team'], []),
    IF(raw_snapshot.gsis_id IS NULL, ['missing_gsis_id'], []),
    IF(identity_bridge.player_id_internal IS NULL, ['missing_identity_bridge_match'], [])
  )) AS missing_flags_json,
  TO_JSON_STRING(STRUCT(
    'raw_sleeper_players_snapshot' AS source_table,
    raw_snapshot.source_url AS source_url,
    raw_snapshot.source_version AS source_version,
    raw_snapshot.snapshot_id AS snapshot_id
  )) AS source_provenance_json,
  raw_snapshot.loaded_at
FROM latest_raw raw_snapshot
LEFT JOIN identity_bridge
  ON (
    raw_snapshot.sleeper_player_id IS NOT NULL
    AND identity_bridge.sleeper_player_id = raw_snapshot.sleeper_player_id
  )
  OR (
    raw_snapshot.gsis_id IS NOT NULL
    AND identity_bridge.gsis_id = raw_snapshot.gsis_id
  )
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY raw_snapshot.snapshot_id, raw_snapshot.sleeper_player_id
  ORDER BY
    IF(identity_bridge.sleeper_player_id = raw_snapshot.sleeper_player_id, 0, 1),
    IF(identity_bridge.gsis_id = raw_snapshot.gsis_id, 0, 1),
    identity_bridge.player_id_internal
) = 1;
