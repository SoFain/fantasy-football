# Phase 29.46 Staging Materialization 2025 Report

Final decision: **2025 STAGING MATERIALIZED WITH WARNINGS**

## Scope

Owner correction accepted: the Phase 29.44 current-season lane recommendation remains superseded for this task. Season 2025 was treated as a completed historical season and continued through the Phase 29 completed-season lane.

This phase wrote only 2025 rows to the six `stg_*` nflverse staging tables:

- `stg_player_identity`
- `stg_game_context`
- `stg_player_week_stats`
- `stg_team_week_stats`
- `stg_play_player_events`
- `stg_participation_context`

No raw backfill, advanced metrics materialization, Pigskin packet refresh, current metric view write, deployment, ranking build, Cloud Run Job, Scheduler job, LLM call, Pigskin prompt, scrape, or feature flag change was run.

## Authorization Gate

Pre-run gates were all empty or unset:

| Gate | State |
|---|---|
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

Live staging gate was set only inside the same-session wrapper:

```powershell
try {
  $env:ALLOW_NFLVERSE_STAGING_MATERIALIZATION = "true"
  .\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2025 --season-end 2025 --all-targets --write --strict
} finally {
  Remove-Item Env:\ALLOW_NFLVERSE_STAGING_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

Post-wrapper checks confirmed `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` was removed. Historical backfill, advanced metrics, Pigskin packet, weekly refresh, production deploy, and local subprocess gates remained unset.

## Git State

Latest commit at start: `3c83af6 Expand nflverse Pigskin packets through 2024`.

No files were staged. The working tree still contains the known untracked historical validation backlog and owner-review reports, including:

- `docs/rebuild/validation/phase-29-44-2025-current-season-lane-decision-report.md`
- `docs/rebuild/validation/phase-29-45-raw-backfill-2025-report.md`

No tracked Phase 29 package files were modified unexpectedly before the staging write.

## Baseline Checks

All baseline checks passed before the write:

| Check | Result |
|---|---|
| `scripts/check_deployment_safety.py` | pass |
| `py_compile src\nflverse_staging.py` | pass |
| `py_compile src\nflverse_backfill.py` | pass |
| `py_compile src\nflverse_backfill_plan.py` | pass |
| `compileall -q src scripts` | pass |
| `unittest tests.test_nflverse_staging` | pass, 11 tests |
| `unittest tests.test_nflverse_backfill_executor` | pass, 18 tests |
| `unittest discover tests` | pass, 487 tests |
| `scripts/run_bigquery_migrations.py --list-pending` | no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | catalog discovered through 200 |

## Raw Source Precheck

Read-only counts confirmed 2025 raw source coverage from Phase 29.45.

| Table | Total rows | 2025 rows | 2026+ rows | Season range | Week range |
|---|---:|---:|---:|---|---|
| `raw_nflverse_schedules` | 3,295 | 285 | 0 | 2014-2025 | 1-22 |
| `raw_nflverse_rosters` | 35,336 | 3,134 | 0 | 2014-2025 | n/a |
| `raw_nflverse_rosters_weekly` | 526,550 | 46,831 | 0 | 2014-2025 | 1-22 |
| `raw_nflverse_weekly` | 217,230 | 19,399 | 0 | 2014-2025 | 1-22 |
| `raw_nflverse_pbp` | 580,005 | 48,771 | 0 | 2014-2025 | 1-22 |
| `raw_nflverse_snap_counts` | 300,812 | 26,612 | 0 | 2014-2025 | 1-22 |

Static/global raw tables were unchanged:

| Table | Row count |
|---|---:|
| `raw_nflverse_teams` | 36 |
| `raw_nflverse_players` | 25,033 |
| `raw_nflverse_ff_playerids` | 69,060 |

## Staging Pre-Write State

Read-only counts confirmed all six staging targets had 0 rows for 2025 before the materialization write.

| Table | Total before | 2025 rows before | 2026+ rows before | Season range before | Week range before |
|---|---:|---:|---:|---|---|
| `stg_player_identity` | 479,719 | 0 | 0 | 2014-2024 | 1-22 |
| `stg_game_context` | 3,010 | 0 | 0 | 2014-2024 | 1-22 |
| `stg_player_week_stats` | 197,831 | 0 | 0 | 2014-2024 | 1-22 |
| `stg_team_week_stats` | 6,020 | 0 | 0 | 2014-2024 | 1-22 |
| `stg_play_player_events` | 1,291,263 | 0 | 0 | 2014-2024 | 1-22 |
| `stg_participation_context` | 274,200 | 0 | 0 | 2014-2024 | 1-22 |

## Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2025 --season-end 2025 --dry-run --all-targets --strict
```

