# Live 2026 Ranking Review Boards

Review version: `phase32_32_live_2026_review_20260706`

Scope: review-only 2026 BQML boards for Standard, Half PPR, PPR, and GNG Keeper. The input is CTE-only and outcome-free. No live ranking table was written, no champion was activated, no Gemini call was made, and `analytics_pigskin_rankings_candidates` was not overwritten.

Scoring profile display order: Standard, Half PPR, PPR, then GNG Keeper. Do not choose one global winner averaged across scoring systems.

TE owner-review output is capped at TE35. Live ranking tables still have TE60 per scoring profile and were not changed.

Future owner-approved live-ranking depth change: reduce TE from 60 to 35.

## Profile Decision Summary
| Scoring profile | Board status | Best review-only challenger | Decision |
|---|---|---|---|
| standard | ready with warnings | ranking_bqml_enriched_logistic_elite_v1 | Current Pigskin holds. Logistic is bounded owner-review challenger. Linear points is context only. |
| half_ppr | ready with warnings | ranking_bqml_enriched_logistic_elite_v1 | Current Pigskin holds. Logistic is bounded owner-review challenger. Linear points is context only. |
| ppr | ready with warnings | ranking_bqml_enriched_logistic_elite_v1 | Current Pigskin holds. Logistic is bounded owner-review challenger. Linear points is context only. |
| gng_keeper | ready with warnings | ranking_bqml_enriched_logistic_elite_v1 | Current Pigskin holds. Logistic is bounded owner-review challenger. Linear points is context only. |

## Candidate Coverage
| Profile | Position | Candidates | Rank range | Missing ID | Missing score | Profile points missing | Grade missing |
|---|---|---|---|---|---|---|---|
| standard | QB | 128 | 1-128 | 0 | 0 | 43.0% | 43.0% |
| standard | RB | 202 | 1-202 | 0 | 0 | 40.6% | 40.6% |
| standard | TE | 213 | 1-213 | 0 | 0 | 42.7% | 42.7% |
| standard | WR | 393 | 1-393 | 0 | 0 | 49.1% | 49.1% |
| half_ppr | QB | 128 | 1-128 | 0 | 0 | 43.0% | 43.0% |
| half_ppr | RB | 202 | 1-202 | 0 | 0 | 40.6% | 40.6% |
| half_ppr | TE | 213 | 1-213 | 0 | 0 | 42.7% | 42.7% |
| half_ppr | WR | 393 | 1-393 | 0 | 0 | 49.1% | 49.1% |
| ppr | QB | 128 | 1-128 | 0 | 0 | 43.0% | 43.0% |
| ppr | RB | 202 | 1-202 | 0 | 0 | 40.6% | 40.6% |
| ppr | TE | 213 | 1-213 | 0 | 0 | 42.7% | 42.7% |
| ppr | WR | 393 | 1-393 | 0 | 0 | 49.1% | 49.1% |
| gng_keeper | QB | 128 | 1-128 | 0 | 0 | 43.0% | 43.0% |
| gng_keeper | RB | 202 | 1-202 | 0 | 0 | 40.6% | 40.6% |
| gng_keeper | TE | 213 | 1-213 | 0 | 0 | 42.7% | 42.7% |
| gng_keeper | WR | 393 | 1-393 | 0 | 0 | 49.1% | 49.1% |

## Model Summary
| Profile | Model | Predictions | Min | Max | Avg | Missing % | QBs in top 50 |
|---|---|---|---|---|---|---|---|
| standard | enriched_logistic | 936 | 4.13 | 99.79 | 18.19 | 69.0% | 7 |
| standard | enriched_linear_points | 936 | -23.10 | 849.07 | 67.54 | 69.0% | 0 |
| half_ppr | enriched_logistic | 936 | 4.11 | 99.79 | 18.27 | 69.0% | 6 |
| half_ppr | enriched_linear_points | 936 | -22.90 | 852.23 | 68.19 | 69.0% | 0 |
| ppr | enriched_logistic | 936 | 4.07 | 99.80 | 18.44 | 68.3% | 6 |
| ppr | enriched_linear_points | 936 | -22.81 | 855.78 | 68.86 | 68.3% | 0 |
| gng_keeper | enriched_logistic | 936 | 4.18 | 99.77 | 18.04 | 69.0% | 6 |
| gng_keeper | enriched_linear_points | 936 | -26.80 | 845.95 | 66.35 | 69.0% | 0 |

# Standard Review Boards

## Current Pigskin Top 50 Overall
| Rank | Player | Pos | Team | Score | Pos rank |
|---|---|---|---|---|---|
| 1 | Jaxon Smith-Njigba | WR | SEA | 99.50 | 1 |
| 2 | Puka Nacua | WR | LAR | 98.80 | 2 |
| 3 | Christian McCaffrey | RB | SF | 98.50 | 1 |
| 4 | Josh Allen | QB | BUF | 98.50 | 1 |
| 5 | Trey McBride | TE | ARI | 98.00 | 1 |
| 6 | Amon-Ra St. Brown | WR | DET | 98.00 | 3 |
| 7 | Ja'Marr Chase | WR | CIN | 97.50 | 4 |
| 8 | Drake London | WR | ATL | 96.20 | 5 |
| 9 | Drake Maye | QB | NE | 96.00 | 2 |
| 10 | Bijan Robinson | RB | ATL | 95.00 | 2 |
| 11 | Brock Bowers | TE | LV | 95.00 | 2 |
| 12 | Patrick Mahomes | QB | KC | 95.00 | 3 |
| 13 | Chris Olave | WR | NO | 95.00 | 6 |
| 14 | A.J. Brown | WR | NE | 94.50 | 7 |
| 15 | Rashee Rice | WR | KC | 93.80 | 8 |
| 16 | Jahmyr Gibbs | RB | DET | 93.50 | 3 |
| 17 | Justin Jefferson | WR | MIN | 93.00 | 9 |
| 18 | Garrett Wilson | WR | NYJ | 92.50 | 10 |
| 19 | George Kittle | TE | SF | 92.00 | 3 |
| 20 | Jonathan Taylor | RB | IND | 92.00 | 4 |
| 21 | George Pickens | WR | DAL | 91.80 | 11 |
| 22 | Matthew Stafford | QB | LAR | 91.50 | 4 |
| 23 | De'Von Achane | RB | MIA | 91.00 | 5 |
| 24 | Zay Flowers | WR | BAL | 91.00 | 12 |
| 25 | Sam LaPorta | TE | DET | 90.00 | 4 |
| 26 | Jordan Love | QB | GB | 90.00 | 5 |
| 27 | Davante Adams | WR | LAR | 89.50 | 13 |
| 28 | Dak Prescott | QB | DAL | 89.00 | 6 |
| 29 | CeeDee Lamb | WR | DAL | 88.80 | 14 |
| 30 | Kyren Williams | RB | LAR | 88.50 | 6 |
| 31 | Tucker Kraft | TE | GB | 88.00 | 5 |
| 32 | Brock Purdy | QB | SF | 88.00 | 7 |
| 33 | Nico Collins | WR | HOU | 88.00 | 15 |
| 34 | Jalen Hurts | QB | PHI | 87.50 | 8 |
| 35 | Tetairoa McMillan | WR | CAR | 87.20 | 16 |
| 36 | James Cook | RB | BUF | 87.00 | 7 |
| 37 | Wan'Dale Robinson | WR | TEN | 86.50 | 17 |
| 38 | Kyle Pitts | TE | ATL | 86.00 | 6 |
| 39 | Trevor Lawrence | QB | JAX | 86.00 | 9 |
| 40 | Malik Nabers | WR | NYG | 85.80 | 18 |
| 41 | Chase Brown | RB | CIN | 85.50 | 8 |
| 42 | Dallas Goedert | TE | PHI | 85.00 | 7 |
| 43 | Daniel Jones | QB | IND | 85.00 | 10 |
| 44 | Rome Odunze | WR | CHI | 85.00 | 19 |
| 45 | Javonte Williams | RB | DAL | 84.50 | 9 |
| 46 | DeVonta Smith | WR | PHI | 84.20 | 20 |
| 47 | Tyler Warren | TE | IND | 84.00 | 8 |
| 48 | Bo Nix | QB | DEN | 84.00 | 11 |
| 49 | Saquon Barkley | RB | PHI | 83.50 | 10 |
| 50 | Terry McLaurin | WR | WAS | 83.50 | 21 |

## BQML Logistic Top 50 Overall
| Logistic rank | Player | Pos | Team | Score | Current rank | Delta | Missing % |
|---|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey | RB | SF | 99.79 | 3 | +2 | 17.2% |
| 2 | Jonathan Taylor | RB | IND | 99.53 | 20 | +18 | 24.1% |
| 3 | Bijan Robinson | RB | ATL | 99.52 | 10 | +7 | 34.5% |
| 4 | Saquon Barkley | RB | PHI | 99.40 | 49 | +45 | 19.5% |
| 5 | Kyren Williams | RB | LAR | 99.30 | 30 | +25 | 24.1% |
| 6 | Derrick Henry | RB | BAL | 99.27 | 91 | +85 | 17.2% |
| 7 | Jahmyr Gibbs | RB | DET | 99.16 | 16 | +9 | 34.5% |
| 8 | James Cook | RB | BUF | 99.07 | 36 | +28 | 24.1% |
| 9 | Travis Etienne | RB | NO | 98.94 | 68 | +59 | 24.1% |
| 10 | De'Von Achane | RB | MIA | 98.82 | 23 | +13 | 34.5% |
| 11 | Breece Hall | RB | NYJ | 98.55 | 74 | +63 | 24.1% |
| 12 | Josh Jacobs | RB | GB | 98.13 | 63 | +51 | 19.5% |
| 13 | Javonte Williams | RB | DAL | 97.60 | 45 | +32 | 24.1% |
| 14 | Tony Pollard | RB | TEN | 97.25 | 116 | +102 | 19.5% |
| 15 | D'Andre Swift | RB | CHI | 96.72 | 69 | +54 | 21.8% |
| 16 | Kenneth Walker III | RB | KC | 96.38 | 109 | +93 | 24.1% |
| 17 | Jaylen Warren | RB | PIT | 94.53 | 87 | +70 | 24.1% |
| 18 | Chase Brown | RB | CIN | 93.62 | 41 | +23 | 34.5% |
| 19 | Rico Dowdle | RB | PIT | 93.51 | 99 | +80 | 27.6% |
| 20 | Alvin Kamara | RB | NO | 92.87 | 141 | +121 | 19.5% |
| 21 | David Montgomery | RB | HOU | 91.33 | 166 | +145 | 17.2% |
| 22 | Josh Allen | QB | BUF | 91.14 | 4 | -18 | 23.0% |
| 23 | Rachaad White | RB | WAS | 91.00 | 170 | +147 | 24.1% |
| 24 | Jalen Hurts | QB | PHI | 90.80 | 34 | +10 | 23.0% |
| 25 | Puka Nacua | WR | LAR | 90.35 | 2 | -23 | 34.5% |
| 26 | Aaron Jones | RB | MIN | 90.24 | 112 | +86 | 19.5% |
| 27 | Ja'Marr Chase | WR | CIN | 89.99 | 7 | -20 | 21.8% |
| 28 | Amon-Ra St. Brown | WR | DET | 89.26 | 6 | -22 | 24.1% |
| 29 | Rhamondre Stevenson | RB | NE | 88.25 | 104 | +75 | 24.1% |
| 30 | Isiah Pacheco | RB | DET | 88.04 | 174 | +144 | 24.1% |
| 31 | Zach Charbonnet | RB | SEA | 87.16 | 128 | +97 | 34.5% |
| 32 | Justin Jefferson | WR | MIN | 86.73 | 17 | -15 | 21.8% |
| 33 | Ashton Jeanty | RB | LV | 86.34 | 59 | +26 | 85.1% |
| 34 | CeeDee Lamb | WR | DAL | 84.75 | 29 | -5 | 21.8% |
| 35 | J.K. Dobbins | RB | DEN | 82.58 | 102 | +67 | 24.1% |
| 36 | Lamar Jackson | QB | BAL | 82.23 | 76 | +40 | 18.4% |
| 37 | Chuba Hubbard | RB | CAR | 81.27 | 177 | +140 | 24.1% |
| 38 | Justin Fields | QB | KC | 79.29 | 263 | +225 | 27.6% |
| 39 | Trey McBride | TE | ARI | 79.21 | 5 | -34 | 28.7% |
| 40 | Kenneth Gainwell | RB | TB | 78.89 | 138 | +98 | 21.8% |
| 41 | Davante Adams | WR | LAR | 78.83 | 27 | -14 | 19.5% |
| 42 | Trevor Lawrence | QB | JAX | 75.17 | 39 | -3 | 27.6% |
| 43 | Chris Olave | WR | NO | 75.00 | 13 | -30 | 28.7% |
| 44 | Tyler Allgeier | RB | ARI | 74.84 | 198 | +154 | 24.1% |
| 45 | A.J. Brown | WR | NE | 74.84 | 14 | -31 | 24.1% |
| 46 | Justin Herbert | QB | LAC | 74.17 | 72 | +26 | 23.0% |
| 47 | Zay Flowers | WR | BAL | 73.50 | 24 | -23 | 34.5% |
| 48 | George Pickens | WR | DAL | 73.29 | 21 | -27 | 24.1% |
| 49 | Travis Kelce | TE | KC | 72.60 | 51 | +2 | 19.5% |
| 50 | Patrick Mahomes | QB | KC | 72.21 | 12 | -38 | 18.4% |

## BQML Linear Points Top 50 Overall
| Linear rank | Player | Pos | Team | Score | Current rank | Delta | Missing % |
|---|---|---|---|---|---|---|---|
| 1 | Ja'Marr Chase | WR | CIN | 849.07 | 7 | +6 | 21.8% |
| 2 | Amon-Ra St. Brown | WR | DET | 793.56 | 6 | +4 | 24.1% |
| 3 | Trey McBride | TE | ARI | 784.28 | 5 | +2 | 28.7% |
| 4 | Puka Nacua | WR | LAR | 762.71 | 2 | -2 | 34.5% |
| 5 | Jaxon Smith-Njigba | WR | SEA | 758.62 | 1 | -4 | 39.1% |
| 6 | Chris Olave | WR | NO | 720.54 | 13 | +7 | 28.7% |
| 7 | Justin Jefferson | WR | MIN | 649.14 | 17 | +10 | 21.8% |
| 8 | Wan'Dale Robinson | WR | TEN | 648.67 | 37 | +29 | 24.1% |
| 9 | George Pickens | WR | DAL | 636.86 | 21 | +12 | 24.1% |
| 10 | Michael Wilson | WR | ARI | 583.74 | 77 | +67 | 39.1% |
| 11 | Emeka Egbuka | WR | TB | 579.22 | 60 | +49 | 85.1% |
| 12 | Courtland Sutton | WR | DEN | 573.64 | 57 | +45 | 17.2% |
| 13 | A.J. Brown | WR | NE | 562.83 | 14 | +1 | 24.1% |
| 14 | Tetairoa McMillan | WR | CAR | 561.98 | 35 | +21 | 85.1% |
| 15 | Nico Collins | WR | HOU | 560.74 | 33 | +18 | 24.1% |
| 16 | Zay Flowers | WR | BAL | 546.17 | 24 | +8 | 34.5% |
| 17 | Kyle Pitts | TE | ATL | 545.24 | 38 | +21 | 24.1% |
| 18 | CeeDee Lamb | WR | DAL | 543.66 | 29 | +11 | 21.8% |
| 19 | Davante Adams | WR | LAR | 530.89 | 27 | +8 | 19.5% |
| 20 | Drake London | WR | ATL | 528.59 | 8 | -12 | 26.4% |
| 21 | DeVonta Smith | WR | PHI | 522.70 | 46 | +25 | 28.7% |
| 22 | Tyler Warren | TE | IND | 508.42 | 47 | +25 | 85.1% |
| 23 | Jakobi Meyers | WR | JAX | 505.95 | 65 | +42 | 17.2% |
| 24 | Michael Pittman | WR | PIT | 503.21 | 139 | +115 | 24.1% |
| 25 | Travis Kelce | TE | KC | 492.50 | 51 | +26 | 19.5% |
| 26 | Jerry Jeudy | WR | CLE | 488.23 | 108 | +82 | 24.1% |
| 27 | Dalton Schultz | TE | HOU | 485.14 | 62 | +35 | 24.1% |
| 28 | Ladd McConkey | WR | LAC | 483.65 | 90 | +62 | 85.1% |
| 29 | Jameson Williams | WR | DET | 479.32 | 64 | +35 | 24.1% |
| 30 | Harold Fannin Jr. | TE | CLE | 479.27 | 80 | +50 | 85.1% |
| 31 | Christian McCaffrey | RB | SF | 475.40 | 3 | -28 | 17.2% |
| 32 | Juwan Johnson | TE | NO | 471.67 | 66 | +34 | 28.7% |
| 33 | Jake Ferguson | TE | DAL | 470.80 | 75 | +42 | 28.7% |
| 34 | Troy Franklin | WR | DEN | 470.62 | 105 | +71 | 85.1% |
| 35 | Jaylen Waddle | WR | DEN | 464.62 | 53 | +18 | 24.1% |
| 36 | Tee Higgins | WR | CIN | 456.55 | 56 | +20 | 28.7% |
| 37 | DK Metcalf | WR | PIT | 454.97 | 86 | +49 | 24.1% |
| 38 | Parker Washington | WR | JAX | 442.66 | 101 | +63 | 39.1% |
| 39 | Khalil Shakir | WR | BUF | 441.17 | 120 | +81 | 24.1% |
| 40 | Tre Tucker | WR | LV | 427.70 | 98 | +58 | 34.5% |
| 41 | Jauan Jennings | WR | MIN | 424.66 | 96 | +55 | 21.8% |
| 42 | Rashid Shaheed | WR | SEA | 420.83 | 157 | +115 | 24.1% |
| 43 | Rome Odunze | WR | CHI | 418.95 | 44 | +1 | 85.1% |
| 44 | Brian Thomas Jr. | WR | JAX | 409.97 | 129 | +85 | 85.1% |
| 45 | Hunter Henry | TE | NE | 404.77 | 58 | +13 | 24.1% |
| 46 | Elic Ayomanor | WR | TEN | 404.68 | 111 | +65 | 85.1% |
| 47 | Josh Downs | WR | IND | 403.43 | 153 | +106 | 39.1% |
| 48 | Brock Bowers | TE | LV | 399.43 | 11 | -37 | 85.1% |
| 49 | Romeo Doubs | WR | NE | 398.19 | 92 | +43 | 21.8% |
| 50 | Quentin Johnston | WR | LAC | 397.80 | 73 | +23 | 34.5% |

## Side-by-Side Top 100 Overall
| Rank | Current | Pos | Logistic | Pos | Score | Linear | Pos | Score |
|---|---|---|---|---|---|---|---|---|
| 1 | Jaxon Smith-Njigba | WR | Christian McCaffrey | RB | 99.79 | Ja'Marr Chase | WR | 849.07 |
| 2 | Puka Nacua | WR | Jonathan Taylor | RB | 99.53 | Amon-Ra St. Brown | WR | 793.56 |
| 3 | Christian McCaffrey | RB | Bijan Robinson | RB | 99.52 | Trey McBride | TE | 784.28 |
| 4 | Josh Allen | QB | Saquon Barkley | RB | 99.40 | Puka Nacua | WR | 762.71 |
| 5 | Trey McBride | TE | Kyren Williams | RB | 99.30 | Jaxon Smith-Njigba | WR | 758.62 |
| 6 | Amon-Ra St. Brown | WR | Derrick Henry | RB | 99.27 | Chris Olave | WR | 720.54 |
| 7 | Ja'Marr Chase | WR | Jahmyr Gibbs | RB | 99.16 | Justin Jefferson | WR | 649.14 |
| 8 | Drake London | WR | James Cook | RB | 99.07 | Wan'Dale Robinson | WR | 648.67 |
| 9 | Drake Maye | QB | Travis Etienne | RB | 98.94 | George Pickens | WR | 636.86 |
| 10 | Bijan Robinson | RB | De'Von Achane | RB | 98.82 | Michael Wilson | WR | 583.74 |
| 11 | Brock Bowers | TE | Breece Hall | RB | 98.55 | Emeka Egbuka | WR | 579.22 |
| 12 | Patrick Mahomes | QB | Josh Jacobs | RB | 98.13 | Courtland Sutton | WR | 573.64 |
| 13 | Chris Olave | WR | Javonte Williams | RB | 97.60 | A.J. Brown | WR | 562.83 |
| 14 | A.J. Brown | WR | Tony Pollard | RB | 97.25 | Tetairoa McMillan | WR | 561.98 |
| 15 | Rashee Rice | WR | D'Andre Swift | RB | 96.72 | Nico Collins | WR | 560.74 |
| 16 | Jahmyr Gibbs | RB | Kenneth Walker III | RB | 96.38 | Zay Flowers | WR | 546.17 |
| 17 | Justin Jefferson | WR | Jaylen Warren | RB | 94.53 | Kyle Pitts | TE | 545.24 |
| 18 | Garrett Wilson | WR | Chase Brown | RB | 93.62 | CeeDee Lamb | WR | 543.66 |
| 19 | George Kittle | TE | Rico Dowdle | RB | 93.51 | Davante Adams | WR | 530.89 |
| 20 | Jonathan Taylor | RB | Alvin Kamara | RB | 92.87 | Drake London | WR | 528.59 |
| 21 | George Pickens | WR | David Montgomery | RB | 91.33 | DeVonta Smith | WR | 522.70 |
| 22 | Matthew Stafford | QB | Josh Allen | QB | 91.14 | Tyler Warren | TE | 508.42 |
| 23 | De'Von Achane | RB | Rachaad White | RB | 91.00 | Jakobi Meyers | WR | 505.95 |
| 24 | Zay Flowers | WR | Jalen Hurts | QB | 90.80 | Michael Pittman | WR | 503.21 |
| 25 | Sam LaPorta | TE | Puka Nacua | WR | 90.35 | Travis Kelce | TE | 492.50 |
| 26 | Jordan Love | QB | Aaron Jones | RB | 90.24 | Jerry Jeudy | WR | 488.23 |
| 27 | Davante Adams | WR | Ja'Marr Chase | WR | 89.99 | Dalton Schultz | TE | 485.14 |
| 28 | Dak Prescott | QB | Amon-Ra St. Brown | WR | 89.26 | Ladd McConkey | WR | 483.65 |
| 29 | CeeDee Lamb | WR | Rhamondre Stevenson | RB | 88.25 | Jameson Williams | WR | 479.32 |
| 30 | Kyren Williams | RB | Isiah Pacheco | RB | 88.04 | Harold Fannin Jr. | TE | 479.27 |
| 31 | Tucker Kraft | TE | Zach Charbonnet | RB | 87.16 | Christian McCaffrey | RB | 475.40 |
| 32 | Brock Purdy | QB | Justin Jefferson | WR | 86.73 | Juwan Johnson | TE | 471.67 |
| 33 | Nico Collins | WR | Ashton Jeanty | RB | 86.34 | Jake Ferguson | TE | 470.80 |
| 34 | Jalen Hurts | QB | CeeDee Lamb | WR | 84.75 | Troy Franklin | WR | 470.62 |
| 35 | Tetairoa McMillan | WR | J.K. Dobbins | RB | 82.58 | Jaylen Waddle | WR | 464.62 |
| 36 | James Cook | RB | Lamar Jackson | QB | 82.23 | Tee Higgins | WR | 456.55 |
| 37 | Wan'Dale Robinson | WR | Chuba Hubbard | RB | 81.27 | DK Metcalf | WR | 454.97 |
| 38 | Kyle Pitts | TE | Justin Fields | QB | 79.29 | Parker Washington | WR | 442.66 |
| 39 | Trevor Lawrence | QB | Trey McBride | TE | 79.21 | Khalil Shakir | WR | 441.17 |
| 40 | Malik Nabers | WR | Kenneth Gainwell | RB | 78.89 | Tre Tucker | WR | 427.70 |
| 41 | Chase Brown | RB | Davante Adams | WR | 78.83 | Jauan Jennings | WR | 424.66 |
| 42 | Dallas Goedert | TE | Trevor Lawrence | QB | 75.17 | Rashid Shaheed | WR | 420.83 |
| 43 | Daniel Jones | QB | Chris Olave | WR | 75.00 | Rome Odunze | WR | 418.95 |
| 44 | Rome Odunze | WR | Tyler Allgeier | RB | 74.84 | Brian Thomas Jr. | WR | 409.97 |
| 45 | Javonte Williams | RB | A.J. Brown | WR | 74.84 | Hunter Henry | TE | 404.77 |
| 46 | DeVonta Smith | WR | Justin Herbert | QB | 74.17 | Elic Ayomanor | WR | 404.68 |
| 47 | Tyler Warren | TE | Zay Flowers | WR | 73.50 | Josh Downs | WR | 403.43 |
| 48 | Bo Nix | QB | George Pickens | WR | 73.29 | Brock Bowers | TE | 399.43 |
| 49 | Saquon Barkley | RB | Travis Kelce | TE | 72.60 | Romeo Doubs | WR | 398.19 |
| 50 | Terry McLaurin | WR | Patrick Mahomes | QB | 72.21 | Quentin Johnston | WR | 397.80 |
| 51 | Travis Kelce | TE | Quinshon Judkins | RB | 72.07 | Alec Pierce | WR | 397.33 |
| 52 | Caleb Williams | QB | Jaxon Smith-Njigba | WR | 72.06 | Dallas Goedert | TE | 382.23 |
| 53 | Jaylen Waddle | WR | Brian Robinson | RB | 71.75 | DJ Moore | WR | 379.64 |
| 54 | Omarion Hampton | RB | Courtland Sutton | WR | 70.10 | Cade Otton | TE | 374.53 |
| 55 | Alec Pierce | WR | Nico Collins | WR | 69.52 | Rashee Rice | WR | 373.35 |
| 56 | Tee Higgins | WR | Jakobi Meyers | WR | 69.35 | Colston Loveland | TE | 371.75 |
| 57 | Courtland Sutton | WR | George Kittle | TE | 68.35 | Jordan Addison | WR | 369.46 |
| 58 | Hunter Henry | TE | Michael Pittman | WR | 67.96 | Bijan Robinson | RB | 368.58 |
| 59 | Ashton Jeanty | RB | Baker Mayfield | QB | 67.57 | Chig Okonkwo | TE | 357.44 |
| 60 | Emeka Egbuka | WR | C.J. Stroud | QB | 67.37 | Kenneth Gainwell | RB | 350.61 |
| 61 | Jared Goff | QB | DJ Moore | WR | 67.22 | Jahmyr Gibbs | RB | 344.40 |
| 62 | Dalton Schultz | TE | Devin Singletary | RB | 67.16 | Evan Engram | TE | 342.42 |
| 63 | Josh Jacobs | RB | Jaylen Waddle | WR | 66.39 | Marquise Brown | WR | 337.27 |
| 64 | Jameson Williams | WR | DeVonta Smith | WR | 66.15 | Theo Johnson | TE | 336.84 |
| 65 | Jakobi Meyers | WR | James Conner | RB | 66.03 | Chase Brown | RB | 334.23 |
| 66 | Juwan Johnson | TE | Tyjae Spears | RB | 65.75 | Darnell Mooney | WR | 333.22 |
| 67 | C.J. Stroud | QB | Jordan Mason | RB | 64.82 | Adonai Mitchell | WR | 332.56 |
| 68 | Travis Etienne | RB | Brock Purdy | QB | 64.81 | George Kittle | TE | 328.30 |
| 69 | D'Andre Swift | RB | Rashee Rice | WR | 64.35 | Xavier Worthy | WR | 328.11 |
| 70 | Mike Evans | WR | Sam LaPorta | TE | 63.23 | Chimere Dike | WR | 327.26 |
| 71 | Colston Loveland | TE | Mike Evans | WR | 62.60 | Cooper Kupp | WR | 319.39 |
| 72 | Justin Herbert | QB | Cooper Kupp | WR | 61.09 | Mark Andrews | TE | 318.92 |
| 73 | Quentin Johnston | WR | DK Metcalf | WR | 60.91 | Oronde Gadsden II | TE | 312.34 |
| 74 | Breece Hall | RB | Drake London | WR | 60.73 | De'Von Achane | RB | 310.74 |
| 75 | Jake Ferguson | TE | Garrett Wilson | WR | 60.65 | Jayden Higgins | WR | 304.67 |
| 76 | Lamar Jackson | QB | Jordan Addison | WR | 60.61 | Mack Hollins | WR | 303.69 |
| 77 | Michael Wilson | WR | Woody Marks | RB | 60.51 | AJ Barner | TE | 303.25 |
| 78 | Bucky Irving | RB | Tee Higgins | WR | 59.72 | T.J. Hockenson | TE | 301.65 |
| 79 | Christian Watson | WR | Daniel Jones | QB | 59.09 | Olamide Zaccheaus | WR | 300.48 |
| 80 | Harold Fannin Jr. | TE | Dak Prescott | QB | 59.03 | Mike Evans | WR | 295.31 |
| 81 | Jayden Daniels | QB | Tank Dell | WR | 58.93 | Darius Slayton | WR | 295.08 |
| 82 | Cam Skattebo | RB | Kyler Murray | QB | 58.00 | Mason Taylor | TE | 294.61 |
| 83 | Jordan Addison | WR | TreVeyon Henderson | RB | 57.89 | Garrett Wilson | WR | 292.15 |
| 84 | Dalton Kincaid | TE | Michael Wilson | WR | 57.89 | Brenton Strange | TE | 288.61 |
| 85 | Baker Mayfield | QB | Wan'Dale Robinson | WR | 57.63 | Xavier Legette | WR | 287.94 |
| 86 | DK Metcalf | WR | Tyrone Tracy Jr. | RB | 57.57 | Terry McLaurin | WR | 286.78 |
| 87 | Jaylen Warren | RB | Jake Ferguson | TE | 57.54 | Malik Washington | WR | 284.35 |
| 88 | Mark Andrews | TE | Kyle Pitts | TE | 57.50 | Andrei Iosivas | WR | 271.24 |
| 89 | Joe Burrow | QB | Bucky Irving | RB | 56.05 | Keon Coleman | WR | 270.18 |
| 90 | Ladd McConkey | WR | Mark Andrews | TE | 54.99 | Christian Watson | WR | 266.19 |
| 91 | Derrick Henry | RB | Jerome Ford | RB | 54.80 | Xavier Hutchinson | WR | 265.99 |
| 92 | Romeo Doubs | WR | Chris Godwin Jr. | WR | 54.40 | Colby Parkinson | TE | 265.31 |
| 93 | T.J. Hockenson | TE | Chris Rodriguez Jr. | RB | 54.18 | Luther Burden III | WR | 262.16 |
| 94 | Sam Darnold | QB | Michael Carter | RB | 53.89 | Calvin Austin III | WR | 259.13 |
| 95 | Quinshon Judkins | RB | Terry McLaurin | WR | 53.69 | Ashton Jeanty | RB | 251.41 |
| 96 | Jauan Jennings | WR | Emanuel Wilson | RB | 53.55 | Jalen Nailor | WR | 249.82 |
| 97 | Jaxson Dart | QB | Jared Goff | QB | 53.32 | Pat Freiermuth | TE | 247.76 |
| 98 | Tre Tucker | WR | Bryce Young | QB | 52.14 | Ryan Flournoy | WR | 247.75 |
| 99 | Rico Dowdle | RB | Dallas Goedert | TE | 52.11 | Ricky Pearsall | WR | 246.14 |
| 100 | Kyler Murray | QB | Romeo Doubs | WR | 51.23 | Kendrick Bourne | WR | 244.61 |

## QB Board Top 45
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Josh Allen | 98.50 | Josh Allen | 91.14 | Jameis Winston | 22.45 |
| 2 | Drake Maye | 96.00 | Jalen Hurts | 90.80 | Aaron Rodgers | 16.70 |
| 3 | Patrick Mahomes | 95.00 | Lamar Jackson | 82.23 | Sam Howell | 16.25 |
| 4 | Matthew Stafford | 91.50 | Justin Fields | 79.29 | Josh Johnson | 15.76 |
| 5 | Jordan Love | 90.00 | Trevor Lawrence | 75.17 | Brock Purdy | 14.77 |
| 6 | Dak Prescott | 89.00 | Justin Herbert | 74.17 | Blake Bortles | 14.54 |
| 7 | Brock Purdy | 88.00 | Patrick Mahomes | 72.21 | Matthew Stafford | 14.49 |
| 8 | Jalen Hurts | 87.50 | Baker Mayfield | 67.57 | Jared Goff | 13.39 |
| 9 | Trevor Lawrence | 86.00 | C.J. Stroud | 67.37 | Deshaun Watson | 13.29 |
| 10 | Daniel Jones | 85.00 | Brock Purdy | 64.81 | Tommy DeVito | 12.56 |
| 11 | Bo Nix | 84.00 | Daniel Jones | 59.09 | Ben Roethlisberger | 12.38 |
| 12 | Caleb Williams | 83.00 | Dak Prescott | 59.03 | Will Levis | 12.30 |
| 13 | Jared Goff | 79.50 | Kyler Murray | 58.00 | Joe Burrow | 11.67 |
| 14 | C.J. Stroud | 78.00 | Jared Goff | 53.32 | Malik Willis | 11.66 |
| 15 | Justin Herbert | 77.00 | Bryce Young | 52.14 | Brandon Allen | 11.22 |
| 16 | Lamar Jackson | 76.00 | Geno Smith | 50.48 | Jake Browning | 11.06 |
| 17 | Jayden Daniels | 75.00 | Joe Burrow | 49.52 | Aidan O'Connell | 11.01 |
| 18 | Baker Mayfield | 74.00 | Matthew Stafford | 49.32 | Davis Mills | 10.66 |
| 19 | Joe Burrow | 73.00 | Jordan Love | 47.36 | Bailey Zappe | 9.45 |
| 20 | Sam Darnold | 72.00 | Tua Tagovailoa | 45.93 | Carson Wentz | 9.36 |
| 21 | Jaxson Dart | 71.00 | Sam Darnold | 45.84 | Joe Flacco | 9.26 |
| 22 | Kyler Murray | 70.00 | Blake Bortles | 44.78 | Tua Tagovailoa | 8.83 |
| 23 | Jacoby Brissett | 68.00 | Marcus Mariota | 44.23 | Kyler Murray | 8.76 |
| 24 | Aaron Rodgers | 66.00 | Anthony Richardson | 42.42 | Kirk Cousins | 8.32 |
| 25 | Malik Willis | 65.00 | Sam Howell | 41.96 | Jordan Love | 7.65 |
| 26 | Tyler Shough | 64.00 | Carson Wentz | 40.57 | Sam Ehlinger | 7.55 |
| 27 | Tua Tagovailoa | 62.00 | Deshaun Watson | 39.12 | Trevor Siemian | 7.34 |
| 28 | Bryce Young | 60.00 | Will Levis | 38.62 | Skylar Thompson | 7.30 |
| 29 | Shedeur Sanders | 58.00 | Joe Flacco | 37.46 | Tyrod Taylor | 6.50 |
| 30 | Cam Ward | 55.00 | Tyler Huntley | 37.44 | Sam Darnold | 6.43 |
| 31 | Geno Smith | 50.00 | Mac Jones | 37.33 | Case Keenum | 6.03 |
| 32 | Fernando Mendoza | 40.00 | Jacoby Brissett | 36.64 | Jacoby Brissett | 4.68 |
| 33 | Mac Jones | 35.00 | Kirk Cousins | 34.04 | Mitchell Trubisky | 4.43 |
| 34 | Jameis Winston | 33.00 | Tyson Bagent | 32.86 | Easton Stick | 4.40 |
| 35 | Tyler Huntley | 30.00 | Aaron Rodgers | 32.62 | Andy Dalton | 3.71 |
| 36 | Carson Wentz | 28.00 | Ben Roethlisberger | 32.00 | Mason Rudolph | 3.56 |
| 37 | Marcus Mariota | 25.00 | Mason Rudolph | 31.06 | Teddy Bridgewater | 3.25 |
| 38 | Justin Fields | 22.00 | Tommy DeVito | 29.99 | Tyler Huntley | 3.18 |
| 39 | Spencer Rattler | 20.00 | Tyrod Taylor | 29.24 | Patrick Mahomes | 3.06 |
| 40 | Davis Mills | 18.00 | Aidan O'Connell | 28.89 | Kyle Allen | 2.52 |
| 41 | J.J. McCarthy | 15.00 | Trey Lance | 28.72 | Drew Lock | 1.79 |
| 42 | Quinn Ewers | 12.00 | Drake Maye | 27.95 | Anthony Richardson | 1.79 |
| 43 | Josh Johnson | 10.00 | Jameis Winston | 27.64 | Spencer Rattler | 1.54 |
| 44 | Jake Browning | 8.00 | Zach Wilson | 25.85 | Quinn Ewers | 1.36 |
| 45 | Joe Flacco | 5.00 | Davis Mills | 25.11 | Mac Jones | 1.26 |

