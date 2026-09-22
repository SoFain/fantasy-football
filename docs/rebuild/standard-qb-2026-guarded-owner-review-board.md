# Standard QB 2026 Guarded Owner-Review Board

This review artifact records the board promoted in Phase 35.11.

## Board contract

- `Live`: current Flash-adjusted Standard QB rank.
- `Anchor`: deterministic candidate rank supplied to the old LLM layer.
- `75/25`: raw 75% anchor, 12.5% linear-points, 12.5% logistic-bust consensus.
- `70/30`: raw 70% anchor, 30% linear-points challenger.
- `Guarded`: exact constrained assignment based on 75/25 consensus.
- `Move`: positive values rise from the deterministic anchor.

Guarded constraints:

- maximum movement of four ranks;
- missing-history and rookie lanes stay at their deterministic anchor;
- a QB with non-positive passing EPA and CPOE cannot rise more than one rank;
- that weak-passing QB cannot cross QB6, QB12, or QB24 upward;
- every final rank is unique.
- starter or unknown QBs occupy QB1-32, second-string QBs QB33-43, and third-string QBs QB44-45;
- verified role buckets override the four-rank formula cap when the prior deterministic rank conflicts with current depth order.

## Player-by-player comparison

| Guarded | Player | Team | Live | Anchor | 75/25 | 70/30 | Move | EPA/DB | CPOE | Rush | Lane |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Josh Allen | BUF | 1 | 1 | 1 | 1 | 0 | 0.140 | 3.14 | 49.9 | BQML |
| 2 | Drake Maye | NE | 2 | 2 | 2 | 2 | 0 | - | - | - | deterministic |
| 3 | Patrick Mahomes | KC | 3 | 3 | 3 | 3 | 0 | 0.176 | 4.63 | 27.6 | BQML |
| 4 | Jalen Hurts | PHI | 8 | 5 | 4 | 4 | +1 | 0.051 | 1.89 | 53.2 | BQML |
| 5 | Brock Purdy | SF | 7 | 4 | 5 | 6 | -1 | 0.266 | 3.05 | 17.7 | BQML |
| 6 | Trevor Lawrence | JAX | 9 | 6 | 9 | 10 | 0 | -0.007 | -1.44 | 23.0 | BQML |
| 7 | Daniel Jones | IND | 10 | 7 | 8 | 11 | 0 | -0.116 | -0.95 | 42.6 | BQML |
| 8 | Bo Nix | DEN | 11 | 8 | 6 | 5 | 0 | - | - | - | deterministic |
| 9 | Caleb Williams | CHI | 12 | 9 | 7 | 7 | 0 | - | - | - | deterministic |
| 10 | Justin Herbert | LAC | 15 | 11 | 10 | 9 | +1 | 0.114 | -1.89 | 20.3 | BQML |
| 11 | Lamar Jackson | BAL | 16 | 14 | 11 | 8 | +3 | 0.162 | 4.57 | 42.2 | BQML |
| 12 | Jayden Daniels | WAS | 17 | 12 | 12 | 12 | 0 | - | - | - | deterministic |
| 13 | Dak Prescott | DAL | 6 | 13 | 13 | 13 | 0 | 0.095 | 2.35 | 31.2 | BQML |
| 14 | Matthew Stafford | LAR | 4 | 10 | 14 | 16 | -4 | 0.146 | 0.51 | 9.4 | BQML |
| 15 | Kyler Murray | MIN | 22 | 18 | 15 | 14 | +3 | 0.004 | 0.49 | 34.0 | BQML |
| 16 | Jaxson Dart | NYG | 21 | 16 | 17 | 17 | 0 | - | - | - | deterministic |
| 17 | Jared Goff | DET | 13 | 17 | 16 | 15 | 0 | 0.149 | 0.95 | 9.9 | BQML |
| 18 | C.J. Stroud | HOU | 14 | 19 | 18 | 18 | +1 | 0.156 | -0.04 | 19.2 | BQML |
| 19 | Jordan Love | GB | 5 | 15 | 19 | 21 | -4 | 0.160 | -0.32 | 10.7 | BQML |
| 20 | Tyler Shough | NO | 26 | 20 | 20 | 20 | 0 | - | - | - | deterministic |
| 21 | Joe Burrow | CIN | 19 | 24 | 21 | 19 | +3 | 0.102 | 3.72 | 22.0 | BQML |
| 22 | Baker Mayfield | TB | 18 | 23 | 22 | 22 | +1 | 0.217 | 2.74 | 19.4 | BQML |
| 23 | Aaron Rodgers | PIT | 24 | 22 | 23 | 26 | -1 | -0.674 | -0.65 | 6.1 | BQML |
| 24 | Bryce Young | CAR | 28 | 21 | 27 | 28 | -3 | -0.302 | -1.25 | 15.9 | BQML |
| 25 | Geno Smith | NYJ | 31 | 28 | 25 | 25 | +3 | 0.059 | 6.24 | 16.0 | BQML |
| 26 | Tua Tagovailoa | ATL | 27 | 29 | 26 | 23 | +3 | 0.039 | -2.77 | 14.0 | BQML |
| 27 | Malik Willis | MIA | 25 | 26 | 31 | 31 | -1 | -0.325 | 0.08 | 15.2 | BQML |
| 28 | Sam Darnold | SEA | 20 | 27 | 28 | 27 | -1 | -0.128 | -0.36 | 17.6 | BQML |
| 29 | Jacoby Brissett | ARI | 23 | 25 | 29 | 29 | -4 | 0.177 | 5.17 | 15.3 | BQML |
| 30 | Shedeur Sanders | CLE | 29 | 30 | 30 | 30 | 0 | - | - | - | deterministic |
| 31 | Cam Ward | TEN | 30 | 31 | 32 | 32 | 0 | - | - | - | deterministic |
| 32 | Fernando Mendoza | LV | 32 | 41 | 41 | 42 | +9 | - | - | - | rookie, current QB1 role override |
| 33 | Justin Fields | KC | 38 | 32 | 24 | 24 | -1 | -0.185 | -1.46 | 44.2 | BQML, current QB2 role bucket |
| 34 | Marcus Mariota | WAS | 37 | 34 | 34 | 34 | 0 | 0.078 | 0.87 | 20.8 | BQML, QB2 |
| 35 | J.J. McCarthy | MIN | 41 | 35 | 35 | 36 | 0 | - | - | - | deterministic, QB2 |
| 36 | Spencer Rattler | NO | 39 | 36 | 37 | 37 | 0 | - | - | - | deterministic, QB2 |
| 37 | Jake Browning | TB | 44 | 37 | 38 | 39 | 0 | 0.096 | -1.18 | 13.7 | BQML, QB2 |
| 38 | Tyler Huntley | BAL | 35 | 39 | 36 | 35 | +1 | -0.002 | -0.01 | 44.3 | BQML, QB2 and weak-passing lock |
| 39 | Mac Jones | SF | 33 | 38 | 39 | 38 | -1 | -0.008 | 0.62 | 12.1 | BQML, QB2 |
| 40 | Joe Flacco | CIN | 45 | 40 | 40 | 40 | 0 | -0.128 | -1.56 | 10.1 | BQML, QB2 |
| 41 | Quinn Ewers | MIA | 42 | 45 | 45 | 45 | +4 | - | - | - | deterministic, QB2 |
| 42 | Davis Mills | HOU | 40 | 42 | 42 | 41 | 0 | -0.395 | 4.04 | 8.9 | BQML, QB2 |
| 43 | Jameis Winston | NYG | 34 | 44 | 43 | 43 | +1 | -0.115 | -4.76 | 8.1 | BQML, QB2 and weak-passing lock |
| 44 | Josh Johnson | CIN | 43 | 43 | 44 | 44 | -1 | -0.392 | 1.66 | 8.5 | BQML, QB3 |
| 45 | Carson Wentz | MIN | 36 | 33 | 33 | 33 | -12 | -0.054 | 5.79 | 34.7 | BQML, QB3 role override |

