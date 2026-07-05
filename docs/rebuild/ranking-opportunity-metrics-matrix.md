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
| PBP pass split xFP proxies | `raw_ffopportunity_pbp_pass`, `player_week_pbp_opportunity_metrics` | Available from ffopportunity `pbp_pass` for 2014-2025 | `receiving_xfp_pbp_3yr`, `passing_xfp_pbp_3yr`, `high_value_target_xfp_score_3yr`, `receiving_xfp_share_pbp_3yr` |
| PBP rush split xFP proxies | `raw_ffopportunity_pbp_rush`, `player_week_pbp_opportunity_metrics` | Available from ffopportunity `pbp_rush` for 2014-2025 | `rushing_xfp_pbp_3yr`, `high_value_rush_xfp_score_3yr`, `rushing_xfp_share_pbp_3yr` |
| PBP red-zone and goal-line quality | `raw_ffopportunity_pbp_pass`, `raw_ffopportunity_pbp_rush`, `player_week_pbp_opportunity_metrics` | Available when `yardline_100` or `goal_to_go` context exists | `red_zone_xfp_score_3yr`, `goal_line_xfp_score_3yr`, `opportunity_quality_score_3yr` |
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

Phase 32.15 adds three PBP split objects:

- `raw_ffopportunity_pbp_pass`, one row per `source_version`, `season`, `week`, `game_id`, `play_id`, passer, and receiver when available.
- `raw_ffopportunity_pbp_rush`, one row per `source_version`, `season`, `week`, `game_id`, `play_id`, and rusher.
- `player_week_pbp_opportunity_metrics`, one row per `source_version`, `season`, `week`, `player_id_internal`, and position.

Backfill result:

- Pass rows loaded: 227,146.
- Rush rows loaded: 175,775.
- Derived PBP weekly player rows: 65,358.
- Seasons: 2014-2025.
- Source version: `ffopportunity_pbp_latest`.

The feature mart can now carry these additional leakage-safe historical predictors:

- `receiving_xfp_pbp_3yr`
- `rushing_xfp_pbp_3yr`
- `passing_xfp_pbp_3yr`
- `red_zone_xfp_score_3yr`
- `goal_line_xfp_score_3yr`
- `high_value_target_xfp_score_3yr`
- `high_value_rush_xfp_score_3yr`
- `receiving_xfp_share_pbp_3yr`
- `rushing_xfp_share_pbp_3yr`
- `opportunity_quality_score_3yr`
- `pbp_xfp_missing_flags_json`

PBP values are xFP-like component proxies, not official fantasy-point xFP columns. The source exposes expected pass, rush, touchdown, first-down, yardline, and two-point components. The derived table records that policy in `missing_flags_json`.

## Guardrails

- Blocked advanced metrics are not fabricated.
- Missing metrics remain flagged in `missing_flags_json`.
- Feature-mart enrichment does not write live rankings.
- Diagnostic tournament smoke is read-only and summary-only.
- No Python full result-row tournament path was used.
- Phase 32.13 xFP predictors come only from source seasons before the target season.
- Phase 32.14 formula weights are profile-aware in the SQL-native evaluator. PPR, Half PPR, Standard, and GNG Keeper can differ without falling back to a single board.
- Phase 32.14 writes summary-only backtest evidence. It does not write `ranking_backtest_results`, `ranking_formula_champions`, `analytics_pigskin_rankings`, or `analytics_pigskin_rankings_candidates`.
- Phase 32.15 writes summary-only PBP diagnostic evidence. It does not write detail rows, live rankings, or champion rows.

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

1. Derive direct injury and depth role scoring.
2. Improve TE role context with route or participation coverage if it can be sourced without fabrication.
3. Replace QB NGS proxy with direct passing/rushing NGS features only after coverage is proven.
4. Consider a fast second-pass RB/WR formula refinement that blends PBP split xFP with the stronger Stats02 weekly ideal features.

## Phase 32.15 PBP Split Coverage

| Slice | Read |
|---|---|
| Raw pass rows | 227,146 rows, 2014-2025. Receiver ID mapped on 219,842 rows. |
| Raw rush rows | 175,775 rows, 2014-2025. Rusher ID mapped on all normalized rows. |
| Derived QB/RB/WR/TE rows | 65,358 rows in `player_week_pbp_opportunity_metrics`. |
| Feature mart refresh | 156,244 rows across 2017-2025, four profiles, QB/RB/WR/TE. |
| Red-zone and goal-line quality | Improved versus Phase 32.14 because PBP `yardline_100` and `goal_to_go` are now available. |
| Missing policy | Missing PBP values remain null and are flagged. No zero-fill was introduced. |

