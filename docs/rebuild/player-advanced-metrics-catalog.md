# Player Advanced Metrics Warehouse Catalog

## Schema Definitions

### 1. `player_season_advanced_metrics`
Seasonal aggregates of player volume, opportunity, and efficiency metrics. Grouped by `metric_version`, `season`, `season_type`, `player_id_internal`, and `position`.

| Column | Type | Description |
|---|---|---|
| `metric_version` | STRING | ID of the calculations build (e.g., `advanced_player_metrics_v1`). |
| `generated_at` | TIMESTAMP | Timestamp when the row was written. |
| `season` | INT64 | The NFL season (e.g., `2024`). |
| `season_type` | STRING | `REG` for regular season, `POST` for postseason. |
| `player_id_internal` | STRING | Unique internal identifier for the player. |
| `gsis_id` | STRING | GSIS ID of the player. |
| `player_name` | STRING | Player's display name. |
| `position` | STRING | Primary positional designation (e.g., `QB`, `RB`, `WR`, `TE`). |
| `position_group` | STRING | Position group designation (e.g., `QB`, `RB`, `WR`, `TE`, `OL`). |
| `team` | STRING | Last active team of the season (or the latest week active). |
| `teams_json` | STRING | JSON array of all teams the player played for in the season. |
| `targets` | FLOAT64 | Sum of targets. |
| `receptions` | FLOAT64 | Sum of receptions. |
| `carries` | FLOAT64 | Sum of carries. |
| `attempts` | FLOAT64 | Sum of passing attempts. |
| `dropbacks` | FLOAT64 | Sum of dropbacks (attempts + sacks). |
| `routes_run` | FLOAT64 | **BLOCKED (NULL)**. Routes run data is not available. |
| `pass_play_snaps` | FLOAT64 | **BLOCKED (NULL)**. |
| `offensive_snaps` | FLOAT64 | Sum of snap counts. |
| `receiving_yards` | FLOAT64 | Sum of receiving yards. |
| `receiving_air_yards` | FLOAT64 | Sum of receiving air yards. |
| `receiving_yards_after_catch`| FLOAT64 | Sum of yards after catch. |
| `receiving_epa` | FLOAT64 | Sum of EPA on target events. |
| `receiving_epa_per_target` | FLOAT64 | `receiving_epa / targets`. |
| `receiving_first_downs` | FLOAT64 | Sum of receiving first downs. |
| `receiving_first_down_rate` | FLOAT64 | `receiving_first_downs / targets`. |
| `target_share` | FLOAT64 | Seasonal target share (active weeks on team). |
| `air_yards_share` | FLOAT64 | Seasonal air yards share (active weeks on team). |
| `wopr` | FLOAT64 | Weighted Opportunity Rating: `1.5 * target_share + 0.7 * air_yards_share`. |
| `racr` | FLOAT64 | Receiver Air Yard Conversion Ratio: `receiving_yards / air_yards`. |
| `adot` | FLOAT64 | Average Depth of Target: `air_yards / targets`. |
| `red_zone_targets` | FLOAT64 | Target events inside the 20-yard line. |
| `goal_line_targets` | FLOAT64 | Target events inside the 5-yard line. |
| `end_zone_targets` | FLOAT64 | **BLOCKED (NULL)**. |
| `yprr` | FLOAT64 | **BLOCKED (NULL)** (Yards Per Route Run). |
| `tprr` | FLOAT64 | **BLOCKED (NULL)** (Targets Per Route Run). |
| `receiving_first_downs_per_route`| FLOAT64 | **BLOCKED (NULL)**. |
| `route_participation_rate` | FLOAT64 | **BLOCKED (NULL)**. |
| `rushing_yards` | FLOAT64 | Sum of rushing yards. |
| `rushing_epa` | FLOAT64 | Sum of rushing EPA. |
| `rushing_epa_per_carry` | FLOAT64 | `rushing_epa / carries`. |
| `rushing_first_downs` | FLOAT64 | Sum of rushing first downs. |
| `rushing_first_down_rate` | FLOAT64 | `rushing_first_downs / carries`. |
| `red_zone_carries` | FLOAT64 | Rushing attempts inside the 20-yard line. |
| `goal_line_carries` | FLOAT64 | Rushing attempts inside the 5-yard line. |
| `red_zone_opportunities` | FLOAT64 | `red_zone_targets + red_zone_carries`. |
| `goal_line_opportunities` | FLOAT64 | `goal_line_targets + goal_line_carries`. |
| `weighted_opportunity_standard`| FLOAT64 | Weighted Opportunity (Standard scoring coefficients). |
| `weighted_opportunity_half_ppr`| FLOAT64 | Weighted Opportunity (Half PPR scoring coefficients). |
| `weighted_opportunity_ppr` | FLOAT64 | Weighted Opportunity (PPR scoring coefficients). |
| `weighted_opportunity_gng_keeper`| FLOAT64 | Weighted Opportunity (GNG Keeper scoring coefficients). |
| `passing_yards` | FLOAT64 | Sum of passing yards. |
| `passing_epa` | FLOAT64 | Sum of passing EPA. |
| `passing_epa_per_attempt` | FLOAT64 | `passing_epa / attempts`. |
| `passing_epa_per_dropback` | FLOAT64 | `passing_epa / dropbacks`. |
| `passing_cpoe` | FLOAT64 | Average completion percentage over expected. |
| `dakota` | FLOAT64 | **BLOCKED (NULL)**. |
| `passing_first_downs` | FLOAT64 | Sum of passing first downs. |
| `passing_first_down_rate` | FLOAT64 | `passing_first_downs / attempts`. |
| `qb_rushing_baseline_score` | FLOAT64 | QB rushing baseline rating. |
| `ngs_avg_separation` | FLOAT64 | Seasonal average separation (WR/TE/RB). |
| `ngs_avg_cushion` | FLOAT64 | Seasonal average cushion (WR/TE/RB). |
| `ngs_yac_above_expectation` | FLOAT64 | Seasonal average yards after catch above expected. |
| `ngs_rushing_efficiency` | FLOAT64 | NGS rushing efficiency score. |
| `ngs_rush_yards_over_expected` | FLOAT64 | Average rush yards over expected. |
| `ngs_rush_yards_over_expected_per_att`| FLOAT64| Average rush yards over expected per attempt. |
| `ngs_box_count_rate` | FLOAT64 | Percentage of attempts against 8+ defenders. |
| `ngs_qb_time_to_throw` | FLOAT64 | Average time to throw (QB). |
| `ngs_qb_aggressiveness` | FLOAT64 | Average QB aggressiveness percentage. |
| `ngs_qb_cpoe` | FLOAT64 | NGS calculated CPOE (QB). |
| `offensive_snap_share` | FLOAT64 | Average offensive snap share. |
| `snap_role_stability` | FLOAT64 | Rolling weekly participation stability index derived from offensive snap share. |
| `availability_score` | FLOAT64 | Average availability metric (100.0 is fully healthy/available, 0.0 is injured/out). |
| `injury_status_score` | FLOAT64 | Total weeks appearing on the injury report. |
| `injury_burden_score` | FLOAT64 | Average injury burden rating. |
| `missed_time_risk_score` | FLOAT64 | Total weeks designated as OUT or missed. |
| `route_metrics_source_status` | STRING | `BLOCKED` for all seasons. |
| `ngs_source_status` | STRING | `AVAILABLE` (2016+), `UNAVAILABLE` (2014-2015). |
| `participation_source_status` | STRING | `AVAILABLE` (2014+). |
| `contract_source_status` | STRING | `UNAVAILABLE` for all seasons. |
| `pressure_coverage_source_status`| STRING| `UNAVAILABLE` for all seasons. |
| `source_coverage_json` | STRING | Auditing JSON listing week-level source metadata. |
| `missing_flags_json` | STRING | Boolean indicators identifying missing source weeks. |
| `proxy_flags_json` | STRING | Indicators of proxy route/pressure usage. |
| `blocked_flags_json` | STRING | Indicators of permanently blocked columns. |

