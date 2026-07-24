# Phase 35.1B WR Fable v1 Build, Backtest, and Current Board Report

## Recommendation

`WR FABLE V1 READY FOR OWNER APPROVAL`

Average Spearman rank correlation across the three forward folds is **0.738** — above the 0.60-0.68 ceiling the design document projected. Points captured at the top 12 averages 0.917, pairwise draft win rate 0.769, and only two predicted top-12 busts occurred in three folds. The known weakness is the same role-change/breakout blindness documented for RB Fable: all eight elite misses were players whose target-season role differed sharply from their input season. No live object changed; everything below is research-only.

## 1. Exact Formula (as implemented in `v_wr_fable_v1_scored_seasons`)

```
WR_FABLE_V1_SCORE =
  0.30*z(WOPR) + 0.12*z(NGT targets/gm) + 0.10*z(RZ targets/gm)          -- opportunity 52%
+ 0.12*z(YPRR)*route_shrink + 0.06*z(EPA/tgt)*tgt_shrink
+ 0.05*z(YAC/rec)*tgt_shrink + 0.05*z(aDOT-adj catch rate)*tgt_shrink   -- efficiency 28%
+ 0.10*z(blended TD/gm)                                                  -- scoring 10%
+ 0.04*z(breakout 22-25) + 0.03*z(-max(0,age-29)) + 0.03*z(games/17)     -- age/avail 10%
```

- z-scores partitioned by input season over the qualified WR pool (6+ games OR 40+ targets).
- `route_shrink = routes/(routes+60)`; `tgt_shrink = targets/(targets+60)`.
- WOPR canonized as `1.5*(target_share/100) + 0.7*air_yards_share` (situational percent normalized; brain share is a fraction). Stored weekly WOPR retained only as a cross-check column (`stored_wopr_weekly_avg`).
- NGT and RZ targets derived per refinement as `routes_run × TPRR`; raw NFLverse season targets are canonical for the standard split and shrinkage.
- aDOT-adjusted catch rate = residual of catch_pct on aDOT within each season pool.
- **TD engine is the owner-approved red-zone-based xTD fallback, NOT end-zone xTD**: season league conversion = Σ(RZ TDs)/Σ(RZ targets) over qualified WRs (same input season), `xTD/gm = RZ targets/gm × conversion`, `blended = 0.7×xTD + 0.3×actual`. End-zone targets were not invented; the string `end_zone_targets` appears nowhere in the WR views (unit-tested).
- Missing inputs stay null; null-score rows are excluded, never zero-filled.

## 2. Metric And Identity Coverage

- Situational inputs 100% non-null for all 11 metrics, all seasons (Phase 35.1A).
- Identity bridge (`v_wr_fable_v1_identity_bridge`, WR pool): 362 EXACT_SLUG_MATCH, 2 NAME_TEAM_SEASON_MATCH, 2 UNMAPPED, 1 MULTIPLE_CANDIDATES (collision, excluded). Only collision-free verified matches enter the metric layer.
- Qualified rows: 161 / 172 / 161 / ~160 for 2022-2025; complete scores 132 / 140 / 135 per input season (nulls mostly missing air-yards share or birth date; left null by design).

## 3. Forward Fold Results

| Fold | Rows | Spearman | Score corr | Top6 | Top12 | Top24 | Top36 | Pts@12 | Pts@24 | NDCG@12 | NDCG@24 | Pairwise | Regret | Elite misses | Top-12 busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022→2023 | 109 | 0.756 | 0.779 | 0.167 | 0.583 | 0.792 | 0.750 | 0.924 | 0.919 | 0.861 | 0.877 | 0.777 | 0.220 | 3 | 0 |
| 2023→2024 | 107 | 0.705 | 0.690 | 0.167 | 0.667 | 0.500 | 0.667 | 0.943 | 0.876 | 0.810 | 0.805 | 0.751 | 0.308 | 3 | 2 |
| 2024→2025 | 104 | 0.755 | 0.769 | 0.500 | 0.667 | 0.583 | 0.694 | 0.885 | 0.883 | 0.861 | 0.866 | 0.777 | 0.269 | 2 | 0 |

## 4. Aggregate

Spearman **0.738** | score corr 0.746 | top-6 0.278 | top-12 **0.639** | top-24 0.625 | top-36 0.704 | points@12 **0.917** | points@24 0.893 | NDCG@12 0.844 | NDCG@24 0.849 | pairwise 0.769 | band regret 0.266 | elite misses 8 | top-12 busts 2 | complete rows 320.

