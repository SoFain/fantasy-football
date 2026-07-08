# Phase Report — Phase 33.17 BQML v2 Advanced Feature Contract

## 1. Executive Summary

This report documents the rebuild of the BQML v2 feature contract to integrate the audited `advanced_player_metrics_v1` warehouse, replacing scattered feature-mart fields. All unit tests have been successfully updated and passed, and dry-run query coverage validations have been run against BigQuery.

* **Final Decision**: **BQML V2 ADVANCED FEATURE CONTRACT READY**
* **Recommended Next Phase**: **Phase 33.18 — Profile-specific advanced-metrics BQML v2 training**

---

## 2. Phase 33.16 Preservation (Part 0)

The working directory was inspected, and the 6 files belonging to Phase 33.16 were staged and committed:
* **Commit Hash**: `8852bbd`
* **Commit Message**: `phase 33.16 audit advanced metrics formulas`
* **Files Committed**:
  1. `src/nflverse_advanced_metrics_warehouse.py`
  2. `docs/rebuild/pigskin-advanced-metrics-warehouse.md`
  3. `docs/rebuild/player-advanced-metrics-catalog.md`
  4. `bigquery/validations/193a_advanced_metrics_formula_sanity.sql`
  5. `bigquery/validations/194a_injury_availability_games_sanity.sql`
  6. `docs/rebuild/validation/phase-33-16-advanced-metrics-formula-audit-report.md`

---

## 3. Feature Mapping (Part A)

For each current BQML v2 predictor, the following decisions were made and mapped to the new `advanced_player_metrics_v1` warehouse columns:

| Position | Current Feature | New Advanced Metric | Action | Reason | Source Status | Coverage Status | Model Family Use |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **All** | `profile_points_score` | `profile_points_score_3yr` | **Keep** | Retained as baseline baseline context | `AVAILABLE` | 100% | Predictor |
| **All** | `recent_points_avg` | `recent_points_avg_3yr` | **Keep** | Retained as recent fantasy performance form | `AVAILABLE` | 100% | Predictor |
| **All** | `team_environment_score` | `team_environment_score_3yr` | **Keep** | Sourced outside advanced metrics | `AVAILABLE` | 100% | Predictor |
| **QB** | `passing_epa_per_play` | `adv_passing_epa_3yr` | **Replace** | Replaced with warehouse 3-year aggregated EPA | `AVAILABLE` | 100% | Predictor |
| **QB** | `cpoe` | `adv_passing_cpoe_3yr` | **Replace** | Replaced with warehouse 3-year completion over expected | `AVAILABLE` | 100% | Predictor |
| **QB** | `ngs_qb_passing_efficiency_score_3yr` | `adv_ngs_qb_cpoe_3yr` | **Replace** | Sourced from corrected NGS QB metrics | `AVAILABLE` | 2016+ | Predictor |
| **QB** | `rushing_attempts` | `adv_carries_3yr` | **Replace** | Sourced from warehouse carries | `AVAILABLE` | 100% | Predictor |
| **QB** | `qb_rushing_leverage_index` | `adv_qb_rushing_baseline_3yr` | **Replace** | Sourced from warehouse rushing baseline | `AVAILABLE` | 100% | Predictor |
| **RB** | `carries` | `adv_carries_3yr` | **Replace** | Sourced from warehouse carries | `AVAILABLE` | 100% | Predictor |
| **RB** | `targets` | `adv_targets_3yr` | **Replace** | Sourced from warehouse targets | `AVAILABLE` | 100% | Predictor |
| **RB** | `rb_high_value_opportunity_score` | `adv_weighted_opportunity_profile_3yr` | **Replace** | Replaced with profile-specific weighted opportunity | `AVAILABLE` | 100% | Predictor |
| **RB** | `red_zone_opportunities` | `adv_red_zone_opportunities_3yr` | **Replace** | Replaced with warehouse opportunities | `AVAILABLE` | 100% | Predictor |
| **RB** | `goal_line_opportunities` | `adv_goal_line_opportunities_3yr` | **Replace** | Replaced with warehouse opportunities | `AVAILABLE` | 100% | Predictor |
| **RB** | `ngs_rushing_efficiency_score_3yr` | `adv_ngs_rushing_efficiency_3yr` | **Replace** | Sourced from warehouse NGS efficiency | `AVAILABLE` | 2016+ | Predictor |
| **RB** | `ngs_rush_yards_over_expected_score_3yr` | `adv_ngs_rush_yards_over_expected_3yr` | **Replace** | Sourced from warehouse NGS RYOE | `AVAILABLE` | 2016+ | Predictor |
| **RB** | `ngs_box_resilience_score_3yr` | `adv_ngs_box_count_rate_3yr` | **Replace** | Sourced from warehouse box defenders count rate | `AVAILABLE` | 2016+ | Predictor |
| **WR/TE** | `receiving_yards` | `adv_receiving_yards_3yr` | **Replace** | Sourced from warehouse receiving yards | `AVAILABLE` | 100% | Predictor |
| **WR/TE** | `receiving_epa` | `adv_receiving_epa_3yr` | **Replace** | Sourced from warehouse receiving EPA | `AVAILABLE` | 100% | Predictor |
| **WR/TE** | `red_zone_targets` | `adv_red_zone_targets_3yr` | **Replace** | Sourced from warehouse red zone targets | `AVAILABLE` | 100% | Predictor |
| **WR/TE** | `air_yards` | `adv_receiving_air_yards_3yr` | **Replace** | Sourced from corrected air yards | `AVAILABLE` | 100% | Predictor |
| **WR/TE** | `receiving_usage` | `adv_wopr_3yr` | **Replace** | Replaced with corrected WOPR | `AVAILABLE` | 100% | Predictor |
| **WR/TE** | `receiving_role_dominance_score` | `adv_target_share_3yr` / `adv_air_yards_share_3yr` | **Replace** | Expanded to separate shares | `AVAILABLE` | 100% | Predictor |
| **WR/TE** | `receiving_first_down_exp_pbp_3yr` | `adv_receiving_first_down_rate_3yr` | **Replace** | Replaced with warehouse first down rate | `AVAILABLE` | 100% | Predictor |
| **WR/TE** | `ngs_receiving_efficiency_score_3yr` | `adv_ngs_avg_separation_3yr` | **Replace** | Sourced from warehouse NGS average separation | `AVAILABLE` | 2016+ | Predictor |
| **WR/TE** | `ngs_yac_over_expected_score_3yr` | `adv_ngs_yac_above_expectation_3yr` | **Replace** | Sourced from warehouse NGS YAC above expectation | `AVAILABLE` | 2016+ | Predictor |
| **TE** | `offensive_snap_share_3yr` | `adv_offensive_snap_share_3yr` | **Replace** | Sourced from warehouse snaps | `AVAILABLE` | 100% | Predictor |
| **TE** | `snap_role_stability_3yr` | `adv_snap_role_stability_3yr` | **Replace** | Sourced from corrected snap stability | `AVAILABLE` | 100% | Predictor |
| **All** | `availability_score_3yr` | `adv_availability_score_3yr_context` | **Context** | Restricted to risk context, not direct predictor | `AVAILABLE` | 100% | Context/Risk |

