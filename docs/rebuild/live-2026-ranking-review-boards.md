# Live 2026 Ranking Review Boards

Review version: `phase32_30_live_2026_ppr_review_20260706`

Scope: PPR-only BQML review boards from the 2026 candidate universe. Active live rankings for all four scoring profiles were verified separately, but non-PPR BQML boards were not generated because `analytics_pigskin_rankings_candidates` only has `ppr` rows for 2026.

Phase 32.31 Standard-first audit result: non-PPR review inputs are blocked. `standard`, `half_ppr`, and `gng_keeper` each have active live final rankings and profile fantasy-point history, but they do not have 2026 review candidate rows. Do not derive those boards from the PPR candidate slice.

TE owner-review output is capped at TE35. Live ranking tables still have TE60 per scoring profile and were not changed.

Owner-review scoring profile order is Standard, Half PPR, PPR, then GNG Keeper. Phase 32.30 can only display PPR BQML review boards because the available 2026 candidate input is PPR-only. Standard, Half PPR, and GNG Keeper are blocked for this review-board run. Do not treat the PPR challenger as a global winner across scoring systems.

Profile-specific challenger classification:

| Scoring profile | Board status | Best review-only challenger |
|---|---|---|
| standard | blocked | not selected |
| half_ppr | blocked | not selected |
| ppr | generated with warnings | ranking_bqml_enriched_logistic_elite_v1 |
| gng_keeper | blocked | not selected |

Phase 32.31 classification:

| Scoring profile | Candidate rows | Active baseline rows | Review input status |
|---|---:|---:|---|
| standard | 0 | 285 | blocked |
| half_ppr | 0 | 285 | blocked |
| ppr | 936 | 285 | ready with warnings |
| gng_keeper | 0 | 285 | blocked |

## Model Summary
| Model | Rows | Score min | Score max | Score avg | Avg missing % |
| --- | --- | --- | --- | --- | --- |
| enriched_logistic | 936 | 0.66 | 99.80 | 15.47 | 77.9 |
| enriched_linear_points | 936 | -340.08 | 620.70 | 24.55 | 77.9 |
| ngs_logistic_context | 936 | 0.67 | 99.71 | 15.25 | 77.9 |
| ngs_linear_points_context | 936 | -147.96 | 22766.48 | 1544.69 | 77.9 |

## PPR Current Pigskin Top 50 Overall
| Rank | Player | Pos | Team | Score | Pos rank |
| --- | --- | --- | --- | --- | --- |
| 1 | Jaxon Smith-Njigba | WR | SEA | 98.50 | 1 |
| 2 | Josh Allen | QB | BUF | 98.50 | 1 |
| 3 | Christian McCaffrey | RB | SF | 98.00 | 1 |
| 4 | Trey McBride | TE | ARI | 98.00 | 1 |
| 5 | Puka Nacua | WR | LAR | 97.80 | 2 |
| 6 | Ja'Marr Chase | WR | CIN | 96.50 | 3 |
| 7 | Drake Maye | QB | NE | 96.00 | 2 |
| 8 | Amon-Ra St. Brown | WR | DET | 95.90 | 4 |
| 9 | Bijan Robinson | RB | ATL | 95.00 | 2 |
| 10 | Patrick Mahomes | QB | KC | 95.00 | 3 |
| 11 | Drake London | WR | ATL | 94.20 | 5 |
| 12 | Brock Bowers | TE | LV | 94.00 | 2 |
| 13 | Jalen Hurts | QB | PHI | 94.00 | 4 |
| 14 | Garrett Wilson | WR | NYJ | 93.00 | 6 |
| 15 | Jahmyr Gibbs | RB | DET | 93.00 | 3 |
| 16 | Brock Purdy | QB | SF | 92.50 | 5 |
| 17 | Rashee Rice | WR | KC | 91.50 | 7 |
| 18 | George Kittle | TE | SF | 91.00 | 3 |
| 19 | Jonathan Taylor | RB | IND | 91.00 | 4 |
| 20 | Chris Olave | WR | NO | 90.80 | 8 |
| 21 | De'Von Achane | RB | MIA | 90.00 | 5 |
| 22 | Trevor Lawrence | QB | JAX | 90.00 | 6 |
| 23 | A.J. Brown | WR | NE | 89.90 | 9 |
| 24 | Justin Jefferson | WR | MIN | 89.00 | 10 |
| 25 | Matthew Stafford | QB | LAR | 88.50 | 7 |
| 26 | CeeDee Lamb | WR | DAL | 88.20 | 11 |
| 27 | James Cook | RB | BUF | 88.00 | 6 |
| 28 | Tucker Kraft | TE | GB | 88.00 | 4 |
| 29 | Zay Flowers | WR | BAL | 87.50 | 12 |
| 30 | Jordan Love | QB | GB | 87.00 | 8 |
| 31 | George Pickens | WR | DAL | 86.90 | 13 |
| 32 | Dak Prescott | QB | DAL | 86.00 | 9 |
| 33 | Kyren Williams | RB | LAR | 86.00 | 7 |
| 34 | Nico Collins | WR | HOU | 86.00 | 14 |
| 35 | Sam LaPorta | TE | DET | 86.00 | 5 |
| 36 | Davante Adams | WR | LAR | 85.10 | 15 |
| 37 | Caleb Williams | QB | CHI | 85.00 | 10 |
| 38 | Dallas Goedert | TE | PHI | 85.00 | 6 |
| 39 | Malik Nabers | WR | NYG | 84.50 | 16 |
| 40 | Bo Nix | QB | DEN | 84.00 | 11 |
| 41 | Kyle Pitts | TE | ATL | 84.00 | 7 |
| 42 | Saquon Barkley | RB | PHI | 84.00 | 8 |
| 43 | Daniel Jones | QB | IND | 83.00 | 12 |
| 44 | Travis Kelce | TE | KC | 83.00 | 8 |
| 45 | Wan'Dale Robinson | WR | TEN | 83.00 | 17 |
| 46 | Tetairoa McMillan | WR | CAR | 82.20 | 18 |
| 47 | Chase Brown | RB | CIN | 82.00 | 9 |
| 48 | Justin Herbert | QB | LAC | 82.00 | 13 |
| 49 | Rome Odunze | WR | CHI | 81.50 | 19 |
| 50 | Lamar Jackson | QB | BAL | 81.00 | 14 |

## PPR BQML Logistic Top 50 Overall
| Rank | Player | Pos | Sleeper team | Score | Current rank | Delta | Missing % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Bijan Robinson | RB | unknown | 99.80 | 9 | +8 | 73.6 |
| 2 | Jonathan Taylor | RB | unknown | 99.79 | 19 | +17 | 73.6 |
| 3 | James Cook | RB | unknown | 99.51 | 27 | +24 | 73.6 |
| 4 | Jahmyr Gibbs | RB | unknown | 99.37 | 15 | +11 | 73.6 |
| 5 | De'Von Achane | RB | unknown | 99.04 | 21 | +16 | 73.6 |
| 6 | Kyren Williams | RB | unknown | 98.83 | 33 | +27 | 73.6 |
| 7 | Chase Brown | RB | unknown | 98.63 | 47 | +40 | 73.6 |
| 8 | Travis Etienne | RB | unknown | 98.51 | 62 | +54 | 73.6 |
| 9 | Javonte Williams | RB | unknown | 98.30 | 52 | +43 | 73.6 |
| 10 | Ashton Jeanty | RB | unknown | 98.27 | 79 | +69 | 73.6 |
| 11 | Breece Hall | RB | unknown | 97.56 | 69 | +58 | 73.6 |
| 12 | Rico Dowdle | RB | unknown | 97.37 | 98 | +86 | 73.6 |
| 13 | D'Andre Swift | RB | unknown | 97.23 | 72 | +59 | 73.6 |
| 14 | Jaylen Warren | RB | unknown | 96.00 | 84 | +70 | 73.6 |
| 15 | Kenneth Walker III | RB | unknown | 95.08 | 129 | +114 | 73.6 |
| 16 | Quinshon Judkins | RB | unknown | 94.50 | 100 | +84 | 73.6 |
| 17 | TreVeyon Henderson | RB | unknown | 91.45 | 105 | +88 | 73.6 |
| 18 | Puka Nacua | WR | unknown | 90.52 | 5 | -13 | 74.7 |
| 19 | Woody Marks | RB | unknown | 90.17 | 156 | +137 | 73.6 |
| 20 | Tyrone Tracy Jr. | RB | unknown | 89.78 | 132 | +112 | 73.6 |
| 21 | Zach Charbonnet | RB | unknown | 88.47 | 137 | +116 | 73.6 |
| 22 | RJ Harvey | RB | unknown | 85.36 | 159 | +137 | 73.6 |
| 23 | Jaxon Smith-Njigba | WR | unknown | 84.91 | 1 | -22 | 74.7 |
| 24 | Kenneth Gainwell | RB | unknown | 84.51 | 119 | +95 | 73.6 |
| 25 | Kyle Monangai | RB | unknown | 84.12 | 161 | +136 | 73.6 |
| 26 | Bucky Irving | RB | unknown | 83.86 | 93 | +67 | 73.6 |
| 27 | Saquon Barkley | RB | PHI | 83.60 | 42 | +15 | 14.9 |
| 28 | Drake Maye | QB | unknown | 83.18 | 7 | -21 | 73.6 |
| 29 | Trey McBride | TE | unknown | 81.81 | 4 | -25 | 74.7 |
| 30 | Ja'Marr Chase | WR | unknown | 81.52 | 6 | -24 | 74.7 |
| 31 | Jacory Croskey-Merritt | RB | unknown | 80.61 | 171 | +140 | 73.6 |
| 32 | Amon-Ra St. Brown | WR | unknown | 79.86 | 8 | -24 | 74.7 |
| 33 | Derrick Henry | RB | BAL | 78.73 | 87 | +54 | 12.6 |
| 34 | Josh Allen | QB | BUF | 78.46 | 2 | -32 | 18.4 |
| 35 | Rachaad White | RB | unknown | 78.03 | 148 | +113 | 73.6 |
| 36 | Alvin Kamara | RB | NO | 77.27 | 143 | +107 | 14.9 |
| 37 | J.K. Dobbins | RB | unknown | 76.55 | 107 | +70 | 73.6 |
| 38 | Lamar Jackson | QB | BAL | 75.55 | 50 | +12 | 13.8 |
| 39 | Omarion Hampton | RB | unknown | 75.18 | 66 | +27 | 73.6 |
| 40 | Kimani Vidal | RB | unknown | 75.09 | 190 | +150 | 73.6 |
| 41 | Rhamondre Stevenson | RB | unknown | 75.01 | 115 | +74 | 73.6 |
| 42 | Christian McCaffrey | RB | SF | 74.86 | 3 | -39 | 12.6 |
| 43 | Jordan Mason | RB | unknown | 74.70 | 175 | +132 | 73.6 |
| 44 | Josh Jacobs | RB | unknown | 73.58 | 57 | +13 | 14.9 |
| 45 | Chuba Hubbard | RB | unknown | 72.71 | 167 | +122 | 73.6 |
| 46 | George Pickens | WR | unknown | 72.05 | 31 | -15 | 74.7 |
| 47 | Blake Corum | RB | unknown | 71.08 | 181 | +134 | 73.6 |
| 48 | Chris Olave | WR | unknown | 67.65 | 20 | -28 | 74.7 |
| 49 | James Conner | RB | ARI | 67.56 | 123 | +74 | 14.9 |
| 50 | Tyler Allgeier | RB | unknown | 67.06 | 202 | +152 | 73.6 |

## PPR BQML Linear Points Top 50 Overall
| Rank | Player | Pos | Sleeper team | Score | Current rank | Delta | Missing % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ja'Marr Chase | WR | unknown | 620.70 | 6 | +5 | 74.7 |
| 2 | Amon-Ra St. Brown | WR | unknown | 580.95 | 8 | +6 | 74.7 |
| 3 | Trey McBride | TE | unknown | 574.81 | 4 | +1 | 74.7 |
| 4 | Puka Nacua | WR | unknown | 554.22 | 5 | +1 | 74.7 |
| 5 | Jaxon Smith-Njigba | WR | unknown | 549.93 | 1 | -4 | 74.7 |
| 6 | Chris Olave | WR | unknown | 527.70 | 20 | +14 | 74.7 |
| 7 | Justin Jefferson | WR | unknown | 474.34 | 24 | +17 | 74.7 |
| 8 | George Pickens | WR | unknown | 470.21 | 31 | +23 | 74.7 |
| 9 | Wan'Dale Robinson | WR | unknown | 469.94 | 45 | +36 | 74.7 |
| 10 | Michael Wilson | WR | unknown | 425.42 | 77 | +67 | 74.7 |
| 11 | Emeka Egbuka | WR | unknown | 425.40 | 67 | +56 | 74.7 |
| 12 | Tetairoa McMillan | WR | unknown | 417.94 | 46 | +34 | 74.7 |
| 13 | Nico Collins | WR | unknown | 408.78 | 34 | +21 | 74.7 |
| 14 | CeeDee Lamb | WR | unknown | 401.01 | 26 | +12 | 74.7 |
| 15 | Kyle Pitts | TE | unknown | 399.33 | 41 | +26 | 74.7 |
| 16 | Zay Flowers | WR | unknown | 390.84 | 29 | +13 | 74.7 |
| 17 | Drake London | WR | unknown | 389.27 | 11 | -6 | 74.7 |
| 18 | DeVonta Smith | WR | unknown | 387.96 | 51 | +33 | 74.7 |
| 19 | Tyler Warren | TE | unknown | 369.35 | 54 | +35 | 74.7 |
| 20 | Michael Pittman | WR | unknown | 368.66 | 126 | +106 | 74.7 |
| 21 | Ladd McConkey | WR | unknown | 358.45 | 86 | +65 | 74.7 |
| 22 | Jerry Jeudy | WR | unknown | 353.55 | 106 | +84 | 74.7 |
| 23 | Juwan Johnson | TE | unknown | 343.96 | 76 | +53 | 74.7 |
| 24 | Harold Fannin Jr. | TE | unknown | 342.82 | 90 | +66 | 74.7 |
| 25 | Troy Franklin | WR | unknown | 342.53 | 102 | +77 | 74.7 |
| 26 | Jaylen Waddle | WR | unknown | 342.23 | 55 | +29 | 74.7 |
| 27 | Jameson Williams | WR | unknown | 341.35 | 71 | +44 | 74.7 |
| 28 | Jake Ferguson | TE | unknown | 340.99 | 83 | +55 | 74.7 |
| 29 | Tee Higgins | WR | unknown | 337.67 | 58 | +29 | 74.7 |
| 30 | Khalil Shakir | WR | unknown | 316.95 | 114 | +84 | 74.7 |
| 31 | Rome Odunze | WR | unknown | 314.29 | 49 | +18 | 74.7 |
| 32 | Parker Washington | WR | unknown | 311.82 | 99 | +67 | 74.7 |
| 33 | Jauan Jennings | WR | unknown | 307.15 | 92 | +59 | 74.7 |
| 34 | Elic Ayomanor | WR | unknown | 300.73 | 109 | +75 | 74.7 |
| 35 | Brian Thomas Jr. | WR | unknown | 300.60 | 122 | +87 | 74.7 |
| 36 | Brock Bowers | TE | unknown | 297.32 | 12 | -24 | 74.7 |
| 37 | Tre Tucker | WR | unknown | 296.98 | 95 | +58 | 74.7 |
| 38 | Alec Pierce | WR | unknown | 294.74 | 63 | +25 | 74.7 |
| 39 | Romeo Doubs | WR | unknown | 293.45 | 94 | +55 | 74.7 |
| 40 | Rashid Shaheed | WR | unknown | 292.71 | 150 | +110 | 74.7 |
| 41 | Josh Downs | WR | unknown | 292.20 | 149 | +108 | 74.7 |
| 42 | Quentin Johnston | WR | unknown | 288.33 | 78 | +36 | 74.7 |
| 43 | Colston Loveland | TE | unknown | 279.35 | 80 | +37 | 74.7 |
| 44 | Cade Otton | TE | unknown | 273.75 | 113 | +69 | 74.7 |
| 45 | Rashee Rice | WR | unknown | 271.54 | 17 | -28 | 74.7 |
| 46 | Jordan Addison | WR | unknown | 271.47 | 85 | +39 | 74.7 |
| 47 | Chig Okonkwo | TE | unknown | 258.19 | 158 | +111 | 74.7 |
| 48 | Theo Johnson | TE | unknown | 252.77 | 116 | +68 | 74.7 |
| 49 | Darnell Mooney | WR | unknown | 246.25 | 125 | +76 | 74.7 |
| 50 | Adonai Mitchell | WR | unknown | 245.33 | 176 | +126 | 74.7 |

