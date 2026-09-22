# Phase 33.10 Standard BQML V2 Overall-Board Rule Report

Final decision: STANDARD BQML V2 CONSERVATIVE OVERLAY READY

## Scope

Phase 33.10 tested Standard-only overall draft-board rules that combine the selected QB/RB/WR/TE Standard BQML v2 finalists into one cross-position owner-review board.

This phase did not train BQML models, create models, write live rankings, activate champions, call Gemini, call Pigskin chat, call Sleeper, deploy, run source ingest, overwrite candidate rankings, write `ranking_backtest_results`, write `ranking_formula_champions`, or write `analytics_pigskin_rankings`.

## Git State

Phase 33.9 was already committed before this phase:

- `0f4cd42 phase 33.9 review standard bqml v2 finalists`

Phase 33.10 documentation package commit:

- `953b7d8 phase 33.10 prototype standard overall board rules`

Known untracked files remain historical validation backlog and owner-review artifacts. Generated evidence under `output/` is local only and was not staged.

## Input Audit

| Position | Finalist |
|---|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` |
| TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` |

Read-only evidence generation:

| Item | Result |
|---|---:|
| Dry-run bytes | 10,839,573 |
| Signal rows | 26,436 |
| Player-season records | 642 |
| Rule rows evaluated | 11,556 |

Evidence file:

- `output/phase-33-10-standard-overall-board-rules-evidence.md`

This file is generated local evidence and should not be committed.

## Candidate Rules

| Rule | Purpose | Result |
|---|---|---|
| `standard_current_pigskin_baseline_v0` | Baseline Current Pigskin board. | Live baseline. |
| `standard_bqml_v2_vor_only_v0` | Pure BQML VOR board. | Too risky. |
| `standard_bqml_v2_points_to_vor_v0` | Paper-style points minus replacement baseline. | Sensitive and weaker early. |
| `standard_bqml_v2_vor_plus_bust_safety_v0` | VOR plus bounded safety or elite signal. | Better than VOR-only, not best. |
| `standard_bqml_v2_cutline_value_v0` | VOR plus scarcity/cutline bonus. | Top-24 lift, weaker points capture. |
| `standard_bqml_v2_conservative_overlay_v0` | Current Pigskin plus VOR plus safety. | Best owner-review rule. |

Conservative overlay formula shape:

- 70 percent Current Pigskin normalized score.
- 20 percent BQML VOR score.
- 10 percent BQML finalist safety or elite score.

## Replacement Policies

| Policy | Ranks tested | Result |
|---|---|---|
| `project_default_like` | Existing project-like baseline policy. | Overlay stable. |
| `draft_paper_candidate` | QB15/RB36/WR55/TE12. | Test candidate only. |
| `conservative_owner_review` | QB12/RB24/WR36/TE12. | Safer policy, but points-to-VOR still lagged. |

Replacement policy mostly affected `standard_bqml_v2_points_to_vor_v0`. It did not change the selected overlay result.

## Draft Priority Index

Draft Priority Index was calculated as a display-only 1-100 rank-derived score. It was not used to evaluate the rules.

## Combined Results

| Rule | Top-24 | Top-50 | Top-100 | Points cap100 | VOR cap100 | Missing | Extreme top100 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Conservative overlay | 0.479 | 0.560 | 0.810 | 1.022 | 1.081 | 0.003 | 0 |
| Current Pigskin baseline | 0.417 | 0.550 | 0.810 | 1.001 | 1.074 | 0.003 | 0 |
| Cutline value | 0.479 | 0.550 | 0.810 | 0.991 | 1.032 | 0.003 | 0 |
| Points-to-VOR | 0.438 | 0.550 | 0.810 | 0.941 | 1.013 | 0.003 | 0 |
| VOR plus safety | 0.458 | 0.550 | 0.805 | 1.003 | 0.997 | 0.003 | 0 |
| VOR only | 0.438 | 0.550 | 0.790 | 0.985 | 0.973 | 0.003 | 0 |

The conservative overlay is the only rule that improved top-24, top-50, points capture, and VOR capture while preserving baseline top-100 and avoiding extreme top-100 movement.

## Holdout Result

| Rule | Top-24 | Top-50 | Top-100 | Points cap100 | VOR cap100 | Top-24 balance |
|---|---:|---:|---:|---:|---:|---|
| 2025 conservative overlay | 0.500 | 0.660 | 1.000 | 1.051 | 1.059 | QB5, RB14, WR3, TE2 |
| 2025 Current Pigskin baseline | 0.458 | 0.640 | 1.000 | 1.014 | 1.022 | RB14, QB4, WR5, TE1 |
| 2024 conservative overlay | 0.458 | 0.460 | 0.620 | 0.992 | 1.103 | QB4, RB20 |
| 2024 Current Pigskin baseline | 0.375 | 0.460 | 0.620 | 0.988 | 1.125 | RB21, QB3 |

The overlay improves early-board hit rate in both seasons. The 2024 VOR capture still favors Current Pigskin, so this is not activation evidence by itself.

## Cutline Evaluation

Cutlines reviewed:

- QB6/QB12
- RB6/RB12/RB18/RB24/RB36
- WR12/WR24/WR36/WR48
- TE3/TE6/TE12/TE18/TE35

Notable reads:

- 2024 top 24 is heavy RB with four QBs.
- 2025 top 24 is more balanced: QB5, RB14, WR3, TE2.
- TE appears inside the 2025 top 50, but 2024 TE starts later.
- WR remains lower than a human draft board may expect in early Standard output. This needs owner review.

## Summary-Only Write Decision

No summary rows were written.

Reason: the current repo evaluator does not expose a tested summary-only overall-board contract for this cross-position rule family. The prototype uses local rule assembly over read-only `ML.PREDICT` outputs. Forcing a manual write into `ranking_backtest_candidate_summaries` would risk inconsistent metric semantics.

## Owner-Readable Board Examples

The generated evidence includes:

- top 50 Current Pigskin 2024 and 2025 boards
- top 50 conservative overlay 2024 and 2025 boards
- VOR-only and VOR-plus-safety comparisons
- cutline top sets for the conservative overlay

## Decision

Standard BQML v2 can move to owner champion-selection review only as a conservative overlay candidate.

Do not activate VOR-only. Do not activate points-to-VOR. Do not promote the paper replacement baselines as defaults.

Recommended next phase:

- Phase 33.11: Standard BQML v2 champion-selection review

Alternate next phase:

- Generate a 2026 Standard owner-review board from the conservative overlay.

## Files Changed

- `docs/rebuild/validation/phase-33-10-standard-bqml-v2-overall-board-rule-report.md`
- `docs/rebuild/standard-bqml-v2-overall-board-rules.md`
- `docs/rebuild/standard-bqml-v2-owner-review-boards.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

## Checks

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract` | PASS, 19 tests. PowerShell reported native stderr as `NativeCommandError`, but the process exit code was 0. |
| `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py` | PASS |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS |
| `git diff --check` | PASS, with Git LF-to-CRLF working-copy warnings only |
