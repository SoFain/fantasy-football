# Phase 29.40 - 2024 Advanced Metrics Materialization Report

## Final Decision

**2024 ADVANCED METRICS MATERIALIZED WITH WARNINGS**

The 2024 base advanced metrics were dry-run first, then materialized with the single authorized gate in a same-session PowerShell wrapper. The write touched only:

- `player_week_advanced_metrics`
- `team_week_context_metrics`
- `qb_week_environment_metrics`

No 2025 or current-season rows were written. No raw backfill, staging materialization, Pigskin packet refresh, deployment, Cloud Run Job trigger, Scheduler job, LLM call, scrape, or commit occurred.

## Authorization Gate

Before the write, all checked gates were empty or unset:

- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

Live write gate was set only inside this wrapper:

```powershell
try {
$env:ALLOW_ADVANCED_METRICS_MATERIALIZATION = "true"

echo "ALLOW_ADVANCED_METRICS_MATERIALIZATION=$env:ALLOW_ADVANCED_METRICS_MATERIALIZATION"

.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2024 --season-end 2024 --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --write --strict --metric-version nflverse_adv_metrics_v0_2024_001

} finally {
Remove-Item Env:\ALLOW_ADVANCED_METRICS_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

After the wrapper, all checked gates were empty or unset again.

## Git State

- Latest commit: `e56afa3 Expand nflverse Pigskin packets through 2023`
- No files staged.
- Working tree still contains the known historical untracked validation backlog.
- Newly relevant untracked Phase 29 reports before this report: `phase-29-38-raw-backfill-2024-report.md`, `phase-29-39-staging-materialization-2024-report.md`.

## Baseline Checks

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_advanced_metrics.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_staging.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill.py`
- `.\venv\Scripts\python.exe -m py_compile src\nflverse_backfill_plan.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_advanced_metrics`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_staging`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

Results:

- Safety checker passed.
- `tests.test_nflverse_advanced_metrics`: 12 tests passed.
- `tests.test_nflverse_staging`: 11 tests passed.
- Full suite: 487 tests passed.
- No pending migrations.
- Validation catalog discovered through `200`.

## Staging Source Precheck

Read-only 2024 staging source counts matched Phase 29.39:

| Table | 2024 rows | Week range | 2025+ rows |
|---|---:|---:|---:|
| `stg_player_identity` | 46,572 | 1-22 | 0 |
| `stg_game_context` | 285 | 1-22 | 0 |
| `stg_player_week_stats` | 18,959 | 1-22 | 0 |
| `stg_team_week_stats` | 570 | 1-22 | 0 |
| `stg_play_player_events` | 118,037 | 1-22 | 0 |
| `stg_participation_context` | 26,615 | 1-22 | 0 |

## Feature Pre-Write State

Before the 2024 feature write:

| Object | Total rows | 2024 rows | 2025+ rows |
|---|---:|---:|---:|
| `player_week_advanced_metrics` | 178,872 | 0 | 0 |
| `team_week_context_metrics` | 5,450 | 0 | 0 |
| `qb_week_environment_metrics` | 6,643 | 0 | 0 |
| `player_recent_advanced_metrics_current` | 5,497 | derived view | n/a |
| `player_role_usage_metrics_current` | 5,497 | derived view | n/a |
| `pigskin_player_context_packet_current` | 3,082 | unchanged | n/a |
| `compat_pigskin_player_context_current` | 3,082 | unchanged | n/a |

## Dry-Run Summary

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_advanced_metrics --season-start 2024 --season-end 2024 --dry-run --target player_week_advanced_metrics --target team_week_context_metrics --target qb_week_environment_metrics --strict --metric-version nflverse_adv_metrics_v0_2024_001
```

Result: exit `0`, `wrote=false`, three target summaries produced.

| Target | Planned rows | Source rows | Duplicate grains | Readiness |
|---|---:|---:|---:|---|
| `player_week_advanced_metrics` | 18,959 | 18,959 | 0 | Ready with warnings |
| `team_week_context_metrics` | 570 | 570 | 0 | Ready with warnings |
| `qb_week_environment_metrics` | 707 | 20,082 source candidate rows | 0 | Ready with warnings |

Dry-run diagnostics:

- `player_week_advanced_metrics`: `target_share` null count 0, `air_yards_share` null count 13,371, `wopr` null count 13,371, `epa_per_opportunity` null count 13,474, `snap_share` null count 20.
- `team_week_context_metrics`: `pass_rate_over_expected` null count 570, red-zone model metrics blocked count 570, EPA coverage count 570.
- `qb_week_environment_metrics`: missing QB identity count 44, sack/scramble fields unavailable count 707, CPOE coverage count 694, EPA coverage count 707, null dropbacks 0.