## PPR Side-By-Side Current Top 100
| Current rank | Player | Pos | Team | Current score | Logistic rank | Logistic score | Linear rank | Linear score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Jaxon Smith-Njigba | WR | SEA | 98.50 | 23 | 84.91 | 5 | 549.93 |
| 2 | Josh Allen | QB | BUF | 98.50 | 34 | 78.46 | 181 | 26.19 |
| 3 | Christian McCaffrey | RB | SF | 98.00 | 42 | 74.86 | 210 | 17.25 |
| 4 | Trey McBride | TE | ARI | 98.00 | 29 | 81.81 | 3 | 574.81 |
| 5 | Puka Nacua | WR | LAR | 97.80 | 18 | 90.52 | 4 | 554.22 |
| 6 | Ja'Marr Chase | WR | CIN | 96.50 | 30 | 81.52 | 1 | 620.70 |
| 7 | Drake Maye | QB | NE | 96.00 | 28 | 83.18 | 910 | -129.35 |
| 8 | Amon-Ra St. Brown | WR | DET | 95.90 | 32 | 79.86 | 2 | 580.95 |
| 9 | Bijan Robinson | RB | ATL | 95.00 | 1 | 99.80 | 900 | -93.04 |
| 10 | Patrick Mahomes | QB | KC | 95.00 | 60 | 58.83 | 191 | 21.82 |
| 11 | Drake London | WR | ATL | 94.20 | 80 | 49.17 | 17 | 389.27 |
| 12 | Brock Bowers | TE | LV | 94.00 | 113 | 38.45 | 36 | 297.32 |
| 13 | Jalen Hurts | QB | PHI | 94.00 | 61 | 58.44 | 914 | -146.43 |
| 14 | Garrett Wilson | WR | NYJ | 93.00 | 211 | 19.56 | 56 | 218.83 |
| 15 | Jahmyr Gibbs | RB | DET | 93.00 | 4 | 99.37 | 882 | -53.46 |
| 16 | Brock Purdy | QB | SF | 92.50 | 96 | 45.49 | 858 | -25.12 |
| 17 | Rashee Rice | WR | KC | 91.50 | 114 | 37.86 | 45 | 271.54 |
| 18 | George Kittle | TE | SF | 91.00 | 55 | 60.30 | 244 | 13.09 |
| 19 | Jonathan Taylor | RB | IND | 91.00 | 2 | 99.79 | 935 | -307.48 |
| 20 | Chris Olave | WR | NO | 90.80 | 48 | 67.65 | 6 | 527.70 |
| 21 | De'Von Achane | RB | MIA | 90.00 | 5 | 99.04 | 894 | -76.93 |
| 22 | Trevor Lawrence | QB | JAX | 90.00 | 82 | 49.06 | 907 | -110.31 |
| 23 | A.J. Brown | WR | NE | 89.90 | 66 | 56.59 | 221 | 15.69 |
| 24 | Justin Jefferson | WR | MIN | 89.00 | 85 | 48.48 | 7 | 474.34 |
| 25 | Matthew Stafford | QB | LAR | 88.50 | 112 | 38.76 | 203 | 18.29 |
| 26 | CeeDee Lamb | WR | DAL | 88.20 | 76 | 51.39 | 14 | 401.01 |
| 27 | James Cook | RB | BUF | 88.00 | 3 | 99.51 | 936 | -340.08 |
| 28 | Tucker Kraft | TE | GB | 88.00 | 133 | 32.55 | 78 | 164.89 |
| 29 | Zay Flowers | WR | BAL | 87.50 | 56 | 59.45 | 16 | 390.84 |
| 30 | Jordan Love | QB | GB | 87.00 | 87 | 47.81 | 878 | -50.20 |
| 31 | George Pickens | WR | DAL | 86.90 | 46 | 72.05 | 8 | 470.21 |
| 32 | Dak Prescott | QB | DAL | 86.00 | 98 | 44.58 | 202 | 18.77 |
| 33 | Kyren Williams | RB | LAR | 86.00 | 6 | 98.83 | 933 | -225.34 |
| 34 | Nico Collins | WR | HOU | 86.00 | 70 | 55.54 | 13 | 408.78 |
| 35 | Sam LaPorta | TE | DET | 86.00 | 146 | 29.71 | 72 | 180.22 |
| 36 | Davante Adams | WR | LAR | 85.10 | 52 | 64.60 | 213 | 17.01 |
| 37 | Caleb Williams | QB | CHI | 85.00 | 101 | 43.76 | 902 | -96.69 |
| 38 | Dallas Goedert | TE | PHI | 85.00 | 109 | 38.97 | 277 | 9.43 |
| 39 | Malik Nabers | WR | NYG | 84.50 | 254 | 14.98 | 92 | 138.51 |
| 40 | Bo Nix | QB | DEN | 84.00 | 77 | 50.99 | 906 | -108.20 |
| 41 | Kyle Pitts | TE | ATL | 84.00 | 89 | 47.55 | 15 | 399.33 |
| 42 | Saquon Barkley | RB | PHI | 84.00 | 27 | 83.60 | 195 | 20.93 |
| 43 | Daniel Jones | QB | IND | 83.00 | 97 | 45.08 | 204 | 17.76 |
| 44 | Travis Kelce | TE | KC | 83.00 | 57 | 59.24 | 242 | 13.20 |
| 45 | Wan'Dale Robinson | WR | TEN | 83.00 | 63 | 57.90 | 9 | 469.94 |
| 46 | Tetairoa McMillan | WR | CAR | 82.20 | 83 | 48.94 | 12 | 417.94 |
| 47 | Chase Brown | RB | CIN | 82.00 | 7 | 98.63 | 888 | -61.67 |
| 48 | Justin Herbert | QB | LAC | 82.00 | 107 | 41.00 | 908 | -115.33 |
| 49 | Rome Odunze | WR | CHI | 81.50 | 124 | 35.55 | 31 | 314.29 |
| 50 | Lamar Jackson | QB | BAL | 81.00 | 38 | 75.55 | 178 | 27.95 |
| 51 | DeVonta Smith | WR | PHI | 80.90 | 75 | 51.63 | 18 | 387.96 |
| 52 | Javonte Williams | RB | DAL | 80.00 | 9 | 98.30 | 929 | -212.02 |
| 53 | Terry McLaurin | WR | WAS | 80.00 | 88 | 47.70 | 243 | 13.13 |
| 54 | Tyler Warren | TE | IND | 80.00 | 100 | 44.33 | 19 | 369.35 |
| 55 | Jaylen Waddle | WR | DEN | 79.40 | 103 | 42.51 | 26 | 342.23 |
| 56 | Jayden Daniels | QB | WAS | 79.00 | 206 | 20.00 | 895 | -77.81 |
| 57 | Josh Jacobs | RB | GB | 79.00 | 44 | 73.58 | 212 | 17.13 |
| 58 | Tee Higgins | WR | CIN | 78.80 | 104 | 41.76 | 29 | 337.67 |
| 59 | Courtland Sutton | WR | DEN | 78.00 | 86 | 48.41 | 246 | 13.04 |
| 60 | Dalton Kincaid | TE | BUF | 78.00 | 164 | 25.02 | 75 | 172.52 |
| 61 | Joe Burrow | QB | CIN | 78.00 | 203 | 20.24 | 454 | -4.46 |
| 62 | Travis Etienne | RB | NO | 78.00 | 8 | 98.51 | 932 | -224.99 |
| 63 | Alec Pierce | WR | IND | 77.50 | 106 | 41.15 | 38 | 294.74 |
| 64 | Hunter Henry | TE | NE | 77.00 | 138 | 32.15 | 291 | 7.83 |
| 65 | Jared Goff | QB | DET | 77.00 | 72 | 53.96 | 196 | 20.84 |
| 66 | Omarion Hampton | RB | LAC | 77.00 | 39 | 75.18 | 886 | -58.23 |
| 67 | Emeka Egbuka | WR | TB | 76.90 | 95 | 45.52 | 11 | 425.40 |
| 68 | Jakobi Meyers | WR | JAX | 76.20 | 74 | 51.76 | 252 | 12.35 |
| 69 | Breece Hall | RB | NYJ | 76.00 | 11 | 97.56 | 928 | -211.72 |
| 70 | Dalton Schultz | TE | HOU | 76.00 | 137 | 32.23 | 286 | 8.25 |
| 71 | Jameson Williams | WR | DET | 75.50 | 78 | 49.66 | 27 | 341.35 |
| 72 | D'Andre Swift | RB | CHI | 75.00 | 13 | 97.23 | 922 | -177.72 |
| 73 | Jaxson Dart | QB | NYG | 75.00 | 94 | 45.81 | 909 | -117.99 |
| 74 | Mike Evans | WR | SF | 74.80 | 58 | 59.17 | 233 | 14.54 |
| 75 | Baker Mayfield | QB | TB | 74.00 | 71 | 55.19 | 194 | 21.31 |
| 76 | Juwan Johnson | TE | NO | 74.00 | 105 | 41.55 | 23 | 343.96 |
| 77 | Michael Wilson | WR | ARI | 74.00 | 79 | 49.41 | 10 | 425.42 |
| 78 | Quentin Johnston | WR | LAC | 73.50 | 130 | 33.92 | 42 | 288.33 |
| 79 | Ashton Jeanty | RB | LV | 73.00 | 10 | 98.27 | 920 | -171.07 |
| 80 | Colston Loveland | TE | CHI | 73.00 | 119 | 36.97 | 43 | 279.35 |
| 81 | Christian Watson | WR | GB | 72.80 | 152 | 27.84 | 61 | 198.15 |
| 82 | Jacoby Brissett | QB | ARI | 72.00 | 173 | 23.86 | 254 | 11.70 |
| 83 | Jake Ferguson | TE | DAL | 72.00 | 115 | 37.80 | 28 | 340.99 |
| 84 | Jaylen Warren | RB | PIT | 72.00 | 14 | 96.00 | 919 | -169.36 |
| 85 | Jordan Addison | WR | MIN | 72.00 | 143 | 30.16 | 46 | 271.47 |
| 86 | Ladd McConkey | WR | LAC | 71.50 | 126 | 35.05 | 21 | 358.45 |
| 87 | Derrick Henry | RB | BAL | 71.00 | 33 | 78.73 | 201 | 19.34 |
| 88 | DK Metcalf | WR | PIT | 70.80 | 93 | 45.93 | 248 | 12.83 |
| 89 | Cam Skattebo | RB | NYG | 70.00 | 59 | 58.97 | 868 | -34.72 |
| 90 | Harold Fannin Jr. | TE | CLE | 70.00 | 118 | 37.59 | 24 | 342.82 |
| 91 | Kyler Murray | QB | MIN | 70.00 | 73 | 53.95 | 193 | 21.62 |
| 92 | Jauan Jennings | WR | MIN | 69.50 | 156 | 26.88 | 33 | 307.15 |
| 93 | Bucky Irving | RB | TB | 69.00 | 26 | 83.86 | 913 | -143.12 |
| 94 | Romeo Doubs | WR | NE | 68.80 | 131 | 33.51 | 39 | 293.45 |
| 95 | Tre Tucker | WR | LV | 68.20 | 116 | 37.69 | 37 | 296.98 |
| 96 | Brenton Strange | TE | JAX | 68.00 | 155 | 26.91 | 59 | 209.69 |
| 97 | C.J. Stroud | QB | HOU | 68.00 | 136 | 32.32 | 884 | -57.59 |
| 98 | Rico Dowdle | RB | PIT | 68.00 | 12 | 97.37 | 927 | -196.28 |
| 99 | Parker Washington | WR | JAX | 67.50 | 110 | 38.92 | 32 | 311.82 |
| 100 | Quinshon Judkins | RB | CLE | 67.00 | 16 | 94.50 | 934 | -234.36 |

## QB Position Board: Current Pigskin Top 45
| Pos rank | Player | Team | Score |
| --- | --- | --- | --- |
| 1 | Josh Allen | BUF | 98.50 |
| 2 | Drake Maye | NE | 96.00 |
| 3 | Patrick Mahomes | KC | 95.00 |
| 4 | Jalen Hurts | PHI | 94.00 |
| 5 | Brock Purdy | SF | 92.50 |
| 6 | Trevor Lawrence | JAX | 90.00 |
| 7 | Matthew Stafford | LAR | 88.50 |
| 8 | Jordan Love | GB | 87.00 |
| 9 | Dak Prescott | DAL | 86.00 |
| 10 | Caleb Williams | CHI | 85.00 |
| 11 | Bo Nix | DEN | 84.00 |
| 12 | Daniel Jones | IND | 83.00 |
| 13 | Justin Herbert | LAC | 82.00 |
| 14 | Lamar Jackson | BAL | 81.00 |
| 15 | Jayden Daniels | WAS | 79.00 |
| 16 | Joe Burrow | CIN | 78.00 |
| 17 | Jared Goff | DET | 77.00 |
| 18 | Jaxson Dart | NYG | 75.00 |
| 19 | Baker Mayfield | TB | 74.00 |
| 20 | Jacoby Brissett | ARI | 72.00 |
| 21 | Kyler Murray | MIN | 70.00 |
| 22 | C.J. Stroud | HOU | 68.00 |
| 23 | Sam Darnold | SEA | 66.00 |
| 24 | Aaron Rodgers | PIT | 64.00 |
| 25 | Tyler Shough | NO | 62.00 |
| 26 | Bryce Young | CAR | 60.00 |
| 27 | Malik Willis | MIA | 58.00 |
| 28 | Geno Smith | NYJ | 55.00 |
| 29 | Tua Tagovailoa | ATL | 54.00 |
| 30 | Cam Ward | TEN | 50.00 |
| 31 | Shedeur Sanders | CLE | 48.00 |
| 32 | Fernando Mendoza | LV | 45.00 |
| 33 | Justin Fields | KC | 40.00 |
| 34 | Jameis Winston | NYG | 38.00 |
| 35 | Carson Wentz | MIN | 35.00 |
| 36 | J.J. McCarthy | MIN | 34.00 |
| 37 | Marcus Mariota | WAS | 32.00 |
| 38 | Mac Jones | SF | 30.00 |
| 39 | Davis Mills | HOU | 28.00 |
| 40 | Joe Flacco | CIN | 26.00 |
| 41 | Spencer Rattler | NO | 24.00 |
| 42 | Jake Browning | TB | 22.00 |
| 43 | Quinn Ewers | MIA | 18.00 |
| 44 | Josh Johnson | CIN | 15.00 |
| 45 | Tyler Huntley | BAL | 12.00 |

## QB Position Board: BQML Logistic Top 45
| Pos rank | Player | Sleeper team | Score | Current pos rank | Delta | Missing % | Status | Injury |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Drake Maye | unknown | 83.18 | 2 | +1 | 73.6 |  |  |
| 2 | Josh Allen | BUF | 78.46 | 1 | -1 | 18.4 | Active |  |
| 3 | Lamar Jackson | BAL | 75.55 | 14 | +11 | 13.8 | Active |  |
| 4 | Patrick Mahomes | KC | 58.83 | 3 | -1 | 13.8 | Active | Questionable |
| 5 | Jalen Hurts | unknown | 58.44 | 4 | -1 | 73.6 |  |  |
| 6 | Baker Mayfield | TB | 55.19 | 19 | +13 | 18.4 | Active |  |
| 7 | Jared Goff | DET | 53.96 | 17 | +10 | 13.8 | Active |  |
| 8 | Kyler Murray | unknown | 53.95 | 21 | +13 | 18.4 |  |  |
| 9 | Bo Nix | unknown | 50.99 | 11 | +2 | 73.6 |  |  |
| 10 | Trevor Lawrence | unknown | 49.06 | 6 | -4 | 73.6 |  |  |
| 11 | Jordan Love | unknown | 47.81 | 8 | -3 | 73.6 |  |  |
| 12 | Jaxson Dart | unknown | 45.81 | 18 | +6 | 73.6 |  |  |
| 13 | Brock Purdy | unknown | 45.49 | 5 | -8 | 73.6 |  |  |
| 14 | Daniel Jones | unknown | 45.08 | 12 | -2 | 18.4 |  |  |
| 15 | Dak Prescott | DAL | 44.58 | 9 | -6 | 18.4 | Active | Questionable |
| 16 | Geno Smith | NYJ | 44.53 | 28 | +12 | 13.8 | Active |  |
| 17 | Caleb Williams | unknown | 43.76 | 10 | -7 | 73.6 |  |  |
| 18 | Justin Herbert | unknown | 41.00 | 13 | -5 | 73.6 |  |  |
| 19 | Matthew Stafford | LAR | 38.76 | 7 | -12 | 13.8 | Active |  |
| 20 | Carson Wentz | MIN | 37.60 | 35 | +15 | 19.5 | Active |  |
| 21 | Mason Rudolph | PIT | 35.86 | missing | new | 23.0 | Active |  |
| 22 | Sam Darnold | SEA | 35.76 | 23 | +1 | 18.4 | Active |  |
| 23 | Kirk Cousins | LV | 33.45 | missing | new | 13.8 | Active |  |
| 24 | C.J. Stroud | unknown | 32.32 | 22 | -2 | 73.6 |  |  |
| 25 | Marcus Mariota | WAS | 31.82 | 37 | +12 | 18.4 | Active |  |
| 26 | Joe Flacco | CIN | 31.52 | 40 | +14 | 13.8 | Active |  |
| 27 | Malik Willis | unknown | 29.89 | 27 | 0 | 73.6 |  |  |
| 28 | Drew Lock | unknown | 25.57 | missing | new | 18.4 |  |  |
| 29 | Aaron Rodgers | PIT | 25.40 | 24 | -5 | 18.4 | Active |  |
| 30 | Jarrett Stidham | unknown | 24.94 | missing | new | 18.4 |  |  |
| 31 | Tyrod Taylor | GB | 24.12 | missing | new | 18.4 | Active |  |
| 32 | Jacoby Brissett | ARI | 23.86 | 20 | -12 | 23.0 | Active |  |
| 33 | Jameis Winston | NYG | 22.52 | 34 | +1 | 18.4 | Active |  |
| 34 | Mac Jones | unknown | 22.46 | 38 | +4 | 73.6 |  |  |
| 35 | Andy Dalton | PHI | 22.27 | missing | new | 18.4 | Active |  |
| 36 | Justin Fields | unknown | 21.56 | 33 | -3 | 73.6 |  |  |
| 37 | Mitchell Trubisky | TEN | 21.49 | missing | new | 18.4 | Active |  |
| 38 | Joe Burrow | unknown | 20.24 | 16 | -22 | 73.6 |  |  |
| 39 | Jayden Daniels | unknown | 20.00 | 15 | -24 | 73.6 |  |  |
| 40 | Nick Mullens | JAX | 19.83 | missing | new | 23.0 | Active |  |
| 41 | Tyler Shough | unknown | 17.45 | 25 | -16 | 73.6 |  |  |
| 42 | Tyler Huntley | unknown | 16.73 | 45 | +3 | 73.6 |  |  |
| 43 | Bryce Young | unknown | 16.70 | 26 | -17 | 73.6 |  |  |
| 44 | Jake Browning | unknown | 13.26 | 42 | -2 | 13.8 |  |  |
| 45 | Michael Penix Jr. | unknown | 12.00 | missing | new | 73.6 |  |  |

## QB Position Board: BQML Linear Points Top 45
| Pos rank | Player | Sleeper team | Score | Current pos rank | Delta | Missing % | Status | Injury |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lamar Jackson | BAL | 27.95 | 14 | +13 | 13.8 | Active |  |
| 2 | Josh Allen | BUF | 26.19 | 1 | -1 | 18.4 | Active |  |
| 3 | Patrick Mahomes | KC | 21.82 | 3 | 0 | 13.8 | Active | Questionable |
| 4 | Kyler Murray | unknown | 21.62 | 21 | +17 | 18.4 |  |  |
| 5 | Baker Mayfield | TB | 21.31 | 19 | +14 | 18.4 | Active |  |
| 6 | Jared Goff | DET | 20.84 | 17 | +11 | 13.8 | Active |  |
| 7 | Geno Smith | NYJ | 19.92 | 28 | +21 | 13.8 | Active |  |
| 8 | Dak Prescott | DAL | 18.77 | 9 | +1 | 18.4 | Active | Questionable |
| 9 | Matthew Stafford | LAR | 18.29 | 7 | -2 | 13.8 | Active |  |
| 10 | Daniel Jones | unknown | 17.76 | 12 | +2 | 18.4 |  |  |
| 11 | Sam Darnold | SEA | 17.59 | 23 | +12 | 18.4 | Active |  |
| 12 | Kirk Cousins | LV | 17.24 | missing | new | 13.8 | Active |  |
| 13 | Joe Flacco | CIN | 16.12 | 40 | +27 | 13.8 | Active |  |
| 14 | Marcus Mariota | WAS | 16.00 | 37 | +23 | 18.4 | Active |  |
| 15 | Carson Wentz | MIN | 15.36 | 35 | +20 | 19.5 | Active |  |
| 16 | Mason Rudolph | PIT | 15.05 | missing | new | 23.0 | Active |  |
| 17 | Aaron Rodgers | PIT | 14.86 | 24 | +7 | 18.4 | Active |  |
| 18 | Drew Lock | unknown | 14.60 | missing | new | 18.4 |  |  |
| 19 | Andy Dalton | PHI | 13.90 | missing | new | 18.4 | Active |  |
| 20 | Jameis Winston | NYG | 13.70 | 34 | +14 | 18.4 | Active |  |
| 21 | Jarrett Stidham | unknown | 13.33 | missing | new | 18.4 |  |  |
| 22 | Tyrod Taylor | GB | 12.82 | missing | new | 18.4 | Active |  |
| 23 | Mitchell Trubisky | TEN | 12.25 | missing | new | 18.4 | Active |  |
| 24 | Jacoby Brissett | ARI | 11.70 | 20 | -4 | 23.0 | Active |  |
| 25 | Nick Mullens | JAX | 11.55 | missing | new | 23.0 | Active |  |
| 26 | Kyle Allen | BUF | 10.25 | missing | new | 23.0 | Active |  |
| 27 | Jake Browning | unknown | 10.24 | 42 | +15 | 13.8 |  |  |
| 28 | Brandon Allen | NYG | 10.02 | missing | new | 23.0 | Active |  |
| 29 | Teddy Bridgewater | DET | 9.22 | missing | new | 18.4 | Active |  |
| 30 | Josh Johnson | unknown | 8.35 | 44 | +14 | 24.1 |  |  |
| 31 | Tyson Bagent | unknown | 0.08 | missing | new | 73.6 |  |  |
| 32 | Anthony Richardson | unknown | -2.74 | missing | new | 73.6 |  |  |
| 33 | Aidan O'Connell | unknown | -2.76 | missing | new | 73.6 |  |  |
| 34 | Kedon Slovis | unknown | -3.03 | missing | new | 73.6 |  |  |
| 35 | Quinn Ewers | unknown | -3.55 | 43 | +8 | 73.6 |  |  |
| 36 | Joe Burrow | unknown | -4.46 | 16 | -20 | 73.6 |  |  |
| 37 | Aaron Bailey | BAL | -5.57 | missing | new | 96.6 | Active |  |
| 38 | Athan Kaliakmanis | unknown | -5.57 | missing | new | 96.6 |  |  |
| 39 | Bailey Zappe | unknown | -5.57 | missing | new | 96.6 |  |  |
| 40 | Behren Morton | unknown | -5.57 | missing | new | 96.6 |  |  |
| 41 | Ben Roethlisberger | PIT | -5.57 | missing | new | 96.6 | Active |  |
| 42 | Blake Bortles | NO | -5.57 | missing | new | 96.6 | Active |  |
| 43 | Cade Klubnik | unknown | -5.57 | missing | new | 96.6 |  |  |
| 44 | Cam Miller | unknown | -5.57 | missing | new | 96.6 |  |  |
| 45 | Carson Beck | unknown | -5.57 | missing | new | 96.6 |  |  |

