# Phase 38.20 Standard RB and WR Verdict Repair

## Decision

Standard RB and WR public summaries now explain why each player holds the rank. The old formula-name and rank repetition is removed.

The rank order did not change.

## Summary Contract

RB verdicts now cite:

- non-garbage-time touches per game
- target share and red-zone touches
- blended touchdowns per game
- EPA per touch as the efficiency counterweight

WR verdicts now cite target share, WOPR, meaningful targets per game, and YPRR. They add scoring context or an availability warning when the source data supports it.

## Production Result

- Positional version: `standard-fable-v1-safety-20260713195239`
- Unified version: `unified-fable-v1-standard-summary-20260713195400`
- Standard public object SHA-256: `b332e5c4b20554c61ff5d1527eea721155f6957ccc862b4e27aa5c522981a1fb`
- Immutable manifest SHA-256: `75a6fcc0b8e625bb7e675becd4c2bd4c2b91b63be0450681782fe82c00a66599`
- Public warnings: 0

All 85 RB rows and 100 WR rows have zero legacy rank-only placeholders.

## Rank Preservation

The before and after positional fingerprints match exactly:

| Position | Rows | SHA-256 rank fingerprint |
|---|---:|---|
| RB | 85 | `16de7e15265a53d67ccfa056641f3c3e8a3b7de43319f0739fb5157911f6b131` |
| WR | 100 | `e7e396f585d08d9b56b7e646a39a679360c097a9bb945c263a889281c59b718a` |

The regenerated unified Standard board had zero player-order mismatches against the prior live board.

## Checks

- Eight focused promotion and feed tests passed.
- BigQuery promotion completed with contiguous ranks and zero teamless rows.
- Local public generation completed with zero warnings before publication.
- Anonymous Standard download returned HTTP 200 and matched the manifest hash.
- CORS allowed `https://www.thegng.us`.

## Files Changed

- `scripts/promote_standard_fable_v1_positional.py`
- `tests/test_promote_standard_fable_v1_positional.py`
- `AGENTS.md`
