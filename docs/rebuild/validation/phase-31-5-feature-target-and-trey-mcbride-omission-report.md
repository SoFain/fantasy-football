# Phase 31.5 Feature/Target Availability And Trey McBride Omission Report

Final decision: TREY MCBRIDE OMISSION NEEDS RANKING GENERATOR FIX

## Scope

Phase 31.5 audited feature and target availability for ranking formula backtests, improved seeded-candidate dry-runs across all draft candidates per position, and diagnosed the owner-flagged Trey McBride TE ranking omission.

No production deploy, staging deploy, materialization, Cloud Run Job trigger, Scheduler job, Pigskin prompt, LLM-backed action, Sleeper API call, champion selection, or backtest write occurred.

## Git State

Starting tracked changes:

- `src/materialize.py`
- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`

New phase file:

- `tests/test_pigskin_rankings_materialize_identity.py`
- `docs/rebuild/validation/phase-31-5-feature-target-and-trey-mcbride-omission-report.md`

Existing untracked historical validation backlog remains intentionally untracked.

Commit hash: created after this report was written for the phase package.

## Trey McBride Identity Resolution

Resolved using approved identity/current roster sources only.

- `sleeper_players_current`: `sleeper_player_id=8130`, player name `Trey McBride`, position `TE`, current team `ARI`, status `Active`, source timestamp `2026-06-15T19:14:53.601698Z`; `gsis_id` is null in this source.
- `player_identity_bridge`: `player_id_internal=sleeper:8130`, `gsis_id=00-0037744`, `sleeper_player_id=8130`, player name `Trey McBride`, position `TE`, current team `ARI`, active status `Active`, confidence `0.95`, updated at `2026-06-16T05:47:32.145903Z`.
- `stg_player_identity`: `player_id_internal=00-0037744`, `gsis_id=00-0037744`, player name `Trey McBride`, position `TE`, current team `ARI`, confidence `0.95`, latest rows created `2026-06-30T18:16:48.029655Z`.

Identity is not ambiguous. The key mismatch is the important part: current Sleeper source starts from `8130`, identity bridge maps that to GSIS `00-0037744`, and historical metrics use `00-0037744`.

## Current Ranking Presence

Checked current ranking outputs and app-facing ranking sources.

- `analytics_pigskin_rankings`: no Trey McBride rows found by `player_id`, `gsis_id`, `sleeper_player_id`, full name, or TE position/name filters.
- `analytics_pigskin_rankings_candidates`: one Trey McBride row found. `player_id=8130`, `sleeper_player_id=8130`, position `TE`, current team `ARI`, `is_active=true`, rank `148`, ranking score `5.0`, confidence `35.0`, tier `deep or watchlist`, risk flag `missing recent weekly sample`, generated at `2026-06-17T02:41:06.036397Z`.
- `projection_rankings_current`: Trey McBride rows found with `player_id_internal=sleeper:8130`, position `TE`, team `ARI`, PPR redraft one-QB, season `2025`, week `18`, rank position `17` in model run `weekly_projection-2025-18-20260618T152142Z-6752df98` and rank position `11` in model run `weekly_projection-2025-18-20260618T044039Z-e3978cd6`.

Current app ranking query uses `analytics_pigskin_rankings WHERE is_active = TRUE`. Since Trey is absent from that table, he cannot appear in the app’s canonical Pigskin rankings board.

## Omission Root Cause

Classification:

- identity mismatch
- stale ranking output
- ranking generator source feature row missing due to identity join
- threshold/minimum candidate filter issue

Root cause:

`analytics_pigskin_rankings_candidates` ranked Trey McBride at TE candidate rank `148` because the candidate materialization attached no weekly production metrics. The candidate row has `weekly_rows=0`, `avg_ppr=null`, `total_ppr=null`, `avg_wopr=null`, `avg_target_share=null`, `avg_receiving_epa=null`, and `risk_flags=missing recent weekly sample`.

That is wrong for the current warehouse state. Approved input tables contain real McBride rows keyed by GSIS `00-0037744`.

The generator only sends the top `60` TE candidates to the LLM final ranking path. Because McBride’s candidate row is ranked `148`, he is excluded before final `analytics_pigskin_rankings` is written.

Fix implemented:

- `src/materialize.py` now uses `player_identity_bridge` in `build_pigskin_rankings_sql`.
- Sleeper-only rows can recover `ib.gsis_id` before joining `player_weekly_agg` and `player_multi_season`.
- The ranking candidate `player_id` now prefers a canonical key and falls back to `sleeper:<id>` instead of a bare Sleeper id.
- `materialize_pigskin_rankings` now fails closed if `player_identity_bridge` is missing.

This code fix was not materialized in Phase 31.5. A future authorized ranking candidate rebuild is required before the live ranking output changes.

## Trey McBride Feature/Input Availability

Approved input table checks:

- `player_week_advanced_metrics`: `62` rows, seasons `2022` through `2025`, weeks `1` through `18`, position `TE`, team `ARI`.
- `analytics_player_weekly_truth`: `17` rows, season `2025`, weeks `1` through `18`, position `TE`, team `ARI`.
- `analytics_player_fantasy_points_by_profile`: `51` rows, season `2025`, weeks `1` through `18`, position `TE`, team `ARI`.
- `pigskin_player_context_packet_current`: `3` rows, seasons `2023` through `2025`, week `18`, position `TE`, team `ARI`.
- `player_recent_advanced_metrics_current`: `1` row, season `2025`, week `18`, position `TE`, team `ARI`.
- `player_role_usage_metrics_current`: `1` row, season `2025`, week `18`, position `TE`, team `ARI`.

Recent sample from `player_week_advanced_metrics` shows Trey at `player_id_internal=00-0037744`, not raw Sleeper id `8130`.

## Regression/Diagnostic Tests Added

Added `tests/test_pigskin_rankings_materialize_identity.py`.

Coverage:

- candidate SQL uses `player_identity_bridge`;
- candidate SQL carries `metrics_player_id`;
- weekly aggregate join uses `rp.metrics_player_id = agg.player_id`;
- multi-season join uses `rp.metrics_player_id = ms.player_id`;
- fallback candidate id uses `CONCAT('sleeper:', sc.sleeper_player_id)`;
- `materialize_pigskin_rankings` refuses to run when `player_identity_bridge` is missing.

Updated `tests/test_ranking_formula_backtests.py`.

Coverage:

- all position candidates for a formula set load through a parameterized `formula_set_id` filter;
- feature and target availability reports show available and missing candidate inputs;
- dry-run remains non-mutating.

## Feature Mapping Improvements

`src/ranking_formula_backtests.py` now maps additional available seeded formula features:

- `recent_points_avg`
- `passing_success_rate`
- `dropbacks`
- `rushing_attempts`
- `rush_success_rate`
- `receiving_usage`
- `passing_epa_per_play`
- `goal_line_opportunities`

Missing or blocked inputs remain missing. They are not zero-filled. Examples still missing in bounded dry-runs include `pigskin_context_score`, `team_pass_rate`, and some red-zone fields where the source rows do not provide values.

The dry-run result now includes:

- `feature_availability`
- `target_availability`
- all draft candidates for the requested position tied to the formula set

## Target Data Availability Findings

Original 2014 weeks 1 through 4 TE check:

- candidate count: `3`
- input row count: `100`
- result-shaped rows: `300`
- target rows: `0`
- target available: `false`
- rank correlation: `null`
- top-N hit rate: `null`

The target truth join remains unavailable for that 2014 sample.

Bounded 2025 weeks 1 through 4 provides target truth for all four positions and is suitable for dry-run comparison.

## Bounded Dry-Run Results

All dry-runs used:

- formula set: `ranking_formula_set_v0_2026_001`
- status: `draft`
- season: `2025`
- weeks: `1` through `4`
- scoring profile: `ppr`
- league type: `redraft`
- roster format: `one_qb`
- limit: `100` for position comparisons
- dry-run only

| Position | Candidate Count | Input Rows | Result-Shaped Rows | Summary-Shaped Rows | Target Rows | Missing Input Rate | Top-N Hit Rate | Rank Correlation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QB | 3 | 100 | 300 | 3 | 100 | 0.224 | 0.36 | 0.8833034666826977 |
| RB | 3 | 100 | 300 | 3 | 100 | 0.226 | 0.16 | 0.975748450466485 |
| WR | 3 | 100 | 300 | 3 | 100 | 0.200 | 0.12 | 0.9519831983198321 |
| TE | 3 | 100 | 300 | 3 | 100 | 0.400 | 0.24 | 0.9815629499203145 |

TE McBride-specific dry-run used `limit=500` to cover the full bounded TE week slice:

- candidate count: `3`
- input rows: `298`
- result-shaped rows: `894`
- target rows: `298`
- Trey McBride result rows: `12`
- Trey McBride actual ranks: week 1 rank `12`, week 2 rank `5`, week 3 rank `6`, week 4 rank `8`
- Trey McBride predicted ranks included week 4 rank `1` in balanced and volume formulas

This proves the backtest runner can see Trey when the approved feature inputs are keyed through GSIS.

## Row Counts After Dry-Run

Read-only count check after all dry-runs:

- `ranking_formula_candidates`: `12`
- `ranking_formula_sets`: `1`
- `ranking_backtest_runs`: `0`
- `ranking_backtest_results`: `0`
- `ranking_backtest_candidate_summaries`: `0`
- `ranking_formula_champions`: `0`

No backtest rows were written.

## Pigskin Exposure Confirmation

Searched:

- `app.py`
- `src/pigskin_context_tools.py`
- `src/pigskin_packet_guardrails.py`
- `src/pigskin_context_qa.py`

Search terms:

- `ranking_formula`
- `ranking_backtest`
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE`

