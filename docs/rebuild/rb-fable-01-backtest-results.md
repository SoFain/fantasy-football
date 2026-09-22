# RB Fable 01 Backtest Results

RB Fable 01 is evaluated on prior-season metrics against next-season Standard PPG. The 2022-2025 same-season boards below are descriptive only.

## Forward Predictive Summary

| Fold | Rows | Top 6 | Top 12 | Top 24 | Top 36 | Points captured | NDCG@24 | Pairwise | Band regret | Score corr | Rank corr | Elite misses |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 to 2023 | 66 | 0.167 | 0.500 | 0.708 | 0.778 | 0.836 | 0.799 | 0.732 | 0.394 | 0.642 | 0.640 | 2 |
| 2023 to 2024 | 73 | 0.333 | 0.667 | 0.750 | 0.806 | 0.888 | 0.872 | 0.795 | 0.288 | 0.739 | 0.766 | 2 |
| 2024 to 2025 | 65 | 0.500 | 0.667 | 0.750 | 0.861 | 0.895 | 0.870 | 0.780 | 0.277 | 0.775 | 0.768 | 2 |

## Predictive Top 25 Boards

### 2022 to 2023

| Rank | Player | Team | Score | Actual finish | Labels | Actual points | Touches | Rush | Rec | Yards | TD | YAC/rush | EPA/touch | Success | Explosive | 1st down | TFL | Box YPC | Avail | Age penalty | Reason |
|---:|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Austin Ekeler | LAC | 1.421 | 28 | T36 | 134.4 | 311 | 204 | 107 | 1637 | 18 | 2.907 | -0.008 | 41.7 | 6.4 | 22.6 | 9.8 | 4.040 | 1.000 | -2 | opportunity led (+1.077) |
| 2 | Josh Jacobs | LV | 1.277 | 19 | T24/T36 | 144.1 | 393 | 340 | 53 | 2053 | 12 | 3.371 | -0.002 | 44.4 | 9.1 | 27.6 | 7.7 | 3.840 | 1.000 | 0 | opportunity led (+0.959) |
| 3 | Derrick Henry | TEN | 1.249 | 10 | T12/T24/T36 | 218.7 | 382 | 349 | 33 | 1936 | 13 | 3.527 | -0.058 | 38.4 | 7.7 | 19.2 | 9.7 | 4.130 | 0.941 | -3 | opportunity led (+0.983) |
| 4 | Saquon Barkley | NYG | 1.183 | 9 | T12/T24/T36 | 182.2 | 352 | 295 | 57 | 1650 | 10 | 2.895 | -0.044 | 35.9 | 9.2 | 21.4 | 10.5 | 4.260 | 0.941 | 0 | opportunity led (+1.010) |
| 5 | Christian McCaffrey | SF | 1.180 | 1 | T6/T12/T24/T36 | 324.3 | 329 | 244 | 85 | 1880 | 13 | 2.762 | 0.012 | 40.2 | 9.0 | 24.2 | 8.6 | 3.830 | 1.059 | -1 | opportunity led (+0.959) |
| 6 | Joe Mixon | CIN | 1.085 | 12 | T12/T24/T36 | 215.0 | 270 | 210 | 60 | 1255 | 9 | 2.614 | -0.043 | 40.5 | 5.2 | 22.4 | 7.1 | 2.990 | 0.824 | -1 | opportunity led (+0.918) |
| 7 | Jonathan Taylor | IND | 0.929 | 5 | T6/T12/T24/T36 | 137.4 | 220 | 192 | 28 | 1004 | 4 | 2.839 | -0.130 | 38.5 | 8.3 | 21.9 | 7.8 | 2.680 | 0.647 | 0 | opportunity led (+0.839) |
| 8 | Kenneth Walker | SEA | 0.891 | 17 | T24/T36 | 170.4 | 255 | 228 | 27 | 1215 | 9 | 2.952 | -0.058 | 33.3 | 10.5 | 22.4 | 14.5 | 4.300 | 0.882 | 0 | opportunity led (+0.653) |
| 9 | Rhamondre Stevenson | NE | 0.888 | 30 | T36 | 107.7 | 279 | 210 | 69 | 1461 | 6 | 3.595 | -0.034 | 40.5 | 10.5 | 23.8 | 8.6 | 3.520 | 1.000 | 0 | opportunity led (+0.677) |
| 10 | Najee Harris | PIT | 0.838 | 27 | T36 | 166.5 | 313 | 272 | 41 | 1263 | 10 | 2.728 | -0.092 | 40.4 | 5.2 | 16.5 | 8.1 | 3.700 | 1.000 | 0 | opportunity led (+0.685) |
| 11 | Alvin Kamara | NO | 0.832 | 14 | T24/T36 | 158.0 | 280 | 223 | 57 | 1387 | 4 | 2.830 | -0.147 | 37.2 | 6.7 | 17.9 | 7.2 | 3.120 | 0.882 | -2 | opportunity led (+0.841) |
| 12 | Miles Sanders | PHI | 0.815 | 65 | - | 60.6 | 279 | 259 | 20 | 1347 | 11 | 2.988 | 0.049 | 49.0 | 9.7 | 23.9 | 8.5 | 3.260 | 1.000 | 0 | opportunity led (+0.492) |
| 13 | Aaron Jones | GB | 0.812 | 29 | T36 | 104.9 | 272 | 213 | 59 | 1516 | 7 | 3.155 | 0.044 | 46.5 | 9.4 | 25.8 | 10.8 | 5.230 | 1.000 | -2 | opportunity led (+0.616) |
| 14 | Dameon Pierce | HST | 0.801 | 47 | - | 69.7 | 250 | 220 | 30 | 1104 | 5 | 3.041 | -0.112 | 37.7 | 6.4 | 24.6 | 12.3 | 3.540 | 0.765 | 0 | opportunity led (+0.701) |
| 15 | Jamaal Williams | DET | 0.782 | 68 | - | 42.8 | 274 | 262 | 12 | 1139 | 17 | 2.893 | -0.095 | 42.8 | 6.9 | 25.2 | 7.6 | 3.390 | 1.000 | -2 | opportunity led (+0.488) |
| 16 | Dalvin Cook | MIN | 0.778 | 86 | - | 25.2 | 303 | 264 | 39 | 1468 | 10 | 3.114 | -0.160 | 34.1 | 7.2 | 18.9 | 12.5 | 3.850 | 1.000 | -2 | opportunity led (+0.647) |
| 17 | Breece Hall | NYJ | 0.773 | 13 | T24/T36 | 214.5 | 99 | 80 | 19 | 681 | 5 | 3.875 | 0.140 | 41.2 | 15.0 | 25.0 | 11.2 | 2.360 | 0.412 | 0 | opportunity led (+0.524) |
| 18 | James Conner | ARZ | 0.708 | 7 | T12/T24/T36 | 174.5 | 229 | 183 | 46 | 1082 | 8 | 2.721 | -0.011 | 42.6 | 5.5 | 26.2 | 6.6 | 3.900 | 0.765 | -2 | opportunity led (+0.613) |
| 19 | Tony Pollard | DAL | 0.678 | 25 | T36 | 167.6 | 232 | 193 | 39 | 1378 | 12 | 3.731 | 0.019 | 40.4 | 11.9 | 23.8 | 9.8 | 4.680 | 0.941 | 0 | opportunity led (+0.388) |
| 20 | Travis Etienne | JAX | 0.676 | 8 | T12/T24/T36 | 224.4 | 255 | 220 | 35 | 1441 | 5 | 3.214 | -0.038 | 40.5 | 9.6 | 24.6 | 13.2 | 4.050 | 1.000 | 0 | opportunity led (+0.469) |
| 21 | Ezekiel Elliott | DAL | 0.633 | 38 | - | 123.5 | 248 | 231 | 17 | 968 | 12 | 2.619 | -0.047 | 42.0 | 5.2 | 22.5 | 6.9 | 3.390 | 0.882 | -2 | opportunity led (+0.473) |
| 22 | David Montgomery | CHI | 0.603 | 6 | T6/T12/T24/T36 | 191.2 | 235 | 201 | 34 | 1117 | 6 | 2.965 | -0.065 | 36.3 | 5.5 | 20.9 | 6.5 | 3.090 | 0.941 | 0 | opportunity led (+0.496) |
| 23 | Devin Singletary | BUF | 0.570 | 35 | T36 | 137.3 | 215 | 177 | 38 | 1099 | 6 | 2.983 | -0.078 | 41.8 | 9.6 | 24.3 | 10.7 | 3.890 | 0.941 | 0 | opportunity led (+0.406) |
| 24 | D'Andre Swift | DET | 0.561 | 24 | T24/T36 | 160.3 | 147 | 99 | 48 | 931 | 8 | 3.384 | 0.038 | 40.4 | 9.1 | 21.2 | 12.1 | 1.197 | 0.824 | 0 | opportunity led (+0.369) |
| 25 | Tyler Allgeier | ATL | 0.554 | 39 | - | 119.6 | 226 | 210 | 16 | 1174 | 4 | 3.529 | 0.046 | 42.9 | 9.1 | 25.2 | 6.7 | 5.050 | 0.941 | 0 | opportunity led (+0.307) |