### Blocked Features (100% Blocked/NULL)
The following columns remain strictly blocked and must yield `NULL`:
* `routes_run` / `yprr` / `tprr` / `receiving_first_downs_per_route` / `route_participation_rate`
* `end_zone_targets`
* `dakota`
* `pressure_epa` / `covered_receiver_epa`
* `contract_aav`
* `pigskin_context_score`

---

## 4. Leakage-Safe Dataset Design (Part B)

To protect the model from target-season data leakage, we implemented a rolling historical window using a SQL CTE join structure. 

For a target season $N$ (e.g. 2024), advanced features are aggregated only over the window $[N-3, N-1]$ (e.g. 2021-2023) from rows matching `metric_version = 'advanced_player_metrics_v1'`.

### Leakage Assertion Rule:
```sql
ON hist.season BETWEEN t.target_season - 3 AND t.target_season - 1
```
No target-season advanced metrics are exposed as predictors.

---

## 5. Dry-Run Coverage (Part D)

A dry-run query check was executed on BigQuery over target seasons 2017-2025.

### A. Integrity check:
* **Record Count**: `39,061` rows
* **Leakage Window Count**: `0` (Confirmed: NO leakage)
* **Missing Player IDs**: `0`
* **Missing Labels**: `0`
* **Duplicate Grain Count**: `0` (Confirmed: Grain is unique at `target_season`, `target_week`, `position`, `player_id_internal`)
* **Estimated Bytes Processed**: `15.85 MB`

### B. Positional Split Coverage Example (Target Season 2017):
* **QB (538 rows)**: 100% baseline/opportunity/XFP coverage, 90.8% NGS coverage.
* **RB (1,147 rows)**: 100% baseline/opportunity/XFP coverage, 69.5% NGS coverage.
* **WR (1,852 rows)**: 100% baseline/opportunity/XFP coverage, 78.7% NGS coverage.
* **TE (1,004 rows)**: 100% baseline/opportunity/XFP coverage, 59.5% NGS coverage.

NGS coverage is 0.0% for seasons < 2016 (as expected by temporal policy), and averages > 75% for seasons 2016-2025.

---

## 6. Verification & Confirmations

* **No BQML models were trained** during this phase.
* **No live rankings** were written or modified.
* **No formula champions** were activated.
* **All 26 unit tests passed** in `tests/test_bqml_v2_feature_contract.py`.
* **Deployment safety check passed** without issues.
* **BigQuery validations** successfully passed.