Result: pass, `dry_run=true`, `wrote=false`.

| Target | Planned rows | Source rows | Duplicate grain count | Readiness | Identity gaps | Route share non-null | True route source |
|---|---:|---:|---:|---|---:|---:|---:|
| `stg_player_identity` | 46,831 | n/a | 0 | ready with warnings | n/a | n/a | n/a |
| `stg_game_context` | 285 | 285 | 0 | ready | n/a | n/a | n/a |
| `stg_player_week_stats` | 19,399 | 19,399 | 0 | ready with warnings | 0 | n/a | n/a |
| `stg_team_week_stats` | 570 | 48,771 | 0 | ready with warnings | n/a | n/a | n/a |
| `stg_play_player_events` | 116,369 | 48,771 | 0 | ready with warnings | 0 | n/a | n/a |
| `stg_participation_context` | 26,612 | 26,612 | 0 | ready with warnings | 80 | 0 | 0 |

Dry-run warnings were expected:

- default mode is read-only and writes require `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`;
- raw `raw_nflverse_*` tables remain internal and are not Pigskin or UI-safe surfaces;
- `stg_participation_context` uses PFR identifiers from snap counts, with 80 missing identity matches;
- `route_share` remains null and `has_true_route_source` remains false.

No target was blocked unexpectedly.

