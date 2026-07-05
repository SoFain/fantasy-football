# Ranking Opportunity Metrics Matrix

Phase 32.12 added an explicit opportunity and role metrics lane for ranking research. Phase 32.13 adds a bounded ffopportunity/xFP lane. Phase 32.14 uses those ideal-stat fields in Stats02 formula candidates. These lanes are additive and do not change live Pigskin rankings, ranking champions, or Pigskin tools.

## Source Availability

| Feature family | Source tables | 2014-2025 status | Implemented field |
| --- | --- | --- | --- |
| QB rushing leverage | `player_week_advanced_metrics`, `stg_player_week_stats` | Available from carries, carry share, red-zone carries, inside-five carries | `qb_rushing_leverage_index` |
| RB high-value opportunity | `player_week_advanced_metrics` | Available from red-zone touches, high-value touches, target share, opportunity share | `rb_high_value_opportunity_score` in the feature mart |
| WR dominance | `player_week_advanced_metrics` | Available from target share, air-yards share, WOPR, red-zone targets | `receiving_role_dominance_score` for WR rows |
| TE receiving role dominance | `player_week_advanced_metrics` | Available from target share, air-yards share, WOPR, red-zone targets, snap share proxy | `receiving_role_dominance_score` for TE rows |
| Red-zone usage | `player_week_advanced_metrics`, `stg_team_week_stats` | Available from red-zone targets, carries, touches, and team red-zone rates | `red_zone_usage_score` |
| Goal-line usage | `player_week_advanced_metrics` | Available from inside-ten and inside-five carries | `goal_line_usage_score` |
| Team environment | `stg_team_week_stats` | Available from plays, EPA per play, neutral pass rate | `team_environment_score` |
| Ceiling and bust history | `analytics_player_fantasy_points_by_profile` | Available from PPR weekly point thresholds by position | `spike_week_rate_3yr`, `bust_week_rate_3yr`, `elite_week_rate_3yr` |
| Expected fantasy points | `raw_ffopportunity_weekly`, `player_week_ideal_opportunity_metrics` | Available from ffopportunity weekly for 2014-2025 | `xfp_score_3yr`, `xfp_share_3yr`, `fantasy_points_over_expectation_3yr` |
| Rush and receiving xFP | `raw_ffopportunity_weekly`, `player_week_ideal_opportunity_metrics` | Available from ffopportunity weekly for 2014-2025 | `high_value_xfp_score_3yr`, `receiving_role_dominance_xfp_3yr` |
| Snap role stability | `stg_participation_context`, `player_week_ideal_opportunity_metrics` | Available as snap-count and offensive-pct proxy where snap count identity maps | `offensive_snap_share_3yr`, `snap_role_stability_3yr` |
| NGS QB efficiency | `player_week_advanced_metrics` | Proxy only in Phase 32.13 through existing `cpoe`; direct NGS fields remain deferred | `qb_ngs_efficiency_score_3yr` |
| Injury context | `raw_nflverse_injuries` | Source exists in repo lane, direct derived scoring deferred | `injury_risk_score_3yr` remains null with missing flags |
| Depth chart context | `raw_nflverse_depth_charts` | Source exists in repo lane, direct derived scoring deferred | `depth_chart_role_score_3yr` remains null with missing flags |
| True route share | `stg_participation_context` | Source flag exists, true route source is not consistently available | Missing flag only |
| First-read share | No approved source | Unavailable | Missing flag only |
| YPRR | No approved route source | Unavailable | Missing flag only |
| End-zone targets | No approved source field | Unavailable | Missing flag only |

## Warehouse Objects

`player_week_opportunity_metrics` is one row per:

- `opportunity_metric_version`
- `season`
- `week`
- `player_id_internal`
- `position`

Backfill result:

- Seasons: 2014-2025
- Rows: 70,356
- Season-weeks: 257
- Metric version: `opportunity_metrics_v0`

