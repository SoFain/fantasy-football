# Content Brief Review UI

Phase 13.5 adds a default-off Streamlit review surface for deterministic content briefs.

## Feature Flag

`USE_CONTENT_BRIEF_REVIEW_UI=false`

When the flag is false, the dashboard behavior is unchanged and no Content Briefs tab is shown.

When the flag is true, Streamlit shows a Content Briefs tab that reads only:

- `content_brief_runs`
- `content_briefs`
- `content_brief_items`

The helper module is [src/content_brief_review.py](../../src/content_brief_review.py).

## Purpose

The UI lets admins inspect deterministic show-prep briefs before any show-writing AI is used.

Supported workflows:

- Review content brief generation runs.
- Show brief and item row counts per run.
- Filter content briefs by type, status, season, week, model run, and run id.
- Inspect `brief_text`, `brief_json`, source freshness, and missing-data flags.
- Inspect linked brief items, claims, evidence summaries, counterarguments, snark hooks, and confidence.
- Explicitly mark a brief as `draft`, `reviewed`, `approved`, or `archived`.
- Export a Markdown version of a brief.
- Copy the deterministic show-writer payload if it is present in `brief_json`.
- Preview a local dry-run generation command.

## Safety Rules

- No LLM calls are made by default.
- No content is published automatically.
- No raw/source tables are queried.
- Streamlit does not run long content generation work in the request path.
- Review status changes require an explicit button click.
- Reviewer notes are displayed in the UI but are not persisted until the warehouse schema supports them.

## Helper API

[src/content_brief_review.py](../../src/content_brief_review.py) provides:

- `list_content_brief_runs()`
- `list_content_briefs()`
- `get_content_brief_detail()`
- `list_content_brief_items()`
- `update_content_brief_review_status()`
- `export_content_brief_markdown()`
- `build_content_brief_generation_preview_command()`

Queries use BigQuery parameters and table identifiers come from the trusted project and dataset configuration.

## Manual QA

Use the repo venv:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_content_brief_review
.\venv\Scripts\python.exe -m py_compile app.py
```

Dashboard checks:

1. Start with `USE_CONTENT_BRIEF_REVIEW_UI` unset and confirm the Content Briefs tab is absent.
2. Set `USE_CONTENT_BRIEF_REVIEW_UI=true` and restart Streamlit.
3. Confirm the tab shows a clean empty state if no briefs exist.
4. Confirm Brief Runs and Brief List filters do not trigger raw/source queries.
5. Select a brief and verify detail, items, freshness, missing flags, and Markdown export.
6. Mark a brief `reviewed`, then `approved`, and confirm the status changes only after button clicks.
7. Confirm generation preview displays a dry-run command and does not execute generation.

## Phase 14.6 QA Result

On 2026-06-16, the Content Brief Review UI was exercised with:

```powershell
$env:USE_CONTENT_BRIEF_REVIEW_UI="true"
.\venv\Scripts\python.exe -m streamlit run app.py --server.port 8502 --server.headless true
```

The seeded deterministic brief was:

- `content_brief_id`: `brief-weekly_streamers_show-2025-w1-20260616T131307Z-e7fd38e1`
- `brief_type`: `weekly_streamers_show`
- `season`: `2025`
- `week`: `1`
- `review_status`: `draft`
- `item_count`: 8

UI checks passed:

- Content Briefs tab rendered only when `USE_CONTENT_BRIEF_REVIEW_UI=true`.
- Brief Runs, Brief List, Brief Detail, Brief Items, Review Actions, and Generation Preview rendered.
- Seeded `Weekly Streamers Show Brief` was selectable.
- Player item content rendered.
- Review buttons were visible.
- Markdown export rendered from the active tab.
- Helper-level review status update succeeded and was restored to `draft`.

No LLM calls were made and no content was published.

Known notes:

- Reviewer notes are not persisted yet.
- Source freshness and missing flags are available through helper output and stored columns. Depending on Streamlit expansion state, they may not be visible in the first viewport.
- Freshly written briefs should use the load-job writer path so review status updates are not blocked by BigQuery streaming buffers.

See [phase-14-6-content-brief-review-report.md](validation/phase-14-6-content-brief-review-report.md).

## Rollback

Set `USE_CONTENT_BRIEF_REVIEW_UI=false` or remove the environment variable, then restart or redeploy the Cloud Run service. No migration rollback is required.
