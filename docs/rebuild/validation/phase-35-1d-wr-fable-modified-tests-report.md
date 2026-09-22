# Phase 35.1D WR Fable Modified-Formula Tests

## Final Recommendation

`WR FABLE NEEDS ONE FINAL TWEAK`

Keep WR Fable v1 as the live baseline. I4 is the best tested injury candidate, but it misses the top-12 precision guardrail: 0.611 versus 0.639, a decline of 0.0278. Its other results are useful. Coverage rises from 320 to 328 complete fold rows, top-6 precision improves, points@12 improves, regret falls, and neither elite misses nor top-12 busts increase.

The next narrow test should preserve the exact v1 score for every v1-qualified season. Apply I4 and the rookie rule only to players v1 would otherwise exclude. Reject all three environment modifiers as score inputs. Keep environment delta as review context.

## Baseline Reproduction

The existing WR Fable v1 baseline reproduced exactly. The runner stops on any baseline mismatch.

| Formula | Complete | Spearman | Score corr. | Top 6 | Top 12 | Top 24 | Pts@12 | Pts@24 | NDCG@12 | NDCG@24 | Pairwise | Regret | Misses | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| WR Fable v1 | 320 | 0.7383 | 0.7460 | 0.2778 | 0.6389 | 0.6250 | 0.9172 | 0.8928 | 0.8437 | 0.8494 | 0.7686 | 0.2659 | 8 | 2 |

## Injury Threshold Comparison

The three candidates use unchanged v1 weights and v1 reference distributions. Healthy seasons receive zero prior-performance weight. Availability remains a separate two-year component.

| Variant | Complete | Spearman | Score corr. | Top 6 | Top 12 | Top 24 | Pts@12 | Pts@24 | NDCG@12 | NDCG@24 | Pairwise | Regret | Misses | Busts | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| I4 | 328 | 0.7396 | 0.7481 | 0.3333 | 0.6111 | 0.6250 | 0.9216 | 0.8929 | 0.8423 | 0.8509 | 0.7695 | 0.2568 | 8 | 2 | Best tested; top-12 guardrail failed |
| I7 | 328 | 0.7394 | 0.7478 | 0.2778 | 0.6111 | 0.6250 | 0.9216 | 0.8929 | 0.8412 | 0.8500 | 0.7693 | 0.2599 | 8 | 2 | Top-12 guardrail failed |
| I10 | 328 | 0.7384 | 0.7458 | 0.2778 | 0.6111 | 0.6250 | 0.9216 | 0.8929 | 0.8404 | 0.8495 | 0.7690 | 0.2599 | 8 | 2 | Top-12 guardrail failed |

All three pass the points@12, NDCG@24, pairwise, elite-miss, bust, and coverage checks. All fail only the maximum 0.01 top-12 precision decline.

I4 complete-row coverage by fold:

| Fold | Baseline | I4 | Added players | Blended players |
|---|---:|---:|---|---:|
| 2022 to 2023 | 109 | 112 | Brandon Johnson, Jalen Tolbert, Samori Toure | 0 |
| 2023 to 2024 | 107 | 107 | None | 17 |
| 2024 to 2025 | 104 | 109 | Britain Covey, Deven Thompkins, Malik Heath, Rashee Rice, Tyquan Thornton | 20 |

## Rookie And No-Prior Handling

Rookie status uses `dim_players_current.rookie_year`, with first observed WR season from `stg_player_week_stats` as a source-backed fallback. That history spans 2014-2025. No college value or invented prior season is used.

- Shortened rookies can now score when required rate metrics exist. Bub Means produced a complete score from four games and 92 routes with zero prior weight and `ROOKIE_LIMITED_SAMPLE`.
- Brandon Johnson, Jalen Tolbert, and Samori Toure add complete 2022 fold rows. Their prior weight is zero.
- A shortened rookie with missing rate inputs remains incomplete. The layer does not fill missing rates with zero or league-average performance.
- Tetairoa McMillan and Emeka Egbuka are flagged on the current board. Their efficiency shrinkage uses `routes / (routes + 90)` and `targets / (targets + 90)`.

## Team Environment Comparison

