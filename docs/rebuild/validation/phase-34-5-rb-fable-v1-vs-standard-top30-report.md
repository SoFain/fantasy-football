# Phase 34.5 RB Fable v1 vs Current Standard Top-30 Report

## Final Decision

`RB FABLE V1 TOP-30 COMPARISON READY` and `CURRENT PIGSKIN STILL HOLDS LIVE`

The comparison is complete, identity-clean, and read-only. The two boards agree far more than they disagree: 27 of 30 players are shared between the two top-30 lists, and 24 of the 33 union players sit within four rank slots of each other. The disagreements are concentrated and explainable. Fable v1 remains owner-review only; no historical baseline win exists (Phase 34.3/34.4), so Current Pigskin holds live by default.

## Sources

Fable side: `fantasy_football_advanced_metrics.v_rb_fable_01_scored_seasons`, season 2025, complete scores only, ranked by `rb_fable_01_score`. This is the **Fable v1 board from 2025 source metrics** — an input board for the upcoming season, not a completed 2026 backtest. The formula is the Phase 34.4 refinement including volume-conditioned age forgiveness.

Standard side: `fantasy_football_brain.analytics_pigskin_rankings` filtered to `is_active = TRUE`, `position = 'RB'`, `scoring_profile_id = 'standard'`.

- Ranking version: `pigskin-llm-20260704071412`
- Season/phase/format: 2026 preseason Standard
- Model run: `pigskin_rankings-2026-na-20260704T071419Z-9c498edc`, generated 2026-07-04T07:14 UTC
- Rows: 80, all RB. Exactly one active Standard RB board exists — no ambiguity.

The Standard board was used as comparison evidence only, never as a Fable input.

## Comparison Universe

Union of both top 30s: 33 players. Delta = Standard rank − Fable rank (positive = Fable values the player higher). Identity: every joined player is `EXACT_SLUG_MATCH` with zero collisions; Sleeper IDs come from the Standard board. One Standard top-30 player (James Conner, Standard 29) has **no qualified 2025 Fable row** and is flagged below.

## Table 1 — Top 30 by RB Fable v1

