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
- Phase 32.32 confirms CTE-only live 2026 BQML review input is available for Standard, Half PPR, PPR, and GNG Keeper. The production candidate table remains PPR-only and was not overwritten.
- Phase 32.37 deployed the read-only Formula Review dashboard code and reduced active live TE depth to 35 per scoring profile. It did not run live ranking generation, write champions, overwrite candidates, call Gemini, call Pigskin chat, call Sleeper, train BQML, or ingest source data.
- Phase 32.38 keeps opportunity, role, ideal, PBP, NGS, injury, and availability fields as explanation context only for v1.0. Current Pigskin remains the live formula for every scoring profile and position. Pigskin chat can use `docs/rebuild/pigskin-live-ranking-formula-context.md` as static policy context, but it must not treat any component lane as an active champion.

## Phase 32.38 Formula-Context Status

| Field family | Pigskin chat use for v1.0 | Live formula status |
|---|---|---|
| Analytical grade proxy | Explain Current Pigskin candidate evidence. | Part of Current Pigskin candidate proxy. |
| Opportunity score proxy | Explain role and workload strength. | Part of Current Pigskin candidate proxy. |
| Efficiency score proxy | Explain production quality. | Part of Current Pigskin candidate proxy. |
| Role stability score | Explain role reliability and volatility. | Part of Current Pigskin candidate proxy. |
| Profile points score | Explain scoring-profile fit. | Part of Current Pigskin candidate proxy. |
| Stats02 fields | Owner-review component signal only. | Not live. |
| PBP xFP fields | Owner-review component signal only. | Not live. |
| Direct NGS fields | Owner-review component signal only. | Not live. |
| Injury and availability fields | Risk flags only. | Not live. |
| Historical depth context | Blocked. | Not live. |

## Phase 32.23 Owner-Review Status

| Signal family | Current owner-review status | Notes |
|---|---|---|
| Stats02 ideal fields | owner-review concept | Useful WR/TE and QB component signal. Not a champion formula. |
| PBP xFP fields | owner-review concept | Useful RB/WR component lane. RB improves selected short windows. WR helps captured points but weakens pairwise. |
| Availability score | risk flag only | Keep beside rankings or in diagnostics until a separate owner-approved modifier phase. |
| Injury burden and missed-time risk | risk flag only | Useful explanatory context, not a standalone ranking default. |
| RB availability modifier | risk flag only | Phase 32.22 validation cutlines did not clear owner-review challenger threshold. |
| TE availability modifier | risk flag only | Better TE cutline story than RB, but TE3 and 2024 TE12 instability block default use. |
| WR availability modifier | rejected or deferred | Pairwise fragility remains the blocker. |
| Generic 5 percent availability blend | rejected as default | Over-penalization risk. |
| Historical depth role | blocked | No approved historical depth source. |
| Sleeper current context | live-only display context | Do not use in historical backtests. |
| Direct NGS receiving/rushing | not yet ingested | Candidate next source lane if owner wants source expansion before BQML retrain. |

Phase 32.23 keeps these signals out of live rankings. The comparison report recommends BQML retrain with ideal, PBP, injury, and role context as the next technical lane unless the owner chooses NGS ingest first.

## Phase 32.24 BQML Enriched Feature Read

Phase 32.24 used enriched BQML v1 models to test the current feature mart as a model challenger lane. It did not write live rankings or champions.

| Feature family | BQML v1 status | Read |
|---|---|---|
| Baseline Pigskin proxies | included | Still useful. Boosted tree importance included `analytical_grade_proxy`, `opportunity_score_proxy`, and `profile_points_score`. |
| Ideal xFP fields | included | `xfp_share_3yr` and `fantasy_points_over_expectation_3yr` showed model signal. |
| PBP xFP fields | included | Logistic elite used receiving and rushing xFP share fields as positive signals. |
| First-down proxies | included | Included as bounded predictors. No standalone causal claim. |
| Injury and availability | included as predictors, still risk flags | Coverage is sparse in 2024 and stronger in 2025. They remain risk flags, not default ranking formulas. |
| Historical depth | excluded | Still blocked. `depth_chart_role_score_3yr` was intentionally excluded from enriched BQML predictors. |
| Sleeper current context | excluded | Live-only display context. Not used in historical training. |
| Direct NGS receiving/rushing | not yet ingested | Still the cleanest source gap if the owner wants better feature signal before another retrain. |