## RB Board Top 80
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey | 98.50 | Christian McCaffrey | 99.79 | Christian McCaffrey | 475.40 |
| 2 | Bijan Robinson | 95.00 | Jonathan Taylor | 99.53 | Bijan Robinson | 368.58 |
| 3 | Jahmyr Gibbs | 93.50 | Bijan Robinson | 99.52 | Kenneth Gainwell | 350.61 |
| 4 | Jonathan Taylor | 92.00 | Saquon Barkley | 99.40 | Jahmyr Gibbs | 344.40 |
| 5 | De'Von Achane | 91.00 | Kyren Williams | 99.30 | Chase Brown | 334.23 |
| 6 | Kyren Williams | 88.50 | Derrick Henry | 99.27 | De'Von Achane | 310.74 |
| 7 | James Cook | 87.00 | Jahmyr Gibbs | 99.16 | Ashton Jeanty | 251.41 |
| 8 | Chase Brown | 85.50 | James Cook | 99.07 | RJ Harvey | 220.57 |
| 9 | Javonte Williams | 84.50 | Travis Etienne | 98.94 | Tyjae Spears | 200.83 |
| 10 | Saquon Barkley | 83.50 | De'Von Achane | 98.82 | Michael Carter | 169.88 |
| 11 | Omarion Hampton | 82.00 | Breece Hall | 98.55 | Tyrone Tracy Jr. | 166.48 |
| 12 | Ashton Jeanty | 80.00 | Josh Jacobs | 98.13 | Dylan Sampson | 159.32 |
| 13 | Josh Jacobs | 79.00 | Javonte Williams | 97.60 | Rico Dowdle | 158.43 |
| 14 | Travis Etienne | 78.00 | Tony Pollard | 97.25 | Rachaad White | 149.02 |
| 15 | D'Andre Swift | 77.50 | D'Andre Swift | 96.72 | Kyren Williams | 145.60 |
| 16 | Breece Hall | 76.50 | Kenneth Walker III | 96.38 | Javonte Williams | 144.22 |
| 17 | Bucky Irving | 75.50 | Jaylen Warren | 94.53 | Brashard Smith | 140.90 |
| 18 | Cam Skattebo | 74.50 | Chase Brown | 93.62 | Travis Etienne | 140.34 |
| 19 | Jaylen Warren | 73.50 | Rico Dowdle | 93.51 | Tyler Badie | 139.45 |
| 20 | Derrick Henry | 72.50 | Alvin Kamara | 92.87 | D'Andre Swift | 138.59 |
| 21 | Quinshon Judkins | 71.50 | David Montgomery | 91.33 | TreVeyon Henderson | 138.18 |
| 22 | Rico Dowdle | 70.50 | Rachaad White | 91.00 | Jaylen Warren | 137.79 |
| 23 | J.K. Dobbins | 69.50 | Aaron Jones | 90.24 | Omarion Hampton | 136.84 |
| 24 | Rhamondre Stevenson | 68.50 | Rhamondre Stevenson | 88.25 | Jerome Ford | 134.62 |
| 25 | Kenneth Walker III | 67.50 | Isiah Pacheco | 88.04 | Ty Johnson | 134.26 |
| 26 | Aaron Jones | 66.50 | Zach Charbonnet | 87.16 | Aaron Jones | 132.32 |
| 27 | Tony Pollard | 65.50 | Ashton Jeanty | 86.34 | Jonathan Taylor | 131.33 |
| 28 | TreVeyon Henderson | 64.50 | J.K. Dobbins | 82.58 | Cam Skattebo | 130.86 |
| 29 | James Conner | 63.50 | Chuba Hubbard | 81.27 | Breece Hall | 130.79 |
| 30 | Zach Charbonnet | 62.50 | Kenneth Gainwell | 78.89 | Jeremy McNichols | 130.07 |
| 31 | Kenneth Gainwell | 60.00 | Tyler Allgeier | 74.84 | Chuba Hubbard | 125.48 |
| 32 | Alvin Kamara | 59.00 | Quinshon Judkins | 72.07 | Rhamondre Stevenson | 122.04 |
| 33 | Tyrone Tracy Jr. | 58.00 | Brian Robinson | 71.75 | Alvin Kamara | 121.90 |
| 34 | Woody Marks | 57.00 | Devin Singletary | 67.16 | Saquon Barkley | 119.19 |
| 35 | RJ Harvey | 56.00 | James Conner | 66.03 | Justice Hill | 116.83 |
| 36 | Trey Benson | 55.00 | Tyjae Spears | 65.75 | Bucky Irving | 116.13 |
| 37 | Kimani Vidal | 54.00 | Jordan Mason | 64.82 | Isaiah Davis | 111.36 |
| 38 | Kyle Monangai | 53.00 | Woody Marks | 60.51 | Josh Jacobs | 107.96 |
| 39 | David Montgomery | 52.00 | TreVeyon Henderson | 57.89 | Woody Marks | 104.59 |
| 40 | Rachaad White | 51.00 | Tyrone Tracy Jr. | 57.57 | Quinshon Judkins | 95.61 |
| 41 | Isiah Pacheco | 50.00 | Bucky Irving | 56.05 | Tony Pollard | 90.09 |
| 42 | Chuba Hubbard | 49.00 | Jerome Ford | 54.80 | Kyle Monangai | 84.83 |
| 43 | Tyjae Spears | 48.00 | Chris Rodriguez Jr. | 54.18 | James Cook | 80.77 |
| 44 | Michael Carter | 47.00 | Michael Carter | 53.89 | Kenneth Walker III | 78.33 |
| 45 | Jacory Croskey-Merritt | 46.00 | Emanuel Wilson | 53.55 | Trey Benson | 76.12 |
| 46 | Jordan Mason | 45.00 | RJ Harvey | 49.76 | Emari Demercado | 73.46 |
| 47 | Jawhar Jordan | 44.00 | Kyle Monangai | 49.32 | Devin Neal | 71.17 |
| 48 | Chris Rodriguez Jr. | 43.00 | Jacory Croskey-Merritt | 46.99 | Ameer Abdullah | 70.16 |
| 49 | Tyler Allgeier | 42.00 | Keaton Mitchell | 46.27 | Isiah Pacheco | 69.74 |
| 50 | Blake Corum | 41.00 | Samaje Perine | 44.18 | Chris Brooks | 68.50 |
| 51 | Raheim Sanders | 40.00 | Kimani Vidal | 43.34 | David Montgomery | 67.09 |
| 52 | Devin Singletary | 39.00 | Omarion Hampton | 41.02 | Samaje Perine | 65.84 |
| 53 | Devin Neal | 38.00 | Emari Demercado | 37.79 | Zavier Scott | 59.90 |
| 54 | Emanuel Wilson | 37.00 | Blake Corum | 36.48 | Kimani Vidal | 56.08 |
| 55 | Samaje Perine | 36.00 | AJ Dillon | 36.12 | Zach Charbonnet | 52.67 |
| 56 | Jaylen Wright | 35.00 | Jeremy McNichols | 34.84 | Will Shipley | 43.88 |
| 57 | Phil Mafah | 34.00 | Ty Johnson | 34.35 | Rasheen Ali | 42.66 |
| 58 | Dylan Sampson | 33.00 | Justice Hill | 33.73 | Emanuel Wilson | 39.21 |
| 59 | Ty Johnson | 32.00 | Sean Tucker | 33.40 | Bhayshul Tuten | 38.13 |
| 60 | Bhayshul Tuten | 31.00 | Cam Skattebo | 33.06 | LeQuint Allen Jr. | 36.71 |
| 61 | Justice Hill | 28.00 | Kendre Miller | 32.44 | Ray Davis | 36.54 |
| 62 | Jaret Patterson | 27.00 | Malik Davis | 32.22 | Devin Singletary | 34.02 |
| 63 | Kendre Miller | 26.00 | Jaleel McLaughlin | 29.40 | Keaton Mitchell | 31.16 |
| 64 | Jeremy McNichols | 25.00 | Ty Chandler | 29.16 | Jawhar Jordan | 27.77 |
| 65 | Braelon Allen | 24.00 | Tank Bigsby | 29.05 | James Conner | 27.52 |
| 66 | Keaton Mitchell | 23.00 | Jaret Patterson | 28.43 | Jordan Mason | 27.49 |
| 67 | Emari Demercado | 22.00 | Le'Veon Bell | 27.49 | Sean Tucker | 23.33 |
| 68 | Jaydon Blue | 21.00 | Elijah McGuire | 26.45 | Jaylen Wright | 20.58 |
| 69 | Isaiah Davis | 20.00 | Ameer Abdullah | 23.25 | Blake Corum | 18.24 |
| 70 | Brian Robinson | 19.00 | Chris Brooks | 22.96 | Ty Chandler | 18.01 |
| 71 | Sean Tucker | 18.00 | Tyler Badie | 22.52 | Raheim Sanders | 16.65 |
| 72 | Brashard Smith | 17.00 | Roschon Johnson | 20.82 | Phil Mafah | 15.39 |
| 73 | Jerome Ford | 16.00 | Ito Smith | 20.20 | J.K. Dobbins | 14.56 |
| 74 | Malik Davis | 15.00 | Dameon Pierce | 20.13 | Ollie Gordon II | 14.38 |
| 75 | Tank Bigsby | 14.00 | Salvon Ahmed | 19.17 | Tyler Allgeier | 14.37 |
| 76 | DJ Giddens | 13.00 | Bhayshul Tuten | 19.08 | Braelon Allen | 13.08 |
| 77 | Ray Davis | 12.00 | Dylan Sampson | 19.02 | Jaleel McLaughlin | 12.11 |
| 78 | Zavier Scott | 11.00 | Jalen Richard | 18.67 | Tyler Goodson | 9.17 |
| 79 | Terrell Jennings | 10.00 | Elijah Mitchell | 18.56 | Corey Kiner | 9.01 |
| 80 | Jaleel McLaughlin | 9.00 | Pierre Strong | 18.07 | Jaret Patterson | 8.88 |

## WR Board Top 100
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Jaxon Smith-Njigba | 99.50 | Puka Nacua | 90.35 | Ja'Marr Chase | 849.07 |
| 2 | Puka Nacua | 98.80 | Ja'Marr Chase | 89.99 | Amon-Ra St. Brown | 793.56 |
| 3 | Amon-Ra St. Brown | 98.00 | Amon-Ra St. Brown | 89.26 | Puka Nacua | 762.71 |
| 4 | Ja'Marr Chase | 97.50 | Justin Jefferson | 86.73 | Jaxon Smith-Njigba | 758.62 |
| 5 | Drake London | 96.20 | CeeDee Lamb | 84.75 | Chris Olave | 720.54 |
| 6 | Chris Olave | 95.00 | Davante Adams | 78.83 | Justin Jefferson | 649.14 |
| 7 | A.J. Brown | 94.50 | Chris Olave | 75.00 | Wan'Dale Robinson | 648.67 |
| 8 | Rashee Rice | 93.80 | A.J. Brown | 74.84 | George Pickens | 636.86 |
| 9 | Justin Jefferson | 93.00 | Zay Flowers | 73.50 | Michael Wilson | 583.74 |
| 10 | Garrett Wilson | 92.50 | George Pickens | 73.29 | Emeka Egbuka | 579.22 |
| 11 | George Pickens | 91.80 | Jaxon Smith-Njigba | 72.06 | Courtland Sutton | 573.64 |
| 12 | Zay Flowers | 91.00 | Courtland Sutton | 70.10 | A.J. Brown | 562.83 |
| 13 | Davante Adams | 89.50 | Nico Collins | 69.52 | Tetairoa McMillan | 561.98 |
| 14 | CeeDee Lamb | 88.80 | Jakobi Meyers | 69.35 | Nico Collins | 560.74 |
| 15 | Nico Collins | 88.00 | Michael Pittman | 67.96 | Zay Flowers | 546.17 |
| 16 | Tetairoa McMillan | 87.20 | DJ Moore | 67.22 | CeeDee Lamb | 543.66 |
| 17 | Wan'Dale Robinson | 86.50 | Jaylen Waddle | 66.39 | Davante Adams | 530.89 |
| 18 | Malik Nabers | 85.80 | DeVonta Smith | 66.15 | Drake London | 528.59 |
| 19 | Rome Odunze | 85.00 | Rashee Rice | 64.35 | DeVonta Smith | 522.70 |
| 20 | DeVonta Smith | 84.20 | Mike Evans | 62.60 | Jakobi Meyers | 505.95 |
| 21 | Terry McLaurin | 83.50 | Cooper Kupp | 61.09 | Michael Pittman | 503.21 |
| 22 | Jaylen Waddle | 82.80 | DK Metcalf | 60.91 | Jerry Jeudy | 488.23 |
| 23 | Alec Pierce | 82.00 | Drake London | 60.73 | Ladd McConkey | 483.65 |
| 24 | Tee Higgins | 81.20 | Garrett Wilson | 60.65 | Jameson Williams | 479.32 |
| 25 | Courtland Sutton | 80.50 | Jordan Addison | 60.61 | Troy Franklin | 470.62 |
| 26 | Emeka Egbuka | 79.80 | Tee Higgins | 59.72 | Jaylen Waddle | 464.62 |
| 27 | Jameson Williams | 79.00 | Tank Dell | 58.93 | Tee Higgins | 456.55 |
| 28 | Jakobi Meyers | 78.20 | Michael Wilson | 57.89 | DK Metcalf | 454.97 |
| 29 | Mike Evans | 77.50 | Wan'Dale Robinson | 57.63 | Parker Washington | 442.66 |
| 30 | Quentin Johnston | 76.80 | Chris Godwin Jr. | 54.40 | Khalil Shakir | 441.17 |
| 31 | Michael Wilson | 76.00 | Terry McLaurin | 53.69 | Tre Tucker | 427.70 |
| 32 | Christian Watson | 75.20 | Romeo Doubs | 51.23 | Jauan Jennings | 424.66 |
| 33 | Jordan Addison | 74.50 | Jerry Jeudy | 49.80 | Rashid Shaheed | 420.83 |
| 34 | DK Metcalf | 73.80 | Brandon Aiyuk | 48.10 | Rome Odunze | 418.95 |
| 35 | Ladd McConkey | 73.00 | Rashid Shaheed | 46.35 | Brian Thomas Jr. | 409.97 |
| 36 | Romeo Doubs | 72.20 | Josh Downs | 45.39 | Elic Ayomanor | 404.68 |
| 37 | Jauan Jennings | 71.50 | Jameson Williams | 44.99 | Josh Downs | 403.43 |
| 38 | Tre Tucker | 70.80 | Calvin Ridley | 44.44 | Romeo Doubs | 398.19 |
| 39 | Parker Washington | 70.00 | Christian Watson | 44.13 | Quentin Johnston | 397.80 |
| 40 | Ricky Pearsall | 69.20 | Quentin Johnston | 42.17 | Alec Pierce | 397.33 |
| 41 | Troy Franklin | 68.50 | Tre Tucker | 41.37 | DJ Moore | 379.64 |
| 42 | Jerry Jeudy | 67.80 | Jayden Reed | 40.76 | Rashee Rice | 373.35 |
| 43 | Elic Ayomanor | 67.00 | Khalil Shakir | 40.25 | Jordan Addison | 369.46 |
| 44 | Darius Slayton | 66.20 | Parker Washington | 37.64 | Marquise Brown | 337.27 |
| 45 | Calvin Ridley | 65.50 | Jauan Jennings | 37.15 | Darnell Mooney | 333.22 |
| 46 | Khalil Shakir | 64.80 | Alec Pierce | 36.43 | Adonai Mitchell | 332.56 |
| 47 | Darnell Mooney | 64.00 | Marquise Brown | 36.16 | Xavier Worthy | 328.11 |
| 48 | Keon Coleman | 63.20 | Darius Slayton | 35.83 | Chimere Dike | 327.26 |
| 49 | Brian Thomas Jr. | 62.50 | Darnell Mooney | 34.39 | Cooper Kupp | 319.39 |
| 50 | Xavier Worthy | 61.80 | Christian Kirk | 34.26 | Jayden Higgins | 304.67 |
| 51 | Travis Hunter | 61.00 | DeMario Douglas | 31.97 | Mack Hollins | 303.69 |
| 52 | Mack Hollins | 60.20 | Dontayvion Wicks | 31.52 | Olamide Zaccheaus | 300.48 |
| 53 | Michael Pittman | 59.50 | Mack Hollins | 31.24 | Mike Evans | 295.31 |
| 54 | Jakobie Keeney-James | 58.80 | Odell Beckham Jr. | 29.10 | Darius Slayton | 295.08 |
| 55 | Kayshon Boutte | 58.00 | Andrei Iosivas | 29.00 | Garrett Wilson | 292.15 |
| 56 | Jayden Reed | 57.20 | Kendrick Bourne | 28.04 | Xavier Legette | 287.94 |
| 57 | Jalen Coker | 56.50 | K.J. Osborn | 27.01 | Terry McLaurin | 286.78 |
| 58 | Josh Downs | 55.80 | Olamide Zaccheaus | 26.85 | Malik Washington | 284.35 |
| 59 | Rashid Shaheed | 55.00 | Demarcus Robinson | 25.64 | Andrei Iosivas | 271.24 |
| 60 | Cooper Kupp | 54.20 | Marvin Mims Jr. | 24.90 | Keon Coleman | 270.18 |
| 61 | Chris Godwin Jr. | 53.50 | Calvin Austin III | 24.42 | Christian Watson | 266.19 |
| 62 | Jalen McMillan | 52.80 | Van Jefferson | 24.21 | Xavier Hutchinson | 265.99 |
| 63 | Devaughn Vele | 52.00 | Elijah Moore | 24.04 | Luther Burden III | 262.16 |
| 64 | Marquise Brown | 51.20 | Trey Palmer | 23.99 | Calvin Austin III | 259.13 |
| 65 | Van Jefferson | 50.50 | Cedric Tillman | 23.60 | Jalen Nailor | 249.82 |
| 66 | Xavier Legette | 49.80 | Rashod Bateman | 23.47 | Ryan Flournoy | 247.75 |
| 67 | Jayden Higgins | 49.00 | Xavier Hutchinson | 22.81 | Ricky Pearsall | 246.14 |
| 68 | DJ Moore | 48.20 | Tutu Atwell | 22.74 | Kendrick Bourne | 244.61 |
| 69 | Adonai Mitchell | 47.50 | Jahan Dotson | 22.62 | Van Jefferson | 240.83 |
| 70 | Theo Wease Jr. | 46.80 | KaVontae Turpin | 22.58 | Christian Kirk | 235.95 |
| 71 | Tyquan Thornton | 46.00 | Tim Patrick | 22.12 | Chris Godwin Jr. | 232.17 |
| 72 | Andrei Iosivas | 45.20 | Emeka Egbuka | 22.06 | Marvin Mims Jr. | 228.71 |
| 73 | Olamide Zaccheaus | 44.50 | John Metchie III | 21.93 | Kayshon Boutte | 224.17 |
| 74 | Chimere Dike | 43.80 | Tetairoa McMillan | 21.91 | John Metchie III | 221.34 |
| 75 | Kendrick Bourne | 43.00 | Greg Dortch | 20.96 | Pat Bryant | 218.40 |
| 76 | Malik Washington | 42.20 | Allen Hurns | 20.34 | Dontayvion Wicks | 214.97 |
| 77 | Ryan Flournoy | 41.50 | Marquez Valdes-Scantling | 20.21 | Travis Hunter | 207.96 |
| 78 | Calvin Austin III | 40.80 | JuJu Smith-Schuster | 18.84 | DeMario Douglas | 205.83 |
| 79 | Pat Bryant | 40.00 | Kayshon Boutte | 18.83 | JuJu Smith-Schuster | 203.97 |
| 80 | Dontayvion Wicks | 39.20 | Tyler Johnson | 18.31 | Jalen Coker | 196.56 |
| 81 | Xavier Hutchinson | 38.50 | Quez Watkins | 18.17 | Matthew Golden | 192.23 |
| 82 | Rashod Bateman | 37.80 | David Moore | 17.83 | Tez Johnson | 192.19 |
| 83 | Matthew Golden | 37.00 | Jalen Nailor | 17.81 | Isaiah Bond | 192.11 |
| 84 | Jalen Nailor | 36.20 | Ladd McConkey | 17.77 | Tre Harris | 187.00 |
| 85 | Tory Horton | 35.50 | Brandon Johnson | 17.76 | Cedric Tillman | 184.33 |
| 86 | Tez Johnson | 34.80 | Troy Franklin | 17.73 | Rashod Bateman | 179.28 |
| 87 | Luther Burden III | 34.00 | Nick Westbrook-Ikhine | 17.66 | Malik Nabers | 178.19 |
| 88 | DeMario Douglas | 33.20 | Jonathan Mingo | 17.65 | Devaughn Vele | 177.53 |
| 89 | Christian Kirk | 32.50 | Terrace Marshall Jr. | 17.12 | Tyquan Thornton | 176.10 |
| 90 | Isaiah Bond | 31.80 | Rome Odunze | 16.99 | Dyami Brown | 175.07 |
| 91 | Treylon Burks | 31.00 | Kalif Raymond | 16.95 | KaVontae Turpin | 172.26 |
| 92 | Tre Harris | 30.20 | Lil'Jordan Humphrey | 16.93 | Calvin Ridley | 170.15 |
| 93 | Isaac TeSlaa | 29.50 | Jalen Tolbert | 16.88 | David Sills | 169.36 |
| 94 | Casey Washington | 28.80 | David Sills | 16.86 | Jahan Dotson | 163.20 |
| 95 | Marquez Valdes-Scantling | 28.00 | Tyquan Thornton | 16.77 | Jalen Tolbert | 162.97 |
| 96 | Cedric Tillman | 27.20 | Dyami Brown | 16.42 | Demarcus Robinson | 159.92 |
| 97 | Jalen Tolbert | 26.50 | Tyler Scott | 16.34 | Isaiah Williams | 151.85 |
| 98 | Devontez Walker | 25.80 | Treylon Burks | 15.77 | Greg Dortch | 148.59 |
| 99 | Lil'Jordan Humphrey | 25.00 | Brian Thomas Jr. | 15.48 | Jaylin Noel | 145.98 |
| 100 | John Metchie III | 24.20 | Cedrick Wilson Jr. | 15.15 | Kalif Raymond | 135.79 |

## TE Board Top 35
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Trey McBride | 98.00 | Trey McBride | 79.21 | Trey McBride | 784.28 |
| 2 | Brock Bowers | 95.00 | Travis Kelce | 72.60 | Kyle Pitts | 545.24 |
| 3 | George Kittle | 92.00 | George Kittle | 68.35 | Tyler Warren | 508.42 |
| 4 | Sam LaPorta | 90.00 | Sam LaPorta | 63.23 | Travis Kelce | 492.50 |
| 5 | Tucker Kraft | 88.00 | Jake Ferguson | 57.54 | Dalton Schultz | 485.14 |
| 6 | Kyle Pitts | 86.00 | Kyle Pitts | 57.50 | Harold Fannin Jr. | 479.27 |
| 7 | Dallas Goedert | 85.00 | Mark Andrews | 54.99 | Juwan Johnson | 471.67 |
| 8 | Tyler Warren | 84.00 | Dallas Goedert | 52.11 | Jake Ferguson | 470.80 |
| 9 | Travis Kelce | 83.00 | Dalton Schultz | 50.02 | Hunter Henry | 404.77 |
| 10 | Hunter Henry | 80.00 | David Njoku | 49.32 | Brock Bowers | 399.43 |
| 11 | Dalton Schultz | 79.00 | Evan Engram | 49.17 | Dallas Goedert | 382.23 |
| 12 | Juwan Johnson | 78.00 | Hunter Henry | 47.99 | Cade Otton | 374.53 |
| 13 | Colston Loveland | 77.00 | Juwan Johnson | 46.00 | Colston Loveland | 371.75 |
| 14 | Jake Ferguson | 76.00 | T.J. Hockenson | 45.73 | Chig Okonkwo | 357.44 |
| 15 | Harold Fannin Jr. | 75.00 | Cade Otton | 44.23 | Evan Engram | 342.42 |
| 16 | Dalton Kincaid | 74.00 | Cole Kmet | 42.29 | Theo Johnson | 336.84 |
| 17 | Mark Andrews | 73.00 | Dalton Kincaid | 41.18 | George Kittle | 328.30 |
| 18 | T.J. Hockenson | 72.00 | Tucker Kraft | 39.23 | Mark Andrews | 318.92 |
| 19 | Brenton Strange | 68.00 | Chig Okonkwo | 36.31 | Oronde Gadsden II | 312.34 |
| 20 | Cade Otton | 67.00 | Pat Freiermuth | 33.44 | AJ Barner | 303.25 |
| 21 | Theo Johnson | 66.00 | Tyler Higbee | 28.00 | T.J. Hockenson | 301.65 |
| 22 | Mason Taylor | 65.00 | Mike Gesicki | 27.75 | Mason Taylor | 294.61 |
| 23 | Oronde Gadsden II | 64.00 | Michael Mayer | 27.61 | Brenton Strange | 288.61 |
| 24 | AJ Barner | 63.00 | Dawson Knox | 25.98 | Colby Parkinson | 265.31 |
| 25 | Greg Dulcich | 62.00 | Luke Musgrave | 25.13 | Pat Freiermuth | 247.76 |
| 26 | David Njoku | 61.00 | Noah Fant | 24.27 | Gunnar Helm | 242.34 |
| 27 | Colby Parkinson | 60.00 | Jack Doyle | 24.20 | Michael Mayer | 234.93 |
| 28 | Pat Freiermuth | 59.00 | Colby Parkinson | 24.17 | Sam LaPorta | 234.44 |
| 29 | Dawson Knox | 58.00 | Isaiah Likely | 23.67 | Dalton Kincaid | 229.73 |
| 30 | Cole Kmet | 57.00 | Brenton Strange | 23.65 | Dawson Knox | 227.95 |
| 31 | Evan Engram | 56.00 | Darren Fells | 23.41 | Jake Tonges | 225.93 |
| 32 | Michael Mayer | 55.00 | Noah Gray | 21.93 | Tucker Kraft | 220.83 |
| 33 | Isaiah Likely | 54.00 | Tyler Warren | 21.52 | David Njoku | 220.77 |
| 34 | Chig Okonkwo | 53.00 | Davis Allen | 21.31 | Cole Kmet | 220.45 |
| 35 | Mike Gesicki | 52.00 | Tyler Conklin | 20.62 | Darnell Washington | 206.81 |

## Logistic Risers
| Player | Pos | Current | Logistic | Delta | Missing % |
|---|---|---|---|---|---|
| Justin Fields | QB | 263 | 38 | +225 | 27.6% |
| Brian Robinson | RB | 269 | 53 | +216 | 24.1% |
| Jerome Ford | RB | 273 | 91 | +182 | 24.1% |
| Tyler Allgeier | RB | 198 | 44 | +154 | 24.1% |
| Rachaad White | RB | 170 | 23 | +147 | 24.1% |
| Devin Singletary | RB | 209 | 62 | +147 | 17.2% |
| Keaton Mitchell | RB | 262 | 115 | +147 | 37.9% |
| David Montgomery | RB | 166 | 21 | +145 | 17.2% |
| Isiah Pacheco | RB | 174 | 30 | +144 | 24.1% |
| Joe Flacco | QB | 285 | 144 | +141 | 18.4% |
| Chuba Hubbard | RB | 177 | 37 | +140 | 24.1% |
| Marcus Mariota | QB | 256 | 124 | +132 | 23.0% |
| Emari Demercado | RB | 264 | 142 | +122 | 34.5% |
| Alvin Kamara | RB | 141 | 20 | +121 | 19.5% |
| Jordan Mason | RB | 188 | 67 | +121 | 24.1% |
| Emanuel Wilson | RB | 215 | 96 | +119 | 37.9% |
| DJ Moore | WR | 179 | 61 | +118 | 17.2% |
| Tyjae Spears | RB | 180 | 66 | +114 | 34.5% |
| Sean Tucker | RB | 271 | 162 | +109 | 37.9% |
| Jaleel McLaughlin | RB | 283 | 174 | +109 | 37.9% |

## Logistic Fallers
| Player | Pos | Current | Logistic | Delta | Missing % |
|---|---|---|---|---|---|
| Fernando Mendoza | QB | 203 | 719 | -516 | 100.0% |
| Malik Nabers | WR | 40 | 375 | -335 | 85.1% |
| Jakobie Keeney-James | WR | 142 | 469 | -327 | 85.1% |
| Jalen McMillan | WR | 164 | 447 | -283 | 85.1% |
| Theo Wease Jr. | WR | 183 | 461 | -278 | 85.1% |
| Drake Dabney | TE | 187 | 459 | -272 | 85.1% |
| Ricky Pearsall | WR | 103 | 372 | -269 | 85.1% |
| Travis Hunter | WR | 134 | 399 | -265 | 85.1% |
| Shedeur Sanders | QB | 144 | 405 | -261 | 85.1% |
| Jalen Coker | WR | 150 | 406 | -256 | 85.1% |
| Ja'Tavion Sanders | TE | 173 | 426 | -253 | 85.1% |
| Devaughn Vele | WR | 167 | 417 | -250 | 85.1% |
| Keon Coleman | WR | 126 | 374 | -248 | 85.1% |
| Brock Bowers | TE | 11 | 254 | -243 | 85.1% |
| Casey Washington | WR | 244 | 482 | -238 | 85.1% |
| Devontez Walker | WR | 255 | 491 | -236 | 85.1% |
| Mason Taylor | TE | 118 | 348 | -230 | 85.1% |
| Tory Horton | WR | 220 | 449 | -229 | 85.1% |
| Rome Odunze | WR | 44 | 272 | -228 | 85.1% |
| Jackson Hawes | TE | 218 | 445 | -227 | 85.1% |

## Cutline Crossings
| Model | Cutline | Entered | Entered sample | Exited | Exited sample |
|---|---|---|---|---|---|
| enriched_logistic | overall top 24 | 18 | Saquon Barkley, Kyren Williams, Derrick Henry, James Cook, Travis Etienne | 18 | Puka Nacua, Ja'Marr Chase, Amon-Ra St. Brown, Justin Jefferson, Trey McBride |
| enriched_logistic | overall top 50 | 25 | Derrick Henry, Travis Etienne, Breece Hall, Josh Jacobs, Tony Pollard | 25 | Jaxon Smith-Njigba, Nico Collins, George Kittle, DeVonta Smith, Brock Purdy |
| enriched_logistic | overall top 100 | 32 | Tony Pollard, Kenneth Walker III, Alvin Kamara, David Montgomery, Rachaad White | 32 | Dalton Schultz, Joe Burrow, Matthew Stafford, Hunter Henry, Jordan Love |
| enriched_logistic | QB12 | 5 | Lamar Jackson, Justin Fields, Justin Herbert, Baker Mayfield, C.J. Stroud | 5 | Matthew Stafford, Jordan Love, Drake Maye, Bo Nix, Caleb Williams |
| enriched_logistic | RB12 | 4 | Derrick Henry, Travis Etienne, Breece Hall, Josh Jacobs | 4 | Javonte Williams, Chase Brown, Ashton Jeanty, Omarion Hampton |
| enriched_logistic | RB24 | 6 | Tony Pollard, Kenneth Walker III, Alvin Kamara, David Montgomery, Rachaad White | 6 | Ashton Jeanty, J.K. Dobbins, Quinshon Judkins, Bucky Irving, Omarion Hampton |
| enriched_logistic | RB36 | 8 | David Montgomery, Rachaad White, Isiah Pacheco, Chuba Hubbard, Tyler Allgeier | 8 | Woody Marks, TreVeyon Henderson, Tyrone Tracy Jr., Bucky Irving, RJ Harvey |
| enriched_logistic | WR12 | 3 | CeeDee Lamb, Davante Adams, Courtland Sutton | 3 | Rashee Rice, Drake London, Garrett Wilson |
| enriched_logistic | WR24 | 7 | Courtland Sutton, Jakobi Meyers, Michael Pittman, DJ Moore, Mike Evans | 7 | Tee Higgins, Wan'Dale Robinson, Terry McLaurin, Alec Pierce, Tetairoa McMillan |
| enriched_logistic | WR36 | 9 | Michael Pittman, DJ Moore, Cooper Kupp, Tank Dell, Chris Godwin Jr. | 9 | Jameson Williams, Christian Watson, Quentin Johnston, Alec Pierce, Emeka Egbuka |
| enriched_logistic | TE6 | 2 | Travis Kelce, Jake Ferguson | 2 | Tucker Kraft, Brock Bowers |
| enriched_logistic | TE12 | 4 | Jake Ferguson, Mark Andrews, David Njoku, Evan Engram | 4 | Juwan Johnson, Tucker Kraft, Tyler Warren, Brock Bowers |
| enriched_logistic | TE18 | 4 | David Njoku, Evan Engram, Cade Otton, Cole Kmet | 4 | Tyler Warren, Harold Fannin Jr., Brock Bowers, Colston Loveland |
| enriched_linear_points | overall top 24 | 13 | Wan'Dale Robinson, Michael Wilson, Emeka Egbuka, Courtland Sutton, Tetairoa McMillan | 13 | Christian McCaffrey, Brock Bowers, Rashee Rice, Bijan Robinson, Jahmyr Gibbs |
| enriched_linear_points | overall top 50 | 28 | Michael Wilson, Emeka Egbuka, Courtland Sutton, Jakobi Meyers, Michael Pittman | 28 | Dallas Goedert, Rashee Rice, Bijan Robinson, Jahmyr Gibbs, Chase Brown |
| enriched_linear_points | overall top 100 | 42 | Michael Pittman, Jerry Jeudy, Troy Franklin, Parker Washington, Khalil Shakir | 42 | Sam LaPorta, Dalton Kincaid, Tucker Kraft, Malik Nabers, Rico Dowdle |
| enriched_linear_points | QB12 | 10 | Jameis Winston, Aaron Rodgers, Sam Howell, Josh Johnson, Blake Bortles | 10 | Jordan Love, Patrick Mahomes, Dak Prescott, Daniel Jones, Trevor Lawrence |
| enriched_linear_points | RB12 | 6 | Kenneth Gainwell, RJ Harvey, Tyjae Spears, Michael Carter, Tyrone Tracy Jr. | 6 | Kyren Williams, Javonte Williams, Omarion Hampton, Jonathan Taylor, Saquon Barkley |
| enriched_linear_points | RB24 | 11 | Kenneth Gainwell, RJ Harvey, Tyjae Spears, Michael Carter, Tyrone Tracy Jr. | 11 | Jonathan Taylor, Cam Skattebo, Breece Hall, Rhamondre Stevenson, Saquon Barkley |
| enriched_linear_points | RB36 | 11 | Tyjae Spears, Michael Carter, Dylan Sampson, Rachaad White, Brashard Smith | 11 | Josh Jacobs, Woody Marks, Quinshon Judkins, Tony Pollard, James Cook |
| enriched_linear_points | WR12 | 4 | Wan'Dale Robinson, Michael Wilson, Emeka Egbuka, Courtland Sutton | 4 | Zay Flowers, Drake London, Rashee Rice, Garrett Wilson |
| enriched_linear_points | WR24 | 8 | Michael Wilson, Emeka Egbuka, Courtland Sutton, Jakobi Meyers, Michael Pittman | 8 | Jaylen Waddle, Tee Higgins, Rome Odunze, Alec Pierce, Rashee Rice |
| enriched_linear_points | WR36 | 10 | Michael Pittman, Jerry Jeudy, Troy Franklin, Parker Washington, Khalil Shakir | 10 | Romeo Doubs, Quentin Johnston, Alec Pierce, Rashee Rice, Jordan Addison |
| enriched_linear_points | TE6 | 4 | Tyler Warren, Travis Kelce, Dalton Schultz, Harold Fannin Jr. | 4 | Brock Bowers, George Kittle, Sam LaPorta, Tucker Kraft |
| enriched_linear_points | TE12 | 3 | Harold Fannin Jr., Jake Ferguson, Cade Otton | 3 | George Kittle, Sam LaPorta, Tucker Kraft |
| enriched_linear_points | TE18 | 4 | Cade Otton, Chig Okonkwo, Evan Engram, Theo Johnson | 4 | T.J. Hockenson, Sam LaPorta, Dalton Kincaid, Tucker Kraft |