| Fable | Player | Team | Score | Std rank | Delta | Reason | NGT T/G | RZ T/G | Tgt% | YAC/rush | Succ | EPA/t | Expl | BoxYPC | TD blend | AgePen | Avail | AgeForgive |
|---:|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Christian McCaffrey | SF | 1.845 | 1 | 0 | opportunity led (+1.573) | 24.1 | 5.59 | 23.4 | 2.56 | 39.2 | -0.051 | 6.4 | 3.36 | 0.876 | -4 | 1.00 | 0.40 |
| 2 | Jonathan Taylor | IND | 1.433 | 4 | +2 | opportunity led (+0.991) | 21.7 | 4.35 | 10.4 | 3.30 | 44.3 | 0.048 | 8.1 | 4.11 | 0.831 | -1 | 1.00 | 0.40 |
| 3 | Bijan Robinson | ATL | 1.269 | 2 | -1 | opportunity led (+1.006) | 21.2 | 2.59 | 19.9 | 3.80 | 41.1 | -0.036 | 8.4 | 3.56 | 0.462 | 0 | 1.00 | 0.40 |
| 4 | Jahmyr Gibbs | DET | 1.264 | 3 | -1 | opportunity led (+0.943) | 18.6 | 3.76 | 17.1 | 3.00 | 39.9 | -0.008 | 8.6 | 4.46 | 0.710 | 0 | 1.00 | 0.44 |
| 5 | Devon Achane | MIA | 1.174 | 5 | 0 | opportunity led (+0.837) | 18.3 | 2.44 | 19.4 | 3.89 | 38.2 | 0.046 | 13.4 | 5.57 | 0.480 | 0 | 0.94 | 0.47 |
| 6 | James Cook | BUF | 1.110 | 7 | +1 | opportunity led (+0.764) | 20.1 | 3.47 | 8.3 | 3.11 | 45.6 | 0.016 | 8.7 | 4.72 | 0.628 | 0 | 1.00 | 0.40 |
| 7 | Javonte Williams | DAL | 1.046 | 9 | +2 | opportunity led (+0.711) | 17.9 | 3.88 | 8.7 | 3.26 | 45.6 | 0.043 | 6.8 | 3.05 | 0.657 | 0 | 0.94 | 0.53 |
| 8 | Derrick Henry | BAL | 0.989 | 20 | +12 | opportunity led (+0.650) | 18.6 | 3.82 | 5.2 | 3.45 | 41.7 | 0.028 | 9.8 | 5.08 | 0.706 | -6 | 1.00 | 0.44 |
| 9 | Josh Jacobs | GB | 0.977 | 13 | +4 | opportunity led (+0.747) | 18.0 | 3.80 | 10.3 | 2.95 | 43.6 | -0.055 | 6.0 | 2.62 | 0.692 | -2 | 0.88 | 0.51 |
| 10 | Kyren Williams | LAR | 0.951 | 6 | -4 | opportunity led (+0.625) | 16.8 | 3.59 | 8.6 | 2.95 | 50.2 | 0.017 | 7.0 | 4.16 | 0.612 | 0 | 1.00 | 0.66 |
| 11 | Chase Brown | CIN | 0.861 | 8 | -3 | opportunity led (+0.681) | 17.3 | 2.59 | 14.5 | 2.78 | 40.1 | -0.011 | 8.2 | 4.21 | 0.464 | 0 | 1.00 | 0.60 |
| 12 | Saquon Barkley | PHI | 0.853 | 10 | -2 | opportunity led (+0.757) | 19.8 | 3.00 | 10.8 | 2.82 | 37.5 | -0.079 | 7.1 | 3.31 | 0.492 | -3 | 0.94 | 0.40 |
| 13 | Travis Etienne | JAX->NO | 0.847 | 14 | +1 | opportunity led (+0.657) | 16.9 | 3.65 | 9.5 | 2.88 | 35.8 | -0.064 | 5.8 | 4.65 | 0.618 | -1 | 1.00 | 0.66 |
| 14 | Omarion Hampton | LAC | 0.798 | 11 | -3 | opportunity led (+0.683) | 17.2 | 3.11 | 12.3 | 2.72 | 41.9 | -0.005 | 7.3 | 3.11 | 0.506 | 0 | 0.53 | 0.61 |
| 15 | Ashton Jeanty | LV | 0.780 | 12 | -3 | opportunity led (+0.742) | 18.5 | 2.53 | 14.8 | 3.07 | 31.9 | -0.200 | 6.0 | 1.65 | 0.438 | 0 | 1.00 | 0.44 |
| 16 | Cam Skattebo | NYG | 0.769 | 18 | +2 | opportunity led (+0.638) | 15.5 | 3.25 | 13.2 | 2.80 | 40.6 | -0.105 | 5.9 | 3.50 | 0.611 | 0 | 0.47 | 0.83 |
| 17 | D'Andre Swift | CHI | 0.729 | 15 | -2 | opportunity led (+0.483) | 15.8 | 2.56 | 9.6 | 3.05 | 48.0 | 0.060 | 8.5 | 3.87 | 0.472 | -1 | 0.94 | 0.80 |
| 18 | Jaylen Warren | PIT | 0.655 | 19 | +1 | opportunity led (+0.485) | 15.7 | 2.75 | 9.0 | 3.00 | 42.6 | -0.002 | 7.6 | 3.50 | 0.448 | -1 | 0.94 | 0.81 |
| 19 | Rico Dowdle | CAR->PIT | 0.599 | 22 | +3 | opportunity led (+0.468) | 15.9 | 2.18 | 10.4 | 3.12 | 42.4 | -0.005 | 8.5 | 3.58 | 0.360 | -2 | 1.00 | 0.78 |
| 20 | Bucky Irving | TB | 0.597 | 17 | -3 | opportunity led (+0.690) | 20.3 | 2.10 | 11.3 | 2.39 | 34.7 | -0.175 | 4.6 | 2.60 | 0.343 | 0 | 0.59 | 0.40 |
| 21 | Zach Charbonnet | SEA | 0.558 | 30 | +9 | opportunity led (+0.309) | 12.4 | 3.38 | 5.5 | 3.07 | 41.3 | -0.011 | 6.0 | 3.03 | 0.595 | 0 | 0.94 | 1.00 |
| 22 | Breece Hall | NYJ | 0.549 | 16 | -6 | opportunity led (+0.466) | 17.1 | 1.63 | 10.7 | 3.02 | 40.7 | -0.080 | 8.6 | 4.65 | 0.270 | 0 | 0.94 | 0.63 |
| 23 | Quinshon Judkins | CLE | 0.548 | 21 | -2 | opportunity led (+0.506) | 17.4 | 2.36 | 8.3 | 2.89 | 33.0 | -0.102 | 5.7 | 3.06 | 0.411 | 0 | 0.82 | 0.59 |
| 24 | Kenneth Walker | SEA->KC | 0.501 | 25 | +1 | opportunity led (+0.341) | 14.8 | 2.12 | 7.9 | 3.35 | 38.0 | -0.057 | 9.9 | 4.64 | 0.320 | 0 | 1.00 | 0.93 |
| 25 | Kenneth Gainwell | PIT->TB | 0.495 | 31 | +6 | opportunity led (+0.368) | 10.8 | 2.18 | 16.3 | 2.82 | 45.6 | -0.004 | 8.8 | 4.53 | 0.350 | -1 | 1.00 | 1.00 |
| 26 | TreVeyon Henderson | NE | 0.494 | 28 | +2 | opportunity led (+0.278) | 12.5 | 2.35 | 8.7 | 2.89 | 41.7 | 0.039 | 8.9 | 5.09 | 0.430 | 0 | 1.00 | 1.00 |
| 27 | J.K. Dobbins | DEN | 0.427 | 23 | -4 | opportunity led (+0.315) | 16.4 | 2.00 | 4.2 | 3.05 | 45.8 | 0.025 | 11.1 | 4.43 | 0.344 | -1 | 0.59 | 0.72 |
| 28 | Tyrone Tracy | NYG | 0.351 | 33 | +5 | opportunity led (+0.323) | 13.9 | 1.67 | 10.8 | 2.78 | 36.9 | -0.046 | 6.8 | 3.72 | 0.255 | 0 | 0.88 | 1.00 |
| 29 | Rhamondre Stevenson | NE | 0.308 | 24 | -5 | opportunity led (+0.234) | 11.5 | 2.21 | 9.4 | 3.25 | 36.9 | -0.119 | 7.7 | 5.35 | 0.426 | -2 | 0.82 | 1.00 |
| 30 | Woody Marks | HOU | 0.293 | 34 | +4 | opportunity led (+0.291) | 13.6 | 2.38 | 6.9 | 2.44 | 36.2 | -0.133 | 5.1 | 2.44 | 0.347 | 0 | 0.94 | 1.00 |

