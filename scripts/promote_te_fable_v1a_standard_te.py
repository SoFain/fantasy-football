"""Promote TE Fable v1.0a no-man as the active Standard TE formula and board.

Scope is Standard/redraft/one-QB TE only. Writes require
ALLOW_TE_FABLE_V1A_STANDARD_TE_PROMOTION=true and --apply.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone


WRITE_GATE = "ALLOW_TE_FABLE_V1A_STANDARD_TE_PROMOTION"
CANDIDATE_ID = "te_fable_v1a_no_man_standard_te"
FORMULA_VERSION = "1.0a-no-man-phase-35.2a"

FORMULA_JSON = json.dumps({
    "score": "te_fable_v1a_no_man_score",
    "weights": {
        "routes_per_game": 0.22,
        "target_share": 0.16,
        "red_zone_targets_per_game": 0.12,
        "targets_per_route_run": 0.12,
        "yprr": 0.13,
        "epa_per_target": 0.05,
        "blended_td_per_game": 0.10,
        "breakout_window_bonus": 0.04,
        "decline_penalty": 0.03,
        "games_played_rate": 0.03,
    },
    "qualification": "games_played >= 4 AND routes_run >= 100",
    "efficiency_shrinkage": "n / (n + 70)",
    "source_view": "fantasy_football_advanced_metrics.v_te_fable_v1a_scored_seasons",
    "contract": "docs/rebuild/te_fable_v1_ranking_formula.md",
}, sort_keys=True)


def build_statements(project: str, brain: str, metrics: str, version: str, run_id: str) -> list[tuple[str, str]]:
    live = f"`{project}.{brain}.analytics_pigskin_rankings`"
    history = f"`{project}.{brain}.analytics_pigskin_rankings_history`"
    candidates = f"`{project}.{brain}.ranking_formula_candidates`"
    champions = f"`{project}.{brain}.ranking_formula_champions`"
    scored = f"`{project}.{metrics}.v_te_fable_v1a_scored_seasons`"
    sleeper = f"`{project}.{metrics}.sleeper_current_player_context`"
    scope = "position = 'TE' AND scoring_profile_id = 'standard' AND league_type_id = 'redraft' AND roster_format_id = 'one_qb'"

    register = f"""
MERGE {candidates} AS target
USING (SELECT '{CANDIDATE_ID}' AS candidate_id) AS source
ON target.candidate_id = source.candidate_id
WHEN MATCHED THEN UPDATE SET
  status='champion', formula_version='{FORMULA_VERSION}', formula_json='''{FORMULA_JSON}''',
  notes='Owner-approved Standard TE promotion. Phase 35.2A same-cohort evidence.', updated_at=CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT
  (candidate_id, formula_set_id, formula_name, formula_version, position, formula_json,
   feature_allowlist_json, target_definition_json, source_requirements_json, status, notes,
   created_by, created_at, updated_at)
