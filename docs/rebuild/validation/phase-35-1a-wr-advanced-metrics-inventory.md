# Phase 35.1A WR Advanced Metrics Inventory

## 1. Final Decision

`WR FABLE V1 NEEDS FALLBACKS`

Every requested WR Fable v1 input is available directly or through an exact, source-backed derivation — with one exception. **End-zone targets do not exist anywhere in the warehouse** (the `player_week_advanced_metrics.end_zone_targets` column exists but is 0% populated for 2022-2025). An exact build of the specified formula is blocked by that single input; a red-zone-based expected-TD proxy is a viable, clearly-labeled fallback that requires an owner decision. Nothing was built, backtested, promoted, trained, or written in this phase; all queries were read-only.

## 2. WR Refinements Available (2022-2025)

All eight expected refinements exist in `wr_situational_metrics`, each covering all four seasons:

| Refinement | Rows | Seasons |
|---|---:|---|
| standard | 842 | 2022-2025 |
| non_garbage_time | 828 | 2022-2025 |
| vs_zone | 817 | 2022-2025 |
| when_trailing | 788 | 2022-2025 |
| late_down | 740 | 2022-2025 |
| vs_man | 710 | 2022-2025 |
| when_leading | 709 | 2022-2025 |
| red_zone | 597 | 2022-2025 |

Row-count differences between refinements reflect real usage (not every WR has qualifying red-zone or vs-man snaps), not import gaps.

## 3. WR Metric Inventory — `wr_situational_metrics` / `v_wr_standard_situational`

All eleven governed metrics are `SOURCE_BACKED`, FLOAT64, available in every refinement, and **100% non-null in every season 2022-2025** (verified via `situational_metric_coverage`, standard refinement shown; all 2,472 position-season-refinement-metric coverage rows were generated at import).

| Column | Raw JSON key | Group | Unit | Higher better | Class |
|---|---|---|---|---|---|
| adot | ADoT | role | yards | yes (depth context) | role |
| catch_pct | Catch % | efficiency | percent | yes | efficiency |
| receiving_yards | Rec. Yards | volume | yards | yes | volume |
| receptions | Receptions | volume | count | yes | volume |
| routes_run | Routes Run | role | count | yes | role/route |
| target_share | Target Share | opportunity | percent | yes | opportunity |
| targets_per_route_run | Targets/Route Run | route | ratio | yes | route/opportunity |
| total_epa | Total EPA | efficiency | epa | yes | efficiency |
| touchdowns | Touchdowns | volume | count | yes | scoring |
| yac | YAC | volume | yards | yes | volume/efficiency |
| yprr | YPRR | route | yards/route | yes | route/efficiency |

Supporting brain-dataset sources inspected (WR-relevant only):

| Source | Fields | 2022-2025 coverage |
|---|---|---|
| `raw_nflverse_weekly` | targets, receptions, receiving_yards, receiving_tds | targets 10,242/10,242 WR rows (100%); **air_yards column exists but is 0% populated** |
| `player_week_advanced_metrics` | targets, target_share, air_yards_share, wopr, red_zone_targets, end_zone_targets, goal_line_targets, receiving_air_yards, receiving_epa_per_target | targets 100%; air_yards_share and wopr ~93% of weekly rows; red_zone_targets ~59% (null vs zero ambiguity, see section 7); **end_zone_targets 0% in all four seasons**; receiving_air_yards ~33% |
| `player_week_opportunity_metrics` | red_zone_targets, team_pass_attempts, team_targets, target_share | team_pass_attempts 100%; red_zone_targets 88% |
| `dim_players_current` | birth_date, age | identity layer already used by RB Fable |
| `analytics_player_fantasy_points_by_profile` | Standard fantasy points, weekly rows for games played | used by RB Fable, weeks 1-18, seasons through 2025 |
| `stg_team_week_stats` / `team_week_context_metrics` | pass_attempts, neutral_pass_rate, team_targets | team pass volume available |

## 4. WR Fable v1 Input Availability