AgeForgive is the Phase 34.4 protection multiplier on the age term (1.00 = no forgiveness applies or no volume qualification; 0.40 = maximum 60% forgiveness). Team arrows show where the Standard board's current team differs from the Fable 2025 source team — a role-change staleness signal.

## Table 2 — Top 30 by Current Standard

| Std | Player | Team | Std score | Tier | Fable rank | Delta | Fable score | Alignment |
|---:|---|---|---:|---|---:|---:|---:|---|
| 1 | Christian McCaffrey | SF | 98.5 | elite | 1 | 0 | 1.845 | aligned |
| 2 | Bijan Robinson | ATL | 95.0 | elite | 3 | -1 | 1.269 | aligned |
| 3 | Jahmyr Gibbs | DET | 93.5 | elite | 4 | -1 | 1.264 | aligned |
| 4 | Jonathan Taylor | IND | 92.0 | elite | 2 | +2 | 1.433 | aligned |
| 5 | Devon Achane | MIA | 91.0 | elite | 5 | 0 | 1.174 | aligned |
| 6 | Kyren Williams | LAR | 88.5 | front-line starter | 10 | -4 | 0.951 | aligned |
| 7 | James Cook | BUF | 87.0 | front-line starter | 6 | +1 | 1.110 | aligned |
| 8 | Chase Brown | CIN | 85.5 | front-line starter | 11 | -3 | 0.861 | aligned |
| 9 | Javonte Williams | DAL | 84.5 | front-line starter | 7 | +2 | 1.046 | aligned |
| 10 | Saquon Barkley | PHI | 83.5 | front-line starter | 12 | -2 | 0.853 | aligned |
| 11 | Omarion Hampton | LAC | 82.0 | front-line starter | 14 | -3 | 0.798 | aligned |
| 12 | Ashton Jeanty | LV | 80.0 | starter | 15 | -3 | 0.780 | aligned |
| 13 | Josh Jacobs | GB | 79.0 | starter | 9 | +4 | 0.977 | aligned |
| 14 | Travis Etienne | NO | 78.0 | starter | 13 | +1 | 0.847 | aligned |
| 15 | D'Andre Swift | CHI | 77.5 | starter | 17 | -2 | 0.729 | aligned |
| 16 | Breece Hall | NYJ | 76.5 | starter | 22 | -6 | 0.549 | Standard higher by 5-9 |
| 17 | Bucky Irving | TB | 75.5 | starter | 20 | -3 | 0.597 | aligned |
| 18 | Cam Skattebo | NYG | 74.5 | starter | 16 | +2 | 0.769 | aligned |
| 19 | Jaylen Warren | PIT | 73.5 | starter | 18 | +1 | 0.655 | aligned |
| 20 | Derrick Henry | BAL | 72.5 | starter | 8 | +12 | 0.989 | Fable higher by 10+ |
| 21 | Quinshon Judkins | CLE | 71.5 | starter | 23 | -2 | 0.548 | aligned |
| 22 | Rico Dowdle | PIT | 70.5 | starter | 19 | +3 | 0.599 | aligned |
| 23 | J.K. Dobbins | DEN | 69.5 | starter | 27 | -4 | 0.427 | aligned |
| 24 | Rhamondre Stevenson | NE | 68.5 | starter | 29 | -5 | 0.308 | Standard higher by 5-9 |
| 25 | Kenneth Walker | KC | 67.5 | starter | 24 | +1 | 0.501 | aligned |
| 26 | Aaron Jones | MIN | 66.5 | starter | 34 | -8 | 0.199 | Standard higher by 5-9 / only on Standard top 30 |
| 27 | Tony Pollard | TEN | 65.5 | starter | 35 | -8 | 0.196 | Standard higher by 5-9 / only on Standard top 30 |
| 28 | TreVeyon Henderson | NE | 64.5 | starter | 26 | +2 | 0.494 | aligned |
| 29 | James Conner | ARI | 63.5 | starter | n/a | n/a | n/a | only on Standard top 30; no qualified 2025 Fable row |
| 30 | Zach Charbonnet | SEA | 62.5 | starter | 21 | +9 | 0.558 | Fable higher by 5-9 |

