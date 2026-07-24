"""Promote reviewed PPR Fable RB/WR/TE queues with archive and rollback provenance."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os

from google.cloud import bigquery


WRITE_GATE="ALLOW_PPR_FABLE_POSITIONAL_PROMOTION"
VERSION="ppr-fable-v1-20260711"


def build_sql(
    project: str,
    dataset: str,
    scoring_profile: str = "ppr",
    metrics_dataset: str = "fantasy_football_advanced_metrics",
    version: str | None = None,
) -> str:
    live=f"`{project}.{dataset}.analytics_pigskin_rankings`"
    history=f"`{project}.{dataset}.analytics_pigskin_rankings_history`"
    prefix="ppr_fable" if scoring_profile=="ppr" else "half_ppr_fable"
    candidates=f"`{project}.{dataset}.{prefix}_rankings_current`"
    safety=f"`{project}.{metrics_dataset}.v_ranking_post_formula_safety`"
    rb=f"`{project}.{metrics_dataset}.v_rb_fable_01_scored_seasons`"
    wr=f"`{project}.{metrics_dataset}.v_wr_fable_v1_current_candidates`"
    te=f"`{project}.{metrics_dataset}.v_te_fable_v1a_scored_seasons`"
    profile_label="PPR" if scoring_profile=="ppr" else "Half-PPR"
    version=version or (VERSION if scoring_profile=="ppr" else "half-ppr-fable-v1-20260711")
    return f"""
ASSERT NOT EXISTS (
  SELECT 1
  FROM {candidates} AS candidate
  LEFT JOIN {safety} AS context
    ON context.gsis_id=candidate.player_id AND context.position=candidate.position
  WHERE (candidate.promotion_eligible OR candidate.recommended_rank IS NOT NULL)
    AND candidate.formula_rank <= CASE candidate.position
      WHEN 'RB' THEN 80 WHEN 'WR' THEN 100 WHEN 'TE' THEN 35
    END
    AND (
      context.gsis_id IS NULL
      OR (context.current_board_rank_eligible AND context.sleeper_hard_review)
    )
) AS 'Selected Fable rows contain unresolved Sleeper roster hard reviews';

