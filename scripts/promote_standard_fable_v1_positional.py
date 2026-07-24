"""Rebuild active Standard RB, WR, and TE boards through the shared safety layer."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os

from google.cloud import bigquery


WRITE_GATE = "ALLOW_STANDARD_FABLE_POSITIONAL_REBUILD"


def build_sql(project: str, brain: str, metrics: str, version: str) -> str:
    live = f"`{project}.{brain}.analytics_pigskin_rankings`"
    history = f"`{project}.{brain}.analytics_pigskin_rankings_history`"
    safety = f"`{project}.{metrics}.v_ranking_post_formula_safety`"
    rb = f"`{project}.{metrics}.v_rb_fable_01_scored_seasons`"
    wr = f"`{project}.{metrics}.standard_wr_fable_v1_post_formula_review`"
    wr_scored = f"`{project}.{metrics}.v_wr_fable_v1_current_candidates`"
    te = f"`{project}.{metrics}.v_te_fable_v1a_scored_seasons`"
    columns = """
  ranking_version, generated_at, adjudicated_at, season, ranking_phase, format, position, rank, tier,
  player_id, player_name, current_team, stat_season, ranking_score, raw_ranking_score,
  candidate_rank, candidate_ranking_score, rank_rationale, pigskin_verdict, what_would_change_mind,
  risk_flags, model_name, prompt_version, data_snapshot_label, is_active,
  sleeper_player_id, sleeper_team, sleeper_active, sleeper_status, sleeper_injury_status,
  sleeper_depth_chart_position, sleeper_depth_chart_order, ranking_eligibility, rank_source,
  model_run_id, scoring_profile_id, league_type_id, roster_format_id, llm_adjustment_code,
  llm_adjustment_detail, llm_adjustment_evidence, llm_estimated_games_missed, llm_rank_delta
"""
    return f"""
ASSERT (
  SELECT COUNT(*) = 85 AND COUNTIF(context.team IS NULL) = 0
  FROM {rb} source
  JOIN {safety} context ON context.position='RB' AND context.gsis_id=source.candidate_internal_player_id
  WHERE source.season=2025 AND source.rb_fable_01_score IS NOT NULL
    AND context.current_board_rank_eligible
) AS 'Standard RB safety preflight failed';

ASSERT (
  SELECT COUNT(*) = 100 AND COUNTIF(current_team IS NULL OR teamless_unranked OR sleeper_hard_review) = 0
  FROM {wr}
) AS 'Standard WR repaired-board preflight failed';

ASSERT (
  SELECT COUNT(*) >= 35 AND COUNTIF(context.team IS NULL) = 0
  FROM {te} source
  JOIN {safety} context ON context.position='TE' AND context.gsis_id=source.candidate_internal_player_id
  WHERE source.season=2025 AND source.te_fable_v1a_no_man_score IS NOT NULL
    AND context.current_board_rank_eligible
) AS 'Standard TE safety preflight failed';

BEGIN TRANSACTION;

INSERT INTO {history}
SELECT current_rows.*
FROM {live} current_rows
WHERE current_rows.is_active
  AND current_rows.scoring_profile_id='standard'
  AND current_rows.position IN ('RB','WR','TE')
  AND NOT EXISTS (
    SELECT 1 FROM {history} archived
    WHERE archived.ranking_version=current_rows.ranking_version
      AND archived.player_id=current_rows.player_id
      AND archived.position=current_rows.position
      AND archived.scoring_profile_id=current_rows.scoring_profile_id
  );

UPDATE {live}
SET is_active=FALSE
WHERE is_active AND scoring_profile_id='standard' AND position IN ('RB','WR','TE');