## Table 3 — Biggest Fable Risers vs Standard

Only ten players clear a meaningful (2+ slot) riser threshold; listing all of them rather than padding to fifteen.

| Player | Team | Fable | Std | Delta | Source-backed reason |
|---|---|---:|---:|---:|---|
| Derrick Henry | BAL | 8 | 20 | +12 | 18.6 NGT touches/gm, 3.82 RZ touches/gm, 5.08 box-YPC, 9.8% explosive at age penalty -6; elite-volume protection retains 56% of the age penalty forgiveness case that fixed his 2023-to-2024 backtest miss |
| Zach Charbonnet | SEA | 21 | 30 | +9 | 3.38 RZ touches/gm (top-10 in cohort) and 0.595 blended TD/gm on modest 12.4 touches/gm; Fable's red-zone weight likes him more than his committee role |
| Kenneth Gainwell | PIT->TB | 25 | 31 | +6 | 16.3% target share and 45.6% success on only 10.8 touches/gm; receiving-usage-driven and team changed since the source season |
| Tyrone Tracy | NYG | 28 | 33 | +5 | Volume-only case (13.9 touches/gm); weak efficiency (-0.046 EPA/touch) but enough prior role to crack Fable's top 30 |
| Woody Marks | HOU | 30 | 34 | +4 | Rookie-season volume (13.6 touches/gm) with below-average efficiency; marginal top-30 entry |
| Rico Dowdle | CAR->PIT | 19 | 22 | +3 | 3.12 YAC/rush and 8.5% explosive on a full 17-game season; team changed since the source season |
| Jonathan Taylor | IND | 2 | 4 | +2 | 21.7 NGT touches/gm, 4.35 RZ touches/gm, 0.831 blended TD/gm; second-best opportunity profile in the pool |
| Javonte Williams | DAL | 7 | 9 | +2 | 3.88 RZ touches/gm and 45.6% success; the 2024 role-change miss is now fully priced in by his 2025 Dallas volume |
| Cam Skattebo | NYG | 16 | 18 | +2 | 3.25 RZ touches/gm and 0.611 blended TD/gm in only 8 games; availability 0.47 already penalizes the injury |
| TreVeyon Henderson | NE | 26 | 28 | +2 | Best-in-cohort 5.09 box-adjusted YPC and +0.039 EPA/touch on a rotational 12.5 touches/gm |