## TE35 Watch Band
| Model | TE rank | Player | Score | Current TE rank | Missing % |
|---|---|---|---|---|---|
| enriched_logistic | 30 | Brenton Strange | 23.65 | 19 | 42.5% |
| enriched_logistic | 31 | Darren Fells | 23.41 |  | 27.6% |
| enriched_logistic | 32 | Noah Gray | 21.93 |  | 24.1% |
| enriched_logistic | 33 | Tyler Warren | 21.52 | 8 | 85.1% |
| enriched_logistic | 34 | Davis Allen | 21.31 | 53 | 39.1% |
| enriched_logistic | 35 | Tyler Conklin | 20.62 |  | 19.5% |
| enriched_logistic | 36 | Tommy Tremble | 20.55 | 38 | 24.1% |
| enriched_logistic | 37 | Harold Fannin Jr. | 19.96 | 15 | 85.1% |
| enriched_logistic | 38 | Ryan Izzo | 19.94 |  | 41.4% |
| enriched_logistic | 39 | Daniel Bellinger | 19.12 | 45 | 21.8% |
| enriched_logistic | 40 | Darnell Washington | 19.12 | 42 | 42.5% |
| enriched_linear_points | 30 | Dawson Knox | 227.95 | 29 | 24.1% |
| enriched_linear_points | 31 | Jake Tonges | 225.93 | 40 | 43.7% |
| enriched_linear_points | 32 | Tucker Kraft | 220.83 | 5 | 39.1% |
| enriched_linear_points | 33 | David Njoku | 220.77 | 26 | 19.5% |
| enriched_linear_points | 34 | Cole Kmet | 220.45 | 30 | 24.1% |
| enriched_linear_points | 35 | Darnell Washington | 206.81 | 42 | 42.5% |
| enriched_linear_points | 36 | Mike Gesicki | 195.17 | 35 | 24.1% |
| enriched_linear_points | 37 | Noah Fant | 186.75 | 60 | 24.1% |
| enriched_linear_points | 38 | Tommy Tremble | 172.21 | 38 | 24.1% |
| enriched_linear_points | 39 | Elijah Higgins | 171.64 |  | 42.5% |
| enriched_linear_points | 40 | Noah Gray | 170.97 |  | 24.1% |

# Half PPR Review Boards

## Current Pigskin Top 50 Overall
| Rank | Player | Pos | Team | Score | Pos rank |
|---|---|---|---|---|---|
| 1 | Jaxon Smith-Njigba | WR | SEA | 98.50 | 1 |
| 2 | Josh Allen | QB | BUF | 98.50 | 1 |
| 3 | Christian McCaffrey | RB | SF | 98.00 | 1 |
| 4 | Trey McBride | TE | ARI | 98.00 | 1 |
| 5 | Puka Nacua | WR | LAR | 97.00 | 2 |
| 6 | Ja'Marr Chase | WR | CIN | 96.00 | 3 |
| 7 | Amon-Ra St. Brown | WR | DET | 95.50 | 4 |
| 8 | Bijan Robinson | RB | ATL | 95.00 | 2 |
| 9 | Brock Bowers | TE | LV | 95.00 | 2 |
| 10 | Drake Maye | QB | NE | 95.00 | 2 |
| 11 | Patrick Mahomes | QB | KC | 94.00 | 3 |
| 12 | Drake London | WR | ATL | 94.00 | 5 |
| 13 | Jahmyr Gibbs | RB | DET | 93.00 | 3 |
| 14 | Garrett Wilson | WR | NYJ | 93.00 | 6 |
| 15 | De'Von Achane | RB | MIA | 92.00 | 4 |
| 16 | Rashee Rice | WR | KC | 92.00 | 7 |
| 17 | Jonathan Taylor | RB | IND | 91.00 | 5 |
| 18 | Chris Olave | WR | NO | 91.00 | 8 |
| 19 | George Kittle | TE | SF | 90.00 | 3 |
| 20 | A.J. Brown | WR | NE | 90.00 | 9 |
| 21 | Justin Jefferson | WR | MIN | 89.50 | 10 |
| 22 | Brock Purdy | QB | SF | 89.00 | 4 |
| 23 | Breece Hall | RB | NYJ | 89.00 | 6 |
| 24 | Tucker Kraft | TE | GB | 88.00 | 4 |
| 25 | Jalen Hurts | QB | PHI | 88.00 | 5 |
| 26 | Saquon Barkley | RB | PHI | 88.00 | 7 |
| 27 | George Pickens | WR | DAL | 88.00 | 11 |
| 28 | Zay Flowers | WR | BAL | 87.50 | 12 |
| 29 | Trevor Lawrence | QB | JAX | 87.00 | 6 |
| 30 | Kyren Williams | RB | LAR | 87.00 | 8 |
| 31 | Davante Adams | WR | LAR | 86.50 | 13 |
| 32 | Daniel Jones | QB | IND | 86.00 | 7 |
| 33 | James Cook | RB | BUF | 86.00 | 9 |
| 34 | CeeDee Lamb | WR | DAL | 86.00 | 14 |
| 35 | Nico Collins | WR | HOU | 85.50 | 15 |
| 36 | Kyle Pitts | TE | ATL | 85.00 | 5 |
| 37 | Bo Nix | QB | DEN | 85.00 | 8 |
| 38 | Josh Jacobs | RB | GB | 85.00 | 10 |
| 39 | Wan'Dale Robinson | WR | TEN | 85.00 | 16 |
| 40 | Tetairoa McMillan | WR | CAR | 84.50 | 17 |
| 41 | Dallas Goedert | TE | PHI | 84.00 | 6 |
| 42 | Caleb Williams | QB | CHI | 84.00 | 9 |
| 43 | Travis Etienne | RB | NO | 84.00 | 11 |
| 44 | Malik Nabers | WR | NYG | 84.00 | 18 |
| 45 | Sam LaPorta | TE | DET | 83.00 | 7 |
| 46 | Matthew Stafford | QB | LAR | 83.00 | 10 |
| 47 | Chase Brown | RB | CIN | 83.00 | 12 |
| 48 | Rome Odunze | WR | CHI | 83.00 | 19 |
| 49 | DeVonta Smith | WR | PHI | 82.50 | 20 |
| 50 | Justin Herbert | QB | LAC | 82.00 | 11 |

## BQML Logistic Top 50 Overall
| Logistic rank | Player | Pos | Team | Score | Current rank | Delta | Missing % |
|---|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey | RB | SF | 99.79 | 3 | +2 | 17.2% |
| 2 | Bijan Robinson | RB | ATL | 99.53 | 8 | +6 | 34.5% |
| 3 | Jonathan Taylor | RB | IND | 99.53 | 17 | +14 | 24.1% |
| 4 | Saquon Barkley | RB | PHI | 99.41 | 26 | +22 | 19.5% |
| 5 | Kyren Williams | RB | LAR | 99.33 | 30 | +25 | 24.1% |
| 6 | Derrick Henry | RB | BAL | 99.27 | 55 | +49 | 17.2% |
| 7 | Jahmyr Gibbs | RB | DET | 99.20 | 13 | +6 | 34.5% |
| 8 | James Cook | RB | BUF | 99.10 | 33 | +25 | 24.1% |
| 9 | Travis Etienne | RB | NO | 98.98 | 43 | +34 | 24.1% |
| 10 | De'Von Achane | RB | MIA | 98.86 | 15 | +5 | 34.5% |
| 11 | Breece Hall | RB | NYJ | 98.62 | 23 | +12 | 24.1% |
| 12 | Josh Jacobs | RB | GB | 98.15 | 38 | +26 | 19.5% |
| 13 | Javonte Williams | RB | DAL | 97.64 | 51 | +38 | 24.1% |
| 14 | Tony Pollard | RB | TEN | 97.28 | 94 | +80 | 19.5% |
| 15 | D'Andre Swift | RB | CHI | 96.72 | 86 | +71 | 21.8% |
| 16 | Kenneth Walker III | RB | KC | 96.42 | 60 | +44 | 24.1% |
| 17 | Jaylen Warren | RB | PIT | 94.77 | 73 | +56 | 24.1% |
| 18 | Chase Brown | RB | CIN | 93.81 | 47 | +29 | 34.5% |
| 19 | Rico Dowdle | RB | PIT | 93.70 | 102 | +83 | 27.6% |
| 20 | Alvin Kamara | RB | NO | 93.06 | 116 | +96 | 19.5% |
| 21 | David Montgomery | RB | HOU | 91.40 | 133 | +112 | 17.2% |
| 22 | Rachaad White | RB | WAS | 91.23 | 155 | +133 | 24.1% |
| 23 | Josh Allen | QB | BUF | 91.09 | 2 | -21 | 23.0% |
| 24 | Puka Nacua | WR | LAR | 90.95 | 5 | -19 | 34.5% |
| 25 | Jalen Hurts | QB | PHI | 90.75 | 25 | +0 | 23.0% |
| 26 | Ja'Marr Chase | WR | CIN | 90.67 | 6 | -20 | 21.8% |
| 27 | Aaron Jones | RB | MIN | 90.35 | 91 | +64 | 19.5% |
| 28 | Amon-Ra St. Brown | WR | DET | 89.95 | 7 | -21 | 24.1% |
| 29 | Rhamondre Stevenson | RB | NE | 88.55 | 77 | +48 | 24.1% |
| 30 | Isiah Pacheco | RB | DET | 88.45 | 159 | +129 | 24.1% |
| 31 | Zach Charbonnet | RB | SEA | 87.22 | 125 | +94 | 34.5% |
| 32 | Justin Jefferson | WR | MIN | 87.10 | 21 | -11 | 21.8% |
| 33 | Ashton Jeanty | RB | LV | 86.63 | 68 | +35 | 85.1% |
| 34 | CeeDee Lamb | WR | DAL | 85.68 | 34 | +0 | 21.8% |
| 35 | J.K. Dobbins | RB | DEN | 82.72 | 99 | +64 | 24.1% |
| 36 | Lamar Jackson | QB | BAL | 82.14 | 63 | +27 | 18.4% |
| 37 | Chuba Hubbard | RB | CAR | 81.55 | 140 | +103 | 24.1% |
| 38 | Trey McBride | TE | ARI | 80.93 | 4 | -34 | 28.7% |
| 39 | Kenneth Gainwell | RB | TB | 79.44 | 148 | +109 | 21.8% |
| 40 | Davante Adams | WR | LAR | 79.36 | 31 | -9 | 19.5% |
| 41 | Justin Fields | QB | KC | 79.18 | 226 | +185 | 27.6% |
| 42 | Chris Olave | WR | NO | 76.21 | 18 | -24 | 28.7% |
| 43 | A.J. Brown | WR | NE | 75.55 | 20 | -23 | 24.1% |
| 44 | Trevor Lawrence | QB | JAX | 75.05 | 29 | -15 | 27.6% |
| 45 | Tyler Allgeier | RB | ARI | 74.89 | 193 | +148 | 24.1% |
| 46 | George Pickens | WR | DAL | 74.38 | 27 | -19 | 24.1% |
| 47 | Zay Flowers | WR | BAL | 74.32 | 28 | -19 | 34.5% |
| 48 | Justin Herbert | QB | LAC | 74.06 | 50 | +2 | 23.0% |
| 49 | Jaxon Smith-Njigba | WR | SEA | 73.27 | 1 | -48 | 39.1% |
| 50 | Travis Kelce | TE | KC | 73.23 | 66 | +16 | 19.5% |

## BQML Linear Points Top 50 Overall
| Linear rank | Player | Pos | Team | Score | Current rank | Delta | Missing % |
|---|---|---|---|---|---|---|---|
| 1 | Ja'Marr Chase | WR | CIN | 852.23 | 6 | +5 | 21.8% |
| 2 | Amon-Ra St. Brown | WR | DET | 796.41 | 7 | +5 | 24.1% |
| 3 | Trey McBride | TE | ARI | 787.56 | 4 | +1 | 28.7% |
| 4 | Puka Nacua | WR | LAR | 765.88 | 5 | +1 | 34.5% |
| 5 | Jaxon Smith-Njigba | WR | SEA | 761.42 | 1 | -4 | 39.1% |
| 6 | Chris Olave | WR | NO | 723.17 | 18 | +12 | 28.7% |
| 7 | Wan'Dale Robinson | WR | TEN | 651.23 | 39 | +32 | 24.1% |
| 8 | Justin Jefferson | WR | MIN | 651.11 | 21 | +13 | 21.8% |
| 9 | George Pickens | WR | DAL | 639.19 | 27 | +18 | 24.1% |
| 10 | Michael Wilson | WR | ARI | 585.69 | 70 | +60 | 39.1% |
| 11 | Emeka Egbuka | WR | TB | 580.86 | 61 | +50 | 85.1% |
| 12 | Courtland Sutton | WR | DEN | 575.56 | 57 | +45 | 17.2% |
| 13 | A.J. Brown | WR | NE | 564.93 | 20 | +7 | 24.1% |
| 14 | Tetairoa McMillan | WR | CAR | 563.76 | 40 | +26 | 85.1% |
| 15 | Nico Collins | WR | HOU | 562.90 | 35 | +20 | 24.1% |
| 16 | Zay Flowers | WR | BAL | 548.28 | 28 | +12 | 34.5% |
| 17 | Kyle Pitts | TE | ATL | 547.34 | 36 | +19 | 24.1% |
| 18 | CeeDee Lamb | WR | DAL | 546.22 | 34 | +16 | 21.8% |
| 19 | Davante Adams | WR | LAR | 532.69 | 31 | +12 | 19.5% |
| 20 | Drake London | WR | ATL | 530.91 | 12 | -8 | 26.4% |
| 21 | DeVonta Smith | WR | PHI | 524.69 | 49 | +28 | 28.7% |
| 22 | Tyler Warren | TE | IND | 510.33 | 58 | +36 | 85.1% |
| 23 | Jakobi Meyers | WR | JAX | 508.00 | 62 | +39 | 17.2% |
| 24 | Michael Pittman | WR | PIT | 505.27 | 117 | +93 | 24.1% |
| 25 | Travis Kelce | TE | KC | 494.37 | 66 | +41 | 19.5% |
| 26 | Jerry Jeudy | WR | CLE | 489.63 | 96 | +70 | 24.1% |
| 27 | Dalton Schultz | TE | HOU | 487.15 | 80 | +53 | 24.1% |
| 28 | Ladd McConkey | WR | LAC | 485.44 | 83 | +55 | 85.1% |
| 29 | Harold Fannin Jr. | TE | CLE | 481.19 | 119 | +90 | 85.1% |
| 30 | Jameson Williams | WR | DET | 481.17 | 64 | +34 | 24.1% |
| 31 | Christian McCaffrey | RB | SF | 477.64 | 3 | -28 | 17.2% |
| 32 | Juwan Johnson | TE | NO | 473.69 | 89 | +57 | 28.7% |
| 33 | Jake Ferguson | TE | DAL | 473.17 | 105 | +72 | 28.7% |
| 34 | Troy Franklin | WR | DEN | 472.29 | 95 | +61 | 85.1% |
| 35 | Jaylen Waddle | WR | DEN | 466.25 | 53 | +18 | 24.1% |
| 36 | Tee Higgins | WR | CIN | 458.15 | 56 | +20 | 28.7% |
| 37 | DK Metcalf | WR | PIT | 456.61 | 79 | +42 | 24.1% |
| 38 | Parker Washington | WR | JAX | 444.26 | 92 | +54 | 39.1% |
| 39 | Khalil Shakir | WR | BUF | 443.28 | 104 | +65 | 24.1% |
| 40 | Tre Tucker | WR | LV | 429.21 | 88 | +48 | 34.5% |
| 41 | Jauan Jennings | WR | MIN | 426.27 | 84 | +43 | 21.8% |
| 42 | Rashid Shaheed | WR | SEA | 422.43 | 135 | +93 | 24.1% |
| 43 | Rome Odunze | WR | CHI | 420.57 | 48 | +5 | 85.1% |
| 44 | Brian Thomas Jr. | WR | JAX | 411.50 | 112 | +68 | 85.1% |
| 45 | Hunter Henry | TE | NE | 406.43 | 72 | +27 | 24.1% |
| 46 | Elic Ayomanor | WR | TEN | 405.91 | 100 | +54 | 85.1% |
| 47 | Josh Downs | WR | IND | 405.04 | 134 | +87 | 39.1% |
| 48 | Brock Bowers | TE | LV | 401.64 | 9 | -39 | 85.1% |
| 49 | Romeo Doubs | WR | NE | 399.83 | 87 | +38 | 21.8% |
| 50 | Quentin Johnston | WR | LAC | 399.51 | 74 | +24 | 34.5% |

## Side-by-Side Top 100 Overall
| Rank | Current | Pos | Logistic | Pos | Score | Linear | Pos | Score |
|---|---|---|---|---|---|---|---|---|
| 1 | Jaxon Smith-Njigba | WR | Christian McCaffrey | RB | 99.79 | Ja'Marr Chase | WR | 852.23 |
| 2 | Josh Allen | QB | Bijan Robinson | RB | 99.53 | Amon-Ra St. Brown | WR | 796.41 |
| 3 | Christian McCaffrey | RB | Jonathan Taylor | RB | 99.53 | Trey McBride | TE | 787.56 |
| 4 | Trey McBride | TE | Saquon Barkley | RB | 99.41 | Puka Nacua | WR | 765.88 |
| 5 | Puka Nacua | WR | Kyren Williams | RB | 99.33 | Jaxon Smith-Njigba | WR | 761.42 |
| 6 | Ja'Marr Chase | WR | Derrick Henry | RB | 99.27 | Chris Olave | WR | 723.17 |
| 7 | Amon-Ra St. Brown | WR | Jahmyr Gibbs | RB | 99.20 | Wan'Dale Robinson | WR | 651.23 |
| 8 | Bijan Robinson | RB | James Cook | RB | 99.10 | Justin Jefferson | WR | 651.11 |
| 9 | Brock Bowers | TE | Travis Etienne | RB | 98.98 | George Pickens | WR | 639.19 |
| 10 | Drake Maye | QB | De'Von Achane | RB | 98.86 | Michael Wilson | WR | 585.69 |
| 11 | Patrick Mahomes | QB | Breece Hall | RB | 98.62 | Emeka Egbuka | WR | 580.86 |
| 12 | Drake London | WR | Josh Jacobs | RB | 98.15 | Courtland Sutton | WR | 575.56 |
| 13 | Jahmyr Gibbs | RB | Javonte Williams | RB | 97.64 | A.J. Brown | WR | 564.93 |
| 14 | Garrett Wilson | WR | Tony Pollard | RB | 97.28 | Tetairoa McMillan | WR | 563.76 |
| 15 | De'Von Achane | RB | D'Andre Swift | RB | 96.72 | Nico Collins | WR | 562.90 |
| 16 | Rashee Rice | WR | Kenneth Walker III | RB | 96.42 | Zay Flowers | WR | 548.28 |
| 17 | Jonathan Taylor | RB | Jaylen Warren | RB | 94.77 | Kyle Pitts | TE | 547.34 |
| 18 | Chris Olave | WR | Chase Brown | RB | 93.81 | CeeDee Lamb | WR | 546.22 |
| 19 | George Kittle | TE | Rico Dowdle | RB | 93.70 | Davante Adams | WR | 532.69 |
| 20 | A.J. Brown | WR | Alvin Kamara | RB | 93.06 | Drake London | WR | 530.91 |
| 21 | Justin Jefferson | WR | David Montgomery | RB | 91.40 | DeVonta Smith | WR | 524.69 |
| 22 | Brock Purdy | QB | Rachaad White | RB | 91.23 | Tyler Warren | TE | 510.33 |
| 23 | Breece Hall | RB | Josh Allen | QB | 91.09 | Jakobi Meyers | WR | 508.00 |
| 24 | Tucker Kraft | TE | Puka Nacua | WR | 90.95 | Michael Pittman | WR | 505.27 |
| 25 | Jalen Hurts | QB | Jalen Hurts | QB | 90.75 | Travis Kelce | TE | 494.37 |
| 26 | Saquon Barkley | RB | Ja'Marr Chase | WR | 90.67 | Jerry Jeudy | WR | 489.63 |
| 27 | George Pickens | WR | Aaron Jones | RB | 90.35 | Dalton Schultz | TE | 487.15 |
| 28 | Zay Flowers | WR | Amon-Ra St. Brown | WR | 89.95 | Ladd McConkey | WR | 485.44 |
| 29 | Trevor Lawrence | QB | Rhamondre Stevenson | RB | 88.55 | Harold Fannin Jr. | TE | 481.19 |
| 30 | Kyren Williams | RB | Isiah Pacheco | RB | 88.45 | Jameson Williams | WR | 481.17 |
| 31 | Davante Adams | WR | Zach Charbonnet | RB | 87.22 | Christian McCaffrey | RB | 477.64 |
| 32 | Daniel Jones | QB | Justin Jefferson | WR | 87.10 | Juwan Johnson | TE | 473.69 |
| 33 | James Cook | RB | Ashton Jeanty | RB | 86.63 | Jake Ferguson | TE | 473.17 |
| 34 | CeeDee Lamb | WR | CeeDee Lamb | WR | 85.68 | Troy Franklin | WR | 472.29 |
| 35 | Nico Collins | WR | J.K. Dobbins | RB | 82.72 | Jaylen Waddle | WR | 466.25 |
| 36 | Kyle Pitts | TE | Lamar Jackson | QB | 82.14 | Tee Higgins | WR | 458.15 |
| 37 | Bo Nix | QB | Chuba Hubbard | RB | 81.55 | DK Metcalf | WR | 456.61 |
| 38 | Josh Jacobs | RB | Trey McBride | TE | 80.93 | Parker Washington | WR | 444.26 |
| 39 | Wan'Dale Robinson | WR | Kenneth Gainwell | RB | 79.44 | Khalil Shakir | WR | 443.28 |
| 40 | Tetairoa McMillan | WR | Davante Adams | WR | 79.36 | Tre Tucker | WR | 429.21 |
| 41 | Dallas Goedert | TE | Justin Fields | QB | 79.18 | Jauan Jennings | WR | 426.27 |
| 42 | Caleb Williams | QB | Chris Olave | WR | 76.21 | Rashid Shaheed | WR | 422.43 |
| 43 | Travis Etienne | RB | A.J. Brown | WR | 75.55 | Rome Odunze | WR | 420.57 |
| 44 | Malik Nabers | WR | Trevor Lawrence | QB | 75.05 | Brian Thomas Jr. | WR | 411.50 |
| 45 | Sam LaPorta | TE | Tyler Allgeier | RB | 74.89 | Hunter Henry | TE | 406.43 |
| 46 | Matthew Stafford | QB | George Pickens | WR | 74.38 | Elic Ayomanor | WR | 405.91 |
| 47 | Chase Brown | RB | Zay Flowers | WR | 74.32 | Josh Downs | WR | 405.04 |
| 48 | Rome Odunze | WR | Justin Herbert | QB | 74.06 | Brock Bowers | TE | 401.64 |
| 49 | DeVonta Smith | WR | Jaxon Smith-Njigba | WR | 73.27 | Romeo Doubs | WR | 399.83 |
| 50 | Justin Herbert | QB | Travis Kelce | TE | 73.23 | Quentin Johnston | WR | 399.51 |
| 51 | Javonte Williams | RB | Quinshon Judkins | RB | 72.30 | Alec Pierce | WR | 398.70 |
| 52 | Terry McLaurin | WR | Brian Robinson | RB | 72.22 | Dallas Goedert | TE | 383.93 |
| 53 | Jaylen Waddle | WR | Patrick Mahomes | QB | 72.10 | DJ Moore | WR | 381.12 |
| 54 | Jayden Daniels | QB | Courtland Sutton | WR | 70.99 | Cade Otton | TE | 376.28 |
| 55 | Derrick Henry | RB | Nico Collins | WR | 70.80 | Rashee Rice | WR | 376.01 |
| 56 | Tee Higgins | WR | Jakobi Meyers | WR | 70.34 | Colston Loveland | TE | 373.35 |
| 57 | Courtland Sutton | WR | George Kittle | TE | 69.47 | Jordan Addison | WR | 370.84 |
| 58 | Tyler Warren | TE | Michael Pittman | WR | 69.04 | Bijan Robinson | RB | 370.55 |
| 59 | Dak Prescott | QB | DJ Moore | WR | 68.05 | Chig Okonkwo | TE | 359.08 |
| 60 | Kenneth Walker III | RB | Baker Mayfield | QB | 67.43 | Kenneth Gainwell | RB | 352.44 |
| 61 | Emeka Egbuka | WR | C.J. Stroud | QB | 67.23 | Jahmyr Gibbs | RB | 346.33 |
| 62 | Jakobi Meyers | WR | DeVonta Smith | WR | 67.17 | Evan Engram | TE | 343.79 |
| 63 | Lamar Jackson | QB | Devin Singletary | RB | 67.07 | Marquise Brown | WR | 338.50 |
| 64 | Jameson Williams | WR | Jaylen Waddle | WR | 66.82 | Theo Johnson | TE | 338.22 |
| 65 | Mike Evans | WR | James Conner | RB | 66.42 | Chase Brown | RB | 335.99 |
| 66 | Travis Kelce | TE | Tyjae Spears | RB | 66.36 | Darnell Mooney | WR | 334.13 |
| 67 | Jordan Love | QB | Rashee Rice | WR | 65.65 | Adonai Mitchell | WR | 333.61 |
| 68 | Ashton Jeanty | RB | Jordan Mason | RB | 64.93 | George Kittle | TE | 330.52 |
| 69 | Alec Pierce | WR | Brock Purdy | QB | 64.67 | Xavier Worthy | WR | 329.50 |
| 70 | Michael Wilson | WR | Sam LaPorta | TE | 64.07 | Chimere Dike | WR | 328.58 |
| 71 | Omarion Hampton | RB | Mike Evans | WR | 63.28 | Cooper Kupp | WR | 320.70 |
| 72 | Hunter Henry | TE | Garrett Wilson | WR | 61.93 | Mark Andrews | TE | 320.17 |
| 73 | Jaylen Warren | RB | Drake London | WR | 61.84 | Oronde Gadsden II | TE | 313.82 |
| 74 | Quentin Johnston | WR | DK Metcalf | WR | 61.44 | De'Von Achane | RB | 312.55 |
| 75 | Christian Watson | WR | Cooper Kupp | WR | 61.33 | Jayden Higgins | WR | 305.85 |
| 76 | Jaxson Dart | QB | Jordan Addison | WR | 61.15 | Mack Hollins | WR | 305.09 |
| 77 | Rhamondre Stevenson | RB | Woody Marks | RB | 60.71 | AJ Barner | TE | 304.66 |
| 78 | Jordan Addison | WR | Tee Higgins | WR | 60.13 | T.J. Hockenson | TE | 303.04 |
| 79 | DK Metcalf | WR | Tank Dell | WR | 59.87 | Olamide Zaccheaus | WR | 301.81 |
| 80 | Dalton Schultz | TE | Jake Ferguson | TE | 59.57 | Mike Evans | WR | 296.95 |
| 81 | Jared Goff | QB | Wan'Dale Robinson | WR | 59.29 | Darius Slayton | WR | 296.30 |
| 82 | Bucky Irving | RB | Daniel Jones | QB | 58.94 | Mason Taylor | TE | 296.13 |
| 83 | Ladd McConkey | WR | Dak Prescott | QB | 58.87 | Garrett Wilson | WR | 294.37 |
| 84 | Jauan Jennings | WR | Michael Wilson | WR | 58.80 | Brenton Strange | TE | 290.29 |
| 85 | Kyler Murray | QB | Kyle Pitts | TE | 58.39 | Xavier Legette | WR | 289.09 |
| 86 | D'Andre Swift | RB | TreVeyon Henderson | RB | 58.21 | Terry McLaurin | WR | 288.47 |
| 87 | Romeo Doubs | WR | Tyrone Tracy Jr. | RB | 57.97 | Malik Washington | WR | 285.64 |
| 88 | Tre Tucker | WR | Kyler Murray | QB | 57.84 | Andrei Iosivas | WR | 272.34 |
| 89 | Juwan Johnson | TE | Bucky Irving | RB | 56.60 | Keon Coleman | WR | 271.62 |
| 90 | C.J. Stroud | QB | Jerome Ford | RB | 56.12 | Christian Watson | WR | 267.69 |
| 91 | Aaron Jones | RB | Mark Andrews | TE | 55.25 | Xavier Hutchinson | WR | 267.09 |
| 92 | Parker Washington | WR | Chris Godwin Jr. | WR | 54.80 | Colby Parkinson | TE | 266.78 |
| 93 | Ricky Pearsall | WR | Terry McLaurin | WR | 54.50 | Luther Burden III | WR | 263.59 |
| 94 | Tony Pollard | RB | Michael Carter | RB | 54.17 | Calvin Austin III | WR | 260.24 |
| 95 | Troy Franklin | WR | Chris Rodriguez Jr. | RB | 54.08 | Ashton Jeanty | RB | 252.88 |
| 96 | Jerry Jeudy | WR | Emanuel Wilson | RB | 53.60 | Jalen Nailor | WR | 250.71 |
| 97 | Colston Loveland | TE | Jared Goff | QB | 53.16 | Ryan Flournoy | WR | 249.02 |
| 98 | Tyler Shough | QB | Dallas Goedert | TE | 52.80 | Pat Freiermuth | TE | 248.96 |
| 99 | J.K. Dobbins | RB | Romeo Doubs | WR | 52.15 | Ricky Pearsall | WR | 247.88 |
| 100 | Elic Ayomanor | WR | Bryce Young | QB | 51.98 | Kendrick Bourne | WR | 245.85 |

## QB Board Top 45
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Josh Allen | 98.50 | Josh Allen | 91.09 | Jameis Winston | 22.90 |
| 2 | Drake Maye | 95.00 | Jalen Hurts | 90.75 | Aaron Rodgers | 17.05 |
| 3 | Patrick Mahomes | 94.00 | Lamar Jackson | 82.14 | Sam Howell | 16.60 |
| 4 | Brock Purdy | 89.00 | Justin Fields | 79.18 | Josh Johnson | 16.09 |
| 5 | Jalen Hurts | 88.00 | Trevor Lawrence | 75.05 | Brock Purdy | 15.10 |
| 6 | Trevor Lawrence | 87.00 | Justin Herbert | 74.06 | Blake Bortles | 14.87 |
| 7 | Daniel Jones | 86.00 | Patrick Mahomes | 72.10 | Matthew Stafford | 14.82 |
| 8 | Bo Nix | 85.00 | Baker Mayfield | 67.43 | Jared Goff | 13.72 |
| 9 | Caleb Williams | 84.00 | C.J. Stroud | 67.23 | Deshaun Watson | 13.62 |
| 10 | Matthew Stafford | 83.00 | Brock Purdy | 64.67 | Tommy DeVito | 12.89 |
| 11 | Justin Herbert | 82.00 | Daniel Jones | 58.94 | Ben Roethlisberger | 12.71 |
| 12 | Jayden Daniels | 81.00 | Dak Prescott | 58.87 | Will Levis | 12.63 |
| 13 | Dak Prescott | 80.00 | Kyler Murray | 57.84 | Joe Burrow | 11.99 |
| 14 | Lamar Jackson | 79.00 | Jared Goff | 53.16 | Malik Willis | 11.98 |
| 15 | Jordan Love | 78.00 | Bryce Young | 51.98 | Brandon Allen | 11.55 |
| 16 | Jaxson Dart | 75.00 | Geno Smith | 50.32 | Jake Browning | 11.38 |
| 17 | Jared Goff | 74.00 | Joe Burrow | 49.36 | Aidan O'Connell | 11.34 |
| 18 | Kyler Murray | 73.00 | Matthew Stafford | 49.16 | Davis Mills | 10.98 |
| 19 | C.J. Stroud | 72.00 | Jordan Love | 47.20 | Bailey Zappe | 9.81 |
| 20 | Tyler Shough | 70.00 | Tua Tagovailoa | 45.77 | Carson Wentz | 9.69 |
| 21 | Bryce Young | 68.00 | Sam Darnold | 45.68 | Joe Flacco | 9.59 |
| 22 | Aaron Rodgers | 67.00 | Blake Bortles | 44.61 | Tua Tagovailoa | 9.16 |
| 23 | Baker Mayfield | 66.00 | Marcus Mariota | 44.08 | Kyler Murray | 9.09 |
| 24 | Joe Burrow | 65.00 | Anthony Richardson | 42.38 | Kirk Cousins | 8.65 |
| 25 | Jacoby Brissett | 64.00 | Sam Howell | 41.83 | Jordan Love | 7.98 |
| 26 | Malik Willis | 63.00 | Carson Wentz | 40.42 | Sam Ehlinger | 7.87 |
| 27 | Sam Darnold | 62.00 | Deshaun Watson | 38.97 | Trevor Siemian | 7.67 |
| 28 | Geno Smith | 60.00 | Will Levis | 38.47 | Skylar Thompson | 7.63 |
| 29 | Tua Tagovailoa | 58.00 | Joe Flacco | 37.31 | Tyrod Taylor | 6.83 |
| 30 | Shedeur Sanders | 55.00 | Tyler Huntley | 37.29 | Sam Darnold | 6.76 |
| 31 | Cam Ward | 50.00 | Mac Jones | 37.18 | Case Keenum | 6.36 |
| 32 | Fernando Mendoza | 35.00 | Jacoby Brissett | 36.49 | Jacoby Brissett | 5.01 |
| 33 | Justin Fields | 30.00 | Kirk Cousins | 33.90 | Mitchell Trubisky | 4.75 |
| 34 | Carson Wentz | 28.00 | Tyson Bagent | 32.72 | Easton Stick | 4.73 |
| 35 | Marcus Mariota | 27.00 | Aaron Rodgers | 32.50 | Andy Dalton | 4.04 |
| 36 | J.J. McCarthy | 26.00 | Ben Roethlisberger | 31.86 | Mason Rudolph | 3.89 |
| 37 | Spencer Rattler | 25.00 | Mason Rudolph | 30.92 | Teddy Bridgewater | 3.57 |
| 38 | Jake Browning | 24.00 | Tommy DeVito | 29.86 | Tyler Huntley | 3.51 |
| 39 | Mac Jones | 23.00 | Tyrod Taylor | 29.11 | Patrick Mahomes | 3.41 |
| 40 | Tyler Huntley | 22.00 | Aidan O'Connell | 28.76 | Kyle Allen | 2.85 |
| 41 | Joe Flacco | 21.00 | Trey Lance | 28.59 | Anthony Richardson | 2.29 |
| 42 | Jameis Winston | 20.00 | Drake Maye | 27.83 | Drew Lock | 2.11 |
| 43 | Davis Mills | 19.00 | Jameis Winston | 27.58 | Spencer Rattler | 1.91 |
| 44 | Josh Johnson | 18.00 | Zach Wilson | 25.75 | Quinn Ewers | 1.78 |
| 45 | Quinn Ewers | 15.00 | Davis Mills | 24.99 | Mac Jones | 1.59 |

