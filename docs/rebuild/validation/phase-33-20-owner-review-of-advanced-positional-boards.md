# Validation Report — Phase 33.20 Owner Review of Advanced Positional Boards

## 1. Final Decision

`ADVANCED POSITIONAL BOARDS ACCEPTED WITH GUARDRAILS`

Positional boards for Standard (QB, RB, WR, TE), Half PPR (QB, RB, WR), PPR (QB, RB, WR), and GNG Keeper (RB, WR) are accepted for owner review with required guardrails. Weak correlation boards (Half PPR TE, PPR TE, GNG Keeper QB, GNG Keeper TE) will be held behind Current Pigskin.

---

## 2. Boards Reviewed & Classifications

Each of the 16 positional review boards has been evaluated and classified:

### Standard
- **QB**: `accept with guardrails` (finalist model `logistic_bust` is stable, but alternate `linear_points` exhibits severe rushing bias and must be capped).
- **RB**: `accept for owner review` (linear points regression is highly robust).
- **WR**: `accept for owner review` (logistic elite finish tracking is extremely clean).
- **TE**: `accept with guardrails` (TE validation correlation declined by `-0.0342`, requires a Current Pigskin floor).

### Half PPR
- **QB**: `accept with guardrails` (same rushing bias guardrails as Standard QB).
- **RB**: `accept with guardrails` (linear VOR is solid, but needs alternate points sanity checks).
- **WR**: `accept for owner review` (solid).
- **TE**: `hold Current Pigskin` (weak TE combined correlation; hold behind Current Pigskin).

### PPR
- **QB**: `accept with guardrails` (same rushing bias guardrails as Standard QB).
- **RB**: `accept for owner review` (logistic elite model captures receiving-back volume cleanly).
- **WR**: `accept for owner review` (solid).
- **TE**: `hold Current Pigskin` (low TE combined correlation; hold behind Current Pigskin).

### GNG Keeper
- **QB**: `hold Current Pigskin` (weak combined predictive correlation below 0.45; hold behind Current Pigskin).
- **RB**: `accept for owner review` (linear points is solid).
- **WR**: `accept for owner review` (logistic bust risk protection is very suitable for keeper formats).
- **TE**: `hold Current Pigskin` (TE correlation is too low; hold behind Current Pigskin).

---

## 3. Movement and Alternate Disagreement Analysis

### Major Movements evaluation:
1. **Ray Davis (RB)**: Pigskin 77 -> Adv 37 (Standard, +40). *Decision: Makes football sense.* Pre-2026 stats show elite efficiency and high goal-line carry potential.
2. **DJ Moore (WR)**: Pigskin 68 -> Adv 24 (Standard, +44). *Decision: Makes football sense.* Heavy target-earning history (WOPR: 0.58) justifies high advanced rank.
3. **Casey Washington (WR)**: Pigskin 94 -> Adv 165 (Standard, -71). *Decision: Plausible but needs review.* Demotion is driven by lack of pre-2026 targets, but the magnitude is aggressive. A ceiling-floor guardrail must be applied.
4. **Omarion Hampton (RB)**: Pigskin 10 -> Adv 56 (Standard, -46). *Decision: Model overreaction.* Demoting an elite prospect to RB56 due to thin early nflverse stats is a model artifact. Must be guarded by Current Pigskin floor.