INSERT INTO {live} ({columns})
WITH base AS (
  SELECT
    source.*,
    ROW_NUMBER() OVER (ORDER BY source.rb_fable_01_score DESC, source.player_name) AS formula_rank
  FROM {rb} source
  WHERE source.season=2025 AND source.rb_fable_01_score IS NOT NULL
), eligible AS (
  SELECT base.*, context, base.rb_fable_01_score + context.post_formula_adjustment AS adjusted_score
  FROM base
  JOIN {safety} context ON context.position='RB' AND context.gsis_id=base.candidate_internal_player_id
  WHERE context.current_board_rank_eligible
), ranked AS (
  SELECT eligible.*,
    ROW_NUMBER() OVER (ORDER BY adjusted_score DESC, formula_rank, player_name) AS final_rank,
    MIN(adjusted_score) OVER () AS min_score,
    MAX(adjusted_score) OVER () AS max_score
  FROM eligible
)
SELECT
  '{version}', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 2026, 'preseason', 'Standard', 'RB', final_rank,
  CASE WHEN final_rank<=5 THEN 'elite' WHEN final_rank<=12 THEN 'front-line starter'
       WHEN final_rank<=30 THEN 'starter' WHEN final_rank<=40 THEN 'flex or matchup' ELSE 'depth' END,
  candidate_internal_player_id, player_name, context.team, 2025,
  ROUND(50 + 49*SAFE_DIVIDE(adjusted_score-min_score,max_score-min_score),1), rb_fable_01_score,
  formula_rank, rb_fable_01_score,
  FORMAT('RB Fable v1 components: opportunity %+.3f, efficiency %+.3f, TD blend %+.3f, age/availability %+.3f. %s',
    opportunity_component, efficiency_component, scoring_component, age_availability_component,
    context.post_formula_adjustment_detail),
  CONCAT(
    FORMAT('%s earns RB%d on %.1f non-garbage-time touches per game plus %.1f%% target share. ',
      player_name, final_rank, non_garbage_time_touches_per_game, target_share),
    FORMAT('His %.1f red-zone touches and %.2f blended TDs per game support the scoring case',
      red_zone_touches_per_game, blended_td_per_game),
    CASE WHEN epa_per_touch < 0
      THEN FORMAT(', while %.2f EPA per touch limits the efficiency boost.', epa_per_touch)
      ELSE FORMAT('; %+.2f EPA per touch adds efficiency support.', epa_per_touch)
    END
  ),
  'Revisit on a verified team, depth-chart, injury, or role change.',
  NULLIF(context.review_flags_text,''), 'rb_fable_01', 'deterministic-no-llm',
  'advanced_situational_2025+current_sleeper', TRUE,
  CAST(context.sleeper_player_id AS STRING), context.team, context.active, context.status,
  context.injury_status, context.depth_chart_position, context.depth_chart_order,
  context.ranking_eligibility, 'rb_fable_v1_formula', '{version}', 'standard', 'redraft', 'one_qb',
  IF(context.post_formula_adjustment=0,'NO_ADJUSTMENT',context.post_formula_adjustment_code),
  context.post_formula_adjustment_detail,
  FORMAT('Sleeper snapshot %t; depth order %d',context.fetched_at,context.depth_chart_order),
  NULL, formula_rank-final_rank
FROM ranked;

INSERT INTO {live} ({columns})
WITH scored AS (
  SELECT source.*,
    ROW_NUMBER() OVER (ORDER BY source.te_fable_v1a_no_man_score DESC, source.player_name) AS formula_rank
  FROM {te} source
  WHERE source.season=2025 AND source.te_fable_v1a_no_man_score IS NOT NULL
), eligible AS (
  SELECT scored.*, context,
    scored.te_fable_v1a_no_man_score + context.post_formula_adjustment AS adjusted_score
  FROM scored
  JOIN {safety} context ON context.position='TE' AND context.gsis_id=scored.candidate_internal_player_id
  WHERE context.current_board_rank_eligible
), reranked AS (
  SELECT eligible.*,
    ROW_NUMBER() OVER (ORDER BY adjusted_score DESC, formula_rank, player_name) AS final_rank
  FROM eligible
), ranked AS (
  SELECT reranked.*,
    MIN(adjusted_score) OVER () AS min_score,
    MAX(adjusted_score) OVER () AS max_score
  FROM reranked
  WHERE final_rank<=35
)
SELECT
  '{version}', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 2026, 'preseason', 'Standard', 'TE', final_rank,
  CASE WHEN final_rank<=5 THEN 'elite' WHEN final_rank<=12 THEN 'front-line starter'
       WHEN final_rank<=24 THEN 'starter' ELSE 'flex or matchup' END,
  candidate_internal_player_id, player_name, context.team, 2025,
  ROUND(50 + 49*SAFE_DIVIDE(adjusted_score-min_score,max_score-min_score),1), te_fable_v1a_no_man_score,
  formula_rank, te_fable_v1a_no_man_score,
  FORMAT('TE Fable v1.0a no-man: opportunity %+.3f, efficiency %+.3f, TD %+.3f, age/availability %+.3f. %s',
    opportunity_component, no_man_efficiency_component, scoring_component, age_availability_component,
    context.post_formula_adjustment_detail),
  CONCAT(
    FORMAT('%s earns TE%d with %.1f routes per game, %.1f%% target share and %.2f red-zone targets per game. ',
      player_name, final_rank, routes_per_game, target_share, red_zone_targets_per_game),
    CASE
      WHEN yprr >= 1.80 THEN FORMAT('His %.2f YPRR and %.2f targets per route reinforce the efficiency case.', yprr, targets_per_route_run)
      WHEN yprr >= 1.40 THEN FORMAT('His %.2f YPRR and %.2f targets per route support the efficiency case.', yprr, targets_per_route_run)
      ELSE FORMAT('At %.2f YPRR, route volume carries more of the ranking.', yprr)
    END,
    CASE
      WHEN games_played_rate < 0.80
        THEN FORMAT(' Availability is the clear risk after a %.0f%% games-played rate.', 100*games_played_rate)
      ELSE FORMAT(' %.2f blended TDs per game shape the scoring outlook.', blended_td_per_game)
    END
  ),
  'Revisit on a verified team, depth-chart, injury, or role change.',
  NULLIF(context.review_flags_text,''), 'te_fable_v1a_no_man', 'deterministic-no-llm',
  'advanced_situational_2025+current_sleeper', TRUE,
  CAST(context.sleeper_player_id AS STRING), context.team, context.active, context.status,
  context.injury_status, context.depth_chart_position, context.depth_chart_order,
  context.ranking_eligibility, 'te_fable_v1a_no_man_formula', '{version}', 'standard', 'redraft', 'one_qb',
  IF(context.post_formula_adjustment=0,'NO_ADJUSTMENT',context.post_formula_adjustment_code),
  context.post_formula_adjustment_detail,
  FORMAT('Sleeper snapshot %t; depth order %d',context.fetched_at,context.depth_chart_order),
  NULL, formula_rank-final_rank