CREATE TEMP TABLE promoted AS
WITH templates AS (
  SELECT * FROM {live}
  QUALIFY ROW_NUMBER() OVER(PARTITION BY player_id,position ORDER BY is_active DESC,generated_at DESC)=1
), eligible AS (
  SELECT
    c.*,t,context,
    rb.non_garbage_time_touches_per_game AS rb_touches_per_game,
    rb.target_share AS rb_target_share,
    rb.red_zone_touches_per_game AS rb_red_zone_touches_per_game,
    rb.blended_td_per_game AS rb_blended_td_per_game,
    rb.epa_per_touch AS rb_epa_per_touch,
    wr.target_share AS wr_target_share,
    wr.wopr AS wr_wopr,
    wr.non_garbage_time_targets_per_game AS wr_targets_per_game,
    wr.yprr AS wr_yprr,
    wr.red_zone_targets_per_game AS wr_red_zone_targets_per_game,
    wr.blended_td_per_game AS wr_blended_td_per_game,
    wr.games_played_rate AS wr_games_played_rate,
    wr.games_played AS wr_games_played,
    wr.targets AS wr_targets,
    wr.coverage_method AS wr_coverage_method,
    wr.score_source_season AS wr_score_source_season,
    wr.prior_v1_score AS wr_prior_v1_score,
    wr.prior_v1_age_availability_component AS wr_prior_v1_age_availability_component,
    wr.age_availability_component AS wr_current_age_availability_component,
    te.routes_per_game AS te_routes_per_game,
    te.target_share AS te_target_share,
    te.red_zone_targets_per_game AS te_red_zone_targets_per_game,
    te.yprr AS te_yprr,
    te.targets_per_route_run AS te_targets_per_route_run,
    te.blended_td_per_game AS te_blended_td_per_game,
    te.games_played_rate AS te_games_played_rate
  FROM {candidates} c
  JOIN templates t USING(player_id,position)
  JOIN {safety} context
    ON context.gsis_id=c.player_id AND context.position=c.position
  LEFT JOIN {rb} rb
    ON c.position='RB' AND rb.season=2025 AND rb.candidate_internal_player_id=c.player_id
  LEFT JOIN {wr} wr
    ON c.position='WR' AND wr.candidate_internal_player_id=c.player_id
  LEFT JOIN {te} te
    ON c.position='TE' AND te.season=2025 AND te.candidate_internal_player_id=c.player_id
  WHERE (c.promotion_eligible OR c.recommended_rank IS NOT NULL)
    AND context.current_board_rank_eligible
), adjusted AS (
  SELECT
    c.*,
    formula_score + context.post_formula_adjustment AS adjusted_score,
    ROW_NUMBER() OVER (
      PARTITION BY position
      ORDER BY formula_score + context.post_formula_adjustment DESC, formula_rank, player_name
    ) AS adjusted_formula_rank
  FROM eligible c
), candidate_pre AS (
  SELECT
    adjusted.*,
    ROW_NUMBER() OVER (
      PARTITION BY position
      ORDER BY COALESCE(
        IF(decision_code='FORMULA_DEFAULT',NULL,recommended_rank),
        adjusted_formula_rank
      ),adjusted_formula_rank,formula_rank,player_name
    ) AS new_rank
  FROM adjusted
), candidate_rows AS (
  SELECT
    t.* REPLACE(
      '{version}' AS ranking_version,
      CURRENT_TIMESTAMP() AS generated_at,
      'preseason' AS ranking_phase,
      c.new_rank AS rank,
      context.team AS current_team,
      c.adjusted_score AS ranking_score,
      c.formula_score AS raw_ranking_score,
      GREATEST(0.0,-context.post_formula_adjustment) AS depth_chart_penalty,
      c.formula_rank AS candidate_rank,
      c.formula_score AS candidate_ranking_score,
      CASE
        WHEN c.position='WR' AND c.player_id='00-0039849' THEN FORMAT(
          '{profile_label} WR Fable identity repair: the verified 2025 row qualified on %d games and %.0f targets with raw score %.4f. %s Formula weights did not change.',
          c.wr_games_played,c.wr_targets,c.formula_score,context.post_formula_adjustment_detail)
        WHEN c.position='WR' AND c.wr_coverage_method='PRIOR_QUALIFIED_VETERAN_CARRY_FORWARD' THEN FORMAT(
          '{profile_label} WR Fable veteran coverage: %d qualified score %.4f. Replaced prior availability %.4f with current two-year availability %.4f, yielding raw %.4f. Latest sample was %d games and %.0f targets, below the 6-game or 40-target gate. %s Injury is review-only. Formula weights unchanged.',
          c.wr_score_source_season,c.wr_prior_v1_score,c.wr_prior_v1_age_availability_component,
          c.wr_current_age_availability_component,c.formula_score,c.wr_games_played,c.wr_targets,
          context.post_formula_adjustment_detail)
        ELSE CONCAT('{profile_label} Fable v1; ',context.post_formula_adjustment_detail,' ',c.decision_note)
      END AS rank_rationale,
      CASE c.position
        WHEN 'RB' THEN CONCAT(
          FORMAT('%s earns RB%d in {profile_label} with %.1f%% target share and %.1f non-garbage-time touches per game. ',
            c.player_name,c.new_rank,c.rb_target_share,c.rb_touches_per_game),
          FORMAT('His %.1f red-zone touches and %.2f blended TDs per game support the scoring case',
            c.rb_red_zone_touches_per_game,c.rb_blended_td_per_game),
          CASE WHEN c.rb_epa_per_touch < 0
            THEN FORMAT(', while %.2f EPA per touch limits the efficiency boost.',c.rb_epa_per_touch)
            ELSE FORMAT('; %+.2f EPA per touch adds efficiency support.',c.rb_epa_per_touch)
          END
        )
        WHEN 'WR' THEN CONCAT(
          CASE
            WHEN c.wr_coverage_method = 'PRIOR_QUALIFIED_VETERAN_CARRY_FORWARD' THEN CONCAT(
              FORMAT('%s receives veteran coverage at WR%d in {profile_label} because %d games and %.0f targets miss the one-season threshold. ',
                c.player_name,c.new_rank,c.wr_games_played,c.wr_targets),
              FORMAT('His qualified %d Fable score is carried forward with the current availability component. ',
                c.wr_score_source_season),
              FORMAT('The short sample still shows %.1f%% target share and %.2f YPRR; availability remains the risk.',
                c.wr_target_share,c.wr_yprr)
            )
            ELSE CONCAT(
              FORMAT('%s lands at WR%d in {profile_label} on a %.1f%% target share, %.2f WOPR and %.1f non-garbage-time targets per game. ',
                c.player_name,c.new_rank,c.wr_target_share,c.wr_wopr,c.wr_targets_per_game),
              CASE
                WHEN c.wr_yprr >= 2.30 THEN FORMAT('His %.2f YPRR reinforces the efficiency case.',c.wr_yprr)
                WHEN c.wr_yprr >= 2.00 THEN FORMAT('His %.2f YPRR supports the efficiency case.',c.wr_yprr)
                ELSE FORMAT('At %.2f YPRR, volume carries more of the ranking.',c.wr_yprr)
              END,
              CASE
                WHEN c.wr_games_played_rate < 0.80
                  THEN FORMAT(' Availability is the clear risk after a %.0f%% games-played rate.',100*c.wr_games_played_rate)
                ELSE FORMAT(' %.2f red-zone targets and %.2f blended TDs per game shape the scoring outlook.',
                  c.wr_red_zone_targets_per_game,c.wr_blended_td_per_game)
              END
            )
          END
        )
        WHEN 'TE' THEN CONCAT(
          FORMAT('%s earns TE%d in {profile_label} with %.1f routes per game, %.1f%% target share and %.2f red-zone targets per game. ',
            c.player_name,c.new_rank,c.te_routes_per_game,c.te_target_share,c.te_red_zone_targets_per_game),
          CASE
            WHEN c.te_yprr >= 1.80 THEN FORMAT('His %.2f YPRR and %.2f targets per route reinforce the efficiency case.',c.te_yprr,c.te_targets_per_route_run)
            WHEN c.te_yprr >= 1.40 THEN FORMAT('His %.2f YPRR and %.2f targets per route support the efficiency case.',c.te_yprr,c.te_targets_per_route_run)
            ELSE FORMAT('At %.2f YPRR, route volume carries more of the ranking.',c.te_yprr)
          END,
          CASE
            WHEN c.te_games_played_rate < 0.80
              THEN FORMAT(' Availability is the clear risk after a %.0f%% games-played rate.',100*c.te_games_played_rate)
            ELSE FORMAT(' %.2f blended TDs per game shape the scoring outlook.',c.te_blended_td_per_game)
          END
        )
      END AS pigskin_verdict,
      ARRAY_TO_STRING(ARRAY(
        SELECT flag FROM UNNEST([
          NULLIF(c.risk_flags,''),
          NULLIF(context.review_flags_text,''),
          c.decision_code
        ]) flag WHERE flag IS NOT NULL
      ),'; ') AS risk_flags,
      context.sleeper_player_id AS sleeper_player_id,
      context.team AS sleeper_team,
      context.active AS sleeper_active,
      context.status AS sleeper_status,
      context.injury_status AS sleeper_injury_status,
      context.depth_chart_position AS sleeper_depth_chart_position,
      context.depth_chart_order AS sleeper_depth_chart_order,
      context.ranking_eligibility AS ranking_eligibility,
      'ppr_fable_v1_formula' AS rank_source,
      'deterministic_ppr_fable_v1' AS model_name,
      'ppr-fable-v1' AS prompt_version,
      TRUE AS is_active,
      '{scoring_profile}' AS scoring_profile_id,
      'redraft' AS league_type_id,
      'one_qb' AS roster_format_id,
      CONCAT('{scoring_profile}-fable-v1-',FORMAT_TIMESTAMP('%Y%m%dT%H%M%SZ',CURRENT_TIMESTAMP())) AS model_run_id,
      IF(context.post_formula_adjustment=0.0,'NO_ADJUSTMENT','CURRENT_ROLE') AS llm_adjustment_code,
      context.post_formula_adjustment_detail AS llm_adjustment_detail,
      CASE
        WHEN c.position='WR' AND c.player_id='00-0039849' THEN FORMAT(
          'Identity override: source-local d96487d (marvin-harrison) verified to GSIS 00-0039849; reason MARVIN_HARRISON_JR_SOURCE_ID; 2025 games %d; targets %.0f; raw score %.4f; formula weights unchanged. Sleeper snapshot %t; depth order %d.',
          c.wr_games_played,c.wr_targets,c.formula_score,context.fetched_at,context.depth_chart_order)
        WHEN c.position='WR' AND c.wr_coverage_method='PRIOR_QUALIFIED_VETERAN_CARRY_FORWARD' THEN FORMAT(
          'Coverage PRIOR_QUALIFIED_VETERAN_CARRY_FORWARD; source season %d; prior score %.4f; prior availability component %.4f; current two-year availability component %.4f; raw score %.4f; latest games %d; targets %.0f; rookie fallback excluded; injury status review-only; formula weights unchanged. Sleeper snapshot %t; depth order %d.',
          c.wr_score_source_season,c.wr_prior_v1_score,c.wr_prior_v1_age_availability_component,
          c.wr_current_age_availability_component,c.formula_score,c.wr_games_played,c.wr_targets,
          context.fetched_at,context.depth_chart_order)
        ELSE FORMAT('Sleeper snapshot %t; depth order %d',context.fetched_at,context.depth_chart_order)
      END AS llm_adjustment_evidence,
      CAST(NULL AS INT64) AS llm_estimated_games_missed,
      c.formula_rank-c.new_rank AS llm_rank_delta
    )
  FROM candidate_pre c
), fallback AS (
  SELECT ppr.* REPLACE(
    context.team AS current_team,
    context.sleeper_player_id AS sleeper_player_id,
    context.team AS sleeper_team,
    context.active AS sleeper_active,
    context.status AS sleeper_status,
    context.injury_status AS sleeper_injury_status,
    context.depth_chart_position AS sleeper_depth_chart_position,
    context.depth_chart_order AS sleeper_depth_chart_order,
    COALESCE(context.ranking_eligibility,'current_roster_review_required') AS ranking_eligibility,
    ARRAY_TO_STRING(ARRAY(
      SELECT flag FROM UNNEST([
        NULLIF(ppr.risk_flags,''),
        COALESCE(NULLIF(context.review_flags_text,''),'SLEEPER_CONTEXT_MISSING')
      ]) flag WHERE flag IS NOT NULL
    ),'; ') AS risk_flags
  )
  FROM {live} ppr
  LEFT JOIN {safety} context
    ON context.gsis_id=ppr.player_id AND context.position=ppr.position
  WHERE ppr.is_active AND ppr.scoring_profile_id='{scoring_profile}' AND ppr.position IN ('RB','WR','TE')
    AND COALESCE(context.current_board_rank_eligible,FALSE)
    AND NOT EXISTS(SELECT 1 FROM {candidates} c WHERE c.player_id=ppr.player_id AND c.position=ppr.position)
), combined AS (
  SELECT * FROM candidate_rows
  UNION ALL
  SELECT fallback.* REPLACE(
    '{version}' AS ranking_version,
    CURRENT_TIMESTAMP() AS generated_at,
    1000+fallback.rank AS rank,
    'ppr_fable_live_fallback' AS rank_source,
    TRUE AS is_active,
    CONCAT('{scoring_profile}-fable-v1-',FORMAT_TIMESTAMP('%Y%m%dT%H%M%SZ',CURRENT_TIMESTAMP())) AS model_run_id
  ) FROM fallback
), combined_pre AS (
  SELECT combined.*,ROW_NUMBER() OVER(PARTITION BY position ORDER BY rank,player_name) AS final_rank FROM combined
), reranked AS (
  SELECT combined_pre.* EXCEPT(final_rank) REPLACE(final_rank AS rank)
  FROM combined_pre
), limited AS (
  SELECT * FROM reranked
  WHERE rank<=CASE position WHEN 'RB' THEN 80 WHEN 'WR' THEN 100 WHEN 'TE' THEN 35 END
), normalized AS (
  SELECT limited.*,
    MIN(ranking_score) OVER(PARTITION BY position) AS min_score,
    MAX(ranking_score) OVER(PARTITION BY position) AS max_score
  FROM limited
)
SELECT normalized.* EXCEPT(min_score,max_score) REPLACE(
  ROUND(50+49*SAFE_DIVIDE(ranking_score-min_score,max_score-min_score),1) AS ranking_score
)
FROM normalized;

