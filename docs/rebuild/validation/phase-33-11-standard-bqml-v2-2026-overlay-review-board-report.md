# Phase 33.11 Standard BQML V2 2026 Overlay Review Board Report

Final decision: STANDARD 2026 OVERLAY REVIEW BOARD READY WITH WARNINGS

## Scope

Phase 33.11 generated an outcome-free 2026 Standard owner-review board using the Phase 33.10 conservative overlay rule.

This phase did not train BQML models, create models, write live rankings, activate champions, call Gemini, call Pigskin chat, call Sleeper, deploy, run source ingest, run production ranking generation, overwrite candidate rankings, write `ranking_backtest_results`, write `ranking_formula_champions`, or write `analytics_pigskin_rankings`.

## Git State

Phase 33.10 was already committed before this phase:

- `953b7d8 phase 33.10 prototype standard overall board rules`
- `ba30f2d phase 33.10 record overall board package evidence`

Known untracked files remain historical validation backlog and owner-review artifacts. Generated evidence under `output/` is local only and was not staged.

## Live Standard Baseline

Read-only live ranking check:

| Position | Active rows | Ranking version | Latest generated at |
|---|---:|---|---|
| QB | 45 | `pigskin-llm-20260704071412` | 2026-07-04 07:15:26 UTC |
| RB | 80 | `pigskin-llm-20260704071412` | 2026-07-04 07:17:12 UTC |
| TE | 35 | `pigskin-llm-20260704071412` | 2026-07-04 07:21:00 UTC |
| WR | 100 | `pigskin-llm-20260704071412` | 2026-07-04 07:18:53 UTC |

Total active Standard rows: 260.

`ranking_formula_champions` count: 0.

## Input Method

The feature mart does not have a persisted 2026 target slice. The latest Standard feature-mart rows stop at target season 2025 with source windows ending 2024.

For this owner-review board:

- Active 2026 Standard Current Pigskin rows supplied the review universe and baseline ranks.
- Latest pre-2026 `ranking_backtest_feature_mart` rows supplied BQML predictors where available.
- Source rows required `source_window_end_season < 2026`.
- Sleeper current context was used only as display context.
- No 2026 outcome fields, target labels, actual ranks, Sleeper current context, or `pigskin_context_score` were used as predictors.

Read-only evidence generation:

| Item | Result |
|---|---:|
| Review version | `phase33_11_standard_2026_overlay_review` |
| Dry-run bytes | 57,609,511 |
| Review records | 260 |
| Rows by position | QB45, RB80, WR100, TE35 |
| Missing player IDs | 0 |
| Missing feature records | 82 |
| Leakage records | 0 |
| VOR unavailable rows | 0 |
| Finalist signal unavailable rows | 0 |
| Rank delta over 20 rows | 46 |
| Injury status flag rows | 30 |

Feature-family missingness:

| Family | Records | Missing feature records | Leakage records |
|---|---:|---:|---:|
| all | 260 | 82 | 0 |
| baseline candidate proxies | 260 | 82 | 0 |
| ideal xFP | 260 | 82 | 0 |
| PBP xFP | 260 | 82 | 0 |
| NGS | 260 | 92 | 0 |
| role history | 260 | 82 | 0 |

The first coverage query accidentally used `rows` as an alias and BigQuery rejected it. The check was rerun with neutral aliases and passed.

## Overlay Formula

Rule: `standard_bqml_v2_conservative_overlay_v0`.

Formula:

- 70 percent Current Pigskin normalized score.
- 20 percent BQML VOR normalized score.
- 10 percent BQML finalist safety or elite normalized score.

Finalist signals:

| Position | Finalist signal |
|---|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` |
| TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` |

Draft Priority Index is display-only.

## Board Summary

Owner-review artifact:

- `docs/rebuild/standard-bqml-v2-2026-conservative-overlay-review-board.md`

Generated local evidence:

- `output/phase-33-11-standard-2026-overlay-evidence.md`