Decision: enriched BQML improved the challenger lane, especially logistic elite and linear points, but not enough to activate a champion.

## Phase 32.25 BQML Owner-Review Feature Read

Phase 32.25 reviewed enriched BQML player movement and cutlines without training new models or changing live rankings.

| Feature family | Owner-review read | Decision |
|---|---|---|
| Baseline Pigskin proxies | Still protect pairwise and rank correlation. | Keep current Pigskin live. |
| Ideal xFP fields | Helped enough to keep enriched BQML alive as a challenger lane. | Use in BQML owner-review cuts. |
| PBP xFP fields | Useful in RB movement and some upside signals. WR movement remains fragile. | Component signal, not a standalone formula. |
| First-down proxies | Included in BQML v1, but no separate activation proof. | Keep as supporting context. |
| Role-history metrics | Logistic elite weights favored elite rate, spike rate, target slope, carry slope, and WOPR slope. | Strongest explainability lane. |
| Injury and availability | Useful for warning context, but sparse in 2024 and not proven as a default formula. | Risk flag only. |
| Historical depth | Not used because source context remains blocked. | Blocked. |
| Direct NGS receiving/rushing | Still not ingested. | Best next source gap if owner wants better signal before another retrain. |

Owner-read summary: enriched logistic elite v1 is the cleaner top-N utility challenger. Enriched linear points v1 is the better board-ordering challenger. Neither should replace current Pigskin without owner review of generated candidate boards.

## Phase 32.26 BQML Board Movement Read

Phase 32.26 generated review-only BQML candidate boards for PPR, Half PPR, Standard, and GNG Keeper from the existing 2025 Week 18 feature-mart slice.

| Feature family | Movement read | Decision |
|---|---|---|
| Baseline Pigskin proxies | Current Pigskin remains the comparison baseline for every row. | Keep live. |
| Ideal xFP fields | Present in board explanation fields and useful for BQML movement context. | Owner-review signal. |
| PBP xFP fields | Visible in movement explanations, especially for RB and some upside WR movement. | Component signal. |
| First-down proxies | Available to the enriched model family, but not surfaced as a standalone owner explanation in the compact board tables. | Supporting context. |
| Role-history metrics | Elite-week rate, spike rate, and bust rate are the clearest review fields for logistic movement. | Strong explanation lane. |
| Injury and availability | Included as warning fields. Still not proof of a default ranking formula. | Risk flag only. |
| Historical depth | Not used. | Blocked. |
| Direct NGS receiving/rushing | Still absent from the board. | Best next source gap. |

Decision: BQML board movement is useful enough for owner review. It is not enough for champion activation, mostly because WR movement remains fragile and current Pigskin still protects the live baseline.

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

## Phase 32.27 Direct nflverse NGS Metrics

Phase 32.27 moved direct public nflverse Next Gen Stats from a source gap to an implemented research lane. The data is source-versioned, bounded by season, and consumed by the ranking feature mart with a strict target-season leakage guard.

| Source | Fields ingested | Coverage/status | Use decision |
|---|---|---|---|
| `raw_nflverse_ngs_receiving` | `avg_cushion`, `avg_separation`, `avg_intended_air_yards`, `percent_share_of_intended_air_yards`, `receptions`, `targets`, `catch_percentage`, `yards`, `rec_touchdowns`, `avg_yac`, `avg_expected_yac`, `avg_yac_above_expectation` | 14,716 loaded rows for 2016-2025 | Use for WR/TE receiving efficiency, separation, and YAC over expected. |
| `raw_nflverse_ngs_rushing` | `efficiency`, `percent_attempts_gte_eight_defenders`, `avg_time_to_los`, `rush_attempts`, `expected_yards`, `rush_yards_over_expected`, `rush_yards_over_expected_per_att`, `rush_pct_over_expected` | 6,052 loaded rows for 2016-2025 | Use for RB rushing efficiency, RYOE, and box resilience. |
| `raw_nflverse_ngs_passing` | `avg_time_to_throw`, `avg_intended_air_yards`, `aggressiveness`, `expected_completion_percentage`, `completion_percentage_above_expectation` | 5,925 loaded rows for 2016-2025 | Use for QB passing efficiency context. |
| Expected catch and catch-over-expected | Not present in the public nflverse receiving feed used here | Explicitly unavailable | Keep null with missing flags. Do not fabricate or zero-fill. |