The revised environment score weights QB passing EPA at 0.45 and team passing EPA at 0.25. Pass attempts, points, and win percentage carry the remaining weight. Only known team changes receive a continuous, capped adjustment.

| Formula | Complete | Spearman | Score corr. | Top 6 | Top 12 | Top 24 | Pts@12 | NDCG@24 | Pairwise | Regret | Material movers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| I4, no environment | 328 | 0.7396 | 0.7481 | 0.3333 | 0.6111 | 0.6250 | 0.9216 | 0.8509 | 0.7695 | 0.2568 | 0 |
| I4 + E15 | 328 | 0.7378 | 0.7479 | 0.3333 | 0.6111 | 0.6250 | 0.9216 | 0.8509 | 0.7685 | 0.2568 | 2 |
| I4 + E25 | 328 | 0.7369 | 0.7476 | 0.3333 | 0.6111 | 0.6250 | 0.9216 | 0.8509 | 0.7683 | 0.2599 | 7 |
| I4 + E40 | 328 | 0.7360 | 0.7472 | 0.3333 | 0.6111 | 0.6250 | 0.9216 | 0.8509 | 0.7677 | 0.2599 | 17 |

E15 is the least harmful environment variant. It still lowers correlation and pairwise ordering. E25 and E40 create more movement without selection lift.

## Team-Changing Movement Audit

Every move of at least three ranks or across a top-12/top-24 boundary is included. No mover crossed the top-12 or top-24 boundary.

| Variant | Fold | Player | Teams | Source/Dest env. | Delta | Adjustment | Rank | Actual finish | Effect |
|---|---|---|---|---|---:|---:|---:|---:|---|
| E15 | 2022 to 2023 | Noah Brown | DAL to HOU | 0.452 / -1.323 | -1.775 | -0.0225 | 62 to 66 | 48 | Hurt |
| E15 | 2024 to 2025 | Lil'Jordan Humphrey | DEN to NYG | 0.104 / -1.085 | -1.189 | -0.0178 | 94 to 97 | 98 | Hurt |
| E25 | 2022 to 2023 | D.J. Chark | DET to CAR | 1.221 / -0.837 | -2.058 | -0.0375 | 61 to 64 | 56 | Hurt |
| E25 | 2022 to 2023 | Noah Brown | DAL to HOU | 0.452 / -1.323 | -1.775 | -0.0375 | 62 to 68 | 48 | Hurt |
| E25 | 2022 to 2023 | Richie James | NYG to KC | -0.068 / 2.058 | 2.126 | 0.0375 | 66 to 63 | 149 | Hurt |
| E25 | 2024 to 2025 | Adam Thielen | CAR to MIN | -0.869 / 0.358 | 1.227 | 0.0307 | 38 to 34 | 144 | Hurt |
| E25 | 2024 to 2025 | Nick Westbrook-Ikhine | TEN to MIA | -1.051 / 0.206 | 1.257 | 0.0314 | 66 to 63 | 163 | Hurt |
| E25 | 2024 to 2025 | Olamide Zaccheaus | WAS to CHI | 0.627 / -0.729 | -1.357 | -0.0339 | 74 to 77 | 93 | Hurt |
| E25 | 2024 to 2025 | Lil'Jordan Humphrey | DEN to NYG | 0.104 / -1.085 | -1.189 | -0.0297 | 94 to 97 | 98 | Hurt |
| E40 | 2022 to 2023 | Mack Hollins | LV to ATL | 0.152 / -0.449 | -0.601 | -0.0241 | 50 to 53 | 125 | Helped |
| E40 | 2022 to 2023 | D.J. Chark | DET to CAR | 1.221 / -0.837 | -2.058 | -0.0600 | 61 to 66 | 56 | Hurt |
| E40 | 2022 to 2023 | Noah Brown | DAL to HOU | 0.452 / -1.323 | -1.775 | -0.0600 | 62 to 70 | 48 | Hurt |
| E40 | 2022 to 2023 | Richie James | NYG to KC | -0.068 / 2.058 | 2.126 | 0.0600 | 66 to 61 | 149 | Hurt |
| E40 | 2022 to 2023 | Demarcus Robinson | BAL to LAR | -0.500 / -0.914 | -0.414 | -0.0166 | 69 to 72 | 38 | Hurt |
| E40 | 2022 to 2023 | Chris Moore | HOU to TEN | -1.323 / -0.665 | 0.658 | 0.0263 | 71 to 67 | 96 | Hurt |
| E40 | 2022 to 2023 | Isaiah McKenzie | BUF to IND | 1.264 / -1.154 | -2.417 | -0.0600 | 75 to 78 | 165 | Helped |
| E40 | 2023 to 2024 | Mack Hollins | ATL to BUF | -0.595 / 0.876 | 1.471 | 0.0589 | 83 to 80 | 89 | Helped |
| E40 | 2023 to 2024 | Cedrick Wilson | MIA to NO | 1.141 / 0.418 | -0.723 | -0.0289 | 88 to 92 | 112 | Hurt |
| E40 | 2023 to 2024 | Allen Robinson | PIT to DET | -0.722 / 0.972 | 1.694 | 0.0600 | 94 to 88 | 156 | Hurt |
| E40 | 2024 to 2025 | Adam Thielen | CAR to MIN | -0.869 / 0.358 | 1.227 | 0.0491 | 38 to 34 | 144 | Hurt |
| E40 | 2024 to 2025 | Gabe Davis | JAX to BUF | -0.435 / 1.251 | 1.686 | 0.0600 | 59 to 56 | 96 | Hurt |
| E40 | 2024 to 2025 | Nick Westbrook-Ikhine | TEN to MIA | -1.051 / 0.206 | 1.257 | 0.0503 | 66 to 62 | 163 | Hurt |
| E40 | 2024 to 2025 | Olamide Zaccheaus | WAS to CHI | 0.627 / -0.729 | -1.357 | -0.0543 | 74 to 77 | 93 | Hurt |
| E40 | 2024 to 2025 | Marquez Valdes-Scantling | NO to SF | -0.844 / 0.317 | 1.161 | 0.0465 | 82 to 79 | 128 | Hurt |
| E40 | 2024 to 2025 | Mack Hollins | BUF to NE | 1.251 / -0.939 | -2.189 | -0.0600 | 86 to 89 | 63 | Hurt |
| E40 | 2024 to 2025 | Lil'Jordan Humphrey | DEN to NYG | 0.104 / -1.085 | -1.189 | -0.0476 | 94 to 98 | 98 | Hurt |

