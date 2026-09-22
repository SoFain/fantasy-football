# Phase 33.6 Standard BQML V2 Owner-Review Boards

Final decision: STANDARD BQML V2 OWNER REVIEW READY WITH WARNINGS

## Scope

Phase 33.6 generated Standard-only BQML v2 owner-review boards and cutline evidence from the existing Phase 33.5 trained models.

No model training ran. No live ranking table changed. No champion was activated. No Gemini call, Pigskin chat, Sleeper API call, source ingest, materialization, Cloud Run job, scheduler job, staging deploy, or production deploy occurred.

## Inputs

- Formula version: `ranking_backtest_sql_native_bqml_v2_standard_v0`
- Scoring profile: `standard`
- Validation season: 2024
- Holdout season: 2025
- Review limits: QB45, RB80, WR100, TE35
- Board artifact: `docs/rebuild/standard-bqml-v2-owner-review-boards.md`

## Git State

Phase 33.5 was already committed before this owner-review work:

- `cca365b phase 33.5 train standard bqml v2 models`

Phase 33.6 changed only documentation and owner-review board artifacts:

- `docs/rebuild/standard-bqml-v2-owner-review-boards.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/validation/phase-33-6-standard-bqml-v2-owner-review-boards-report.md`

The older historical validation backlog remains untracked owner-review material and was not staged.

## Selected Candidates

| Position | Candidate | Decision |
|---|---|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | Owner-review finalist with warnings. |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | Owner-review finalist with warnings. |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` | Owner-review finalist. |
| TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` | Owner-review finalist. |

TE note: Phase 33.5 listed `bqml_v2_standard_te_linear_points_v0` as the best combined TE lane. Phase 33.6 keeps linear points as component evidence but uses `bqml_v2_standard_te_logistic_bust_inverse_v0` as the TE owner-review finalist because the bust-inverse lane has stronger 2025 holdout VOR and non-null pairwise evidence.

## Generation Result

| Item | Result |
|---|---:|
| Weekly `ML.PREDICT` rows read | 8,088 |
| Player-season board rows | 783 |
| Selected candidate summary rows | 10 |
| Board rows written to live ranking tables | 0 |
| Champion rows written | 0 |
| Backtest detail rows written | 0 |

The board generator aggregated weekly prediction rows to one player-season row before ranking. The first draft exposed duplicate player rows because the BQML feature mart is weekly. The final board uses player-season aggregates for owner review.

## Summary Metrics

All 16 Standard BQML v2 candidates, combined 2024-2025 averages:

| Position | Candidate | Top-N | Points | VOR | Pairwise | Overall pairwise | NDCG | Bust |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| QB | `bqml_v2_standard_qb_linear_points_v0` | 0.685 | 0.819 | 0.710 | 0.818 | 0.818 | 0.787 | 0.049 |
| QB | `bqml_v2_standard_qb_linear_vor_v0` | 0.685 | 0.814 | 0.705 | null | null | 0.772 | 0.056 |
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | 0.688 | 0.822 | 0.712 | 0.675 | 0.676 | 0.783 | 0.051 |
| QB | `bqml_v2_standard_qb_logistic_elite_v0` | 0.681 | 0.815 | 0.702 | 0.700 | 0.700 | 0.776 | 0.051 |
| RB | `bqml_v2_standard_rb_linear_points_v0` | 0.814 | 0.893 | 0.725 | 0.956 | 0.957 | 0.784 | 0.027 |
| RB | `bqml_v2_standard_rb_linear_vor_v0` | 0.812 | 0.893 | 0.728 | 1.000 | 1.000 | 0.784 | 0.028 |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 0.817 | 0.898 | 0.736 | 0.798 | 0.803 | 0.786 | 0.025 |
| RB | `bqml_v2_standard_rb_logistic_elite_v0` | 0.815 | 0.893 | 0.716 | 0.810 | 0.813 | 0.782 | 0.025 |
| WR | `bqml_v2_standard_wr_linear_points_v0` | 0.630 | 0.749 | 0.687 | 0.958 | 0.946 | 0.651 | 0.137 |
| WR | `bqml_v2_standard_wr_linear_vor_v0` | 0.620 | 0.743 | 0.679 | null | null | 0.649 | 0.138 |
| WR | `bqml_v2_standard_wr_logistic_bust_inverse_v0` | 0.628 | 0.754 | 0.692 | 0.748 | 0.750 | 0.653 | 0.135 |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` | 0.631 | 0.756 | 0.696 | 0.763 | 0.761 | 0.654 | 0.134 |
| TE | `bqml_v2_standard_te_linear_points_v0` | 0.611 | 0.742 | 0.687 | null | null | 0.636 | 0.118 |
| TE | `bqml_v2_standard_te_linear_vor_v0` | 0.597 | 0.731 | 0.674 | null | null | 0.631 | 0.127 |
| TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` | 0.606 | 0.731 | 0.666 | 0.757 | 0.771 | 0.634 | 0.132 |
| TE | `bqml_v2_standard_te_logistic_elite_v0` | 0.609 | 0.731 | 0.665 | 0.766 | 0.779 | 0.635 | 0.125 |