### 2023 to 2024

| Rank | Player | Team | Score | Actual finish | Labels | Actual points | Touches | Rush | Rec | Yards | TD | YAC/rush | EPA/touch | Success | Explosive | 1st down | TFL | Box YPC | Avail | Age penalty | Reason |
|---:|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Kyren Williams | LA | 1.547 | 7 | T12/T24/T36 | 238.1 | 260 | 228 | 32 | 1350 | 15 | 3.110 | 0.086 | 47.4 | 6.1 | 27.6 | 6.6 | 3.270 | 0.706 | 0 | opportunity led (+1.109) |
| 2 | Alvin Kamara | NO | 1.137 | 10 | T12/T24/T36 | 197.3 | 255 | 180 | 75 | 1160 | 6 | 2.578 | -0.012 | 38.3 | 5.6 | 23.9 | 8.3 | 2.820 | 0.765 | -3 | opportunity led (+1.042) |
| 3 | Saquon Barkley | NYG | 1.073 | 1 | T6/T12/T24/T36 | 322.3 | 288 | 247 | 41 | 1242 | 10 | 2.688 | -0.175 | 36.0 | 6.9 | 21.1 | 15.4 | 2.370 | 0.824 | -1 | opportunity led (+0.957) |
| 4 | Joe Mixon | CIN | 1.002 | 9 | T12/T24/T36 | 204.5 | 309 | 257 | 52 | 1410 | 12 | 2.486 | -0.058 | 39.7 | 7.8 | 23.0 | 8.6 | 2.640 | 1.000 | -2 | opportunity led (+0.799) |
| 5 | Tony Pollard | DAL | 0.991 | 24 | T24/T36 | 159.7 | 307 | 252 | 55 | 1316 | 6 | 2.877 | -0.058 | 40.5 | 6.3 | 22.2 | 11.1 | 2.530 | 1.000 | -1 | opportunity led (+0.792) |
| 6 | Josh Jacobs | LV | 0.957 | 6 | T6/T12/T24/T36 | 257.1 | 270 | 233 | 37 | 1101 | 6 | 2.584 | -0.164 | 34.8 | 2.6 | 14.6 | 11.2 | 2.270 | 0.765 | 0 | opportunity led (+0.915) |
| 7 | Isiah Pacheco | KC | 0.944 | 39 | - | 44.9 | 249 | 205 | 44 | 1179 | 9 | 3.088 | -0.015 | 40.0 | 7.3 | 25.9 | 6.3 | 5.090 | 0.824 | 0 | opportunity led (+0.701) |
| 8 | Jonathan Taylor | IND | 0.932 | 5 | T6/T12/T24/T36 | 226.7 | 188 | 169 | 19 | 894 | 8 | 3.077 | -0.054 | 39.0 | 7.7 | 24.9 | 8.3 | 2.750 | 0.588 | 0 | opportunity led (+0.720) |
| 9 | David Montgomery | DET | 0.887 | 11 | T12/T24/T36 | 185.7 | 235 | 219 | 16 | 1132 | 13 | 3.151 | 0.044 | 44.3 | 6.8 | 27.4 | 6.8 | 3.670 | 0.824 | -1 | opportunity led (+0.560) |
| 10 | Jahmyr Gibbs | DET | 0.860 | 3 | T6/T12/T24/T36 | 310.9 | 234 | 182 | 52 | 1261 | 11 | 3.302 | -0.022 | 37.4 | 12.1 | 23.6 | 9.3 | 3.810 | 0.882 | 0 | opportunity led (+0.597) |
| 11 | James Conner | ARZ | 0.859 | 14 | T24/T36 | 206.8 | 235 | 208 | 27 | 1205 | 9 | 3.389 | 0.059 | 42.3 | 9.1 | 27.4 | 10.1 | 4.250 | 0.765 | -3 | opportunity led (+0.618) |
| 12 | Rachaad White | TB | 0.840 | 27 | T36 | 148.6 | 336 | 272 | 64 | 1539 | 9 | 2.581 | -0.134 | 30.1 | 4.4 | 18.0 | 6.2 | 3.030 | 1.000 | 0 | opportunity led (+0.789) |
| 13 | Travis Etienne | JAX | 0.830 | 41 | - | 91.2 | 325 | 267 | 58 | 1484 | 12 | 2.730 | -0.107 | 34.8 | 5.2 | 19.9 | 11.2 | 3.800 | 1.000 | 0 | opportunity led (+0.706) |
| 14 | Breece Hall | NYJ | 0.826 | 19 | T24/T36 | 183.9 | 299 | 223 | 76 | 1585 | 9 | 3.377 | -0.073 | 34.1 | 6.7 | 17.9 | 13.9 | 5.400 | 1.000 | 0 | opportunity led (+0.678) |
| 15 | Aaron Jones | GB | 0.819 | 20 | T24/T36 | 190.6 | 172 | 142 | 30 | 889 | 3 | 2.923 | 0.014 | 47.2 | 6.3 | 23.9 | 7.8 | 4.170 | 0.647 | -3 | opportunity led (+0.698) |
| 16 | Raheem Mostert | MIA | 0.808 | 60 | - | 51.9 | 234 | 209 | 25 | 1187 | 21 | 3.148 | 0.073 | 45.9 | 10.5 | 28.2 | 10.5 | 4.490 | 0.882 | -6 | opportunity led (+0.508) |
| 17 | Bijan Robinson | ATL | 0.740 | 4 | T6/T12/T24/T36 | 280.7 | 272 | 214 | 58 | 1463 | 8 | 3.112 | -0.098 | 34.6 | 9.8 | 24.3 | 9.8 | 4.150 | 1.000 | 0 | opportunity led (+0.613) |
| 18 | D'Andre Swift | PHI | 0.740 | 22 | T24/T36 | 172.5 | 268 | 229 | 39 | 1263 | 6 | 2.751 | 0.007 | 43.7 | 7.4 | 21.8 | 10.0 | 4.160 | 0.941 | 0 | opportunity led (+0.569) |
| 19 | Devon Achane | MIA | 0.730 | 13 | T24/T36 | 221.9 | 130 | 103 | 27 | 997 | 11 | 4.621 | 0.256 | 55.3 | 15.5 | 29.1 | 9.7 | 6.350 | 0.647 | 0 | opportunity led (+0.286) |
| 20 | Javonte Williams | DEN | 0.713 | 40 | - | 105.9 | 264 | 217 | 47 | 1002 | 5 | 2.641 | -0.144 | 34.6 | 6.5 | 19.4 | 11.5 | 2.710 | 0.941 | 0 | opportunity led (+0.641) |
| 21 | Najee Harris | PIT | 0.679 | 26 | T36 | 168.6 | 284 | 255 | 29 | 1205 | 8 | 2.922 | -0.088 | 39.2 | 6.7 | 19.6 | 11.4 | 3.150 | 1.000 | 0 | opportunity led (+0.517) |
| 22 | Zack Moss | IND | 0.662 | 34 | T36 | 58.9 | 210 | 183 | 27 | 986 | 7 | 2.852 | -0.067 | 40.4 | 8.2 | 23.5 | 7.7 | 3.600 | 0.824 | 0 | opportunity led (+0.484) |
| 23 | Kenneth Walker | SEA | 0.659 | 17 | T24/T36 | 135.2 | 248 | 219 | 29 | 1164 | 9 | 2.735 | -0.038 | 38.4 | 8.7 | 21.0 | 11.0 | 3.560 | 0.882 | 0 | opportunity led (+0.489) |
| 24 | Derrick Henry | TEN | 0.654 | 2 | T6/T12/T24/T36 | 317.4 | 308 | 280 | 28 | 1381 | 12 | 3.111 | -0.007 | 37.5 | 6.8 | 22.5 | 9.6 | 3.760 | 1.000 | -4 | opportunity led (+0.503) |
| 25 | James Cook | BUF | 0.623 | 8 | T12/T24/T36 | 234.7 | 281 | 237 | 44 | 1567 | 6 | 2.671 | -0.026 | 42.2 | 9.3 | 22.8 | 9.3 | 4.400 | 1.000 | 0 | opportunity led (+0.480) |