Named historical checks:

- Keenan Allen changed LAC to CHI for the 2024 target. Delta was -0.887; E15/E25/E40 adjustments were -0.0133/-0.0222/-0.0355. His rank stayed 6 while his actual finish was WR42. For the 2025 target, CHI to LAC produced +1.014 and moved him from 29 to 28/27/27 against an actual WR48 finish. The positive movement hurt.
- Deebo Samuel changed SF to WAS for the 2025 target. Delta was +0.310; adjustments were +0.0047/+0.0078/+0.0124. Rank stayed 48 against an actual WR32 finish.
- A.J. Brown, Mike Evans, Tee Higgins, Chris Godwin, Terry McLaurin, Nico Collins, Chris Olave, and Christian Watson did not change teams in the tested historical fold where each row appeared. Their modifier was zero. No named historical miss was fixed.

## Malik Nabers Audit

- Latest season: 4 games, 136 routes, 35 targets. WOPR 0.6104, non-garbage targets/game 8.84, red-zone targets/game 0.9975, YPRR 1.99, EPA/target 0.5926.
- Prior season: WOPR 0.6867, non-garbage targets/game 10.3953, red-zone targets/game 0.9893, YPRR 2.17, EPA/target 0.6169.
- I4 uses exactly 40% prior data and 60% latest data. Modified WOPR is 0.6409, YPRR 2.062, EPA/target 0.6023.
- Games-played rates remain separate: latest 0.2353, prior 0.8824, two-year availability 0.4294. The availability component is +0.0027.
- I4 score is 1.3003 and current rank is WR8. No environment adjustment applies because he remains with NYG.

## A.J. Brown Audit

