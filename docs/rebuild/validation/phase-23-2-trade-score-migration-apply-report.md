# Phase 23.2 Trade Score Migration Apply Report

Date: 2026-06-17

## Final Decision

`TRADE SCORE MIGRATION APPLIED`

Migration `0025__trade_analyzer_score_v0.sql` was applied successfully. The migration created the deterministic Trade Analyzer score table and the current and compatibility views. No score rows were materialized.

No deployment, score materialization, feature flag enablement, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, Firebase artifact creation, or production change was performed.

## Authorization State

Required authorization:

- `ALLOW_TRADE_SCORE_MIGRATION_APPLY=true`

The apply command set and verified `ALLOW_TRADE_SCORE_MIGRATION_APPLY=true` inside the same PowerShell invocation before running the migration runner.

No score write authorization was used. `ALLOW_TRADE_SCORE_MATERIALIZATION` was not used in this phase.

## Preflight Results

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, only `0025` pending |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass, 160 validation files discovered |

Deployment safety checks passed:

- no Firebase artifacts
- no tracked secret files
- no secret content
- required files exist
- feature flags default off
- Pigskin `execute_bigquery_sql` remains absent
- `app.py` compiles
- `src` and `scripts` compile

## Pending Migration List Before Apply

```text
Project: fantasy-football-498121
Dataset: fantasy_football_brain
Pending migrations:
- 0025: trade analyzer score v0 (sql)
```

No unrelated pending migrations were present.

## Migration Review

Migration file:

- `bigquery/migrations/0025__trade_analyzer_score_v0.sql`

Safety review:

| Item | Result |
| --- | --- |
| Additive table DDL | pass, `CREATE TABLE IF NOT EXISTS trade_player_scores` |
| Current view | pass, `CREATE OR REPLACE VIEW trade_player_scores_current` |
| Compatibility view | pass, `CREATE OR REPLACE VIEW compat_trade_player_scores_current` |
| Destructive DDL | pass, no `DROP`, `DELETE`, or `TRUNCATE` found |
| Score generation | pass, no score rows generated or backfilled |
| Raw/source exposure | pass, compatibility view reads only `trade_player_scores_current` |
| Firebase artifact risk | pass, no Firebase artifacts created |

The migration is schema-only. It creates the score storage table and view layer needed for later bounded materialization.

## Apply Command

```powershell
$env:ALLOW_TRADE_SCORE_MIGRATION_APPLY = 'true'
if ($env:ALLOW_TRADE_SCORE_MIGRATION_APPLY -ne 'true') {
  Write-Error 'ALLOW_TRADE_SCORE_MIGRATION_APPLY is not true; refusing to apply migration.'
  exit 1
}
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --apply
```

Result:

```text
Pending migrations:
- 0025: trade analyzer score v0 (sql)
Applying 0025: trade analyzer score v0
Applied 1 migration(s).
```

## Migration Ledger After Apply

```text
No pending migrations.
```

## Objects Verified

Read-only BigQuery checks confirmed:

| Object | Type | Schema fields | Row count |
| --- | --- | ---: | ---: |
| `trade_player_scores` | TABLE | 33 | 0 |
| `trade_player_scores_current` | VIEW | 33 | 0 |
| `compat_trade_player_scores_current` | VIEW | 33 | 0 |

The zero row count is expected. Phase 23.2 applied schema only and did not materialize scores.

## Validation Results

Requested validation commands:

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_score` | pass, 1 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market` | pass, 9 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief` | pass, 11 passed, 0 failed |

Additional score-object validation coverage:

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 passed, 0 failed |

The additional score-object validation was run because the requested `--pattern trade_score` filename filter matched only `151_trade_player_scores_trade_score_range.sql`. The broader `trade_player_scores` and `compat_trade_player_scores` filters covered the grain, component range, JSON, source freshness, current view, compatibility view, raw-source dependency, and identity checks.

## Warnings

1. `trade_player_scores` intentionally has zero rows. Score materialization is still pending and must require separate explicit authorization.
2. Feature flags remain disabled. The UI score path is not enabled by this migration.
3. The migration runner applied all pending migrations, but the pre-apply ledger contained only `0025`, so no unrelated migration was applied.

## Next Step

The next gated step is a bounded 2025 week 18 dry-run of `src.trade_player_scores`. Do not write score rows unless `ALLOW_TRADE_SCORE_MATERIALIZATION=true` is explicitly set.

Final decision: `TRADE SCORE MIGRATION APPLIED`.