### Alternate Disagreements:
- **Standard/PPR QB (Mahomes & Allen)**: Finalist `logistic_bust` ranks them as elite (#1 and #6), but alternate `linear_points` ranks them near the bottom (#115 and #124) because it heavily penalizes passing volume while over-rewarding backup rushing QBs (e.g. Anthony Richardson #1, Tyson Bagent #10). This confirms the alternate model suffers from severe rushing bias and should be rejected for board-ordering.

---

## 4. Guardrail Recommendations

### Rookie & Low-History Guardrails (`ROOKIE_NO_HISTORY`)
1. **Current Pigskin Anchor**: Players with less than 10 weekly rows or 100% missing pre-2026 history must be anchored to their Current Pigskin rank (0 rank movement permitted).
2. **Draft Capital Floor**: High-draft-capital rookies (Round 1-2) cannot be demoted more than 15 ranks below their Current Pigskin rank.
3. **Manual Review Trigger**: Any player flagged with `ROOKIE_NO_HISTORY` inside the top 150 overall must undergo manual owner review before any formula promotion is applied.

### Sparse Feature Guardrails (`SPARSE_FEATURES`)
1. **Upward Cap**: Cap upward movement at `+10` ranks when advanced feature missingness exceeds 50%.
2. **Model Agreement Lock**: If the finalist and alternate models disagree by more than 20 ranks, hold the player at their Current Pigskin rank.
3. **Missingness Badging**: Display the exact missingness percentage on all owner-review screens.

---

## 5. Owner-Review Recommendation Table

| Profile | Position | Finalist Model | Alternate Model | Movement Severity | Rookie Risk | Sparse Risk | Recommendation | Required Guardrail | Next Action |
|---|---|---|---|---|---|---|---|---|---|
| Standard | QB | `logistic_bust` | `linear_points` | Low | Low | Low | Accept with guard | Reject alternate; cap running QBs | Promote to review boards |
| Standard | RB | `linear_points` | `logistic_bust` | Medium | Low | Low | Accept | None | Promote to review boards |
| Standard | WR | `logistic_elite` | N/A | Medium | Low | Low | Accept | None | Promote to review boards |
| Standard | TE | `linear_points` | `logistic_bust` | High | Low | Low | Accept with guard | Current Pigskin floor | Promote with TE floor |
| Half PPR | QB | `logistic_bust` | N/A | Low | Low | Low | Accept with guard | Cap rushing bias | Promote to review boards |
| Half PPR | RB | `linear_vor` | `linear_points` | High | Low | Low | Accept with guard | Points sanity check | Promote with VOR floor |
| Half PPR | WR | `logistic_elite` | N/A | Medium | Low | Low | Accept | None | Promote to review boards |
| Half PPR | TE | `logistic_elite` | N/A | High | Low | Low | Hold Pigskin | Hold behind Pigskin | Hold behind Pigskin |
| PPR | QB | `logistic_bust` | `linear_points` | Low | Low | Low | Accept with guard | Reject alternate | Promote to review boards |
| PPR | RB | `logistic_elite` | `linear_points` | Medium | Low | Low | Accept | None | Promote to review boards |
| PPR | WR | `logistic_elite` | N/A | Medium | Low | Low | Accept | None | Promote to review boards |
| PPR | TE | `logistic_bust` | N/A | High | Low | Low | Hold Pigskin | Hold behind Pigskin | Hold behind Pigskin |
| GNG Keeper | QB | `linear_points` | N/A | Low | Low | Low | Hold Pigskin | Hold behind Pigskin | Hold behind Pigskin |
| GNG Keeper | RB | `linear_points` | N/A | Medium | Low | Low | Accept | None | Promote to review boards |
| GNG Keeper | WR | `logistic_bust` | `linear_points` | Medium | Low | Low | Accept | None | Promote to review boards |
| GNG Keeper | TE | `logistic_bust` | N/A | High | Low | Low | Hold Pigskin | Hold behind Pigskin | Hold behind Pigskin |

---

## 6. Confirmations

- **No training occurred**: Verified. No new BQML models were trained.
- **No live rankings changed**: Verified. No active rankings were written.
- **No champion selected**: Verified.
- **No top-100 ready**: Verified. Positional lists are separate and locked.
- **Route metrics status**: Verified. All route-run, TPRR, and YPRR metrics remain strictly **BLOCKED** and mapped to `NULL`.

---

## 7. Recommended Next Phase

- **Phase 33.21 — Implement review-board guardrails** (to code and apply rookie/sparse/TE floor guardrails to the boards).
