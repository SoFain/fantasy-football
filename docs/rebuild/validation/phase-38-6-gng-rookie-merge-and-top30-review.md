# Phase 38.6 GNG Rookie Merge and Top-30 Review

## Decision

`REVIEW BOARDS COMPLETE; THREE ROSTER DECISIONS BLOCK UNIFIED INTERLEAVING`

The isolated positional boards were rebuilt with corrected Sleeper identities, a bounded rookie overlay, and a materialized top-30 review table. Production remains unchanged.

## Corrected Sleeper Identities

- Bam Knight maps to Zonovan Knight, Sleeper `8122`.
- Audric Estime maps to Sleeper `11579`.
- Josh Palmer maps to Joshua Palmer, Sleeper `7670`.

These exact aliases removed all missing Sleeper joins from the named lower-board identity set.

## Rookie Overlay

The 2026 manual market-value baseline was joined to active, rostered Sleeper rookies by unique normalized name and position. It is used only as a bounded insertion signal, not as GNG historical evidence.

Depth-chart penalties are applied to market position rank: zero for depth 1, plus 3 for depth 2, plus 10 for depth 3, and plus 20 for depth 4 or worse. Only rookies whose adjusted insertion point falls within the positional board limit are inserted.

| Position | Rookies inserted |
|---|---:|
| QB | 3 |
| RB | 9 |
| WR | 15 |
| TE | 2 |

The merged review table is `fantasy-football-498121.fantasy_football_advanced_metrics.gng_2026_positional_boards_with_rookies`.

Notable top-30 insertions include Fernando Mendoza QB15, Jeremiyah Love RB5, Jadarian Price RB19, Carnell Tate WR14, Jordyn Tyson WR23, Makai Lemon WR29, Kenyon Sadiq TE10, and Eli Stowers TE15.

## Top-30 Review

The review table is `fantasy-football-498121.fantasy_football_advanced_metrics.gng_2026_top30_review`.

| Position | Rows | Flagged | Rookies | Rank deltas of 10+ | Hard reviews |
|---|---:|---:|---:|---:|---:|
| QB | 30 | 8 | 1 | 6 | 0 |
| RB | 30 | 10 | 2 | 5 | 0 |
| WR | 30 | 13 | 3 | 4 | 2 |
| TE | 30 | 14 | 2 | 5 | 1 |

Large formula calls include Joe Burrow QB5, Patrick Mahomes QB14, Matthew Stafford QB20, Christian Watson WR11, DJ Moore WR18, Harold Fannin Jr. TE4, and Jake Tonges TE16. They remain formula outputs with explicit review evidence. No arbitrary correction was applied.

## Blocking Roster Decisions

Sleeper currently gives no team to:

- Keenan Allen, candidate WR24.
- Tyreek Hill, candidate WR28, also injury flagged.
- Zach Ertz, candidate TE30, also injury flagged.

Recommended treatment: move all three to a watchlist outside the ranked positional board until Sleeper reports a current team. Backfill the vacated ranks from the next eligible review-board player. This is a roster-status rank change and therefore requires owner approval under the source contract.

## Injury Policy

Injury flags remain evidence-only. No injury penalty is applied without a sourced regular-season games-missed estimate. This affects players including Rashee Rice, Drake London, Malik Nabers, De'Von Achane, Tucker Kraft, and Patrick Mahomes.

## Objects and Checks

- Rebuilt `gng_2026_positional_candidate_boards`.
- Rebuilt `gng_2026_rookie_review`.
- Created `gng_2026_positional_boards_with_rookies`.
- Created `gng_2026_top30_review`.
- Active production GNG version remains `pigskin-llm-20260704072119`.
- No production ranking or champion changed.

## Next Phase

After the three roster decisions, freeze positional boards and build a leakage-safe unified GNG VORP interleaver. Validate position mix, rookie representation, hard-review exclusion policy, and top-100 replacement-value boundaries before promotion.
