# Phase 37.5 PPR and Half-PPR Production Rollout Report

## Final Decision

`PPR AND HALF-PPR FABLE SYSTEMS LIVE IN PRODUCTION DATA`

PPR and half-PPR now use the guarded QB queue plus reviewed Fable RB, WR, and TE positional boards. Both profiles also have unified top-100 boards in production.

## Active Positional Versions

| Profile | QB | RB/WR/TE |
|---|---|---|
| PPR | `ppr-guarded-qb-75-25-20260711` | `ppr-fable-v1-20260711` |
| Half PPR | `half_ppr-guarded-qb-75-25-20260711` | `half-ppr-fable-v1-20260711` |

Each profile has 45 QB, 80 RB, 100 WR, and 35 TE rows with contiguous position ranks. Prior active rows were archived before replacement.

## Formula Decisions

- QB: guarded Standard 75/25 queue copied unchanged because QB scoring is identical.
- RB: 2% shifted from non-garbage touches to target share in both PPR and half-PPR. At 3%, broad-board degradation begins in both profiles.
- WR: WR Fable v1 unchanged.
- TE: TE Fable no-man unchanged.
- Approved current-context holds and unsigned exclusions remain coded in the candidate layer.

## Unified Boards

| Profile | Version | Mix QB/RB/WR/TE | VORP Spearman | VORP capture | Top 24 | Top 100 |
|---|---|---|---:|---:|---:|---:|
| PPR | `unified-ppr-fable-v1-20260711` | 14/31/46/9 | 0.736 | 0.889 | 0.611 | 0.740 |
| Half PPR | `unified-half-ppr-fable-v1-20260711` | 13/35/43/9 | 0.720 | 0.889 | 0.569 | 0.747 |

Half-PPR selected QB13/RB34/WR42/TE9 after sensitivity testing. RB34 outperformed the initial RB32 setup on correlation, top-24, top-50, and top-100 hit rates.

## Production Verification

- `unified_draft_rankings_current` contains exactly one 100-row version for Standard, PPR, and half-PPR.
- Each unified profile has 100 unique players and ranks 1-100.
- PPR and half-PPR positional row counts and rank ranges match their contracts.
- Standard positional and unified boards remain intact.
- No application image was deployed.

## Safety Notes

Two PPR staging attempts failed before mutations because BigQuery disallows window functions directly inside `SELECT * REPLACE`. Window calculations were moved into dedicated CTEs; the final gated apply succeeded. The failure point was temporary-table construction, before archive, deactivation, or insertion.

## Files

- `scripts/promote_ppr_fable_v1_positional.py`
- `scripts/promote_guarded_qb_to_reception_profiles.py`
- `scripts/build_unified_ppr_fable_v1_top100.py`
- `scripts/run_unified_ppr_fable_v1_top100_backtest.py`
- `scripts/promote_unified_ppr_fable_v1_top100.py`
- `docs/rebuild/half-ppr-fable-v1-review-boards.md`
- `docs/rebuild/unified-half-ppr-fable-v1-top100.md`
- this report
