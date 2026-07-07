# BQML V2 Positional Formula Finalists

This document tracks position-specific BQML v2 formula candidates by scoring profile. It is owner-review evidence only.

Current Pigskin remains live. No formula champion is active. No top-100 interleaver is selected here.

## Architecture Rule

V2.0 positional formulas are position-locked:

- QB formulas rank QBs.
- RB formulas rank RBs.
- WR formulas rank WRs.
- TE formulas rank TEs.

A future top-100 builder may decide which position queue to pull from, but it must not reorder players inside a position.

## Standard

Standard finalists remain the Phase 33.9 original Standard v2 set.

| Position | Finalist | Status |
|---|---|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | owner-review finalist |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | owner-review finalist |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` | owner-review finalist |
| TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` | owner-review finalist |

Warning: Standard cross-position overlay work remains separate. Phase 33.12 selected a safer 80/15/5 anchored review board, but Current Pigskin still holds.

## Half PPR

Phase 33.13 trained 16 Half PPR position-specific models.

| Position | Finalist | Status | Combined read |
|---|---|---|---|
| QB | `bqml_v2_half_ppr_qb_linear_points_v0` | owner-review finalist with warnings | Best combined points/VOR/NDCG score in the Half PPR QB set. |
| RB | `bqml_v2_half_ppr_rb_linear_points_v0` | owner-review finalist with warnings | Tied closely with linear VOR; points model is clearer for profile-specific fantasy scoring. |
| WR | `bqml_v2_half_ppr_wr_logistic_bust_inverse_v0` | owner-review finalist with warnings | Slight edge over linear points by combined VOR and NDCG. |
| TE | `bqml_v2_half_ppr_te_linear_vor_v0` | owner-review finalist with warnings | Tied closely with linear points; VOR model fits TE positional scarcity better. |

## PPR

Phase 33.13 trained 16 PPR position-specific models.

| Position | Finalist | Status | Combined read |
|---|---|---|---|
| QB | `bqml_v2_ppr_qb_linear_points_v0` | owner-review finalist with warnings | Best combined PPR QB score in this first pass. |
| RB | `bqml_v2_ppr_rb_linear_points_v0` | owner-review finalist with warnings | Best PPR RB points capture in the candidate set. |
| WR | `bqml_v2_ppr_wr_logistic_elite_v0` | owner-review finalist with warnings | Best PPR WR combined read by the selection score. |
| TE | `bqml_v2_ppr_te_linear_points_v0` | owner-review finalist with warnings | Linear points and VOR are close; points is the simpler first owner-review candidate. |

## GNG Keeper

Phase 33.13 trained 16 GNG Keeper position-specific models.

| Position | Finalist | Status | Combined read |
|---|---|---|---|
| QB | `bqml_v2_gng_keeper_qb_linear_points_v0` | owner-review finalist with warnings | Best combined GNG Keeper QB score in this first pass. |
| RB | `bqml_v2_gng_keeper_rb_logistic_elite_v0` | owner-review finalist with warnings | Strongest GNG Keeper RB combined read. |
| WR | `bqml_v2_gng_keeper_wr_linear_points_v0` | owner-review finalist with warnings | Slight edge over bust inverse and linear VOR. |
| TE | `bqml_v2_gng_keeper_te_linear_points_v0` | owner-review finalist with warnings | Linear points and VOR are effectively tied; points is clearer for owner review. |

## Warnings

- Phase 33.13 summary metrics are position-specific. They do not choose an overall board.
- The first-pass metric scale is low because the evaluator averages top-N hits across the full position universe. Use it for candidate comparison inside the same profile and position, not as a public accuracy claim.
- Missing-input rates remain near 0.52 to 0.57 across many profile-position slices.
- No Standard fallback was used for Half PPR, PPR, or GNG Keeper labels.
- Bust models are inverted for ranking: higher score means safer.

## Next Phase

Recommended next phase: Phase 33.14 profile-specific positional owner-review boards.
