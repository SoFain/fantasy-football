# Standard BQML V2 Overlay Calibration

Phase 33.12 calibrated the Phase 33.11 Standard conservative overlay. This is owner-review evidence only.

Current Pigskin remains live for Standard. No champion is active. No live rankings changed.

Selected review rule: `overlay_80_15_5_anchor_v0`.

Formula:

- 80 percent Current Pigskin normalized score.
- 15 percent BQML VOR normalized score.
- 5 percent finalist safety or elite signal.

Decision read: the 80/15/5 anchor materially reduces the Phase 33.11 movement problem while preserving a small BQML/VOR signal. It is safer for owner review, but it is not ready for champion activation. Historical cross-position evaluation still needs a stronger live-like baseline before champion selection.

Main reasons:

- QB top-24 count fell from 8 in the rerun original overlay to 6.
- Rank deltas over 20 fell from 58 to 21.
- WR/TE current top-24 exits fell from 7 to 4.
- Jaxon Smith-Njigba, Drake London, Rashee Rice, and Garrett Wilson were pulled closer to the Current Pigskin board.
- Jalen Hurts, Daniel Jones, Saquon Barkley, Josh Jacobs, and Lamar Jackson still move enough to require owner review.

Historical caveat: the 2024-2025 proxy evaluation in this pass uses `profile_points_score` as the Current Pigskin-like baseline because historical Current Pigskin live boards are not available in the same shape. That proxy ranks QBs across the whole top 24, so it is useful for directional checks but not sufficient as champion-selection proof.

Recommended next phase: hold Current Pigskin for Standard or build a dashboard-facing calibrated board for owner inspection. Do not activate a Standard BQML champion from this evidence alone.

## Generated Evidence

Generated at: 2026-07-07T18:42:54.181689+00:00

## Read-Only Query Jobs

- 2026 overlay query job: `b2af69f9-0111-49c8-99a8-fc93448f2653`
- 2024-2025 historical query job: `b2fcec8c-aae9-44b9-8f4e-3f6decdcebd8`

## 2026 Candidate Summary

| Rule | Top 24 mix | Top 50 mix | Top 100 mix | Delta >20 | High-missingness risers | QB top24 | WR/TE top24 exits | Top24 overlap |
|---|---|---|---|---:|---:|---:|---:|---:|
| `overlay_70_20_10_original_v0` | {'QB': 8, 'RB': 8, 'WR': 6, 'TE': 2} | {'QB': 14, 'RB': 14, 'WR': 15, 'TE': 7} | {'QB': 21, 'RB': 27, 'WR': 35, 'TE': 17} | 58 | 79 | 8 | 7 | 15 |
| `overlay_80_15_5_anchor_v0` | {'QB': 6, 'RB': 7, 'WR': 9, 'TE': 2} | {'QB': 13, 'RB': 13, 'WR': 16, 'TE': 8} | {'QB': 21, 'RB': 27, 'WR': 34, 'TE': 18} | 21 | 67 | 6 | 4 | 18 |
| `overlay_85_10_5_anchor_v0` | {'QB': 5, 'RB': 6, 'WR': 10, 'TE': 3} | {'QB': 11, 'RB': 12, 'WR': 19, 'TE': 8} | {'QB': 21, 'RB': 26, 'WR': 35, 'TE': 18} | 10 | 70 | 5 | 2 | 21 |
| `overlay_missingness_gate_v0` | {'QB': 6, 'RB': 7, 'WR': 9, 'TE': 2} | {'QB': 11, 'RB': 11, 'WR': 20, 'TE': 8} | {'QB': 21, 'RB': 27, 'WR': 34, 'TE': 18} | 8 | 73 | 6 | 4 | 19 |
| `overlay_vor_percentile_calibrated_v0` | {'QB': 3, 'RB': 6, 'WR': 12, 'TE': 3} | {'QB': 10, 'RB': 12, 'WR': 22, 'TE': 6} | {'QB': 21, 'RB': 25, 'WR': 38, 'TE': 16} | 71 | 102 | 3 | 3 | 19 |
| `overlay_rank_delta_cap_20_v0` | {'QB': 7, 'RB': 8, 'WR': 7, 'TE': 2} | {'QB': 13, 'RB': 14, 'WR': 15, 'TE': 8} | {'QB': 22, 'RB': 25, 'WR': 35, 'TE': 18} | 34 | 83 | 7 | 6 | 16 |

