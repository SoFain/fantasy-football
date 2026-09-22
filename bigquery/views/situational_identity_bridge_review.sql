-- Review-only bridge from source-local situational identities to official warehouse IDs.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.situational_identity_bridge_review` AS
WITH source_candidates AS (
  SELECT
    source_position,
    situational_player_id,
    player_slug,
    player_name,
    seasons_seen,
    teams_seen,
    REGEXP_REPLACE(LOWER(player_name), r'[^a-z0-9]', '') AS normalized_source_name
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.situational_player_identity_candidates`
),
bridge_names AS (
  SELECT
    REGEXP_REPLACE(LOWER(full_name), r'[^a-z0-9]', '') AS normalized_source_name,
    ARRAY_AGG(DISTINCT gsis_id IGNORE NULLS) AS gsis_ids,
    MAX(source_confidence) AS source_confidence
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.player_identity_bridge`
  WHERE position = 'RB'
  GROUP BY normalized_source_name
),
staging_matches AS (
  SELECT
    source.situational_player_id,
    source.player_slug,
    ARRAY_AGG(DISTINCT staging.player_id_internal IGNORE NULLS) AS player_ids,
    MAX(staging.identity_confidence) AS identity_confidence
  FROM source_candidates AS source
  JOIN `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.stg_player_identity` AS staging
    ON source.source_position = 'RB'
   AND staging.position = 'RB'
   AND staging.season IN UNNEST(source.seasons_seen)
   AND staging.team IN UNNEST(source.teams_seen)
   AND REGEXP_REPLACE(LOWER(staging.player_name), r'[^a-z0-9]', '') = source.normalized_source_name
  GROUP BY source.situational_player_id, source.player_slug
),
resolved AS (
  SELECT
    source.* EXCEPT(normalized_source_name),
    IFNULL(ARRAY_LENGTH(bridge.gsis_ids), 0) AS exact_match_count,
    IFNULL(ARRAY_LENGTH(staging.player_ids), 0) AS name_team_season_match_count,
    CASE
      WHEN ARRAY_LENGTH(bridge.gsis_ids) = 1 THEN bridge.gsis_ids[SAFE_OFFSET(0)]
      WHEN IFNULL(ARRAY_LENGTH(bridge.gsis_ids), 0) = 0
       AND ARRAY_LENGTH(staging.player_ids) = 1 THEN staging.player_ids[SAFE_OFFSET(0)]
    END AS candidate_internal_player_id,
    CASE
      WHEN ARRAY_LENGTH(bridge.gsis_ids) = 1 THEN 'EXACT_SLUG_MATCH'
      WHEN IFNULL(ARRAY_LENGTH(bridge.gsis_ids), 0) = 0
       AND ARRAY_LENGTH(staging.player_ids) = 1
       AND staging.identity_confidence >= 0.90 THEN 'NAME_TEAM_SEASON_MATCH'
      WHEN ARRAY_LENGTH(bridge.gsis_ids) > 1 OR ARRAY_LENGTH(staging.player_ids) > 1 THEN 'MULTIPLE_CANDIDATES'
      ELSE 'UNMAPPED'
    END AS identity_status,
    CASE
      WHEN ARRAY_LENGTH(bridge.gsis_ids) = 1 THEN LEAST(IFNULL(bridge.source_confidence, 0.95), 0.99)
      WHEN IFNULL(ARRAY_LENGTH(bridge.gsis_ids), 0) = 0
       AND ARRAY_LENGTH(staging.player_ids) = 1 THEN staging.identity_confidence
      ELSE 0.0
    END AS identity_confidence
  FROM source_candidates AS source
  LEFT JOIN bridge_names AS bridge USING (normalized_source_name)
  LEFT JOIN staging_matches AS staging USING (situational_player_id, player_slug)
)
SELECT
  *,
  identity_status IN ('UNMAPPED', 'MULTIPLE_CANDIDATES') AS manual_review_required,
  exact_match_count > 1
    OR (exact_match_count = 0 AND name_team_season_match_count > 1) AS duplicate_identity_collision,
  CASE
    WHEN identity_status = 'UNMAPPED' THEN 'No collision-safe warehouse identity match.'
    WHEN identity_status = 'MULTIPLE_CANDIDATES' THEN 'Ambiguous identity; excluded from formula joins.'
    WHEN identity_status = 'NAME_TEAM_SEASON_MATCH' THEN 'Unique normalized name, team, and season match.'
    ELSE 'Unique normalized full-name match with official GSIS ID.'
  END AS notes
FROM resolved;
