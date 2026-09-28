# Phase 38.21 Standard TE Verdict Repair

## Decision

Standard TE public summaries now cite the actual inputs behind the rank. The TE formula and ranking order did not change.

## Summary Contract

Each TE verdict uses routes per game, target share, red-zone targets, YPRR, targets per route, and either blended touchdowns or an availability warning.

## Production Result

- Active positional version: `standard-fable-v1-safety-20260713223322`
- Current public Standard version: `unified-fable-v1-standard-20260713223145`
- Current public object SHA-256: `085312f013e7a3f3e9802fc7d507e2e8cbcdff5b47c4a6d5394f2cdc329406df`
- Published TE rows: `35`
- Legacy TE rank-only verdicts: `0`
- Public warnings: `0`

The published feed has detailed TE verdicts. The source copy also corrects the final sentence to use plural grammar. Its unified-board publication is waiting on BigQuery's temporary 100-row streaming buffer, which rejects a replacement `DELETE` until it clears.

## Checks

- Focused positional-promotion tests: `4` passed.
- Positional dry run passed.
- Positional rebuild completed with contiguous TE ranks and zero teamless rows.
- Unified preflight confirmed all 100 overall rows match the active positional ranks.
- Public Standard feed dry run completed with zero warnings.
- Public manifest check confirmed 35 TE rows and zero legacy placeholders.

## Files Changed

- `scripts/promote_standard_fable_v1_positional.py`
- `tests/test_promote_standard_fable_v1_positional.py`

## Next Phase

After the streaming buffer clears, rerun `scripts/promote_unified_fable_v1_standard_top100.py --apply`, then publish the Standard feed to release the grammar correction.