### 2024 to 2025

| Rank | Player | Team | Score | Actual finish | Labels | Actual points | Touches | Rush | Rec | Yards | TD | YAC/rush | EPA/touch | Success | Explosive | 1st down | TFL | Box YPC | Avail | Age penalty | Reason |
|---:|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Saquon Barkley | PHI | 1.453 | 15 | T24/T36 | 195.3 | 378 | 345 | 33 | 2283 | 15 | 3.183 | 0.090 | 44.1 | 8.7 | 23.8 | 9.6 | 3.980 | 0.941 | -2 | opportunity led (+1.091) |
| 2 | Bijan Robinson | ATL | 1.356 | 3 | T6/T12/T24/T36 | 295.8 | 365 | 304 | 61 | 1887 | 15 | 3.010 | 0.046 | 49.3 | 9.2 | 27.3 | 7.2 | 3.690 | 1.000 | 0 | opportunity led (+0.996) |
| 3 | Kyren Williams | LA | 1.266 | 9 | T12/T24/T36 | 231.3 | 350 | 316 | 34 | 1481 | 16 | 2.633 | -0.067 | 44.0 | 5.7 | 26.9 | 8.9 | 3.360 | 0.941 | 0 | opportunity led (+0.970) |
| 4 | Jahmyr Gibbs | DET | 1.198 | 4 | T6/T12/T24/T36 | 291.9 | 302 | 250 | 52 | 1929 | 20 | 3.136 | 0.116 | 44.4 | 13.6 | 28.0 | 7.6 | 5.000 | 1.000 | 0 | opportunity led (+0.766) |
| 5 | Jonathan Taylor | IND | 1.186 | 1 | T6/T12/T24/T36 | 316.3 | 321 | 303 | 18 | 1567 | 12 | 2.677 | -0.065 | 36.0 | 8.9 | 23.8 | 9.2 | 3.760 | 0.824 | 0 | opportunity led (+0.965) |
| 6 | Alvin Kamara | NO | 1.143 | 42 | - | 71.7 | 296 | 228 | 68 | 1493 | 8 | 2.697 | -0.061 | 39.9 | 7.9 | 22.8 | 12.7 | 3.690 | 0.824 | -4 | opportunity led (+1.074) |
| 7 | Chuba Hubbard | CAR | 1.104 | 43 | - | 97.4 | 293 | 250 | 43 | 1366 | 11 | 3.272 | 0.033 | 44.4 | 9.6 | 24.8 | 6.0 | 4.590 | 0.882 | 0 | opportunity led (+0.809) |
| 8 | Josh Jacobs | GB | 1.069 | 8 | T12/T24/T36 | 205.1 | 337 | 301 | 36 | 1671 | 16 | 3.276 | -0.054 | 39.2 | 7.6 | 24.9 | 9.3 | 3.710 | 1.000 | -1 | opportunity led (+0.792) |
| 9 | Derrick Henry | BLT | 1.062 | 7 | T12/T24/T36 | 270.5 | 344 | 325 | 19 | 2114 | 18 | 3.689 | 0.118 | 47.7 | 11.4 | 28.6 | 8.0 | 5.850 | 1.000 | -5 | opportunity led (+0.632) |
| 10 | Devon Achane | MIA | 0.930 | 6 | T6/T12/T24/T36 | 255.8 | 281 | 203 | 78 | 1499 | 12 | 2.941 | -0.040 | 41.9 | 9.4 | 18.7 | 17.2 | 3.580 | 1.000 | 0 | opportunity led (+0.719) |
| 11 | Chase Brown | CIN | 0.892 | 13 | T24/T36 | 211.6 | 283 | 229 | 54 | 1350 | 11 | 2.873 | -0.021 | 38.4 | 7.4 | 21.4 | 8.3 | 3.230 | 0.941 | 0 | opportunity led (+0.700) |
| 12 | Kenneth Walker | SEA | 0.857 | 28 | T36 | 160.9 | 199 | 153 | 46 | 872 | 8 | 3.059 | -0.061 | 41.2 | 5.2 | 18.3 | 13.1 | 2.820 | 0.647 | 0 | opportunity led (+0.743) |
| 13 | Aaron Jones | MIN | 0.839 | 35 | T36 | 92.7 | 306 | 255 | 51 | 1546 | 7 | 2.929 | -0.044 | 40.4 | 7.8 | 19.2 | 8.2 | 3.680 | 1.000 | -4 | opportunity led (+0.732) |
| 14 | David Montgomery | DET | 0.822 | 32 | T36 | 142.9 | 221 | 185 | 36 | 1116 | 12 | 2.930 | -0.036 | 48.1 | 6.5 | 27.0 | 7.0 | 3.330 | 0.824 | -2 | opportunity led (+0.596) |
| 15 | James Cook | BUF | 0.810 | 5 | T6/T12/T24/T36 | 275.2 | 239 | 207 | 32 | 1267 | 18 | 3.227 | 0.044 | 42.5 | 7.7 | 23.7 | 10.1 | 4.120 | 0.941 | 0 | opportunity led (+0.475) |
| 16 | J.K. Dobbins | LAC | 0.775 | 23 | T24/T36 | 104.9 | 227 | 195 | 32 | 1058 | 9 | 3.092 | 0.019 | 35.4 | 10.8 | 24.1 | 9.2 | 4.960 | 0.765 | 0 | opportunity led (+0.595) |
| 17 | Bucky Irving | TB | 0.747 | 19 | T24/T36 | 110.5 | 254 | 207 | 47 | 1514 | 8 | 3.874 | 0.082 | 44.9 | 9.7 | 25.1 | 7.2 | 5.400 | 1.000 | 0 | opportunity led (+0.448) |
| 18 | Kareem Hunt | KC | 0.680 | 36 | T36 | 129.4 | 223 | 200 | 23 | 904 | 7 | 2.270 | 0.010 | 44.0 | 4.0 | 21.0 | 5.5 | 3.230 | 0.765 | -4 | opportunity led (+0.613) |
| 19 | Rhamondre Stevenson | NE | 0.668 | 21 | T24/T36 | 148.8 | 240 | 207 | 33 | 969 | 8 | 3.000 | -0.158 | 35.3 | 7.7 | 19.8 | 9.7 | 3.440 | 0.882 | -1 | opportunity led (+0.562) |
| 20 | Tony Pollard | TEN | 0.660 | 29 | T36 | 158.8 | 301 | 260 | 41 | 1317 | 5 | 2.973 | -0.090 | 34.2 | 7.7 | 20.4 | 9.6 | 4.300 | 0.941 | -2 | opportunity led (+0.627) |
| 21 | Breece Hall | NYJ | 0.639 | 20 | T24/T36 | 175.7 | 266 | 209 | 57 | 1359 | 8 | 2.990 | -0.083 | 35.9 | 9.1 | 19.1 | 10.1 | 2.380 | 0.941 | 0 | opportunity led (+0.564) |
| 22 | Christian McCaffrey | SF | 0.579 | 2 | T6/T12/T24/T36 | 314.6 | 65 | 50 | 15 | 348 | 0 | 2.500 | -0.044 | 40.0 | 8.0 | 24.0 | 10.0 | -0.286 | 0.235 | -3 | opportunity led (+0.737) |
| 23 | Brian Robinson | WAS | 0.562 | 68 | - | 54.5 | 207 | 187 | 20 | 958 | 8 | 2.727 | -0.058 | 42.2 | 6.4 | 25.1 | 9.6 | 3.710 | 0.824 | 0 | opportunity led (+0.406) |
| 24 | Rico Dowdle | DAL | 0.524 | 22 | T24/T36 | 179.3 | 274 | 235 | 39 | 1328 | 5 | 3.123 | -0.038 | 44.3 | 8.1 | 22.6 | 8.1 | 4.370 | 0.941 | -1 | opportunity led (+0.422) |
| 25 | D'Andre Swift | CHI | 0.496 | 14 | T24/T36 | 198.6 | 295 | 253 | 42 | 1345 | 6 | 2.656 | -0.132 | 34.0 | 5.9 | 17.0 | 12.2 | 2.770 | 1.000 | 0 | opportunity led (+0.498) |