## RB Position Board: Current Pigskin Top 80
| Pos rank | Player | Team | Score |
| --- | --- | --- | --- |
| 1 | Christian McCaffrey | SF | 98.00 |
| 2 | Bijan Robinson | ATL | 95.00 |
| 3 | Jahmyr Gibbs | DET | 93.00 |
| 4 | Jonathan Taylor | IND | 91.00 |
| 5 | De'Von Achane | MIA | 90.00 |
| 6 | James Cook | BUF | 88.00 |
| 7 | Kyren Williams | LAR | 86.00 |
| 8 | Saquon Barkley | PHI | 84.00 |
| 9 | Chase Brown | CIN | 82.00 |
| 10 | Javonte Williams | DAL | 80.00 |
| 11 | Josh Jacobs | GB | 79.00 |
| 12 | Travis Etienne | NO | 78.00 |
| 13 | Omarion Hampton | LAC | 77.00 |
| 14 | Breece Hall | NYJ | 76.00 |
| 15 | D'Andre Swift | CHI | 75.00 |
| 16 | Ashton Jeanty | LV | 73.00 |
| 17 | Jaylen Warren | PIT | 72.00 |
| 18 | Derrick Henry | BAL | 71.00 |
| 19 | Cam Skattebo | NYG | 70.00 |
| 20 | Bucky Irving | TB | 69.00 |
| 21 | Rico Dowdle | PIT | 68.00 |
| 22 | Quinshon Judkins | CLE | 67.00 |
| 23 | TreVeyon Henderson | NE | 66.00 |
| 24 | J.K. Dobbins | DEN | 65.00 |
| 25 | Aaron Jones | MIN | 64.00 |
| 26 | Rhamondre Stevenson | NE | 63.00 |
| 27 | Kenneth Gainwell | TB | 62.00 |
| 28 | James Conner | ARI | 61.00 |
| 29 | Kenneth Walker III | KC | 60.00 |
| 30 | Tyrone Tracy Jr. | NYG | 59.00 |
| 31 | Zach Charbonnet | SEA | 58.00 |
| 32 | Tony Pollard | TEN | 57.00 |
| 33 | Alvin Kamara | NO | 56.00 |
| 34 | Rachaad White | WAS | 55.00 |
| 35 | David Montgomery | HOU | 54.00 |
| 36 | Woody Marks | HOU | 53.00 |
| 37 | RJ Harvey | DEN | 52.00 |
| 38 | Kyle Monangai | CHI | 51.00 |
| 39 | Tyjae Spears | TEN | 50.00 |
| 40 | Chuba Hubbard | CAR | 49.00 |
| 41 | Jacory Croskey-Merritt | WAS | 48.00 |
| 42 | Jordan Mason | MIN | 47.00 |
| 43 | Chris Rodriguez Jr. | JAX | 46.00 |
| 44 | Blake Corum | LAR | 45.00 |
| 45 | Trey Benson | ARI | 44.00 |
| 46 | Kimani Vidal | LAC | 43.00 |
| 47 | Isiah Pacheco | DET | 42.00 |
| 48 | Jawhar Jordan | HOU | 41.00 |
| 49 | Tyler Allgeier | ARI | 40.00 |
| 50 | Ty Johnson | BUF | 39.00 |
| 51 | Samaje Perine | CIN | 38.00 |
| 52 | Jaylen Wright | MIA | 37.00 |
| 53 | Justice Hill | BAL | 36.00 |
| 54 | Bhayshul Tuten | JAX | 35.00 |
| 55 | Michael Carter | TEN | 34.00 |
| 56 | Devin Singletary | NYG | 33.00 |
| 57 | Emanuel Wilson | SEA | 32.00 |
| 58 | Dylan Sampson | CLE | 31.00 |
| 59 | Kendre Miller | NO | 30.00 |
| 60 | Phil Mafah | DAL | 28.00 |
| 61 | Raheim Sanders | CLE | 27.00 |
| 62 | Devin Neal | NO | 26.00 |
| 63 | Jeremy McNichols | WAS | 25.00 |
| 64 | Emari Demercado | KC | 24.00 |
| 65 | Keaton Mitchell | LAC | 23.00 |
| 66 | Braelon Allen | NYJ | 22.00 |
| 67 | Isaiah Davis | NYJ | 21.00 |
| 68 | Jaydon Blue | DAL | 20.00 |
| 69 | Jerome Ford | WAS | 19.00 |
| 70 | Brian Robinson | ATL | 18.00 |
| 71 | Sean Tucker | TB | 17.00 |
| 72 | Jaret Patterson | LAC | 16.00 |
| 73 | Brashard Smith | KC | 15.00 |
| 74 | Malik Davis | DAL | 14.00 |
| 75 | Tank Bigsby | PHI | 13.00 |
| 76 | Ray Davis | BUF | 12.00 |
| 77 | DJ Giddens | IND | 11.00 |
| 78 | Zavier Scott | MIN | 10.00 |
| 79 | Jaleel McLaughlin | DEN | 9.00 |
| 80 | Ameer Abdullah | JAX | 8.00 |

## RB Position Board: BQML Logistic Top 80
| Pos rank | Player | Sleeper team | Score | Current pos rank | Delta | Missing % | Status | Injury |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Bijan Robinson | unknown | 99.80 | 2 | +1 | 73.6 |  |  |
| 2 | Jonathan Taylor | unknown | 99.79 | 4 | +2 | 73.6 |  |  |
| 3 | James Cook | unknown | 99.51 | 6 | +3 | 73.6 |  |  |
| 4 | Jahmyr Gibbs | unknown | 99.37 | 3 | -1 | 73.6 |  |  |
| 5 | De'Von Achane | unknown | 99.04 | 5 | 0 | 73.6 |  |  |
| 6 | Kyren Williams | unknown | 98.83 | 7 | +1 | 73.6 |  |  |
| 7 | Chase Brown | unknown | 98.63 | 9 | +2 | 73.6 |  |  |
| 8 | Travis Etienne | unknown | 98.51 | 12 | +4 | 73.6 |  |  |
| 9 | Javonte Williams | unknown | 98.30 | 10 | +1 | 73.6 |  |  |
| 10 | Ashton Jeanty | unknown | 98.27 | 16 | +6 | 73.6 |  |  |
| 11 | Breece Hall | unknown | 97.56 | 14 | +3 | 73.6 |  |  |
| 12 | Rico Dowdle | unknown | 97.37 | 21 | +9 | 73.6 |  |  |
| 13 | D'Andre Swift | unknown | 97.23 | 15 | +2 | 73.6 |  |  |
| 14 | Jaylen Warren | unknown | 96.00 | 17 | +3 | 73.6 |  |  |
| 15 | Kenneth Walker III | unknown | 95.08 | 29 | +14 | 73.6 |  |  |
| 16 | Quinshon Judkins | unknown | 94.50 | 22 | +6 | 73.6 |  |  |
| 17 | TreVeyon Henderson | unknown | 91.45 | 23 | +6 | 73.6 |  |  |
| 18 | Woody Marks | unknown | 90.17 | 36 | +18 | 73.6 |  |  |
| 19 | Tyrone Tracy Jr. | unknown | 89.78 | 30 | +11 | 73.6 |  |  |
| 20 | Zach Charbonnet | unknown | 88.47 | 31 | +11 | 73.6 |  |  |
| 21 | RJ Harvey | unknown | 85.36 | 37 | +16 | 73.6 |  |  |
| 22 | Kenneth Gainwell | unknown | 84.51 | 27 | +5 | 73.6 |  |  |
| 23 | Kyle Monangai | unknown | 84.12 | 38 | +15 | 73.6 |  |  |
| 24 | Bucky Irving | unknown | 83.86 | 20 | -4 | 73.6 |  |  |
| 25 | Saquon Barkley | PHI | 83.60 | 8 | -17 | 14.9 | Active |  |
| 26 | Jacory Croskey-Merritt | unknown | 80.61 | 41 | +15 | 73.6 |  |  |
| 27 | Derrick Henry | BAL | 78.73 | 18 | -9 | 12.6 | Active |  |
| 28 | Rachaad White | unknown | 78.03 | 34 | +6 | 73.6 |  |  |
| 29 | Alvin Kamara | NO | 77.27 | 33 | +4 | 14.9 | Active |  |
| 30 | J.K. Dobbins | unknown | 76.55 | 24 | -6 | 73.6 |  |  |
| 31 | Omarion Hampton | unknown | 75.18 | 13 | -18 | 73.6 |  |  |
| 32 | Kimani Vidal | unknown | 75.09 | 46 | +14 | 73.6 |  |  |
| 33 | Rhamondre Stevenson | unknown | 75.01 | 26 | -7 | 73.6 |  |  |
| 34 | Christian McCaffrey | SF | 74.86 | 1 | -33 | 12.6 | Active |  |
| 35 | Jordan Mason | unknown | 74.70 | 42 | +7 | 73.6 |  |  |
| 36 | Josh Jacobs | unknown | 73.58 | 11 | -25 | 14.9 |  |  |
| 37 | Chuba Hubbard | unknown | 72.71 | 40 | +3 | 73.6 |  |  |
| 38 | Blake Corum | unknown | 71.08 | 44 | +6 | 73.6 |  |  |
| 39 | James Conner | ARI | 67.56 | 28 | -11 | 14.9 | Active | Questionable |
| 40 | Tyler Allgeier | unknown | 67.06 | 49 | +9 | 73.6 |  |  |
| 41 | Aaron Jones | MIN | 65.42 | 25 | -16 | 14.9 | Active |  |
| 42 | David Montgomery | unknown | 64.24 | 35 | -7 | 12.6 |  |  |
| 43 | Tony Pollard | unknown | 63.48 | 32 | -11 | 14.9 |  |  |
| 44 | Cam Skattebo | unknown | 58.97 | 19 | -25 | 73.6 |  |  |
| 45 | Emanuel Wilson | unknown | 57.23 | 57 | +12 | 73.6 |  |  |
| 46 | Isiah Pacheco | unknown | 56.68 | 47 | +1 | 73.6 |  |  |
| 47 | Michael Carter | unknown | 55.84 | 55 | +8 | 73.6 |  |  |
| 48 | Chris Rodriguez Jr. | unknown | 48.92 | 43 | -5 | 73.6 |  |  |
| 49 | Tyjae Spears | unknown | 47.50 | 39 | -10 | 73.6 |  |  |
| 50 | Devin Singletary | unknown | 36.72 | 56 | +6 | 12.6 |  |  |
| 51 | Brian Robinson | unknown | 35.40 | 70 | +19 | 73.6 |  |  |
| 52 | Dylan Sampson | unknown | 34.69 | 58 | +6 | 73.6 |  |  |
| 53 | Bhayshul Tuten | unknown | 34.27 | 54 | +1 | 73.6 |  |  |
| 54 | Sean Tucker | unknown | 32.50 | 71 | +17 | 73.6 |  |  |
| 55 | Justice Hill | unknown | 31.21 | 53 | -2 | 14.9 |  |  |
| 56 | Jaylen Wright | unknown | 24.61 | 52 | -4 | 73.6 |  |  |
| 57 | Ameer Abdullah | JAX | 23.07 | 80 | +23 | 14.9 | Active |  |
| 58 | Ray Davis | unknown | 22.70 | 76 | +18 | 73.6 |  |  |
| 59 | Devin Neal | unknown | 22.62 | 62 | +3 | 73.6 |  |  |
| 60 | Keaton Mitchell | unknown | 22.23 | 65 | +5 | 73.6 |  |  |
| 61 | Brashard Smith | unknown | 22.20 | 73 | +12 | 73.6 |  |  |
| 62 | Isaiah Davis | unknown | 22.18 | 67 | +5 | 73.6 |  |  |
| 63 | Tank Bigsby | unknown | 22.14 | 75 | +12 | 73.6 |  |  |
| 64 | Samaje Perine | CIN | 22.09 | 51 | -13 | 14.9 | Active |  |
| 65 | Ollie Gordon II | unknown | 21.85 | missing | new | 73.6 |  |  |
| 66 | Ty Johnson | unknown | 20.51 | 50 | -16 | 18.4 |  |  |
| 67 | Jeremy McNichols | WAS | 19.84 | 63 | -4 | 23.0 | Active |  |
| 68 | Emari Demercado | unknown | 18.09 | 64 | -4 | 73.6 |  |  |
| 69 | Malik Davis | unknown | 16.92 | 74 | +5 | 73.6 |  |  |
| 70 | Kendre Miller | unknown | 15.96 | 59 | -11 | 73.6 |  |  |
| 71 | Jerome Ford | unknown | 15.04 | 69 | -2 | 73.6 |  |  |
| 72 | Jaret Patterson | unknown | 13.94 | 72 | 0 | 73.6 |  |  |
| 73 | Raheim Sanders | unknown | 13.88 | 61 | -12 | 73.6 |  |  |
| 74 | Jawhar Jordan | unknown | 13.68 | 48 | -26 | 73.6 |  |  |
| 75 | Trey Benson | unknown | 13.41 | 45 | -30 | 73.6 |  |  |
| 76 | Jaleel McLaughlin | unknown | 13.23 | 79 | +3 | 73.6 |  |  |
| 77 | Zavier Scott | unknown | 12.61 | 78 | +1 | 73.6 |  |  |
| 78 | Chris Brooks | unknown | 12.05 | missing | new | 73.6 |  |  |
| 79 | Tyler Badie | unknown | 10.85 | missing | new | 73.6 |  |  |
| 80 | Jaydon Blue | unknown | 10.57 | 68 | -12 | 73.6 |  |  |