## RB Board Top 80
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey | 98.00 | Christian McCaffrey | 99.79 | Christian McCaffrey | 477.64 |
| 2 | Bijan Robinson | 95.00 | Bijan Robinson | 99.53 | Bijan Robinson | 370.55 |
| 3 | Jahmyr Gibbs | 93.00 | Jonathan Taylor | 99.53 | Kenneth Gainwell | 352.44 |
| 4 | De'Von Achane | 92.00 | Saquon Barkley | 99.41 | Jahmyr Gibbs | 346.33 |
| 5 | Jonathan Taylor | 91.00 | Kyren Williams | 99.33 | Chase Brown | 335.99 |
| 6 | Breece Hall | 89.00 | Derrick Henry | 99.27 | De'Von Achane | 312.55 |
| 7 | Saquon Barkley | 88.00 | Jahmyr Gibbs | 99.20 | Ashton Jeanty | 252.88 |
| 8 | Kyren Williams | 87.00 | James Cook | 99.10 | RJ Harvey | 221.87 |
| 9 | James Cook | 86.00 | Travis Etienne | 98.98 | Tyjae Spears | 202.38 |
| 10 | Josh Jacobs | 85.00 | De'Von Achane | 98.86 | Michael Carter | 171.06 |
| 11 | Travis Etienne | 84.00 | Breece Hall | 98.62 | Tyrone Tracy Jr. | 167.66 |
| 12 | Chase Brown | 83.00 | Josh Jacobs | 98.15 | Dylan Sampson | 160.42 |
| 13 | Javonte Williams | 82.00 | Javonte Williams | 97.64 | Rico Dowdle | 159.68 |
| 14 | Derrick Henry | 81.00 | Tony Pollard | 97.28 | Rachaad White | 150.27 |
| 15 | Kenneth Walker III | 80.00 | D'Andre Swift | 96.72 | Kyren Williams | 146.84 |
| 16 | Ashton Jeanty | 78.00 | Kenneth Walker III | 96.42 | Javonte Williams | 145.33 |
| 17 | Omarion Hampton | 77.00 | Jaylen Warren | 94.77 | Brashard Smith | 141.74 |
| 18 | Jaylen Warren | 76.00 | Chase Brown | 93.81 | Travis Etienne | 141.58 |
| 19 | Rhamondre Stevenson | 75.00 | Rico Dowdle | 93.70 | Tyler Badie | 140.20 |
| 20 | Bucky Irving | 74.00 | Alvin Kamara | 93.06 | D'Andre Swift | 139.57 |
| 21 | D'Andre Swift | 73.00 | David Montgomery | 91.40 | TreVeyon Henderson | 139.23 |
| 22 | Aaron Jones | 72.00 | Rachaad White | 91.23 | Jaylen Warren | 139.22 |
| 23 | Tony Pollard | 71.00 | Aaron Jones | 90.35 | Omarion Hampton | 138.42 |
| 24 | J.K. Dobbins | 70.00 | Rhamondre Stevenson | 88.55 | Jerome Ford | 135.96 |
| 25 | Rico Dowdle | 69.00 | Isiah Pacheco | 88.45 | Ty Johnson | 135.10 |
| 26 | Quinshon Judkins | 68.00 | Zach Charbonnet | 87.22 | Aaron Jones | 133.44 |
| 27 | Cam Skattebo | 67.00 | Ashton Jeanty | 86.63 | Jonathan Taylor | 132.55 |
| 28 | Alvin Kamara | 66.00 | J.K. Dobbins | 82.72 | Breece Hall | 132.27 |
| 29 | James Conner | 65.00 | Chuba Hubbard | 81.55 | Cam Skattebo | 132.25 |
| 30 | Zach Charbonnet | 64.00 | Kenneth Gainwell | 79.44 | Jeremy McNichols | 131.01 |
| 31 | David Montgomery | 62.00 | Tyler Allgeier | 74.89 | Chuba Hubbard | 126.56 |
| 32 | TreVeyon Henderson | 61.00 | Quinshon Judkins | 72.30 | Alvin Kamara | 123.33 |
| 33 | Chuba Hubbard | 60.00 | Brian Robinson | 72.22 | Rhamondre Stevenson | 123.27 |
| 34 | Jacory Croskey-Merritt | 59.00 | Devin Singletary | 67.07 | Saquon Barkley | 120.25 |
| 35 | Kenneth Gainwell | 58.00 | James Conner | 66.42 | Justice Hill | 118.01 |
| 36 | Tyrone Tracy Jr. | 57.00 | Tyjae Spears | 66.36 | Bucky Irving | 117.52 |
| 37 | Rachaad White | 56.00 | Jordan Mason | 64.93 | Isaiah Davis | 112.15 |
| 38 | Isiah Pacheco | 55.00 | Woody Marks | 60.71 | Josh Jacobs | 109.08 |
| 39 | Tyjae Spears | 54.00 | TreVeyon Henderson | 58.21 | Woody Marks | 105.45 |
| 40 | Jordan Mason | 53.00 | Tyrone Tracy Jr. | 57.97 | Quinshon Judkins | 96.59 |
| 41 | Trey Benson | 52.00 | Bucky Irving | 56.60 | Tony Pollard | 91.11 |
| 42 | Kimani Vidal | 51.00 | Jerome Ford | 56.12 | Kyle Monangai | 85.53 |
| 43 | Kyle Monangai | 50.00 | Michael Carter | 54.17 | James Cook | 81.94 |
| 44 | Woody Marks | 49.00 | Chris Rodriguez Jr. | 54.08 | Kenneth Walker III | 79.31 |
| 45 | RJ Harvey | 48.00 | Emanuel Wilson | 53.60 | Trey Benson | 77.60 |
| 46 | Bhayshul Tuten | 47.00 | RJ Harvey | 50.27 | Emari Demercado | 74.17 |
| 47 | Chris Rodriguez Jr. | 46.00 | Kyle Monangai | 49.41 | Devin Neal | 72.16 |
| 48 | Tyler Allgeier | 45.00 | Jacory Croskey-Merritt | 46.96 | Ameer Abdullah | 70.97 |
| 49 | Blake Corum | 44.00 | Keaton Mitchell | 46.28 | Isiah Pacheco | 70.82 |
| 50 | Raheim Sanders | 43.00 | Samaje Perine | 44.17 | Chris Brooks | 69.10 |
| 51 | Devin Singletary | 40.00 | Kimani Vidal | 43.47 | David Montgomery | 67.93 |
| 52 | Jaylen Wright | 39.00 | Omarion Hampton | 41.70 | Samaje Perine | 66.53 |
| 53 | Dylan Sampson | 38.00 | Emari Demercado | 37.89 | Zavier Scott | 60.67 |
| 54 | Phil Mafah | 37.00 | Blake Corum | 36.43 | Kimani Vidal | 56.85 |
| 55 | Ty Johnson | 36.00 | AJ Dillon | 36.35 | Zach Charbonnet | 53.44 |
| 56 | Justice Hill | 35.00 | Jeremy McNichols | 35.23 | Will Shipley | 44.44 |
| 57 | Samaje Perine | 34.00 | Ty Johnson | 34.55 | Rasheen Ali | 43.20 |
| 58 | Emanuel Wilson | 33.00 | Justice Hill | 34.37 | Emanuel Wilson | 39.85 |
| 59 | Michael Carter | 32.00 | Cam Skattebo | 33.56 | Bhayshul Tuten | 38.69 |
| 60 | Jawhar Jordan | 31.00 | Sean Tucker | 33.36 | LeQuint Allen Jr. | 37.25 |
| 61 | Jaret Patterson | 30.00 | Kendre Miller | 32.45 | Ray Davis | 37.08 |
| 62 | Kendre Miller | 29.00 | Malik Davis | 32.12 | Devin Singletary | 34.66 |
| 63 | Jeremy McNichols | 28.00 | Ty Chandler | 29.64 | Keaton Mitchell | 31.73 |
| 64 | Braelon Allen | 27.00 | Jaleel McLaughlin | 29.37 | James Conner | 28.79 |
| 65 | Emari Demercado | 26.00 | Tank Bigsby | 28.96 | Jawhar Jordan | 28.71 |
| 66 | Keaton Mitchell | 25.00 | Jaret Patterson | 28.40 | Jordan Mason | 28.15 |
| 67 | Isaiah Davis | 24.00 | Le'Veon Bell | 27.01 | Sean Tucker | 23.82 |
| 68 | Jaydon Blue | 23.00 | Elijah McGuire | 26.54 | Jaylen Wright | 21.10 |
| 69 | Brian Robinson | 22.00 | Ameer Abdullah | 23.49 | Ty Chandler | 18.84 |
| 70 | Sean Tucker | 21.00 | Chris Brooks | 22.98 | Blake Corum | 18.74 |
| 71 | Jerome Ford | 20.00 | Tyler Badie | 22.61 | Raheim Sanders | 17.24 |
| 72 | Brashard Smith | 19.00 | Roschon Johnson | 20.72 | Phil Mafah | 16.43 |
| 73 | Malik Davis | 18.00 | Ito Smith | 20.26 | J.K. Dobbins | 15.27 |
| 74 | Tank Bigsby | 17.00 | Dameon Pierce | 19.74 | Tyler Allgeier | 15.00 |
| 75 | DJ Giddens | 16.00 | Dylan Sampson | 19.25 | Ollie Gordon II | 14.85 |
| 76 | Ray Davis | 15.00 | Salvon Ahmed | 19.10 | Braelon Allen | 13.58 |
| 77 | Zavier Scott | 14.00 | Bhayshul Tuten | 19.08 | Jaleel McLaughlin | 12.61 |
| 78 | Jaleel McLaughlin | 13.00 | Jalen Richard | 18.62 | Tyler Goodson | 9.56 |
| 79 | Terrell Jennings | 12.00 | Elijah Mitchell | 18.23 | Corey Kiner | 9.52 |
| 80 | Devin Neal | 10.00 | Pierre Strong | 17.99 | Jaret Patterson | 9.38 |

## WR Board Top 100
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Jaxon Smith-Njigba | 98.50 | Puka Nacua | 90.95 | Ja'Marr Chase | 852.23 |
| 2 | Puka Nacua | 97.00 | Ja'Marr Chase | 90.67 | Amon-Ra St. Brown | 796.41 |
| 3 | Ja'Marr Chase | 96.00 | Amon-Ra St. Brown | 89.95 | Puka Nacua | 765.88 |
| 4 | Amon-Ra St. Brown | 95.50 | Justin Jefferson | 87.10 | Jaxon Smith-Njigba | 761.42 |
| 5 | Drake London | 94.00 | CeeDee Lamb | 85.68 | Chris Olave | 723.17 |
| 6 | Garrett Wilson | 93.00 | Davante Adams | 79.36 | Wan'Dale Robinson | 651.23 |
| 7 | Rashee Rice | 92.00 | Chris Olave | 76.21 | Justin Jefferson | 651.11 |
| 8 | Chris Olave | 91.00 | A.J. Brown | 75.55 | George Pickens | 639.19 |
| 9 | A.J. Brown | 90.00 | George Pickens | 74.38 | Michael Wilson | 585.69 |
| 10 | Justin Jefferson | 89.50 | Zay Flowers | 74.32 | Emeka Egbuka | 580.86 |
| 11 | George Pickens | 88.00 | Jaxon Smith-Njigba | 73.27 | Courtland Sutton | 575.56 |
| 12 | Zay Flowers | 87.50 | Courtland Sutton | 70.99 | A.J. Brown | 564.93 |
| 13 | Davante Adams | 86.50 | Nico Collins | 70.80 | Tetairoa McMillan | 563.76 |
| 14 | CeeDee Lamb | 86.00 | Jakobi Meyers | 70.34 | Nico Collins | 562.90 |
| 15 | Nico Collins | 85.50 | Michael Pittman | 69.04 | Zay Flowers | 548.28 |
| 16 | Wan'Dale Robinson | 85.00 | DJ Moore | 68.05 | CeeDee Lamb | 546.22 |
| 17 | Tetairoa McMillan | 84.50 | DeVonta Smith | 67.17 | Davante Adams | 532.69 |
| 18 | Malik Nabers | 84.00 | Jaylen Waddle | 66.82 | Drake London | 530.91 |
| 19 | Rome Odunze | 83.00 | Rashee Rice | 65.65 | DeVonta Smith | 524.69 |
| 20 | DeVonta Smith | 82.50 | Mike Evans | 63.28 | Jakobi Meyers | 508.00 |
| 21 | Terry McLaurin | 82.00 | Garrett Wilson | 61.93 | Michael Pittman | 505.27 |
| 22 | Jaylen Waddle | 81.50 | Drake London | 61.84 | Jerry Jeudy | 489.63 |
| 23 | Tee Higgins | 81.00 | DK Metcalf | 61.44 | Ladd McConkey | 485.44 |
| 24 | Courtland Sutton | 80.50 | Cooper Kupp | 61.33 | Jameson Williams | 481.17 |
| 25 | Emeka Egbuka | 80.00 | Jordan Addison | 61.15 | Troy Franklin | 472.29 |
| 26 | Jakobi Meyers | 79.50 | Tee Higgins | 60.13 | Jaylen Waddle | 466.25 |
| 27 | Jameson Williams | 79.00 | Tank Dell | 59.87 | Tee Higgins | 458.15 |
| 28 | Mike Evans | 78.50 | Wan'Dale Robinson | 59.29 | DK Metcalf | 456.61 |
| 29 | Alec Pierce | 78.00 | Michael Wilson | 58.80 | Parker Washington | 444.26 |
| 30 | Michael Wilson | 77.50 | Chris Godwin Jr. | 54.80 | Khalil Shakir | 443.28 |
| 31 | Quentin Johnston | 76.00 | Terry McLaurin | 54.50 | Tre Tucker | 429.21 |
| 32 | Christian Watson | 75.50 | Romeo Doubs | 52.15 | Jauan Jennings | 426.27 |
| 33 | Jordan Addison | 75.00 | Jerry Jeudy | 50.41 | Rashid Shaheed | 422.43 |
| 34 | DK Metcalf | 74.50 | Brandon Aiyuk | 49.19 | Rome Odunze | 420.57 |
| 35 | Ladd McConkey | 74.00 | Rashid Shaheed | 47.32 | Brian Thomas Jr. | 411.50 |
| 36 | Jauan Jennings | 73.50 | Jameson Williams | 46.35 | Elic Ayomanor | 405.91 |
| 37 | Romeo Doubs | 73.00 | Josh Downs | 46.10 | Josh Downs | 405.04 |
| 38 | Tre Tucker | 72.50 | Christian Watson | 44.68 | Romeo Doubs | 399.83 |
| 39 | Parker Washington | 72.00 | Calvin Ridley | 44.58 | Quentin Johnston | 399.51 |
| 40 | Ricky Pearsall | 71.50 | Quentin Johnston | 42.94 | Alec Pierce | 398.70 |
| 41 | Troy Franklin | 71.00 | Tre Tucker | 42.00 | DJ Moore | 381.12 |
| 42 | Jerry Jeudy | 70.50 | Khalil Shakir | 41.74 | Rashee Rice | 376.01 |
| 43 | Elic Ayomanor | 70.00 | Jayden Reed | 41.49 | Jordan Addison | 370.84 |
| 44 | Darius Slayton | 69.50 | Parker Washington | 38.31 | Marquise Brown | 338.50 |
| 45 | Calvin Ridley | 69.00 | Jauan Jennings | 37.77 | Darnell Mooney | 334.13 |
| 46 | Khalil Shakir | 68.50 | Alec Pierce | 36.77 | Adonai Mitchell | 333.61 |
| 47 | Darnell Mooney | 68.00 | Marquise Brown | 36.27 | Xavier Worthy | 329.50 |
| 48 | Keon Coleman | 67.50 | Darius Slayton | 36.14 | Chimere Dike | 328.58 |
| 49 | Brian Thomas Jr. | 67.00 | Darnell Mooney | 34.22 | Cooper Kupp | 320.70 |
| 50 | Travis Hunter | 66.50 | Christian Kirk | 34.22 | Jayden Higgins | 305.85 |
| 51 | Michael Pittman | 66.00 | DeMario Douglas | 32.24 | Mack Hollins | 305.09 |
| 52 | Mack Hollins | 65.50 | Dontayvion Wicks | 31.87 | Olamide Zaccheaus | 301.81 |
| 53 | Xavier Worthy | 65.00 | Mack Hollins | 31.52 | Mike Evans | 296.95 |
| 54 | Jakobie Keeney-James | 64.50 | Odell Beckham Jr. | 29.43 | Darius Slayton | 296.30 |
| 55 | Kayshon Boutte | 64.00 | Andrei Iosivas | 29.30 | Garrett Wilson | 294.37 |
| 56 | Jayden Reed | 63.00 | Kendrick Bourne | 28.40 | Xavier Legette | 289.09 |
| 57 | Jalen Coker | 62.50 | K.J. Osborn | 27.51 | Terry McLaurin | 288.47 |
| 58 | Josh Downs | 62.00 | Olamide Zaccheaus | 27.30 | Malik Washington | 285.64 |
| 59 | Rashid Shaheed | 61.50 | Demarcus Robinson | 25.65 | Andrei Iosivas | 272.34 |
| 60 | Cooper Kupp | 61.00 | Marvin Mims Jr. | 25.23 | Keon Coleman | 271.62 |
| 61 | Chris Godwin Jr. | 60.50 | Calvin Austin III | 24.70 | Christian Watson | 267.69 |
| 62 | Jalen McMillan | 60.00 | Trey Palmer | 24.28 | Xavier Hutchinson | 267.09 |
| 63 | Devaughn Vele | 59.50 | Van Jefferson | 24.23 | Luther Burden III | 263.59 |
| 64 | Marquise Brown | 59.00 | Elijah Moore | 24.16 | Calvin Austin III | 260.24 |
| 65 | Van Jefferson | 58.50 | Cedric Tillman | 23.79 | Jalen Nailor | 250.71 |
| 66 | Xavier Legette | 58.00 | Rashod Bateman | 23.44 | Ryan Flournoy | 249.02 |
| 67 | Jayden Higgins | 57.50 | Tutu Atwell | 23.10 | Ricky Pearsall | 247.88 |
| 68 | DJ Moore | 57.00 | Xavier Hutchinson | 23.07 | Kendrick Bourne | 245.85 |
| 69 | Adonai Mitchell | 56.50 | KaVontae Turpin | 22.95 | Van Jefferson | 241.79 |
| 70 | Theo Wease Jr. | 56.00 | Jahan Dotson | 22.83 | Christian Kirk | 237.00 |
| 71 | Andrei Iosivas | 55.50 | Emeka Egbuka | 22.57 | Chris Godwin Jr. | 233.64 |
| 72 | Tyquan Thornton | 55.00 | Tetairoa McMillan | 22.49 | Marvin Mims Jr. | 229.90 |
| 73 | Olamide Zaccheaus | 54.50 | John Metchie III | 22.24 | Kayshon Boutte | 225.33 |
| 74 | Chimere Dike | 54.00 | Tim Patrick | 22.20 | John Metchie III | 222.56 |
| 75 | Kendrick Bourne | 53.50 | Greg Dortch | 21.12 | Pat Bryant | 219.57 |
| 76 | Malik Washington | 52.00 | Allen Hurns | 20.52 | Dontayvion Wicks | 216.11 |
| 77 | Ryan Flournoy | 51.50 | Marquez Valdes-Scantling | 20.20 | Travis Hunter | 209.70 |
| 78 | Calvin Austin III | 51.00 | Kayshon Boutte | 19.08 | DeMario Douglas | 206.84 |
| 79 | Pat Bryant | 50.50 | JuJu Smith-Schuster | 18.62 | JuJu Smith-Schuster | 204.77 |
| 80 | Dontayvion Wicks | 50.00 | Quez Watkins | 18.48 | Jalen Coker | 197.95 |
| 81 | Xavier Hutchinson | 49.50 | Tyler Johnson | 18.26 | Matthew Golden | 193.29 |
| 82 | Rashod Bateman | 49.00 | Ladd McConkey | 18.26 | Tez Johnson | 193.18 |
| 83 | Matthew Golden | 48.50 | Troy Franklin | 18.17 | Isaiah Bond | 192.87 |
| 84 | Jalen Nailor | 48.00 | David Moore | 18.12 | Tre Harris | 187.98 |
| 85 | Tory Horton | 47.50 | Brandon Johnson | 18.05 | Cedric Tillman | 185.28 |
| 86 | Luther Burden III | 47.00 | Jalen Nailor | 17.90 | Malik Nabers | 180.11 |
| 87 | Tez Johnson | 46.50 | Nick Westbrook-Ikhine | 17.63 | Rashod Bateman | 180.06 |
| 88 | DeMario Douglas | 46.00 | Jonathan Mingo | 17.59 | Devaughn Vele | 178.84 |
| 89 | Christian Kirk | 45.50 | Rome Odunze | 17.40 | Tyquan Thornton | 176.92 |
| 90 | Isaiah Bond | 45.00 | Terrace Marshall Jr. | 17.36 | Dyami Brown | 176.03 |
| 91 | Tre Harris | 44.50 | Lil'Jordan Humphrey | 17.29 | KaVontae Turpin | 173.27 |
| 92 | Treylon Burks | 44.00 | Jalen Tolbert | 17.22 | Calvin Ridley | 171.25 |
| 93 | Isaac TeSlaa | 43.50 | David Sills | 16.98 | David Sills | 170.22 |
| 94 | Casey Washington | 43.00 | Kalif Raymond | 16.91 | Jahan Dotson | 164.03 |
| 95 | Marquez Valdes-Scantling | 42.50 | Tyquan Thornton | 16.79 | Jalen Tolbert | 163.96 |
| 96 | Cedric Tillman | 42.00 | Dyami Brown | 16.55 | Demarcus Robinson | 160.74 |
| 97 | Jalen Tolbert | 41.50 | Tyler Scott | 16.42 | Isaiah Williams | 152.78 |
| 98 | John Metchie III | 41.00 | Brian Thomas Jr. | 15.84 | Greg Dortch | 149.72 |
| 99 | Lil'Jordan Humphrey | 40.50 | Treylon Burks | 15.62 | Jaylin Noel | 146.85 |
| 100 | Devontez Walker | 40.00 | Cedrick Wilson Jr. | 15.23 | Kalif Raymond | 136.58 |

## TE Board Top 35
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Trey McBride | 98.00 | Trey McBride | 80.93 | Trey McBride | 787.56 |
| 2 | Brock Bowers | 95.00 | Travis Kelce | 73.23 | Kyle Pitts | 547.34 |
| 3 | George Kittle | 90.00 | George Kittle | 69.47 | Tyler Warren | 510.33 |
| 4 | Tucker Kraft | 88.00 | Sam LaPorta | 64.07 | Travis Kelce | 494.37 |
| 5 | Kyle Pitts | 85.00 | Jake Ferguson | 59.57 | Dalton Schultz | 487.15 |
| 6 | Dallas Goedert | 84.00 | Kyle Pitts | 58.39 | Harold Fannin Jr. | 481.19 |
| 7 | Sam LaPorta | 83.00 | Mark Andrews | 55.25 | Juwan Johnson | 473.69 |
| 8 | Tyler Warren | 80.00 | Dallas Goedert | 52.80 | Jake Ferguson | 473.17 |
| 9 | Travis Kelce | 78.00 | Dalton Schultz | 50.93 | Hunter Henry | 406.43 |
| 10 | Hunter Henry | 76.00 | David Njoku | 50.07 | Brock Bowers | 401.64 |
| 11 | Dalton Schultz | 74.00 | Evan Engram | 49.68 | Dallas Goedert | 383.93 |
| 12 | Juwan Johnson | 72.00 | Hunter Henry | 48.97 | Cade Otton | 376.28 |
| 13 | Colston Loveland | 70.00 | Juwan Johnson | 47.24 | Colston Loveland | 373.35 |
| 14 | Jake Ferguson | 68.00 | T.J. Hockenson | 46.02 | Chig Okonkwo | 359.08 |
| 15 | Brenton Strange | 66.00 | Cade Otton | 45.09 | Evan Engram | 343.79 |
| 16 | Harold Fannin Jr. | 65.00 | Cole Kmet | 42.74 | Theo Johnson | 338.22 |
| 17 | Cade Otton | 63.00 | Dalton Kincaid | 41.79 | George Kittle | 330.52 |
| 18 | Dalton Kincaid | 62.00 | Tucker Kraft | 40.00 | Mark Andrews | 320.17 |
| 19 | Oronde Gadsden II | 58.00 | Chig Okonkwo | 37.35 | Oronde Gadsden II | 313.82 |
| 20 | Theo Johnson | 56.00 | Pat Freiermuth | 33.66 | AJ Barner | 304.66 |
| 21 | Mason Taylor | 54.00 | Mike Gesicki | 28.39 | T.J. Hockenson | 303.04 |
| 22 | AJ Barner | 52.00 | Michael Mayer | 28.00 | Mason Taylor | 296.13 |
| 23 | Mark Andrews | 50.00 | Tyler Higbee | 27.90 | Brenton Strange | 290.29 |
| 24 | T.J. Hockenson | 48.00 | Dawson Knox | 26.04 | Colby Parkinson | 266.78 |
| 25 | Greg Dulcich | 46.00 | Luke Musgrave | 25.35 | Pat Freiermuth | 248.96 |
| 26 | Pat Freiermuth | 44.00 | Colby Parkinson | 24.73 | Gunnar Helm | 243.64 |
| 27 | Evan Engram | 42.00 | Noah Fant | 24.64 | Sam LaPorta | 236.34 |
| 28 | Chig Okonkwo | 40.00 | Jack Doyle | 24.41 | Michael Mayer | 236.20 |
| 29 | Mike Gesicki | 38.00 | Brenton Strange | 24.20 | Dalton Kincaid | 231.20 |
| 30 | Gunnar Helm | 36.00 | Isaiah Likely | 23.84 | Dawson Knox | 228.98 |
| 31 | Ja'Tavion Sanders | 34.00 | Darren Fells | 23.68 | Jake Tonges | 227.46 |
| 32 | Terrance Ferguson | 32.00 | Noah Gray | 22.21 | Tucker Kraft | 222.57 |
| 33 | Jake Tonges | 30.00 | Tyler Warren | 22.14 | David Njoku | 222.20 |
| 34 | David Njoku | 28.00 | Davis Allen | 21.46 | Cole Kmet | 221.49 |
| 35 | Colby Parkinson | 26.00 | Tommy Tremble | 20.75 | Darnell Washington | 207.98 |

## Logistic Risers
| Player | Pos | Current | Logistic | Delta | Missing % |
|---|---|---|---|---|---|
| Brian Robinson | RB | 248 | 52 | +196 | 24.1% |
| Justin Fields | QB | 226 | 41 | +185 | 27.6% |
| Jerome Ford | RB | 254 | 90 | +164 | 24.1% |
| Tyler Allgeier | RB | 193 | 45 | +148 | 24.1% |
| Devin Singletary | RB | 209 | 63 | +146 | 17.2% |
| Rachaad White | RB | 155 | 22 | +133 | 24.1% |
| Isiah Pacheco | RB | 159 | 30 | +129 | 24.1% |
| Michael Carter | RB | 223 | 94 | +129 | 24.1% |
| Emanuel Wilson | RB | 221 | 96 | +125 | 37.9% |
| David Njoku | TE | 230 | 105 | +125 | 19.5% |
| Keaton Mitchell | RB | 239 | 117 | +122 | 37.9% |
| Cole Kmet | TE | 243 | 130 | +113 | 24.1% |
| David Montgomery | RB | 133 | 21 | +112 | 17.2% |
| Kenneth Gainwell | RB | 148 | 39 | +109 | 21.8% |
| Marcus Mariota | QB | 232 | 127 | +105 | 23.0% |
| Joe Flacco | QB | 250 | 146 | +104 | 18.4% |
| Chuba Hubbard | RB | 140 | 37 | +103 | 24.1% |
| Woody Marks | RB | 179 | 77 | +102 | 85.1% |
| Tyler Huntley | QB | 247 | 147 | +100 | 27.6% |
| Jordan Mason | RB | 166 | 68 | +98 | 24.1% |

## Logistic Fallers
| Player | Pos | Current | Logistic | Delta | Missing % |
|---|---|---|---|---|---|
| Fernando Mendoza | QB | 217 | 719 | -502 | 100.0% |
| Jakobie Keeney-James | WR | 123 | 465 | -342 | 85.1% |
| Malik Nabers | WR | 44 | 368 | -324 | 85.1% |
| Theo Wease Jr. | WR | 156 | 457 | -301 | 85.1% |
| Jalen McMillan | WR | 141 | 441 | -300 | 85.1% |
| Devontez Walker | WR | 210 | 491 | -281 | 85.1% |
| Travis Hunter | WR | 113 | 392 | -279 | 85.1% |
| Casey Washington | WR | 201 | 480 | -279 | 85.1% |
| Jalen Coker | WR | 130 | 403 | -273 | 85.1% |
| Devaughn Vele | WR | 142 | 413 | -271 | 85.1% |
| Ricky Pearsall | WR | 93 | 362 | -269 | 85.1% |
| Tory Horton | WR | 185 | 449 | -264 | 85.1% |
| Keon Coleman | WR | 109 | 371 | -262 | 85.1% |
| Shedeur Sanders | QB | 158 | 407 | -249 | 85.1% |
| Isaac TeSlaa | WR | 199 | 447 | -248 | 85.1% |
| Brock Bowers | TE | 9 | 249 | -240 | 85.1% |
| Phil Mafah | RB | 214 | 450 | -236 | 85.1% |
| Pat Bryant | WR | 173 | 408 | -235 | 85.1% |
| Tyler Shough | QB | 98 | 331 | -233 | 85.1% |
| Xavier Legette | WR | 149 | 376 | -227 | 85.1% |

## Cutline Crossings
| Model | Cutline | Entered | Entered sample | Exited | Exited sample |
|---|---|---|---|---|---|
| enriched_logistic | overall top 24 | 16 | Saquon Barkley, Kyren Williams, Derrick Henry, James Cook, Travis Etienne | 16 | Ja'Marr Chase, Amon-Ra St. Brown, Justin Jefferson, Trey McBride, Chris Olave |
| enriched_logistic | overall top 50 | 22 | Derrick Henry, Javonte Williams, Tony Pollard, D'Andre Swift, Kenneth Walker III | 22 | Patrick Mahomes, Nico Collins, George Kittle, DeVonta Smith, Rashee Rice |
| enriched_logistic | overall top 100 | 32 | Rico Dowdle, Alvin Kamara, David Montgomery, Rachaad White, Isiah Pacheco | 32 | Dalton Schultz, Jerry Jeudy, Matthew Stafford, Hunter Henry, Juwan Johnson |
| enriched_logistic | QB12 | 5 | Lamar Jackson, Justin Fields, Baker Mayfield, C.J. Stroud, Dak Prescott | 5 | Matthew Stafford, Drake Maye, Bo Nix, Caleb Williams, Jayden Daniels |
| enriched_logistic | RB12 | 1 | Derrick Henry | 1 | Chase Brown |
| enriched_logistic | RB24 | 4 | Rico Dowdle, Alvin Kamara, David Montgomery, Rachaad White | 4 | Ashton Jeanty, J.K. Dobbins, Bucky Irving, Omarion Hampton |
| enriched_logistic | RB36 | 6 | Rachaad White, Isiah Pacheco, Tyler Allgeier, Brian Robinson, Devin Singletary | 6 | TreVeyon Henderson, Tyrone Tracy Jr., Bucky Irving, Jacory Croskey-Merritt, Omarion Hampton |
| enriched_logistic | WR12 | 3 | CeeDee Lamb, Davante Adams, Courtland Sutton | 3 | Rashee Rice, Garrett Wilson, Drake London |
| enriched_logistic | WR24 | 6 | Jakobi Meyers, Michael Pittman, DJ Moore, Mike Evans, DK Metcalf | 6 | Tee Higgins, Wan'Dale Robinson, Terry McLaurin, Tetairoa McMillan, Rome Odunze |
| enriched_logistic | WR36 | 9 | Michael Pittman, DJ Moore, Cooper Kupp, Tank Dell, Chris Godwin Jr. | 9 | Christian Watson, Quentin Johnston, Jauan Jennings, Alec Pierce, Emeka Egbuka |
| enriched_logistic | TE6 | 3 | Travis Kelce, Sam LaPorta, Jake Ferguson | 3 | Dallas Goedert, Tucker Kraft, Brock Bowers |
| enriched_logistic | TE12 | 4 | Jake Ferguson, Mark Andrews, David Njoku, Evan Engram | 4 | Juwan Johnson, Tucker Kraft, Tyler Warren, Brock Bowers |
| enriched_logistic | TE18 | 5 | Mark Andrews, David Njoku, Evan Engram, T.J. Hockenson, Cole Kmet | 5 | Brenton Strange, Tyler Warren, Harold Fannin Jr., Brock Bowers, Colston Loveland |
| enriched_linear_points | overall top 24 | 15 | Wan'Dale Robinson, George Pickens, Michael Wilson, Emeka Egbuka, Courtland Sutton | 15 | Christian McCaffrey, Brock Bowers, Rashee Rice, Bijan Robinson, Jahmyr Gibbs |
| enriched_linear_points | overall top 50 | 29 | Michael Wilson, Emeka Egbuka, Courtland Sutton, Tyler Warren, Jakobi Meyers | 29 | Dallas Goedert, Rashee Rice, Bijan Robinson, Jahmyr Gibbs, Chase Brown |
| enriched_linear_points | overall top 100 | 41 | Michael Pittman, Harold Fannin Jr., Jake Ferguson, Khalil Shakir, Rashid Shaheed | 41 | Sam LaPorta, Tucker Kraft, Malik Nabers, Kyren Williams, Javonte Williams |
| enriched_linear_points | QB12 | 10 | Jameis Winston, Aaron Rodgers, Sam Howell, Josh Johnson, Blake Bortles | 10 | Patrick Mahomes, Daniel Jones, Trevor Lawrence, Caleb Williams, Jayden Daniels |
| enriched_linear_points | RB12 | 7 | Kenneth Gainwell, Ashton Jeanty, RJ Harvey, Tyjae Spears, Michael Carter | 7 | Kyren Williams, Travis Etienne, Jonathan Taylor, Breece Hall, Saquon Barkley |
| enriched_linear_points | RB24 | 12 | Kenneth Gainwell, RJ Harvey, Tyjae Spears, Michael Carter, Tyrone Tracy Jr. | 12 | Aaron Jones, Jonathan Taylor, Breece Hall, Rhamondre Stevenson, Saquon Barkley |
| enriched_linear_points | RB36 | 11 | RJ Harvey, Tyjae Spears, Michael Carter, Dylan Sampson, Rachaad White | 11 | Josh Jacobs, Quinshon Judkins, Tony Pollard, James Cook, Kenneth Walker III |
| enriched_linear_points | WR12 | 4 | Wan'Dale Robinson, Michael Wilson, Emeka Egbuka, Courtland Sutton | 4 | Zay Flowers, Drake London, Rashee Rice, Garrett Wilson |
| enriched_linear_points | WR24 | 7 | Michael Wilson, Emeka Egbuka, Jakobi Meyers, Michael Pittman, Jerry Jeudy | 7 | Jaylen Waddle, Tee Higgins, Rome Odunze, Rashee Rice, Garrett Wilson |
| enriched_linear_points | WR36 | 9 | Michael Pittman, Jerry Jeudy, Troy Franklin, Parker Washington, Khalil Shakir | 9 | Quentin Johnston, Alec Pierce, Rashee Rice, Jordan Addison, Mike Evans |
| enriched_linear_points | TE6 | 4 | Tyler Warren, Travis Kelce, Dalton Schultz, Harold Fannin Jr. | 4 | Brock Bowers, Dallas Goedert, George Kittle, Tucker Kraft |
| enriched_linear_points | TE12 | 3 | Harold Fannin Jr., Jake Ferguson, Cade Otton | 3 | George Kittle, Sam LaPorta, Tucker Kraft |
| enriched_linear_points | TE18 | 4 | Chig Okonkwo, Evan Engram, Theo Johnson, Mark Andrews | 4 | Brenton Strange, Sam LaPorta, Dalton Kincaid, Tucker Kraft |

