# Phase 38.27: Unified Top 150 Production Publication

## Decision

Expand the unified overall board from 100 to 150 players for Standard, PPR, Half-PPR, and GNG Keeper. Positional formulas, positional ranks, and post-formula safety decisions remain unchanged.

## Production Result

| Profile | Board version | Overall rows | Composition QB/RB/WR/TE | Public SHA-256 |
|---|---|---:|---|---|
| Standard | `unified-fable-v1-standard-20260722060111` | 150 | 19 / 47 / 66 / 18 | `59ed3671c18879605bc2135639e1a6d631d44ccab2221031a88e5711d3900c88` |
| PPR | `unified-ppr-fable-v1-20260722060123` | 150 | 22 / 44 / 68 / 16 | `23942dc81858283b5c59467572ea5338b27f2e7c14c36b0813610b2f17ccfd2d` |
| Half-PPR | `unified-half-ppr-fable-v1-20260722060136` | 150 | 20 / 47 / 66 / 17 | `6cab8068a6dd1d9d66bc104585311d2263234f54306de109c99645a2c1477ba3` |
| GNG Keeper | `unified-gng-keeper-2026-20260722060148` | 150 | 16 / 44 / 73 / 17 | `71b96ec4b3eafeef51be84ef2718f76303f2f7564b784391db8ca6cab97b2725` |

Public schema version is `1.2`. Immutable manifest: `v1/manifests/sha256-c8f7ff4cc747448089a7c810a169c3ca3e81bc0db1b56b6b10057a8968b82b25.json`.

## Verification

- The current-player coverage gate passed before and after promotion with zero blocking omissions.
- Every candidate contained 150 unique players with contiguous overall and positional queues.
- Each candidate's first 100 player IDs, positions, and positional ranks exactly matched the prior production board.
- Unified promotion archived the prior boards and used committed BigQuery load jobs.
- The GNG unified-only promoter verified active positional rank and formula ID, then changed no positional row.
- Public dry run and anonymous verification returned four profiles, 150 overall rows each, matching SHA-256 values, and zero warnings.
- The IONOS import loaded 410 rows for GNG Keeper, PPR, and Half-PPR, plus 415 for Standard. Production health reported four healthy boards and 600 total overall rows.

## Warning

The Sleeper context snapshot was 52 hours old during the final coverage audit. This did not block the board expansion because no formula or current-status decision changed. Refresh that context before the next roster-sensitive positional rebuild.