`ranking_backtest_feature_mart` now carries opportunity features for target seasons 2017-2025. Predictors still use historical source windows only. Target-season outcomes remain separate.

Phase 32.13 adds two objects:

- `raw_ffopportunity_weekly`, one row per `source_version`, `season`, `week`, `game_id`, and `player_id_internal`.
- `player_week_ideal_opportunity_metrics`, one row per `source_version`, `season`, `week`, `player_id_internal`, and `position`.

The feature mart can now carry these leakage-safe historical predictors:

- `xfp_score_3yr`
- `xfp_share_3yr`
- `fantasy_points_over_expectation_3yr`
- `offensive_snap_share_3yr`
- `snap_role_stability_3yr`
- `receiving_role_dominance_xfp_3yr`
- `high_value_xfp_score_3yr`
- `qb_ngs_efficiency_score_3yr`
- `injury_risk_score_3yr`
- `depth_chart_role_score_3yr`

## Guardrails

- Blocked advanced metrics are not fabricated.
- Missing metrics remain flagged in `missing_flags_json`.
- Feature-mart enrichment does not write live rankings.
- Diagnostic tournament smoke is read-only and summary-only.
- No Python full result-row tournament path was used.
- Phase 32.13 xFP predictors come only from source seasons before the target season.
- Phase 32.14 formula weights are profile-aware in the SQL-native evaluator. PPR, Half PPR, Standard, and GNG Keeper can differ without falling back to a single board.
- Phase 32.14 writes summary-only backtest evidence. It does not write `ranking_backtest_results`, `ranking_formula_champions`, `analytics_pigskin_rankings`, or `analytics_pigskin_rankings_candidates`.

## Phase 32.14 Formula Usage

| Feature | Used in Stats02 formulas | Coverage read |
|---|---|---|
| `xfp_score_3yr` | QB, RB, WR, TE | Strong 2024 and 2025 coverage. RB/WR/TE missing rate stayed below 1 percent in the validation and holdout slices. |
| `xfp_share_3yr` | QB, RB, WR, TE | Strong coverage and useful for scoring-profile differences. PPR weights lean higher than Standard for RB/WR/TE. |
| `fantasy_points_over_expectation_3yr` | WR | Available with low missing rate, but not enough by itself to create a champion signal. |
| `offensive_snap_share_3yr` | QB, RB, WR, TE | Strong coverage. Used as an additive role feature and in the bounded availability multiplier. |
| `snap_role_stability_3yr` | QB, RB, WR, TE | Strong coverage. Helped TE and WR stability reads, but multiplier results were mixed. |
| `receiving_role_dominance_xfp_3yr` | WR, TE | Strong coverage. Best visible signal was WR and TE validation or holdout improvement. |
| `high_value_xfp_score_3yr` | RB | Strong coverage. It did not beat the current RB baseline broadly enough in validation. |
| `qb_ngs_efficiency_score_3yr` | QB | Strong QB-only coverage as the current CPOE proxy. Direct NGS remains deferred. |
| `injury_risk_score_3yr` | Not used | Deferred because current values are null or not model-ready. |
| `depth_chart_role_score_3yr` | Not used | Deferred because current values are null or not model-ready. |

Stats02 result read:

- WR and TE showed the cleanest improvement signal from xFP and role fields.
- RB remains better served by the current Pigskin and opportunity diagnostic baselines in validation.
- QB improved selected top-N slices, but not enough on captured points or aggregate utility.
- Red-zone and goal-line score derivations are weak in the current feature mart because validation and holdout min/max often sit at zero. Treat them as placeholders until the PBP ffopportunity pass/rush lane is complete.

Next source priorities:

1. Add PBP-level ffopportunity pass/rush splits.
2. Derive direct injury and depth role scoring.
3. Improve TE role context with route or participation coverage if it can be sourced without fabrication.
4. Replace QB NGS proxy with direct passing/rushing NGS features only after coverage is proven.