2024-2025 PPR diagnostic read:

| Candidate | Position | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| `pbp_xfp_rb_high_value_rush_recv_v0` | RB | 0.7900 | 0.8171 | 0.8931 | 0.0052 |
| `pbp_xfp_wr_high_value_receiving_v0` | WR | 0.7357 | 0.6458 | 0.7923 | 0.0027 |
| `pbp_xfp_te_receiving_role_v0` | TE | 0.7721 | 0.6088 | 0.7520 | 0.0055 |
| `pbp_xfp_qb_pass_rush_v0` | QB | 0.7032 | 0.6759 | 0.8152 | 0.0000 |

Decision read:

- RB PBP split xFP showed useful validation and holdout signal, but it did not beat all RB baselines on captured points.
- WR PBP split xFP is useful as a component, especially when compared with simple projection and scarcity baselines, but current Pigskin still wins pairwise.
- TE PBP split xFP is not enough by itself. Stats02 weekly ideal TE remains the stronger TE challenger.
- No champion formula was activated.

## Phase 32.17 RB/WR PBP Refinement Read

Phase 32.17 used these PBP and Stats02 fields in the refined RB/WR formulas:

| Field | Used for | Coverage read | Result |
|---|---|---|---|
| `xfp_score_3yr` | RB, WR | Near complete in 2024 and 2025 for RB/WR | Useful base opportunity stabilizer |
| `high_value_xfp_score_3yr` | RB | Near complete in 2024 and 2025 | Still useful, but not enough to beat aggregate current Pigskin |
| `xfp_share_3yr` | RB, WR | Near complete in 2024 and 2025 | Useful profile-sensitive share input |
| `receiving_role_dominance_xfp_3yr` | WR | Near complete in 2024 and 2025 | Stronger WR component than PBP fields alone |
| `receiving_role_dominance_score` | WR | Complete in 2024 and 2025 WR rows | Helps preserve role signal. Not used for RB because RB coverage is zero |
| `receiving_xfp_pbp_3yr` | RB, WR | RB 98.67 percent non-null in 2024 and 100 percent in 2025. WR 99.50 percent in 2024 and 99.69 percent in 2025 | Helps RB pairwise on short windows. Helps WR captured points but hurts pairwise |
| `rushing_xfp_pbp_3yr` | RB | RB 98.75 percent non-null in 2024 and 99.45 percent in 2025 | Useful RB signal. WR rush coverage is about 76 percent, so WR formulas do not use it |
| `red_zone_xfp_score_3yr` | RB, WR | Near complete in 2024 and 2025 | Helpful as a profile-sensitive secondary input |
| `goal_line_xfp_score_3yr` | RB, WR | Near complete in 2024 and 2025 | Useful for Standard and RB scoring context |
| `high_value_target_xfp_score_3yr` | RB, WR | RB near complete, WR near complete | RB receiving-weighted and WR PPR/GNG component |
| `high_value_rush_xfp_score_3yr` | RB | RB 98.75 percent non-null in 2024 and 99.45 percent in 2025 | Useful RB component |
| `receiving_xfp_share_pbp_3yr` | RB, WR | RB 98.67 percent non-null in 2024 and 100 percent in 2025. WR 99.50 percent in 2024 and 99.69 percent in 2025 | Profile-aware share signal |
| `rushing_xfp_share_pbp_3yr` | not used in Phase 32.17 formulas | RB coverage is high, WR coverage is sparse | Candidate formulas used rush xFP level instead of rush share |
| `opportunity_quality_score_3yr` | not used in final refined formulas | Near complete | Useful diagnostic field, but excluded to keep weights tight |
| `offensive_snap_share_3yr` | RB, WR | Near complete in 2024 and 2025 | Role stabilizer |
| `snap_role_stability_3yr` | RB, WR | Near complete in 2024 and 2025 | Role stabilizer |
| `team_environment_score` | RB, WR | Complete in 2024 and 2025 | Context stabilizer |
| `rb_high_value_opportunity_score` | RB | Complete for RB. Zero coverage for WR | RB-only legacy opportunity input |

Phase 32.17 result:

- RB PBP split xFP improved short-window pairwise signal in validation and holdout, but did not beat current Pigskin on the 2017-2025 aggregate.
- WR PBP split xFP improved captured points in 2024 and 2025 slices, but pairwise remained weaker than current Pigskin.
- Missing PBP metrics remain null and are reflected through missing-input rates. No zero-fill policy was introduced.
- No champion activation is supported by this evidence.

Next missing source recommendation:

1. Injury and depth role scoring for RB/WR.
2. Direct NGS receiving and rushing ingest if source coverage is real.
3. A narrower WR refinement that preserves current Pigskin pairwise strength before adding PBP captured-points boosters.

