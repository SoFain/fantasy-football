"""Promote RB Fable v1 as the active Standard RB formula and board.

Owner-approved Phase 34.7 promotion. Scope is strictly Standard scoring, RB
position only:

1. Register/refresh the formula candidate `rb_fable_v1_standard_rb`.
2. Activate it as the Standard RB champion in `ranking_formula_champions`.
3. Archive the current active Standard RB board rows to
   `analytics_pigskin_rankings_history` (preserved fallback).
4. Deactivate those rows in `analytics_pigskin_rankings`.
5. Insert the new active Standard RB board generated from
   `v_rb_fable_01_scored_seasons` (2025 source metrics, Phase 34.4 formula).

Sleeper context is attached to board rows as display/review evidence only; it
never enters `rb_fable_01_score`. No QB/WR/TE, Half PPR, PPR, or GNG Keeper
object is touched. No model training, Gemini, or Pigskin chat call occurs.

Writes require ALLOW_RB_FABLE_V1_STANDARD_RB_PROMOTION=true and --apply.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_BRAIN_DATASET = "fantasy_football_brain"
DEFAULT_METRICS_DATASET = "fantasy_football_advanced_metrics"
WRITE_GATE = "ALLOW_RB_FABLE_V1_STANDARD_RB_PROMOTION"

CANDIDATE_ID = "rb_fable_v1_standard_rb"
FORMULA_VERSION = "1.1-phase-34.4"

FORMULA_JSON = json.dumps({
    "score": "rb_fable_01_score",
    "weights": {
        "non_garbage_time_touches_per_game": 0.30,
        "red_zone_touches_per_game": 0.13,
        "target_share": 0.12,
        "yac_per_rush": 0.08,
        "success_pct": 0.06,
        "epa_per_touch": 0.05,
        "explosive_pct": 0.04,
        "box_adjusted_ypc": 0.04,
        "blended_td_per_game": 0.10,
        "age_penalty": 0.05,
        "games_played_rate": 0.03,
    },
    "efficiency_shrinkage": "n / (n + 125) per metric sample",
    "age_elite_volume_protection": "age term * (1 - 0.6 * clamp((z_ngt_tpg - 0.75) / 0.75, 0, 1))",
    "z_scores": "partitioned by input season",
    "source_view": "fantasy_football_advanced_metrics.v_rb_fable_01_scored_seasons",
    "contract": "docs/rebuild/rb-fable-01-metric-contract.md",
}, sort_keys=True)


def build_statements(*, project: str, brain: str, metrics: str, version: str, run_id: str, selected_by: str, board_only: bool = False) -> list[tuple[str, str]]:
    live = f"`{project}.{brain}.analytics_pigskin_rankings`"
    history = f"`{project}.{brain}.analytics_pigskin_rankings_history`"
    candidates = f"`{project}.{brain}.ranking_formula_candidates`"
    champions = f"`{project}.{brain}.ranking_formula_champions`"
    scored = f"`{project}.{metrics}.v_rb_fable_01_scored_seasons`"
    sleeper = f"`{project}.{metrics}.sleeper_current_player_context`"
    scope = "position = 'RB' AND scoring_profile_id = 'standard'"

    register_candidate = f"""
MERGE {candidates} AS target
USING (SELECT '{CANDIDATE_ID}' AS candidate_id) AS source
ON target.candidate_id = source.candidate_id
WHEN MATCHED THEN UPDATE SET
  status = 'champion',
  formula_version = '{FORMULA_VERSION}',
  formula_json = '''{FORMULA_JSON}''',
  notes = 'Phase 34.7 owner-approved Standard RB champion. Backtest evidence: phases 34.3/34.4.',
  updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT
  (candidate_id, formula_set_id, formula_name, formula_version, position, formula_json,
   feature_allowlist_json, target_definition_json, source_requirements_json,
   status, notes, created_by, created_at, updated_at)