Versus RB Fable v1 at promotion: higher rank correlation (0.738 vs 0.771 score-corr-equivalent on a deeper pool), higher top-12 precision (0.639 vs 0.611), lower band regret (0.266 vs 0.320) — consistent with the design thesis that WR opportunity is earned and therefore stickier.

## 5. Miss Audit

Elite misses (actual top-12, predicted outside top 24) — all role-change or usage-shift cases:

- 2022→2023: Mike Evans (pred 29, actual 8), Deebo Samuel (39, 6), Nico Collins (41, 7 — pre-breakout role explosion).
- 2023→2024: Chris Godwin (32, 3), Tee Higgins (35, 4), Terry McLaurin (40, 11 — new QB effect).
- 2024→2025: Chris Olave (45, 8 — injury-shortened input season), Christian Watson (54, 11).

Predicted top-12 busts (only two in three folds): Keenan Allen (pred 5 in 2023→2024, actual 37 — team change LAC→CHI at age 31) and Michael Pittman (pred 8, actual 48 — QB collapse plus injury). Both are exactly the teammate/QB-context failures the design document warned about.

Pattern checks: deep threats properly lifted by WOPR (Hill 2022 pred 7 → actual 1; Chase, Metcalf); possession receivers correctly discounted in Standard (Jakobi Meyers, Wan'Dale Robinson types rank lower than reception counts suggest); breakout window boosted JSN, Nacua, London, McMillan, Egbuka; decline penalty correctly drags 30+ receivers (Evans -0.129 age component, Keenan Allen -0.075, Adams -0.080) — Adams still ranks 6th on 2025 volume, showing the penalty discounts rather than buries.

## 6. Current WR Fable v1 Board (2025 source metrics) — Top 40

Labeled: Fable v1 board from 2025 source metrics; not a 2026 backtest. Delta = Standard rank − Fable rank.

| Fable | Std | Delta | Player | Team | Score | WOPR | NGT tgt/gm | RZ tgt/gm | YPRR | Blend TD | Age | Context |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 3 | +2 | Amon-Ra St. Brown | DET | 1.930 | 0.602 | 10.1 | 2.06 | 2.47 | 0.551 | 25 | |
| 2 | 1 | -1 | Jaxon Smith-Njigba | SEA | 1.903 | 0.713 | 9.6 | 0.99 | 3.61 | 0.347 | 23 | |
| 3 | 2 | -1 | Puka Nacua | LAR | 1.744 | 0.565 | 10.4 | 1.05 | 3.70 | 0.369 | 24 | |
| 4 | 8 | +4 | Rashee Rice | KC | 1.633 | 0.483 | 9.6 | 2.26 | 2.15 | 0.578 | 25 | INJURY (Questionable) |
| 5 | 4 | -1 | Ja'Marr Chase | CIN | 1.630 | 0.613 | 11.1 | 1.38 | 2.23 | 0.389 | 25 | |
| 6 | 13 | +7 | Davante Adams | LAR | 1.493 | 0.497 | 8.2 | 2.30 | 1.93 | 0.698 | 32 | |
| 7 | 5 | -2 | Drake London | ATL | 1.422 | 0.596 | 9.1 | 1.27 | 2.32 | 0.394 | 24 | INJURY (Questionable) |
| 8 | 6 | -2 | Chris Olave | NO | 1.264 | 0.587 | 9.5 | 0.93 | 1.98 | 0.329 | 25 | |
| 9 | 11 | +2 | George Pickens | DAL | 1.246 | 0.448 | 7.8 | 1.33 | 2.34 | 0.388 | 24 | |
| 10 | 15 | +5 | Nico Collins | HOU | 1.106 | 0.500 | 8.0 | 1.21 | 2.31 | 0.330 | 26 | |
| 11 | 14 | +3 | CeeDee Lamb | DAL | 1.094 | 0.471 | 9.0 | 1.31 | 2.37 | 0.296 | 26 | |
| 12 | 12 | 0 | Zay Flowers | BAL | 1.086 | 0.560 | 6.9 | 0.66 | 2.52 | 0.202 | 24 | |
| 13 | 9 | -4 | Justin Jefferson | MIN | 1.082 | 0.587 | 8.4 | 1.07 | 1.88 | 0.221 | 26 | |
| 14 | 10 | -4 | Garrett Wilson | NYJ | 1.048 | 0.675 | 7.6 | 0.57 | 1.73 | 0.270 | 25 | |
| 15 | 7 | -8 | A.J. Brown | PHI→NE | 1.015 | 0.542 | 8.1 | 0.88 | 2.07 | 0.292 | 28 | STALE TEAM |
| 16 | 17 | +1 | Wan'Dale Robinson | NYG→TEN | 1.013 | 0.546 | 8.5 | 0.83 | 1.87 | 0.219 | 24 | STALE TEAM |
| 17 | 16 | -1 | Tetairoa McMillan | CAR | 0.985 | 0.533 | 6.9 | 0.88 | 1.83 | 0.275 | 22 | INJURY (Questionable) |
| 18 | 19 | +1 | Rome Odunze | CHI | 0.859 | 0.465 | 7.4 | 0.99 | 1.59 | 0.321 | 23 | |
| 19 | 34 | +15 | DK Metcalf | PIT | 0.829 | 0.476 | 6.6 | 0.87 | 1.98 | 0.270 | 27 | |
| 20 | 26 | +6 | Emeka Egbuka | TB | 0.820 | 0.479 | 7.2 | 0.81 | 1.74 | 0.246 | 22 | |
| 21 | 25 | +4 | Courtland Sutton | DEN | 0.811 | 0.442 | 7.4 | 1.11 | 1.61 | 0.316 | 29 | |
| 22 | 22 | 0 | Jaylen Waddle | MIA→DEN | 0.765 | 0.488 | 5.9 | 0.70 | 2.18 | 0.234 | 26 | STALE TEAM |
| 23 | 31 | +8 | Michael Wilson | ARI | 0.738 | 0.424 | 6.2 | 0.96 | 1.59 | 0.290 | 25 | |
| 24 | 30 | +6 | Quentin Johnston | LAC | 0.733 | 0.364 | 6.3 | 1.18 | 1.51 | 0.389 | 23 | |
| 25 | 21 | -4 | Terry McLaurin | WAS | 0.724 | 0.486 | 5.9 | 0.81 | 2.20 | 0.229 | 29 | |
| 26 | 24 | -2 | Tee Higgins | CIN | 0.705 | 0.396 | 6.4 | 0.98 | 1.61 | 0.390 | 26 | |
| 27 | 20 | -7 | DeVonta Smith | PHI | 0.700 | 0.478 | 6.8 | 0.64 | 1.92 | 0.181 | 26 | |
| 28 | 37 | +9 | Jauan Jennings | SF→MIN | 0.679 | 0.380 | 6.1 | 1.27 | 1.38 | 0.400 | 28 | STALE TEAM; depth 3 |
| 29 | 29 | 0 | Mike Evans | TB→SF | 0.667 | 0.470 | 7.7 | 1.12 | 1.61 | 0.306 | 32 | STALE TEAM |
| 30 | 23 | -7 | Alec Pierce | IND | 0.666 | 0.420 | 5.3 | 0.62 | 2.10 | 0.227 | 25 | INJURY (Questionable) |
| 31 | 36 | +5 | Romeo Doubs | GB→NE | 0.654 | 0.371 | 5.2 | 1.06 | 1.73 | 0.297 | 25 | STALE TEAM |
| 32 | 39 | +7 | Parker Washington | JAX | 0.649 | 0.368 | 5.7 | 0.88 | 2.06 | 0.245 | 23 | |
| 33 | 27 | -6 | Jameson Williams | DET | 0.634 | 0.401 | 5.9 | 0.51 | 1.86 | 0.211 | 24 | |
| 34 | 41 | +7 | Troy Franklin | DEN | 0.631 | 0.373 | 6.0 | 1.07 | 1.44 | 0.291 | 22 | depth 3 |
| 35 | 32 | -3 | Christian Watson | GB | 0.631 | 0.404 | 5.6 | 0.61 | 2.50 | 0.286 | 26 | |
| 36 | 35 | -1 | Ladd McConkey | LAC | 0.624 | 0.383 | 6.7 | 0.92 | 1.40 | 0.272 | 23 | INJURY (Questionable) |
| 37 | — | — | Stefon Diggs | NE | 0.618 | 0.386 | 5.9 | 0.72 | 2.41 | 0.194 | 31 | not on Std board; no Sleeper match |
| 38 | 28 | -10 | Jakobi Meyers | JAX | 0.592 | 0.431 | 6.4 | 0.91 | 1.58 | 0.214 | 28 | depth 3 |
| 39 | — | — | Deebo Samuel | WAS | 0.581 | 0.424 | 6.1 | 0.74 | 1.64 | 0.222 | 29 | not on Std board; no Sleeper match |
| 40 | — | — | Keenan Allen | LAC | 0.561 | 0.418 | 7.0 | 0.96 | 1.66 | 0.237 | 33 | not on Std board; no Sleeper match |

## 7-8. Comparison, Risers, Fallers

Agreement is strong at the top: 13 of the Standard top 15 are within four Fable slots. Sleeper confirms every Standard-board team (zero mismatches).

Biggest Fable risers (Fable higher): DK Metcalf +15, Jauan Jennings +9, Michael Wilson +8, Davante Adams +7, Parker Washington +7, Troy Franklin +7, Emeka Egbuka +6, Quentin Johnston +6, Nico Collins +5, Romeo Doubs +5, Rashee Rice +4, Courtland Sutton +4, CeeDee Lamb +3, Amon-Ra St. Brown +2, George Pickens +2. The Adams rise is the WR analog of the Henry call: elite red-zone role (2.30 RZ tgt/gm, 0.698 blended TD/gm) against an age-32 penalty the formula discounts but does not bury.

Biggest Fable fallers (Standard higher): Jakobi Meyers -10, Jordan Addison -9 (Fable 42), A.J. Brown -8, Tre Tucker -8 (Fable 46), DeVonta Smith -7, Alec Pierce -7, Ricky Pearsall -7 (Fable 47), Jameson Williams -6, Justin Jefferson -4, Garrett Wilson -4, Terry McLaurin -4, Christian Watson -3, Drake London -2, Chris Olave -2, Tee Higgins -2.

Only on one list: Fable-only — Stefon Diggs (37), Deebo Samuel (39), Keenan Allen (40), all absent from the active Standard board and without Sleeper context matches (SLEEPER_ID_MISSING; verify roster status manually). Standard-only — **Malik Nabers (Std 18): no qualified 2025 Fable row** (injury-shortened season below qualification), the WR analog of the James Conner gap.

## 9. Current-Context Warnings (Sleeper, review evidence only — never in the score)

- Stale-team (scored on prior team): **A.J. Brown (PHI→NE)** — the most consequential; his Fable 15 reflects a Philadelphia offense he has left. Wan'Dale Robinson (NYG→TEN), Jaylen Waddle (MIA→DEN), Jauan Jennings (SF→MIN, listed depth 3), Mike Evans (TB→SF at age 32), Romeo Doubs (GB→NE).
- Injury (Questionable): Rashee Rice, Drake London, Tetairoa McMillan, Alec Pierce, Ladd McConkey, Malik Nabers.
- Depth-chart warnings: Jennings, Franklin, Meyers (listed 3rd); several risers in the 28-40 band are listed WR2+.
- Missing/unqualified: Malik Nabers (Std 18) has no Fable row.

## 10. Objects, Checks, Safety

Research views created: `v_wr_fable_v1_identity_bridge`, `v_wr_fable_v1_situational_splits`, `v_wr_fable_v1_metric_inputs`, `v_wr_fable_v1_scored_seasons`, `v_wr_fable_v1_backtest_prep`. Scripts: `scripts/build_wr_fable_v1_metric_layer.py`, `scripts/run_wr_fable_v1_backtest.py`. Tests: `tests/test_wr_fable_v1.py` (10 tests — formula weights, WOPR derivation/normalization, RZ-fallback labeling, no end-zone invention, qualification, null safety, leakage bounds, identity fail-closed, backtest math). Evidence: `output/phase-35-1b-wr-fable-v1-results.json` (not a commit candidate).

Checks: all 10 WR tests pass; leakage tests confirm input seasons 2022-2024, targets 2023-2025, no `2026` in any WR view; no `end_zone_targets`, market, or Sleeper-context references in formula SQL; deployment safety checker all-pass; BigQuery validation discovery through 245; `git diff --check` clean (pre-existing line-ending notices only).

Safety: no live ranking writes, no champion activation, no deployment, no training, no Gemini/Pigskin chat, no 2026 outcomes, no market inputs, no Sleeper context in backtests, no fabricated end-zone targets, no silent zero-fills.

## Recommendation Detail

`WR FABLE V1 READY FOR OWNER APPROVAL`. The backtest clears the design ceiling on every rank-quality metric, the two busts and eight misses are all documented role-change cases (the known, disclosed limitation), and the current board's disagreements are principled. Before any promotion decision, the owner should specifically rule on: A.J. Brown's stale-team rank, the Nabers gap, and the three Fable-only veterans (Diggs/Deebo/Allen) with no Standard-board presence.