## Cutline review

| Cutline | Guarded entrant | Guarded exit | Decision read |
|---|---|---|---|
| QB6 | none | none | Trevor Lawrence remains QB6; weak passing prevents an unsupported rise into the tier. |
| QB12 | Lamar Jackson | Matthew Stafford | Lamar has positive EPA, positive CPOE, and the strongest paired BQML signal. Stafford retains good passing efficiency but has a materially weaker model rank. |
| QB24 | none | none | Justin Fields' raw QB24 rise is rejected by both the weak-passing guard and current QB2 role bucket. |

## Three-or-four-rank movement review

| Player | Anchor -> guarded | Evidence read |
|---|---|---|
| Lamar Jackson | 14 -> 11 | Supported: EPA 0.162, CPOE 4.57, linear rank 1, logistic rank 1. |
| Matthew Stafford | 10 -> 14 | Review warning: positive passing evidence, but both model signals rank him 22nd in the matched cohort. |
| Kyler Murray | 18 -> 15 | Modest positive passing evidence; movement remains below QB12. |
| Jordan Love | 15 -> 19 | Mixed: strong EPA, slightly negative CPOE, weak model placement. |
| Joe Burrow | 24 -> 21 | Supported: EPA 0.102, CPOE 3.72, top-eight model signals. |
| Bryce Young | 21 -> 24 | Supported demotion: EPA -0.302 and CPOE -1.25. |
| Geno Smith | 28 -> 25 | Supported: positive EPA and CPOE 6.24. |
| Tua Tagovailoa | 29 -> 26 | Warning: positive EPA but CPOE -2.77. No cutline crossing. |
| Jacoby Brissett | 25 -> 29 | Warning: positive efficiency but model ranks 29 and 27. No cutline crossing. |

## Data limitations

- BQML features are available for 33 of 45 players.
- Twelve players use the missing-history or rookie lane. Fernando Mendoza is the only `years_exp=0` rookie and is placed at QB32 because Sleeper currently lists him first on his team depth chart.
- Latest feature seasons vary between 2024 and 2025. No 2026 outcomes are used.
- Current team fields are inherited from the active ranking table and should receive a separate roster-context audit before promotion.
- Patrick Mahomes, Bo Nix, Daniel Jones, and Mac Jones carry current Sleeper injury flags. These flags are display context only and do not alter this review board.

Promotion review query job: `caf8d1b1-712b-475e-b3b7-a11905ae6f3f`.