## RB Position Board: BQML Linear Points Top 80
| Pos rank | Player | Sleeper team | Score | Current pos rank | Delta | Missing % | Status | Injury |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Kenneth Gainwell | unknown | 111.55 | 27 | +26 | 73.6 |  |  |
| 2 | Tyler Badie | unknown | 88.39 | missing | new | 73.6 |  |  |
| 3 | Jerome Ford | unknown | 70.33 | 69 | +66 | 73.6 |  |  |
| 4 | Tyjae Spears | unknown | 60.09 | 39 | +35 | 73.6 |  |  |
| 5 | Brashard Smith | unknown | 46.64 | 73 | +68 | 73.6 |  |  |
| 6 | Dylan Sampson | unknown | 32.56 | 58 | +52 | 73.6 |  |  |
| 7 | Isaiah Davis | unknown | 27.67 | 67 | +60 | 73.6 |  |  |
| 8 | Rasheen Ali | unknown | 23.71 | missing | new | 73.6 |  |  |
| 9 | Saquon Barkley | PHI | 20.93 | 8 | -1 | 14.9 | Active |  |
| 10 | Trey Benson | unknown | 20.42 | 45 | +35 | 73.6 |  |  |
| 11 | Alvin Kamara | NO | 20.23 | 33 | +22 | 14.9 | Active |  |
| 12 | Derrick Henry | BAL | 19.34 | 18 | +6 | 12.6 | Active |  |
| 13 | Christian McCaffrey | SF | 17.25 | 1 | -12 | 12.6 | Active |  |
| 14 | Josh Jacobs | unknown | 17.13 | 11 | -3 | 14.9 |  |  |
| 15 | James Conner | ARI | 16.35 | 28 | +13 | 14.9 | Active | Questionable |
| 16 | Aaron Jones | MIN | 15.74 | 25 | +9 | 14.9 | Active |  |
| 17 | Tony Pollard | unknown | 15.72 | 32 | +15 | 14.9 |  |  |
| 18 | David Montgomery | unknown | 15.59 | 35 | +17 | 12.6 |  |  |
| 19 | Will Shipley | unknown | 14.64 | missing | new | 73.6 |  |  |
| 20 | Chris Brooks | unknown | 12.99 | missing | new | 73.6 |  |  |
| 21 | Michael Carter | unknown | 12.56 | 55 | +34 | 73.6 |  |  |
| 22 | Justice Hill | unknown | 11.55 | 53 | +31 | 14.9 |  |  |
| 23 | Devin Singletary | unknown | 11.38 | 56 | +33 | 12.6 |  |  |
| 24 | Samaje Perine | CIN | 10.14 | 51 | +27 | 14.9 | Active |  |
| 25 | Ameer Abdullah | JAX | 9.89 | 80 | +55 | 14.9 | Active |  |
| 26 | Ty Johnson | unknown | 9.71 | 50 | +24 | 18.4 |  |  |
| 27 | Phil Mafah | unknown | 9.27 | 60 | +33 | 73.6 |  |  |
| 28 | Jeremy McNichols | WAS | 7.20 | 63 | +35 | 23.0 | Active |  |
| 29 | Travis Homer | unknown | 6.51 | missing | new | 18.4 |  |  |
| 30 | Zavier Scott | unknown | 2.81 | 78 | +48 | 73.6 |  |  |
| 31 | Adam Randall | unknown | 1.82 | missing | new | 96.6 |  |  |
| 32 | Ahmani Marshall | unknown | 1.82 | missing | new | 96.6 |  |  |
| 33 | Anderson Castle | unknown | 1.82 | missing | new | 96.6 |  |  |
| 34 | Andrew Beck | NYJ | 1.82 | missing | new | 96.6 | Active |  |
| 35 | Anthony Hankerson | unknown | 1.82 | missing | new | 96.6 |  |  |
| 36 | Anthony Tyus III | unknown | 1.82 | missing | new | 96.6 |  |  |
| 37 | Audric Estime | NO | 1.82 | missing | new | 96.6 | Active |  |
| 38 | Benny LeMay | unknown | 1.82 | missing | new | 96.6 |  |  |
| 39 | CJ Donaldson | unknown | 1.82 | missing | new | 96.6 |  |  |
| 40 | Carlos Washington | unknown | 1.82 | missing | new | 96.6 |  |  |
| 41 | Carson Steele | unknown | 1.82 | missing | new | 96.6 |  |  |
| 42 | Cash Jones | unknown | 1.82 | missing | new | 96.6 |  |  |
| 43 | Chris Collier | unknown | 1.82 | missing | new | 96.6 |  |  |
| 44 | Cody Schrader | unknown | 1.82 | missing | new | 96.6 |  |  |
| 45 | Coleman Bennett | unknown | 1.82 | missing | new | 96.6 |  |  |
| 46 | Damien Martinez | unknown | 1.82 | missing | new | 96.6 |  |  |
| 47 | Damon Bankston | unknown | 1.82 | missing | new | 96.6 |  |  |
| 48 | Dante Miller | unknown | 1.82 | missing | new | 96.6 |  |  |
| 49 | Davon Booth | unknown | 1.82 | missing | new | 96.6 |  |  |
| 50 | DeaMonte Trayanum | NYJ | 1.82 | missing | new | 96.6 | Active |  |
| 51 | Dean Connors | unknown | 1.82 | missing | new | 96.6 |  |  |
| 52 | Demond Claiborne | unknown | 1.82 | missing | new | 96.6 |  |  |
| 53 | Dominic Richardson | unknown | 1.82 | missing | new | 96.6 |  |  |
| 54 | Donovan Edwards | unknown | 1.82 | missing | new | 96.6 |  |  |
| 55 | Dontae McMillan | unknown | 1.82 | missing | new | 96.6 |  |  |
| 56 | EJ Smith | unknown | 1.82 | missing | new | 96.6 |  |  |
| 57 | Eli Heidenreich | unknown | 1.82 | missing | new | 96.6 |  |  |
| 58 | Elijah McGuire | KC | 1.82 | missing | new | 96.6 | Active |  |
| 59 | Elijah Tau-Tolliver | unknown | 1.82 | missing | new | 96.6 |  |  |
| 60 | Emmett Johnson | unknown | 1.82 | missing | new | 96.6 |  |  |
| 61 | Frank Gore Jr. | unknown | 1.82 | missing | new | 96.6 |  |  |
| 62 | Gregory Desrosiers | unknown | 1.82 | missing | new | 96.6 |  |  |
| 63 | Israel Abanikanda | unknown | 1.82 | missing | new | 96.6 |  |  |
| 64 | Ito Smith | DAL | 1.82 | missing | new | 96.6 | Active |  |
| 65 | J'Mari Taylor | unknown | 1.82 | missing | new | 96.6 |  |  |
| 66 | Jabari Small | unknown | 1.82 | missing | new | 96.6 |  |  |
| 67 | Jadarian Price | unknown | 1.82 | missing | new | 96.6 |  |  |
| 68 | Jaden Nixon | unknown | 1.82 | missing | new | 96.6 |  |  |
| 69 | Jalen Richard | LV | 1.82 | missing | new | 96.6 | Active |  |
| 70 | Jam Miller | unknown | 1.82 | missing | new | 96.6 |  |  |
| 71 | Jamal Haynes | unknown | 1.82 | missing | new | 96.6 |  |  |
| 72 | Jarquez Hunter | unknown | 1.82 | missing | new | 96.6 |  |  |
| 73 | Jaydn Ott | unknown | 1.82 | missing | new | 96.6 |  |  |
| 74 | Jeremiyah Love | unknown | 1.82 | missing | new | 96.6 |  |  |
| 75 | Jonah Coleman | unknown | 1.82 | missing | new | 96.6 |  |  |
| 76 | Jonathon Brooks | unknown | 1.82 | missing | new | 96.6 |  |  |
| 77 | Jordan James | unknown | 1.82 | missing | new | 96.6 |  |  |
| 78 | Jordan Waters | unknown | 1.82 | missing | new | 96.6 |  |  |
| 79 | Joshua Pitsenberger | unknown | 1.82 | missing | new | 96.6 |  |  |
| 80 | Kadarius Calloway | unknown | 1.82 | missing | new | 96.6 |  |  |

## WR Position Board: Current Pigskin Top 100
| Pos rank | Player | Team | Score |
| --- | --- | --- | --- |
| 1 | Jaxon Smith-Njigba | SEA | 98.50 |
| 2 | Puka Nacua | LAR | 97.80 |
| 3 | Ja'Marr Chase | CIN | 96.50 |
| 4 | Amon-Ra St. Brown | DET | 95.90 |
| 5 | Drake London | ATL | 94.20 |
| 6 | Garrett Wilson | NYJ | 93.00 |
| 7 | Rashee Rice | KC | 91.50 |
| 8 | Chris Olave | NO | 90.80 |
| 9 | A.J. Brown | NE | 89.90 |
| 10 | Justin Jefferson | MIN | 89.00 |
| 11 | CeeDee Lamb | DAL | 88.20 |
| 12 | Zay Flowers | BAL | 87.50 |
| 13 | George Pickens | DAL | 86.90 |
| 14 | Nico Collins | HOU | 86.00 |
| 15 | Davante Adams | LAR | 85.10 |
| 16 | Malik Nabers | NYG | 84.50 |
| 17 | Wan'Dale Robinson | TEN | 83.00 |
| 18 | Tetairoa McMillan | CAR | 82.20 |
| 19 | Rome Odunze | CHI | 81.50 |
| 20 | DeVonta Smith | PHI | 80.90 |
| 21 | Terry McLaurin | WAS | 80.00 |
| 22 | Jaylen Waddle | DEN | 79.40 |
| 23 | Tee Higgins | CIN | 78.80 |
| 24 | Courtland Sutton | DEN | 78.00 |
| 25 | Alec Pierce | IND | 77.50 |
| 26 | Emeka Egbuka | TB | 76.90 |
| 27 | Jakobi Meyers | JAX | 76.20 |
| 28 | Jameson Williams | DET | 75.50 |
| 29 | Mike Evans | SF | 74.80 |
| 30 | Michael Wilson | ARI | 74.00 |
| 31 | Quentin Johnston | LAC | 73.50 |
| 32 | Christian Watson | GB | 72.80 |
| 33 | Jordan Addison | MIN | 72.00 |
| 34 | Ladd McConkey | LAC | 71.50 |
| 35 | DK Metcalf | PIT | 70.80 |
| 36 | Jauan Jennings | MIN | 69.50 |
| 37 | Romeo Doubs | NE | 68.80 |
| 38 | Tre Tucker | LV | 68.20 |
| 39 | Parker Washington | JAX | 67.50 |
| 40 | Ricky Pearsall | SF | 66.90 |
| 41 | Troy Franklin | DEN | 66.20 |
| 42 | Jerry Jeudy | CLE | 65.50 |
| 43 | Elic Ayomanor | TEN | 64.80 |
| 44 | Darius Slayton | NYG | 64.10 |
| 45 | Khalil Shakir | BUF | 63.50 |
| 46 | Calvin Ridley | TEN | 62.80 |
| 47 | Keon Coleman | BUF | 62.10 |
| 48 | Brian Thomas Jr. | JAX | 61.50 |
| 49 | Darnell Mooney | NYG | 60.80 |
| 50 | Michael Pittman | PIT | 60.10 |
| 51 | Travis Hunter | JAX | 59.50 |
| 52 | Mack Hollins | NE | 58.80 |
| 53 | Xavier Worthy | KC | 58.10 |
| 54 | Jakobie Keeney-James | GB | 57.50 |
| 55 | Jayden Reed | GB | 56.80 |
| 56 | Kayshon Boutte | NE | 56.10 |
| 57 | Jalen Coker | CAR | 55.50 |
| 58 | Josh Downs | IND | 54.80 |
| 59 | Rashid Shaheed | SEA | 54.10 |
| 60 | Cooper Kupp | SEA | 53.50 |
| 61 | Chris Godwin Jr. | TB | 52.80 |
| 62 | Jalen McMillan | TB | 51.50 |
| 63 | Devaughn Vele | NO | 50.80 |
| 64 | Marquise Brown | PHI | 50.10 |
| 65 | Van Jefferson | WAS | 49.50 |
| 66 | Xavier Legette | CAR | 48.80 |
| 67 | Jayden Higgins | HOU | 48.10 |
| 68 | DJ Moore | BUF | 47.50 |
| 69 | Adonai Mitchell | NYJ | 46.80 |
| 70 | Theo Wease Jr. | MIA | 46.10 |
| 71 | Andrei Iosivas | CIN | 45.50 |
| 72 | Chimere Dike | TEN | 44.80 |
| 73 | Tyquan Thornton | KC | 44.10 |
| 74 | Olamide Zaccheaus | ATL | 43.50 |
| 75 | Malik Washington | MIA | 42.80 |
| 76 | Kendrick Bourne | ARI | 42.10 |
| 77 | Ryan Flournoy | DAL | 41.50 |
| 78 | Calvin Austin III | NYG | 40.80 |
| 79 | Pat Bryant | DEN | 40.10 |
| 80 | Dontayvion Wicks | PHI | 39.50 |
| 81 | Xavier Hutchinson | HOU | 38.80 |
| 82 | Matthew Golden | GB | 38.10 |
| 83 | Rashod Bateman | BAL | 37.50 |
| 84 | Jalen Nailor | LV | 36.80 |
| 85 | Tory Horton | SEA | 36.10 |
| 86 | Luther Burden III | CHI | 35.50 |
| 87 | Tez Johnson | TB | 34.80 |
| 88 | DeMario Douglas | NE | 34.10 |
| 89 | Christian Kirk | SF | 33.50 |
| 90 | Isaiah Bond | CLE | 32.80 |
| 91 | Tre Harris | LAC | 32.10 |
| 92 | Treylon Burks | WAS | 31.50 |
| 93 | Isaac TeSlaa | DET | 30.80 |
| 94 | Marquez Valdes-Scantling | DAL | 30.10 |
| 95 | Casey Washington | ATL | 29.50 |
| 96 | Cedric Tillman | CLE | 28.80 |
| 97 | Jalen Tolbert | MIA | 28.10 |
| 98 | John Metchie III | CAR | 27.50 |
| 99 | Lil'Jordan Humphrey | DEN | 26.80 |
| 100 | Devontez Walker | BAL | 25.00 |

## WR Position Board: BQML Logistic Top 100
| Pos rank | Player | Sleeper team | Score | Current pos rank | Delta | Missing % | Status | Injury |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Puka Nacua | unknown | 90.52 | 2 | +1 | 74.7 |  |  |
| 2 | Jaxon Smith-Njigba | unknown | 84.91 | 1 | -1 | 74.7 |  |  |
| 3 | Ja'Marr Chase | unknown | 81.52 | 3 | 0 | 74.7 |  |  |
| 4 | Amon-Ra St. Brown | unknown | 79.86 | 4 | 0 | 74.7 |  |  |
| 5 | George Pickens | unknown | 72.05 | 13 | +8 | 74.7 |  |  |
| 6 | Chris Olave | unknown | 67.65 | 8 | +2 | 74.7 |  |  |
| 7 | Davante Adams | LAR | 64.60 | 15 | +8 | 16.1 | Active |  |
| 8 | Zay Flowers | unknown | 59.45 | 12 | +4 | 74.7 |  |  |
| 9 | Mike Evans | SF | 59.17 | 29 | +20 | 20.7 | Active |  |
| 10 | Cooper Kupp | SEA | 58.39 | 60 | +50 | 13.8 | Active |  |
| 11 | Wan'Dale Robinson | unknown | 57.90 | 17 | +6 | 74.7 |  |  |
| 12 | A.J. Brown | unknown | 56.59 | 9 | -3 | 20.7 |  |  |
| 13 | DJ Moore | BUF | 56.28 | 68 | +55 | 13.8 | Active |  |
| 14 | Chris Godwin Jr. | TB | 56.07 | 61 | +47 | 13.8 | Active |  |
| 15 | Nico Collins | unknown | 55.54 | 14 | -1 | 74.7 |  |  |
| 16 | Jakobi Meyers | unknown | 51.76 | 27 | +11 | 13.8 |  |  |
| 17 | DeVonta Smith | unknown | 51.63 | 20 | +3 | 74.7 |  |  |
| 18 | CeeDee Lamb | unknown | 51.39 | 11 | -7 | 74.7 |  |  |
| 19 | Jameson Williams | unknown | 49.66 | 28 | +9 | 74.7 |  |  |
| 20 | Michael Wilson | unknown | 49.41 | 30 | +10 | 74.7 |  |  |
| 21 | Drake London | unknown | 49.17 | 5 | -16 | 74.7 |  |  |
| 22 | Tetairoa McMillan | unknown | 48.94 | 18 | -4 | 74.7 |  |  |
| 23 | Justin Jefferson | unknown | 48.48 | 10 | -13 | 74.7 |  |  |
| 24 | Courtland Sutton | DEN | 48.41 | 24 | 0 | 13.8 | Active |  |
| 25 | Terry McLaurin | unknown | 47.70 | 21 | -4 | 16.1 |  |  |
| 26 | Calvin Ridley | TEN | 46.44 | 46 | +20 | 16.1 | Active |  |
| 27 | DK Metcalf | unknown | 45.93 | 35 | +8 | 20.7 |  |  |
| 28 | Emeka Egbuka | unknown | 45.52 | 26 | -2 | 74.7 |  |  |
| 29 | Jaylen Waddle | unknown | 42.51 | 22 | -7 | 74.7 |  |  |
| 30 | Tee Higgins | unknown | 41.76 | 23 | -7 | 74.7 |  |  |
| 31 | Alec Pierce | unknown | 41.15 | 25 | -6 | 74.7 |  |  |
| 32 | Parker Washington | unknown | 38.92 | 39 | +7 | 74.7 |  |  |
| 33 | Michael Pittman | unknown | 38.82 | 50 | +17 | 74.7 |  |  |
| 34 | Rashee Rice | unknown | 37.86 | 7 | -27 | 74.7 |  |  |
| 35 | Tre Tucker | unknown | 37.69 | 38 | +3 | 74.7 |  |  |
| 36 | Troy Franklin | unknown | 35.85 | 41 | +5 | 74.7 |  |  |
| 37 | Rome Odunze | unknown | 35.55 | 19 | -18 | 74.7 |  |  |
| 38 | Ladd McConkey | unknown | 35.05 | 34 | -4 | 74.7 |  |  |
| 39 | Christian Kirk | SF | 34.57 | 89 | +50 | 18.4 | Active |  |
| 40 | Quentin Johnston | unknown | 33.92 | 31 | -9 | 74.7 |  |  |
| 41 | Romeo Doubs | unknown | 33.51 | 37 | -4 | 74.7 |  |  |
| 42 | Brian Thomas Jr. | unknown | 32.37 | 48 | +6 | 74.7 |  |  |
| 43 | Jordan Addison | unknown | 30.16 | 33 | -10 | 74.7 |  |  |
| 44 | Khalil Shakir | unknown | 30.00 | 45 | +1 | 74.7 |  |  |
| 45 | Rashid Shaheed | unknown | 28.83 | 59 | +14 | 74.7 |  |  |
| 46 | Xavier Worthy | unknown | 28.68 | 53 | +7 | 74.7 |  |  |
| 47 | Darius Slayton | unknown | 28.27 | 44 | -3 | 16.1 |  |  |
| 48 | Christian Watson | unknown | 27.84 | 32 | -16 | 74.7 |  |  |
| 49 | Marquise Brown | unknown | 27.10 | 64 | +15 | 16.1 |  |  |
| 50 | Jauan Jennings | unknown | 26.88 | 36 | -14 | 74.7 |  |  |
| 51 | Josh Downs | unknown | 26.87 | 58 | +7 | 74.7 |  |  |
| 52 | Demarcus Robinson | SF | 26.84 | missing | new | 16.1 | Active |  |
| 53 | Jerry Jeudy | unknown | 25.69 | 42 | -11 | 74.7 |  |  |
| 54 | David Moore | CAR | 25.11 | missing | new | 16.1 | Active |  |
| 55 | Tim Patrick | NYJ | 24.74 | missing | new | 35.6 | Active |  |
| 56 | Ricky Pearsall | unknown | 24.32 | 40 | -16 | 74.7 |  |  |
| 57 | Kendrick Bourne | ARI | 23.64 | 76 | +19 | 13.8 | Active |  |
| 58 | Elic Ayomanor | unknown | 23.46 | 43 | -15 | 74.7 |  |  |
| 59 | Mack Hollins | NE | 23.00 | 52 | -7 | 13.8 | Active |  |
| 60 | Luther Burden III | unknown | 22.73 | 86 | +26 | 74.7 |  |  |
| 61 | Chimere Dike | unknown | 22.62 | 72 | +11 | 74.7 |  |  |
| 62 | Marquez Valdes-Scantling | DAL | 21.12 | 94 | +32 | 16.1 | Active |  |
| 63 | Ryan Flournoy | unknown | 21.06 | 77 | +14 | 74.7 |  |  |
| 64 | Malik Washington | unknown | 20.88 | 75 | +11 | 74.7 |  |  |
| 65 | Jayden Higgins | unknown | 20.71 | 67 | +2 | 74.7 |  |  |
| 66 | Darnell Mooney | unknown | 20.47 | 49 | -17 | 74.7 |  |  |
| 67 | Kayshon Boutte | unknown | 20.17 | 56 | -11 | 74.7 |  |  |
| 68 | Greg Dortch | unknown | 20.05 | missing | new | 16.1 |  |  |
| 69 | Olamide Zaccheaus | unknown | 19.89 | 74 | +5 | 16.1 |  |  |
| 70 | Garrett Wilson | unknown | 19.56 | 6 | -64 | 74.7 |  |  |
| 71 | Keon Coleman | unknown | 19.44 | 47 | -24 | 74.7 |  |  |
| 72 | Justin Watson | HOU | 18.98 | missing | new | 21.8 | Active |  |
| 73 | Cedrick Wilson Jr. | unknown | 18.77 | missing | new | 13.8 |  |  |
| 74 | Kalif Raymond | CHI | 18.04 | missing | new | 16.1 | Active |  |
| 75 | Andrei Iosivas | unknown | 17.90 | 71 | -4 | 74.7 |  |  |
| 76 | DeMario Douglas | unknown | 17.76 | 88 | +12 | 74.7 |  |  |
| 77 | Xavier Hutchinson | unknown | 17.75 | 81 | +4 | 74.7 |  |  |
| 78 | Jalen Coker | unknown | 17.33 | 57 | -21 | 74.7 |  |  |
| 79 | Matthew Golden | unknown | 17.24 | 82 | +3 | 74.7 |  |  |
| 80 | JuJu Smith-Schuster | NYG | 16.92 | missing | new | 20.7 | Active |  |
| 81 | Marvin Mims Jr. | unknown | 16.87 | missing | new | 74.7 |  |  |
| 82 | Adonai Mitchell | unknown | 16.45 | 69 | -13 | 74.7 |  |  |
| 83 | Lil'Jordan Humphrey | unknown | 16.42 | 99 | +16 | 25.3 |  |  |
| 84 | KaVontae Turpin | unknown | 16.37 | missing | new | 74.7 |  |  |
| 85 | Xavier Legette | unknown | 16.18 | 66 | -19 | 74.7 |  |  |
| 86 | Devaughn Vele | unknown | 15.67 | 63 | -23 | 74.7 |  |  |
| 87 | Tez Johnson | unknown | 15.54 | 87 | 0 | 74.7 |  |  |
| 88 | Tyquan Thornton | unknown | 15.45 | 73 | -15 | 74.7 |  |  |
| 89 | Pat Bryant | unknown | 15.44 | 79 | -10 | 74.7 |  |  |
| 90 | Mecole Hardman | unknown | 15.42 | missing | new | 17.2 |  |  |
| 91 | Jalen Nailor | unknown | 15.41 | 84 | -7 | 74.7 |  |  |
| 92 | Van Jefferson | unknown | 15.25 | 65 | -27 | 74.7 |  |  |
| 93 | Malik Nabers | unknown | 14.98 | 16 | -77 | 74.7 |  |  |
| 94 | Jayden Reed | unknown | 14.88 | 55 | -39 | 74.7 |  |  |
| 95 | Dontayvion Wicks | unknown | 14.86 | 80 | -15 | 74.7 |  |  |
| 96 | David Sills | unknown | 14.54 | missing | new | 40.2 |  |  |
| 97 | Ashton Dulin | unknown | 14.17 | missing | new | 17.2 |  |  |
| 98 | Calvin Austin III | unknown | 13.66 | 78 | -20 | 74.7 |  |  |
| 99 | Tre Harris | unknown | 13.50 | 91 | -8 | 74.7 |  |  |
| 100 | Jalen McMillan | unknown | 13.28 | 62 | -38 | 74.7 |  |  |

