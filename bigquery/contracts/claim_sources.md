# claim_sources Contract

Migration: [bigquery/migrations/0022__create_meatbag_claim_ledger.sql](../migrations/0022__create_meatbag_claim_ledger.sql)

Helper: [src/claim_ledger.py](../../src/claim_ledger.py)

## Purpose

Registry of manual claim sources for analysts, shows, channels, articles, internal Pigskin references, and other future claim inputs.

## Grain

One row per `source_id`.

## Source Types

- `youtube`
- `tv`
- `podcast`
- `article`
- `internal_pigskin`
- `manual`

## Rules

- This table does not authorize scraping.
- Source rows are created or updated manually through `src.claim_ledger`.
- `source_id` is normalized to a safe lowercase identifier.
- Inactive sources stay available for historical joins.

## UI and LLM Safety

Safe for backend admin use. It is metadata only and should not be exposed to Pigskin as an arbitrary query surface.