- Current I4 score with no environment adjustment: 1.0105, WR17.
- Source PHI environment: 0.0035. Destination NE environment: 1.5405. Delta: +1.5370.
- E15 adds +0.0225 for a 1.0330 score and WR16.
- E25 adds +0.0375 for a 1.0480 score and WR16.
- E40 adds +0.0600 for a 1.0705 score and WR16.
- Sleeper reports NE and depth order 1. Depth is display-only. No alpha-role points enter any score.

## Current Top-40 Comparison

This is the union of the v1, I4, and I4+E15 top-40 boards, so 42 players appear. `Avail` is the formula component, not games played. Current status and depth are display fields only.

| Player | Old | I4 | E15 | Std | GP | Routes | Prior | Prior wt. | Rookie | Avail | Teams | Delta | Adj. | Status | Depth | Reason |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---|---:|---:|---|---:|---|
| Amon-Ra St. Brown | 1 | 1 | 1 | 3 | 17 | 567 | Y | 0% | N | 0.082 | DET to DET | 0.00 | 0.0000 | Active | 1 | Baseline rates |
| Jaxon Smith-Njigba | 2 | 2 | 2 | 1 | 17 | 497 | Y | 0% | N | 0.082 | SEA to SEA | 0.00 | 0.0000 | Active | 1 | Baseline rates |
| Puka Nacua | 3 | 3 | 3 | 2 | 16 | 463 | Y | 0% | N | 0.062 | LAR to LAR | 0.00 | 0.0000 | Active | 1 | Baseline rates |
| Ja'Marr Chase | 5 | 4 | 4 | 4 | 16 | 634 | Y | 0% | N | 0.076 | CIN to CIN | 0.00 | 0.0000 | Active | 1 | Baseline rates |
| Rashee Rice | 4 | 5 | 5 | 8 | 8 | 266 | Y | 0% | N | -0.001 | KC to KC | 0.00 | 0.0000 | Active/Questionable | 1 | Required prior rate missing; no blend |
| Davante Adams | 6 | 6 | 6 | 13 | 14 | 409 | Y | 0% | N | -0.080 | LAR to LAR | 0.00 | 0.0000 | Active | 2 | Baseline rates |
| Drake London | 7 | 7 | 7 | 5 | 12 | 396 | Y | 15% | N | 0.053 | ATL to ATL | 0.00 | 0.0000 | Active/Questionable | 1 | 15% prior blend |
| Malik Nabers | - | 8 | 8 | 18 | 4 | 136 | Y | 40% | N | 0.003 | NYG to NYG | 0.00 | 0.0000 | Active/Questionable | 1 | 40% prior blend |
| Chris Olave | 8 | 9 | 9 | 6 | 16 | 586 | Y | 0% | N | 0.054 | NO to NO | 0.00 | 0.0000 | Active | 1 | Baseline rates |
| George Pickens | 9 | 10 | 10 | 11 | 17 | 610 | Y | 0% | N | 0.075 | DAL to DAL | 0.00 | 0.0000 | Active | 2 | Baseline rates |
| CeeDee Lamb | 11 | 11 | 11 | 14 | 13 | 454 | Y | 0% | N | -0.026 | DAL to DAL | 0.00 | 0.0000 | Active | 1 | Baseline rates |
| Nico Collins | 10 | 12 | 12 | 15 | 15 | 483 | Y | 0% | N | -0.022 | HOU to HOU | 0.00 | 0.0000 | Active | 1 | Baseline rates |
| Garrett Wilson | 14 | 13 | 13 | 10 | 7 | 228 | Y | 30% | N | 0.025 | NYJ to NYJ | 0.00 | 0.0000 | Active | 1 | 30% prior blend |
| Zay Flowers | 12 | 14 | 14 | 12 | 17 | 480 | Y | 0% | N | 0.082 | BAL to BAL | 0.00 | 0.0000 | Active | 1 | Baseline rates |
| Justin Jefferson | 13 | 15 | 15 | 9 | 17 | 558 | Y | 0% | N | 0.002 | MIN to MIN | 0.00 | 0.0000 | Active | 1 | Baseline rates |
| A.J. Brown | 15 | 17 | 16 | 7 | 15 | 484 | Y | 0% | N | -0.019 | PHI to NE | 1.54 | 0.0225 | Active | 1 | Environment review |
| Wan'Dale Robinson | 16 | 16 | 17 | 17 | 16 | 543 | Y | 0% | N | 0.076 | NYG to TEN | -1.13 | -0.0170 | Active | 2 | Environment review |
| Tetairoa McMillan | 17 | 18 | 18 | 16 | 17 | 553 | N | 0% | Y | 0.082 | CAR to CAR | 0.00 | 0.0000 | Active/Questionable | 1 | ROOKIE_LIMITED_SAMPLE |
| DK Metcalf | 19 | 19 | 19 | 34 | 15 | 429 | Y | 0% | N | -0.015 | PIT to PIT | 0.00 | 0.0000 | Active | 1 | Baseline rates |
| Rome Odunze | 18 | 20 | 20 | 19 | 12 | 415 | Y | 15% | N | 0.053 | CHI to CHI | 0.00 | 0.0000 | Active | 1 | 15% prior blend |
| Emeka Egbuka | 20 | 21 | 21 | 26 | 17 | 540 | N | 0% | Y | 0.082 | TB to TB | 0.00 | 0.0000 | Active | 1 | ROOKIE_LIMITED_SAMPLE |
| Courtland Sutton | 21 | 22 | 22 | 25 | 17 | 633 | Y | 0% | N | -0.001 | DEN to DEN | 0.00 | 0.0000 | Active | 2 | Baseline rates |
| Mike Evans | 29 | 23 | 23 | 29 | 8 | 228 | Y | 30% | N | -0.114 | TB to SF | 1.12 | 0.0168 | Active | 1 | 30% prior blend; environment review |
| Terry McLaurin | 25 | 24 | 24 | 21 | 10 | 264 | Y | 15% | N | -0.038 | WAS to WAS | 0.00 | 0.0000 | Active | 1 | 15% prior blend |
| Jaylen Waddle | 22 | 25 | 25 | 22 | 16 | 417 | Y | 0% | N | -0.009 | MIA to DEN | 1.01 | 0.0152 | Active | 1 | Environment review |
| Tyreek Hill | - | 26 | 26 | - | 4 | 105 | Y | 40% | N | -0.111 | MIA to unknown | - | 0.0000 | Active/Questionable | - | 40% prior blend |
| Quentin Johnston | 24 | 27 | 27 | 30 | 13 | 487 | Y | 0% | N | 0.054 | LAC to LAC | 0.00 | 0.0000 | Active | 2 | Baseline rates |
| Michael Wilson | 23 | 28 | 28 | 31 | 17 | 632 | Y | 0% | N | 0.079 | ARI to ARI | 0.00 | 0.0000 | Active | 2 | Baseline rates |
| Tee Higgins | 26 | 29 | 29 | 24 | 15 | 527 | Y | 0% | N | -0.022 | CIN to CIN | 0.00 | 0.0000 | Active | 2 | Baseline rates |
| DeVonta Smith | 27 | 30 | 30 | 20 | 17 | 524 | Y | 0% | N | -0.008 | PHI to PHI | 0.00 | 0.0000 | Active | 1 | Baseline rates |
| Alec Pierce | 30 | 32 | 31 | 23 | 15 | 478 | Y | 0% | N | 0.068 | IND to IND | 0.00 | 0.0000 | Active/Questionable | 1 | Baseline rates |
| Jauan Jennings | 28 | 31 | 32 | 37 | 15 | 466 | Y | 0% | N | -0.015 | SF to MIN | -2.16 | -0.0225 | Active | 3 | Environment review |
| Romeo Doubs | 31 | 33 | 33 | 36 | 16 | 419 | Y | 0% | N | 0.066 | GB to NE | 0.60 | 0.0090 | Active | 2 | Environment review |
| Parker Washington | 32 | 34 | 34 | 39 | 16 | 412 | Y | 0% | N | 0.069 | JAX to JAX | 0.00 | 0.0000 | Active | 2 | Baseline rates |
| Troy Franklin | 34 | 35 | 35 | 41 | 17 | 491 | Y | 0% | N | 0.079 | DEN to DEN | 0.00 | 0.0000 | Active | 3 | Baseline rates |
| Jameson Williams | 33 | 36 | 36 | 27 | 17 | 600 | Y | 0% | N | 0.077 | DET to DET | 0.00 | 0.0000 | Active | 2 | Baseline rates |
| Ladd McConkey | 36 | 37 | 37 | 35 | 16 | 562 | Y | 0% | N | 0.074 | LAC to LAC | 0.00 | 0.0000 | Active/Questionable | 1 | Baseline rates |
| Stefon Diggs | 37 | 38 | 38 | - | 17 | 421 | Y | 0% | N | -0.058 | NE to unknown | - | 0.0000 | Active | - | Baseline rates |
| Jakobi Meyers | 38 | 39 | 39 | 28 | 16 | 529 | Y | 0% | N | -0.009 | JAX to JAX | 0.00 | 0.0000 | Active | 3 | Baseline rates |
| Christian Watson | 35 | 40 | 40 | 32 | 10 | 244 | Y | 15% | N | -0.046 | GB to GB | 0.00 | 0.0000 | Active | 1 | 15% prior blend |
| Deebo Samuel | 39 | 41 | 41 | - | 16 | 442 | Y | 0% | N | -0.009 | WAS to unknown | - | 0.0000 | Active | - | Baseline rates |
| Keenan Allen | 40 | 42 | 42 | - | 17 | 468 | Y | 0% | N | -0.080 | LAC to unknown | - | 0.0000 | Active | - | Baseline rates |

