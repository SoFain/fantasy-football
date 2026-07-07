# Standard BQML V2 Owner-Review Boards

Generated from existing Phase 33.5 BQML models and summary rows. No live ranking table, champion table, or backtest detail table was written.

Review limits: QB45, RB80, WR100, TE35. Standard is the only scoring profile in scope. Board rows aggregate weekly predictions to one player-season row for owner review.

## Phase 33.10 Overall-Board Rule Status

Phase 33.10 tested Standard-only cross-position board rules that combine the Phase 33.9 position finalists into one overall board.

Owner-review rule: `standard_bqml_v2_conservative_overlay_v0`.

Rule shape:

- 70 percent Current Pigskin normalized score.
- 20 percent BQML VOR score.
- 10 percent BQML finalist safety or elite score.

Combined 2024-2025 read:

| Rule | Top-24 | Top-50 | Top-100 | Points cap100 | VOR cap100 |
|---|---:|---:|---:|---:|---:|
| Conservative overlay | 0.479 | 0.560 | 0.810 | 1.022 | 1.081 |
| Current Pigskin baseline | 0.417 | 0.550 | 0.810 | 1.001 | 1.074 |

The overlay is owner-review evidence only. It did not write live rankings, activate a champion, train models, or replace Current Pigskin.

## Selected Candidates

| Position | Owner-review candidate | Decision note |
|---|---|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | Standard v2 challenger, but prior BQML linear points remains a QB comparison warning. |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | Strong Standard v2 challenger with 2025 VOR denominator warning. |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` | Strong Standard v2 challenger. |
| TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` | Owner-review finalist for 2025 holdout VOR and bust-risk control. Linear points remains component evidence. |

## Summary Metrics

| Candidate | Season | Top-N | Points captured | VOR captured | Pairwise | Overall pairwise | NDCG@K | Bust rate | Missing input |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `bqml_v2_standard_qb_logistic_bust_inverse_v0` | 2024 | 0.523 | 0.754 | 0.574 | 0.693 | 0.694 | 0.734 | 0.102 | 0.000 |
| `bqml_v2_standard_qb_logistic_bust_inverse_v0` | 2025 | 0.852 | 0.890 | 0.851 | 0.656 | 0.658 | 0.832 | 0.000 | 0.000 |
| `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 2024 | 0.634 | 0.796 | 0.736 | 0.781 | 0.785 | 0.730 | 0.051 | 0.000 |
| `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 2025 | 1.000 | 1.000 | null | 0.815 | 0.820 | 0.842 | 0.000 | 0.000 |
| `bqml_v2_standard_te_linear_points_v0` | 2024 | 0.463 | 0.652 | 0.551 | null | null | 0.584 | 0.231 | 0.000 |
| `bqml_v2_standard_te_linear_points_v0` | 2025 | 0.759 | 0.832 | 0.823 | null | null | 0.687 | 0.005 | 0.000 |
| `bqml_v2_standard_te_logistic_bust_inverse_v0` | 2024 | 0.454 | 0.620 | 0.497 | 0.764 | 0.775 | 0.564 | 0.259 | 0.000 |
| `bqml_v2_standard_te_logistic_bust_inverse_v0` | 2025 | 0.759 | 0.843 | 0.836 | 0.751 | 0.768 | 0.705 | 0.005 | 0.000 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2024 | 0.431 | 0.624 | 0.505 | 0.760 | 0.740 | 0.558 | 0.269 | 0.000 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2025 | 0.831 | 0.887 | 0.886 | 0.766 | 0.782 | 0.751 | 0.000 | 0.000 |

## TE Candidate Check

TE linear points has the best combined scorecard VOR from Phase 33.5, but its persisted pairwise fields are null. TE bust inverse has the stronger 2025 holdout VOR and lower 2025 bust rate in the selected comparison. Phase 33.6 uses bust inverse as the TE finalist and keeps linear points as a component signal. No TE champion was activated.

## Cutline Audit