## Phase 32.18 Role Context, First-Down Proxy, Weighted Opportunity, and VOR Sensitivity Matrix

Phase 32.18 added first-down PBP proxy fields to the PBP derived table and ranking feature mart. These fields are chain-mover proxies from existing `ffopportunity` PBP fields. They are not route-based metrics and must not be described as `1D/RR`, route share, or first-read share.

| Field | Source | Feature mart field | Coverage/status | Use decision |
|---|---|---|---|---|
| `receiving_first_down_exp_pbp` | `raw_ffopportunity_pbp_pass.pass_first_down_exp` | `receiving_first_down_exp_pbp_3yr` | 53,018 derived player-week rows. Strong WR/TE/RB receiving coverage in 2024 and 2025 feature mart slices. | Keep as WR/TE/RB receiving chain-mover proxy. |
| `rushing_first_down_exp_pbp` | `raw_ffopportunity_pbp_rush.rushing_fd_exp` or `rush_first_down_exp` | `rushing_first_down_exp_pbp_3yr` | 27,023 derived player-week rows. Strong RB/QB rushing coverage, sparse WR/TE by design. | Keep as RB/QB rushing chain-mover proxy. |
| `passing_first_down_exp_pbp` | `raw_ffopportunity_pbp_pass.pass_first_down_exp` on passer rows | `passing_first_down_exp_pbp_3yr` | 7,961 derived player-week rows. QB-only practical use. | Keep for QB diagnostics only. |
| `high_value_first_down_opportunity_score` | Derived from passing, rushing, and receiving first-down expected values | `high_value_first_down_opportunity_score_3yr` | Near complete where PBP identity exists. | Useful as secondary high-value opportunity context. |
| `receiving_chain_mover_score` | Bounded score from receiving first-down proxy | `receiving_chain_mover_score_3yr` | Strong WR/TE/RB receiving coverage. | Useful for WR/TE context. |
| `rushing_chain_mover_score` | Bounded score from rushing first-down proxy | `rushing_chain_mover_score_3yr` | Strong RB/QB coverage. | Useful for RB/QB context. |
| `gemini31_rb_weighted_opportunity_ppr` | `0.47 * outside_red_zone_carries + 1.28 * red_zone_carries + 1.54 * outside_red_zone_targets + 2.39 * red_zone_targets` | `gemini31_rb_weighted_opportunity_ppr` | Populated for PPR feature mart target seasons 2017-2025 after migration 0035. | PPR-only diagnostic. Do not apply to Standard, Half PPR, or GNG Keeper. |
| `injury_risk_score_3yr` | `raw_nflverse_injuries` lane | existing feature mart field | Blocked. `raw_nflverse_injuries` currently has 0 rows. | Leave missing and flagged. Do not fabricate. |
| `depth_chart_role_score_3yr` | `raw_nflverse_depth_charts` lane | existing feature mart field | Blocked. `raw_nflverse_depth_charts` currently has 0 rows. | Leave missing and flagged. Do not fabricate. |

Feature refresh and validation:

- Migration `0034__first_down_pbp_proxy_features.sql` applied.
- Migration `0035__ranking_feature_mart_rb_weighted_opportunity.sql` applied.
- `player_week_pbp_opportunity_metrics` refreshed for 2014-2025 with 65,358 rows.
- `ranking_backtest_feature_mart` PPR QB/RB/WR/TE slices refreshed for target seasons 2017-2025 after migration 0035.
- PBP validations 223 through 230 passed after the validation contract was extended to include first-down proxy fields.
- Feature mart validations 213, 214, 221, 222, and 228 through 231 passed after adding RB weighted-opportunity columns.
- Broad ranking validation still has an unrelated projection-rank ordering failure in validation 093. Ranking formula and feature mart validations passed.

VOR baseline sensitivity:

| Policy | Replacement ranks | Result |
|---|---|---|
| `current_sql_vorp_qb12_rb24_wr24_te12` | QB12/RB24/WR24/TE12 | Best VOR captured on refreshed 2024-2025 PPR slice: 0.6911. |
| `middle_vorp_qb12_rb30_wr42_te12` | QB12/RB30/WR42/TE12 | Lower VOR captured: 0.6690. |
| `deep_vorp_qb15_rb36_wr55_te12` | QB15/RB36/WR55/TE12 | Lowest tested VOR captured: 0.6370, highest pick-band regret. |

Decision: keep first-down proxies and the PPR RB weighted-opportunity diagnostic as component inputs. Injury/depth needs source remediation before scoring. Do not change the official stored VOR semantics yet.