## 2026 VOR And Finalist Diagnostics

| Position | VOR norm avg | VOR norm min | VOR norm max | Finalist avg | Finalist min | Finalist max | Avg original rank delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| QB | 0.239 | 0.018 | 1.000 | 0.369 | 0.000 | 1.000 | -8.7 |
| RB | 0.167 | 0.018 | 0.502 | 0.385 | 0.000 | 0.978 | -9.4 |
| WR | 0.049 | 0.000 | 0.153 | 0.158 | 0.000 | 0.603 | 9.6 |
| TE | 0.052 | 0.018 | 0.106 | 0.327 | 0.000 | 0.670 | 5.3 |

## Major Movers Under Original 70/20/10

| Player | Pos | Current | Original rank | 80/15/5 rank | VOR norm | Finalist norm | Current norm | Missing rate | Flags |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Jalen Hurts | QB | 34 | 2 | 3 | 1.000 | 1.000 | 0.873 | 0.600 | fragile role; box-score support outruns role quality |
| Lamar Jackson | QB | 76 | 22 | 39 | 0.548 | 0.918 | 0.751 | 0.523 | fragile role; box-score support outruns role quality |
| Daniel Jones | QB | 43 | 12 | 18 | 0.541 | 0.663 | 0.847 | 0.529 | fragile role; box-score support outruns role quality |
| Kyler Murray | QB | 100 | 48 | 65 | 0.540 | 0.713 | 0.688 | 0.547 | fragile role; box-score support outruns role quality |
| Saquon Barkley | RB | 49 | 10 | 20 | 0.502 | 0.978 | 0.831 | 0.477 | no major Pigskin ranking flag |
| Josh Jacobs | RB | 64 | 26 | 38 | 0.433 | 0.890 | 0.783 | 0.488 | no major Pigskin ranking flag |
| Derrick Henry | RB | 91 | 42 | 58 | 0.436 | 0.883 | 0.714 | 0.435 | no major Pigskin ranking flag |
| Jaxon Smith-Njigba | WR | 1 | 24 | 13 | 0.046 | 0.160 | 1.000 | 0.588 | no major Pigskin ranking flag |
| Drake London | WR | 8 | 29 | 19 | 0.056 | 0.211 | 0.965 | 0.565 | no major Pigskin ranking flag |
| Brock Bowers | TE | 11 | 44 | 31 | 0.018 | 0.000 | 0.952 | 0.000 | no major Pigskin ranking flag |
| Rashee Rice | WR | 15 | 34 | 23 | 0.071 | 0.293 | 0.940 | 0.553 | no major Pigskin ranking flag |
| Garrett Wilson | WR | 18 | 31 | 27 | 0.082 | 0.392 | 0.926 | 0.518 | no major Pigskin ranking flag |

## Historical Evaluation

