# league_types Contract

Migration SQL: [bigquery/migrations/0003__model_run_config_foundation.sql](../migrations/0003__model_run_config_foundation.sql)

## Purpose

Defines league context for projection and ranking model runs.

## Required Grain

One row per league type ID.

## Required Fields

- `league_type_id`
- `display_name`
- `description`
- `created_at`
- `updated_at`
- `active`

## Seed Rows

- `redraft`
- `keeper`
- `dynasty`
- `best_ball`