Result: no matches. No ranking formula read/write tool is exposed to Pigskin, no arbitrary SQL path was added, and no Streamlit request-time formula/backtest write path was added.

## Checks Run

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed
- `.\venv\Scripts\python.exe -m compileall -q src scripts`: passed
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`: passed, `28` tests
- `.\venv\Scripts\python.exe -m unittest tests.test_seed_ranking_formula_candidates`: passed, `6` tests
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_rankings_materialize_identity`: passed, `2` tests
- `.\venv\Scripts\python.exe -m unittest discover tests`: passed, `652` tests
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: discovered `209` validations
- BigQuery dry-run for patched `build_pigskin_rankings_sql`: passed, estimated `5,738,438` bytes processed

## Remaining Warnings

- Current `analytics_pigskin_rankings` remains stale. Trey McBride will stay absent until an authorized Pigskin ranking candidate rebuild and final ranking generation or review path runs.
- Current `analytics_pigskin_rankings_candidates` still has the old Trey row at rank `148`.
- `player_recent_advanced_metrics_current` and `player_role_usage_metrics_current` exist but have limited current rows. They are not yet a broad source for formula dry-runs.
- `pigskin_context_score` and `team_pass_rate` remain unavailable in the dry-run formula mapper.
- Red-zone target fields are still often missing for the tested slices. Missing stays visible in `missing_flags_json`.
- The Phase 31.5 code fix changes future ranking candidate materialization SQL only. It does not mutate warehouse data.

## Recommended Next Phase

Recommended next phase: Phase 31.6 — Current ranking output rebuild after TE omission fix.

Boundaries for that phase:

- authorized materialization only;
- no Pigskin chat exposure of ranking formula tables;
- no champion formula selection;
- verify Trey McBride in regenerated `analytics_pigskin_rankings_candidates` before any LLM final ranking step;
- if final ranking generation is needed, it requires explicit LLM authorization.