| Input | Status | Source / derivation |
|---|---|---|
| **Opportunity** | | |
| Target share | AVAILABLE_DIRECTLY | `wr_situational_metrics.target_share` (100%) |
| Air yards share | AVAILABLE_FROM_OTHER_TABLE | `player_week_advanced_metrics.air_yards_share` (~93% weekly; season aggregate from air yards sums) |
| WOPR | AVAILABLE_FROM_OTHER_TABLE / AVAILABLE_DERIVED | direct `wopr` column, or `1.5 * target_share + 0.7 * air_yards_share` |
| Non-garbage-time targets per game | AVAILABLE_DERIVED | `routes_run(non_garbage_time) * targets_per_route_run(non_garbage_time) / games` — both factors 100% in the situational source |
| Red-zone targets per game | AVAILABLE_DERIVED | `routes_run(red_zone) * targets_per_route_run(red_zone) / games` (situational, 100% where the split exists); brain `red_zone_targets` as cross-check |
| End-zone targets per game | **MISSING** | no populated source anywhere; column exists empty |
| **Efficiency** | | |
| Routes run | AVAILABLE_DIRECTLY | situational, 100% |
| YPRR | AVAILABLE_DIRECTLY | situational, 100% |
| Targets per route run | AVAILABLE_DIRECTLY | situational, 100% |
| Targets | AVAILABLE_FROM_OTHER_TABLE (raw) / AVAILABLE_DERIVED (situational splits) | raw: `raw_nflverse_weekly.targets` (100%); per-refinement: `routes_run * targets_per_route_run` |
| Receiving yards | AVAILABLE_DIRECTLY | situational, 100% |
| Yards per target | AVAILABLE_DERIVED | `receiving_yards / targets` |
| EPA | AVAILABLE_DIRECTLY | situational `total_epa`, 100% |
| EPA per target | AVAILABLE_DERIVED / AVAILABLE_FROM_OTHER_TABLE | `total_epa / targets`; brain `receiving_epa_per_target` as cross-check |
| YAC | AVAILABLE_DIRECTLY | situational, 100% |
| YAC per reception | AVAILABLE_DERIVED | `yac / receptions` |
| aDOT | AVAILABLE_DIRECTLY | situational, 100% |
| Catch percentage | AVAILABLE_DIRECTLY | situational, 100% |
| aDOT-adjusted catch rate | AVAILABLE_DERIVED | residual of `catch_pct` regressed on `adot` within the WR season pool (both inputs 100%) |
| **Scoring** | | |
| Receiving TDs | AVAILABLE_DIRECTLY | situational `touchdowns` (standard refinement); `raw_nflverse_weekly.receiving_tds` cross-check |
| Red-zone TD context | AVAILABLE_DIRECTLY | situational `touchdowns` under the `red_zone` refinement |
| End-zone TD context | **MISSING** | depends on end-zone targets |
| Expected TD proxy inputs | NEEDS_OWNER_DECISION | exact spec needs end-zone targets; red-zone-only proxy is buildable (see section 6) |
| Blended TD inputs | AVAILABLE_DERIVED (with the above fallback decision) | actual TD/gm available; expected side pending owner decision |
| **Age / availability** | | |
| Age / birth date | AVAILABLE_FROM_OTHER_TABLE | `dim_players_current.birth_date` (same layer RB Fable uses) |
| Games played | AVAILABLE_FROM_OTHER_TABLE | weekly rows in `analytics_player_fantasy_points_by_profile` (RB Fable pattern) |
| Breakout-window flag (age 22-25) | AVAILABLE_DERIVED | boolean from age |
| Decline penalty input (age > 29) | AVAILABLE_DERIVED | from age, same construction as RB age penalty |

## 5. Missing Metrics

- **End-zone targets** — the only true gap. `player_week_advanced_metrics.end_zone_targets` is defined but 0% populated for 2022-2025; no other table carries it. Not fabricatable.
- **Raw air yards in `raw_nflverse_weekly`** — column empty; air-yards needs come from `player_week_advanced_metrics` (air_yards_share, receiving_air_yards) instead.
- Everything else on the WR Fable v1 list is present or exactly derivable.

## 6. Derived Metrics Allowed (exact derivations)

- `targets_split = routes_run(split) * targets_per_route_run(split)` — per refinement, both factors source-backed; raw season targets preferred from `raw_nflverse_weekly` where the standard split is needed.
- `epa_per_target = total_epa / targets` (guard: targets >= 1).
- `yards_per_target = receiving_yards / targets`.
- `yac_per_reception = yac / receptions` (guard: receptions >= 1).
- `wopr = 1.5 * target_share + 0.7 * air_yards_share` (or use the stored `wopr` column; pick one and record it).
- `adot_adjusted_catch_rate` = residual from `catch_pct ~ adot` fit within each WR season pool (mirrors the RB box-adjusted-YPC residual method).
- `non_garbage_time_targets_per_game = targets(non_garbage_time) / games_played`.
- `red_zone_targets_per_game = targets(red_zone) / games_played`.
- `breakout_window = age BETWEEN 22 AND 25`; `decline_input = GREATEST(0, age - 29)` (final shape is a formula-phase decision).

## 7. Metrics Requiring Owner Decision

1. **Expected-TD proxy without end-zone targets.** The RB pattern (`0.16 * rz_rushes/gm + 0.10 * rz_receptions/gm`) suggests a WR analog built from red-zone targets/receptions only. Per the rules, red-zone targets are NOT being treated as end-zone targets — adopting a red-zone-only proxy must be an explicit, labeled owner-approved fallback.
2. **Brain red-zone target nulls.** `player_week_advanced_metrics.red_zone_targets` is null on ~41% of weekly rows with no way to distinguish "zero" from "not tracked." The situational `red_zone` refinement derivation avoids this entirely and is the recommended source; if the brain column is used anyway, the null policy needs an owner ruling (no silent zero-fill).
3. **WOPR source choice.** Stored `wopr` vs derived from shares — results differ slightly at season aggregation; one must be canonized.

## 8. Recommendation

WR Fable v1 **cannot be built exactly as specified** — end-zone targets and everything downstream of them (end-zone TD context, the exact expected-TD blend) are missing from all sources. It **can be built completely and honestly** with one owner-approved fallback: a red-zone-only expected-TD proxy, clearly labeled as such. All other 20+ inputs are available at 100% (situational) or high (brain weekly) coverage across 2022-2025, including the full route triad (routes, YPRR, TPRR), raw targets, air-yards share/WOPR, EPA per target, and the aDOT-adjusted catch rate derivation. Identity will need the same slug-bridge treatment the RB build used; `situational_player_identity_candidates` remains the safe path.

Recommended next phase: owner ruling on the expected-TD fallback (section 7), then Phase 35.1B metric contract for WR Fable v1 mirroring `rb-fable-01-metric-contract.md`.

## Safety Confirmation

- Read-only phase: no table, view, formula, ranking, champion, or model was created or changed.
- No Gemini or Pigskin chat call. No 2026 outcomes touched. No market data. No fabricated route, target, air-yard, or end-zone data. No silent zero-fills — null ambiguities are flagged above instead.
