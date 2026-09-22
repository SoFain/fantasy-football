# Technical Plan — Position-Locked Top-100 Interleaver

## 1. Purpose & Owner Decision Source

This technical planning document designs a future **position-locked top-100 interleaver** using the owner-accepted guarded positional boards. 

*   **Owner Decision Source**: [phase-33-23-owner-decision-guarded-positional-boards.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-23-owner-decision-guarded-positional-boards.md)
*   **Approval Status**: Formally accepted for planning by the owner in Phase 33.23.
*   **Planning Scope**: This document is for planning purposes only. No interleaver code will be built, and no live rankings will be activated during this phase.

---

## 2. Core Rule: Position-Locked Queue Pulls

The interleaver must operate under a strict position-locked constraint:
1.  **Selection Control**: The interleaver's queue selector may decide which positional queue (QB, RB, WR, or TE) to pull from next.
2.  **Strict Queue Order**: Once a position is selected, the interleaver **must** pull the next available player from that position's queue.
3.  **No Reordering**: The interleaver **must never reorder players** inside individual positional boards (e.g., WR1 must always be selected before WR2, which must be selected before WR3).
4.  **No Skip-ahead**: The interleaver cannot skip a player in a queue to select a player lower in the same queue.

---

## 3. Position-Locked Input Queues

For each of the four scoring profiles, the interleaver will ingest the following input queues:

| Scoring Profile | QB Queue Input | RB Queue Input | WR Queue Input | TE Queue Input |
|---|---|---|---|---|
| **Standard** | Guarded BQML v2 | Guarded BQML v2 | Guarded BQML v2 | Guarded BQML v2 |
| **Half PPR** | Guarded BQML v2 | Guarded BQML v2 | Guarded BQML v2 | **Current Pigskin TE Queue** |
| **PPR** | Guarded BQML v2 | Guarded BQML v2 | Guarded BQML v2 | **Current Pigskin TE Queue** |
| **GNG Keeper** | **Current Pigskin QB Queue** | Guarded BQML v2 | Guarded BQML v2 | **Current Pigskin TE Queue** |

---

## 4. Identity Hardening Requirement & Preflight Audit