| Year | Rule | Top24 | Top50 | Top100 | Points cap100 | VOR cap100 | Bust top50 | Missing top100 | Top24 mix |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2024 | `current_pigskin_proxy_v0` | 0.708 | 0.900 | 0.980 | 1.000 | 1.000 | 0.020 | 0.548 | {'QB': 24} |
| 2025 | `current_pigskin_proxy_v0` | 0.875 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.529 | {'QB': 24} |
| 2024 | `overlay_70_20_10_original_v0` | 0.667 | 0.900 | 0.960 | 0.995 | 1.002 | 0.020 | 0.552 | {'QB': 24} |
| 2025 | `overlay_70_20_10_original_v0` | 0.875 | 1.000 | 1.000 | 0.956 | 0.564 | 0.000 | 0.492 | {'QB': 24} |
| 2024 | `overlay_80_15_5_anchor_v0` | 0.708 | 0.900 | 0.960 | 0.995 | 1.002 | 0.020 | 0.552 | {'QB': 24} |
| 2025 | `overlay_80_15_5_anchor_v0` | 0.875 | 1.000 | 1.000 | 0.968 | 0.747 | 0.000 | 0.507 | {'QB': 24} |
| 2024 | `overlay_85_10_5_anchor_v0` | 0.708 | 0.900 | 0.960 | 0.995 | 1.002 | 0.020 | 0.552 | {'QB': 24} |
| 2025 | `overlay_85_10_5_anchor_v0` | 0.875 | 1.000 | 1.000 | 0.961 | 0.739 | 0.000 | 0.506 | {'QB': 24} |
| 2024 | `overlay_vor_percentile_calibrated_v0` | 0.708 | 0.900 | 0.960 | 0.995 | 1.002 | 0.020 | 0.552 | {'QB': 24} |
| 2025 | `overlay_vor_percentile_calibrated_v0` | 0.875 | 1.000 | 1.000 | 0.976 | 0.745 | 0.000 | 0.505 | {'QB': 24} |
| 2024 | `overlay_missingness_gate_v0` | 0.708 | 0.900 | 0.960 | 0.995 | 1.002 | 0.020 | 0.552 | {'QB': 24} |
| 2025 | `overlay_missingness_gate_v0` | 0.875 | 1.000 | 1.000 | 0.968 | 0.747 | 0.000 | 0.507 | {'QB': 24} |

## Best Calibrated 2026 Board: 80/15/5 Anchor

### Top 50

| Rank | Player | Pos | Team | Current rank | Delta | DPI | Warnings |
|---:|---|---|---|---:|---:|---:|---|
| 1 | Josh Allen | QB | BUF | 4 | -3 | 100.0 | high_missingness |
| 2 | Christian McCaffrey | RB | SF | 3 | -1 | 99.6 |  |
| 3 | Jalen Hurts | QB | PHI | 34 | -31 | 99.2 | delta_over_20, high_missingness |
| 4 | Jonathan Taylor | RB | IND | 20 | -16 | 98.9 | high_missingness |
| 5 | Patrick Mahomes | QB | KC | 13 | -8 | 98.5 | high_missingness |
| 6 | Bijan Robinson | RB | ATL | 10 | -4 | 98.1 | high_missingness |
| 7 | Jahmyr Gibbs | RB | DET | 16 | -9 | 97.7 | high_missingness |
| 8 | Puka Nacua | WR | LAR | 2 | 6 | 97.3 | high_missingness |
| 9 | Ja'Marr Chase | WR | CIN | 7 | 2 | 96.9 | high_missingness |
| 10 | Amon-Ra St. Brown | WR | DET | 5 | 5 | 96.6 | high_missingness |
| 11 | De'Von Achane | RB | MIA | 23 | -12 | 96.2 | high_missingness |
| 12 | Trey McBride | TE | ARI | 6 | 6 | 95.8 | high_missingness |
| 13 | Jaxon Smith-Njigba | WR | SEA | 1 | 12 | 95.4 | high_missingness |
| 14 | Kyren Williams | RB | LAR | 30 | -16 | 95.0 | high_missingness |
| 15 | A.J. Brown | WR | NE | 14 | 1 | 94.6 |  |
| 16 | Justin Jefferson | WR | MIN | 17 | -1 | 94.3 | high_missingness |
| 17 | Chris Olave | WR | NO | 12 | 5 | 93.9 | high_missingness |
| 18 | Daniel Jones | QB | IND | 43 | -25 | 93.5 | delta_over_20, high_missingness |
| 19 | Drake London | WR | ATL | 8 | 11 | 93.1 | high_missingness |
| 20 | Saquon Barkley | RB | PHI | 49 | -29 | 92.7 | delta_over_20 |
| 21 | George Kittle | TE | SF | 19 | 2 | 92.4 |  |
| 22 | Dak Prescott | QB | DAL | 28 | -6 | 92.0 | high_missingness |
| 23 | Rashee Rice | WR | KC | 15 | 8 | 91.6 | high_missingness |
| 24 | Brock Purdy | QB | SF | 31 | -7 | 91.2 | high_missingness |
| 25 | Drake Maye | QB | NE | 9 | 16 | 90.8 | high_missingness, missing_feature_row |
| 26 | James Cook | RB | BUF | 36 | -10 | 90.4 | high_missingness |
| 27 | Garrett Wilson | WR | NYJ | 18 | 9 | 90.1 | high_missingness |
| 28 | Matthew Stafford | QB | LAR | 22 | 6 | 89.7 | high_missingness |
| 29 | Trevor Lawrence | QB | JAX | 39 | -10 | 89.3 | high_missingness |
| 30 | Sam LaPorta | TE | DET | 26 | 4 | 88.9 | high_missingness |
| 31 | Brock Bowers | TE | LV | 11 | 20 | 88.5 | high_missingness, missing_feature_row |
| 32 | George Pickens | WR | DAL | 21 | 11 | 88.2 | high_missingness |
| 33 | Davante Adams | WR | LAR | 27 | 6 | 87.8 |  |
| 34 | CeeDee Lamb | WR | DAL | 29 | 5 | 87.4 | high_missingness |
| 35 | Javonte Williams | RB | DAL | 45 | -10 | 87.0 | high_missingness |
| 36 | Zay Flowers | WR | BAL | 24 | 12 | 86.6 | high_missingness |
| 37 | Jordan Love | QB | GB | 25 | 12 | 86.2 | high_missingness |
| 38 | Josh Jacobs | RB | GB | 64 | -26 | 85.9 | delta_over_20 |
| 39 | Lamar Jackson | QB | BAL | 76 | -37 | 85.5 | delta_over_20, high_missingness |
| 40 | Nico Collins | WR | HOU | 32 | 8 | 85.1 | high_missingness |
| 41 | Tucker Kraft | TE | GB | 33 | 8 | 84.7 | high_missingness |
| 42 | Kyle Pitts | TE | ATL | 38 | 4 | 84.3 | high_missingness |
| 43 | Chase Brown | RB | CIN | 41 | 2 | 83.9 | high_missingness |
| 44 | Travis Etienne | RB | NO | 68 | -24 | 83.6 | delta_over_20, high_missingness |
| 45 | Dallas Goedert | TE | PHI | 42 | 3 | 83.2 |  |
| 46 | Travis Kelce | TE | KC | 52 | -6 | 82.8 |  |
| 47 | Breece Hall | RB | NYJ | 74 | -27 | 82.4 | delta_over_20, high_missingness |
| 48 | Wan'Dale Robinson | WR | TEN | 37 | 11 | 82.0 | high_missingness |
| 49 | Justin Herbert | QB | LAC | 72 | -23 | 81.7 | delta_over_20, high_missingness |
| 50 | C.J. Stroud | QB | HOU | 66 | -16 | 81.3 | high_missingness |