## WR Position Board: BQML Linear Points Top 100
| Pos rank | Player | Sleeper team | Score | Current pos rank | Delta | Missing % | Status | Injury |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ja'Marr Chase | unknown | 620.70 | 3 | +2 | 74.7 |  |  |
| 2 | Amon-Ra St. Brown | unknown | 580.95 | 4 | +2 | 74.7 |  |  |
| 3 | Puka Nacua | unknown | 554.22 | 2 | -1 | 74.7 |  |  |
| 4 | Jaxon Smith-Njigba | unknown | 549.93 | 1 | -3 | 74.7 |  |  |
| 5 | Chris Olave | unknown | 527.70 | 8 | +3 | 74.7 |  |  |
| 6 | Justin Jefferson | unknown | 474.34 | 10 | +4 | 74.7 |  |  |
| 7 | George Pickens | unknown | 470.21 | 13 | +6 | 74.7 |  |  |
| 8 | Wan'Dale Robinson | unknown | 469.94 | 17 | +9 | 74.7 |  |  |
| 9 | Michael Wilson | unknown | 425.42 | 30 | +21 | 74.7 |  |  |
| 10 | Emeka Egbuka | unknown | 425.40 | 26 | +16 | 74.7 |  |  |
| 11 | Tetairoa McMillan | unknown | 417.94 | 18 | +7 | 74.7 |  |  |
| 12 | Nico Collins | unknown | 408.78 | 14 | +2 | 74.7 |  |  |
| 13 | CeeDee Lamb | unknown | 401.01 | 11 | -2 | 74.7 |  |  |
| 14 | Zay Flowers | unknown | 390.84 | 12 | -2 | 74.7 |  |  |
| 15 | Drake London | unknown | 389.27 | 5 | -10 | 74.7 |  |  |
| 16 | DeVonta Smith | unknown | 387.96 | 20 | +4 | 74.7 |  |  |
| 17 | Michael Pittman | unknown | 368.66 | 50 | +33 | 74.7 |  |  |
| 18 | Ladd McConkey | unknown | 358.45 | 34 | +16 | 74.7 |  |  |
| 19 | Jerry Jeudy | unknown | 353.55 | 42 | +23 | 74.7 |  |  |
| 20 | Troy Franklin | unknown | 342.53 | 41 | +21 | 74.7 |  |  |
| 21 | Jaylen Waddle | unknown | 342.23 | 22 | +1 | 74.7 |  |  |
| 22 | Jameson Williams | unknown | 341.35 | 28 | +6 | 74.7 |  |  |
| 23 | Tee Higgins | unknown | 337.67 | 23 | 0 | 74.7 |  |  |
| 24 | Khalil Shakir | unknown | 316.95 | 45 | +21 | 74.7 |  |  |
| 25 | Rome Odunze | unknown | 314.29 | 19 | -6 | 74.7 |  |  |
| 26 | Parker Washington | unknown | 311.82 | 39 | +13 | 74.7 |  |  |
| 27 | Jauan Jennings | unknown | 307.15 | 36 | +9 | 74.7 |  |  |
| 28 | Elic Ayomanor | unknown | 300.73 | 43 | +15 | 74.7 |  |  |
| 29 | Brian Thomas Jr. | unknown | 300.60 | 48 | +19 | 74.7 |  |  |
| 30 | Tre Tucker | unknown | 296.98 | 38 | +8 | 74.7 |  |  |
| 31 | Alec Pierce | unknown | 294.74 | 25 | -6 | 74.7 |  |  |
| 32 | Romeo Doubs | unknown | 293.45 | 37 | +5 | 74.7 |  |  |
| 33 | Rashid Shaheed | unknown | 292.71 | 59 | +26 | 74.7 |  |  |
| 34 | Josh Downs | unknown | 292.20 | 58 | +24 | 74.7 |  |  |
| 35 | Quentin Johnston | unknown | 288.33 | 31 | -4 | 74.7 |  |  |
| 36 | Rashee Rice | unknown | 271.54 | 7 | -29 | 74.7 |  |  |
| 37 | Jordan Addison | unknown | 271.47 | 33 | -4 | 74.7 |  |  |
| 38 | Darnell Mooney | unknown | 246.25 | 49 | +11 | 74.7 |  |  |
| 39 | Adonai Mitchell | unknown | 245.33 | 69 | +30 | 74.7 |  |  |
| 40 | Xavier Worthy | unknown | 232.77 | 53 | +13 | 74.7 |  |  |
| 41 | Chimere Dike | unknown | 229.42 | 72 | +31 | 74.7 |  |  |
| 42 | Jayden Higgins | unknown | 228.70 | 67 | +25 | 74.7 |  |  |
| 43 | Garrett Wilson | unknown | 218.83 | 6 | -37 | 74.7 |  |  |
| 44 | Xavier Legette | unknown | 214.51 | 66 | +22 | 74.7 |  |  |
| 45 | Keon Coleman | unknown | 205.04 | 47 | +2 | 74.7 |  |  |
| 46 | Christian Watson | unknown | 198.15 | 32 | -14 | 74.7 |  |  |
| 47 | Andrei Iosivas | unknown | 191.61 | 71 | +24 | 74.7 |  |  |
| 48 | Malik Washington | unknown | 189.78 | 75 | +27 | 74.7 |  |  |
| 49 | Luther Burden III | unknown | 189.24 | 86 | +37 | 74.7 |  |  |
| 50 | Ricky Pearsall | unknown | 188.24 | 40 | -10 | 74.7 |  |  |
| 51 | Xavier Hutchinson | unknown | 187.06 | 81 | +30 | 74.7 |  |  |
| 52 | Calvin Austin III | unknown | 185.41 | 78 | +26 | 74.7 |  |  |
| 53 | Ryan Flournoy | unknown | 182.93 | 77 | +24 | 74.7 |  |  |
| 54 | Van Jefferson | unknown | 177.03 | 65 | +11 | 74.7 |  |  |
| 55 | Jalen Nailor | unknown | 176.18 | 84 | +29 | 74.7 |  |  |
| 56 | Pat Bryant | unknown | 167.11 | 79 | +23 | 74.7 |  |  |
| 57 | Kayshon Boutte | unknown | 161.91 | 56 | -1 | 74.7 |  |  |
| 58 | Travis Hunter | unknown | 156.65 | 51 | -7 | 74.7 |  |  |
| 59 | Dontayvion Wicks | unknown | 155.08 | 80 | +21 | 74.7 |  |  |
| 60 | Jalen Coker | unknown | 152.74 | 57 | -3 | 74.7 |  |  |
| 61 | John Metchie III | unknown | 151.07 | 98 | +37 | 74.7 |  |  |
| 62 | Marvin Mims Jr. | unknown | 146.88 | missing | new | 74.7 |  |  |
| 63 | DeMario Douglas | unknown | 142.86 | 88 | +25 | 74.7 |  |  |
| 64 | Tre Harris | unknown | 140.76 | 91 | +27 | 74.7 |  |  |
| 65 | Isaiah Bond | unknown | 139.63 | 90 | +25 | 74.7 |  |  |
| 66 | Devaughn Vele | unknown | 138.79 | 63 | -3 | 74.7 |  |  |
| 67 | Malik Nabers | unknown | 138.51 | 16 | -51 | 74.7 |  |  |
| 68 | Tez Johnson | unknown | 137.54 | 87 | +19 | 74.7 |  |  |
| 69 | Matthew Golden | unknown | 135.21 | 82 | +13 | 74.7 |  |  |
| 70 | Cedric Tillman | unknown | 134.04 | 96 | +26 | 74.7 |  |  |
| 71 | Rashod Bateman | unknown | 130.61 | 83 | +12 | 74.7 |  |  |
| 72 | Tyquan Thornton | unknown | 130.03 | 73 | +1 | 74.7 |  |  |
| 73 | Jahan Dotson | unknown | 118.37 | missing | new | 74.7 |  |  |
| 74 | Dyami Brown | unknown | 116.44 | missing | new | 74.7 |  |  |
| 75 | Jalen Tolbert | unknown | 114.65 | 97 | +22 | 74.7 |  |  |
| 76 | Isaiah Williams | unknown | 111.97 | missing | new | 74.7 |  |  |
| 77 | Jaylin Noel | unknown | 103.97 | missing | new | 74.7 |  |  |
| 78 | Jaylin Lane | unknown | 102.62 | missing | new | 74.7 |  |  |
| 79 | KaVontae Turpin | unknown | 98.91 | missing | new | 74.7 |  |  |
| 80 | Dont'e Thornton Jr. | unknown | 96.77 | missing | new | 74.7 |  |  |
| 81 | Jack Bech | unknown | 95.71 | missing | new | 74.7 |  |  |
| 82 | Isaac TeSlaa | unknown | 92.68 | 93 | +11 | 74.7 |  |  |
| 83 | Jayden Reed | unknown | 81.55 | 55 | -28 | 74.7 |  |  |
| 84 | Tory Horton | unknown | 79.41 | 85 | +1 | 74.7 |  |  |
| 85 | Xavier Smith | unknown | 78.32 | missing | new | 74.7 |  |  |
| 86 | Tyrell Shavers | unknown | 78.25 | missing | new | 74.7 |  |  |
| 87 | Kevin Austin Jr. | unknown | 78.19 | missing | new | 74.7 |  |  |
| 88 | Treylon Burks | unknown | 76.44 | 92 | +4 | 74.7 |  |  |
| 89 | Jordan Whittington | unknown | 75.79 | missing | new | 74.7 |  |  |
| 90 | Konata Mumpfield | unknown | 74.27 | missing | new | 74.7 |  |  |
| 91 | Roman Wilson | unknown | 71.47 | missing | new | 74.7 |  |  |
| 92 | Isaiah Hodgins | unknown | 71.30 | missing | new | 74.7 |  |  |
| 93 | Kyle Williams | unknown | 65.30 | missing | new | 74.7 |  |  |
| 94 | Nick Westbrook-Ikhine | unknown | 64.21 | missing | new | 74.7 |  |  |
| 95 | Tyler Johnson | unknown | 63.01 | missing | new | 74.7 |  |  |
| 96 | Jalen McMillan | unknown | 60.06 | 62 | -34 | 74.7 |  |  |
| 97 | Brycen Tremayne | unknown | 56.22 | missing | new | 74.7 |  |  |
| 98 | Luke McCaffrey | unknown | 51.89 | missing | new | 74.7 |  |  |
| 99 | Casey Washington | unknown | 51.57 | 95 | -4 | 74.7 |  |  |
| 100 | Jamari Thrash | unknown | 49.11 | missing | new | 74.7 |  |  |

## TE Position Board: Current Pigskin Top 35
| Pos rank | Player | Team | Score |
| --- | --- | --- | --- |
| 1 | Trey McBride | ARI | 98.00 |
| 2 | Brock Bowers | LV | 94.00 |
| 3 | George Kittle | SF | 91.00 |
| 4 | Tucker Kraft | GB | 88.00 |
| 5 | Sam LaPorta | DET | 86.00 |
| 6 | Dallas Goedert | PHI | 85.00 |
| 7 | Kyle Pitts | ATL | 84.00 |
| 8 | Travis Kelce | KC | 83.00 |
| 9 | Tyler Warren | IND | 80.00 |
| 10 | Dalton Kincaid | BUF | 78.00 |
| 11 | Hunter Henry | NE | 77.00 |
| 12 | Dalton Schultz | HOU | 76.00 |
| 13 | Juwan Johnson | NO | 74.00 |
| 14 | Colston Loveland | CHI | 73.00 |
| 15 | Jake Ferguson | DAL | 72.00 |
| 16 | Harold Fannin Jr. | CLE | 70.00 |
| 17 | Brenton Strange | JAX | 68.00 |
| 18 | Mark Andrews | BAL | 66.00 |
| 19 | T.J. Hockenson | MIN | 65.00 |
| 20 | Cade Otton | TB | 64.00 |
| 21 | Theo Johnson | NYG | 63.00 |
| 22 | Mason Taylor | NYJ | 62.00 |
| 23 | Oronde Gadsden II | LAC | 61.00 |
| 24 | AJ Barner | SEA | 60.00 |
| 25 | Jake Tonges | SF | 59.00 |
| 26 | Greg Dulcich | MIA | 58.00 |
| 27 | Drake Dabney | GB | 57.00 |
| 28 | David Njoku | LAC | 56.00 |
| 29 | Colby Parkinson | LAR | 55.00 |
| 30 | Pat Freiermuth | PIT | 54.00 |
| 31 | Evan Engram | DEN | 53.00 |
| 32 | Chig Okonkwo | WAS | 52.00 |
| 33 | Darnell Washington | PIT | 48.00 |
| 34 | Dawson Knox | BUF | 47.00 |
| 35 | Cole Kmet | CHI | 46.00 |

## TE Position Board: BQML Logistic Top 35
| Pos rank | Player | Sleeper team | Score | Current pos rank | Delta | Missing % | Status | Injury |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Trey McBride | unknown | 81.81 | 1 | 0 | 74.7 |  |  |
| 2 | George Kittle | SF | 60.30 | 3 | +1 | 16.1 | Active | Questionable |
| 3 | Travis Kelce | KC | 59.24 | 8 | +5 | 16.1 | Active |  |
| 4 | David Njoku | LAC | 49.10 | 28 | +24 | 16.1 | Active |  |
| 5 | Kyle Pitts | unknown | 47.55 | 7 | +2 | 74.7 |  |  |
| 6 | Mark Andrews | BAL | 46.11 | 18 | +12 | 16.1 | Active |  |
| 7 | Tyler Warren | unknown | 44.33 | 9 | +2 | 74.7 |  |  |
| 8 | Evan Engram | DEN | 43.16 | 31 | +23 | 16.1 | Active |  |
| 9 | Juwan Johnson | unknown | 41.55 | 13 | +4 | 74.7 |  |  |
| 10 | T.J. Hockenson | unknown | 39.90 | 19 | +9 | 20.7 |  |  |
| 11 | Dallas Goedert | PHI | 38.97 | 6 | -5 | 16.1 | Active |  |
| 12 | Brock Bowers | unknown | 38.45 | 2 | -10 | 74.7 |  |  |
| 13 | Jake Ferguson | unknown | 37.80 | 15 | +2 | 74.7 |  |  |
| 14 | Harold Fannin Jr. | unknown | 37.59 | 16 | +2 | 74.7 |  |  |
| 15 | Colston Loveland | unknown | 36.97 | 14 | -1 | 74.7 |  |  |
| 16 | Tucker Kraft | unknown | 32.55 | 4 | -12 | 74.7 |  |  |
| 17 | Dalton Schultz | HOU | 32.23 | 12 | -5 | 20.7 | Active |  |
| 18 | Hunter Henry | NE | 32.15 | 11 | -7 | 20.7 | Active |  |
| 19 | AJ Barner | unknown | 31.48 | 24 | +5 | 74.7 |  |  |
| 20 | Sam LaPorta | unknown | 29.71 | 5 | -15 | 74.7 |  |  |
| 21 | Tyler Conklin | unknown | 28.13 | missing | new | 16.1 | Active |  |
| 22 | Tyler Higbee | LAR | 27.93 | 39 | +17 | 20.7 | Active |  |
| 23 | Mike Gesicki | CIN | 27.16 | 40 | +17 | 20.7 | Active |  |
| 24 | Brenton Strange | unknown | 26.91 | 17 | -7 | 74.7 |  |  |
| 25 | Cade Otton | unknown | 25.07 | 20 | -5 | 74.7 |  |  |
| 26 | Dalton Kincaid | unknown | 25.02 | 10 | -16 | 74.7 |  |  |
| 27 | Noah Fant | unknown | 24.76 | 58 | +31 | 20.7 |  |  |
| 28 | Theo Johnson | unknown | 24.14 | 21 | -7 | 74.7 |  |  |
| 29 | Oronde Gadsden II | unknown | 24.10 | 23 | -6 | 74.7 |  |  |
| 30 | Chig Okonkwo | unknown | 23.65 | 32 | +2 | 74.7 |  |  |
| 31 | Dawson Knox | unknown | 22.39 | 34 | +3 | 20.7 |  |  |
| 32 | Mason Taylor | unknown | 21.22 | 22 | -10 | 74.7 |  |  |
| 33 | Foster Moreau | unknown | 20.93 | missing | new | 20.7 |  |  |
| 34 | Pat Freiermuth | unknown | 19.91 | 30 | -4 | 74.7 |  |  |
| 35 | Colby Parkinson | unknown | 18.98 | 29 | -6 | 74.7 |  |  |

