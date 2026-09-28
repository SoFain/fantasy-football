# Phase 20.4B Admin Ingest Audit Report

## Purpose

Phase 20.4B audited the partner-run browser admin ingest before rerunning Phase 20.5 current-season mart planning.

This audit was read-only for warehouse state. No ingestion, `WRITE_APPEND`, `WRITE_TRUNCATE`, materialization, deployment, Cloud Run Job trigger, Scheduler job, LLM call, scraping, Firebase artifact creation, or BigQuery data mutation was run.

## Ingest Origin

The operator confirmed that a partner ran the 2025 ingest through the browser admin path.

BigQuery table metadata supports that explanation:

| Table | Last modified UTC | 2025 rows |
| --- | --- | ---: |
| `play_by_play` | 2026-06-17 02:40:02.719 | 48,771 |
| `weekly_metrics` | 2026-06-17 02:40:07.396 | 19,421 |
| `team_descriptions` | 2026-06-17 02:40:09.581 | 36 |
| `draft_picks` | 2026-06-17 02:40:11.873 | 257 |
| `player_rosters` | 2026-06-17 02:40:15.299 | 25,040 |
| `player_contracts` | 2026-06-17 02:40:21.995 | 51,629 |
| `ngs_passing` | 2026-06-17 02:40:25.148 | 605 |
| `ngs_rushing` | 2026-06-17 02:40:27.780 | 648 |
| `ngs_receiving` | 2026-06-17 02:40:31.764 | 1,402 |
| `ftn_charting` | 2026-06-17 02:40:36.507 | 47,316 |
| `weekly_snap_counts` | 2026-06-17 02:40:39.898 | 26,612 |
| `injury_reports` | 2026-06-17 02:40:43.491 | 6,068 |
| `depth_charts` | 2026-06-17 02:40:47.283 | 554,215 |

The local Codex pipeline attempt reached the local BigQuery load step after the successful admin-run source rows were already visible in table metadata. The local attempt then failed on a schema mismatch. It should not be treated as the successful origin of the source rows.

## BigQuery Job History

Read-only INFORMATION_SCHEMA job-history queries were attempted.

| View | Result |
| --- | --- |
| `fantasy-football-498121.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT` | 403 access denied |
| `fantasy-football-498121.region-us.INFORMATION_SCHEMA.JOBS_BY_USER` | 403 access denied |

Because the current credential cannot query those views, this audit could not independently record:

- job IDs for the admin-run ingest;
- `user_email` for the successful browser-admin load jobs;
- load job status from BigQuery job metadata;
- error details from the successful admin-run path.

The successful origin is documented from operator confirmation plus table metadata timestamps. The precise BigQuery `user_email` remains unavailable until the credential has job-history access.

## Current 2025 Source Coverage

Schema-aware read-only counts were run for all planned source tables.

| Table | Grain checked | 2025 rows | Week coverage |
| --- | --- | ---: | --- |
| `play_by_play` | season/week | 48,771 | weeks 1 through 22 |
| `weekly_metrics` | season/week | 19,421 | weeks 1 through 22 |
| `team_descriptions` | season total | 36 | not week-grained |
| `draft_picks` | season total | 257 | not week-grained |
| `player_rosters` | season total | 25,040 | not week-grained |
| `player_contracts` | season total | 51,629 | not week-grained |
| `ngs_passing` | season/week | 605 | weeks 0 through 23 |
| `ngs_rushing` | season/week | 648 | weeks 0 through 23 |
| `ngs_receiving` | season/week | 1,402 | weeks 0 through 23 |
| `ftn_charting` | season/week | 47,316 | weeks 1 through 22 |
| `weekly_snap_counts` | season/week | 26,612 | weeks 1 through 22 |
| `injury_reports` | season/week | 6,068 | weeks 1 through 22 |
| `depth_charts` | season total | 554,215 | not week-grained |

Coverage is sufficient to rerun Phase 20.5 planning for 2025 source-backed marts. The NGS tables include week `0` and week `23`; that is a source-shape warning to account for in downstream logic, not a blocker for `play_by_play` and `weekly_metrics` driven mart planning.

