# Standard BQML V2 2026 Conservative Overlay Review Board

Warning: owner-review only. This board is not live, is not a champion activation, and did not write ranking tables.

Current Pigskin remains the live Standard ranking source. No formula champion is active.

Phase 33.12 calibration note: this Phase 33.11 original overlay is too aggressive for activation. It overweights uncalibrated cross-position BQML VOR, pushes QBs and RBs up too hard, and suppresses several WR/TE anchors. Use `docs/rebuild/standard-bqml-v2-overlay-calibration.md` for the safer 80/15/5 owner-review anchor. Current Pigskin still holds for Standard.

Review version: `phase33_11_standard_2026_overlay_review`.

Rule formula:

- 70 percent Current Pigskin normalized score.
- 20 percent BQML VOR normalized score.
- 10 percent BQML finalist safety or elite normalized score.

Input policy:

- Standard only.
- Active 2026 Standard Current Pigskin rows supplied the review universe and baseline comparison.
- Latest pre-2026 `ranking_backtest_feature_mart` rows supplied BQML predictors where available.
- Sleeper current context is display only.
- Draft Priority Index is display only.
- No 2026 outcomes, target labels, Sleeper current fields, or `pigskin_context_score` were used as predictors.

Owner decision read: inspectable with warnings. Movement is too aggressive for direct champion activation, especially QB/RB risers and WR/TE fallers in the top 24.

## Query Summary
- Dry-run bytes: 57,609,511
- Review rows: 260
- Rows by position: QB45, RB80, TE35, WR100
- Missing feature rows: 82
- High missingness rows over 50 percent: 82
- VOR score unavailable rows: 0
- Finalist signal unavailable rows: 0
- Rank delta over 20 rows: 46
- Injury status flag rows: 30

## Top 24 Overlay Overall
| Rank | Player | Pos | Team | DPI | Overlay | Current rank | Delta | VOR | Signal | Miss | Warnings |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Josh Allen | QB | BUF | 100.0 | 0.946 | 3 | +2 | 24.707 | 82.425 | 0.277 |  |
| 2 | Jalen Hurts | QB | PHI | 99.6 | 0.911 | 34 | +32 | 31.411 | 85.901 | 0.170 | rank_delta_over_20 |
| 3 | Christian McCaffrey | RB | SF | 99.2 | 0.886 | 4 | +1 | 15.346 | 81.006 | 0.128 |  |
| 4 | Jonathan Taylor | RB | IND | 98.9 | 0.840 | 19 | +15 | 15.449 | 81.897 | 0.170 |  |
| 5 | Patrick Mahomes | QB | KC | 98.5 | 0.814 | 10 | +5 | 11.480 | 63.258 | 0.170 | injury_status_flag |
| 6 | Jahmyr Gibbs | RB | DET | 98.1 | 0.813 | 16 | +10 | 11.547 | 71.082 | 0.234 |  |
| 7 | Bijan Robinson | RB | ATL | 97.7 | 0.810 | 11 | +4 | 9.450 | 70.009 | 0.234 |  |
| 8 | De'Von Achane | RB | MIA | 97.3 | 0.796 | 23 | +15 | 11.683 | 71.721 | 0.213 | injury_status_flag |
| 9 | Kyren Williams | RB | LAR | 96.9 | 0.783 | 30 | +21 | 12.232 | 73.101 | 0.170 | rank_delta_over_20 |
| 10 | Saquon Barkley | RB | PHI | 96.6 | 0.779 | 49 | +39 | 15.474 | 84.003 | 0.149 | rank_delta_over_20 |
| 11 | Puka Nacua | WR | LAR | 96.2 | 0.766 | 2 | -9 | 3.115 | 43.301 | 0.234 |  |
| 12 | Daniel Jones | QB | IND | 95.8 | 0.765 | 42 | +30 | 16.737 | 56.940 | 0.277 | rank_delta_over_20, injury_status_flag |
| 13 | Ja'Marr Chase | WR | CIN | 95.4 | 0.761 | 7 | -6 | 3.580 | 44.941 | 0.128 |  |
| 14 | Amon-Ra St. Brown | WR | DET | 95.0 | 0.757 | 5 | -9 | 3.015 | 41.632 | 0.149 |  |
| 15 | Trey McBride | TE | ARI | 94.6 | 0.750 | 6 | -9 | 1.802 | 42.345 | 0.234 |  |
| 16 | Justin Jefferson | WR | MIN | 94.3 | 0.741 | 17 | +1 | 4.327 | 51.815 | 0.128 |  |
| 17 | A.J. Brown | WR | NE | 93.9 | 0.738 | 14 | -3 | 3.454 | 44.652 | 0.234 |  |
| 18 | James Cook | RB | BUF | 93.5 | 0.736 | 36 | +18 | 8.329 | 63.502 | 0.170 |  |
| 19 | Dak Prescott | QB | DAL | 93.1 | 0.734 | 28 | +9 | 8.588 | 48.992 | 0.277 |  |
| 20 | Drake Maye | QB | NE | 92.7 | 0.734 | 9 | -11 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 21 | George Kittle | TE | SF | 92.4 | 0.727 | 20 | -1 | 2.817 | 54.563 | 0.170 | injury_status_flag |
| 22 | Lamar Jackson | QB | BAL | 92.0 | 0.727 | 75 | +53 | 16.955 | 78.898 | 0.170 | rank_delta_over_20 |
| 23 | Trevor Lawrence | QB | JAX | 91.6 | 0.727 | 38 | +15 | 11.218 | 47.581 | 0.277 |  |
| 24 | Brock Purdy | QB | SF | 91.2 | 0.724 | 31 | +7 | 9.257 | 43.460 | 0.277 |  |

## Top 50 Overlay Overall
| Rank | Player | Pos | Team | DPI | Overlay | Current rank | Delta | VOR | Signal | Miss | Warnings |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Josh Allen | QB | BUF | 100.0 | 0.946 | 3 | +2 | 24.707 | 82.425 | 0.277 |  |
| 2 | Jalen Hurts | QB | PHI | 99.6 | 0.911 | 34 | +32 | 31.411 | 85.901 | 0.170 | rank_delta_over_20 |
| 3 | Christian McCaffrey | RB | SF | 99.2 | 0.886 | 4 | +1 | 15.346 | 81.006 | 0.128 |  |
| 4 | Jonathan Taylor | RB | IND | 98.9 | 0.840 | 19 | +15 | 15.449 | 81.897 | 0.170 |  |
| 5 | Patrick Mahomes | QB | KC | 98.5 | 0.814 | 10 | +5 | 11.480 | 63.258 | 0.170 | injury_status_flag |
| 6 | Jahmyr Gibbs | RB | DET | 98.1 | 0.813 | 16 | +10 | 11.547 | 71.082 | 0.234 |  |
| 7 | Bijan Robinson | RB | ATL | 97.7 | 0.810 | 11 | +4 | 9.450 | 70.009 | 0.234 |  |
| 8 | De'Von Achane | RB | MIA | 97.3 | 0.796 | 23 | +15 | 11.683 | 71.721 | 0.213 | injury_status_flag |
| 9 | Kyren Williams | RB | LAR | 96.9 | 0.783 | 30 | +21 | 12.232 | 73.101 | 0.170 | rank_delta_over_20 |
| 10 | Saquon Barkley | RB | PHI | 96.6 | 0.779 | 49 | +39 | 15.474 | 84.003 | 0.149 | rank_delta_over_20 |
| 11 | Puka Nacua | WR | LAR | 96.2 | 0.766 | 2 | -9 | 3.115 | 43.301 | 0.234 |  |
| 12 | Daniel Jones | QB | IND | 95.8 | 0.765 | 42 | +30 | 16.737 | 56.940 | 0.277 | rank_delta_over_20, injury_status_flag |
| 13 | Ja'Marr Chase | WR | CIN | 95.4 | 0.761 | 7 | -6 | 3.580 | 44.941 | 0.128 |  |
| 14 | Amon-Ra St. Brown | WR | DET | 95.0 | 0.757 | 5 | -9 | 3.015 | 41.632 | 0.149 |  |
| 15 | Trey McBride | TE | ARI | 94.6 | 0.750 | 6 | -9 | 1.802 | 42.345 | 0.234 |  |
| 16 | Justin Jefferson | WR | MIN | 94.3 | 0.741 | 17 | +1 | 4.327 | 51.815 | 0.128 |  |
| 17 | A.J. Brown | WR | NE | 93.9 | 0.738 | 14 | -3 | 3.454 | 44.652 | 0.234 |  |
| 18 | James Cook | RB | BUF | 93.5 | 0.736 | 36 | +18 | 8.329 | 63.502 | 0.170 |  |
| 19 | Dak Prescott | QB | DAL | 93.1 | 0.734 | 28 | +9 | 8.588 | 48.992 | 0.277 |  |
| 20 | Drake Maye | QB | NE | 92.7 | 0.734 | 9 | -11 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 21 | George Kittle | TE | SF | 92.4 | 0.727 | 20 | -1 | 2.817 | 54.563 | 0.170 | injury_status_flag |
| 22 | Lamar Jackson | QB | BAL | 92.0 | 0.727 | 75 | +53 | 16.955 | 78.898 | 0.170 | rank_delta_over_20 |
| 23 | Trevor Lawrence | QB | JAX | 91.6 | 0.727 | 38 | +15 | 11.218 | 47.581 | 0.277 |  |
| 24 | Brock Purdy | QB | SF | 91.2 | 0.724 | 31 | +7 | 9.257 | 43.460 | 0.277 |  |
| 25 | Josh Jacobs | RB | GB | 90.8 | 0.723 | 62 | +37 | 13.284 | 76.421 | 0.149 | rank_delta_over_20 |
| 26 | Javonte Williams | RB | DAL | 90.4 | 0.723 | 45 | +19 | 8.930 | 65.075 | 0.170 |  |
| 27 | Jaxon Smith-Njigba | WR | SEA | 90.1 | 0.721 | 1 | -26 | 0.896 | 13.721 | 0.298 | rank_delta_over_20 |
| 28 | Chris Olave | WR | NO | 89.7 | 0.716 | 12 | -16 | 2.277 | 30.018 | 0.234 | injury_status_flag |
| 29 | Sam LaPorta | TE | DET | 89.3 | 0.712 | 26 | -3 | 2.753 | 54.538 | 0.234 | injury_status_flag |
| 30 | Drake London | WR | ATL | 88.9 | 0.704 | 8 | -22 | 1.233 | 18.139 | 0.191 | rank_delta_over_20 |
| 31 | Matthew Stafford | QB | LAR | 88.5 | 0.704 | 22 | -9 | 3.999 | 32.405 | 0.170 |  |
| 32 | Brock Bowers | TE | LV | 88.2 | 0.701 | 13 | -19 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness |
| 33 | Garrett Wilson | WR | NYJ | 87.8 | 0.701 | 18 | -15 | 2.067 | 33.671 | 0.128 |  |
| 34 | CeeDee Lamb | WR | DAL | 87.4 | 0.701 | 29 | -5 | 3.895 | 46.620 | 0.128 |  |
| 35 | Davante Adams | WR | LAR | 87.0 | 0.700 | 27 | -8 | 3.522 | 43.646 | 0.149 |  |
| 36 | Rashee Rice | WR | KC | 86.6 | 0.698 | 15 | -21 | 1.713 | 25.146 | 0.234 | rank_delta_over_20, injury_status_flag |
| 37 | Travis Etienne | RB | NO | 86.2 | 0.697 | 67 | +30 | 10.722 | 74.056 | 0.170 | rank_delta_over_20 |
| 38 | Breece Hall | RB | NYJ | 85.9 | 0.692 | 74 | +36 | 11.498 | 75.245 | 0.170 | rank_delta_over_20 |
| 39 | George Pickens | WR | DAL | 85.5 | 0.689 | 21 | -18 | 2.276 | 27.289 | 0.170 |  |
| 40 | Jordan Love | QB | GB | 85.1 | 0.680 | 25 | -15 | 3.851 | 22.503 | 0.277 |  |
| 41 | Zay Flowers | WR | BAL | 84.7 | 0.679 | 24 | -17 | 1.957 | 25.853 | 0.234 |  |
| 42 | Justin Herbert | QB | LAC | 84.3 | 0.678 | 71 | +29 | 11.996 | 58.004 | 0.170 | rank_delta_over_20 |
| 43 | Derrick Henry | RB | BAL | 83.9 | 0.675 | 91 | +48 | 13.383 | 75.852 | 0.128 | rank_delta_over_20 |
| 44 | D'Andre Swift | RB | CHI | 83.6 | 0.670 | 69 | +25 | 9.480 | 61.659 | 0.128 | rank_delta_over_20 |
| 45 | C.J. Stroud | QB | HOU | 83.2 | 0.667 | 66 | +21 | 10.965 | 48.738 | 0.234 | rank_delta_over_20 |
| 46 | Travis Kelce | TE | KC | 82.8 | 0.663 | 52 | +6 | 2.692 | 57.511 | 0.170 |  |
| 47 | Kyle Pitts | TE | ATL | 82.4 | 0.662 | 39 | -8 | 2.133 | 41.118 | 0.170 |  |
| 48 | Kyler Murray | QB | MIN | 82.0 | 0.659 | 100 | +52 | 16.707 | 61.210 | 0.277 | rank_delta_over_20 |
| 49 | Nico Collins | WR | HOU | 81.7 | 0.655 | 32 | -17 | 1.922 | 23.899 | 0.170 |  |
| 50 | Dallas Goedert | TE | PHI | 81.3 | 0.652 | 44 | -6 | 1.653 | 41.374 | 0.170 |  |