### Position Boards

#### QB45

| Pos rank | Overall | Player | Current overall | Delta |
|---:|---:|---|---:|---:|
| 1 | 1 | Josh Allen | 4 | -3 |
| 2 | 3 | Jalen Hurts | 34 | -31 |
| 3 | 5 | Patrick Mahomes | 13 | -8 |
| 4 | 18 | Daniel Jones | 43 | -25 |
| 5 | 22 | Dak Prescott | 28 | -6 |
| 6 | 24 | Brock Purdy | 31 | -7 |
| 7 | 25 | Drake Maye | 9 | 16 |
| 8 | 28 | Matthew Stafford | 22 | 6 |
| 9 | 29 | Trevor Lawrence | 39 | -10 |
| 10 | 37 | Jordan Love | 25 | 12 |
| 11 | 39 | Lamar Jackson | 76 | -37 |
| 12 | 49 | Justin Herbert | 72 | -23 |
| 13 | 50 | C.J. Stroud | 66 | -16 |
| 14 | 56 | Jared Goff | 61 | -5 |
| 15 | 61 | Bo Nix | 47 | 14 |
| 16 | 65 | Kyler Murray | 100 | -35 |
| 17 | 66 | Caleb Williams | 51 | 15 |
| 18 | 68 | Joe Burrow | 88 | -20 |
| 19 | 73 | Baker Mayfield | 84 | -11 |
| 20 | 81 | Sam Darnold | 93 | -12 |
| 21 | 97 | Jayden Daniels | 81 | 16 |
| 22 | 102 | Jacoby Brissett | 107 | -5 |
| 23 | 108 | Jaxson Dart | 97 | 11 |
| 24 | 112 | Aaron Rodgers | 114 | -2 |
| 25 | 115 | Tua Tagovailoa | 131 | -16 |
| 26 | 118 | Malik Willis | 118 | 0 |
| 27 | 124 | Bryce Young | 136 | -12 |
| 28 | 131 | Tyler Shough | 124 | 7 |
| 29 | 152 | Shedeur Sanders | 145 | 7 |
| 30 | 160 | Geno Smith | 171 | -11 |
| 31 | 165 | Cam Ward | 154 | 11 |
| 32 | 192 | Tyler Huntley | 222 | -30 |
| 33 | 199 | Fernando Mendoza | 195 | 4 |
| 34 | 202 | Mac Jones | 209 | -7 |
| 35 | 207 | Carson Wentz | 225 | -18 |
| 36 | 210 | Justin Fields | 240 | -30 |
| 37 | 211 | Jameis Winston | 215 | -4 |
| 38 | 221 | Marcus Mariota | 235 | -14 |
| 39 | 244 | Davis Mills | 245 | -1 |
| 40 | 246 | Spencer Rattler | 243 | 3 |
| 41 | 251 | J.J. McCarthy | 249 | 2 |
| 42 | 252 | Jake Browning | 259 | -7 |
| 43 | 255 | Quinn Ewers | 253 | 2 |
| 44 | 257 | Josh Johnson | 256 | 1 |
| 45 | 260 | Joe Flacco | 260 | 0 |

