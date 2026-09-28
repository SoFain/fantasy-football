# Phase 34.7 RB Fable v1 Standard RB Promotion Implementation Note

## Final Decision

`RB FABLE V1 PROMOTED AS STANDARD RB FORMULA`

The owner decision was applied. RB Fable v1 (RB Fable 01, Phase 34.4 refined version with volume-conditioned age forgiveness) is now the registered champion Standard RB formula, and the active Standard RB board in `analytics_pigskin_rankings` is generated from it. The prior Current Pigskin LLM board is preserved as an archived fallback. Scope was strictly Standard scoring, RB only.

## What Changed In BigQuery

| Step | Object | Result |
|---|---|---|
| Candidate registered | `fantasy_football_brain.ranking_formula_candidates` | `rb_fable_v1_standard_rb`, version `1.1-phase-34.4`, status `champion`, full formula JSON (11 weights, shrinkage, age protection) recorded |
| Champion activated | `fantasy_football_brain.ranking_formula_champions` | First champion row in the table: position RB, formula set `standard_redraft_one_qb`, active TRUE, metric `avg_ndcg_at_24 = 0.847` from the Phase 34.4 forward folds, selected_by owner |
| Prior board archived | `fantasy_football_brain.analytics_pigskin_rankings_history` | `pigskin-llm-20260704071412` (80 RB rows) confirmed present in history; the idempotent archive guard found all 80 rows already archived, so no duplicates were created |
| Prior board deactivated | `fantasy_football_brain.analytics_pigskin_rankings` | 80 rows set `is_active = FALSE`; rows remain queryable as fallback |
| New board inserted | `fantasy_football_brain.analytics_pigskin_rankings` | 90 active rows, `ranking_version = rb-fable-v1-standard-20260710054940`, `rank_source = rb_fable_v1_formula`, `model_run_id = rb_fable_v1_promotion-20260710T054940Z` |

Board construction details:

- Ranks come solely from `rb_fable_01_score` (2025 source metrics, all 90 complete-score RBs). Sleeper context and prior-board data never influence rank order.
- `ranking_score` is a 50-99 min-max display normalization of the Fable score; the raw score is preserved in `raw_ranking_score`.
- `current_team` and the `risk_flags` column carry Sleeper review evidence (stale-team, injury, depth-order flags). 77 of 90 rows carry Sleeper IDs via the archived board's verified mapping with a GSIS fallback; the remainder are deep-roster backs that fall back to the normalized Fable source team.
- One defect was caught and fixed during implementation: the first insert joined Sleeper context on GSIS ID only, which is sparse in Sleeper, leaving stale teams displayed. The join now prefers the archived board's `player_id -> sleeper_player_id` mapping. The board rows were rebuilt with `--refresh-board-only` (delete + reinsert of the Fable rows only; registry and archive untouched).

## Owner Rulings Applied

| Ruling | Board result |
|---|---|
| Derrick Henry at Fable RB8 | Rank 8 (was Standard 20) |
| Breece Hall at Fable RB22 | Rank 22 (was 16) |
| Zach Charbonnet at Fable RB21 | Rank 21 (was 30) |
| Rico Dowdle trusted at Fable RB19 | Rank 19 (was 22), risk-flagged STALE_TEAM_CONTEXT_REVIEW and SLEEPER_DEPTH_ORDER_2 |
| Kenneth Gainwell trusted at Fable RB25 | Rank 25 (was 31), same two risk flags |
| James Conner not forced onto the board | Absent (no qualified 2025 Fable row; Sleeper lists him ARI RB3). Available in the archived fallback at 29 |
| Aaron Jones / Tony Pollard fades accepted | Ranks 34 / 35 (were 26 / 27) |

## New Active Standard RB Board — Top 40

