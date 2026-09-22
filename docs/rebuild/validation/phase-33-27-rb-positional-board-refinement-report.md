# Phase 33.27 RB Positional Board Refinement

Final decision: `RB POSITIONAL BOARD READY WITH ELITE TRIPWIRES`

Secondary decision: `TOP-100 REMAINS BLOCKED`

## Scope

This phase refined the RB positional-board review path after Phase 33.26D proved that Jahmyr Gibbs and other elite RBs were being misranked before the top-100 interleaver ran.

No live ranking writes, champion activation, deployment, Gemini call, Pigskin chat, 2026 outcome usage, market training target, or route-metric fabrication occurred.

## Files Changed

- Created `docs/rebuild/validation/phase-33-27-rb-positional-board-refinement-report.md`.
- Generated local review evidence `output/phase-33-27-rb-board-evidence.json`.
- Appended Phase 33.27 notes to:
  - `docs/rebuild/advanced-bqml-v2-owner-review-boards.md`
  - `docs/rebuild/position-locked-top-100-interleaver-plan.md`
  - `docs/rebuild/ranking-algorithm-scorecard.md`
  - `docs/rebuild/bqml-v2-ranking-architecture.md`
  - `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- Did not update `docs/rebuild/position-locked-top-100-prototype-review.md`.

Preexisting git state included staged/modified Phase 33 docs, modified `src/bqml_v2_feature_contract.py`, and untracked Phase 33 review artifacts. This phase did not revert or overwrite that work.

## RB Board Problem Summary

The existing guarded RB finalist boards bury several current or market-backed RBs too far down the positional queue:

- Jahmyr Gibbs: Current Pigskin RB3 in every profile, market RB2, guarded RB18/RB19 outside PPR and RB9 in PPR.
- De'Von Achane: Current Pigskin RB4/RB5, market RB5, guarded RB13 to RB18.
- Chase Brown: Current Pigskin RB6, guarded RB25 to RB32.
- Omarion Hampton: Current Pigskin RB10 and market RB6, but guarded RB55/RB56 due prospect history.

The root issue is not identity or missing source data. It is RB model and queue behavior. The current finalist boards underweight receiving value, current role expansion, and current/market elite anchors in the review context.

## Existing RB Models

| Profile | Accepted RB Finalist | Alternate Available | Current Finalist Status |
| --- | --- | --- | --- |
| standard | `ranking_bqml_v2_adv_standard_rb_linear_points_advanced_v0` | `ranking_bqml_v2_adv_standard_rb_logistic_bust_advanced_v0` | Fails elite RB tripwires without correction |
| half_ppr | `ranking_bqml_v2_adv_half_ppr_rb_linear_vor_advanced_v0` | `ranking_bqml_v2_adv_half_ppr_rb_linear_points_advanced_v0` | Fails elite RB tripwires without correction |
| ppr | `ranking_bqml_v2_adv_ppr_rb_logistic_elite_advanced_v0` | `ranking_bqml_v2_adv_ppr_rb_linear_points_advanced_v0` | Better for Gibbs, still fails Achane and Chase Brown |
| gng_keeper | `ranking_bqml_v2_adv_gng_keeper_rb_linear_points_advanced_v0` | `ranking_bqml_v2_adv_gng_keeper_rb_logistic_elite_v0` | Fails elite RB tripwires without correction |

The existing alternates do not fix the issue. Standard alternate leaves Gibbs RB9. Half PPR and PPR alternates leave Gibbs RB12. GNG alternate behaves like Current Pigskin for the audited top group but does not solve the broader model decision because it is not documented in the current owner board with full alternate diagnostics.

## Candidate Board Comparison

Review-only candidates tested:

- `current_hold`: Current Pigskin RB queue.
- `finalist_tripwire`: current finalist with tripwire lock boosts.
- `anchored_blend`: tiered Current Pigskin blend with current finalist.
- `anchored_blend_tripwire`: tiered Current Pigskin blend with elite tripwire locks.
- `receiving_aware_blend`: current, guarded, and receiving/opportunity feature blend.
- `receiving_aware_blend_tripwire`: receiving-aware blend with tripwire locks.
- `alternate_existing`: documented alternate rank where available.

Selected candidate: `anchored_blend_tripwire`.

Why: it passes the explicit elite RB acceptance checks in every profile, keeps the board anchored to current RB context, still preserves finalist signal inside tiers, and labels the model weakness instead of treating the old RB finalist as safe.

| Profile | Candidate | Gibbs | Achane | Chase Brown | Ashton Jeanty | Omarion Hampton | Current Top-6 Misses | Market Top-3 Misses | Unexplained Market Top-6 Misses | Accepted |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| standard | current_hold | 3 | 5 | 6 | 12 | 10 | 0 | 1 | 0 | No |
| standard | finalist_tripwire | 3 | 6 | 7 | 4 | 12 | 0 | 0 | 0 | Yes |
| standard | anchored_blend | 4 | 5 | 10 | 9 | 20 | 0 | 1 | 0 | No |
| standard | anchored_blend_tripwire | 3 | 6 | 7 | 4 | 12 | 0 | 0 | 0 | Yes |
| standard | receiving_aware_blend | 3 | 5 | 9 | 7 | 22 | 0 | 0 | 0 | Yes |
| standard | alternate_existing | 9 | 15 | 20 | 5 | 49 | 2 | 1 | 1 | No |
| half_ppr | current_hold | 3 | 4 | 6 | 11 | 10 | 0 | 1 | 0 | No |
| half_ppr | finalist_tripwire | 3 | 6 | 7 | 4 | 12 | 0 | 0 | 0 | Yes |
| half_ppr | anchored_blend | 4 | 6 | 10 | 9 | 18 | 0 | 1 | 0 | No |
| half_ppr | anchored_blend_tripwire | 3 | 6 | 7 | 4 | 12 | 0 | 0 | 0 | Yes |
| half_ppr | receiving_aware_blend | 3 | 5 | 9 | 7 | 21 | 0 | 0 | 0 | Yes |
| half_ppr | alternate_existing | 12 | 11 | 29 | 5 | 53 | 1 | 1 | 0 | No |
| ppr | current_hold | 3 | 4 | 6 | 11 | 10 | 0 | 1 | 0 | No |
| ppr | finalist_tripwire | 3 | 5 | 7 | 4 | 12 | 0 | 0 | 0 | Yes |
| ppr | anchored_blend | 3 | 5 | 10 | 9 | 19 | 0 | 1 | 0 | No |
| ppr | anchored_blend_tripwire | 3 | 6 | 7 | 4 | 12 | 0 | 0 | 0 | Yes |
| ppr | receiving_aware_blend | 3 | 4 | 8 | 7 | 21 | 0 | 0 | 0 | Yes |
| ppr | alternate_existing | 12 | 10 | 24 | 5 | 55 | 1 | 1 | 0 | No |
| gng_keeper | current_hold | 3 | 5 | 6 | 11 | 10 | 0 | 1 | 0 | No |
| gng_keeper | finalist_tripwire | 3 | 6 | 7 | 4 | 12 | 0 | 0 | 0 | Yes |
| gng_keeper | anchored_blend | 4 | 6 | 10 | 9 | 20 | 0 | 1 | 0 | No |
| gng_keeper | anchored_blend_tripwire | 3 | 6 | 7 | 4 | 12 | 0 | 0 | 0 | Yes |
| gng_keeper | receiving_aware_blend | 3 | 5 | 9 | 7 | 22 | 0 | 0 | 0 | Yes |
| gng_keeper | alternate_existing | 3 | 5 | 6 | 11 | 10 | 0 | 1 | 0 | No |

## Selected Corrected RB Board Candidate

Candidate: `anchored_blend_tripwire`.

Rule shape:

- Top 12 Current Pigskin RBs: 80% Current Pigskin rank, 20% guarded finalist rank.
- RB13 to RB24: 65% Current Pigskin rank, 35% guarded finalist rank.
- RB25 and below: 50% Current Pigskin rank, 50% guarded finalist rank.
- Current or market top-3 RBs get an RB8 review cap.
- Current top-6 RBs get an RB12 review cap.
- Market top-6 RBs get an RB12 review cap unless a prospect/low-history manual-review exception is documented.
- All interventions are review-only and require explanation labels.

Selected top 24, PPR:

| Rank | Player | Current RB | Guarded RB | Market RB | Review Labels |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | Christian McCaffrey | 1 | 5 | 9 | OK |
| 2 | Bijan Robinson | 2 | 1 | 1 | OK |
| 3 | Jahmyr Gibbs | 3 | 9 | 2 | OK |
| 4 | Ashton Jeanty | 11 | 4 | 3 | OK |
| 5 | Jonathan Taylor | 5 | 3 | 7 | OK |
| 6 | De'Von Achane | 4 | 13 | 5 | `RB_RECEIVING_VALUE_UNDERWEIGHTED` |
| 7 | Chase Brown | 6 | 25 | 15 | `RB_RECEIVING_VALUE_UNDERWEIGHTED` |
| 8 | Saquon Barkley | 8 | 2 | 13 | OK |
| 9 | Kyren Williams | 9 | 7 | 16 | OK |
| 10 | Javonte Williams | 7 | 16 | 20 | OK |
| 11 | James Cook | 12 | 22 | 8 | OK |
| 12 | Omarion Hampton | 10 | 55 | 6 | `RB_ROLE_EXPANSION_UNDERWEIGHTED` |
| 13 | Travis Etienne | 14 | 11 | 21 | OK |
| 14 | Josh Jacobs | 13 | 14 | 23 | OK |
| 15 | Breece Hall | 18 | 8 | 10 | OK |
| 16 | Cam Skattebo | 15 | 15 | 18 | `RB_ROLE_EXPANSION_UNDERWEIGHTED` |
| 17 | Derrick Henry | 20 | 6 | 22 | OK |
| 18 | D'Andre Swift | 17 | 19 | 26 | OK |
| 19 | Bucky Irving | 16 | 23 | 19 | OK |
| 20 | Rhamondre Stevenson | 21 | 18 | 42 | OK |
| 21 | Quinshon Judkins | 22 | 21 | 12 | OK |
| 22 | Jaylen Warren | 19 | 33 | 30 | OK |
| 23 | Rico Dowdle | 23 | 42 | 32 | OK |
| 24 | Alvin Kamara | 27 | 15 | 53 | OK |

The selected top 12 shape is identical across all profiles:

1. Christian McCaffrey
2. Bijan Robinson
3. Jahmyr Gibbs
4. Ashton Jeanty
5. Jonathan Taylor
6. De'Von Achane
7. Chase Brown
8. Saquon Barkley
9. Kyren Williams
10. Javonte Williams
11. James Cook
12. Omarion Hampton

This is intentionally conservative. It makes the review board safe enough for a rebuilt top-100 prototype, but it is not a champion and not a live queue.

## RB Source-Feature Comparison

PPR source-backed feature slice, 2025 rows:

| Player | Games | Carries | Rush Yds | Targets | Rec | Rec Yds | RZ Opp | GL Opp | PPR WO | PPR WO/G | Targets/G | Rec Yds/G | PPR Total | PPR/G | Rush EPA | Rec EPA | Snap Share | Availability | Route Metrics |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Jahmyr Gibbs | 17 | 243 | 1,223 | 94 | 77 | 616 | 67 | 12 | 313.84 | 18.46 | 5.53 | 36.24 | 366.90 | 21.58 | -2.67 | 17.75 | 0.67 | 100.0 | BLOCKED |
| De'Von Achane | 16 | 238 | 1,350 | 85 | 67 | 488 | 43 | 6 | 278.03 | 17.38 | 5.31 | 30.50 | 322.80 | 20.17 | 14.04 | -10.23 | 0.75 | 100.0 | BLOCKED |
| Chase Brown | 17 | 232 | 1,019 | 88 | 69 | 445 | 49 | 17 | 284.73 | 16.75 | 5.18 | 26.18 | 282.60 | 16.62 | -4.24 | -10.33 | 0.67 | 100.0 | BLOCKED |
| Breece Hall | 16 | 243 | 1,065 | 48 | 36 | 350 | 33 | 5 | 215.22 | 13.45 | 3.00 | 21.88 | 207.66 | 12.98 | -22.27 | 8.67 | 0.64 | 100.0 | BLOCKED |
| Bijan Robinson | 17 | 287 | 1,478 | 103 | 79 | 820 | 49 | 12 | 333.72 | 19.63 | 6.06 | 48.24 | 370.80 | 21.81 | -12.25 | 26.59 | 0.78 | 100.0 | BLOCKED |
| Christian McCaffrey | 17 | 311 | 1,202 | 129 | 102 | 924 | 100 | 24 | 426.83 | 25.11 | 7.59 | 54.35 | 416.60 | 24.51 | -4.91 | 39.03 | 0.83 | 100.0 | BLOCKED |
| Jonathan Taylor | 17 | 323 | 1,585 | 55 | 46 | 378 | 76 | 25 | 298.27 | 17.55 | 3.24 | 22.24 | 362.30 | 21.31 | 18.77 | 9.23 | 0.83 | 100.0 | BLOCKED |
| Derrick Henry | 17 | 307 | 1,595 | 21 | 15 | 150 | 65 | 27 | 229.36 | 13.49 | 1.24 | 8.82 | 279.50 | 16.44 | 9.17 | -2.88 | 0.55 | 100.0 | BLOCKED |
| Ashton Jeanty | 17 | 266 | 975 | 73 | 55 | 346 | 45 | 12 | 274.29 | 16.13 | 4.29 | 20.35 | 245.10 | 14.42 | -65.18 | -11.88 | 0.78 | 100.0 | BLOCKED |
| Kyren Williams | 17 | 259 | 1,252 | 50 | 36 | 281 | 63 | 18 | 250.16 | 14.72 | 2.94 | 16.53 | 263.30 | 15.49 | 4.93 | 8.54 | 0.68 | 100.0 | BLOCKED |
| Josh Jacobs | 15 | 234 | 929 | 44 | 36 | 282 | 58 | 20 | 224.96 | 15.00 | 2.93 | 18.80 | 237.10 | 15.81 | -4.80 | 11.85 | 0.63 | 100.0 | BLOCKED |
| Cam Skattebo | 8 | 101 | 410 | 32 | 24 | 207 | 28 | 10 | 119.59 | 14.95 | 4.00 | 25.88 | 127.70 | 15.96 | -12.10 | 3.35 | 0.52 | 100.0 | BLOCKED |
| Jaylen Warren | 16 | 211 | 958 | 45 | 40 | 335 | 45 | 15 | 205.12 | 12.82 | 2.81 | 20.94 | 217.10 | 13.57 | -0.50 | 10.64 | 0.51 | 100.0 | BLOCKED |
| Omarion Hampton | 9 | 124 | 545 | 35 | 32 | 192 | 28 | 9 | 134.94 | 14.99 | 3.89 | 21.33 | 135.70 | 15.08 | -0.70 | -0.59 | 0.63 | 100.0 | BLOCKED |

## Explanation Flags

Review-only RB labels introduced:

- `RB_RECEIVING_VALUE_UNDERWEIGHTED`
- `RB_ROLE_EXPANSION_UNDERWEIGHTED`
- `RB_SPLIT_BACKFIELD_OVERPENALIZED`
- `RB_GOAL_LINE_OVERWEIGHTED`
- `RB_TRADITIONAL_RUSHING_OVERWEIGHTED`
- `RB_MARKET_TRIPWIRE`
- `RB_CURRENT_PIGSKIN_TRIPWIRE`
- `RB_MANUAL_REVIEW_REQUIRED`
- `RB_POSITIONAL_MODEL_MISS`
- `RB_MODEL_SWITCH_CANDIDATE`

Applied in selected candidate:

- Gibbs: `RB_RECEIVING_VALUE_UNDERWEIGHTED` outside PPR because targets and receiving production are source-backed but the guarded finalist ranks him RB18/RB19.
- Achane: `RB_RECEIVING_VALUE_UNDERWEIGHTED` because he is market RB5 and Current Pigskin RB4/RB5 with 5.31 targets per game, but the guarded finalist ranks him RB13 to RB18.
- Chase Brown: `RB_RECEIVING_VALUE_UNDERWEIGHTED` because he is Current Pigskin RB6 with 5.18 targets per game, but guarded finalist ranks him RB25 to RB32.
- Hampton and Skattebo: `RB_ROLE_EXPANSION_UNDERWEIGHTED` because current and market signals are strong but history volume remains short. These remain manual review players.

## Rejected Candidates

- `current_hold`: safest current context, but it fails market top-3 tripwire for Ashton Jeanty.
- Existing finalist without locks: fails Gibbs, Achane, and Chase Brown.
- Existing alternates: do not fix Gibbs or Chase Brown enough in Standard, Half PPR, or PPR.
- Plain anchored blend: improves Gibbs but still leaves market top-3 Ashton Jeanty outside RB8.
- Receiving-aware blend: promising, but it is a new review scoring formula and should stay a diagnostic until it gets its own validation pass.

## Can Top-100 Resume?

Top-100 can resume only as a review-only Phase 33.28 rebuild using the selected RB candidate or an owner-approved equivalent.

Top-100 should not resume from the Phase 33.26C RB queues. Those queues are known to bury elite receiving backs before the interleaver runs.

## Is New RB Model Training Required?

Not required before the next review-only top-100 prototype if the selected `anchored_blend_tripwire` candidate is used.

Recommended later: train or design a receiving-aware RB model that directly handles:

- weighted opportunity per game
- targets per game
- receiving yards per game
- receiving EPA
- role expansion
- split-backfield penalties
- goal-line and traditional rushing weights

That later model should not use market data as a training target.

## No-Live-Change Confirmation

- No live rankings were written.
- No champions were activated.
- No deployment occurred.
- No Gemini call occurred.
- No Pigskin chat call occurred.
- No 2026 outcomes were used.
- No market data was used as a training target.
- No Sleeper current context was used as historical input.
- `pigskin_context_score` was not used.
- Route metrics remain blocked/null.

## Checks

Checks run after report creation:

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract` | PASS, 26 tests |
| `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py` | PASS |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | PASS, validation discovery completed |
| Focused RB board checks from `output/phase-33-27-rb-board-evidence.json` | PASS |
| Focused elite RB tripwire checks from `output/phase-33-27-rb-board-evidence.json` | PASS |
| `git diff --check` | PASS with Git LF-to-CRLF warnings on preexisting docs |

## Warnings

- Market consensus is a PPR tripwire snapshot, not a training target.
- The selected candidate is a review-only board candidate. It is not a champion and not a live ranking queue.
- Current RB history still contains known model weaknesses around receiving value and role expansion.
- The worktree had preexisting staged, modified, and untracked Phase 33 files before this phase.

## Recommended Next Phase

Recommended next phase: Phase 33.28, rebuild top-100 prototype with refined RB board.

Alternate next phases:

- Phase 33.28, train new RB receiving-aware model.
- Phase 33.28, add market/current tripwire dashboard.
- Phase 33.28, hold top-100 behind Current Pigskin.
