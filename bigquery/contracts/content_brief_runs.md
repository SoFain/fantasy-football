# content_brief_runs Contract

Migration: [bigquery/migrations/0024__create_content_briefs.sql](../migrations/0024__create_content_briefs.sql)

Helper: [src/content_briefs.py](../../src/content_briefs.py)

## Purpose

Run ledger for deterministic show content brief generation.

## Grain

One row per `content_brief_run_id`.

## Required Fields

- `content_brief_run_id`
- `brief_type`
- `season`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `status`
- `created_at`

## Rules

- Runs are created for content-brief orchestration only.
- The helper does not call LLMs.
- The helper reads only curated packets, projection outputs, grading outputs, and config tables.
- Brief rows and item rows must reference a run.

## Status Values

- `created`
- `completed`
- `failed`