## Miss And Component Audit

### 2022 to 2023

- Failed predicted top-12: Miles Sanders (pred 12, cohort actual 47).
- Actual elite misses outside predicted top 24: Raheem Mostert (pred 34, cohort actual 2), Isiah Pacheco (pred 36, cohort actual 12).
- Largest efficiency lifts: Tony Pollard, Tyler Allgeier, Breece Hall, Josh Jacobs, Khalil Herbert.
- Strongest age/availability penalties: Latavius Murray, Cordarrelle Patterson, Raheem Mostert, Jerick McKinnon, Gus Edwards.
- Strongest receiving-usage support: Christian McCaffrey, Austin Ekeler, Alvin Kamara, Javonte Williams, Rhamondre Stevenson.
- Highest TFL-risk watch: Raheem Blackshear, Zamir White, Ty Johnson, Alexander Mattison, Boston Scott. TFL is diagnostic only and is not a Fable score component.

### 2023 to 2024

- Failed predicted top-12: None.
- Actual elite misses outside predicted top 24: James Cook (pred 25, cohort actual 8), Chuba Hubbard (pred 28, cohort actual 12).
- Largest efficiency lifts: Devon Achane, Raheem Mostert, James Conner, Jaylen Warren, Kyren Williams.
- Strongest age/availability penalties: Cordarrelle Patterson, Dare Ogunbowale, Raheem Mostert, Aaron Jones, D'Onta Foreman.
- Strongest receiving-usage support: Alvin Kamara, Bijan Robinson, Breece Hall, Saquon Barkley, Jaylen Warren.
- Highest TFL-risk watch: Chase Brown, Cam Akers, DeeJay Dallas, Jerome Ford, Saquon Barkley. TFL is diagnostic only and is not a Fable score component.

### 2024 to 2025

- Failed predicted top-12: None.
- Actual elite misses outside predicted top 24: Javonte Williams (pred 30, cohort actual 10), Travis Etienne (pred 31, cohort actual 11).
- Largest efficiency lifts: Derrick Henry, Bucky Irving, Jahmyr Gibbs, Saquon Barkley, Bijan Robinson.
- Strongest age/availability penalties: Raheem Mostert, Ameer Abdullah, Christian McCaffrey, Nick Chubb, Dare Ogunbowale.
- Strongest receiving-usage support: Alvin Kamara, Christian McCaffrey, Devon Achane, Breece Hall, Kenneth Walker.
- Highest TFL-risk watch: Jaylen Wright, Kendre Miller, Dare Ogunbowale, Devon Achane, Raheem Mostert. TFL is diagnostic only and is not a Fable score component.

## Same-Season Descriptive Boards

**DESCRIPTIVE ONLY - NOT A FORWARD-LOOKING BACKTEST**

### 2022