Top-24 position mix:

| Position | Count |
|---|---:|
| QB | 9 |
| RB | 8 |
| WR | 5 |
| TE | 2 |

Top-50 position mix:

| Position | Count |
|---|---:|
| QB | 14 |
| RB | 14 |
| WR | 15 |
| TE | 7 |

Top-100 position mix:

| Position | Count |
|---|---:|
| QB | 21 |
| RB | 28 |
| WR | 33 |
| TE | 18 |

Top-24 entrants versus Current Pigskin:

- Jalen Hurts
- Kyren Williams
- Saquon Barkley
- Daniel Jones
- James Cook
- Dak Prescott
- Lamar Jackson
- Trevor Lawrence
- Brock Purdy

Top-24 exits versus Current Pigskin:

- Jaxon Smith-Njigba
- Drake London
- Chris Olave
- Brock Bowers
- Rashee Rice
- Garrett Wilson
- George Pickens
- Matthew Stafford
- Zay Flowers

## Movement Read

The board is inspectable, but movement is too aggressive for direct activation.

Main movement warnings:

- QB rises sharply: Jalen Hurts moves from 34 to 2, Lamar Jackson from 75 to 22.
- RB rises sharply: Saquon Barkley moves from 49 to 10, Derrick Henry from 91 to 43, several older RBs also rise.
- WR is pushed down in the early board: Jaxon Smith-Njigba moves from 1 to 27, Drake London from 8 to 30, Rashee Rice from 15 to 36.
- TE movement is mixed: Trey McBride stays high at 15 overall, while Brock Bowers falls from 13 to 32 with missing feature flags.
- 82 active Standard rows lack a feature-mart row. That includes rookies and other players without historical BQML context.

## Cutline Summary

Key cutline movement:

| Cutline | Entering | Leaving |
|---|---|---|
| QB12 | Lamar Jackson, Justin Herbert | Bo Nix, Caleb Williams |
| RB12 | Travis Etienne, Josh Jacobs, Breece Hall | Omarion Hampton, Ashton Jeanty, Chase Brown |
| Top 24 | 9 players entered | 9 players left |
| Top 50 | Lamar Jackson, Josh Jacobs, Travis Etienne, Breece Hall, Justin Herbert, Derrick Henry, D'Andre Swift, C.J. Stroud, Travis Kelce, Kyler Murray | multiple WR/TE-heavy current top-50 rows moved out |

Detailed cutline crossings are in `docs/rebuild/standard-bqml-v2-2026-conservative-overlay-review-board.md`.

## Owner Decision Recommendation

The 2026 Standard overlay board is inspectable and useful for owner review, but it is not ready for champion selection.

Recommended next phase:

- Phase 33.12: Refine Standard overall-board rule

Reason:

- The conservative overlay is still too responsive to VOR and bust-safety signals for QBs and RBs.
- WR/TE current-board anchors are demoted enough to require rule tuning.
- Missing feature rows are high enough that rookie and low-history players should receive a stronger baseline-protection policy.

Current Pigskin should hold for Standard.

## Files Changed

- `docs/rebuild/standard-bqml-v2-2026-conservative-overlay-review-board.md`
- `docs/rebuild/validation/phase-33-11-standard-bqml-v2-2026-overlay-review-board-report.md`
- `docs/rebuild/standard-bqml-v2-overall-board-rules.md`
- `docs/rebuild/standard-bqml-v2-owner-review-boards.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

## Checks

- `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract`: passed, 19 tests.
- `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py`: passed.
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed.
- `git diff --check`: passed. Git reported LF-to-CRLF working-copy warnings only.
- Feature-family coverage query: passed after replacing the reserved BigQuery alias `rows` with neutral alias `record_count`.

No full test suite was run. This phase changed owner-review docs only and used read-only BigQuery checks.

## No-Live-Change Confirmation

No live ranking rows changed. No champion row was written. No production ranking generation ran.
