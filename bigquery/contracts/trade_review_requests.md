# trade_review_requests Contract

Migration: [bigquery/migrations/0016__create_trade_review_packets.sql](../migrations/0016__create_trade_review_packets.sql)

Helper: [src/trade_review_packets.py](../../src/trade_review_packets.py)

## Purpose

Request ledger for deterministic trade review packets.

This table records the requested trade sides, scoring context, optional league or roster context, status, and any error message. It does not store raw analytical rows.

## Grain

One row per `trade_review_id`.

## Required Fields

- `trade_review_id`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `side_a_json`
- `side_b_json`
- `created_at`
- `status`

## Source Rules

Rows are written by [src/trade_review_packets.py](../../src/trade_review_packets.py). Future UI or Pigskin code should create requests through that helper or a backend API wrapper.

## Missing Data Behavior

Unknown assets should fail cleanly before packet rows are written. Failed requests may be stored with `status = 'failed'` and an `error_message`.

## Runtime Status

No Streamlit runtime behavior is wired to this table yet.