## TE35 Watch Band
| Model | TE rank | Player | Score | Current TE rank | Missing % |
|---|---|---|---|---|---|
| enriched_logistic | 30 | Isaiah Likely | 23.84 | 40 | 28.7% |
| enriched_logistic | 31 | Darren Fells | 23.68 |  | 27.6% |
| enriched_logistic | 32 | Noah Gray | 22.21 |  | 24.1% |
| enriched_logistic | 33 | Tyler Warren | 22.14 | 8 | 85.1% |
| enriched_logistic | 34 | Davis Allen | 21.46 | 57 | 39.1% |
| enriched_logistic | 35 | Tommy Tremble | 20.75 | 44 | 24.1% |
| enriched_logistic | 36 | Tyler Conklin | 20.66 |  | 19.5% |
| enriched_logistic | 37 | Harold Fannin Jr. | 20.56 | 16 | 85.1% |
| enriched_logistic | 38 | Ryan Izzo | 19.99 |  | 41.4% |
| enriched_logistic | 39 | Darnell Washington | 19.38 | 36 | 42.5% |
| enriched_logistic | 40 | Daniel Bellinger | 19.10 | 42 | 21.8% |
| enriched_linear_points | 30 | Dawson Knox | 228.98 | 37 | 24.1% |
| enriched_linear_points | 31 | Jake Tonges | 227.46 | 33 | 43.7% |
| enriched_linear_points | 32 | Tucker Kraft | 222.57 | 4 | 39.1% |
| enriched_linear_points | 33 | David Njoku | 222.20 | 34 | 19.5% |
| enriched_linear_points | 34 | Cole Kmet | 221.49 | 38 | 24.1% |
| enriched_linear_points | 35 | Darnell Washington | 207.98 | 36 | 42.5% |
| enriched_linear_points | 36 | Mike Gesicki | 196.44 | 29 | 24.1% |
| enriched_linear_points | 37 | Noah Fant | 188.00 | 49 | 24.1% |
| enriched_linear_points | 38 | Tommy Tremble | 173.18 | 44 | 24.1% |
| enriched_linear_points | 39 | Elijah Higgins | 172.59 |  | 42.5% |
| enriched_linear_points | 40 | Noah Gray | 171.90 |  | 24.1% |

# PPR Review Boards

## Current Pigskin Top 50 Overall
| Rank | Player | Pos | Team | Score | Pos rank |
|---|---|---|---|---|---|
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
| 14 | Jahmyr Gibbs | RB | DET | 93.00 | 3 |
| 15 | Garrett Wilson | WR | NYJ | 93.00 | 6 |
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
| 27 | Tucker Kraft | TE | GB | 88.00 | 4 |
| 28 | James Cook | RB | BUF | 88.00 | 6 |
| 29 | Zay Flowers | WR | BAL | 87.50 | 12 |
| 30 | Jordan Love | QB | GB | 87.00 | 8 |
| 31 | George Pickens | WR | DAL | 86.90 | 13 |
| 32 | Sam LaPorta | TE | DET | 86.00 | 5 |
| 33 | Kyren Williams | RB | LAR | 86.00 | 7 |
| 34 | Dak Prescott | QB | DAL | 86.00 | 9 |
| 35 | Nico Collins | WR | HOU | 86.00 | 14 |
| 36 | Davante Adams | WR | LAR | 85.10 | 15 |
| 37 | Dallas Goedert | TE | PHI | 85.00 | 6 |
| 38 | Caleb Williams | QB | CHI | 85.00 | 10 |
| 39 | Malik Nabers | WR | NYG | 84.50 | 16 |
| 40 | Kyle Pitts | TE | ATL | 84.00 | 7 |
| 41 | Saquon Barkley | RB | PHI | 84.00 | 8 |
| 42 | Bo Nix | QB | DEN | 84.00 | 11 |
| 43 | Travis Kelce | TE | KC | 83.00 | 8 |
| 44 | Daniel Jones | QB | IND | 83.00 | 12 |
| 45 | Wan'Dale Robinson | WR | TEN | 83.00 | 17 |
| 46 | Tetairoa McMillan | WR | CAR | 82.20 | 18 |
| 47 | Chase Brown | RB | CIN | 82.00 | 9 |
| 48 | Justin Herbert | QB | LAC | 82.00 | 13 |
| 49 | Rome Odunze | WR | CHI | 81.50 | 19 |
| 50 | Lamar Jackson | QB | BAL | 81.00 | 14 |

## BQML Logistic Top 50 Overall
| Logistic rank | Player | Pos | Team | Score | Current rank | Delta | Missing % |
|---|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey | RB | SF | 99.80 | 3 | +2 | 14.9% |
| 2 | Jonathan Taylor | RB | IND | 99.55 | 19 | +17 | 21.8% |
| 3 | Bijan Robinson | RB | ATL | 99.54 | 9 | +6 | 32.2% |
| 4 | Saquon Barkley | RB | PHI | 99.43 | 41 | +37 | 17.2% |
| 5 | Kyren Williams | RB | LAR | 99.39 | 33 | +28 | 21.8% |
| 6 | Derrick Henry | RB | BAL | 99.30 | 87 | +81 | 14.9% |
| 7 | Jahmyr Gibbs | RB | DET | 99.26 | 14 | +7 | 32.2% |
| 8 | James Cook | RB | BUF | 99.16 | 28 | +20 | 21.8% |
| 9 | Travis Etienne | RB | NO | 99.03 | 60 | +51 | 21.8% |
| 10 | De'Von Achane | RB | MIA | 98.88 | 21 | +11 | 32.2% |
| 11 | Breece Hall | RB | NYJ | 98.68 | 70 | +59 | 21.8% |
| 12 | Josh Jacobs | RB | GB | 98.15 | 56 | +44 | 17.2% |
| 13 | Javonte Williams | RB | DAL | 97.72 | 53 | +40 | 21.8% |
| 14 | Tony Pollard | RB | TEN | 97.32 | 140 | +126 | 17.2% |
| 15 | D'Andre Swift | RB | CHI | 96.74 | 72 | +57 | 19.5% |
| 16 | Kenneth Walker III | RB | KC | 96.61 | 129 | +113 | 21.8% |
| 17 | Jaylen Warren | RB | PIT | 95.02 | 83 | +66 | 21.8% |
| 18 | Chase Brown | RB | CIN | 94.20 | 47 | +29 | 32.2% |
| 19 | Rico Dowdle | RB | PIT | 94.06 | 97 | +78 | 25.3% |
| 20 | Alvin Kamara | RB | NO | 93.38 | 144 | +124 | 17.2% |
| 21 | Puka Nacua | WR | LAR | 91.99 | 5 | -16 | 32.2% |
| 22 | David Montgomery | RB | HOU | 91.73 | 153 | +131 | 14.9% |
| 23 | Rachaad White | RB | WAS | 91.65 | 148 | +125 | 21.8% |
| 24 | Ja'Marr Chase | WR | CIN | 91.60 | 6 | -18 | 19.5% |
| 25 | Josh Allen | QB | BUF | 91.43 | 2 | -23 | 20.7% |
| 26 | Amon-Ra St. Brown | WR | DET | 90.98 | 8 | -18 | 21.8% |
| 27 | Jalen Hurts | QB | PHI | 90.74 | 13 | -14 | 20.7% |
| 28 | Aaron Jones | RB | MIN | 90.36 | 113 | +85 | 17.2% |
| 29 | Isiah Pacheco | RB | DET | 89.24 | 194 | +165 | 21.8% |
| 30 | Rhamondre Stevenson | RB | NE | 88.62 | 116 | +86 | 21.8% |
| 31 | Zach Charbonnet | RB | SEA | 87.74 | 137 | +106 | 32.2% |
| 32 | Justin Jefferson | WR | MIN | 87.68 | 24 | -8 | 19.5% |
| 33 | CeeDee Lamb | WR | DAL | 86.91 | 26 | -7 | 19.5% |
| 34 | Ashton Jeanty | RB | LV | 86.89 | 80 | +46 | 85.1% |
| 35 | J.K. Dobbins | RB | DEN | 83.04 | 108 | +73 | 21.8% |
| 36 | Trey McBride | TE | ARI | 83.02 | 4 | -32 | 26.4% |
| 37 | Lamar Jackson | QB | BAL | 82.69 | 50 | +13 | 16.1% |
| 38 | Chuba Hubbard | RB | CAR | 81.34 | 167 | +129 | 21.8% |
| 39 | Davante Adams | WR | LAR | 80.48 | 36 | -3 | 17.2% |
| 40 | Kenneth Gainwell | RB | TB | 80.08 | 121 | +81 | 19.5% |
| 41 | Justin Fields | QB | KC | 79.51 | 200 | +159 | 25.3% |
| 42 | Chris Olave | WR | NO | 78.22 | 20 | -22 | 26.4% |
| 43 | A.J. Brown | WR | NE | 76.88 | 23 | -20 | 21.8% |
| 44 | George Pickens | WR | DAL | 75.51 | 31 | -13 | 21.8% |
| 45 | Zay Flowers | WR | BAL | 75.24 | 29 | -16 | 32.2% |
| 46 | Trevor Lawrence | QB | JAX | 75.24 | 22 | -24 | 25.3% |
| 47 | Jaxon Smith-Njigba | WR | SEA | 75.24 | 1 | -46 | 36.8% |
| 48 | Tyler Allgeier | RB | ARI | 74.50 | 202 | +154 | 21.8% |
| 49 | Travis Kelce | TE | KC | 73.49 | 43 | -6 | 17.2% |
| 50 | Justin Herbert | QB | LAC | 73.27 | 48 | -2 | 20.7% |

## BQML Linear Points Top 50 Overall
| Linear rank | Player | Pos | Team | Score | Current rank | Delta | Missing % |
|---|---|---|---|---|---|---|---|
| 1 | Ja'Marr Chase | WR | CIN | 855.78 | 6 | +5 | 19.5% |
| 2 | Amon-Ra St. Brown | WR | DET | 799.96 | 8 | +6 | 21.8% |
| 3 | Trey McBride | TE | ARI | 791.12 | 4 | +1 | 26.4% |
| 4 | Puka Nacua | WR | LAR | 769.90 | 5 | +1 | 32.2% |
| 5 | Jaxon Smith-Njigba | WR | SEA | 764.71 | 1 | -4 | 36.8% |
| 6 | Chris Olave | WR | NO | 726.29 | 20 | +14 | 26.4% |
| 7 | Wan'Dale Robinson | WR | TEN | 654.20 | 45 | +38 | 21.8% |
| 8 | Justin Jefferson | WR | MIN | 653.50 | 24 | +16 | 19.5% |
| 9 | George Pickens | WR | DAL | 641.55 | 31 | +22 | 21.8% |
| 10 | Michael Wilson | WR | ARI | 587.90 | 77 | +67 | 36.8% |
| 11 | Emeka Egbuka | WR | TB | 582.38 | 67 | +56 | 85.1% |
| 12 | Courtland Sutton | WR | DEN | 577.66 | 62 | +50 | 14.9% |
| 13 | A.J. Brown | WR | NE | 567.29 | 23 | +10 | 21.8% |
| 14 | Tetairoa McMillan | WR | CAR | 565.42 | 46 | +32 | 85.1% |
| 15 | Nico Collins | WR | HOU | 565.22 | 35 | +20 | 21.8% |
| 16 | Zay Flowers | WR | BAL | 550.73 | 29 | +13 | 32.2% |
| 17 | Kyle Pitts | TE | ATL | 549.36 | 40 | +23 | 21.8% |
| 18 | CeeDee Lamb | WR | DAL | 549.08 | 26 | +8 | 19.5% |
| 19 | Davante Adams | WR | LAR | 535.11 | 36 | +17 | 17.2% |
| 20 | Drake London | WR | ATL | 533.13 | 11 | -9 | 24.1% |
| 21 | DeVonta Smith | WR | PHI | 526.98 | 51 | +30 | 26.4% |
| 22 | Tyler Warren | TE | IND | 512.12 | 52 | +30 | 85.1% |
| 23 | Jakobi Meyers | WR | JAX | 510.32 | 68 | +45 | 14.9% |
| 24 | Michael Pittman | WR | PIT | 507.47 | 126 | +102 | 21.8% |
| 25 | Travis Kelce | TE | KC | 496.31 | 43 | +18 | 17.2% |
| 26 | Jerry Jeudy | WR | CLE | 491.48 | 106 | +80 | 21.8% |
| 27 | Dalton Schultz | TE | HOU | 489.24 | 69 | +42 | 21.8% |
| 28 | Ladd McConkey | WR | LAC | 487.11 | 86 | +58 | 85.1% |
| 29 | Jameson Williams | WR | DET | 483.70 | 71 | +42 | 21.8% |
| 30 | Harold Fannin Jr. | TE | CLE | 482.99 | 89 | +59 | 85.1% |
| 31 | Christian McCaffrey | RB | SF | 479.48 | 3 | -28 | 14.9% |
| 32 | Juwan Johnson | TE | NO | 476.19 | 75 | +43 | 26.4% |
| 33 | Jake Ferguson | TE | DAL | 475.85 | 82 | +49 | 26.4% |
| 34 | Troy Franklin | WR | DEN | 473.85 | 102 | +68 | 85.1% |
| 35 | Jaylen Waddle | WR | DEN | 467.74 | 55 | +20 | 21.8% |
| 36 | Tee Higgins | WR | CIN | 460.01 | 58 | +22 | 26.4% |
| 37 | DK Metcalf | WR | PIT | 458.85 | 88 | +51 | 21.8% |
| 38 | Parker Washington | WR | JAX | 446.06 | 99 | +61 | 36.8% |
| 39 | Khalil Shakir | WR | BUF | 445.82 | 114 | +75 | 21.8% |
| 40 | Tre Tucker | WR | LV | 431.41 | 95 | +55 | 32.2% |
| 41 | Jauan Jennings | WR | MIN | 428.29 | 92 | +51 | 19.5% |
| 42 | Rashid Shaheed | WR | SEA | 424.52 | 150 | +108 | 21.8% |
| 43 | Rome Odunze | WR | CHI | 422.07 | 49 | +6 | 85.1% |
| 44 | Brian Thomas Jr. | WR | JAX | 412.93 | 122 | +78 | 85.1% |
| 45 | Hunter Henry | TE | NE | 407.56 | 64 | +19 | 21.8% |
| 46 | Elic Ayomanor | WR | TEN | 407.03 | 109 | +63 | 85.1% |
| 47 | Josh Downs | WR | IND | 406.77 | 149 | +102 | 36.8% |
| 48 | Brock Bowers | TE | LV | 403.74 | 12 | -36 | 85.1% |
| 49 | Romeo Doubs | WR | NE | 401.94 | 94 | +45 | 19.5% |
| 50 | Quentin Johnston | WR | LAC | 401.45 | 78 | +28 | 32.2% |

## Side-by-Side Top 100 Overall
| Rank | Current | Pos | Logistic | Pos | Score | Linear | Pos | Score |
|---|---|---|---|---|---|---|---|---|
| 1 | Jaxon Smith-Njigba | WR | Christian McCaffrey | RB | 99.80 | Ja'Marr Chase | WR | 855.78 |
| 2 | Josh Allen | QB | Jonathan Taylor | RB | 99.55 | Amon-Ra St. Brown | WR | 799.96 |
| 3 | Christian McCaffrey | RB | Bijan Robinson | RB | 99.54 | Trey McBride | TE | 791.12 |
| 4 | Trey McBride | TE | Saquon Barkley | RB | 99.43 | Puka Nacua | WR | 769.90 |
| 5 | Puka Nacua | WR | Kyren Williams | RB | 99.39 | Jaxon Smith-Njigba | WR | 764.71 |
| 6 | Ja'Marr Chase | WR | Derrick Henry | RB | 99.30 | Chris Olave | WR | 726.29 |
| 7 | Drake Maye | QB | Jahmyr Gibbs | RB | 99.26 | Wan'Dale Robinson | WR | 654.20 |
| 8 | Amon-Ra St. Brown | WR | James Cook | RB | 99.16 | Justin Jefferson | WR | 653.50 |
| 9 | Bijan Robinson | RB | Travis Etienne | RB | 99.03 | George Pickens | WR | 641.55 |
| 10 | Patrick Mahomes | QB | De'Von Achane | RB | 98.88 | Michael Wilson | WR | 587.90 |
| 11 | Drake London | WR | Breece Hall | RB | 98.68 | Emeka Egbuka | WR | 582.38 |
| 12 | Brock Bowers | TE | Josh Jacobs | RB | 98.15 | Courtland Sutton | WR | 577.66 |
| 13 | Jalen Hurts | QB | Javonte Williams | RB | 97.72 | A.J. Brown | WR | 567.29 |
| 14 | Jahmyr Gibbs | RB | Tony Pollard | RB | 97.32 | Tetairoa McMillan | WR | 565.42 |
| 15 | Garrett Wilson | WR | D'Andre Swift | RB | 96.74 | Nico Collins | WR | 565.22 |
| 16 | Brock Purdy | QB | Kenneth Walker III | RB | 96.61 | Zay Flowers | WR | 550.73 |
| 17 | Rashee Rice | WR | Jaylen Warren | RB | 95.02 | Kyle Pitts | TE | 549.36 |
| 18 | George Kittle | TE | Chase Brown | RB | 94.20 | CeeDee Lamb | WR | 549.08 |
| 19 | Jonathan Taylor | RB | Rico Dowdle | RB | 94.06 | Davante Adams | WR | 535.11 |
| 20 | Chris Olave | WR | Alvin Kamara | RB | 93.38 | Drake London | WR | 533.13 |
| 21 | De'Von Achane | RB | Puka Nacua | WR | 91.99 | DeVonta Smith | WR | 526.98 |
| 22 | Trevor Lawrence | QB | David Montgomery | RB | 91.73 | Tyler Warren | TE | 512.12 |
| 23 | A.J. Brown | WR | Rachaad White | RB | 91.65 | Jakobi Meyers | WR | 510.32 |
| 24 | Justin Jefferson | WR | Ja'Marr Chase | WR | 91.60 | Michael Pittman | WR | 507.47 |
| 25 | Matthew Stafford | QB | Josh Allen | QB | 91.43 | Travis Kelce | TE | 496.31 |
| 26 | CeeDee Lamb | WR | Amon-Ra St. Brown | WR | 90.98 | Jerry Jeudy | WR | 491.48 |
| 27 | Tucker Kraft | TE | Jalen Hurts | QB | 90.74 | Dalton Schultz | TE | 489.24 |
| 28 | James Cook | RB | Aaron Jones | RB | 90.36 | Ladd McConkey | WR | 487.11 |
| 29 | Zay Flowers | WR | Isiah Pacheco | RB | 89.24 | Jameson Williams | WR | 483.70 |
| 30 | Jordan Love | QB | Rhamondre Stevenson | RB | 88.62 | Harold Fannin Jr. | TE | 482.99 |
| 31 | George Pickens | WR | Zach Charbonnet | RB | 87.74 | Christian McCaffrey | RB | 479.48 |
| 32 | Sam LaPorta | TE | Justin Jefferson | WR | 87.68 | Juwan Johnson | TE | 476.19 |
| 33 | Kyren Williams | RB | CeeDee Lamb | WR | 86.91 | Jake Ferguson | TE | 475.85 |
| 34 | Dak Prescott | QB | Ashton Jeanty | RB | 86.89 | Troy Franklin | WR | 473.85 |
| 35 | Nico Collins | WR | J.K. Dobbins | RB | 83.04 | Jaylen Waddle | WR | 467.74 |
| 36 | Davante Adams | WR | Trey McBride | TE | 83.02 | Tee Higgins | WR | 460.01 |
| 37 | Dallas Goedert | TE | Lamar Jackson | QB | 82.69 | DK Metcalf | WR | 458.85 |
| 38 | Caleb Williams | QB | Chuba Hubbard | RB | 81.34 | Parker Washington | WR | 446.06 |
| 39 | Malik Nabers | WR | Davante Adams | WR | 80.48 | Khalil Shakir | WR | 445.82 |
| 40 | Kyle Pitts | TE | Kenneth Gainwell | RB | 80.08 | Tre Tucker | WR | 431.41 |
| 41 | Saquon Barkley | RB | Justin Fields | QB | 79.51 | Jauan Jennings | WR | 428.29 |
| 42 | Bo Nix | QB | Chris Olave | WR | 78.22 | Rashid Shaheed | WR | 424.52 |
| 43 | Travis Kelce | TE | A.J. Brown | WR | 76.88 | Rome Odunze | WR | 422.07 |
| 44 | Daniel Jones | QB | George Pickens | WR | 75.51 | Brian Thomas Jr. | WR | 412.93 |
| 45 | Wan'Dale Robinson | WR | Zay Flowers | WR | 75.24 | Hunter Henry | TE | 407.56 |
| 46 | Tetairoa McMillan | WR | Trevor Lawrence | QB | 75.24 | Elic Ayomanor | WR | 407.03 |
| 47 | Chase Brown | RB | Jaxon Smith-Njigba | WR | 75.24 | Josh Downs | WR | 406.77 |
| 48 | Justin Herbert | QB | Tyler Allgeier | RB | 74.50 | Brock Bowers | TE | 403.74 |
| 49 | Rome Odunze | WR | Travis Kelce | TE | 73.49 | Romeo Doubs | WR | 401.94 |
| 50 | Lamar Jackson | QB | Justin Herbert | QB | 73.27 | Quentin Johnston | WR | 401.45 |
| 51 | DeVonta Smith | WR | Quinshon Judkins | RB | 72.50 | Alec Pierce | WR | 400.19 |
| 52 | Tyler Warren | TE | Brian Robinson | RB | 72.26 | Dallas Goedert | TE | 385.88 |
| 53 | Javonte Williams | RB | Courtland Sutton | WR | 71.92 | DJ Moore | WR | 382.60 |
| 54 | Terry McLaurin | WR | Nico Collins | WR | 71.87 | Rashee Rice | WR | 379.23 |
| 55 | Jaylen Waddle | WR | Jakobi Meyers | WR | 71.81 | Cade Otton | TE | 378.51 |
| 56 | Josh Jacobs | RB | Patrick Mahomes | QB | 71.61 | Colston Loveland | TE | 374.85 |
| 57 | Jayden Daniels | QB | George Kittle | TE | 70.94 | Jordan Addison | WR | 372.65 |
| 58 | Tee Higgins | WR | Michael Pittman | WR | 70.48 | Bijan Robinson | RB | 372.43 |
| 59 | Dalton Kincaid | TE | DJ Moore | WR | 68.86 | Chig Okonkwo | TE | 361.16 |
| 60 | Travis Etienne | RB | DeVonta Smith | WR | 68.31 | Kenneth Gainwell | RB | 354.58 |
| 61 | Joe Burrow | QB | Baker Mayfield | QB | 68.20 | Jahmyr Gibbs | RB | 348.94 |
| 62 | Courtland Sutton | WR | Rashee Rice | WR | 67.80 | Evan Engram | TE | 345.57 |
| 63 | Alec Pierce | WR | Tyjae Spears | RB | 67.71 | Marquise Brown | WR | 339.82 |
| 64 | Hunter Henry | TE | Devin Singletary | RB | 67.19 | Theo Johnson | TE | 339.49 |
| 65 | Omarion Hampton | RB | James Conner | RB | 67.17 | Chase Brown | RB | 338.15 |
| 66 | Jared Goff | QB | Jaylen Waddle | WR | 66.91 | Darnell Mooney | WR | 335.42 |
| 67 | Emeka Egbuka | WR | C.J. Stroud | QB | 66.90 | Adonai Mitchell | WR | 334.55 |
| 68 | Jakobi Meyers | WR | Sam LaPorta | TE | 65.96 | George Kittle | TE | 333.10 |
| 69 | Dalton Schultz | TE | Jordan Mason | RB | 65.72 | Xavier Worthy | WR | 330.77 |
| 70 | Breece Hall | RB | Brock Purdy | QB | 65.25 | Chimere Dike | WR | 329.79 |
| 71 | Jameson Williams | WR | Mike Evans | WR | 64.92 | Cooper Kupp | WR | 322.37 |
| 72 | D'Andre Swift | RB | DK Metcalf | WR | 63.27 | Mark Andrews | TE | 321.85 |
| 73 | Jaxson Dart | QB | Garrett Wilson | WR | 62.92 | Oronde Gadsden II | TE | 315.19 |
| 74 | Mike Evans | WR | Drake London | WR | 62.39 | De'Von Achane | RB | 314.21 |
| 75 | Juwan Johnson | TE | Jake Ferguson | TE | 62.27 | Mack Hollins | WR | 307.05 |
| 76 | Baker Mayfield | QB | Jordan Addison | WR | 62.15 | Jayden Higgins | WR | 306.91 |
| 77 | Michael Wilson | WR | Cooper Kupp | WR | 62.11 | AJ Barner | TE | 305.95 |
| 78 | Quentin Johnston | WR | Wan'Dale Robinson | WR | 61.57 | T.J. Hockenson | TE | 304.66 |
| 79 | Colston Loveland | TE | Tank Dell | WR | 61.28 | Olamide Zaccheaus | WR | 303.50 |
| 80 | Ashton Jeanty | RB | Tee Higgins | WR | 61.01 | Mike Evans | WR | 298.90 |
| 81 | Christian Watson | WR | Woody Marks | RB | 60.86 | Darius Slayton | WR | 297.67 |
| 82 | Jake Ferguson | TE | Michael Wilson | WR | 60.54 | Mason Taylor | TE | 297.54 |
| 83 | Jaylen Warren | RB | Kyler Murray | QB | 59.31 | Garrett Wilson | WR | 296.37 |
| 84 | Jacoby Brissett | QB | Dak Prescott | QB | 59.20 | Brenton Strange | TE | 291.85 |
| 85 | Jordan Addison | WR | Daniel Jones | QB | 59.09 | Terry McLaurin | WR | 290.52 |
| 86 | Ladd McConkey | WR | Kyle Pitts | TE | 58.69 | Xavier Legette | WR | 290.13 |
| 87 | Derrick Henry | RB | TreVeyon Henderson | RB | 58.50 | Malik Washington | WR | 286.80 |
| 88 | DK Metcalf | WR | Tyrone Tracy Jr. | RB | 58.34 | Andrei Iosivas | WR | 273.84 |
| 89 | Harold Fannin Jr. | TE | Bucky Irving | RB | 57.11 | Keon Coleman | WR | 272.95 |
| 90 | Cam Skattebo | RB | Jerome Ford | RB | 56.90 | Christian Watson | WR | 269.66 |
| 91 | Kyler Murray | QB | Mark Andrews | TE | 56.60 | Colby Parkinson | TE | 268.75 |
| 92 | Jauan Jennings | WR | Chris Godwin Jr. | WR | 56.16 | Xavier Hutchinson | WR | 268.34 |
| 93 | Bucky Irving | RB | Terry McLaurin | WR | 55.63 | Luther Burden III | WR | 264.91 |
| 94 | Romeo Doubs | WR | Michael Carter | RB | 55.31 | Calvin Austin III | WR | 261.37 |
| 95 | Tre Tucker | WR | Emanuel Wilson | RB | 54.56 | Ashton Jeanty | RB | 254.23 |
| 96 | Brenton Strange | TE | Dallas Goedert | TE | 54.34 | Jalen Nailor | WR | 251.67 |
| 97 | Rico Dowdle | RB | Romeo Doubs | WR | 53.98 | Pat Freiermuth | TE | 250.19 |
| 98 | C.J. Stroud | QB | Jared Goff | QB | 53.82 | Ryan Flournoy | WR | 250.17 |
| 99 | Parker Washington | WR | Chris Rodriguez Jr. | RB | 53.75 | Ricky Pearsall | WR | 249.51 |
| 100 | Quinshon Judkins | RB | Dalton Schultz | TE | 52.21 | Kendrick Bourne | WR | 247.41 |

## QB Board Top 45
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Josh Allen | 98.50 | Josh Allen | 91.43 | Jameis Winston | 23.39 |
| 2 | Drake Maye | 96.00 | Jalen Hurts | 90.74 | Aaron Rodgers | 18.02 |
| 3 | Patrick Mahomes | 95.00 | Lamar Jackson | 82.69 | Sam Howell | 17.12 |
| 4 | Jalen Hurts | 94.00 | Justin Fields | 79.51 | Josh Johnson | 16.91 |
| 5 | Brock Purdy | 92.50 | Trevor Lawrence | 75.24 | Brock Purdy | 15.84 |
| 6 | Trevor Lawrence | 90.00 | Justin Herbert | 73.27 | Matthew Stafford | 15.51 |
| 7 | Matthew Stafford | 88.50 | Patrick Mahomes | 71.61 | Blake Bortles | 15.09 |
| 8 | Jordan Love | 87.00 | Baker Mayfield | 68.20 | Deshaun Watson | 14.51 |
| 9 | Dak Prescott | 86.00 | C.J. Stroud | 66.90 | Jared Goff | 14.39 |
| 10 | Caleb Williams | 85.00 | Brock Purdy | 65.25 | Tommy DeVito | 13.63 |
| 11 | Bo Nix | 84.00 | Kyler Murray | 59.31 | Joe Burrow | 12.90 |
| 12 | Daniel Jones | 83.00 | Dak Prescott | 59.20 | Malik Willis | 12.66 |
| 13 | Justin Herbert | 82.00 | Daniel Jones | 59.09 | Will Levis | 12.65 |
| 14 | Lamar Jackson | 81.00 | Jared Goff | 53.82 | Brandon Allen | 12.58 |
| 15 | Jayden Daniels | 79.00 | Geno Smith | 51.55 | Jake Browning | 12.43 |
| 16 | Joe Burrow | 78.00 | Bryce Young | 51.00 | Aidan O'Connell | 12.35 |
| 17 | Jared Goff | 77.00 | Joe Burrow | 49.86 | Ben Roethlisberger | 12.23 |
| 18 | Jaxson Dart | 75.00 | Matthew Stafford | 49.57 | Davis Mills | 11.91 |
| 19 | Baker Mayfield | 74.00 | Jordan Love | 47.95 | Joe Flacco | 10.32 |
| 20 | Jacoby Brissett | 72.00 | Marcus Mariota | 45.54 | Kyler Murray | 10.19 |
| 21 | Kyler Murray | 70.00 | Tua Tagovailoa | 45.24 | Bailey Zappe | 9.90 |
| 22 | C.J. Stroud | 68.00 | Sam Darnold | 45.24 | Tua Tagovailoa | 9.34 |
| 23 | Sam Darnold | 66.00 | Blake Bortles | 44.41 | Carson Wentz | 8.79 |
| 24 | Aaron Rodgers | 64.00 | Anthony Richardson | 43.52 | Jordan Love | 8.78 |
| 25 | Tyler Shough | 62.00 | Sam Howell | 41.18 | Kirk Cousins | 8.77 |
| 26 | Bryce Young | 60.00 | Deshaun Watson | 39.66 | Sam Ehlinger | 8.08 |
| 27 | Malik Willis | 58.00 | Carson Wentz | 39.13 | Trevor Siemian | 7.88 |
| 28 | Geno Smith | 55.00 | Joe Flacco | 37.92 | Skylar Thompson | 7.84 |
| 29 | Tua Tagovailoa | 54.00 | Will Levis | 37.42 | Sam Darnold | 7.31 |
| 30 | Cam Ward | 50.00 | Mac Jones | 36.88 | Tyrod Taylor | 7.15 |
| 31 | Shedeur Sanders | 48.00 | Tyler Huntley | 36.75 | Case Keenum | 6.57 |
| 32 | Fernando Mendoza | 45.00 | Jacoby Brissett | 35.65 | Mitchell Trubisky | 5.58 |
| 33 | Justin Fields | 40.00 | Kirk Cousins | 33.48 | Easton Stick | 4.94 |
| 34 | Jameis Winston | 38.00 | Aaron Rodgers | 33.21 | Jacoby Brissett | 4.80 |
| 35 | Carson Wentz | 35.00 | Tyson Bagent | 32.66 | Andy Dalton | 4.37 |
| 36 | J.J. McCarthy | 34.00 | Ben Roethlisberger | 31.70 | Teddy Bridgewater | 4.24 |
| 37 | Marcus Mariota | 32.00 | Mason Rudolph | 30.84 | Mason Rudolph | 4.10 |
| 38 | Mac Jones | 30.00 | Tommy DeVito | 30.29 | Patrick Mahomes | 3.85 |
| 39 | Davis Mills | 28.00 | Aidan O'Connell | 29.65 | Tyler Huntley | 3.81 |
| 40 | Joe Flacco | 26.00 | Tyrod Taylor | 28.79 | Kyle Allen | 3.56 |
| 41 | Spencer Rattler | 24.00 | Trey Lance | 28.43 | Anthony Richardson | 3.21 |
| 42 | Jake Browning | 22.00 | Drake Maye | 27.68 | Drew Lock | 2.58 |
| 43 | Quinn Ewers | 18.00 | Jameis Winston | 26.92 | Geno Smith | 2.23 |
| 44 | Josh Johnson | 15.00 | Davis Mills | 25.89 | Spencer Rattler | 2.16 |
| 45 | Tyler Huntley | 12.00 | Zach Wilson | 25.62 | Dak Prescott | 2.13 |