| Rank | Player | Team | Score | Actual finish | Labels | Actual points | Touches | Rush | Rec | Yards | TD | YAC/rush | EPA/touch | Success | Explosive | 1st down | TFL | Box YPC | Avail | Age penalty | Reason |
|---:|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Austin Ekeler | LAC | 1.421 | 4 | T6/T12/T24/T36 | 265.7 | 311 | 204 | 107 | 1637 | 18 | 2.907 | -0.008 | 41.7 | 6.4 | 22.6 | 9.8 | 4.040 | 1.000 | -2 | opportunity led (+1.077) |
| 2 | Josh Jacobs | LV | 1.277 | 2 | T6/T12/T24/T36 | 275.3 | 393 | 340 | 53 | 2053 | 12 | 3.371 | -0.002 | 44.4 | 9.1 | 27.6 | 7.7 | 3.840 | 1.000 | 0 | opportunity led (+0.959) |
| 3 | Derrick Henry | TEN | 1.249 | 1 | T6/T12/T24/T36 | 269.8 | 382 | 349 | 33 | 1936 | 13 | 3.527 | -0.058 | 38.4 | 7.7 | 19.2 | 9.7 | 4.130 | 0.941 | -3 | opportunity led (+0.983) |
| 4 | Saquon Barkley | NYG | 1.183 | 6 | T6/T12/T24/T36 | 227.0 | 352 | 295 | 57 | 1650 | 10 | 2.895 | -0.044 | 35.9 | 9.2 | 21.4 | 10.5 | 4.260 | 0.941 | 0 | opportunity led (+1.010) |
| 5 | Christian McCaffrey | SF | 1.180 | 3 | T6/T12/T24/T36 | 271.4 | 329 | 244 | 85 | 1880 | 13 | 2.762 | 0.012 | 40.2 | 9.0 | 24.2 | 8.6 | 3.830 | 1.059 | -1 | opportunity led (+0.959) |
| 6 | Joe Mixon | CIN | 1.085 | 9 | T12/T24/T36 | 179.5 | 270 | 210 | 60 | 1255 | 9 | 2.614 | -0.043 | 40.5 | 5.2 | 22.4 | 7.1 | 2.990 | 0.824 | -1 | opportunity led (+0.918) |
| 7 | Nick Chubb | CLV | 0.985 | 5 | T6/T12/T24/T36 | 254.4 | 329 | 302 | 27 | 1764 | 13 | 3.474 | 0.040 | 43.4 | 11.6 | 22.9 | 9.3 | 4.230 | 1.000 | -1 | opportunity led (+0.642) |
| 8 | Jonathan Taylor | IND | 0.929 | 18 | T24/T36 | 118.4 | 220 | 192 | 28 | 1004 | 4 | 2.839 | -0.130 | 38.5 | 8.3 | 21.9 | 7.8 | 2.680 | 0.647 | 0 | opportunity led (+0.839) |
| 9 | Kenneth Walker | SEA | 0.891 | 12 | T12/T24/T36 | 175.5 | 255 | 228 | 27 | 1215 | 9 | 2.952 | -0.058 | 33.3 | 10.5 | 22.4 | 14.5 | 4.300 | 0.882 | 0 | opportunity led (+0.653) |
| 10 | Rhamondre Stevenson | NE | 0.888 | 19 | T24/T36 | 180.1 | 279 | 210 | 69 | 1461 | 6 | 3.595 | -0.034 | 40.5 | 10.5 | 23.8 | 8.6 | 3.520 | 1.000 | 0 | opportunity led (+0.677) |
| 11 | Najee Harris | PIT | 0.838 | 17 | T24/T36 | 184.5 | 313 | 272 | 41 | 1263 | 10 | 2.728 | -0.092 | 40.4 | 5.2 | 16.5 | 8.1 | 3.700 | 1.000 | 0 | opportunity led (+0.685) |
| 12 | Alvin Kamara | NO | 0.832 | 21 | T24/T36 | 154.7 | 280 | 223 | 57 | 1387 | 4 | 2.830 | -0.147 | 37.2 | 6.7 | 17.9 | 7.2 | 3.120 | 0.882 | -2 | opportunity led (+0.841) |
| 13 | Miles Sanders | PHI | 0.815 | 14 | T24/T36 | 196.7 | 279 | 259 | 20 | 1347 | 11 | 2.988 | 0.049 | 49.0 | 9.7 | 23.9 | 8.5 | 3.260 | 1.000 | 0 | opportunity led (+0.492) |
| 14 | Aaron Jones | GB | 0.812 | 16 | T24/T36 | 189.6 | 272 | 213 | 59 | 1516 | 7 | 3.155 | 0.044 | 46.5 | 9.4 | 25.8 | 10.8 | 5.230 | 1.000 | -2 | opportunity led (+0.616) |
| 15 | Dameon Pierce | HST | 0.801 | 20 | T24/T36 | 136.4 | 250 | 220 | 30 | 1104 | 5 | 3.041 | -0.112 | 37.7 | 6.4 | 24.6 | 12.3 | 3.540 | 0.765 | 0 | opportunity led (+0.701) |
| 16 | Jamaal Williams | DET | 0.782 | 10 | T12/T24/T36 | 213.9 | 274 | 262 | 12 | 1139 | 17 | 2.893 | -0.095 | 42.8 | 6.9 | 25.2 | 7.6 | 3.390 | 1.000 | -2 | opportunity led (+0.488) |
| 17 | Dalvin Cook | MIN | 0.778 | 13 | T24/T36 | 198.8 | 303 | 264 | 39 | 1468 | 10 | 3.114 | -0.160 | 34.1 | 7.2 | 18.9 | 12.5 | 3.850 | 1.000 | -2 | opportunity led (+0.647) |
| 18 | Breece Hall | NYJ | 0.773 | 7 | T12/T24/T36 | 96.1 | 99 | 80 | 19 | 681 | 5 | 3.875 | 0.140 | 41.2 | 15.0 | 25.0 | 11.2 | 2.360 | 0.412 | 0 | opportunity led (+0.524) |
| 19 | James Conner | ARZ | 0.708 | 11 | T12/T24/T36 | 154.2 | 229 | 183 | 46 | 1082 | 8 | 2.721 | -0.011 | 42.6 | 5.5 | 26.2 | 6.6 | 3.900 | 0.765 | -2 | opportunity led (+0.613) |
| 20 | Tony Pollard | DAL | 0.678 | 8 | T12/T24/T36 | 209.8 | 232 | 193 | 39 | 1378 | 12 | 3.731 | 0.019 | 40.4 | 11.9 | 23.8 | 9.8 | 4.680 | 0.941 | 0 | opportunity led (+0.388) |
| 21 | Travis Etienne | JAX | 0.676 | 24 | T24/T36 | 170.1 | 255 | 220 | 35 | 1441 | 5 | 3.214 | -0.038 | 40.5 | 9.6 | 24.6 | 13.2 | 4.050 | 1.000 | 0 | opportunity led (+0.469) |
| 22 | Ezekiel Elliott | DAL | 0.633 | 15 | T24/T36 | 168.8 | 248 | 231 | 17 | 968 | 12 | 2.619 | -0.047 | 42.0 | 5.2 | 22.5 | 6.9 | 3.390 | 0.882 | -2 | opportunity led (+0.473) |
| 23 | David Montgomery | CHI | 0.603 | 28 | T36 | 143.7 | 235 | 201 | 34 | 1117 | 6 | 2.965 | -0.065 | 36.3 | 5.5 | 20.9 | 6.5 | 3.090 | 0.941 | 0 | opportunity led (+0.496) |
| 24 | Devin Singletary | BUF | 0.570 | 30 | T36 | 139.9 | 215 | 177 | 38 | 1099 | 6 | 2.983 | -0.078 | 41.8 | 9.6 | 24.3 | 10.7 | 3.890 | 0.941 | 0 | opportunity led (+0.406) |
| 25 | D'Andre Swift | DET | 0.561 | 23 | T24/T36 | 143.1 | 147 | 99 | 48 | 931 | 8 | 3.384 | 0.038 | 40.4 | 9.1 | 21.2 | 12.1 | 1.197 | 0.824 | 0 | opportunity led (+0.369) |

### 2023