FROM ranked;

INSERT INTO {live} ({columns})
WITH ranked AS (
  SELECT board.*,
    metrics.target_share, metrics.wopr, metrics.yprr,
    metrics.non_garbage_time_targets_per_game, metrics.red_zone_targets_per_game,
    metrics.blended_td_per_game, metrics.games_played_rate,
    metrics.games_played, metrics.targets, metrics.prior_v1_score,
    -- Narrative-only inputs for the veteran carry-forward rationale; both live
    -- in the candidates view rather than the review table, so they must be
    -- carried through this CTE for the outer FORMAT calls to resolve.
    metrics.prior_v1_age_availability_component, metrics.age_availability_component,
    MIN(post_formula_score) OVER () AS min_score,
    MAX(post_formula_score) OVER () AS max_score
  FROM {wr} board
  JOIN {wr_scored} metrics
    ON metrics.season=2025 AND metrics.candidate_internal_player_id=board.player_id
)
SELECT
  '{version}', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 2026, 'preseason', 'Standard', 'WR', final_rank,
  CASE WHEN final_rank<=5 THEN 'elite' WHEN final_rank<=12 THEN 'front-line starter'
       WHEN final_rank<=30 THEN 'starter' WHEN final_rank<=50 THEN 'flex or matchup' ELSE 'depth' END,
  player_id, player_name, current_team, 2025,
  ROUND(50 + 49*SAFE_DIVIDE(post_formula_score-min_score,max_score-min_score),1), formula_score,
  formula_rank, formula_score,
  CASE
    WHEN player_id = '00-0039849' THEN FORMAT(
      'WR Fable v1 identity repair: the verified 2025 row qualified on %d games and %.0f targets with raw score %.4f. %s Formula weights did not change.',
      games_played, targets, formula_score, final_adjustment_detail)
    WHEN coverage_method = 'PRIOR_QUALIFIED_VETERAN_CARRY_FORWARD'
      THEN FORMAT(
        'WR Fable v1 veteran coverage: %d qualified score %.4f. Replaced prior availability %.4f with current two-year availability %.4f, yielding raw %.4f. Latest sample was %d games and %.0f targets, below the 6-game or 40-target gate. %s Injury is review-only. Formula weights unchanged.',
        score_source_season, prior_v1_score, prior_v1_age_availability_component,
        age_availability_component, formula_score, games_played, targets, final_adjustment_detail)
    ELSE CONCAT('WR Fable v1. ', final_adjustment_detail)
  END,
  CASE
    WHEN coverage_method = 'PRIOR_QUALIFIED_VETERAN_CARRY_FORWARD' THEN CONCAT(
      FORMAT('%s receives veteran coverage at WR%d because %d games and %.0f targets miss the one-season threshold. ',
        player_name, final_rank, games_played, targets),
      FORMAT('His qualified %d Fable score is carried forward with the current availability component. ',
        score_source_season),
      FORMAT('The short sample still shows %.1f%% target share and %.2f YPRR; availability remains the risk.',
        target_share, yprr)
    )
    ELSE CONCAT(
      FORMAT('%s lands at WR%d on a %.1f%% target share, %.2f WOPR and %.1f non-garbage-time targets per game. ',
        player_name, final_rank, target_share, wopr, non_garbage_time_targets_per_game),
      CASE
        WHEN yprr >= 2.30 THEN FORMAT('His %.2f YPRR reinforces the efficiency case.', yprr)
        WHEN yprr >= 2.00 THEN FORMAT('His %.2f YPRR supports the efficiency case.', yprr)
        ELSE FORMAT('At %.2f YPRR, volume carries more of the ranking.', yprr)
      END,
      CASE
        WHEN REGEXP_CONTAINS(COALESCE(review_flags_json,''), r'INJURY_UNCERTAIN') OR games_played_rate < 0.80
          THEN FORMAT(' Availability is the clear risk after a %.0f%% games-played rate.', 100*games_played_rate)
        ELSE FORMAT(' %.2f red-zone targets per game and %.2f blended TDs per game shape the scoring outlook.',
          red_zone_targets_per_game, blended_td_per_game)
      END
    )
  END,
  'Revisit on a verified team, depth-chart, injury, or role change.',
  NULLIF(review_flags_json,'[]'), 'wr_fable_v1', 'deterministic-no-llm',
  'advanced_situational_2025+current_sleeper', TRUE,
  CAST(sleeper_player_id AS STRING), current_team, sleeper_active, sleeper_status,
  sleeper_injury_status, sleeper_depth_chart_position, sleeper_depth_chart_order,
  ranking_eligibility, 'wr_fable_v1_formula', '{version}', 'standard', 'redraft', 'one_qb',
  final_adjustment_code, final_adjustment_detail,
  CASE
    WHEN player_id = '00-0039849' THEN FORMAT(
      'Identity override: source-local d96487d (marvin-harrison) verified to GSIS 00-0039849; reason MARVIN_HARRISON_JR_SOURCE_ID; 2025 games %d; targets %.0f; raw score %.4f; formula weights unchanged. Sleeper snapshot %t; depth order %d.',
      games_played, targets, formula_score, sleeper_fetched_at, sleeper_depth_chart_order)
    WHEN coverage_method = 'PRIOR_QUALIFIED_VETERAN_CARRY_FORWARD' THEN FORMAT(
      'Coverage PRIOR_QUALIFIED_VETERAN_CARRY_FORWARD; source season %d; prior score %.4f; prior availability component %.4f; current two-year availability component %.4f; raw score %.4f; latest games %d; targets %.0f; rookie fallback excluded; injury status review-only; formula weights unchanged. Sleeper snapshot %t; depth order %d.',
      score_source_season, prior_v1_score, prior_v1_age_availability_component,
      age_availability_component, formula_score, games_played, targets,
      sleeper_fetched_at, sleeper_depth_chart_order)
    ELSE FORMAT('Sleeper snapshot %t; depth order %d',sleeper_fetched_at,sleeper_depth_chart_order)
  END,
  NULL, formula_rank-final_rank