## Duplicate-Risk Checks

Duplicate checks were run on the best available keys after inspecting schema.

| Table | Key | Duplicate groups | Excess rows | Result |
| --- | --- | ---: | ---: | --- |
| `play_by_play` | `season`, `week`, `game_id`, `play_id` | 0 | 0 | pass |
| `weekly_metrics` | `season`, `week`, `player_id` | 0 | 0 | pass |
| `weekly_metrics` | `season`, `week`, `team`, `player_id` | 0 | 0 | pass |

No dedupe or cleanup is required before Phase 20.5 based on these checks.

## Partial-Load Assessment

The planned source-table set is populated for 2025. There are no missing required source tables from the planned ingest list.

No obvious append duplication was detected in the required source tables:

- `play_by_play` has 22 weeks, with regular-season row counts around expected game-play volume and lower postseason week counts.
- `weekly_metrics` has 22 weeks, with regular-season row counts around expected player-week volume and lower postseason week counts.
- `ftn_charting`, `weekly_snap_counts`, and `injury_reports` have week 1 through 22 coverage.
- season-grain tables have nonzero 2025 totals.

Warnings:

- NGS tables include week `0` and week `23`.
- BigQuery job metadata could not be queried, so actor and load-job sequence are not independently confirmed from INFORMATION_SCHEMA.
- The local pipeline append path still fails on schema autodetect and should not be reused without hardening.

## Schema Mismatch Assessment

Current BigQuery schema for the mismatch field:

| Table | Field | BigQuery type |
| --- | --- | --- |
| `play_by_play` | `lateral_sack_player_id` | `STRING` |

Related lateral player ID fields in BigQuery are also strings, including:

- `lateral_receiver_player_id`
- `lateral_rusher_player_id`
- `lateral_sack_player_id`
- `lateral_interception_player_id`
- `lateral_punt_returner_player_id`
- `lateral_kickoff_returner_player_id`

Current pipeline behavior:

- `src.transform.transform_pbp_data` coerces `season` only.
- `src.load.load_df_to_partitioned_table` pins only `season` in the load schema.
- all other fields rely on BigQuery autodetect.

The local failed append logged:

```text
Field lateral_sack_player_id has changed type from STRING to INTEGER
```

That means the current source dataframe or BigQuery load autodetect inferred `lateral_sack_player_id` as integer for this 2025 load attempt, while the existing table expects string.

Recommendation before any future source ingest:

- add schema-aware append hardening;
- coerce player ID and player name ID-like columns to string before load;
- compare dataframe dtypes to existing BigQuery schema before append;
- consider staging-table plus merge instead of direct append for source restores.

Do not rerun local `WRITE_APPEND` ingest until this is fixed or explicitly bypassed with a duplicate-control plan.

## Safety Check

`scripts/check_deployment_safety.py` passed.

| Safety rule | Status |
| --- | --- |
| No ingestion during Phase 20.4B | pass |
| No `WRITE_APPEND` | pass |
| No `WRITE_TRUNCATE` | pass |
| No materialization | pass |
| No deployment | pass |
| No Cloud Run Job trigger | pass |
| No Scheduler job | pass |
| No LLM call | pass |
| No scraping | pass |
| No Firebase artifacts | pass |
| No BigQuery data mutation | pass |

## Phase 20.5 Readiness

Phase 20.5 can be rerun as a planning/materialization phase against the now-present 2025 source rows.

Guardrails for the next step:

- do not rerun source ingest first;
- use bounded `season=2025`;
- dry-run or inspect materializer commands first if supported;
- keep current outputs labeled as 2025 source-backed only after marts are rebuilt;
- separately schedule append-path hardening for `src.load` and `src.transform`.

## Final Decision

`ADMIN INGEST AUDIT PASS WITH WARNINGS, SAFE TO PLAN 20.5`

Warnings are limited to job-history IAM visibility, NGS week-shape differences, and the local append schema mismatch. No source-table dedupe or cleanup is required before Phase 20.5 based on the checks performed.