## Top 100 Overlay Overall
| Rank | Player | Pos | Team | DPI | Overlay | Current rank | Delta | VOR | Signal | Miss | Warnings |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Josh Allen | QB | BUF | 100.0 | 0.946 | 3 | +2 | 24.707 | 82.425 | 0.277 |  |
| 2 | Jalen Hurts | QB | PHI | 99.6 | 0.911 | 34 | +32 | 31.411 | 85.901 | 0.170 | rank_delta_over_20 |
| 3 | Christian McCaffrey | RB | SF | 99.2 | 0.886 | 4 | +1 | 15.346 | 81.006 | 0.128 |  |
| 4 | Jonathan Taylor | RB | IND | 98.9 | 0.840 | 19 | +15 | 15.449 | 81.897 | 0.170 |  |
| 5 | Patrick Mahomes | QB | KC | 98.5 | 0.814 | 10 | +5 | 11.480 | 63.258 | 0.170 | injury_status_flag |
| 6 | Jahmyr Gibbs | RB | DET | 98.1 | 0.813 | 16 | +10 | 11.547 | 71.082 | 0.234 |  |
| 7 | Bijan Robinson | RB | ATL | 97.7 | 0.810 | 11 | +4 | 9.450 | 70.009 | 0.234 |  |
| 8 | De'Von Achane | RB | MIA | 97.3 | 0.796 | 23 | +15 | 11.683 | 71.721 | 0.213 | injury_status_flag |
| 9 | Kyren Williams | RB | LAR | 96.9 | 0.783 | 30 | +21 | 12.232 | 73.101 | 0.170 | rank_delta_over_20 |
| 10 | Saquon Barkley | RB | PHI | 96.6 | 0.779 | 49 | +39 | 15.474 | 84.003 | 0.149 | rank_delta_over_20 |
| 11 | Puka Nacua | WR | LAR | 96.2 | 0.766 | 2 | -9 | 3.115 | 43.301 | 0.234 |  |
| 12 | Daniel Jones | QB | IND | 95.8 | 0.765 | 42 | +30 | 16.737 | 56.940 | 0.277 | rank_delta_over_20, injury_status_flag |
| 13 | Ja'Marr Chase | WR | CIN | 95.4 | 0.761 | 7 | -6 | 3.580 | 44.941 | 0.128 |  |
| 14 | Amon-Ra St. Brown | WR | DET | 95.0 | 0.757 | 5 | -9 | 3.015 | 41.632 | 0.149 |  |
| 15 | Trey McBride | TE | ARI | 94.6 | 0.750 | 6 | -9 | 1.802 | 42.345 | 0.234 |  |
| 16 | Justin Jefferson | WR | MIN | 94.3 | 0.741 | 17 | +1 | 4.327 | 51.815 | 0.128 |  |
| 17 | A.J. Brown | WR | NE | 93.9 | 0.738 | 14 | -3 | 3.454 | 44.652 | 0.234 |  |
| 18 | James Cook | RB | BUF | 93.5 | 0.736 | 36 | +18 | 8.329 | 63.502 | 0.170 |  |
| 19 | Dak Prescott | QB | DAL | 93.1 | 0.734 | 28 | +9 | 8.588 | 48.992 | 0.277 |  |
| 20 | Drake Maye | QB | NE | 92.7 | 0.734 | 9 | -11 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 21 | George Kittle | TE | SF | 92.4 | 0.727 | 20 | -1 | 2.817 | 54.563 | 0.170 | injury_status_flag |
| 22 | Lamar Jackson | QB | BAL | 92.0 | 0.727 | 75 | +53 | 16.955 | 78.898 | 0.170 | rank_delta_over_20 |
| 23 | Trevor Lawrence | QB | JAX | 91.6 | 0.727 | 38 | +15 | 11.218 | 47.581 | 0.277 |  |
| 24 | Brock Purdy | QB | SF | 91.2 | 0.724 | 31 | +7 | 9.257 | 43.460 | 0.277 |  |
| 25 | Josh Jacobs | RB | GB | 90.8 | 0.723 | 62 | +37 | 13.284 | 76.421 | 0.149 | rank_delta_over_20 |
| 26 | Javonte Williams | RB | DAL | 90.4 | 0.723 | 45 | +19 | 8.930 | 65.075 | 0.170 |  |
| 27 | Jaxon Smith-Njigba | WR | SEA | 90.1 | 0.721 | 1 | -26 | 0.896 | 13.721 | 0.298 | rank_delta_over_20 |
| 28 | Chris Olave | WR | NO | 89.7 | 0.716 | 12 | -16 | 2.277 | 30.018 | 0.234 | injury_status_flag |
| 29 | Sam LaPorta | TE | DET | 89.3 | 0.712 | 26 | -3 | 2.753 | 54.538 | 0.234 | injury_status_flag |
| 30 | Drake London | WR | ATL | 88.9 | 0.704 | 8 | -22 | 1.233 | 18.139 | 0.191 | rank_delta_over_20 |
| 31 | Matthew Stafford | QB | LAR | 88.5 | 0.704 | 22 | -9 | 3.999 | 32.405 | 0.170 |  |
| 32 | Brock Bowers | TE | LV | 88.2 | 0.701 | 13 | -19 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness |
| 33 | Garrett Wilson | WR | NYJ | 87.8 | 0.701 | 18 | -15 | 2.067 | 33.671 | 0.128 |  |
| 34 | CeeDee Lamb | WR | DAL | 87.4 | 0.701 | 29 | -5 | 3.895 | 46.620 | 0.128 |  |
| 35 | Davante Adams | WR | LAR | 87.0 | 0.700 | 27 | -8 | 3.522 | 43.646 | 0.149 |  |
| 36 | Rashee Rice | WR | KC | 86.6 | 0.698 | 15 | -21 | 1.713 | 25.146 | 0.234 | rank_delta_over_20, injury_status_flag |
| 37 | Travis Etienne | RB | NO | 86.2 | 0.697 | 67 | +30 | 10.722 | 74.056 | 0.170 | rank_delta_over_20 |
| 38 | Breece Hall | RB | NYJ | 85.9 | 0.692 | 74 | +36 | 11.498 | 75.245 | 0.170 | rank_delta_over_20 |
| 39 | George Pickens | WR | DAL | 85.5 | 0.689 | 21 | -18 | 2.276 | 27.289 | 0.170 |  |
| 40 | Jordan Love | QB | GB | 85.1 | 0.680 | 25 | -15 | 3.851 | 22.503 | 0.277 |  |
| 41 | Zay Flowers | WR | BAL | 84.7 | 0.679 | 24 | -17 | 1.957 | 25.853 | 0.234 |  |
| 42 | Justin Herbert | QB | LAC | 84.3 | 0.678 | 71 | +29 | 11.996 | 58.004 | 0.170 | rank_delta_over_20 |
| 43 | Derrick Henry | RB | BAL | 83.9 | 0.675 | 91 | +48 | 13.383 | 75.852 | 0.128 | rank_delta_over_20 |
| 44 | D'Andre Swift | RB | CHI | 83.6 | 0.670 | 69 | +25 | 9.480 | 61.659 | 0.128 | rank_delta_over_20 |
| 45 | C.J. Stroud | QB | HOU | 83.2 | 0.667 | 66 | +21 | 10.965 | 48.738 | 0.234 | rank_delta_over_20 |
| 46 | Travis Kelce | TE | KC | 82.8 | 0.663 | 52 | +6 | 2.692 | 57.511 | 0.170 |  |
| 47 | Kyle Pitts | TE | ATL | 82.4 | 0.662 | 39 | -8 | 2.133 | 41.118 | 0.170 |  |
| 48 | Kyler Murray | QB | MIN | 82.0 | 0.659 | 100 | +52 | 16.707 | 61.210 | 0.277 | rank_delta_over_20 |
| 49 | Nico Collins | WR | HOU | 81.7 | 0.655 | 32 | -17 | 1.922 | 23.899 | 0.170 |  |
| 50 | Dallas Goedert | TE | PHI | 81.3 | 0.652 | 44 | -6 | 1.653 | 41.374 | 0.170 |  |
| 51 | Tucker Kraft | TE | GB | 80.9 | 0.651 | 33 | -18 | 0.729 | 27.510 | 0.298 | injury_status_flag |
| 52 | Chase Brown | RB | CIN | 80.5 | 0.647 | 41 | -11 | 3.091 | 26.540 | 0.234 |  |
| 53 | Bo Nix | QB | DEN | 80.1 | 0.645 | 47 | -6 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 54 | Jared Goff | QB | DET | 79.7 | 0.642 | 61 | +7 | 6.154 | 43.747 | 0.170 |  |
| 55 | Caleb Williams | QB | CHI | 79.4 | 0.637 | 51 | -4 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 56 | DeVonta Smith | WR | PHI | 79.0 | 0.631 | 46 | -10 | 1.898 | 27.685 | 0.234 |  |
| 57 | Terry McLaurin | WR | WAS | 78.6 | 0.631 | 50 | -7 | 2.339 | 29.588 | 0.170 |  |
| 58 | Joe Burrow | QB | CIN | 78.2 | 0.631 | 88 | +30 | 9.965 | 54.008 | 0.277 | rank_delta_over_20 |
| 59 | Omarion Hampton | RB | LAC | 77.8 | 0.630 | 54 | -5 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 60 | Tetairoa McMillan | WR | CAR | 77.4 | 0.630 | 35 | -25 | 1.165 | 12.564 | 1.000 | rank_delta_over_20, missing_feature_row, high_missingness, injury_status_flag |
| 61 | Jaylen Waddle | WR | DEN | 77.1 | 0.627 | 53 | -8 | 2.506 | 29.937 | 0.170 |  |
| 62 | Wan'Dale Robinson | WR | TEN | 76.7 | 0.624 | 37 | -25 | 0.951 | 13.325 | 0.170 | rank_delta_over_20 |
| 63 | Aaron Jones | RB | MIN | 76.3 | 0.621 | 112 | +49 | 12.205 | 73.871 | 0.170 | rank_delta_over_20 |
| 64 | Tyler Warren | TE | IND | 75.9 | 0.620 | 48 | -16 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness |
| 65 | Kenneth Walker III | RB | KC | 75.5 | 0.620 | 109 | +44 | 11.874 | 68.630 | 0.170 | rank_delta_over_20 |
| 66 | Malik Nabers | WR | NYG | 75.2 | 0.620 | 40 | -26 | 1.165 | 12.564 | 1.000 | rank_delta_over_20, missing_feature_row, high_missingness, injury_status_flag |
| 67 | Jaylen Warren | RB | PIT | 74.8 | 0.617 | 87 | +20 | 6.336 | 58.578 | 0.170 |  |
| 68 | Ashton Jeanty | RB | LV | 74.4 | 0.616 | 58 | -10 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 69 | Rome Odunze | WR | CHI | 74.0 | 0.614 | 43 | -26 | 1.165 | 12.564 | 1.000 | rank_delta_over_20, missing_feature_row, high_missingness |
| 70 | Hunter Henry | TE | NE | 73.6 | 0.612 | 59 | -11 | 1.594 | 39.226 | 0.234 |  |
| 71 | Tee Higgins | WR | CIN | 73.2 | 0.611 | 56 | -15 | 2.313 | 27.539 | 0.234 |  |
| 72 | Baker Mayfield | QB | TB | 72.9 | 0.609 | 84 | +12 | 7.416 | 43.724 | 0.277 |  |
| 73 | Rhamondre Stevenson | RB | NE | 72.5 | 0.609 | 104 | +31 | 9.385 | 66.299 | 0.170 | rank_delta_over_20 |
| 74 | Courtland Sutton | WR | DEN | 72.1 | 0.608 | 57 | -17 | 2.261 | 29.261 | 0.128 |  |
| 75 | Mike Evans | WR | SF | 71.7 | 0.607 | 70 | -5 | 3.292 | 41.251 | 0.234 |  |
| 76 | Tony Pollard | RB | TEN | 71.3 | 0.604 | 116 | +40 | 10.900 | 73.241 | 0.170 | rank_delta_over_20 |
| 77 | J.K. Dobbins | RB | DEN | 70.9 | 0.600 | 102 | +25 | 7.402 | 63.069 | 0.170 | rank_delta_over_20 |
| 78 | Dalton Schultz | TE | HOU | 70.6 | 0.597 | 64 | -14 | 1.251 | 34.953 | 0.234 |  |
| 79 | James Conner | RB | ARI | 70.2 | 0.593 | 125 | +46 | 11.690 | 72.404 | 0.170 | rank_delta_over_20, injury_status_flag |
| 80 | Juwan Johnson | TE | NO | 69.8 | 0.589 | 68 | -12 | 1.452 | 32.920 | 0.234 |  |
| 81 | Sam Darnold | QB | SEA | 69.4 | 0.587 | 93 | +12 | 7.403 | 37.544 | 0.277 |  |
| 82 | Jakobi Meyers | WR | JAX | 69.0 | 0.587 | 65 | -17 | 1.858 | 28.162 | 0.128 |  |
| 83 | Alec Pierce | WR | IND | 68.7 | 0.582 | 55 | -28 | 0.465 | 8.584 | 0.234 | rank_delta_over_20, injury_status_flag |
| 84 | Bucky Irving | RB | TB | 68.3 | 0.582 | 78 | -6 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 85 | Jake Ferguson | TE | DAL | 67.9 | 0.581 | 77 | -8 | 1.212 | 39.885 | 0.234 |  |
| 86 | Jayden Daniels | QB | WAS | 67.5 | 0.578 | 80 | -6 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 87 | Emeka Egbuka | WR | TB | 67.1 | 0.575 | 60 | -27 | 1.165 | 12.564 | 1.000 | rank_delta_over_20, missing_feature_row, high_missingness |
| 88 | Alvin Kamara | RB | NO | 66.7 | 0.575 | 140 | +52 | 12.833 | 78.763 | 0.170 | rank_delta_over_20 |
| 89 | Cam Skattebo | RB | NYG | 66.4 | 0.575 | 82 | -7 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 90 | Colston Loveland | TE | CHI | 66.0 | 0.568 | 72 | -18 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness |
| 91 | Mark Andrews | TE | BAL | 65.6 | 0.565 | 90 | -1 | 2.100 | 40.980 | 0.170 |  |
| 92 | Jameson Williams | WR | DET | 65.2 | 0.564 | 63 | -29 | 0.957 | 9.051 | 0.170 | rank_delta_over_20 |
| 93 | T.J. Hockenson | TE | MIN | 64.8 | 0.563 | 94 | +1 | 2.019 | 45.072 | 0.234 |  |
| 94 | Dalton Kincaid | TE | BUF | 64.5 | 0.560 | 85 | -9 | 1.127 | 35.222 | 0.298 |  |
| 95 | Jordan Addison | WR | MIN | 64.1 | 0.556 | 83 | -12 | 1.979 | 25.184 | 0.234 |  |
| 96 | DK Metcalf | WR | PIT | 63.7 | 0.556 | 86 | -10 | 2.001 | 29.192 | 0.234 |  |
| 97 | Harold Fannin Jr. | TE | CLE | 63.3 | 0.553 | 81 | -16 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 98 | Christian Watson | WR | GB | 62.9 | 0.553 | 79 | -19 | 1.798 | 18.876 | 0.170 |  |
| 99 | Quinshon Judkins | RB | CLE | 62.5 | 0.553 | 95 | -4 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 100 | Michael Wilson | WR | ARI | 62.2 | 0.552 | 76 | -24 | 1.497 | 15.155 | 0.298 | rank_delta_over_20 |

