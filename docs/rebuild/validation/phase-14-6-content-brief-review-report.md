# Phase 14.6 Content Brief Review Report

Date: 2026-06-16

## Purpose

Exercise the deterministic content brief pipeline and the default-off Content Brief Review UI without LLM calls, publishing, scraping, Firebase artifacts, or invented evidence.

## Source Row Counts

Live BigQuery project and dataset:

- Project: `fantasy-football-498121`
- Dataset: `fantasy_football_brain`

Initial source/output state:

- `fraud_watch_packets`: 0 rows
- `sleeper_breakout_packets`: 0 rows
- `trade_review_packets`: 0 rows
- `meatbag_receipt_packets`: missing
- `claim_grades`: 0 rows
- `projection_rankings_current`: 50 rows
- `content_brief_runs`: 0 rows before this phase
- `content_briefs`: 0 rows before this phase
- `content_brief_items`: 0 rows before this phase

The packet tables were empty, so no Fraud Watch or Sleeper Breakout brief was generated. A deterministic `weekly_streamers_show` brief was generated from existing `projection_rankings_current` rows for:

- `season=2025`
- `week=1`
- `scoring_profile_id=ppr`
- `league_type_id=redraft`
- `roster_format_id=one_qb`
- `projection_horizon=weekly`

## Dry Run

Command run:

```powershell
.\venv\Scripts\python.exe -m src.content_briefs --brief-type weekly_streamers_show --season 2025 --week 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
```

The CLI dry-run is write-safe but currently does not instantiate a BigQuery client, so it validates output shape without reading source data.

A no-write builder dry run was also executed with a BigQuery client:

```powershell
.\venv\Scripts\python.exe - <<'PY'
from src.content_briefs import build_weekly_streamers_brief, save_content_brief, get_bigquery_client
client = get_bigquery_client()
brief = build_weekly_streamers_brief(
    season=2025,
    week=1,
    scoring_profile_id="ppr",
    league_type_id="redraft",
    roster_format_id="one_qb",
    client=client,
)
print(save_content_brief(brief, client=client, dry_run=True))
PY
```

Result:

- 8 deterministic brief items previewed.
- Missing flags: `[]`
- Source rows came from `projection_rankings_current`.
- No LLM calls.
- No Firebase artifacts.

## Materialization

Command run:

```powershell
.\venv\Scripts\python.exe -m src.content_briefs --brief-type weekly_streamers_show --season 2025 --week 1 --scoring-profile ppr --league-type redraft --roster-format one_qb
```

Generated reviewable brief:

- `content_brief_id`: `brief-weekly_streamers_show-2025-w1-20260616T131307Z-e7fd38e1`
- `content_brief_run_id`: `weekly_streamers_show-2025-w1-20260616T131307Z-4b436599`
- `brief_type`: `weekly_streamers_show`
- `review_status`: `draft`
- `item_count`: 8
- `token_estimate`: 753
- `missing_data_flags`: `[]`

Final live counts after this phase:

- `content_brief_runs`: 2 rows
- `content_briefs`: 2 rows
- `content_brief_items`: 16 rows

One earlier row was written before the writer fix and exposed a streaming-buffer limitation. The later row above was written through a BigQuery load job and is the row used for review-status QA.

## Fixes Made

Two content brief issues were found during QA:

1. `projection_rankings_current` contained duplicate rows per player for the available weekly projection run. The content brief ranking loader now dedupes ranking rows by `player_id_internal`, falling back to display name, position, and team.
2. `save_content_brief()` used streaming inserts, which made immediate review-status updates fail with BigQuery streaming-buffer errors. The writer now uses `load_table_from_json()` when available and falls back to streaming inserts only for simple test doubles.

## UI QA

Local Streamlit was started with only:

```powershell
$env:USE_CONTENT_BRIEF_REVIEW_UI="true"
.\venv\Scripts\python.exe -m streamlit run app.py --server.port 8502 --server.headless true
```

Observed UI status:

- Content Briefs tab rendered behind the default-off feature flag.
- Brief Runs section rendered.
- Brief List section rendered.
- Brief Detail section rendered.
- Brief Items section rendered.
- Review Actions section rendered.
- Generation Preview section rendered.
- Seeded `Weekly Streamers Show Brief` was selectable.
- Seeded brief displayed player content, including Austin Ekeler.
- Review action buttons were visible: `Mark draft`, `Mark reviewed`, `Mark approved`, `Mark archived`.
- `Export Markdown` button was visible and clickable from the active tab.

Helper QA:

- `list_content_brief_runs()` returned the generated run.
- `list_content_briefs()` returned the generated brief.
- `get_content_brief_detail()` returned 8 items.
- `export_content_brief_markdown()` returned Markdown with brief items and show-writer payload.
- `update_content_brief_review_status()` successfully changed the load-job row to `reviewed`.
- Status was restored to `draft` after the reversible QA check.

Reviewer notes are still not persisted because the current schema does not support a reviewer notes column.

## Validation

Command run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
```

Result:

- 11 passed
- 0 failed

Passing checks included:

- content brief run grain
- content brief grain
- content brief item grain
- required JSON keys
- size bounds
- source freshness
- missing flags
- review status values
- item joins
- no raw source dependency

## Tests Planned In This Phase

Focused unit coverage added or confirmed:

- Deterministic brief builder behavior.
- Ranking loader dedupe guard.
- Load-job writer path for immediately reviewable rows.
- Review status update validation.
- Markdown export.
- Feature flag default false.
- No LLM calls in review helper.

## Remaining Limitations

- Fraud Watch, Sleeper Breakout, Trade Review, and Meatbag Accountability briefs are still empty until their packet or claim-grading inputs are populated.
- The CLI `--dry-run` validates write shape but does not currently read BigQuery source rows. The no-write builder dry run with an explicit client was used to validate real input data.
- Reviewer notes are accepted in the UI but ignored until a schema migration adds storage.
- One earlier streaming-inserted sample row remains in the tables and will become updateable only after BigQuery clears the streaming buffer. It is draft-only and deterministic.

## Decision

GO WITH WARNINGS

The content brief review workflow is now exerciseable with deterministic, non-LLM data. The remaining warnings are source-packet empty states and reviewer-note persistence.
