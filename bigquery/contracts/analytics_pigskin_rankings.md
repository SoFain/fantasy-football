# analytics_pigskin_rankings Contract

Migration SQL: [bigquery/migrations/0004__add_model_run_id_to_pigskin_rankings.sql](../migrations/0004__add_model_run_id_to_pigskin_rankings.sql)

## Purpose

Stores current and historical Pigskin-authored rankings generated from curated ranking candidate evidence.

## Tables

- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_history`

## Compatibility Rules

- `ranking_version` remains the UI and display compatibility label.
- `model_run_id` is the reproducibility and governance key for new generated ranking rows.
- Existing pre-migration rows may have `NULL` `model_run_id`.
- New generated rows from `src/generate_pigskin_rankings.py` must include `model_run_id` and context IDs.

## Required Lineage Fields For New Rows

- `model_run_id`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `feature_config_version_id`
- `source_freshness_snapshot_id`

## Source Rules

Ranking rows should be written only after a `model_runs` row is created with `run_type = 'pigskin_rankings'`.

Successful writes to both current and history tables should mark the model run complete.

Failures after model-run creation should mark the model run failed while preserving the original exception.
