# Phase 27.5 Trade Score V1 Materialization Report

## Final Decision

TRADE SCORE V1 MATERIALIZATION BLOCKED

The requested Phase 27.5 materialization did not proceed because the required write authorization gate was not present at phase start.

`ALLOW_TRADE_SCORE_MATERIALIZATION` was unset. Per the phase instructions, this blocks the run before preflight and before any write-capable command.

## Scope

This phase created this blocked report only. No score rows were written. No deployment, production feature flag change, Cloud Run Job trigger, Scheduler job, ingestion, LLM action, Pigskin prompt, scrape, Firebase artifact, draft-pick materialization, or BigQuery write occurred.

## Authorization Gate State

| Moment | `ALLOW_TRADE_SCORE_MATERIALIZATION` |
| --- | --- |
| Before preflight | unset |
| During write | not reached |
| After stop | unset |

The same-session write wrapper was not run because Task 1 required stopping when the authorization gate was not already true.

## Preflight Results

Preflight was not run. The phase stopped at authorization confirmation.

Commands not run:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

## Pre-Existing Table State

Not checked. The phase stopped before read-only BigQuery checks because authorization was missing.

## Final Dry-Run Summary

Not run. The phase stopped before the final v1 dry-run because authorization was missing.

Expected Phase 27.4 dry-run context remains the last known evidence:

| Metric | Expected From Phase 27.4 |
| --- | ---: |
| Source rows | 100 |
| Score rows | 100 |
| Materializable player rows | 77 |
| Excluded rows | 23 |
| Excluded pick rows | 13 |
| Duplicate dry-run grain rows | 0 |
| Written rows | 0 |

## Write Command

Not run.

The requested bounded write command was not executed because `ALLOW_TRADE_SCORE_MATERIALIZATION` was unset at authorization confirmation.

## Rows Written Or Merged

| Metric | Value |
| --- | ---: |
| Rows written | 0 |
| Rows merged | 0 |
| PICK rows written | 0 |

## Post-Write Verification

Not applicable. No write occurred.

The following acceptance criteria remain untested for Phase 27.5 because materialization was blocked:

- v1 target row count
- duplicate grain rows
- missing `model_run_id` rows
- unresolved identity rows
- invalid score rows
- missing confidence rows
- warning row counts
- compatibility view validation after write

## Score Distribution

Not captured. No v1 target rows were materialized in this phase.

## Confidence Distribution

Not captured. No v1 target rows were materialized in this phase.

## Warning Rows

Not rechecked in this blocked phase.

Known warnings from Phase 27.4 remain the current working context:

- `projection_freshness_metadata_missing` should remain visible.
- Five team-context mismatch rows need human review.
- Draft picks remain diagnostic-only and excluded from player materialization.
- Production score flags must remain false.

## Validation Results

Not run because authorization failed before preflight.

## Production Untouched Confirmation

No production command was run in this phase.

Confirmed by action scope:

- no deploy command was run
- no production feature flag command was run
- no Cloud Run Job was triggered
- no Scheduler job was created
- no ingestion was run
- no LLM-backed action was called
- no Pigskin prompt was submitted
- no Firebase artifact was created

Production score flags were not changed by this phase.

## Remaining Warnings

The phase request is internally strict: it requires stopping when `ALLOW_TRADE_SCORE_MATERIALIZATION` is not true, but the supplied same-session authorization wrapper appears later in the requested task sequence. This run honored the earlier stop condition and did not execute the wrapper.

## Recommended Next Phase

Run a new bounded Phase 27.5 retry with explicit authorization already present at the start of the phase, or revise the phase instruction to state that the same-session wrapper is the authorization source of truth.

If retried, keep the same safety boundaries:

- staging-review data only
- no production flag changes
- no deploys
- no Cloud Run Job triggers
- no ingestion
- no LLM actions
- no draft-pick materialization