## RB Board Top 80
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey | 98.00 | Christian McCaffrey | 99.80 | Christian McCaffrey | 479.48 |
| 2 | Bijan Robinson | 95.00 | Jonathan Taylor | 99.55 | Bijan Robinson | 372.43 |
| 3 | Jahmyr Gibbs | 93.00 | Bijan Robinson | 99.54 | Kenneth Gainwell | 354.58 |
| 4 | Jonathan Taylor | 91.00 | Saquon Barkley | 99.43 | Jahmyr Gibbs | 348.94 |
| 5 | De'Von Achane | 90.00 | Kyren Williams | 99.39 | Chase Brown | 338.15 |
| 6 | James Cook | 88.00 | Derrick Henry | 99.30 | De'Von Achane | 314.21 |
| 7 | Kyren Williams | 86.00 | Jahmyr Gibbs | 99.26 | Ashton Jeanty | 254.23 |
| 8 | Saquon Barkley | 84.00 | James Cook | 99.16 | RJ Harvey | 223.06 |
| 9 | Chase Brown | 82.00 | Travis Etienne | 99.03 | Tyjae Spears | 204.37 |
| 10 | Javonte Williams | 80.00 | De'Von Achane | 98.88 | Michael Carter | 172.50 |
| 11 | Josh Jacobs | 79.00 | Breece Hall | 98.68 | Tyrone Tracy Jr. | 168.72 |
| 12 | Travis Etienne | 78.00 | Josh Jacobs | 98.15 | Dylan Sampson | 161.41 |
| 13 | Omarion Hampton | 77.00 | Javonte Williams | 97.72 | Rico Dowdle | 161.25 |
| 14 | Breece Hall | 76.00 | Tony Pollard | 97.32 | Rachaad White | 152.01 |
| 15 | D'Andre Swift | 75.00 | D'Andre Swift | 96.74 | Kyren Williams | 148.93 |
| 16 | Ashton Jeanty | 73.00 | Kenneth Walker III | 96.61 | Javonte Williams | 146.89 |
| 17 | Jaylen Warren | 72.00 | Jaylen Warren | 95.02 | Travis Etienne | 143.00 |
| 18 | Derrick Henry | 71.00 | Chase Brown | 94.20 | Brashard Smith | 142.47 |
| 19 | Cam Skattebo | 70.00 | Rico Dowdle | 94.06 | D'Andre Swift | 140.86 |
| 20 | Bucky Irving | 69.00 | Alvin Kamara | 93.38 | Tyler Badie | 140.83 |
| 21 | Rico Dowdle | 68.00 | David Montgomery | 91.73 | Jaylen Warren | 140.69 |
| 22 | Quinshon Judkins | 67.00 | Rachaad White | 91.65 | TreVeyon Henderson | 140.17 |
| 23 | TreVeyon Henderson | 66.00 | Aaron Jones | 90.36 | Omarion Hampton | 139.89 |
| 24 | J.K. Dobbins | 65.00 | Isiah Pacheco | 89.24 | Jerome Ford | 137.30 |
| 25 | Aaron Jones | 64.00 | Rhamondre Stevenson | 88.62 | Ty Johnson | 136.65 |
| 26 | Rhamondre Stevenson | 63.00 | Zach Charbonnet | 87.74 | Aaron Jones | 134.79 |
| 27 | Kenneth Gainwell | 62.00 | Ashton Jeanty | 86.89 | Jonathan Taylor | 133.89 |
| 28 | James Conner | 61.00 | J.K. Dobbins | 83.04 | Cam Skattebo | 133.52 |
| 29 | Kenneth Walker III | 60.00 | Chuba Hubbard | 81.34 | Breece Hall | 133.52 |
| 30 | Tyrone Tracy Jr. | 59.00 | Kenneth Gainwell | 80.08 | Jeremy McNichols | 131.84 |
| 31 | Zach Charbonnet | 58.00 | Tyler Allgeier | 74.50 | Chuba Hubbard | 127.34 |
| 32 | Tony Pollard | 57.00 | Quinshon Judkins | 72.50 | Alvin Kamara | 125.05 |
| 33 | Alvin Kamara | 56.00 | Brian Robinson | 72.26 | Rhamondre Stevenson | 124.38 |
| 34 | Rachaad White | 55.00 | Tyjae Spears | 67.71 | Saquon Barkley | 121.56 |
| 35 | David Montgomery | 54.00 | Devin Singletary | 67.19 | Justice Hill | 119.60 |
| 36 | Woody Marks | 53.00 | James Conner | 67.17 | Bucky Irving | 118.79 |
| 37 | RJ Harvey | 52.00 | Jordan Mason | 65.72 | Isaiah Davis | 112.83 |
| 38 | Kyle Monangai | 51.00 | Woody Marks | 60.86 | Josh Jacobs | 110.16 |
| 39 | Tyjae Spears | 50.00 | TreVeyon Henderson | 58.50 | Woody Marks | 106.19 |
| 40 | Chuba Hubbard | 49.00 | Tyrone Tracy Jr. | 58.34 | Quinshon Judkins | 97.46 |
| 41 | Jacory Croskey-Merritt | 48.00 | Bucky Irving | 57.11 | Tony Pollard | 92.02 |
| 42 | Jordan Mason | 47.00 | Jerome Ford | 56.90 | Kyle Monangai | 86.11 |
| 43 | Chris Rodriguez Jr. | 46.00 | Michael Carter | 55.31 | James Cook | 83.54 |
| 44 | Blake Corum | 45.00 | Emanuel Wilson | 54.56 | Kenneth Walker III | 80.79 |
| 45 | Trey Benson | 44.00 | Chris Rodriguez Jr. | 53.75 | Trey Benson | 78.96 |
| 46 | Kimani Vidal | 43.00 | RJ Harvey | 50.73 | Emari Demercado | 75.50 |
| 47 | Isiah Pacheco | 42.00 | Kyle Monangai | 49.47 | Devin Neal | 73.04 |
| 48 | Jawhar Jordan | 41.00 | Keaton Mitchell | 47.02 | Isiah Pacheco | 72.44 |
| 49 | Tyler Allgeier | 40.00 | Jacory Croskey-Merritt | 46.89 | Ameer Abdullah | 72.20 |
| 50 | Ty Johnson | 39.00 | Samaje Perine | 43.70 | Chris Brooks | 69.58 |
| 51 | Samaje Perine | 38.00 | Kimani Vidal | 43.56 | David Montgomery | 69.11 |
| 52 | Jaylen Wright | 37.00 | Omarion Hampton | 42.34 | Samaje Perine | 67.30 |
| 53 | Justice Hill | 36.00 | Emari Demercado | 39.52 | Zavier Scott | 61.34 |
| 54 | Bhayshul Tuten | 35.00 | Ty Johnson | 36.69 | Kimani Vidal | 57.49 |
| 55 | Michael Carter | 34.00 | AJ Dillon | 36.54 | Zach Charbonnet | 54.70 |
| 56 | Devin Singletary | 33.00 | Blake Corum | 36.35 | Will Shipley | 44.88 |
| 57 | Emanuel Wilson | 32.00 | Justice Hill | 36.03 | Rasheen Ali | 43.63 |
| 58 | Dylan Sampson | 31.00 | Jeremy McNichols | 35.59 | Emanuel Wilson | 40.96 |
| 59 | Kendre Miller | 30.00 | Cam Skattebo | 34.03 | Bhayshul Tuten | 39.14 |
| 60 | Phil Mafah | 28.00 | Kendre Miller | 33.55 | LeQuint Allen Jr. | 37.69 |
| 61 | Raheim Sanders | 27.00 | Sean Tucker | 33.33 | Ray Davis | 37.50 |
| 62 | Devin Neal | 26.00 | Malik Davis | 31.99 | Devin Singletary | 35.44 |
| 63 | Jeremy McNichols | 25.00 | Ty Chandler | 30.55 | Keaton Mitchell | 32.67 |
| 64 | Emari Demercado | 24.00 | Jaleel McLaughlin | 29.74 | James Conner | 30.52 |
| 65 | Keaton Mitchell | 23.00 | Tank Bigsby | 29.21 | Jawhar Jordan | 29.54 |
| 66 | Braelon Allen | 22.00 | Jaret Patterson | 28.33 | Jordan Mason | 29.10 |
| 67 | Isaiah Davis | 21.00 | Le'Veon Bell | 27.35 | Sean Tucker | 24.57 |
| 68 | Jaydon Blue | 20.00 | Elijah McGuire | 26.51 | Jaylen Wright | 21.51 |
| 69 | Jerome Ford | 19.00 | Ameer Abdullah | 24.32 | Ty Chandler | 20.09 |
| 70 | Brian Robinson | 18.00 | Chris Brooks | 22.97 | Blake Corum | 19.11 |
| 71 | Sean Tucker | 17.00 | Tyler Badie | 22.67 | Raheim Sanders | 17.72 |
| 72 | Jaret Patterson | 16.00 | Roschon Johnson | 21.05 | Phil Mafah | 17.35 |
| 73 | Brashard Smith | 15.00 | Ito Smith | 20.98 | J.K. Dobbins | 16.12 |
| 74 | Malik Davis | 14.00 | Dylan Sampson | 19.45 | Tyler Allgeier | 15.54 |
| 75 | Tank Bigsby | 13.00 | Dameon Pierce | 19.32 | Ollie Gordon II | 15.21 |
| 76 | Ray Davis | 12.00 | Bhayshul Tuten | 19.06 | Braelon Allen | 13.97 |
| 77 | DJ Giddens | 11.00 | Salvon Ahmed | 19.00 | Jaleel McLaughlin | 13.56 |
| 78 | Zavier Scott | 10.00 | Jalen Richard | 18.96 | Tyler Goodson | 10.09 |
| 79 | Jaleel McLaughlin | 9.00 | Elijah Mitchell | 17.87 | Corey Kiner | 9.91 |
| 80 | Ameer Abdullah | 8.00 | Pierre Strong | 17.76 | Kendre Miller | 9.87 |

## WR Board Top 100
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Jaxon Smith-Njigba | 98.50 | Puka Nacua | 91.99 | Ja'Marr Chase | 855.78 |
| 2 | Puka Nacua | 97.80 | Ja'Marr Chase | 91.60 | Amon-Ra St. Brown | 799.96 |
| 3 | Ja'Marr Chase | 96.50 | Amon-Ra St. Brown | 90.98 | Puka Nacua | 769.90 |
| 4 | Amon-Ra St. Brown | 95.90 | Justin Jefferson | 87.68 | Jaxon Smith-Njigba | 764.71 |
| 5 | Drake London | 94.20 | CeeDee Lamb | 86.91 | Chris Olave | 726.29 |
| 6 | Garrett Wilson | 93.00 | Davante Adams | 80.48 | Wan'Dale Robinson | 654.20 |
| 7 | Rashee Rice | 91.50 | Chris Olave | 78.22 | Justin Jefferson | 653.50 |
| 8 | Chris Olave | 90.80 | A.J. Brown | 76.88 | George Pickens | 641.55 |
| 9 | A.J. Brown | 89.90 | George Pickens | 75.51 | Michael Wilson | 587.90 |
| 10 | Justin Jefferson | 89.00 | Zay Flowers | 75.24 | Emeka Egbuka | 582.38 |
| 11 | CeeDee Lamb | 88.20 | Jaxon Smith-Njigba | 75.24 | Courtland Sutton | 577.66 |
| 12 | Zay Flowers | 87.50 | Courtland Sutton | 71.92 | A.J. Brown | 567.29 |
| 13 | George Pickens | 86.90 | Nico Collins | 71.87 | Tetairoa McMillan | 565.42 |
| 14 | Nico Collins | 86.00 | Jakobi Meyers | 71.81 | Nico Collins | 565.22 |
| 15 | Davante Adams | 85.10 | Michael Pittman | 70.48 | Zay Flowers | 550.73 |
| 16 | Malik Nabers | 84.50 | DJ Moore | 68.86 | CeeDee Lamb | 549.08 |
| 17 | Wan'Dale Robinson | 83.00 | DeVonta Smith | 68.31 | Davante Adams | 535.11 |
| 18 | Tetairoa McMillan | 82.20 | Rashee Rice | 67.80 | Drake London | 533.13 |
| 19 | Rome Odunze | 81.50 | Jaylen Waddle | 66.91 | DeVonta Smith | 526.98 |
| 20 | DeVonta Smith | 80.90 | Mike Evans | 64.92 | Jakobi Meyers | 510.32 |
| 21 | Terry McLaurin | 80.00 | DK Metcalf | 63.27 | Michael Pittman | 507.47 |
| 22 | Jaylen Waddle | 79.40 | Garrett Wilson | 62.92 | Jerry Jeudy | 491.48 |
| 23 | Tee Higgins | 78.80 | Drake London | 62.39 | Ladd McConkey | 487.11 |
| 24 | Courtland Sutton | 78.00 | Jordan Addison | 62.15 | Jameson Williams | 483.70 |
| 25 | Alec Pierce | 77.50 | Cooper Kupp | 62.11 | Troy Franklin | 473.85 |
| 26 | Emeka Egbuka | 76.90 | Wan'Dale Robinson | 61.57 | Jaylen Waddle | 467.74 |
| 27 | Jakobi Meyers | 76.20 | Tank Dell | 61.28 | Tee Higgins | 460.01 |
| 28 | Jameson Williams | 75.50 | Tee Higgins | 61.01 | DK Metcalf | 458.85 |
| 29 | Mike Evans | 74.80 | Michael Wilson | 60.54 | Parker Washington | 446.06 |
| 30 | Michael Wilson | 74.00 | Chris Godwin Jr. | 56.16 | Khalil Shakir | 445.82 |
| 31 | Quentin Johnston | 73.50 | Terry McLaurin | 55.63 | Tre Tucker | 431.41 |
| 32 | Christian Watson | 72.80 | Romeo Doubs | 53.98 | Jauan Jennings | 428.29 |
| 33 | Jordan Addison | 72.00 | Jerry Jeudy | 51.50 | Rashid Shaheed | 424.52 |
| 34 | Ladd McConkey | 71.50 | Brandon Aiyuk | 51.08 | Rome Odunze | 422.07 |
| 35 | DK Metcalf | 70.80 | Rashid Shaheed | 49.53 | Brian Thomas Jr. | 412.93 |
| 36 | Jauan Jennings | 69.50 | Jameson Williams | 48.89 | Elic Ayomanor | 407.03 |
| 37 | Romeo Doubs | 68.80 | Josh Downs | 47.26 | Josh Downs | 406.77 |
| 38 | Tre Tucker | 68.20 | Christian Watson | 46.13 | Romeo Doubs | 401.94 |
| 39 | Parker Washington | 67.50 | Calvin Ridley | 44.80 | Quentin Johnston | 401.45 |
| 40 | Ricky Pearsall | 66.90 | Khalil Shakir | 44.12 | Alec Pierce | 400.19 |
| 41 | Troy Franklin | 66.20 | Tre Tucker | 43.84 | DJ Moore | 382.60 |
| 42 | Jerry Jeudy | 65.50 | Quentin Johnston | 43.73 | Rashee Rice | 379.23 |
| 43 | Elic Ayomanor | 64.80 | Jayden Reed | 43.12 | Jordan Addison | 372.65 |
| 44 | Darius Slayton | 64.10 | Parker Washington | 39.38 | Marquise Brown | 339.82 |
| 45 | Khalil Shakir | 63.50 | Jauan Jennings | 39.15 | Darnell Mooney | 335.42 |
| 46 | Calvin Ridley | 62.80 | Alec Pierce | 37.53 | Adonai Mitchell | 334.55 |
| 47 | Keon Coleman | 62.10 | Darius Slayton | 36.66 | Xavier Worthy | 330.77 |
| 48 | Brian Thomas Jr. | 61.50 | Marquise Brown | 35.95 | Chimere Dike | 329.79 |
| 49 | Darnell Mooney | 60.80 | Christian Kirk | 34.98 | Cooper Kupp | 322.37 |
| 50 | Michael Pittman | 60.10 | Darnell Mooney | 34.97 | Mack Hollins | 307.05 |
| 51 | Travis Hunter | 59.50 | Dontayvion Wicks | 33.01 | Jayden Higgins | 306.91 |
| 52 | Mack Hollins | 58.80 | Mack Hollins | 32.90 | Olamide Zaccheaus | 303.50 |
| 53 | Xavier Worthy | 58.10 | DeMario Douglas | 31.36 | Mike Evans | 298.90 |
| 54 | Jakobie Keeney-James | 57.50 | Andrei Iosivas | 30.37 | Darius Slayton | 297.67 |
| 55 | Jayden Reed | 56.80 | Odell Beckham Jr. | 29.92 | Garrett Wilson | 296.37 |
| 56 | Kayshon Boutte | 56.10 | Kendrick Bourne | 29.27 | Terry McLaurin | 290.52 |
| 57 | Jalen Coker | 55.50 | K.J. Osborn | 28.41 | Xavier Legette | 290.13 |
| 58 | Josh Downs | 54.80 | Olamide Zaccheaus | 28.02 | Malik Washington | 286.80 |
| 59 | Rashid Shaheed | 54.10 | Demarcus Robinson | 26.09 | Andrei Iosivas | 273.84 |
| 60 | Cooper Kupp | 53.50 | Marvin Mims Jr. | 25.92 | Keon Coleman | 272.95 |
| 61 | Chris Godwin Jr. | 52.80 | Calvin Austin III | 25.05 | Christian Watson | 269.66 |
| 62 | Jalen McMillan | 51.50 | Trey Palmer | 25.01 | Xavier Hutchinson | 268.34 |
| 63 | Devaughn Vele | 50.80 | Tutu Atwell | 24.62 | Luther Burden III | 264.91 |
| 64 | Marquise Brown | 50.10 | Elijah Moore | 23.88 | Calvin Austin III | 261.37 |
| 65 | Van Jefferson | 49.50 | Van Jefferson | 23.80 | Jalen Nailor | 251.67 |
| 66 | Xavier Legette | 48.80 | Cedric Tillman | 23.78 | Ryan Flournoy | 250.17 |
| 67 | Jayden Higgins | 48.10 | Rashod Bateman | 23.53 | Ricky Pearsall | 249.51 |
| 68 | DJ Moore | 47.50 | John Metchie III | 23.50 | Kendrick Bourne | 247.41 |
| 69 | Adonai Mitchell | 46.80 | KaVontae Turpin | 23.29 | Van Jefferson | 242.65 |
| 70 | Theo Wease Jr. | 46.10 | Xavier Hutchinson | 23.17 | Christian Kirk | 238.52 |
| 71 | Andrei Iosivas | 45.50 | Emeka Egbuka | 23.06 | Chris Godwin Jr. | 235.60 |
| 72 | Chimere Dike | 44.80 | Tetairoa McMillan | 23.04 | Marvin Mims Jr. | 231.55 |
| 73 | Tyquan Thornton | 44.10 | Tim Patrick | 22.87 | Kayshon Boutte | 226.64 |
| 74 | Olamide Zaccheaus | 43.50 | Jahan Dotson | 22.66 | John Metchie III | 224.38 |
| 75 | Malik Washington | 42.80 | Greg Dortch | 22.41 | Pat Bryant | 220.63 |
| 76 | Kendrick Bourne | 42.10 | Marquez Valdes-Scantling | 20.76 | Dontayvion Wicks | 217.73 |
| 77 | Ryan Flournoy | 41.50 | Allen Hurns | 20.67 | Travis Hunter | 211.33 |
| 78 | Calvin Austin III | 40.80 | David Moore | 19.64 | DeMario Douglas | 207.58 |
| 79 | Pat Bryant | 40.10 | Kayshon Boutte | 19.23 | JuJu Smith-Schuster | 205.66 |
| 80 | Dontayvion Wicks | 39.50 | Tyler Johnson | 18.78 | Jalen Coker | 199.22 |
| 81 | Xavier Hutchinson | 38.80 | Lil'Jordan Humphrey | 18.78 | Matthew Golden | 194.23 |
| 82 | Matthew Golden | 38.10 | Quez Watkins | 18.77 | Tez Johnson | 194.05 |
| 83 | Rashod Bateman | 37.50 | Ladd McConkey | 18.74 | Isaiah Bond | 193.50 |
| 84 | Jalen Nailor | 36.80 | Brandon Johnson | 18.64 | Tre Harris | 188.86 |
| 85 | Tory Horton | 36.10 | Troy Franklin | 18.61 | Cedric Tillman | 185.91 |
| 86 | Luther Burden III | 35.50 | JuJu Smith-Schuster | 18.13 | Malik Nabers | 181.91 |
| 87 | Tez Johnson | 34.80 | Jalen Tolbert | 18.02 | Rashod Bateman | 181.19 |
| 88 | DeMario Douglas | 34.10 | Rome Odunze | 17.80 | Devaughn Vele | 180.03 |
| 89 | Christian Kirk | 33.50 | Jalen Nailor | 17.74 | Tyquan Thornton | 177.85 |
| 90 | Isaiah Bond | 32.80 | Nick Westbrook-Ikhine | 17.56 | Dyami Brown | 177.17 |
| 91 | Tre Harris | 32.10 | Kalif Raymond | 17.33 | KaVontae Turpin | 174.18 |
| 92 | Treylon Burks | 31.50 | Terrace Marshall Jr. | 17.13 | Calvin Ridley | 172.24 |
| 93 | Isaac TeSlaa | 30.80 | David Sills | 17.07 | David Sills | 170.96 |
| 94 | Marquez Valdes-Scantling | 30.10 | Jonathan Mingo | 17.01 | Jalen Tolbert | 165.25 |
| 95 | Casey Washington | 29.50 | Tyler Scott | 16.87 | Jahan Dotson | 165.03 |
| 96 | Cedric Tillman | 28.80 | Tyquan Thornton | 16.70 | Demarcus Robinson | 161.93 |
| 97 | Jalen Tolbert | 28.10 | Dyami Brown | 16.38 | Isaiah Williams | 153.61 |
| 98 | John Metchie III | 27.50 | Brian Thomas Jr. | 16.17 | Greg Dortch | 151.61 |
| 99 | Lil'Jordan Humphrey | 26.80 | Cedrick Wilson Jr. | 15.77 | Jaylin Noel | 147.60 |
| 100 | Devontez Walker | 25.00 | Jalin Hyatt | 15.31 | Marquez Valdes-Scantling | 137.87 |

## TE Board Top 35
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Trey McBride | 98.00 | Trey McBride | 83.02 | Trey McBride | 791.12 |
| 2 | Brock Bowers | 94.00 | Travis Kelce | 73.49 | Kyle Pitts | 549.36 |
| 3 | George Kittle | 91.00 | George Kittle | 70.94 | Tyler Warren | 512.12 |
| 4 | Tucker Kraft | 88.00 | Sam LaPorta | 65.96 | Travis Kelce | 496.31 |
| 5 | Sam LaPorta | 86.00 | Jake Ferguson | 62.27 | Dalton Schultz | 489.24 |
| 6 | Dallas Goedert | 85.00 | Kyle Pitts | 58.69 | Harold Fannin Jr. | 482.99 |
| 7 | Kyle Pitts | 84.00 | Mark Andrews | 56.60 | Juwan Johnson | 476.19 |
| 8 | Travis Kelce | 83.00 | Dallas Goedert | 54.34 | Jake Ferguson | 475.85 |
| 9 | Tyler Warren | 80.00 | Dalton Schultz | 52.21 | Hunter Henry | 407.56 |
| 10 | Dalton Kincaid | 78.00 | Evan Engram | 50.72 | Brock Bowers | 403.74 |
| 11 | Hunter Henry | 77.00 | David Njoku | 50.50 | Dallas Goedert | 385.88 |
| 12 | Dalton Schultz | 76.00 | Juwan Johnson | 49.70 | Cade Otton | 378.51 |
| 13 | Juwan Johnson | 74.00 | Hunter Henry | 49.20 | Colston Loveland | 374.85 |
| 14 | Colston Loveland | 73.00 | Cade Otton | 46.54 | Chig Okonkwo | 361.16 |
| 15 | Jake Ferguson | 72.00 | T.J. Hockenson | 46.02 | Evan Engram | 345.57 |
| 16 | Harold Fannin Jr. | 70.00 | Cole Kmet | 43.85 | Theo Johnson | 339.49 |
| 17 | Brenton Strange | 68.00 | Dalton Kincaid | 43.27 | George Kittle | 333.10 |
| 18 | Mark Andrews | 66.00 | Tucker Kraft | 41.65 | Mark Andrews | 321.85 |
| 19 | T.J. Hockenson | 65.00 | Chig Okonkwo | 39.22 | Oronde Gadsden II | 315.19 |
| 20 | Cade Otton | 64.00 | Pat Freiermuth | 33.97 | AJ Barner | 305.95 |
| 21 | Theo Johnson | 63.00 | Michael Mayer | 29.85 | T.J. Hockenson | 304.66 |
| 22 | Mason Taylor | 62.00 | Mike Gesicki | 29.85 | Mason Taylor | 297.54 |
| 23 | Oronde Gadsden II | 61.00 | Tyler Higbee | 28.26 | Brenton Strange | 291.85 |
| 24 | AJ Barner | 60.00 | Dawson Knox | 27.07 | Colby Parkinson | 268.75 |
| 25 | Jake Tonges | 59.00 | Luke Musgrave | 26.26 | Pat Freiermuth | 250.19 |
| 26 | Greg Dulcich | 58.00 | Colby Parkinson | 26.10 | Gunnar Helm | 244.82 |
| 27 | Drake Dabney | 57.00 | Noah Fant | 26.08 | Sam LaPorta | 238.92 |
| 28 | David Njoku | 56.00 | Jack Doyle | 25.55 | Michael Mayer | 238.67 |
| 29 | Colby Parkinson | 55.00 | Darren Fells | 24.87 | Dalton Kincaid | 233.11 |
| 30 | Pat Freiermuth | 54.00 | Brenton Strange | 24.74 | Dawson Knox | 230.56 |
| 31 | Evan Engram | 53.00 | Isaiah Likely | 24.13 | Jake Tonges | 228.87 |
| 32 | Chig Okonkwo | 52.00 | Noah Gray | 23.19 | Tucker Kraft | 224.79 |
| 33 | Darnell Washington | 48.00 | Tyler Warren | 22.75 | David Njoku | 223.64 |
| 34 | Dawson Knox | 47.00 | Davis Allen | 22.70 | Cole Kmet | 222.83 |
| 35 | Cole Kmet | 46.00 | Tyler Conklin | 21.33 | Darnell Washington | 209.17 |

## Logistic Risers
| Player | Pos | Current | Logistic | Delta | Missing % |
|---|---|---|---|---|---|
| Brian Robinson | RB | 273 | 52 | +221 | 21.8% |
| Jerome Ford | RB | 271 | 90 | +181 | 21.8% |
| Isiah Pacheco | RB | 194 | 29 | +165 | 21.8% |
| Devin Singletary | RB | 229 | 64 | +165 | 14.9% |
| Justin Fields | QB | 200 | 41 | +159 | 25.3% |
| Tyler Allgeier | RB | 202 | 48 | +154 | 21.8% |
| Keaton Mitchell | RB | 264 | 117 | +147 | 35.6% |
| Emanuel Wilson | RB | 234 | 95 | +139 | 35.6% |
| Michael Carter | RB | 226 | 94 | +132 | 21.8% |
| David Montgomery | RB | 153 | 22 | +131 | 14.9% |
| Tyler Huntley | QB | 280 | 149 | +131 | 25.3% |
| Chuba Hubbard | RB | 167 | 38 | +129 | 21.8% |
| Tony Pollard | RB | 140 | 14 | +126 | 17.2% |
| Rachaad White | RB | 148 | 23 | +125 | 21.8% |
| Alvin Kamara | RB | 144 | 20 | +124 | 17.2% |
| Emari Demercado | RB | 262 | 140 | +122 | 32.2% |
| DJ Moore | WR | 173 | 59 | +114 | 14.9% |
| Kenneth Walker III | RB | 129 | 16 | +113 | 21.8% |
| Marcus Mariota | QB | 232 | 122 | +110 | 20.7% |
| Sean Tucker | RB | 274 | 164 | +110 | 35.6% |

## Logistic Fallers
| Player | Pos | Current | Logistic | Delta | Missing % |
|---|---|---|---|---|---|
| Fernando Mendoza | QB | 181 | 719 | -538 | 100.0% |
| Jakobie Keeney-James | WR | 138 | 463 | -325 | 85.1% |
| Malik Nabers | WR | 39 | 361 | -322 | 85.1% |
| Drake Dabney | TE | 139 | 457 | -318 | 85.1% |
| Jalen McMillan | WR | 160 | 438 | -278 | 85.1% |
| Theo Wease Jr. | WR | 177 | 454 | -277 | 85.1% |
| Travis Hunter | WR | 130 | 390 | -260 | 85.1% |
| Ricky Pearsall | WR | 101 | 360 | -259 | 85.1% |
| Jalen Coker | WR | 145 | 400 | -255 | 85.1% |
| Devaughn Vele | WR | 162 | 410 | -248 | 85.1% |
| Keon Coleman | WR | 118 | 363 | -245 | 85.1% |
| Shedeur Sanders | QB | 170 | 409 | -239 | 85.1% |
| Casey Washington | WR | 243 | 480 | -237 | 85.1% |
| Tory Horton | WR | 215 | 448 | -233 | 85.1% |
| Devontez Walker | WR | 259 | 492 | -233 | 85.1% |
| Brock Bowers | TE | 12 | 243 | -231 | 85.1% |
| Jayden Daniels | QB | 57 | 281 | -224 | 85.1% |
| Mason Taylor | TE | 119 | 339 | -220 | 85.1% |
| Jackson Hawes | TE | 225 | 445 | -220 | 85.1% |
| Rome Odunze | WR | 49 | 267 | -218 | 85.1% |

## Cutline Crossings
| Model | Cutline | Entered | Entered sample | Exited | Exited sample |
|---|---|---|---|---|---|
| enriched_logistic | overall top 24 | 17 | Saquon Barkley, Kyren Williams, Derrick Henry, James Cook, Travis Etienne | 17 | Josh Allen, Amon-Ra St. Brown, Jalen Hurts, Justin Jefferson, Trey McBride |
| enriched_logistic | overall top 50 | 23 | Derrick Henry, Travis Etienne, Breece Hall, Josh Jacobs, Javonte Williams | 23 | Nico Collins, Patrick Mahomes, George Kittle, Rashee Rice, Sam LaPorta |
| enriched_logistic | overall top 100 | 32 | Tony Pollard, Kenneth Walker III, Alvin Kamara, David Montgomery, Rachaad White | 32 | Joe Burrow, Juwan Johnson, Matthew Stafford, Hunter Henry, Jameson Williams |
| enriched_logistic | QB12 | 6 | Lamar Jackson, Justin Fields, Justin Herbert, Baker Mayfield, C.J. Stroud | 6 | Daniel Jones, Matthew Stafford, Jordan Love, Drake Maye, Bo Nix |
| enriched_logistic | RB12 | 2 | Derrick Henry, Breece Hall | 2 | Javonte Williams, Chase Brown |
| enriched_logistic | RB24 | 7 | Tony Pollard, Kenneth Walker III, Alvin Kamara, David Montgomery, Rachaad White | 7 | Ashton Jeanty, J.K. Dobbins, Quinshon Judkins, TreVeyon Henderson, Bucky Irving |
| enriched_logistic | RB36 | 6 | Isiah Pacheco, Chuba Hubbard, Tyler Allgeier, Brian Robinson, Tyjae Spears | 6 | Woody Marks, TreVeyon Henderson, Tyrone Tracy Jr., Bucky Irving, Omarion Hampton |
| enriched_logistic | WR12 | 3 | Davante Adams, George Pickens, Courtland Sutton | 3 | Rashee Rice, Garrett Wilson, Drake London |
| enriched_logistic | WR24 | 6 | Jakobi Meyers, Michael Pittman, DJ Moore, Mike Evans, DK Metcalf | 6 | Wan'Dale Robinson, Tee Higgins, Terry McLaurin, Tetairoa McMillan, Rome Odunze |
| enriched_logistic | WR36 | 9 | Michael Pittman, DJ Moore, Cooper Kupp, Tank Dell, Chris Godwin Jr. | 9 | Christian Watson, Quentin Johnston, Jauan Jennings, Alec Pierce, Emeka Egbuka |
| enriched_logistic | TE6 | 3 | Travis Kelce, Jake Ferguson, Kyle Pitts | 3 | Dallas Goedert, Tucker Kraft, Brock Bowers |
| enriched_logistic | TE12 | 5 | Jake Ferguson, Mark Andrews, Evan Engram, David Njoku, Juwan Johnson | 5 | Hunter Henry, Dalton Kincaid, Tucker Kraft, Tyler Warren, Brock Bowers |
| enriched_logistic | TE18 | 5 | Evan Engram, David Njoku, Cade Otton, T.J. Hockenson, Cole Kmet | 5 | Brenton Strange, Tyler Warren, Harold Fannin Jr., Brock Bowers, Colston Loveland |
| enriched_linear_points | overall top 24 | 15 | Wan'Dale Robinson, George Pickens, Michael Wilson, Emeka Egbuka, Courtland Sutton | 15 | Christian McCaffrey, Brock Bowers, Rashee Rice, Bijan Robinson, Jahmyr Gibbs |
| enriched_linear_points | overall top 50 | 29 | Michael Wilson, Emeka Egbuka, Courtland Sutton, DeVonta Smith, Tyler Warren | 29 | Dallas Goedert, Rashee Rice, Bijan Robinson, Jahmyr Gibbs, Chase Brown |
| enriched_linear_points | overall top 100 | 42 | Michael Pittman, Jerry Jeudy, Troy Franklin, Khalil Shakir, Rashid Shaheed | 42 | Sam LaPorta, Dalton Kincaid, Tucker Kraft, Malik Nabers, Rico Dowdle |
| enriched_linear_points | QB12 | 10 | Jameis Winston, Aaron Rodgers, Sam Howell, Josh Johnson, Blake Bortles | 10 | Jordan Love, Patrick Mahomes, Dak Prescott, Daniel Jones, Trevor Lawrence |
| enriched_linear_points | RB12 | 7 | Kenneth Gainwell, Ashton Jeanty, RJ Harvey, Tyjae Spears, Michael Carter | 7 | Kyren Williams, Javonte Williams, Travis Etienne, Jonathan Taylor, Saquon Barkley |
| enriched_linear_points | RB24 | 10 | Kenneth Gainwell, RJ Harvey, Tyjae Spears, Michael Carter, Tyrone Tracy Jr. | 10 | Jonathan Taylor, Cam Skattebo, Breece Hall, Saquon Barkley, Bucky Irving |
| enriched_linear_points | RB36 | 11 | RJ Harvey, Tyjae Spears, Michael Carter, Dylan Sampson, Brashard Smith | 11 | Josh Jacobs, Woody Marks, Quinshon Judkins, Tony Pollard, James Cook |
| enriched_linear_points | WR12 | 5 | Wan'Dale Robinson, George Pickens, Michael Wilson, Emeka Egbuka, Courtland Sutton | 5 | Zay Flowers, CeeDee Lamb, Drake London, Rashee Rice, Garrett Wilson |
| enriched_linear_points | WR24 | 7 | Michael Wilson, Emeka Egbuka, Jakobi Meyers, Michael Pittman, Jerry Jeudy | 7 | Jaylen Waddle, Tee Higgins, Rome Odunze, Rashee Rice, Garrett Wilson |
| enriched_linear_points | WR36 | 9 | Michael Pittman, Jerry Jeudy, Troy Franklin, Parker Washington, Khalil Shakir | 9 | Quentin Johnston, Alec Pierce, Rashee Rice, Jordan Addison, Mike Evans |
| enriched_linear_points | TE6 | 5 | Kyle Pitts, Tyler Warren, Travis Kelce, Dalton Schultz, Harold Fannin Jr. | 5 | Brock Bowers, Dallas Goedert, George Kittle, Sam LaPorta, Tucker Kraft |
| enriched_linear_points | TE12 | 4 | Harold Fannin Jr., Juwan Johnson, Jake Ferguson, Cade Otton | 4 | George Kittle, Sam LaPorta, Dalton Kincaid, Tucker Kraft |
| enriched_linear_points | TE18 | 4 | Cade Otton, Chig Okonkwo, Evan Engram, Theo Johnson | 4 | Brenton Strange, Sam LaPorta, Dalton Kincaid, Tucker Kraft |

## TE35 Watch Band
| Model | TE rank | Player | Score | Current TE rank | Missing % |
|---|---|---|---|---|---|
| enriched_logistic | 30 | Brenton Strange | 24.74 | 17 | 42.5% |
| enriched_logistic | 31 | Isaiah Likely | 24.13 | 38 | 26.4% |
| enriched_logistic | 32 | Noah Gray | 23.19 |  | 21.8% |
| enriched_logistic | 33 | Tyler Warren | 22.75 | 9 | 85.1% |
| enriched_logistic | 34 | Davis Allen | 22.70 | 51 | 36.8% |
| enriched_logistic | 35 | Tyler Conklin | 21.33 |  | 17.2% |
| enriched_logistic | 36 | Harold Fannin Jr. | 21.14 | 16 | 85.1% |
| enriched_logistic | 37 | Tommy Tremble | 20.42 | 46 | 21.8% |
| enriched_logistic | 38 | Ryan Izzo | 20.02 |  | 41.4% |
| enriched_logistic | 39 | Darnell Washington | 19.71 | 33 | 40.2% |
| enriched_logistic | 40 | Brock Bowers | 19.60 | 2 | 85.1% |
| enriched_linear_points | 30 | Dawson Knox | 230.56 | 34 | 21.8% |
| enriched_linear_points | 31 | Jake Tonges | 228.87 | 25 | 43.7% |
| enriched_linear_points | 32 | Tucker Kraft | 224.79 | 4 | 36.8% |
| enriched_linear_points | 33 | David Njoku | 223.64 | 28 | 17.2% |
| enriched_linear_points | 34 | Cole Kmet | 222.83 | 35 | 21.8% |
| enriched_linear_points | 35 | Darnell Washington | 209.17 | 33 | 40.2% |
| enriched_linear_points | 36 | Mike Gesicki | 198.45 | 40 | 21.8% |
| enriched_linear_points | 37 | Noah Fant | 189.85 | 58 | 21.8% |
| enriched_linear_points | 38 | Tommy Tremble | 173.85 | 46 | 21.8% |
| enriched_linear_points | 39 | Elijah Higgins | 173.80 |  | 40.2% |
| enriched_linear_points | 40 | Noah Gray | 173.37 |  | 21.8% |

