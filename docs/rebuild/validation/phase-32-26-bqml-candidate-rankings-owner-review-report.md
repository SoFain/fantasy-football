# Phase 32.26: BQML Candidate Rankings Owner Review Report

Final decision: BQML CANDIDATE RANKINGS READY WITH WARNINGS

## Scope

Phase 32.26 generated review-only candidate ranking boards from the existing Phase 32.24 enriched BQML models. Output is Markdown-only. No review table was persisted because the report gives enough owner-inspection evidence for this phase.

No deploy occurred. No live rankings were regenerated. No champion formula was activated. No new BQML model was trained. No source ingest, Pigskin chat, Gemini, live Sleeper API, old Python tournament path, detail-row write, or global truncate occurred.

## Files Changed

- `docs/rebuild/validation/phase-32-26-bqml-candidate-rankings-owner-review-report.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

Initial package commit: `d8920db phase 32.26 document bqml review boards`.

## Git State

Before Phase 32.26:

- Latest commit: `fe1f90f phase 32.25 document bqml owner review`.
- Worktree: standing untracked historical validation backlog only.

After initial Phase 32.26 package:

- Latest commit: `d8920db phase 32.26 document bqml review boards`.
- Worktree: standing untracked historical validation backlog only.

Repeated-prompt review:

- The second Phase 32.26 prompt matched the completed scope.
- No additional BigQuery analysis, model training, ranking writes, or persistent review-table work was required.
- This metadata addendum records the package commit and explicit git state.

## Evidence And Model Verification

- `ranking_bqml_enriched_logistic_elite_v1`: exists.
- `ranking_bqml_enriched_linear_points_v1`: exists.
- BQML enriched run rows: 8.
- BQML enriched summary rows: 128.
- `ranking_formula_champions`: 0.
- Active live rankings: 1,140.
- Board slice: historical-review holdout, season 2025, week 18.
- Read-only board query dry-run bytes: 4,232,093.

## Board Generation Method

Review boards were generated with read-only `ML.PREDICT` against the already-trained enriched BQML models and `ranking_backtest_feature_mart`. Current Pigskin used the deterministic proxy weights from the SQL-native evaluator. This is a historical-review board, not a 2026 live board.

Review-only board IDs:

- `bqml_enriched_logistic_elite_v1_owner_review`
- `bqml_enriched_linear_points_v1_owner_review`

No persistent `ranking_owner_review_candidate_boards` table was created. Persistence remains optional for a later owner-approved phase.

## All-Profile Coverage

| Profile | Board | Record count | Top five |
| --- | --- | --- | --- |
| ppr | Current Pigskin | 93 | Derrick Henry, Christian McCaffrey, Tony Pollard, David Montgomery, Lamar Jackson |
| ppr | BQML Logistic | 93 | Derrick Henry, Lamar Jackson, Christian McCaffrey, David Montgomery, Tony Pollard |
| ppr | BQML Linear Points | 93 | Lamar Jackson, Baker Mayfield, Jared Goff, Derrick Henry, Dak Prescott |
| half_ppr | Current Pigskin | 93 | Derrick Henry, Christian McCaffrey, Tony Pollard, David Montgomery, Lamar Jackson |
| half_ppr | BQML Logistic | 93 | Derrick Henry, Christian McCaffrey, Lamar Jackson, David Montgomery, Tony Pollard |
| half_ppr | BQML Linear Points | 93 | Lamar Jackson, Baker Mayfield, Jared Goff, Derrick Henry, Dak Prescott |
| standard | Current Pigskin | 93 | Derrick Henry, Christian McCaffrey, Tony Pollard, David Montgomery, Lamar Jackson |
| standard | BQML Logistic | 93 | Derrick Henry, Lamar Jackson, Christian McCaffrey, David Montgomery, Tony Pollard |
| standard | BQML Linear Points | 93 | Lamar Jackson, Baker Mayfield, Jared Goff, Dak Prescott, Matthew Stafford |
| gng_keeper | Current Pigskin | 93 | Derrick Henry, Christian McCaffrey, Tony Pollard, David Montgomery, Lamar Jackson |
| gng_keeper | BQML Logistic | 93 | Derrick Henry, Christian McCaffrey, Lamar Jackson, David Montgomery, Tony Pollard |
| gng_keeper | BQML Linear Points | 93 | Lamar Jackson, Jared Goff, Baker Mayfield, Dak Prescott, Derrick Henry |

## PPR Overall Board: Current Pigskin Top 50

| Rank | Player | Pos | Team | Score | Current rank | Delta vs current |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Derrick Henry | RB | BAL | 71.14 | 1 | 0 |
| 2 | Christian McCaffrey | RB | SF | 67.55 | 2 | 0 |
| 3 | Tony Pollard | RB | TEN | 63.24 | 3 | 0 |
| 4 | David Montgomery | RB | DET | 59.41 | 4 | 0 |
| 5 | Lamar Jackson | QB | BAL | 57.40 | 5 | 0 |
| 6 | Jared Goff | QB | DET | 52.86 | 6 | 0 |
| 7 | Stefon Diggs | WR | NE | 52.72 | 7 | 0 |
| 8 | Travis Kelce | TE | KC | 52.68 | 8 | 0 |
| 9 | Devin Singletary | RB | NYG | 51.83 | 9 | 0 |
| 10 | Keenan Allen | WR | LAC | 51.73 | 10 | 0 |
| 11 | Mike Evans | WR | TB | 51.53 | 11 | 0 |
| 12 | Chris Godwin Jr. | WR | TB | 51.51 | 12 | 0 |
| 13 | Kareem Hunt | RB | KC | 50.93 | 13 | 0 |
| 14 | George Kittle | TE | SF | 50.14 | 14 | 0 |
| 15 | Terry McLaurin | WR | WAS | 49.95 | 15 | 0 |
| 16 | DJ Moore | WR | CHI | 49.68 | 16 | 0 |
| 17 | Deebo Samuel Sr. | WR | WAS | 49.49 | 17 | 0 |
| 18 | Cooper Kupp | WR | SEA | 49.11 | 18 | 0 |
| 19 | Jakobi Meyers | WR | JAX | 48.53 | 19 | 0 |
| 20 | Adam Thielen | WR | PIT | 47.11 | 20 | 0 |
| 21 | Courtland Sutton | WR | DEN | 46.87 | 21 | 0 |
| 22 | DeAndre Hopkins | WR | BAL | 46.81 | 22 | 0 |
| 23 | Mark Andrews | TE | BAL | 46.53 | 23 | 0 |
| 24 | Tyler Lockett | WR | LV | 46.11 | 24 | 0 |
| 25 | Taysom Hill | TE | NO | 44.93 | 25 | 0 |
| 26 | Evan Engram | TE | DEN | 44.78 | 26 | 0 |
| 27 | Christian Kirk | WR | HOU | 44.71 | 27 | 0 |
| 28 | Josh Palmer | WR | BUF | 42.94 | 28 | 0 |
| 29 | Dalton Schultz | TE | HOU | 42.47 | 29 | 0 |
| 30 | Samaje Perine | RB | CIN | 42.05 | 30 | 0 |
| 31 | Darius Slayton | WR | NYG | 41.92 | 31 | 0 |
| 32 | Dak Prescott | QB | DAL | 41.74 | 32 | 0 |
| 33 | Baker Mayfield | QB | TB | 41.60 | 33 | 0 |
| 34 | Hunter Henry | TE | NE | 40.53 | 34 | 0 |
| 35 | Kalif Raymond | WR | DET | 40.43 | 35 | 0 |
| 36 | Jonnu Smith | TE | PIT | 40.19 | 36 | 0 |
| 37 | Demarcus Robinson | WR | SF | 40.06 | 37 | 0 |
| 38 | Tyler Higbee | TE | LA | 40.00 | 38 | 0 |
| 39 | Marquise Brown | WR | KC | 39.73 | 39 | 0 |
| 40 | Tyler Conklin | TE | LAC | 39.32 | 40 | 0 |
| 41 | JuJu Smith-Schuster | WR | KC | 39.25 | 41 | 0 |
| 42 | Noah Fant | TE | CIN | 38.85 | 42 | 0 |
| 43 | Austin Hooper | TE | NE | 38.38 | 43 | 0 |
| 44 | Dawson Knox | TE | BUF | 37.97 | 44 | 0 |
| 45 | Justin Watson | WR | HOU | 37.70 | 45 | 0 |
| 46 | Will Dissly | TE | LAC | 37.60 | 46 | 0 |
| 47 | Tim Patrick | WR | JAX | 37.51 | 47 | 0 |
| 48 | Marquez Valdes-Scantling | WR | PIT | 37.44 | 48 | 0 |
| 49 | Mike Gesicki | TE | CIN | 37.00 | 49 | 0 |
| 50 | Audric Estimé | RB | NO | 36.85 | 50 | 0 |

## PPR Overall Board: BQML Logistic Elite Top 50

| Rank | Player | Pos | Team | Score | Current rank | Delta vs current |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Derrick Henry | RB | BAL | 79.52 | 1 | 0 |
| 2 | Lamar Jackson | QB | BAL | 76.43 | 5 | 3 |
| 3 | Christian McCaffrey | RB | SF | 75.75 | 2 | -1 |
| 4 | David Montgomery | RB | DET | 65.33 | 4 | 0 |
| 5 | Tony Pollard | RB | TEN | 64.58 | 3 | -2 |
| 6 | George Kittle | TE | SF | 60.30 | 14 | 8 |
| 7 | Keenan Allen | WR | LAC | 59.64 | 10 | 3 |
| 8 | Travis Kelce | TE | KC | 59.24 | 8 | 0 |
| 9 | Mike Evans | WR | TB | 59.17 | 11 | 2 |
| 10 | Cooper Kupp | WR | SEA | 58.39 | 18 | 8 |
| 11 | Baker Mayfield | QB | TB | 56.38 | 33 | 22 |
| 12 | DJ Moore | WR | CHI | 56.28 | 16 | 4 |
| 13 | Chris Godwin Jr. | WR | TB | 56.07 | 12 | -1 |
| 14 | Jared Goff | QB | DET | 55.15 | 6 | -8 |
| 15 | Stefon Diggs | WR | NE | 52.77 | 7 | -8 |
| 16 | Jakobi Meyers | WR | JAX | 51.76 | 19 | 3 |
| 17 | Courtland Sutton | WR | DEN | 48.41 | 21 | 4 |
| 18 | Terry McLaurin | WR | WAS | 47.70 | 15 | -3 |
| 19 | Kareem Hunt | RB | KC | 47.41 | 13 | -6 |
| 20 | Adam Thielen | WR | PIT | 46.52 | 20 | 0 |
| 21 | Mark Andrews | TE | BAL | 46.11 | 23 | 2 |
| 22 | Deebo Samuel Sr. | WR | WAS | 45.89 | 17 | -5 |
| 23 | Dak Prescott | QB | DAL | 45.77 | 32 | 9 |
| 24 | Joshua Dobbs | QB | NE | 44.80 | 66 | 42 |
| 25 | Evan Engram | TE | DEN | 43.16 | 26 | 1 |
| 26 | Taysom Hill | TE | NO | 42.59 | 25 | -1 |
| 27 | Jonnu Smith | TE | PIT | 42.05 | 36 | 9 |
| 28 | Matthew Stafford | QB | LA | 39.90 | 54 | 26 |
| 29 | Devin Singletary | RB | NYG | 37.84 | 9 | -20 |
| 30 | DeAndre Hopkins | WR | BAL | 37.57 | 22 | -8 |
| 31 | Sam Darnold | QB | SEA | 36.86 | 52 | 21 |
| 32 | Jimmy Garoppolo | QB | LA | 34.76 | 64 | 32 |
| 33 | Christian Kirk | WR | HOU | 34.57 | 27 | -6 |
| 34 | Kirk Cousins | QB | ATL | 34.52 | 70 | 36 |
| 35 | Joe Flacco | QB | CIN | 32.56 | 86 | 51 |
| 36 | Dalton Schultz | TE | HOU | 32.23 | 29 | -7 |
| 37 | Hunter Henry | TE | NE | 32.15 | 34 | -3 |
| 38 | Tyler Lockett | WR | LV | 30.80 | 24 | -14 |
| 39 | Josh Palmer | WR | BUF | 30.08 | 28 | -11 |
| 40 | Darius Slayton | WR | NYG | 28.27 | 31 | -9 |
| 41 | Tyler Conklin | TE | LAC | 28.13 | 40 | -1 |
| 42 | Tyler Higbee | TE | LA | 27.93 | 38 | -4 |
| 43 | Mike Gesicki | TE | CIN | 27.16 | 49 | 6 |
| 44 | Marquise Brown | WR | KC | 27.10 | 39 | -5 |
| 45 | Demarcus Robinson | WR | SF | 26.84 | 37 | -8 |
| 46 | Aaron Rodgers | QB | PIT | 26.32 | 81 | 35 |
| 47 | Noah Fant | TE | CIN | 24.76 | 42 | -5 |
| 48 | Jacoby Brissett | QB | ARI | 24.74 | 71 | 23 |
| 49 | Tim Patrick | WR | JAX | 24.74 | 47 | -2 |
| 50 | Ameer Abdullah | RB | IND | 23.93 | 56 | 6 |

## PPR Overall Board: BQML Linear Points Top 50

| Rank | Player | Pos | Team | Score | Current rank | Delta vs current |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Lamar Jackson | QB | BAL | 24.60 | 5 | 4 |
| 2 | Baker Mayfield | QB | TB | 17.95 | 33 | 31 |
| 3 | Jared Goff | QB | DET | 17.49 | 6 | 3 |
| 4 | Derrick Henry | RB | BAL | 15.98 | 1 | -3 |
| 5 | Dak Prescott | QB | DAL | 15.41 | 32 | 27 |
| 6 | Matthew Stafford | QB | LA | 14.94 | 54 | 48 |
| 7 | Cooper Kupp | WR | SEA | 14.90 | 18 | 11 |
| 8 | Keenan Allen | WR | LAC | 14.67 | 10 | 2 |
| 9 | Mike Evans | WR | TB | 14.54 | 11 | 2 |
| 10 | Sam Darnold | QB | SEA | 14.24 | 52 | 42 |
| 11 | DJ Moore | WR | CHI | 14.16 | 16 | 5 |
| 12 | Joshua Dobbs | QB | NE | 13.98 | 66 | 54 |
| 13 | Christian McCaffrey | RB | SF | 13.88 | 2 | -11 |
| 14 | Kirk Cousins | QB | ATL | 13.88 | 70 | 56 |
| 15 | Travis Kelce | TE | KC | 13.20 | 8 | -7 |
| 16 | Stefon Diggs | WR | NE | 13.16 | 7 | -9 |
| 17 | Terry McLaurin | WR | WAS | 13.13 | 15 | -2 |
| 18 | George Kittle | TE | SF | 13.09 | 14 | -4 |
| 19 | Courtland Sutton | WR | DEN | 13.04 | 21 | 2 |
| 20 | Joe Flacco | QB | CIN | 12.77 | 86 | 66 |
| 21 | Chris Godwin Jr. | WR | TB | 12.72 | 12 | -9 |
| 22 | Jimmy Garoppolo | QB | LA | 12.43 | 64 | 42 |
| 23 | Tony Pollard | RB | TEN | 12.37 | 3 | -20 |
| 24 | Jakobi Meyers | WR | JAX | 12.35 | 19 | -5 |
| 25 | David Montgomery | RB | DET | 12.24 | 4 | -21 |
| 26 | Deebo Samuel Sr. | WR | WAS | 11.91 | 17 | -9 |
| 27 | DeAndre Hopkins | WR | BAL | 11.73 | 22 | -5 |
| 28 | Aaron Rodgers | QB | PIT | 11.50 | 81 | 53 |
| 29 | Adam Thielen | WR | PIT | 11.38 | 20 | -9 |
| 30 | Mark Andrews | TE | BAL | 11.21 | 23 | -7 |
| 31 | Evan Engram | TE | DEN | 10.04 | 26 | -5 |
| 32 | Christian Kirk | WR | HOU | 9.95 | 27 | -5 |
| 33 | Tyler Lockett | WR | LV | 9.81 | 24 | -9 |
| 34 | Jonnu Smith | TE | PIT | 9.61 | 36 | 2 |
| 35 | Josh Palmer | WR | BUF | 9.06 | 28 | -7 |
| 36 | Mitchell Trubisky | QB | BUF | 8.89 | 87 | 51 |
| 37 | Kareem Hunt | RB | KC | 8.84 | 13 | -24 |
| 38 | Taysom Hill | TE | NO | 8.78 | 25 | -13 |
| 39 | Marquise Brown | WR | KC | 8.47 | 39 | 0 |
| 40 | Jacoby Brissett | QB | ARI | 8.35 | 71 | 31 |
| 41 | Dalton Schultz | TE | HOU | 8.25 | 29 | -12 |
| 42 | Darius Slayton | WR | NYG | 8.21 | 31 | -11 |
| 43 | Nick Mullens | QB | JAX | 8.19 | 63 | 20 |
| 44 | Devin Singletary | RB | NYG | 8.03 | 9 | -35 |
| 45 | Mike Gesicki | TE | CIN | 8.01 | 49 | 4 |
| 46 | Demarcus Robinson | WR | SF | 7.94 | 37 | -9 |
| 47 | Hunter Henry | TE | NE | 7.83 | 34 | -13 |
| 48 | Audric Estimé | RB | NO | 7.59 | 50 | 2 |
| 49 | Tim Patrick | WR | JAX | 7.50 | 47 | -2 |
| 50 | Tyler Higbee | TE | LA | 7.17 | 38 | -12 |

## PPR Side-by-Side Current Top 100

| Current rank | Current player | Log rank | Log delta | Linear rank | Linear delta |
| --- | --- | --- | --- | --- | --- |
| 1 | Derrick Henry (RB, BAL) | 1 | 0 | 4 | -3 |
| 2 | Christian McCaffrey (RB, SF) | 3 | -1 | 13 | -11 |
| 3 | Tony Pollard (RB, TEN) | 5 | -2 | 23 | -20 |
| 4 | David Montgomery (RB, DET) | 4 | 0 | 25 | -21 |
| 5 | Lamar Jackson (QB, BAL) | 2 | 3 | 1 | 4 |
| 6 | Jared Goff (QB, DET) | 14 | -8 | 3 | 3 |
| 7 | Stefon Diggs (WR, NE) | 15 | -8 | 16 | -9 |
| 8 | Travis Kelce (TE, KC) | 8 | 0 | 15 | -7 |
| 9 | Devin Singletary (RB, NYG) | 29 | -20 | 44 | -35 |
| 10 | Keenan Allen (WR, LAC) | 7 | 3 | 8 | 2 |
| 11 | Mike Evans (WR, TB) | 9 | 2 | 9 | 2 |
| 12 | Chris Godwin Jr. (WR, TB) | 13 | -1 | 21 | -9 |
| 13 | Kareem Hunt (RB, KC) | 19 | -6 | 37 | -24 |
| 14 | George Kittle (TE, SF) | 6 | 8 | 18 | -4 |
| 15 | Terry McLaurin (WR, WAS) | 18 | -3 | 17 | -2 |
| 16 | DJ Moore (WR, CHI) | 12 | 4 | 11 | 5 |
| 17 | Deebo Samuel Sr. (WR, WAS) | 22 | -5 | 26 | -9 |
| 18 | Cooper Kupp (WR, SEA) | 10 | 8 | 7 | 11 |
| 19 | Jakobi Meyers (WR, JAX) | 16 | 3 | 24 | -5 |
| 20 | Adam Thielen (WR, PIT) | 20 | 0 | 29 | -9 |
| 21 | Courtland Sutton (WR, DEN) | 17 | 4 | 19 | 2 |
| 22 | DeAndre Hopkins (WR, BAL) | 30 | -8 | 27 | -5 |
| 23 | Mark Andrews (TE, BAL) | 21 | 2 | 30 | -7 |
| 24 | Tyler Lockett (WR, LV) | 38 | -14 | 33 | -9 |
| 25 | Taysom Hill (TE, NO) | 26 | -1 | 38 | -13 |
| 26 | Evan Engram (TE, DEN) | 25 | 1 | 31 | -5 |
| 27 | Christian Kirk (WR, HOU) | 33 | -6 | 32 | -5 |
| 28 | Josh Palmer (WR, BUF) | 39 | -11 | 35 | -7 |
| 29 | Dalton Schultz (TE, HOU) | 36 | -7 | 41 | -12 |
| 30 | Samaje Perine (RB, CIN) | 53 | -23 | 54 | -24 |
| 31 | Darius Slayton (WR, NYG) | 40 | -9 | 42 | -11 |
| 32 | Dak Prescott (QB, DAL) | 23 | 9 | 5 | 27 |
| 33 | Baker Mayfield (QB, TB) | 11 | 22 | 2 | 31 |
| 34 | Hunter Henry (TE, NE) | 37 | -3 | 47 | -13 |
| 35 | Kalif Raymond (WR, DET) | 64 | -29 | 57 | -22 |
| 36 | Jonnu Smith (TE, PIT) | 27 | 9 | 34 | 2 |
| 37 | Demarcus Robinson (WR, SF) | 45 | -8 | 46 | -9 |
| 38 | Tyler Higbee (TE, LA) | 42 | -4 | 50 | -12 |
| 39 | Marquise Brown (WR, KC) | 44 | -5 | 39 | 0 |
| 40 | Tyler Conklin (TE, LAC) | 41 | -1 | 51 | -11 |
| 41 | JuJu Smith-Schuster (WR, KC) | 68 | -27 | 65 | -24 |
| 42 | Noah Fant (TE, CIN) | 47 | -5 | 52 | -10 |
| 43 | Austin Hooper (TE, NE) | 63 | -20 | 63 | -20 |
| 44 | Dawson Knox (TE, BUF) | 55 | -11 | 61 | -17 |
| 45 | Justin Watson (WR, HOU) | 65 | -20 | 66 | -21 |
| 46 | Will Dissly (TE, LAC) | 61 | -15 | 60 | -14 |
| 47 | Tim Patrick (WR, JAX) | 49 | -2 | 49 | -2 |
| 48 | Marquez Valdes-Scantling (WR, PIT) | 57 | -9 | 59 | -11 |
| 49 | Mike Gesicki (TE, CIN) | 43 | 6 | 45 | 4 |
| 50 | Audric Estimé (RB, NO) | 52 | -2 | 48 | 2 |
| 51 | Nyheim Hines (RB, NO) | 54 | -3 | 58 | -7 |
| 52 | Sam Darnold (QB, SEA) | 31 | 21 | 10 | 42 |
| 53 | Kendrick Bourne (WR, SF) | 51 | 2 | 53 | 0 |
| 54 | Matthew Stafford (QB, LA) | 28 | 26 | 6 | 48 |
| 55 | Ty Johnson (RB, BUF) | 58 | -3 | 62 | -7 |
| 56 | Ameer Abdullah (RB, IND) | 50 | 6 | 56 | 0 |
| 57 | Cedrick Wilson Jr. (WR, MIA) | 62 | -5 | 64 | -7 |
| 58 | Johnny Mundt (TE, JAX) | 71 | -13 | 71 | -13 |
| 59 | Scott Miller (WR, PIT) | 79 | -20 | 83 | -24 |
| 60 | Durham Smythe (TE, CHI) | 69 | -9 | 76 | -16 |
| 61 | Josh Oliver (TE, MIN) | 66 | -5 | 68 | -7 |
| 62 | Dante Pettis (WR, NO) | 67 | -5 | 67 | -5 |
| 63 | Nick Mullens (QB, JAX) | 59 | 4 | 43 | 20 |
| 64 | Jimmy Garoppolo (QB, LA) | 32 | 32 | 22 | 42 |
| 65 | Anthony Firkser (TE, DET) | 83 | -18 | 93 | -28 |
| 66 | Joshua Dobbs (QB, NE) | 24 | 42 | 12 | 54 |
| 67 | David Sills (WR, ATL) | 76 | -9 | 69 | -2 |
| 68 | Mo Alie-Cox (TE, IND) | 75 | -7 | 72 | -4 |
| 69 | Ashton Dulin (WR, IND) | 80 | -11 | 85 | -16 |
| 70 | Kirk Cousins (QB, ATL) | 34 | 36 | 14 | 56 |
| 71 | Jacoby Brissett (QB, ARI) | 48 | 23 | 40 | 31 |
| 72 | Jeremy McNichols (RB, WAS) | 60 | 12 | 74 | -2 |
| 73 | Dare Ogunbowale (RB, HOU) | 70 | 3 | 78 | -5 |
| 74 | River Cracraft (WR, WAS) | 77 | -3 | 79 | -5 |
| 75 | Hunter Luepke (RB, DAL) | 73 | 2 | 77 | -2 |
| 76 | D'Ernest Johnson (RB, NE) | 72 | 4 | 75 | 1 |
| 77 | Eric Saubert (TE, SEA) | 82 | -5 | 81 | -4 |
| 78 | Pharaoh Brown (TE, ARI) | 85 | -7 | 84 | -6 |
| 79 | Steven Sims (WR, ARI) | 90 | -11 | 89 | -10 |
| 80 | Chris Manhertz (TE, NYG) | 86 | -6 | 88 | -8 |
| 81 | Aaron Rodgers (QB, PIT) | 46 | 35 | 28 | 53 |
| 82 | Trayveon Williams (RB, CLE) | 89 | -7 | 86 | -4 |
| 83 | Drew Sample (TE, CIN) | 74 | 9 | 73 | 10 |
| 84 | Alex Bachman (WR, LV) | 78 | 6 | 90 | -6 |
| 85 | Travis Homer (RB, CHI) | 87 | -2 | 82 | 3 |
| 86 | Joe Flacco (QB, CIN) | 35 | 51 | 20 | 66 |
| 87 | Mitchell Trubisky (QB, BUF) | 56 | 31 | 36 | 51 |
| 88 | Adam Prentice (RB, DEN) | 91 | -3 | 92 | -4 |
| 89 | Andrew Beck (RB, NYJ) | 81 | 8 | 80 | 9 |
| 90 | Gunner Olszewski (WR, NYG) | 93 | -3 | 91 | -1 |
| 91 | Tom Kennedy (WR, DET) | 92 | -1 | 87 | 4 |
| 92 | Brandon Allen (QB, TEN) | 84 | 8 | 55 | 37 |
| 93 | Josh Johnson (QB, WAS) | 88 | 5 | 70 | 23 |

## PPR QB Board Comparison

| Current pos rank | Player | Team | Log pos rank | Log delta | Linear pos rank | Linear delta |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Lamar Jackson | BAL | 1 | 0 | 1 | 0 |
| 2 | Jared Goff | DET | 3 | -1 | 3 | -1 |
| 3 | Dak Prescott | DAL | 4 | -1 | 4 | -1 |
| 4 | Baker Mayfield | TB | 2 | 2 | 2 | 2 |
| 5 | Sam Darnold | SEA | 7 | -2 | 6 | -1 |
| 6 | Matthew Stafford | LA | 6 | 0 | 5 | 1 |
| 7 | Nick Mullens | JAX | 14 | -7 | 14 | -7 |
| 8 | Jimmy Garoppolo | LA | 8 | 0 | 10 | -2 |
| 9 | Joshua Dobbs | NE | 5 | 4 | 7 | 2 |
| 10 | Kirk Cousins | ATL | 9 | 1 | 8 | 2 |
| 11 | Jacoby Brissett | ARI | 12 | -1 | 13 | -2 |
| 12 | Aaron Rodgers | PIT | 11 | 1 | 11 | 1 |
| 13 | Joe Flacco | CIN | 10 | 3 | 9 | 4 |
| 14 | Mitchell Trubisky | BUF | 13 | 1 | 12 | 2 |
| 15 | Brandon Allen | TEN | 15 | 0 | 15 | 0 |
| 16 | Josh Johnson | WAS | 16 | 0 | 16 | 0 |

## PPR RB Board Comparison

| Current pos rank | Player | Team | Log pos rank | Log delta | Linear pos rank | Linear delta |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Derrick Henry | BAL | 1 | 0 | 1 | 0 |
| 2 | Christian McCaffrey | SF | 2 | 0 | 2 | 0 |
| 3 | Tony Pollard | TEN | 4 | -1 | 3 | 0 |
| 4 | David Montgomery | DET | 3 | 1 | 4 | 0 |
| 5 | Devin Singletary | NYG | 6 | -1 | 6 | -1 |
| 6 | Kareem Hunt | KC | 5 | 1 | 5 | 1 |
| 7 | Samaje Perine | CIN | 9 | -2 | 8 | -1 |
| 8 | Audric Estimé | NO | 8 | 0 | 7 | 1 |
| 9 | Nyheim Hines | NO | 10 | -1 | 10 | -1 |
| 10 | Ty Johnson | BUF | 11 | -1 | 11 | -1 |
| 11 | Ameer Abdullah | IND | 7 | 4 | 9 | 2 |
| 12 | Jeremy McNichols | WAS | 12 | 0 | 12 | 0 |
| 13 | Dare Ogunbowale | HOU | 13 | 0 | 15 | -2 |
| 14 | Hunter Luepke | DAL | 15 | -1 | 14 | 0 |
| 15 | D'Ernest Johnson | NE | 14 | 1 | 13 | 2 |
| 16 | Trayveon Williams | CLE | 18 | -2 | 18 | -2 |
| 17 | Travis Homer | CHI | 17 | 0 | 17 | 0 |
| 18 | Adam Prentice | DEN | 19 | -1 | 19 | -1 |
| 19 | Andrew Beck | NYJ | 16 | 3 | 16 | 3 |

## PPR WR Board Comparison

| Current pos rank | Player | Team | Log pos rank | Log delta | Linear pos rank | Linear delta |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Stefon Diggs | NE | 6 | -5 | 5 | -4 |
| 2 | Keenan Allen | LAC | 1 | 1 | 2 | 0 |
| 3 | Mike Evans | TB | 2 | 1 | 3 | 0 |
| 4 | Chris Godwin Jr. | TB | 5 | -1 | 8 | -4 |
| 5 | Terry McLaurin | WAS | 9 | -4 | 6 | -1 |
| 6 | DJ Moore | CHI | 4 | 2 | 4 | 2 |
| 7 | Deebo Samuel Sr. | WAS | 11 | -4 | 10 | -3 |
| 8 | Cooper Kupp | SEA | 3 | 5 | 1 | 7 |
| 9 | Jakobi Meyers | JAX | 7 | 2 | 9 | 0 |
| 10 | Adam Thielen | PIT | 10 | 0 | 12 | -2 |
| 11 | Courtland Sutton | DEN | 8 | 3 | 7 | 4 |
| 12 | DeAndre Hopkins | BAL | 12 | 0 | 11 | 1 |
| 13 | Tyler Lockett | LV | 14 | -1 | 14 | -1 |
| 14 | Christian Kirk | HOU | 13 | 1 | 13 | 1 |
| 15 | Josh Palmer | BUF | 15 | 0 | 15 | 0 |
| 16 | Darius Slayton | NYG | 16 | 0 | 17 | -1 |
| 17 | Kalif Raymond | DET | 23 | -6 | 21 | -4 |
| 18 | Demarcus Robinson | SF | 18 | 0 | 18 | 0 |
| 19 | Marquise Brown | KC | 17 | 2 | 16 | 3 |
| 20 | JuJu Smith-Schuster | KC | 26 | -6 | 24 | -4 |
| 21 | Justin Watson | HOU | 24 | -3 | 25 | -4 |
| 22 | Tim Patrick | JAX | 19 | 3 | 19 | 3 |
| 23 | Marquez Valdes-Scantling | PIT | 21 | 2 | 22 | 1 |
| 24 | Kendrick Bourne | SF | 20 | 4 | 20 | 4 |
| 25 | Cedrick Wilson Jr. | MIA | 22 | 3 | 23 | 2 |
| 26 | Scott Miller | PIT | 30 | -4 | 29 | -3 |
| 27 | Dante Pettis | NO | 25 | 2 | 26 | 1 |
| 28 | David Sills | ATL | 27 | 1 | 27 | 1 |
| 29 | Ashton Dulin | IND | 31 | -2 | 30 | -1 |
| 30 | River Cracraft | WAS | 28 | 2 | 28 | 2 |
| 31 | Steven Sims | ARI | 32 | -1 | 32 | -1 |
| 32 | Alex Bachman | LV | 29 | 3 | 33 | -1 |
| 33 | Gunner Olszewski | NYG | 34 | -1 | 34 | -1 |
| 34 | Tom Kennedy | DET | 33 | 1 | 31 | 3 |

## PPR TE Board Comparison

| Current pos rank | Player | Team | Log pos rank | Log delta | Linear pos rank | Linear delta |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Travis Kelce | KC | 2 | -1 | 1 | 0 |
| 2 | George Kittle | SF | 1 | 1 | 2 | 0 |
| 3 | Mark Andrews | BAL | 3 | 0 | 3 | 0 |
| 4 | Taysom Hill | NO | 5 | -1 | 6 | -2 |
| 5 | Evan Engram | DEN | 4 | 1 | 4 | 1 |
| 6 | Dalton Schultz | HOU | 7 | -1 | 7 | -1 |
| 7 | Hunter Henry | NE | 8 | -1 | 9 | -2 |
| 8 | Jonnu Smith | PIT | 6 | 2 | 5 | 3 |
| 9 | Tyler Higbee | LA | 10 | -1 | 10 | -1 |
| 10 | Tyler Conklin | LAC | 9 | 1 | 11 | -1 |
| 11 | Noah Fant | CIN | 12 | -1 | 12 | -1 |
| 12 | Austin Hooper | NE | 15 | -3 | 15 | -3 |
| 13 | Dawson Knox | BUF | 13 | 0 | 14 | -1 |
| 14 | Will Dissly | LAC | 14 | 0 | 13 | 1 |
| 15 | Mike Gesicki | CIN | 11 | 4 | 8 | 7 |
| 16 | Johnny Mundt | JAX | 18 | -2 | 17 | -1 |
| 17 | Durham Smythe | CHI | 17 | 0 | 20 | -3 |
| 18 | Josh Oliver | MIN | 16 | 2 | 16 | 2 |
| 19 | Anthony Firkser | DET | 22 | -3 | 24 | -5 |
| 20 | Mo Alie-Cox | IND | 20 | 0 | 18 | 2 |
| 21 | Eric Saubert | SEA | 21 | 0 | 21 | 0 |
| 22 | Pharaoh Brown | ARI | 23 | -1 | 22 | 0 |
| 23 | Chris Manhertz | NYG | 24 | -1 | 23 | 0 |
| 24 | Drew Sample | CIN | 19 | 5 | 19 | 5 |

## Movement Tables

### Logistic Elite Top 25 Risers

| Player | Pos | Team | Current | BQML | Delta | xFP share | Elite rate | Spike | Bust | Avail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Joe Flacco | QB | CIN | 86 | 35 | 51 | 0.169 | 0.000 | 0.114 | 0.248 | 100.0 |
| Joshua Dobbs | QB | NE | 66 | 24 | 42 | 0.172 | 0.000 | 0.051 | 0.269 | 100.0 |
| Kirk Cousins | QB | ATL | 70 | 34 | 36 | 0.183 | 0.042 | 0.168 | 0.306 | 100.0 |
| Aaron Rodgers | QB | PIT | 81 | 46 | 35 | 0.121 | 0.020 | 0.020 | 0.431 | 97.5 |
| Jimmy Garoppolo | QB | LA | 64 | 32 | 32 | 0.163 | 0.000 | 0.030 | 0.251 | 100.0 |
| Mitchell Trubisky | QB | BUF | 87 | 56 | 31 | 0.101 | 0.000 | 0.000 | 0.592 | 100.0 |
| Matthew Stafford | QB | LA | 54 | 28 | 26 | 0.189 | 0.000 | 0.019 | 0.225 | 100.0 |
| Jacoby Brissett | QB | ARI | 71 | 48 | 23 | 0.140 | 0.000 | 0.024 | 0.548 |  |
| Baker Mayfield | QB | TB | 33 | 11 | 22 | 0.192 | 0.019 | 0.129 | 0.256 | 86.2 |
| Sam Darnold | QB | SEA | 52 | 31 | 21 | 0.155 | 0.019 | 0.019 | 0.411 | 100.0 |
| Jeremy McNichols | RB | WAS | 72 | 60 | 12 | 0.041 | 0.000 | 0.028 | 0.833 | 100.0 |
| Dak Prescott | QB | DAL | 32 | 23 | 9 | 0.185 | 0.037 | 0.200 | 0.145 | 100.0 |
| Jonnu Smith | TE | PIT | 36 | 27 | 9 | 0.095 | 0.098 | 0.137 | 0.343 | 85.3 |
| Drew Sample | TE | CIN | 83 | 74 | 9 | 0.026 | 0.000 | 0.000 | 0.814 | 84.7 |
| George Kittle | TE | SF | 14 | 6 | 8 | 0.126 | 0.278 | 0.412 | 0.170 | 81.9 |
| Cooper Kupp | WR | SEA | 18 | 10 | 8 | 0.179 | 0.310 | 0.418 | 0.260 | 88.8 |
| Andrew Beck | RB | NYJ | 89 | 81 | 8 | 0.029 | 0.000 | 0.000 | 0.886 |  |
| Brandon Allen | QB | TEN | 92 | 84 | 8 | 0.038 | 0.000 | 0.000 | 1.000 |  |
| Mike Gesicki | TE | CIN | 49 | 43 | 6 | 0.073 | 0.039 | 0.081 | 0.489 | 100.0 |
| Ameer Abdullah | RB | IND | 56 | 50 | 6 | 0.064 | 0.000 | 0.000 | 0.803 | 82.5 |
| Alex Bachman | WR | LV | 84 | 78 | 6 | 0.059 | 0.000 | 0.000 | 1.000 |  |
| Josh Johnson | QB | WAS | 93 | 88 | 5 | 0.030 | 0.000 | 0.000 | 0.750 |  |
| DJ Moore | WR | CHI | 16 | 12 | 4 | 0.178 | 0.137 | 0.275 | 0.255 | 65.0 |
| Courtland Sutton | WR | DEN | 21 | 17 | 4 | 0.154 | 0.020 | 0.059 | 0.191 | 79.2 |
| Nick Mullens | QB | JAX | 63 | 59 | 4 | 0.068 | 0.000 | 0.000 | 0.800 |  |

### Logistic Elite Top 25 Fallers

| Player | Pos | Team | Current | BQML | Delta | xFP share | Elite rate | Spike | Bust | Avail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Kalif Raymond | WR | DET | 35 | 64 | -29 | 0.059 | 0.000 | 0.000 | 0.643 | 66.7 |
| JuJu Smith-Schuster | WR | KC | 41 | 68 | -27 | 0.075 | 0.018 | 0.076 | 0.513 | 79.7 |
| Samaje Perine | RB | CIN | 30 | 53 | -23 | 0.072 | 0.018 | 0.035 | 0.605 | 94.3 |
| Devin Singletary | RB | NYG | 9 | 29 | -20 | 0.111 | 0.000 | 0.072 | 0.419 | 90.0 |
| Austin Hooper | TE | NE | 43 | 63 | -20 | 0.067 | 0.000 | 0.020 | 0.586 | 96.7 |
| Justin Watson | WR | HOU | 45 | 65 | -20 | 0.049 | 0.000 | 0.000 | 0.621 | 100.0 |
| Scott Miller | WR | PIT | 59 | 79 | -20 | 0.049 | 0.000 | 0.000 | 0.826 | 100.0 |
| Anthony Firkser | TE | DET | 65 | 83 | -18 | 0.025 | 0.000 | 0.000 | 0.667 |  |
| Will Dissly | TE | LAC | 46 | 61 | -15 | 0.056 | 0.000 | 0.042 | 0.650 | 79.7 |
| Tyler Lockett | WR | LV | 24 | 38 | -14 | 0.129 | 0.059 | 0.098 | 0.353 | 82.5 |
| Johnny Mundt | TE | JAX | 58 | 71 | -13 | 0.040 | 0.000 | 0.000 | 0.797 | 100.0 |
| Josh Palmer | WR | BUF | 28 | 39 | -11 | 0.106 | 0.020 | 0.053 | 0.398 | 81.1 |
| Dawson Knox | TE | BUF | 44 | 55 | -11 | 0.068 | 0.020 | 0.020 | 0.382 | 85.2 |
| Ashton Dulin | WR | IND | 69 | 80 | -11 | 0.049 | 0.000 | 0.000 | 0.812 | 77.5 |
| Steven Sims | WR | ARI | 79 | 90 | -11 | 0.028 | 0.000 | 0.000 | 0.828 | 100.0 |
| Darius Slayton | WR | NYG | 31 | 40 | -9 | 0.105 | 0.021 | 0.040 | 0.474 | 42.9 |
| Marquez Valdes-Scantling | WR | PIT | 48 | 57 | -9 | 0.073 | 0.026 | 0.026 | 0.588 | 87.2 |
| Durham Smythe | TE | CHI | 60 | 69 | -9 | 0.041 | 0.000 | 0.000 | 0.667 | 85.0 |
| David Sills | WR | ATL | 67 | 76 | -9 | 0.051 | 0.000 | 0.000 | 1.000 |  |
| Jared Goff | QB | DET | 6 | 14 | -8 | 0.180 | 0.073 | 0.223 | 0.186 | 100.0 |
| Stefon Diggs | WR | NE | 7 | 15 | -8 | 0.167 | 0.091 | 0.296 | 0.090 | 81.9 |
| DeAndre Hopkins | WR | BAL | 22 | 30 | -8 | 0.158 | 0.094 | 0.150 | 0.238 | 82.1 |
| Demarcus Robinson | WR | SF | 37 | 45 | -8 | 0.094 | 0.018 | 0.074 | 0.483 | 80.1 |
| Dalton Schultz | TE | HOU | 29 | 36 | -7 | 0.108 | 0.039 | 0.135 | 0.299 | 92.7 |
| Mo Alie-Cox | TE | IND | 68 | 75 | -7 | 0.042 | 0.024 | 0.024 | 0.802 | 85.0 |

### Linear Points Top 25 Risers

| Player | Pos | Team | Current | BQML | Delta | xFP share | Elite rate | Spike | Bust | Avail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Joe Flacco | QB | CIN | 86 | 20 | 66 | 0.169 | 0.000 | 0.114 | 0.248 | 100.0 |
| Kirk Cousins | QB | ATL | 70 | 14 | 56 | 0.183 | 0.042 | 0.168 | 0.306 | 100.0 |
| Joshua Dobbs | QB | NE | 66 | 12 | 54 | 0.172 | 0.000 | 0.051 | 0.269 | 100.0 |
| Aaron Rodgers | QB | PIT | 81 | 28 | 53 | 0.121 | 0.020 | 0.020 | 0.431 | 97.5 |
| Mitchell Trubisky | QB | BUF | 87 | 36 | 51 | 0.101 | 0.000 | 0.000 | 0.592 | 100.0 |
| Matthew Stafford | QB | LA | 54 | 6 | 48 | 0.189 | 0.000 | 0.019 | 0.225 | 100.0 |
| Sam Darnold | QB | SEA | 52 | 10 | 42 | 0.155 | 0.019 | 0.019 | 0.411 | 100.0 |
| Jimmy Garoppolo | QB | LA | 64 | 22 | 42 | 0.163 | 0.000 | 0.030 | 0.251 | 100.0 |
| Brandon Allen | QB | TEN | 92 | 55 | 37 | 0.038 | 0.000 | 0.000 | 1.000 |  |
| Baker Mayfield | QB | TB | 33 | 2 | 31 | 0.192 | 0.019 | 0.129 | 0.256 | 86.2 |
| Jacoby Brissett | QB | ARI | 71 | 40 | 31 | 0.140 | 0.000 | 0.024 | 0.548 |  |
| Dak Prescott | QB | DAL | 32 | 5 | 27 | 0.185 | 0.037 | 0.200 | 0.145 | 100.0 |
| Josh Johnson | QB | WAS | 93 | 70 | 23 | 0.030 | 0.000 | 0.000 | 0.750 |  |
| Nick Mullens | QB | JAX | 63 | 43 | 20 | 0.068 | 0.000 | 0.000 | 0.800 |  |
| Cooper Kupp | WR | SEA | 18 | 7 | 11 | 0.179 | 0.310 | 0.418 | 0.260 | 88.8 |
| Drew Sample | TE | CIN | 83 | 73 | 10 | 0.026 | 0.000 | 0.000 | 0.814 | 84.7 |
| Andrew Beck | RB | NYJ | 89 | 80 | 9 | 0.029 | 0.000 | 0.000 | 0.886 |  |
| DJ Moore | WR | CHI | 16 | 11 | 5 | 0.178 | 0.137 | 0.275 | 0.255 | 65.0 |
| Lamar Jackson | QB | BAL | 5 | 1 | 4 | 0.240 | 0.181 | 0.288 | 0.065 | 95.3 |
| Mike Gesicki | TE | CIN | 49 | 45 | 4 | 0.073 | 0.039 | 0.081 | 0.489 | 100.0 |
| Tom Kennedy | WR | DET | 91 | 87 | 4 | 0.033 | 0.000 | 0.000 | 0.900 |  |
| Jared Goff | QB | DET | 6 | 3 | 3 | 0.180 | 0.073 | 0.223 | 0.186 | 100.0 |
| Travis Homer | RB | CHI | 85 | 82 | 3 | 0.033 | 0.000 | 0.000 | 0.933 | 90.8 |
| Keenan Allen | WR | LAC | 10 | 8 | 2 | 0.175 | 0.155 | 0.386 | 0.164 | 68.7 |
| Mike Evans | WR | TB | 11 | 9 | 2 | 0.163 | 0.196 | 0.280 | 0.139 | 81.8 |

### Linear Points Top 25 Fallers

| Player | Pos | Team | Current | BQML | Delta | xFP share | Elite rate | Spike | Bust | Avail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Devin Singletary | RB | NYG | 9 | 44 | -35 | 0.111 | 0.000 | 0.072 | 0.419 | 90.0 |
| Anthony Firkser | TE | DET | 65 | 93 | -28 | 0.025 | 0.000 | 0.000 | 0.667 |  |
| Kareem Hunt | RB | KC | 13 | 37 | -24 | 0.114 | 0.000 | 0.040 | 0.386 | 97.5 |
| Samaje Perine | RB | CIN | 30 | 54 | -24 | 0.072 | 0.018 | 0.035 | 0.605 | 94.3 |
| JuJu Smith-Schuster | WR | KC | 41 | 65 | -24 | 0.075 | 0.018 | 0.076 | 0.513 | 79.7 |
| Scott Miller | WR | PIT | 59 | 83 | -24 | 0.049 | 0.000 | 0.000 | 0.826 | 100.0 |
| Kalif Raymond | WR | DET | 35 | 57 | -22 | 0.059 | 0.000 | 0.000 | 0.643 | 66.7 |
| David Montgomery | RB | DET | 4 | 25 | -21 | 0.157 | 0.020 | 0.148 | 0.124 | 80.3 |
| Justin Watson | WR | HOU | 45 | 66 | -21 | 0.049 | 0.000 | 0.000 | 0.621 | 100.0 |
| Tony Pollard | RB | TEN | 3 | 23 | -20 | 0.162 | 0.037 | 0.150 | 0.192 | 71.9 |
| Austin Hooper | TE | NE | 43 | 63 | -20 | 0.067 | 0.000 | 0.020 | 0.586 | 96.7 |
| Dawson Knox | TE | BUF | 44 | 61 | -17 | 0.068 | 0.020 | 0.020 | 0.382 | 85.2 |
| Durham Smythe | TE | CHI | 60 | 76 | -16 | 0.041 | 0.000 | 0.000 | 0.667 | 85.0 |
| Ashton Dulin | WR | IND | 69 | 85 | -16 | 0.049 | 0.000 | 0.000 | 0.812 | 77.5 |
| Will Dissly | TE | LAC | 46 | 60 | -14 | 0.056 | 0.000 | 0.042 | 0.650 | 79.7 |
| Taysom Hill | TE | NO | 25 | 38 | -13 | 0.105 | 0.104 | 0.167 | 0.354 | 90.8 |
| Hunter Henry | TE | NE | 34 | 47 | -13 | 0.103 | 0.000 | 0.165 | 0.420 | 72.5 |
| Johnny Mundt | TE | JAX | 58 | 71 | -13 | 0.040 | 0.000 | 0.000 | 0.797 | 100.0 |
| Dalton Schultz | TE | HOU | 29 | 41 | -12 | 0.108 | 0.039 | 0.135 | 0.299 | 92.7 |
| Tyler Higbee | TE | LA | 38 | 50 | -12 | 0.111 | 0.021 | 0.062 | 0.317 | 78.8 |
| Christian McCaffrey | RB | SF | 2 | 13 | -11 | 0.234 | 0.201 | 0.338 | 0.000 | 84.1 |
| Darius Slayton | WR | NYG | 31 | 42 | -11 | 0.105 | 0.021 | 0.040 | 0.474 | 42.9 |
| Tyler Conklin | TE | LAC | 40 | 51 | -11 | 0.097 | 0.040 | 0.060 | 0.341 | 80.0 |
| Marquez Valdes-Scantling | WR | PIT | 48 | 59 | -11 | 0.073 | 0.026 | 0.026 | 0.588 | 87.2 |
| Noah Fant | TE | CIN | 42 | 52 | -10 | 0.076 | 0.000 | 0.024 | 0.389 | 91.1 |

## Cutline Crossings

### Logistic Elite

| Cutline | Moved in | Moved out |
| --- | --- | --- |
| QB12 | Joe Flacco (13->10) | Nick Mullens (7->14) |
| RB12 | none | none |
| RB24 | none | none |
| RB36 | none | none |
| WR12 | none | none |
| WR24 | Cedrick Wilson Jr. (25->22) | JuJu Smith-Schuster (20->26) |
| WR36 | none | none |
| TE6 | Jonnu Smith (8->6) | Dalton Schultz (6->7) |
| TE12 | Mike Gesicki (15->11) | Austin Hooper (12->15) |
| overall top 24 | Baker Mayfield (33->11); Dak Prescott (32->23); Joshua Dobbs (66->24) | Devin Singletary (9->29); DeAndre Hopkins (22->30); Tyler Lockett (24->38) |
| overall top 50 | Joshua Dobbs (66->24); Matthew Stafford (54->28); Sam Darnold (52->31); Jimmy Garoppolo (64->32); Kirk Cousins (70->34) | Audric Estimé (50->52); Samaje Perine (30->53); Dawson Knox (44->55); Marquez Valdes-Scantling (48->57); Will Dissly (46->61) |
| overall top 100 | none | none |

### Linear Points

| Cutline | Moved in | Moved out |
| --- | --- | --- |
| QB12 | Joe Flacco (13->9); Mitchell Trubisky (14->12) | Jacoby Brissett (11->13); Nick Mullens (7->14) |
| RB12 | none | none |
| RB24 | none | none |
| RB36 | none | none |
| WR12 | none | none |
| WR24 | Cedrick Wilson Jr. (25->23) | Justin Watson (21->25) |
| WR36 | none | none |
| TE6 | Jonnu Smith (8->5) | Dalton Schultz (6->7) |
| TE12 | Mike Gesicki (15->8) | Austin Hooper (12->15) |
| overall top 24 | Baker Mayfield (33->2); Dak Prescott (32->5); Matthew Stafford (54->6); Sam Darnold (52->10); Joshua Dobbs (66->12) | David Montgomery (4->25); Deebo Samuel Sr. (17->26); DeAndre Hopkins (22->27); Adam Thielen (20->29); Mark Andrews (23->30) |
| overall top 50 | Matthew Stafford (54->6); Sam Darnold (52->10); Joshua Dobbs (66->12); Kirk Cousins (70->14); Joe Flacco (86->20) | Tyler Conklin (40->51); Noah Fant (42->52); Samaje Perine (30->54); Kalif Raymond (35->57); Marquez Valdes-Scantling (48->59) |
| overall top 100 | none | none |

## Risky Movement Notes

- WR movement remains the largest risk. Both BQML boards move several WRs against current Pigskin by more than 20 ranks.
- Logistic elite is aggressive around elite-week rate and xFP share. It can identify upside, but it also creates sharper misses when WR spike outcomes are not explained by available history.
- Linear points is easier to use for board ordering, but its feature explanation remains weaker because Phase 32.24 showed noisy missing-indicator coefficients.
- Injury and availability fields are present as explanation context. They remain risk flags only.
- No Sleeper current context was used. Team labels are historical feature-mart values.

## Logistic Elite Owner Read

Logistic elite is a review-only challenger for top-N utility and bust-control inspection. It should not become the default board because Phase 32.25 showed overall pairwise weakness, and this board still shows sharp WR movement.

## Linear Points Owner Read

Linear points is the better review-only board-ordering challenger. Its early-board movement is more useful for owner review than logistic, but it is not clean enough for champion activation without owner inspection.

## Owner Decision Summary

- Current Pigskin remains the live baseline.
- Both enriched BQML boards are ready for owner review as review-only boards.
- Do not activate a champion from this evidence alone.
- Direct NGS receiving/rushing ingest remains the best feature-signal upgrade if the owner wants better source quality before more modeling.
- Live 2026 context integration should be a separate phase because this board is historical-review evidence.

## Recommended Next Phase

Recommended: Phase 32.27 owner selection of challenger lane. If the owner wants better input signal first, choose direct NGS receiving/rushing ingest. If the owner wants live review boards, choose live 2026 context integration into review rankings.

## Checks Run

- `git status --short`
- BigQuery model existence checks for the two enriched BQML models.
- BigQuery read-only checks for champions, active live rankings, BQML enriched run rows, and BQML enriched summary rows.
- BigQuery read-only `ML.PREDICT` board generation for PPR, Half PPR, Standard, and GNG Keeper.
- `git diff --check`

## No-Live-Change Confirmation

- No live ranking table writes occurred.
- No `analytics_pigskin_rankings` writes occurred.
- `ranking_formula_champions` remains 0.
- No detail rows were written to `ranking_backtest_results`.
- No review-only persistent table was created.
- No deploy occurred.

## Remaining Warnings

- This is a 2025 Week 18 historical-review board, not a live 2026 board.
- WR movement is too risky for default activation.
- Logistic elite remains weak on overall pairwise evidence.
- Linear points remains less explainable than logistic.
- Availability and injury burden remain risk flags only.
