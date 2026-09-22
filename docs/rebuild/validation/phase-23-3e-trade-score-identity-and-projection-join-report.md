# Phase 23.3E Trade Score Identity And Projection Join Report

Date: 2026-06-18

## Final Decision

`TRADE SCORE MATERIALIZATION NOT RECOMMENDED`

Projection/model-run join handling was hardened and diagnostics are clearer. The builder now records projection join strategy/key metadata, uses refreshed weekly projection source keys where available, clears `temporary_name_join_identity` only when a stable projection identity attaches, and excludes draft-pick rows from future materialized score writes while keeping them visible in dry-run diagnostics.

The code fix reduced `temporary_name_join_identity` from 87 rows to 35 rows. `missing_model_run_id` stayed at 48 rows because the bounded projection refresh produced projection rows for only part of the top 100 market-value candidate set. That is a source coverage limitation, not an unsafe name-join problem.

No Trade Analyzer score rows were written. No projection context was regenerated. No deployment, feature flag enablement, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, Firebase artifact creation, or production change was performed.

## Root Cause

The old source query joined `projection_rankings_current` to candidate assets only through:

```sql
COALESCE(a.player_id_internal, a.source_player_key) = p.player_key
```

That was too opaque and did not preserve the actual projection join strategy. It also could not use `projections_player_weekly.source_player_key`, even though that output table has a stable source key.

Read-only diagnostics showed the bigger remaining blocker:

- 100 market-value candidate assets are scored.
- Refreshed 2025 week 18 projection output contains 100 projection rows, but only 51 of the top 100 market assets match those target rows by stable IDs.
- The score builder attaches 52 model-run rows because one asset matches an older allowed projection row and is flagged `stale_projection_context`.
- The remaining 48 rows lack target projection/model-run context because they are absent from the bounded projection output or are draft picks.

## Identity Columns Inspected

| Source | Available identity columns |
| --- | --- |
| `projection_rankings_current` | `player_id_internal`, `display_name`, `position`, `team` |
| `projections_player_weekly` | `player_id_internal`, `source_player_key`, `display_name`, `position`, `team` |
| `model_runs` | none |
| `compat_trade_assets_current` | `player_id_internal`, `source_player_key`, `gsis_id`, `display_name`, `normalized_name`, `position`, `team` |
| `compat_trade_player_history` | `player_id_internal`, `source_player_key`, `normalized_name`, `position`, `team` |
| `analytics_player_weekly_truth` | `player_id`, `player_name`, `position`, `team` |
| `analytics_player_fantasy_points_by_profile` | `player_id_internal`, `source_player_key`, `position`, `team` |
| `analytics_fraud_watch` | `player_id`, `player_name`, `position`, `team` |

## Join Matrix

Read-only match counts against the top 100 trade candidates:

| Strategy | Matched assets |
| --- | ---: |
| candidate `source_player_key` to ranking `player_id_internal` | 0 |
| candidate `gsis_id` to ranking `player_id_internal` | 0 |
| candidate `player_id_internal` to ranking `player_id_internal` | 51 |
| candidate exact name + position + team to ranking | 47 |
| candidate normalized name + position + team to ranking, unique only | 47 |
| candidate normalized name + position to ranking, unique only | 51 |
| candidate `source_player_key` to weekly projection `source_player_key` | 51 |
| candidate `gsis_id` to weekly projection `source_player_key` | 51 |
| candidate `player_id_internal` to weekly projection `player_id_internal` | 51 |
| candidate exact name + position + team to weekly projection | 47 |
| candidate normalized name + position + team to weekly projection, unique only | 47 |

Sample assets missing stable target-week projection rows included `Jeremiyah Love`, `CeeDee Lamb`, `Drake London`, `Tetairoa McMillan`, `Breece Hall`, `Garrett Wilson`, and draft-pick assets.

## Code Changes

Files changed:

- `src/trade_player_scores.py`
- `tests/test_trade_player_scores.py`

Changes:

- Added `projections_player_weekly` as a safe source object for score-source context.
- Rebuilt projection matching to use `projection_rankings_current` joined to `projections_player_weekly`.
- Added projection match priority:
  1. candidate `source_player_key` to projection `source_player_key`
  2. candidate `gsis_id` to projection `source_player_key`
  3. candidate `player_id_internal` to projection `player_id_internal`
  4. exact name + position + team
  5. normalized name + position + team, only when unique
- Added `projection_join_key` and `projection_join_strategy` to source rows.
- Recorded projection join metadata in `component_json`.
- Recorded projection join metadata in `source_freshness_json`.
- Cleared inherited `temporary_name_join_identity` only when a stable projection join attaches.
- Added `projection_name_fallback_used` when projection context attaches by safe name fallback.
- Added `materializable_player_row_count`, `excluded_pick_count`, and `written_row_count` to score build results.
- Kept draft-pick rows in dry-run diagnostics.
- Excluded draft-pick rows from any future write path unless a separate pick scoring lane is approved.