## Table 4 — Biggest Fable Fallers vs Standard

Twelve players fall 2+ slots (or are missing); listing all rather than padding to fifteen.

| Player | Team | Std | Fable | Delta | Source-backed reason |
|---|---|---:|---:|---:|---|
| James Conner | ARI | 29 | n/a | n/a | No qualified 2025 Fable inputs (2025 season below the qualification threshold); Fable cannot rank him at all |
| Aaron Jones | MIN | 26 | 34 | -8 | Age penalty -5 with only 13.3 touches/gm (volume z too low for elite-volume protection) and 0.71 availability; the formula's biggest veteran discount |
| Tony Pollard | TEN | 27 | 35 | -8 | Age penalty -3, 1.18 RZ touches/gm (near-bottom), negative TD blend z; low-value volume profile |
| Breece Hall | NYJ | 16 | 22 | -6 | 1.63 RZ touches/gm (bottom-quartile) and 0.270 blended TD/gm; Fable's red-zone and TD weights drive the discount |
| Rhamondre Stevenson | NE | 24 | 29 | -5 | 11.5 touches/gm, -0.119 EPA/touch, 36.9% success; weak on both volume and efficiency |
| Kyren Williams | LAR | 6 | 10 | -4 | Good but not elite volume (16.8 touches/gm); 50.2% success is excellent, yet opportunity weights cap him below the Standard board's view |
| J.K. Dobbins | DEN | 23 | 27 | -4 | 0.59 availability and 4.2% target share offset strong 11.1% explosive rate |
| Chase Brown | CIN | 8 | 11 | -3 | 2.59 RZ touches/gm and 0.464 blended TD/gm lag his overall volume; mild TD-based discount |
| Omarion Hampton | LAC | 11 | 14 | -3 | 0.53 availability from the injury-shortened rookie year drags an otherwise front-line profile |
| Ashton Jeanty | LV | 12 | 15 | -3 | Worst efficiency among ranked starters (-0.200 EPA/touch, 1.65 box-YPC, 31.9% success); volume carries him anyway |
| Bucky Irving | TB | 17 | 20 | -3 | 0.59 availability and -0.175 EPA/touch in the injury-affected 2025 season override his strong 2024 |
| Saquon Barkley | PHI | 10 | 12 | -2 | Down-year efficiency (-0.079 EPA/touch, 37.5% success) plus age penalty -3 at maximum forgiveness |

## Table 5 — Manual Review List