Separate requested audits not already discussed: Chris Olave moves 8 to 9, Tee Higgins 26 to 29, Davante Adams stays 6, DK Metcalf stays 19, Rashee Rice moves 4 to 5 without blending because a required prior rate is unavailable, Stefon Diggs moves 37 to 38, Deebo Samuel moves 39 to 41, and Keenan Allen moves 40 to 42.

## Sleeper Archive

- `sleeper_player_snapshot_history` remains append-only at `(snapshot_date, sleeper_player_id)`.
- Latest snapshot: `2026-07-10`; 12,200 rows; duplicate grains: 0.
- `sleeper_current_player_context` has the same `2026-07-10` fetch date.
- `v_sleeper_player_status_changes` returns zero rows because only one snapshot date exists. Its SQL compares the newest snapshot with the previous dated snapshot when one becomes available.
- No weekly Scheduler or Cloud Run Job was deployed.

## Files And Checks

Files created:

- `bigquery/views/v_wr_fable_v1d_team_environment.sql`
- `bigquery/views/v_wr_fable_v1d_metric_inputs.sql`
- `bigquery/views/v_wr_fable_v1d_scored_seasons.sql`
- `bigquery/views/v_wr_fable_v1d_backtest_prep.sql`
- `bigquery/views/v_wr_fable_v1d_current_board.sql`
- `scripts/build_wr_fable_v1d_layer.py`
- `scripts/run_wr_fable_v1d_tests.py`
- `tests/test_wr_fable_v1d.py`
- this report

