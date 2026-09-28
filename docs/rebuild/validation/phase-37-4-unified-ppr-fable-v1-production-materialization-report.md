# Phase 37.4 Unified PPR Fable v1 Production Materialization Report

## Final Decision

`UNIFIED PPR TOP-100 LIVE IN PRODUCTION DATA`

The validated unified PPR board is published alongside Standard in `fantasy_football_brain.unified_draft_rankings_current`.

## Verification

- PPR version: `unified-ppr-fable-v1-20260711`
- Rows and unique players: 100
- Overall rank range: 1-100
- Composition: 14 QB, 31 RB, 46 WR, 9 TE
- Every positional queue starts at 1 and remains contiguous.
- The Standard unified version remains present with 100 rows.
- Active PPR positional boards remain the July 3 Pigskin version and were not changed.

## Production Evidence

- Realized-VORP Spearman: 0.736 average
- Positive VORP captured at 100: 0.889
- Top-24 hit rate: 0.611
- Top-100 hit rate: 0.740
- Latest-fold correlation: 0.753

## Safety

- Write gate: `ALLOW_UNIFIED_PPR_FABLE_V1_TOP100_PROMOTION=true`, scoped to the applying process and removed afterward.
- Publication is additive by scoring profile.
- No Standard unified rows changed.
- No PPR positional row or formula champion changed.
- Held and unsigned players did not enter the PPR top 100.
- No application image was deployed.

## Files

- `scripts/promote_unified_ppr_fable_v1_top100.py`
- `docs/rebuild/validation/phase-37-3-unified-ppr-fable-v1-production-gate-report.md`
- this report