## Current Pigskin vs Overlay Top 100
| Current rank | Overlay rank | Player | Pos | Team | Current score | Overlay | Delta | Warnings |
|---|---|---|---|---|---|---|---|---|
| 1 | 27 | Jaxon Smith-Njigba | WR | SEA | 99.5 | 0.721 | -26 | rank_delta_over_20 |
| 2 | 11 | Puka Nacua | WR | LAR | 98.8 | 0.766 | -9 |  |
| 3 | 1 | Josh Allen | QB | BUF | 98.5 | 0.946 | +2 |  |
| 4 | 3 | Christian McCaffrey | RB | SF | 98.5 | 0.886 | +1 |  |
| 5 | 14 | Amon-Ra St. Brown | WR | DET | 98.0 | 0.757 | -9 |  |
| 6 | 15 | Trey McBride | TE | ARI | 98.0 | 0.750 | -9 |  |
| 7 | 13 | Ja'Marr Chase | WR | CIN | 97.5 | 0.761 | -6 |  |
| 8 | 30 | Drake London | WR | ATL | 96.2 | 0.704 | -22 | rank_delta_over_20 |
| 9 | 20 | Drake Maye | QB | NE | 96.0 | 0.734 | -11 | missing_feature_row, high_missingness |
| 10 | 5 | Patrick Mahomes | QB | KC | 95.0 | 0.814 | +5 | injury_status_flag |
| 11 | 7 | Bijan Robinson | RB | ATL | 95.0 | 0.810 | +4 |  |
| 12 | 28 | Chris Olave | WR | NO | 95.0 | 0.716 | -16 | injury_status_flag |
| 13 | 32 | Brock Bowers | TE | LV | 95.0 | 0.701 | -19 | missing_feature_row, high_missingness |
| 14 | 17 | A.J. Brown | WR | NE | 94.5 | 0.738 | -3 |  |
| 15 | 36 | Rashee Rice | WR | KC | 93.8 | 0.698 | -21 | rank_delta_over_20, injury_status_flag |
| 16 | 6 | Jahmyr Gibbs | RB | DET | 93.5 | 0.813 | +10 |  |
| 17 | 16 | Justin Jefferson | WR | MIN | 93.0 | 0.741 | +1 |  |
| 18 | 33 | Garrett Wilson | WR | NYJ | 92.5 | 0.701 | -15 |  |
| 19 | 4 | Jonathan Taylor | RB | IND | 92.0 | 0.840 | +15 |  |
| 20 | 21 | George Kittle | TE | SF | 92.0 | 0.727 | -1 | injury_status_flag |
| 21 | 39 | George Pickens | WR | DAL | 91.8 | 0.689 | -18 |  |
| 22 | 31 | Matthew Stafford | QB | LAR | 91.5 | 0.704 | -9 |  |
| 23 | 8 | De'Von Achane | RB | MIA | 91.0 | 0.796 | +15 | injury_status_flag |
| 24 | 41 | Zay Flowers | WR | BAL | 91.0 | 0.679 | -17 |  |
| 25 | 40 | Jordan Love | QB | GB | 90.0 | 0.680 | -15 |  |
| 26 | 29 | Sam LaPorta | TE | DET | 90.0 | 0.712 | -3 | injury_status_flag |
| 27 | 35 | Davante Adams | WR | LAR | 89.5 | 0.700 | -8 |  |
| 28 | 19 | Dak Prescott | QB | DAL | 89.0 | 0.734 | +9 |  |
| 29 | 34 | CeeDee Lamb | WR | DAL | 88.8 | 0.701 | -5 |  |
| 30 | 9 | Kyren Williams | RB | LAR | 88.5 | 0.783 | +21 | rank_delta_over_20 |
| 31 | 24 | Brock Purdy | QB | SF | 88.0 | 0.724 | +7 |  |
| 32 | 49 | Nico Collins | WR | HOU | 88.0 | 0.655 | -17 |  |
| 33 | 51 | Tucker Kraft | TE | GB | 88.0 | 0.651 | -18 | injury_status_flag |
| 34 | 2 | Jalen Hurts | QB | PHI | 87.5 | 0.911 | +32 | rank_delta_over_20 |
| 35 | 60 | Tetairoa McMillan | WR | CAR | 87.2 | 0.630 | -25 | rank_delta_over_20, missing_feature_row, high_missingness, injury_status_flag |
| 36 | 18 | James Cook | RB | BUF | 87.0 | 0.736 | +18 |  |
| 37 | 62 | Wan'Dale Robinson | WR | TEN | 86.5 | 0.624 | -25 | rank_delta_over_20 |
| 38 | 23 | Trevor Lawrence | QB | JAX | 86.0 | 0.727 | +15 |  |
| 39 | 47 | Kyle Pitts | TE | ATL | 86.0 | 0.662 | -8 |  |
| 40 | 66 | Malik Nabers | WR | NYG | 85.8 | 0.620 | -26 | rank_delta_over_20, missing_feature_row, high_missingness, injury_status_flag |
| 41 | 52 | Chase Brown | RB | CIN | 85.5 | 0.647 | -11 |  |
| 42 | 12 | Daniel Jones | QB | IND | 85.0 | 0.765 | +30 | rank_delta_over_20, injury_status_flag |
| 43 | 69 | Rome Odunze | WR | CHI | 85.0 | 0.614 | -26 | rank_delta_over_20, missing_feature_row, high_missingness |
| 44 | 50 | Dallas Goedert | TE | PHI | 85.0 | 0.652 | -6 |  |
| 45 | 26 | Javonte Williams | RB | DAL | 84.5 | 0.723 | +19 |  |
| 46 | 56 | DeVonta Smith | WR | PHI | 84.2 | 0.631 | -10 |  |
| 47 | 53 | Bo Nix | QB | DEN | 84.0 | 0.645 | -6 | missing_feature_row, high_missingness, injury_status_flag |
| 48 | 64 | Tyler Warren | TE | IND | 84.0 | 0.620 | -16 | missing_feature_row, high_missingness |
| 49 | 10 | Saquon Barkley | RB | PHI | 83.5 | 0.779 | +39 | rank_delta_over_20 |
| 50 | 57 | Terry McLaurin | WR | WAS | 83.5 | 0.631 | -7 |  |
| 51 | 55 | Caleb Williams | QB | CHI | 83.0 | 0.637 | -4 | missing_feature_row, high_missingness |
| 52 | 46 | Travis Kelce | TE | KC | 83.0 | 0.663 | +6 |  |
| 53 | 61 | Jaylen Waddle | WR | DEN | 82.8 | 0.627 | -8 |  |
| 54 | 59 | Omarion Hampton | RB | LAC | 82.0 | 0.630 | -5 | missing_feature_row, high_missingness |
| 55 | 83 | Alec Pierce | WR | IND | 82.0 | 0.582 | -28 | rank_delta_over_20, injury_status_flag |
| 56 | 71 | Tee Higgins | WR | CIN | 81.2 | 0.611 | -15 |  |
| 57 | 74 | Courtland Sutton | WR | DEN | 80.5 | 0.608 | -17 |  |
| 58 | 68 | Ashton Jeanty | RB | LV | 80.0 | 0.616 | -10 | missing_feature_row, high_missingness |
| 59 | 70 | Hunter Henry | TE | NE | 80.0 | 0.612 | -11 |  |
| 60 | 87 | Emeka Egbuka | WR | TB | 79.8 | 0.575 | -27 | rank_delta_over_20, missing_feature_row, high_missingness |
| 61 | 54 | Jared Goff | QB | DET | 79.5 | 0.642 | +7 |  |
| 62 | 25 | Josh Jacobs | RB | GB | 79.0 | 0.723 | +37 | rank_delta_over_20 |
| 63 | 92 | Jameson Williams | WR | DET | 79.0 | 0.564 | -29 | rank_delta_over_20 |
| 64 | 78 | Dalton Schultz | TE | HOU | 79.0 | 0.597 | -14 |  |
| 65 | 82 | Jakobi Meyers | WR | JAX | 78.2 | 0.587 | -17 |  |
| 66 | 45 | C.J. Stroud | QB | HOU | 78.0 | 0.667 | +21 | rank_delta_over_20 |
| 67 | 37 | Travis Etienne | RB | NO | 78.0 | 0.697 | +30 | rank_delta_over_20 |
| 68 | 80 | Juwan Johnson | TE | NO | 78.0 | 0.589 | -12 |  |
| 69 | 44 | D'Andre Swift | RB | CHI | 77.5 | 0.670 | +25 | rank_delta_over_20 |
| 70 | 75 | Mike Evans | WR | SF | 77.5 | 0.607 | -5 |  |
| 71 | 42 | Justin Herbert | QB | LAC | 77.0 | 0.678 | +29 | rank_delta_over_20 |
| 72 | 90 | Colston Loveland | TE | CHI | 77.0 | 0.568 | -18 | missing_feature_row, high_missingness |
| 73 | 102 | Quentin Johnston | WR | LAC | 76.8 | 0.545 | -29 | rank_delta_over_20 |
| 74 | 38 | Breece Hall | RB | NYJ | 76.5 | 0.692 | +36 | rank_delta_over_20 |
| 75 | 22 | Lamar Jackson | QB | BAL | 76.0 | 0.727 | +53 | rank_delta_over_20 |
| 76 | 100 | Michael Wilson | WR | ARI | 76.0 | 0.552 | -24 | rank_delta_over_20 |
| 77 | 85 | Jake Ferguson | TE | DAL | 76.0 | 0.581 | -8 |  |
| 78 | 84 | Bucky Irving | RB | TB | 75.5 | 0.582 | -6 | missing_feature_row, high_missingness, injury_status_flag |
| 79 | 98 | Christian Watson | WR | GB | 75.2 | 0.553 | -19 |  |
| 80 | 86 | Jayden Daniels | QB | WAS | 75.0 | 0.578 | -6 | missing_feature_row, high_missingness |
| 81 | 97 | Harold Fannin Jr. | TE | CLE | 75.0 | 0.553 | -16 | missing_feature_row, high_missingness, injury_status_flag |
| 82 | 89 | Cam Skattebo | RB | NYG | 74.5 | 0.575 | -7 | missing_feature_row, high_missingness |
| 83 | 95 | Jordan Addison | WR | MIN | 74.5 | 0.556 | -12 |  |
| 84 | 72 | Baker Mayfield | QB | TB | 74.0 | 0.609 | +12 |  |
| 85 | 94 | Dalton Kincaid | TE | BUF | 74.0 | 0.560 | -9 |  |
| 86 | 96 | DK Metcalf | WR | PIT | 73.8 | 0.556 | -10 |  |
| 87 | 67 | Jaylen Warren | RB | PIT | 73.5 | 0.617 | +20 |  |
| 88 | 58 | Joe Burrow | QB | CIN | 73.0 | 0.631 | +30 | rank_delta_over_20 |
| 89 | 105 | Ladd McConkey | WR | LAC | 73.0 | 0.525 | -16 | missing_feature_row, high_missingness |
| 90 | 91 | Mark Andrews | TE | BAL | 73.0 | 0.565 | -1 |  |
| 91 | 43 | Derrick Henry | RB | BAL | 72.5 | 0.675 | +48 | rank_delta_over_20 |
| 92 | 106 | Romeo Doubs | WR | NE | 72.2 | 0.524 | -14 |  |
| 93 | 81 | Sam Darnold | QB | SEA | 72.0 | 0.587 | +12 |  |
| 94 | 93 | T.J. Hockenson | TE | MIN | 72.0 | 0.563 | +1 |  |
| 95 | 99 | Quinshon Judkins | RB | CLE | 71.5 | 0.553 | -4 | missing_feature_row, high_missingness, injury_status_flag |
| 96 | 108 | Jauan Jennings | WR | MIN | 71.5 | 0.505 | -12 |  |
| 97 | 101 | Jaxson Dart | QB | NYG | 71.0 | 0.548 | -4 | missing_feature_row, high_missingness |
| 98 | 113 | Tre Tucker | WR | LV | 70.8 | 0.499 | -15 |  |
| 99 | 104 | Rico Dowdle | RB | PIT | 70.5 | 0.540 | -5 |  |
| 100 | 48 | Kyler Murray | QB | MIN | 70.0 | 0.659 | +52 | rank_delta_over_20 |

