# Phase 23.3B Projection Context Refresh Report

Date: 2026-06-18

## Final Decision

`PROJECTION CONTEXT REFRESHED WITH WARNINGS`

Projection context was rebuilt for the target 2025 week 18 PPR redraft one-QB slice using the deterministic `src.projection_engine` path after the operator authorized this single step with `ALLOW_PROJECTION_CONTEXT_REFRESH=true`.

The authorization gate was removed immediately after the bounded projection refresh. The follow-up Trade Analyzer score run was dry-run only, and `ALLOW_TRADE_SCORE_MATERIALIZATION` was not set.

Trade Analyzer score materialization remains not recommended yet. The score dry-run improved from 98 rows with `missing_model_run_id` to 48 rows, but confidence remains below the target review threshold and identity joins still rely heavily on temporary name matching.

No Trade Analyzer score rows were written. No deployment, feature flag enablement, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, Firebase artifact creation, or production change was performed.

## Target

| Field | Value |
| --- | --- |
| season | `2025` |
| week | `18` |
| scoring_profile_id | `ppr` |
| league_type_id | `redraft` |
| roster_format_id | `one_qb` |

## Current Projection And Model-Run Coverage

Read-only warehouse checks showed:

| Object | 2025 target coverage |
| --- | --- |
| `projection_rankings_current` | 50 rows, 25 players, week 1 only, 2 model runs |
| `projections_player_weekly` | 50 rows, 25 players, week 1 only, 2 model runs |
| `projections_player_ros` | 0 rows for 2025 |
| `projections_player_dynasty` | 0 rows for 2025 |
| `model_runs` | 2 rows for 2025 week 1 weekly projection, 1 complete and 1 failed |
| `feature_config_versions` | active baseline weekly, ros, and dynasty configs exist |
| `analytics_player_fantasy_points_by_profile` | week 18 PPR rows exist, 1,067 players |
| `analytics_player_weekly_truth` | week 18 rows exist, 1,067 rows and 1,066 players |
| `llm_player_context_packet` | week 18 PPR redraft one-QB rows exist, 9,340 rows and 9,288 players, but `model_run_id` count is 0 |

The old `model_run_config_foundation` table does not exist in this warehouse. The active config table is `feature_config_versions`.

## Initial Join Coverage Against Trade Score Candidates

For the top 100 Trade Analyzer candidate assets:

| Metric | Value |
| --- | ---: |
| candidate rows | 100 |
| joined projection rows | 2 |
| joined week 18 projection rows | 0 |
| joined stale projection rows | 2 |
| joined model runs | 1 |

This explained why the initial Trade Analyzer score dry-run reported:

- `missing_model_run_id`: 98 rows
- `stale_projection_context`: 2 rows

## Supported Refresh Commands

`src.projection_engine` exposes a bounded deterministic CLI:

```powershell
.\venv\Scripts\python.exe -m src.projection_engine --horizon weekly --season 2025 --week 18 --scoring-profile ppr --league-type redraft --roster-format one_qb --limit 100 --dry-run
```

The dry-run is non-mutating. The module has no separate `--write` flag, so removing `--dry-run` would create model-run metadata and write projection/ranking rows. That write path requires explicit authorization:

```powershell
$env:ALLOW_PROJECTION_CONTEXT_REFRESH = "true"
```

`src.generate_pigskin_rankings` exposes CLI help, but it is LLM-authored ranking generation. It was not run beyond `--help` because this phase prohibits LLM calls.

## Projection Dry-Run Result

Bounded command:

```powershell
.\venv\Scripts\python.exe -m src.projection_engine --horizon weekly --season 2025 --week 18 --scoring-profile ppr --league-type redraft --roster-format one_qb --limit 100 --dry-run
```

Dry-run summary:

| Metric | Value |
| --- | --- |
| authorization | `ALLOW_PROJECTION_CONTEXT_REFRESH` unset |
| model_run_id | `dry-run` |
| feature_config_version_id | `baseline_weekly_v1` |
| projection_rows | 100 |
| ranking_rows | 100 |
| writes | 0 |

Top 10 dry-run rankings:

| Rank | Player | Pos | Team | Projected value | Confidence | Risk |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 | Chris Olave | WR | NO | 42.539 | 71.4 | 37.0 |
| 2 | Chase Brown | RB | CIN | 41.033 | 72.1 | 37.0 |
| 3 | Derrick Henry | RB | BAL | 41.015 | 71.63 | 37.723 |
| 4 | Bijan Robinson | RB | ATL | 40.787 | 72.1 | 37.0 |
| 5 | Brock Purdy | QB | SF | 39.825 | 58.284 | 44.255 |
| 6 | Christian McCaffrey | RB | SF | 39.517 | 72.1 | 37.0 |
| 7 | Trevor Lawrence | QB | JAX | 39.28 | 48.542 | 67.858 |
| 8 | Drake Maye | QB | NE | 38.98 | 64.648 | 43.08 |
| 9 | Matthew Stafford | QB | LA | 38.357 | 46.334 | 71.255 |
| 10 | Rhamondre Stevenson | RB | NE | 38.171 | 67.884 | 40.256 |

## Selected Path

Selected path: `A. Rebuild projection_rankings_current for 2025 week 18 PPR redraft one-QB`.

Reason:

- Current projection context is week 1 only.
- Deterministic weekly projection dry-run can build 100 week 18 projection rows.
- Current Trade Analyzer candidate coverage would materially improve if those week 18 projection rankings were written.

Status:

- Dry-run completed.
- Write authorized for this single step.
- Bounded write completed.
- Authorization gate was removed after the write.

## Projection Refresh Result

Command:

```powershell
$env:ALLOW_PROJECTION_CONTEXT_REFRESH = "true"
.\venv\Scripts\python.exe -m src.projection_engine --horizon weekly --season 2025 --week 18 --scoring-profile ppr --league-type redraft --roster-format one_qb --limit 100
Remove-Item Env:\ALLOW_PROJECTION_CONTEXT_REFRESH
```

Result:

| Metric | Value |
| --- | --- |
| exit code | 0 |
| model_run_id | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` |
| feature_config_version_id | `baseline_weekly_v1` |
| source_freshness_snapshot_id | `freshness-20260618T044025Z-bd445907` |
| projection_rows | 100 |
| ranking_rows | 100 |
| authorization after command | unset |

## Trade Score Dry-Run After Projection Plan

Command:

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v0_2025_001 --dry-run
```

Dry-run summary after the projection refresh:

| Metric | Value |
| --- | ---: |
| score rows before | 0 |
| score rows after | 0 |
| wrote | `false` |
| candidate rows | 100 |
| trade score min | 11.5784 |
| trade score max | 55.2387 |
| trade score avg | 33.9357 |
| confidence min | 28.66 |
| confidence max | 57.0 |
| confidence avg | 48.5489 |
| `missing_model_run_id` | 48 |
| `stale_projection_context` | 1 |
| `missing_fraud_context` | 45 |
| `temporary_name_join_identity` | 87 |
| draft pick assets | 13 |

The projection refresh improved model-run coverage, but not enough to recommend score materialization.

Top 10 score dry-run rows:

| Rank | Player | Pos | Team | Score | Confidence | Model run | Tier |
| ---: | --- | --- | --- | ---: | ---: | --- | --- |
| 1 | Bijan Robinson | RB | ATL | 55.2387 | 50.53 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 2 | Jeremiyah Love | RB | ARI | 52.8696 | 52.0 |  | flex |
| 3 | Jahmyr Gibbs | RB | DET | 50.5711 | 50.53 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 4 | Ja'Marr Chase | WR | CIN | 50.5418 | 49.35 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 5 | Drake Maye | QB | NE | 50.4203 | 43.66 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 6 | CeeDee Lamb | WR | DAL | 49.6311 | 51.5 |  | flex |
| 7 | Puka Nacua | WR | LAR | 49.3276 | 43.72 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 8 | Josh Allen | QB | BUF | 49.21 | 42.97 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 9 | Jaxon Smith-Njigba | WR | SEA | 48.1628 | 50.53 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 10 | 2026 Pick 1.01 | PICK |  | 48.062 | 49.0 |  | flex |

## Verification After Authorized Refresh

Read-only checks after the phase:

| Object | Target rows |
| --- | ---: |
| `trade_player_scores` | 0 |
| `projection_rankings_current` 2025 week 18 PPR redraft one-QB | 100 |
| `projections_player_weekly` 2025 week 18 PPR redraft one-QB | 100 |

## Local Checks

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 passed, 0 failed |

## Recommendation

Do not materialize Trade Analyzer score rows yet.

Next gated step:

1. Investigate the remaining 48 rows with `missing_model_run_id`.
2. Reduce `temporary_name_join_identity` usage before write approval.
3. Reassess confidence thresholds after identity coverage improves.
4. Keep `ALLOW_TRADE_SCORE_MATERIALIZATION` unset until the next explicit approval.

Final decision: `PROJECTION CONTEXT REFRESHED WITH WARNINGS`.
