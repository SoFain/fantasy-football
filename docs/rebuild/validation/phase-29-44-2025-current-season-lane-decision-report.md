# Phase 29.44 - 2025 Current-Season Lane Decision and Guardrail Audit

Date: 2026-06-30

Final decision: 2025 NEEDS TWO-LANE HISTORICAL AND CURRENT DESIGN

## Executive Decision

Do not run a 2025 write yet.

`core_historical` technically accepts `--season-start 2025 --season-end 2025`, but it treats 2025 as a historical season-range backfill. That is not the right operating model for any lane that is still meant to behave like current-season or refreshable evidence.

Recommended model:
- Keep Phase 29 as the completed-season historical expansion lane.
- Start a separate current-season lane before any refreshable 2025/current-season write.
- Promote current-season rows into the historical lane only after an explicit season-close or owner-approved freeze point.

Recommended next phase:
- `Phase 30.1 - Current-season nflverse lane contracts and guardrails`

Allowed scope for next phase:
- Design only, or code/test-only guardrails.
- Add current-season source freshness contracts, refresh IDs, run metadata, validation SQL, and dry-run planners.
- No writes until a later authorized phase.

Forbidden in next phase unless explicitly authorized:
- Raw backfill writes
- Prepare-only loader runs
- Staging materialization
- Advanced metrics materialization
- Pigskin packet refresh
- Deployment
- Feature flag changes
- Cloud Run Jobs
- LLM-backed actions
- Pigskin prompts
- Scraping or external fetches

## Gate State

All checked gates were unset before and after this phase:
- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

No authorization gate was set.

## Git State

Latest commit:
- `3c83af6 Expand nflverse Pigskin packets through 2024`

Repo state:
- No tracked modifications.
- No files staged.
- Historical validation backlog remains untracked.
- `phase-29-43-2024-expansion-commit-report.md` remains untracked evidence from the prior phase.

No commit was created.

## Baseline Checks

Baseline checks passed:
- `scripts/check_deployment_safety.py`
- `py_compile` for:
  - `src/nflverse_backfill_plan.py`
  - `src/nflverse_backfill.py`
  - `src/nflverse_staging.py`
  - `src/nflverse_advanced_metrics.py`
  - `src/nflverse_pigskin_packets.py`
- `compileall -q src scripts`
- `tests.test_nflverse_backfill_plan`: 15 tests passed
- `tests.test_nflverse_backfill_executor`: 18 tests passed
- `tests.test_nflverse_staging`: 11 tests passed
- `tests.test_nflverse_advanced_metrics`: 12 tests passed
- `tests.test_nflverse_pigskin_packets`: 15 tests passed
- `unittest discover tests`: 487 tests passed
- `scripts/run_bigquery_migrations.py --list-pending`: no pending migrations
- `scripts/run_bigquery_validations.py --dry-run`: validation catalog discovered through `200`

## 2025 and Future Warehouse State

Read-only BigQuery counts used neutral aliases such as `row_count`, `target_snapshot`, and `future_snapshot`.

Raw nflverse tables:

| Table | Total rows | 2025 rows | Future rows |
|---|---:|---:|---:|
| `raw_nflverse_schedules` | 3,010 | 0 | 0 |
| `raw_nflverse_rosters` | 32,202 | 0 | 0 |
| `raw_nflverse_rosters_weekly` | 479,719 | 0 | 0 |
| `raw_nflverse_weekly` | 197,831 | 0 | 0 |
| `raw_nflverse_pbp` | 531,234 | 0 | 0 |
| `raw_nflverse_snap_counts` | 274,200 | 0 | 0 |

Staging tables:

| Table | Total rows | 2025 rows | Future rows |
|---|---:|---:|---:|
| `stg_player_identity` | 479,719 | 0 | 0 |
| `stg_game_context` | 3,010 | 0 | 0 |
| `stg_player_week_stats` | 197,831 | 0 | 0 |
| `stg_team_week_stats` | 6,020 | 0 | 0 |
| `stg_play_player_events` | 1,291,263 | 0 | 0 |
| `stg_participation_context` | 274,200 | 0 | 0 |

Advanced metrics:

| Table | Total rows | 2025 rows | Future rows |
|---|---:|---:|---:|
| `player_week_advanced_metrics` | 197,831 | 0 | 0 |
| `team_week_context_metrics` | 6,020 | 0 | 0 |
| `qb_week_environment_metrics` | 7,350 | 0 | 0 |

Current metric views:

| View | Total rows | 2025 rows | Future rows |
|---|---:|---:|---:|
| `player_recent_advanced_metrics_current` | 5,883 | 0 | 0 |
| `player_role_usage_metrics_current` | 5,883 | 0 | 0 |

Pigskin packets:

| Table or view | Total rows | 2025 rows | Future rows |
|---|---:|---:|---:|
| `pigskin_player_context_packet_current` | 3,574 | 0 | 0 |
| `compat_pigskin_player_context_current` | 3,574 | 0 | 0 |

Score lanes were read-only checked as unrelated lanes:
- `trade_player_scores`: 154 total rows, all with `season = 2025`
- `trade_player_scores_current`: 77 total rows, all with `season = 2025`
- `compat_trade_player_scores_current`: 77 total rows, all with `season = 2025`
- `trade_pick_scores`: 64 total rows, all with `pick_year = 2026`
- `trade_pick_scores_current`: 64 total rows, all with `pick_year = 2026`
- `compat_trade_pick_scores_current`: 64 total rows, all with `pick_year = 2026`

Those score-lane rows were not changed and are outside the nflverse historical/current-season decision.

## 2025 Plan-Only Result

Command:

```powershell
.\venv\Scripts\python.exe -m src.nflverse_backfill_plan --plan-only --preset core_historical --season-start 2025 --season-end 2025
```

