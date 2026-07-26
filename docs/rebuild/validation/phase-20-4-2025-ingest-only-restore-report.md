# Phase 20.4 2025 Ingest-Only Restore Report

## Purpose

Phase 20.4 tested the bounded 2025 source restore path for `play_by_play` and `weekly_metrics` using the safe ingest-only pipeline mode. The run used plan-only first and did not write data because `ALLOW_MODERN_SOURCE_INGEST=true` was not set in the local environment.

## Authorization State

| Gate | Value |
| --- | --- |
| `ALLOW_MODERN_SOURCE_INGEST` | unset |
| Write authorized | no |
| Live ingest run | no |
| Downstream materialization run | no |

Final authorization result: not authorized to write.

## Preflight

Commands run with the repo venv:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_pipeline_plan
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
```

Results:

| Check | Result |
| --- | --- |
| `tests.test_pipeline_plan` | pass, 8 tests |
| Full unittest discovery | pass, 309 tests |
| `app.py` compile | pass |
| `src` and `scripts` compile | pass |

## Source Coverage Before Restore

Bounded BigQuery row-count checks were run for season `2025` in project `fantasy-football-498121`, dataset `fantasy_football_brain`.

| Table | 2025 rows | Weeks found |
| --- | ---: | --- |
| `play_by_play` | 0 | none |
| `weekly_metrics` | 0 | none |
| `analytics_player_weekly_truth` | 0 | none |
| `analytics_fraud_watch` | 0 | none |

The current warehouse still lacks 2025 source rows needed for modern-season truth tables and current-season Fraud Watch.

## Plan-Only Command

Command run:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --season 2025 --ingest-only --plan-only
```

Plan-only result:

| Field | Value |
| --- | --- |
| Seasons | `2025` |
| Bounded by | `season` |
| Week bounds supported | `false` |
| Source library | `nflreadpy` |
| Dataset | `fantasy_football_brain` |
| Write disposition | `WRITE_APPEND` |
| Ingest only | `true` |
| Plan mode writes BigQuery | `false` |
| Live ingest would write BigQuery | `true` |
| Live ingest would materialize derived analytics | `false` |
| Live ingest would call LLMs | `false` |
| Live ingest would scrape | `false` |
| Live ingest would trigger Cloud Run Jobs | `false` |
| Raw load truncate risk | `false` |
| Derived materialization in ingest-only | skipped |

Planned raw/source tables:

| Table |
| --- |
| `play_by_play` |
| `weekly_metrics` |
| `team_descriptions` |
| `draft_picks` |
| `player_rosters` |
| `player_contracts` |
| `ngs_passing` |
| `ngs_rushing` |
| `ngs_receiving` |
| `ftn_charting` |
| `weekly_snap_counts` |
| `injury_reports` |
| `depth_charts` |

Plan notes confirmed:

- Plan mode does not extract, transform, load, or materialize data.
- Ingest-only mode extracts, transforms, and loads source tables, then stops before derived analytics materialization.
- `WRITE_APPEND` is the intended modern season restore mode.
- `WRITE_TRUNCATE` requires `--allow-full-refresh` for live runs.
- Derived analytics materialization remains separate and was not run.

## Ingest Command

No ingest command was run because the authorization gate was not satisfied.

Authorized command for a future restore:

```powershell
$env:ALLOW_MODERN_SOURCE_INGEST="true"
.\venv\Scripts\python.exe -m src.pipeline --season 2025 --ingest-only
```

Required safeguards for that future run:

- Keep `WRITE_APPEND`.
- Do not pass `--allow-full-refresh`.
- Do not pass `--write-disposition WRITE_TRUNCATE`.
- Do not run downstream materialization in the same prompt.
- Verify `play_by_play` and `weekly_metrics` coverage after ingest.

## Source Coverage After Restore

No after-restore checks were needed because no live ingest was run.

| Table | After state |
| --- | --- |
| `play_by_play` | unchanged, 0 rows for 2025 |
| `weekly_metrics` | unchanged, 0 rows for 2025 |

## Safety Status

| Safety rule | Status |
| --- | --- |
| No scraping | pass |
| No LLM calls | pass |
| No Firebase artifacts | pass |
| No unbounded ingestion | pass |
| No destructive overwrite | pass |
| No downstream mart rebuild | pass |
| No ranking, projection, or content jobs | pass |
| No Cloud Run Jobs triggered | pass |

## Blockers

The only blocker is missing authorization:

```text
ALLOW_MODERN_SOURCE_INGEST=true
```

Without that explicit gate, Phase 20.4 correctly stopped after plan-only.

## Initial Decision

`2025 SOURCE RESTORE NOT AUTHORIZED`

At the time of the initial run, the ingest-only path was ready for a bounded 2025 source restore once the operator explicitly authorized the write. The warehouse still had no 2025 `play_by_play` or `weekly_metrics` rows before the later live authorization addendum below.

## Live Authorization Addendum

Phase 20.4A later clarified that the successful 2025 source-row load was run through the browser admin by the operator's partner. The local Codex live pipeline attempts failed on the `play_by_play` append schema mismatch below and should not be treated as the successful origin of the loaded source rows. See `docs/rebuild/validation/phase-20-4a-unexpected-ingest-investigation-report.md`.

The operator later authorized the bounded 2025 ingest-only restore by requesting `ALLOW_MODERN_SOURCE_INGEST=true`.

Authorization and command:

```powershell
$env:ALLOW_MODERN_SOURCE_INGEST="true"
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_APPEND --dataset fantasy_football_brain --ingest-only
```

Plan-only was rerun first:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_APPEND --dataset fantasy_football_brain --ingest-only --plan-only
```

Plan-only confirmed:

| Field | Value |
| --- | --- |
| Season bound | `2025` |
| Write disposition | `WRITE_APPEND` |
| `--allow-full-refresh` used | no |
| `WRITE_TRUNCATE` used | no |
| Ingest only | yes |
| Downstream materialization | no |
| LLM calls | no |
| Scraping | no |
| Cloud Run Jobs triggered | no |

### Live Run Result

The live pipeline process exited with status `1` after logging a BigQuery append schema mismatch on `play_by_play`:

```text
Provided Schema does not match Table fantasy-football-498121:fantasy_football_brain.play_by_play. Field lateral_sack_player_id has changed type from STRING to INTEGER
```

Despite the nonzero process exit, post-run bounded row-count checks confirmed that the required 2025 source rows are now present.

| Table | Rows before live run | Rows after live run | Week coverage after |
| --- | ---: | ---: | --- |
| `play_by_play` | 0 | 48,771 | weeks 1 through 22 |
| `weekly_metrics` | 0 | 19,421 | weeks 1 through 22 |

Additional 2025 raw/source table counts observed after the run:

| Table | 2025 rows |
| --- | ---: |
| `team_descriptions` | 36 |
| `draft_picks` | 257 |
| `player_rosters` | 25,040 |
| `player_contracts` | 51,629 |
| `ngs_passing` | 605 |
| `ngs_rushing` | 648 |
| `ngs_receiving` | 1,402 |
| `ftn_charting` | 47,316 |
| `weekly_snap_counts` | 26,612 |
| `injury_reports` | 6,068 |
| `depth_charts` | 554,215 |

### Live Addendum Decision

`2025 SOURCE RESTORE PARTIAL`

The required `play_by_play` and `weekly_metrics` source coverage now exists for 2025, but the ingest-only command did not exit cleanly. Do not rerun the same `WRITE_APPEND` command without a duplicate-control plan. The next safe step is to rerun Phase 20.5 current-season mart planning against the newly present source rows, while separately hardening the append path for schema-aware loads.
