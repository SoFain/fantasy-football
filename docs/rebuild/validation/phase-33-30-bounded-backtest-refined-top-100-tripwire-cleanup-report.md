# Phase 33.30 Bounded Backtest Refined Top-100 Tripwire Cleanup Report

Final decision: `REFINED TOP-100 NEEDS TARGETED QB/WR CLEANUP`.

The bounded historical proxy backtest does not support live activation of the refined top-100. It is still useful for owner review, but Current Pigskin or a Pigskin-heavy conservative variant remains the safer live baseline until QB and WR tripwires are cleaned up and a prospect-lane policy exists.

## Files Changed

- `docs/rebuild/validation/phase-33-30-bounded-backtest-refined-top-100-tripwire-cleanup-report.md`
- `docs/rebuild/position-locked-top-100-interleaver-plan.md`
- `docs/rebuild/advanced-bqml-v2-owner-review-boards.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `output/phase-33-30-bounded-backtest-evidence.json`

## Git State

The worktree was already dirty with Phase 33 artifacts. This phase did not stage files or revert unrelated work.
- Status rows observed: `28`

## Bounded Backtest Scope

- Source: `ranking_backtest_feature_mart`.
- Target seasons: 2024 validation and 2025 holdout.
- Target week: 18 only, one player-season row per player/profile/position.
- Scoring profiles: standard, half_ppr, ppr, gng_keeper.
- Rows evaluated: `1,464`.
- No 2026 outcomes queried or used.
- The exact 2026 owner-review queues do not exist point-in-time for 2024/2025, so this is a source-window proxy backtest, not a perfect replay.

## Metrics Table By Profile

| Profile | Variant | Top24 | Top50 | Top100 | Points | VOR | NDCG | Pairwise | Regret | Elite Miss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GNG Keeper | Conservative Pigskin-heavy proxy | 0.250 | 0.520 | 0.685 | 0.792 | 0.800 | 0.455 | 0.591 | 38.1 | 12.5 |
| GNG Keeper | Current Pigskin proxy | 0.250 | 0.520 | 0.685 | 0.815 | 0.836 | 0.468 | 0.584 | 38.4 | 12.5 |
| GNG Keeper | Phase 33.26C proxy | 0.250 | 0.530 | 0.680 | 0.795 | 0.814 | 0.460 | 0.604 | 37.6 | 12.0 |
| GNG Keeper | Refined 33.28 proxy | 0.271 | 0.540 | 0.675 | 0.790 | 0.808 | 0.459 | 0.610 | 38.3 | 11.5 |
| Half PPR | Conservative Pigskin-heavy proxy | 0.229 | 0.510 | 0.670 | 0.806 | 0.811 | 0.492 | 0.571 | 38.4 | 13.0 |
| Half PPR | Current Pigskin proxy | 0.229 | 0.520 | 0.680 | 0.815 | 0.818 | 0.495 | 0.563 | 37.0 | 12.5 |
| Half PPR | Phase 33.26C proxy | 0.208 | 0.540 | 0.680 | 0.791 | 0.779 | 0.482 | 0.587 | 36.1 | 12.5 |
| Half PPR | Refined 33.28 proxy | 0.208 | 0.530 | 0.670 | 0.787 | 0.779 | 0.485 | 0.591 | 37.2 | 12.5 |
| PPR | Conservative Pigskin-heavy proxy | 0.271 | 0.500 | 0.680 | 0.812 | 0.821 | 0.493 | 0.577 | 38.1 | 12.0 |
| PPR | Current Pigskin proxy | 0.271 | 0.500 | 0.685 | 0.817 | 0.821 | 0.493 | 0.573 | 37.4 | 12.0 |
| PPR | Phase 33.26C proxy | 0.250 | 0.520 | 0.680 | 0.795 | 0.789 | 0.505 | 0.594 | 36.7 | 11.5 |
| PPR | Refined 33.28 proxy | 0.250 | 0.520 | 0.675 | 0.789 | 0.783 | 0.505 | 0.598 | 37.9 | 11.5 |
| Standard | Conservative Pigskin-heavy proxy | 0.271 | 0.490 | 0.660 | 0.792 | 0.797 | 0.481 | 0.571 | 39.5 | 13.0 |
| Standard | Current Pigskin proxy | 0.271 | 0.490 | 0.670 | 0.799 | 0.796 | 0.481 | 0.563 | 38.3 | 13.0 |
| Standard | Phase 33.26C proxy | 0.250 | 0.490 | 0.665 | 0.766 | 0.758 | 0.461 | 0.587 | 39.2 | 13.0 |
| Standard | Refined 33.28 proxy | 0.271 | 0.490 | 0.660 | 0.765 | 0.758 | 0.462 | 0.586 | 39.4 | 13.0 |

## Comparison Against Current Pigskin

The refined proxy does not cleanly beat the Current Pigskin proxy. Current Pigskin proxy has stronger points/VOR capture in Standard, Half PPR, PPR, and GNG Keeper. Refined proxy improves or ties some top-24 and pairwise readings, but that is not enough to move toward live use.

## Refined RB Queue Backtest

| Profile | Variant | RB Top6 | RB Top12 | RB Top24 | RB Points | RB VOR | RB NDCG | RB Pairwise | Elite Miss | Prospect Exposure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GNG Keeper | Current Pigskin proxy | 0.500 | 0.708 | 0.625 | 0.841 | 0.329 | 0.296 | 0.691 | 2.000 | 2.000 |
| GNG Keeper | Phase 33.26C proxy | 0.417 | 0.667 | 0.688 | 0.901 | 0.398 | 0.324 | 0.631 | 1.000 | 1.500 |
| GNG Keeper | RB receiving-aware diagnostic | 0.500 | 0.708 | 0.646 | 0.861 | 0.359 | 0.306 | 0.679 | 1.500 | 2.000 |
| GNG Keeper | Refined 33.28 proxy | 0.500 | 0.708 | 0.646 | 0.861 | 0.359 | 0.307 | 0.682 | 1.500 | 2.000 |
| Half PPR | Current Pigskin proxy | 0.583 | 0.708 | 0.667 | 0.884 | 0.380 | 0.312 | 0.677 | 2.000 | 2.000 |
| Half PPR | Phase 33.26C proxy | 0.500 | 0.667 | 0.667 | 0.911 | 0.421 | 0.328 | 0.652 | 1.500 | 1.500 |
| Half PPR | RB receiving-aware diagnostic | 0.583 | 0.708 | 0.667 | 0.906 | 0.421 | 0.329 | 0.664 | 1.500 | 2.000 |
| Half PPR | Refined 33.28 proxy | 0.583 | 0.708 | 0.667 | 0.903 | 0.421 | 0.334 | 0.670 | 1.500 | 2.000 |
| PPR | Current Pigskin proxy | 0.583 | 0.708 | 0.667 | 0.877 | 0.372 | 0.281 | 0.708 | 2.000 | 2.000 |
| PPR | Phase 33.26C proxy | 0.500 | 0.667 | 0.688 | 0.912 | 0.408 | 0.318 | 0.657 | 1.500 | 1.500 |
| PPR | RB receiving-aware diagnostic | 0.583 | 0.708 | 0.688 | 0.906 | 0.408 | 0.324 | 0.676 | 1.500 | 1.500 |
| PPR | Refined 33.28 proxy | 0.583 | 0.708 | 0.688 | 0.902 | 0.408 | 0.329 | 0.685 | 1.500 | 2.000 |
| Standard | Current Pigskin proxy | 0.500 | 0.667 | 0.646 | 0.873 | 0.370 | 0.316 | 0.671 | 2.000 | 2.000 |
| Standard | Phase 33.26C proxy | 0.417 | 0.625 | 0.667 | 0.908 | 0.413 | 0.330 | 0.635 | 1.500 | 1.500 |
| Standard | RB receiving-aware diagnostic | 0.500 | 0.667 | 0.667 | 0.905 | 0.413 | 0.330 | 0.640 | 1.500 | 2.000 |
| Standard | Refined 33.28 proxy | 0.417 | 0.667 | 0.667 | 0.905 | 0.413 | 0.328 | 0.632 | 1.500 | 2.000 |

RB finding: the refined RB proxy improves 2026 sanity and generally keeps RB top-12/top-24 hit rates competitive, but it does not clearly beat the original advanced RB proxy on every historical metric. It is a review improvement, not live proof.

## Remaining Tripwire Audit

| Profile | Player | Pos | Current | Prototype | Queue Rank | Class | Fix | Blocks Owner Review | Blocks Live Use |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| All | Jeremiyah Love | RB | none | none | none | market/prospect lane issue | prospect lane | No | Yes |
| All | Breece Hall | varies | not a Phase 33.29 tripwire | see Phase 33.28 board | see Phase 33.28 board | manual review required | targeted queue refresh | No | Yes |
| Standard | Patrick Mahomes | QB | 10 | 53 | 6 | interleaver issue | QB anchor/cap review | No | Yes |
| Half PPR | Patrick Mahomes | QB | 11 | 64 | 6 | interleaver issue | QB anchor/cap review | No | Yes |
| PPR | Patrick Mahomes | QB | 9 | 56 | 6 | interleaver issue | QB anchor/cap review | No | Yes |
| Standard | Rashee Rice | WR | 15 | 95 | 30 | position-board issue | WR board review | No | Yes |
| Half PPR | Rashee Rice | WR | 16 | 91 | 29 | position-board issue | WR board review | No | Yes |
| PPR | Rashee Rice | WR | 17 | 88 | 28 | position-board issue | WR board review | No | Yes |
| GNG Keeper | Rashee Rice | WR | 22 | 96 | 34 | position-board issue | WR board review | No | Yes |
| Standard | Matthew Stafford | QB | 22 | 101 | outside top 100 | interleaver issue | QB anchor/cap review | No | Yes |
| Half PPR | Matthew Stafford | QB | 45 | 101 | outside top 100 | interleaver issue | QB anchor/cap review | No | No |
| PPR | Matthew Stafford | QB | 25 | 101 | outside top 100 | interleaver issue | QB anchor/cap review | No | No |
| GNG Keeper | Matthew Stafford | QB | 21 | 51 | 9 | interleaver issue | QB anchor/cap review | No | Yes |
| Standard | Drake Maye | QB | 9 | 35 | 5 | interleaver issue | QB anchor/cap review | No | Yes |
| Half PPR | Drake Maye | QB | 8 | 34 | 5 | interleaver issue | QB anchor/cap review | No | Yes |
| PPR | Drake Maye | QB | 7 | 39 | 5 | interleaver issue | QB anchor/cap review | No | Yes |
| Standard | Jaxon Smith-Njigba | WR | 1 | 19 | 8 | position-board issue | WR board review | No | Yes |
| GNG Keeper | Jaxon Smith-Njigba | WR | 5 | 21 | 8 | position-board issue | WR board review | No | Yes |
| Standard | Chris Olave | WR | 13 | 75 | 22 | position-board issue | WR board review | No | Yes |
| Standard | Tetairoa McMillan | WR | 35 | 99 | 34 | position-board issue | WR board review | No | No |
| Half PPR | Tetairoa McMillan | WR | 40 | 98 | 36 | position-board issue | WR board review | No | No |
| PPR | Tetairoa McMillan | WR | 46 | 97 | 37 | position-board issue | WR board review | No | No |
| Standard | Wan'Dale Robinson | WR | 37 | 101 | outside top 100 | position-board issue | WR board review | No | No |
| Half PPR | Wan'Dale Robinson | WR | 39 | 95 | 33 | position-board issue | WR board review | No | No |
| PPR | Wan'Dale Robinson | WR | 45 | 90 | 30 | position-board issue | WR board review | No | No |
| GNG Keeper | Nico Collins | WR | 47 | 88 | 27 | position-board issue | WR board review | No | No |
| All | Jaylen Waddle | varies | not a Phase 33.29 tripwire | see Phase 33.28 board | see Phase 33.28 board | acceptable model disagreement | manual review | No | Yes |

## Jeremiyah Love Decision

Jeremiyah Love remains a market-only prospect. He has no active Current Pigskin row and no selected RB feature queue row. Do not force him into rankings. He does not block owner review, but he blocks live top-100 advancement until a prospect lane exists or the owner explicitly rejects market-only prospect influence.

## Half PPR Breece Hall Decision

Breece Hall is stale Current Pigskin context. Phase 33.27 evidence used Half PPR RB18, while the current active table had him RB6 and the prototype had him RB16. Owner review can proceed with that warning, but live approval needs a targeted Current Pigskin refresh and regenerated RB evidence.

## Patrick Mahomes And QB Decision

Mahomes and the other QB warnings point to the interleaver, not just the QB queue. A one-QB top-100 can discount quarterback scarcity, but pushing Current Pigskin top-12 QBs outside the allowed range needs a QB anchor or top-24 cap review before live use.

## Rashee Rice And WR Decision

Rashee Rice is a WR position-board warning. The guarded WR queue is too far from Current Pigskin for live approval. The next cleanup should test a WR elite tripwire or a Current Pigskin anchor for high-ranked WRs with no source-backed demotion reason.

## Candidate Decision

Decision B: refined top-100 needs targeted QB/WR tripwire cleanup before another review. Current Pigskin holds for live use.

## Safety Confirmations

- No live ranking writes.
- No champion activation.
- No model training.
- No deployment.
- No Gemini call.
- No Pigskin chat call.
- No 2026 outcomes used.
- Route metrics remain blocked/null.
- No market data used as a training target.

## Checks Run

| Check | Result |
| --- | --- |
| Bounded SQL proxy evaluator | PASS, 1,464 season-end rows |
| `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract` | PASS, 26 tests |
| `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py` | PASS |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | PASS, discovered 251 validation files |
| Focused top-100 backtest checks | PASS |
| Focused tripwire checks | PASS |
| Focused RB queue checks | PASS |
| `git diff --check` | PASS with existing LF-to-CRLF warning on `docs/rebuild/bqml-v2-positional-formula-finalists.md` |

## Recommended Next Phase

Phase 33.31: Targeted QB/WR tripwire cleanup, including QB anchor/cap review, WR elite tripwire review, Breece Hall stale-context refresh, and a prospect lane policy for market-only players.