| Flag | Players |
|---|---|
| Top-12 disagreement of 5+ spots | Derrick Henry (Fable 8 vs Standard 20) |
| Top-24 disagreement of 10+ spots | Derrick Henry (12 spots) |
| Only on Fable top 30 | Kenneth Gainwell (Std 31), Tyrone Tracy (Std 33), Woody Marks (Std 34) |
| Only on Standard top 30 | Aaron Jones (Fable 34), Tony Pollard (Fable 35), James Conner (no Fable row) |
| Identity warnings | None; all 32 joined players are EXACT_SLUG_MATCH with zero collisions |
| Missing Fable components | James Conner: no qualified 2025 metric row at all |
| Boosted by age forgiveness (factor at or near 0.40-0.51 with age penalty of 2+) | Derrick Henry (-6, factor 0.44), Christian McCaffrey (-4, 0.40), Saquon Barkley (-3, 0.40), Josh Jacobs (-2, 0.51) |
| Punished by availability | Cam Skattebo (0.47), Omarion Hampton (0.53), Bucky Irving (0.59), J.K. Dobbins (0.59), Aaron Jones (0.71) |
| Possible role-change staleness (team changed since 2025 source season) | Travis Etienne (JAX to NO), Rico Dowdle (CAR to PIT), Kenneth Walker (SEA to KC), Kenneth Gainwell (PIT to TB) |

## Assessment

- Viable Standard RB replacement candidate: **directionally yes, not proven**. The boards agree on 14 of the Standard top 15 within four slots, and the disagreements land exactly where Fable's design says they should (red-zone/TD weighting, availability, age). But the backtest record (Phase 34.4: top-6 precision 0.333, five structural role-change misses) and four stale-team rows mean it cannot yet replace a board that incorporates current depth charts.
- Owner-review only: **yes**. The Etienne/Dowdle/Walker/Gainwell rows are scored on the wrong team context, and Conner is unrankable.
- Current Pigskin holds live: **yes, by default**. No leakage-safe historical baseline comparison has ever been possible, so Fable has not earned challenger status.

## Files Changed

- `docs/rebuild/validation/phase-34-5-rb-fable-v1-vs-standard-top30-report.md` (this report)
- `docs/rebuild/rb-fable-v1-vs-standard-top30.md`

No SQL, script, view, or production object changed in this phase.

## BigQuery Objects Queried (read-only)

- `fantasy_football_advanced_metrics.v_rb_fable_01_scored_seasons`
- `fantasy_football_advanced_metrics.v_rb_fable_01_metric_inputs`
- `fantasy_football_brain.analytics_pigskin_rankings` (active Standard RB board, comparison evidence only)
- `INFORMATION_SCHEMA.COLUMNS` in both datasets for schema confirmation

## Safety Confirmation

- No live ranking write occurred; queries were SELECT-only through the read-only endpoint.
- No champion was activated.
- No model was trained.
- No deployment occurred.
- No Gemini or Pigskin chat call occurred.
- No 2026 outcomes or actuals were used; the comparison is a preseason board versus a prior-season metric board.
- No market data entered the Fable formula; the Standard board was evidence only.
- No historical Pigskin rankings were fabricated.
- Broken tackles, YAC above expectation, and RB route metrics were not invented or added.
- No production feature mart was touched.

## Checks

- `venv\Scripts\python.exe scripts\check_deployment_safety.py`: all checks passed.
- `venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: discovery passed through validation 245.
- Focused comparison checks: exactly one active Standard RB board; 80 board rows, all RB; Fable 2025 complete-score count 94; union count 33; duplicate player-season count 0.
- Focused identity check: all joined rows EXACT_SLUG_MATCH, zero collisions.
- Focused no-2026-outcome check: no 2026 references in the Fable view definitions; Fable inputs bounded to seasons 2022-2025.
- Focused no-live-write check: read-only tool for all queries; no DML issued.
- `git diff --check`: pass; existing line-ending warnings are informational.

## Recommended Next Phase

Phase 34.6: resolve the four stale-team rows and the Conner gap by adding a current-team/depth-chart context join (evidence layer only, not a formula input), then present both boards to the owner for the Standard RB review decision. The Phase 34.4 recommendation of a team RB touch-share signal remains open for the formula itself.