Result:
- Exit code: 0
- `dry_run: True`
- `mode: historical_backfill`
- Season range: `2025-2025`
- Selected source families: `schedules`, `teams`, `players`, `ff_playerids`, `rosters`, `rosters_weekly`, `weekly`, `pbp`, `snap_counts`
- Target raw tables include `raw_nflverse_schedules`, `raw_nflverse_rosters`, `raw_nflverse_rosters_weekly`, `raw_nflverse_weekly`, `raw_nflverse_pbp`, and `raw_nflverse_snap_counts`
- Future authorization gate: `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- Global warning: `Raw raw_nflverse_* tables are not Pigskin/UI-safe surfaces.`
- The planner labels the next required phase as authorized historical backfill implementation.

Important planner warnings:
- `pbp`, `weekly`, `rosters_weekly`, and `snap_counts` are season-level loaders.
- Week planning is post-load merge planning, not week-bounded extraction.
- The planner does not distinguish a refreshable current-season lane from a historical season-range backfill.

## Historical vs Current-Season Code Audit

`src/nflverse_backfill_plan.py`:
- The module is explicitly a historical backfill planner.
- `core_historical` includes season-level loaders and uses `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`.
- The planner accepts 2025 without knowing whether 2025 is completed-season historical or current-season refreshable.
- It warns raw tables are not UI/Pigskin-safe.

`src/nflverse_backfill.py`:
- `--write` requires `ALLOW_NFLVERSE_HISTORICAL_BACKFILL=true`.
- `weekly_refresh` mode exists as an argument but execution is blocked.
- `prepare-only` and `inspect-source-schema` call nflreadpy loaders, so they are not allowed in this read-only phase.
- Writes merge into raw tables by natural keys with null-safe merge logic.
- `source_refresh_id` is generated from preset and season range, but there is no current-season run-state or freshness policy.

`src/nflverse_staging.py`:
- Staging writes require `ALLOW_NFLVERSE_STAGING_MATERIALIZATION=true`.
- SQL is season/week bounded.
- MERGE logic is idempotent by staging grain.
- There is no current-season freeze/promotion policy.
- There is no partial-week completeness rule.

`src/nflverse_advanced_metrics.py`:
- Base metric writes require `ALLOW_ADVANCED_METRICS_MATERIALIZATION=true`.
- Week bounds exist.
- Current targets are placeholders and not writable through the current write path.
- Current-placeholder diagnostics require base `player_week_advanced_metrics` rows before rolling current materialization.
- Existing current views select latest available rows, but there is no separate current-season freshness horizon or stale-row guardrail.

`src/nflverse_pigskin_packets.py`:
- Packet writes require `ALLOW_PIGSKIN_PACKET_REFRESH=true`.
- Packet SQL reads current/base feature marts only, not raw/source tables.
- `--as-of-week`, packet version, and source metric version exist.
- The write path is a MERGE into `pigskin_player_context_packet_current`.
- Packet payload uses `current_view_latest_row` as a sample window label.
- There is no current-season packet version contract, freshness age limit, or promotion rule that separates volatile in-season packets from stable historical packets.

## Validation Gap Audit

Existing validations cover:
- Raw table existence and metadata columns.
- Raw coverage as informational review.
- Staging table existence and duplicate grain checks.
- Advanced metrics table existence, grain, range sanity, and denominator flags.
- Source freshness and missing flags presence.
- Compatibility Pigskin view existence and no raw dependencies.
- Blocked route and pressure metrics.
- Trade score lane safety.

Current-season gaps before any 2025 write:
- No validation for partial-week completeness.
- No validation for in-progress games.
- No validation for schedule changes or postponed games.
- No validation for repeated current-season refresh duplicate behavior by refresh ID.
- No source freshness age threshold.
- No validation that current-season packets use a separate version namespace.
- No validation that current-season rows are hidden from stable historical packet surfaces until promoted.
- No validation that current metric views cannot accidentally mix historical and volatile current rows.
- No validation for stale current rows after a failed refresh.
- No validation that 2025/current-season rows do not flow into public Pigskin/context surfaces prematurely.

## Lane Options

### Option A: Continue Phase 29 with 2025 historical-style raw backfill

Benefits:
- Uses the proven 2014-2024 pathway.
- Existing historical raw, staging, advanced, and packet validations are already in place.
- Minimal new code if 2025 is explicitly treated as completed-season historical data.

Risks:
- Unsafe if the intent is current-season behavior.
- `core_historical` uses season-level loaders, not true week-bounded refresh semantics.
- Current views may treat latest 2025 rows as stable without a current-season promotion contract.
- Public-facing packet surfaces could receive volatile rows if packets are refreshed without a separate versioning rule.

Required guardrails:
- Owner must declare 2025 historical/frozen.
- Use historical-only versions such as `nflverse_adv_metrics_v0_2025_historical_001` and `nflverse_pigskin_packet_v0_2025_historical_001`.
- Add validations that 2025 rows are complete enough to be historical.
- Keep current-season/promo labels out of the historical package.

Safe now:
- No. It is technically plannable, but not safe to execute as "current-season" work.

### Option B: Start a separate current-season lane

Benefits:
- Clear semantics for partial, refreshable, and volatile data.
- Avoids mixing current-season rows into stable historical packet surfaces.
- Can add freshness, refresh, and scheduling rules before first write.

Risks:
- Requires new contracts and validations before data can flow.
- More setup before useful packets exist.
- Needs explicit owner decisions about publishability and promotion.

Required guardrails:
- Current-season source contract.
- Refresh run metadata and source freshness age thresholds.
- Partial-week and in-progress game validations.
- Current packet version namespace.
- Current-only compatibility surface or visibility gate.
- Explicit promotion to historical after season close.

Safe now:
- Safe only as design/code/test work. Not safe for writes yet.

### Option C: Two-lane approach

Benefits:
- Keeps completed-season backfills simple.
- Gives current-season refreshes the freshness and volatility controls they need.
- Makes promotion from current to historical explicit.

Risks:
- Requires discipline around version naming and public surfaces.
- Requires both current-season and historical validations.
- More lifecycle states to document.

Proposed split:
- Historical lane: completed seasons only, stable versions, Phase 29 style.
- Current-season lane: refreshable rows, current versions, freshness and partial-week guards.
- Promotion: owner-approved season freeze copies/promotes current-season data into historical versions after validation.

Required validations and flags:
- Current raw/staging/feature/packet row counts by refresh ID.
- Duplicate checks by natural grain and refresh ID.
- Source freshness age limit.
- In-progress game exclusion or explicit tagging.
- Partial-week completeness.
- Current-season packet visibility/promotion gate.
- No raw/staging exposure in Pigskin.
- No current rows in historical packet versions.

Safe now:
- Safe as the recommended design direction. Writes still need a later authorized phase.

## Recommendation

Use the two-lane model.

Explicit answers:

Is it safe to run `core_historical` for 2025 now?
- No, not as a current-season lane. It is technically accepted by the planner, but it runs through historical backfill semantics.

Should 2025 data be treated as historical, current-season, or staged/current?
- Treat it as staged/current until the owner explicitly declares a completed-season historical freeze.

What new guardrails are needed before the first 2025 write?
- Current-season contracts and version naming.
- Refresh ID and source freshness validations.
- Partial-week and in-progress game handling.
- Current-only packet visibility rules.
- Promotion validation from current to historical.
- A dry-run planner that uses `ALLOW_NFLVERSE_WEEKLY_REFRESH` or a new current-season gate, not `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`.

What should the next phase be called?
- `Phase 30.1 - Current-season nflverse lane contracts and guardrails`

What should the next phase be allowed to do?
- Inspect code and contracts.
- Add dry-run planners, validations, and docs.
- Add tests for current-season gates and no-write behavior.
- Run read-only warehouse checks and dry-run validation discovery.

What should remain forbidden?
- Any BigQuery write.
- Any nflreadpy loader call.
- Any prepare-only fetch.
- Any staging, advanced metrics, or packet materialization.
- Any deployment or feature flag change.
- Any Cloud Run Job trigger.
- Any Pigskin prompt or LLM-backed action.

## No-State-Change Confirmation

After the plan-only review and code audit:
- 2025/future raw nflverse rows remain 0.
- 2025/future staging rows remain 0.
- 2025/future advanced metric rows remain 0.
- 2025/future Pigskin packet rows remain 0.
- `pigskin_player_context_packet_current` remains 3,574 rows.
- `compat_pigskin_player_context_current` remains 3,574 rows.
- No deployment occurred.
- No feature flags changed.
- No Cloud Run Jobs were triggered.

## Validation Results

Read-only validation patterns:
- `raw_nflverse`: 3 passed, 0 failed. One informational coverage warning.
- `stg_`: 7 passed, 0 failed.
- `advanced_metrics`: 4 passed, 0 failed.
- `compat_pigskin`: 2 passed, 0 failed.
- `trade_player_scores`: 12 passed, 0 failed.
- `trade_pick_scores`: 17 passed, 0 failed. One informational model-version coverage warning.

## Final Local Checks

Final checks passed:
- `scripts/check_deployment_safety.py`
- `py_compile` for all nflverse modules in scope
- `compileall -q src scripts`
- `tests.test_nflverse_backfill_plan`: 15 tests passed
- `tests.test_nflverse_backfill_executor`: 18 tests passed
- `tests.test_nflverse_advanced_metrics`: 12 tests passed
- `tests.test_nflverse_pigskin_packets`: 15 tests passed
- `unittest discover tests`: 487 tests passed
- `scripts/run_bigquery_migrations.py --list-pending`: no pending migrations
- `scripts/run_bigquery_validations.py --dry-run`: validation catalog discovered through `200`

`tests.test_staging` is not applicable. The module does not exist. The scoped staging module used in the baseline check, `tests.test_nflverse_staging`, passed 11 tests.

## Staging and Production Untouched

Production readback:
- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Data Ops trigger flags: false
- Local subprocess flags: false
- Trade score flags: false
- Trade History compatibility: false

Staging readback:
- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Data Ops trigger flags: false
- Local subprocess flags: false
- Existing staging score and Trade History QA flags remained unchanged.

## Remaining Warnings

- Historical validation backlog remains untracked.
- `phase-29-43-2024-expansion-commit-report.md` remains untracked from the previous phase.
- `raw_nflverse` validation has an informational coverage warning.
- `trade_pick_scores` validation has an informational model-version coverage warning.
- Score lanes contain existing 2025 player-score and 2026 pick-score rows unrelated to the nflverse lane.
- Current-season validation coverage is not sufficient for 2025 writes yet.

## Next Phase

Recommended next phase:
- `Phase 30.1 - Current-season nflverse lane contracts and guardrails`

Recommended purpose:
- Design and implement current-season lane guardrails before any 2025/current-season write.

Do not run a 2025 nflverse write until those guardrails exist and the owner explicitly authorizes the correct lane.
