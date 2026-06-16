# claim_evaluation_windows Contract

Migration: [bigquery/migrations/0022__create_meatbag_claim_ledger.sql](../migrations/0022__create_meatbag_claim_ledger.sql)

Helper: [src/claim_ledger.py](../../src/claim_ledger.py)

## Purpose

Stores the default window used to decide when a claim is eligible for grading.

## Grain

One row per `claim_id` and `evaluation_window_id`.

## Horizon Defaults

- `weekly`: start and end at the claim week.
- `ros`: start at claim week when supplied and end at Week 18.
- `season`: start at Week 1 unless supplied and end at Week 18.
- `dynasty`: placeholder ending two seasons after the claim season.
- `multi_year`: placeholder ending one season after the claim season.

## Status Values

- `pending`
- `ready_to_grade`
- `graded`
- `deferred`
- `correction`

## UI and LLM Safety

This table is operational metadata for grading jobs. Future UI should consume summary views or claim packets rather than raw windows.
