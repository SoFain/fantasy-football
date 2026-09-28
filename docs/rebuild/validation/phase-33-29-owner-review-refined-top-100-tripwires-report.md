# Phase 33.29 Owner Review Of Refined Top-100 Prototype With Tripwires

Final decision: `REFINED TOP-100 READY FOR OWNER REVIEW WITH TRIPWIRES`.

The refined top-100 prototype is acceptable for owner review. It is not approved for live rankings, champion activation, production exposure, or deployment.

## Files Changed

- `docs/rebuild/validation/phase-33-29-owner-review-refined-top-100-tripwires-report.md`
- `docs/rebuild/position-locked-top-100-interleaver-plan.md`
- `docs/rebuild/advanced-bqml-v2-owner-review-boards.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `output/phase-33-29-owner-review-tripwires-evidence.json`

## Git State

The worktree was already dirty with Phase 33 artifacts. This phase did not stage files or revert unrelated work.

- Status rows observed: `27`
- Existing modified source/report files remain outside this owner-review decision unless listed above.

## Board Review Summary

### Standard

- Top 12: 1. Ja'Marr Chase (WR), 2. Christian McCaffrey (RB), 3. Amon-Ra St. Brown (WR), 4. Puka Nacua (WR), 5. Trey McBride (TE), 6. Bijan Robinson (RB), 7. Jahmyr Gibbs (RB), 8. Ashton Jeanty (RB), 9. Jonathan Taylor (RB), 10. CeeDee Lamb (WR), 11. Josh Allen (QB), 12. Brock Bowers (TE)
- Rank 24 cutline: Jayden Daniels (QB3)
- Rank 50 cutline: Rhamondre Stevenson (RB20)
- Rank 100 cutline: Jakobi Meyers (WR35)

| Top N | QB | RB | WR | TE |
| --- | --- | --- | --- | --- |
| 12 | 1 | 5 | 4 | 2 |
| 24 | 3 | 8 | 10 | 3 |
| 50 | 5 | 20 | 18 | 7 |
| 100 | 13 | 38 | 35 | 14 |

Owner-decision note: reviewable with tripwires. Do not activate live without a bounded historical backtest and explicit owner approval.

### Half PPR

- Top 12: 1. Ja'Marr Chase (WR), 2. Christian McCaffrey (RB), 3. Amon-Ra St. Brown (WR), 4. Trey McBride (TE), 5. Bijan Robinson (RB), 6. Jahmyr Gibbs (RB), 7. Ashton Jeanty (RB), 8. CeeDee Lamb (WR), 9. Puka Nacua (WR), 10. Jonathan Taylor (RB), 11. Malik Nabers (WR), 12. Josh Allen (QB)
- Rank 24 cutline: Garrett Wilson (WR12)
- Rank 50 cutline: Nico Collins (WR21)
- Rank 100 cutline: Josh Downs (WR38)

| Top N | QB | RB | WR | TE |
| --- | --- | --- | --- | --- |
| 12 | 1 | 5 | 5 | 1 |
| 24 | 1 | 7 | 12 | 4 |
| 50 | 5 | 16 | 21 | 8 |
| 100 | 13 | 34 | 38 | 15 |

Owner-decision note: reviewable with tripwires. Do not activate live without a bounded historical backtest and explicit owner approval.

### PPR

- Top 12: 1. Christian McCaffrey (RB), 2. Ja'Marr Chase (WR), 3. Bijan Robinson (RB), 4. Jahmyr Gibbs (RB), 5. Amon-Ra St. Brown (WR), 6. Trey McBride (TE), 7. CeeDee Lamb (WR), 8. Puka Nacua (WR), 9. Drake London (WR), 10. Ashton Jeanty (RB), 11. Malik Nabers (WR), 12. Jaxon Smith-Njigba (WR)
- Rank 24 cutline: Garrett Wilson (WR12)
- Rank 50 cutline: Mike Evans (WR21)
- Rank 100 cutline: Xavier Worthy (WR40)

| Top N | QB | RB | WR | TE |
| --- | --- | --- | --- | --- |
| 12 | 0 | 4 | 7 | 1 |
| 24 | 1 | 7 | 12 | 4 |
| 50 | 5 | 16 | 21 | 8 |
| 100 | 13 | 33 | 40 | 14 |

Owner-decision note: reviewable with tripwires. Do not activate live without a bounded historical backtest and explicit owner approval.

### GNG Keeper

- Top 12: 1. Ja'Marr Chase (WR), 2. Christian McCaffrey (RB), 3. Amon-Ra St. Brown (WR), 4. Trey McBride (TE), 5. Bijan Robinson (RB), 6. Jahmyr Gibbs (RB), 7. Ashton Jeanty (RB), 8. Jonathan Taylor (RB), 9. CeeDee Lamb (WR), 10. Puka Nacua (WR), 11. A.J. Brown (WR), 12. Josh Allen (QB)
- Rank 24 cutline: Brock Purdy (QB3)
- Rank 50 cutline: Breece Hall (RB15)
- Rank 100 cutline: Brian Thomas Jr. (WR38)

| Top N | QB | RB | WR | TE |
| --- | --- | --- | --- | --- |
| 12 | 1 | 5 | 5 | 1 |
| 24 | 3 | 8 | 10 | 3 |
| 50 | 8 | 15 | 19 | 8 |
| 100 | 15 | 33 | 38 | 14 |

Owner-decision note: reviewable with tripwires. Do not activate live without a bounded historical backtest and explicit owner approval.

## Top 20 Risers Vs Current Pigskin

| Profile | Player | Pos | Current | Prototype | Delta |
| --- | --- | --- | --- | --- | --- |
| Standard | Chuba Hubbard | RB | 174 | 61 | 113 |
| Standard | Kimani Vidal | RB | 159 | 67 | 92 |
| Standard | DJ Moore | WR | 176 | 87 | 89 |
| Standard | Rachaad White | RB | 169 | 84 | 85 |
| Standard | Isiah Pacheco | RB | 172 | 89 | 83 |
| Standard | Tyrone Tracy Jr. | RB | 144 | 64 | 80 |
| Standard | Alvin Kamara | RB | 140 | 63 | 77 |
| Standard | James Conner | RB | 125 | 57 | 68 |
| Standard | Michael Pittman | WR | 139 | 72 | 67 |
| Standard | Woody Marks | RB | 148 | 83 | 65 |
| Standard | Chris Godwin Jr. | WR | 161 | 98 | 63 |
| Standard | David Njoku | TE | 133 | 71 | 62 |
| Standard | RJ Harvey | RB | 151 | 90 | 61 |
| Standard | Tony Pollard | RB | 116 | 59 | 57 |
| Standard | Jayden Daniels | QB | 80 | 24 | 56 |
| Standard | Rhamondre Stevenson | RB | 104 | 50 | 54 |
| Standard | Aaron Jones | RB | 112 | 58 | 54 |
| Standard | Lamar Jackson | QB | 75 | 23 | 52 |
| Standard | Kenneth Gainwell | RB | 137 | 86 | 51 |
| Standard | Ashton Jeanty | RB | 58 | 8 | 50 |
| Half PPR | Kimani Vidal | RB | 171 | 68 | 103 |
| Half PPR | Woody Marks | RB | 179 | 87 | 92 |
| Half PPR | Michael Pittman | WR | 117 | 35 | 82 |
| Half PPR | Tyrone Tracy Jr. | RB | 151 | 76 | 75 |
| Half PPR | Chuba Hubbard | RB | 140 | 70 | 70 |
| Half PPR | DJ Moore | WR | 152 | 82 | 70 |
| Half PPR | Rachaad White | RB | 154 | 88 | 66 |
| Half PPR | Cam Skattebo | RB | 111 | 47 | 64 |
| Half PPR | Ashton Jeanty | RB | 67 | 7 | 60 |
| Half PPR | James Conner | RB | 120 | 60 | 60 |
| Half PPR | Quinshon Judkins | RB | 106 | 61 | 45 |
| Half PPR | Colston Loveland | TE | 99 | 55 | 44 |
| Half PPR | Chris Godwin Jr. | WR | 138 | 94 | 44 |
| Half PPR | DK Metcalf | WR | 79 | 38 | 41 |
| Half PPR | Alvin Kamara | RB | 115 | 75 | 40 |
| Half PPR | Rico Dowdle | RB | 102 | 63 | 39 |
| Half PPR | Juwan Johnson | TE | 91 | 54 | 37 |
| Half PPR | Brenton Strange | TE | 116 | 80 | 36 |
| Half PPR | Tee Higgins | WR | 56 | 21 | 35 |
| Half PPR | Lamar Jackson | QB | 63 | 28 | 35 |
| PPR | DJ Moore | WR | 173 | 79 | 94 |
| PPR | Michael Pittman | WR | 126 | 42 | 84 |
| PPR | Chuba Hubbard | RB | 167 | 85 | 82 |
| PPR | Alvin Kamara | RB | 143 | 64 | 79 |
| PPR | Tony Pollard | RB | 139 | 65 | 74 |
| PPR | Ashton Jeanty | RB | 79 | 10 | 69 |
| PPR | Woody Marks | RB | 155 | 87 | 68 |
| PPR | Chris Godwin Jr. | WR | 157 | 92 | 65 |
| PPR | Kenneth Walker III | RB | 128 | 69 | 59 |
| PPR | Rhamondre Stevenson | RB | 115 | 60 | 55 |
| PPR | James Conner | RB | 123 | 68 | 55 |
| PPR | Josh Downs | WR | 149 | 96 | 53 |
| PPR | Kenneth Gainwell | RB | 120 | 70 | 50 |
| PPR | Cam Skattebo | RB | 90 | 41 | 49 |
| PPR | Tyrone Tracy Jr. | RB | 131 | 86 | 45 |
| PPR | DK Metcalf | WR | 88 | 47 | 41 |
| PPR | Aaron Jones | RB | 112 | 72 | 40 |
| PPR | Quinshon Judkins | RB | 100 | 61 | 39 |
| PPR | Tee Higgins | WR | 58 | 21 | 37 |
| PPR | Calvin Ridley | WR | 117 | 82 | 35 |
| GNG Keeper | Michael Pittman | WR | 149 | 39 | 110 |
| GNG Keeper | James Conner | RB | 164 | 61 | 103 |
| GNG Keeper | Calvin Ridley | WR | 179 | 85 | 94 |
| GNG Keeper | DJ Moore | WR | 175 | 84 | 91 |
| GNG Keeper | Kimani Vidal | RB | 167 | 81 | 86 |
| GNG Keeper | Chris Godwin Jr. | WR | 166 | 94 | 72 |
| GNG Keeper | DK Metcalf | WR | 109 | 48 | 61 |
| GNG Keeper | Rhamondre Stevenson | RB | 126 | 66 | 60 |
| GNG Keeper | Jaylen Warren | RB | 120 | 68 | 52 |
| GNG Keeper | Tyrone Tracy Jr. | RB | 132 | 82 | 50 |
| GNG Keeper | Ashton Jeanty | RB | 55 | 7 | 48 |
| GNG Keeper | Alvin Kamara | RB | 123 | 75 | 48 |
| GNG Keeper | Woody Marks | RB | 134 | 89 | 45 |
| GNG Keeper | Brian Thomas Jr. | WR | 144 | 100 | 44 |
| GNG Keeper | Tee Higgins | WR | 76 | 33 | 43 |
| GNG Keeper | Mike Evans | WR | 90 | 49 | 41 |
| GNG Keeper | Jerry Jeudy | WR | 130 | 91 | 39 |
| GNG Keeper | Chuba Hubbard | RB | 111 | 74 | 37 |
| GNG Keeper | Derrick Henry | RB | 82 | 47 | 35 |
| GNG Keeper | CeeDee Lamb | WR | 43 | 9 | 34 |

## Top 20 Fallers Vs Current Pigskin

| Profile | Player | Pos | Current | Prototype | Delta |
| --- | --- | --- | --- | --- | --- |
| Standard | Rashee Rice | WR | 15 | 95 | -80 |
| Standard | Tetairoa McMillan | WR | 35 | 99 | -64 |
| Standard | Chris Olave | WR | 13 | 75 | -62 |
| Standard | Dak Prescott | QB | 28 | 80 | -52 |
| Standard | Brock Purdy | QB | 31 | 78 | -47 |
| Standard | Patrick Mahomes | QB | 10 | 53 | -43 |
| Standard | Trevor Lawrence | QB | 38 | 79 | -41 |
| Standard | Jaylen Waddle | WR | 53 | 94 | -41 |
| Standard | Nico Collins | WR | 33 | 73 | -40 |
| Standard | Alec Pierce | WR | 55 | 93 | -38 |
| Standard | Sam LaPorta | TE | 26 | 62 | -36 |
| Standard | Jakobi Meyers | WR | 65 | 100 | -35 |
| Standard | Emeka Egbuka | WR | 60 | 92 | -32 |
| Standard | Caleb Williams | QB | 51 | 82 | -31 |
| Standard | Drake Maye | QB | 9 | 35 | -26 |
| Standard | Dallas Goedert | TE | 43 | 69 | -26 |
| Standard | Bo Nix | QB | 47 | 66 | -19 |
| Standard | Jaxon Smith-Njigba | WR | 1 | 19 | -18 |
| Standard | Dalton Schultz | TE | 63 | 81 | -18 |
| Standard | Courtland Sutton | WR | 57 | 74 | -17 |
| Half PPR | Rashee Rice | WR | 16 | 91 | -75 |
| Half PPR | Tetairoa McMillan | WR | 40 | 98 | -58 |
| Half PPR | Wan'Dale Robinson | WR | 39 | 95 | -56 |
| Half PPR | Brock Purdy | QB | 22 | 77 | -55 |
| Half PPR | Patrick Mahomes | QB | 11 | 64 | -53 |
| Half PPR | Trevor Lawrence | QB | 29 | 79 | -50 |
| Half PPR | Caleb Williams | QB | 41 | 81 | -40 |
| Half PPR | Jaylen Waddle | WR | 53 | 90 | -37 |
| Half PPR | Bo Nix | QB | 36 | 72 | -36 |
| Half PPR | Jakobi Meyers | WR | 62 | 97 | -35 |
| Half PPR | Emeka Egbuka | WR | 61 | 89 | -28 |
| Half PPR | Drake Maye | QB | 8 | 34 | -26 |
| Half PPR | Breece Hall | RB | 23 | 48 | -25 |
| Half PPR | Alec Pierce | WR | 69 | 92 | -23 |
| Half PPR | Dak Prescott | QB | 58 | 78 | -20 |
| Half PPR | Chris Olave | WR | 18 | 37 | -19 |
| Half PPR | Jordan Addison | WR | 78 | 96 | -18 |
| Half PPR | Jaxon Smith-Njigba | WR | 2 | 18 | -16 |
| Half PPR | Travis Etienne | RB | 42 | 58 | -16 |
| Half PPR | Courtland Sutton | WR | 57 | 73 | -16 |
| PPR | Rashee Rice | WR | 17 | 88 | -71 |
| PPR | Brock Purdy | QB | 16 | 75 | -59 |
| PPR | Trevor Lawrence | QB | 21 | 77 | -56 |
| PPR | Tetairoa McMillan | WR | 46 | 97 | -51 |
| PPR | Patrick Mahomes | QB | 9 | 56 | -47 |
| PPR | Wan'Dale Robinson | WR | 45 | 90 | -45 |
| PPR | Dak Prescott | QB | 32 | 76 | -44 |
| PPR | Caleb Williams | QB | 37 | 78 | -41 |
| PPR | Jaylen Waddle | WR | 55 | 89 | -34 |
| PPR | Drake Maye | QB | 7 | 39 | -32 |
| PPR | Alec Pierce | WR | 63 | 93 | -30 |
| PPR | Bo Nix | QB | 40 | 67 | -27 |
| PPR | Jalen Hurts | QB | 12 | 38 | -26 |
| PPR | Chris Olave | WR | 20 | 46 | -26 |
| PPR | Jakobi Meyers | WR | 68 | 94 | -26 |
| PPR | Michael Wilson | WR | 77 | 99 | -22 |
| PPR | Emeka Egbuka | WR | 67 | 84 | -17 |
| PPR | Zay Flowers | WR | 29 | 43 | -14 |
| PPR | Nico Collins | WR | 35 | 49 | -14 |
| PPR | George Pickens | WR | 31 | 44 | -13 |
| GNG Keeper | Rashee Rice | WR | 22 | 96 | -74 |
| GNG Keeper | Jordan Love | QB | 28 | 80 | -52 |
| GNG Keeper | Tetairoa McMillan | WR | 51 | 98 | -47 |
| GNG Keeper | Nico Collins | WR | 47 | 88 | -41 |
| GNG Keeper | Wan'Dale Robinson | WR | 58 | 97 | -39 |
| GNG Keeper | Dak Prescott | QB | 25 | 57 | -32 |
| GNG Keeper | Matthew Stafford | QB | 21 | 51 | -30 |
| GNG Keeper | Lamar Jackson | QB | 54 | 79 | -25 |
| GNG Keeper | Jake Ferguson | TE | 60 | 83 | -23 |
| GNG Keeper | Chris Olave | WR | 24 | 43 | -19 |
| GNG Keeper | Caleb Williams | QB | 33 | 52 | -19 |
| GNG Keeper | Jaylen Waddle | WR | 74 | 93 | -19 |
| GNG Keeper | Jaxon Smith-Njigba | WR | 5 | 21 | -16 |
| GNG Keeper | Patrick Mahomes | QB | 10 | 25 | -15 |
| GNG Keeper | George Pickens | WR | 29 | 42 | -13 |
| GNG Keeper | Dalton Schultz | TE | 49 | 62 | -13 |
| GNG Keeper | DeVonta Smith | WR | 65 | 78 | -13 |
| GNG Keeper | Travis Kelce | TE | 42 | 54 | -12 |
| GNG Keeper | Josh Allen | QB | 1 | 12 | -11 |
| GNG Keeper | Juwan Johnson | TE | 52 | 63 | -11 |

## Gibbs And Refined RB Queue Confirmation

| Profile | Player | Overall | RB Rank | Previous Overall |
| --- | --- | --- | --- | --- |
| Standard | Jahmyr Gibbs | 7 | 3 | 48 |
| Standard | De'Von Achane | 13 | 6 | 46 |
| Standard | Chase Brown | 14 | 7 | 64 |
| Standard | Omarion Hampton | 42 | 12 | None |
| Standard | Cam Skattebo | 46 | 16 | 67 |
| Half PPR | Jahmyr Gibbs | 6 | 3 | 58 |
| Half PPR | De'Von Achane | 13 | 6 | 57 |
| Half PPR | Chase Brown | 14 | 7 | 76 |
| Half PPR | Omarion Hampton | 44 | 12 | None |
| Half PPR | Cam Skattebo | 47 | 15 | 75 |
| PPR | Jahmyr Gibbs | 4 | 3 | 27 |
| PPR | De'Von Achane | 17 | 6 | 35 |
| PPR | Chase Brown | 18 | 7 | 65 |
| PPR | Omarion Hampton | 34 | 12 | None |
| PPR | Cam Skattebo | 41 | 16 | 73 |
| GNG Keeper | Jahmyr Gibbs | 6 | 3 | 60 |
| GNG Keeper | De'Von Achane | 13 | 6 | 59 |
| GNG Keeper | Chase Brown | 14 | 7 | 82 |
| GNG Keeper | Omarion Hampton | 45 | 12 | None |
| GNG Keeper | Cam Skattebo | 58 | 16 | 81 |

- Gibbs is inside RB8 and top 24 overall in every profile.
- Achane and Chase Brown are not buried outside RB24.
- Omarion Hampton and Cam Skattebo remain manual-review prospect-history cases.
- RB tripwire labels are visible in the Phase 33.28 prototype board and evidence JSON.

## Unresolved RB Tripwire Review

| Profile | Player | Tripwire | Source Rank | Prototype RB Rank | Classification | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| Standard | Jeremiyah Love | Market top 6 RB | 4 | 999 | market/prospect lane issue | Owner review allowed, no live use |
| Half PPR | Breece Hall | Current Pigskin top 6 RB | 6 | 16 | stale Current Pigskin context | Owner review allowed, no live use |
| Half PPR | Jeremiyah Love | Market top 6 RB | 4 | 999 | market/prospect lane issue | Owner review allowed, no live use |
| PPR | Jeremiyah Love | Market top 6 RB | 4 | 999 | market/prospect lane issue | Owner review allowed, no live use |
| GNG Keeper | Jeremiyah Love | Market top 6 RB | 4 | 999 | market/prospect lane issue | Owner review allowed, no live use |

Jeremiyah Love decision: keep him as a market-only tripwire. His absence does not block owner review, but it blocks live use until a prospect lane exists or a source-backed active ranking row covers him.

Half PPR Breece Hall decision: Phase 33.27 evidence rank was RB18; current active Pigskin rank is RB6; prototype rank is RB16. This is stale Current Pigskin context, not proof that the refined queue is globally safe. Targeted refresh is required before live approval.

## Current Pigskin Tripwire Review

Total Current Pigskin tripwire warnings reviewed: `39`.

| Profile | Player | Pos | Current Overall | Prototype Rank | Position Queue Rank | Source Queue | Classification | Blocks Prototype |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Standard | Patrick Mahomes | QB | 10 | 53 | 6 | Guarded BQML v2 | interleaver issue | No owner review, yes live use |
| Standard | Rashee Rice | WR | 15 | 95 | 30 | Guarded BQML v2 | position-board issue | No owner review, yes live use |
| Standard | Matthew Stafford | QB | 22 | 101 | outside top 100 | Not in top 100 | interleaver issue | No owner review, yes live use |
| Half PPR | Patrick Mahomes | QB | 11 | 64 | 6 | Guarded BQML v2 | interleaver issue | No owner review, yes live use |
| Half PPR | Rashee Rice | WR | 16 | 91 | 29 | Guarded BQML v2 | position-board issue | No owner review, yes live use |
| Half PPR | Matthew Stafford | QB | 45 | 101 | outside top 100 | Not in top 100 | interleaver issue | No |
| PPR | Patrick Mahomes | QB | 9 | 56 | 6 | Guarded BQML v2 | interleaver issue | No owner review, yes live use |
| PPR | Rashee Rice | WR | 17 | 88 | 28 | Guarded BQML v2 | position-board issue | No owner review, yes live use |
| PPR | Matthew Stafford | QB | 25 | 101 | outside top 100 | Not in top 100 | interleaver issue | No |
| GNG Keeper | Matthew Stafford | QB | 21 | 51 | 9 | Current Pigskin held board | interleaver issue | No owner review, yes live use |
| GNG Keeper | Rashee Rice | WR | 22 | 96 | 34 | Guarded BQML v2 | position-board issue | No owner review, yes live use |

Patrick Mahomes is an interleaver issue: the prototype is too willing to push elite QBs into later overall slots. Rashee Rice is a position-board issue: the guarded WR queue disagrees sharply with Current Pigskin. Matthew Stafford is a Standard QB depth warning. These do not block owner review, but they block live use.

## Severe Warning Classifications

| Profile | Player | Pos | Current Overall | Prototype Rank | Position Queue Rank | Source Queue | Classification | Blocks Prototype |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Standard | Jaxon Smith-Njigba | WR | 1 | 19 | 8 | Guarded BQML v2 | position-board issue | No owner review, yes live use |
| Standard | Drake Maye | QB | 9 | 35 | 5 | Guarded BQML v2 | interleaver issue | No owner review, yes live use |
| Standard | Patrick Mahomes | QB | 10 | 53 | 6 | Guarded BQML v2 | interleaver issue | No owner review, yes live use |
| Standard | Chris Olave | WR | 13 | 75 | 22 | Guarded BQML v2 | position-board issue | No owner review, yes live use |
| Standard | Rashee Rice | WR | 15 | 95 | 30 | Guarded BQML v2 | position-board issue | No owner review, yes live use |
| Standard | Matthew Stafford | QB | 22 | 101 | outside top 100 | Not in top 100 | interleaver issue | No owner review, yes live use |
| Standard | Jordan Love | QB | 25 | 101 | outside top 100 | Not in top 100 | interleaver issue | No |
| Standard | Tetairoa McMillan | WR | 35 | 99 | 34 | Guarded BQML v2 | position-board issue | No |
| Standard | Wan'Dale Robinson | WR | 37 | 101 | outside top 100 | Not in top 100 | position-board issue | No |
| Standard | Daniel Jones | QB | 42 | 101 | outside top 100 | Not in top 100 | interleaver issue | No |
| Standard | Rome Odunze | WR | 44 | 101 | outside top 100 | Not in top 100 | position-board issue | No |
| Half PPR | Drake Maye | QB | 8 | 34 | 5 | Guarded BQML v2 | interleaver issue | No owner review, yes live use |
| Half PPR | Patrick Mahomes | QB | 11 | 64 | 6 | Guarded BQML v2 | interleaver issue | No owner review, yes live use |
| Half PPR | Rashee Rice | WR | 16 | 91 | 29 | Guarded BQML v2 | position-board issue | No owner review, yes live use |
| Half PPR | Brock Purdy | QB | 22 | 77 | 9 | Guarded BQML v2 | interleaver issue | No owner review, yes live use |
| Half PPR | Daniel Jones | QB | 32 | 101 | outside top 100 | Not in top 100 | interleaver issue | No |
| Half PPR | Wan'Dale Robinson | WR | 39 | 95 | 33 | Guarded BQML v2 | position-board issue | No |
| Half PPR | Tetairoa McMillan | WR | 40 | 98 | 36 | Guarded BQML v2 | position-board issue | No |
| Half PPR | Caleb Williams | QB | 41 | 81 | 12 | Guarded BQML v2 | interleaver issue | No |
| Half PPR | Matthew Stafford | QB | 45 | 101 | outside top 100 | Not in top 100 | interleaver issue | No |
| Half PPR | Rome Odunze | WR | 48 | 101 | outside top 100 | Not in top 100 | position-board issue | No |
| Half PPR | Justin Herbert | QB | 50 | 101 | outside top 100 | Not in top 100 | interleaver issue | No |
| PPR | Drake Maye | QB | 7 | 39 | 5 | Guarded BQML v2 | interleaver issue | No owner review, yes live use |
| PPR | Patrick Mahomes | QB | 9 | 56 | 6 | Guarded BQML v2 | interleaver issue | No owner review, yes live use |
| PPR | Jalen Hurts | QB | 12 | 38 | 4 | Guarded BQML v2 | manual review required | No owner review, yes live use |
| PPR | Brock Purdy | QB | 16 | 75 | 9 | Guarded BQML v2 | interleaver issue | No owner review, yes live use |
| PPR | Rashee Rice | WR | 17 | 88 | 28 | Guarded BQML v2 | position-board issue | No owner review, yes live use |
| PPR | Trevor Lawrence | QB | 21 | 77 | 11 | Guarded BQML v2 | interleaver issue | No owner review, yes live use |
| PPR | Matthew Stafford | QB | 25 | 101 | outside top 100 | Not in top 100 | interleaver issue | No |
| PPR | Jordan Love | QB | 30 | 101 | outside top 100 | Not in top 100 | interleaver issue | No |
| PPR | Daniel Jones | QB | 43 | 101 | outside top 100 | Not in top 100 | interleaver issue | No |
| PPR | Wan'Dale Robinson | WR | 45 | 90 | 30 | Guarded BQML v2 | position-board issue | No |
| PPR | Tetairoa McMillan | WR | 46 | 97 | 37 | Guarded BQML v2 | position-board issue | No |
| PPR | Justin Herbert | QB | 47 | 101 | outside top 100 | Not in top 100 | interleaver issue | No |
| PPR | Rome Odunze | WR | 49 | 101 | outside top 100 | Not in top 100 | position-board issue | No |
| GNG Keeper | Jaxon Smith-Njigba | WR | 5 | 21 | 8 | Guarded BQML v2 | position-board issue | No owner review, yes live use |
| GNG Keeper | Matthew Stafford | QB | 21 | 51 | 9 | Current Pigskin held board | interleaver issue | No owner review, yes live use |
| GNG Keeper | Rashee Rice | WR | 22 | 96 | 34 | Guarded BQML v2 | position-board issue | No owner review, yes live use |
| GNG Keeper | Nico Collins | WR | 47 | 88 | 27 | Guarded BQML v2 | position-board issue | No |

## Remaining Blockers

- Live use remains blocked.
- Bounded historical backtest is required before any top-100 activation decision.
- Jeremiyah Love requires a prospect lane or explicit owner rejection of market-only prospect influence.
- Half PPR Breece Hall requires targeted stale-context refresh before approval beyond owner review.
- Mahomes and other QB tripwires require interleaver review before live use.
- Rashee Rice and several WR warnings require position-board review before live use.

## Required Backtest

A bounded historical backtest is required before live use. Phase 33.29 is owner-review classification only and does not recompute points captured, VOR captured, NDCG, pairwise win rate, or pick-band regret.

## Checks Run

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract` | PASS, 26 tests |
| `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py` | PASS |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | PASS, discovered 251 validation files |
| Focused owner-review checks | PASS |
| Focused top-100/RB tripwire checks | PASS |
| `git diff --check` | PASS with existing LF-to-CRLF warning on `docs/rebuild/bqml-v2-positional-formula-finalists.md` |

## Safety Confirmations

- No live ranking writes.
- No champion activation.
- No model training.
- No deployment.
- No Gemini call.
- No Pigskin chat call.
- No 2026 outcomes used.
- Route metrics remain blocked/null.
- No market data used as a training target.

## Recommended Next Phase

Phase 33.30: Bounded historical backtest of the refined top-100, with a companion targeted tripwire cleanup plan for Jeremiyah Love, Half PPR Breece Hall, Patrick Mahomes, and Rashee Rice.
