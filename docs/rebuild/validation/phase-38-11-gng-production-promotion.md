# Phase 38.11 GNG Production Promotion

## Decision

`LIVE AND VERIFIED`

The owner approved production publication. The guarded promotion completed under version `gng-formula-2026-20260712151557`.

## Active Positional Boards

| Position | Rows | Rank range | Distinct players |
|---|---:|---|---:|
| QB | 45 | 1-45 | 45 |
| RB | 80 | 1-80 | 80 |
| WR | 100 | 1-100 | 100 |
| TE | 35 | 1-35 | 35 |

Every active GNG positional row uses the same ranking version.

## Active Unified Board

`fantasy-football-498121.fantasy_football_brain.unified_draft_rankings_current` contains 100 GNG rows, 100 distinct players, and contiguous overall ranks 1-100 under the same version.

The current top ten are Christian McCaffrey, Jahmyr Gibbs, Amon-Ra St. Brown, Josh Allen, Saquon Barkley, Ja'Marr Chase, Bijan Robinson, Puka Nacua, Drake London, and Jared Goff.

## Safety Verification

- Teamless-watchlist leaks: 0.
- Duplicate unified ranks: 0.
- Sleeper hard reviews at preflight: 0.
- Prior positional rows captured in rollback: 260, one version.
- Prior unified GNG rollback rows: 0 because no GNG unified scope existed before this promotion.

Rollback objects:

- `fantasy-football-498121.fantasy_football_advanced_metrics.gng_2026_production_rollback_positional`
- `fantasy-football-498121.fantasy_football_advanced_metrics.gng_2026_production_rollback_unified`

## Adjacent Profiles

Standard, PPR, and Half PPR unified boards remain at 100 rows with their prior versions. Their active positional row counts also remain unchanged. The promotion transaction touched only `gng_keeper`.

## Final Formula Set

| Position | Formula |
|---|---|
| QB | Q4 GNG bonus proxy |
| RB | R7 H1/R2 compromise |
| WR | W10 H5 floor first plus live-WR guardrails |
| TE | H5 stability hybrid |

Unified replacement ranks are QB13, RB36, WR55, and TE12. Jeremiyah Love is capped at overall 20. QB positional rank 4 is held outside the top 24.

## Commands and Checks

- Guard: `ALLOW_GNG_2026_PRODUCTION_PROMOTION=true`.
- Apply: `scripts/promote_gng_2026_rankings.py --apply`.
- Transactional positional and unified write: passed.
- Post-write positional counts: passed.
- Unified identity, continuity, duplicate, and watchlist checks: passed.
- Adjacent-profile preservation: passed.