Derived table:

| Object | Grain | Rows/status |
|---|---|---:|
| `player_week_ngs_metrics` | `source_version`, `season`, `week`, `player_id_internal`, `position` | 24,557 rows for `nflverse_ngs_direct_latest` |

Feature mart columns:

- `ngs_receiving_efficiency_score_3yr`
- `ngs_yac_over_expected_score_3yr`
- `ngs_separation_score_3yr`
- `ngs_catch_over_expected_score_3yr`
- `ngs_rushing_efficiency_score_3yr`
- `ngs_rush_yards_over_expected_score_3yr`
- `ngs_box_resilience_score_3yr`
- `ngs_qb_passing_efficiency_score_3yr`
- `ngs_missing_flags_json`

Recent target-season coverage:

| Target season | QB passing NGS | RB rushing NGS | TE receiving NGS | WR receiving NGS |
|---:|---:|---:|---:|---:|
| 2024 | 2,280 of 2,292 | 4,240 of 5,104 | 3,264 of 4,348 | 7,020 of 7,928 |
| 2025 | 1,168 of 1,180 | 1,076 of 1,464 | 1,364 of 1,568 | 2,376 of 2,552 |

Decision:

- Direct NGS should feed the next BQML retrain.
- The standalone NGS diagnostic lanes are useful for owner review and explainability, but not champion selection.
- RB rushing NGS and WR/TE receiving NGS are the strongest component lanes.
- Missing expected catch and catch-over-expected stay flagged.

## Phase 32.28 BQML NGS Retrain Feature Read

Phase 32.28 retrained bounded BQML challengers with direct NGS feature-mart columns included. The split stayed chronological: train on 2017-2023, validate on 2024, and hold out 2025. No live rankings, champions, detail rows, deployment, Sleeper calls, Pigskin chat, or Gemini calls changed.

| NGS field | BQML status | Read |
|---|---|---|
| `ngs_receiving_efficiency_score_3yr` | included | Real WR/TE coverage. Did not produce a broad WR champion signal in the NGS retrain. |
| `ngs_yac_over_expected_score_3yr` | included | Real WR/TE YAC signal, useful for explanation but not enough to fix WR movement risk alone. |
| `ngs_separation_score_3yr` | included | Real WR/TE separation signal. Linear models leaned more on missingness than the raw signal. |
| `ngs_catch_over_expected_score_3yr` | included as nullable and missing-flagged | Public nflverse receiving did not provide expected catch or catch-over-expected. Keep null. Do not fabricate. |
| `ngs_rushing_efficiency_score_3yr` | included | Strongest direct NGS signal in boosted-tree VOR. Keep as RB component signal. |
| `ngs_rush_yards_over_expected_score_3yr` | included | Used by boosted-tree VOR, but not enough for a standalone champion path. |
| `ngs_box_resilience_score_3yr` | included | Real RB context. Useful as explainability, not a default formula. |
| `ngs_qb_passing_efficiency_score_3yr` | included | Strong QB coverage. No clear QB champion change from this retrain. |
| `ngs_missing_flags_json` | included as evidence | Missingness matters. Linear BQML weights show missing indicators can dominate, so reports must show missingness beside scores. |

Recent PPR coverage:

| Target season | QB passing NGS | RB rushing NGS | TE receiving NGS | WR receiving NGS | Catch-over-expected |
|---:|---:|---:|---:|---:|---:|
| 2024 | 570 of 573 | 1,060 of 1,276 | 816 of 1,087 | 1,755 of 1,982 | 0 |
| 2025 | 292 of 295 | 269 of 366 | 341 of 392 | 594 of 638 | 0 |
| 2017-2025 | 4,474 of 4,646 | 8,066 of 9,969 | 6,082 of 8,458 | 13,814 of 15,988 | 0 |

Decision:

- Direct NGS remains a model feature and component signal.
- It does not become a live ranking formula or champion.
- RB rushing NGS is the clearest additive component signal.
- WR/TE receiving NGS helps explain movement, but WR movement remains too fragile for automatic promotion.
- Missing expected catch and catch-over-expected stay blocked and visible.