# GNG Keeper Review Boards

## Current Pigskin Top 50 Overall
| Rank | Player | Pos | Team | Score | Pos rank |
|---|---|---|---|---|---|
| 1 | Christian McCaffrey | RB | SF | 98.50 | 1 |
| 2 | Josh Allen | QB | BUF | 98.50 | 1 |
| 3 | Puka Nacua | WR | LAR | 98.50 | 1 |
| 4 | Trey McBride | TE | ARI | 98.50 | 1 |
| 5 | Jaxon Smith-Njigba | WR | SEA | 97.00 | 2 |
| 6 | Drake Maye | QB | NE | 96.00 | 2 |
| 7 | Amon-Ra St. Brown | WR | DET | 96.00 | 3 |
| 8 | Bijan Robinson | RB | ATL | 95.00 | 2 |
| 9 | Ja'Marr Chase | WR | CIN | 95.00 | 4 |
| 10 | Patrick Mahomes | QB | KC | 94.50 | 3 |
| 11 | Brock Bowers | TE | LV | 94.00 | 2 |
| 12 | Jahmyr Gibbs | RB | DET | 93.50 | 3 |
| 13 | Justin Jefferson | WR | MIN | 93.50 | 5 |
| 14 | Brock Purdy | QB | SF | 93.00 | 4 |
| 15 | Jonathan Taylor | RB | IND | 92.00 | 4 |
| 16 | Jalen Hurts | QB | PHI | 91.50 | 5 |
| 17 | De'Von Achane | RB | MIA | 91.00 | 5 |
| 18 | Garrett Wilson | WR | NYJ | 91.00 | 6 |
| 19 | Drake London | WR | ATL | 90.00 | 7 |
| 20 | George Kittle | TE | SF | 89.50 | 3 |
| 21 | Matthew Stafford | QB | LAR | 89.00 | 6 |
| 22 | Rashee Rice | WR | KC | 89.00 | 8 |
| 23 | Tucker Kraft | TE | GB | 88.00 | 4 |
| 24 | Chris Olave | WR | NO | 88.00 | 9 |
| 25 | Dak Prescott | QB | DAL | 87.50 | 7 |
| 26 | A.J. Brown | WR | NE | 87.00 | 10 |
| 27 | Kyle Pitts | TE | ATL | 86.50 | 5 |
| 28 | Jordan Love | QB | GB | 86.00 | 8 |
| 29 | George Pickens | WR | DAL | 85.50 | 11 |
| 30 | Chase Brown | RB | CIN | 85.00 | 6 |
| 31 | Sam LaPorta | TE | DET | 85.00 | 6 |
| 32 | Trevor Lawrence | QB | JAX | 85.00 | 9 |
| 33 | Javonte Williams | RB | DAL | 84.00 | 7 |
| 34 | Tyler Warren | TE | IND | 84.00 | 7 |
| 35 | Caleb Williams | QB | CHI | 84.00 | 10 |
| 36 | Davante Adams | WR | LAR | 84.00 | 12 |
| 37 | Dallas Goedert | TE | PHI | 83.00 | 8 |
| 38 | Saquon Barkley | RB | PHI | 83.00 | 8 |
| 39 | Bo Nix | QB | DEN | 83.00 | 11 |
| 40 | Zay Flowers | WR | BAL | 83.00 | 13 |
| 41 | Kyren Williams | RB | LAR | 82.50 | 9 |
| 42 | Travis Kelce | TE | KC | 82.00 | 9 |
| 43 | CeeDee Lamb | WR | DAL | 82.00 | 14 |
| 44 | Daniel Jones | QB | IND | 81.50 | 12 |
| 45 | Hunter Henry | TE | NE | 81.00 | 10 |
| 46 | Omarion Hampton | RB | LAC | 81.00 | 10 |
| 47 | Nico Collins | WR | HOU | 81.00 | 15 |
| 48 | Dalton Schultz | TE | HOU | 80.00 | 11 |
| 49 | James Cook | RB | BUF | 80.00 | 11 |
| 50 | Justin Herbert | QB | LAC | 79.50 | 13 |

## BQML Logistic Top 50 Overall
| Logistic rank | Player | Pos | Team | Score | Current rank | Delta | Missing % |
|---|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey | RB | SF | 99.77 | 1 | +0 | 17.2% |
| 2 | Jonathan Taylor | RB | IND | 99.49 | 15 | +13 | 24.1% |
| 3 | Bijan Robinson | RB | ATL | 99.45 | 8 | +5 | 34.5% |
| 4 | Saquon Barkley | RB | PHI | 99.34 | 38 | +34 | 19.5% |
| 5 | Derrick Henry | RB | BAL | 99.19 | 81 | +76 | 17.2% |
| 6 | Kyren Williams | RB | LAR | 99.17 | 41 | +35 | 24.1% |
| 7 | Jahmyr Gibbs | RB | DET | 99.07 | 12 | +5 | 34.5% |
| 8 | James Cook | RB | BUF | 98.88 | 49 | +41 | 24.1% |
| 9 | Travis Etienne | RB | NO | 98.85 | 62 | +53 | 24.1% |
| 10 | De'Von Achane | RB | MIA | 98.68 | 17 | +7 | 34.5% |
| 11 | Breece Hall | RB | NYJ | 98.36 | 77 | +66 | 24.1% |
| 12 | Josh Jacobs | RB | GB | 98.00 | 57 | +45 | 19.5% |
| 13 | Javonte Williams | RB | DAL | 97.42 | 33 | +20 | 24.1% |
| 14 | Tony Pollard | RB | TEN | 97.07 | 102 | +88 | 19.5% |
| 15 | D'Andre Swift | RB | CHI | 96.43 | 73 | +58 | 21.8% |
| 16 | Kenneth Walker III | RB | KC | 96.07 | 99 | +83 | 24.1% |
| 17 | Jaylen Warren | RB | PIT | 93.86 | 120 | +103 | 24.1% |
| 18 | Chase Brown | RB | CIN | 93.13 | 30 | +12 | 34.5% |
| 19 | Rico Dowdle | RB | PIT | 92.70 | 89 | +70 | 27.6% |
| 20 | Alvin Kamara | RB | NO | 92.49 | 124 | +104 | 19.5% |
| 21 | David Montgomery | RB | HOU | 90.96 | 108 | +87 | 17.2% |
| 22 | Josh Allen | QB | BUF | 90.60 | 2 | -20 | 23.0% |
| 23 | Jalen Hurts | QB | PHI | 90.27 | 16 | -7 | 23.0% |
| 24 | Rachaad White | RB | WAS | 90.12 | 143 | +119 | 24.1% |
| 25 | Aaron Jones | RB | MIN | 89.69 | 96 | +71 | 19.5% |
| 26 | Puka Nacua | WR | LAR | 89.55 | 3 | -23 | 34.5% |
| 27 | Ja'Marr Chase | WR | CIN | 89.53 | 9 | -18 | 21.8% |
| 28 | Amon-Ra St. Brown | WR | DET | 88.51 | 7 | -21 | 24.1% |
| 29 | Rhamondre Stevenson | RB | NE | 87.52 | 126 | +97 | 24.1% |
| 30 | Isiah Pacheco | RB | DET | 87.43 | 146 | +116 | 24.1% |
| 31 | Zach Charbonnet | RB | SEA | 86.60 | 129 | +98 | 34.5% |
| 32 | Justin Jefferson | WR | MIN | 86.35 | 13 | -19 | 21.8% |
| 33 | Ashton Jeanty | RB | LV | 85.47 | 54 | +21 | 85.1% |
| 34 | CeeDee Lamb | WR | DAL | 83.71 | 43 | +9 | 21.8% |
| 35 | J.K. Dobbins | RB | DEN | 82.13 | 92 | +57 | 24.1% |
| 36 | Lamar Jackson | QB | BAL | 81.27 | 56 | +20 | 18.4% |
| 37 | Chuba Hubbard | RB | CAR | 80.43 | 112 | +75 | 24.1% |
| 38 | Davante Adams | WR | LAR | 78.44 | 36 | -2 | 19.5% |
| 39 | Trey McBride | TE | ARI | 78.36 | 4 | -35 | 28.7% |
| 40 | Kenneth Gainwell | RB | TB | 78.03 | 159 | +119 | 21.8% |
| 41 | Justin Fields | QB | KC | 77.65 | 189 | +148 | 27.6% |
| 42 | Tyler Allgeier | RB | ARI | 74.83 | 153 | +111 | 24.1% |
| 43 | A.J. Brown | WR | NE | 74.22 | 26 | -17 | 24.1% |
| 44 | Chris Olave | WR | NO | 74.17 | 24 | -20 | 28.7% |
| 45 | Trevor Lawrence | QB | JAX | 73.77 | 32 | -13 | 27.6% |
| 46 | Justin Herbert | QB | LAC | 72.64 | 50 | +4 | 23.0% |
| 47 | Travis Kelce | TE | KC | 72.53 | 42 | -5 | 19.5% |
| 48 | Zay Flowers | WR | BAL | 72.41 | 40 | -8 | 34.5% |
| 49 | George Pickens | WR | DAL | 71.52 | 29 | -20 | 24.1% |
| 50 | Brian Robinson | RB | ATL | 70.98 | 261 | +211 | 24.1% |

## BQML Linear Points Top 50 Overall
| Linear rank | Player | Pos | Team | Score | Current rank | Delta | Missing % |
|---|---|---|---|---|---|---|---|
| 1 | Ja'Marr Chase | WR | CIN | 845.95 | 9 | +8 | 21.8% |
| 2 | Amon-Ra St. Brown | WR | DET | 790.33 | 7 | +5 | 24.1% |
| 3 | Trey McBride | TE | ARI | 782.05 | 4 | +1 | 28.7% |
| 4 | Puka Nacua | WR | LAR | 758.48 | 3 | -1 | 34.5% |
| 5 | Jaxon Smith-Njigba | WR | SEA | 754.51 | 5 | +0 | 39.1% |
| 6 | Chris Olave | WR | NO | 717.83 | 24 | +18 | 28.7% |
| 7 | Justin Jefferson | WR | MIN | 646.78 | 13 | +6 | 21.8% |
| 8 | Wan'Dale Robinson | WR | TEN | 646.06 | 58 | +50 | 24.1% |
| 9 | George Pickens | WR | DAL | 633.34 | 29 | +20 | 24.1% |
| 10 | Michael Wilson | WR | ARI | 581.34 | 100 | +90 | 39.1% |
| 11 | Emeka Egbuka | WR | TB | 576.84 | 88 | +77 | 85.1% |
| 12 | Courtland Sutton | WR | DEN | 571.13 | 84 | +72 | 17.2% |
| 13 | A.J. Brown | WR | NE | 560.31 | 26 | +13 | 24.1% |
| 14 | Tetairoa McMillan | WR | CAR | 559.49 | 51 | +37 | 85.1% |
| 15 | Nico Collins | WR | HOU | 557.43 | 47 | +32 | 24.1% |
| 16 | Kyle Pitts | TE | ATL | 543.58 | 27 | +11 | 24.1% |
| 17 | Zay Flowers | WR | BAL | 543.17 | 40 | +23 | 34.5% |
| 18 | CeeDee Lamb | WR | DAL | 540.29 | 43 | +25 | 21.8% |
| 19 | Davante Adams | WR | LAR | 528.68 | 36 | +17 | 19.5% |
| 20 | Drake London | WR | ATL | 525.56 | 19 | -1 | 26.4% |
| 21 | DeVonta Smith | WR | PHI | 520.25 | 65 | +44 | 28.7% |
| 22 | Tyler Warren | TE | IND | 506.77 | 34 | +12 | 85.1% |
| 23 | Jakobi Meyers | WR | JAX | 503.76 | 115 | +92 | 17.2% |
| 24 | Michael Pittman | WR | PIT | 501.39 | 149 | +125 | 24.1% |
| 25 | Travis Kelce | TE | KC | 490.91 | 42 | +17 | 19.5% |
| 26 | Jerry Jeudy | WR | CLE | 486.51 | 130 | +104 | 24.1% |
| 27 | Dalton Schultz | TE | HOU | 483.69 | 48 | +21 | 24.1% |
| 28 | Ladd McConkey | WR | LAC | 481.60 | 113 | +85 | 85.1% |
| 29 | Harold Fannin Jr. | TE | CLE | 477.71 | 67 | +38 | 85.1% |
| 30 | Jameson Williams | WR | DET | 476.33 | 94 | +64 | 24.1% |
| 31 | Christian McCaffrey | RB | SF | 470.40 | 1 | -30 | 17.2% |
| 32 | Juwan Johnson | TE | NO | 469.84 | 52 | +20 | 28.7% |
| 33 | Jake Ferguson | TE | DAL | 469.56 | 59 | +26 | 28.7% |
| 34 | Troy Franklin | WR | DEN | 468.82 | 133 | +99 | 85.1% |
| 35 | Jaylen Waddle | WR | DEN | 462.09 | 74 | +39 | 24.1% |
| 36 | Tee Higgins | WR | CIN | 454.28 | 76 | +40 | 28.7% |
| 37 | DK Metcalf | WR | PIT | 452.53 | 109 | +72 | 24.1% |
| 38 | Parker Washington | WR | JAX | 440.38 | 125 | +87 | 39.1% |
| 39 | Khalil Shakir | WR | BUF | 439.11 | 138 | +99 | 24.1% |
| 40 | Tre Tucker | WR | LV | 425.77 | 121 | +81 | 34.5% |
| 41 | Jauan Jennings | WR | MIN | 422.82 | 136 | +95 | 21.8% |
| 42 | Rashid Shaheed | WR | SEA | 418.89 | 160 | +118 | 24.1% |
| 43 | Rome Odunze | WR | CHI | 416.59 | 61 | +18 | 85.1% |
| 44 | Brian Thomas Jr. | WR | JAX | 407.70 | 144 | +100 | 85.1% |
| 45 | Elic Ayomanor | WR | TEN | 403.13 | 199 | +154 | 85.1% |
| 46 | Hunter Henry | TE | NE | 403.06 | 45 | -1 | 24.1% |
| 47 | Josh Downs | WR | IND | 401.90 | 157 | +110 | 39.1% |
| 48 | Brock Bowers | TE | LV | 397.61 | 11 | -37 | 85.1% |
| 49 | Romeo Doubs | WR | NE | 396.10 | 119 | +70 | 21.8% |
| 50 | Quentin Johnston | WR | LAC | 395.39 | 97 | +47 | 34.5% |

## Side-by-Side Top 100 Overall
| Rank | Current | Pos | Logistic | Pos | Score | Linear | Pos | Score |
|---|---|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey | RB | Christian McCaffrey | RB | 99.77 | Ja'Marr Chase | WR | 845.95 |
| 2 | Josh Allen | QB | Jonathan Taylor | RB | 99.49 | Amon-Ra St. Brown | WR | 790.33 |
| 3 | Puka Nacua | WR | Bijan Robinson | RB | 99.45 | Trey McBride | TE | 782.05 |
| 4 | Trey McBride | TE | Saquon Barkley | RB | 99.34 | Puka Nacua | WR | 758.48 |
| 5 | Jaxon Smith-Njigba | WR | Derrick Henry | RB | 99.19 | Jaxon Smith-Njigba | WR | 754.51 |
| 6 | Drake Maye | QB | Kyren Williams | RB | 99.17 | Chris Olave | WR | 717.83 |
| 7 | Amon-Ra St. Brown | WR | Jahmyr Gibbs | RB | 99.07 | Justin Jefferson | WR | 646.78 |
| 8 | Bijan Robinson | RB | James Cook | RB | 98.88 | Wan'Dale Robinson | WR | 646.06 |
| 9 | Ja'Marr Chase | WR | Travis Etienne | RB | 98.85 | George Pickens | WR | 633.34 |
| 10 | Patrick Mahomes | QB | De'Von Achane | RB | 98.68 | Michael Wilson | WR | 581.34 |
| 11 | Brock Bowers | TE | Breece Hall | RB | 98.36 | Emeka Egbuka | WR | 576.84 |
| 12 | Jahmyr Gibbs | RB | Josh Jacobs | RB | 98.00 | Courtland Sutton | WR | 571.13 |
| 13 | Justin Jefferson | WR | Javonte Williams | RB | 97.42 | A.J. Brown | WR | 560.31 |
| 14 | Brock Purdy | QB | Tony Pollard | RB | 97.07 | Tetairoa McMillan | WR | 559.49 |
| 15 | Jonathan Taylor | RB | D'Andre Swift | RB | 96.43 | Nico Collins | WR | 557.43 |
| 16 | Jalen Hurts | QB | Kenneth Walker III | RB | 96.07 | Kyle Pitts | TE | 543.58 |
| 17 | De'Von Achane | RB | Jaylen Warren | RB | 93.86 | Zay Flowers | WR | 543.17 |
| 18 | Garrett Wilson | WR | Chase Brown | RB | 93.13 | CeeDee Lamb | WR | 540.29 |
| 19 | Drake London | WR | Rico Dowdle | RB | 92.70 | Davante Adams | WR | 528.68 |
| 20 | George Kittle | TE | Alvin Kamara | RB | 92.49 | Drake London | WR | 525.56 |
| 21 | Matthew Stafford | QB | David Montgomery | RB | 90.96 | DeVonta Smith | WR | 520.25 |
| 22 | Rashee Rice | WR | Josh Allen | QB | 90.60 | Tyler Warren | TE | 506.77 |
| 23 | Tucker Kraft | TE | Jalen Hurts | QB | 90.27 | Jakobi Meyers | WR | 503.76 |
| 24 | Chris Olave | WR | Rachaad White | RB | 90.12 | Michael Pittman | WR | 501.39 |
| 25 | Dak Prescott | QB | Aaron Jones | RB | 89.69 | Travis Kelce | TE | 490.91 |
| 26 | A.J. Brown | WR | Puka Nacua | WR | 89.55 | Jerry Jeudy | WR | 486.51 |
| 27 | Kyle Pitts | TE | Ja'Marr Chase | WR | 89.53 | Dalton Schultz | TE | 483.69 |
| 28 | Jordan Love | QB | Amon-Ra St. Brown | WR | 88.51 | Ladd McConkey | WR | 481.60 |
| 29 | George Pickens | WR | Rhamondre Stevenson | RB | 87.52 | Harold Fannin Jr. | TE | 477.71 |
| 30 | Chase Brown | RB | Isiah Pacheco | RB | 87.43 | Jameson Williams | WR | 476.33 |
| 31 | Sam LaPorta | TE | Zach Charbonnet | RB | 86.60 | Christian McCaffrey | RB | 470.40 |
| 32 | Trevor Lawrence | QB | Justin Jefferson | WR | 86.35 | Juwan Johnson | TE | 469.84 |
| 33 | Javonte Williams | RB | Ashton Jeanty | RB | 85.47 | Jake Ferguson | TE | 469.56 |
| 34 | Tyler Warren | TE | CeeDee Lamb | WR | 83.71 | Troy Franklin | WR | 468.82 |
| 35 | Caleb Williams | QB | J.K. Dobbins | RB | 82.13 | Jaylen Waddle | WR | 462.09 |
| 36 | Davante Adams | WR | Lamar Jackson | QB | 81.27 | Tee Higgins | WR | 454.28 |
| 37 | Dallas Goedert | TE | Chuba Hubbard | RB | 80.43 | DK Metcalf | WR | 452.53 |
| 38 | Saquon Barkley | RB | Davante Adams | WR | 78.44 | Parker Washington | WR | 440.38 |
| 39 | Bo Nix | QB | Trey McBride | TE | 78.36 | Khalil Shakir | WR | 439.11 |
| 40 | Zay Flowers | WR | Kenneth Gainwell | RB | 78.03 | Tre Tucker | WR | 425.77 |
| 41 | Kyren Williams | RB | Justin Fields | QB | 77.65 | Jauan Jennings | WR | 422.82 |
| 42 | Travis Kelce | TE | Tyler Allgeier | RB | 74.83 | Rashid Shaheed | WR | 418.89 |
| 43 | CeeDee Lamb | WR | A.J. Brown | WR | 74.22 | Rome Odunze | WR | 416.59 |
| 44 | Daniel Jones | QB | Chris Olave | WR | 74.17 | Brian Thomas Jr. | WR | 407.70 |
| 45 | Hunter Henry | TE | Trevor Lawrence | QB | 73.77 | Elic Ayomanor | WR | 403.13 |
| 46 | Omarion Hampton | RB | Justin Herbert | QB | 72.64 | Hunter Henry | TE | 403.06 |
| 47 | Nico Collins | WR | Travis Kelce | TE | 72.53 | Josh Downs | WR | 401.90 |
| 48 | Dalton Schultz | TE | Zay Flowers | WR | 72.41 | Brock Bowers | TE | 397.61 |
| 49 | James Cook | RB | George Pickens | WR | 71.52 | Romeo Doubs | WR | 396.10 |
| 50 | Justin Herbert | QB | Brian Robinson | RB | 70.98 | Quentin Johnston | WR | 395.39 |
| 51 | Tetairoa McMillan | WR | Quinshon Judkins | RB | 70.70 | Alec Pierce | WR | 394.45 |
| 52 | Juwan Johnson | TE | Jaxon Smith-Njigba | WR | 70.31 | Dallas Goedert | TE | 380.91 |
| 53 | Malik Nabers | WR | Patrick Mahomes | QB | 70.16 | DJ Moore | WR | 377.65 |
| 54 | Ashton Jeanty | RB | Courtland Sutton | WR | 69.12 | Cade Otton | TE | 373.18 |
| 55 | Colston Loveland | TE | Jakobi Meyers | WR | 68.50 | Rashee Rice | WR | 370.61 |
| 56 | Lamar Jackson | QB | George Kittle | TE | 67.60 | Colston Loveland | TE | 370.09 |
| 57 | Josh Jacobs | RB | Nico Collins | WR | 67.58 | Jordan Addison | WR | 367.24 |
| 58 | Wan'Dale Robinson | WR | Michael Pittman | WR | 67.49 | Bijan Robinson | RB | 362.64 |
| 59 | Jake Ferguson | TE | Devin Singletary | RB | 67.12 | Chig Okonkwo | TE | 356.23 |
| 60 | Jaxson Dart | QB | DJ Moore | WR | 66.60 | Kenneth Gainwell | RB | 347.81 |
| 61 | Rome Odunze | WR | C.J. Stroud | QB | 65.97 | Evan Engram | TE | 341.39 |
| 62 | Travis Etienne | RB | Baker Mayfield | QB | 65.87 | Jahmyr Gibbs | RB | 339.59 |
| 63 | Brenton Strange | TE | Jaylen Waddle | WR | 65.28 | Marquise Brown | WR | 335.73 |
| 64 | Jared Goff | QB | DeVonta Smith | WR | 65.13 | Theo Johnson | TE | 335.44 |
| 65 | DeVonta Smith | WR | Tyjae Spears | RB | 65.07 | Darnell Mooney | WR | 331.88 |
| 66 | Cam Skattebo | RB | James Conner | RB | 64.99 | Adonai Mitchell | WR | 331.12 |
| 67 | Harold Fannin Jr. | TE | Jordan Mason | RB | 63.97 | Chase Brown | RB | 330.35 |
| 68 | Joe Burrow | QB | Rashee Rice | WR | 63.23 | George Kittle | TE | 326.37 |
| 69 | Terry McLaurin | WR | Sam LaPorta | TE | 62.63 | Xavier Worthy | WR | 326.12 |
| 70 | Bucky Irving | RB | Mike Evans | WR | 61.99 | Chimere Dike | WR | 326.01 |
| 71 | Dalton Kincaid | TE | Brock Purdy | QB | 61.30 | Mark Andrews | TE | 317.81 |
| 72 | Baker Mayfield | QB | Cooper Kupp | WR | 60.84 | Cooper Kupp | WR | 317.74 |
| 73 | D'Andre Swift | RB | Garrett Wilson | WR | 60.03 | Oronde Gadsden II | TE | 310.61 |
| 74 | Jaylen Waddle | WR | DK Metcalf | WR | 59.88 | De'Von Achane | RB | 305.63 |
| 75 | Jayden Daniels | QB | Jordan Addison | WR | 59.80 | Jayden Higgins | WR | 303.16 |
| 76 | Tee Higgins | WR | Woody Marks | RB | 59.29 | Mack Hollins | WR | 302.03 |
| 77 | Breece Hall | RB | Drake London | WR | 59.25 | AJ Barner | TE | 302.03 |
| 78 | Cade Otton | TE | Tee Higgins | WR | 59.12 | T.J. Hockenson | TE | 300.66 |
| 79 | Kyler Murray | QB | Daniel Jones | QB | 58.13 | Olamide Zaccheaus | WR | 299.33 |
| 80 | Alec Pierce | WR | Tank Dell | WR | 57.79 | Mason Taylor | TE | 293.58 |
| 81 | Derrick Henry | RB | Dak Prescott | QB | 57.35 | Mike Evans | WR | 293.36 |
| 82 | Mark Andrews | TE | Kyle Pitts | TE | 57.27 | Darius Slayton | WR | 293.35 |
| 83 | C.J. Stroud | QB | Michael Wilson | WR | 56.93 | Garrett Wilson | WR | 290.00 |
| 84 | Courtland Sutton | WR | Jake Ferguson | TE | 56.82 | Brenton Strange | TE | 286.97 |
| 85 | Quinshon Judkins | RB | TreVeyon Henderson | RB | 56.39 | Xavier Legette | WR | 286.70 |
| 86 | T.J. Hockenson | TE | Wan'Dale Robinson | WR | 56.18 | Terry McLaurin | WR | 284.37 |
| 87 | Sam Darnold | QB | Tyrone Tracy Jr. | RB | 56.02 | Malik Washington | WR | 283.13 |
| 88 | Emeka Egbuka | WR | Kyler Murray | QB | 55.62 | Andrei Iosivas | WR | 269.74 |
| 89 | Rico Dowdle | RB | Mark Andrews | TE | 54.95 | Keon Coleman | WR | 268.65 |
| 90 | Mike Evans | WR | Bucky Irving | RB | 54.01 | Xavier Hutchinson | WR | 264.56 |
| 91 | Oronde Gadsden II | TE | Chris Godwin Jr. | WR | 53.97 | Colby Parkinson | TE | 264.14 |
| 92 | J.K. Dobbins | RB | Michael Carter | RB | 53.87 | Christian Watson | WR | 263.64 |
| 93 | Jacoby Brissett | QB | Chris Rodriguez Jr. | RB | 53.21 | Luther Burden III | WR | 260.11 |
| 94 | Jameson Williams | WR | Terry McLaurin | WR | 52.88 | Calvin Austin III | WR | 257.77 |
| 95 | AJ Barner | TE | Emanuel Wilson | RB | 52.88 | Jalen Nailor | WR | 248.49 |
| 96 | Aaron Jones | RB | Jerome Ford | RB | 52.31 | Ashton Jeanty | RB | 247.80 |
| 97 | Quentin Johnston | WR | Dallas Goedert | TE | 51.97 | Pat Freiermuth | TE | 246.43 |
| 98 | Aaron Rodgers | QB | Jared Goff | QB | 51.97 | Ryan Flournoy | WR | 246.17 |
| 99 | Kenneth Walker III | RB | Bryce Young | QB | 50.92 | Ricky Pearsall | WR | 243.69 |
| 100 | Michael Wilson | WR | Romeo Doubs | WR | 50.24 | Kendrick Bourne | WR | 242.81 |

## QB Board Top 45
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Josh Allen | 98.50 | Josh Allen | 90.60 | Jameis Winston | 18.88 |
| 2 | Drake Maye | 96.00 | Jalen Hurts | 90.27 | Aaron Rodgers | 14.09 |
| 3 | Patrick Mahomes | 94.50 | Lamar Jackson | 81.27 | Josh Johnson | 12.92 |
| 4 | Brock Purdy | 93.00 | Justin Fields | 77.65 | Matthew Stafford | 11.85 |
| 5 | Jalen Hurts | 91.50 | Trevor Lawrence | 73.77 | Brock Purdy | 10.94 |
| 6 | Matthew Stafford | 89.00 | Justin Herbert | 72.64 | Jared Goff | 10.37 |
| 7 | Dak Prescott | 87.50 | Patrick Mahomes | 70.16 | Blake Bortles | 9.88 |
| 8 | Jordan Love | 86.00 | C.J. Stroud | 65.97 | Jake Browning | 9.69 |
| 9 | Trevor Lawrence | 85.00 | Baker Mayfield | 65.87 | Brandon Allen | 9.63 |
| 10 | Caleb Williams | 84.00 | Brock Purdy | 61.30 | Joe Burrow | 9.49 |
| 11 | Bo Nix | 83.00 | Daniel Jones | 58.13 | Sam Howell | 9.35 |
| 12 | Daniel Jones | 81.50 | Dak Prescott | 57.35 | Ben Roethlisberger | 9.31 |
| 13 | Justin Herbert | 79.50 | Kyler Murray | 55.62 | Malik Willis | 9.01 |
| 14 | Lamar Jackson | 78.00 | Jared Goff | 51.97 | Aidan O'Connell | 8.73 |
| 15 | Jaxson Dart | 77.00 | Bryce Young | 50.92 | Davis Mills | 8.55 |
| 16 | Jared Goff | 76.00 | Joe Burrow | 49.26 | Deshaun Watson | 8.01 |
| 17 | Joe Burrow | 75.00 | Geno Smith | 49.08 | Will Levis | 7.23 |
| 18 | Baker Mayfield | 74.00 | Matthew Stafford | 48.19 | Tommy DeVito | 7.16 |
| 19 | Jayden Daniels | 73.00 | Tua Tagovailoa | 44.56 | Sam Ehlinger | 6.90 |
| 20 | Kyler Murray | 72.00 | Jordan Love | 44.31 | Joe Flacco | 6.61 |
| 21 | C.J. Stroud | 71.00 | Marcus Mariota | 43.83 | Tua Tagovailoa | 6.32 |
| 22 | Sam Darnold | 70.00 | Sam Darnold | 43.29 | Kirk Cousins | 6.16 |
| 23 | Jacoby Brissett | 68.00 | Anthony Richardson | 42.57 | Carson Wentz | 6.03 |
| 24 | Aaron Rodgers | 66.00 | Blake Bortles | 42.46 | Bailey Zappe | 5.49 |
| 25 | Tyler Shough | 64.00 | Carson Wentz | 39.78 | Skylar Thompson | 5.08 |
| 26 | Bryce Young | 62.00 | Tyler Huntley | 37.68 | Trevor Siemian | 4.89 |
| 27 | Malik Willis | 60.00 | Deshaun Watson | 36.66 | Case Keenum | 4.72 |
| 28 | Tua Tagovailoa | 58.00 | Mac Jones | 36.50 | Kyler Murray | 4.68 |
| 29 | Geno Smith | 55.00 | Sam Howell | 36.12 | Jordan Love | 3.94 |
| 30 | Shedeur Sanders | 52.00 | Joe Flacco | 36.09 | Easton Stick | 3.85 |
| 31 | Cam Ward | 50.00 | Will Levis | 36.02 | Tyrod Taylor | 3.83 |
| 32 | Fernando Mendoza | 40.00 | Jacoby Brissett | 35.66 | Mitchell Trubisky | 3.71 |
| 33 | Justin Fields | 35.00 | Kirk Cousins | 33.58 | Sam Darnold | 2.89 |
| 34 | Jameis Winston | 33.00 | Tyson Bagent | 32.83 | Teddy Bridgewater | 2.72 |
| 35 | Carson Wentz | 31.00 | Aaron Rodgers | 31.50 | Andy Dalton | 2.63 |
| 36 | Mac Jones | 29.00 | Ben Roethlisberger | 31.27 | Kyle Allen | 2.23 |
| 37 | Marcus Mariota | 27.00 | Mason Rudolph | 30.46 | Mason Rudolph | 2.16 |
| 38 | J.J. McCarthy | 25.00 | Tyrod Taylor | 28.78 | Jacoby Brissett | 1.61 |
| 39 | Davis Mills | 23.00 | Aidan O'Connell | 28.17 | Anthony Richardson | 1.04 |
| 40 | Joe Flacco | 21.00 | Trey Lance | 27.91 | Drew Lock | 0.98 |
| 41 | Spencer Rattler | 18.00 | Tommy DeVito | 27.52 | Tyler Huntley | 0.80 |
| 42 | Jake Browning | 15.00 | Zach Wilson | 27.03 | Nick Mullens | -0.56 |
| 43 | Quinn Ewers | 12.00 | Jameis Winston | 26.44 | Quinn Ewers | -0.97 |
| 44 | Tyler Huntley | 10.00 | Drake Maye | 26.30 | Patrick Mahomes | -1.29 |
| 45 | Josh Johnson | 5.00 | Davis Mills | 25.41 | Mac Jones | -1.30 |