| Rank | Player | Team | Score | Actual finish | Labels | Actual points | Touches | Rush | Rec | Yards | TD | YAC/rush | EPA/touch | Success | Explosive | 1st down | TFL | Box YPC | Avail | Age penalty | Reason |
|---:|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Christian McCaffrey | SF | 1.774 | 1 | T6/T12/T24/T36 | 324.3 | 339 | 272 | 67 | 2023 | 21 | 3.386 | 0.042 | 46.7 | 12.9 | 30.9 | 9.2 | 5.510 | 0.941 | -2 | opportunity led (+1.242) |
| 2 | Kyren Williams | LA | 1.547 | 2 | T6/T12/T24/T36 | 223.0 | 260 | 228 | 32 | 1350 | 15 | 3.110 | 0.086 | 47.4 | 6.1 | 27.6 | 6.6 | 3.270 | 0.706 | 0 | opportunity led (+1.109) |
| 3 | Alvin Kamara | NO | 1.137 | 14 | T24/T36 | 158.0 | 255 | 180 | 75 | 1160 | 6 | 2.578 | -0.012 | 38.3 | 5.6 | 23.9 | 8.3 | 2.820 | 0.765 | -3 | opportunity led (+1.042) |
| 4 | Saquon Barkley | NYG | 1.073 | 9 | T12/T24/T36 | 182.2 | 288 | 247 | 41 | 1242 | 10 | 2.688 | -0.175 | 36.0 | 6.9 | 21.1 | 15.4 | 2.370 | 0.824 | -1 | opportunity led (+0.957) |
| 5 | Joe Mixon | CIN | 1.002 | 12 | T12/T24/T36 | 215.0 | 309 | 257 | 52 | 1410 | 12 | 2.486 | -0.058 | 39.7 | 7.8 | 23.0 | 8.6 | 2.640 | 1.000 | -2 | opportunity led (+0.799) |
| 6 | Tony Pollard | DAL | 0.991 | 25 | T36 | 167.6 | 307 | 252 | 55 | 1316 | 6 | 2.877 | -0.058 | 40.5 | 6.3 | 22.2 | 11.1 | 2.530 | 1.000 | -1 | opportunity led (+0.792) |
| 7 | Josh Jacobs | LV | 0.957 | 19 | T24/T36 | 144.1 | 270 | 233 | 37 | 1101 | 6 | 2.584 | -0.164 | 34.8 | 2.6 | 14.6 | 11.2 | 2.270 | 0.765 | 0 | opportunity led (+0.915) |
| 8 | Isiah Pacheco | KC | 0.944 | 15 | T24/T36 | 169.9 | 249 | 205 | 44 | 1179 | 9 | 3.088 | -0.015 | 40.0 | 7.3 | 25.9 | 6.3 | 5.090 | 0.824 | 0 | opportunity led (+0.701) |
| 9 | Jonathan Taylor | IND | 0.932 | 5 | T6/T12/T24/T36 | 137.4 | 188 | 169 | 19 | 894 | 8 | 3.077 | -0.054 | 39.0 | 7.7 | 24.9 | 8.3 | 2.750 | 0.588 | 0 | opportunity led (+0.720) |
| 10 | David Montgomery | DET | 0.887 | 6 | T6/T12/T24/T36 | 191.2 | 235 | 219 | 16 | 1132 | 13 | 3.151 | 0.044 | 44.3 | 6.8 | 27.4 | 6.8 | 3.670 | 0.824 | -1 | opportunity led (+0.560) |
| 11 | Jahmyr Gibbs | DET | 0.860 | 11 | T12/T24/T36 | 190.1 | 234 | 182 | 52 | 1261 | 11 | 3.302 | -0.022 | 37.4 | 12.1 | 23.6 | 9.3 | 3.810 | 0.882 | 0 | opportunity led (+0.597) |
| 12 | James Conner | ARZ | 0.859 | 7 | T12/T24/T36 | 174.5 | 235 | 208 | 27 | 1205 | 9 | 3.389 | 0.059 | 42.3 | 9.1 | 27.4 | 10.1 | 4.250 | 0.765 | -3 | opportunity led (+0.618) |
| 13 | Rachaad White | TB | 0.840 | 16 | T24/T36 | 203.9 | 336 | 272 | 64 | 1539 | 9 | 2.581 | -0.134 | 30.1 | 4.4 | 18.0 | 6.2 | 3.030 | 1.000 | 0 | opportunity led (+0.789) |
| 14 | Travis Etienne | JAX | 0.830 | 8 | T12/T24/T36 | 224.4 | 325 | 267 | 58 | 1484 | 12 | 2.730 | -0.107 | 34.8 | 5.2 | 19.9 | 11.2 | 3.800 | 1.000 | 0 | opportunity led (+0.706) |
| 15 | Breece Hall | NYJ | 0.826 | 13 | T24/T36 | 214.5 | 299 | 223 | 76 | 1585 | 9 | 3.377 | -0.073 | 34.1 | 6.7 | 17.9 | 13.9 | 5.400 | 1.000 | 0 | opportunity led (+0.678) |
| 16 | Aaron Jones | GB | 0.819 | 29 | T36 | 104.9 | 172 | 142 | 30 | 889 | 3 | 2.923 | 0.014 | 47.2 | 6.3 | 23.9 | 7.8 | 4.170 | 0.647 | -3 | opportunity led (+0.698) |
| 17 | Raheem Mostert | MIA | 0.808 | 3 | T6/T12/T24/T36 | 242.7 | 234 | 209 | 25 | 1187 | 21 | 3.148 | 0.073 | 45.9 | 10.5 | 28.2 | 10.5 | 4.490 | 0.882 | -6 | opportunity led (+0.508) |
| 18 | Bijan Robinson | ATL | 0.740 | 20 | T24/T36 | 188.3 | 272 | 214 | 58 | 1463 | 8 | 3.112 | -0.098 | 34.6 | 9.8 | 24.3 | 9.8 | 4.150 | 1.000 | 0 | opportunity led (+0.613) |
| 19 | D'Andre Swift | PHI | 0.740 | 24 | T24/T36 | 160.3 | 268 | 229 | 39 | 1263 | 6 | 2.751 | 0.007 | 43.7 | 7.4 | 21.8 | 10.0 | 4.160 | 0.941 | 0 | opportunity led (+0.569) |
| 20 | Devon Achane | MIA | 0.730 | 4 | T6/T12/T24/T36 | 163.7 | 130 | 103 | 27 | 997 | 11 | 4.621 | 0.256 | 55.3 | 15.5 | 29.1 | 9.7 | 6.350 | 0.647 | 0 | opportunity led (+0.286) |
| 21 | Javonte Williams | DEN | 0.713 | 34 | T36 | 132.2 | 264 | 217 | 47 | 1002 | 5 | 2.641 | -0.144 | 34.6 | 6.5 | 19.4 | 11.5 | 2.710 | 0.941 | 0 | opportunity led (+0.641) |
| 22 | Najee Harris | PIT | 0.679 | 27 | T36 | 166.5 | 284 | 255 | 29 | 1205 | 8 | 2.922 | -0.088 | 39.2 | 6.7 | 19.6 | 11.4 | 3.150 | 1.000 | 0 | opportunity led (+0.517) |
| 23 | Zack Moss | IND | 0.662 | 23 | T24/T36 | 142.6 | 210 | 183 | 27 | 986 | 7 | 2.852 | -0.067 | 40.4 | 8.2 | 23.5 | 7.7 | 3.600 | 0.824 | 0 | opportunity led (+0.484) |
| 24 | Kenneth Walker | SEA | 0.659 | 17 | T24/T36 | 170.4 | 248 | 219 | 29 | 1164 | 9 | 2.735 | -0.038 | 38.4 | 8.7 | 21.0 | 11.0 | 3.560 | 0.882 | 0 | opportunity led (+0.489) |
| 25 | Derrick Henry | TEN | 0.654 | 10 | T12/T24/T36 | 218.7 | 308 | 280 | 28 | 1381 | 12 | 3.111 | -0.007 | 37.5 | 6.8 | 22.5 | 9.6 | 3.760 | 1.000 | -4 | opportunity led (+0.503) |

### 2024