## Phase 32.29 Final Source Status

Phase 32.29 holds current Pigskin as the live baseline. No formula champion is active.

| Source or signal | Final status | Use |
|---|---|---|
| Current Pigskin final rankings | live baseline | Keep as production ranking source. |
| Simple projection | owner-review signal | Keep as a basic sanity-check challenger. |
| Enriched BQML logistic elite v1 | owner-review signal | Use for top-N, VOR, NDCG, and bust-control review. |
| Enriched BQML linear points v1 | owner-review signal | Use for board-ordering review. |
| BQML NGS models | context only | Direct NGS did not materially improve over enriched v1. |
| Direct NGS diagnostics | component signal | RB rushing NGS is the strongest component. WR/TE receiving NGS is explainability context. |
| Stats02 WR/TE | component signal | Keep for position-specific review, not default ranking. |
| PBP RB/WR | component signal | Keep RB high-value opportunity. Protect WR movement. |
| Injury and availability | risk flag only | Display as low-weight context. Do not promote as a formula. |
| Sleeper current context | live-only display/context | Use only for live review fields with freshness. Never use as historical truth. |
| Historical depth | blocked | Keep blocked until a historical source with season/week role context exists. |

Live 2026 review-board source read:

- `analytics_pigskin_rankings_candidates` contains 936 PPR candidate rows for 2026.
- `ranking_backtest_feature_mart` does not yet contain a 2026 target slice.
- `sleeper_player_context_current` contains 12,200 latest-context rows with snapshot timestamp `2026-07-05T17:52:48.174830Z`.
- A future review board needs an outcome-free 2026 prediction input before BQML challenger ranks can be generated safely.

## Phase 32.30 Live Review Input Coverage

Phase 32.30 built the first outcome-free 2026 BQML review input and generated PPR-only owner boards. It did not write live rankings, champions, detail backtest rows, or persistent review tables.

Input source status:

| Source or family | Live 2026 status | Review use |
|---|---|---|
| Current Pigskin active rankings | 1,140 active rows, four scoring profiles | Live baseline only. |
| 2026 ranking candidates | 936 PPR rows | PPR review universe. No non-PPR fallback. |
| `ranking_backtest_feature_mart` | 0 target-season 2026 rows | Prior compatible predictors only. No outcome fields selected. |
| Sleeper current context | 12,200 rows, latest snapshot `2026-07-05 17:52:48.174830+00:00` | Display-only context joined by internal ID and GSIS ID. |
| Direct NGS | Sparse in live review input | Component signal and context only. |
| Injury and availability | Sparse in live review input | Risk flag only. |

Feature coverage in the PPR review input:

| Feature family | Populated values | Possible values | Coverage |
|---|---:|---:|---:|
| Baseline candidate proxies | 3,090 | 5,616 | 55.0% |
| Trend proxies | 523 | 4,680 | 11.2% |
| Ideal xFP | 428 | 3,744 | 11.4% |
| PBP xFP and first-down proxies | 416 | 5,616 | 7.4% |
| Direct NGS | 236 | 7,488 | 3.2% |
| Injury and availability | 484 | 5,616 | 8.6% |

Decision:

- Baseline candidate proxies are usable for owner review.
- Ideal, PBP, NGS, and injury families remain too sparse for automatic promotion.
- Sleeper current context is display-only. Null current teams remain unknown, with no stale identity-team fallback.
- At Phase 32.30, Standard, Half PPR, and GNG Keeper live review boards were blocked because the 2026 candidate input was PPR-only.
- Scoring systems should be reviewed in this order when all are available: Standard, Half PPR, PPR, GNG Keeper.
- All-profile aggregate should be treated as stability/context only, not as a champion-selection decision.
- Current Pigskin remains the live baseline.


## Phase 32.32 Profile-Specific Review Coverage

| Profile | Candidate rows | Average missing feature rate | Standard-first status |
|---|---:|---:|---|
| `standard` | 936 | 69.0% | ready with warnings |
| `half_ppr` | 936 | 69.0% | ready with warnings |
| `ppr` | 936 | 69.0% | ready with warnings |
| `gng_keeper` | 936 | 69.0% | ready with warnings |

The review input uses source-backed candidate and historical feature fields only. `pigskin_context_score` is not required or fabricated. Missing NGS, PBP, ideal, and injury fields stay visible as missingness warnings.

