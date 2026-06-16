# roster_formats Contract

Migration SQL: [bigquery/migrations/0003__model_run_config_foundation.sql](../migrations/0003__model_run_config_foundation.sql)

## Purpose

Defines roster structure for projection and ranking model runs.

## Required Grain

One row per roster format ID.

## Required Fields

- `roster_format_id`
- `display_name`
- `description`
- `roster_rules_json`
- `created_at`
- `updated_at`
- `active`

## Seed Rows

- `one_qb`
- `superflex`
- `two_qb`
- `best_ball`