## RB Board Top 80
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey | 98.50 | Christian McCaffrey | 99.77 | Christian McCaffrey | 470.40 |
| 2 | Bijan Robinson | 95.00 | Jonathan Taylor | 99.49 | Bijan Robinson | 362.64 |
| 3 | Jahmyr Gibbs | 93.50 | Bijan Robinson | 99.45 | Kenneth Gainwell | 347.81 |
| 4 | Jonathan Taylor | 92.00 | Saquon Barkley | 99.34 | Jahmyr Gibbs | 339.59 |
| 5 | De'Von Achane | 91.00 | Derrick Henry | 99.19 | Chase Brown | 330.35 |
| 6 | Chase Brown | 85.00 | Kyren Williams | 99.17 | De'Von Achane | 305.63 |
| 7 | Javonte Williams | 84.00 | Jahmyr Gibbs | 99.07 | Ashton Jeanty | 247.80 |
| 8 | Saquon Barkley | 83.00 | James Cook | 98.88 | RJ Harvey | 217.99 |
| 9 | Kyren Williams | 82.50 | Travis Etienne | 98.85 | Tyjae Spears | 198.75 |
| 10 | Omarion Hampton | 81.00 | De'Von Achane | 98.68 | Michael Carter | 167.82 |
| 11 | James Cook | 80.00 | Breece Hall | 98.36 | Tyrone Tracy Jr. | 163.21 |
| 12 | Ashton Jeanty | 78.00 | Josh Jacobs | 98.00 | Dylan Sampson | 157.67 |
| 13 | Josh Jacobs | 77.50 | Javonte Williams | 97.42 | Rico Dowdle | 154.26 |
| 14 | Travis Etienne | 76.00 | Tony Pollard | 97.07 | Rachaad White | 146.18 |
| 15 | Cam Skattebo | 75.00 | D'Andre Swift | 96.43 | Kyren Williams | 140.72 |
| 16 | Bucky Irving | 74.00 | Kenneth Walker III | 96.07 | Javonte Williams | 140.36 |
| 17 | D'Andre Swift | 73.50 | Jaylen Warren | 93.86 | Brashard Smith | 139.65 |
| 18 | Breece Hall | 72.00 | Chase Brown | 93.13 | Tyler Badie | 138.56 |
| 19 | Derrick Henry | 71.00 | Rico Dowdle | 92.70 | Travis Etienne | 136.44 |
| 20 | Quinshon Judkins | 70.00 | Alvin Kamara | 92.49 | TreVeyon Henderson | 134.96 |
| 21 | Rico Dowdle | 69.00 | David Montgomery | 90.96 | D'Andre Swift | 134.46 |
| 22 | J.K. Dobbins | 68.00 | Rachaad White | 90.12 | Jaylen Warren | 133.65 |
| 23 | Aaron Jones | 67.00 | Aaron Jones | 89.69 | Omarion Hampton | 133.08 |
| 24 | Kenneth Walker III | 66.00 | Rhamondre Stevenson | 87.52 | Jerome Ford | 132.89 |
| 25 | Tony Pollard | 65.00 | Isiah Pacheco | 87.43 | Ty Johnson | 132.59 |
| 26 | TreVeyon Henderson | 64.00 | Zach Charbonnet | 86.60 | Aaron Jones | 129.26 |
| 27 | David Montgomery | 63.00 | Ashton Jeanty | 85.47 | Jeremy McNichols | 128.32 |
| 28 | Chuba Hubbard | 62.00 | J.K. Dobbins | 82.13 | Cam Skattebo | 127.26 |
| 29 | Jacory Croskey-Merritt | 61.00 | Chuba Hubbard | 80.43 | Jonathan Taylor | 126.40 |
| 30 | Bhayshul Tuten | 60.00 | Kenneth Gainwell | 78.03 | Breece Hall | 126.27 |
| 31 | Jaylen Warren | 59.00 | Tyler Allgeier | 74.83 | Chuba Hubbard | 122.90 |
| 32 | Alvin Kamara | 58.00 | Brian Robinson | 70.98 | Alvin Kamara | 119.02 |
| 33 | Rhamondre Stevenson | 57.00 | Quinshon Judkins | 70.70 | Rhamondre Stevenson | 118.74 |
| 34 | Zach Charbonnet | 56.00 | Devin Singletary | 67.12 | Justice Hill | 115.23 |
| 35 | Tyrone Tracy Jr. | 55.00 | Tyjae Spears | 65.07 | Saquon Barkley | 114.89 |
| 36 | Woody Marks | 54.00 | James Conner | 64.99 | Bucky Irving | 112.13 |
| 37 | RJ Harvey | 53.00 | Jordan Mason | 63.97 | Isaiah Davis | 109.79 |
| 38 | Kyle Monangai | 52.00 | Woody Marks | 59.29 | Josh Jacobs | 104.22 |
| 39 | Rachaad White | 51.00 | TreVeyon Henderson | 56.39 | Woody Marks | 101.74 |
| 40 | Isiah Pacheco | 50.00 | Tyrone Tracy Jr. | 56.02 | Quinshon Judkins | 92.18 |
| 41 | Jordan Mason | 49.00 | Bucky Irving | 54.01 | Tony Pollard | 86.53 |
| 42 | Chris Rodriguez Jr. | 48.00 | Michael Carter | 53.87 | Kyle Monangai | 82.00 |
| 43 | Tyler Allgeier | 47.00 | Chris Rodriguez Jr. | 53.21 | James Cook | 75.04 |
| 44 | Blake Corum | 46.00 | Emanuel Wilson | 52.88 | Kenneth Walker III | 74.57 |
| 45 | Kenneth Gainwell | 45.00 | Jerome Ford | 52.31 | Trey Benson | 73.44 |
| 46 | Tyjae Spears | 44.00 | RJ Harvey | 48.66 | Emari Demercado | 71.53 |
| 47 | James Conner | 43.00 | Kyle Monangai | 48.05 | Devin Neal | 69.30 |
| 48 | Kimani Vidal | 42.00 | Jacory Croskey-Merritt | 45.83 | Ameer Abdullah | 69.07 |
| 49 | Jawhar Jordan | 41.00 | Keaton Mitchell | 45.70 | Chris Brooks | 67.52 |
| 50 | Devin Singletary | 40.00 | Samaje Perine | 43.93 | Isiah Pacheco | 67.35 |
| 51 | Emanuel Wilson | 39.00 | Kimani Vidal | 41.99 | David Montgomery | 64.44 |
| 52 | Kendre Miller | 38.00 | Omarion Hampton | 39.20 | Samaje Perine | 64.14 |
| 53 | Jaydon Blue | 37.00 | Emari Demercado | 37.18 | Zavier Scott | 58.63 |
| 54 | Isaiah Davis | 36.00 | Blake Corum | 35.54 | Kimani Vidal | 53.09 |
| 55 | Sean Tucker | 35.00 | AJ Dillon | 35.36 | Zach Charbonnet | 49.90 |
| 56 | Ray Davis | 34.00 | Jeremy McNichols | 33.84 | Will Shipley | 43.07 |
| 57 | Trey Benson | 33.00 | Ty Johnson | 33.78 | Rasheen Ali | 41.90 |
| 58 | Michael Carter | 32.00 | Sean Tucker | 33.14 | Emanuel Wilson | 37.25 |
| 59 | Raheim Sanders | 31.00 | Justice Hill | 33.13 | Bhayshul Tuten | 36.54 |
| 60 | Devin Neal | 30.00 | Kendre Miller | 31.92 | LeQuint Allen Jr. | 35.81 |
| 61 | Phil Mafah | 29.00 | Malik Davis | 31.81 | Ray Davis | 35.14 |
| 62 | Jaret Patterson | 28.00 | Cam Skattebo | 31.50 | Devin Singletary | 32.27 |
| 63 | Jerome Ford | 27.00 | Jaleel McLaughlin | 29.02 | Keaton Mitchell | 29.35 |
| 64 | Brashard Smith | 26.00 | Tank Bigsby | 28.69 | James Conner | 25.18 |
| 65 | Zavier Scott | 25.00 | Jaret Patterson | 28.03 | Jawhar Jordan | 24.94 |
| 66 | Jeremy McNichols | 24.00 | Ty Chandler | 28.00 | Jordan Mason | 24.91 |
| 67 | Terrell Jennings | 23.00 | Le'Veon Bell | 27.80 | Sean Tucker | 21.93 |
| 68 | Ameer Abdullah | 22.00 | Elijah McGuire | 26.04 | Jaylen Wright | 18.51 |
| 69 | Samaje Perine | 21.00 | Ameer Abdullah | 22.98 | Ty Chandler | 16.33 |
| 70 | Jaylen Wright | 20.00 | Chris Brooks | 22.95 | Blake Corum | 15.78 |
| 71 | Dylan Sampson | 19.00 | Tyler Badie | 22.56 | Raheim Sanders | 14.96 |
| 72 | Ty Johnson | 18.00 | Dameon Pierce | 21.05 | Phil Mafah | 13.76 |
| 73 | Justice Hill | 17.00 | Roschon Johnson | 20.96 | Ollie Gordon II | 13.29 |
| 74 | Braelon Allen | 16.00 | Ito Smith | 20.04 | Tyler Allgeier | 12.56 |
| 75 | Keaton Mitchell | 15.00 | Elijah Mitchell | 19.55 | Braelon Allen | 11.58 |
| 76 | Emari Demercado | 14.00 | Salvon Ahmed | 19.23 | J.K. Dobbins | 11.03 |
| 77 | Brian Robinson | 13.00 | Bhayshul Tuten | 18.82 | Jaleel McLaughlin | 10.46 |
| 78 | Malik Davis | 12.00 | Jalen Richard | 18.76 | Tyler Goodson | 8.50 |
| 79 | DJ Giddens | 11.00 | Dylan Sampson | 18.74 | Dylan Laube | 7.89 |
| 80 | Tank Bigsby | 10.00 | Pierre Strong | 17.71 | Corey Kiner | 7.73 |

## WR Board Top 100
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Puka Nacua | 98.50 | Puka Nacua | 89.55 | Ja'Marr Chase | 845.95 |
| 2 | Jaxon Smith-Njigba | 97.00 | Ja'Marr Chase | 89.53 | Amon-Ra St. Brown | 790.33 |
| 3 | Amon-Ra St. Brown | 96.00 | Amon-Ra St. Brown | 88.51 | Puka Nacua | 758.48 |
| 4 | Ja'Marr Chase | 95.00 | Justin Jefferson | 86.35 | Jaxon Smith-Njigba | 754.51 |
| 5 | Justin Jefferson | 93.50 | CeeDee Lamb | 83.71 | Chris Olave | 717.83 |
| 6 | Garrett Wilson | 91.00 | Davante Adams | 78.44 | Justin Jefferson | 646.78 |
| 7 | Drake London | 90.00 | A.J. Brown | 74.22 | Wan'Dale Robinson | 646.06 |
| 8 | Rashee Rice | 89.00 | Chris Olave | 74.17 | George Pickens | 633.34 |
| 9 | Chris Olave | 88.00 | Zay Flowers | 72.41 | Michael Wilson | 581.34 |
| 10 | A.J. Brown | 87.00 | George Pickens | 71.52 | Emeka Egbuka | 576.84 |
| 11 | George Pickens | 85.50 | Jaxon Smith-Njigba | 70.31 | Courtland Sutton | 571.13 |
| 12 | Davante Adams | 84.00 | Courtland Sutton | 69.12 | A.J. Brown | 560.31 |
| 13 | Zay Flowers | 83.00 | Jakobi Meyers | 68.50 | Tetairoa McMillan | 559.49 |
| 14 | CeeDee Lamb | 82.00 | Nico Collins | 67.58 | Nico Collins | 557.43 |
| 15 | Nico Collins | 81.00 | Michael Pittman | 67.49 | Zay Flowers | 543.17 |
| 16 | Tetairoa McMillan | 79.50 | DJ Moore | 66.60 | CeeDee Lamb | 540.29 |
| 17 | Malik Nabers | 78.50 | Jaylen Waddle | 65.28 | Davante Adams | 528.68 |
| 18 | Wan'Dale Robinson | 77.50 | DeVonta Smith | 65.13 | Drake London | 525.56 |
| 19 | Rome Odunze | 76.50 | Rashee Rice | 63.23 | DeVonta Smith | 520.25 |
| 20 | DeVonta Smith | 75.50 | Mike Evans | 61.99 | Jakobi Meyers | 503.76 |
| 21 | Terry McLaurin | 74.50 | Cooper Kupp | 60.84 | Michael Pittman | 501.39 |
| 22 | Jaylen Waddle | 73.50 | Garrett Wilson | 60.03 | Jerry Jeudy | 486.51 |
| 23 | Tee Higgins | 72.50 | DK Metcalf | 59.88 | Ladd McConkey | 481.60 |
| 24 | Alec Pierce | 71.50 | Jordan Addison | 59.80 | Jameson Williams | 476.33 |
| 25 | Courtland Sutton | 70.50 | Drake London | 59.25 | Troy Franklin | 468.82 |
| 26 | Emeka Egbuka | 69.50 | Tee Higgins | 59.12 | Jaylen Waddle | 462.09 |
| 27 | Mike Evans | 68.50 | Tank Dell | 57.79 | Tee Higgins | 454.28 |
| 28 | Jameson Williams | 67.50 | Michael Wilson | 56.93 | DK Metcalf | 452.53 |
| 29 | Quentin Johnston | 66.50 | Wan'Dale Robinson | 56.18 | Parker Washington | 440.38 |
| 30 | Michael Wilson | 65.50 | Chris Godwin Jr. | 53.97 | Khalil Shakir | 439.11 |
| 31 | Christian Watson | 64.50 | Terry McLaurin | 52.88 | Tre Tucker | 425.77 |
| 32 | Jordan Addison | 63.50 | Romeo Doubs | 50.24 | Jauan Jennings | 422.82 |
| 33 | DK Metcalf | 62.50 | Jerry Jeudy | 49.15 | Rashid Shaheed | 418.89 |
| 34 | Ladd McConkey | 61.50 | Brandon Aiyuk | 46.71 | Rome Odunze | 416.59 |
| 35 | Jakobi Meyers | 60.50 | Rashid Shaheed | 45.54 | Brian Thomas Jr. | 407.70 |
| 36 | Romeo Doubs | 59.50 | Josh Downs | 45.02 | Elic Ayomanor | 403.13 |
| 37 | Tre Tucker | 58.50 | Calvin Ridley | 43.35 | Josh Downs | 401.90 |
| 38 | Parker Washington | 57.50 | Jameson Williams | 43.22 | Romeo Doubs | 396.10 |
| 39 | Ricky Pearsall | 56.50 | Christian Watson | 43.20 | Quentin Johnston | 395.39 |
| 40 | Jerry Jeudy | 55.50 | Quentin Johnston | 41.22 | Alec Pierce | 394.45 |
| 41 | Troy Franklin | 54.50 | Tre Tucker | 40.74 | DJ Moore | 377.65 |
| 42 | Jauan Jennings | 53.50 | Jayden Reed | 40.09 | Rashee Rice | 370.61 |
| 43 | Khalil Shakir | 52.50 | Khalil Shakir | 38.98 | Jordan Addison | 367.24 |
| 44 | Keon Coleman | 51.50 | Parker Washington | 36.81 | Marquise Brown | 335.73 |
| 45 | Brian Thomas Jr. | 50.50 | Jauan Jennings | 36.59 | Darnell Mooney | 331.88 |
| 46 | Xavier Worthy | 49.50 | Marquise Brown | 36.05 | Adonai Mitchell | 331.12 |
| 47 | Michael Pittman | 48.50 | Darius Slayton | 35.58 | Xavier Worthy | 326.12 |
| 48 | Jalen Coker | 47.50 | Alec Pierce | 35.38 | Chimere Dike | 326.01 |
| 49 | Jayden Reed | 46.50 | Christian Kirk | 34.56 | Cooper Kupp | 317.74 |
| 50 | Josh Downs | 45.50 | Darnell Mooney | 34.51 | Jayden Higgins | 303.16 |
| 51 | Rashid Shaheed | 44.50 | DeMario Douglas | 31.65 | Mack Hollins | 302.03 |
| 52 | Cooper Kupp | 43.50 | Dontayvion Wicks | 31.32 | Olamide Zaccheaus | 299.33 |
| 53 | Chris Godwin Jr. | 42.50 | Mack Hollins | 31.05 | Mike Evans | 293.36 |
| 54 | Devaughn Vele | 41.50 | Andrei Iosivas | 28.70 | Darius Slayton | 293.35 |
| 55 | Jalen McMillan | 40.50 | Odell Beckham Jr. | 28.67 | Garrett Wilson | 290.00 |
| 56 | Marquise Brown | 39.50 | Kendrick Bourne | 27.65 | Xavier Legette | 286.70 |
| 57 | DJ Moore | 38.50 | K.J. Osborn | 26.81 | Terry McLaurin | 284.37 |
| 58 | Darius Slayton | 37.50 | Olamide Zaccheaus | 26.79 | Malik Washington | 283.13 |
| 59 | Calvin Ridley | 36.50 | Demarcus Robinson | 25.42 | Andrei Iosivas | 269.74 |
| 60 | Darnell Mooney | 35.50 | Marvin Mims Jr. | 24.72 | Keon Coleman | 268.65 |
| 61 | Travis Hunter | 34.50 | Van Jefferson | 24.51 | Xavier Hutchinson | 264.56 |
| 62 | Mack Hollins | 33.50 | Calvin Austin III | 24.23 | Christian Watson | 263.64 |
| 63 | Elic Ayomanor | 32.50 | Elijah Moore | 24.07 | Luther Burden III | 260.11 |
| 64 | Jakobie Keeney-James | 31.50 | Trey Palmer | 23.90 | Calvin Austin III | 257.77 |
| 65 | Kayshon Boutte | 30.50 | Rashod Bateman | 23.52 | Jalen Nailor | 248.49 |
| 66 | Van Jefferson | 29.50 | Cedric Tillman | 23.46 | Ryan Flournoy | 246.17 |
| 67 | Xavier Legette | 28.50 | Jahan Dotson | 22.77 | Ricky Pearsall | 243.69 |
| 68 | Jayden Higgins | 27.50 | Xavier Hutchinson | 22.59 | Kendrick Bourne | 242.81 |
| 69 | Adonai Mitchell | 26.50 | Tutu Atwell | 22.17 | Van Jefferson | 239.71 |
| 70 | Andrei Iosivas | 25.50 | Tim Patrick | 22.11 | Christian Kirk | 235.00 |
| 71 | Tyquan Thornton | 24.50 | KaVontae Turpin | 21.95 | Chris Godwin Jr. | 230.51 |
| 72 | Theo Wease Jr. | 23.50 | John Metchie III | 21.88 | Marvin Mims Jr. | 227.38 |
| 73 | Olamide Zaccheaus | 22.50 | Emeka Egbuka | 21.41 | Kayshon Boutte | 222.29 |
| 74 | Chimere Dike | 21.50 | Tetairoa McMillan | 21.21 | John Metchie III | 220.28 |
| 75 | Malik Washington | 20.50 | Greg Dortch | 21.02 | Pat Bryant | 216.96 |
| 76 | Ryan Flournoy | 19.50 | Marquez Valdes-Scantling | 20.35 | Dontayvion Wicks | 213.65 |
| 77 | Kendrick Bourne | 18.50 | Allen Hurns | 20.22 | Travis Hunter | 206.18 |
| 78 | Calvin Austin III | 17.50 | JuJu Smith-Schuster | 19.11 | DeMario Douglas | 204.32 |
| 79 | Pat Bryant | 16.50 | Kayshon Boutte | 18.45 | JuJu Smith-Schuster | 203.01 |
| 80 | Dontayvion Wicks | 15.50 | Tyler Johnson | 18.36 | Jalen Coker | 194.92 |
| 81 | Xavier Hutchinson | 14.50 | Quez Watkins | 17.99 | Tez Johnson | 190.94 |
| 82 | Rashod Bateman | 13.50 | Jalen Nailor | 17.87 | Matthew Golden | 190.74 |
| 83 | Matthew Golden | 12.50 | Nick Westbrook-Ikhine | 17.78 | Isaiah Bond | 190.70 |
| 84 | Jalen Nailor | 11.50 | David Moore | 17.77 | Tre Harris | 185.83 |
| 85 | Tory Horton | 10.50 | Jonathan Mingo | 17.75 | Cedric Tillman | 183.08 |
| 86 | Tez Johnson | 9.50 | Troy Franklin | 17.40 | Rashod Bateman | 178.24 |
| 87 | DeMario Douglas | 8.50 | Brandon Johnson | 17.37 | Devaughn Vele | 176.00 |
| 88 | Christian Kirk | 7.50 | Ladd McConkey | 17.34 | Malik Nabers | 175.41 |
| 89 | Luther Burden III | 6.50 | Kalif Raymond | 17.09 | Tyquan Thornton | 174.29 |
| 90 | Isaiah Bond | 5.50 | Terrace Marshall Jr. | 17.05 | Dyami Brown | 173.79 |
| 91 | Treylon Burks | 4.50 | David Sills | 16.85 | KaVontae Turpin | 170.46 |
| 92 | Tre Harris | 3.50 | Lil'Jordan Humphrey | 16.72 | David Sills | 168.36 |
| 93 | Isaac TeSlaa | 3.00 | Jalen Tolbert | 16.58 | Calvin Ridley | 168.00 |
| 94 | Marquez Valdes-Scantling | 2.50 | Tyquan Thornton | 16.53 | Jahan Dotson | 162.15 |
| 95 | Casey Washington | 2.00 | Rome Odunze | 16.46 | Jalen Tolbert | 161.78 |
| 96 | Jalen Tolbert | 1.50 | Tyler Scott | 16.33 | Demarcus Robinson | 158.70 |
| 97 | Cedric Tillman | 1.00 | Dyami Brown | 16.32 | Isaiah Williams | 150.91 |
| 98 | Devontez Walker | 0.50 | Treylon Burks | 15.98 | Greg Dortch | 147.63 |
| 99 | John Metchie III | 0.20 | Cedrick Wilson Jr. | 15.21 | Jaylin Noel | 144.89 |
| 100 | Lil'Jordan Humphrey | 0.10 | Brian Thomas Jr. | 15.03 | Marquez Valdes-Scantling | 134.84 |

## TE Board Top 35
| Rank | Current | Score | Logistic | Score | Linear | Score |
|---|---|---|---|---|---|---|
| 1 | Trey McBride | 98.50 | Trey McBride | 78.36 | Trey McBride | 782.05 |
| 2 | Brock Bowers | 94.00 | Travis Kelce | 72.53 | Kyle Pitts | 543.58 |
| 3 | George Kittle | 89.50 | George Kittle | 67.60 | Tyler Warren | 506.77 |
| 4 | Tucker Kraft | 88.00 | Sam LaPorta | 62.63 | Travis Kelce | 490.91 |
| 5 | Kyle Pitts | 86.50 | Kyle Pitts | 57.27 | Dalton Schultz | 483.69 |
| 6 | Sam LaPorta | 85.00 | Jake Ferguson | 56.82 | Harold Fannin Jr. | 477.71 |
| 7 | Tyler Warren | 84.00 | Mark Andrews | 54.95 | Juwan Johnson | 469.84 |
| 8 | Dallas Goedert | 83.00 | Dallas Goedert | 51.97 | Jake Ferguson | 469.56 |
| 9 | Travis Kelce | 82.00 | Dalton Schultz | 49.74 | Hunter Henry | 403.06 |
| 10 | Hunter Henry | 81.00 | David Njoku | 49.43 | Brock Bowers | 397.61 |
| 11 | Dalton Schultz | 80.00 | Evan Engram | 49.35 | Dallas Goedert | 380.91 |
| 12 | Juwan Johnson | 79.00 | Hunter Henry | 47.49 | Cade Otton | 373.18 |
| 13 | Colston Loveland | 78.00 | T.J. Hockenson | 45.85 | Colston Loveland | 370.09 |
| 14 | Jake Ferguson | 77.00 | Juwan Johnson | 45.33 | Chig Okonkwo | 356.23 |
| 15 | Brenton Strange | 76.00 | Cade Otton | 43.91 | Evan Engram | 341.39 |
| 16 | Harold Fannin Jr. | 75.00 | Cole Kmet | 42.20 | Theo Johnson | 335.44 |
| 17 | Dalton Kincaid | 74.00 | Dalton Kincaid | 40.59 | George Kittle | 326.37 |
| 18 | Cade Otton | 72.00 | Tucker Kraft | 38.37 | Mark Andrews | 317.81 |
| 19 | Mark Andrews | 71.00 | Chig Okonkwo | 36.25 | Oronde Gadsden II | 310.61 |
| 20 | T.J. Hockenson | 70.00 | Pat Freiermuth | 33.24 | AJ Barner | 302.03 |
| 21 | Oronde Gadsden II | 68.00 | Tyler Higbee | 28.04 | T.J. Hockenson | 300.66 |
| 22 | AJ Barner | 67.00 | Michael Mayer | 27.57 | Mason Taylor | 293.58 |
| 23 | Greg Dulcich | 65.00 | Mike Gesicki | 27.55 | Brenton Strange | 286.97 |
| 24 | Pat Freiermuth | 64.00 | Dawson Knox | 25.93 | Colby Parkinson | 264.14 |
| 25 | Evan Engram | 62.00 | Luke Musgrave | 25.13 | Pat Freiermuth | 246.43 |
| 26 | Isaiah Likely | 60.00 | Noah Fant | 24.25 | Gunnar Helm | 241.43 |
| 27 | Chig Okonkwo | 58.00 | Jack Doyle | 24.20 | Michael Mayer | 233.88 |
| 28 | Mike Gesicki | 56.00 | Colby Parkinson | 23.99 | Sam LaPorta | 232.54 |
| 29 | Gunnar Helm | 54.00 | Isaiah Likely | 23.39 | Dalton Kincaid | 227.86 |
| 30 | Ja'Tavion Sanders | 52.00 | Brenton Strange | 23.32 | Dawson Knox | 226.80 |
| 31 | Terrance Ferguson | 48.00 | Darren Fells | 23.28 | Jake Tonges | 224.86 |
| 32 | Theo Johnson | 46.00 | Noah Gray | 21.89 | David Njoku | 219.79 |
| 33 | Mason Taylor | 45.00 | Davis Allen | 21.39 | Cole Kmet | 219.38 |
| 34 | Jake Tonges | 44.00 | Tyler Warren | 21.20 | Tucker Kraft | 218.53 |
| 35 | Albert Okwuegbunam | 43.00 | Tyler Conklin | 20.65 | Darnell Washington | 205.58 |

## Logistic Risers
| Player | Pos | Current | Logistic | Delta | Missing % |
|---|---|---|---|---|---|
| Brian Robinson | RB | 261 | 50 | +211 | 24.1% |
| Justin Fields | QB | 189 | 41 | +148 | 27.6% |
| Keaton Mitchell | RB | 257 | 114 | +143 | 37.9% |
| Tyler Huntley | QB | 268 | 139 | +129 | 27.6% |
| Jerome Ford | RB | 219 | 96 | +123 | 24.1% |
| Samaje Perine | RB | 240 | 120 | +120 | 19.5% |
| Rachaad White | RB | 143 | 24 | +119 | 24.1% |
| Kenneth Gainwell | RB | 159 | 40 | +119 | 21.8% |
| DJ Moore | WR | 179 | 60 | +119 | 17.2% |
| Emari Demercado | RB | 259 | 140 | +119 | 34.5% |
| Christian Kirk | WR | 272 | 155 | +117 | 21.8% |
| Isiah Pacheco | RB | 146 | 30 | +116 | 24.1% |
| Devin Singletary | RB | 175 | 59 | +116 | 17.2% |
| Tyler Allgeier | RB | 153 | 42 | +111 | 24.1% |
| Michael Carter | RB | 201 | 92 | +109 | 24.1% |
| DeMario Douglas | WR | 271 | 166 | +105 | 34.5% |
| Alvin Kamara | RB | 124 | 20 | +104 | 19.5% |
| Jaylen Warren | RB | 120 | 17 | +103 | 24.1% |
| James Conner | RB | 165 | 66 | +99 | 19.5% |
| Malik Davis | RB | 264 | 165 | +99 | 34.5% |

## Logistic Fallers
| Player | Pos | Current | Logistic | Delta | Missing % |
|---|---|---|---|---|---|
| Fernando Mendoza | QB | 173 | 719 | -546 | 100.0% |
| Malik Nabers | WR | 53 | 384 | -331 | 85.1% |
| Ja'Tavion Sanders | TE | 139 | 426 | -287 | 85.1% |
| Terrance Ferguson | TE | 150 | 436 | -286 | 85.1% |
| Jalen McMillan | WR | 172 | 455 | -283 | 85.1% |
| Shedeur Sanders | QB | 140 | 417 | -277 | 85.1% |
| Jakobie Keeney-James | WR | 202 | 468 | -266 | 85.1% |
| Jalen Coker | WR | 152 | 408 | -256 | 85.1% |
| Gunnar Helm | TE | 134 | 389 | -255 | 85.1% |
| Ricky Pearsall | WR | 127 | 378 | -251 | 85.1% |
| Devaughn Vele | WR | 169 | 420 | -251 | 85.1% |
| Oronde Gadsden II | TE | 91 | 339 | -248 | 85.1% |
| Brock Bowers | TE | 11 | 255 | -244 | 85.1% |
| Colston Loveland | TE | 55 | 299 | -244 | 85.1% |
| Phil Mafah | RB | 212 | 453 | -241 | 85.1% |
| Tyler Shough | QB | 105 | 344 | -239 | 85.1% |
| Jackson Hawes | TE | 204 | 443 | -239 | 85.1% |
| Theo Wease Jr. | WR | 230 | 469 | -239 | 85.1% |
| Ben Sinnott | TE | 228 | 466 | -238 | 85.1% |
| Keon Coleman | WR | 142 | 375 | -233 | 85.1% |

## Cutline Crossings
| Model | Cutline | Entered | Entered sample | Exited | Exited sample |
|---|---|---|---|---|---|
| enriched_logistic | overall top 24 | 17 | Saquon Barkley, Derrick Henry, Kyren Williams, James Cook, Travis Etienne | 17 | Puka Nacua, Ja'Marr Chase, Amon-Ra St. Brown, Justin Jefferson, Trey McBride |
| enriched_logistic | overall top 50 | 24 | Derrick Henry, Travis Etienne, Breece Hall, Josh Jacobs, Tony Pollard | 24 | Jaxon Smith-Njigba, Patrick Mahomes, George Kittle, Nico Collins, Rashee Rice |
| enriched_logistic | overall top 100 | 34 | Tony Pollard, Jaylen Warren, Alvin Kamara, David Montgomery, Rachaad White | 34 | Dalton Schultz, Joe Burrow, Matthew Stafford, Hunter Henry, T.J. Hockenson |
| enriched_logistic | QB12 | 5 | Lamar Jackson, Justin Fields, Justin Herbert, C.J. Stroud, Baker Mayfield | 5 | Matthew Stafford, Jordan Love, Drake Maye, Bo Nix, Caleb Williams |
| enriched_logistic | RB12 | 4 | Derrick Henry, Travis Etienne, Breece Hall, Josh Jacobs | 4 | Javonte Williams, Chase Brown, Ashton Jeanty, Omarion Hampton |
| enriched_logistic | RB24 | 6 | Tony Pollard, Jaylen Warren, Alvin Kamara, David Montgomery, Rachaad White | 6 | Ashton Jeanty, J.K. Dobbins, Quinshon Judkins, Bucky Irving, Omarion Hampton |
| enriched_logistic | RB36 | 8 | Rachaad White, Isiah Pacheco, Kenneth Gainwell, Tyler Allgeier, Brian Robinson | 8 | Woody Marks, TreVeyon Henderson, Tyrone Tracy Jr., Bucky Irving, Jacory Croskey-Merritt |
| enriched_logistic | WR12 | 3 | CeeDee Lamb, Zay Flowers, Courtland Sutton | 3 | Rashee Rice, Garrett Wilson, Drake London |
| enriched_logistic | WR24 | 8 | Courtland Sutton, Jakobi Meyers, Michael Pittman, DJ Moore, Mike Evans | 8 | Drake London, Tee Higgins, Wan'Dale Robinson, Terry McLaurin, Alec Pierce |
| enriched_logistic | WR36 | 9 | Michael Pittman, DJ Moore, Cooper Kupp, Tank Dell, Chris Godwin Jr. | 9 | Jameson Williams, Christian Watson, Quentin Johnston, Alec Pierce, Emeka Egbuka |
| enriched_logistic | TE6 | 2 | Travis Kelce, Jake Ferguson | 2 | Tucker Kraft, Brock Bowers |
| enriched_logistic | TE12 | 4 | Jake Ferguson, Mark Andrews, David Njoku, Evan Engram | 4 | Juwan Johnson, Tucker Kraft, Tyler Warren, Brock Bowers |
| enriched_logistic | TE18 | 5 | Mark Andrews, David Njoku, Evan Engram, T.J. Hockenson, Cole Kmet | 5 | Brenton Strange, Tyler Warren, Harold Fannin Jr., Brock Bowers, Colston Loveland |
| enriched_linear_points | overall top 24 | 16 | Wan'Dale Robinson, George Pickens, Michael Wilson, Emeka Egbuka, Courtland Sutton | 16 | Christian McCaffrey, Brock Bowers, Rashee Rice, Bijan Robinson, Jahmyr Gibbs |
| enriched_linear_points | overall top 50 | 29 | Wan'Dale Robinson, Michael Wilson, Emeka Egbuka, Courtland Sutton, Tetairoa McMillan | 29 | Dallas Goedert, Rashee Rice, Bijan Robinson, Jahmyr Gibbs, Chase Brown |
| enriched_linear_points | overall top 100 | 46 | Jakobi Meyers, Michael Pittman, Jerry Jeudy, Ladd McConkey, Troy Franklin | 46 | Sam LaPorta, Dalton Kincaid, Tucker Kraft, Malik Nabers, Rico Dowdle |
| enriched_linear_points | QB12 | 10 | Jameis Winston, Aaron Rodgers, Josh Johnson, Jared Goff, Blake Bortles | 10 | Jordan Love, Patrick Mahomes, Dak Prescott, Daniel Jones, Trevor Lawrence |
| enriched_linear_points | RB12 | 6 | Kenneth Gainwell, RJ Harvey, Tyjae Spears, Michael Carter, Tyrone Tracy Jr. | 6 | Kyren Williams, Javonte Williams, Omarion Hampton, Jonathan Taylor, Saquon Barkley |
| enriched_linear_points | RB24 | 12 | Kenneth Gainwell, RJ Harvey, Tyjae Spears, Michael Carter, Tyrone Tracy Jr. | 12 | Aaron Jones, Cam Skattebo, Jonathan Taylor, Breece Hall, Saquon Barkley |
| enriched_linear_points | RB36 | 12 | Kenneth Gainwell, RJ Harvey, Tyjae Spears, Michael Carter, Dylan Sampson | 12 | Josh Jacobs, Woody Marks, Quinshon Judkins, Tony Pollard, James Cook |
| enriched_linear_points | WR12 | 4 | Wan'Dale Robinson, Michael Wilson, Emeka Egbuka, Courtland Sutton | 4 | Davante Adams, Drake London, Rashee Rice, Garrett Wilson |
| enriched_linear_points | WR24 | 8 | Michael Wilson, Emeka Egbuka, Courtland Sutton, Jakobi Meyers, Michael Pittman | 8 | Jaylen Waddle, Tee Higgins, Rome Odunze, Alec Pierce, Rashee Rice |
| enriched_linear_points | WR36 | 10 | Michael Pittman, Jerry Jeudy, Troy Franklin, Parker Washington, Khalil Shakir | 10 | Romeo Doubs, Quentin Johnston, Alec Pierce, Rashee Rice, Jordan Addison |
| enriched_linear_points | TE6 | 4 | Tyler Warren, Travis Kelce, Dalton Schultz, Harold Fannin Jr. | 4 | Brock Bowers, George Kittle, Sam LaPorta, Tucker Kraft |
| enriched_linear_points | TE12 | 3 | Harold Fannin Jr., Jake Ferguson, Cade Otton | 3 | George Kittle, Sam LaPorta, Tucker Kraft |
| enriched_linear_points | TE18 | 4 | Chig Okonkwo, Evan Engram, Theo Johnson, Mark Andrews | 4 | Brenton Strange, Sam LaPorta, Dalton Kincaid, Tucker Kraft |

## TE35 Watch Band
| Model | TE rank | Player | Score | Current TE rank | Missing % |
|---|---|---|---|---|---|
| enriched_logistic | 30 | Brenton Strange | 23.32 | 15 | 42.5% |
| enriched_logistic | 31 | Darren Fells | 23.28 |  | 27.6% |
| enriched_logistic | 32 | Noah Gray | 21.89 |  | 24.1% |
| enriched_logistic | 33 | Davis Allen | 21.39 | 53 | 39.1% |
| enriched_logistic | 34 | Tyler Warren | 21.20 | 7 | 85.1% |
| enriched_logistic | 35 | Tyler Conklin | 20.65 |  | 19.5% |
| enriched_logistic | 36 | Tommy Tremble | 20.61 | 48 | 24.1% |
| enriched_logistic | 37 | Ryan Izzo | 19.89 |  | 41.4% |
| enriched_logistic | 38 | Harold Fannin Jr. | 19.70 | 16 | 85.1% |
| enriched_logistic | 39 | Daniel Bellinger | 19.02 | 44 | 21.8% |
| enriched_logistic | 40 | Darnell Washington | 19.02 | 38 | 42.5% |
| enriched_linear_points | 30 | Dawson Knox | 226.80 | 39 | 24.1% |
| enriched_linear_points | 31 | Jake Tonges | 224.86 | 34 | 43.7% |
| enriched_linear_points | 32 | David Njoku | 219.79 | 36 | 19.5% |
| enriched_linear_points | 33 | Cole Kmet | 219.38 | 40 | 24.1% |
| enriched_linear_points | 34 | Tucker Kraft | 218.53 | 4 | 39.1% |
| enriched_linear_points | 35 | Darnell Washington | 205.58 | 38 | 42.5% |
| enriched_linear_points | 36 | Mike Gesicki | 194.00 | 28 | 24.1% |
| enriched_linear_points | 37 | Noah Fant | 185.81 | 59 | 24.1% |
| enriched_linear_points | 38 | Tommy Tremble | 171.35 | 48 | 24.1% |
| enriched_linear_points | 39 | Elijah Higgins | 170.72 |  | 42.5% |
| enriched_linear_points | 40 | Noah Gray | 170.15 |  | 24.1% |
