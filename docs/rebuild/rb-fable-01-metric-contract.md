# RB Fable 01 Metric Contract

## Purpose

RB Fable 01 predicts next-season Standard-scoring RB fantasy points per game from prior-season source-backed data. It is a research formula. It does not write rankings or activate a champion.

## Formula

```text
RB_SCORE =
  0.30 * z(non_garbage_time_touches_per_game)
  + 0.13 * z(red_zone_touches_per_game)
  + 0.12 * z(target_share)
  + 0.08 * z(yac_per_rush) * rushing_efficiency_shrink
  + 0.06 * z(success_pct) * rushing_efficiency_shrink
  + 0.05 * z(epa_per_touch) * touch_efficiency_shrink
  + 0.04 * z(explosive_pct) * rushing_efficiency_shrink
  + 0.04 * z(box_adjusted_ypc) * box_efficiency_shrink
  + 0.10 * z(blended_td_per_game)
  + 0.05 * z(age_penalty) * (1 - 0.6 * clamp((z(non_garbage_time_touches_per_game) - 0.75) / 0.75, 0, 1))
  + 0.03 * z(games_played_rate)
```

Phase 34.4 elite-volume protection: the age term is forgiven linearly up to 60% as prior-season non-garbage-time volume rises from z = 0.75 to z = 1.5. Workhorse veterans (Derrick Henry) keep most of their score; moderate-volume veterans (Raheem Mostert) stay fully penalized. All other weights are unchanged from the Phase 34.2B definition.

`blended_td_per_game = 0.7 * expected_td_per_game + 0.3 * actual_td_per_game`.

`expected_td_per_game = 0.16 * red_zone_rushes_per_game + 0.10 * red_zone_receptions_per_game`.

## Source Metrics

Primary situational source: `fantasy_football_advanced_metrics.rb_situational_metrics`.

| Context | Fields |
|---|---|
| Standard | Rushes, receptions, rush/receiving TDs, yards per carry, total EPA, success percentage, explosive percentage, target share, average box defenders, yards after contact. |
| Non-garbage time | Rushes and receptions. |
| Red zone | Rushes and receptions. |
| Eight-plus box defenders | Rushes and yards per carry. |
| Identity/basic context | `player_identity_bridge`, `stg_player_identity`, and regular-season `player_season_advanced_metrics`. |
| Target | `analytics_player_fantasy_points_by_profile`, Standard profile, weeks 1-18. |

Goal-line carries are source-backed in the existing season advanced metrics lane, but RB Fable 01 currently uses the documented red-zone approximation. Goal-line data is not silently substituted into the formula.

## Derived Metrics

- `standard_touches = standard_rushes + standard_receptions`
- `non_garbage_time_touches = non_garbage_time_rushes + non_garbage_time_receptions`
- `red_zone_touches = red_zone_rushes + red_zone_receptions`
- per-game touch metrics divide by regular-season games played
- `yac_per_rush = yards_after_contact / standard_rushes`
- `epa_per_touch = total_epa / standard_touches`
- `actual_td = standard_rush_td + standard_receiving_td`
- `age_penalty = -max(0, age - 25)`
- `games_played_rate = games_played / 17`

Box-adjusted YPC uses the eight-plus-box split when at least 20 carries are present. Otherwise it uses the within-season residual of Standard YPC against average box defenders. The residual is source-backed and fitted within the input season only.

## Preprocessing

- Qualification: at least 6 regular-season games or 50 Standard touches.
- Every z-score is computed within one input season. Seasons are never pooled for normalization.
- Rushing efficiency shrinkage: `standard_rushes / (standard_rushes + 125)`.
- EPA-per-touch shrinkage: `standard_touches / (standard_touches + 125)`.
- Box-adjusted YPC shrinkage uses stacked-box carries when that split qualifies, otherwise Standard rushes.
- Missing source metrics remain null. They are not converted to zero merely to complete a score.

## Identity And Eligibility

Eligible statuses are `VERIFIED`, `EXACT_SLUG_MATCH`, or a high-confidence `NAME_TEAM_SEASON_MATCH`. Ambiguous, colliding, and unmapped identities fail closed. Target Standard points must exist for the next season. The target season must have at least six weekly point records.

## Backtest Folds

| Input | Target |
|---:|---:|
| 2022 | 2023 |
| 2023 | 2024 |
| 2024 | 2025 |

No 2025 input predicts 2025. No 2026 outcome is permitted.

## Blocked Inputs

The formula must not use broken tackles, YAC above expectation, market value, subjective rankings, Current Pigskin score as an input, route share, YPRR, or any fabricated proxy. Current Pigskin is comparison evidence only when a valid historical baseline exists.

