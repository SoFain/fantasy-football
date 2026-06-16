# fantasy_claims Contract

Migration: [bigquery/migrations/0022__create_meatbag_claim_ledger.sql](../migrations/0022__create_meatbag_claim_ledger.sql)

Helper: [src/claim_ledger.py](../../src/claim_ledger.py)

## Purpose

Manual ledger of fantasy-football claims made by outside analysts, show hosts, or internal references. This is the source table for future grading, receipts, show segments, and Pigskin versus Meatbag comparisons.

## Grain

One row per `claim_id`.

## Required Review Context

Draft claims can be incomplete beyond the minimum entry fields. Claims marked `reviewed`, `ready_to_grade`, or `graded` must include:

- `source_id`
- `source_name`
- `claim_text`
- `claim_type`
- `claim_direction`
- `time_horizon`
- `season`
- at least one player or team reference

## Lineage Fields

- `model_run_id_at_claim` records Pigskin model context at the moment of entry when available.
- `pigskin_rank_at_claim` stores the Pigskin snapshot rank when available.
- `market_rank_at_claim` stores the market or consensus snapshot rank when available.
- `context_json` stores small manual context only. Large artifacts belong in Cloud Storage or curated BigQuery tables.

Rank snapshots may come only from curated outputs such as `projection_rankings_current` and `market_consensus_baseline_current`. They should not query raw source tables.

## Status Rules

- `draft`: editable manual entry.
- `reviewed`: checked for required metadata.
- `ready_to_grade`: evaluation window is ready.
- `graded`: immutable unless explicitly moved to `correction`.
- `correction`: controlled exception path for audited fixes.
- `archived`: hidden from active workflows.

## UI and LLM Safety

This table is not a Pigskin context tool by itself. Future Pigskin access should use curated evidence packets that include only needed claim rows.