## Live Staging Write Result

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_staging --season-start 2025 --season-end 2025 --all-targets --write --strict
```

Result: pass, exit 0, `wrote=true`.

All writes used `MERGE`.

| Target | DML affected rows | Bounded 2025 rows after | Duplicate grain count after | Missing freshness rows | Missing flags rows |
|---|---:|---:|---:|---:|---:|
| `stg_player_identity` | 46,831 | 46,831 | 0 | 0 | 0 |
| `stg_game_context` | 285 | 285 | 0 | 0 | 0 |
| `stg_player_week_stats` | 19,399 | 19,399 | 0 | 0 | 0 |
| `stg_team_week_stats` | 570 | 570 | 0 | 0 | 0 |
| `stg_play_player_events` | 116,369 | 116,369 | 0 | 0 | 0 |
| `stg_participation_context` | 26,612 | 26,612 | 0 | 0 | 0 |

## Post-Write Staging Verification

All diagnostics below are scoped to `season = 2025` except total row count and full season range.

| Table | Total after | 2025 rows | 2026+ rows | Season range | 2025 week range | Duplicate groups | Missing required fields | Missing identity | Missing freshness | Missing flags |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| `stg_player_identity` | 526,550 | 46,831 | 0 | 2014-2025 | 1-22 | 0 | 0 | 0 | 0 | 0 |
| `stg_game_context` | 3,295 | 285 | 0 | 2014-2025 | 1-22 | 0 | 0 | n/a | 0 | 0 |
| `stg_player_week_stats` | 217,230 | 19,399 | 0 | 2014-2025 | 1-22 | 0 | 0 | 0 | 0 | 0 |
| `stg_team_week_stats` | 6,590 | 570 | 0 | 2014-2025 | 1-22 | 0 | 0 | n/a | 0 | 0 |
| `stg_play_player_events` | 1,407,632 | 116,369 | 0 | 2014-2025 | 1-22 | 0 | 0 | 0 | 0 | 0 |
| `stg_participation_context` | 300,812 | 26,612 | 0 | 2014-2025 | 1-22 | 0 | 0 | 80 | 0 | 0 |

Route metrics remain blocked:

| Table | 2025 `route_share` non-null rows | 2025 `has_true_route_source=true` rows |
|---|---:|---:|
| `stg_participation_context` | 0 | 0 |

## Identity Gap Summary

Only `stg_participation_context` has documented identity gaps:

- 80 of 26,612 2025 snap-count participation rows have `missing_identity_match=true`.
- 26,532 participation rows matched identity by PFR bridge.
- No identity gaps appeared in `stg_player_identity`, `stg_player_week_stats`, or `stg_play_player_events`.

These gaps are visible in `missing_data_flags`; they were not hidden or coerced.

## 2025 and Week 22 Behavior

All six staging targets now span 2025 Week 1 through Week 22 where a week column exists. This is consistent with the accepted completed-season, postseason-inclusive 2025 source behavior.

No 2026+ rows were written to the staging targets.

## Non-Target Object Verification

Raw nflverse counts remained unchanged from Phase 29.45 post-write:

| Table | Total rows | 2025 rows | 2026+ rows |
|---|---:|---:|---:|
| `raw_nflverse_schedules` | 3,295 | 285 | 0 |
| `raw_nflverse_rosters` | 35,336 | 3,134 | 0 |
| `raw_nflverse_rosters_weekly` | 526,550 | 46,831 | 0 |
| `raw_nflverse_weekly` | 217,230 | 19,399 | 0 |
| `raw_nflverse_pbp` | 580,005 | 48,771 | 0 |
| `raw_nflverse_snap_counts` | 300,812 | 26,612 | 0 |
| `raw_nflverse_teams` | 36 | n/a | n/a |
| `raw_nflverse_players` | 25,033 | n/a | n/a |
| `raw_nflverse_ff_playerids` | 69,060 | n/a | n/a |

Advanced metrics and Pigskin packet objects remained unchanged:

| Object | Total rows | 2025 rows | 2026+ rows |
|---|---:|---:|---:|
| `player_week_advanced_metrics` | 197,831 | 0 | 0 |
| `team_week_context_metrics` | 6,020 | 0 | 0 |
| `qb_week_environment_metrics` | 7,350 | 0 | 0 |
| `player_recent_advanced_metrics_current` | 5,883 | n/a | n/a |
| `player_role_usage_metrics_current` | 5,883 | n/a | n/a |
| `pigskin_player_context_packet_current` | 3,574 | n/a | n/a |
| `compat_pigskin_player_context_current` | 3,574 | n/a | n/a |

Score lanes remained unchanged:

| Object | Total rows | Notes |
|---|---:|---|
| `trade_player_scores` | 154 | existing 2025 trade score lane, outside nflverse staging |
| `trade_player_scores_current` | 77 | unchanged |
| `compat_trade_player_scores_current` | 77 | unchanged |
| `trade_pick_scores` | 64 | unchanged |
| `trade_pick_scores_current` | 64 | unchanged |
| `compat_trade_pick_scores_current` | 64 | unchanged |

## Validation Results

| Pattern | Result |
|---|---|
| `raw_nflverse` | 3 passed, 0 failed. Coverage review warning returned 2014-2025 rows. |
| `stg_` | 7 passed, 0 failed. |
| `advanced_metrics` | 4 passed, 0 failed. |
| `compat_pigskin` | 2 passed, 0 failed. |
| `trade_player_scores` | 12 passed, 0 failed. |
| `trade_pick_scores` | 17 passed, 0 failed. Existing model-version coverage review warning only. |

## Final Local Checks

All final checks passed after staging materialization:

| Check | Result |
|---|---|
| `scripts/check_deployment_safety.py` | pass |
| `py_compile src\nflverse_staging.py` | pass |
| `py_compile src\nflverse_backfill.py` | pass |
| `py_compile src\nflverse_backfill_plan.py` | pass |
| `compileall -q src scripts` | pass |
| `unittest tests.test_nflverse_staging` | pass, 11 tests |
| `unittest tests.test_nflverse_backfill_executor` | pass, 18 tests |
| `unittest discover tests` | pass, 487 tests |
| `scripts/run_bigquery_migrations.py --list-pending` | no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | catalog discovered through 200 |

## Staging and Production Untouched

Read-only Cloud Run describes confirmed no deployment occurred.

| Service | Revision | Traffic | Image digest | Relevant flag state |
|---|---|---|---|---|
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100 percent to `00077-2jp` | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | all production risk flags false, score flags false, Trade History compat false, Data Ops trigger/local subprocess flags false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100 percent to `00029-jtb` | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | staging score/history flags true as before, Data Ops trigger/local subprocess flags false |

## Remaining Warnings

- `stg_participation_context` has 80 documented 2025 identity gaps from PFR-based snap-count matching.
- `route_share` remains null and `has_true_route_source` remains false by design.
- 2025 includes Week 22 coverage, consistent with postseason-inclusive historical source behavior.
- `raw_nflverse` validation includes an informational coverage review row now spanning 2014-2025.
- `trade_pick_scores` validation includes the existing informational model-version coverage warning.
- The staging dry-run output still includes a stale wording reference to "Phase 29.8 staging writes" even though this authorized execution is Phase 29.46. The gate used was the correct `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`.

## Recommended Next Phase

Proceed to a separate authorized 2025 base advanced metrics materialization phase. Keep Pigskin packet refresh as a later, separate phase after advanced metrics are validated.
