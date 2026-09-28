# Phase 37.2 PPR Decisions Publish and Unified Start Report

## Final Decision

`PPR CANDIDATES PUBLISHED; UNIFIED PPR V1 STARTED`

The seven approved player rulings are published as structured production candidate data. The active July 3 PPR rankings remain unchanged.

## Published Candidate Data

- Current table: `fantasy_football_brain.ppr_fable_rankings_current`
- History table: `fantasy_football_brain.ppr_fable_rankings_history`
- Board version: `ppr-fable-v1-review-20260711`
- Rows and unique players: 301
- Decision counts: 294 formula defaults, two accepted Fable ranks, three unsigned exclusions, one role hold, and one injury hold.

Each row retains formula rank, recommended rank, live PPR rank, decision code, promotion eligibility, note, and risk flags.

## Approved Decisions

- DK Metcalf: accepted at WR19.
- Kimani Vidal: provisionally accepted; formula RB32 and unified eligible RB31 after the Charbonnet exclusion.
- Colby Parkinson: held pending receiving-role verification.
- Zach Charbonnet: held at the injury gate pending ACL recovery evidence.
- Stefon Diggs, Deebo Samuel, Keenan Allen: excluded until officially signed.

## Automation Backlog

`docs/rebuild/ppr-ranking-future-tasks.md` now specifies deterministic unsigned-player exclusion, long-term injury recovery gates, official-depth/Sleeper conflict handling, TE route-role verification, evidence provenance, and signing-triggered re-entry.

## Unified PPR Start

The first PPR-specific VORP build uses fitted 2022-2025 PPR curves and separate PPR replacement assumptions:

- QB13
- RB30
- WR44
- TE9

Initial top-100 composition is 31 RB, 46 WR, 14 QB, and 9 TE. That is a plausible PPR shape and is not copied from Standard. Unsigned players and unresolved holds are excluded automatically.

The unified PPR board is review-only and has not been published to a production unified table. It needs the same forward-fold realized-VORP and replacement-sensitivity gate used by Standard.

## Checks

- Three focused tests passed across decision publishing and PPR unified configuration.
- Candidate table has 301 rows and 301 unique players.
- The unified board contains Metcalf and Vidal.
- Parkinson, Charbonnet, Diggs, Deebo, and Allen are absent from the unified top 100 because they are not promotion eligible.
- No active PPR ranking changed.

## Files

- `scripts/publish_ppr_fable_v1_candidate_boards.py`
- `scripts/build_unified_ppr_fable_v1_top100.py`
- `tests/test_publish_ppr_fable_v1_candidate_boards.py`
- `tests/test_build_unified_ppr_fable_v1_top100.py`
- `docs/rebuild/ppr-ranking-future-tasks.md`
- `docs/rebuild/unified-ppr-fable-v1-top100.md`
- this report
