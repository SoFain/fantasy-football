# claim_grades Contract

Migration: [bigquery/migrations/0023__create_claim_grading.sql](../migrations/0023__create_claim_grading.sql)

Helper: [src/claim_grading.py](../../src/claim_grading.py)

## Purpose

One deterministic grade per claim per grading run. Grades compare the manual claim to actual outcomes, Pigskin projection context, and market context where available.

## Grain

One row per `claim_grading_run_id` and `claim_id`.

## Verdicts

- `good_take`: claim direction clearly matches the outcome.
- `wrong`: claim direction clearly misses the outcome.
- `lucky`: result was right but confidence is weak.
- `fraud`: take was strongly wrong and contradicted available Pigskin or market evidence.
- `galaxy_brain`: take was strongly right against available Pigskin or market evidence.
- `inconclusive`: insufficient data or incomplete evaluation window.

## Inputs

Allowed curated inputs:

- `fantasy_claims`
- `fantasy_claim_players`
- `claim_evaluation_windows`
- `analytics_player_fantasy_points_by_profile`
- `projection_rankings_current`
- `market_consensus_baseline_current`

Raw source tables are not allowed in the grading helper.

## Missing Data

Missing actuals, missing player identity, missing Pigskin snapshots, missing market snapshots, and insufficient dynasty windows are represented in `missing_data_flags`.

Missing data should produce `inconclusive` where the claim cannot be honestly graded.