Selected review candidates by season:

| Candidate | Season | Top-N | Points captured | VOR captured | Pairwise | Overall pairwise |
|---|---:|---:|---:|---:|---:|---:|
| `bqml_v2_standard_qb_logistic_bust_inverse_v0` | 2024 | 0.523 | 0.754 | 0.574 | 0.693 | 0.694 |
| `bqml_v2_standard_qb_logistic_bust_inverse_v0` | 2025 | 0.852 | 0.890 | 0.851 | 0.656 | 0.658 |
| `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 2024 | 0.634 | 0.796 | 0.736 | 0.781 | 0.785 |
| `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 2025 | 1.000 | 1.000 | null | 0.815 | 0.820 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2024 | 0.431 | 0.624 | 0.505 | 0.760 | 0.740 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2025 | 0.831 | 0.887 | 0.886 | 0.766 | 0.782 |
| `bqml_v2_standard_te_logistic_bust_inverse_v0` | 2024 | 0.454 | 0.620 | 0.497 | 0.764 | 0.775 |
| `bqml_v2_standard_te_logistic_bust_inverse_v0` | 2025 | 0.759 | 0.843 | 0.836 | 0.751 | 0.768 |
| `bqml_v2_standard_te_linear_points_v0` | 2024 | 0.463 | 0.652 | 0.551 | null | null |
| `bqml_v2_standard_te_linear_points_v0` | 2025 | 0.759 | 0.832 | 0.823 | null | null |

## No-Activation Verification

| Table | Relevant count |
|---|---:|
| `ranking_backtest_runs` for the Phase 33.5 formula version | 2 |
| `ranking_backtest_candidate_summaries` for the Phase 33.5 formula version | 32 |
| `ranking_backtest_results` for the Phase 33.5 formula version | 0 |
| `ranking_formula_champions` | 0 |
| `analytics_pigskin_rankings` Standard rows | 285 |

The 285 Standard live ranking rows are existing current-state rows. Phase 33.6 did not write to `analytics_pigskin_rankings`.

## Cutline Review

The board file includes cutline checks for:

- QB12, QB24, QB45
- RB12, RB24, RB36, RB48, RB80
- WR12, WR24, WR36, WR48, WR60, WR100
- TE6, TE12, TE18, TE35

The cutline audit is useful, but not clean enough for activation. Some finalist boards place unintuitive names near important cutlines. That is review evidence, not a production board.

## Warnings

- All 16 Standard v2 candidates are viable research evidence, but Phase 33.6 only chooses owner-review finalists. It does not pick a champion.
- QB has no clean winner. Linear points has stronger pairwise summary evidence, while logistic bust inverse has the best combined VOR and points capture. Keep both visible in owner review.
- QB Standard v2 remains weaker than prior QB BQML linear-points evidence.
- RB 2025 VOR capture is null because the denominator is unavailable or zero in that slice.
- TE finalist selection differs from the Phase 33.5 combined-scorecard label. The change is intentional for owner review.
- The board is position-specific. It is not a profile-wide overall board builder.
- A production-grade Standard overall board still needs an owner-approved VOR, scarcity, and cutline rule.
- Deferred feature-mart patch work remains for EPA, receiving yards, red-zone targets, red-zone opportunities, and goal-line opportunities.

## Documentation Updated

- `docs/rebuild/standard-bqml-v2-owner-review-boards.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

## Checks

Passed:

- `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract`: passed, 19 tests.
- `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py`: passed.
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed.
- `git diff --check`: passed with existing line-ending warnings for touched markdown files.

## Recommended Next Phase

Phase 33.7 should run an owner-review decision pass:

- decide whether Standard v2 should remain research-only;
- decide whether to patch the feature mart before more BQML work;
- define the Standard overall-board rule if owner wants a champion-selection path;
- keep Current Pigskin live until a separate activation phase.
