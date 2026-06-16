# content_briefs Contract

Migration: [bigquery/migrations/0024__create_content_briefs.sql](../migrations/0024__create_content_briefs.sql)

Helper: [src/content_briefs.py](../../src/content_briefs.py)

## Purpose

Compact show-ready brief rows for recurring AI vs. Meatbags segment types.

## Grain

One row per `content_brief_id`.

## Supported Brief Types

- `fraud_watch_show`
- `sleeper_breakout_show`
- `trade_review_show`
- `rankings_debate_show`
- `meatbag_accountability_show`
- `weekly_streamers_show`
- `dynasty_value_show`
- `full_weekly_show_prep`

## Required JSON Keys

`brief_json` must include:

- `title`
- `brief_type`
- `segment_objective`
- `top_items`
- `items`
- `suggested_segment_order`
- `do_not_overclaim_caveats`
- `source_freshness_json`
- `missing_data_flags`
- `llm_prompt_payload_json`

## Bounds

- `brief_text` should stay at or below 12000 characters.
- `token_estimate` should stay at or below 3500.
- Store packet IDs and summaries, not full nested evidence payloads.

## Review Status

- `draft`
- `reviewed`
- `approved`
- `archived`