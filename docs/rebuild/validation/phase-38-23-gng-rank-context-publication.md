# Phase 38.23: GNG Rank Context Publication

## Scope

Add a GNG-only public `context` field without changing formulas, positional queues, or the unified Top 100.

## Contract

- `scripts/build_gng_rank_context.py` reads the active GNG board and the metric query used by the approved position formulas.
- Each veteran explanation states the relevant GNG scoring effect, two weighted advanced drivers, and the weakest available formula input.
- Rookie explanations are marked provisional. Missing NFL history is never replaced with zero or borrowed veteran data.
- Context is capped at 320 characters.
- The materialized table is `fantasy_football_advanced_metrics.gng_2026_rank_context` and uses a committed `WRITE_TRUNCATE` load job.
- The context builder cannot update ranking or unified-board tables.
- Public JSON schema `1.1` exposes `context` for GNG players only and fails closed on missing text.

## Dry-run evidence

The live dry run preserved all 260 active GNG positional rows:

| Position | Rows | Rookie context | Maximum length |
|---|---:|---:|---:|
| QB | 45 | 3 | 314 |
| RB | 80 | 9 | 296 |
| WR | 100 | 15 | 280 |
| TE | 35 | 2 | 266 |

The first pass correctly stopped when one context exceeded the limit. Fixed scoring copy was shortened, then the full-board dry run passed.

## Validation and publication

- Focused tests: 11 passed across `test_build_gng_rank_context` and `test_public_rankings_feed`.
- Python compilation passed for the context builder, publisher, and feed builder.
- The materialized context table contains 260 rows for 260 active GNG rows.
- Missing context rows: 0.
- Formula, rank, and rank-source mismatches: 0.
- Blank contexts: 0.
- Public all-profile dry run: 4 profiles, 100 overall players each, zero warnings.
- Public manifest schema: `1.1`.
- Published at: `2026-07-14T04:31:27.709817Z`.
- Immutable manifest: `v1/manifests/sha256-36adecd3aeff0a7736223a8ce4c47eee57d079beec28f8fc0cec6572184ff38a.json`.
- GNG board hash: `94f9d51c4876f4ca124eb41633a0677880ab86939ba1fb0efeaa6d57307d3caa`.
- Anonymous verification: every board returned HTTP 200 and matched its manifest hash.
- GNG context coverage: 100 of 100 overall players and 260 of 260 positional players.
- Standard, PPR, and Half-PPR context keys: 0, as required by the optional GNG-only contract.