Unsafe metrics stayed blocked in the dry-run plan.

## Live Write Result

Command used the same target list and metric version with `--write --strict`.

| Target | Affected rows | 2024 rows after write | Duplicate grains | Feature run IDs | Metric versions |
|---|---:|---:|---:|---:|---:|
| `player_week_advanced_metrics` | 18,959 | 18,959 | 0 | 1 | 1 |
| `team_week_context_metrics` | 570 | 570 | 0 | 1 | 1 |
| `qb_week_environment_metrics` | 707 | 707 | 0 | 1 | 1 |

Write kind was `MERGE` for each target. The metric version was `nflverse_adv_metrics_v0_2024_001`.

## Post-Write Feature Verification

| Target | Total rows | 2024 rows | 2025+ rows | Season range | Week range | Source freshness missing | Missing flags missing |
|---|---:|---:|---:|---|---|---:|---:|
| `player_week_advanced_metrics` | 197,831 | 18,959 | 0 | 2014-2024 | 1-22 | 0 | 0 |
| `team_week_context_metrics` | 6,020 | 570 | 0 | 2014-2024 | 1-22 | 0 | 0 |
| `qb_week_environment_metrics` | 7,350 | 707 | 0 | 2014-2024 | 1-22 | 0 | 0 |

Post-write range and grain checks:

- Duplicate grains: 0 for all three targets.
- Invalid metric range rows: 0 for all three targets.
- Blocked metric non-null rows: 0 for all three targets.
- 2025 or later rows: 0 for all three targets.

Detailed null checks:

| Target | Notable null counts |
|---|---|
| `player_week_advanced_metrics` | `target_share` 0, `air_yards_share` 13,371, `wopr` 13,371, `epa_per_opportunity` 13,474, `epa_total` 13,371, `success_rate` 13,371, `cpoe` 13,838, `snap_share` 20 |
| `team_week_context_metrics` | `seconds_per_play` 570, `pass_rate_over_expected` 570, `pass_epa_per_play` 570, `rush_epa_per_play` 570, `red_zone_pass_rate` 570, `red_zone_rush_rate` 570, `team_epa_per_play` 0, `team_success_rate` 0 |
| `qb_week_environment_metrics` | `sacks` 707, `scrambles` 707, `designed_rushes` 707, `sack_rate` 707, `scramble_rate` 707, `pass_rate_over_expected_context` 707, `cpoe` 13, `epa_per_dropback` 0, `deep_attempt_rate` 0 |

## Metric Sanity Results

Sanity queries used neutral aliases such as `row_count`, `metric_snapshot`, and `target_snapshot`; no BigQuery alias named `rows` was used.

Player examples from top-ranked sanity slices:

- Top WOPR example: `M.Nabers`, WR, NYG, Week 2, WOPR `1.4366`, target share `0.6207`, air yards share `0.7222`.
- Top target share example: `M.Nabers`, WR, NYG, Week 2, target share `0.6207`, targets `18`.
- Top weighted opportunity example: `G.Wilson`, WR, NYJ, Week 5, weighted opportunity `55.0`, targets `22`.
- Top EPA per opportunity sample-size example: `D.Lock`, QB, NYG, Week 17, EPA per opportunity `5.507`, opportunities `5`.

Team examples:

- Top team EPA per play: DET vs JAX, Week 11, `0.4441`, success rate `0.6703`, plays `92`.
- Bottom team EPA per play: DAL vs PHI, Week 10, `-0.4867`, success rate `0.44`, plays `75`.
- Neutral pass rate distribution: min `0.0`, average `0.4217`, max `1.0`, `pass_rate_over_expected` null count `570`.

QB examples:

- Top QB EPA per dropback: `D.Lock`, NYG, Week 17, `1.2013`, dropbacks `23`, CPOE `10.6579`.
- Bottom QB EPA per dropback: `W.Levis`, TEN, Week 15, `-0.9461`, dropbacks `13`, CPOE `-4.4979`.
- QB coverage: 707 rows, CPOE coverage 694 rows, deep attempt coverage 707 rows.

Position null review:

- WR: 2,542 rows, null WOPR 321, zero-opportunity rows 326.
- RB: 1,597 rows, null WOPR 172, zero-opportunity rows 172.
- TE: 1,287 rows, null WOPR 146, zero-opportunity rows 148.
- QB: 697 rows, null WOPR 0, zero-opportunity rows 83.
- Defensive, special-team, and offensive-line positions mostly have null WOPR by design because they do not have offensive opportunity rows.

No formula tuning was performed.