#### RB80

| Pos rank | Overall | Player | Current overall | Delta |
|---:|---:|---|---:|---:|
| 1 | 2 | Christian McCaffrey | 3 | -1 |
| 2 | 4 | Jonathan Taylor | 20 | -16 |
| 3 | 6 | Bijan Robinson | 10 | -4 |
| 4 | 7 | Jahmyr Gibbs | 16 | -9 |
| 5 | 11 | De'Von Achane | 23 | -12 |
| 6 | 14 | Kyren Williams | 30 | -16 |
| 7 | 20 | Saquon Barkley | 49 | -29 |
| 8 | 26 | James Cook | 36 | -10 |
| 9 | 35 | Javonte Williams | 45 | -10 |
| 10 | 38 | Josh Jacobs | 64 | -26 |
| 11 | 43 | Chase Brown | 41 | 2 |
| 12 | 44 | Travis Etienne | 68 | -24 |
| 13 | 47 | Breece Hall | 74 | -27 |
| 14 | 53 | D'Andre Swift | 69 | -16 |
| 15 | 58 | Derrick Henry | 91 | -33 |
| 16 | 71 | Omarion Hampton | 55 | 16 |
| 17 | 75 | Jaylen Warren | 87 | -12 |
| 18 | 77 | Ashton Jeanty | 58 | 19 |
| 19 | 80 | Kenneth Walker III | 109 | -29 |
| 20 | 82 | Aaron Jones | 112 | -30 |
| 21 | 83 | Rhamondre Stevenson | 104 | -21 |
| 22 | 84 | J.K. Dobbins | 102 | -18 |
| 23 | 93 | Tony Pollard | 117 | -24 |
| 24 | 95 | Bucky Irving | 78 | 17 |
| 25 | 98 | James Conner | 125 | -27 |
| 26 | 99 | Cam Skattebo | 82 | 17 |
| 27 | 100 | Rico Dowdle | 99 | 1 |
| 28 | 106 | Alvin Kamara | 140 | -34 |
| 29 | 107 | Quinshon Judkins | 96 | 11 |
| 30 | 120 | Zach Charbonnet | 129 | -9 |
| 31 | 127 | Kenneth Gainwell | 138 | -11 |
| 32 | 129 | TreVeyon Henderson | 121 | 8 |
| 33 | 134 | David Montgomery | 165 | -31 |
| 34 | 141 | Isiah Pacheco | 172 | -31 |
| 35 | 146 | Rachaad White | 169 | -23 |
| 36 | 153 | Tyrone Tracy Jr. | 146 | 7 |
| 37 | 157 | Woody Marks | 149 | 8 |
| 38 | 161 | Chuba Hubbard | 174 | -13 |
| 39 | 163 | RJ Harvey | 152 | 11 |
| 40 | 166 | Trey Benson | 157 | 9 |
| 41 | 168 | Kimani Vidal | 160 | 8 |
| 42 | 169 | Tyjae Spears | 177 | -8 |
| 43 | 171 | Kyle Monangai | 163 | 8 |
| 44 | 175 | Michael Carter | 179 | -4 |
| 45 | 177 | Tyler Allgeier | 191 | -14 |
| 46 | 180 | Jordan Mason | 184 | -4 |
| 47 | 183 | Chris Rodriguez Jr. | 188 | -5 |
| 48 | 185 | Jacory Croskey-Merritt | 181 | 4 |
| 49 | 187 | Devin Singletary | 199 | -12 |
| 50 | 190 | Jawhar Jordan | 186 | 4 |
| 51 | 196 | Blake Corum | 193 | 3 |
| 52 | 198 | Emanuel Wilson | 203 | -5 |
| 53 | 201 | Raheim Sanders | 197 | 4 |
| 54 | 203 | Samaje Perine | 206 | -3 |
| 55 | 206 | Devin Neal | 201 | 5 |
| 56 | 213 | Ty Johnson | 217 | -4 |
| 57 | 214 | Jaylen Wright | 208 | 6 |
| 58 | 219 | Phil Mafah | 212 | 7 |
| 59 | 220 | Dylan Sampson | 214 | 6 |
| 60 | 222 | Justice Hill | 226 | -4 |
| 61 | 225 | Bhayshul Tuten | 219 | 6 |
| 62 | 227 | Jaret Patterson | 229 | -2 |
| 63 | 229 | Kendre Miller | 231 | -2 |
| 64 | 232 | Keaton Mitchell | 238 | -6 |
| 65 | 233 | Brian Robinson | 244 | -11 |
| 66 | 235 | Jeremy McNichols | 233 | 2 |
| 67 | 239 | Emari Demercado | 239 | 0 |
| 68 | 241 | Braelon Allen | 237 | 4 |
| 69 | 242 | Jerome Ford | 248 | -6 |
| 70 | 243 | Jaydon Blue | 241 | 2 |
| 71 | 245 | Isaiah Davis | 242 | 3 |
| 72 | 247 | Sean Tucker | 246 | 1 |
| 73 | 248 | Malik Davis | 250 | -2 |
| 74 | 249 | Brashard Smith | 247 | 2 |
| 75 | 250 | Tank Bigsby | 251 | -1 |
| 76 | 253 | Jaleel McLaughlin | 258 | -5 |
| 77 | 254 | DJ Giddens | 252 | 2 |
| 78 | 256 | Ray Davis | 254 | 2 |
| 79 | 258 | Zavier Scott | 255 | 3 |
| 80 | 259 | Terrell Jennings | 257 | 2 |

