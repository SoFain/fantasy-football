# Phase 38.19 Coordinated Production Rebuild and Publication

## Decision

The repaired positional queues and all four unified Top 100 boards are live. New content-addressed JSON objects were published, then `v1/manifest.json` was updated last.

Teamless players are absent from every active positional queue, every unified board, and every public object.

## Positional Promotion

| Profile | QB | RB | WR | TE | Current-team rejects |
|---|---:|---:|---:|---:|---:|
| Standard | 45 | 85 | 100 | 35 | 0 |
| PPR | 45 | 80 | 100 | 35 | 0 |
| Half-PPR | 45 | 80 | 100 | 35 | 0 |
| GNG Keeper | 45 | 80 | 100 | 35 | 0 |

Standard RB has 85 rows because all five teamless formula-qualified players were removed. No weaker non-formula fallback was invented.

Production positional versions:

- Standard RB, WR, TE: `standard-fable-v1-safety-20260713184307`
- PPR RB, WR, TE: `ppr-fable-v1-safety-20260713184347`
- Half-PPR RB, WR, TE: `half-ppr-fable-v1-safety-20260713184414`
- GNG Keeper: `gng-formula-2026-20260713184437`

The approved Standard WR guardrail is intact: A.J. Brown WR13, Justin Jefferson WR14, Garrett Wilson WR15.

## Unified Boards

| Profile | Board version | Queue mismatches | Teamless rows |
|---|---|---:|---:|
| Standard | `unified-fable-v1-standard-20260713184600` | 0 | 0 |
| PPR | `unified-ppr-fable-v1-20260713184600` | 0 | 0 |
| Half-PPR | `unified-half-ppr-fable-v1-20260713184600` | 0 | 0 |
| GNG Keeper | `gng-formula-2026-20260713184437` | 0 | 0 |

The rebuilt Standard Top 10 begins Christian McCaffrey, Jonathan Taylor, Bijan Robinson. Josh Allen is overall 6. A.J. Brown is overall 35, ahead of Justin Jefferson at 38 and Garrett Wilson at 40.

## Public JSON

Current manifest: `https://storage.googleapis.com/fantasy-football-498121-public-rankings/v1/manifest.json`

Immutable manifest: `https://storage.googleapis.com/fantasy-football-498121-public-rankings/v1/manifests/sha256-924b86496ce44ade39ca07c03f5f8cc27a0471db222de41b936fdd3272bbecdf.json`

| Profile | Object SHA-256 | Warnings |
|---|---|---:|
| Standard | `eb19e83bfb7e37e6413f7522fa6f3a09877be002a02e4386ec1a8577e1f7790c` | 0 |
| PPR | `a89a924f34a7b784321702a1ac301856349c18bacc723e2fb136744de299eae6` | 0 |
| Half-PPR | `f544228e88c067834fa0d348dba24283f1f3461fdaea7107fda34945f5f3d76b` | 0 |
| GNG Keeper | `f991ee55a0170f72eef7efe27fd8632e7c0c2b3c7eb5593814560a0f2900c59e` | 0 |

Anonymous verification returned HTTP 200. Every downloaded object matched its manifest SHA-256. The manifest returned `Cache-Control: public, max-age=300, must-revalidate` and CORS for `https://www.thegng.us`.

## Files Changed

- `scripts/promote_standard_fable_v1_positional.py`
- `scripts/promote_ppr_fable_v1_positional.py`
- `scripts/build_unified_ppr_fable_v1_top100.py`
- `scripts/promote_unified_fable_v1_standard_top100.py`
- `scripts/promote_unified_ppr_fable_v1_top100.py`
- `scripts/promote_gng_2026_rankings.py`
- regenerated unified board JSON and markdown artifacts
- `AGENTS.md`

## Checks

- Python compilation passed for all changed rollout scripts.
- Fourteen focused promotion and safety tests passed.
- Fourteen unified PPR and GNG tests passed.
- All active positional ranks are unique and contiguous.
- All unified boards contain 100 unique players and exactly preserve active positional order.
- Local public JSON generation completed with zero warnings before publication.

## Remaining Risk

The Standard formula has only 85 rank-eligible RB inputs. That is sufficient for the Top 100, but the public Standard RB list is shorter than its former 90-player list by design.
