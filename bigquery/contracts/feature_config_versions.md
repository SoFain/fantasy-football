# feature_config_versions Contract

Migration SQL: [bigquery/migrations/0003__model_run_config_foundation.sql](../migrations/0003__model_run_config_foundation.sql)

## Purpose

Stores versioned feature and weighting configuration used by model runs.

## Required Grain

One row per feature configuration version.

## Required Fields

- `feature_config_version_id`
- `config_name`
- `model_name`
- `projection_horizon`
- `config_json`
- `created_by`
- `created_at`
- `published_at`
- `archived_at`
- `active`
- `notes`

## Compatibility Rules

Generated rankings and projections should reference `feature_config_version_id` through `model_runs` before the UI depends on those configs directly.