## Tests Added

Added or updated tests for:

- Projection source query uses stable projection keys before name fallback.
- Projection join strategy and join key are recorded.
- Stable projection join clears inherited `temporary_name_join_identity`.
- Name fallback keeps `temporary_name_join_identity` and records `projection_name_fallback_used`.
- `missing_model_run_id` clears only when model-run context attaches.
- Draft-pick rows remain visible in dry-run diagnostics.
- Draft-pick rows are excluded from future materialized score writes.
- Dry-run remains non-mutating.
- `--write` remains required for score writes.

## Dry-Run Comparison

Target:

| Field | Value |
| --- | --- |
| season | `2025` |
| week | `18` |
| scoring_profile_id | `ppr` |
| league_type_id | `redraft` |
| roster_format_id | `one_qb` |
| model_version | `trade_score_v0_2025_001` |

Command:

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v0_2025_001 --dry-run
```

Summary:

| Metric | Before 23.3E | After 23.3E | Result |
| --- | ---: | ---: | --- |
| wrote | `false` | `false` | unchanged |
| score row count | 100 | 100 | unchanged |
| materializable player row count | not reported | 87 | added |
| excluded pick count | not reported | 13 | added |
| written row count | not reported | 0 | added |
| trade score min | 11.5784 | 11.5784 | unchanged |
| trade score max | 55.2387 | 55.2387 | unchanged |
| trade score avg | 33.9357 | 33.9620 | slightly improved |
| confidence min | 28.66 | 28.66 | unchanged |
| confidence max | 57.0 | 57.0 | unchanged |
| confidence avg | 48.5489 | 48.7489 | slightly improved |
| rows with confidence >= 70 | 0 | 0 | unchanged |
| nonzero `fraud_score` rows | 55 | 55 | unchanged |
| `missing_model_run_id` | 48 | 48 | unchanged |
| `stale_projection_context` | 1 | 1 | unchanged |
| `missing_fraud_context` | 45 | 45 | unchanged |
| `temporary_name_join_identity` | 87 | 35 | improved |
| draft pick assets | 13 | 13 | unchanged |
| dry-run duplicate grain count | not reported | 0 | added |

Projection join distribution after the fix:

| Strategy | Rows |
| --- | ---: |
| `source_player_key` | 52 |
| none | 48 |

No normalized name fallback was needed in the target dry-run. The safe fallback remains available and tested for future slices.

## Top 25 Trade Score Dry-Run Rows After Fix

| Rank | Player | Pos | Team | Score | Confidence | Fraud | Model run | Join strategy | Tier |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | Bijan Robinson | RB | ATL | 55.2387 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | flex |
| 2 | Jeremiyah Love | RB | ARI | 52.8696 | 52.00 | 0.00 |  |  | flex |
| 3 | Ja'Marr Chase | WR | CIN | 50.7167 | 49.35 | 60.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | flex |
| 4 | Jahmyr Gibbs | RB | DET | 50.5711 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | flex |
| 5 | Drake Maye | QB | NE | 50.4203 | 43.66 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | flex |
| 6 | CeeDee Lamb | WR | DAL | 49.6311 | 51.50 | 43.00 |  |  | flex |
| 7 | Puka Nacua | WR | LAR | 49.3276 | 43.72 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | flex |
| 8 | Josh Allen | QB | BUF | 49.2100 | 42.97 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | flex |
| 9 | Jaxon Smith-Njigba | WR | SEA | 48.3378 | 50.53 | 65.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | flex |
| 10 | 2026 Pick 1.01 | PICK |  | 48.0620 | 49.00 | 0.00 |  |  | flex |
| 11 | Drake London | WR | ATL | 47.0918 | 50.50 | 0.00 |  |  | flex |
| 12 | De'Von Achane | RB | MIA | 46.8853 | 49.35 | 0.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | flex |
| 13 | Amon-Ra St. Brown | WR | DET | 46.5500 | 50.53 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | flex |
| 14 | Christian McCaffrey | RB | SF | 46.4166 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | flex |
| 15 | 2026 Pick 1.02 | PICK |  | 45.9088 | 49.00 | 0.00 |  |  | flex |
| 16 | Breece Hall | RB | NYJ | 45.0541 | 54.50 | 0.00 |  |  | flex |
| 17 | Ashton Jeanty | RB | LV | 44.4202 | 50.53 | 25.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | depth |
| 18 | Tetairoa McMillan | WR | CAR | 43.8477 | 55.50 | 50.00 |  |  | depth |
| 19 | 2026 Pick 1.03 | PICK |  | 43.7556 | 49.00 | 0.00 |  |  | depth |
| 20 | Carnell Tate | WR | TEN | 43.0738 | 52.00 | 0.00 |  |  | depth |
| 21 | Chase Brown | RB | CIN | 41.7102 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | depth |
| 22 | 2026 Pick 1.04 | PICK |  | 41.6024 | 49.00 | 0.00 |  |  | depth |
| 23 | Trey McBride | TE | ARI | 41.4666 | 43.72 | 35.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | depth |
| 24 | Quinshon Judkins | RB | CLE | 40.7715 | 52.50 | 0.00 |  |  | depth |
| 25 | Brock Bowers | TE | LV | 40.6903 | 44.23 | 78.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | depth |

## Bottom 25 Trade Score Dry-Run Rows After Fix

| Rank | Player | Pos | Team | Score | Confidence | Fraud | Model run | Join strategy | Tier |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | Quentin Johnston | WR | LAC | 11.5784 | 44.96 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | avoid |
| 2 | RJ Harvey | RB | DEN | 15.1620 | 50.53 | 85.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | avoid |
| 3 | Chuba Hubbard | RB | CAR | 16.4500 | 53.50 | 45.00 |  |  | avoid |
| 4 | Alec Pierce | WR | IND | 16.8427 | 47.26 | 85.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | avoid |
| 5 | D'Andre Swift | RB | CHI | 16.8910 | 49.16 | 0.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | avoid |
| 6 | Bo Nix | QB | DEN | 17.0614 | 44.12 | 75.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | avoid |
| 7 | Bhayshul Tuten | RB | JAX | 18.3278 | 53.50 | 85.00 |  |  | avoid |
| 8 | Jalen Hurts | QB | PHI | 18.4702 | 42.20 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | avoid |
| 9 | 2026 Pick 1.11 | PICK |  | 20.5639 | 49.00 | 0.00 |  |  | avoid |
| 10 | David Montgomery | RB | HOU | 21.1841 | 55.50 | 60.00 |  |  | avoid |
| 11 | Jaxson Dart | QB | NYG | 21.3500 | 46.09 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | avoid |
| 12 | Sam LaPorta | TE | DET | 21.5922 | 51.41 | 53.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | avoid |
| 13 | Denzel Boston | WR | CLE | 21.8414 | 52.00 | 0.00 |  |  | avoid |
| 14 | Christian Watson | WR | GB | 22.5102 | 48.50 | 95.00 |  |  | avoid |
| 15 | 2026 Pick 1.10 | PICK |  | 22.9229 | 49.00 | 0.00 |  |  | avoid |
| 16 | Jayden Daniels | QB | WAS | 22.9821 | 30.04 | 80.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | avoid |
| 17 | Jonah Coleman | RB | DEN | 23.9400 | 52.00 | 0.00 |  |  | avoid |
| 18 | Jaylen Waddle | WR | DEN | 25.2101 | 54.50 | 70.00 |  |  | avoid |
| 19 | 2026 Pick 1.09 | PICK |  | 25.3071 | 49.00 | 0.00 |  |  | avoid |
| 20 | Tee Higgins | WR | CIN | 25.4076 | 47.24 | 55.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | avoid |
| 21 | Omar Cooper | WR | NYJ | 25.5906 | 52.00 | 0.00 |  |  | avoid |
| 22 | Kenyon Sadiq | TE | NYJ | 26.1576 | 52.00 | 0.00 |  |  | avoid |
| 23 | Harold Fannin | TE | CLE | 26.7809 | 48.14 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | avoid |
| 24 | Cam Skattebo | RB | NYG | 26.9472 | 50.52 | 70.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | `source_player_key` | avoid |
| 25 | KC Concepcion | WR | CLE | 27.1306 | 52.00 | 0.00 |  |  | avoid |

## Validations

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass, 22 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 340 tests |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 passed, 0 failed |

Final row-count verification:

| Object | Rows |
| --- | ---: |
| `trade_player_scores` | 0 |
| `projection_rankings_current` 2025 week 18 PPR redraft one-QB | 100 |
| `projections_player_weekly` 2025 week 18 PPR redraft one-QB | 100 |

## Draft Pick Decision

Draft-pick rows remain in dry-run diagnostics because they are useful for review, but they are excluded from the future materialized write path by default.

Current dry-run:

| Metric | Value |
| --- | ---: |
| score rows | 100 |
| materializable player rows | 87 |
| excluded pick rows | 13 |

Pick scoring still needs a separate score lane or explicit owner approval before public score use.

## Recommendation

Do not materialize Trade Analyzer score rows yet.

Remaining blockers:

- 48 dry-run rows still lack model-run context.
- 35 rows still carry `temporary_name_join_identity`.
- No rows meet confidence 70.
- Draft-pick score handling is diagnostic only.

Recommended next step:

1. Decide whether to expand the projection refresh beyond limit 100 or align projection candidate selection with the Trade Analyzer top 100 market assets.
2. Continue reducing temporary identity joins in `compat_trade_assets_current`.
3. Keep `ALLOW_TRADE_SCORE_MATERIALIZATION` unset until explicit score-write approval.

Final decision: `TRADE SCORE MATERIALIZATION NOT RECOMMENDED`.