## QB45 Overlay Board
| Rank | Player | Pos | Team | DPI | Overlay | Current rank | Delta | VOR | Signal | Miss | Warnings |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Josh Allen | QB | BUF | 100.0 | 0.946 | 3 | +2 | 24.707 | 82.425 | 0.277 |  |
| 2 | Jalen Hurts | QB | PHI | 99.6 | 0.911 | 34 | +32 | 31.411 | 85.901 | 0.170 | rank_delta_over_20 |
| 5 | Patrick Mahomes | QB | KC | 98.5 | 0.814 | 10 | +5 | 11.480 | 63.258 | 0.170 | injury_status_flag |
| 12 | Daniel Jones | QB | IND | 95.8 | 0.765 | 42 | +30 | 16.737 | 56.940 | 0.277 | rank_delta_over_20, injury_status_flag |
| 19 | Dak Prescott | QB | DAL | 93.1 | 0.734 | 28 | +9 | 8.588 | 48.992 | 0.277 |  |
| 20 | Drake Maye | QB | NE | 92.7 | 0.734 | 9 | -11 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 22 | Lamar Jackson | QB | BAL | 92.0 | 0.727 | 75 | +53 | 16.955 | 78.898 | 0.170 | rank_delta_over_20 |
| 23 | Trevor Lawrence | QB | JAX | 91.6 | 0.727 | 38 | +15 | 11.218 | 47.581 | 0.277 |  |
| 24 | Brock Purdy | QB | SF | 91.2 | 0.724 | 31 | +7 | 9.257 | 43.460 | 0.277 |  |
| 31 | Matthew Stafford | QB | LAR | 88.5 | 0.704 | 22 | -9 | 3.999 | 32.405 | 0.170 |  |
| 40 | Jordan Love | QB | GB | 85.1 | 0.680 | 25 | -15 | 3.851 | 22.503 | 0.277 |  |
| 42 | Justin Herbert | QB | LAC | 84.3 | 0.678 | 71 | +29 | 11.996 | 58.004 | 0.170 | rank_delta_over_20 |
| 45 | C.J. Stroud | QB | HOU | 83.2 | 0.667 | 66 | +21 | 10.965 | 48.738 | 0.234 | rank_delta_over_20 |
| 48 | Kyler Murray | QB | MIN | 82.0 | 0.659 | 100 | +52 | 16.707 | 61.210 | 0.277 | rank_delta_over_20 |
| 53 | Bo Nix | QB | DEN | 80.1 | 0.645 | 47 | -6 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 54 | Jared Goff | QB | DET | 79.7 | 0.642 | 61 | +7 | 6.154 | 43.747 | 0.170 |  |
| 55 | Caleb Williams | QB | CHI | 79.4 | 0.637 | 51 | -4 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 58 | Joe Burrow | QB | CIN | 78.2 | 0.631 | 88 | +30 | 9.965 | 54.008 | 0.277 | rank_delta_over_20 |
| 72 | Baker Mayfield | QB | TB | 72.9 | 0.609 | 84 | +12 | 7.416 | 43.724 | 0.277 |  |
| 81 | Sam Darnold | QB | SEA | 69.4 | 0.587 | 93 | +12 | 7.403 | 37.544 | 0.277 |  |
| 86 | Jayden Daniels | QB | WAS | 67.5 | 0.578 | 80 | -6 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 101 | Jaxson Dart | QB | NYG | 61.8 | 0.548 | 97 | -4 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 103 | Jacoby Brissett | QB | ARI | 61.0 | 0.542 | 106 | +3 | 7.257 | 25.848 | 0.277 |  |
| 107 | Tua Tagovailoa | QB | ATL | 59.5 | 0.515 | 130 | +23 | 6.943 | 41.667 | 0.277 | rank_delta_over_20 |
| 112 | Aaron Rodgers | QB | PIT | 57.6 | 0.500 | 114 | +2 | 3.073 | 24.731 | 0.277 |  |
| 116 | Tyler Shough | QB | NO | 56.0 | 0.497 | 122 | +6 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 124 | Malik Willis | QB | MIA | 53.0 | 0.485 | 118 | -6 | 3.931 | 14.719 | 0.277 |  |
| 126 | Bryce Young | QB | CAR | 52.2 | 0.481 | 136 | +10 | 7.107 | 25.211 | 0.340 |  |
| 140 | Shedeur Sanders | QB | CLE | 46.9 | 0.452 | 143 | +3 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 151 | Cam Ward | QB | TEN | 42.7 | 0.430 | 154 | +3 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 154 | Geno Smith | QB | NYJ | 41.5 | 0.424 | 171 | +17 | 6.137 | 44.135 | 0.170 |  |
| 184 | Tyler Huntley | QB | BAL | 30.1 | 0.342 | 222 | +38 | 16.317 | 46.416 | 0.277 | rank_delta_over_20 |
| 190 | Fernando Mendoza | QB | LV | 27.8 | 0.319 | 195 | +5 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 191 | Justin Fields | QB | KC | 27.4 | 0.310 | 239 | +48 | 17.108 | 64.001 | 0.277 | rank_delta_over_20 |
| 198 | Carson Wentz | QB | MIN | 24.7 | 0.297 | 225 | +27 | 11.748 | 44.504 | 0.277 | rank_delta_over_20 |
| 201 | Mac Jones | QB | SF | 23.6 | 0.286 | 208 | +7 | 4.472 | 30.581 | 0.277 | injury_status_flag |
| 212 | Marcus Mariota | QB | WAS | 19.3 | 0.254 | 233 | +21 | 8.640 | 43.997 | 0.277 | rank_delta_over_20 |
| 216 | Jameis Winston | QB | NYG | 17.8 | 0.246 | 214 | -2 | 2.450 | 20.460 | 0.277 |  |
| 242 | Spencer Rattler | QB | NO | 7.9 | 0.171 | 242 | +0 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 247 | Davis Mills | QB | HOU | 6.0 | 0.136 | 245 | -2 | 2.672 | 20.395 | 0.277 |  |
| 248 | J.J. McCarthy | QB | MIN | 5.6 | 0.134 | 249 | +1 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 253 | Quinn Ewers | QB | MIA | 3.7 | 0.111 | 253 | +0 | 2.218 | 38.553 | 1.000 | missing_feature_row, high_missingness |
| 257 | Jake Browning | QB | TB | 2.1 | 0.093 | 259 | +2 | 6.565 | 25.779 | 0.170 |  |
| 259 | Josh Johnson | QB | CIN | 1.4 | 0.061 | 256 | -3 | 1.810 | 11.491 | 0.298 |  |
| 260 | Joe Flacco | QB | CIN | 1.0 | 0.059 | 260 | +0 | 3.555 | 31.654 | 0.191 |  |