#### WR100

| Pos rank | Overall | Player | Current overall | Delta |
|---:|---:|---|---:|---:|
| 1 | 8 | Puka Nacua | 2 | 6 |
| 2 | 9 | Ja'Marr Chase | 7 | 2 |
| 3 | 10 | Amon-Ra St. Brown | 5 | 5 |
| 4 | 13 | Jaxon Smith-Njigba | 1 | 12 |
| 5 | 15 | A.J. Brown | 14 | 1 |
| 6 | 16 | Justin Jefferson | 17 | -1 |
| 7 | 17 | Chris Olave | 12 | 5 |
| 8 | 19 | Drake London | 8 | 11 |
| 9 | 23 | Rashee Rice | 15 | 8 |
| 10 | 27 | Garrett Wilson | 18 | 9 |
| 11 | 32 | George Pickens | 21 | 11 |
| 12 | 33 | Davante Adams | 27 | 6 |
| 13 | 34 | CeeDee Lamb | 29 | 5 |
| 14 | 36 | Zay Flowers | 24 | 12 |
| 15 | 40 | Nico Collins | 32 | 8 |
| 16 | 48 | Wan'Dale Robinson | 37 | 11 |
| 17 | 51 | Tetairoa McMillan | 35 | 16 |
| 18 | 52 | DeVonta Smith | 46 | 6 |
| 19 | 54 | Terry McLaurin | 50 | 4 |
| 20 | 55 | Jaylen Waddle | 53 | 2 |
| 21 | 57 | Malik Nabers | 40 | 17 |
| 22 | 59 | Rome Odunze | 44 | 15 |
| 23 | 60 | Tee Higgins | 56 | 4 |
| 24 | 63 | Courtland Sutton | 57 | 6 |
| 25 | 67 | Alec Pierce | 54 | 13 |
| 26 | 69 | Mike Evans | 70 | -1 |
| 27 | 72 | Jakobi Meyers | 65 | 7 |
| 28 | 76 | Jameson Williams | 63 | 13 |
| 29 | 78 | Emeka Egbuka | 60 | 18 |
| 30 | 85 | Michael Wilson | 77 | 8 |
| 31 | 86 | Quentin Johnston | 73 | 13 |
| 32 | 87 | Christian Watson | 79 | 8 |
| 33 | 88 | Jordan Addison | 83 | 5 |
| 34 | 92 | DK Metcalf | 86 | 6 |
| 35 | 101 | Romeo Doubs | 92 | 9 |
| 36 | 103 | Ladd McConkey | 89 | 14 |
| 37 | 104 | Jauan Jennings | 95 | 9 |
| 38 | 105 | Tre Tucker | 98 | 7 |
| 39 | 109 | Parker Washington | 101 | 8 |
| 40 | 110 | Jerry Jeudy | 108 | 2 |
| 41 | 114 | Ricky Pearsall | 103 | 11 |
| 42 | 116 | Calvin Ridley | 116 | 0 |
| 43 | 117 | Troy Franklin | 105 | 12 |
| 44 | 119 | Darius Slayton | 113 | 6 |
| 45 | 121 | Elic Ayomanor | 111 | 10 |
| 46 | 123 | Khalil Shakir | 120 | 3 |
| 47 | 125 | Darnell Mooney | 122 | 3 |
| 48 | 133 | Keon Coleman | 126 | 7 |
| 49 | 136 | Michael Pittman | 139 | -3 |
| 50 | 137 | Brian Thomas Jr. | 128 | 9 |
| 51 | 139 | Xavier Worthy | 132 | 7 |
| 52 | 142 | Mack Hollins | 135 | 7 |
| 53 | 143 | Travis Hunter | 134 | 9 |
| 54 | 148 | Jayden Reed | 147 | 1 |
| 55 | 149 | Jakobie Keeney-James | 142 | 7 |
| 56 | 150 | Kayshon Boutte | 144 | 6 |
| 57 | 151 | Cooper Kupp | 158 | -7 |
| 58 | 154 | Josh Downs | 153 | 1 |
| 59 | 156 | Chris Godwin Jr. | 161 | -5 |
| 60 | 158 | Rashid Shaheed | 156 | 2 |
| 61 | 159 | Jalen Coker | 150 | 9 |
| 62 | 170 | Marquise Brown | 168 | 2 |
| 63 | 172 | Jalen McMillan | 164 | 8 |
| 64 | 173 | Devaughn Vele | 166 | 7 |
| 65 | 174 | Van Jefferson | 170 | 4 |
| 66 | 176 | DJ Moore | 176 | 0 |
| 67 | 178 | Xavier Legette | 173 | 5 |
| 68 | 179 | Jayden Higgins | 175 | 4 |
| 69 | 181 | Adonai Mitchell | 178 | 3 |
| 70 | 182 | Theo Wease Jr. | 180 | 2 |
| 71 | 184 | Tyquan Thornton | 182 | 2 |
| 72 | 186 | Andrei Iosivas | 183 | 3 |
| 73 | 188 | Olamide Zaccheaus | 185 | 3 |
| 74 | 189 | Kendrick Bourne | 189 | 0 |
| 75 | 191 | Chimere Dike | 187 | 4 |
| 76 | 193 | Malik Washington | 190 | 3 |
| 77 | 194 | Ryan Flournoy | 192 | 2 |
| 78 | 195 | Calvin Austin III | 194 | 1 |
| 79 | 197 | Dontayvion Wicks | 198 | -1 |
| 80 | 200 | Pat Bryant | 196 | 4 |
| 81 | 204 | Rashod Bateman | 202 | 2 |
| 82 | 205 | Xavier Hutchinson | 200 | 5 |
| 83 | 208 | Matthew Golden | 204 | 4 |
| 84 | 209 | Jalen Nailor | 205 | 4 |
| 85 | 212 | Tory Horton | 207 | 5 |
| 86 | 215 | Christian Kirk | 216 | -1 |
| 87 | 216 | Tez Johnson | 210 | 6 |
| 88 | 217 | DeMario Douglas | 213 | 4 |
| 89 | 218 | Luther Burden III | 211 | 7 |
| 90 | 223 | Treylon Burks | 220 | 3 |
| 91 | 224 | Isaiah Bond | 218 | 6 |
| 92 | 226 | Tre Harris | 221 | 5 |
| 93 | 228 | Isaac TeSlaa | 223 | 5 |
| 94 | 230 | Marquez Valdes-Scantling | 227 | 3 |
| 95 | 231 | Casey Washington | 224 | 7 |
| 96 | 234 | Cedric Tillman | 228 | 6 |
| 97 | 236 | Jalen Tolbert | 230 | 6 |
| 98 | 237 | Devontez Walker | 232 | 5 |
| 99 | 238 | Lil'Jordan Humphrey | 234 | 4 |
| 100 | 240 | John Metchie III | 236 | 4 |