| Rank | Player | Team | Score | Actual finish | Labels | Actual points | Touches | Rush | Rec | Yards | TD | YAC/rush | EPA/touch | Success | Explosive | 1st down | TFL | Box YPC | Avail | Age penalty | Reason |
|---:|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Saquon Barkley | PHI | 1.453 | 1 | T6/T12/T24/T36 | 322.3 | 378 | 345 | 33 | 2283 | 15 | 3.183 | 0.090 | 44.1 | 8.7 | 23.8 | 9.6 | 3.980 | 0.941 | -2 | opportunity led (+1.091) |
| 2 | Bijan Robinson | ATL | 1.356 | 4 | T6/T12/T24/T36 | 280.7 | 365 | 304 | 61 | 1887 | 15 | 3.010 | 0.046 | 49.3 | 9.2 | 27.3 | 7.2 | 3.690 | 1.000 | 0 | opportunity led (+0.996) |
| 3 | Kyren Williams | LA | 1.266 | 7 | T12/T24/T36 | 238.1 | 350 | 316 | 34 | 1481 | 16 | 2.633 | -0.067 | 44.0 | 5.7 | 26.9 | 8.9 | 3.360 | 0.941 | 0 | opportunity led (+0.970) |
| 4 | Jahmyr Gibbs | DET | 1.198 | 3 | T6/T12/T24/T36 | 310.9 | 302 | 250 | 52 | 1929 | 20 | 3.136 | 0.116 | 44.4 | 13.6 | 28.0 | 7.6 | 5.000 | 1.000 | 0 | opportunity led (+0.766) |
| 5 | Jonathan Taylor | IND | 1.186 | 5 | T6/T12/T24/T36 | 226.7 | 321 | 303 | 18 | 1567 | 12 | 2.677 | -0.065 | 36.0 | 8.9 | 23.8 | 9.2 | 3.760 | 0.824 | 0 | opportunity led (+0.965) |
| 6 | Alvin Kamara | NO | 1.143 | 10 | T12/T24/T36 | 197.3 | 296 | 228 | 68 | 1493 | 8 | 2.697 | -0.061 | 39.9 | 7.9 | 22.8 | 12.7 | 3.690 | 0.824 | -4 | opportunity led (+1.074) |
| 7 | Joe Mixon | HST | 1.141 | 9 | T12/T24/T36 | 204.5 | 281 | 245 | 36 | 1325 | 12 | 2.984 | -0.047 | 34.3 | 8.2 | 21.2 | 14.3 | 3.620 | 0.824 | -3 | opportunity led (+0.935) |
| 8 | Chuba Hubbard | CAR | 1.104 | 12 | T12/T24/T36 | 198.6 | 293 | 250 | 43 | 1366 | 11 | 3.272 | 0.033 | 44.4 | 9.6 | 24.8 | 6.0 | 4.590 | 0.882 | 0 | opportunity led (+0.809) |
| 9 | Josh Jacobs | GB | 1.069 | 6 | T6/T12/T24/T36 | 257.1 | 337 | 301 | 36 | 1671 | 16 | 3.276 | -0.054 | 39.2 | 7.6 | 24.9 | 9.3 | 3.710 | 1.000 | -1 | opportunity led (+0.792) |
| 10 | Derrick Henry | BLT | 1.062 | 2 | T6/T12/T24/T36 | 317.4 | 344 | 325 | 19 | 2114 | 18 | 3.689 | 0.118 | 47.7 | 11.4 | 28.6 | 8.0 | 5.850 | 1.000 | -5 | opportunity led (+0.632) |
| 11 | Devon Achane | MIA | 0.930 | 13 | T24/T36 | 221.9 | 281 | 203 | 78 | 1499 | 12 | 2.941 | -0.040 | 41.9 | 9.4 | 18.7 | 17.2 | 3.580 | 1.000 | 0 | opportunity led (+0.719) |
| 12 | James Conner | ARZ | 0.924 | 14 | T24/T36 | 206.8 | 283 | 236 | 47 | 1508 | 9 | 3.165 | 0.000 | 42.4 | 11.0 | 28.0 | 8.9 | 3.540 | 0.941 | -4 | opportunity led (+0.725) |
| 13 | Chase Brown | CIN | 0.892 | 15 | T24/T36 | 201.0 | 283 | 229 | 54 | 1350 | 11 | 2.873 | -0.021 | 38.4 | 7.4 | 21.4 | 8.3 | 3.230 | 0.941 | 0 | opportunity led (+0.700) |
| 14 | Kenneth Walker | SEA | 0.857 | 17 | T24/T36 | 135.2 | 199 | 153 | 46 | 872 | 8 | 3.059 | -0.061 | 41.2 | 5.2 | 18.3 | 13.1 | 2.820 | 0.647 | 0 | opportunity led (+0.743) |
| 15 | Aaron Jones | MIN | 0.839 | 20 | T24/T36 | 190.6 | 306 | 255 | 51 | 1546 | 7 | 2.929 | -0.044 | 40.4 | 7.8 | 19.2 | 8.2 | 3.680 | 1.000 | -4 | opportunity led (+0.732) |
| 16 | David Montgomery | DET | 0.822 | 11 | T12/T24/T36 | 185.7 | 221 | 185 | 36 | 1116 | 12 | 2.930 | -0.036 | 48.1 | 6.5 | 27.0 | 7.0 | 3.330 | 0.824 | -2 | opportunity led (+0.596) |
| 17 | James Cook | BUF | 0.810 | 8 | T12/T24/T36 | 234.7 | 239 | 207 | 32 | 1267 | 18 | 3.227 | 0.044 | 42.5 | 7.7 | 23.7 | 10.1 | 4.120 | 0.941 | 0 | opportunity led (+0.475) |
| 18 | J.K. Dobbins | LAC | 0.775 | 16 | T24/T36 | 159.8 | 227 | 195 | 32 | 1058 | 9 | 3.092 | 0.019 | 35.4 | 10.8 | 24.1 | 9.2 | 4.960 | 0.765 | 0 | opportunity led (+0.595) |
| 19 | Najee Harris | PIT | 0.752 | 26 | T36 | 168.6 | 299 | 263 | 36 | 1326 | 6 | 2.817 | -0.057 | 35.4 | 5.7 | 19.4 | 8.4 | 3.320 | 1.000 | -1 | opportunity led (+0.656) |
| 20 | Bucky Irving | TB | 0.747 | 18 | T24/T36 | 197.4 | 254 | 207 | 47 | 1514 | 8 | 3.874 | 0.082 | 44.9 | 9.7 | 25.1 | 7.2 | 5.400 | 1.000 | 0 | opportunity led (+0.448) |
| 21 | Kareem Hunt | KC | 0.680 | 21 | T24/T36 | 132.4 | 223 | 200 | 23 | 904 | 7 | 2.270 | 0.010 | 44.0 | 4.0 | 21.0 | 5.5 | 3.230 | 0.765 | -4 | opportunity led (+0.613) |
| 22 | Rhamondre Stevenson | NE | 0.668 | 28 | T36 | 142.9 | 240 | 207 | 33 | 969 | 8 | 3.000 | -0.158 | 35.3 | 7.7 | 19.8 | 9.7 | 3.440 | 0.882 | -1 | opportunity led (+0.562) |
| 23 | Tony Pollard | TEN | 0.660 | 24 | T24/T36 | 159.7 | 301 | 260 | 41 | 1317 | 5 | 2.973 | -0.090 | 34.2 | 7.7 | 20.4 | 9.6 | 4.300 | 0.941 | -2 | opportunity led (+0.627) |
| 24 | Breece Hall | NYJ | 0.639 | 19 | T24/T36 | 183.9 | 266 | 209 | 57 | 1359 | 8 | 2.990 | -0.083 | 35.9 | 9.1 | 19.1 | 10.1 | 2.380 | 0.941 | 0 | opportunity led (+0.564) |
| 25 | Brian Robinson | WAS | 0.562 | 23 | T24/T36 | 139.8 | 207 | 187 | 20 | 958 | 8 | 2.727 | -0.058 | 42.2 | 6.4 | 25.1 | 9.6 | 3.710 | 0.824 | 0 | opportunity led (+0.406) |

### 2025

