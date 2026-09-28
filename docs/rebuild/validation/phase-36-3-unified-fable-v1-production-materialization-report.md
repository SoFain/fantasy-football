# Phase 36.3 Unified Fable v1 Production Materialization Report

## Final Decision

`UNIFIED STANDARD TOP-100 LIVE IN PRODUCTION DATA`

The validated Unified Fable v1 Standard top-100 is published as an additive production artifact. Existing positional ranking tables and champion records were not changed.

## Production Objects

- Current table: `fantasy-football-498121.fantasy_football_brain.unified_draft_rankings_current`
- History table: `fantasy-football-498121.fantasy_football_brain.unified_draft_rankings_history`
- Board version: `unified-fable-v1-standard-20260711`
- Rows: 100
- Unique players: 100
- Overall rank range: 1-100

## Composition

| Position | Rows | Positional rank range |
|---|---:|---|
| QB | 13 | 1-13 |
| RB | 35 | 1-35 |
| WR | 43 | 1-43 |
| TE | 9 | 1-9 |

Every included position starts at rank 1 and remains contiguous. Overall and positional ranks are stored separately.

## Safety

- Write gate: `ALLOW_UNIFIED_FABLE_V1_TOP100_PROMOTION=true`, scoped to the applying process and removed afterward.
- The first apply attempt failed on a reserved BigQuery alias before any delete or insert. Only the two empty destination tables had been created. The alias was corrected and the guarded apply succeeded.
- Active Standard positional row counts remain QB 45, RB 90, WR 100, and TE 35.
- No row in `analytics_pigskin_rankings` changed.
- No formula champion changed.
- No application service was deployed.
- QB proxy disclosure is stored on every unified row.

## Validation

- Seven focused tests passed across board construction, pooled backtesting, and guarded promotion.
- Post-write verification confirmed one board version, 100 rows, 100 unique players, and ranks 1-100.
- Production-gate evidence: average realized-VORP Spearman 0.693, positive VORP capture 0.893, and top-100 hit rate 0.737.

## Files

- `scripts/promote_unified_fable_v1_standard_top100.py`
- `tests/test_promote_unified_fable_v1_standard_top100.py`
- `docs/rebuild/validation/phase-36-2-unified-fable-v1-production-gate-report.md`
- this report

## Rollback

The first version has no prior unified board to restore. A rollback now means deleting only rows with board version `unified-fable-v1-standard-20260711` from `unified_draft_rankings_current`. Future promotions must archive the current version before replacement and restore from `unified_draft_rankings_history` if needed. Positional ranking tables remain outside this rollback scope.
