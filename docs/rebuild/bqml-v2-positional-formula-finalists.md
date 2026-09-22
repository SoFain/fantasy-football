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

| Position | Advanced owner-review finalist | Prior Finalist (Phase 33.13) | Status | Notes |
|---|---|---|---|---|
| QB | `adv_standard_qb_logistic_bust` | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | owner-review finalist | High correlation (`0.4550`) and de-correlated bust risk protection. |
| RB | `adv_standard_rb_linear_points` | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | owner-review finalist | Linear points captures raw scoring patterns exceptionally well. |
| WR | `adv_standard_wr_logistic_elite` | `bqml_v2_standard_wr_logistic_elite_v0` | owner-review finalist | Elite probability model yields robust intermediate target-earning metrics. |
| TE | `adv_standard_te_linear_points` | `bqml_v2_standard_te_logistic_bust_inverse_v0` | owner-review finalist with warnings | Warning: validation (2024) correlation declined by `-0.0342` (`0.4687` vs `0.5029`) despite holdout improvement. |

*Warning*: Standard cross-position overlay work remains separate. Phase 33.12 selected a safer 80/15/5 anchored review board, but Current Pigskin still holds.

## Half PPR

| Position | Advanced owner-review finalist | Prior Finalist (Phase 33.13) | Status | Notes |
|---|---|---|---|---|
| QB | `adv_half_ppr_qb_logistic_bust` | `bqml_v2_half_ppr_qb_linear_points_v0` | owner-review finalist | Inverted bust risk model achieves highest rank correlation (`0.4550`). Baseline evaluator incompatible. |
| RB | `adv_half_ppr_rb_linear_vor` | `bqml_v2_half_ppr_rb_linear_points_v0` | owner-review finalist | VOR model aligns closely with positional scarcity in Half PPR. Baseline evaluator incompatible. |
| WR | `adv_half_ppr_wr_logistic_elite` | `bqml_v2_half_ppr_wr_logistic_bust_inverse_v0` | owner-review finalist | Elite finish model outperforms bust inverse on target capture. Baseline evaluator incompatible. |
| TE | `adv_half_ppr_te_logistic_elite` | `bqml_v2_half_ppr_te_linear_vor_v0` | component signal | Low TE combined correlation. Recommended as component signal only. Baseline evaluator incompatible. |

## PPR

| Position | Advanced owner-review finalist | Prior Finalist (Phase 33.13) | Status | Notes |
|---|---|---|---|---|
| QB | `adv_ppr_qb_logistic_bust` | `bqml_v2_ppr_qb_linear_points_v0` | owner-review finalist | Stable bust prediction improves holdout correlation (`0.4501`). Baseline evaluator incompatible. |
| RB | `adv_ppr_rb_logistic_elite` | `bqml_v2_ppr_rb_linear_points_v0` | owner-review finalist | Logistic elite model captures high-volume receiving RBs. Baseline evaluator incompatible. |
| WR | `adv_ppr_wr_logistic_elite` | `bqml_v2_ppr_wr_logistic_elite_v0` | owner-review finalist | Maintains elite-level volume tracking. Baseline evaluator incompatible. |
| TE | `adv_ppr_te_logistic_bust` | `bqml_v2_ppr_te_linear_points_v0` | component signal | Low TE combined correlation. Recommended as component signal only. Baseline evaluator incompatible. |

## GNG Keeper

| Position | Advanced owner-review finalist | Prior Finalist (Phase 33.13) | Status | Notes |
|---|---|---|---|---|
| QB | `adv_gng_keeper_qb_linear_points` | `bqml_v2_gng_keeper_qb_linear_points_v0` | owner-review finalist with warnings | Warning: combined predictive correlation remains below 0.45 (`0.4217`). Baseline evaluator incompatible. |
| RB | `adv_gng_keeper_rb_linear_points` | `bqml_v2_gng_keeper_rb_logistic_elite_v0` | owner-review finalist | Linear points regression provides the clearest baseline. Baseline evaluator incompatible. |
| WR | `adv_gng_keeper_wr_logistic_bust` | `bqml_v2_gng_keeper_wr_linear_points_v0` | owner-review finalist | Bust risk model prevents selecting regression-heavy WRs. Baseline evaluator incompatible. |
| TE | `adv_gng_keeper_te_logistic_bust` | `bqml_v2_gng_keeper_te_linear_points_v0` | component signal | Low TE combined correlation. Recommended as component signal only. Baseline evaluator incompatible. |

