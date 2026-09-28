# Phase 20.4A Unexpected Ingest Investigation Report

## Purpose

Phase 20.4A investigated why the Phase 20.4 report contained a live ingest addendum and why 2025 source rows appeared after earlier reports showed no 2025 `play_by_play` or `weekly_metrics` rows.

This investigation was read-only for warehouse state. No ingestion, materialization, deployment, Cloud Run Job trigger, Scheduler job, scraping, LLM call, Firebase artifact creation, `WRITE_APPEND`, or `WRITE_TRUNCATE` command was run during Phase 20.4A.

## Operator Clarification

The operator clarified that a 2025 ingest was run through the browser admin by their partner.

That clarification explains the presence of 2025 source rows. The local Codex pipeline commands visible in local logs failed at the `play_by_play` append schema check and should not be treated as the successful origin of the loaded source data.

## Git And Report History

Commands inspected:

```powershell
git status --short
git diff -- docs/rebuild/validation/phase-20-4-2025-ingest-only-restore-report.md
git log --oneline -- docs/rebuild/validation/phase-20-4-2025-ingest-only-restore-report.md
```

Findings:

| Item | Finding |
| --- | --- |
| Phase 20.4 report git status | untracked |
| Git diff for report | no tracked diff because the file is untracked |
| Git log for report | no history because the file is untracked |
| Phase 20.4 report created | 2026-06-16 22:34:44 local |
| Phase 20.4 report last written | 2026-06-16 22:42:21 local |
| Phase 20.5 report created | 2026-06-16 22:37:10 local |

Because the report is untracked, git cannot identify the author or exact commit-level history for the live addendum. The file timestamp and local output logs show the addendum was produced during the Codex session after the Phase 20.5 blocked report.

## Local Shell And Session Evidence

PowerShell history was checked with:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath |
  Select-String "ALLOW_MODERN_SOURCE_INGEST|src.pipeline|--ingest-only|WRITE_APPEND|2025"
```

Finding:

- No matching operator-entered PowerShell history lines were found.

Local evidence files:

| Path | Finding |
| --- | --- |
| `output/phase-20-4/before-coverage.json` | initial read-only check showed 0 source rows |
| `output/phase-20-4/plan-only.log` | non-mutating plan-only output |
| `output/phase-20-5/source-and-mart-coverage-before.json` | Phase 20.5 source check still showed no 2025 `play_by_play` or `weekly_metrics` rows at that time |
| `output/phase-20-4-live/ingest-only.log` | local Codex live attempt at 22:40 failed on `play_by_play` schema mismatch |
| `pipeline_execution.log` | shows local Codex pipeline attempts at 22:40 and 22:42, both failing on the same schema mismatch |

The local logs show extraction and transformation occurred locally, followed by a failed BigQuery load attempt at `play_by_play`. They do not show a clean local ingest completion.

## BigQuery Job History

Read-only INFORMATION_SCHEMA job history was attempted for both project and user scopes:

| View | Result |
| --- | --- |
| `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT` | blocked, 403 access denied |
| `region-us.INFORMATION_SCHEMA.JOBS_BY_USER` | blocked, 403 access denied |

Because the current identity cannot query those job-history views, this investigation could not independently retrieve:

- BigQuery job IDs for the successful browser-admin ingest.
- `user_email` for the successful load jobs.
- exact load-job creation times.
- destination-table write sequence from BigQuery metadata.

The origin is therefore based on operator confirmation plus local evidence that no matching PowerShell command exists and the local Codex pipeline attempts failed.

## Current 2025 Source Counts

Current read-only counts show 2025 source coverage now exists.

| Table | 2025 rows |
| --- | ---: |
| `play_by_play` | 48,771 |
| `weekly_metrics` | 19,421 |
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

`play_by_play` and `weekly_metrics` both cover 2025 weeks 1 through 22.

## Duplicate-Risk Checks

Read-only duplicate checks were run on likely source keys.

| Check | Result |
| --- | --- |
| `play_by_play`: `season`, `week`, `game_id`, `play_id` | 0 duplicate groups, 0 excess rows |
| `weekly_metrics`: `season`, `week`, `player_id` | 0 duplicate groups, 0 excess rows |
| `weekly_metrics`: `season`, `week`, `recent_team`, `player_id` | not applicable, `recent_team` column is absent |

No duplicate cleanup is indicated for the two required source tables based on the available keys.

## Partial-Load Risk

The current warehouse is not partially empty for the planned source-table set. Every planned source table has nonzero 2025 rows.

However, the local Codex attempts were partial failed attempts:

- they started extraction and transformation;
- they attempted to load `play_by_play`;
- they failed at `play_by_play` with a schema mismatch;
- they did not cleanly proceed through the source table list.

That local failure pattern is inconsistent with the current state where all planned raw/source tables have 2025 rows. The current state is consistent with the operator clarification that a browser-admin ingest ran separately.

## Schema Mismatch Details

The local failed pipeline attempts logged this BigQuery error:

```text
Provided Schema does not match Table fantasy-football-498121:fantasy_football_brain.play_by_play. Field lateral_sack_player_id has changed type from STRING to INTEGER
```

Interpretation:

- the existing BigQuery table expects `lateral_sack_player_id` as `STRING`;
- pandas or BigQuery autodetect inferred the current dataframe column as `INTEGER`;
- the append job failed during local pipeline execution.

This should be addressed before rerunning local ingest with `WRITE_APPEND`, especially because the target 2025 rows already exist.

## Phase 20.5 Recommendation

Phase 20.5 can safely be planned again against current source coverage.

Conditions:

- Do not rerun source ingest first.
- Do not run another `WRITE_APPEND` restore without a duplicate-control and schema-coercion plan.
- Treat the successful source-row origin as partner browser-admin ingest, not the failed local Codex attempts.
- Use bounded season `2025` materialization.
- Keep downstream outputs clearly marked as 2025 source-backed only after marts are rebuilt from these rows.

## Cleanup Recommendation

No cleanup is indicated for `play_by_play` or `weekly_metrics` based on the duplicate checks above.

Follow-up hardening needed:

- make the append path schema-aware for existing tables;
- coerce string-like player ID columns to string before BigQuery load;
- add a pre-load schema compatibility check for append mode;
- avoid rerunning source ingest until those safeguards exist or a staging table plus merge strategy is implemented.

## Safety Check

`scripts/check_deployment_safety.py` passed during the investigation.

Safety status:

| Rule | Status |
| --- | --- |
| No ingestion during Phase 20.4A | pass |
| No materialization | pass |
| No deploy | pass |
| No Cloud Run Job trigger | pass |
| No Scheduler job | pass |
| No LLM call | pass |
| No scraping | pass |
| No Firebase artifacts | pass |
| No BigQuery data mutation during investigation | pass |

## Final Decision

`UNEXPECTED INGEST CONFIRMED, SAFE TO PLAN 20.5`

The 2025 source rows are present and duplicate checks for the required source tables passed. The successful origin is now explained by the operator-confirmed browser-admin ingest by the partner. BigQuery job-history identity could not be independently verified because the current credential lacks access to INFORMATION_SCHEMA job views.