## RB80 Overlay Board
| Rank | Player | Pos | Team | DPI | Overlay | Current rank | Delta | VOR | Signal | Miss | Warnings |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | Christian McCaffrey | RB | SF | 99.2 | 0.886 | 4 | +1 | 15.346 | 81.006 | 0.128 |  |
| 4 | Jonathan Taylor | RB | IND | 98.9 | 0.840 | 19 | +15 | 15.449 | 81.897 | 0.170 |  |
| 6 | Jahmyr Gibbs | RB | DET | 98.1 | 0.813 | 16 | +10 | 11.547 | 71.082 | 0.234 |  |
| 7 | Bijan Robinson | RB | ATL | 97.7 | 0.810 | 11 | +4 | 9.450 | 70.009 | 0.234 |  |
| 8 | De'Von Achane | RB | MIA | 97.3 | 0.796 | 23 | +15 | 11.683 | 71.721 | 0.213 | injury_status_flag |
| 9 | Kyren Williams | RB | LAR | 96.9 | 0.783 | 30 | +21 | 12.232 | 73.101 | 0.170 | rank_delta_over_20 |
| 10 | Saquon Barkley | RB | PHI | 96.6 | 0.779 | 49 | +39 | 15.474 | 84.003 | 0.149 | rank_delta_over_20 |
| 18 | James Cook | RB | BUF | 93.5 | 0.736 | 36 | +18 | 8.329 | 63.502 | 0.170 |  |
| 25 | Josh Jacobs | RB | GB | 90.8 | 0.723 | 62 | +37 | 13.284 | 76.421 | 0.149 | rank_delta_over_20 |
| 26 | Javonte Williams | RB | DAL | 90.4 | 0.723 | 45 | +19 | 8.930 | 65.075 | 0.170 |  |
| 37 | Travis Etienne | RB | NO | 86.2 | 0.697 | 67 | +30 | 10.722 | 74.056 | 0.170 | rank_delta_over_20 |
| 38 | Breece Hall | RB | NYJ | 85.9 | 0.692 | 74 | +36 | 11.498 | 75.245 | 0.170 | rank_delta_over_20 |
| 43 | Derrick Henry | RB | BAL | 83.9 | 0.675 | 91 | +48 | 13.383 | 75.852 | 0.128 | rank_delta_over_20 |
| 44 | D'Andre Swift | RB | CHI | 83.6 | 0.670 | 69 | +25 | 9.480 | 61.659 | 0.128 | rank_delta_over_20 |
| 52 | Chase Brown | RB | CIN | 80.5 | 0.647 | 41 | -11 | 3.091 | 26.540 | 0.234 |  |
| 59 | Omarion Hampton | RB | LAC | 77.8 | 0.630 | 54 | -5 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 63 | Aaron Jones | RB | MIN | 76.3 | 0.621 | 112 | +49 | 12.205 | 73.871 | 0.170 | rank_delta_over_20 |
| 65 | Kenneth Walker III | RB | KC | 75.5 | 0.620 | 109 | +44 | 11.874 | 68.630 | 0.170 | rank_delta_over_20 |
| 67 | Jaylen Warren | RB | PIT | 74.8 | 0.617 | 87 | +20 | 6.336 | 58.578 | 0.170 |  |
| 68 | Ashton Jeanty | RB | LV | 74.4 | 0.616 | 58 | -10 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 73 | Rhamondre Stevenson | RB | NE | 72.5 | 0.609 | 104 | +31 | 9.385 | 66.299 | 0.170 | rank_delta_over_20 |
| 76 | Tony Pollard | RB | TEN | 71.3 | 0.604 | 116 | +40 | 10.900 | 73.241 | 0.170 | rank_delta_over_20 |
| 77 | J.K. Dobbins | RB | DEN | 70.9 | 0.600 | 102 | +25 | 7.402 | 63.069 | 0.170 | rank_delta_over_20 |
| 79 | James Conner | RB | ARI | 70.2 | 0.593 | 125 | +46 | 11.690 | 72.404 | 0.170 | rank_delta_over_20, injury_status_flag |
| 84 | Bucky Irving | RB | TB | 68.3 | 0.582 | 78 | -6 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 88 | Alvin Kamara | RB | NO | 66.7 | 0.575 | 140 | +52 | 12.833 | 78.763 | 0.170 | rank_delta_over_20 |
| 89 | Cam Skattebo | RB | NYG | 66.4 | 0.575 | 82 | -7 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 99 | Quinshon Judkins | RB | CLE | 62.5 | 0.553 | 95 | -4 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 104 | Rico Dowdle | RB | PIT | 60.6 | 0.540 | 99 | -5 | 2.391 | 33.767 | 0.191 |  |
| 110 | TreVeyon Henderson | RB | NE | 58.3 | 0.501 | 121 | +11 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 111 | David Montgomery | RB | HOU | 58.0 | 0.501 | 165 | +54 | 11.654 | 66.391 | 0.128 | rank_delta_over_20 |
| 118 | Zach Charbonnet | RB | SEA | 55.3 | 0.494 | 128 | +10 | 4.745 | 32.975 | 0.234 | injury_status_flag |
| 119 | Isiah Pacheco | RB | DET | 54.9 | 0.493 | 172 | +53 | 11.338 | 74.107 | 0.170 | rank_delta_over_20 |
| 128 | Kenneth Gainwell | RB | TB | 51.5 | 0.480 | 137 | +9 | 4.691 | 36.403 | 0.128 |  |
| 132 | Rachaad White | RB | WAS | 49.9 | 0.471 | 169 | +37 | 7.887 | 67.076 | 0.170 | rank_delta_over_20 |
| 138 | Tyrone Tracy Jr. | RB | NYG | 47.6 | 0.453 | 144 | +6 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 143 | Woody Marks | RB | HOU | 45.7 | 0.445 | 148 | +5 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 147 | RJ Harvey | RB | DEN | 44.2 | 0.438 | 151 | +4 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 150 | Trey Benson | RB | ARI | 43.0 | 0.430 | 155 | +5 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 152 | Chuba Hubbard | RB | CAR | 42.3 | 0.429 | 174 | +22 | 6.907 | 50.168 | 0.170 | rank_delta_over_20 |
| 155 | Kimani Vidal | RB | LAC | 41.1 | 0.423 | 159 | +4 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 160 | Kyle Monangai | RB | CHI | 39.2 | 0.416 | 162 | +2 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 169 | Tyjae Spears | RB | TEN | 35.8 | 0.394 | 177 | +8 | 4.815 | 38.043 | 0.234 |  |
| 170 | Tyler Allgeier | RB | ARI | 35.4 | 0.388 | 191 | +21 | 8.560 | 50.620 | 0.170 | rank_delta_over_20 |
| 173 | Michael Carter | RB | TEN | 34.3 | 0.373 | 179 | +6 | 4.187 | 30.474 | 0.170 |  |
| 177 | Jacory Croskey-Merritt | RB | WAS | 32.7 | 0.364 | 181 | +4 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 180 | Jawhar Jordan | RB | HOU | 31.6 | 0.349 | 186 | +6 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 182 | Devin Singletary | RB | NYG | 30.8 | 0.345 | 199 | +17 | 6.343 | 44.951 | 0.128 |  |
| 183 | Jordan Mason | RB | MIN | 30.4 | 0.343 | 184 | +1 | 2.120 | 28.691 | 0.170 |  |
| 185 | Chris Rodriguez Jr. | RB | JAX | 29.7 | 0.336 | 188 | +3 | 2.905 | 31.343 | 0.234 | injury_status_flag |
| 188 | Blake Corum | RB | LAR | 28.5 | 0.327 | 193 | +5 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 189 | Raheim Sanders | RB | CLE | 28.1 | 0.319 | 196 | +7 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 196 | Devin Neal | RB | NO | 25.5 | 0.304 | 201 | +5 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 202 | Jaylen Wright | RB | MIA | 23.2 | 0.282 | 209 | +7 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 203 | Emanuel Wilson | RB | SEA | 22.8 | 0.281 | 203 | +0 | 2.962 | 21.936 | 0.298 |  |
| 205 | Samaje Perine | RB | CIN | 22.0 | 0.278 | 206 | +1 | 3.150 | 24.478 | 0.170 |  |
| 207 | Phil Mafah | RB | DAL | 21.3 | 0.275 | 211 | +4 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 209 | Dylan Sampson | RB | CLE | 20.5 | 0.267 | 215 | +6 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 213 | Bhayshul Tuten | RB | JAX | 19.0 | 0.253 | 219 | +6 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 217 | Ty Johnson | RB | BUF | 17.4 | 0.246 | 217 | +0 | 2.893 | 24.145 | 0.234 |  |
| 222 | Brian Robinson | RB | ATL | 15.5 | 0.234 | 244 | +22 | 8.421 | 65.102 | 0.170 | rank_delta_over_20 |
| 223 | Justice Hill | RB | BAL | 15.1 | 0.232 | 226 | +3 | 4.090 | 30.416 | 0.170 |  |
| 227 | Keaton Mitchell | RB | LAC | 13.6 | 0.207 | 238 | +11 | 5.412 | 33.507 | 0.298 |  |
| 228 | Jaret Patterson | RB | LAC | 13.2 | 0.205 | 229 | +1 | 2.548 | 22.778 | 0.234 |  |
| 231 | Kendre Miller | RB | NO | 12.1 | 0.202 | 231 | +0 | 2.521 | 26.134 | 0.234 | injury_status_flag |
| 232 | Braelon Allen | RB | NYJ | 11.7 | 0.201 | 237 | +5 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 234 | Jeremy McNichols | RB | WAS | 10.9 | 0.187 | 234 | +0 | 1.889 | 23.552 | 0.255 |  |
| 236 | Emari Demercado | RB | KC | 10.2 | 0.179 | 240 | +4 | 2.522 | 31.555 | 0.234 |  |
| 237 | Jaydon Blue | RB | DAL | 9.8 | 0.179 | 241 | +4 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 238 | Jerome Ford | RB | WAS | 9.4 | 0.177 | 248 | +10 | 5.288 | 52.303 | 0.170 |  |
| 241 | Isaiah Davis | RB | NYJ | 8.3 | 0.171 | 243 | +2 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 245 | Brashard Smith | RB | KC | 6.7 | 0.149 | 247 | +2 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 249 | Malik Davis | RB | DAL | 5.2 | 0.133 | 250 | +1 | 3.739 | 30.269 | 0.234 |  |
| 250 | Sean Tucker | RB | TB | 4.8 | 0.124 | 246 | -4 | 0.739 | 20.217 | 0.298 |  |
| 251 | DJ Giddens | RB | IND | 4.4 | 0.119 | 252 | +1 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 252 | Ray Davis | RB | BUF | 4.1 | 0.112 | 254 | +2 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 254 | Zavier Scott | RB | MIN | 3.3 | 0.104 | 255 | +1 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 255 | Tank Bigsby | RB | PHI | 2.9 | 0.102 | 251 | -4 | 2.161 | 19.460 | 0.234 |  |
| 256 | Terrell Jennings | RB | NE | 2.5 | 0.097 | 257 | +1 | 2.451 | 37.776 | 1.000 | missing_feature_row, high_missingness |
| 258 | Jaleel McLaughlin | RB | DEN | 1.8 | 0.089 | 258 | +0 | 3.799 | 30.257 | 0.298 |  |