| Rank | Player | Team | Tier | Score | Fable score | Prior rank | Move |
|---:|---|---|---|---:|---:|---:|---|
| 1 | Christian McCaffrey | SF | elite | 99.0 | 1.845 | 1 | — |
| 2 | Jonathan Taylor | IND | elite | 91.7 | 1.433 | 4 | +2 |
| 3 | Bijan Robinson | ATL | elite | 88.8 | 1.269 | 2 | -1 |
| 4 | Jahmyr Gibbs | DET | elite | 88.7 | 1.264 | 3 | -1 |
| 5 | Devon Achane | MIA | elite | 87.1 | 1.174 | 5 | — |
| 6 | James Cook | BUF | front-line starter | 85.9 | 1.110 | 7 | +1 |
| 7 | Javonte Williams | DAL | front-line starter | 84.8 | 1.046 | 9 | +2 |
| 8 | Derrick Henry | BAL | front-line starter | 83.8 | 0.989 | 20 | **+12** |
| 9 | Josh Jacobs | GB | front-line starter | 83.6 | 0.977 | 13 | +4 |
| 10 | Kyren Williams | LAR | front-line starter | 83.1 | 0.951 | 6 | -4 |
| 11 | Chase Brown | CIN | front-line starter | 81.5 | 0.861 | 8 | -3 |
| 12 | Saquon Barkley | PHI | front-line starter | 81.4 | 0.853 | 10 | -2 |
| 13 | Travis Etienne | NO | starter | 81.3 | 0.847 | 14 | +1 |
| 14 | Omarion Hampton | LAC | starter | 80.4 | 0.798 | 11 | -3 |
| 15 | Ashton Jeanty | LV | starter | 80.1 | 0.780 | 12 | -3 |
| 16 | Cam Skattebo | NYG | starter | 79.9 | 0.769 | 18 | +2 |
| 17 | D'Andre Swift | CHI | starter | 79.2 | 0.729 | 15 | -2 |
| 18 | Jaylen Warren | PIT | starter | 77.9 | 0.655 | 19 | +1 |
| 19 | Rico Dowdle | PIT | starter | 76.9 | 0.599 | 22 | +3 |
| 20 | Bucky Irving | TB | starter | 76.8 | 0.597 | 17 | -3 |
| 21 | Zach Charbonnet | SEA | starter | 76.1 | 0.558 | 30 | **+9** |
| 22 | Breece Hall | NYJ | starter | 76.0 | 0.549 | 16 | **-6** |
| 23 | Quinshon Judkins | CLE | starter | 76.0 | 0.548 | 21 | -2 |
| 24 | Kenneth Walker | KC | starter | 75.1 | 0.501 | 25 | +1 |
| 25 | Kenneth Gainwell | TB | starter | 75.0 | 0.495 | 31 | +6 |
| 26 | TreVeyon Henderson | NE | starter | 75.0 | 0.494 | 28 | +2 |
| 27 | J.K. Dobbins | DEN | starter | 73.8 | 0.427 | 23 | -4 |
| 28 | Tyrone Tracy | NYG | starter | 72.4 | 0.351 | 33 | +5 |
| 29 | Rhamondre Stevenson | NE | starter | 71.7 | 0.308 | 24 | -5 |
| 30 | Woody Marks | HOU | starter | 71.4 | 0.293 | 34 | +4 |
| 31 | R.J. Harvey | DEN | flex or matchup | 71.4 | 0.289 | 35 | +4 |
| 32 | Kimani Vidal | LAC | flex or matchup | 70.7 | 0.253 | 37 | +5 |
| 33 | Kyle Monangai | CHI | flex or matchup | 70.4 | 0.235 | 38 | +5 |
| 34 | Aaron Jones | MIN | flex or matchup | 69.7 | 0.199 | 26 | **-8** |
| 35 | Tony Pollard | TEN | flex or matchup | 69.7 | 0.196 | 27 | **-8** |
| 36 | Chris Rodriguez | WAS | flex or matchup | 69.1 | 0.163 | 48 | +12 |
| 37 | David Montgomery | HOU | flex or matchup | 68.8 | 0.145 | 39 | +2 |
| 38 | Jordan Mason | MIN | flex or matchup | 68.7 | 0.141 | 46 | +8 |
| 39 | Jacory Croskey-Merritt | WAS | flex or matchup | 68.5 | 0.131 | 45 | +6 |
| 40 | Rachaad White | TB | flex or matchup | 68.3 | 0.120 | 40 | — |

## Before/After Diff Summary vs Prior Current Standard

- Board size: 80 rows (LLM board) to 90 rows (all complete-score Fable RBs).
- Largest rises: Derrick Henry 20→8, Chris Rodriguez 48→36, Zach Charbonnet 30→21, Jordan Mason 46→38, Kenneth Gainwell 31→25.
- Largest falls: Aaron Jones 26→34, Tony Pollard 27→35, Breece Hall 16→22, Rhamondre Stevenson 24→29.
- Dropped from the board: James Conner (prior 29) and Trey Benson (prior 36) — no qualified 2025 Fable rows. Both remain in the archived fallback and can be manually reviewed at draft time; Sleeper lists both as Arizona depth (RB3/RB4) and Questionable.
- Rank agreement elsewhere is high: 24 of the prior top 30 remain within five slots.

## Explicitly Out Of Scope (untouched)

- QB, WR, TE boards: 180 active non-RB Standard rows verified unchanged.
- Half PPR, PPR, and GNG Keeper formulas and boards.
- The top-100 interleaver: it was not modified. If it reads the active Standard RB board it will pick up RB Fable v1 automatically; that behavior should be verified in its own phase before the next top-100 publish.
- No Cloud Run or app deployment occurred; promotion is data-layer only and deployment remains separately gated.

## Safety Confirmation

- No 2026 outcomes used anywhere; board inputs are 2025 source metrics, and the champion registration records `no_2026_outcomes: true`.
- Sleeper context appears only in display/review columns (`current_team`, `sleeper_*`, `risk_flags`); rank order is a pure function of `rb_fable_01_score`. A unit test enforces this.
- No market data entered the formula. No metrics were invented; broken tackles, YAC above expectation, and RB route metrics remain absent.
- No Gemini call. No Pigskin chat call. No model training. No deployment.
- Writes were gated behind `ALLOW_RB_FABLE_V1_STANDARD_RB_PROMOTION=true` and scoped by `position = 'RB' AND scoring_profile_id = 'standard'` in every mutating statement (unit-tested).

## Checks

- `venv\Scripts\python.exe -m py_compile scripts\promote_rb_fable_v1_standard_rb.py`: pass.
- `venv\Scripts\python.exe -m unittest` (promotion, Fable SQL contract, Sleeper context suites): all pass. Promotion tests cover Standard-RB-only scope, archive-before-deactivate ordering, idempotent archive, no-2026-outcome/no-invented-metric guards, Sleeper-display-only, and the write-gate name.
- Post-apply verification queries: prior board 80/80 in history and deactivated; 90 new active rows; zero other active Standard RB rows; 180 non-RB Standard rows untouched; exactly 1 active champion.
- `scripts/check_deployment_safety.py`: all checks passed.
- `scripts/run_bigquery_validations.py --dry-run`: discovery passed through validation 245.
- `git diff --check`: pass; existing line-ending warnings informational.

## Files Changed

- `scripts/promote_rb_fable_v1_standard_rb.py` (new)
- `tests/test_promote_rb_fable_v1_standard_rb.py` (new)
- this report

## Rollback

Set the Fable rows `is_active = FALSE`, restore `is_active = TRUE` on the `pigskin-llm-20260704071412` RB Standard rows (all still present in the live table and in history), and set the champion row `active = FALSE`. No data was deleted.