## Phase 32.33 Dashboard Source Status

| Source or display lane | Status | Owner-review use |
|---|---|---|
| `docs/rebuild/live-2026-ranking-review-boards.md` | dashboard source | Static read-only source for Standard, Half PPR, PPR, and GNG Keeper review boards. |
| Formula Review app tab | ready behind `USE_FORMULA_COMPARISON_DASHBOARD` | Owner-facing review only. It does not write warehouse rows or run BQML predictions. |
| Enriched Logistic Elite | review-only challenger | Displayed per scoring profile. It is not a champion or live ranking source. |
| Enriched Linear Points | context only | Displayed as volatile board-ordering context. |
| BQML NGS | context only | Not included as a candidate board in the dashboard source. |
| Missingness warnings | visible | Average missingness and high family missingness remain owner-review warnings. |
| TE owner-review output | capped at TE35 | TE6, TE12, and TE18 cutlines remain visible. Live TE60 rows are unchanged. |
| `USE_FORMULA_COMPARISON_DASHBOARD` | default-off activation flag | Phase 32.34 smoke verified `true` enables the dashboard locally while unset remains hidden. |

The dashboard does not use `pigskin_context_score`, does not query BigQuery at runtime, and does not use Sleeper current context as historical input.

Phase 32.34 smoke confirmed the dashboard source remains read-only, feature missingness remains visible, BQML outputs stay review-only, and no production ranking/champion path is exposed by the tab.

## Phase 33.2 BQML V2 Feature Contract Status

Phase 33.2 added a source-backed BQML v2 contract for the Standard-first research lane. It does not train models, write live rankings, or activate a champion.

Standard dry-run dataset:

- Version: `bqml_v2_standard_training_dataset_v0`
- Source: `ranking_backtest_feature_mart`
- Scope: `standard`, QB/RB/WR/TE, target seasons 2017-2025
- Split: train 2017-2023, validation 2024, holdout 2025
- Leakage rule: `source_window_end_season < target_season`

Feature status:

| Family | Status | Contract decision |
|---|---|---|
| Baseline Pigskin proxies | available now | Allowed when source-backed fields are present, for example `profile_points_score` and `recent_points_avg`. |
| Opportunity | available now | RB carries, targets, red-zone opportunities, goal-line opportunities, and high-value opportunity fields are allowed by position. |
| Ideal xFP | available now | `xfp_score_3yr`, `xfp_share_3yr`, and high-value xFP fields are allowed where position-specific. |
| PBP xFP | available now | Passing, rushing, and receiving xFP fields are allowed by position. |
| First-down proxies | proxy | `receiving_first_down_exp_pbp_3yr` is a chain-mover proxy. Do not call it `1D/RR`. |
| NGS | available as source-backed fields | Position-specific NGS passing, rushing, and receiving fields are allowed where present. |
| Role history | available now | Carry share, target share, WOPR, offensive snap share, and snap stability are allowed by position. |
| Injury and availability | source columns present, 0 Standard non-null rows in probe | Do not require for Standard v2. Keep as source gap until coverage exists. |
| Route metrics | blocked | Do not use YPRR, TPRR, route share, first-read share, pressure EPA, or covered-receiver EPA. |
| Historical depth | blocked | `depth_chart_role_score_3yr` had 0 non-null Standard rows in the Phase 33.2 probe and remains blocked. |
| Sleeper current context | display only | Not a historical predictor. |

Coverage summary:

| Feature family | Populated Standard rows | Possible Standard rows |
|---|---:|---:|
| Baseline | 39,033 | 39,061 |
| Opportunity | 39,061 | 39,061 |
| Ideal xFP | 38,321 | 39,061 |
| PBP xFP | 38,321 | 39,061 |
| First-down proxy | 38,321 | 39,061 |
| NGS | 32,436 | 39,061 |
| Role history | 38,650 | 39,061 |

## Phase 33.3 Standard Dataset Coverage Readiness

Phase 33.3 converted the Phase 33.2 contract into a Standard-only dataset readiness check. The training query keeps 41 predictors and excludes zero-coverage fields from the initial Standard training set.

Deferred zero-coverage fields:

| Field | Status |
|---|---|
| `passing_epa_per_play` | Future-eligible, excluded from initial Standard training query. |
| `red_zone_opportunities` | Future-eligible, excluded from initial Standard training query. |
| `goal_line_opportunities` | Future-eligible, excluded from initial Standard training query. |
| `receiving_yards` | Future-eligible, excluded from initial Standard training query. |
| `receiving_epa` | Future-eligible, excluded from initial Standard training query. |
| `red_zone_targets` | Future-eligible, excluded from initial Standard training query. |
| `ngs_catch_over_expected_score_3yr` | Future-eligible, excluded from initial Standard training query. |

Position readiness:

| Position | Predictor count | Minimum feature coverage | Readiness |
|---|---:|---:|---|
| QB | 11 | 96.3% | ready |
| RB | 19 | 62.0% | ready with warnings |
| WR | 19 | 77.0% | ready with warnings |
| TE | 23 | 71.9% | ready with warnings |

Low-coverage warnings:

| Position | Low-coverage fields |
|---|---|
| RB | `target_share_slope_3yr`, `carry_share_slope_3yr`, `ngs_box_resilience_score_3yr`, `ngs_rushing_efficiency_score_3yr`, `ngs_rush_yards_over_expected_score_3yr` |
| WR | `wopr_slope_3yr`, `target_share_slope_3yr`, `ngs_receiving_efficiency_score_3yr`, `ngs_separation_score_3yr`, `ngs_yac_over_expected_score_3yr` |
| TE | `wopr_slope_3yr`, `target_share_slope_3yr`, `ngs_receiving_efficiency_score_3yr`, `ngs_separation_score_3yr`, `ngs_yac_over_expected_score_3yr` |

Blocked fields remain blocked:

- `pigskin_context_score`
- route-derived metrics without source-backed route denominators
- historical depth
- current Sleeper context as historical predictor
- legacy `injury_risk_score_3yr` for the first Standard v2 training dataset

## Phase 33.4 nflverse Source-Gap Classification

Phase 33.4 checked only the Standard BQML v2 zero-coverage fields from Phase 33.3. No source ingest, feature-mart refresh, BQML training, or live ranking write occurred.

Warehouse and nflreadpy evidence:

| Field | Source evidence | Classification | Next action |
|---|---|---|---|
| `passing_epa_per_play` | `nflreadpy.load_player_stats` exposes `passing_epa`; `stg_play_player_events` has 242,829 passer EPA events for 2014-2025. | recoverable wiring gap | Add leakage-safe rolling QB EPA feature in a later patch. |
| `receiving_yards` | `stg_player_week_stats` and `player_week_opportunity_metrics` have populated `receiving_yards` for QB/RB/WR/TE. | recoverable wiring gap | Wire rolling receiving yards into feature mart. |
| `receiving_epa` | `nflreadpy.load_player_stats` exposes `receiving_epa`; `stg_play_player_events` has 219,876 receiver EPA events for 2014-2025. | recoverable wiring gap | Add leakage-safe rolling receiving EPA feature. |
| `red_zone_targets` | Raw and staging PBP have `yardline_100`; 29,600 target events fall at `yardline_100 <= 20`. Existing `red_zone_flag` is not populated. | recoverable from PBP yardline derivation | Derive from yardline, not from current red-zone flags. |
| `red_zone_opportunities` | Raw PBP has 29,600 red-zone targets and 28,712 red-zone rushes by yardline. Staging events have 29,600 target and 29,386 rusher events by yardline. | recoverable from PBP yardline derivation | Derive target plus rusher opportunities with source-window bounds. |
| `goal_line_opportunities` | Raw PBP has 8,916 inside-five rushes by yardline. Staging events have 9,056 inside-five rusher events by yardline. Existing inside-five flags are not populated. | recoverable from PBP yardline derivation | Derive explicitly from `yardline_100 <= 5`, then name it clearly. |
| `ngs_catch_over_expected_score_3yr` | `raw_nflverse_ngs_receiving` has `avg_expected_yac`, `avg_yac_above_expectation`, and `catch_percentage`; loaded NGS has 0 non-null expected catch and catch-over-expected rows. | unavailable in current public NGS lane | Keep deferred. Do not fabricate catch-over-expected. |

Source caution:

- `red_zone_flag` and `inside_5_flag` currently have 0 true rows in raw/staging checks. Yardline-derived logic is the recoverable path.
- Public NGS receiving in this lane supports YAC and separation style context, not expected catch or CPOE-style receiving catch-over-expected.
- These fields should remain out of the Standard training predictor set until a later additive feature-mart patch proves coverage and leakage safety.

## Phase 33.5 Standard V2 Feature Signal

Phase 33.5 trained the first Standard-only BQML v2 model set with the 41 Phase 33.3 predictors. The seven zero-coverage fields stayed excluded.

Observed model-weight signal:

| Position | Helpful or high-magnitude fields | Interpretation |
|---|---|---|
| QB | `rushing_xfp_share_pbp_3yr`, `rushing_attempts`, `qb_rushing_leverage_index`, `weekly_volatility_3yr` | QB v2 signal exists but is less stable than RB/WR/TE and trails prior BQML linear points in combined comparison. |
| RB | `target_share_slope_3yr`, `xfp_share_3yr`, `carry_share_slope_3yr` | Role and opportunity share are useful Standard RB signals. |
| WR | `target_share_slope_3yr`, `wopr_slope_3yr`, `air_yards`, `receiving_first_down_exp_pbp_3yr`, `receiving_xfp_share_pbp_3yr` | Target role, air-yard context, and chain-mover proxy are useful Standard WR signals. |
| TE | `target_share_slope_3yr`, `wopr_slope_3yr`, `air_yards`, `receiving_xfp_share_pbp_3yr`, `offensive_snap_share_3yr` | TE benefits from role-history and receiving-opportunity context. |

Deferred after training:

- `passing_epa_per_play`
- `receiving_yards`
- `receiving_epa`
- `red_zone_targets`
- `red_zone_opportunities`
- `goal_line_opportunities`
- `ngs_catch_over_expected_score_3yr`

The first six remain feature-mart patch candidates. `ngs_catch_over_expected_score_3yr` remains blocked by source availability.

## Phase 33.6 Standard Owner-Review Signal

Phase 33.6 used the Phase 33.5 Standard BQML v2 models to generate owner-review boards. The phase did not change feature definitions, train models, write live rankings, or activate a champion.

Signal interpretation by position:

| Position | Finalist | Opportunity signal status | Warning |
|---|---|---|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | Uses source-backed QB rushing and volatility terms. | QB board quality is not strong enough for activation. Prior BQML linear-points evidence remains important. |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | Uses role share, xFP, NGS rushing, and team context signals. | 2025 VOR denominator is null in the summary slice. Cutline shape needs owner review. |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` | Uses target role, WOPR, air yards, xFP, first-down proxy, and NGS receiving fields. | Keep deferred receiving yards, receiving EPA, and red-zone targets out until the feature-mart patch proves coverage. |
| TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` | Uses WR-style receiving opportunity plus snap-role context. | Linear points remains useful component evidence. Bust inverse is the Phase 33.6 review finalist, not an activated champion. |

Feature backlog after Phase 33.6:

- Add leakage-safe rolling `passing_epa_per_play`.
- Add rolling `receiving_yards` and `receiving_epa`.
- Derive red-zone targets and red-zone opportunities from `yardline_100`.
- Derive goal-line opportunities from an owner-approved yardline rule.
- Keep `ngs_catch_over_expected_score_3yr` blocked until a real source exists.

Do not fabricate route share, yards per route run, first-read share, historical depth, or current Sleeper context as historical predictors.

## Phase 33.7 EPA, Receiving, Red-Zone, and Goal-Line Patch

Phase 33.7 moved six recoverable fields from source-gap backlog into the leakage-safe feature-mart path. No model was trained and no live ranking table changed.

Patch status:

| Field | Source | Derivation policy | Status |
|---|---|---|---|
| `passing_epa_per_play` | `stg_play_player_events` | passer EPA divided by passer event count inside the historical source window | populated |
| `receiving_yards` | `stg_player_week_stats` | weekly receiving yards, clamped at zero in the feature mart | populated |
| `receiving_epa` | `stg_play_player_events` | receiver EPA by player-week inside the historical source window | populated |
| `red_zone_targets` | `stg_play_player_events` | target events where `yardline_100 <= 20` | populated |
| `red_zone_opportunities` | `stg_play_player_events` | target plus rusher events where `yardline_100 <= 20` | populated |
| `goal_line_opportunities` | `stg_play_player_events` | target plus rusher events where `yardline_100 <= 5` | populated |