## Blocked Metric Confirmation

The following metric families remain intentionally null or blocked unless true source fields are proven:

- Route metrics: route share, yards per route run, targets per route run.
- First-read metrics.
- Pressure and sack source metrics.
- Contact-yard metrics.
- Slot, wide, inline alignment.
- Red-zone, inside-10, inside-5, high-value, touchdown, and reception-dependent metrics.
- Team pass rate over expected until a model source exists.

Blocked metric non-null count was 0 after write.

## Derived Current-View Behavior

The current metric views changed because they are derived from base metrics. No direct write was run against these views.

| Object | Count after write | Behavior |
|---|---:|---|
| `player_recent_advanced_metrics_current` | 5,883 | Derived from base metrics |
| `player_role_usage_metrics_current` | 5,883 | Derived from base metrics |
| `pigskin_player_context_packet_current` | 3,082 | Unchanged |
| `compat_pigskin_player_context_current` | 3,082 | Unchanged |

## 2024 Week 22 Behavior

Week 22 rows were materialized as part of the 2024 historical, postseason-inclusive batch:

| Target | 2024 Week 22 rows | Feature run IDs | Metric versions | 2025+ rows |
|---|---:|---:|---:|---:|
| `player_week_advanced_metrics` | 69 | 1 | 1 | 0 |
| `team_week_context_metrics` | 2 | 1 | 1 | 0 |
| `qb_week_environment_metrics` | 3 | 1 | 1 | 0 |

Week 22 is historical-only in this phase and was not treated as current-season content.

## 2025 And Current-Season Separation

Confirmed:

- 2025 or later source rows in 2024 staging checks: 0.
- 2025 or later rows in all three advanced metric targets: 0.
- No current-season lane was run.
- No Pigskin packet refresh was run.
- No rankings, content packet, or LLM path was run.

## Non-Target Object Verification

Raw nflverse counts remained bounded through 2024, with 2025+ counts at 0 for season-bearing raw tables. Examples:

- `raw_nflverse_pbp`: 531,234 total, 49,492 rows for 2024, season range 2014-2024.
- `raw_nflverse_weekly`: 197,831 total, 18,959 rows for 2024, season range 2014-2024.
- `raw_nflverse_snap_counts`: 274,200 total, 26,615 rows for 2024, season range 2014-2024.

Staging counts remained the same as the pre-write snapshot.

Score lanes remained unchanged:

| Object | Count |
|---|---:|
| `trade_player_scores` | 154 |
| `trade_player_scores_current` | 77 |
| `compat_trade_player_scores_current` | 77 |
| `trade_pick_scores` | 64 |
| `trade_pick_scores_current` | 64 |
| `compat_trade_pick_scores_current` | 64 |

## Validation Results

Post-write validation commands:

- `raw_nflverse`: 3 passed, 0 failed. Warning: informational season-week coverage review returned 3 rows.
- `stg_`: 7 passed, 0 failed.
- `advanced_metrics`: 4 passed, 0 failed.
- `compat_pigskin`: 2 passed, 0 failed.
- `trade_player_scores`: 12 passed, 0 failed.
- `trade_pick_scores`: 17 passed, 0 failed. Warning: informational model-version coverage returned 1 row.

## Final Local Checks

Passed:

- Safety checker.
- Targeted py_compile checks.
- `compileall -q src scripts`.
- `tests.test_nflverse_advanced_metrics`: 12 tests.
- `tests.test_nflverse_staging`: 11 tests.
- Full test suite: 487 tests.
- Migrations list: no pending migrations.
- Validation dry-run: catalog discovered through `200`.

## Staging And Production Untouched

Read-only Cloud Run checks:

| Service | Revision | Traffic | Image digest |
|---|---|---:|---|
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100% | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100% | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` |

Production remains all risk flags off:

- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

No deployment occurred.

## Remaining Warnings

- This is a historical 2024 batch and must not be presented as current-season output.
- 2024 includes postseason Week 22 rows.
- `stg_participation_context` retains the known snap-count/PFR identity gap behavior from Phase 29.39.
- Route, red-zone, pressure, first-read, contact-yard, alignment, touchdown, and reception-dependent metrics remain blocked or null.
- `pass_rate_over_expected` remains null until a model source exists.
- Raw nflverse validation season-week coverage is informational and requires review, not a failure.
- Trade pick score model-version coverage validation is informational and unchanged.
- Historical untracked validation backlog remains in the working tree.

## Recommended Next Phase

Run a dry-run Pigskin current-view and packet refresh for 2024 only. Do not refresh Pigskin packets until the 2024 advanced metric rows are accepted for historical packet use and the phase explicitly authorizes that write.