## TE Position Board: BQML Linear Points Top 35
| Pos rank | Player | Sleeper team | Score | Current pos rank | Delta | Missing % | Status | Injury |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Trey McBride | unknown | 574.81 | 1 | 0 | 74.7 |  |  |
| 2 | Kyle Pitts | unknown | 399.33 | 7 | +5 | 74.7 |  |  |
| 3 | Tyler Warren | unknown | 369.35 | 9 | +6 | 74.7 |  |  |
| 4 | Juwan Johnson | unknown | 343.96 | 13 | +9 | 74.7 |  |  |
| 5 | Harold Fannin Jr. | unknown | 342.82 | 16 | +11 | 74.7 |  |  |
| 6 | Jake Ferguson | unknown | 340.99 | 15 | +9 | 74.7 |  |  |
| 7 | Brock Bowers | unknown | 297.32 | 2 | -5 | 74.7 |  |  |
| 8 | Colston Loveland | unknown | 279.35 | 14 | +6 | 74.7 |  |  |
| 9 | Cade Otton | unknown | 273.75 | 20 | +11 | 74.7 |  |  |
| 10 | Chig Okonkwo | unknown | 258.19 | 32 | +22 | 74.7 |  |  |
| 11 | Theo Johnson | unknown | 252.77 | 21 | +10 | 74.7 |  |  |
| 12 | Oronde Gadsden II | unknown | 234.97 | 23 | +11 | 74.7 |  |  |
| 13 | Mason Taylor | unknown | 222.71 | 22 | +9 | 74.7 |  |  |
| 14 | AJ Barner | unknown | 216.76 | 24 | +10 | 74.7 |  |  |
| 15 | Brenton Strange | unknown | 209.69 | 17 | +2 | 74.7 |  |  |
| 16 | Colby Parkinson | unknown | 190.80 | 29 | +13 | 74.7 |  |  |
| 17 | Pat Freiermuth | unknown | 183.67 | 30 | +13 | 74.7 |  |  |
| 18 | Gunnar Helm | unknown | 182.62 | 41 | +23 | 74.7 |  |  |
| 19 | Sam LaPorta | unknown | 180.22 | 5 | -14 | 74.7 |  |  |
| 20 | Dalton Kincaid | unknown | 172.52 | 10 | -10 | 74.7 |  |  |
| 21 | Michael Mayer | unknown | 167.84 | 36 | +15 | 74.7 |  |  |
| 22 | Tucker Kraft | unknown | 164.89 | 4 | -18 | 74.7 |  |  |
| 23 | Cole Kmet | unknown | 162.60 | 35 | +12 | 74.7 |  |  |
| 24 | Jake Tonges | unknown | 158.47 | 25 | +1 | 74.7 |  |  |
| 25 | Darnell Washington | unknown | 148.03 | 33 | +8 | 74.7 |  |  |
| 26 | Tommy Tremble | unknown | 124.06 | 46 | +20 | 74.7 |  |  |
| 27 | Isaiah Likely | unknown | 123.58 | 38 | +11 | 74.7 |  |  |
| 28 | Noah Gray | unknown | 121.14 | missing | new | 74.7 |  |  |
| 29 | Elijah Higgins | unknown | 120.15 | missing | new | 74.7 |  |  |
| 30 | Greg Dulcich | unknown | 115.69 | 26 | -4 | 74.7 |  |  |
| 31 | Ja'Tavion Sanders | unknown | 115.08 | 44 | +13 | 74.7 |  |  |
| 32 | Davis Allen | unknown | 109.14 | 51 | +19 | 74.7 |  |  |
| 33 | Luke Musgrave | unknown | 103.31 | 52 | +19 | 74.7 |  |  |
| 34 | Jeremy Ruckert | unknown | 95.60 | 55 | +21 | 74.7 |  |  |
| 35 | Daniel Bellinger | unknown | 89.85 | 42 | +7 | 74.7 |  |  |

## Movement: Logistic Risers Top 25
| Pred rank | Player | Pos | Score | Current rank | Delta | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| 121 | Mason Rudolph | QB | 35.86 | missing | new | PIT |
| 132 | Kirk Cousins | QB | 33.45 | missing | new | LV |
| 150 | Tyler Conklin | TE | 28.13 | missing | new | unknown |
| 158 | Demarcus Robinson | WR | 26.84 | missing | new | SF |
| 160 | Drew Lock | QB | 25.57 | missing | new | unknown |
| 162 | David Moore | WR | 25.11 | missing | new | CAR |
| 165 | Jarrett Stidham | QB | 24.94 | missing | new | unknown |
| 167 | Tim Patrick | WR | 24.74 | missing | new | NYJ |
| 171 | Tyrod Taylor | QB | 24.12 | missing | new | GB |
| 186 | Andy Dalton | QB | 22.27 | missing | new | PHI |
| 192 | Ollie Gordon II | RB | 21.85 | missing | new | unknown |
| 194 | Mitchell Trubisky | QB | 21.49 | missing | new | TEN |
| 198 | Foster Moreau | TE | 20.93 | missing | new | unknown |
| 205 | Greg Dortch | WR | 20.05 | missing | new | unknown |
| 210 | Nick Mullens | QB | 19.83 | missing | new | JAX |
| 214 | Justin Watson | WR | 18.98 | missing | new | HOU |
| 215 | Tanner Hudson | TE | 18.82 | missing | new | CIN |
| 216 | Cedrick Wilson Jr. | WR | 18.77 | missing | new | unknown |
| 219 | Kalif Raymond | WR | 18.04 | missing | new | CHI |
| 228 | JuJu Smith-Schuster | WR | 16.92 | missing | new | NYG |
| 230 | Marvin Mims Jr. | WR | 16.87 | missing | new | unknown |
| 233 | Durham Smythe | TE | 16.51 | missing | new | BAL |
| 236 | KaVontae Turpin | WR | 16.37 | missing | new | unknown |
| 238 | Johnny Mundt | TE | 15.97 | missing | new | PHI |
| 247 | Mecole Hardman | WR | 15.42 | missing | new | unknown |

## Movement: Logistic Fallers Top 25
| Pred rank | Player | Pos | Score | Current rank | Delta | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| 923 | Shedeur Sanders | QB | 3.66 | 172 | -751 | unknown |
| 674 | Fernando Mendoza | QB | 4.41 | 182 | -492 | unknown |
| 411 | Drake Dabney | TE | 5.86 | 139 | -272 | unknown |
| 426 | Cam Ward | QB | 5.52 | 164 | -262 | unknown |
| 383 | Jakobie Keeney-James | WR | 6.54 | 138 | -245 | unknown |
| 254 | Malik Nabers | WR | 14.98 | 39 | -215 | unknown |
| 211 | Garrett Wilson | WR | 19.56 | 14 | -197 | unknown |
| 437 | Davis Mills | QB | 5.18 | 247 | -190 | unknown |
| 441 | Shane Zylstra | TE | 5.09 | 270 | -171 | unknown |
| 338 | Theo Wease Jr. | WR | 8.27 | 177 | -161 | unknown |
| 431 | Quinn Ewers | QB | 5.35 | 273 | -158 | unknown |
| 379 | J.J. McCarthy | QB | 6.63 | 224 | -155 | unknown |
| 387 | Treylon Burks | WR | 6.50 | 235 | -152 | unknown |
| 206 | Jayden Daniels | QB | 20.00 | 56 | -150 | unknown |
| 203 | Joe Burrow | QB | 20.24 | 61 | -142 | unknown |
| 268 | Travis Hunter | WR | 12.93 | 130 | -138 | unknown |
| 289 | Tua Tagovailoa | QB | 10.89 | 153 | -136 | unknown |
| 305 | Albert Okwuegbunam | TE | 9.98 | 186 | -119 | unknown |
| 249 | Greg Dulcich | TE | 15.37 | 135 | -114 | unknown |
| 255 | Jayden Reed | WR | 14.88 | 141 | -114 | unknown |
| 378 | Ben Sims | TE | 6.66 | 265 | -113 | unknown |
| 146 | Sam LaPorta | TE | 29.71 | 35 | -111 | unknown |
| 347 | Cade Stover | TE | 7.93 | 236 | -111 | unknown |
| 349 | Casey Washington | WR | 7.90 | 243 | -106 | unknown |
| 372 | Braelon Allen | RB | 6.86 | 266 | -106 | unknown |

## Movement: Linear Points Risers Top 25
| Pred rank | Player | Pos | Score | Current rank | Delta | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| 87 | Marvin Mims Jr. | WR | 146.88 | missing | new | unknown |
| 100 | Noah Gray | TE | 121.14 | missing | new | unknown |
| 101 | Elijah Higgins | TE | 120.15 | missing | new | unknown |
| 102 | Jahan Dotson | WR | 118.37 | missing | new | unknown |
| 103 | Dyami Brown | WR | 116.44 | missing | new | unknown |
| 107 | Isaiah Williams | WR | 111.97 | missing | new | unknown |
| 110 | Jaylin Noel | WR | 103.97 | missing | new | unknown |
| 112 | Jaylin Lane | WR | 102.62 | missing | new | unknown |
| 113 | KaVontae Turpin | WR | 98.91 | missing | new | unknown |
| 114 | Dont'e Thornton Jr. | WR | 96.77 | missing | new | unknown |
| 115 | Jack Bech | WR | 95.71 | missing | new | unknown |
| 119 | Tyler Badie | RB | 88.39 | missing | new | unknown |
| 120 | Elijah Arroyo | TE | 83.62 | missing | new | unknown |
| 123 | Mitchell Evans | TE | 80.25 | missing | new | unknown |
| 125 | Xavier Smith | WR | 78.32 | missing | new | unknown |
| 126 | Tyrell Shavers | WR | 78.25 | missing | new | unknown |
| 127 | Kevin Austin Jr. | WR | 78.19 | missing | new | unknown |
| 128 | Adam Trautman | TE | 76.80 | missing | new | unknown |
| 130 | Jordan Whittington | WR | 75.79 | missing | new | unknown |
| 131 | Konata Mumpfield | WR | 74.27 | missing | new | unknown |
| 133 | Luke Schoonmaker | TE | 73.49 | missing | new | unknown |
| 134 | Roman Wilson | WR | 71.47 | missing | new | unknown |
| 135 | Isaiah Hodgins | WR | 71.30 | missing | new | unknown |
| 137 | Kyle Williams | WR | 65.30 | missing | new | unknown |
| 139 | Nick Westbrook-Ikhine | WR | 64.21 | missing | new | unknown |

## Movement: Linear Points Fallers Top 25
| Pred rank | Player | Pos | Score | Current rank | Delta | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| 935 | Jonathan Taylor | RB | -307.48 | 19 | -916 | unknown |
| 936 | James Cook | RB | -340.08 | 27 | -909 | unknown |
| 910 | Drake Maye | QB | -129.35 | 7 | -903 | unknown |
| 914 | Jalen Hurts | QB | -146.43 | 13 | -901 | unknown |
| 933 | Kyren Williams | RB | -225.34 | 33 | -900 | unknown |
| 900 | Bijan Robinson | RB | -93.04 | 9 | -891 | unknown |
| 907 | Trevor Lawrence | QB | -110.31 | 22 | -885 | unknown |
| 929 | Javonte Williams | RB | -212.02 | 52 | -877 | unknown |
| 894 | De'Von Achane | RB | -76.93 | 21 | -873 | unknown |
| 932 | Travis Etienne | RB | -224.99 | 62 | -870 | unknown |
| 882 | Jahmyr Gibbs | RB | -53.46 | 15 | -867 | unknown |
| 906 | Bo Nix | QB | -108.20 | 40 | -866 | unknown |
| 902 | Caleb Williams | QB | -96.69 | 37 | -865 | unknown |
| 908 | Justin Herbert | QB | -115.33 | 48 | -860 | unknown |
| 928 | Breece Hall | RB | -211.72 | 69 | -859 | unknown |
| 922 | D'Andre Swift | RB | -177.72 | 72 | -850 | unknown |
| 878 | Jordan Love | QB | -50.20 | 30 | -848 | unknown |
| 858 | Brock Purdy | QB | -25.12 | 16 | -842 | unknown |
| 888 | Chase Brown | RB | -61.67 | 47 | -841 | unknown |
| 920 | Ashton Jeanty | RB | -171.07 | 79 | -841 | unknown |
| 895 | Jayden Daniels | QB | -77.81 | 56 | -839 | unknown |
| 909 | Jaxson Dart | QB | -117.99 | 73 | -836 | unknown |
| 919 | Jaylen Warren | RB | -169.36 | 84 | -835 | unknown |
| 934 | Quinshon Judkins | RB | -234.36 | 100 | -834 | unknown |
| 927 | Rico Dowdle | RB | -196.28 | 98 | -829 | unknown |

## Cutline Crossings: Logistic
### Overall top 24
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | James Cook | RB | 3 | 27 | 99.51 | unknown |
| enters | Kyren Williams | RB | 6 | 33 | 98.83 | unknown |
| enters | Chase Brown | RB | 7 | 47 | 98.63 | unknown |
| enters | Travis Etienne | RB | 8 | 62 | 98.51 | unknown |
| enters | Javonte Williams | RB | 9 | 52 | 98.30 | unknown |
| enters | Ashton Jeanty | RB | 10 | 79 | 98.27 | unknown |
| enters | Breece Hall | RB | 11 | 69 | 97.56 | unknown |
| enters | Rico Dowdle | RB | 12 | 98 | 97.37 | unknown |
| enters | D'Andre Swift | RB | 13 | 72 | 97.23 | unknown |
| enters | Jaylen Warren | RB | 14 | 84 | 96.00 | unknown |
| enters | Kenneth Walker III | RB | 15 | 129 | 95.08 | unknown |
| enters | Quinshon Judkins | RB | 16 | 100 | 94.50 | unknown |
| enters | TreVeyon Henderson | RB | 17 | 105 | 91.45 | unknown |
| enters | Woody Marks | RB | 19 | 156 | 90.17 | unknown |
| enters | Tyrone Tracy Jr. | RB | 20 | 132 | 89.78 | unknown |
| enters | Zach Charbonnet | RB | 21 | 137 | 88.47 | unknown |
| enters | RJ Harvey | RB | 22 | 159 | 85.36 | unknown |
| enters | Kenneth Gainwell | RB | 24 | 119 | 84.51 | unknown |
| exits | Drake Maye | QB | 28 | 7 | 83.18 | unknown |
| exits | Trey McBride | TE | 29 | 4 | 81.81 | unknown |
| exits | Ja'Marr Chase | WR | 30 | 6 | 81.52 | unknown |
| exits | Amon-Ra St. Brown | WR | 32 | 8 | 79.86 | unknown |
| exits | Josh Allen | QB | 34 | 2 | 78.46 | BUF |
| exits | Christian McCaffrey | RB | 42 | 3 | 74.86 | SF |
| exits | Chris Olave | WR | 48 | 20 | 67.65 | unknown |
| exits | George Kittle | TE | 55 | 18 | 60.30 | SF |
| exits | Patrick Mahomes | QB | 60 | 10 | 58.83 | KC |
| exits | Jalen Hurts | QB | 61 | 13 | 58.44 | unknown |
| exits | A.J. Brown | WR | 66 | 23 | 56.59 | unknown |
| exits | Drake London | WR | 80 | 11 | 49.17 | unknown |
| exits | Trevor Lawrence | QB | 82 | 22 | 49.06 | unknown |
| exits | Justin Jefferson | WR | 85 | 24 | 48.48 | unknown |
| exits | Brock Purdy | QB | 96 | 16 | 45.49 | unknown |
| exits | Brock Bowers | TE | 113 | 12 | 38.45 | unknown |
| exits | Rashee Rice | WR | 114 | 17 | 37.86 | unknown |
| exits | Garrett Wilson | WR | 211 | 14 | 19.56 | unknown |

### Overall top 50
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Travis Etienne | RB | 8 | 62 | 98.51 | unknown |
| enters | Javonte Williams | RB | 9 | 52 | 98.30 | unknown |
| enters | Ashton Jeanty | RB | 10 | 79 | 98.27 | unknown |
| enters | Breece Hall | RB | 11 | 69 | 97.56 | unknown |
| enters | Rico Dowdle | RB | 12 | 98 | 97.37 | unknown |
| enters | D'Andre Swift | RB | 13 | 72 | 97.23 | unknown |
| enters | Jaylen Warren | RB | 14 | 84 | 96.00 | unknown |
| enters | Kenneth Walker III | RB | 15 | 129 | 95.08 | unknown |
| enters | Quinshon Judkins | RB | 16 | 100 | 94.50 | unknown |
| enters | TreVeyon Henderson | RB | 17 | 105 | 91.45 | unknown |
| enters | Woody Marks | RB | 19 | 156 | 90.17 | unknown |
| enters | Tyrone Tracy Jr. | RB | 20 | 132 | 89.78 | unknown |
| enters | Zach Charbonnet | RB | 21 | 137 | 88.47 | unknown |
| enters | RJ Harvey | RB | 22 | 159 | 85.36 | unknown |
| enters | Kenneth Gainwell | RB | 24 | 119 | 84.51 | unknown |
| enters | Kyle Monangai | RB | 25 | 161 | 84.12 | unknown |
| enters | Bucky Irving | RB | 26 | 93 | 83.86 | unknown |
| enters | Jacory Croskey-Merritt | RB | 31 | 171 | 80.61 | unknown |
| enters | Derrick Henry | RB | 33 | 87 | 78.73 | BAL |
| enters | Rachaad White | RB | 35 | 148 | 78.03 | unknown |
| enters | Alvin Kamara | RB | 36 | 143 | 77.27 | NO |
| enters | J.K. Dobbins | RB | 37 | 107 | 76.55 | unknown |
| enters | Omarion Hampton | RB | 39 | 66 | 75.18 | unknown |
| enters | Kimani Vidal | RB | 40 | 190 | 75.09 | unknown |
| enters | Rhamondre Stevenson | RB | 41 | 115 | 75.01 | unknown |
| enters | Jordan Mason | RB | 43 | 175 | 74.70 | unknown |
| enters | Josh Jacobs | RB | 44 | 57 | 73.58 | unknown |
| enters | Chuba Hubbard | RB | 45 | 167 | 72.71 | unknown |
| enters | Blake Corum | RB | 47 | 181 | 71.08 | unknown |
| enters | James Conner | RB | 49 | 123 | 67.56 | ARI |
| enters | Tyler Allgeier | RB | 50 | 202 | 67.06 | unknown |
| exits | Davante Adams | WR | 52 | 36 | 64.60 | LAR |
| exits | George Kittle | TE | 55 | 18 | 60.30 | SF |
| exits | Zay Flowers | WR | 56 | 29 | 59.45 | unknown |
| exits | Travis Kelce | TE | 57 | 44 | 59.24 | KC |
| exits | Patrick Mahomes | QB | 60 | 10 | 58.83 | KC |
| exits | Jalen Hurts | QB | 61 | 13 | 58.44 | unknown |
| exits | Wan'Dale Robinson | WR | 63 | 45 | 57.90 | unknown |
| exits | A.J. Brown | WR | 66 | 23 | 56.59 | unknown |
| exits | Nico Collins | WR | 70 | 34 | 55.54 | unknown |