To prevent retired-player collisions and name-matching errors from entering the top-100, a mandatory **Identity Preflight Audit** must run before any interleaver build as detailed in [top-100-identity-preflight.md](file:///e:/Fantasy%20Football/docs/rebuild/top-100-identity-preflight.md):

### Preflight Checks:
-   **Retired-Player Collisions**: Detect and resolve retired players sharing names with active players (e.g., Marvin Harrison Jr. vs. retired Marvin Harrison Sr. `00-0007024`).
-   **College/Prospect Mappings**: Identify college prospects (e.g., Fernando Mendoza `MEN516487`) and mark them as prospect-only.
-   **Name-Only Collisions**: Flag duplicate active player names in the roster context.
-   **Identity Ambiguity**: Block the top-100 build if any player inside the top 150 overall equivalent has an unresolved identity collision.

### Required Identity Status Field:
*   `ID_VERIFIED`: Stable ID mapped correctly to Career NFL Stats history.
*   `ID_PROSPECT_ONLY`: Valid college player context, no NFL stats expected.
*   `ID_LOW_HISTORY`: Veteran player with > 0 but < 10 career NFL games.
*   `ID_JOIN_FAILED`: Veteran player whose advanced stats join failed.
*   `ID_COLLISION`: Name matches multiple records; requires resolution.
*   `ID_RETIRED_COLLISION`: Active player shares name with a retired player (e.g. Marvin Harrison Jr. vs. Sr.).
*   `ID_NAME_ONLY_COLLISION`: Joined purely by name without suffix or ID verification.
*   `ID_MANUAL_REVIEW_REQUIRED`: Undergoing active identity verification.

---

## 5. Preserved Guardrails

All positional board guardrails remain active and will be carried over directly:
-   **ROOKIE_NO_HISTORY / LOW_HISTORY**: Anchored to Current Pigskin ranks.
-   **PROSPECT_HISTORY**: Flags single-season players for manual review inside top 150.
-   **SPARSE_FEATURES**: Capped upward movement at +10 ranks.
-   **MODEL_DISAGREEMENT_LOCK**: divergence > 20 ranks anchors to Current Pigskin.
-   **QB Rushing Bias Warning**: Flags rushing-only QBs.
-   **Standard TE Floor**: Restricts standard TE demotion below Current Pigskin.
-   **Held-Board Lock**: Held boards use Current Pigskin queues.
-   **Route Metrics Blocked Policy**: True route run metrics remain strictly **BLOCKED** and mapped to `NULL`.

---

## 6. Queue Selection Strategy Options

The interleaver will evaluate three possible strategies to decide which queue to pull from next:

## Phase 33.31 Targeted QB/WR Cleanup Update

Phase 33.31 did not approve live interleaver use. The next review-only interleaver pass must carry these extra guardrails:

- QB: Current Pigskin QB1-QB3 cannot fall outside top 36 overall without manual review, and QB4-QB6 cannot fall outside top 60 overall without manual review.
- QB pull floor: QB1 must appear by top 24. QB2 must appear by top 50 when Current Pigskin has QB2 inside top 24. Do not force more than three QBs into top 24.
- WR: Current Pigskin WR1-WR6 cannot fall outside WR12, WR7-WR12 cannot fall outside WR24, and a Current Pigskin top-24 overall WR cannot fall outside top 60 without manual review.
- WR demotion rule: a Current Pigskin top-12 WR may only fall more than 12 WR spots if at least two source-backed concerns are present.
- Prospect policy: market-only prospects such as Jeremiyah Love stay outside the official top-100 until a prospect watch lane exists or the owner rejects market-only prospects.

Current Pigskin remains the live-safe baseline. Phase 33.31 is review evidence only.

### Strategy A: VOR-First Queue Selector
-   **Logic**: Use the raw profile-specific Value-over-Replacement (VOR) signal to choose the position with the highest relative VOR gap between the next available player and the replacement baseline.
-   **Pull**: Select next available player from that position's locked queue.

### Strategy B: Scarcity-Adjusted VOR Selector
-   **Logic**: Adjust raw VOR signals based on positional scarcity and draft-board tier dropoffs (e.g., WR/RB dropoffs vs. QB/TE availability).
-   **Pull**: Select next available player from the chosen scarcity-adjusted queue.

### Strategy C: Guarded Hybrid Selector
-   **Logic**: Blend Current Pigskin overall pressure, VOR signals, positional scarcity, and guardrail confidence metrics to select the next position.
-   **Pull**: Select next available player from the chosen hybrid queue.

---

## 7. Replacement Baseline Assumptions

Baselines for VOR calculations are defined as planning assumptions (subject to validation):
*   **Quarterbacks**: QB12 (1-QB formats) or QB15
*   **Running Backs**: RB24 or RB36
*   **Wide Receivers**: WR36 or WR55
*   **Tight Ends**: TE12 or TE18

---

## 8. Validation Test Plan for Future Phase

When a prototype interleaver is built in a future phase, it must be validated against:
-   **NDCG**: Compare output ranking order against historic expert consensus.
-   **Pairwise Draft Win Rate**: Simulate mock drafts to test top-100 queue strength.
-   **Hit Rates**: Top-24, Top-50, and Top-100 player success rates.
-   **Positional Mix Sanity**: Verify WR/RB balance in the top 100.
-   **Rookie/Identity Risk Exposure**: Count how many rookie anchors or identity-failed players populate the top 50.
-   **Extreme Movement Count**: Flag players moving > 25 overall ranks.

---

## 9. Future Top-100 Row Schema

Each row in the future top-100 output will contain:
```json
{
  "scoring_profile": "STRING",
  "overall_rank": "INTEGER",
  "player_name": "STRING",
  "team": "STRING",
  "position": "STRING",
  "position_rank": "INTEGER",
  "source_queue": "STRING",
  "queue_pull_reason": "STRING",
  "guarded_position_rank": "INTEGER",
  "current_pigskin_position_rank": "INTEGER",
  "vor_signal": "FLOAT",
  "scarcity_signal": "FLOAT",
  "guardrail_labels": "STRING",
  "identity_status": "STRING",
  "missingness": "FLOAT",
  "manual_review_required": "BOOLEAN",
  "route_metrics_status": "STRING"
}
```

---

## 10. Manual Review Displays

The top-100 review dashboard will display:
1.  **Top Identity-Risk Players**: List of players flagged with `ID_COLLISION` or `ID_JOIN_FAILED`.
2.  **Top Rookie/Prospect Anchors**: Active players anchored to Current Pigskin ranks.
3.  **Positional Mix Summary**: Positional breakdown by counts in top 12, 24, 50, and 100.
4.  **Disagreement Highlights**: Biggest discrepancies between Current Pigskin overall ranks and Advanced overall ranks.

---

## 11. Non-Goals

-   **No Live Activation**: This plan does not activate any live overall rankings.
-   **No Model Re-Tuning**: No BQML positional models will be retrained or altered.
-   **No Positional Reordering**: The interleaver will not reorder the accepted positional boards.

---

## 12. Phase 33.26 Prototype Verification & Decision

The first position-locked top-100 interleaver prototype has been built and verified.
- **Prototype Results**: Generated [position-locked-top-100-prototype-review.md](file:///e:/Fantasy%20Football/docs/rebuild/position-locked-top-100-prototype-review.md) containing the top-100 boards.
- **Validation Report**: Generated [phase-33-26-position-locked-top-100-prototype-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-26-position-locked-top-100-prototype-report.md).
- **Best Setup Selected**: **Option 2** (QB15 / RB36 / WR55 / TE12 baselines) combined with **Strategy C** (Guarded Hybrid selection logic) achieved the highest Top-24 hit rate (0.349), maximum points captured (0.797), and VOR captured (0.774) across seasons.
- **Preflight & Safety**: Preflight gate checks successfully isolated Marvin Harrison Sr. and Purdy/Wilson/Rice veterans from rookie/no-history classification.

---

## 13. Phase 33.26B Calibrated Prototype Verification & Decision

The position-locked top-100 interleaver prototype was calibrated to resolve WR overpull and protect elite RBs.
- **Diagnosis**: WR model probability scale (0-100%) mismatch against RB linear z-score points scale (-1.7 to 15.3) created a 5x raw VOR inflation for WRs.
- **Calibrated Setup**: Option 2 baseline (QB12/RB30/WR42/TE12) and `prototype_v2_mix_guarded_hybrid` strategy.
- **Sanity Gates & Anti-Monopoly**: Implemented look-ahead constraints (WR max 6 in top 12, max 13 in top 24; RB min 4 in top 12, min 7 in top 24) and elite RB protection forcing top-6/12 RBs to be selected within top 24/36/40.
- **Calibrated Boards**: Generated [position-locked-top-100-prototype-review.md](file:///e:/Fantasy%20Football/docs/rebuild/position-locked-top-100-prototype-review.md) containing the top-100 boards.
- **Validation Report**: Generated [phase-33-26b-top-100-positional-mix-calibration-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-26b-top-100-positional-mix-calibration-report.md).
- **Safety**: Checked all constraints. No model training, database writes, or live activation occurred. Route run metrics remain strictly blocked.

---

## 14. Phase 33.26C Calibrated Weighting & Movement Caps Decision

The position-locked top-100 interleaver was calibrated with soft mix penalties and band-specific weighting percentages to resolve early RB/TE overforcing.
- **Calibrated Setup**: Option 2 baseline (QB12/RB30/WR42/TE12) and `prototype_v3_balanced` strategy.
- **Soft mix targets**: Implemented dynamic soft penalties/boosts (offsets up to $+/- 40$ on a 100-point scale) instead of hard gates.
- **Movement Caps**: Enforced overall draft-band caps (top-12 cannot fall outside top 24/36) and elite RB/WR caps (top-6 RB cannot fall outside top 24).
- **Calibrated Boards**: Generated [position-locked-top-100-prototype-review.md](file:///e:/Fantasy%20Football/docs/rebuild/position-locked-top-100-prototype-review.md).
- **Validation Report**: Generated [phase-33-26c-top-100-weighting-calibration-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-26c-top-100-weighting-calibration-report.md).
- **Safety**: Passed all compilation, unit test, and dry-run safety checks. Route run metrics remain blocked.

---

## 15. Phase 33.26D Elite Market-Miss Audit Decision

The calibrated top-100 interleaver remains blocked for owner-facing use because elite player misses are too severe.

- **Primary finding**: Jahmyr Gibbs is a guarded RB positional-board miss before the interleaver runs. He is Current Pigskin RB3 in every profile and market rank 2 overall, but the guarded RB queue ranks him RB18/RB19 outside PPR and RB9 in PPR.
- **Decision**: Do not create a new top-100 champion or owner-facing v4 board until the RB positional board is refined or explicit review-only anchor rules are approved.
- **Tripwire policy**: Future review prototypes must report Current Pigskin and market anchor violations before presenting the board.
- **Validation Report**: Generated [phase-33-26d-elite-market-miss-audit-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-26d-elite-market-miss-audit-report.md).
- **Safety**: No model training, live ranking writes, champion activation, deployment, Gemini call, or Pigskin chat occurred. Route metrics remain blocked.

---

## 16. Phase 33.27 RB Positional Refinement Decision

The RB positional queue was refined for review-only use after the Gibbs, Achane, and Chase Brown miss audit.

- **Selected RB candidate**: `anchored_blend_tripwire`.
- **Board behavior**: Tiered Current Pigskin anchoring plus RB elite tripwire locks. Top-12 Current Pigskin RBs use an 80/20 Current Pigskin to guarded-finalist blend, RB13-RB24 uses 65/35, and RB25+ uses 50/50.
- **Tripwire locks**: Current or market top-3 RBs must be inside RB8. Current top-6 RBs must be inside RB12. Market top-6 RBs require RB12 placement unless prospect/low-history manual review explains the exception.
- **Top-100 status**: Top-100 remains blocked until a review-only rebuild uses the refined RB queue.
- **Validation Report**: Generated [phase-33-27-rb-positional-board-refinement-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-27-rb-positional-board-refinement-report.md).
- **Safety**: No live ranking writes, champion activation, deployment, Gemini call, Pigskin chat, or route-metric population occurred.

## Phase 33.28 Refined RB Top-100 Rebuild Note

Phase 33.28 keeps the Phase 33.26C calibrated weighted hybrid position-pull sequence and swaps only the RB queue to the Phase 33.27 `anchored_blend_tripwire` review queue. This fixes Jahmyr Gibbs inside RB3 and top 7 overall across all profiles, but the result remains review-only because Current Pigskin and market tripwires still require owner judgment.

Stable constraints:

- Do not write this prototype to `analytics_pigskin_rankings`.
- Do not activate formula champions from this phase.
- Keep Half PPR TE, PPR TE, GNG Keeper QB, and GNG Keeper TE held behind Current Pigskin.
- Treat Jeremiyah Love as a market-only prospect tripwire until the player appears in a source-backed active ranking or approved prospect lane.
- Treat Half PPR Breece Hall as a current-state drift warning because live Current Pigskin now lists him RB6 while the Phase 33.27 evidence used an older RB18 context.
- Route metrics remain blocked/null.

## Phase 33.29 Refined Top-100 Owner Review Decision

Final decision: `REFINED TOP-100 READY FOR OWNER REVIEW WITH TRIPWIRES`.

Phase 33.29 accepts the Phase 33.28 refined top-100 prototype for owner review only. It does not approve live ranking writes, champion activation, production exposure, or deployment.

Owner-review findings:

- Gibbs is fixed at RB3 and inside the top 24 overall in every scoring profile.
- Achane and Chase Brown are not buried outside RB24.
- Omarion Hampton and Cam Skattebo remain manual-review prospect-history cases.
- Jeremiyah Love remains a market-only tripwire and needs a prospect lane or explicit owner rejection before live use.
- Half PPR Breece Hall is stale Current Pigskin context: Phase 33.27 evidence used RB18, while the current active table now lists RB6.
- Patrick Mahomes is an interleaver warning. The prototype pushes elite QBs too low for live use without backtest support.
- Rashee Rice is a WR position-board warning. The guarded WR queue disagrees sharply with Current Pigskin.

Next required gate: bounded historical backtest before any live top-100 decision.

## Phase 33.30 Bounded Backtest And Tripwire Cleanup Decision

Final decision: `REFINED TOP-100 NEEDS TARGETED QB/WR CLEANUP`.

Phase 33.30 ran a bounded proxy backtest against `ranking_backtest_feature_mart` using target seasons 2024 and 2025, target week 18, all four scoring profiles, and no 2026 outcomes. The exact 2026 owner-review queues do not exist historically, so the test used source-window feature proxies and the Phase 33.26C position-pull sequence.

Decision summary:

- The refined RB queue remains useful for owner review and fixes 2026 Gibbs sanity.
- The refined top-100 does not cleanly beat the Current Pigskin proxy on points/VOR capture.
- QB tripwires, especially Patrick Mahomes, point to an interleaver anchor/cap problem.
- WR tripwires, especially Rashee Rice, point to a WR position-board or elite-anchor problem.
- Jeremiyah Love requires a prospect lane or explicit owner rejection of market-only prospect influence.
- Half PPR Breece Hall requires stale-context refresh before live approval.
- Current Pigskin holds for live use.

Next gate: targeted QB/WR tripwire cleanup before another owner-review top-100 pass.
