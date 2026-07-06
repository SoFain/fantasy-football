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
| Injury context | `raw_nflverse_injuries`, `player_week_role_context_metrics` | Historical injury rows are loaded for 2014-2025 and grouped into player-week risk context | `injury_risk_score_3yr` has a direct source lane ready for a controlled ideal-stat and feature-mart refresh |
| Depth chart context | `raw_nflverse_depth_charts` | Historical depth remains blocked. Current `nflreadpy.load_depth_charts` output lacks historical `season` and `week` keys | `depth_chart_role_score_3yr` remains null with missing flags |
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

## Phase 32.19 Depth, Injury, and Sleeper Context Remediation

Phase 32.19 fixed the historical injury source lane and added a current Sleeper player snapshot lane. It did not change live rankings, champion formulas, or Pigskin chat exposure.

| Lane | Result |
|---|---|
| Historical injuries | `raw_nflverse_injuries` loaded 65,866 rows for 2014-2025. |
| Injury role context | `player_week_role_context_metrics` materialized 65,864 grouped player-week rows. Injury risk is bounded 0-100. |
| Historical depth charts | Still blocked. `nflreadpy.load_depth_charts` returned current snapshot-style rows without historical `season` and `week`, so no depth rows were written. |
| Sleeper 2026 current snapshot | `raw_sleeper_players_snapshot` captured 12,200 rows from `/players/nfl`; `sleeper_player_context_current` exposes the latest point-in-time context. |
| Tyreek current-team safety | Latest Sleeper context has `sleeper_current_team = null` for `00-0033040`; the identity bridge still has `identity_current_team = MIA`, so downstream current-roster displays should prefer Sleeper current team when avoiding stale-team inference. |
| Feature mart | Existing `injury_risk_score_3yr` and `depth_chart_role_score_3yr` columns remain in place. A later controlled refresh should wire injury context into `player_week_ideal_stats` and `ranking_backtest_feature_mart`; depth stays flagged unavailable. |

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
| `injury_risk_score_3yr` | `raw_nflverse_injuries`, `player_week_role_context_metrics` | existing feature mart field | Source lane implemented in Phase 32.19. `raw_nflverse_injuries` has 65,866 rows for 2014-2025. `player_week_role_context_metrics` has 65,864 grouped player-week rows. | Ready for a separate controlled ideal-stat and feature-mart refresh. Do not backfill live rankings in the source-remediation phase. |
| `depth_chart_role_score_3yr` | `raw_nflverse_depth_charts` lane | existing feature mart field | Still blocked. `nflreadpy.load_depth_charts` returned 554,215 current snapshot rows with no historical `season` or `week`; the raw historical table remains empty. | Leave missing and flagged. Do not fabricate. |

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

## Phase 32.20 Injury Context Feature Refresh

Phase 32.20 moved historical injury context from source remediation into the ranking research feature mart. This did not regenerate live rankings, activate champions, expose Pigskin chat, or use Sleeper current team as historical truth.

| Field | Source | Feature mart field | Coverage/status | Use decision |
|---|---|---|---|---|
| `injury_status_score` | `raw_nflverse_injuries`, grouped in `player_week_role_context_metrics` | `injury_status_score_3yr` | Populated in 2017-2025 target seasons from source seasons strictly before the target season. | Keep as a health-side modifier. |
| `injury_burden_score` | Injury report count plus report/practice status counts | `injury_burden_score_3yr` | Bounded 0-100 and validated after feature-mart refresh. | Useful as a risk-side diagnostic, inverted by SQL-native scoring. |
| `missed_time_risk_score` | Explicit Out and Doubtful injury statuses only | `missed_time_risk_score_3yr` | Bounded 0-100. Sparse missed-time signal by design. | Keep, but do not overweight. |
| `availability_score` | Inverse of source-supported injury risk | `availability_score_3yr` | Best injury-context modifier in aggregate tests. | Candidate input for future RB/WR/TE blends. |
| `identity_mapping_method` | `player_identity_bridge` exact GSIS, then `gsis:` fallback | role-context provenance only | `missing_identity_count = 0` after deterministic fallback. `gsis_exact_fallback` remains explicit. | Safe for research. Do not use fallback as current roster truth. |
| `depth_chart_role_score` | Historical depth chart lane | `depth_chart_role_score_3yr` | Still unavailable because historical season/week depth rows remain absent. | Leave null and flagged. |

Feature refresh and validation:

- Migration `0038__injury_context_feature_mart_columns.sql` applied.
- `player_week_role_context_metrics` refreshed for 2014-2025 with 65,864 rows.
- `ranking_backtest_feature_mart` refreshed for target seasons 2017-2025, four profiles, QB/RB/WR/TE.
- Focused validations 234 through 240 passed.
- SQL-native PPR diagnostic wrote summary-only evidence: 40 candidate summaries, zero detail rows, no champion activation.

2017-2025 PPR injury-context read:

| Position | Best injury-context candidate | Pairwise | Top-N | Rank corr. | Missing |
|---|---|---:|---:|---:|---:|
| QB | `availability_adjusted_current_pigskin_v0` | 0.6870 | 0.5728 | 0.4343 | 0.0305 |
| RB | `availability_adjusted_current_pigskin_v0` | 0.7436 | 0.6200 | 0.5476 | 0.0358 |
| WR | `availability_adjusted_current_pigskin_v0` | 0.7590 | 0.5058 | 0.5586 | 0.0351 |
| TE | `availability_adjusted_current_pigskin_v0` | 0.7364 | 0.4731 | 0.4941 | 0.0357 |

Decision read:

- Injury context is useful as a modifier, especially for RB, but it does not beat the current Pigskin baseline outright on aggregate.
- The direct injury-only diagnostic is not a champion path.
- Depth remains blocked and must stay null until a historical source with season/week truth exists.
- Sleeper 2026 snapshot is live-current context only. It was not used in the historical feature mart.

## Phase 32.21 Low-Weight Injury Availability Modifier

Phase 32.21 tested whether the Phase 32.20 injury fields help when used as a small modifier rather than a standalone formula. It used SQL-native summary evaluation only.

| Field | Direction | Modifier use | Read |
|---|---|---|---|
| `availability_score_3yr` | Higher is healthier | 3 percent or 5 percent blend with current Pigskin and position-specific xFP candidates | 3 percent is safer. 5 percent over-penalizes in several slices. |
| `injury_status_score_3yr` | Higher is healthier | Available but not selected as the main low-weight blend field | Keep as supporting context. |
| `injury_burden_score_3yr` | Higher is riskier | Inverted by SQL-native scoring in capped penalty candidate | Useful as a tiny risk-side signal. Do not overweight. |
| `missed_time_risk_score_3yr` | Higher is riskier | Inverted by SQL-native scoring in capped penalty candidate | Sparse but useful for penalty-cap tests. Do not overweight. |
| `depth_chart_role_score_3yr` | Higher would be stronger role | Not used | Still blocked because historical season/week depth rows are unavailable. |
| Sleeper current context | Current roster display only | Not used | Must stay out of historical backtest features. |

Coverage read:

| Slice | QB availability non-null | RB availability non-null | WR availability non-null | TE availability non-null |
|---|---:|---:|---:|---:|
| 2017-2025 aggregate | 0.7152 | 0.7137 | 0.7344 | 0.7012 |
| 2024 validation | 0.5079 | 0.3378 | 0.3895 | 0.3707 |
| 2025 holdout | 0.8983 | 0.8716 | 0.8652 | 0.9796 |

Summary-only write:

- Four run rows were written, one per scoring profile.
- 284 summary rows were written across the comparison set.
- 60 rows covered the six new low-weight injury availability candidate IDs.
- Zero detail rows were written.
- Zero champion rows were written.

Result read:

- RB low-weight availability plus high-value rush xFP improved pairwise on 2025 holdout and aggregate profile slices, but captured points often slipped slightly.
- TE low-weight availability plus receiving role dominance xFP showed the cleanest aggregate signal, especially PPR and Half PPR.
- QB saw tiny gains only from capped penalty in selected profiles.
- WR remains fragile. It should not be promoted until it protects pairwise strength.

Decision: keep injury availability as a low-weight modifier lane. Do not activate a champion. Do not tune on 2025 holdout. Do not use Sleeper current roster data as historical input.

## Phase 32.22 Owner-Review Cutline Read

Phase 32.22 evaluated the RB and TE availability modifiers as draft-utility cutline tools. It used read-only SQL only.

| Field | Cutline read | Carry-forward decision |
|---|---|---|
| `availability_score_3yr` | Helps selected RB and TE movement, but does not consistently improve position cutlines. | Keep as a small risk flag and explainability field. |
| `injury_burden_score_3yr` | Useful for capped penalty context, but missingness and source sparsity make it too rough for promotion. | Keep inverted and low-weight only. |
| `missed_time_risk_score_3yr` | Sparse. It helps explain some penalty movement but cannot carry a formula. | Keep as warning context. |
| `high_value_rush_xfp_score_3yr` | Drives much of the RB modifier movement. Overall draft cutlines improved, position cutlines did not. | Keep as RB component. Do not call the RB result an injury win. |
| `receiving_role_dominance_xfp_3yr` | Drives much of the TE modifier movement. TE6 and TE12 improved in 2025 holdout, but 2024 TE12 weakened. | Keep as TE component with risk-flag overlay. |
| `depth_chart_role_score_3yr` | Still unavailable. | Keep blocked and null. |
| Sleeper current context | Not used. | Keep live-current display only, never historical backtest input. |

Cutline decision:

- RB availability modifier: `use as risk flag only`.
- TE availability modifier: `use as risk flag only`.
- Generic 5 percent availability blend: `reject as default`.
- WR availability modifier: `reject for owner-review`.

Reason: RB and TE have useful examples, but neither passes the full owner-review challenger threshold. RB improves overall draft-board cuts while failing position validation cuts. TE improves TE6 and TE12 in the holdout but has unstable TE3 and 2024 TE12 behavior. This is a risk-adjustment signal, not a ranking model.