## WR100 Overlay Board
| Rank | Player | Pos | Team | DPI | Overlay | Current rank | Delta | VOR | Signal | Miss | Warnings |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 11 | Puka Nacua | WR | LAR | 96.2 | 0.766 | 2 | -9 | 3.115 | 43.301 | 0.234 |  |
| 13 | Ja'Marr Chase | WR | CIN | 95.4 | 0.761 | 7 | -6 | 3.580 | 44.941 | 0.128 |  |
| 14 | Amon-Ra St. Brown | WR | DET | 95.0 | 0.757 | 5 | -9 | 3.015 | 41.632 | 0.149 |  |
| 16 | Justin Jefferson | WR | MIN | 94.3 | 0.741 | 17 | +1 | 4.327 | 51.815 | 0.128 |  |
| 17 | A.J. Brown | WR | NE | 93.9 | 0.738 | 14 | -3 | 3.454 | 44.652 | 0.234 |  |
| 27 | Jaxon Smith-Njigba | WR | SEA | 90.1 | 0.721 | 1 | -26 | 0.896 | 13.721 | 0.298 | rank_delta_over_20 |
| 28 | Chris Olave | WR | NO | 89.7 | 0.716 | 12 | -16 | 2.277 | 30.018 | 0.234 | injury_status_flag |
| 30 | Drake London | WR | ATL | 88.9 | 0.704 | 8 | -22 | 1.233 | 18.139 | 0.191 | rank_delta_over_20 |
| 33 | Garrett Wilson | WR | NYJ | 87.8 | 0.701 | 18 | -15 | 2.067 | 33.671 | 0.128 |  |
| 34 | CeeDee Lamb | WR | DAL | 87.4 | 0.701 | 29 | -5 | 3.895 | 46.620 | 0.128 |  |
| 35 | Davante Adams | WR | LAR | 87.0 | 0.700 | 27 | -8 | 3.522 | 43.646 | 0.149 |  |
| 36 | Rashee Rice | WR | KC | 86.6 | 0.698 | 15 | -21 | 1.713 | 25.146 | 0.234 | rank_delta_over_20, injury_status_flag |
| 39 | George Pickens | WR | DAL | 85.5 | 0.689 | 21 | -18 | 2.276 | 27.289 | 0.170 |  |
| 41 | Zay Flowers | WR | BAL | 84.7 | 0.679 | 24 | -17 | 1.957 | 25.853 | 0.234 |  |
| 49 | Nico Collins | WR | HOU | 81.7 | 0.655 | 32 | -17 | 1.922 | 23.899 | 0.170 |  |
| 56 | DeVonta Smith | WR | PHI | 79.0 | 0.631 | 46 | -10 | 1.898 | 27.685 | 0.234 |  |
| 57 | Terry McLaurin | WR | WAS | 78.6 | 0.631 | 50 | -7 | 2.339 | 29.588 | 0.170 |  |
| 60 | Tetairoa McMillan | WR | CAR | 77.4 | 0.630 | 35 | -25 | 1.165 | 12.564 | 1.000 | rank_delta_over_20, missing_feature_row, high_missingness, injury_status_flag |
| 61 | Jaylen Waddle | WR | DEN | 77.1 | 0.627 | 53 | -8 | 2.506 | 29.937 | 0.170 |  |
| 62 | Wan'Dale Robinson | WR | TEN | 76.7 | 0.624 | 37 | -25 | 0.951 | 13.325 | 0.170 | rank_delta_over_20 |
| 66 | Malik Nabers | WR | NYG | 75.2 | 0.620 | 40 | -26 | 1.165 | 12.564 | 1.000 | rank_delta_over_20, missing_feature_row, high_missingness, injury_status_flag |
| 69 | Rome Odunze | WR | CHI | 74.0 | 0.614 | 43 | -26 | 1.165 | 12.564 | 1.000 | rank_delta_over_20, missing_feature_row, high_missingness |
| 71 | Tee Higgins | WR | CIN | 73.2 | 0.611 | 56 | -15 | 2.313 | 27.539 | 0.234 |  |
| 74 | Courtland Sutton | WR | DEN | 72.1 | 0.608 | 57 | -17 | 2.261 | 29.261 | 0.128 |  |
| 75 | Mike Evans | WR | SF | 71.7 | 0.607 | 70 | -5 | 3.292 | 41.251 | 0.234 |  |
| 82 | Jakobi Meyers | WR | JAX | 69.0 | 0.587 | 65 | -17 | 1.858 | 28.162 | 0.128 |  |
| 83 | Alec Pierce | WR | IND | 68.7 | 0.582 | 55 | -28 | 0.465 | 8.584 | 0.234 | rank_delta_over_20, injury_status_flag |
| 87 | Emeka Egbuka | WR | TB | 67.1 | 0.575 | 60 | -27 | 1.165 | 12.564 | 1.000 | rank_delta_over_20, missing_feature_row, high_missingness |
| 92 | Jameson Williams | WR | DET | 65.2 | 0.564 | 63 | -29 | 0.957 | 9.051 | 0.170 | rank_delta_over_20 |
| 95 | Jordan Addison | WR | MIN | 64.1 | 0.556 | 83 | -12 | 1.979 | 25.184 | 0.234 |  |
| 96 | DK Metcalf | WR | PIT | 63.7 | 0.556 | 86 | -10 | 2.001 | 29.192 | 0.234 |  |
| 98 | Christian Watson | WR | GB | 62.9 | 0.553 | 79 | -19 | 1.798 | 18.876 | 0.170 |  |
| 100 | Michael Wilson | WR | ARI | 62.2 | 0.552 | 76 | -24 | 1.497 | 15.155 | 0.298 | rank_delta_over_20 |
| 102 | Quentin Johnston | WR | LAC | 61.4 | 0.545 | 73 | -29 | 0.533 | 9.374 | 0.234 | rank_delta_over_20 |
| 105 | Ladd McConkey | WR | LAC | 60.2 | 0.525 | 89 | -16 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 106 | Romeo Doubs | WR | NE | 59.9 | 0.524 | 92 | -14 | 1.191 | 16.488 | 0.128 |  |
| 108 | Jauan Jennings | WR | MIN | 59.1 | 0.505 | 96 | -12 | 0.647 | 8.438 | 0.128 |  |
| 113 | Tre Tucker | WR | LV | 57.2 | 0.499 | 98 | -15 | 0.575 | 7.672 | 0.234 |  |
| 114 | Jerry Jeudy | WR | CLE | 56.8 | 0.498 | 108 | -6 | 1.542 | 20.166 | 0.170 | injury_status_flag |
| 115 | Ricky Pearsall | WR | SF | 56.4 | 0.497 | 103 | -12 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 117 | Calvin Ridley | WR | TEN | 55.7 | 0.495 | 117 | +0 | 2.047 | 29.240 | 0.170 |  |
| 120 | Troy Franklin | WR | DEN | 54.5 | 0.491 | 105 | -15 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 121 | Parker Washington | WR | JAX | 54.1 | 0.491 | 101 | -20 | 0.358 | 6.941 | 0.298 |  |
| 127 | Elic Ayomanor | WR | TEN | 51.8 | 0.480 | 110 | -17 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 130 | Darius Slayton | WR | NYG | 50.7 | 0.474 | 113 | -17 | 1.027 | 12.563 | 0.170 | injury_status_flag |
| 134 | Darnell Mooney | WR | NYG | 49.2 | 0.460 | 123 | -11 | 0.934 | 14.952 | 0.170 |  |
| 135 | Khalil Shakir | WR | BUF | 48.8 | 0.458 | 120 | -15 | 0.887 | 9.067 | 0.170 |  |
| 136 | Michael Pittman | WR | PIT | 48.4 | 0.455 | 139 | +3 | 2.193 | 31.986 | 0.170 |  |
| 139 | Keon Coleman | WR | BUF | 47.3 | 0.452 | 126 | -13 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 141 | Brian Thomas Jr. | WR | JAX | 46.5 | 0.447 | 129 | -12 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 145 | Xavier Worthy | WR | KC | 45.0 | 0.442 | 132 | -13 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 148 | Travis Hunter | WR | JAX | 43.8 | 0.436 | 133 | -15 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 153 | Jayden Reed | WR | GB | 41.9 | 0.425 | 147 | -6 | 2.108 | 21.766 | 0.234 |  |
| 157 | Mack Hollins | WR | NE | 40.4 | 0.421 | 135 | -22 | 0.546 | 8.669 | 0.128 | rank_delta_over_20 |
| 158 | Cooper Kupp | WR | SEA | 40.0 | 0.421 | 158 | +0 | 2.878 | 32.834 | 0.128 |  |
| 159 | Jakobie Keeney-James | WR | GB | 39.6 | 0.420 | 142 | -17 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 161 | Chris Godwin Jr. | WR | TB | 38.8 | 0.414 | 161 | +0 | 2.158 | 34.957 | 0.128 |  |
| 163 | Jalen Coker | WR | CAR | 38.1 | 0.403 | 150 | -13 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 165 | Josh Downs | WR | IND | 37.3 | 0.399 | 153 | -12 | 1.102 | 14.529 | 0.298 |  |
| 167 | Kayshon Boutte | WR | NE | 36.5 | 0.398 | 145 | -22 | 0.132 | 5.187 | 0.362 | rank_delta_over_20 |
| 168 | Rashid Shaheed | WR | SEA | 36.2 | 0.396 | 156 | -12 | 1.598 | 14.210 | 0.170 |  |
| 172 | Jalen McMillan | WR | TB | 34.6 | 0.375 | 164 | -8 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 174 | Devaughn Vele | WR | NO | 33.9 | 0.369 | 166 | -8 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 175 | Marquise Brown | WR | PHI | 33.5 | 0.369 | 168 | -7 | 1.177 | 17.137 | 0.170 |  |
| 176 | DJ Moore | WR | BUF | 33.1 | 0.368 | 176 | +0 | 1.964 | 30.208 | 0.128 |  |
| 178 | Xavier Legette | WR | CAR | 32.3 | 0.353 | 173 | -5 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 179 | Van Jefferson | WR | WAS | 32.0 | 0.352 | 170 | -9 | 0.716 | 10.085 | 0.170 |  |
| 181 | Jayden Higgins | WR | HOU | 31.2 | 0.347 | 175 | -6 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 186 | Adonai Mitchell | WR | NYJ | 29.3 | 0.336 | 178 | -8 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 187 | Theo Wease Jr. | WR | MIA | 28.9 | 0.331 | 180 | -7 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 192 | Tyquan Thornton | WR | KC | 27.0 | 0.309 | 182 | -10 | -0.025 | 5.884 | 0.170 |  |
| 193 | Chimere Dike | WR | TEN | 26.6 | 0.309 | 187 | -6 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 194 | Andrei Iosivas | WR | CIN | 26.2 | 0.308 | 183 | -11 | 0.407 | 7.611 | 0.298 |  |
| 195 | Olamide Zaccheaus | WR | ATL | 25.8 | 0.305 | 185 | -10 | 0.742 | 8.010 | 0.170 |  |
| 197 | Kendrick Bourne | WR | ARI | 25.1 | 0.301 | 189 | -8 | 0.996 | 11.747 | 0.128 |  |
| 199 | Malik Washington | WR | MIA | 24.3 | 0.297 | 190 | -9 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 200 | Ryan Flournoy | WR | DAL | 23.9 | 0.291 | 192 | -8 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 204 | Pat Bryant | WR | DEN | 22.4 | 0.280 | 197 | -7 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 206 | Dontayvion Wicks | WR | PHI | 21.6 | 0.275 | 198 | -8 | 1.278 | 12.307 | 0.191 |  |
| 208 | Calvin Austin III | WR | NYG | 20.9 | 0.274 | 194 | -14 | 0.348 | 6.351 | 0.234 |  |
| 210 | Rashod Bateman | WR | BAL | 20.1 | 0.262 | 202 | -8 | 1.029 | 11.478 | 0.170 | injury_status_flag |
| 211 | Matthew Golden | WR | GB | 19.7 | 0.258 | 204 | -7 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 214 | Xavier Hutchinson | WR | HOU | 18.6 | 0.252 | 200 | -14 | -0.102 | 4.533 | 0.298 |  |
| 215 | Tory Horton | WR | SEA | 18.2 | 0.247 | 207 | -8 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 218 | Tez Johnson | WR | TB | 17.1 | 0.242 | 210 | -8 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 219 | Jalen Nailor | WR | LV | 16.7 | 0.240 | 205 | -14 | 0.353 | 6.496 | 0.234 |  |
| 220 | Christian Kirk | WR | SF | 16.3 | 0.239 | 216 | -4 | 1.666 | 21.628 | 0.128 |  |
| 221 | Luther Burden III | WR | CHI | 15.9 | 0.236 | 212 | -9 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 224 | DeMario Douglas | WR | NE | 14.8 | 0.226 | 213 | -11 | 0.478 | 12.685 | 0.234 |  |
| 225 | Isaiah Bond | WR | CLE | 14.4 | 0.220 | 218 | -7 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 226 | Tre Harris | WR | LAC | 14.0 | 0.208 | 221 | -5 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 229 | Treylon Burks | WR | WAS | 12.8 | 0.205 | 220 | -9 | 0.426 | 9.171 | 0.170 |  |
| 230 | Isaac TeSlaa | WR | DET | 12.5 | 0.203 | 223 | -7 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 233 | Casey Washington | WR | ATL | 11.3 | 0.197 | 224 | -9 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 235 | Marquez Valdes-Scantling | WR | DAL | 10.6 | 0.184 | 227 | -8 | 0.713 | 8.975 | 0.170 |  |
| 239 | Devontez Walker | WR | BAL | 9.0 | 0.175 | 232 | -7 | 1.165 | 12.564 | 1.000 | missing_feature_row, high_missingness |
| 240 | Cedric Tillman | WR | CLE | 8.6 | 0.172 | 228 | -12 | -0.059 | 7.429 | 0.234 |  |
| 243 | Jalen Tolbert | WR | MIA | 7.5 | 0.165 | 230 | -13 | 0.177 | 4.877 | 0.234 |  |
| 244 | Lil'Jordan Humphrey | WR | DEN | 7.1 | 0.158 | 235 | -9 | 0.447 | 7.194 | 0.234 |  |
| 246 | John Metchie III | WR | CAR | 6.4 | 0.142 | 236 | -10 | -0.561 | 4.133 | 0.234 |  |