Checks:

- 34 focused tests passed across v1d, v1.1, v1, and Sleeper archive behavior.
- Both new Python scripts compile.
- Deployment safety checker passed every check.
- Backtest duplicate grains: 0. Backtest 2026 rows: 0.
- Historical market references: 0. Historical current-context relation references: 0.
- Revised team environment scores are non-null for all 128 team-season rows.
- Current I4 board contains 144 rows and 144 unique players.
- Active WR Fable v1d ranking rows: 0.

No live ranking was written. No champion was activated. No app, job, or Scheduler was deployed. The test used no 2026 outcomes, market value, fabricated metric, current depth input in historical folds, Gemini call, or Pigskin chat call.

Remaining warnings:

- I4 fails the top-12 precision acceptance limit despite improving most secondary metrics.
- Tyreek Hill, Stefon Diggs, Deebo Samuel, and Keenan Allen have no current team in the retained snapshot, so current environment adjustment correctly stays zero.
- The shared worktree has 103 existing or concurrent status entries. This phase did not stage, commit, revert, or package them.

## Selected Formula

I4 is the research finalist. It is not ready for promotion because it fails the stated top-12 precision requirement. E15, E25, and E40 are rejected as score modifiers.

Recommended next test: use the untouched v1 score whenever v1 produces a complete row. Add I4 and source-backed rookie handling only for otherwise excluded players. This directly tests whether coverage can improve without disturbing the baseline top 12.