| Rank | Player | Team | Score | Actual finish | Labels | Actual points | Touches | Rush | Rec | Yards | TD | YAC/rush | EPA/touch | Success | Explosive | 1st down | TFL | Box YPC | Avail | Age penalty | Reason |
|---:|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Christian McCaffrey | SF | 1.845 | 2 | T6/T12/T24/T36 | 314.6 | 413 | 311 | 102 | 2126 | 17 | 2.559 | -0.051 | 39.2 | 6.4 | 22.5 | 9.7 | 3.360 | 1.000 | -4 | opportunity led (+1.573) |
| 2 | Jonathan Taylor | IND | 1.433 | 1 | T6/T12/T24/T36 | 316.3 | 369 | 323 | 46 | 1963 | 20 | 3.303 | 0.048 | 44.3 | 8.1 | 26.0 | 8.7 | 4.110 | 1.000 | -1 | opportunity led (+0.991) |
| 3 | Bijan Robinson | ATL | 1.269 | 3 | T6/T12/T24/T36 | 295.8 | 366 | 287 | 79 | 2298 | 11 | 3.801 | -0.036 | 41.1 | 8.4 | 21.9 | 9.1 | 3.560 | 1.000 | 0 | opportunity led (+1.006) |
| 4 | Jahmyr Gibbs | DET | 1.264 | 4 | T6/T12/T24/T36 | 291.9 | 320 | 243 | 77 | 1839 | 18 | 2.996 | -0.008 | 39.9 | 8.6 | 23.1 | 11.1 | 4.460 | 1.000 | 0 | opportunity led (+0.943) |
| 5 | Devon Achane | MIA | 1.174 | 6 | T6/T12/T24/T36 | 255.8 | 305 | 238 | 67 | 1838 | 12 | 3.895 | 0.046 | 38.2 | 13.4 | 23.9 | 9.7 | 5.570 | 0.941 | 0 | opportunity led (+0.837) |
| 6 | James Cook | BUF | 1.110 | 5 | T6/T12/T24/T36 | 275.2 | 342 | 309 | 33 | 1912 | 14 | 3.113 | 0.016 | 45.6 | 8.7 | 22.0 | 4.5 | 4.720 | 1.000 | 0 | opportunity led (+0.764) |
| 7 | Javonte Williams | DAL | 1.046 | 10 | T12/T24/T36 | 211.8 | 287 | 252 | 35 | 1338 | 13 | 3.258 | 0.043 | 45.6 | 6.8 | 27.0 | 5.2 | 3.050 | 0.941 | 0 | opportunity led (+0.711) |
| 8 | Derrick Henry | BLT | 0.989 | 7 | T12/T24/T36 | 270.5 | 322 | 307 | 15 | 1745 | 16 | 3.453 | 0.028 | 41.7 | 9.8 | 26.4 | 7.2 | 5.080 | 1.000 | -6 | opportunity led (+0.650) |
| 9 | Josh Jacobs | GB | 0.977 | 8 | T12/T24/T36 | 205.1 | 270 | 234 | 36 | 1211 | 14 | 2.949 | -0.055 | 43.6 | 6.0 | 23.5 | 8.1 | 2.620 | 0.882 | -2 | opportunity led (+0.747) |
| 10 | Kyren Williams | LA | 0.951 | 9 | T12/T24/T36 | 231.3 | 295 | 259 | 36 | 1533 | 13 | 2.950 | 0.017 | 50.2 | 7.0 | 29.3 | 4.6 | 4.160 | 1.000 | 0 | opportunity led (+0.625) |
| 11 | Chase Brown | CIN | 0.861 | 13 | T24/T36 | 211.6 | 301 | 232 | 69 | 1456 | 11 | 2.784 | -0.011 | 40.1 | 8.2 | 22.4 | 6.9 | 4.210 | 1.000 | 0 | opportunity led (+0.681) |
| 12 | Saquon Barkley | PHI | 0.853 | 15 | T24/T36 | 195.3 | 317 | 280 | 37 | 1413 | 9 | 2.821 | -0.079 | 37.5 | 7.1 | 17.1 | 14.6 | 3.310 | 0.941 | -3 | opportunity led (+0.757) |
| 13 | Travis Etienne | JAX | 0.847 | 12 | T12/T24/T36 | 217.9 | 296 | 260 | 36 | 1399 | 13 | 2.877 | -0.064 | 35.8 | 5.8 | 18.5 | 10.0 | 4.650 | 1.000 | -1 | opportunity led (+0.657) |
| 14 | Omarion Hampton | LAC | 0.798 | 16 | T24/T36 | 103.7 | 156 | 124 | 32 | 737 | 5 | 2.718 | -0.005 | 41.9 | 7.3 | 25.0 | 12.1 | 3.110 | 0.529 | 0 | opportunity led (+0.683) |
| 15 | Ashton Jeanty | LV | 0.780 | 17 | T24/T36 | 192.1 | 321 | 266 | 55 | 1321 | 10 | 3.068 | -0.200 | 31.9 | 6.0 | 16.5 | 16.9 | 1.650 | 1.000 | 0 | opportunity led (+0.742) |
| 16 | Cam Skattebo | NYG | 0.769 | 11 | T12/T24/T36 | 103.7 | 125 | 101 | 24 | 617 | 7 | 2.802 | -0.105 | 40.6 | 5.9 | 26.7 | 7.9 | 3.500 | 0.471 | 0 | opportunity led (+0.638) |
| 17 | D'Andre Swift | CHI | 0.729 | 14 | T24/T36 | 198.6 | 257 | 223 | 34 | 1386 | 10 | 3.054 | 0.060 | 48.0 | 8.5 | 27.8 | 6.3 | 3.870 | 0.941 | -1 | opportunity led (+0.483) |
| 18 | Jaylen Warren | PIT | 0.655 | 18 | T24/T36 | 177.1 | 251 | 211 | 40 | 1291 | 8 | 2.995 | -0.002 | 42.6 | 7.6 | 24.6 | 8.1 | 3.500 | 0.941 | -1 | opportunity led (+0.485) |
| 19 | Rico Dowdle | CAR | 0.599 | 22 | T24/T36 | 179.3 | 275 | 236 | 39 | 1373 | 7 | 3.123 | -0.005 | 42.4 | 8.5 | 21.6 | 6.4 | 3.580 | 1.000 | -2 | opportunity led (+0.468) |
| 20 | Bucky Irving | TB | 0.597 | 19 | T24/T36 | 110.5 | 203 | 173 | 30 | 865 | 4 | 2.393 | -0.175 | 34.7 | 4.6 | 15.6 | 12.1 | 2.600 | 0.588 | 0 | opportunity led (+0.690) |
| 21 | Zach Charbonnet | SEA | 0.558 | 26 | T36 | 159.4 | 204 | 184 | 20 | 874 | 12 | 3.065 | -0.011 | 41.3 | 6.0 | 26.1 | 10.9 | 3.030 | 0.941 | 0 | opportunity led (+0.309) |
| 22 | Breece Hall | NYJ | 0.549 | 20 | T24/T36 | 175.7 | 279 | 243 | 36 | 1415 | 5 | 3.016 | -0.080 | 40.7 | 8.6 | 24.3 | 13.6 | 4.650 | 0.941 | 0 | opportunity led (+0.466) |
| 23 | Quinshon Judkins | CLV | 0.548 | 25 | T36 | 141.8 | 256 | 230 | 26 | 998 | 7 | 2.887 | -0.102 | 33.0 | 5.7 | 21.7 | 10.4 | 3.060 | 0.824 | 0 | opportunity led (+0.506) |
| 24 | Kenneth Walker | SEA | 0.501 | 28 | T36 | 160.9 | 252 | 221 | 31 | 1309 | 5 | 3.348 | -0.057 | 38.0 | 9.9 | 20.8 | 11.8 | 4.640 | 1.000 | 0 | opportunity led (+0.341) |
| 25 | Kenneth Gainwell | PIT | 0.495 | 30 | T36 | 150.3 | 187 | 114 | 73 | 1023 | 8 | 2.825 | -0.004 | 45.6 | 8.8 | 29.8 | 13.2 | 4.530 | 1.000 | -1 | opportunity led (+0.368) |

## Baselines

- HISTORICAL CURRENT PIGSKIN BASELINE UNAVAILABLE
- PRIOR EPISODE FORMULA BASELINE UNAVAILABLE

## Show-Ready Talking Points

- The formula is dominated by role and non-garbage-time volume, as designed.
- Efficiency is visible but shrunk, so low-volume outliers cannot control the board.
- Missing red-zone or age inputs fail closed instead of becoming invented zeroes.
- The honest comparison is against actual outcomes because valid historical baselines are unavailable.
