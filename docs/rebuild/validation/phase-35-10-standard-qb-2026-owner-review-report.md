# Phase 35.10: Standard QB 2026 Owner-Review Board

## Final decision

**GUARDED 75/25 STANDARD QB BOARD IS A SERIOUS REPLACEMENT CANDIDATE WITH TWO OWNER WARNINGS**

Phase 35.11 subsequently added deterministic Sleeper depth-order buckets and promoted the revised board. See `phase-35-11-standard-qb-guarded-promotion-report.md` for the live result.

The exact guarded board is suitable for final owner approval and a separate controlled promotion phase. The raw 75/25 consensus and raw 70/30 linear boards are not suitable for direct promotion.

No ranking rows were written. No model was trained or activated. No production or staging deployment occurred. No LLM, Pigskin prompt, Sleeper API, ingestion, or materialization action ran.

## Inputs

- Live Standard QB universe: 45 active rows from `analytics_pigskin_rankings`.
- Live version: `pigskin-llm-20260704071412`.
- Live model run: `pigskin_rankings-2026-na-20260704T071419Z-9c498edc`.
- Deterministic control: `candidate_rank` from the active ranking rows.
- BQML inputs: latest available leakage-safe pre-2026 feature record per player.
- Models: existing advanced Standard QB linear-points and logistic-bust models.
- Final verification query job: `ebeb60ea-f957-403d-9889-d7f87bd78132`.
- Dry-run bytes: 19,832,010.

The currently displayed `rank` is an older Flash-adjusted result. Historical formula validation used the deterministic candidate, so the guarded board correctly anchors to `candidate_rank` while retaining live rank as a comparison column.

## Coverage

| Item | Result |
|---|---:|
| Review players | 45 |
| Players with BQML features | 33 |
| Deterministic-lane players | 12 |
| `years_exp=0` rookies | 1 |
| Missing-history and rookie ranks changed by guarded assignment | 0 |
| 2026 outcome fields used | 0 |

The first query incorrectly required a 2025 feature row and matched only 19 players. The final query uses the established latest-pre-2026 policy and recovers 33 players without introducing outcome leakage.

## Raw challenger findings

| Board | Maximum move | Moves at least 3 | QB6 crossings | QB12 crossings | QB24 crossings |
|---|---:|---:|---:|---:|---:|
| Raw 75/25 consensus | 8 | 13 | 2 | 2 | 2 |
| Raw 70/30 linear | 8 | 16 | 2 | 2 | 4 |

The raw boards fail promotion guardrails. The clearest failure is Justin Fields moving from deterministic QB32 to QB24 despite passing EPA `-0.185` and CPOE `-1.46`.

## Exact guardrails

The finalized review candidate uses a unique-rank constrained assignment over 45 players:

- returning-player movement is capped at four ranks;
- missing-history and rookie players are locked to deterministic rank;
- QBs with non-positive passing EPA and CPOE may rise no more than one rank;
- those weak passers cannot cross QB6, QB12, or QB24 upward;
- the assignment minimizes deviation from the raw 75/25 consensus while satisfying every constraint.

The assignment runs locally on the 45-row read-only result. It does not write a temporary or permanent table.

## Guarded result

| Check | Result |
|---|---:|
| Maximum move | 4 |
| Moves at least 3 | 9 |
| Weak-passing violations | 0 |
| QB6 crossings | 0 |
| QB12 crossings | 2 |
| QB24 crossings | 0 |
| Duplicate ranks | 0 |

QB12 changes:

- Lamar Jackson enters at QB11. His evidence is strong: passing EPA `0.162`, CPOE `4.57`, linear model rank 1, logistic model rank 1.
- Matthew Stafford exits at QB14. His passing efficiency is positive, but both model signals place him 22nd among matched players.

## Old LLM-layer differences

The guarded formula also removes several large old Flash movements:

- Dak Prescott: live QB6, deterministic and guarded QB13.
- Jordan Love: live QB5, guarded QB19.
- Matthew Stafford: live QB4, guarded QB14.
- Lamar Jackson: live QB16, guarded QB11.
- Joe Burrow: live QB19, guarded QB21 versus deterministic QB24.

These differences are not new LLM adjustments. They expose how far the current live board moved from the deterministic inputs before adjustment codes existed.

## Owner warnings

1. **Matthew Stafford:** the guarded demotion to QB14 conflicts with strong passing EPA and positive CPOE. The BQML signals are materially lower, so this is explainable but should be explicitly approved.
2. **Jordan Love:** the guarded demotion from deterministic QB15 to QB19 occurs despite strong EPA. Slightly negative CPOE and weak model placement drive the move. This is the least comfortable non-cutline movement.

Tua Tagovailoa and Jacoby Brissett also warrant observation, but neither crosses a protected cutline.

## Artifacts

- `scripts/run_standard_qb_2026_owner_review.py`
- `tests/test_standard_qb_2026_owner_review.py`
- `docs/rebuild/standard-qb-2026-guarded-owner-review-board.md`
- `docs/rebuild/validation/phase-35-10-standard-qb-2026-owner-review-report.md`

## Recommendation

Use the exact guarded 75/25 board as the proposed Standard QB replacement. Do not use the raw 75/25 or 70/30 ranks.

A later promotion phase should preserve the current board in ranking history, replace only active Standard QB rows, attach a deterministic rank-source/version marker, and avoid any LLM reordering. Injury adjustments should remain a separate coded layer with estimated-games-missed evidence.
