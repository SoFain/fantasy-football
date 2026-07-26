-- Phase 33.15: Add missing goal_line_carries column to weekly advanced metrics.
-- Additive schema-only migration. No destructive DDL.

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_advanced_metrics`
ADD COLUMN IF NOT EXISTS goal_line_carries FLOAT64;