ASSERT NOT EXISTS (
  SELECT 1 FROM promoted
  WHERE ranking_eligibility != 'eligible_current_sleeper_player'
) AS 'Promoted Fable rows contain unresolved current-roster context';

ASSERT NOT EXISTS (
  SELECT 1 FROM promoted
  WHERE pigskin_verdict IS NULL OR pigskin_verdict=''
    OR REGEXP_CONTAINS(pigskin_verdict,r'Fable v1.*ranks .* after the shared current-roster safety layer')
) AS 'Promoted Fable rows contain missing or rank-only Pigskin verdicts';

ASSERT NOT EXISTS (
  SELECT 1
  FROM (
    SELECT position,MIN(ranking_score) AS min_score,MAX(ranking_score) AS max_score
    FROM promoted GROUP BY position
  )
  WHERE min_score!=50.0 OR max_score!=99.0
) AS 'Promoted Fable ranking scores are not normalized to 50-99';

INSERT INTO {history}
SELECT prior.* FROM {live} prior
WHERE prior.is_active AND prior.scoring_profile_id='{scoring_profile}' AND prior.position IN ('RB','WR','TE')
  AND NOT EXISTS(SELECT 1 FROM {history} h WHERE h.ranking_version=prior.ranking_version AND h.player_id=prior.player_id AND h.position=prior.position);
