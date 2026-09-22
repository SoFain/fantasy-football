# Phase Report — Phase 33.16 Advanced Metrics Warehouse Formula Audit and Fixes

## 1. Executive Summary

This report documents the audit, engineering fixes, and backfill execution for **Phase 33.16 — Advanced metrics warehouse formula audit and fixes**. During this phase, we completed a detailed code and database query audit of the advanced metrics pipeline constructed in Phase 33.15, resolved 6 distinct formula/join bugs, promoted the data versioning to `advanced_player_metrics_v1`, ran a complete backfill from 2014 to 2025, and validated all results against a 97-rule suite.

---

## 2. Technical Audit & Bug Fixes

The audit of `src/nflverse_advanced_metrics_warehouse.py` and staging tables revealed the following critical bugs which have been fully resolved:

### A. Role Context Join Key Mismatch
* **Root Cause**: `stg_player_week_stats` contains internal IDs without a prefix (e.g. `00-0031941`), whereas `player_week_role_context_metrics` contains internal IDs prefixed with `gsis:` (e.g. `gsis:00-0031941`). This mismatch caused the `LEFT JOIN` condition `pws.player_id_internal = role.player_id_internal` to yield 0 matches. As a result, all weekly and seasonal injury/availability features were `NULL`.
* **Correction**: Modified the join condition to strip the `gsis:` prefix:
  `pws.player_id_internal = REGEXP_REPLACE(role.player_id_internal, r'^gsis:', '')`

### B. Availability Direction Bug
* **Root Cause**: The weekly query mapped raw `injury_risk_score` (where higher = higher risk) directly to `availability_score` (where higher should mean healthier/more available).
* **Correction**: Sourced the score directly from the healthy-scale `role.availability_score` column (with default of 100.0 for healthy/available weeks), and correctly mapped the remaining injury features:
  * `availability_score = COALESCE(role.availability_score, 100.0)`
  * `injury_burden_score = COALESCE(role.injury_burden_score, 0.0)`
  * `injury_status_score = COALESCE(role.injury_report_count, 0.0)`
  * `missed_time_risk_score = COALESCE(role.missed_time_risk_score, 0.0)`

### C. Missing Air Yards Source
* **Root Cause**: The weekly query used `COALESCE(pws.air_yards, opp.air_yards)` for receiving air yards, which were both 100% `NULL` in the staging/opportunity tables. This led to `NULL` seasonal air yards, ADOT, and RACR.
* **Correction**: Sourced `receiving_air_yards` directly from the raw payload JSON (`receiving_air_yards`) and recalculated all dependent shares (WOPR, ADOT, RACR).

### D. Overcounted Weekly Games
* **Root Cause**: Weekly games were unconditionally set to `1`, overcounting active games for inactive roster weeks.
* **Correction**: Calculated `games` dynamically (value is `1` if player recorded a snap or positive stats like targets, carries, receptions, pass attempts, or passing yards; and `0` otherwise).

### E. Rolling Snap Stability Index
* **Root Cause**: Sourced from `role.depth_chart_role_score` which was blocked (100% `NULL`).
* **Correction**: Implemented a participation-derived rolling stability index using a 4-week moving standard deviation of offensive snap share.

### F. Outside Red-Zone Opportunity Guards
* **Root Cause**: Lacked `GREATEST(0.0, ...)` bounds, allowing negative outside targets/carries if red-zone counts exceeded total counts.
* **Correction**: Added bounds checking to all weighted opportunity formulas:
  `GREATEST(0.0, targets - red_zone_targets)` and `GREATEST(0.0, carries - red_zone_carries)`.

---

## 3. Backfill Execution

The backfill script was executed for seasons 2014-2025 using the new version `advanced_player_metrics_v1`. 

### Materialization Metrics:
* **Weekly advanced metrics rows written**: `217,232`
* **Seasonal advanced metrics rows written**: `28,865`
* **Coverage audit rows written**: `120`

---

## 4. Verification & Sanity Checks

### A. Automated Validations
Two new validations were written to ensure the integrity of the corrected formulas and data boundaries:
1. [193a_advanced_metrics_formula_sanity.sql](file:///e:/Fantasy%20Football/bigquery/validations/193a_advanced_metrics_formula_sanity.sql): Verifies opportunity sums, WOPR consistency, and weighted opportunity bounds.
2. [194a_injury_availability_games_sanity.sql](file:///e:/Fantasy%20Football/bigquery/validations/194a_injury_availability_games_sanity.sql): Verifies health metrics direction, NGS temporal availability (null/unavailable 2014-2015, available 2016+), and metadata schema.

All 97 validation scripts (including these new additions) passed successfully.

### B. 2024 REG Positional Leaderboards Sanity Check

#### 1. Wide Receivers & Tight Ends (Ordered by WOPR)
| Player Name | Team | WOPR | Target Share | Air Yards Share | Receiving EPA |
| :--- | :--- | :---: | :---: | :---: | :---: |
| A.Brown | PHI | 0.8417 | 34.15% | 47.06% | 61.81 |
| M.Nabers | NYG | 0.8351 | 34.62% | 45.11% | 45.69 |
| R.Shaheed | NO | 0.7163 | 24.26% | 50.35% | -5.93 |
| D.London | ATL | 0.7090 | 29.26% | 38.58% | 36.73 |
| C.Sutton | DEN | 0.7010 | 25.71% | 45.04% | 37.14 |

#### 2. Running Backs (Ordered by PPR Weighted Opportunity)
| Player Name | Team | Weighted Opportunity (PPR) | Red Zone Opps | Goal Line Opps | Rushing EPA |
| :--- | :--- | :---: | :---: | :---: | :---: |
| B.Robinson | ATL | 309.12 | 68 | 18 | 17.94 |
| S.Barkley | PHI | 289.56 | 75 | 21 | 37.26 |
| A.Kamara | NO | 277.67 | 41 | 11 | -18.17 |
| K.Williams | LA | 274.47 | 79 | 22 | -23.53 |
| D.Achane | MIA | 272.07 | 52 | 18 | -11.28 |

#### 3. Quarterbacks (Ordered by Passing EPA)
| Player Name | Team | Passing EPA | Passing EPA / Attempt | Rushing Yards | QB Rushing Baseline Score |
| :--- | :--- | :---: | :---: | :---: | :---: |
| L.Jackson | BAL | 172.28 | 0.363 | 915 | 36.82 |
| J.Goff | DET | 168.55 | 0.313 | 56 | 12.41 |
| J.Allen | BUF | 130.11 | 0.269 | 531 | 41.61 |
| B.Mayfield | TB | 115.39 | 0.202 | 378 | 17.48 |
| J.Burrow | CIN | 115.13 | 0.177 | 201 | 14.37 |

---

## 5. Conclusion & Handoff

The advanced metrics warehouse calculations version `advanced_player_metrics_v1` is clean, structurally sound, and mathematically verified. The dataset is fully ready for downstream consumption, including:
1. BQML v2 model training and parameter recalibration.
2. Generating LLM player profile context packets.
3. Powering owner-review boards and Streamlit dashboard overlays.
