# Phase 38.13 Standard Unified Active-WR Rebuild

Date: 2026-07-13

## Final Decision

`PROMOTED AND PUBLIC JSON REPUBLISHED`

The Standard Top 100 now uses the active Standard QB, RB, WR, and TE queues. The prior unified board used the retained WR Fable research queue even though the public positional board used the active Standard WR ranking. That caused 37 rank mismatches among 40 joined Top 100 receivers.

## Production Result

- Current board version: `unified-fable-v1-standard-active-wr-20260713`
- Current rows: 100
- Unique players: 100
- Unique overall ranks: 100
- Active positional rank or source-version mismatches: 0
- Prior `unified-fable-v1-standard-20260711` rows archived: 100

A.J. Brown is now overall 20 and WR7. Justin Jefferson is overall 25 and WR9. Garrett Wilson is overall 28 and WR10.

## Membership Changes

Added to the Top 100: Malik Nabers, Tre Tucker, Ricky Pearsall, Jerry Jeudy, and Elic Ayomanor.

Removed from the Top 100: Stefon Diggs, Deebo Samuel, Keenan Allen, Michael Pittman, and Khalil Shakir.

## Public Feed

- Manifest: `https://storage.googleapis.com/fantasy-football-498121-public-rankings/v1/manifest.json`
- Standard board SHA-256: `63f0bdbe3b4844710290d3c6d7eac7341c5d4a12704d8df903e0f9451536b855`
- Feed warnings: 0

## Checks

- Six focused builder and promotion tests passed.
- Edited Python files compiled.
- Promotion dry run confirmed 100 rows and active positional source agreement.
- Public board download returned 100 overall players with the corrected WR order.

## Files Changed

- `scripts/build_unified_fable_v1_top100.py`
- `scripts/promote_unified_fable_v1_standard_top100.py`
- `tests/test_promote_unified_fable_v1_standard_top100.py`
- `docs/rebuild/unified-fable-v1-standard-top100.md`
- `docs/rebuild/validation/phase-38-13-standard-unified-active-wr-rebuild.md`
- `AGENTS.md`

## Warning

The website must refresh the public manifest before it sees the new Standard object URL. No website files were changed in this phase.