| Candidate | Season | Cutline | Player at cutline | Score | Season VOR | Weeks |
|---|---:|---:|---|---:|---:|---:|
| `bqml_v2_standard_qb_logistic_bust_inverse_v0` | 2024 | 12 | J.Burrow (CIN) | 0.5133 | 106.100 | 17 |
| `bqml_v2_standard_qb_logistic_bust_inverse_v0` | 2024 | 24 | G.Smith (SEA) | 0.3785 | 37.000 | 17 |
| `bqml_v2_standard_qb_logistic_bust_inverse_v0` | 2024 | 45 | J.Brissett (NE) | 0.2702 | 0 | 7 |
| `bqml_v2_standard_qb_logistic_bust_inverse_v0` | 2025 | 12 | Baker Mayfield (TB) | 0.4173 | 154.580 | 17 |
| `bqml_v2_standard_qb_logistic_bust_inverse_v0` | 2025 | 24 | Jacoby Brissett (ARI) | 0.2398 | 156.220 | 14 |
| `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 2024 | 12 | K.Williams (LA) | 0.6417 | 105.300 | 16 |
| `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 2024 | 24 | J.Cook (BUF) | 0.5710 | 111.200 | 16 |
| `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 2024 | 36 | D.Foreman (CLE) | 0.4494 | 0 | 10 |
| `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 2024 | 48 | T.Spears (TEN) | 0.3459 | 26.200 | 12 |
| `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 2024 | 80 | D.Evans (CHI) | 0.2167 | 0 | 1 |
| `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 2025 | 12 | Kareem Hunt (KC) | 0.4405 | 0 | 17 |
| `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 2025 | 24 | Audric Estimé (NO) | 0.1841 | 0 | 5 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2024 | 12 | M.Evans (TB) | 0.3906 | 69.000 | 14 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2024 | 24 | D.Samuel (SF) | 0.2861 | 24.800 | 15 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2024 | 36 | T.McLaurin (WAS) | 0.2523 | 69.080 | 17 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2024 | 48 | D.London (ATL) | 0.1782 | 57.580 | 17 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2024 | 60 | O.Beckham (MIA) | 0.1388 | 0 | 8 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2024 | 100 | T.Palmer (TB) | 0.0804 | 0.100 | 15 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2025 | 12 | Courtland Sutton (DEN) | 0.2878 | 127.200 | 17 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2025 | 24 | Darius Slayton (NYG) | 0.1250 | 46.100 | 14 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2025 | 36 | Mecole Hardman (BUF) | 0.0866 | 0 | 2 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2025 | 48 | Jamal Agnew (ATL) | 0.0658 | 0 | 11 |
| `bqml_v2_standard_wr_logistic_elite_v0` | 2025 | 60 | River Cracraft (WAS) | 0.0463 | 0 | 2 |
| `bqml_v2_standard_te_logistic_bust_inverse_v0` | 2024 | 6 | D.Njoku (CLE) | 0.4548 | 27.800 | 11 |
| `bqml_v2_standard_te_logistic_bust_inverse_v0` | 2024 | 12 | J.Ferguson (DAL) | 0.3965 | 6.100 | 14 |
| `bqml_v2_standard_te_logistic_bust_inverse_v0` | 2024 | 18 | C.Otton (TB) | 0.3342 | 23.600 | 14 |
| `bqml_v2_standard_te_logistic_bust_inverse_v0` | 2024 | 35 | F.Moreau (NO) | 0.2154 | 14.400 | 16 |
| `bqml_v2_standard_te_logistic_bust_inverse_v0` | 2025 | 6 | T.J. Hockenson (MIN) | 0.4481 | 37.500 | 15 |
| `bqml_v2_standard_te_logistic_bust_inverse_v0` | 2025 | 12 | Jonnu Smith (PIT) | 0.3584 | 23.900 | 17 |
| `bqml_v2_standard_te_logistic_bust_inverse_v0` | 2025 | 18 | Will Dissly (LAC) | 0.2570 | 0 | 8 |
| `bqml_v2_standard_te_logistic_bust_inverse_v0` | 2025 | 35 | Chris Manhertz (NYG) | 0.1449 | 0 | 4 |

## 2024 Top Board Samples

### QB `bqml_v2_standard_qb_logistic_bust_inverse_v0`

| Rank | Player | Team | Score | Profile points | Season VOR | Weeks |
|---:|---|---|---:|---:|---:|---:|
| 1 | J.Hurts | PHI | 0.8037 | 89.067 | 87.940 | 15 |
| 2 | J.Allen | BUF | 0.7918 | 95.330 | 134.900 | 16 |
| 3 | L.Jackson | BAL | 0.7652 | 80.497 | 152.320 | 17 |
| 4 | P.Mahomes | KC | 0.6461 | 84.376 | 36.340 | 16 |
| 5 | K.Murray | ARI | 0.5983 | 77.316 | 60.080 | 17 |
| 6 | J.Fields | PIT | 0.5897 | 64.006 | 24.880 | 10 |
| 7 | C.Wentz | KC | 0.5734 | 72.370 | 0 | 2 |
| 8 | D.Prescott | DAL | 0.5552 | 75.669 | 14.900 | 8 |
| 9 | A.Richardson | IND | 0.5545 | 72.680 | 23.020 | 11 |
| 10 | J.Herbert | LAC | 0.5470 | 75.680 | 43.920 | 17 |
| 11 | D.Jones | NYG | 0.5182 | 56.925 | 18.680 | 10 |
| 12 | J.Burrow | CIN | 0.5133 | 75.033 | 106.100 | 17 |

### RB `bqml_v2_standard_rb_logistic_bust_inverse_v0`

| Rank | Player | Team | Score | Profile points | Season VOR | Weeks |
|---:|---|---|---:|---:|---:|---:|
| 1 | C.McCaffrey | SF | 0.7736 | 64.823 | 7.100 | 4 |
| 2 | D.Henry | BAL | 0.7190 | 68.846 | 179.500 | 17 |
| 3 | J.Taylor | IND | 0.7069 | 58.797 | 118.300 | 14 |
| 4 | J.Jacobs | GB | 0.6952 | 51.661 | 121.500 | 17 |
| 5 | S.Barkley | PHI | 0.6873 | 47.305 | 193.000 | 16 |
| 6 | B.Hall | NYJ | 0.6809 | 52.692 | 66.900 | 16 |
| 7 | A.Kamara | NO | 0.6711 | 49.208 | 89.200 | 14 |
| 8 | J.Mixon | HOU | 0.6691 | 54.450 | 108.700 | 14 |
| 9 | A.Ekeler | WAS | 0.6653 | 56.456 | 22.900 | 12 |
| 10 | T.Etienne | JAX | 0.6556 | 46.412 | 3.300 | 15 |
| 11 | I.Pacheco | KC | 0.6454 | 38.624 | 5.600 | 7 |
| 12 | K.Williams | LA | 0.6417 | 42.542 | 105.300 | 16 |

### WR `bqml_v2_standard_wr_logistic_elite_v0`

| Rank | Player | Team | Score | Profile points | Season VOR | Weeks |
|---:|---|---|---:|---:|---:|---:|
| 1 | T.Hill | MIA | 0.5595 | 53.897 | 29.500 | 17 |
| 2 | K.Wilkerson | LV | 0.5434 | 64.800 | 0 | 1 |
| 3 | J.Jefferson | MIN | 0.5107 | 54.212 | 78.060 | 17 |
| 4 | D.Adams | NYJ | 0.4906 | 49.650 | 61.000 | 14 |
| 5 | C.Kupp | LA | 0.4813 | 53.535 | 37.300 | 12 |
| 6 | C.Lamb | DAL | 0.4600 | 49.115 | 49.100 | 15 |
| 7 | J.Chase | CIN | 0.4424 | 48.364 | 140.580 | 17 |
| 8 | K.Allen | CHI | 0.4306 | 43.241 | 39.900 | 15 |
| 9 | P.Nacua | LA | 0.4286 | 45.529 | 46.300 | 11 |
| 10 | A.St. Brown | DET | 0.4095 | 42.567 | 70.760 | 17 |
| 11 | A.Brown | PHI | 0.3968 | 43.088 | 54.800 | 13 |
| 12 | M.Evans | TB | 0.3906 | 44.860 | 69.000 | 14 |

### TE `bqml_v2_standard_te_logistic_bust_inverse_v0`

| Rank | Player | Team | Score | Profile points | Season VOR | Weeks |
|---:|---|---|---:|---:|---:|---:|
| 1 | T.Kelce | KC | 0.6436 | 41.649 | 23.900 | 16 |
| 2 | S.LaPorta | DET | 0.5423 | 36.071 | 31.400 | 16 |
| 3 | M.Andrews | BAL | 0.5339 | 37.721 | 46.800 | 17 |
| 4 | T.Hockenson | MIN | 0.5247 | 30.695 | 6.700 | 10 |
| 5 | G.Kittle | SF | 0.4981 | 36.101 | 74.200 | 15 |
| 6 | D.Njoku | CLE | 0.4548 | 24.381 | 27.800 | 11 |
| 7 | T.McBride | ARI | 0.4225 | 17.240 | 46.100 | 16 |
| 8 | E.Engram | JAX | 0.4223 | 22.293 | 1.800 | 9 |
| 9 | D.Schultz | HOU | 0.4182 | 26.010 | 9.300 | 17 |
| 10 | D.Goedert | PHI | 0.4123 | 26.629 | 18.300 | 10 |
| 11 | K.Pitts | ATL | 0.4098 | 21.476 | 22.000 | 17 |
| 12 | J.Ferguson | DAL | 0.3965 | 17.828 | 6.100 | 14 |

## 2025 Top Board Samples

### QB `bqml_v2_standard_qb_logistic_bust_inverse_v0`

| Rank | Player | Team | Score | Profile points | Season VOR | Weeks |
|---:|---|---|---:|---:|---:|---:|
| 1 | Josh Allen | BUF | 0.7755 | 95.342 | 241.980 | 16 |
| 2 | Lamar Jackson | BAL | 0.7557 | 87.166 | 114.060 | 13 |
| 3 | Patrick Mahomes | KC | 0.6034 | 79.512 | 157.700 | 14 |
| 4 | Kyler Murray | ARI | 0.5603 | 72.012 | 23.260 | 5 |
| 5 | Daniel Jones | IND | 0.5173 | 54.781 | 124.760 | 13 |
| 6 | Dak Prescott | DAL | 0.4651 | 68.376 | 181.660 | 17 |
| 7 | Russell Wilson | NYG | 0.4440 | 63.757 | 19.540 | 6 |
| 8 | Joshua Dobbs | NE | 0.4434 | 55.034 | 0 | 4 |
| 9 | Geno Smith | LV | 0.4269 | 64.808 | 73.320 | 15 |
| 10 | Jared Goff | DET | 0.4217 | 70.265 | 168.880 | 17 |
| 11 | Marcus Mariota | WAS | 0.4181 | 48.338 | 62.820 | 10 |
| 12 | Baker Mayfield | TB | 0.4173 | 63.676 | 154.580 | 17 |

### RB `bqml_v2_standard_rb_logistic_bust_inverse_v0`

| Rank | Player | Team | Score | Profile points | Season VOR | Weeks |
|---:|---|---|---:|---:|---:|---:|
| 1 | Saquon Barkley | PHI | 0.7584 | 63.127 | 0 | 16 |
| 2 | Christian McCaffrey | SF | 0.7157 | 58.518 | 0 | 17 |
| 3 | Alvin Kamara | NO | 0.7022 | 48.747 | 0 | 11 |
| 4 | Derrick Henry | BAL | 0.6708 | 64.524 | 0 | 17 |
| 5 | Josh Jacobs | GB | 0.6633 | 56.536 | 0 | 15 |
| 6 | Tony Pollard | TEN | 0.6416 | 43.937 | 0 | 17 |
| 7 | Aaron Jones | MIN | 0.6269 | 42.535 | 0 | 12 |
| 8 | James Conner | ARI | 0.6228 | 50.946 | 0 | 3 |
| 9 | David Montgomery | DET | 0.5481 | 47.872 | 0 | 17 |
| 10 | Nick Chubb | HOU | 0.5315 | 42.403 | 0 | 15 |
| 11 | Austin Ekeler | WAS | 0.5045 | 44.450 | 0 | 2 |
| 12 | Kareem Hunt | KC | 0.4405 | 29.979 | 0 | 17 |

### WR `bqml_v2_standard_wr_logistic_elite_v0`

| Rank | Player | Team | Score | Profile points | Season VOR | Weeks |
|---:|---|---|---:|---:|---:|---:|
| 1 | A.J. Brown | PHI | 0.4420 | 46.370 | 125.100 | 15 |
| 2 | Tyreek Hill | MIA | 0.4289 | 50.109 | 24.100 | 4 |
| 3 | Davante Adams | LA | 0.4281 | 46.094 | 145.900 | 14 |
| 4 | Mike Evans | TB | 0.4075 | 45.000 | 44.200 | 8 |
| 5 | Keenan Allen | LAC | 0.3720 | 40.760 | 83.100 | 17 |
| 6 | Stefon Diggs | NE | 0.3457 | 42.952 | 106.100 | 17 |
| 7 | Chris Godwin Jr. | TB | 0.3447 | 37.182 | 39.100 | 9 |
| 8 | Cooper Kupp | SEA | 0.3224 | 42.437 | 52.800 | 16 |
| 9 | DJ Moore | CHI | 0.2981 | 36.604 | 105.180 | 17 |
| 10 | Terry McLaurin | WAS | 0.2924 | 36.706 | 64.500 | 10 |
| 11 | Calvin Ridley | TEN | 0.2880 | 34.012 | 18.300 | 7 |
| 12 | Courtland Sutton | DEN | 0.2878 | 32.688 | 127.200 | 17 |

### TE `bqml_v2_standard_te_logistic_bust_inverse_v0`

| Rank | Player | Team | Score | Profile points | Season VOR | Weeks |
|---:|---|---|---:|---:|---:|---:|
| 1 | Travis Kelce | KC | 0.5709 | 35.616 | 85.300 | 17 |
| 2 | George Kittle | SF | 0.5430 | 38.103 | 84.200 | 11 |
| 3 | David Njoku | CLE | 0.4829 | 28.259 | 36.600 | 11 |
| 4 | Darren Waller | MIA | 0.4790 | 24.400 | 50.700 | 9 |
| 5 | Evan Engram | DEN | 0.4537 | 23.567 | 26.900 | 16 |
| 6 | T.J. Hockenson | MIN | 0.4481 | 27.395 | 37.500 | 15 |
| 7 | Dallas Goedert | PHI | 0.4117 | 25.153 | 96.800 | 15 |
| 8 | Mark Andrews | BAL | 0.4069 | 32.992 | 53.700 | 17 |
| 9 | Zach Ertz | WAS | 0.3977 | 22.589 | 52.100 | 13 |
| 10 | Hunter Henry | NE | 0.3906 | 19.848 | 86.700 | 17 |
| 11 | Taysom Hill | NO | 0.3709 | 33.833 | 16.620 | 13 |
| 12 | Jonnu Smith | PIT | 0.3584 | 19.131 | 23.900 | 17 |

## Movement Samples

### QB

| Player | 2024 rank | 2025 rank | Movement | 2024 team | 2025 team |
|---|---:|---:|---:|---|---|
| Marcus Mariota | 44 | 11 | 33 | WAS | WAS |
| Andy Dalton | 42 | 21 | 21 | CAR | CAR |
| Jacoby Brissett | 45 | 24 | 21 | NE | ARI |
| Sam Darnold | 36 | 16 | 20 | MIN | SEA |
| Aaron Rodgers | 41 | 22 | 19 | NYJ | PIT |
| Joshua Dobbs | 26 | 8 | 18 | SF | NE |
| Baker Mayfield | 30 | 12 | 18 | TB | TB |
| Joe Flacco | 37 | 19 | 18 | IND | CIN |

### RB

| Player | 2024 rank | 2025 rank | Movement | 2024 team | 2025 team |
|---|---:|---:|---:|---|---|
| D'Ernest Johnson | 78 | 22 | 56 | JAX | NE |
| Ty Johnson | 73 | 21 | 52 | BUF | BUF |
| Craig Reynolds | 75 | 23 | 52 | DET | DET |
| Justice Hill | 63 | 16 | 47 | BAL | BAL |
| Myles Gaskin | 67 | 27 | 40 | MIN | SEA |
| Kareem Hunt | 43 | 12 | 31 | KC | KC |
| Samaje Perine | 49 | 20 | 29 | KC | CIN |
| Miles Sanders | 41 | 15 | 26 | CAR | DAL |

### WR

| Player | 2024 rank | 2025 rank | Movement | 2024 team | 2025 team |
|---|---:|---:|---:|---|---|
| Lil'Jordan Humphrey | 98 | 44 | 54 | DEN | DEN |
| Marquez Valdes-Scantling | 87 | 35 | 52 | NO | PIT |
| Kalif Raymond | 97 | 45 | 52 | DET | DET |
| Noah Brown | 74 | 23 | 51 | WAS | WAS |
| Mack Hollins | 89 | 38 | 51 | BUF | NE |
| Greg Dortch | 82 | 32 | 50 | ARI | ARI |
| Cedrick Wilson Jr. | 96 | 46 | 50 | NO | MIA |
| Demarcus Robinson | 70 | 26 | 44 | LA | SF |

### TE

| Player | 2024 rank | 2025 rank | Movement | 2024 team | 2025 team |
|---|---:|---:|---:|---|---|
| Jonnu Smith | 31 | 12 | 19 | MIA | PIT |
| Mike Gesicki | 32 | 16 | 16 | CIN | CIN |
| Noah Fant | 33 | 17 | 16 | SEA | CIN |
| Foster Moreau | 35 | 21 | 14 | NO | NO |
| Taysom Hill | 23 | 11 | 12 | NO | NO |
| Tanner Hudson | 34 | 25 | 9 | CIN | CIN |
| Tyler Conklin | 22 | 15 | 7 | NYJ | LAC |
| Hunter Henry | 16 | 10 | 6 | NE | NE |

## No-Activation Verification

| Table | Relevant row count |
|---|---:|
| `ranking_backtest_runs` | 2 |
| `ranking_backtest_candidate_summaries` | 32 |
| `ranking_backtest_results` | 0 |
| `ranking_formula_champions` | 0 |
| `analytics_pigskin_rankings_standard` | 285 |

## Overall Board Interpretation

This is a position-review board, not a production overall-board builder. A production-grade Standard overall board still needs an owner-approved VOR and scarcity rule, plus a separate activation phase. No global all-profile winner is recommended.
## Phase 33.9 Original vs Patched Review

Phase 33.9 compared original Standard BQML v2 models against patched Standard BQML v2 models using read-only `ML.PREDICT`, persisted summary evidence, and generated owner-review boards for 2024 validation and 2025 holdout.

No live rankings changed. No champion was activated.

Selected Standard owner-review finalists:

| Position | Finalist | Status | Warning |
|---|---|---|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | original Standard v2 finalist | Patched QB adds `passing_epa_per_play`, but the summary and movement evidence remain noisy. |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | original Standard v2 finalist | Patched logistic elite is useful component evidence, especially 2024 top-N/points. |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` | original Standard v2 finalist | Patched bust inverse improves 2025 points/VOR, but original keeps stronger top-N/NDCG reads. |
| TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` | original Standard v2 finalist | Patched bust inverse improves 2025. 2024 TE still favors original linear points. |

Owner-review board notes:

- Position output remains capped at QB45, RB80, WR100, TE35.
- TE owner-review output stays TE35.
- Some generated historical boards show odd or low-volume names near cutlines. Treat those as movement warnings.
- The 2025 board slice is thin or rank-collapsed for several positions, so summary metrics carry more weight than generated board movement.
- Current Pigskin remains live.

Overall-board gap:

- No production-grade Standard overall board rule exists yet.
- A later phase must define VOR, scarcity, cutline, bust-safety, and deterministic tie-breaker rules before champion review.