Source-policy notes:

- Red-zone and goal-line derivations use `yardline_100`.
- `red_zone_flag` and `inside_5_flag` remain unusable for this patch because prior checks showed zero true rows.
- `ngs_catch_over_expected_score_3yr` remains blocked. Do not fabricate it from YAC or catch-percentage fields.

Refresh scope:

- Feature mart: `ranking_backtest_feature_mart`.
- Target seasons: 2017-2025.
- Source windows: rolling historical windows ending before the target season.
- Scoring profiles: `standard`, `half_ppr`, `ppr`, `gng_keeper`.
- Positions: QB, RB, WR, TE.
- Total refreshed rows: 156,244.

Range and leakage checks:

- `source_window_end_season >= target_season`: 0 rows.
- `target_season = 2026`: 0 rows.
- Negative `receiving_yards`, red-zone, and goal-line counts: 0 rows after the receiving-yard clamp.
- Extreme red-zone and goal-line count checks: 0 rows.

The patched fields are now eligible for Standard BQML v2 retraining in a separate phase.

## Phase 33.8 Patched Model Signal

Phase 33.8 proved the newly patched fields are visible to Standard BQML v2 training, but the model results are mixed.

Observed patched-field signal:

| Position | Model inspected | High-magnitude patched or opportunity fields |
|---|---|---|
| QB | `ranking_bqml_v2_standard_patched_qb_linear_points_v0` | `passing_epa_per_play`, `rushing_xfp_pbp_3yr`, `rushing_xfp_share_pbp_3yr` |
| RB | `ranking_bqml_v2_standard_patched_rb_logistic_elite_v0` | `target_share_slope_3yr`, `xfp_share_3yr`, `carry_share_slope_3yr`, `red_zone_opportunities`, `receiving_xfp_pbp_3yr` |
| WR | `ranking_bqml_v2_standard_patched_wr_logistic_bust_v0` | `target_share_slope_3yr`, `wopr_slope_3yr`, `xfp_share_3yr`, `receiving_xfp_share_pbp_3yr`, `air_yards`, `receiving_epa` |
| TE | `ranking_bqml_v2_standard_patched_te_logistic_bust_v0` | `target_share_slope_3yr`, `xfp_share_3yr`, `wopr_slope_3yr`, `air_yards`, `receiving_xfp_share_pbp_3yr`, `receiving_epa` |

Interpretation:

- RB and TE show the clearest owner-review value from the patched opportunity fields.
- WR has useful patched evidence, but original Standard v2 still wins some rank-quality metrics.
- QB remains noisy. `passing_epa_per_play` is active but not enough to displace the original QB Standard v2 lane.
- `ngs_catch_over_expected_score_3yr` remains blocked. Do not fabricate it from catch percentage, YAC, or separation fields.

Next action: generate patched Standard owner-review boards only if the owner wants to inspect these challengers. Do not activate a patched champion from summary evidence alone.

## Phase 33.9 Patched Feature Impact

Phase 33.9 compared original and patched Standard BQML v2 boards. The patched fields helped selected component lanes, but did not produce a clean replacement.

Impact by position:

| Position | Patched fields that showed signal | Owner-review read |
|---|---|---|
| QB | `passing_epa_per_play` appeared in patched QB weights. | Helpful context, but QB remains noisy. Keep original QB finalist. |
| RB | `red_zone_opportunities` and `receiving_xfp_pbp_3yr` appeared in patched RB logistic elite weights. | Useful RB component signal. Keep original RB finalist until overall-board rule review. |
| WR | `receiving_epa` appeared in patched WR bust weights beside target-share, WOPR, xFP share, and air yards. | Useful 2025 points/VOR signal, but movement risk remains. |
| TE | `receiving_epa` appeared in patched TE bust weights beside target-share, WOPR, xFP share, and air yards. | Useful 2025 TE signal, but 2024 still keeps original TE evidence important. |

Still blocked:

- `ngs_catch_over_expected_score_3yr`
- true route share
- YPRR
- TPRR
- first-read share
- pressure EPA
- covered-receiver EPA
- historical depth
- `pigskin_context_score`
- Sleeper current context as a historical predictor

Policy: patched fields may support explainability and component review. They do not activate a champion.
