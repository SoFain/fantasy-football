# Phase 38.7 GNG Watchlist Freeze and Unified Top 100

## Decision

`UNIFIED REVIEW BOARD GENERATED; TWO ROSTER AND ONE ROOKIE DECISION REMAIN`

The owner-approved teamless watchlist was applied, positional queues were backfilled, and a position-locked GNG Top 100 was generated. Production remains unchanged.

## Approved Watchlist

`fantasy-football-498121.fantasy_football_advanced_metrics.gng_2026_unranked_watchlist` contains:

- Keenan Allen.
- Tyreek Hill.
- Zach Ertz.

Each row is marked `OWNER_APPROVED_TEAMLESS_WATCHLIST`. None appears in the unified board.

## Unified Object

`fantasy-football-498121.fantasy_football_advanced_metrics.unified_gng_2026_top100_review`

The interleaver uses the previously validated Option 2 replacement levels: QB15, RB36, WR55, and TE12. It fits GNG historical PPG curves over 2022-2025 and preserves strict positional queue order.

| Position | Top 24 | Top 50 | Top 100 |
|---|---:|---:|---:|
| QB | 4 | 7 | 13 |
| RB | 10 | 18 | 32 |
| WR | 9 | 22 | 46 |
| TE | 1 | 3 | 9 |

The board has 100 rows, 100 distinct player IDs, ranks 1-100, zero duplicate players, and zero approved-watchlist leaks.

## Top Ten

| Overall | Player | Position |
|---:|---|---|
| 1 | Jonathan Taylor | RB |
| 2 | Christian McCaffrey | RB |
| 3 | Puka Nacua | WR |
| 4 | Brock Purdy | QB |
| 5 | Jahmyr Gibbs | RB |
| 6 | Jaxon Smith-Njigba | WR |
| 7 | Saquon Barkley | RB |
| 8 | Rashee Rice | WR |
| 9 | Trevor Lawrence | QB |
| 10 | Jeremiyah Love | RB, rookie overlay |

## Rookie Exposure

Eight market-overlay rookies enter the Top 100: Jeremiyah Love 10, Carnell Tate 33, Jadarian Price 52, Jordyn Tyson 53, Makai Lemon 61, KC Concepcion 71, Omar Cooper 81, and Denzel Boston 91.

Jeremiyah Love is supported by market RB4 and current Sleeper depth order 1, but his overall rank 10 is still derived without NFL production. Owner approval is required to retain a market-only rookie inside the top 24.

## Remaining Teamless Players

Extending beyond the positional top-30 review exposed two additional teamless players:

- Stefon Diggs, overall 87.
- Deebo Samuel Sr., overall 99.

Recommended treatment is the same approved watchlist policy: remove both and backfill from the locked WR queue.

## Checks

- Position order is contiguous and preserved for every queue.
- Python compilation passed.
- Unified row, identity, duplicate, watchlist, rookie, and position-mix queries passed.
- Active production remains `pigskin-llm-20260704072119` with 260 GNG positional rows.
- No production row or formula champion changed.

## Next Phase

Decide the two additional teamless veterans and Jeremiyah Love's top-24 eligibility. Rebuild once, run unified historical backtesting, then consider production promotion.
