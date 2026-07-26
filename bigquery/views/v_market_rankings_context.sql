-- Pigskin-vs-market context for articles and show prep. REVIEW/CONTENT EVIDENCE ONLY.
-- Market perception comes from Sleeper's daily search_rank snapshot (already ingested by the
-- 07:00 ingest-sleeper-news job). This view must never feed a formula, candidate table,
-- promotion, or unified board: market data is not a ranking input, it is quotable context.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_market_rankings_context` AS
WITH sleeper_market AS (
  SELECT
    sleeper_player_id,
    gsis_id,
    player_name AS sleeper_player_name,
    position,
    team AS sleeper_team,
    search_rank AS sleeper_search_rank,
    snapshot_at AS market_snapshot_at,
    RANK() OVER (ORDER BY search_rank) AS market_overall_rank,
    RANK() OVER (PARTITION BY position ORDER BY search_rank) AS market_position_rank
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.sleeper_players_current`
  WHERE position IN ('QB', 'RB', 'WR', 'TE')
    AND active
    AND search_rank IS NOT NULL
    AND search_rank < 9999999
),
boards AS (
  SELECT
    scoring_profile_id,
    position,
    rank AS pigskin_position_rank,
    tier AS pigskin_tier,
    ranking_score AS pigskin_score,
    player_id,
    player_name,
    current_team,
    sleeper_player_id,
    ranking_version
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.analytics_pigskin_rankings`
  WHERE is_active AND position IN ('QB', 'RB', 'WR', 'TE')
)
SELECT
  boards.scoring_profile_id,
  boards.position,
  boards.player_id,
  COALESCE(boards.sleeper_player_id, market.sleeper_player_id) AS sleeper_player_id,
  boards.player_name,
  boards.current_team,
  boards.pigskin_position_rank,
  boards.pigskin_tier,
  boards.pigskin_score,
  boards.ranking_version,
  market.sleeper_search_rank,
  market.market_overall_rank,
  market.market_position_rank,
  market.market_snapshot_at,
  market.market_position_rank - boards.pigskin_position_rank AS market_delta,
  CASE
    WHEN market.market_position_rank IS NULL THEN 'NO_MARKET_SIGNAL'
    WHEN market.market_position_rank - boards.pigskin_position_rank >= 10 THEN 'PIGSKIN_MUCH_HIGHER'
    WHEN market.market_position_rank - boards.pigskin_position_rank >= 4 THEN 'PIGSKIN_HIGHER'
    WHEN boards.pigskin_position_rank - market.market_position_rank >= 10 THEN 'MARKET_MUCH_HIGHER'
    WHEN boards.pigskin_position_rank - market.market_position_rank >= 4 THEN 'MARKET_HIGHER'
    ELSE 'ALIGNED'
  END AS market_gap_bucket,
  'sleeper_search_rank' AS market_source_id
FROM boards
LEFT JOIN sleeper_market AS market
  ON market.sleeper_player_id = boards.sleeper_player_id
  OR (boards.sleeper_player_id IS NULL AND market.gsis_id = boards.player_id);