### Overall top 100
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Kenneth Walker III | RB | 15 | 129 | 95.08 | unknown |
| enters | TreVeyon Henderson | RB | 17 | 105 | 91.45 | unknown |
| enters | Woody Marks | RB | 19 | 156 | 90.17 | unknown |
| enters | Tyrone Tracy Jr. | RB | 20 | 132 | 89.78 | unknown |
| enters | Zach Charbonnet | RB | 21 | 137 | 88.47 | unknown |
| enters | RJ Harvey | RB | 22 | 159 | 85.36 | unknown |
| enters | Kenneth Gainwell | RB | 24 | 119 | 84.51 | unknown |
| enters | Kyle Monangai | RB | 25 | 161 | 84.12 | unknown |
| enters | Jacory Croskey-Merritt | RB | 31 | 171 | 80.61 | unknown |
| enters | Rachaad White | RB | 35 | 148 | 78.03 | unknown |
| enters | Alvin Kamara | RB | 36 | 143 | 77.27 | NO |
| enters | J.K. Dobbins | RB | 37 | 107 | 76.55 | unknown |
| enters | Kimani Vidal | RB | 40 | 190 | 75.09 | unknown |
| enters | Rhamondre Stevenson | RB | 41 | 115 | 75.01 | unknown |
| enters | Jordan Mason | RB | 43 | 175 | 74.70 | unknown |
| enters | Chuba Hubbard | RB | 45 | 167 | 72.71 | unknown |
| enters | Blake Corum | RB | 47 | 181 | 71.08 | unknown |
| enters | James Conner | RB | 49 | 123 | 67.56 | ARI |
| enters | Tyler Allgeier | RB | 50 | 202 | 67.06 | unknown |
| enters | Aaron Jones | RB | 51 | 111 | 65.42 | MIN |
| enters | David Montgomery | RB | 53 | 151 | 64.24 | unknown |
| enters | Tony Pollard | RB | 54 | 140 | 63.48 | unknown |
| enters | Cooper Kupp | WR | 62 | 154 | 58.39 | SEA |
| enters | Emanuel Wilson | RB | 64 | 233 | 57.23 | unknown |
| enters | Isiah Pacheco | RB | 65 | 193 | 56.68 | unknown |
| enters | DJ Moore | WR | 67 | 173 | 56.28 | BUF |
| enters | Chris Godwin Jr. | WR | 68 | 157 | 56.07 | TB |
| enters | Michael Carter | RB | 69 | 226 | 55.84 | unknown |
| enters | David Njoku | TE | 81 | 144 | 49.10 | LAC |
| enters | Chris Rodriguez Jr. | RB | 84 | 178 | 48.92 | unknown |
| enters | Tyjae Spears | RB | 90 | 165 | 47.50 | unknown |
| enters | Calvin Ridley | WR | 91 | 117 | 46.44 | TEN |
| enters | Mark Andrews | TE | 92 | 103 | 46.11 | BAL |
| enters | Geno Smith | QB | 99 | 147 | 44.53 | NYJ |
| exits | Caleb Williams | QB | 101 | 37 | 43.76 | unknown |
| exits | Jaylen Waddle | WR | 103 | 55 | 42.51 | unknown |
| exits | Tee Higgins | WR | 104 | 58 | 41.76 | unknown |
| exits | Juwan Johnson | TE | 105 | 76 | 41.55 | unknown |
| exits | Alec Pierce | WR | 106 | 63 | 41.15 | unknown |
| exits | Justin Herbert | QB | 107 | 48 | 41.00 | unknown |

### QB12
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Lamar Jackson | QB | 3 | 14 | 75.55 | BAL |
| enters | Baker Mayfield | QB | 6 | 19 | 55.19 | TB |
| enters | Jared Goff | QB | 7 | 17 | 53.96 | DET |
| enters | Kyler Murray | QB | 8 | 21 | 53.95 | unknown |
| enters | Jaxson Dart | QB | 12 | 18 | 45.81 | unknown |
| exits | Brock Purdy | QB | 13 | 5 | 45.49 | unknown |
| exits | Daniel Jones | QB | 14 | 12 | 45.08 | unknown |
| exits | Dak Prescott | QB | 15 | 9 | 44.58 | DAL |
| exits | Caleb Williams | QB | 17 | 10 | 43.76 | unknown |
| exits | Matthew Stafford | QB | 19 | 7 | 38.76 | LAR |

### RB12
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Ashton Jeanty | RB | 10 | 16 | 98.27 | unknown |
| enters | Breece Hall | RB | 11 | 14 | 97.56 | unknown |
| enters | Rico Dowdle | RB | 12 | 21 | 97.37 | unknown |
| exits | Saquon Barkley | RB | 25 | 8 | 83.60 | PHI |
| exits | Christian McCaffrey | RB | 34 | 1 | 74.86 | SF |
| exits | Josh Jacobs | RB | 36 | 11 | 73.58 | unknown |

### RB24
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Kenneth Walker III | RB | 15 | 29 | 95.08 | unknown |
| enters | Woody Marks | RB | 18 | 36 | 90.17 | unknown |
| enters | Tyrone Tracy Jr. | RB | 19 | 30 | 89.78 | unknown |
| enters | Zach Charbonnet | RB | 20 | 31 | 88.47 | unknown |
| enters | RJ Harvey | RB | 21 | 37 | 85.36 | unknown |
| enters | Kenneth Gainwell | RB | 22 | 27 | 84.51 | unknown |
| enters | Kyle Monangai | RB | 23 | 38 | 84.12 | unknown |
| exits | Saquon Barkley | RB | 25 | 8 | 83.60 | PHI |
| exits | Derrick Henry | RB | 27 | 18 | 78.73 | BAL |
| exits | J.K. Dobbins | RB | 30 | 24 | 76.55 | unknown |
| exits | Omarion Hampton | RB | 31 | 13 | 75.18 | unknown |
| exits | Christian McCaffrey | RB | 34 | 1 | 74.86 | SF |
| exits | Josh Jacobs | RB | 36 | 11 | 73.58 | unknown |
| exits | Cam Skattebo | RB | 44 | 19 | 58.97 | unknown |

### RB36
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | RJ Harvey | RB | 21 | 37 | 85.36 | unknown |
| enters | Kyle Monangai | RB | 23 | 38 | 84.12 | unknown |
| enters | Jacory Croskey-Merritt | RB | 26 | 41 | 80.61 | unknown |
| enters | Kimani Vidal | RB | 32 | 46 | 75.09 | unknown |
| enters | Jordan Mason | RB | 35 | 42 | 74.70 | unknown |
| exits | James Conner | RB | 39 | 28 | 67.56 | ARI |
| exits | Aaron Jones | RB | 41 | 25 | 65.42 | MIN |
| exits | David Montgomery | RB | 42 | 35 | 64.24 | unknown |
| exits | Tony Pollard | RB | 43 | 32 | 63.48 | unknown |
| exits | Cam Skattebo | RB | 44 | 19 | 58.97 | unknown |

### WR12
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | George Pickens | WR | 5 | 13 | 72.05 | unknown |
| enters | Davante Adams | WR | 7 | 15 | 64.60 | LAR |
| enters | Mike Evans | WR | 9 | 29 | 59.17 | SF |
| enters | Cooper Kupp | WR | 10 | 60 | 58.39 | SEA |
| enters | Wan'Dale Robinson | WR | 11 | 17 | 57.90 | unknown |
| exits | CeeDee Lamb | WR | 18 | 11 | 51.39 | unknown |
| exits | Drake London | WR | 21 | 5 | 49.17 | unknown |
| exits | Justin Jefferson | WR | 23 | 10 | 48.48 | unknown |
| exits | Rashee Rice | WR | 34 | 7 | 37.86 | unknown |
| exits | Garrett Wilson | WR | 70 | 6 | 19.56 | unknown |

### WR24
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Mike Evans | WR | 9 | 29 | 59.17 | SF |
| enters | Cooper Kupp | WR | 10 | 60 | 58.39 | SEA |
| enters | DJ Moore | WR | 13 | 68 | 56.28 | BUF |
| enters | Chris Godwin Jr. | WR | 14 | 61 | 56.07 | TB |
| enters | Jakobi Meyers | WR | 16 | 27 | 51.76 | unknown |
| enters | Jameson Williams | WR | 19 | 28 | 49.66 | unknown |
| enters | Michael Wilson | WR | 20 | 30 | 49.41 | unknown |
| exits | Terry McLaurin | WR | 25 | 21 | 47.70 | unknown |
| exits | Jaylen Waddle | WR | 29 | 22 | 42.51 | unknown |
| exits | Tee Higgins | WR | 30 | 23 | 41.76 | unknown |
| exits | Rashee Rice | WR | 34 | 7 | 37.86 | unknown |
| exits | Rome Odunze | WR | 37 | 19 | 35.55 | unknown |
| exits | Garrett Wilson | WR | 70 | 6 | 19.56 | unknown |
| exits | Malik Nabers | WR | 93 | 16 | 14.98 | unknown |

### WR36
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Cooper Kupp | WR | 10 | 60 | 58.39 | SEA |
| enters | DJ Moore | WR | 13 | 68 | 56.28 | BUF |
| enters | Chris Godwin Jr. | WR | 14 | 61 | 56.07 | TB |
| enters | Calvin Ridley | WR | 26 | 46 | 46.44 | TEN |
| enters | Parker Washington | WR | 32 | 39 | 38.92 | unknown |
| enters | Michael Pittman | WR | 33 | 50 | 38.82 | unknown |
| enters | Tre Tucker | WR | 35 | 38 | 37.69 | unknown |
| enters | Troy Franklin | WR | 36 | 41 | 35.85 | unknown |
| exits | Rome Odunze | WR | 37 | 19 | 35.55 | unknown |
| exits | Ladd McConkey | WR | 38 | 34 | 35.05 | unknown |
| exits | Quentin Johnston | WR | 40 | 31 | 33.92 | unknown |
| exits | Jordan Addison | WR | 43 | 33 | 30.16 | unknown |
| exits | Christian Watson | WR | 48 | 32 | 27.84 | unknown |
| exits | Jauan Jennings | WR | 50 | 36 | 26.88 | unknown |
| exits | Garrett Wilson | WR | 70 | 6 | 19.56 | unknown |
| exits | Malik Nabers | WR | 93 | 16 | 14.98 | unknown |

### TE6
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Travis Kelce | TE | 3 | 8 | 59.24 | KC |
| enters | David Njoku | TE | 4 | 28 | 49.10 | LAC |
| enters | Kyle Pitts | TE | 5 | 7 | 47.55 | unknown |
| enters | Mark Andrews | TE | 6 | 18 | 46.11 | BAL |
| exits | Dallas Goedert | TE | 11 | 6 | 38.97 | PHI |
| exits | Brock Bowers | TE | 12 | 2 | 38.45 | unknown |
| exits | Tucker Kraft | TE | 16 | 4 | 32.55 | unknown |
| exits | Sam LaPorta | TE | 20 | 5 | 29.71 | unknown |

### TE12
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | David Njoku | TE | 4 | 28 | 49.10 | LAC |
| enters | Mark Andrews | TE | 6 | 18 | 46.11 | BAL |
| enters | Evan Engram | TE | 8 | 31 | 43.16 | DEN |
| enters | Juwan Johnson | TE | 9 | 13 | 41.55 | unknown |
| enters | T.J. Hockenson | TE | 10 | 19 | 39.90 | unknown |
| exits | Tucker Kraft | TE | 16 | 4 | 32.55 | unknown |
| exits | Dalton Schultz | TE | 17 | 12 | 32.23 | HOU |
| exits | Hunter Henry | TE | 18 | 11 | 32.15 | NE |
| exits | Sam LaPorta | TE | 20 | 5 | 29.71 | unknown |
| exits | Dalton Kincaid | TE | 26 | 10 | 25.02 | unknown |

### TE18
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | David Njoku | TE | 4 | 28 | 49.10 | LAC |
| enters | Evan Engram | TE | 8 | 31 | 43.16 | DEN |
| enters | T.J. Hockenson | TE | 10 | 19 | 39.90 | unknown |
| exits | Sam LaPorta | TE | 20 | 5 | 29.71 | unknown |
| exits | Brenton Strange | TE | 24 | 17 | 26.91 | unknown |
| exits | Dalton Kincaid | TE | 26 | 10 | 25.02 | unknown |

## Cutline Crossings: Linear points
### Overall top 24
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | George Pickens | WR | 8 | 31 | 470.21 | unknown |
| enters | Wan'Dale Robinson | WR | 9 | 45 | 469.94 | unknown |
| enters | Michael Wilson | WR | 10 | 77 | 425.42 | unknown |
| enters | Emeka Egbuka | WR | 11 | 67 | 425.40 | unknown |
| enters | Tetairoa McMillan | WR | 12 | 46 | 417.94 | unknown |
| enters | Nico Collins | WR | 13 | 34 | 408.78 | unknown |
| enters | CeeDee Lamb | WR | 14 | 26 | 401.01 | unknown |
| enters | Kyle Pitts | TE | 15 | 41 | 399.33 | unknown |
| enters | Zay Flowers | WR | 16 | 29 | 390.84 | unknown |
| enters | DeVonta Smith | WR | 18 | 51 | 387.96 | unknown |
| enters | Tyler Warren | TE | 19 | 54 | 369.35 | unknown |
| enters | Michael Pittman | WR | 20 | 126 | 368.66 | unknown |
| enters | Ladd McConkey | WR | 21 | 86 | 358.45 | unknown |
| enters | Jerry Jeudy | WR | 22 | 106 | 353.55 | unknown |
| enters | Juwan Johnson | TE | 23 | 76 | 343.96 | unknown |
| enters | Harold Fannin Jr. | TE | 24 | 90 | 342.82 | unknown |
| exits | Brock Bowers | TE | 36 | 12 | 297.32 | unknown |
| exits | Rashee Rice | WR | 45 | 17 | 271.54 | unknown |
| exits | Garrett Wilson | WR | 56 | 14 | 218.83 | unknown |
| exits | Josh Allen | QB | 181 | 2 | 26.19 | BUF |
| exits | Patrick Mahomes | QB | 191 | 10 | 21.82 | KC |
| exits | Christian McCaffrey | RB | 210 | 3 | 17.25 | SF |
| exits | A.J. Brown | WR | 221 | 23 | 15.69 | unknown |
| exits | George Kittle | TE | 244 | 18 | 13.09 | SF |
| exits | Brock Purdy | QB | 858 | 16 | -25.12 | unknown |
| exits | Jahmyr Gibbs | RB | 882 | 15 | -53.46 | unknown |
| exits | De'Von Achane | RB | 894 | 21 | -76.93 | unknown |
| exits | Bijan Robinson | RB | 900 | 9 | -93.04 | unknown |
| exits | Trevor Lawrence | QB | 907 | 22 | -110.31 | unknown |
| exits | Drake Maye | QB | 910 | 7 | -129.35 | unknown |
| exits | Jalen Hurts | QB | 914 | 13 | -146.43 | unknown |
| exits | Jonathan Taylor | RB | 935 | 19 | -307.48 | unknown |

### Overall top 50
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Michael Wilson | WR | 10 | 77 | 425.42 | unknown |
| enters | Emeka Egbuka | WR | 11 | 67 | 425.40 | unknown |
| enters | DeVonta Smith | WR | 18 | 51 | 387.96 | unknown |
| enters | Tyler Warren | TE | 19 | 54 | 369.35 | unknown |
| enters | Michael Pittman | WR | 20 | 126 | 368.66 | unknown |
| enters | Ladd McConkey | WR | 21 | 86 | 358.45 | unknown |
| enters | Jerry Jeudy | WR | 22 | 106 | 353.55 | unknown |
| enters | Juwan Johnson | TE | 23 | 76 | 343.96 | unknown |
| enters | Harold Fannin Jr. | TE | 24 | 90 | 342.82 | unknown |
| enters | Troy Franklin | WR | 25 | 102 | 342.53 | unknown |
| enters | Jaylen Waddle | WR | 26 | 55 | 342.23 | unknown |
| enters | Jameson Williams | WR | 27 | 71 | 341.35 | unknown |
| enters | Jake Ferguson | TE | 28 | 83 | 340.99 | unknown |
| enters | Tee Higgins | WR | 29 | 58 | 337.67 | unknown |
| enters | Khalil Shakir | WR | 30 | 114 | 316.95 | unknown |
| enters | Parker Washington | WR | 32 | 99 | 311.82 | unknown |
| enters | Jauan Jennings | WR | 33 | 92 | 307.15 | unknown |
| enters | Elic Ayomanor | WR | 34 | 109 | 300.73 | unknown |
| enters | Brian Thomas Jr. | WR | 35 | 122 | 300.60 | unknown |
| enters | Tre Tucker | WR | 37 | 95 | 296.98 | unknown |
| enters | Alec Pierce | WR | 38 | 63 | 294.74 | unknown |
| enters | Romeo Doubs | WR | 39 | 94 | 293.45 | unknown |
| enters | Rashid Shaheed | WR | 40 | 150 | 292.71 | unknown |
| enters | Josh Downs | WR | 41 | 149 | 292.20 | unknown |
| enters | Quentin Johnston | WR | 42 | 78 | 288.33 | unknown |
| enters | Colston Loveland | TE | 43 | 80 | 279.35 | unknown |
| enters | Cade Otton | TE | 44 | 113 | 273.75 | unknown |
| enters | Jordan Addison | WR | 46 | 85 | 271.47 | unknown |
| enters | Chig Okonkwo | TE | 47 | 158 | 258.19 | unknown |
| enters | Theo Johnson | TE | 48 | 116 | 252.77 | unknown |
| enters | Darnell Mooney | WR | 49 | 125 | 246.25 | unknown |
| enters | Adonai Mitchell | WR | 50 | 176 | 245.33 | unknown |
| exits | Garrett Wilson | WR | 56 | 14 | 218.83 | unknown |
| exits | Sam LaPorta | TE | 72 | 35 | 180.22 | unknown |
| exits | Tucker Kraft | TE | 78 | 28 | 164.89 | unknown |
| exits | Malik Nabers | WR | 92 | 39 | 138.51 | unknown |
| exits | Lamar Jackson | QB | 178 | 50 | 27.95 | BAL |
| exits | Josh Allen | QB | 181 | 2 | 26.19 | BUF |
| exits | Patrick Mahomes | QB | 191 | 10 | 21.82 | KC |
| exits | Saquon Barkley | RB | 195 | 42 | 20.93 | PHI |

### Overall top 100
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Michael Pittman | WR | 20 | 126 | 368.66 | unknown |
| enters | Jerry Jeudy | WR | 22 | 106 | 353.55 | unknown |
| enters | Troy Franklin | WR | 25 | 102 | 342.53 | unknown |
| enters | Khalil Shakir | WR | 30 | 114 | 316.95 | unknown |
| enters | Elic Ayomanor | WR | 34 | 109 | 300.73 | unknown |
| enters | Brian Thomas Jr. | WR | 35 | 122 | 300.60 | unknown |
| enters | Rashid Shaheed | WR | 40 | 150 | 292.71 | unknown |
| enters | Josh Downs | WR | 41 | 149 | 292.20 | unknown |
| enters | Cade Otton | TE | 44 | 113 | 273.75 | unknown |
| enters | Chig Okonkwo | TE | 47 | 158 | 258.19 | unknown |
| enters | Theo Johnson | TE | 48 | 116 | 252.77 | unknown |
| enters | Darnell Mooney | WR | 49 | 125 | 246.25 | unknown |
| enters | Adonai Mitchell | WR | 50 | 176 | 245.33 | unknown |
| enters | Oronde Gadsden II | TE | 51 | 124 | 234.97 | unknown |
| enters | Xavier Worthy | WR | 52 | 134 | 232.77 | unknown |
| enters | Chimere Dike | WR | 53 | 184 | 229.42 | unknown |
| enters | Jayden Higgins | WR | 54 | 169 | 228.70 | unknown |
| enters | Mason Taylor | TE | 55 | 120 | 222.71 | unknown |
| enters | AJ Barner | TE | 57 | 127 | 216.76 | unknown |
| enters | Xavier Legette | WR | 58 | 168 | 214.51 | unknown |
| enters | Keon Coleman | WR | 60 | 118 | 205.04 | unknown |
| enters | Andrei Iosivas | WR | 62 | 180 | 191.61 | unknown |
| enters | Colby Parkinson | TE | 63 | 146 | 190.80 | unknown |
| enters | Malik Washington | WR | 64 | 191 | 189.78 | unknown |
| enters | Luther Burden III | WR | 65 | 218 | 189.24 | unknown |
| enters | Ricky Pearsall | WR | 66 | 101 | 188.24 | unknown |
| enters | Xavier Hutchinson | WR | 67 | 206 | 187.06 | unknown |
| enters | Calvin Austin III | WR | 68 | 198 | 185.41 | unknown |
| enters | Pat Freiermuth | TE | 69 | 152 | 183.67 | unknown |
| enters | Ryan Flournoy | WR | 70 | 195 | 182.93 | unknown |
| enters | Gunnar Helm | TE | 71 | 200 | 182.62 | unknown |
| enters | Van Jefferson | WR | 73 | 166 | 177.03 | unknown |
| enters | Jalen Nailor | WR | 74 | 214 | 176.18 | unknown |
| enters | Michael Mayer | TE | 76 | 183 | 167.84 | unknown |
| enters | Pat Bryant | WR | 77 | 199 | 167.11 | unknown |
| enters | Cole Kmet | TE | 79 | 179 | 162.60 | unknown |
| enters | Kayshon Boutte | WR | 80 | 142 | 161.91 | unknown |
| enters | Jake Tonges | TE | 81 | 131 | 158.47 | unknown |
| enters | Travis Hunter | WR | 82 | 130 | 156.65 | unknown |
| enters | Dontayvion Wicks | WR | 83 | 203 | 155.08 | unknown |