FROM ranked;

ASSERT NOT EXISTS (
  SELECT 1 FROM {live}
  WHERE is_active AND scoring_profile_id='standard' AND position IN ('RB','WR','TE')
    AND current_team IS NULL
) AS 'Teamless player entered an active Standard board';

ASSERT NOT EXISTS (
  SELECT 1
  FROM (
    SELECT position, COUNT(*) row_count, COUNT(DISTINCT rank) distinct_ranks, MIN(rank) min_rank, MAX(rank) max_rank
    FROM {live}
    WHERE is_active AND scoring_profile_id='standard' AND position IN ('RB','WR','TE')
    GROUP BY position
  )
  WHERE row_count!=distinct_ranks OR min_rank!=1 OR max_rank!=row_count
) AS 'Active Standard position ranks are not contiguous';

ASSERT (
  SELECT COUNT(*) = 3
    AND STRING_AGG(player_name, '|' ORDER BY rank) = 'A.J. Brown|Justin Jefferson|Garrett Wilson'
  FROM {live}
  WHERE is_active AND scoring_profile_id='standard' AND position='WR'
    AND player_name IN ('A.J. Brown', 'Justin Jefferson', 'Garrett Wilson')
) AS 'Approved Standard WR elite order was not preserved';

COMMIT TRANSACTION;
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--brain-dataset", default="fantasy_football_brain")
    parser.add_argument("--metrics-dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    version = datetime.now(timezone.utc).strftime("standard-fable-v1-safety-%Y%m%d%H%M%S")
    sql = build_sql(args.project, args.brain_dataset, args.metrics_dataset, version)
    client = bigquery.Client(project=args.project)
    if not args.apply:
        job = client.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
        print(json.dumps({"writes": False, "version": version, "bytes": job.total_bytes_processed}, indent=2))
        return 0
    if os.environ.get(WRITE_GATE, "").lower() != "true":
        raise RuntimeError(f"{WRITE_GATE}=true is required")
    client.query(sql).result()
    rows = [dict(row) for row in client.query(f"""
SELECT position, COUNT(*) AS row_count, MIN(rank) AS min_rank, MAX(rank) AS max_rank,
  COUNTIF(current_team IS NULL) AS teamless_rows
FROM `{args.project}.{args.brain_dataset}.analytics_pigskin_rankings`
WHERE is_active AND scoring_profile_id='standard' AND position IN ('RB','WR','TE')
GROUP BY position ORDER BY position
""").result()]
    print(json.dumps({"writes": True, "version": version, "positions": rows}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