## Verification & Warnings

- **Route Metrics**: **ROUTE METRICS REMAIN BLOCKED**. Sourcing routes run/YPRR is blocked due to the lack of player-level routing denominators in nflverse.
- **Top-100**: Positional models do not define an overall board. Top-100 rank merges will be handled separately.
- **Missing-Input Rates**: Reduced to 0% in advanced features through leakage-safe imputation.
- **Bust Model Inversion**: Inverted for ranking: higher score means safer.
- **Evaluator Mismatch**: Baselines for `half_ppr`, `ppr`, and `gng_keeper` are evaluator-incompatible. Direct point or VOR capture comparison with Phase 33.13 baseline records is mathematically invalid.

## Next Phase

Recommended next phase: **Phase 33.20 — Owner review of advanced positional boards**.

## Phase 33.19 Advanced BQML v2 Owner-Review Boards

Phase 33.19 generated owner-review boards for the 16 positional BQML v2 finalists and alternates using active 2026 player contexts, without live ranking updates or champion promotion.

Selected Finalist Models & alternates:
- **Standard**: QB (`logistic_bust`, alt `linear_points`), RB (`linear_points`, alt `logistic_bust` warning), WR (`logistic_elite`), TE (`linear_points`, alt `logistic_bust` warning).
- **Half PPR**: QB (`logistic_bust`), RB (`linear_vor`, alt `linear_points` warning), WR (`logistic_elite`), TE (`logistic_elite`).
- **PPR**: QB (`logistic_bust`, alt `linear_points` strength), RB (`logistic_elite`, alt `linear_points` strength), WR (`logistic_elite`), TE (`logistic_bust`).
- **GNG Keeper**: QB (`linear_points` warning), RB (`linear_points`), WR (`logistic_bust`, alt `linear_points`), TE (`logistic_bust`).

Key features from pre-2026 contexts were integrated with 0% missingness via leakage-safe rolling averages (2023-2025). Route metrics remain strictly **BLOCKED** and mapped to `NULL`.

## Phase 33.20 Owner Review of Positional Boards

Phase 33.20 reviewed the 16 positional BQML v2 candidate boards and alternates:
- **Accepted boards**: Standard (QB, RB, WR, TE), Half PPR (QB, RB, WR), PPR (QB, RB, WR), GNG Keeper (RB, WR).
- **Accepted with guardrails**: QB boards require capping running QB bias; Standard TE requires Current Pigskin floor.
- **Held behind Current Pigskin**: Half PPR TE, PPR TE, GNG Keeper QB, GNG Keeper TE.
- **Guardrail policies proposed**: Rookie draft capital floors (Round 1-2 cap -15), sparse feature upward movement caps (+10), and alternate-model disagreement locks.

Recommended next phase: **Phase 33.22 — Owner approval packet for guarded positional boards**.

## Phase 33.21B Guardrail Identity and History Fix

Phase 33.21B corrected the rookie/low-history classification logic:
- **History Volume Correction**: Resolved the false-positive rookie bug by checking total career games played in 2023-2025 (`hist_games_3yr` >= 10) instead of latest-season weekly rows. Reclassified established veterans (Brock Purdy, Garrett Wilson, Rashee Rice, Malik Nabers, Mike Evans, James Conner, Jayden Reed, Chris Godwin, Sam LaPorta) as having sufficient history.
- **Rookie & Low-History**: Retained true rookies (Omarion Hampton, Travis Hunter) under `ROOKIE_NO_HISTORY` and low-history career players (Cam Skattebo, Casey Washington) under `LOW_HISTORY`, anchoring them to Current Pigskin.
- **QB Disagreement Lock Fix**: Disabled `MODEL_DISAGREEMENT_LOCK` on QB boards to prevent the rejected points alternate from anchoring all 45 QBs.
- **Diagnostic Validation**: Generated `docs/rebuild/validation/phase-33-21b-guardrail-identity-history-fix-report.md`.