### QB12
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Lamar Jackson | QB | 1 | 14 | 27.95 | BAL |
| enters | Kyler Murray | QB | 4 | 21 | 21.62 | unknown |
| enters | Baker Mayfield | QB | 5 | 19 | 21.31 | TB |
| enters | Jared Goff | QB | 6 | 17 | 20.84 | DET |
| enters | Geno Smith | QB | 7 | 28 | 19.92 | NYJ |
| enters | Sam Darnold | QB | 11 | 23 | 17.59 | SEA |
| enters | Kirk Cousins | QB | 12 | missing | 17.24 | LV |
| exits | Brock Purdy | QB | 107 | 5 | -25.12 | unknown |
| exits | Jordan Love | QB | 114 | 8 | -50.20 | unknown |
| exits | Caleb Williams | QB | 122 | 10 | -96.69 | unknown |
| exits | Bo Nix | QB | 123 | 11 | -108.20 | unknown |
| exits | Trevor Lawrence | QB | 124 | 6 | -110.31 | unknown |
| exits | Drake Maye | QB | 127 | 2 | -129.35 | unknown |
| exits | Jalen Hurts | QB | 128 | 4 | -146.43 | unknown |

### RB12
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Kenneth Gainwell | RB | 1 | 27 | 111.55 | unknown |
| enters | Tyler Badie | RB | 2 | missing | 88.39 | unknown |
| enters | Jerome Ford | RB | 3 | 69 | 70.33 | unknown |
| enters | Tyjae Spears | RB | 4 | 39 | 60.09 | unknown |
| enters | Brashard Smith | RB | 5 | 73 | 46.64 | unknown |
| enters | Dylan Sampson | RB | 6 | 58 | 32.56 | unknown |
| enters | Isaiah Davis | RB | 7 | 67 | 27.67 | unknown |
| enters | Rasheen Ali | RB | 8 | missing | 23.71 | unknown |
| enters | Trey Benson | RB | 10 | 45 | 20.42 | unknown |
| enters | Alvin Kamara | RB | 11 | 33 | 20.23 | NO |
| enters | Derrick Henry | RB | 12 | 18 | 19.34 | BAL |
| exits | Christian McCaffrey | RB | 13 | 1 | 17.25 | SF |
| exits | Josh Jacobs | RB | 14 | 11 | 17.13 | unknown |
| exits | Jahmyr Gibbs | RB | 162 | 3 | -53.46 | unknown |
| exits | Chase Brown | RB | 164 | 9 | -61.67 | unknown |
| exits | De'Von Achane | RB | 169 | 5 | -76.93 | unknown |
| exits | Bijan Robinson | RB | 174 | 2 | -93.04 | unknown |
| exits | Javonte Williams | RB | 195 | 10 | -212.02 | unknown |
| exits | Travis Etienne | RB | 198 | 12 | -224.99 | unknown |
| exits | Kyren Williams | RB | 199 | 7 | -225.34 | unknown |
| exits | Jonathan Taylor | RB | 201 | 4 | -307.48 | unknown |
| exits | James Cook | RB | 202 | 6 | -340.08 | unknown |

### RB24
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Kenneth Gainwell | RB | 1 | 27 | 111.55 | unknown |
| enters | Tyler Badie | RB | 2 | missing | 88.39 | unknown |
| enters | Jerome Ford | RB | 3 | 69 | 70.33 | unknown |
| enters | Tyjae Spears | RB | 4 | 39 | 60.09 | unknown |
| enters | Brashard Smith | RB | 5 | 73 | 46.64 | unknown |
| enters | Dylan Sampson | RB | 6 | 58 | 32.56 | unknown |
| enters | Isaiah Davis | RB | 7 | 67 | 27.67 | unknown |
| enters | Rasheen Ali | RB | 8 | missing | 23.71 | unknown |
| enters | Trey Benson | RB | 10 | 45 | 20.42 | unknown |
| enters | Alvin Kamara | RB | 11 | 33 | 20.23 | NO |
| enters | James Conner | RB | 15 | 28 | 16.35 | ARI |
| enters | Aaron Jones | RB | 16 | 25 | 15.74 | MIN |
| enters | Tony Pollard | RB | 17 | 32 | 15.72 | unknown |
| enters | David Montgomery | RB | 18 | 35 | 15.59 | unknown |
| enters | Will Shipley | RB | 19 | missing | 14.64 | unknown |
| enters | Chris Brooks | RB | 20 | missing | 12.99 | unknown |
| enters | Michael Carter | RB | 21 | 55 | 12.56 | unknown |
| enters | Justice Hill | RB | 22 | 53 | 11.55 | unknown |
| enters | Devin Singletary | RB | 23 | 56 | 11.38 | unknown |
| enters | Samaje Perine | RB | 24 | 51 | 10.14 | CIN |
| exits | Cam Skattebo | RB | 152 | 19 | -34.72 | unknown |
| exits | Jahmyr Gibbs | RB | 162 | 3 | -53.46 | unknown |
| exits | Omarion Hampton | RB | 163 | 13 | -58.23 | unknown |
| exits | Chase Brown | RB | 164 | 9 | -61.67 | unknown |
| exits | De'Von Achane | RB | 169 | 5 | -76.93 | unknown |
| exits | Bijan Robinson | RB | 174 | 2 | -93.04 | unknown |
| exits | TreVeyon Henderson | RB | 178 | 23 | -133.32 | unknown |
| exits | Bucky Irving | RB | 180 | 20 | -143.12 | unknown |
| exits | Jaylen Warren | RB | 185 | 17 | -169.36 | unknown |
| exits | Ashton Jeanty | RB | 186 | 16 | -171.07 | unknown |
| exits | D'Andre Swift | RB | 188 | 15 | -177.72 | unknown |
| exits | J.K. Dobbins | RB | 189 | 24 | -179.19 | unknown |
| exits | Rico Dowdle | RB | 193 | 21 | -196.28 | unknown |
| exits | Breece Hall | RB | 194 | 14 | -211.72 | unknown |
| exits | Javonte Williams | RB | 195 | 10 | -212.02 | unknown |
| exits | Travis Etienne | RB | 198 | 12 | -224.99 | unknown |
| exits | Kyren Williams | RB | 199 | 7 | -225.34 | unknown |
| exits | Quinshon Judkins | RB | 200 | 22 | -234.36 | unknown |
| exits | Jonathan Taylor | RB | 201 | 4 | -307.48 | unknown |
| exits | James Cook | RB | 202 | 6 | -340.08 | unknown |

### RB36
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Tyler Badie | RB | 2 | missing | 88.39 | unknown |
| enters | Jerome Ford | RB | 3 | 69 | 70.33 | unknown |
| enters | Tyjae Spears | RB | 4 | 39 | 60.09 | unknown |
| enters | Brashard Smith | RB | 5 | 73 | 46.64 | unknown |
| enters | Dylan Sampson | RB | 6 | 58 | 32.56 | unknown |
| enters | Isaiah Davis | RB | 7 | 67 | 27.67 | unknown |
| enters | Rasheen Ali | RB | 8 | missing | 23.71 | unknown |
| enters | Trey Benson | RB | 10 | 45 | 20.42 | unknown |
| enters | Will Shipley | RB | 19 | missing | 14.64 | unknown |
| enters | Chris Brooks | RB | 20 | missing | 12.99 | unknown |
| enters | Michael Carter | RB | 21 | 55 | 12.56 | unknown |
| enters | Justice Hill | RB | 22 | 53 | 11.55 | unknown |
| enters | Devin Singletary | RB | 23 | 56 | 11.38 | unknown |
| enters | Samaje Perine | RB | 24 | 51 | 10.14 | CIN |
| enters | Ameer Abdullah | RB | 25 | 80 | 9.89 | JAX |
| enters | Ty Johnson | RB | 26 | 50 | 9.71 | unknown |
| enters | Phil Mafah | RB | 27 | 60 | 9.27 | unknown |
| enters | Jeremy McNichols | RB | 28 | 63 | 7.20 | WAS |
| enters | Travis Homer | RB | 29 | missing | 6.51 | unknown |
| enters | Zavier Scott | RB | 30 | 78 | 2.81 | unknown |
| enters | Adam Randall | RB | 31 | missing | 1.82 | unknown |
| enters | Ahmani Marshall | RB | 32 | missing | 1.82 | unknown |
| enters | Anderson Castle | RB | 33 | missing | 1.82 | unknown |
| enters | Andrew Beck | RB | 34 | missing | 1.82 | NYJ |
| enters | Anthony Hankerson | RB | 35 | missing | 1.82 | unknown |
| enters | Anthony Tyus III | RB | 36 | missing | 1.82 | unknown |
| exits | Cam Skattebo | RB | 152 | 19 | -34.72 | unknown |
| exits | Rachaad White | RB | 159 | 34 | -50.24 | unknown |
| exits | Jahmyr Gibbs | RB | 162 | 3 | -53.46 | unknown |
| exits | Omarion Hampton | RB | 163 | 13 | -58.23 | unknown |
| exits | Chase Brown | RB | 164 | 9 | -61.67 | unknown |
| exits | Rhamondre Stevenson | RB | 166 | 26 | -67.49 | unknown |
| exits | De'Von Achane | RB | 169 | 5 | -76.93 | unknown |
| exits | Bijan Robinson | RB | 174 | 2 | -93.04 | unknown |
| exits | Tyrone Tracy Jr. | RB | 177 | 30 | -108.03 | unknown |
| exits | TreVeyon Henderson | RB | 178 | 23 | -133.32 | unknown |
| exits | Bucky Irving | RB | 180 | 20 | -143.12 | unknown |
| exits | Jaylen Warren | RB | 185 | 17 | -169.36 | unknown |
| exits | Ashton Jeanty | RB | 186 | 16 | -171.07 | unknown |
| exits | D'Andre Swift | RB | 188 | 15 | -177.72 | unknown |

### WR12
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | George Pickens | WR | 7 | 13 | 470.21 | unknown |
| enters | Wan'Dale Robinson | WR | 8 | 17 | 469.94 | unknown |
| enters | Michael Wilson | WR | 9 | 30 | 425.42 | unknown |
| enters | Emeka Egbuka | WR | 10 | 26 | 425.40 | unknown |
| enters | Tetairoa McMillan | WR | 11 | 18 | 417.94 | unknown |
| enters | Nico Collins | WR | 12 | 14 | 408.78 | unknown |
| exits | CeeDee Lamb | WR | 13 | 11 | 401.01 | unknown |
| exits | Zay Flowers | WR | 14 | 12 | 390.84 | unknown |
| exits | Drake London | WR | 15 | 5 | 389.27 | unknown |
| exits | Rashee Rice | WR | 36 | 7 | 271.54 | unknown |
| exits | Garrett Wilson | WR | 43 | 6 | 218.83 | unknown |
| exits | A.J. Brown | WR | 126 | 9 | 15.69 | unknown |

### WR24
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Michael Wilson | WR | 9 | 30 | 425.42 | unknown |
| enters | Emeka Egbuka | WR | 10 | 26 | 425.40 | unknown |
| enters | Michael Pittman | WR | 17 | 50 | 368.66 | unknown |
| enters | Ladd McConkey | WR | 18 | 34 | 358.45 | unknown |
| enters | Jerry Jeudy | WR | 19 | 42 | 353.55 | unknown |
| enters | Troy Franklin | WR | 20 | 41 | 342.53 | unknown |
| enters | Jameson Williams | WR | 22 | 28 | 341.35 | unknown |
| enters | Khalil Shakir | WR | 24 | 45 | 316.95 | unknown |
| exits | Rome Odunze | WR | 25 | 19 | 314.29 | unknown |
| exits | Rashee Rice | WR | 36 | 7 | 271.54 | unknown |
| exits | Garrett Wilson | WR | 43 | 6 | 218.83 | unknown |
| exits | Malik Nabers | WR | 67 | 16 | 138.51 | unknown |
| exits | Davante Adams | WR | 125 | 15 | 17.01 | LAR |
| exits | A.J. Brown | WR | 126 | 9 | 15.69 | unknown |
| exits | Terry McLaurin | WR | 134 | 21 | 13.13 | unknown |
| exits | Courtland Sutton | WR | 136 | 24 | 13.04 | DEN |

### WR36
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Michael Pittman | WR | 17 | 50 | 368.66 | unknown |
| enters | Jerry Jeudy | WR | 19 | 42 | 353.55 | unknown |
| enters | Troy Franklin | WR | 20 | 41 | 342.53 | unknown |
| enters | Khalil Shakir | WR | 24 | 45 | 316.95 | unknown |
| enters | Parker Washington | WR | 26 | 39 | 311.82 | unknown |
| enters | Elic Ayomanor | WR | 28 | 43 | 300.73 | unknown |
| enters | Brian Thomas Jr. | WR | 29 | 48 | 300.60 | unknown |
| enters | Tre Tucker | WR | 30 | 38 | 296.98 | unknown |
| enters | Romeo Doubs | WR | 32 | 37 | 293.45 | unknown |
| enters | Rashid Shaheed | WR | 33 | 59 | 292.71 | unknown |
| enters | Josh Downs | WR | 34 | 58 | 292.20 | unknown |
| exits | Jordan Addison | WR | 37 | 33 | 271.47 | unknown |
| exits | Garrett Wilson | WR | 43 | 6 | 218.83 | unknown |
| exits | Christian Watson | WR | 46 | 32 | 198.15 | unknown |
| exits | Malik Nabers | WR | 67 | 16 | 138.51 | unknown |
| exits | Davante Adams | WR | 125 | 15 | 17.01 | LAR |
| exits | A.J. Brown | WR | 126 | 9 | 15.69 | unknown |
| exits | Mike Evans | WR | 130 | 29 | 14.54 | SF |
| exits | Terry McLaurin | WR | 134 | 21 | 13.13 | unknown |
| exits | Courtland Sutton | WR | 136 | 24 | 13.04 | DEN |
| exits | DK Metcalf | WR | 137 | 35 | 12.83 | unknown |
| exits | Jakobi Meyers | WR | 139 | 27 | 12.35 | unknown |

### TE6
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Kyle Pitts | TE | 2 | 7 | 399.33 | unknown |
| enters | Tyler Warren | TE | 3 | 9 | 369.35 | unknown |
| enters | Juwan Johnson | TE | 4 | 13 | 343.96 | unknown |
| enters | Harold Fannin Jr. | TE | 5 | 16 | 342.82 | unknown |
| enters | Jake Ferguson | TE | 6 | 15 | 340.99 | unknown |
| exits | Brock Bowers | TE | 7 | 2 | 297.32 | unknown |
| exits | Sam LaPorta | TE | 19 | 5 | 180.22 | unknown |
| exits | Tucker Kraft | TE | 22 | 4 | 164.89 | unknown |
| exits | George Kittle | TE | 70 | 3 | 13.09 | SF |
| exits | Dallas Goedert | TE | 77 | 6 | 9.43 | PHI |

### TE12
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Juwan Johnson | TE | 4 | 13 | 343.96 | unknown |
| enters | Harold Fannin Jr. | TE | 5 | 16 | 342.82 | unknown |
| enters | Jake Ferguson | TE | 6 | 15 | 340.99 | unknown |
| enters | Colston Loveland | TE | 8 | 14 | 279.35 | unknown |
| enters | Cade Otton | TE | 9 | 20 | 273.75 | unknown |
| enters | Chig Okonkwo | TE | 10 | 32 | 258.19 | unknown |
| enters | Theo Johnson | TE | 11 | 21 | 252.77 | unknown |
| enters | Oronde Gadsden II | TE | 12 | 23 | 234.97 | unknown |
| exits | Sam LaPorta | TE | 19 | 5 | 180.22 | unknown |
| exits | Dalton Kincaid | TE | 20 | 10 | 172.52 | unknown |
| exits | Tucker Kraft | TE | 22 | 4 | 164.89 | unknown |
| exits | Travis Kelce | TE | 69 | 8 | 13.20 | KC |
| exits | George Kittle | TE | 70 | 3 | 13.09 | SF |
| exits | Dallas Goedert | TE | 77 | 6 | 9.43 | PHI |
| exits | Dalton Schultz | TE | 80 | 12 | 8.25 | HOU |
| exits | Hunter Henry | TE | 83 | 11 | 7.83 | NE |

### TE18
| Direction | Player | Pos | Pred rank | Current rank | Score | Sleeper team |
| --- | --- | --- | --- | --- | --- | --- |
| enters | Cade Otton | TE | 9 | 20 | 273.75 | unknown |
| enters | Chig Okonkwo | TE | 10 | 32 | 258.19 | unknown |
| enters | Theo Johnson | TE | 11 | 21 | 252.77 | unknown |
| enters | Oronde Gadsden II | TE | 12 | 23 | 234.97 | unknown |
| enters | Mason Taylor | TE | 13 | 22 | 222.71 | unknown |
| enters | AJ Barner | TE | 14 | 24 | 216.76 | unknown |
| enters | Colby Parkinson | TE | 16 | 29 | 190.80 | unknown |
| enters | Pat Freiermuth | TE | 17 | 30 | 183.67 | unknown |
| enters | Gunnar Helm | TE | 18 | 41 | 182.62 | unknown |
| exits | Sam LaPorta | TE | 19 | 5 | 180.22 | unknown |
| exits | Dalton Kincaid | TE | 20 | 10 | 172.52 | unknown |
| exits | Tucker Kraft | TE | 22 | 4 | 164.89 | unknown |
| exits | Travis Kelce | TE | 69 | 8 | 13.20 | KC |
| exits | George Kittle | TE | 70 | 3 | 13.09 | SF |
| exits | Mark Andrews | TE | 71 | 18 | 11.21 | BAL |
| exits | Dallas Goedert | TE | 77 | 6 | 9.43 | PHI |
| exits | Dalton Schultz | TE | 80 | 12 | 8.25 | HOU |
| exits | Hunter Henry | TE | 83 | 11 | 7.83 | NE |