UPDATE {live} SET is_active=FALSE WHERE is_active AND scoring_profile_id='{scoring_profile}' AND position IN ('RB','WR','TE');
INSERT INTO {live} SELECT * FROM promoted;
"""


def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--project",default="fantasy-football-498121"); parser.add_argument("--dataset",default="fantasy_football_brain"); parser.add_argument("--metrics-dataset",default="fantasy_football_advanced_metrics"); parser.add_argument("--scoring-profile",choices=("ppr","half_ppr"),default="ppr"); parser.add_argument("--apply",action="store_true"); args=parser.parse_args()
    version=datetime.now(timezone.utc).strftime(f"{args.scoring_profile.replace('_','-')}-fable-v1-safety-%Y%m%d%H%M%S")
    sql=build_sql(args.project,args.dataset,args.scoring_profile,args.metrics_dataset,version)
    client=bigquery.Client(project=args.project)
    if not args.apply:
        job=client.query(sql,job_config=bigquery.QueryJobConfig(dry_run=True,use_query_cache=False)); print({"writes":False,"version":version,"bytes":job.total_bytes_processed}); return 0
    if os.environ.get(WRITE_GATE,"").lower()!="true": raise RuntimeError(f"{WRITE_GATE}=true is required")
    client.query(sql).result()
    rows=[dict(row) for row in client.query(f"SELECT position,COUNT(*) row_count,MIN(rank) min_rank,MAX(rank) max_rank FROM `{args.project}.{args.dataset}.analytics_pigskin_rankings` WHERE is_active AND scoring_profile_id='{args.scoring_profile}' AND position IN ('RB','WR','TE') GROUP BY position ORDER BY position").result()]
    print({"version":version,"positions":rows}); return 0


if __name__=="__main__": raise SystemExit(main())
