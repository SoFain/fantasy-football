# Phase 37.3 Unified PPR Fable v1 Production Gate Report

## Final Decision

`GO FOR ADDITIVE PPR UNIFIED BOARD`

The unified PPR board passes the same realized-VORP and replacement-sensitivity gate used for Standard. Publish it as a separate `scoring_profile_id='ppr'` version. Do not replace the active PPR positional rankings in this phase.

## Selected Setup

- QB13
- RB30
- WR44
- TE9

Current review composition: 31 RB, 46 WR, 14 QB, and 9 TE.

## Forward Folds

| Fold | Pool | VORP Spearman | VORP captured | Top 24 | Top 50 | Top 100 | Mix QB/RB/WR/TE |
|---|---:|---:|---:|---:|---:|---:|---|
| 2022 to 2023 | 259 | 0.714 | 0.908 | 0.542 | 0.680 | 0.740 | 13/31/47/9 |
| 2023 to 2024 | 267 | 0.740 | 0.862 | 0.667 | 0.560 | 0.730 | 14/31/46/9 |
| 2024 to 2025 | 265 | 0.753 | 0.895 | 0.625 | 0.560 | 0.750 | 14/31/46/9 |
| Average | — | **0.736** | **0.889** | **0.611** | **0.600** | **0.740** | stable |

## Sensitivity

| Setup | Spearman | VORP captured | Top 24 | Top 50 | Top 100 |
|---|---:|---:|---:|---:|---:|
| Selected RB30/WR44/TE9 | 0.736 | 0.889 | **0.611** | 0.600 | 0.740 |
| RB28 | 0.734 | 0.886 | 0.597 | 0.587 | 0.743 |
| RB32 | **0.742** | **0.889** | 0.583 | **0.627** | **0.747** |
| WR42 | 0.733 | 0.888 | 0.583 | 0.600 | 0.743 |
| WR46 | 0.739 | 0.887 | 0.597 | 0.593 | 0.740 |
| TE10 | 0.732 | 0.887 | **0.611** | 0.600 | 0.743 |

RB32 improves tail metrics but weakens the top-24 hit rate by 2.8 percentage points. RB30 is selected because early draft ordering is the higher-value objective and its aggregate correlation remains strong.

## Context Decisions

The board reads only promotion-eligible rows from `ppr_fable_rankings_current`. Metcalf and Vidal are included. Parkinson, Charbonnet, Diggs, Deebo, and Allen are excluded while their approved holds remain active.

## Disclosed Limitation

The three-fold QB lane uses the leakage-safe QB Fable prior-season proxy because the promoted guarded QB evidence is weekly and does not cover the same preseason folds. QB scoring itself is unchanged between Standard and PPR.

## Checks

- One focused sensitivity-contract test passed.
- Three forward folds completed.
- Replacement variants cover RB28/RB30/RB32, WR42/WR44/WR46, and TE9/TE10.
- Current board has 100 unique players.
- No held or unsigned player entered the current PPR top 100.
- No live PPR positional row changed.

## Files

- `scripts/run_unified_ppr_fable_v1_top100_backtest.py`
- `tests/test_unified_ppr_fable_v1_top100_backtest.py`
- `output/unified-ppr-fable-v1-top100-backtest.json` (local evidence)
- this report
