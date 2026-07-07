# Standard BQML V2 Overall Board Rules

Phase 33.10 tested Standard-only overall board rules from the original Standard BQML v2 position finalists. This document is owner-review evidence. It is not a live ranking switch.

Current Pigskin remains live. No champion is active.

## Input Set

| Position | Finalist signal | Supporting signal |
|---|---|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | linear points and linear VOR |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | linear points and linear VOR |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` | linear points and linear VOR |
| TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` | linear points and linear VOR |

Evaluation used read-only `ML.PREDICT` against existing models and `ranking_backtest_feature_mart` for Standard 2024 validation and 2025 holdout rows. Actual outcomes were joined only after prediction.

## Candidate Rules

| Rule | Formula shape | Phase 33.10 read |
|---|---|---|
| `standard_current_pigskin_baseline_v0` | Current Pigskin proxy from feature-mart fields. | Baseline. Still live. |
| `standard_bqml_v2_vor_only_v0` | BQML linear VOR prediction as cross-position score. | Too risky. Combined top-100 and VOR capture trailed baseline. |
| `standard_bqml_v2_points_to_vor_v0` | BQML linear points minus replacement baseline. | Sensitive to replacement policy and weak in top-24/top-50. |
| `standard_bqml_v2_vor_plus_bust_safety_v0` | Predicted VOR plus bounded finalist safety or elite signal. | Better than VOR-only, still below overlay. |
| `standard_bqml_v2_cutline_value_v0` | Predicted VOR plus cutline scarcity bonus. | Improved top-24 but weaker points capture. |
| `standard_bqml_v2_conservative_overlay_v0` | 70 percent Current Pigskin, 20 percent BQML VOR, 10 percent finalist safety or elite score. | Best owner-review rule. |

## Replacement Policies

| Policy | Replacement ranks | Phase 33.10 result |
|---|---|---|
| `project_default_like` | Existing project-like baseline policy. | Same conservative-overlay result as the other policies. |
| `draft_paper_candidate` | QB15, RB36, WR55, TE12. | Test candidate only. Do not promote as truth. |
| `conservative_owner_review` | QB12, RB24, WR36, TE12. | Safer paper alternative. Points-to-VOR still underperformed the overlay. |

Replacement policy mostly changed the points-to-VOR rule. The conservative overlay was stable across policies because it used predicted VOR and finalist safety directly.

## Draft Priority Index

Draft Priority Index is display-only in this prototype. It is a 1-100 normalization derived from each candidate board rank, with the top player near 100. It was not used as the metric source of truth.

## Combined Results

| Rule | Top-24 | Top-50 | Top-100 | Points cap100 | VOR cap100 | Missing | Extreme top100 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Conservative overlay | 0.479 | 0.560 | 0.810 | 1.022 | 1.081 | 0.003 | 0 |
| Current Pigskin baseline | 0.417 | 0.550 | 0.810 | 1.001 | 1.074 | 0.003 | 0 |
| Cutline value | 0.479 | 0.550 | 0.810 | 0.991 | 1.032 | 0.003 | 0 |
| Points-to-VOR, conservative policy | 0.438 | 0.550 | 0.810 | 0.941 | 1.013 | 0.003 | 0 |
| VOR plus safety | 0.458 | 0.550 | 0.805 | 1.003 | 0.997 | 0.003 | 0 |
| VOR only | 0.438 | 0.550 | 0.790 | 0.985 | 0.973 | 0.003 | 0 |

The conservative overlay is the only rule that beats the baseline on top-24, top-50, points capture, and VOR capture while preserving baseline top-100 hit rate and avoiding extreme top-100 movement.

## Warnings

- This is a two-season prototype: 2024 validation and 2025 holdout.
- The 2025 RB VOR denominator remains thin in upstream position evidence.
- Several historical boards still surface low-volume names near important areas. The overlay reduces, but does not eliminate, that review burden.
- Summary-only persistence was not written because the repo does not yet have a tested overall-board evaluator contract for these cross-position rule families.
- The rule is Standard-only. It is not approved for Half PPR, PPR, or GNG Keeper.

## Decision

Final Phase 33.10 rule status: `STANDARD BQML V2 CONSERVATIVE OVERLAY READY`.

Meaning:

- Ready for owner champion-selection review.
- Not ready for live activation.
- Not ready for global scoring-profile expansion without separate profile-specific tests.
- Current Pigskin remains live.