## Phase 33.22 Owner Approval Packet

Phase 33.22 generated the owner approval packet:
- **Approval Packet**: Generated `docs/rebuild/advanced-bqml-v2-owner-approval-packet.md` presenting the guarded boards, top-level recommendation table, and player movement examples.
- **Validation Report**: Generated `docs/rebuild/validation/phase-33-22-owner-approval-packet-report.md` validating git state and safety constraints.
- **Recommended Next Phase**: **Phase 33.23 — Position-locked top-100 planning only after owner accepts positional boards**.

## Phase 33.23 Owner Decision for Guarded Positional Boards

Phase 33.23 recorded the owner decision and top-100 planning authorization:
- **Owner Decision Record**: Generated `docs/rebuild/validation/phase-33-23-owner-decision-guarded-positional-boards.md` documenting the accepted/held boards and mandatory guardrail policies.
- **Top-100 Planning**: Authorized technical planning for a future position-locked top-100 interleaver without live activation.
- **Label Cleanup**: Corrected Marvin Harrison (Jr.) from `ROOKIE_NO_HISTORY` to `PROSPECT_HISTORY` based on career NFL games.
- **Recommended Next Phase**: **Phase 33.24 — Position-locked top-100 interleaver planning**.

## Phase 33.24 Position-Locked Top-100 Interleaver Planning

Phase 33.24 created the technical plan for the top-100 interleaver:
- **Interleaver Plan**: Generated `docs/rebuild/position-locked-top-100-interleaver-plan.md` defining position-locked queue rules, identity audits, and VOR selection options.
- **Validation Report**: Generated `docs/rebuild/validation/phase-33-24-position-locked-top-100-planning-report.md`.
- **Identity Hardening**: Labeled identity preflight checks to resolve collisions like Marvin Harrison Jr.
- **Recommended Next Phase**: **Phase 33.25 — Top-100 identity preflight**.

## Phase 33.25 Top-100 Player Identity Preflight

Phase 33.25 successfully audited and hardened player identity mappings:
- **Identity Gate**: Created [top-100-identity-preflight.md](file:///e:/Fantasy%20Football/docs/rebuild/top-100-identity-preflight.md) establishing preflight universes, allowed statuses, and preflight gate blocking rules.
- **Marvin Harrison Jr. Resolution**: Applied manual override in `player_identity_overrides` mapping Sleeper `11628` to active player `00-0039849` and isolating retired Sr. `00-0007024`. Corrected his WR boards placement to rank 34/35 with verified career history.
- **Validation Report**: Generated [phase-33-25-top-100-identity-preflight-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-25-top-100-identity-preflight-report.md).
- **Recommended Next Phase**: **Phase 33.26 — Position-locked top-100 prototype, review-only**.

## Phase 33.26 Position-Locked Top-100 Prototype

Phase 33.26 successfully compiled and backtested the first top-100 overall rankings interleaver prototypes:
- **Interleaver Compilation**: Built a python compiler executing three queue-selection strategies under three baseline structures.
- **Top-100 Boards**: Generated [position-locked-top-100-prototype-review.md](file:///e:/Fantasy%20Football/docs/rebuild/position-locked-top-100-prototype-review.md) containing the top-100 overall boards for 2026.
- **Validation Report**: Generated [phase-33-26-position-locked-top-100-prototype-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-26-position-locked-top-100-prototype-report.md).
- **Recommended Next Phase**: **Phase 33.27 — Owner review of top-100 prototype**.
