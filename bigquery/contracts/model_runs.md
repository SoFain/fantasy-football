# model_runs Contract

Base SQL: [bigquery/migrations/0002__create_model_runs.sql](../migrations/0002__create_model_runs.sql)

Additive foundation SQL: [bigquery/migrations/0003__model_run_config_foundation.sql](../migrations/0003__model_run_config_foundation.sql)

## Purpose

Metadata table for every generated projection, ranking, content packet, trade evaluation, and backtest output.

Existing `ranking_version` remains a display and backward-compatibility label until the UI migration is complete.

## Required Grain

One row per model or rules-based generation run.

## Required Fields

- `model_run_id`
- `run_type`
- `model_name`
- `model_version`
- `prompt_version`
- `code_version`
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `feature_config_version_id`
- `source_freshness_snapshot_id`
- `status`
- `created_by`
- `created_at`
- `completed_at`
- `error_message`
- `notes`

Legacy fields from the base migration may remain during transition:

- `source_freshness_json`
- `feature_config_version`
- `scoring_profile`
- `league_type`
- `roster_format`

## Source Rules

Every future generated output must store `model_run_id`. The run row must be created before output rows are published.

Pigskin ranking generation uses `run_type = 'pigskin_rankings'` and stores the generated `ranking_version` in the run notes for compatibility lookup.

`mark_model_run_complete()` must set `status` and `completed_at`.

`mark_model_run_failed()` must set `status`, `completed_at`, and preserve `error_message`.

## Compatibility Rules

Keep `ranking_version` on current ranking outputs until Player Profiles and Pigskin chat are migrated to `model_run_id`.

During migration:

- `ranking_version` remains the display and backward-compatibility label.
- `model_run_id` becomes the authoritative lineage key for new generated rankings, projections, backtests, and evidence packets.
- Pigskin should defend rankings from rows tied to a `model_run_id` once ranking writes are patched.
- Existing pre-migration ranking rows may have `NULL` `model_run_id`.
