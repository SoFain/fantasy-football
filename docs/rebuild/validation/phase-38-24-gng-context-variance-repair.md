# Phase 38.24: GNG Context Variance Repair

## Decision

Keep the approved GNG ranking formulas and replace the repetitive context renderer. Cosmetic template rotation was rejected. Context now selects a player archetype from the strongest percentile input and chooses a supporting metric from a different family when available.

## Behavior

- QB explanations can lead with passing volume, rushing, or efficiency.
- RB explanations distinguish workload from receiving and rushing-first-down profiles.
- WR and TE text separates high-value opportunity from role stability, target control, or direct first-down value.
- The lowest remaining formula input still supplies the tradeoff.
- Rookie text remains provisional and is personalized by player and position.
- Context version is `gng-rank-context-v2`.
- Formula scores, positional ranks, and the unified board are read-only inputs.

## Dry-run evidence

| Position | Rows | Rookie context | Maximum length | Driver metrics used |
|---|---:|---:|---:|---:|
| QB | 45 | 3 | 286 | 6 |
| RB | 80 | 9 | 296 | 7 |
| WR | 100 | 15 | 279 | 8 |
| TE | 35 | 2 | 258 | 7 |

The five players shown in the defect report now lead with different evidence: Christian McCaffrey uses target share, Jahmyr Gibbs uses expected receiving first downs, Saquon Barkley uses GNG-weighted opportunity, Josh Allen uses QB rushing, and Amon-Ra St. Brown uses GNG-weighted opportunity with role support.

## Validation

- Focused context and feed tests: 12 passed.
- Full 260-row context dry run: passed.
- Contexts over 320 characters: 0.
- Missing or generic veteran metric context: 0.
- Materialized table version: `gng-rank-context-v2`.
- Rank, formula, or rank-source mismatches: 0.
- All-profile public dry run: passed with zero warnings.
- Published at: `2026-07-14T13:23:58.584523Z`.
- Immutable manifest: `v1/manifests/sha256-2caab017ed6c2d77fa1db066ad00c3d95e2703082151c0823b3b37e619bd4f1b.json`.
- GNG board hash: `ac7616017deae4015a67fb14de0ca3148a6dfcc4fc2ce013d26de0054bafcc9e`.
- Anonymous verification: all four board hashes matched, every board had 100 overall players, and warnings were empty.
- Live GNG context coverage: 260 positional rows with a maximum length of 296 characters.