## TE35 Overlay Board
| Rank | Player | Pos | Team | DPI | Overlay | Current rank | Delta | VOR | Signal | Miss | Warnings |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15 | Trey McBride | TE | ARI | 94.6 | 0.750 | 6 | -9 | 1.802 | 42.345 | 0.234 |  |
| 21 | George Kittle | TE | SF | 92.4 | 0.727 | 20 | -1 | 2.817 | 54.563 | 0.170 | injury_status_flag |
| 29 | Sam LaPorta | TE | DET | 89.3 | 0.712 | 26 | -3 | 2.753 | 54.538 | 0.234 | injury_status_flag |
| 32 | Brock Bowers | TE | LV | 88.2 | 0.701 | 13 | -19 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness |
| 46 | Travis Kelce | TE | KC | 82.8 | 0.663 | 52 | +6 | 2.692 | 57.511 | 0.170 |  |
| 47 | Kyle Pitts | TE | ATL | 82.4 | 0.662 | 39 | -8 | 2.133 | 41.118 | 0.170 |  |
| 50 | Dallas Goedert | TE | PHI | 81.3 | 0.652 | 44 | -6 | 1.653 | 41.374 | 0.170 |  |
| 51 | Tucker Kraft | TE | GB | 80.9 | 0.651 | 33 | -18 | 0.729 | 27.510 | 0.298 | injury_status_flag |
| 64 | Tyler Warren | TE | IND | 75.9 | 0.620 | 48 | -16 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness |
| 70 | Hunter Henry | TE | NE | 73.6 | 0.612 | 59 | -11 | 1.594 | 39.226 | 0.234 |  |
| 78 | Dalton Schultz | TE | HOU | 70.6 | 0.597 | 64 | -14 | 1.251 | 34.953 | 0.234 |  |
| 80 | Juwan Johnson | TE | NO | 69.8 | 0.589 | 68 | -12 | 1.452 | 32.920 | 0.234 |  |
| 85 | Jake Ferguson | TE | DAL | 67.9 | 0.581 | 77 | -8 | 1.212 | 39.885 | 0.234 |  |
| 90 | Colston Loveland | TE | CHI | 66.0 | 0.568 | 72 | -18 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness |
| 91 | Mark Andrews | TE | BAL | 65.6 | 0.565 | 90 | -1 | 2.100 | 40.980 | 0.170 |  |
| 93 | T.J. Hockenson | TE | MIN | 64.8 | 0.563 | 94 | +1 | 2.019 | 45.072 | 0.234 |  |
| 94 | Dalton Kincaid | TE | BUF | 64.5 | 0.560 | 85 | -9 | 1.127 | 35.222 | 0.298 |  |
| 97 | Harold Fannin Jr. | TE | CLE | 63.3 | 0.553 | 81 | -16 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 109 | Cade Otton | TE | TB | 58.7 | 0.504 | 111 | +2 | 0.849 | 33.626 | 0.234 |  |
| 122 | Brenton Strange | TE | JAX | 53.7 | 0.489 | 107 | -15 | 0.243 | 18.236 | 0.362 |  |
| 123 | Theo Johnson | TE | NYG | 53.4 | 0.487 | 115 | -8 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness |
| 125 | David Njoku | TE | LAC | 52.6 | 0.485 | 134 | +9 | 1.930 | 48.647 | 0.170 |  |
| 129 | Mason Taylor | TE | NYJ | 51.1 | 0.479 | 119 | -10 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness |
| 131 | Oronde Gadsden II | TE | LAC | 50.3 | 0.472 | 124 | -7 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness |
| 133 | AJ Barner | TE | SEA | 49.5 | 0.464 | 127 | -6 | 0.874 | 25.273 | 1.000 | missing_feature_row, high_missingness, injury_status_flag |
| 137 | Pat Freiermuth | TE | PIT | 48.0 | 0.454 | 141 | +4 | 1.424 | 38.224 | 0.234 |  |
| 142 | Greg Dulcich | TE | MIA | 46.1 | 0.445 | 131 | -11 | 0.550 | 17.412 | 0.234 |  |
| 144 | Evan Engram | TE | DEN | 45.3 | 0.444 | 152 | +8 | 1.934 | 45.555 | 0.170 |  |
| 146 | Cole Kmet | TE | CHI | 44.6 | 0.439 | 149 | +3 | 1.489 | 37.849 | 0.170 |  |
| 149 | Colby Parkinson | TE | LAR | 43.4 | 0.434 | 138 | -11 | 0.352 | 20.863 | 0.234 |  |
| 156 | Dawson Knox | TE | BUF | 40.8 | 0.423 | 146 | -10 | 0.542 | 23.097 | 0.234 |  |
| 162 | Michael Mayer | TE | LV | 38.5 | 0.408 | 157 | -5 | 1.065 | 26.353 | 0.298 |  |
| 164 | Chig Okonkwo | TE | WAS | 37.7 | 0.400 | 163 | -1 | 1.337 | 31.112 | 0.170 |  |
| 166 | Isaiah Likely | TE | NYG | 36.9 | 0.398 | 160 | -6 | 0.942 | 25.408 | 0.234 |  |
| 171 | Mike Gesicki | TE | CIN | 35.0 | 0.387 | 167 | -4 | 0.926 | 28.107 | 0.234 |  |

