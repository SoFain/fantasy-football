# claim_grading_runs Contract

Migration: [bigquery/migrations/0023__create_claim_grading.sql](../migrations/0023__create_claim_grading.sql)

Helper: [src/claim_grading.py](../../src/claim_grading.py)

## Purpose

Run ledger for deterministic Meatbag Claim Ledger grading.

## Grain

One row per `claim_grading_run_id`.

## Required Fields

- `claim_grading_run_id`
- `grading_version`
- `status`
- `created_at`

## Rules

- Every grade and scorecard must reference a grading run.
- Runs are created before grades are written.
- Dry-run mode returns the run row without writing to BigQuery.
- This table does not store raw content, media transcripts, or LLM output.

## Status Values

- `created`
- `running`
- `completed`
- `failed`

## UI and LLM Safety

Safe as operational metadata. Pigskin should consume future curated grading packets, not arbitrary table access.
