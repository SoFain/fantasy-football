# Phase 37.1 PPR Fable Fast-Transfer Report

## Final Decision

`PPR FABLE POSITIONAL CANDIDATES READY FOR OWNER REVIEW`

The Standard system is operating correctly in production data. Its unified board has one current version, 100 unique players, ranks 1-100, contiguous positional queues, and consistent source versions. The application UI still does not display the unified table, so Standard is data-live rather than fully user-facing.

PPR remains entirely on the July 3 Pigskin LLM board. The fastest defensible optimization is to transfer the proven positional architecture, retarget validation to PPR outcomes, and avoid rebuilding formulas that already work.

## Selected PPR Candidates

| Position | Candidate | Decision |
|---|---|---|
| QB | Active guarded Standard QB 75/25 | reuse; QB scoring is unchanged |
| RB | RB Fable v1 with 2% weight shifted from non-garbage touches to target share | selected PPR adjustment |
| WR | WR Fable v1 unchanged | direct transfer |
| TE | TE Fable no-man unchanged | direct transfer |

## Forward-Fold Evidence

| Candidate | Spearman | Pairwise | Top 12 | Top 24 | Points@12 | Points@24 | NDCG@24 | Elite misses | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RB Standard transfer | 0.739 | 0.775 | 0.556 | 0.750 | 0.847 | 0.886 | 0.860 | 6 | 2 |
| **RB 2% receiving shift** | **0.742** | **0.777** | 0.556 | **0.750** | **0.856** | **0.886** | **0.861** | **6** | **1** |
| WR Fable v1 | **0.760** | **0.780** | **0.667** | 0.611 | **0.923** | 0.899 | 0.875 | 8 | 1 |
| TE Fable no-man | 0.703 | 0.760 | 0.611 | **0.806** | 0.852 | **0.906** | **0.905** | **3** | **0** |

The 2% RB adjustment is the elbow. A 3% shift is the first variant that loses top-24 precision, points@24, and adds an elite miss. A 5% shift improves top-12 precision but retains that damage. The 2% candidate improves correlation, pairwise ordering, top-12 point capture, and bust count without sacrificing the broad board.

## Current Review Boards

Generated formula rows:

- RB: 90
- WR: 135
- TE: 76

Full boards: `docs/rebuild/ppr-fable-v1-review-boards.md`.

The important owner-review disagreements are concentrated:

- Colby Parkinson: TE12 formula vs live PPR TE29.
- DK Metcalf: WR19 vs live PPR WR35.
- Zach Charbonnet: RB21 vs live PPR RB31.
- Kimani Vidal: RB32 vs live PPR RB46.
- Stefon Diggs, Deebo Samuel, and Keenan Allen appear in the formula top 40 but have no active PPR match.

These should be reviewed with current Sleeper team/depth and injury context. They are not a reason to discard the formula transfer.

## Why This Is Fast

- No new source family is required.
- No BQML training is required.
- WR and TE need no formula change.
- RB changes one bounded opportunity tradeoff while preserving total weight.
- QB already has a promoted deterministic guarded board.
- The same unified VORP implementation can be reused after fitting PPR-specific rank-to-PPG curves.

## Checks

- Two focused PPR backtest tests passed.
- Three leakage-safe folds ran for RB, WR, and TE.
- Targets use PPR scoring only.
- Input scores remain prior-season only.
- No 2026 outcome, market target, Gemini call, or Pigskin chat was used.
- No live PPR ranking changed.

## Files

- `scripts/run_ppr_fable_transfer_backtest.py`
- `scripts/build_ppr_fable_v1_review_boards.py`
- `tests/test_ppr_fable_transfer_backtest.py`
- `docs/rebuild/ppr-fable-v1-review-boards.md`
- `output/ppr-fable-v1-transfer-backtest.json` (local evidence)
- `output/ppr-fable-v1-review-boards.json` (local evidence)
- this report

## Next Phase

Resolve the named current-player disagreements, then promote the three PPR positional formula boards behind position-scoped write gates. After positional promotion, fit PPR rank-to-PPG curves and build the separate unified PPR top-100. Do not reuse Standard curves or replacement ranks without the PPR fit.