VALUES
  ('{CANDIDATE_ID}', 'standard_redraft_one_qb', 'RB Fable v1', '{FORMULA_VERSION}', 'RB',
   '''{FORMULA_JSON}''',
   '{{"source": "advanced situational metrics 2022-2025; no broken tackles, no YAC above expectation, no RB routes, no market data"}}',
   '{{"target": "next-season Standard RB fantasy points per game", "no_2026_outcomes": true}}',
   '{{"views": ["v_rb_fable_01_metric_inputs", "v_rb_fable_01_scored_seasons"]}}',
   'champion',
   'Phase 34.7 owner-approved Standard RB champion. Backtest evidence: phases 34.3/34.4.',
   '{selected_by}', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
"""

    deactivate_prior_champions = f"""
UPDATE {champions}
SET active = FALSE,
    notes = COALESCE(notes, '') || ' | deactivated by {run_id}'
WHERE active AND position = 'RB' AND formula_set_id = 'standard_redraft_one_qb'
"""

    activate_champion = f"""
INSERT INTO {champions}
  (champion_id, formula_set_id, position, candidate_id, formula_version, backtest_run_id,
   champion_reason, metric_name, metric_value, season_start, season_end, week_start, week_end,
   active, selected_by, selected_at, notes)
VALUES
  ('{version}', 'standard_redraft_one_qb', 'RB', '{CANDIDATE_ID}', '{FORMULA_VERSION}', 'phase-34-4-forward-folds',
   'Owner decision, Phase 34.7: RB Fable v1 replaces Current Pigskin Standard RB. Owner rulings accepted the Fable ranks for Henry, Hall, Charbonnet, Dowdle, and Gainwell, accepted the Jones/Pollard fades, and excluded James Conner (depth RB3, no qualified 2025 row).',
   'avg_ndcg_at_24', 0.847, 2022, 2025, 1, 18,
   TRUE, '{selected_by}', CURRENT_TIMESTAMP(),
   'Standard RB only. Prior LLM board archived in analytics_pigskin_rankings_history as fallback.')
"""

    archive_prior_board = f"""
INSERT INTO {history}
SELECT live.* FROM {live} AS live
WHERE live.is_active AND live.{scope}
  AND NOT EXISTS (
    SELECT 1 FROM {history} AS hist
    WHERE hist.ranking_version = live.ranking_version
      AND hist.player_id = live.player_id
      AND hist.position = live.position
      AND hist.scoring_profile_id = live.scoring_profile_id
  )
"""

    deactivate_prior_board = f"""
UPDATE {live}
SET is_active = FALSE
WHERE is_active AND {scope}
"""

    insert_new_board = f"""
INSERT INTO {live}
  (ranking_version, generated_at, season, ranking_phase, format, position, rank, tier,
   player_id, player_name, current_team, stat_season, ranking_score, raw_ranking_score,
   rank_rationale, risk_flags, model_name, data_snapshot_label, is_active,
   sleeper_player_id, sleeper_team, sleeper_active, sleeper_status, sleeper_injury_status,
   sleeper_depth_chart_position, sleeper_depth_chart_order,
   ranking_eligibility, rank_source, model_run_id, scoring_profile_id, league_type_id, roster_format_id)
WITH fable AS (
  SELECT
    player_name,
    candidate_internal_player_id AS player_id,
    CASE team
      WHEN 'HST' THEN 'HOU' WHEN 'BLT' THEN 'BAL' WHEN 'CLV' THEN 'CLE'
      WHEN 'ARZ' THEN 'ARI' WHEN 'LA' THEN 'LAR' ELSE team
    END AS fable_team,
    rb_fable_01_score,
    opportunity_component, efficiency_component, scoring_component, age_availability_component,
    ROW_NUMBER() OVER (ORDER BY rb_fable_01_score DESC, player_name) AS board_rank,
    MIN(rb_fable_01_score) OVER () AS min_score,
    MAX(rb_fable_01_score) OVER () AS max_score
  FROM {scored}
  WHERE season = 2025 AND rb_fable_01_score IS NOT NULL
)
SELECT
  '{version}' AS ranking_version,
  CURRENT_TIMESTAMP() AS generated_at,
  2026 AS season,
  'preseason' AS ranking_phase,
  'Standard' AS format,
  'RB' AS position,
  fable.board_rank AS rank,
  CASE
    WHEN fable.board_rank <= 5 THEN 'elite'
    WHEN fable.board_rank <= 12 THEN 'front-line starter'
    WHEN fable.board_rank <= 30 THEN 'starter'
    WHEN fable.board_rank <= 40 THEN 'flex or matchup'
    ELSE 'depth'
  END AS tier,
  fable.player_id,
  fable.player_name,
  COALESCE(context.team, fable.fable_team) AS current_team,
  2025 AS stat_season,
  ROUND(50 + 49 * SAFE_DIVIDE(fable.rb_fable_01_score - fable.min_score, fable.max_score - fable.min_score), 1) AS ranking_score,
  fable.rb_fable_01_score AS raw_ranking_score,
  FORMAT(
    'RB Fable v1 components: opportunity %+.3f, efficiency %+.3f, TD blend %+.3f, age/availability %+.3f',
    fable.opportunity_component, fable.efficiency_component, fable.scoring_component, fable.age_availability_component
  ) AS rank_rationale,
  ARRAY_TO_STRING(ARRAY(
    SELECT flag FROM UNNEST([
      IF(context.team IS NOT NULL AND context.team != fable.fable_team, 'STALE_TEAM_CONTEXT_REVIEW', NULL),
      IF(context.injury_status IS NOT NULL, 'SLEEPER_INJURY_' || UPPER(context.injury_status), NULL),
      IF(COALESCE(context.depth_chart_order, 1) > 1, 'SLEEPER_DEPTH_ORDER_' || CAST(context.depth_chart_order AS STRING), NULL)
    ]) AS flag WHERE flag IS NOT NULL
  ), '; ') AS risk_flags,
  'rb_fable_01' AS model_name,
  'advanced_situational_2025' AS data_snapshot_label,
  TRUE AS is_active,
  context.sleeper_player_id,
  context.team AS sleeper_team,
  context.active AS sleeper_active,
  context.status AS sleeper_status,
  context.injury_status AS sleeper_injury_status,
  context.depth_chart_position AS sleeper_depth_chart_position,
  context.depth_chart_order AS sleeper_depth_chart_order,
  'eligible_current_sleeper_player' AS ranking_eligibility,
  'rb_fable_v1_formula' AS rank_source,
  '{run_id}' AS model_run_id,
  'standard' AS scoring_profile_id,
  'redraft' AS league_type_id,
  'one_qb' AS roster_format_id
FROM fable
LEFT JOIN (
  SELECT player_id,
         ARRAY_AGG(sleeper_player_id IGNORE NULLS ORDER BY generated_at DESC LIMIT 1)[SAFE_OFFSET(0)] AS sleeper_player_id
  FROM {history}
  WHERE position = 'RB' AND scoring_profile_id = 'standard'
  GROUP BY player_id
) AS prior_map
  ON prior_map.player_id = fable.player_id
LEFT JOIN {sleeper} AS context
  ON context.sleeper_player_id = prior_map.sleeper_player_id
  OR (prior_map.sleeper_player_id IS NULL AND context.gsis_id = fable.player_id)
"""

    delete_current_fable_board = f"""
DELETE FROM {live}
WHERE rank_source = 'rb_fable_v1_formula' AND {scope}
"""

    if board_only:
        return [
            ("delete_current_fable_board", delete_current_fable_board),
            ("insert_new_board", insert_new_board),
        ]

    return [
        ("register_candidate", register_candidate),
        ("deactivate_prior_champions", deactivate_prior_champions),
        ("activate_champion", activate_champion),
        ("archive_prior_board", archive_prior_board),
        ("deactivate_prior_board", deactivate_prior_board),
        ("insert_new_board", insert_new_board),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--brain-dataset", default=DEFAULT_BRAIN_DATASET)
    parser.add_argument("--metrics-dataset", default=DEFAULT_METRICS_DATASET)
    parser.add_argument("--selected-by", default="owner")
    parser.add_argument("--refresh-board-only", action="store_true",
                        help="Rebuild only the active Fable board rows; skip candidate/champion/archive steps.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Print planned statements without executing.")
    mode.add_argument("--apply", action="store_true", help=f"Execute; requires {WRITE_GATE}=true.")
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    version = now.strftime("rb-fable-v1-standard-%Y%m%d%H%M%S")
    run_id = now.strftime(f"rb_fable_v1_promotion-%Y%m%dT%H%M%SZ")
    statements = build_statements(
        project=args.project, brain=args.brain_dataset, metrics=args.metrics_dataset,
        version=version, run_id=run_id, selected_by=args.selected_by,
        board_only=args.refresh_board_only,
    )

    if args.dry_run:
        print(json.dumps({"mode": "dry-run", "ranking_version": version, "model_run_id": run_id,
                          "statements": [name for name, _ in statements]}, indent=2))
        return 0

    if os.environ.get(WRITE_GATE) != "true":
        print(f"{WRITE_GATE} must be true to apply the promotion", file=sys.stderr)
        return 2

    from google.cloud import bigquery

    client = bigquery.Client(project=args.project)
    results = {}
    for name, sql in statements:
        job = client.query(sql)
        job.result()
        results[name] = job.num_dml_affected_rows
    print(json.dumps({"mode": "apply", "ranking_version": version, "model_run_id": run_id,
                      "affected_rows": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