### 2. `player_metric_source_coverage`
Audit table containing the source coverage stats per metric and season.

| Column | Type | Description |
|---|---|---|
| `metric_version` | STRING | calculations build version (e.g. `advanced_player_metrics_v1`). |
| `season` | INT64 | Season year (2014-2025). |
| `metric_name` | STRING | Name of the checked metric (e.g. `WOPR`, `YPRR`, `NGS Cushion`). |
| `source_status` | STRING | `AVAILABLE`, `UNAVAILABLE`, or `BLOCKED`. |
| `coverage_count` | INT64 | Total weekly rows analyzed. |
| `non_null_count` | INT64 | Total weekly rows where the metric was non-null. |
| `created_at` | TIMESTAMP | Audit generation timestamp. |

---

## Data Policies & Design Decisions

### 1. Route Metrics (YPRR, TPRR, etc.)
* **Policy**: **BLOCKED**.
* **Reasoning**: `stg_participation_context` has `has_true_route_source = false` and `route_share = null` across all seasons (2014-2025). Fabricating routes run is strictly prohibited.
* **Result**: All route-run dependent columns (`routes_run`, `yprr`, `tprr`, `receiving_first_downs_per_route`, `route_participation_rate`) remain `NULL` across all rows. `route_metrics_source_status` is set to `'BLOCKED'`.