## Top 25 Risers
| Player | Pos | Team | Current | Overlay | Delta | Warnings |
|---|---|---|---|---|---|---|
| David Montgomery | RB | HOU | 165 | 111 | +54 | rank_delta_over_20 |
| Lamar Jackson | QB | BAL | 75 | 22 | +53 | rank_delta_over_20 |
| Isiah Pacheco | RB | DET | 172 | 119 | +53 | rank_delta_over_20 |
| Kyler Murray | QB | MIN | 100 | 48 | +52 | rank_delta_over_20 |
| Alvin Kamara | RB | NO | 140 | 88 | +52 | rank_delta_over_20 |
| Aaron Jones | RB | MIN | 112 | 63 | +49 | rank_delta_over_20 |
| Derrick Henry | RB | BAL | 91 | 43 | +48 | rank_delta_over_20 |
| Justin Fields | QB | KC | 239 | 191 | +48 | rank_delta_over_20 |
| James Conner | RB | ARI | 125 | 79 | +46 | rank_delta_over_20, injury_status_flag |
| Kenneth Walker III | RB | KC | 109 | 65 | +44 | rank_delta_over_20 |
| Tony Pollard | RB | TEN | 116 | 76 | +40 | rank_delta_over_20 |
| Saquon Barkley | RB | PHI | 49 | 10 | +39 | rank_delta_over_20 |
| Tyler Huntley | QB | BAL | 222 | 184 | +38 | rank_delta_over_20 |
| Josh Jacobs | RB | GB | 62 | 25 | +37 | rank_delta_over_20 |
| Rachaad White | RB | WAS | 169 | 132 | +37 | rank_delta_over_20 |
| Breece Hall | RB | NYJ | 74 | 38 | +36 | rank_delta_over_20 |
| Jalen Hurts | QB | PHI | 34 | 2 | +32 | rank_delta_over_20 |
| Rhamondre Stevenson | RB | NE | 104 | 73 | +31 | rank_delta_over_20 |
| Daniel Jones | QB | IND | 42 | 12 | +30 | rank_delta_over_20, injury_status_flag |
| Travis Etienne | RB | NO | 67 | 37 | +30 | rank_delta_over_20 |
| Joe Burrow | QB | CIN | 88 | 58 | +30 | rank_delta_over_20 |
| Justin Herbert | QB | LAC | 71 | 42 | +29 | rank_delta_over_20 |
| Carson Wentz | QB | MIN | 225 | 198 | +27 | rank_delta_over_20 |
| D'Andre Swift | RB | CHI | 69 | 44 | +25 | rank_delta_over_20 |
| J.K. Dobbins | RB | DEN | 102 | 77 | +25 | rank_delta_over_20 |

## Top 25 Fallers
| Player | Pos | Team | Current | Overlay | Delta | Warnings |
|---|---|---|---|---|---|---|
| Jameson Williams | WR | DET | 63 | 92 | -29 | rank_delta_over_20 |
| Quentin Johnston | WR | LAC | 73 | 102 | -29 | rank_delta_over_20 |
| Alec Pierce | WR | IND | 55 | 83 | -28 | rank_delta_over_20, injury_status_flag |
| Emeka Egbuka | WR | TB | 60 | 87 | -27 | rank_delta_over_20, missing_feature_row, high_missingness |
| Jaxon Smith-Njigba | WR | SEA | 1 | 27 | -26 | rank_delta_over_20 |
| Malik Nabers | WR | NYG | 40 | 66 | -26 | rank_delta_over_20, missing_feature_row, high_missingness, injury_status_flag |
| Rome Odunze | WR | CHI | 43 | 69 | -26 | rank_delta_over_20, missing_feature_row, high_missingness |
| Tetairoa McMillan | WR | CAR | 35 | 60 | -25 | rank_delta_over_20, missing_feature_row, high_missingness, injury_status_flag |
| Wan'Dale Robinson | WR | TEN | 37 | 62 | -25 | rank_delta_over_20 |
| Michael Wilson | WR | ARI | 76 | 100 | -24 | rank_delta_over_20 |
| Drake London | WR | ATL | 8 | 30 | -22 | rank_delta_over_20 |
| Mack Hollins | WR | NE | 135 | 157 | -22 | rank_delta_over_20 |
| Kayshon Boutte | WR | NE | 145 | 167 | -22 | rank_delta_over_20 |
| Rashee Rice | WR | KC | 15 | 36 | -21 | rank_delta_over_20, injury_status_flag |
| Parker Washington | WR | JAX | 101 | 121 | -20 |  |
| Brock Bowers | TE | LV | 13 | 32 | -19 | missing_feature_row, high_missingness |
| Christian Watson | WR | GB | 79 | 98 | -19 |  |
| George Pickens | WR | DAL | 21 | 39 | -18 |  |
| Tucker Kraft | TE | GB | 33 | 51 | -18 | injury_status_flag |
| Colston Loveland | TE | CHI | 72 | 90 | -18 | missing_feature_row, high_missingness |
| Zay Flowers | WR | BAL | 24 | 41 | -17 |  |
| Nico Collins | WR | HOU | 32 | 49 | -17 |  |
| Courtland Sutton | WR | DEN | 57 | 74 | -17 |  |
| Jakobi Meyers | WR | JAX | 65 | 82 | -17 |  |
| Elic Ayomanor | WR | TEN | 110 | 127 | -17 | missing_feature_row, high_missingness |

## Top Bucket Movement
### Entering Top 24
| Player | Pos | Team | Current | Overlay | Delta | Warnings |
|---|---|---|---|---|---|---|
| Jalen Hurts | QB | PHI | 34 | 2 | +32 | rank_delta_over_20 |
| Kyren Williams | RB | LAR | 30 | 9 | +21 | rank_delta_over_20 |
| Saquon Barkley | RB | PHI | 49 | 10 | +39 | rank_delta_over_20 |
| Daniel Jones | QB | IND | 42 | 12 | +30 | rank_delta_over_20, injury_status_flag |
| James Cook | RB | BUF | 36 | 18 | +18 |  |
| Dak Prescott | QB | DAL | 28 | 19 | +9 |  |
| Lamar Jackson | QB | BAL | 75 | 22 | +53 | rank_delta_over_20 |
| Trevor Lawrence | QB | JAX | 38 | 23 | +15 |  |
| Brock Purdy | QB | SF | 31 | 24 | +7 |  |

### Leaving Top 24
| Player | Pos | Team | Current | Overlay | Delta | Warnings |
|---|---|---|---|---|---|---|
| Jaxon Smith-Njigba | WR | SEA | 1 | 27 | -26 | rank_delta_over_20 |
| Drake London | WR | ATL | 8 | 30 | -22 | rank_delta_over_20 |
| Chris Olave | WR | NO | 12 | 28 | -16 | injury_status_flag |
| Brock Bowers | TE | LV | 13 | 32 | -19 | missing_feature_row, high_missingness |
| Rashee Rice | WR | KC | 15 | 36 | -21 | rank_delta_over_20, injury_status_flag |
| Garrett Wilson | WR | NYJ | 18 | 33 | -15 |  |
| George Pickens | WR | DAL | 21 | 39 | -18 |  |
| Matthew Stafford | QB | LAR | 22 | 31 | -9 |  |
| Zay Flowers | WR | BAL | 24 | 41 | -17 |  |

### Entering Top 50
| Player | Pos | Team | Current | Overlay | Delta | Warnings |
|---|---|---|---|---|---|---|
| Lamar Jackson | QB | BAL | 75 | 22 | +53 | rank_delta_over_20 |
| Josh Jacobs | RB | GB | 62 | 25 | +37 | rank_delta_over_20 |
| Travis Etienne | RB | NO | 67 | 37 | +30 | rank_delta_over_20 |
| Breece Hall | RB | NYJ | 74 | 38 | +36 | rank_delta_over_20 |
| Justin Herbert | QB | LAC | 71 | 42 | +29 | rank_delta_over_20 |
| Derrick Henry | RB | BAL | 91 | 43 | +48 | rank_delta_over_20 |
| D'Andre Swift | RB | CHI | 69 | 44 | +25 | rank_delta_over_20 |
| C.J. Stroud | QB | HOU | 66 | 45 | +21 | rank_delta_over_20 |
| Travis Kelce | TE | KC | 52 | 46 | +6 |  |
| Kyler Murray | QB | MIN | 100 | 48 | +52 | rank_delta_over_20 |

### Leaving Top 50
| Player | Pos | Team | Current | Overlay | Delta | Warnings |
|---|---|---|---|---|---|---|
| Tucker Kraft | TE | GB | 33 | 51 | -18 | injury_status_flag |
| Tetairoa McMillan | WR | CAR | 35 | 60 | -25 | rank_delta_over_20, missing_feature_row, high_missingness, injury_status_flag |
| Wan'Dale Robinson | WR | TEN | 37 | 62 | -25 | rank_delta_over_20 |
| Malik Nabers | WR | NYG | 40 | 66 | -26 | rank_delta_over_20, missing_feature_row, high_missingness, injury_status_flag |
| Chase Brown | RB | CIN | 41 | 52 | -11 |  |
| Rome Odunze | WR | CHI | 43 | 69 | -26 | rank_delta_over_20, missing_feature_row, high_missingness |
| DeVonta Smith | WR | PHI | 46 | 56 | -10 |  |
| Bo Nix | QB | DEN | 47 | 53 | -6 | missing_feature_row, high_missingness, injury_status_flag |
| Tyler Warren | TE | IND | 48 | 64 | -16 | missing_feature_row, high_missingness |
| Terry McLaurin | WR | WAS | 50 | 57 | -7 |  |

## Cutline Crossings
### QB12
Entering: Lamar Jackson (7 from 16), Justin Herbert (12 from 15)
Leaving: Bo Nix (11 to 15), Caleb Williams (12 to 17)

### RB12
Entering: Travis Etienne (11 from 14), Josh Jacobs (9 from 13), Breece Hall (12 from 16)
Leaving: Omarion Hampton (11 to 16), Ashton Jeanty (12 to 20), Chase Brown (8 to 15)

### RB24
Entering: James Conner (24 from 29), Aaron Jones (17 from 26), Tony Pollard (22 from 27), Kenneth Walker III (18 from 25)
Leaving: Cam Skattebo (18 to 27), Rico Dowdle (22 to 29), Quinshon Judkins (21 to 28), Bucky Irving (17 to 25)

### RB36
Entering: Isiah Pacheco (33 from 41), Rachaad White (35 from 40), David Montgomery (31 from 39)
Leaving: Trey Benson (36 to 39), RJ Harvey (35 to 38), Woody Marks (34 to 37)

### WR12
Entering: Davante Adams (11 from 13), CeeDee Lamb (10 from 14)
Leaving: George Pickens (11 to 13), Zay Flowers (12 to 14)

### WR24
Entering: Courtland Sutton (24 from 25)
Leaving: Alec Pierce (23 to 27)

### WR36
Entering: Entering: None
Leaving: Leaving: None

### TE6
Entering: Travis Kelce (5 from 9)
Leaving: Tucker Kraft (5 to 8)

### TE12
Entering: Entering: None
Leaving: Leaving: None

### TE18
Entering: Entering: None
Leaving: Leaving: None

### TE35
Entering: Entering: None
Leaving: Leaving: None