#### TE35

| Pos rank | Overall | Player | Current overall | Delta |
|---:|---:|---|---:|---:|
| 1 | 12 | Trey McBride | 6 | 6 |
| 2 | 21 | George Kittle | 19 | 2 |
| 3 | 30 | Sam LaPorta | 26 | 4 |
| 4 | 31 | Brock Bowers | 11 | 20 |
| 5 | 41 | Tucker Kraft | 33 | 8 |
| 6 | 42 | Kyle Pitts | 38 | 4 |
| 7 | 45 | Dallas Goedert | 42 | 3 |
| 8 | 46 | Travis Kelce | 52 | -6 |
| 9 | 62 | Tyler Warren | 48 | 14 |
| 10 | 64 | Hunter Henry | 59 | 5 |
| 11 | 70 | Dalton Schultz | 62 | 8 |
| 12 | 74 | Juwan Johnson | 67 | 7 |
| 13 | 79 | Jake Ferguson | 75 | 4 |
| 14 | 89 | Dalton Kincaid | 85 | 4 |
| 15 | 90 | Colston Loveland | 71 | 19 |
| 16 | 91 | Mark Andrews | 90 | 1 |
| 17 | 94 | T.J. Hockenson | 94 | 0 |
| 18 | 96 | Harold Fannin Jr. | 80 | 16 |
| 19 | 111 | Cade Otton | 110 | 1 |
| 20 | 113 | Brenton Strange | 106 | 7 |
| 21 | 122 | Theo Johnson | 115 | 7 |
| 22 | 126 | David Njoku | 133 | -7 |
| 23 | 128 | Mason Taylor | 119 | 9 |
| 24 | 130 | Oronde Gadsden II | 123 | 7 |
| 25 | 132 | Greg Dulcich | 130 | 2 |
| 26 | 135 | AJ Barner | 127 | 8 |
| 27 | 138 | Pat Freiermuth | 141 | -3 |
| 28 | 140 | Colby Parkinson | 137 | 3 |
| 29 | 144 | Cole Kmet | 148 | -4 |
| 30 | 145 | Evan Engram | 151 | -6 |
| 31 | 147 | Dawson Knox | 143 | 4 |
| 32 | 155 | Michael Mayer | 155 | 0 |
| 33 | 162 | Isaiah Likely | 159 | 3 |
| 34 | 164 | Chig Okonkwo | 162 | 2 |
| 35 | 167 | Mike Gesicki | 167 | 0 |

## Decision Read

The 80/15/5 anchor is safer than the Phase 33.11 original and preserves a modest BQML/VOR signal, but it still does not justify champion activation. Current Pigskin should hold for Standard while the owner reviews the calibrated board.