### 2. Next Gen Stats (NGS) Scope
* **Policy**: NGS data starts in **2016**.
* **Result**: For seasons 2014 and 2015, all NGS columns are `NULL` and `ngs_source_status` is `'UNAVAILABLE'`. For seasons 2016-2025, NGS columns are populated and `ngs_source_status` is `'AVAILABLE'`.

### 3. Traded Players (Multi-team Seasons)
* **Policy**: Player seasonal statistics are aggregated into a single row per season/position.
* **Team Resolution**: The `team` column contains the last team the player played for during that season (evaluated by the latest active week).
* **Multi-Team Evidence**: The `teams_json` column contains a JSON array of all teams the player represented (e.g., `["BUF", "KC"]`).
* **Volume/Efficiency**: All volume metrics are summed. Shares (e.g. `target_share`, `air_yards_share`) are computed using the sums of the player's metrics divided by the sum of the respective team totals for the specific weeks the player played.

### 4. Weighted Opportunity Formula
Calculated using the following coefficients based on the targets/carries red zone designation:
* **Standard**: `(red_zone_targets * 1.47) + (outside_red_zone_targets * 0.67) + (red_zone_carries * 1.28) + (outside_red_zone_carries * 0.47)`
* **Half PPR**: `(red_zone_targets * 1.93) + (outside_red_zone_targets * 1.00) + (red_zone_carries * 1.28) + (outside_red_zone_carries * 0.47)`
* **PPR**: `(red_zone_targets * 2.39) + (outside_red_zone_targets * 1.54) + (red_zone_carries * 1.28) + (outside_red_zone_carries * 0.47)`
* **GNG Keeper (0.1 PPR)**: `(red_zone_targets * 1.56) + (outside_red_zone_targets * 0.74) + (red_zone_carries * 1.28) + (outside_red_zone_carries * 0.47)`

*Note: `outside_red_zone_targets = GREATEST(0.0, targets - red_zone_targets)` and `outside_red_zone_carries = GREATEST(0.0, carries - red_zone_carries)` to guard against negative outside counts.*

---

## Agent Query Guide

Downstream agents should query `player_season_advanced_metrics` directly for positional analysis.

### Example 1: Top 10 Wide Receivers by WOPR (2024 REG)
```sql
SELECT
  player_name,
  team,
  teams_json,
  targets,
  target_share,
  air_yards_share,
  wopr
FROM `fantasy-football-498121.fantasy_football_brain.player_season_advanced_metrics`
WHERE season = 2024
  AND season_type = 'REG'
  AND position = 'WR'
  AND metric_version = 'advanced_player_metrics_v1'
ORDER BY wopr DESC
LIMIT 10;
```

### Example 2: Comparing Weighted Opportunity Across Profiles (2024 REG, Running Backs)
```sql
SELECT
  player_name,
  team,
  carries,
  targets,
  weighted_opportunity_standard,
  weighted_opportunity_half_ppr,
  weighted_opportunity_ppr,
  weighted_opportunity_gng_keeper
FROM `fantasy-football-498121.fantasy_football_brain.player_season_advanced_metrics`
WHERE season = 2024
  AND season_type = 'REG'
  AND position = 'RB'
  AND metric_version = 'advanced_player_metrics_v1'
ORDER BY weighted_opportunity_ppr DESC
LIMIT 10;
```

---

## BQML v2 Integration

The advanced player metrics warehouse serves as the canonical data source for BQML v2 positional ranking models. 

### 1. Feature Allowlists & Mapping
All positional predictors are mapped to rolling 3-year averages computed from the `advanced_player_metrics_v1` seasonal table. For example:
* **QB**: Passing EPA is mapped via `adv_passing_epa_3yr`.
* **RB**: Opportunity is mapped via `adv_weighted_opportunity_profile_3yr` (profile-specific resolution).
* **WR/TE**: Receiving volume is mapped via `adv_wopr_3yr` and `adv_targets_3yr`.

### 2. Leakage Safeguard Policy
To prevent future leakage, training datasets must aggregate historical data using a strictly bounded window where the historical season is strictly less than the target season:
```sql
hist.season BETWEEN target_season - 3 AND target_season - 1
```
No target-season data from `player_season_advanced_metrics` may be used as a predictor.