VALUES
  ('{CANDIDATE_ID}', 'standard_redraft_one_qb', 'TE Fable v1.0a no-man', '{FORMULA_VERSION}', 'TE',
   '''{FORMULA_JSON}''',
   '{{"features":"source-backed TE situational metrics; no vs_man term; no market or current injury in score"}}',
   '{{"target":"next-season Standard TE fantasy points per game","no_2026_outcomes":true}}',
   '{{"views":["v_te_fable_v1a_metric_inputs","v_te_fable_v1a_scored_seasons"]}}',
   'champion', 'Owner-approved Phase 35.2A Standard TE promotion.', 'owner', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
"""

    deactivate_champion = f"""
UPDATE {champions}
SET active=FALSE, notes=COALESCE(notes,'') || ' | deactivated by {run_id}'
WHERE active AND position='TE' AND formula_set_id='standard_redraft_one_qb'
"""

    activate_champion = f"""
INSERT INTO {champions}
  (champion_id, formula_set_id, position, candidate_id, formula_version, backtest_run_id,
   champion_reason, metric_name, metric_value, season_start, season_end, week_start, week_end,
   active, selected_by, selected_at, notes)
VALUES
  ('{version}', 'standard_redraft_one_qb', 'TE', '{CANDIDATE_ID}', '{FORMULA_VERSION}',
   'phase-35-2a-same-cohort',
   'Owner-approved: no-man Fable won pairwise, top-6, top-12, captured points, NDCG, regret, and bust control.',
   'same_cohort_pairwise_win_rate', 0.761, 2022, 2025, 1, 18, TRUE, 'owner', CURRENT_TIMESTAMP(),
   'Standard TE only. Deterministic TE35 board precedes guarded Pigskin exception review.')
"""

    archive = f"""
INSERT INTO {history}
SELECT live.* FROM {live} AS live
WHERE live.is_active AND live.{scope}
  AND NOT EXISTS (
    SELECT 1 FROM {history} AS prior
    WHERE prior.ranking_version=live.ranking_version AND prior.player_id=live.player_id
      AND prior.position=live.position AND prior.scoring_profile_id=live.scoring_profile_id)
"""

    deactivate = f"""
UPDATE {live} SET is_active=FALSE WHERE is_active AND {scope}
"""

    insert_board = f"""
INSERT INTO {live}
  (ranking_version, generated_at, adjudicated_at, season, ranking_phase, format, position, rank, tier,
   player_id, player_name, current_team, stat_season, ranking_score, raw_ranking_score,
   candidate_rank, candidate_ranking_score, rank_rationale, risk_flags, model_name, prompt_version,
   data_snapshot_label, is_active, sleeper_player_id, sleeper_team, sleeper_active, sleeper_status,
   sleeper_injury_status, sleeper_depth_chart_position, sleeper_depth_chart_order,
   ranking_eligibility, rank_source, model_run_id, scoring_profile_id, league_type_id, roster_format_id,
   llm_adjustment_code, llm_adjustment_detail, llm_adjustment_evidence, llm_estimated_games_missed,
   llm_rank_delta)
WITH ranked AS (
  SELECT
    scored.*,
    ROW_NUMBER() OVER (ORDER BY te_fable_v1a_no_man_score DESC, player_name) AS board_rank,
    MIN(te_fable_v1a_no_man_score) OVER () AS min_score,
    MAX(te_fable_v1a_no_man_score) OVER () AS max_score
  FROM {scored} AS scored
  WHERE season=2025 AND te_fable_v1a_no_man_score IS NOT NULL
  QUALIFY board_rank <= 35
)
SELECT
  '{version}', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 2026, 'preseason', 'Standard', 'TE', board_rank,
  CASE WHEN board_rank<=5 THEN 'elite' WHEN board_rank<=12 THEN 'front-line starter'
       WHEN board_rank<=24 THEN 'starter' ELSE 'flex or matchup' END,
  candidate_internal_player_id, ranked.player_name, COALESCE(context.team, ranked.team), 2025,
  ROUND(50 + 49*SAFE_DIVIDE(te_fable_v1a_no_man_score-min_score,max_score-min_score),1),
  te_fable_v1a_no_man_score, board_rank,
  ROUND(50 + 49*SAFE_DIVIDE(te_fable_v1a_no_man_score-min_score,max_score-min_score),1),
  FORMAT('TE Fable v1.0a no-man: opportunity %+.3f, efficiency %+.3f, TD %+.3f, age/availability %+.3f',
    opportunity_component, no_man_efficiency_component, scoring_component, age_availability_component),
  ARRAY_TO_STRING(ARRAY(SELECT flag FROM UNNEST([
    IF(context.team IS NULL, 'CURRENT_TEAM_UNKNOWN', NULL),
    IF(context.injury_status IS NOT NULL, 'SLEEPER_INJURY_' || UPPER(context.injury_status), NULL),
    IF(COALESCE(context.depth_chart_order,1)>1, 'SLEEPER_DEPTH_ORDER_' || CAST(context.depth_chart_order AS STRING), NULL)
  ]) flag WHERE flag IS NOT NULL), '; '),
  'te_fable_v1a_no_man', 'deterministic-no-llm', 'advanced_situational_2025', TRUE,
  context.sleeper_player_id, context.team, context.active, context.status, context.injury_status,
  context.depth_chart_position, context.depth_chart_order,
  'formula_qualified_returning_te', 'te_fable_v1a_no_man_formula', '{run_id}',
  'standard', 'redraft', 'one_qb', 'NO_ADJUSTMENT',
  'Deterministic formula promotion; no LLM movement applied.',
  'phase-35-2a same-cohort backtest', NULL, 0
FROM ranked
LEFT JOIN {sleeper} AS context ON context.gsis_id=ranked.candidate_internal_player_id
"""

    return [
        ("register_candidate", register),
        ("deactivate_prior_champion", deactivate_champion),
        ("activate_champion", activate_champion),
        ("archive_prior_board", archive),
        ("deactivate_prior_board", deactivate),
        ("insert_fable_board", insert_board),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--brain-dataset", default="fantasy_football_brain")
    parser.add_argument("--metrics-dataset", default="fantasy_football_advanced_metrics")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    version = now.strftime("te-fable-v1a-standard-%Y%m%d%H%M%S")
    run_id = now.strftime("te_fable_v1a_promotion-%Y%m%dT%H%M%SZ")
    statements = build_statements(args.project, args.brain_dataset, args.metrics_dataset, version, run_id)
    if args.dry_run:
        print(json.dumps({"mode":"dry-run","ranking_version":version,"statements":[name for name,_ in statements]},indent=2))
        return 0
    if os.environ.get(WRITE_GATE) != "true":
        print(f"{WRITE_GATE} must be true to apply the promotion", file=sys.stderr)
        return 2

    from google.cloud import bigquery
    client = bigquery.Client(project=args.project)
    affected = {}
    for name, sql in statements:
        job = client.query(sql)
        job.result()
        affected[name] = job.num_dml_affected_rows
    print(json.dumps({"mode":"apply","ranking_version":version,"model_run_id":run_id,"affected_rows":affected},indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
