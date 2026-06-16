# content_brief_items Contract

Migration: [bigquery/migrations/0024__create_content_briefs.sql](../migrations/0024__create_content_briefs.sql)

Helper: [src/content_briefs.py](../../src/content_briefs.py)

## Purpose

Ordered item rows that make each content brief scannable and easy to hand to a future writing agent.

## Grain

One row per `content_brief_id` and `item_id`.

## Item Types

- `player`
- `trade`
- `claim`
- `ranking`
- `team`
- `segment`

## Rules

- Items must be ordered with `item_order`.
- Each item should include a claim, evidence summary, counterargument, snark hook, confidence score, source freshness, and missing-data flags where available.
- Items should reference IDs from upstream packets or outputs instead of copying large payloads.
- Items should not expose source tables or unbounded arrays.