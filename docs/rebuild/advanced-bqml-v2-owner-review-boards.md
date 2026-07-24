# Advanced BQML v2 Owner-Review Boards

This document presents the owner-review boards comparing **Current Pigskin** rankings against the **Phase 33.18C Advanced BQML v2 Finalists** and alternates where applicable. Guardrails have been applied to protect against rookie, low-history, and sparse-feature artifacts.

## Phase 33.31 Owner-Review Status

Phase 33.31 keeps these boards in owner-review mode only. Current Pigskin remains the live baseline.

Key findings:

- QB cleanup needs explicit Current Pigskin anchor/cap review for Mahomes, Purdy, Trevor Lawrence, Caleb Williams, and selected Jordan Love profile cases.
- WR cleanup needs an elite WR anchor plus a source-backed demotion rule. Rashee Rice's WR30-ish demotion was not supported by two source-backed concerns.
- Breece Hall still needs a targeted Half PPR stale-context refresh before live use.
- Jeremiyah Love is a market-only prospect. He should remain outside official top-100 output until a prospect watch lane exists or the owner rejects market-only prospects.
- `Marvin Harrison Jr.` requires exact identity/display verification because Phase 33.31 evidence returned `Marvin Harrison`.

Do not treat Phase 33.31 cleanup candidates as champion activation or live-ranking approval.

## Phase 33.32 Standard RB Formula Sprint

Phase 33.32 produced an episode-only Standard RB formula concept: `standard_rb_elite_receiving_back_protection_v0`.

Owner-review status: not ready. The formula improved 2024 validation top-12 hit rate and pairwise draft win rate, but the 2025 holdout slice was thin and Current Pigskin still held on NDCG and pairwise. Treat it as a transparent discussion formula, not a replacement board.

## Guardrail Legend
- **ROOKIE_NO_HISTORY**: Player is a true rookie/prospect with no prior NFL stats; rank is anchored to Current Pigskin.
- **LOW_HISTORY**: Player has stats history but fewer than 10 historical games; rank is anchored to Current Pigskin.
- **PROSPECT_HISTORY**: Player has stats history for only a single season (e.g., 2025) or mismatched career rows; allowed model-based rank movement but flagged with manual review if inside top 150 overall.
- **HISTORY_JOIN_FAILED**: Player is an established veteran whose advanced stats join failed; rank is anchored to Current Pigskin.
- **CURRENT_PIGSKIN_ANCHOR**: Player's review rank is locked to their Current Pigskin rank due to guardrail triggers.
- **MANUAL_REVIEW_REQUIRED**: Rookie/low-history player inside overall top-150 range, or a player with major guarded movement (> 15 ranks).
- **SPARSE_FEATURES / SPARSE_UPWARD_CAP**: Player missing > 50% advanced features; upward rank movement capped at +10.
- **MODEL_DISAGREEMENT_LOCK**: Finalist and alternate ranks diverge by > 20 ranks; rank anchored to Current Pigskin (disabled for QBs).
- **QB_RUSHING_BIAS_WARNING**: QB elevated primarily by rushing profile with weak passing EPA/CPOE context.
- **STANDARD_TE_FLOOR**: Standard TE protected from downward rank demotion below Current Pigskin.
- **RB_POINTS_SANITY_CHECK_WARNING**: Half PPR VOR rank diverges from Alternate Points rank by > 10.

## Overall Manual Review List

| Player | Team | Position | Profile | Current Pigskin Rank | Reason |
|---|---|---|---|---|---|
| Bryce Young | CAR | QB | standard | 21 | Major guarded movement of -16 ranks (Pigskin=21 -> Guarded=37) |
| Aaron Rodgers | PIT | QB | standard | 22 | Major guarded movement of -19 ranks (Pigskin=22 -> Guarded=41) |
| Justin Fields | KC | QB | standard | 32 | Major guarded movement of +16 ranks (Pigskin=32 -> Guarded=16) |
| Chase Brown | CIN | RB | standard | 6 | Major guarded movement of -25 ranks (Pigskin=6 -> Guarded=31) |
| Omarion Hampton | LAC | RB | standard | 10 | Prospect with single-season/mismatched history inside overall top-150 range (RB10) |
| Ashton Jeanty | LV | RB | standard | 12 | Prospect with single-season/mismatched history inside overall top-150 range (RB12) |
| Cam Skattebo | NYG | RB | standard | 15 | Low-history player (games=8) inside overall top-150 range (RB15) |
| Derrick Henry | BAL | RB | standard | 20 | Major guarded movement of +18 ranks (Pigskin=20 -> Guarded=2) |
| Quinshon Judkins | CLE | RB | standard | 22 | Prospect with single-season/mismatched history inside overall top-150 range (RB22) |
| Zach Charbonnet | SEA | RB | standard | 26 | Major guarded movement of -19 ranks (Pigskin=26 -> Guarded=45) |
| Kenneth Gainwell | TB | RB | standard | 28 | Major guarded movement of -20 ranks (Pigskin=28 -> Guarded=48) |
| Aaron Jones | MIN | RB | standard | 30 | Major guarded movement of +16 ranks (Pigskin=30 -> Guarded=14) |
| Tony Pollard | TEN | RB | standard | 32 | Major guarded movement of +20 ranks (Pigskin=32 -> Guarded=12) |
| TreVeyon Henderson | NE | RB | standard | 33 | Prospect with single-season/mismatched history inside overall top-150 range (RB33) |
| Woody Marks | HOU | RB | standard | 34 | Prospect with single-season/mismatched history inside overall top-150 range (RB34) |
| RJ Harvey | DEN | RB | standard | 35 | Prospect with single-season/mismatched history inside overall top-150 range (RB35) |
| Trey Benson | ARI | RB | standard | 36 | Major guarded movement of -30 ranks (Pigskin=36 -> Guarded=66) |
| Kyle Monangai | CHI | RB | standard | 38 | Prospect with single-season/mismatched history inside overall top-150 range (RB38) |
| Chuba Hubbard | CAR | RB | standard | 42 | Major guarded movement of +33 ranks (Pigskin=42 -> Guarded=9) |
| Jacory Croskey-Merritt | WAS | RB | standard | 45 | Prospect with single-season/mismatched history inside overall top-150 range (RB45) |
| Chris Rodriguez Jr. | JAX | RB | standard | 48 | Major guarded movement of -21 ranks (Pigskin=48 -> Guarded=69) |
| Devin Singletary | NYG | RB | standard | 52 | Major guarded movement of +19 ranks (Pigskin=52 -> Guarded=33) |
| Emanuel Wilson | SEA | RB | standard | 54 | Major guarded movement of -23 ranks (Pigskin=54 -> Guarded=77) |
| Jaylen Wright | MIA | RB | standard | 56 | Major guarded movement of -31 ranks (Pigskin=56 -> Guarded=87) |
| Jeremy McNichols | WAS | RB | standard | 64 | Major guarded movement of -33 ranks (Pigskin=64 -> Guarded=97) |
| Braelon Allen | NYJ | RB | standard | 65 | Major guarded movement of -19 ranks (Pigskin=65 -> Guarded=84) |
| Keaton Mitchell | LAC | RB | standard | 66 | Major guarded movement of -41 ranks (Pigskin=66 -> Guarded=107) |
| Brian Robinson | ATL | RB | standard | 70 | Major guarded movement of +18 ranks (Pigskin=70 -> Guarded=52) |
| Jerome Ford | WAS | RB | standard | 73 | Major guarded movement of +30 ranks (Pigskin=73 -> Guarded=43) |
| Malik Davis | DAL | RB | standard | 74 | Major guarded movement of -19 ranks (Pigskin=74 -> Guarded=93) |
| Ray Davis | BUF | RB | standard | 77 | Major guarded movement of +40 ranks (Pigskin=77 -> Guarded=37) |
| Jaleel McLaughlin | DEN | RB | standard | 80 | Major guarded movement of -19 ranks (Pigskin=80 -> Guarded=99) |
| Rashee Rice | KC | WR | standard | 7 | Major guarded movement of -24 ranks (Pigskin=7 -> Guarded=31) |
| Tetairoa McMillan | CAR | WR | standard | 16 | Prospect with single-season/mismatched history inside overall top-150 range (WR16) |
| Wan'Dale Robinson | TEN | WR | standard | 17 | Major guarded movement of -22 ranks (Pigskin=17 -> Guarded=39) |
| Rome Odunze | CHI | WR | standard | 19 | Major guarded movement of -22 ranks (Pigskin=19 -> Guarded=41) |
| Emeka Egbuka | TB | WR | standard | 26 | Prospect with single-season/mismatched history inside overall top-150 range (WR26) |
| Jameson Williams | DET | WR | standard | 27 | Major guarded movement of -23 ranks (Pigskin=27 -> Guarded=50) |
| Quentin Johnston | LAC | WR | standard | 30 | Major guarded movement of -22 ranks (Pigskin=30 -> Guarded=52) |
| Christian Watson | GB | WR | standard | 32 | Major guarded movement of -29 ranks (Pigskin=32 -> Guarded=61) |
| Marvin Harrison | ARI | WR | standard | 34 | Prospect with single-season/mismatched history inside overall top-150 range (WR34) |
| DK Metcalf | PIT | WR | standard | 35 | Major guarded movement of +19 ranks (Pigskin=35 -> Guarded=16) |
| Jauan Jennings | MIN | WR | standard | 38 | Major guarded movement of -16 ranks (Pigskin=38 -> Guarded=54) |
| Tre Tucker | LV | WR | standard | 39 | Major guarded movement of -16 ranks (Pigskin=39 -> Guarded=55) |
| Ricky Pearsall | SF | WR | standard | 41 | Major guarded movement of -29 ranks (Pigskin=41 -> Guarded=70) |
| Troy Franklin | DEN | WR | standard | 42 | Major guarded movement of -33 ranks (Pigskin=42 -> Guarded=75) |
| Elic Ayomanor | TEN | WR | standard | 44 | Prospect with single-season/mismatched history inside overall top-150 range (WR44) |
| Calvin Ridley | TEN | WR | standard | 46 | Major guarded movement of +19 ranks (Pigskin=46 -> Guarded=27) |
| Travis Hunter | JAX | WR | standard | 52 | Low-history player (games=7) inside overall top-150 range (WR52) |
| Michael Pittman | PIT | WR | standard | 54 | Major guarded movement of +35 ranks (Pigskin=54 -> Guarded=19) |
| Jakobie Keeney-James | GB | WR | standard | 55 | Low-history player (games=1) inside overall top-150 range (WR55) |
| Chris Godwin Jr. | TB | WR | standard | 62 | Major guarded movement of +28 ranks (Pigskin=62 -> Guarded=34) |
| Devaughn Vele | NO | WR | standard | 64 | Major guarded movement of -18 ranks (Pigskin=64 -> Guarded=82) |
| Van Jefferson | WAS | WR | standard | 66 | Major guarded movement of -29 ranks (Pigskin=66 -> Guarded=95) |
| Jayden Higgins | HOU | WR | standard | 68 | Prospect with single-season/mismatched history inside overall top-150 range (WR68) |
| DJ Moore | BUF | WR | standard | 69 | Major guarded movement of +44 ranks (Pigskin=69 -> Guarded=25) |
| Adonai Mitchell | NYJ | WR | standard | 70 | Major guarded movement of -38 ranks (Pigskin=70 -> Guarded=108) |
| Tyquan Thornton | KC | WR | standard | 72 | Major guarded movement of -39 ranks (Pigskin=72 -> Guarded=111) |
| Olamide Zaccheaus | ATL | WR | standard | 74 | Major guarded movement of -38 ranks (Pigskin=74 -> Guarded=112) |
| Ryan Flournoy | DAL | WR | standard | 78 | Major guarded movement of -24 ranks (Pigskin=78 -> Guarded=102) |
| Xavier Hutchinson | HOU | WR | standard | 82 | Major guarded movement of -40 ranks (Pigskin=82 -> Guarded=122) |
| Rashod Bateman | BAL | WR | standard | 83 | Major guarded movement of +17 ranks (Pigskin=83 -> Guarded=66) |
| Christian Kirk | SF | WR | standard | 90 | Major guarded movement of +34 ranks (Pigskin=90 -> Guarded=56) |
| Treylon Burks | WAS | WR | standard | 92 | Major guarded movement of -26 ranks (Pigskin=92 -> Guarded=118) |
| Tyler Warren | IND | TE | standard | 6 | Prospect with single-season/mismatched history inside overall top-150 range (TE6) |
| Colston Loveland | CHI | TE | standard | 13 | Prospect with single-season/mismatched history inside overall top-150 range (TE13) |
| Harold Fannin Jr. | CLE | TE | standard | 16 | Prospect with single-season/mismatched history inside overall top-150 range (TE16) |
| Mason Taylor | NYJ | TE | standard | 19 | Prospect with single-season/mismatched history inside overall top-150 range (TE19) |
| Oronde Gadsden II | LAC | TE | standard | 20 | Prospect with single-season/mismatched history inside overall top-150 range (TE20) |
| David Njoku | LAC | TE | standard | 29 | Major guarded movement of +19 ranks (Pigskin=29 -> Guarded=10) |
| Bryce Young | CAR | QB | half_ppr | 21 | Major guarded movement of -16 ranks (Pigskin=21 -> Guarded=37) |
| Aaron Rodgers | PIT | QB | half_ppr | 22 | Major guarded movement of -20 ranks (Pigskin=22 -> Guarded=42) |
| Justin Fields | KC | QB | half_ppr | 32 | Major guarded movement of +16 ranks (Pigskin=32 -> Guarded=16) |
| Jahmyr Gibbs | DET | RB | half_ppr | 3 | Major guarded movement of -16 ranks (Pigskin=3 -> Guarded=19) |
| Chase Brown | CIN | RB | half_ppr | 6 | Major guarded movement of -26 ranks (Pigskin=6 -> Guarded=32) |
| Omarion Hampton | LAC | RB | half_ppr | 10 | Prospect with single-season/mismatched history inside overall top-150 range (RB10) |
| Ashton Jeanty | LV | RB | half_ppr | 11 | Prospect with single-season/mismatched history inside overall top-150 range (RB11) |
| Cam Skattebo | NYG | RB | half_ppr | 15 | Low-history player (games=8) inside overall top-150 range (RB15) |
| Derrick Henry | BAL | RB | half_ppr | 20 | Major guarded movement of +18 ranks (Pigskin=20 -> Guarded=2) |
| Quinshon Judkins | CLE | RB | half_ppr | 22 | Prospect with single-season/mismatched history inside overall top-150 range (RB22) |
| Kenneth Gainwell | TB | RB | half_ppr | 26 | Major guarded movement of -23 ranks (Pigskin=26 -> Guarded=49) |
| Zach Charbonnet | SEA | RB | half_ppr | 29 | Major guarded movement of -16 ranks (Pigskin=29 -> Guarded=45) |
| Aaron Jones | MIN | RB | half_ppr | 30 | Major guarded movement of +19 ranks (Pigskin=30 -> Guarded=11) |
| TreVeyon Henderson | NE | RB | half_ppr | 33 | Prospect with single-season/mismatched history inside overall top-150 range (RB33) |
| Woody Marks | HOU | RB | half_ppr | 34 | Prospect with single-season/mismatched history inside overall top-150 range (RB34) |
| RJ Harvey | DEN | RB | half_ppr | 35 | Prospect with single-season/mismatched history inside overall top-150 range (RB35) |
| Trey Benson | ARI | RB | half_ppr | 36 | Major guarded movement of -32 ranks (Pigskin=36 -> Guarded=68) |
| Kimani Vidal | LAC | RB | half_ppr | 37 | Major guarded movement of +25 ranks (Pigskin=37 -> Guarded=12) |
| Kyle Monangai | CHI | RB | half_ppr | 38 | Prospect with single-season/mismatched history inside overall top-150 range (RB38) |
| Chuba Hubbard | CAR | RB | half_ppr | 43 | Major guarded movement of +34 ranks (Pigskin=43 -> Guarded=9) |
| Jacory Croskey-Merritt | WAS | RB | half_ppr | 45 | Prospect with single-season/mismatched history inside overall top-150 range (RB45) |
| Chris Rodriguez Jr. | JAX | RB | half_ppr | 48 | Major guarded movement of -23 ranks (Pigskin=48 -> Guarded=71) |
| Tyler Allgeier | ARI | RB | half_ppr | 49 | Major guarded movement of -23 ranks (Pigskin=49 -> Guarded=72) |
| Devin Singletary | NYG | RB | half_ppr | 53 | Major guarded movement of +16 ranks (Pigskin=53 -> Guarded=37) |
| Emanuel Wilson | SEA | RB | half_ppr | 54 | Major guarded movement of -24 ranks (Pigskin=54 -> Guarded=78) |
| Jaylen Wright | MIA | RB | half_ppr | 56 | Major guarded movement of -45 ranks (Pigskin=56 -> Guarded=101) |
| Justice Hill | BAL | RB | half_ppr | 61 | Major guarded movement of +17 ranks (Pigskin=61 -> Guarded=44) |
| Kendre Miller | NO | RB | half_ppr | 63 | Major guarded movement of -16 ranks (Pigskin=63 -> Guarded=79) |
| Jeremy McNichols | WAS | RB | half_ppr | 64 | Major guarded movement of -28 ranks (Pigskin=64 -> Guarded=92) |
| Braelon Allen | NYJ | RB | half_ppr | 65 | Major guarded movement of -18 ranks (Pigskin=65 -> Guarded=83) |
| Keaton Mitchell | LAC | RB | half_ppr | 67 | Major guarded movement of -47 ranks (Pigskin=67 -> Guarded=114) |
| Brian Robinson | ATL | RB | half_ppr | 70 | Major guarded movement of +17 ranks (Pigskin=70 -> Guarded=53) |
| Jerome Ford | WAS | RB | half_ppr | 72 | Major guarded movement of +30 ranks (Pigskin=72 -> Guarded=42) |
| Malik Davis | DAL | RB | half_ppr | 74 | Major guarded movement of -24 ranks (Pigskin=74 -> Guarded=98) |
| Ray Davis | BUF | RB | half_ppr | 77 | Major guarded movement of +44 ranks (Pigskin=77 -> Guarded=33) |
| Jaleel McLaughlin | DEN | RB | half_ppr | 79 | Major guarded movement of -29 ranks (Pigskin=79 -> Guarded=108) |
| Rashee Rice | KC | WR | half_ppr | 7 | Major guarded movement of -23 ranks (Pigskin=7 -> Guarded=30) |
| Wan'Dale Robinson | TEN | WR | half_ppr | 16 | Major guarded movement of -18 ranks (Pigskin=16 -> Guarded=34) |
| Tetairoa McMillan | CAR | WR | half_ppr | 17 | Prospect with single-season/mismatched history inside overall top-150 range (WR17) |
| Rome Odunze | CHI | WR | half_ppr | 19 | Major guarded movement of -24 ranks (Pigskin=19 -> Guarded=43) |
| Emeka Egbuka | TB | WR | half_ppr | 26 | Prospect with single-season/mismatched history inside overall top-150 range (WR26) |
| Jameson Williams | DET | WR | half_ppr | 28 | Major guarded movement of -23 ranks (Pigskin=28 -> Guarded=51) |
| Quentin Johnston | LAC | WR | half_ppr | 31 | Major guarded movement of -22 ranks (Pigskin=31 -> Guarded=53) |
| Christian Watson | GB | WR | half_ppr | 32 | Major guarded movement of -29 ranks (Pigskin=32 -> Guarded=61) |
| DK Metcalf | PIT | WR | half_ppr | 34 | Major guarded movement of +16 ranks (Pigskin=34 -> Guarded=18) |
| Marvin Harrison | ARI | WR | half_ppr | 35 | Prospect with single-season/mismatched history inside overall top-150 range (WR35) |
| Jauan Jennings | MIN | WR | half_ppr | 37 | Major guarded movement of -17 ranks (Pigskin=37 -> Guarded=54) |
| Tre Tucker | LV | WR | half_ppr | 39 | Major guarded movement of -16 ranks (Pigskin=39 -> Guarded=55) |
| Ricky Pearsall | SF | WR | half_ppr | 41 | Major guarded movement of -31 ranks (Pigskin=41 -> Guarded=72) |
| Troy Franklin | DEN | WR | half_ppr | 42 | Major guarded movement of -34 ranks (Pigskin=42 -> Guarded=76) |
| Elic Ayomanor | TEN | WR | half_ppr | 44 | Prospect with single-season/mismatched history inside overall top-150 range (WR44) |
| Calvin Ridley | TEN | WR | half_ppr | 46 | Major guarded movement of +21 ranks (Pigskin=46 -> Guarded=25) |
| Travis Hunter | JAX | WR | half_ppr | 51 | Low-history player (games=7) inside overall top-150 range (WR51) |
| Michael Pittman | PIT | WR | half_ppr | 52 | Major guarded movement of +37 ranks (Pigskin=52 -> Guarded=15) |
| Mack Hollins | NE | WR | half_ppr | 53 | Major guarded movement of -18 ranks (Pigskin=53 -> Guarded=71) |
| Jakobie Keeney-James | GB | WR | half_ppr | 55 | Low-history player (games=1) inside overall top-150 range (WR55) |
| Josh Downs | IND | WR | half_ppr | 59 | Major guarded movement of +19 ranks (Pigskin=59 -> Guarded=40) |
| Chris Godwin Jr. | TB | WR | half_ppr | 62 | Major guarded movement of +29 ranks (Pigskin=62 -> Guarded=33) |
| Devaughn Vele | NO | WR | half_ppr | 64 | Major guarded movement of -16 ranks (Pigskin=64 -> Guarded=80) |
| Van Jefferson | WAS | WR | half_ppr | 66 | Major guarded movement of -34 ranks (Pigskin=66 -> Guarded=100) |
| Jayden Higgins | HOU | WR | half_ppr | 68 | Prospect with single-season/mismatched history inside overall top-150 range (WR68) |
| DJ Moore | BUF | WR | half_ppr | 69 | Major guarded movement of +46 ranks (Pigskin=69 -> Guarded=23) |
| Adonai Mitchell | NYJ | WR | half_ppr | 70 | Major guarded movement of -36 ranks (Pigskin=70 -> Guarded=106) |
| Tyquan Thornton | KC | WR | half_ppr | 73 | Major guarded movement of -46 ranks (Pigskin=73 -> Guarded=119) |
| Olamide Zaccheaus | ATL | WR | half_ppr | 74 | Major guarded movement of -33 ranks (Pigskin=74 -> Guarded=107) |
| Ryan Flournoy | DAL | WR | half_ppr | 78 | Major guarded movement of -16 ranks (Pigskin=78 -> Guarded=94) |
| Calvin Austin III | NYG | WR | half_ppr | 79 | Major guarded movement of -17 ranks (Pigskin=79 -> Guarded=96) |
| Xavier Hutchinson | HOU | WR | half_ppr | 82 | Major guarded movement of -42 ranks (Pigskin=82 -> Guarded=124) |
| Rashod Bateman | BAL | WR | half_ppr | 83 | Major guarded movement of +16 ranks (Pigskin=83 -> Guarded=67) |
| DeMario Douglas | NE | WR | half_ppr | 89 | Major guarded movement of +20 ranks (Pigskin=89 -> Guarded=69) |
| Christian Kirk | SF | WR | half_ppr | 90 | Major guarded movement of +34 ranks (Pigskin=90 -> Guarded=56) |
| Treylon Burks | WAS | WR | half_ppr | 93 | Major guarded movement of -28 ranks (Pigskin=93 -> Guarded=121) |
| Bryce Young | CAR | QB | ppr | 21 | Major guarded movement of -16 ranks (Pigskin=21 -> Guarded=37) |
| Aaron Rodgers | PIT | QB | ppr | 22 | Major guarded movement of -20 ranks (Pigskin=22 -> Guarded=42) |
| Justin Fields | KC | QB | ppr | 32 | Major guarded movement of +16 ranks (Pigskin=32 -> Guarded=16) |
| Chase Brown | CIN | RB | ppr | 6 | Major guarded movement of -19 ranks (Pigskin=6 -> Guarded=25) |
| Omarion Hampton | LAC | RB | ppr | 10 | Prospect with single-season/mismatched history inside overall top-150 range (RB10) |
| Ashton Jeanty | LV | RB | ppr | 11 | Prospect with single-season/mismatched history inside overall top-150 range (RB11) |
| Cam Skattebo | NYG | RB | ppr | 15 | Low-history player (games=8) inside overall top-150 range (RB15) |
| Quinshon Judkins | CLE | RB | ppr | 22 | Prospect with single-season/mismatched history inside overall top-150 range (RB22) |
| Rico Dowdle | PIT | RB | ppr | 23 | Major guarded movement of -19 ranks (Pigskin=23 -> Guarded=42) |
| Kenneth Gainwell | TB | RB | ppr | 24 | Major guarded movement of -27 ranks (Pigskin=24 -> Guarded=51) |
| Tony Pollard | TEN | RB | ppr | 32 | Major guarded movement of +22 ranks (Pigskin=32 -> Guarded=10) |
| TreVeyon Henderson | NE | RB | ppr | 33 | Prospect with single-season/mismatched history inside overall top-150 range (RB33) |
| Woody Marks | HOU | RB | ppr | 34 | Prospect with single-season/mismatched history inside overall top-150 range (RB34) |
| RJ Harvey | DEN | RB | ppr | 35 | Prospect with single-season/mismatched history inside overall top-150 range (RB35) |
| Trey Benson | ARI | RB | ppr | 36 | Major guarded movement of -23 ranks (Pigskin=36 -> Guarded=59) |
| Kyle Monangai | CHI | RB | ppr | 39 | Prospect with single-season/mismatched history inside overall top-150 range (RB39) |
| Chuba Hubbard | CAR | RB | ppr | 43 | Major guarded movement of +31 ranks (Pigskin=43 -> Guarded=12) |
| Jacory Croskey-Merritt | WAS | RB | ppr | 45 | Prospect with single-season/mismatched history inside overall top-150 range (RB45) |
| Devin Singletary | NYG | RB | ppr | 53 | Major guarded movement of +19 ranks (Pigskin=53 -> Guarded=34) |
| Emanuel Wilson | SEA | RB | ppr | 54 | Major guarded movement of -29 ranks (Pigskin=54 -> Guarded=83) |
| Jaylen Wright | MIA | RB | ppr | 58 | Major guarded movement of -17 ranks (Pigskin=58 -> Guarded=75) |
| Justice Hill | BAL | RB | ppr | 61 | Major guarded movement of +17 ranks (Pigskin=61 -> Guarded=44) |
| Jeremy McNichols | WAS | RB | ppr | 64 | Major guarded movement of -30 ranks (Pigskin=64 -> Guarded=94) |
| Braelon Allen | NYJ | RB | ppr | 66 | Major guarded movement of -16 ranks (Pigskin=66 -> Guarded=82) |
| Keaton Mitchell | LAC | RB | ppr | 67 | Major guarded movement of -41 ranks (Pigskin=67 -> Guarded=108) |
| Jerome Ford | WAS | RB | ppr | 70 | Major guarded movement of +31 ranks (Pigskin=70 -> Guarded=39) |
| Brian Robinson | ATL | RB | ppr | 71 | Major guarded movement of +25 ranks (Pigskin=71 -> Guarded=46) |
| Malik Davis | DAL | RB | ppr | 74 | Major guarded movement of -21 ranks (Pigskin=74 -> Guarded=95) |
| Ray Davis | BUF | RB | ppr | 77 | Major guarded movement of +21 ranks (Pigskin=77 -> Guarded=56) |
| Rashee Rice | KC | WR | ppr | 7 | Major guarded movement of -22 ranks (Pigskin=7 -> Guarded=29) |
| Tetairoa McMillan | CAR | WR | ppr | 17 | Prospect with single-season/mismatched history inside overall top-150 range (WR17) |
| Rome Odunze | CHI | WR | ppr | 19 | Major guarded movement of -24 ranks (Pigskin=19 -> Guarded=43) |
| Emeka Egbuka | TB | WR | ppr | 26 | Prospect with single-season/mismatched history inside overall top-150 range (WR26) |
| Jameson Williams | DET | WR | ppr | 28 | Major guarded movement of -23 ranks (Pigskin=28 -> Guarded=51) |
| Quentin Johnston | LAC | WR | ppr | 31 | Major guarded movement of -23 ranks (Pigskin=31 -> Guarded=54) |
| Christian Watson | GB | WR | ppr | 32 | Major guarded movement of -30 ranks (Pigskin=32 -> Guarded=62) |
| DK Metcalf | PIT | WR | ppr | 34 | Major guarded movement of +16 ranks (Pigskin=34 -> Guarded=18) |
| Marvin Harrison | ARI | WR | ppr | 35 | Prospect with single-season/mismatched history inside overall top-150 range (WR35) |
| Tre Tucker | LV | WR | ppr | 39 | Major guarded movement of -16 ranks (Pigskin=39 -> Guarded=55) |
| Ricky Pearsall | SF | WR | ppr | 41 | Major guarded movement of -31 ranks (Pigskin=41 -> Guarded=72) |
| Troy Franklin | DEN | WR | ppr | 42 | Major guarded movement of -32 ranks (Pigskin=42 -> Guarded=74) |
| Elic Ayomanor | TEN | WR | ppr | 45 | Prospect with single-season/mismatched history inside overall top-150 range (WR45) |
| Calvin Ridley | TEN | WR | ppr | 47 | Major guarded movement of +22 ranks (Pigskin=47 -> Guarded=25) |
| Keon Coleman | BUF | WR | ppr | 48 | Major guarded movement of -16 ranks (Pigskin=48 -> Guarded=64) |
| Michael Pittman | PIT | WR | ppr | 51 | Major guarded movement of +38 ranks (Pigskin=51 -> Guarded=13) |
| Travis Hunter | JAX | WR | ppr | 52 | Low-history player (games=7) inside overall top-150 range (WR52) |
| Mack Hollins | NE | WR | ppr | 53 | Major guarded movement of -22 ranks (Pigskin=53 -> Guarded=75) |
| Jakobie Keeney-James | GB | WR | ppr | 55 | Low-history player (games=1) inside overall top-150 range (WR55) |
| Josh Downs | IND | WR | ppr | 59 | Major guarded movement of +21 ranks (Pigskin=59 -> Guarded=38) |
| Chris Godwin Jr. | TB | WR | ppr | 62 | Major guarded movement of +29 ranks (Pigskin=62 -> Guarded=33) |
| Devaughn Vele | NO | WR | ppr | 64 | Major guarded movement of -16 ranks (Pigskin=64 -> Guarded=80) |
| Van Jefferson | WAS | WR | ppr | 66 | Major guarded movement of -36 ranks (Pigskin=66 -> Guarded=102) |
| Jayden Higgins | HOU | WR | ppr | 68 | Prospect with single-season/mismatched history inside overall top-150 range (WR68) |
| DJ Moore | BUF | WR | ppr | 69 | Major guarded movement of +46 ranks (Pigskin=69 -> Guarded=23) |
| Adonai Mitchell | NYJ | WR | ppr | 70 | Major guarded movement of -38 ranks (Pigskin=70 -> Guarded=108) |
| Tyquan Thornton | KC | WR | ppr | 73 | Major guarded movement of -48 ranks (Pigskin=73 -> Guarded=121) |
| Olamide Zaccheaus | ATL | WR | ppr | 74 | Major guarded movement of -33 ranks (Pigskin=74 -> Guarded=107) |
| Calvin Austin III | NYG | WR | ppr | 79 | Major guarded movement of -18 ranks (Pigskin=79 -> Guarded=97) |
| Xavier Hutchinson | HOU | WR | ppr | 82 | Major guarded movement of -43 ranks (Pigskin=82 -> Guarded=125) |
| DeMario Douglas | NE | WR | ppr | 89 | Major guarded movement of +24 ranks (Pigskin=89 -> Guarded=65) |
| Christian Kirk | SF | WR | ppr | 90 | Major guarded movement of +33 ranks (Pigskin=90 -> Guarded=57) |
| Treylon Burks | WAS | WR | ppr | 93 | Major guarded movement of -30 ranks (Pigskin=93 -> Guarded=123) |
| Chase Brown | CIN | RB | gng_keeper | 6 | Major guarded movement of -26 ranks (Pigskin=6 -> Guarded=32) |
| Omarion Hampton | LAC | RB | gng_keeper | 10 | Prospect with single-season/mismatched history inside overall top-150 range (RB10) |
| Ashton Jeanty | LV | RB | gng_keeper | 11 | Prospect with single-season/mismatched history inside overall top-150 range (RB11) |
| Cam Skattebo | NYG | RB | gng_keeper | 15 | Low-history player (games=8) inside overall top-150 range (RB15) |
| Jaylen Warren | PIT | RB | gng_keeper | 19 | Major guarded movement of -18 ranks (Pigskin=19 -> Guarded=37) |
| Derrick Henry | BAL | RB | gng_keeper | 20 | Major guarded movement of +18 ranks (Pigskin=20 -> Guarded=2) |
| Quinshon Judkins | CLE | RB | gng_keeper | 22 | Prospect with single-season/mismatched history inside overall top-150 range (RB22) |
| Zach Charbonnet | SEA | RB | gng_keeper | 25 | Major guarded movement of -18 ranks (Pigskin=25 -> Guarded=43) |
| Kenneth Gainwell | TB | RB | gng_keeper | 27 | Major guarded movement of -22 ranks (Pigskin=27 -> Guarded=49) |
| Aaron Jones | MIN | RB | gng_keeper | 29 | Major guarded movement of +17 ranks (Pigskin=29 -> Guarded=12) |
| Tony Pollard | TEN | RB | gng_keeper | 32 | Major guarded movement of +17 ranks (Pigskin=32 -> Guarded=15) |
| TreVeyon Henderson | NE | RB | gng_keeper | 33 | Prospect with single-season/mismatched history inside overall top-150 range (RB33) |
| Woody Marks | HOU | RB | gng_keeper | 34 | Prospect with single-season/mismatched history inside overall top-150 range (RB34) |
| RJ Harvey | DEN | RB | gng_keeper | 35 | Prospect with single-season/mismatched history inside overall top-150 range (RB35) |
| Trey Benson | ARI | RB | gng_keeper | 36 | Major guarded movement of -32 ranks (Pigskin=36 -> Guarded=68) |
| Kimani Vidal | LAC | RB | gng_keeper | 37 | Major guarded movement of +17 ranks (Pigskin=37 -> Guarded=20) |
| Kyle Monangai | CHI | RB | gng_keeper | 38 | Prospect with single-season/mismatched history inside overall top-150 range (RB38) |
| Chuba Hubbard | CAR | RB | gng_keeper | 42 | Major guarded movement of +33 ranks (Pigskin=42 -> Guarded=9) |
| Jacory Croskey-Merritt | WAS | RB | gng_keeper | 45 | Prospect with single-season/mismatched history inside overall top-150 range (RB45) |
| Chris Rodriguez Jr. | JAX | RB | gng_keeper | 48 | Major guarded movement of -19 ranks (Pigskin=48 -> Guarded=67) |
| Devin Singletary | NYG | RB | gng_keeper | 52 | Major guarded movement of +19 ranks (Pigskin=52 -> Guarded=33) |
| Emanuel Wilson | SEA | RB | gng_keeper | 54 | Major guarded movement of -21 ranks (Pigskin=54 -> Guarded=75) |
| Jaylen Wright | MIA | RB | gng_keeper | 56 | Major guarded movement of -33 ranks (Pigskin=56 -> Guarded=89) |
| Jeremy McNichols | WAS | RB | gng_keeper | 64 | Major guarded movement of -32 ranks (Pigskin=64 -> Guarded=96) |
| Braelon Allen | NYJ | RB | gng_keeper | 65 | Major guarded movement of -19 ranks (Pigskin=65 -> Guarded=84) |
| Keaton Mitchell | LAC | RB | gng_keeper | 66 | Major guarded movement of -42 ranks (Pigskin=66 -> Guarded=108) |
| Brian Robinson | ATL | RB | gng_keeper | 71 | Major guarded movement of +19 ranks (Pigskin=71 -> Guarded=52) |
| Jerome Ford | WAS | RB | gng_keeper | 72 | Major guarded movement of +28 ranks (Pigskin=72 -> Guarded=44) |
| Malik Davis | DAL | RB | gng_keeper | 74 | Major guarded movement of -19 ranks (Pigskin=74 -> Guarded=93) |
| Ray Davis | BUF | RB | gng_keeper | 77 | Major guarded movement of +43 ranks (Pigskin=77 -> Guarded=34) |
| Ameer Abdullah | JAX | RB | gng_keeper | 80 | Major guarded movement of +26 ranks (Pigskin=80 -> Guarded=54) |
| Rashee Rice | KC | WR | gng_keeper | 7 | Major guarded movement of -29 ranks (Pigskin=7 -> Guarded=36) |
| Tetairoa McMillan | CAR | WR | gng_keeper | 16 | Prospect with single-season/mismatched history inside overall top-150 range (WR16) |
| Wan'Dale Robinson | TEN | WR | gng_keeper | 17 | Major guarded movement of -20 ranks (Pigskin=17 -> Guarded=37) |
| Rome Odunze | CHI | WR | gng_keeper | 19 | Major guarded movement of -22 ranks (Pigskin=19 -> Guarded=41) |
| Emeka Egbuka | TB | WR | gng_keeper | 26 | Prospect with single-season/mismatched history inside overall top-150 range (WR26) |
| Jameson Williams | DET | WR | gng_keeper | 29 | Major guarded movement of -20 ranks (Pigskin=29 -> Guarded=49) |
| Quentin Johnston | LAC | WR | gng_keeper | 30 | Major guarded movement of -22 ranks (Pigskin=30 -> Guarded=52) |
| Christian Watson | GB | WR | gng_keeper | 32 | Major guarded movement of -29 ranks (Pigskin=32 -> Guarded=61) |
| Marvin Harrison | ARI | WR | gng_keeper | 34 | Prospect with single-season/mismatched history inside overall top-150 range (WR34) |
| DK Metcalf | PIT | WR | gng_keeper | 35 | Major guarded movement of +17 ranks (Pigskin=35 -> Guarded=18) |
| Jauan Jennings | MIN | WR | gng_keeper | 36 | Major guarded movement of -20 ranks (Pigskin=36 -> Guarded=56) |
| Ricky Pearsall | SF | WR | gng_keeper | 41 | Major guarded movement of -32 ranks (Pigskin=41 -> Guarded=73) |
| Troy Franklin | DEN | WR | gng_keeper | 43 | Major guarded movement of -31 ranks (Pigskin=43 -> Guarded=74) |
| Elic Ayomanor | TEN | WR | gng_keeper | 44 | Prospect with single-season/mismatched history inside overall top-150 range (WR44) |
| Calvin Ridley | TEN | WR | gng_keeper | 46 | Major guarded movement of +22 ranks (Pigskin=46 -> Guarded=24) |
| Travis Hunter | JAX | WR | gng_keeper | 51 | Low-history player (games=7) inside overall top-150 range (WR51) |
| Jakobie Keeney-James | GB | WR | gng_keeper | 54 | Low-history player (games=1) inside overall top-150 range (WR54) |
| Michael Pittman | PIT | WR | gng_keeper | 55 | Major guarded movement of +41 ranks (Pigskin=55 -> Guarded=14) |
| Josh Downs | IND | WR | gng_keeper | 59 | Major guarded movement of +16 ranks (Pigskin=59 -> Guarded=43) |
| Chris Godwin Jr. | TB | WR | gng_keeper | 62 | Major guarded movement of +28 ranks (Pigskin=62 -> Guarded=34) |
| Devaughn Vele | NO | WR | gng_keeper | 63 | Major guarded movement of -20 ranks (Pigskin=63 -> Guarded=83) |
| Jayden Higgins | HOU | WR | gng_keeper | 68 | Prospect with single-season/mismatched history inside overall top-150 range (WR68) |
| DJ Moore | BUF | WR | gng_keeper | 70 | Major guarded movement of +47 ranks (Pigskin=70 -> Guarded=23) |
| Tyquan Thornton | KC | WR | gng_keeper | 72 | Major guarded movement of -38 ranks (Pigskin=72 -> Guarded=110) |
| Olamide Zaccheaus | ATL | WR | gng_keeper | 74 | Major guarded movement of -40 ranks (Pigskin=74 -> Guarded=114) |
| Ryan Flournoy | DAL | WR | gng_keeper | 77 | Major guarded movement of -32 ranks (Pigskin=77 -> Guarded=109) |
| Xavier Hutchinson | HOU | WR | gng_keeper | 82 | Major guarded movement of -39 ranks (Pigskin=82 -> Guarded=121) |
| Rashod Bateman | BAL | WR | gng_keeper | 83 | Major guarded movement of +18 ranks (Pigskin=83 -> Guarded=65) |
| Christian Kirk | SF | WR | gng_keeper | 89 | Major guarded movement of +32 ranks (Pigskin=89 -> Guarded=57) |
| Treylon Burks | WAS | WR | gng_keeper | 92 | Major guarded movement of -25 ranks (Pigskin=92 -> Guarded=117) |
| John Metchie III | CAR | WR | gng_keeper | 100 | Major guarded movement of -16 ranks (Pigskin=100 -> Guarded=116) |

---

## STANDARD PROFILE BOARDS

### QB Board — Status: **Accepted with guardrails**

- **Finalist Model**: `ranking_bqml_v2_adv_standard_qb_logistic_bust_advanced_v0`
- **Alternate Model**: `ranking_bqml_v2_adv_standard_qb_linear_points_advanced_v0` *(REJECTED/HIDDEN due to rushing bias)*

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 32 | 0 | 0 | 5 | 3 | 0 | 0 | 0 | 4 | 1 | 4 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Josh Allen | BUF | 1 | 1 | 1 | 0 | 0 | 0% | NONE |
| Drake Maye | NE | 2 | 5 | 5 | -3 | -3 | 0% | NONE |
| Patrick Mahomes | KC | 3 | 6 | 6 | -3 | -3 | 0% | NONE |
| Brock Purdy | SF | 4 | 9 | 9 | -5 | -5 | 0% | NONE |
| Jalen Hurts | PHI | 5 | 4 | 4 | +1 | +1 | 0% | NONE |
| Trevor Lawrence | JAX | 6 | 10 | 10 | -4 | -4 | 0% | NONE |
| Daniel Jones | IND | 7 | 14 | 14 | -7 | -7 | 0% | NONE |
| Bo Nix | DEN | 8 | 8 | 8 | 0 | 0 | 0% | NONE |
| Caleb Williams | CHI | 9 | 12 | 12 | -3 | -3 | 0% | NONE |
| Matthew Stafford | LAR | 10 | 22 | 22 | -12 | -12 | 0% | NONE |
| Justin Herbert | LAC | 11 | 15 | 15 | -4 | -4 | 0% | NONE |
| Jayden Daniels | WAS | 12 | 3 | 3 | +9 | +9 | 0% | NONE |
| Dak Prescott | DAL | 13 | 11 | 11 | +2 | +2 | 0% | NONE |
| Lamar Jackson | BAL | 14 | 2 | 2 | +12 | +12 | 0% | NONE |
| Jordan Love | GB | 15 | 20 | 20 | -5 | -5 | 0% | NONE |
| Jaxson Dart | NYG | 16 | 7 | 7 | +9 | +9 | 0% | PROSPECT_HISTORY |
| Jared Goff | DET | 17 | 18 | 18 | -1 | -1 | 0% | NONE |
| Kyler Murray | MIN | 18 | 13 | 13 | +5 | +5 | 0% | QB_RUSHING_BIAS_WARNING |
| C.J. Stroud | HOU | 19 | 24 | 24 | -5 | -5 | 0% | NONE |
| Tyler Shough | NO | 20 | 21 | 21 | -1 | -1 | 0% | PROSPECT_HISTORY |
| Bryce Young | CAR | 21 | 37 | 37 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED |
| Aaron Rodgers | PIT | 22 | 41 | 41 | -19 | -19 | 0% | MANUAL_REVIEW_REQUIRED |
| Baker Mayfield | TB | 23 | 17 | 17 | +6 | +6 | 0% | NONE |
| Joe Burrow | CIN | 24 | 19 | 19 | +5 | +5 | 0% | NONE |
| Jacoby Brissett | ARI | 25 | 28 | 28 | -3 | -3 | 0% | NONE |
| Malik Willis | MIA | 26 | 23 | 23 | +3 | +3 | 0% | NONE |
| Sam Darnold | SEA | 27 | 25 | 25 | +2 | +2 | 0% | NONE |
| Geno Smith | NYJ | 28 | 30 | 30 | -2 | -2 | 0% | NONE |
| Tua Tagovailoa | ATL | 29 | 27 | 27 | +2 | +2 | 0% | NONE |
| Shedeur Sanders | CLE | 30 | 49 | 30 | -19 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Cam Ward | TEN | 31 | 54 | 54 | -23 | -23 | 0% | PROSPECT_HISTORY |
| Justin Fields | KC | 32 | 16 | 16 | +16 | +16 | 0% | QB_RUSHING_BIAS_WARNING, MANUAL_REVIEW_REQUIRED |
| Carson Wentz | MIN | 33 | 26 | 33 | +7 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Marcus Mariota | WAS | 34 | 34 | 34 | 0 | 0 | 0% | NONE |
| J.J. McCarthy | MIN | 35 | 40 | 40 | -5 | -5 | 0% | PROSPECT_HISTORY |
| Spencer Rattler | NO | 36 | 43 | 43 | -7 | -7 | 0% | NONE |
| Jake Browning | TB | 37 | 50 | 50 | -13 | -13 | 0% | NONE |
| Mac Jones | SF | 38 | 36 | 36 | +2 | +2 | 0% | NONE |
| Tyler Huntley | BAL | 39 | 29 | 29 | +10 | +10 | 0% | NONE |
| Joe Flacco | CIN | 40 | 46 | 46 | -6 | -6 | 0% | NONE |
| Fernando Mendoza | LV | 41 | 95 | 41 | -54 | 0 | 100% | HISTORY_JOIN_FAILED, CURRENT_PIGSKIN_ANCHOR |
| Davis Mills | HOU | 42 | 52 | 52 | -10 | -10 | 0% | NONE |
| Josh Johnson | CIN | 43 | 44 | 43 | -1 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Jameis Winston | NYG | 44 | 31 | 31 | +13 | +13 | 0% | NONE |
| Quinn Ewers | MIA | 45 | 57 | 45 | -12 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |

#### Movement Tables (QB)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Justin Fields | KC | 32 | 16 | +16 | Passing EPA/dropback: -0.16, Passing CPOE: -15.33 |
| Jameis Winston | NYG | 44 | 31 | +13 | Passing EPA/dropback: -0.02, Passing CPOE: -9.79 |
| Lamar Jackson | BAL | 14 | 2 | +12 | Passing EPA/dropback: 0.17, Passing CPOE: 5.44 |
| Tyler Huntley | BAL | 39 | 29 | +10 | Passing EPA/dropback: 0.01, Passing CPOE: 7.45 |
| Jayden Daniels | WAS | 12 | 3 | +9 | Passing EPA/dropback: 0.12, Passing CPOE: 1.60 |
| Jaxson Dart | NYG | 16 | 7 | +9 | Passing EPA/dropback: 0.01, Passing CPOE: -0.56 |
| Baker Mayfield | TB | 23 | 17 | +6 | Passing EPA/dropback: 0.25, Passing CPOE: 3.62 |
| Kyler Murray | MIN | 18 | 13 | +5 | Passing EPA/dropback: 0.03, Passing CPOE: 0.08 |
| Joe Burrow | CIN | 24 | 19 | +5 | Passing EPA/dropback: 0.11, Passing CPOE: 4.16 |
| Malik Willis | MIA | 26 | 23 | +3 | Passing EPA/dropback: 0.36, Passing CPOE: 10.90 |
| Dak Prescott | DAL | 13 | 11 | +2 | Passing EPA/dropback: 0.08, Passing CPOE: 2.11 |
| Sam Darnold | SEA | 27 | 25 | +2 | Passing EPA/dropback: -0.05, Passing CPOE: 1.28 |
| Tua Tagovailoa | ATL | 29 | 27 | +2 | Passing EPA/dropback: 0.03, Passing CPOE: -1.43 |
| Mac Jones | SF | 38 | 36 | +2 | Passing EPA/dropback: -0.17, Passing CPOE: -4.23 |
| Jalen Hurts | PHI | 5 | 4 | +1 | Passing EPA/dropback: 0.07, Passing CPOE: 3.94 |

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Cam Ward | TEN | 31 | 54 | -23 | Passing EPA/dropback: -0.20, Passing CPOE: -1.86 |
| Aaron Rodgers | PIT | 22 | 41 | -19 | Passing EPA/dropback: -0.69, Passing CPOE: -3.40 |
| Bryce Young | CAR | 21 | 37 | -16 | Passing EPA/dropback: -0.15, Passing CPOE: -1.18 |
| Jake Browning | TB | 37 | 50 | -13 | Passing EPA/dropback: -0.11, Passing CPOE: 2.42 |
| Matthew Stafford | LAR | 10 | 22 | -12 | Passing EPA/dropback: 0.21, Passing CPOE: 0.22 |
| Davis Mills | HOU | 42 | 52 | -10 | Passing EPA/dropback: -0.39, Passing CPOE: -2.44 |
| Daniel Jones | IND | 7 | 14 | -7 | Passing EPA/dropback: -0.11, Passing CPOE: 0.61 |
| Spencer Rattler | NO | 36 | 43 | -7 | Passing EPA/dropback: -0.21, Passing CPOE: -3.75 |
| Joe Flacco | CIN | 40 | 46 | -6 | Passing EPA/dropback: -0.12, Passing CPOE: 0.70 |
| Brock Purdy | SF | 4 | 9 | -5 | Passing EPA/dropback: 0.16, Passing CPOE: 2.12 |
| Jordan Love | GB | 15 | 20 | -5 | Passing EPA/dropback: 0.20, Passing CPOE: 1.59 |
| C.J. Stroud | HOU | 19 | 24 | -5 | Passing EPA/dropback: 0.02, Passing CPOE: -1.28 |
| J.J. McCarthy | MIN | 35 | 40 | -5 | Passing EPA/dropback: -0.22, Passing CPOE: -4.80 |
| Trevor Lawrence | JAX | 6 | 10 | -4 | Passing EPA/dropback: 0.03, Passing CPOE: -1.74 |
| Justin Herbert | LAC | 11 | 15 | -4 | Passing EPA/dropback: -0.18, Passing CPOE: -4.24 |

---

### RB Board — Status: **Accepted**

- **Finalist Model**: `ranking_bqml_v2_adv_standard_rb_linear_points_advanced_v0`
- **Alternate Model**: `ranking_bqml_v2_adv_standard_rb_logistic_bust_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 39 | 0 | 0 | 10 | 29 | 0 | 0 | 0 | 10 | 0 | 11 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels | Alt Rank | Finalist/Alternate Disagreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Christian McCaffrey | SF | 1 | 5 | 5 | -4 | -4 | 0% | NONE | 6 | -1 |
| Bijan Robinson | ATL | 2 | 3 | 3 | -1 | -1 | 0% | NONE | 2 | +1 |
| Jahmyr Gibbs | DET | 3 | 18 | 18 | -15 | -15 | 0% | NONE | 9 | +9 |
| Jonathan Taylor | IND | 4 | 4 | 4 | 0 | 0 | 0% | NONE | 1 | +3 |
| De'Von Achane | MIA | 5 | 16 | 16 | -11 | -11 | 0% | NONE | 15 | +1 |
| Chase Brown | CIN | 6 | 31 | 31 | -25 | -25 | 0% | MANUAL_REVIEW_REQUIRED | 20 | +11 |
| Javonte Williams | DAL | 7 | 20 | 20 | -13 | -13 | 0% | NONE | 16 | +4 |
| Kyren Williams | LAR | 8 | 7 | 7 | +1 | +1 | 0% | NONE | 7 | 0 |
| Saquon Barkley | PHI | 9 | 1 | 1 | +8 | +8 | 0% | NONE | 3 | -2 |
| Omarion Hampton | LAC | 10 | 56 | 56 | -46 | -46 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 50 | +6 |
| James Cook | BUF | 11 | 24 | 24 | -13 | -13 | 0% | NONE | 22 | +2 |
| Ashton Jeanty | LV | 12 | 6 | 6 | +6 | +6 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 5 | +1 |
| Josh Jacobs | GB | 13 | 15 | 15 | -2 | -2 | 0% | NONE | 10 | +5 |
| Travis Etienne | NO | 14 | 25 | 25 | -11 | -11 | 0% | NONE | 11 | +14 |
| Cam Skattebo | NYG | 15 | 32 | 15 | -17 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR, MANUAL_REVIEW_REQUIRED | 28 | +4 |
| Bucky Irving | TB | 16 | 29 | 29 | -13 | -13 | 0% | NONE | 25 | +4 |
| D'Andre Swift | CHI | 17 | 19 | 19 | -2 | -2 | 0% | NONE | 23 | -4 |
| Breece Hall | NYJ | 18 | 8 | 8 | +10 | +10 | 0% | NONE | 8 | 0 |
| Jaylen Warren | PIT | 19 | 34 | 34 | -15 | -15 | 0% | NONE | 37 | -3 |
| Derrick Henry | BAL | 20 | 2 | 2 | +18 | +18 | 0% | MANUAL_REVIEW_REQUIRED | 4 | -2 |
| Rhamondre Stevenson | NE | 21 | 17 | 17 | +4 | +4 | 0% | NONE | 21 | -4 |
| Quinshon Judkins | CLE | 22 | 11 | 11 | +11 | +11 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 13 | -2 |
| Rico Dowdle | PIT | 23 | 38 | 38 | -15 | -15 | 0% | NONE | 41 | -3 |
| J.K. Dobbins | DEN | 24 | 27 | 27 | -3 | -3 | 0% | NONE | 31 | -4 |
| James Conner | ARI | 25 | 13 | 13 | +12 | +12 | 0% | NONE | 18 | -5 |
| Zach Charbonnet | SEA | 26 | 45 | 45 | -19 | -19 | 0% | MANUAL_REVIEW_REQUIRED | 36 | +9 |
| Kenneth Walker III | KC | 27 | 21 | 21 | +6 | +6 | 0% | NONE | 17 | +4 |
| Kenneth Gainwell | TB | 28 | 48 | 48 | -20 | -20 | 0% | MANUAL_REVIEW_REQUIRED | 53 | -5 |
| Alvin Kamara | NO | 29 | 23 | 23 | +6 | +6 | 0% | NONE | 19 | +4 |
| Aaron Jones | MIN | 30 | 14 | 14 | +16 | +16 | 0% | MANUAL_REVIEW_REQUIRED | 24 | -10 |
| Tyrone Tracy Jr. | NYG | 31 | 26 | 26 | +5 | +5 | 0% | NONE | 27 | -1 |
| Tony Pollard | TEN | 32 | 12 | 12 | +20 | +20 | 0% | MANUAL_REVIEW_REQUIRED | 12 | 0 |
| TreVeyon Henderson | NE | 33 | 55 | 55 | -22 | -22 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 52 | +3 |
| Woody Marks | HOU | 34 | 28 | 28 | +6 | +6 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 30 | -2 |
| RJ Harvey | DEN | 35 | 42 | 42 | -7 | -7 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 38 | +4 |
| Trey Benson | ARI | 36 | 66 | 66 | -30 | -30 | 0% | MANUAL_REVIEW_REQUIRED | 65 | +1 |
| Kimani Vidal | LAC | 37 | 22 | 22 | +15 | +15 | 0% | NONE | 42 | -20 |
| Kyle Monangai | CHI | 38 | 41 | 41 | -3 | -3 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 39 | +2 |
| David Montgomery | HOU | 39 | 39 | 39 | 0 | 0 | 0% | NONE | 32 | +7 |
| Rachaad White | WAS | 40 | 30 | 30 | +10 | +10 | 0% | NONE | 29 | +1 |
| Isiah Pacheco | DET | 41 | 35 | 35 | +6 | +6 | 0% | NONE | 34 | +1 |
| Chuba Hubbard | CAR | 42 | 9 | 9 | +33 | +33 | 0% | MANUAL_REVIEW_REQUIRED | 14 | -5 |
| Tyjae Spears | TEN | 43 | 49 | 49 | -6 | -6 | 0% | NONE | 44 | +5 |
| Michael Carter | TEN | 44 | 57 | 57 | -13 | -13 | 0% | NONE | 58 | -1 |
| Jacory Croskey-Merritt | WAS | 45 | 44 | 44 | +1 | +1 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 26 | +18 |
| Jordan Mason | MIN | 46 | 40 | 40 | +6 | +6 | 0% | NONE | 33 | +7 |
| Jawhar Jordan | HOU | 47 | 36 | 47 | +11 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 47 | -11 |
| Chris Rodriguez Jr. | JAX | 48 | 69 | 69 | -21 | -21 | 0% | MANUAL_REVIEW_REQUIRED | 51 | +18 |
| Tyler Allgeier | ARI | 49 | 59 | 59 | -10 | -10 | 0% | NONE | 40 | +19 |
| Blake Corum | LAR | 50 | 62 | 62 | -12 | -12 | 0% | NONE | 63 | -1 |
| Raheim Sanders | CLE | 51 | 65 | 51 | -14 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 66 | -1 |
| Devin Singletary | NYG | 52 | 33 | 33 | +19 | +19 | 0% | MANUAL_REVIEW_REQUIRED | 35 | -2 |
| Devin Neal | NO | 53 | 51 | 53 | +2 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 60 | -9 |
| Emanuel Wilson | SEA | 54 | 77 | 77 | -23 | -23 | 0% | MANUAL_REVIEW_REQUIRED | 81 | -4 |
| Samaje Perine | CIN | 55 | 61 | 61 | -6 | -6 | 0% | NONE | 68 | -7 |
| Jaylen Wright | MIA | 56 | 87 | 87 | -31 | -31 | 0% | MANUAL_REVIEW_REQUIRED | 71 | +16 |
| Phil Mafah | DAL | 57 | 88 | 57 | -31 | 0 | 31% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 91 | -3 |
| Dylan Sampson | CLE | 58 | 75 | 75 | -17 | -17 | 15% | PROSPECT_HISTORY | 79 | -4 |
| Ty Johnson | BUF | 59 | 68 | 68 | -9 | -9 | 0% | NONE | 64 | +4 |
| Bhayshul Tuten | JAX | 60 | 53 | 53 | +7 | +7 | 0% | PROSPECT_HISTORY | 49 | +4 |
| Justice Hill | BAL | 61 | 47 | 47 | +14 | +14 | 0% | NONE | 48 | -1 |
| Jaret Patterson | LAC | 62 | 73 | 62 | -11 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 77 | -4 |
| Kendre Miller | NO | 63 | 76 | 76 | -13 | -13 | 0% | NONE | 78 | -2 |
| Jeremy McNichols | WAS | 64 | 97 | 97 | -33 | -33 | 31% | MANUAL_REVIEW_REQUIRED | 95 | +2 |
| Braelon Allen | NYJ | 65 | 84 | 84 | -19 | -19 | 0% | MANUAL_REVIEW_REQUIRED | 82 | +2 |
| Keaton Mitchell | LAC | 66 | 107 | 107 | -41 | -41 | 15% | MANUAL_REVIEW_REQUIRED | 109 | -2 |
| Emari Demercado | KC | 67 | 58 | 58 | +9 | +9 | 0% | NONE | 69 | -11 |
| Jaydon Blue | DAL | 68 | 64 | 68 | +4 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 72 | -8 |
| Isaiah Davis | NYJ | 69 | 78 | 78 | -9 | -9 | 8% | NONE | 75 | +3 |
| Brian Robinson | ATL | 70 | 52 | 52 | +18 | +18 | 0% | MANUAL_REVIEW_REQUIRED | 45 | +7 |
| Sean Tucker | TB | 71 | 67 | 67 | +4 | +4 | 0% | NONE | 59 | +8 |
| Brashard Smith | KC | 72 | 81 | 81 | -9 | -9 | 0% | PROSPECT_HISTORY | 74 | +7 |
| Jerome Ford | WAS | 73 | 43 | 43 | +30 | +30 | 0% | MANUAL_REVIEW_REQUIRED | 43 | 0 |
| Malik Davis | DAL | 74 | 93 | 93 | -19 | -19 | 0% | MANUAL_REVIEW_REQUIRED | 92 | +1 |
| Tank Bigsby | PHI | 75 | 82 | 82 | -7 | -7 | 0% | NONE | 70 | +12 |
| DJ Giddens | IND | 76 | 90 | 76 | -14 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 89 | +1 |
| Ray Davis | BUF | 77 | 37 | 37 | +40 | +40 | 0% | MANUAL_REVIEW_REQUIRED | 54 | -17 |
| Zavier Scott | MIN | 78 | 103 | 78 | -25 | 0 | 31% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 104 | -1 |
| Terrell Jennings | NE | 79 | 80 | 79 | -1 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 90 | -10 |
| Jaleel McLaughlin | DEN | 80 | 99 | 99 | -19 | -19 | 0% | MANUAL_REVIEW_REQUIRED | 87 | +12 |

#### Movement Tables (RB)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Ray Davis | BUF | 77 | 37 | +40 | Weighted Opportunity: 33.48, NGS Rushes Over Expected: 32.11 |
| Chuba Hubbard | CAR | 42 | 9 | +33 | Weighted Opportunity: 123.09, NGS Rushes Over Expected: 5.09 |
| Jerome Ford | WAS | 73 | 43 | +30 | Weighted Opportunity: 72.93, NGS Rushes Over Expected: 6.06 |
| Tony Pollard | TEN | 32 | 12 | +20 | Weighted Opportunity: 146.80, NGS Rushes Over Expected: -2.17 |
| Devin Singletary | NYG | 52 | 33 | +19 | Weighted Opportunity: 85.27, NGS Rushes Over Expected: 5.17 |
| Derrick Henry | BAL | 20 | 2 | +18 | Weighted Opportunity: 160.26, NGS Rushes Over Expected: 26.91 |
| Brian Robinson | ATL | 70 | 52 | +18 | Weighted Opportunity: 75.13, NGS Rushes Over Expected: -0.09 |
| Aaron Jones | MIN | 30 | 14 | +16 | Weighted Opportunity: 98.53, NGS Rushes Over Expected: 6.21 |
| Kimani Vidal | LAC | 37 | 22 | +15 | Weighted Opportunity: 50.85, NGS Rushes Over Expected: -2.21 |
| Justice Hill | BAL | 61 | 47 | +14 | Weighted Opportunity: 42.08, NGS Rushes Over Expected: 4.61 |
| James Conner | ARI | 25 | 13 | +12 | Weighted Opportunity: 125.62, NGS Rushes Over Expected: 6.82 |
| Quinshon Judkins | CLE | 22 | 11 | +11 | Weighted Opportunity: 159.75, NGS Rushes Over Expected: 6.61 |
| Breece Hall | NYJ | 18 | 8 | +10 | Weighted Opportunity: 181.58, NGS Rushes Over Expected: 7.05 |
| Rachaad White | WAS | 40 | 30 | +10 | Weighted Opportunity: 96.29, NGS Rushes Over Expected: -2.11 |
| Emari Demercado | KC | 67 | 58 | +9 | Weighted Opportunity: 39.93, NGS Rushes Over Expected: 6.24 |

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Omarion Hampton | LAC | 10 | 56 | -46 | Weighted Opportunity: 52.43, NGS Rushes Over Expected: 10.81 |
| Keaton Mitchell | LAC | 66 | 107 | -41 | Weighted Opportunity: 22.08, NGS Rushes Over Expected: -21.24 |
| Jeremy McNichols | WAS | 64 | 97 | -33 | Weighted Opportunity: 24.68, NGS Rushes Over Expected: 0.00 |
| Jaylen Wright | MIA | 56 | 87 | -31 | Weighted Opportunity: 44.74, NGS Rushes Over Expected: 5.78 |
| Trey Benson | ARI | 36 | 66 | -30 | Weighted Opportunity: 32.22, NGS Rushes Over Expected: 1.77 |
| Chase Brown | CIN | 6 | 31 | -25 | Weighted Opportunity: 148.14, NGS Rushes Over Expected: 6.32 |
| Emanuel Wilson | SEA | 54 | 77 | -23 | Weighted Opportunity: 31.42, NGS Rushes Over Expected: 5.08 |
| TreVeyon Henderson | NE | 33 | 55 | -22 | Weighted Opportunity: 82.01, NGS Rushes Over Expected: -6.83 |
| Chris Rodriguez Jr. | JAX | 48 | 69 | -21 | Weighted Opportunity: 46.62, NGS Rushes Over Expected: 13.77 |
| Kenneth Gainwell | TB | 28 | 48 | -20 | Weighted Opportunity: 53.02, NGS Rushes Over Expected: -1.25 |
| Zach Charbonnet | SEA | 26 | 45 | -19 | Weighted Opportunity: 91.24, NGS Rushes Over Expected: 0.97 |
| Braelon Allen | NYJ | 65 | 84 | -19 | Weighted Opportunity: 44.39, NGS Rushes Over Expected: -3.12 |
| Malik Davis | DAL | 74 | 93 | -19 | Weighted Opportunity: 17.13, NGS Rushes Over Expected: 7.01 |
| Jaleel McLaughlin | DEN | 80 | 99 | -19 | Weighted Opportunity: 38.26, NGS Rushes Over Expected: -3.18 |
| Dylan Sampson | CLE | 58 | 75 | -17 | Weighted Opportunity: 67.82, NGS Rushes Over Expected: -7.18 |

---

### WR Board — Status: **Accepted**

- **Finalist Model**: `ranking_bqml_v2_adv_standard_wr_logistic_elite_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 56 | 0 | 0 | 6 | 32 | 0 | 0 | 0 | 6 | 0 | 13 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Jaxon Smith-Njigba | SEA | 1 | 8 | 8 | -7 | -7 | 0% | NONE |
| Puka Nacua | LAR | 2 | 3 | 3 | -1 | -1 | 0% | NONE |
| Amon-Ra St. Brown | DET | 3 | 2 | 2 | +1 | +1 | 0% | NONE |
| Ja'Marr Chase | CIN | 4 | 1 | 1 | +3 | +3 | 0% | NONE |
| Drake London | ATL | 5 | 7 | 7 | -2 | -2 | 0% | NONE |
| Garrett Wilson | NYJ | 6 | 13 | 13 | -7 | -7 | 0% | NONE |
| Rashee Rice | KC | 7 | 31 | 31 | -24 | -24 | 0% | MANUAL_REVIEW_REQUIRED |
| Chris Olave | NO | 8 | 22 | 22 | -14 | -14 | 0% | NONE |
| A.J. Brown | NE | 9 | 6 | 6 | +3 | +3 | 0% | NONE |
| Justin Jefferson | MIN | 10 | 10 | 10 | 0 | 0 | 0% | NONE |
| George Pickens | DAL | 11 | 12 | 12 | -1 | -1 | 0% | NONE |
| Zay Flowers | BAL | 12 | 15 | 15 | -3 | -3 | 0% | NONE |
| Davante Adams | LAR | 13 | 11 | 11 | +2 | +2 | 0% | NONE |
| CeeDee Lamb | DAL | 14 | 4 | 4 | +10 | +10 | 0% | NONE |
| Nico Collins | HOU | 15 | 20 | 20 | -5 | -5 | 0% | NONE |
| Tetairoa McMillan | CAR | 16 | 37 | 37 | -21 | -21 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Wan'Dale Robinson | TEN | 17 | 39 | 39 | -22 | -22 | 0% | MANUAL_REVIEW_REQUIRED |
| Malik Nabers | NYG | 18 | 5 | 5 | +13 | +13 | 0% | NONE |
| Rome Odunze | CHI | 19 | 41 | 41 | -22 | -22 | 0% | MANUAL_REVIEW_REQUIRED |
| DeVonta Smith | PHI | 20 | 18 | 18 | +2 | +2 | 0% | NONE |
| Terry McLaurin | WAS | 21 | 14 | 14 | +7 | +7 | 0% | NONE |
| Jaylen Waddle | DEN | 22 | 30 | 30 | -8 | -8 | 0% | NONE |
| Alec Pierce | IND | 23 | 29 | 29 | -6 | -6 | 0% | NONE |
| Tee Higgins | CIN | 24 | 9 | 9 | +15 | +15 | 0% | NONE |
| Courtland Sutton | DEN | 25 | 21 | 21 | +4 | +4 | 0% | NONE |
| Emeka Egbuka | TB | 26 | 28 | 28 | -2 | -2 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Jameson Williams | DET | 27 | 50 | 50 | -23 | -23 | 0% | MANUAL_REVIEW_REQUIRED |
| Jakobi Meyers | JAX | 28 | 38 | 38 | -10 | -10 | 0% | NONE |
| Mike Evans | SF | 29 | 17 | 17 | +12 | +12 | 0% | NONE |
| Quentin Johnston | LAC | 30 | 52 | 52 | -22 | -22 | 0% | MANUAL_REVIEW_REQUIRED |
| Michael Wilson | ARI | 31 | 42 | 42 | -11 | -11 | 0% | NONE |
| Christian Watson | GB | 32 | 61 | 61 | -29 | -29 | 0% | MANUAL_REVIEW_REQUIRED |
| Jordan Addison | MIN | 33 | 32 | 32 | +1 | +1 | 0% | NONE |
| Marvin Harrison | ARI | 34 | 23 | 23 | +11 | +11 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| DK Metcalf | PIT | 35 | 16 | 16 | +19 | +19 | 0% | MANUAL_REVIEW_REQUIRED |
| Ladd McConkey | LAC | 36 | 24 | 24 | +12 | +12 | 0% | NONE |
| Romeo Doubs | NE | 37 | 47 | 47 | -10 | -10 | 0% | NONE |
| Jauan Jennings | MIN | 38 | 54 | 54 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED |
| Tre Tucker | LV | 39 | 55 | 55 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED |
| Parker Washington | JAX | 40 | 53 | 53 | -13 | -13 | 0% | NONE |
| Ricky Pearsall | SF | 41 | 70 | 70 | -29 | -29 | 0% | MANUAL_REVIEW_REQUIRED |
| Troy Franklin | DEN | 42 | 75 | 75 | -33 | -33 | 0% | MANUAL_REVIEW_REQUIRED |
| Jerry Jeudy | CLE | 43 | 33 | 33 | +10 | +10 | 0% | NONE |
| Elic Ayomanor | TEN | 44 | 58 | 58 | -14 | -14 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Darius Slayton | NYG | 45 | 45 | 45 | 0 | 0 | 0% | NONE |
| Calvin Ridley | TEN | 46 | 27 | 27 | +19 | +19 | 0% | MANUAL_REVIEW_REQUIRED |
| Khalil Shakir | BUF | 47 | 49 | 49 | -2 | -2 | 0% | NONE |
| Darnell Mooney | NYG | 48 | 46 | 46 | +2 | +2 | 0% | NONE |
| Keon Coleman | BUF | 49 | 63 | 63 | -14 | -14 | 0% | NONE |
| Brian Thomas Jr. | JAX | 50 | 40 | 40 | +10 | +10 | 0% | NONE |
| Xavier Worthy | KC | 51 | 43 | 43 | +8 | +8 | 0% | NONE |
| Travis Hunter | JAX | 52 | 76 | 52 | -24 | 0 | 5% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR, MANUAL_REVIEW_REQUIRED |
| Mack Hollins | NE | 53 | 68 | 68 | -15 | -15 | 0% | NONE |
| Michael Pittman | PIT | 54 | 19 | 19 | +35 | +35 | 0% | MANUAL_REVIEW_REQUIRED |
| Jakobie Keeney-James | GB | 55 | 35 | 55 | +20 | 0 | 30% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR, MANUAL_REVIEW_REQUIRED |
| Kayshon Boutte | NE | 56 | 64 | 64 | -8 | -8 | 0% | NONE |
| Jayden Reed | GB | 57 | 57 | 57 | 0 | 0 | 0% | NONE |
| Jalen Coker | CAR | 58 | 48 | 48 | +10 | +10 | 0% | NONE |
| Josh Downs | IND | 59 | 44 | 44 | +15 | +15 | 0% | NONE |
| Rashid Shaheed | SEA | 60 | 62 | 62 | -2 | -2 | 0% | NONE |
| Cooper Kupp | SEA | 61 | 51 | 51 | +10 | +10 | 0% | NONE |
| Chris Godwin Jr. | TB | 62 | 34 | 34 | +28 | +28 | 0% | MANUAL_REVIEW_REQUIRED |
| Jalen McMillan | TB | 63 | 59 | 59 | +4 | +4 | 0% | NONE |
| Devaughn Vele | NO | 64 | 82 | 82 | -18 | -18 | 0% | MANUAL_REVIEW_REQUIRED |
| Marquise Brown | PHI | 65 | 60 | 60 | +5 | +5 | 0% | NONE |
| Van Jefferson | WAS | 66 | 95 | 95 | -29 | -29 | 0% | MANUAL_REVIEW_REQUIRED |
| Xavier Legette | CAR | 67 | 81 | 81 | -14 | -14 | 0% | NONE |
| Jayden Higgins | HOU | 68 | 67 | 67 | +1 | +1 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| DJ Moore | BUF | 69 | 25 | 25 | +44 | +44 | 0% | MANUAL_REVIEW_REQUIRED |
| Adonai Mitchell | NYJ | 70 | 108 | 108 | -38 | -38 | 5% | MANUAL_REVIEW_REQUIRED |
| Theo Wease Jr. | MIA | 71 | 103 | 71 | -32 | 0 | 5% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Tyquan Thornton | KC | 72 | 111 | 111 | -39 | -39 | 0% | MANUAL_REVIEW_REQUIRED |
| Andrei Iosivas | CIN | 73 | 79 | 79 | -6 | -6 | 0% | NONE |
| Olamide Zaccheaus | ATL | 74 | 112 | 112 | -38 | -38 | 0% | MANUAL_REVIEW_REQUIRED |
| Chimere Dike | TEN | 75 | 73 | 73 | +2 | +2 | 0% | PROSPECT_HISTORY |
| Kendrick Bourne | ARI | 76 | 80 | 80 | -4 | -4 | 0% | NONE |
| Malik Washington | MIA | 77 | 89 | 89 | -12 | -12 | 0% | NONE |
| Ryan Flournoy | DAL | 78 | 102 | 102 | -24 | -24 | 0% | MANUAL_REVIEW_REQUIRED |
| Calvin Austin III | NYG | 79 | 90 | 90 | -11 | -11 | 0% | NONE |
| Pat Bryant | DEN | 80 | 120 | 120 | -40 | -40 | 0% | PROSPECT_HISTORY |
| Dontayvion Wicks | PHI | 81 | 71 | 71 | +10 | +10 | 0% | NONE |
| Xavier Hutchinson | HOU | 82 | 122 | 122 | -40 | -40 | 0% | MANUAL_REVIEW_REQUIRED |
| Rashod Bateman | BAL | 83 | 66 | 66 | +17 | +17 | 0% | MANUAL_REVIEW_REQUIRED |
| Matthew Golden | GB | 84 | 78 | 78 | +6 | +6 | 5% | PROSPECT_HISTORY |
| Jalen Nailor | LV | 85 | 86 | 86 | -1 | -1 | 0% | NONE |
| Tory Horton | SEA | 86 | 87 | 86 | -1 | 0 | 15% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Tez Johnson | TB | 87 | 85 | 85 | +2 | +2 | 5% | PROSPECT_HISTORY |
| Luther Burden III | CHI | 88 | 69 | 69 | +19 | +19 | 0% | PROSPECT_HISTORY |
| DeMario Douglas | NE | 89 | 74 | 74 | +15 | +15 | 0% | NONE |
| Christian Kirk | SF | 90 | 56 | 56 | +34 | +34 | 0% | MANUAL_REVIEW_REQUIRED |
| Isaiah Bond | CLE | 91 | 116 | 116 | -25 | -25 | 0% | PROSPECT_HISTORY |
| Treylon Burks | WAS | 92 | 118 | 118 | -26 | -26 | 0% | MANUAL_REVIEW_REQUIRED |
| Tre Harris | LAC | 93 | 96 | 96 | -3 | -3 | 5% | PROSPECT_HISTORY |
| Isaac TeSlaa | DET | 94 | 91 | 91 | +3 | +3 | 0% | PROSPECT_HISTORY |
| Casey Washington | ATL | 95 | 166 | 95 | -71 | 0 | 10% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Marquez Valdes-Scantling | DAL | 96 | 97 | 97 | -1 | -1 | 0% | NONE |
| Cedric Tillman | CLE | 97 | 93 | 93 | +4 | +4 | 0% | NONE |
| Jalen Tolbert | MIA | 98 | 105 | 105 | -7 | -7 | 0% | NONE |
| Devontez Walker | BAL | 99 | 141 | 99 | -42 | 0 | 15% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Lil'Jordan Humphrey | DEN | 100 | 104 | 104 | -4 | -4 | 0% | NONE |

#### Movement Tables (WR)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| DJ Moore | BUF | 69 | 25 | +44 | WOPR: 0.50, Target Share: 0.22 |
| Michael Pittman | PIT | 54 | 19 | +35 | WOPR: 0.55, Target Share: 0.25 |
| Christian Kirk | SF | 90 | 56 | +34 | WOPR: 0.43, Target Share: 0.18 |
| Chris Godwin Jr. | TB | 62 | 34 | +28 | WOPR: 0.47, Target Share: 0.21 |
| DK Metcalf | PIT | 35 | 16 | +19 | WOPR: 0.55, Target Share: 0.21 |
| Calvin Ridley | TEN | 46 | 27 | +19 | WOPR: 0.55, Target Share: 0.21 |
| Luther Burden III | CHI | 88 | 69 | +19 | WOPR: 0.30, Target Share: 0.14 |
| Rashod Bateman | BAL | 83 | 66 | +17 | WOPR: 0.36, Target Share: 0.13 |
| Tee Higgins | CIN | 24 | 9 | +15 | WOPR: 0.54, Target Share: 0.20 |
| Josh Downs | IND | 59 | 44 | +15 | WOPR: 0.42, Target Share: 0.20 |
| DeMario Douglas | NE | 89 | 74 | +15 | WOPR: 0.30, Target Share: 0.14 |
| Malik Nabers | NYG | 18 | 5 | +13 | WOPR: 0.80, Target Share: 0.32 |
| Mike Evans | SF | 29 | 17 | +12 | WOPR: 0.70, Target Share: 0.28 |
| Ladd McConkey | LAC | 36 | 24 | +12 | WOPR: 0.60, Target Share: 0.26 |
| Marvin Harrison | ARI | 34 | 23 | +11 | WOPR: 0.56, Target Share: 0.20 |

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Pat Bryant | DEN | 80 | 120 | -40 | WOPR: 0.18, Target Share: 0.08 |
| Xavier Hutchinson | HOU | 82 | 122 | -40 | WOPR: 0.23, Target Share: 0.10 |
| Tyquan Thornton | KC | 72 | 111 | -39 | WOPR: 0.25, Target Share: 0.08 |
| Adonai Mitchell | NYJ | 70 | 108 | -38 | WOPR: 0.34, Target Share: 0.13 |
| Olamide Zaccheaus | ATL | 74 | 112 | -38 | WOPR: 0.17, Target Share: 0.08 |
| Troy Franklin | DEN | 42 | 75 | -33 | WOPR: 0.37, Target Share: 0.14 |
| Christian Watson | GB | 32 | 61 | -29 | WOPR: 0.39, Target Share: 0.15 |
| Ricky Pearsall | SF | 41 | 70 | -29 | WOPR: 0.33, Target Share: 0.13 |
| Van Jefferson | WAS | 66 | 95 | -29 | WOPR: 0.26, Target Share: 0.10 |
| Treylon Burks | WAS | 92 | 118 | -26 | WOPR: 0.26, Target Share: 0.10 |
| Isaiah Bond | CLE | 91 | 116 | -25 | WOPR: 0.29, Target Share: 0.09 |
| Rashee Rice | KC | 7 | 31 | -24 | WOPR: 0.47, Target Share: 0.24 |
| Ryan Flournoy | DAL | 78 | 102 | -24 | WOPR: 0.16, Target Share: 0.07 |
| Jameson Williams | DET | 27 | 50 | -23 | WOPR: 0.40, Target Share: 0.13 |
| Wan'Dale Robinson | TEN | 17 | 39 | -22 | WOPR: 0.50, Target Share: 0.24 |

---

### TE Board — Status: **Accepted with guardrails**

- **Finalist Model**: `ranking_bqml_v2_adv_standard_te_linear_points_advanced_v0`
- **Alternate Model**: `ranking_bqml_v2_adv_standard_te_logistic_bust_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 0 | 17 | 2 | 6 | 0 | 0 | 0 | 2 | 0 | 5 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels | Alt Rank | Finalist/Alternate Disagreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Trey McBride | ARI | 1 | 1 | 1 | 0 | 0 | 0% | NONE | 1 | 0 |
| Brock Bowers | LV | 2 | 2 | 2 | 0 | 0 | 0% | NONE | 2 | 0 |
| Tucker Kraft | GB | 3 | 18 | 3 | -15 | 0 | 0% | STANDARD_TE_FLOOR | 25 | -7 |
| George Kittle | SF | 4 | 3 | 3 | +1 | +1 | 0% | NONE | 4 | -1 |
| Kyle Pitts | ATL | 5 | 9 | 5 | -4 | 0 | 0% | STANDARD_TE_FLOOR | 7 | +2 |
| Tyler Warren | IND | 6 | 4 | 4 | +2 | +2 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 6 | -2 |
| Sam LaPorta | DET | 7 | 8 | 7 | -1 | 0 | 0% | STANDARD_TE_FLOOR | 8 | 0 |
| Dallas Goedert | PHI | 8 | 12 | 8 | -4 | 0 | 0% | STANDARD_TE_FLOOR | 14 | -2 |
| Travis Kelce | KC | 9 | 5 | 5 | +4 | +4 | 0% | NONE | 3 | +2 |
| Hunter Henry | NE | 10 | 14 | 10 | -4 | 0 | 0% | STANDARD_TE_FLOOR | 9 | +5 |
| Dalton Schultz | HOU | 11 | 21 | 11 | -10 | 0 | 0% | STANDARD_TE_FLOOR | 17 | +4 |
| Juwan Johnson | NO | 12 | 13 | 12 | -1 | 0 | 0% | STANDARD_TE_FLOOR | 12 | +1 |
| Colston Loveland | CHI | 13 | 6 | 6 | +7 | +7 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 5 | +1 |
| Brenton Strange | JAX | 14 | 30 | 14 | -16 | 0 | 0% | STANDARD_TE_FLOOR | 32 | -2 |
| Jake Ferguson | DAL | 15 | 20 | 15 | -5 | 0 | 0% | STANDARD_TE_FLOOR | 13 | +7 |
| Harold Fannin Jr. | CLE | 16 | 7 | 7 | +9 | +9 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 10 | -3 |
| Cade Otton | TB | 17 | 22 | 17 | -5 | 0 | 0% | STANDARD_TE_FLOOR | 21 | +1 |
| Theo Johnson | NYG | 18 | 25 | 18 | -7 | 0 | 0% | STANDARD_TE_FLOOR | 23 | +2 |
| Mason Taylor | NYJ | 19 | 32 | 32 | -13 | -13 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 22 | +10 |
| Oronde Gadsden II | LAC | 20 | 24 | 24 | -4 | -4 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 28 | -4 |
| Dalton Kincaid | BUF | 21 | 15 | 15 | +6 | +6 | 0% | NONE | 18 | -3 |
| AJ Barner | SEA | 22 | 36 | 22 | -14 | 0 | 0% | STANDARD_TE_FLOOR | 30 | +6 |
| Mark Andrews | BAL | 23 | 17 | 17 | +6 | +6 | 0% | NONE | 16 | +1 |
| T.J. Hockenson | MIN | 24 | 16 | 16 | +8 | +8 | 0% | NONE | 11 | +5 |
| Jake Tonges | SF | 25 | 49 | 25 | -24 | 0 | 0% | STANDARD_TE_FLOOR | 48 | +1 |
| Drake Dabney | GB | 26 | 11 | 26 | +15 | 0 | 25% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 29 | -18 |
| Albert Okwuegbunam | LV | 27 | 63 | 27 | -36 | 0 | 5% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 85 | -22 |
| Greg Dulcich | MIA | 28 | 41 | 28 | -13 | 0 | 0% | STANDARD_TE_FLOOR | 59 | -18 |
| David Njoku | LAC | 29 | 10 | 10 | +19 | +19 | 0% | MANUAL_REVIEW_REQUIRED | 15 | -5 |
| Colby Parkinson | LAR | 30 | 37 | 30 | -7 | 0 | 0% | STANDARD_TE_FLOOR | 37 | 0 |
| Darnell Washington | PIT | 31 | 43 | 31 | -12 | 0 | 0% | STANDARD_TE_FLOOR | 51 | -8 |
| Pat Freiermuth | PIT | 32 | 23 | 23 | +9 | +9 | 0% | NONE | 24 | -1 |
| Dawson Knox | BUF | 33 | 35 | 33 | -2 | 0 | 0% | STANDARD_TE_FLOOR | 41 | -6 |
| Cole Kmet | CHI | 34 | 27 | 27 | +7 | +7 | 0% | NONE | 20 | +7 |
| Evan Engram | DEN | 35 | 29 | 29 | +6 | +6 | 0% | NONE | 31 | -2 |

#### Movement Tables (TE)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| David Njoku | LAC | 29 | 10 | +19 | WOPR: 0.44, Target Share: 0.20 |
| Harold Fannin Jr. | CLE | 16 | 7 | +9 | WOPR: 0.45, Target Share: 0.21 |
| Pat Freiermuth | PIT | 32 | 23 | +9 | WOPR: 0.32, Target Share: 0.15 |
| T.J. Hockenson | MIN | 24 | 16 | +8 | WOPR: 0.36, Target Share: 0.17 |
| Colston Loveland | CHI | 13 | 6 | +7 | WOPR: 0.51, Target Share: 0.22 |
| Cole Kmet | CHI | 34 | 27 | +7 | WOPR: 0.24, Target Share: 0.12 |
| Dalton Kincaid | BUF | 21 | 15 | +6 | WOPR: 0.35, Target Share: 0.16 |
| Mark Andrews | BAL | 23 | 17 | +6 | WOPR: 0.35, Target Share: 0.16 |
| Evan Engram | DEN | 35 | 29 | +6 | WOPR: 0.33, Target Share: 0.18 |
| Travis Kelce | KC | 9 | 5 | +4 | WOPR: 0.50, Target Share: 0.23 |
| Tyler Warren | IND | 6 | 4 | +2 | WOPR: 0.41, Target Share: 0.21 |
| George Kittle | SF | 4 | 3 | +1 | WOPR: 0.36, Target Share: 0.16 |

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Mason Taylor | NYJ | 19 | 32 | -13 | WOPR: 0.37, Target Share: 0.18 |
| Oronde Gadsden II | LAC | 20 | 24 | -4 | WOPR: 0.26, Target Share: 0.12 |

---

## HALF PPR PROFILE BOARDS

### QB Board — Status: **Accepted with guardrails**

- **Finalist Model**: `ranking_bqml_v2_adv_half_ppr_qb_logistic_bust_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 32 | 0 | 0 | 5 | 3 | 0 | 0 | 0 | 4 | 1 | 4 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Josh Allen | BUF | 1 | 1 | 1 | 0 | 0 | 0% | NONE |
| Drake Maye | NE | 2 | 5 | 5 | -3 | -3 | 0% | NONE |
| Patrick Mahomes | KC | 3 | 6 | 6 | -3 | -3 | 0% | NONE |
| Brock Purdy | SF | 4 | 9 | 9 | -5 | -5 | 0% | NONE |
| Jalen Hurts | PHI | 5 | 4 | 4 | +1 | +1 | 0% | NONE |
| Trevor Lawrence | JAX | 6 | 11 | 11 | -5 | -5 | 0% | NONE |
| Daniel Jones | IND | 7 | 14 | 14 | -7 | -7 | 0% | NONE |
| Bo Nix | DEN | 8 | 8 | 8 | 0 | 0 | 0% | NONE |
| Caleb Williams | CHI | 9 | 12 | 12 | -3 | -3 | 0% | NONE |
| Matthew Stafford | LAR | 10 | 21 | 21 | -11 | -11 | 0% | NONE |
| Justin Herbert | LAC | 11 | 15 | 15 | -4 | -4 | 0% | NONE |
| Jayden Daniels | WAS | 12 | 3 | 3 | +9 | +9 | 0% | NONE |
| Dak Prescott | DAL | 13 | 10 | 10 | +3 | +3 | 0% | NONE |
| Lamar Jackson | BAL | 14 | 2 | 2 | +12 | +12 | 0% | NONE |
| Jordan Love | GB | 15 | 20 | 20 | -5 | -5 | 0% | NONE |
| Jaxson Dart | NYG | 16 | 7 | 7 | +9 | +9 | 0% | PROSPECT_HISTORY |
| Jared Goff | DET | 17 | 18 | 18 | -1 | -1 | 0% | NONE |
| Kyler Murray | MIN | 18 | 13 | 13 | +5 | +5 | 0% | QB_RUSHING_BIAS_WARNING |
| C.J. Stroud | HOU | 19 | 24 | 24 | -5 | -5 | 0% | NONE |
| Tyler Shough | NO | 20 | 22 | 22 | -2 | -2 | 0% | PROSPECT_HISTORY |
| Bryce Young | CAR | 21 | 37 | 37 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED |
| Aaron Rodgers | PIT | 22 | 42 | 42 | -20 | -20 | 0% | MANUAL_REVIEW_REQUIRED |
| Baker Mayfield | TB | 23 | 17 | 17 | +6 | +6 | 0% | NONE |
| Joe Burrow | CIN | 24 | 19 | 19 | +5 | +5 | 0% | NONE |
| Jacoby Brissett | ARI | 25 | 28 | 28 | -3 | -3 | 0% | NONE |
| Malik Willis | MIA | 26 | 23 | 23 | +3 | +3 | 0% | NONE |
| Sam Darnold | SEA | 27 | 25 | 25 | +2 | +2 | 0% | NONE |
| Geno Smith | NYJ | 28 | 30 | 30 | -2 | -2 | 0% | NONE |
| Tua Tagovailoa | ATL | 29 | 27 | 27 | +2 | +2 | 0% | NONE |
| Shedeur Sanders | CLE | 30 | 49 | 30 | -19 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Cam Ward | TEN | 31 | 55 | 55 | -24 | -24 | 0% | PROSPECT_HISTORY |
| Justin Fields | KC | 32 | 16 | 16 | +16 | +16 | 0% | QB_RUSHING_BIAS_WARNING, MANUAL_REVIEW_REQUIRED |
| Carson Wentz | MIN | 33 | 26 | 33 | +7 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Marcus Mariota | WAS | 34 | 34 | 34 | 0 | 0 | 0% | NONE |
| J.J. McCarthy | MIN | 35 | 40 | 40 | -5 | -5 | 0% | PROSPECT_HISTORY |
| Spencer Rattler | NO | 36 | 43 | 43 | -7 | -7 | 0% | NONE |
| Jake Browning | TB | 37 | 50 | 50 | -13 | -13 | 0% | NONE |
| Mac Jones | SF | 38 | 36 | 36 | +2 | +2 | 0% | NONE |
| Tyler Huntley | BAL | 39 | 29 | 29 | +10 | +10 | 0% | NONE |
| Joe Flacco | CIN | 40 | 45 | 45 | -5 | -5 | 0% | NONE |
| Fernando Mendoza | LV | 41 | 95 | 41 | -54 | 0 | 100% | HISTORY_JOIN_FAILED, CURRENT_PIGSKIN_ANCHOR |
| Jameis Winston | NYG | 42 | 31 | 31 | +11 | +11 | 0% | NONE |
| Davis Mills | HOU | 43 | 52 | 52 | -9 | -9 | 0% | NONE |
| Josh Johnson | CIN | 44 | 44 | 44 | 0 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Quinn Ewers | MIA | 45 | 57 | 45 | -12 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |

#### Movement Tables (QB)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Justin Fields | KC | 32 | 16 | +16 | Passing EPA/dropback: -0.16, Passing CPOE: -15.33 |
| Lamar Jackson | BAL | 14 | 2 | +12 | Passing EPA/dropback: 0.17, Passing CPOE: 5.44 |
| Jameis Winston | NYG | 42 | 31 | +11 | Passing EPA/dropback: -0.02, Passing CPOE: -9.79 |
| Tyler Huntley | BAL | 39 | 29 | +10 | Passing EPA/dropback: 0.01, Passing CPOE: 7.45 |
| Jayden Daniels | WAS | 12 | 3 | +9 | Passing EPA/dropback: 0.12, Passing CPOE: 1.60 |
| Jaxson Dart | NYG | 16 | 7 | +9 | Passing EPA/dropback: 0.01, Passing CPOE: -0.56 |
| Baker Mayfield | TB | 23 | 17 | +6 | Passing EPA/dropback: 0.25, Passing CPOE: 3.62 |
| Kyler Murray | MIN | 18 | 13 | +5 | Passing EPA/dropback: 0.03, Passing CPOE: 0.08 |
| Joe Burrow | CIN | 24 | 19 | +5 | Passing EPA/dropback: 0.11, Passing CPOE: 4.16 |
| Dak Prescott | DAL | 13 | 10 | +3 | Passing EPA/dropback: 0.08, Passing CPOE: 2.11 |
| Malik Willis | MIA | 26 | 23 | +3 | Passing EPA/dropback: 0.36, Passing CPOE: 10.90 |
| Sam Darnold | SEA | 27 | 25 | +2 | Passing EPA/dropback: -0.05, Passing CPOE: 1.28 |
| Tua Tagovailoa | ATL | 29 | 27 | +2 | Passing EPA/dropback: 0.03, Passing CPOE: -1.43 |
| Mac Jones | SF | 38 | 36 | +2 | Passing EPA/dropback: -0.17, Passing CPOE: -4.23 |
| Jalen Hurts | PHI | 5 | 4 | +1 | Passing EPA/dropback: 0.07, Passing CPOE: 3.94 |

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Cam Ward | TEN | 31 | 55 | -24 | Passing EPA/dropback: -0.20, Passing CPOE: -1.86 |
| Aaron Rodgers | PIT | 22 | 42 | -20 | Passing EPA/dropback: -0.69, Passing CPOE: -3.40 |
| Bryce Young | CAR | 21 | 37 | -16 | Passing EPA/dropback: -0.15, Passing CPOE: -1.18 |
| Jake Browning | TB | 37 | 50 | -13 | Passing EPA/dropback: -0.11, Passing CPOE: 2.42 |
| Matthew Stafford | LAR | 10 | 21 | -11 | Passing EPA/dropback: 0.21, Passing CPOE: 0.22 |
| Davis Mills | HOU | 43 | 52 | -9 | Passing EPA/dropback: -0.39, Passing CPOE: -2.44 |
| Daniel Jones | IND | 7 | 14 | -7 | Passing EPA/dropback: -0.11, Passing CPOE: 0.61 |
| Spencer Rattler | NO | 36 | 43 | -7 | Passing EPA/dropback: -0.21, Passing CPOE: -3.75 |
| Brock Purdy | SF | 4 | 9 | -5 | Passing EPA/dropback: 0.16, Passing CPOE: 2.12 |
| Trevor Lawrence | JAX | 6 | 11 | -5 | Passing EPA/dropback: 0.03, Passing CPOE: -1.74 |
| Jordan Love | GB | 15 | 20 | -5 | Passing EPA/dropback: 0.20, Passing CPOE: 1.59 |
| C.J. Stroud | HOU | 19 | 24 | -5 | Passing EPA/dropback: 0.02, Passing CPOE: -1.28 |
| J.J. McCarthy | MIN | 35 | 40 | -5 | Passing EPA/dropback: -0.22, Passing CPOE: -4.80 |
| Joe Flacco | CIN | 40 | 45 | -5 | Passing EPA/dropback: -0.12, Passing CPOE: 0.70 |
| Justin Herbert | LAC | 11 | 15 | -4 | Passing EPA/dropback: -0.18, Passing CPOE: -4.24 |

---

### RB Board — Status: **Accepted with guardrails**

- **Finalist Model**: `ranking_bqml_v2_adv_half_ppr_rb_linear_vor_advanced_v0`
- **Alternate Model**: `ranking_bqml_v2_adv_half_ppr_rb_linear_points_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 35 | 0 | 0 | 10 | 33 | 0 | 0 | 0 | 10 | 0 | 11 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels | Alt Rank | Finalist/Alternate Disagreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Christian McCaffrey | SF | 1 | 4 | 4 | -3 | -3 | 0% | NONE | 4 | 0 |
| Bijan Robinson | ATL | 2 | 3 | 3 | -1 | -1 | 0% | NONE | 2 | +1 |
| Jahmyr Gibbs | DET | 3 | 19 | 19 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED | 12 | +7 |
| De'Von Achane | MIA | 4 | 18 | 18 | -14 | -14 | 0% | NONE | 11 | +7 |
| Jonathan Taylor | IND | 5 | 5 | 5 | 0 | 0 | 0% | NONE | 6 | -1 |
| Chase Brown | CIN | 6 | 32 | 32 | -26 | -26 | 0% | MANUAL_REVIEW_REQUIRED | 30 | +2 |
| Javonte Williams | DAL | 7 | 21 | 21 | -14 | -14 | 0% | NONE | 20 | +1 |
| Saquon Barkley | PHI | 8 | 1 | 1 | +7 | +7 | 0% | NONE | 1 | 0 |
| Kyren Williams | LAR | 9 | 6 | 6 | +3 | +3 | 0% | NONE | 7 | -1 |
| Omarion Hampton | LAC | 10 | 55 | 55 | -45 | -45 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 57 | -2 |
| Ashton Jeanty | LV | 11 | 7 | 7 | +4 | +4 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 5 | +2 |
| James Cook | BUF | 12 | 23 | 23 | -11 | -11 | 0% | NONE | 24 | -1 |
| Josh Jacobs | GB | 13 | 15 | 15 | -2 | -2 | 0% | NONE | 17 | -2 |
| Travis Etienne | NO | 14 | 29 | 29 | -15 | -15 | 0% | NONE | 26 | +3 |
| Cam Skattebo | NYG | 15 | 31 | 15 | -16 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR, MANUAL_REVIEW_REQUIRED | 32 | -1 |
| Bucky Irving | TB | 16 | 27 | 27 | -11 | -11 | 0% | NONE | 28 | -1 |
| D'Andre Swift | CHI | 17 | 16 | 16 | +1 | +1 | 0% | NONE | 21 | -5 |
| Breece Hall | NYJ | 18 | 10 | 10 | +8 | +8 | 0% | NONE | 8 | +2 |
| Jaylen Warren | PIT | 19 | 34 | 34 | -15 | -15 | 0% | NONE | 34 | 0 |
| Derrick Henry | BAL | 20 | 2 | 2 | +18 | +18 | 0% | MANUAL_REVIEW_REQUIRED | 3 | -1 |
| Rhamondre Stevenson | NE | 21 | 14 | 14 | +7 | +7 | 0% | NONE | 14 | 0 |
| Quinshon Judkins | CLE | 22 | 20 | 20 | +2 | +2 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 18 | +2 |
| Rico Dowdle | PIT | 23 | 38 | 38 | -15 | -15 | 0% | NONE | 37 | +1 |
| James Conner | ARI | 24 | 13 | 13 | +11 | +11 | 0% | NONE | 15 | -2 |
| J.K. Dobbins | DEN | 25 | 22 | 22 | +3 | +3 | 0% | NONE | 31 | -9 |
| Kenneth Gainwell | TB | 26 | 49 | 49 | -23 | -23 | 0% | MANUAL_REVIEW_REQUIRED | 49 | 0 |
| Kenneth Walker III | KC | 27 | 24 | 24 | +3 | +3 | 0% | NONE | 22 | +2 |
| Alvin Kamara | NO | 28 | 26 | 26 | +2 | +2 | 0% | NONE | 19 | +7 |
| Zach Charbonnet | SEA | 29 | 45 | 45 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED | 45 | 0 |
| Aaron Jones | MIN | 30 | 11 | 11 | +19 | +19 | 0% | MANUAL_REVIEW_REQUIRED | 10 | +1 |
| Tyrone Tracy Jr. | NYG | 31 | 30 | 30 | +1 | +1 | 0% | NONE | 25 | +5 |
| Tony Pollard | TEN | 32 | 17 | 17 | +15 | +15 | 0% | NONE | 13 | +4 |
| TreVeyon Henderson | NE | 33 | 57 | 57 | -24 | -24 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 55 | +2 |
| Woody Marks | HOU | 34 | 28 | 28 | +6 | +6 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 29 | -1 |
| RJ Harvey | DEN | 35 | 39 | 39 | -4 | -4 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 36 | +3 |
| Trey Benson | ARI | 36 | 68 | 68 | -32 | -32 | 0% | MANUAL_REVIEW_REQUIRED | 62 | +6 |
| Kimani Vidal | LAC | 37 | 12 | 12 | +25 | +25 | 0% | RB_POINTS_SANITY_CHECK_WARNING, MANUAL_REVIEW_REQUIRED | 23 | -11 |
| Kyle Monangai | CHI | 38 | 40 | 40 | -2 | -2 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 41 | -1 |
| David Montgomery | HOU | 39 | 41 | 41 | -2 | -2 | 0% | NONE | 42 | -1 |
| Rachaad White | WAS | 40 | 25 | 25 | +15 | +15 | 0% | NONE | 27 | -2 |
| Isiah Pacheco | DET | 41 | 35 | 35 | +6 | +6 | 0% | NONE | 33 | +2 |
| Tyjae Spears | TEN | 42 | 48 | 48 | -6 | -6 | 0% | NONE | 44 | +4 |
| Chuba Hubbard | CAR | 43 | 9 | 9 | +34 | +34 | 0% | MANUAL_REVIEW_REQUIRED | 9 | 0 |
| Michael Carter | TEN | 44 | 56 | 56 | -12 | -12 | 0% | NONE | 56 | 0 |
| Jacory Croskey-Merritt | WAS | 45 | 50 | 50 | -5 | -5 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 48 | +2 |
| Jordan Mason | MIN | 46 | 46 | 46 | 0 | 0 | 0% | NONE | 43 | +3 |
| Jawhar Jordan | HOU | 47 | 36 | 47 | +11 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 39 | -3 |
| Chris Rodriguez Jr. | JAX | 48 | 71 | 71 | -23 | -23 | 0% | MANUAL_REVIEW_REQUIRED | 72 | -1 |
| Tyler Allgeier | ARI | 49 | 72 | 72 | -23 | -23 | 0% | RB_POINTS_SANITY_CHECK_WARNING, MANUAL_REVIEW_REQUIRED | 61 | +11 |
| Blake Corum | LAR | 50 | 61 | 61 | -11 | -11 | 0% | NONE | 64 | -3 |
| Raheim Sanders | CLE | 51 | 63 | 51 | -12 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 67 | -4 |
| Devin Neal | NO | 52 | 51 | 52 | +1 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 51 | 0 |
| Devin Singletary | NYG | 53 | 37 | 37 | +16 | +16 | 0% | MANUAL_REVIEW_REQUIRED | 35 | +2 |
| Emanuel Wilson | SEA | 54 | 78 | 78 | -24 | -24 | 0% | MANUAL_REVIEW_REQUIRED | 78 | 0 |
| Samaje Perine | CIN | 55 | 60 | 60 | -5 | -5 | 0% | NONE | 60 | 0 |
| Jaylen Wright | MIA | 56 | 101 | 101 | -45 | -45 | 0% | RB_POINTS_SANITY_CHECK_WARNING, MANUAL_REVIEW_REQUIRED | 89 | +12 |
| Dylan Sampson | CLE | 57 | 86 | 86 | -29 | -29 | 15% | PROSPECT_HISTORY | 69 | +17 |
| Phil Mafah | DAL | 58 | 75 | 58 | -17 | 0 | 31% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 87 | -12 |
| Ty Johnson | BUF | 59 | 70 | 70 | -11 | -11 | 0% | NONE | 63 | +7 |
| Bhayshul Tuten | JAX | 60 | 54 | 54 | +6 | +6 | 0% | PROSPECT_HISTORY | 54 | 0 |
| Justice Hill | BAL | 61 | 44 | 44 | +17 | +17 | 0% | MANUAL_REVIEW_REQUIRED | 46 | -2 |
| Jaret Patterson | LAC | 62 | 82 | 62 | -20 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 83 | -1 |
| Kendre Miller | NO | 63 | 79 | 79 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED | 77 | +2 |
| Jeremy McNichols | WAS | 64 | 92 | 92 | -28 | -28 | 31% | MANUAL_REVIEW_REQUIRED | 96 | -4 |
| Braelon Allen | NYJ | 65 | 83 | 83 | -18 | -18 | 0% | MANUAL_REVIEW_REQUIRED | 80 | +3 |
| Emari Demercado | KC | 66 | 59 | 59 | +7 | +7 | 0% | NONE | 58 | +1 |
| Keaton Mitchell | LAC | 67 | 114 | 114 | -47 | -47 | 15% | MANUAL_REVIEW_REQUIRED | 108 | +6 |
| Isaiah Davis | NYJ | 68 | 81 | 81 | -13 | -13 | 8% | NONE | 74 | +7 |
| Jaydon Blue | DAL | 69 | 62 | 69 | +7 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 66 | -4 |
| Brian Robinson | ATL | 70 | 53 | 53 | +17 | +17 | 0% | MANUAL_REVIEW_REQUIRED | 52 | +1 |
| Sean Tucker | TB | 71 | 66 | 66 | +5 | +5 | 0% | NONE | 68 | -2 |
| Jerome Ford | WAS | 72 | 42 | 42 | +30 | +30 | 0% | MANUAL_REVIEW_REQUIRED | 40 | +2 |
| Brashard Smith | KC | 73 | 88 | 88 | -15 | -15 | 0% | PROSPECT_HISTORY | 71 | +17 |
| Malik Davis | DAL | 74 | 98 | 98 | -24 | -24 | 0% | MANUAL_REVIEW_REQUIRED | 99 | -1 |
| Tank Bigsby | PHI | 75 | 87 | 87 | -12 | -12 | 0% | NONE | 84 | +3 |
| DJ Giddens | IND | 76 | 91 | 76 | -15 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 91 | 0 |
| Ray Davis | BUF | 77 | 33 | 33 | +44 | +44 | 0% | MANUAL_REVIEW_REQUIRED | 38 | -5 |
| Zavier Scott | MIN | 78 | 100 | 78 | -22 | 0 | 31% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 100 | 0 |
| Jaleel McLaughlin | DEN | 79 | 108 | 108 | -29 | -29 | 0% | RB_POINTS_SANITY_CHECK_WARNING, MANUAL_REVIEW_REQUIRED | 95 | +13 |
| Terrell Jennings | NE | 80 | 76 | 80 | +4 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 79 | -3 |

#### Movement Tables (RB)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Ray Davis | BUF | 77 | 33 | +44 | Weighted Opportunity: 36.51, NGS Rushes Over Expected: 32.11 |
| Chuba Hubbard | CAR | 43 | 9 | +34 | Weighted Opportunity: 135.31, NGS Rushes Over Expected: 5.09 |
| Jerome Ford | WAS | 72 | 42 | +30 | Weighted Opportunity: 85.07, NGS Rushes Over Expected: 6.06 |
| Kimani Vidal | LAC | 37 | 12 | +25 | Weighted Opportunity: 54.85, NGS Rushes Over Expected: -2.21 |
| Aaron Jones | MIN | 30 | 11 | +19 | Weighted Opportunity: 109.98, NGS Rushes Over Expected: 6.21 |
| Derrick Henry | BAL | 20 | 2 | +18 | Weighted Opportunity: 167.27, NGS Rushes Over Expected: 26.91 |
| Justice Hill | BAL | 61 | 44 | +17 | Weighted Opportunity: 51.10, NGS Rushes Over Expected: 4.61 |
| Brian Robinson | ATL | 70 | 53 | +17 | Weighted Opportunity: 81.17, NGS Rushes Over Expected: -0.09 |
| Devin Singletary | NYG | 53 | 37 | +16 | Weighted Opportunity: 92.89, NGS Rushes Over Expected: 5.17 |
| Tony Pollard | TEN | 32 | 17 | +15 | Weighted Opportunity: 161.74, NGS Rushes Over Expected: -2.17 |
| Rachaad White | WAS | 40 | 25 | +15 | Weighted Opportunity: 109.11, NGS Rushes Over Expected: -2.11 |
| James Conner | ARI | 24 | 13 | +11 | Weighted Opportunity: 136.86, NGS Rushes Over Expected: 6.82 |
| Breece Hall | NYJ | 18 | 10 | +8 | Weighted Opportunity: 206.75, NGS Rushes Over Expected: 7.05 |
| Saquon Barkley | PHI | 8 | 1 | +7 | Weighted Opportunity: 160.12, NGS Rushes Over Expected: 22.49 |
| Rhamondre Stevenson | NE | 21 | 14 | +7 | Weighted Opportunity: 124.75, NGS Rushes Over Expected: 4.45 |

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Keaton Mitchell | LAC | 67 | 114 | -47 | Weighted Opportunity: 24.09, NGS Rushes Over Expected: -21.24 |
| Omarion Hampton | LAC | 10 | 55 | -45 | Weighted Opportunity: 58.33, NGS Rushes Over Expected: 10.81 |
| Jaylen Wright | MIA | 56 | 101 | -45 | Weighted Opportunity: 47.28, NGS Rushes Over Expected: 5.78 |
| Trey Benson | ARI | 36 | 68 | -32 | Weighted Opportunity: 35.98, NGS Rushes Over Expected: 1.77 |
| Dylan Sampson | CLE | 57 | 86 | -29 | Weighted Opportunity: 81.80, NGS Rushes Over Expected: -7.18 |
| Jaleel McLaughlin | DEN | 79 | 108 | -29 | Weighted Opportunity: 43.37, NGS Rushes Over Expected: -3.18 |
| Jeremy McNichols | WAS | 64 | 92 | -28 | Weighted Opportunity: 28.38, NGS Rushes Over Expected: 0.00 |
| Chase Brown | CIN | 6 | 32 | -26 | Weighted Opportunity: 167.79, NGS Rushes Over Expected: 6.32 |
| TreVeyon Henderson | NE | 33 | 57 | -24 | Weighted Opportunity: 90.19, NGS Rushes Over Expected: -6.83 |
| Emanuel Wilson | SEA | 54 | 78 | -24 | Weighted Opportunity: 33.75, NGS Rushes Over Expected: 5.08 |
| Malik Davis | DAL | 74 | 98 | -24 | Weighted Opportunity: 17.96, NGS Rushes Over Expected: 7.01 |
| Kenneth Gainwell | TB | 26 | 49 | -23 | Weighted Opportunity: 61.98, NGS Rushes Over Expected: -1.25 |
| Chris Rodriguez Jr. | JAX | 48 | 71 | -23 | Weighted Opportunity: 47.43, NGS Rushes Over Expected: 13.77 |
| Tyler Allgeier | ARI | 49 | 72 | -23 | Weighted Opportunity: 117.54, NGS Rushes Over Expected: 0.14 |
| Braelon Allen | NYJ | 65 | 83 | -18 | Weighted Opportunity: 49.53, NGS Rushes Over Expected: -3.12 |

---

### WR Board — Status: **Accepted**

- **Finalist Model**: `ranking_bqml_v2_adv_half_ppr_wr_logistic_elite_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 53 | 0 | 0 | 5 | 36 | 0 | 0 | 0 | 5 | 0 | 13 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Jaxon Smith-Njigba | SEA | 1 | 7 | 7 | -6 | -6 | 0% | NONE |
| Puka Nacua | LAR | 2 | 4 | 4 | -2 | -2 | 0% | NONE |
| Ja'Marr Chase | CIN | 3 | 1 | 1 | +2 | +2 | 0% | NONE |
| Amon-Ra St. Brown | DET | 4 | 2 | 2 | +2 | +2 | 0% | NONE |
| Drake London | ATL | 5 | 6 | 6 | -1 | -1 | 0% | NONE |
| Garrett Wilson | NYJ | 6 | 12 | 12 | -6 | -6 | 0% | NONE |
| Rashee Rice | KC | 7 | 30 | 30 | -23 | -23 | 0% | MANUAL_REVIEW_REQUIRED |
| Chris Olave | NO | 8 | 17 | 17 | -9 | -9 | 0% | NONE |
| A.J. Brown | NE | 9 | 8 | 8 | +1 | +1 | 0% | NONE |
| Justin Jefferson | MIN | 10 | 10 | 10 | 0 | 0 | 0% | NONE |
| George Pickens | DAL | 11 | 14 | 14 | -3 | -3 | 0% | NONE |
| Zay Flowers | BAL | 12 | 13 | 13 | -1 | -1 | 0% | NONE |
| Davante Adams | LAR | 13 | 11 | 11 | +2 | +2 | 0% | NONE |
| CeeDee Lamb | DAL | 14 | 3 | 3 | +11 | +11 | 0% | NONE |
| Nico Collins | HOU | 15 | 21 | 21 | -6 | -6 | 0% | NONE |
| Wan'Dale Robinson | TEN | 16 | 34 | 34 | -18 | -18 | 0% | MANUAL_REVIEW_REQUIRED |
| Tetairoa McMillan | CAR | 17 | 38 | 38 | -21 | -21 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Malik Nabers | NYG | 18 | 5 | 5 | +13 | +13 | 0% | NONE |
| Rome Odunze | CHI | 19 | 43 | 43 | -24 | -24 | 0% | MANUAL_REVIEW_REQUIRED |
| DeVonta Smith | PHI | 20 | 19 | 19 | +1 | +1 | 0% | NONE |
| Terry McLaurin | WAS | 21 | 16 | 16 | +5 | +5 | 0% | NONE |
| Jaylen Waddle | DEN | 22 | 29 | 29 | -7 | -7 | 0% | NONE |
| Alec Pierce | IND | 23 | 31 | 31 | -8 | -8 | 0% | NONE |
| Tee Higgins | CIN | 24 | 9 | 9 | +15 | +15 | 0% | NONE |
| Courtland Sutton | DEN | 25 | 22 | 22 | +3 | +3 | 0% | NONE |
| Emeka Egbuka | TB | 26 | 28 | 28 | -2 | -2 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Jakobi Meyers | JAX | 27 | 37 | 37 | -10 | -10 | 0% | NONE |
| Jameson Williams | DET | 28 | 51 | 51 | -23 | -23 | 0% | MANUAL_REVIEW_REQUIRED |
| Mike Evans | SF | 29 | 20 | 20 | +9 | +9 | 0% | NONE |
| Michael Wilson | ARI | 30 | 41 | 41 | -11 | -11 | 0% | NONE |
| Quentin Johnston | LAC | 31 | 53 | 53 | -22 | -22 | 0% | MANUAL_REVIEW_REQUIRED |
| Christian Watson | GB | 32 | 61 | 61 | -29 | -29 | 0% | MANUAL_REVIEW_REQUIRED |
| Jordan Addison | MIN | 33 | 36 | 36 | -3 | -3 | 0% | NONE |
| DK Metcalf | PIT | 34 | 18 | 18 | +16 | +16 | 0% | MANUAL_REVIEW_REQUIRED |
| Marvin Harrison | ARI | 35 | 24 | 24 | +11 | +11 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Ladd McConkey | LAC | 36 | 26 | 26 | +10 | +10 | 0% | NONE |
| Jauan Jennings | MIN | 37 | 54 | 54 | -17 | -17 | 0% | MANUAL_REVIEW_REQUIRED |
| Romeo Doubs | NE | 38 | 46 | 46 | -8 | -8 | 0% | NONE |
| Tre Tucker | LV | 39 | 55 | 55 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED |
| Parker Washington | JAX | 40 | 52 | 52 | -12 | -12 | 0% | NONE |
| Ricky Pearsall | SF | 41 | 72 | 72 | -31 | -31 | 0% | MANUAL_REVIEW_REQUIRED |
| Troy Franklin | DEN | 42 | 76 | 76 | -34 | -34 | 0% | MANUAL_REVIEW_REQUIRED |
| Jerry Jeudy | CLE | 43 | 32 | 32 | +11 | +11 | 0% | NONE |
| Elic Ayomanor | TEN | 44 | 58 | 58 | -14 | -14 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Darius Slayton | NYG | 45 | 47 | 47 | -2 | -2 | 0% | NONE |
| Calvin Ridley | TEN | 46 | 25 | 25 | +21 | +21 | 0% | MANUAL_REVIEW_REQUIRED |
| Khalil Shakir | BUF | 47 | 48 | 48 | -1 | -1 | 0% | NONE |
| Darnell Mooney | NYG | 48 | 45 | 45 | +3 | +3 | 0% | NONE |
| Keon Coleman | BUF | 49 | 63 | 63 | -14 | -14 | 0% | NONE |
| Brian Thomas Jr. | JAX | 50 | 39 | 39 | +11 | +11 | 0% | NONE |
| Travis Hunter | JAX | 51 | 73 | 51 | -22 | 0 | 5% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR, MANUAL_REVIEW_REQUIRED |
| Michael Pittman | PIT | 52 | 15 | 15 | +37 | +37 | 0% | MANUAL_REVIEW_REQUIRED |
| Mack Hollins | NE | 53 | 71 | 71 | -18 | -18 | 0% | MANUAL_REVIEW_REQUIRED |
| Xavier Worthy | KC | 54 | 42 | 42 | +12 | +12 | 0% | NONE |
| Jakobie Keeney-James | GB | 55 | 44 | 55 | +11 | 0 | 30% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR, MANUAL_REVIEW_REQUIRED |
| Kayshon Boutte | NE | 56 | 64 | 64 | -8 | -8 | 0% | NONE |
| Jayden Reed | GB | 57 | 57 | 57 | 0 | 0 | 0% | NONE |
| Jalen Coker | CAR | 58 | 49 | 49 | +9 | +9 | 0% | NONE |
| Josh Downs | IND | 59 | 40 | 40 | +19 | +19 | 0% | MANUAL_REVIEW_REQUIRED |
| Rashid Shaheed | SEA | 60 | 62 | 62 | -2 | -2 | 0% | NONE |
| Cooper Kupp | SEA | 61 | 50 | 50 | +11 | +11 | 0% | NONE |
| Chris Godwin Jr. | TB | 62 | 33 | 33 | +29 | +29 | 0% | MANUAL_REVIEW_REQUIRED |
| Jalen McMillan | TB | 63 | 60 | 60 | +3 | +3 | 0% | NONE |
| Devaughn Vele | NO | 64 | 80 | 80 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED |
| Marquise Brown | PHI | 65 | 59 | 59 | +6 | +6 | 0% | NONE |
| Van Jefferson | WAS | 66 | 100 | 100 | -34 | -34 | 0% | MANUAL_REVIEW_REQUIRED |
| Xavier Legette | CAR | 67 | 81 | 81 | -14 | -14 | 0% | NONE |
| Jayden Higgins | HOU | 68 | 68 | 68 | 0 | 0 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| DJ Moore | BUF | 69 | 23 | 23 | +46 | +46 | 0% | MANUAL_REVIEW_REQUIRED |
| Adonai Mitchell | NYJ | 70 | 106 | 106 | -36 | -36 | 5% | MANUAL_REVIEW_REQUIRED |
| Theo Wease Jr. | MIA | 71 | 102 | 71 | -31 | 0 | 5% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Andrei Iosivas | CIN | 72 | 78 | 78 | -6 | -6 | 0% | NONE |
| Tyquan Thornton | KC | 73 | 119 | 119 | -46 | -46 | 0% | MANUAL_REVIEW_REQUIRED |
| Olamide Zaccheaus | ATL | 74 | 107 | 107 | -33 | -33 | 0% | MANUAL_REVIEW_REQUIRED |
| Chimere Dike | TEN | 75 | 65 | 65 | +10 | +10 | 0% | PROSPECT_HISTORY |
| Kendrick Bourne | ARI | 76 | 83 | 83 | -7 | -7 | 0% | NONE |
| Malik Washington | MIA | 77 | 87 | 87 | -10 | -10 | 0% | NONE |
| Ryan Flournoy | DAL | 78 | 94 | 94 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED |
| Calvin Austin III | NYG | 79 | 96 | 96 | -17 | -17 | 0% | MANUAL_REVIEW_REQUIRED |
| Pat Bryant | DEN | 80 | 115 | 115 | -35 | -35 | 0% | PROSPECT_HISTORY |
| Dontayvion Wicks | PHI | 81 | 75 | 75 | +6 | +6 | 0% | NONE |
| Xavier Hutchinson | HOU | 82 | 124 | 124 | -42 | -42 | 0% | MANUAL_REVIEW_REQUIRED |
| Rashod Bateman | BAL | 83 | 67 | 67 | +16 | +16 | 0% | MANUAL_REVIEW_REQUIRED |
| Matthew Golden | GB | 84 | 79 | 79 | +5 | +5 | 5% | PROSPECT_HISTORY |
| Jalen Nailor | LV | 85 | 88 | 88 | -3 | -3 | 0% | NONE |
| Tory Horton | SEA | 86 | 91 | 86 | -5 | 0 | 15% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Luther Burden III | CHI | 87 | 66 | 66 | +21 | +21 | 0% | PROSPECT_HISTORY |
| Tez Johnson | TB | 88 | 82 | 82 | +6 | +6 | 5% | PROSPECT_HISTORY |
| DeMario Douglas | NE | 89 | 69 | 69 | +20 | +20 | 0% | MANUAL_REVIEW_REQUIRED |
| Christian Kirk | SF | 90 | 56 | 56 | +34 | +34 | 0% | MANUAL_REVIEW_REQUIRED |
| Isaiah Bond | CLE | 91 | 118 | 118 | -27 | -27 | 0% | PROSPECT_HISTORY |
| Tre Harris | LAC | 92 | 97 | 97 | -5 | -5 | 5% | PROSPECT_HISTORY |
| Treylon Burks | WAS | 93 | 121 | 121 | -28 | -28 | 0% | MANUAL_REVIEW_REQUIRED |
| Isaac TeSlaa | DET | 94 | 89 | 89 | +5 | +5 | 0% | PROSPECT_HISTORY |
| Casey Washington | ATL | 95 | 169 | 95 | -74 | 0 | 10% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Marquez Valdes-Scantling | DAL | 96 | 99 | 99 | -3 | -3 | 0% | NONE |
| Cedric Tillman | CLE | 97 | 95 | 95 | +2 | +2 | 0% | NONE |
| Jalen Tolbert | MIA | 98 | 105 | 105 | -7 | -7 | 0% | NONE |
| John Metchie III | CAR | 99 | 113 | 113 | -14 | -14 | 0% | NONE |
| Lil'Jordan Humphrey | DEN | 100 | 104 | 104 | -4 | -4 | 0% | NONE |

#### Movement Tables (WR)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| DJ Moore | BUF | 69 | 23 | +46 | WOPR: 0.50, Target Share: 0.22 |
| Michael Pittman | PIT | 52 | 15 | +37 | WOPR: 0.55, Target Share: 0.25 |
| Christian Kirk | SF | 90 | 56 | +34 | WOPR: 0.43, Target Share: 0.18 |
| Chris Godwin Jr. | TB | 62 | 33 | +29 | WOPR: 0.47, Target Share: 0.21 |
| Calvin Ridley | TEN | 46 | 25 | +21 | WOPR: 0.55, Target Share: 0.21 |
| Luther Burden III | CHI | 87 | 66 | +21 | WOPR: 0.30, Target Share: 0.14 |
| DeMario Douglas | NE | 89 | 69 | +20 | WOPR: 0.30, Target Share: 0.14 |
| Josh Downs | IND | 59 | 40 | +19 | WOPR: 0.42, Target Share: 0.20 |
| DK Metcalf | PIT | 34 | 18 | +16 | WOPR: 0.55, Target Share: 0.21 |
| Rashod Bateman | BAL | 83 | 67 | +16 | WOPR: 0.36, Target Share: 0.13 |
| Tee Higgins | CIN | 24 | 9 | +15 | WOPR: 0.54, Target Share: 0.20 |
| Malik Nabers | NYG | 18 | 5 | +13 | WOPR: 0.80, Target Share: 0.32 |
| Xavier Worthy | KC | 54 | 42 | +12 | WOPR: 0.48, Target Share: 0.19 |
| CeeDee Lamb | DAL | 14 | 3 | +11 | WOPR: 0.66, Target Share: 0.28 |
| Marvin Harrison | ARI | 35 | 24 | +11 | WOPR: 0.56, Target Share: 0.20 |

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Tyquan Thornton | KC | 73 | 119 | -46 | WOPR: 0.25, Target Share: 0.08 |
| Xavier Hutchinson | HOU | 82 | 124 | -42 | WOPR: 0.23, Target Share: 0.10 |
| Adonai Mitchell | NYJ | 70 | 106 | -36 | WOPR: 0.34, Target Share: 0.13 |
| Pat Bryant | DEN | 80 | 115 | -35 | WOPR: 0.18, Target Share: 0.08 |
| Troy Franklin | DEN | 42 | 76 | -34 | WOPR: 0.37, Target Share: 0.14 |
| Van Jefferson | WAS | 66 | 100 | -34 | WOPR: 0.26, Target Share: 0.10 |
| Olamide Zaccheaus | ATL | 74 | 107 | -33 | WOPR: 0.17, Target Share: 0.08 |
| Ricky Pearsall | SF | 41 | 72 | -31 | WOPR: 0.33, Target Share: 0.13 |
| Christian Watson | GB | 32 | 61 | -29 | WOPR: 0.39, Target Share: 0.15 |
| Treylon Burks | WAS | 93 | 121 | -28 | WOPR: 0.26, Target Share: 0.10 |
| Isaiah Bond | CLE | 91 | 118 | -27 | WOPR: 0.29, Target Share: 0.09 |
| Rome Odunze | CHI | 19 | 43 | -24 | WOPR: 0.49, Target Share: 0.19 |
| Rashee Rice | KC | 7 | 30 | -23 | WOPR: 0.47, Target Share: 0.24 |
| Jameson Williams | DET | 28 | 51 | -23 | WOPR: 0.40, Target Share: 0.13 |
| Quentin Johnston | LAC | 31 | 53 | -22 | WOPR: 0.43, Target Share: 0.18 |

---

### TE Board — Status: **Held behind Current Pigskin**

- **Finalist Model**: `ranking_bqml_v2_adv_half_ppr_te_logistic_elite_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Trey McBride | ARI | 1 | 1 | 1 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Brock Bowers | LV | 2 | 2 | 2 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Tucker Kraft | GB | 3 | 26 | 3 | -23 | 0 | 0% | HELD_BOARD_ANCHOR |
| George Kittle | SF | 4 | 4 | 4 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Kyle Pitts | ATL | 5 | 7 | 5 | -2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Tyler Warren | IND | 6 | 5 | 6 | +1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Sam LaPorta | DET | 7 | 9 | 7 | -2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dallas Goedert | PHI | 8 | 14 | 8 | -6 | 0 | 0% | HELD_BOARD_ANCHOR |
| Travis Kelce | KC | 9 | 3 | 9 | +6 | 0 | 0% | HELD_BOARD_ANCHOR |
| Hunter Henry | NE | 10 | 10 | 10 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dalton Schultz | HOU | 11 | 18 | 11 | -7 | 0 | 0% | HELD_BOARD_ANCHOR |
| Juwan Johnson | NO | 12 | 11 | 12 | +1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Colston Loveland | CHI | 13 | 6 | 13 | +7 | 0 | 0% | HELD_BOARD_ANCHOR |
| Jake Ferguson | DAL | 14 | 13 | 14 | +1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Brenton Strange | JAX | 15 | 33 | 15 | -18 | 0 | 0% | HELD_BOARD_ANCHOR |
| Harold Fannin Jr. | CLE | 16 | 8 | 16 | +8 | 0 | 0% | HELD_BOARD_ANCHOR |
| Cade Otton | TB | 17 | 19 | 17 | -2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Theo Johnson | NYG | 18 | 23 | 18 | -5 | 0 | 0% | HELD_BOARD_ANCHOR |
| Mason Taylor | NYJ | 19 | 21 | 19 | -2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Oronde Gadsden II | LAC | 20 | 27 | 20 | -7 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dalton Kincaid | BUF | 21 | 17 | 21 | +4 | 0 | 0% | HELD_BOARD_ANCHOR |
| AJ Barner | SEA | 22 | 31 | 22 | -9 | 0 | 0% | HELD_BOARD_ANCHOR |
| Mark Andrews | BAL | 23 | 16 | 23 | +7 | 0 | 0% | HELD_BOARD_ANCHOR |
| T.J. Hockenson | MIN | 24 | 12 | 24 | +12 | 0 | 0% | HELD_BOARD_ANCHOR |
| Jake Tonges | SF | 25 | 48 | 25 | -23 | 0 | 0% | HELD_BOARD_ANCHOR |
| Albert Okwuegbunam | LV | 26 | 84 | 26 | -58 | 0 | 5% | HELD_BOARD_ANCHOR |
| Drake Dabney | GB | 27 | 30 | 27 | -3 | 0 | 25% | HELD_BOARD_ANCHOR |
| Greg Dulcich | MIA | 28 | 56 | 28 | -28 | 0 | 0% | HELD_BOARD_ANCHOR |
| David Njoku | LAC | 29 | 15 | 29 | +14 | 0 | 0% | HELD_BOARD_ANCHOR |
| Colby Parkinson | LAR | 30 | 41 | 30 | -11 | 0 | 0% | HELD_BOARD_ANCHOR |
| Pat Freiermuth | PIT | 31 | 25 | 31 | +6 | 0 | 0% | HELD_BOARD_ANCHOR |
| Darnell Washington | PIT | 32 | 50 | 32 | -18 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dawson Knox | BUF | 33 | 47 | 33 | -14 | 0 | 0% | HELD_BOARD_ANCHOR |
| Evan Engram | DEN | 34 | 29 | 34 | +5 | 0 | 0% | HELD_BOARD_ANCHOR |
| Cole Kmet | CHI | 35 | 22 | 35 | +13 | 0 | 0% | HELD_BOARD_ANCHOR |

#### Movement Tables (TE)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|

---

## Phase 33.27 RB Refinement Addendum

Phase 33.27 audited the accepted RB boards after the Phase 33.26D elite market-miss finding.

Decision: `RB POSITIONAL BOARD READY WITH ELITE TRIPWIRES`.

Selected review-only RB board candidate: `anchored_blend_tripwire`.

Key findings:

- Jahmyr Gibbs is a guarded RB queue miss, not a top-100 interleaver-only miss.
- Existing RB finalists bury receiving/role-expansion backs too far before top-100 selection.
- Current Pigskin hold alone fails the market top-3 RB tripwire for Ashton Jeanty.
- Existing alternates do not repair Gibbs, Achane, and Chase Brown cleanly enough.
- The selected candidate uses tiered Current Pigskin anchoring plus elite RB tripwire locks.

Selected top 12 RB shape for review-only rebuild:

| Rank | Player |
| ---: | --- |
| 1 | Christian McCaffrey |
| 2 | Bijan Robinson |
| 3 | Jahmyr Gibbs |
| 4 | Ashton Jeanty |
| 5 | Jonathan Taylor |
| 6 | De'Von Achane |
| 7 | Chase Brown |
| 8 | Saquon Barkley |
| 9 | Kyren Williams |
| 10 | Javonte Williams |
| 11 | James Cook |
| 12 | Omarion Hampton |

This addendum is review-only. No live ranking writes, champion activation, deployment, Gemini call, Pigskin chat, or route-metric population occurred.

## PPR PROFILE BOARDS

### QB Board — Status: **Accepted with guardrails**

- **Finalist Model**: `ranking_bqml_v2_adv_ppr_qb_logistic_bust_advanced_v0`
- **Alternate Model**: `ranking_bqml_v2_adv_ppr_qb_linear_points_advanced_v0` *(REJECTED/HIDDEN due to rushing bias)*

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 32 | 0 | 0 | 5 | 3 | 0 | 0 | 0 | 4 | 1 | 4 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Josh Allen | BUF | 1 | 1 | 1 | 0 | 0 | 0% | NONE |
| Drake Maye | NE | 2 | 5 | 5 | -3 | -3 | 0% | NONE |
| Patrick Mahomes | KC | 3 | 6 | 6 | -3 | -3 | 0% | NONE |
| Brock Purdy | SF | 4 | 9 | 9 | -5 | -5 | 0% | NONE |
| Jalen Hurts | PHI | 5 | 4 | 4 | +1 | +1 | 0% | NONE |
| Trevor Lawrence | JAX | 6 | 11 | 11 | -5 | -5 | 0% | NONE |
| Daniel Jones | IND | 7 | 14 | 14 | -7 | -7 | 0% | NONE |
| Bo Nix | DEN | 8 | 8 | 8 | 0 | 0 | 0% | NONE |
| Caleb Williams | CHI | 9 | 12 | 12 | -3 | -3 | 0% | NONE |
| Matthew Stafford | LAR | 10 | 21 | 21 | -11 | -11 | 0% | NONE |
| Justin Herbert | LAC | 11 | 15 | 15 | -4 | -4 | 0% | NONE |
| Jayden Daniels | WAS | 12 | 3 | 3 | +9 | +9 | 0% | NONE |
| Dak Prescott | DAL | 13 | 10 | 10 | +3 | +3 | 0% | NONE |
| Lamar Jackson | BAL | 14 | 2 | 2 | +12 | +12 | 0% | NONE |
| Jordan Love | GB | 15 | 20 | 20 | -5 | -5 | 0% | NONE |
| Jaxson Dart | NYG | 16 | 7 | 7 | +9 | +9 | 0% | PROSPECT_HISTORY |
| Jared Goff | DET | 17 | 17 | 17 | 0 | 0 | 0% | NONE |
| Kyler Murray | MIN | 18 | 13 | 13 | +5 | +5 | 0% | QB_RUSHING_BIAS_WARNING |
| C.J. Stroud | HOU | 19 | 24 | 24 | -5 | -5 | 0% | NONE |
| Tyler Shough | NO | 20 | 22 | 22 | -2 | -2 | 0% | PROSPECT_HISTORY |
| Bryce Young | CAR | 21 | 37 | 37 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED |
| Aaron Rodgers | PIT | 22 | 42 | 42 | -20 | -20 | 0% | MANUAL_REVIEW_REQUIRED |
| Baker Mayfield | TB | 23 | 18 | 18 | +5 | +5 | 0% | NONE |
| Joe Burrow | CIN | 24 | 19 | 19 | +5 | +5 | 0% | NONE |
| Jacoby Brissett | ARI | 25 | 28 | 28 | -3 | -3 | 0% | NONE |
| Malik Willis | MIA | 26 | 23 | 23 | +3 | +3 | 0% | NONE |
| Sam Darnold | SEA | 27 | 25 | 25 | +2 | +2 | 0% | NONE |
| Geno Smith | NYJ | 28 | 30 | 30 | -2 | -2 | 0% | NONE |
| Tua Tagovailoa | ATL | 29 | 27 | 27 | +2 | +2 | 0% | NONE |
| Shedeur Sanders | CLE | 30 | 49 | 30 | -19 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Cam Ward | TEN | 31 | 55 | 55 | -24 | -24 | 0% | PROSPECT_HISTORY |
| Justin Fields | KC | 32 | 16 | 16 | +16 | +16 | 0% | QB_RUSHING_BIAS_WARNING, MANUAL_REVIEW_REQUIRED |
| Carson Wentz | MIN | 33 | 26 | 33 | +7 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Marcus Mariota | WAS | 34 | 34 | 34 | 0 | 0 | 0% | NONE |
| J.J. McCarthy | MIN | 35 | 40 | 40 | -5 | -5 | 0% | PROSPECT_HISTORY |
| Spencer Rattler | NO | 36 | 43 | 43 | -7 | -7 | 0% | NONE |
| Jake Browning | TB | 37 | 50 | 50 | -13 | -13 | 0% | NONE |
| Mac Jones | SF | 38 | 36 | 36 | +2 | +2 | 0% | NONE |
| Tyler Huntley | BAL | 39 | 29 | 29 | +10 | +10 | 0% | NONE |
| Joe Flacco | CIN | 40 | 45 | 45 | -5 | -5 | 0% | NONE |
| Fernando Mendoza | LV | 41 | 95 | 41 | -54 | 0 | 100% | HISTORY_JOIN_FAILED, CURRENT_PIGSKIN_ANCHOR |
| Jameis Winston | NYG | 42 | 31 | 31 | +11 | +11 | 0% | NONE |
| Davis Mills | HOU | 43 | 52 | 52 | -9 | -9 | 0% | NONE |
| Josh Johnson | CIN | 44 | 44 | 44 | 0 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Quinn Ewers | MIA | 45 | 57 | 45 | -12 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |

#### Movement Tables (QB)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Justin Fields | KC | 32 | 16 | +16 | Passing EPA/dropback: -0.16, Passing CPOE: -15.33 |
| Lamar Jackson | BAL | 14 | 2 | +12 | Passing EPA/dropback: 0.17, Passing CPOE: 5.44 |
| Jameis Winston | NYG | 42 | 31 | +11 | Passing EPA/dropback: -0.02, Passing CPOE: -9.79 |
| Tyler Huntley | BAL | 39 | 29 | +10 | Passing EPA/dropback: 0.01, Passing CPOE: 7.45 |
| Jayden Daniels | WAS | 12 | 3 | +9 | Passing EPA/dropback: 0.12, Passing CPOE: 1.60 |
| Jaxson Dart | NYG | 16 | 7 | +9 | Passing EPA/dropback: 0.01, Passing CPOE: -0.56 |
| Kyler Murray | MIN | 18 | 13 | +5 | Passing EPA/dropback: 0.03, Passing CPOE: 0.08 |
| Baker Mayfield | TB | 23 | 18 | +5 | Passing EPA/dropback: 0.25, Passing CPOE: 3.62 |
| Joe Burrow | CIN | 24 | 19 | +5 | Passing EPA/dropback: 0.11, Passing CPOE: 4.16 |
| Dak Prescott | DAL | 13 | 10 | +3 | Passing EPA/dropback: 0.08, Passing CPOE: 2.11 |
| Malik Willis | MIA | 26 | 23 | +3 | Passing EPA/dropback: 0.36, Passing CPOE: 10.90 |
| Sam Darnold | SEA | 27 | 25 | +2 | Passing EPA/dropback: -0.05, Passing CPOE: 1.28 |
| Tua Tagovailoa | ATL | 29 | 27 | +2 | Passing EPA/dropback: 0.03, Passing CPOE: -1.43 |
| Mac Jones | SF | 38 | 36 | +2 | Passing EPA/dropback: -0.17, Passing CPOE: -4.23 |
| Jalen Hurts | PHI | 5 | 4 | +1 | Passing EPA/dropback: 0.07, Passing CPOE: 3.94 |

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Cam Ward | TEN | 31 | 55 | -24 | Passing EPA/dropback: -0.20, Passing CPOE: -1.86 |
| Aaron Rodgers | PIT | 22 | 42 | -20 | Passing EPA/dropback: -0.69, Passing CPOE: -3.40 |
| Bryce Young | CAR | 21 | 37 | -16 | Passing EPA/dropback: -0.15, Passing CPOE: -1.18 |
| Jake Browning | TB | 37 | 50 | -13 | Passing EPA/dropback: -0.11, Passing CPOE: 2.42 |
| Matthew Stafford | LAR | 10 | 21 | -11 | Passing EPA/dropback: 0.21, Passing CPOE: 0.22 |
| Davis Mills | HOU | 43 | 52 | -9 | Passing EPA/dropback: -0.39, Passing CPOE: -2.44 |
| Daniel Jones | IND | 7 | 14 | -7 | Passing EPA/dropback: -0.11, Passing CPOE: 0.61 |
| Spencer Rattler | NO | 36 | 43 | -7 | Passing EPA/dropback: -0.21, Passing CPOE: -3.75 |
| Brock Purdy | SF | 4 | 9 | -5 | Passing EPA/dropback: 0.16, Passing CPOE: 2.12 |
| Trevor Lawrence | JAX | 6 | 11 | -5 | Passing EPA/dropback: 0.03, Passing CPOE: -1.74 |
| Jordan Love | GB | 15 | 20 | -5 | Passing EPA/dropback: 0.20, Passing CPOE: 1.59 |
| C.J. Stroud | HOU | 19 | 24 | -5 | Passing EPA/dropback: 0.02, Passing CPOE: -1.28 |
| J.J. McCarthy | MIN | 35 | 40 | -5 | Passing EPA/dropback: -0.22, Passing CPOE: -4.80 |
| Joe Flacco | CIN | 40 | 45 | -5 | Passing EPA/dropback: -0.12, Passing CPOE: 0.70 |
| Justin Herbert | LAC | 11 | 15 | -4 | Passing EPA/dropback: -0.18, Passing CPOE: -4.24 |

---

### RB Board — Status: **Accepted**

- **Finalist Model**: `ranking_bqml_v2_adv_ppr_rb_logistic_elite_advanced_v0`
- **Alternate Model**: `ranking_bqml_v2_adv_ppr_rb_linear_points_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 43 | 0 | 0 | 9 | 26 | 0 | 0 | 0 | 9 | 0 | 11 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels | Alt Rank | Finalist/Alternate Disagreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Christian McCaffrey | SF | 1 | 5 | 5 | -4 | -4 | 0% | NONE | 3 | +2 |
| Bijan Robinson | ATL | 2 | 1 | 1 | +1 | +1 | 0% | NONE | 2 | -1 |
| Jahmyr Gibbs | DET | 3 | 9 | 9 | -6 | -6 | 0% | NONE | 12 | -3 |
| De'Von Achane | MIA | 4 | 13 | 13 | -9 | -9 | 0% | NONE | 10 | +3 |
| Jonathan Taylor | IND | 5 | 3 | 3 | +2 | +2 | 0% | NONE | 8 | -5 |
| Chase Brown | CIN | 6 | 25 | 25 | -19 | -19 | 0% | MANUAL_REVIEW_REQUIRED | 25 | 0 |
| Javonte Williams | DAL | 7 | 16 | 16 | -9 | -9 | 0% | NONE | 17 | -1 |
| Saquon Barkley | PHI | 8 | 2 | 2 | +6 | +6 | 0% | NONE | 1 | +1 |
| Kyren Williams | LAR | 9 | 7 | 7 | +2 | +2 | 0% | NONE | 7 | 0 |
| Omarion Hampton | LAC | 10 | 55 | 55 | -45 | -45 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 58 | -3 |
| Ashton Jeanty | LV | 11 | 4 | 4 | +7 | +7 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 5 | -1 |
| James Cook | BUF | 12 | 22 | 22 | -10 | -10 | 0% | NONE | 29 | -7 |
| Josh Jacobs | GB | 13 | 14 | 14 | -1 | -1 | 0% | NONE | 18 | -4 |
| Travis Etienne | NO | 14 | 11 | 11 | +3 | +3 | 0% | NONE | 27 | -16 |
| Cam Skattebo | NYG | 15 | 30 | 15 | -15 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR, MANUAL_REVIEW_REQUIRED | 32 | -2 |
| Bucky Irving | TB | 16 | 23 | 23 | -7 | -7 | 0% | NONE | 28 | -5 |
| D'Andre Swift | CHI | 17 | 19 | 19 | -2 | -2 | 0% | NONE | 20 | -1 |
| Breece Hall | NYJ | 18 | 8 | 8 | +10 | +10 | 0% | NONE | 6 | +2 |
| Jaylen Warren | PIT | 19 | 33 | 33 | -14 | -14 | 0% | NONE | 35 | -2 |
| Derrick Henry | BAL | 20 | 6 | 6 | +14 | +14 | 0% | NONE | 4 | +2 |
| Rhamondre Stevenson | NE | 21 | 18 | 18 | +3 | +3 | 0% | NONE | 13 | +5 |
| Quinshon Judkins | CLE | 22 | 21 | 21 | +1 | +1 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 23 | -2 |
| Rico Dowdle | PIT | 23 | 42 | 42 | -19 | -19 | 0% | MANUAL_REVIEW_REQUIRED | 36 | +6 |
| Kenneth Gainwell | TB | 24 | 51 | 51 | -27 | -27 | 0% | MANUAL_REVIEW_REQUIRED | 46 | +5 |
| James Conner | ARI | 25 | 20 | 20 | +5 | +5 | 0% | NONE | 15 | +5 |
| J.K. Dobbins | DEN | 26 | 28 | 28 | -2 | -2 | 0% | NONE | 31 | -3 |
| Alvin Kamara | NO | 27 | 15 | 15 | +12 | +12 | 0% | NONE | 16 | -1 |
| Kenneth Walker III | KC | 28 | 17 | 17 | +11 | +11 | 0% | NONE | 24 | -7 |
| Aaron Jones | MIN | 29 | 24 | 24 | +5 | +5 | 0% | NONE | 9 | +15 |
| Zach Charbonnet | SEA | 30 | 40 | 40 | -10 | -10 | 0% | NONE | 47 | -7 |
| Tyrone Tracy Jr. | NYG | 31 | 27 | 27 | +4 | +4 | 0% | NONE | 21 | +6 |
| Tony Pollard | TEN | 32 | 10 | 10 | +22 | +22 | 0% | MANUAL_REVIEW_REQUIRED | 14 | -4 |
| TreVeyon Henderson | NE | 33 | 52 | 52 | -19 | -19 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 55 | -3 |
| Woody Marks | HOU | 34 | 29 | 29 | +5 | +5 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 30 | -1 |
| RJ Harvey | DEN | 35 | 37 | 37 | -2 | -2 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 33 | +4 |
| Trey Benson | ARI | 36 | 59 | 59 | -23 | -23 | 0% | MANUAL_REVIEW_REQUIRED | 62 | -3 |
| Kimani Vidal | LAC | 37 | 38 | 38 | -1 | -1 | 0% | NONE | 26 | +12 |
| Rachaad White | WAS | 38 | 26 | 26 | +12 | +12 | 0% | NONE | 22 | +4 |
| Kyle Monangai | CHI | 39 | 43 | 43 | -4 | -4 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 42 | +1 |
| David Montgomery | HOU | 40 | 35 | 35 | +5 | +5 | 0% | NONE | 44 | -9 |
| Tyjae Spears | TEN | 41 | 41 | 41 | 0 | 0 | 0% | NONE | 41 | 0 |
| Isiah Pacheco | DET | 42 | 32 | 32 | +10 | +10 | 0% | NONE | 34 | -2 |
| Chuba Hubbard | CAR | 43 | 12 | 12 | +31 | +31 | 0% | MANUAL_REVIEW_REQUIRED | 11 | +1 |
| Michael Carter | TEN | 44 | 49 | 49 | -5 | -5 | 0% | NONE | 54 | -5 |
| Jacory Croskey-Merritt | WAS | 45 | 31 | 31 | +14 | +14 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 49 | -18 |
| Jordan Mason | MIN | 46 | 36 | 36 | +10 | +10 | 0% | NONE | 45 | -9 |
| Jawhar Jordan | HOU | 47 | 47 | 47 | 0 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 40 | +7 |
| Chris Rodriguez Jr. | JAX | 48 | 58 | 58 | -10 | -10 | 0% | NONE | 74 | -16 |
| Tyler Allgeier | ARI | 49 | 45 | 45 | +4 | +4 | 0% | NONE | 65 | -20 |
| Blake Corum | LAR | 50 | 65 | 65 | -15 | -15 | 0% | NONE | 67 | -2 |
| Raheim Sanders | CLE | 51 | 67 | 51 | -16 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 71 | -4 |
| Devin Neal | NO | 52 | 50 | 52 | +2 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 51 | -1 |
| Devin Singletary | NYG | 53 | 34 | 34 | +19 | +19 | 0% | MANUAL_REVIEW_REQUIRED | 37 | -3 |
| Emanuel Wilson | SEA | 54 | 83 | 83 | -29 | -29 | 0% | MANUAL_REVIEW_REQUIRED | 78 | +5 |
| Samaje Perine | CIN | 55 | 61 | 61 | -6 | -6 | 0% | NONE | 59 | +2 |
| Dylan Sampson | CLE | 56 | 76 | 76 | -20 | -20 | 15% | PROSPECT_HISTORY | 63 | +13 |
| Phil Mafah | DAL | 57 | 84 | 57 | -27 | 0 | 31% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 86 | -2 |
| Jaylen Wright | MIA | 58 | 75 | 75 | -17 | -17 | 0% | MANUAL_REVIEW_REQUIRED | 90 | -15 |
| Ty Johnson | BUF | 59 | 62 | 62 | -3 | -3 | 0% | NONE | 61 | +1 |
| Bhayshul Tuten | JAX | 60 | 48 | 48 | +12 | +12 | 0% | PROSPECT_HISTORY | 57 | -9 |
| Justice Hill | BAL | 61 | 44 | 44 | +17 | +17 | 0% | MANUAL_REVIEW_REQUIRED | 43 | +1 |
| Jaret Patterson | LAC | 62 | 81 | 62 | -19 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 89 | -8 |
| Kendre Miller | NO | 63 | 74 | 74 | -11 | -11 | 0% | NONE | 76 | -2 |
| Jeremy McNichols | WAS | 64 | 94 | 94 | -30 | -30 | 31% | MANUAL_REVIEW_REQUIRED | 99 | -5 |
| Emari Demercado | KC | 65 | 64 | 64 | +1 | +1 | 0% | NONE | 56 | +8 |
| Braelon Allen | NYJ | 66 | 82 | 82 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED | 79 | +3 |
| Keaton Mitchell | LAC | 67 | 108 | 108 | -41 | -41 | 15% | MANUAL_REVIEW_REQUIRED | 108 | 0 |
| Isaiah Davis | NYJ | 68 | 71 | 71 | -3 | -3 | 8% | NONE | 72 | -1 |
| Jaydon Blue | DAL | 69 | 72 | 69 | -3 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 69 | +3 |
| Jerome Ford | WAS | 70 | 39 | 39 | +31 | +31 | 0% | MANUAL_REVIEW_REQUIRED | 38 | +1 |
| Brian Robinson | ATL | 71 | 46 | 46 | +25 | +25 | 0% | MANUAL_REVIEW_REQUIRED | 53 | -7 |
| Sean Tucker | TB | 72 | 66 | 66 | +6 | +6 | 0% | NONE | 70 | -4 |
| Brashard Smith | KC | 73 | 78 | 78 | -5 | -5 | 0% | PROSPECT_HISTORY | 64 | +14 |
| Malik Davis | DAL | 74 | 95 | 95 | -21 | -21 | 0% | MANUAL_REVIEW_REQUIRED | 104 | -9 |
| Tank Bigsby | PHI | 75 | 77 | 77 | -2 | -2 | 0% | NONE | 85 | -8 |
| DJ Giddens | IND | 76 | 91 | 76 | -15 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 92 | -1 |
| Ray Davis | BUF | 77 | 56 | 56 | +21 | +21 | 0% | MANUAL_REVIEW_REQUIRED | 39 | +17 |
| Zavier Scott | MIN | 78 | 106 | 78 | -28 | 0 | 31% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 97 | +9 |
| Jaleel McLaughlin | DEN | 79 | 88 | 88 | -9 | -9 | 0% | NONE | 93 | -5 |
| Ameer Abdullah | JAX | 80 | 70 | 70 | +10 | +10 | 0% | NONE | 52 | +18 |

#### Movement Tables (RB)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Chuba Hubbard | CAR | 43 | 12 | +31 | Weighted Opportunity: 153.98, NGS Rushes Over Expected: 5.09 |
| Jerome Ford | WAS | 70 | 39 | +31 | Weighted Opportunity: 103.98, NGS Rushes Over Expected: 6.06 |
| Brian Robinson | ATL | 71 | 46 | +25 | Weighted Opportunity: 90.23, NGS Rushes Over Expected: -0.09 |
| Tony Pollard | TEN | 32 | 10 | +22 | Weighted Opportunity: 184.87, NGS Rushes Over Expected: -2.17 |
| Ray Davis | BUF | 77 | 56 | +21 | Weighted Opportunity: 40.96, NGS Rushes Over Expected: 32.11 |
| Devin Singletary | NYG | 53 | 34 | +19 | Weighted Opportunity: 104.92, NGS Rushes Over Expected: 5.17 |
| Justice Hill | BAL | 61 | 44 | +17 | Weighted Opportunity: 65.17, NGS Rushes Over Expected: 4.61 |
| Derrick Henry | BAL | 20 | 6 | +14 | Weighted Opportunity: 178.01, NGS Rushes Over Expected: 26.91 |
| Jacory Croskey-Merritt | WAS | 45 | 31 | +14 | Weighted Opportunity: 129.04, NGS Rushes Over Expected: 12.64 |
| Alvin Kamara | NO | 27 | 15 | +12 | Weighted Opportunity: 224.26, NGS Rushes Over Expected: -5.25 |
| Rachaad White | WAS | 38 | 26 | +12 | Weighted Opportunity: 128.27, NGS Rushes Over Expected: -2.11 |
| Bhayshul Tuten | JAX | 60 | 48 | +12 | Weighted Opportunity: 43.01, NGS Rushes Over Expected: 12.00 |
| Kenneth Walker III | KC | 28 | 17 | +11 | Weighted Opportunity: 156.35, NGS Rushes Over Expected: 5.72 |
| Breece Hall | NYJ | 18 | 8 | +10 | Weighted Opportunity: 245.50, NGS Rushes Over Expected: 7.05 |
| Isiah Pacheco | DET | 42 | 32 | +10 | Weighted Opportunity: 98.71, NGS Rushes Over Expected: 0.38 |

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Omarion Hampton | LAC | 10 | 55 | -45 | Weighted Opportunity: 67.70, NGS Rushes Over Expected: 10.81 |
| Keaton Mitchell | LAC | 67 | 108 | -41 | Weighted Opportunity: 27.32, NGS Rushes Over Expected: -21.24 |
| Jeremy McNichols | WAS | 64 | 94 | -30 | Weighted Opportunity: 34.09, NGS Rushes Over Expected: 0.00 |
| Emanuel Wilson | SEA | 54 | 83 | -29 | Weighted Opportunity: 37.27, NGS Rushes Over Expected: 5.08 |
| Kenneth Gainwell | TB | 24 | 51 | -27 | Weighted Opportunity: 75.66, NGS Rushes Over Expected: -1.25 |
| Trey Benson | ARI | 36 | 59 | -23 | Weighted Opportunity: 41.84, NGS Rushes Over Expected: 1.77 |
| Malik Davis | DAL | 74 | 95 | -21 | Weighted Opportunity: 19.31, NGS Rushes Over Expected: 7.01 |
| Dylan Sampson | CLE | 56 | 76 | -20 | Weighted Opportunity: 102.92, NGS Rushes Over Expected: -7.18 |
| Chase Brown | CIN | 6 | 25 | -19 | Weighted Opportunity: 197.31, NGS Rushes Over Expected: 6.32 |
| Rico Dowdle | PIT | 23 | 42 | -19 | Weighted Opportunity: 107.98, NGS Rushes Over Expected: 9.18 |
| TreVeyon Henderson | NE | 33 | 52 | -19 | Weighted Opportunity: 102.99, NGS Rushes Over Expected: -6.83 |
| Jaylen Wright | MIA | 58 | 75 | -17 | Weighted Opportunity: 51.29, NGS Rushes Over Expected: 5.78 |
| Braelon Allen | NYJ | 66 | 82 | -16 | Weighted Opportunity: 57.52, NGS Rushes Over Expected: -3.12 |
| Blake Corum | LAR | 50 | 65 | -15 | Weighted Opportunity: 59.74, NGS Rushes Over Expected: -0.45 |
| Jaylen Warren | PIT | 19 | 33 | -14 | Weighted Opportunity: 97.06, NGS Rushes Over Expected: 6.49 |

---

### WR Board — Status: **Accepted**

- **Finalist Model**: `ranking_bqml_v2_adv_ppr_wr_logistic_elite_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 56 | 0 | 0 | 5 | 33 | 0 | 0 | 0 | 5 | 0 | 13 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Jaxon Smith-Njigba | SEA | 1 | 7 | 7 | -6 | -6 | 0% | NONE |
| Puka Nacua | LAR | 2 | 4 | 4 | -2 | -2 | 0% | NONE |
| Ja'Marr Chase | CIN | 3 | 1 | 1 | +2 | +2 | 0% | NONE |
| Amon-Ra St. Brown | DET | 4 | 2 | 2 | +2 | +2 | 0% | NONE |
| Drake London | ATL | 5 | 5 | 5 | 0 | 0 | 0% | NONE |
| Garrett Wilson | NYJ | 6 | 12 | 12 | -6 | -6 | 0% | NONE |
| Rashee Rice | KC | 7 | 29 | 29 | -22 | -22 | 0% | MANUAL_REVIEW_REQUIRED |
| Chris Olave | NO | 8 | 17 | 17 | -9 | -9 | 0% | NONE |
| A.J. Brown | NE | 9 | 8 | 8 | +1 | +1 | 0% | NONE |
| George Pickens | DAL | 10 | 15 | 15 | -5 | -5 | 0% | NONE |
| Justin Jefferson | MIN | 11 | 11 | 11 | 0 | 0 | 0% | NONE |
| Zay Flowers | BAL | 12 | 14 | 14 | -2 | -2 | 0% | NONE |
| CeeDee Lamb | DAL | 13 | 3 | 3 | +10 | +10 | 0% | NONE |
| Davante Adams | LAR | 14 | 10 | 10 | +4 | +4 | 0% | NONE |
| Nico Collins | HOU | 15 | 20 | 20 | -5 | -5 | 0% | NONE |
| Wan'Dale Robinson | TEN | 16 | 31 | 31 | -15 | -15 | 0% | NONE |
| Tetairoa McMillan | CAR | 17 | 39 | 39 | -22 | -22 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Malik Nabers | NYG | 18 | 6 | 6 | +12 | +12 | 0% | NONE |
| Rome Odunze | CHI | 19 | 43 | 43 | -24 | -24 | 0% | MANUAL_REVIEW_REQUIRED |
| DeVonta Smith | PHI | 20 | 19 | 19 | +1 | +1 | 0% | NONE |
| Terry McLaurin | WAS | 21 | 16 | 16 | +5 | +5 | 0% | NONE |
| Jaylen Waddle | DEN | 22 | 30 | 30 | -8 | -8 | 0% | NONE |
| Tee Higgins | CIN | 23 | 9 | 9 | +14 | +14 | 0% | NONE |
| Courtland Sutton | DEN | 24 | 22 | 22 | +2 | +2 | 0% | NONE |
| Alec Pierce | IND | 25 | 34 | 34 | -9 | -9 | 0% | NONE |
| Emeka Egbuka | TB | 26 | 27 | 27 | -1 | -1 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Jakobi Meyers | JAX | 27 | 35 | 35 | -8 | -8 | 0% | NONE |
| Jameson Williams | DET | 28 | 51 | 51 | -23 | -23 | 0% | MANUAL_REVIEW_REQUIRED |
| Mike Evans | SF | 29 | 21 | 21 | +8 | +8 | 0% | NONE |
| Michael Wilson | ARI | 30 | 41 | 41 | -11 | -11 | 0% | NONE |
| Quentin Johnston | LAC | 31 | 54 | 54 | -23 | -23 | 0% | MANUAL_REVIEW_REQUIRED |
| Christian Watson | GB | 32 | 62 | 62 | -30 | -30 | 0% | MANUAL_REVIEW_REQUIRED |
| Jordan Addison | MIN | 33 | 36 | 36 | -3 | -3 | 0% | NONE |
| DK Metcalf | PIT | 34 | 18 | 18 | +16 | +16 | 0% | MANUAL_REVIEW_REQUIRED |
| Marvin Harrison | ARI | 35 | 24 | 24 | +11 | +11 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Ladd McConkey | LAC | 36 | 26 | 26 | +10 | +10 | 0% | NONE |
| Jauan Jennings | MIN | 37 | 52 | 52 | -15 | -15 | 0% | NONE |
| Romeo Doubs | NE | 38 | 44 | 44 | -6 | -6 | 0% | NONE |
| Tre Tucker | LV | 39 | 55 | 55 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED |
| Parker Washington | JAX | 40 | 53 | 53 | -13 | -13 | 0% | NONE |
| Ricky Pearsall | SF | 41 | 72 | 72 | -31 | -31 | 0% | MANUAL_REVIEW_REQUIRED |
| Troy Franklin | DEN | 42 | 74 | 74 | -32 | -32 | 0% | MANUAL_REVIEW_REQUIRED |
| Jerry Jeudy | CLE | 43 | 32 | 32 | +11 | +11 | 0% | NONE |
| Khalil Shakir | BUF | 44 | 45 | 45 | -1 | -1 | 0% | NONE |
| Elic Ayomanor | TEN | 45 | 58 | 58 | -13 | -13 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Darius Slayton | NYG | 46 | 47 | 47 | -1 | -1 | 0% | NONE |
| Calvin Ridley | TEN | 47 | 25 | 25 | +22 | +22 | 0% | MANUAL_REVIEW_REQUIRED |
| Keon Coleman | BUF | 48 | 64 | 64 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED |
| Brian Thomas Jr. | JAX | 49 | 40 | 40 | +9 | +9 | 0% | NONE |
| Darnell Mooney | NYG | 50 | 46 | 46 | +4 | +4 | 0% | NONE |
| Michael Pittman | PIT | 51 | 13 | 13 | +38 | +38 | 0% | MANUAL_REVIEW_REQUIRED |
| Travis Hunter | JAX | 52 | 73 | 52 | -21 | 0 | 5% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR, MANUAL_REVIEW_REQUIRED |
| Mack Hollins | NE | 53 | 75 | 75 | -22 | -22 | 0% | MANUAL_REVIEW_REQUIRED |
| Xavier Worthy | KC | 54 | 42 | 42 | +12 | +12 | 0% | NONE |
| Jakobie Keeney-James | GB | 55 | 49 | 55 | +6 | 0 | 30% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR, MANUAL_REVIEW_REQUIRED |
| Jayden Reed | GB | 56 | 56 | 56 | 0 | 0 | 0% | NONE |
| Kayshon Boutte | NE | 57 | 68 | 68 | -11 | -11 | 0% | NONE |
| Jalen Coker | CAR | 58 | 48 | 48 | +10 | +10 | 0% | NONE |
| Josh Downs | IND | 59 | 38 | 38 | +21 | +21 | 0% | MANUAL_REVIEW_REQUIRED |
| Rashid Shaheed | SEA | 60 | 63 | 63 | -3 | -3 | 0% | NONE |
| Cooper Kupp | SEA | 61 | 50 | 50 | +11 | +11 | 0% | NONE |
| Chris Godwin Jr. | TB | 62 | 33 | 33 | +29 | +29 | 0% | MANUAL_REVIEW_REQUIRED |
| Jalen McMillan | TB | 63 | 60 | 60 | +3 | +3 | 0% | NONE |
| Devaughn Vele | NO | 64 | 80 | 80 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED |
| Marquise Brown | PHI | 65 | 59 | 59 | +6 | +6 | 0% | NONE |
| Van Jefferson | WAS | 66 | 102 | 102 | -36 | -36 | 0% | MANUAL_REVIEW_REQUIRED |
| Xavier Legette | CAR | 67 | 79 | 79 | -12 | -12 | 0% | NONE |
| Jayden Higgins | HOU | 68 | 67 | 67 | +1 | +1 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| DJ Moore | BUF | 69 | 23 | 23 | +46 | +46 | 0% | MANUAL_REVIEW_REQUIRED |
| Adonai Mitchell | NYJ | 70 | 108 | 108 | -38 | -38 | 5% | MANUAL_REVIEW_REQUIRED |
| Theo Wease Jr. | MIA | 71 | 109 | 71 | -38 | 0 | 5% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Andrei Iosivas | CIN | 72 | 77 | 77 | -5 | -5 | 0% | NONE |
| Tyquan Thornton | KC | 73 | 121 | 121 | -48 | -48 | 0% | MANUAL_REVIEW_REQUIRED |
| Olamide Zaccheaus | ATL | 74 | 107 | 107 | -33 | -33 | 0% | MANUAL_REVIEW_REQUIRED |
| Chimere Dike | TEN | 75 | 61 | 61 | +14 | +14 | 0% | PROSPECT_HISTORY |
| Malik Washington | MIA | 76 | 85 | 85 | -9 | -9 | 0% | NONE |
| Kendrick Bourne | ARI | 77 | 83 | 83 | -6 | -6 | 0% | NONE |
| Ryan Flournoy | DAL | 78 | 91 | 91 | -13 | -13 | 0% | NONE |
| Calvin Austin III | NYG | 79 | 97 | 97 | -18 | -18 | 0% | MANUAL_REVIEW_REQUIRED |
| Pat Bryant | DEN | 80 | 112 | 112 | -32 | -32 | 0% | PROSPECT_HISTORY |
| Dontayvion Wicks | PHI | 81 | 76 | 76 | +5 | +5 | 0% | NONE |
| Xavier Hutchinson | HOU | 82 | 125 | 125 | -43 | -43 | 0% | MANUAL_REVIEW_REQUIRED |
| Matthew Golden | GB | 83 | 81 | 81 | +2 | +2 | 5% | PROSPECT_HISTORY |
| Rashod Bateman | BAL | 84 | 69 | 69 | +15 | +15 | 0% | NONE |
| Jalen Nailor | LV | 85 | 87 | 87 | -2 | -2 | 0% | NONE |
| Tory Horton | SEA | 86 | 93 | 86 | -7 | 0 | 15% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Luther Burden III | CHI | 87 | 66 | 66 | +21 | +21 | 0% | PROSPECT_HISTORY |
| Tez Johnson | TB | 88 | 82 | 82 | +6 | +6 | 5% | PROSPECT_HISTORY |
| DeMario Douglas | NE | 89 | 65 | 65 | +24 | +24 | 0% | MANUAL_REVIEW_REQUIRED |
| Christian Kirk | SF | 90 | 57 | 57 | +33 | +33 | 0% | MANUAL_REVIEW_REQUIRED |
| Isaiah Bond | CLE | 91 | 118 | 118 | -27 | -27 | 0% | PROSPECT_HISTORY |
| Tre Harris | LAC | 92 | 96 | 96 | -4 | -4 | 5% | PROSPECT_HISTORY |
| Treylon Burks | WAS | 93 | 123 | 123 | -30 | -30 | 0% | MANUAL_REVIEW_REQUIRED |
| Isaac TeSlaa | DET | 94 | 90 | 90 | +4 | +4 | 0% | PROSPECT_HISTORY |
| Marquez Valdes-Scantling | DAL | 95 | 106 | 106 | -11 | -11 | 0% | NONE |
| Casey Washington | ATL | 96 | 179 | 96 | -83 | 0 | 10% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Cedric Tillman | CLE | 97 | 94 | 94 | +3 | +3 | 0% | NONE |
| Jalen Tolbert | MIA | 98 | 101 | 101 | -3 | -3 | 0% | NONE |
| John Metchie III | CAR | 99 | 110 | 110 | -11 | -11 | 0% | NONE |
| Lil'Jordan Humphrey | DEN | 100 | 103 | 103 | -3 | -3 | 0% | NONE |

#### Movement Tables (WR)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| DJ Moore | BUF | 69 | 23 | +46 | WOPR: 0.50, Target Share: 0.22 |
| Michael Pittman | PIT | 51 | 13 | +38 | WOPR: 0.55, Target Share: 0.25 |
| Christian Kirk | SF | 90 | 57 | +33 | WOPR: 0.43, Target Share: 0.18 |
| Chris Godwin Jr. | TB | 62 | 33 | +29 | WOPR: 0.47, Target Share: 0.21 |
| DeMario Douglas | NE | 89 | 65 | +24 | WOPR: 0.30, Target Share: 0.14 |
| Calvin Ridley | TEN | 47 | 25 | +22 | WOPR: 0.55, Target Share: 0.21 |
| Josh Downs | IND | 59 | 38 | +21 | WOPR: 0.42, Target Share: 0.20 |
| Luther Burden III | CHI | 87 | 66 | +21 | WOPR: 0.30, Target Share: 0.14 |
| DK Metcalf | PIT | 34 | 18 | +16 | WOPR: 0.55, Target Share: 0.21 |
| Rashod Bateman | BAL | 84 | 69 | +15 | WOPR: 0.36, Target Share: 0.13 |
| Tee Higgins | CIN | 23 | 9 | +14 | WOPR: 0.54, Target Share: 0.20 |
| Chimere Dike | TEN | 75 | 61 | +14 | WOPR: 0.31, Target Share: 0.14 |
| Malik Nabers | NYG | 18 | 6 | +12 | WOPR: 0.80, Target Share: 0.32 |
| Xavier Worthy | KC | 54 | 42 | +12 | WOPR: 0.48, Target Share: 0.19 |
| Marvin Harrison | ARI | 35 | 24 | +11 | WOPR: 0.56, Target Share: 0.20 |

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Tyquan Thornton | KC | 73 | 121 | -48 | WOPR: 0.25, Target Share: 0.08 |
| Xavier Hutchinson | HOU | 82 | 125 | -43 | WOPR: 0.23, Target Share: 0.10 |
| Adonai Mitchell | NYJ | 70 | 108 | -38 | WOPR: 0.34, Target Share: 0.13 |
| Van Jefferson | WAS | 66 | 102 | -36 | WOPR: 0.26, Target Share: 0.10 |
| Olamide Zaccheaus | ATL | 74 | 107 | -33 | WOPR: 0.17, Target Share: 0.08 |
| Troy Franklin | DEN | 42 | 74 | -32 | WOPR: 0.37, Target Share: 0.14 |
| Pat Bryant | DEN | 80 | 112 | -32 | WOPR: 0.18, Target Share: 0.08 |
| Ricky Pearsall | SF | 41 | 72 | -31 | WOPR: 0.33, Target Share: 0.13 |
| Christian Watson | GB | 32 | 62 | -30 | WOPR: 0.39, Target Share: 0.15 |
| Treylon Burks | WAS | 93 | 123 | -30 | WOPR: 0.26, Target Share: 0.10 |
| Isaiah Bond | CLE | 91 | 118 | -27 | WOPR: 0.29, Target Share: 0.09 |
| Rome Odunze | CHI | 19 | 43 | -24 | WOPR: 0.49, Target Share: 0.19 |
| Jameson Williams | DET | 28 | 51 | -23 | WOPR: 0.40, Target Share: 0.13 |
| Quentin Johnston | LAC | 31 | 54 | -23 | WOPR: 0.43, Target Share: 0.18 |
| Rashee Rice | KC | 7 | 29 | -22 | WOPR: 0.47, Target Share: 0.24 |

---

### TE Board — Status: **Held behind Current Pigskin**

- **Finalist Model**: `ranking_bqml_v2_adv_ppr_te_logistic_bust_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Trey McBride | ARI | 1 | 1 | 1 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Brock Bowers | LV | 2 | 2 | 2 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Tucker Kraft | GB | 3 | 26 | 3 | -23 | 0 | 0% | HELD_BOARD_ANCHOR |
| George Kittle | SF | 4 | 5 | 4 | -1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Kyle Pitts | ATL | 5 | 7 | 5 | -2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Tyler Warren | IND | 6 | 4 | 6 | +2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Sam LaPorta | DET | 7 | 9 | 7 | -2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dallas Goedert | PHI | 8 | 15 | 8 | -7 | 0 | 0% | HELD_BOARD_ANCHOR |
| Travis Kelce | KC | 9 | 3 | 9 | +6 | 0 | 0% | HELD_BOARD_ANCHOR |
| Hunter Henry | NE | 10 | 10 | 10 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dalton Schultz | HOU | 11 | 16 | 11 | -5 | 0 | 0% | HELD_BOARD_ANCHOR |
| Juwan Johnson | NO | 12 | 11 | 12 | +1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Colston Loveland | CHI | 13 | 6 | 13 | +7 | 0 | 0% | HELD_BOARD_ANCHOR |
| Jake Ferguson | DAL | 14 | 13 | 14 | +1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Brenton Strange | JAX | 15 | 33 | 15 | -18 | 0 | 0% | HELD_BOARD_ANCHOR |
| Harold Fannin Jr. | CLE | 16 | 8 | 16 | +8 | 0 | 0% | HELD_BOARD_ANCHOR |
| Cade Otton | TB | 17 | 17 | 17 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Theo Johnson | NYG | 18 | 24 | 18 | -6 | 0 | 0% | HELD_BOARD_ANCHOR |
| Mason Taylor | NYJ | 19 | 20 | 19 | -1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Oronde Gadsden II | LAC | 20 | 28 | 20 | -8 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dalton Kincaid | BUF | 21 | 19 | 21 | +2 | 0 | 0% | HELD_BOARD_ANCHOR |
| AJ Barner | SEA | 22 | 31 | 22 | -9 | 0 | 0% | HELD_BOARD_ANCHOR |
| Mark Andrews | BAL | 23 | 18 | 23 | +5 | 0 | 0% | HELD_BOARD_ANCHOR |
| T.J. Hockenson | MIN | 24 | 12 | 24 | +12 | 0 | 0% | HELD_BOARD_ANCHOR |
| Albert Okwuegbunam | LV | 25 | 82 | 25 | -57 | 0 | 5% | HELD_BOARD_ANCHOR |
| Jake Tonges | SF | 26 | 48 | 26 | -22 | 0 | 0% | HELD_BOARD_ANCHOR |
| Greg Dulcich | MIA | 27 | 53 | 27 | -26 | 0 | 0% | HELD_BOARD_ANCHOR |
| Drake Dabney | GB | 28 | 30 | 28 | -2 | 0 | 25% | HELD_BOARD_ANCHOR |
| Colby Parkinson | LAR | 29 | 40 | 29 | -11 | 0 | 0% | HELD_BOARD_ANCHOR |
| David Njoku | LAC | 30 | 14 | 30 | +16 | 0 | 0% | HELD_BOARD_ANCHOR |
| Pat Freiermuth | PIT | 31 | 25 | 31 | +6 | 0 | 0% | HELD_BOARD_ANCHOR |
| Darnell Washington | PIT | 32 | 49 | 32 | -17 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dawson Knox | BUF | 33 | 47 | 33 | -14 | 0 | 0% | HELD_BOARD_ANCHOR |
| Evan Engram | DEN | 34 | 27 | 34 | +7 | 0 | 0% | HELD_BOARD_ANCHOR |
| Cole Kmet | CHI | 35 | 22 | 35 | +13 | 0 | 0% | HELD_BOARD_ANCHOR |

#### Movement Tables (TE)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|

---

## GNG KEEPER PROFILE BOARDS

### QB Board — Status: **Held behind Current Pigskin**

- **Finalist Model**: `ranking_bqml_v2_adv_gng_keeper_qb_linear_points_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Josh Allen | BUF | 1 | 1 | 1 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Drake Maye | NE | 2 | 7 | 2 | -5 | 0 | 0% | HELD_BOARD_ANCHOR |
| Brock Purdy | SF | 3 | 9 | 3 | -6 | 0 | 0% | HELD_BOARD_ANCHOR |
| Patrick Mahomes | KC | 4 | 6 | 4 | -2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Jalen Hurts | PHI | 5 | 2 | 5 | +3 | 0 | 0% | HELD_BOARD_ANCHOR |
| Trevor Lawrence | JAX | 6 | 8 | 6 | -2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Daniel Jones | IND | 7 | 13 | 7 | -6 | 0 | 0% | HELD_BOARD_ANCHOR |
| Bo Nix | DEN | 8 | 3 | 8 | +5 | 0 | 0% | HELD_BOARD_ANCHOR |
| Matthew Stafford | LAR | 9 | 15 | 9 | -6 | 0 | 0% | HELD_BOARD_ANCHOR |
| Caleb Williams | CHI | 10 | 11 | 10 | -1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Jayden Daniels | WAS | 11 | 5 | 11 | +6 | 0 | 0% | HELD_BOARD_ANCHOR |
| Justin Herbert | LAC | 12 | 14 | 12 | -2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dak Prescott | DAL | 13 | 10 | 13 | +3 | 0 | 0% | HELD_BOARD_ANCHOR |
| Lamar Jackson | BAL | 14 | 4 | 14 | +10 | 0 | 0% | HELD_BOARD_ANCHOR |
| Jordan Love | GB | 15 | 22 | 15 | -7 | 0 | 0% | HELD_BOARD_ANCHOR |
| Jaxson Dart | NYG | 16 | 16 | 16 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Jared Goff | DET | 17 | 12 | 17 | +5 | 0 | 0% | HELD_BOARD_ANCHOR |
| Aaron Rodgers | PIT | 18 | 33 | 18 | -15 | 0 | 0% | HELD_BOARD_ANCHOR |
| Kyler Murray | MIN | 19 | 18 | 19 | +1 | 0 | 0% | HELD_BOARD_ANCHOR |
| C.J. Stroud | HOU | 20 | 25 | 20 | -5 | 0 | 0% | HELD_BOARD_ANCHOR |
| Bryce Young | CAR | 21 | 37 | 21 | -16 | 0 | 0% | HELD_BOARD_ANCHOR |
| Tyler Shough | NO | 22 | 17 | 22 | +5 | 0 | 0% | HELD_BOARD_ANCHOR |
| Baker Mayfield | TB | 23 | 20 | 23 | +3 | 0 | 0% | HELD_BOARD_ANCHOR |
| Joe Burrow | CIN | 24 | 21 | 24 | +3 | 0 | 0% | HELD_BOARD_ANCHOR |
| Malik Willis | MIA | 25 | 26 | 25 | -1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Jacoby Brissett | ARI | 26 | 28 | 26 | -2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Sam Darnold | SEA | 27 | 23 | 27 | +4 | 0 | 0% | HELD_BOARD_ANCHOR |
| Tua Tagovailoa | ATL | 28 | 27 | 28 | +1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Geno Smith | NYJ | 29 | 30 | 29 | -1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Shedeur Sanders | CLE | 30 | 49 | 30 | -19 | 0 | 0% | HELD_BOARD_ANCHOR |
| Cam Ward | TEN | 31 | 47 | 31 | -16 | 0 | 0% | HELD_BOARD_ANCHOR |
| Justin Fields | KC | 32 | 19 | 32 | +13 | 0 | 0% | HELD_BOARD_ANCHOR |
| Carson Wentz | MIN | 33 | 24 | 33 | +9 | 0 | 0% | HELD_BOARD_ANCHOR |
| Marcus Mariota | WAS | 34 | 41 | 34 | -7 | 0 | 0% | HELD_BOARD_ANCHOR |
| J.J. McCarthy | MIN | 35 | 35 | 35 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Jake Browning | TB | 36 | 48 | 36 | -12 | 0 | 0% | HELD_BOARD_ANCHOR |
| Spencer Rattler | NO | 37 | 45 | 37 | -8 | 0 | 0% | HELD_BOARD_ANCHOR |
| Fernando Mendoza | LV | 38 | 99 | 38 | -61 | 0 | 100% | HELD_BOARD_ANCHOR |
| Mac Jones | SF | 39 | 34 | 39 | +5 | 0 | 0% | HELD_BOARD_ANCHOR |
| Joe Flacco | CIN | 40 | 42 | 40 | -2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Tyler Huntley | BAL | 41 | 32 | 41 | +9 | 0 | 0% | HELD_BOARD_ANCHOR |
| Davis Mills | HOU | 42 | 43 | 42 | -1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Josh Johnson | CIN | 43 | 44 | 43 | -1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Jameis Winston | NYG | 44 | 31 | 44 | +13 | 0 | 0% | HELD_BOARD_ANCHOR |
| Quinn Ewers | MIA | 45 | 55 | 45 | -10 | 0 | 0% | HELD_BOARD_ANCHOR |

#### Movement Tables (QB)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|

---

### RB Board — Status: **Accepted**

- **Finalist Model**: `ranking_bqml_v2_adv_gng_keeper_rb_linear_points_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 37 | 0 | 0 | 10 | 31 | 0 | 0 | 0 | 10 | 0 | 11 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Christian McCaffrey | SF | 1 | 5 | 5 | -4 | -4 | 0% | NONE |
| Bijan Robinson | ATL | 2 | 3 | 3 | -1 | -1 | 0% | NONE |
| Jahmyr Gibbs | DET | 3 | 18 | 18 | -15 | -15 | 0% | NONE |
| Jonathan Taylor | IND | 4 | 4 | 4 | 0 | 0 | 0% | NONE |
| De'Von Achane | MIA | 5 | 17 | 17 | -12 | -12 | 0% | NONE |
| Chase Brown | CIN | 6 | 32 | 32 | -26 | -26 | 0% | MANUAL_REVIEW_REQUIRED |
| Javonte Williams | DAL | 7 | 21 | 21 | -14 | -14 | 0% | NONE |
| Saquon Barkley | PHI | 8 | 1 | 1 | +7 | +7 | 0% | NONE |
| Kyren Williams | LAR | 9 | 6 | 6 | +3 | +3 | 0% | NONE |
| Omarion Hampton | LAC | 10 | 56 | 56 | -46 | -46 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Ashton Jeanty | LV | 11 | 7 | 7 | +4 | +4 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| James Cook | BUF | 12 | 22 | 22 | -10 | -10 | 0% | NONE |
| Josh Jacobs | GB | 13 | 14 | 14 | -1 | -1 | 0% | NONE |
| Travis Etienne | NO | 14 | 26 | 26 | -12 | -12 | 0% | NONE |
| Cam Skattebo | NYG | 15 | 31 | 15 | -16 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR, MANUAL_REVIEW_REQUIRED |
| Bucky Irving | TB | 16 | 29 | 29 | -13 | -13 | 0% | NONE |
| D'Andre Swift | CHI | 17 | 19 | 19 | -2 | -2 | 0% | NONE |
| Breece Hall | NYJ | 18 | 8 | 8 | +10 | +10 | 0% | NONE |
| Jaylen Warren | PIT | 19 | 37 | 37 | -18 | -18 | 0% | MANUAL_REVIEW_REQUIRED |
| Derrick Henry | BAL | 20 | 2 | 2 | +18 | +18 | 0% | MANUAL_REVIEW_REQUIRED |
| Rhamondre Stevenson | NE | 21 | 16 | 16 | +5 | +5 | 0% | NONE |
| Quinshon Judkins | CLE | 22 | 13 | 13 | +9 | +9 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| James Conner | ARI | 23 | 11 | 11 | +12 | +12 | 0% | NONE |
| Rico Dowdle | PIT | 24 | 39 | 39 | -15 | -15 | 0% | NONE |
| Zach Charbonnet | SEA | 25 | 43 | 43 | -18 | -18 | 0% | MANUAL_REVIEW_REQUIRED |
| J.K. Dobbins | DEN | 26 | 25 | 25 | +1 | +1 | 0% | NONE |
| Kenneth Gainwell | TB | 27 | 49 | 49 | -22 | -22 | 0% | MANUAL_REVIEW_REQUIRED |
| Alvin Kamara | NO | 28 | 24 | 24 | +4 | +4 | 0% | NONE |
| Aaron Jones | MIN | 29 | 12 | 12 | +17 | +17 | 0% | MANUAL_REVIEW_REQUIRED |
| Kenneth Walker III | KC | 30 | 23 | 23 | +7 | +7 | 0% | NONE |
| Tyrone Tracy Jr. | NYG | 31 | 28 | 28 | +3 | +3 | 0% | NONE |
| Tony Pollard | TEN | 32 | 15 | 15 | +17 | +17 | 0% | MANUAL_REVIEW_REQUIRED |
| TreVeyon Henderson | NE | 33 | 55 | 55 | -22 | -22 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Woody Marks | HOU | 34 | 27 | 27 | +7 | +7 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| RJ Harvey | DEN | 35 | 42 | 42 | -7 | -7 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Trey Benson | ARI | 36 | 68 | 68 | -32 | -32 | 0% | MANUAL_REVIEW_REQUIRED |
| Kimani Vidal | LAC | 37 | 20 | 20 | +17 | +17 | 0% | MANUAL_REVIEW_REQUIRED |
| Kyle Monangai | CHI | 38 | 41 | 41 | -3 | -3 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| David Montgomery | HOU | 39 | 38 | 38 | +1 | +1 | 0% | NONE |
| Rachaad White | WAS | 40 | 30 | 30 | +10 | +10 | 0% | NONE |
| Isiah Pacheco | DET | 41 | 35 | 35 | +6 | +6 | 0% | NONE |
| Chuba Hubbard | CAR | 42 | 9 | 9 | +33 | +33 | 0% | MANUAL_REVIEW_REQUIRED |
| Tyjae Spears | TEN | 43 | 50 | 50 | -7 | -7 | 0% | NONE |
| Michael Carter | TEN | 44 | 57 | 57 | -13 | -13 | 0% | NONE |
| Jacory Croskey-Merritt | WAS | 45 | 45 | 45 | 0 | 0 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED |
| Jordan Mason | MIN | 46 | 40 | 40 | +6 | +6 | 0% | NONE |
| Jawhar Jordan | HOU | 47 | 36 | 47 | +11 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Chris Rodriguez Jr. | JAX | 48 | 67 | 67 | -19 | -19 | 0% | MANUAL_REVIEW_REQUIRED |
| Tyler Allgeier | ARI | 49 | 60 | 60 | -11 | -11 | 0% | NONE |
| Blake Corum | LAR | 50 | 63 | 63 | -13 | -13 | 0% | NONE |
| Raheim Sanders | CLE | 51 | 62 | 51 | -11 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Devin Singletary | NYG | 52 | 33 | 33 | +19 | +19 | 0% | MANUAL_REVIEW_REQUIRED |
| Devin Neal | NO | 53 | 51 | 53 | +2 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Emanuel Wilson | SEA | 54 | 75 | 75 | -21 | -21 | 0% | MANUAL_REVIEW_REQUIRED |
| Samaje Perine | CIN | 55 | 61 | 61 | -6 | -6 | 0% | NONE |
| Jaylen Wright | MIA | 56 | 89 | 89 | -33 | -33 | 0% | MANUAL_REVIEW_REQUIRED |
| Phil Mafah | DAL | 57 | 87 | 57 | -30 | 0 | 31% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Dylan Sampson | CLE | 58 | 82 | 82 | -24 | -24 | 15% | PROSPECT_HISTORY |
| Bhayshul Tuten | JAX | 59 | 53 | 53 | +6 | +6 | 0% | PROSPECT_HISTORY |
| Ty Johnson | BUF | 60 | 69 | 69 | -9 | -9 | 0% | NONE |
| Justice Hill | BAL | 61 | 47 | 47 | +14 | +14 | 0% | NONE |
| Jaret Patterson | LAC | 62 | 74 | 62 | -12 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Kendre Miller | NO | 63 | 78 | 78 | -15 | -15 | 0% | NONE |
| Jeremy McNichols | WAS | 64 | 96 | 96 | -32 | -32 | 31% | MANUAL_REVIEW_REQUIRED |
| Braelon Allen | NYJ | 65 | 84 | 84 | -19 | -19 | 0% | MANUAL_REVIEW_REQUIRED |
| Keaton Mitchell | LAC | 66 | 108 | 108 | -42 | -42 | 15% | MANUAL_REVIEW_REQUIRED |
| Emari Demercado | KC | 67 | 58 | 58 | +9 | +9 | 0% | NONE |
| Jaydon Blue | DAL | 68 | 64 | 68 | +4 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Isaiah Davis | NYJ | 69 | 79 | 79 | -10 | -10 | 8% | NONE |
| Sean Tucker | TB | 70 | 66 | 66 | +4 | +4 | 0% | NONE |
| Brian Robinson | ATL | 71 | 52 | 52 | +19 | +19 | 0% | MANUAL_REVIEW_REQUIRED |
| Jerome Ford | WAS | 72 | 44 | 44 | +28 | +28 | 0% | MANUAL_REVIEW_REQUIRED |
| Brashard Smith | KC | 73 | 83 | 83 | -10 | -10 | 0% | PROSPECT_HISTORY |
| Malik Davis | DAL | 74 | 93 | 93 | -19 | -19 | 0% | MANUAL_REVIEW_REQUIRED |
| DJ Giddens | IND | 75 | 90 | 75 | -15 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Tank Bigsby | PHI | 76 | 80 | 80 | -4 | -4 | 0% | NONE |
| Ray Davis | BUF | 77 | 34 | 34 | +43 | +43 | 0% | MANUAL_REVIEW_REQUIRED |
| Zavier Scott | MIN | 78 | 103 | 78 | -25 | 0 | 31% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Terrell Jennings | NE | 79 | 77 | 79 | +2 | 0 | 0% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR |
| Ameer Abdullah | JAX | 80 | 54 | 54 | +26 | +26 | 0% | MANUAL_REVIEW_REQUIRED |

#### Movement Tables (RB)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Ray Davis | BUF | 77 | 34 | +43 | Weighted Opportunity: 34.11, NGS Rushes Over Expected: 32.11 |
| Chuba Hubbard | CAR | 42 | 9 | +33 | Weighted Opportunity: 125.65, NGS Rushes Over Expected: 5.09 |
| Jerome Ford | WAS | 72 | 44 | +28 | Weighted Opportunity: 75.48, NGS Rushes Over Expected: 6.06 |
| Ameer Abdullah | JAX | 80 | 54 | +26 | Weighted Opportunity: 43.64, NGS Rushes Over Expected: 8.11 |
| Devin Singletary | NYG | 52 | 33 | +19 | Weighted Opportunity: 86.88, NGS Rushes Over Expected: 5.17 |
| Brian Robinson | ATL | 71 | 52 | +19 | Weighted Opportunity: 76.39, NGS Rushes Over Expected: -0.09 |
| Derrick Henry | BAL | 20 | 2 | +18 | Weighted Opportunity: 161.73, NGS Rushes Over Expected: 26.91 |
| Aaron Jones | MIN | 29 | 12 | +17 | Weighted Opportunity: 100.90, NGS Rushes Over Expected: 6.21 |
| Tony Pollard | TEN | 32 | 15 | +17 | Weighted Opportunity: 149.93, NGS Rushes Over Expected: -2.17 |
| Kimani Vidal | LAC | 37 | 20 | +17 | Weighted Opportunity: 51.68, NGS Rushes Over Expected: -2.21 |
| Justice Hill | BAL | 61 | 47 | +14 | Weighted Opportunity: 43.97, NGS Rushes Over Expected: 4.61 |
| James Conner | ARI | 23 | 11 | +12 | Weighted Opportunity: 127.97, NGS Rushes Over Expected: 6.82 |
| Breece Hall | NYJ | 18 | 8 | +10 | Weighted Opportunity: 186.85, NGS Rushes Over Expected: 7.05 |
| Rachaad White | WAS | 40 | 30 | +10 | Weighted Opportunity: 98.96, NGS Rushes Over Expected: -2.11 |
| Quinshon Judkins | CLE | 22 | 13 | +9 | Weighted Opportunity: 162.29, NGS Rushes Over Expected: 6.61 |

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Omarion Hampton | LAC | 10 | 56 | -46 | Weighted Opportunity: 53.67, NGS Rushes Over Expected: 10.81 |
| Keaton Mitchell | LAC | 66 | 108 | -42 | Weighted Opportunity: 22.51, NGS Rushes Over Expected: -21.24 |
| Jaylen Wright | MIA | 56 | 89 | -33 | Weighted Opportunity: 45.27, NGS Rushes Over Expected: 5.78 |
| Trey Benson | ARI | 36 | 68 | -32 | Weighted Opportunity: 33.01, NGS Rushes Over Expected: 1.77 |
| Jeremy McNichols | WAS | 64 | 96 | -32 | Weighted Opportunity: 25.45, NGS Rushes Over Expected: 0.00 |
| Chase Brown | CIN | 6 | 32 | -26 | Weighted Opportunity: 152.24, NGS Rushes Over Expected: 6.32 |
| Dylan Sampson | CLE | 58 | 82 | -24 | Weighted Opportunity: 70.74, NGS Rushes Over Expected: -7.18 |
| Kenneth Gainwell | TB | 27 | 49 | -22 | Weighted Opportunity: 54.89, NGS Rushes Over Expected: -1.25 |
| TreVeyon Henderson | NE | 33 | 55 | -22 | Weighted Opportunity: 83.73, NGS Rushes Over Expected: -6.83 |
| Emanuel Wilson | SEA | 54 | 75 | -21 | Weighted Opportunity: 31.90, NGS Rushes Over Expected: 5.08 |
| Chris Rodriguez Jr. | JAX | 48 | 67 | -19 | Weighted Opportunity: 46.79, NGS Rushes Over Expected: 13.77 |
| Braelon Allen | NYJ | 65 | 84 | -19 | Weighted Opportunity: 45.47, NGS Rushes Over Expected: -3.12 |
| Malik Davis | DAL | 74 | 93 | -19 | Weighted Opportunity: 17.31, NGS Rushes Over Expected: 7.01 |
| Jaylen Warren | PIT | 19 | 37 | -18 | Weighted Opportunity: 73.77, NGS Rushes Over Expected: 6.49 |
| Zach Charbonnet | SEA | 25 | 43 | -18 | Weighted Opportunity: 93.29, NGS Rushes Over Expected: 0.97 |

---

### WR Board — Status: **Accepted**

- **Finalist Model**: `ranking_bqml_v2_adv_gng_keeper_wr_logistic_bust_advanced_v0`
- **Alternate Model**: `ranking_bqml_v2_adv_gng_keeper_wr_linear_points_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 53 | 0 | 0 | 10 | 31 | 4 | 0 | 0 | 6 | 0 | 13 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels | Alt Rank | Finalist/Alternate Disagreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Jaxon Smith-Njigba | SEA | 1 | 8 | 8 | -7 | -7 | 0% | NONE | 6 | +2 |
| Amon-Ra St. Brown | DET | 2 | 2 | 2 | 0 | 0 | 0% | NONE | 2 | 0 |
| Ja'Marr Chase | CIN | 3 | 1 | 1 | +2 | +2 | 0% | NONE | 1 | 0 |
| Puka Nacua | LAR | 4 | 4 | 4 | 0 | 0 | 0% | NONE | 3 | +1 |
| Garrett Wilson | NYJ | 5 | 10 | 10 | -5 | -5 | 0% | NONE | 22 | -12 |
| Drake London | ATL | 6 | 7 | 7 | -1 | -1 | 0% | NONE | 8 | -1 |
| Rashee Rice | KC | 7 | 36 | 36 | -29 | -29 | 0% | MANUAL_REVIEW_REQUIRED | 20 | +16 |
| Chris Olave | NO | 8 | 17 | 17 | -9 | -9 | 0% | NONE | 23 | -6 |
| A.J. Brown | NE | 9 | 5 | 5 | +4 | +4 | 0% | NONE | 5 | 0 |
| Justin Jefferson | MIN | 10 | 9 | 9 | +1 | +1 | 0% | NONE | 7 | +2 |
| George Pickens | DAL | 11 | 16 | 16 | -5 | -5 | 0% | NONE | 13 | +3 |
| Davante Adams | LAR | 12 | 12 | 12 | 0 | 0 | 0% | NONE | 26 | -14 |
| Zay Flowers | BAL | 13 | 15 | 15 | -2 | -2 | 0% | NONE | 9 | +6 |
| CeeDee Lamb | DAL | 14 | 3 | 3 | +11 | +11 | 0% | NONE | 4 | -1 |
| Nico Collins | HOU | 15 | 27 | 27 | -12 | -12 | 0% | NONE | 11 | +16 |
| Tetairoa McMillan | CAR | 16 | 38 | 38 | -22 | -22 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 37 | +1 |
| Wan'Dale Robinson | TEN | 17 | 37 | 37 | -20 | -20 | 0% | MANUAL_REVIEW_REQUIRED | 51 | -14 |
| Malik Nabers | NYG | 18 | 6 | 6 | +12 | +12 | 0% | NONE | 12 | -6 |
| Rome Odunze | CHI | 19 | 41 | 41 | -22 | -22 | 0% | MANUAL_REVIEW_REQUIRED | 52 | -11 |
| DeVonta Smith | PHI | 20 | 22 | 22 | -2 | -2 | 0% | NONE | 10 | +12 |
| Terry McLaurin | WAS | 21 | 13 | 13 | +8 | +8 | 0% | NONE | 19 | -6 |
| Jaylen Waddle | DEN | 22 | 32 | 32 | -10 | -10 | 0% | NONE | 29 | +3 |
| Tee Higgins | CIN | 23 | 11 | 11 | +12 | +12 | 0% | NONE | 18 | -7 |
| Alec Pierce | IND | 24 | 29 | 29 | -5 | -5 | 0% | NONE | 30 | -1 |
| Courtland Sutton | DEN | 25 | 20 | 20 | +5 | +5 | 0% | NONE | 15 | +5 |
| Emeka Egbuka | TB | 26 | 25 | 25 | +1 | +1 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 44 | -19 |
| Jakobi Meyers | JAX | 27 | 35 | 35 | -8 | -8 | 0% | NONE | 34 | +1 |
| Mike Evans | SF | 28 | 19 | 19 | +9 | +9 | 0% | NONE | 17 | +2 |
| Jameson Williams | DET | 29 | 49 | 49 | -20 | -20 | 0% | MANUAL_REVIEW_REQUIRED | 47 | +2 |
| Quentin Johnston | LAC | 30 | 52 | 52 | -22 | -22 | 0% | MANUAL_REVIEW_REQUIRED | 49 | +3 |
| Michael Wilson | ARI | 31 | 39 | 39 | -8 | -8 | 0% | NONE | 43 | -4 |
| Christian Watson | GB | 32 | 61 | 61 | -29 | -29 | 0% | MANUAL_REVIEW_REQUIRED | 53 | +8 |
| Jordan Addison | MIN | 33 | 31 | 31 | +2 | +2 | 0% | NONE | 31 | 0 |
| Marvin Harrison | ARI | 34 | 21 | 21 | +13 | +13 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 36 | -15 |
| DK Metcalf | PIT | 35 | 18 | 18 | +17 | +17 | 0% | MANUAL_REVIEW_REQUIRED | 25 | -7 |
| Jauan Jennings | MIN | 36 | 56 | 56 | -20 | -20 | 0% | MANUAL_REVIEW_REQUIRED | 60 | -4 |
| Ladd McConkey | LAC | 37 | 26 | 26 | +11 | +11 | 0% | NONE | 16 | +10 |
| Romeo Doubs | NE | 38 | 47 | 47 | -9 | -9 | 0% | NONE | 42 | +5 |
| Tre Tucker | LV | 39 | 53 | 53 | -14 | -14 | 0% | NONE | 65 | -12 |
| Parker Washington | JAX | 40 | 54 | 54 | -14 | -14 | 0% | NONE | 45 | +9 |
| Ricky Pearsall | SF | 41 | 73 | 73 | -32 | -32 | 0% | MANUAL_REVIEW_REQUIRED | 62 | +11 |
| Jerry Jeudy | CLE | 42 | 30 | 30 | +12 | +12 | 0% | NONE | 46 | -16 |
| Troy Franklin | DEN | 43 | 74 | 74 | -31 | -31 | 0% | MANUAL_REVIEW_REQUIRED | 80 | -6 |
| Elic Ayomanor | TEN | 44 | 55 | 55 | -11 | -11 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 97 | -42 |
| Darius Slayton | NYG | 45 | 45 | 45 | 0 | 0 | 0% | NONE | 50 | -5 |
| Calvin Ridley | TEN | 46 | 24 | 24 | +22 | +22 | 0% | MANUAL_REVIEW_REQUIRED | 38 | -14 |
| Darnell Mooney | NYG | 47 | 46 | 46 | +1 | +1 | 0% | NONE | 59 | -13 |
| Khalil Shakir | BUF | 48 | 51 | 51 | -3 | -3 | 0% | NONE | 33 | +18 |
| Keon Coleman | BUF | 49 | 62 | 62 | -13 | -13 | 0% | NONE | 68 | -6 |
| Brian Thomas Jr. | JAX | 50 | 40 | 40 | +10 | +10 | 0% | NONE | 48 | -8 |
| Travis Hunter | JAX | 51 | 72 | 51 | -21 | 0 | 5% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR, MANUAL_REVIEW_REQUIRED | 61 | +11 |
| Mack Hollins | NE | 52 | 67 | 67 | -15 | -15 | 0% | NONE | 75 | -8 |
| Xavier Worthy | KC | 53 | 44 | 44 | +9 | +9 | 0% | NONE | 39 | +5 |
| Jakobie Keeney-James | GB | 54 | 42 | 54 | +12 | 0 | 30% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR, MANUAL_REVIEW_REQUIRED | 27 | +15 |
| Michael Pittman | PIT | 55 | 14 | 14 | +41 | +41 | 0% | MANUAL_REVIEW_REQUIRED | 21 | -7 |
| Kayshon Boutte | NE | 56 | 64 | 64 | -8 | -8 | 0% | NONE | 63 | +1 |
| Jalen Coker | CAR | 57 | 48 | 48 | +9 | +9 | 0% | NONE | 32 | +16 |
| Jayden Reed | GB | 58 | 63 | 63 | -5 | -5 | 0% | NONE | 55 | +8 |
| Josh Downs | IND | 59 | 43 | 43 | +16 | +16 | 0% | MANUAL_REVIEW_REQUIRED | 40 | +3 |
| Rashid Shaheed | SEA | 60 | 58 | 58 | +2 | +2 | 0% | NONE | 54 | +4 |
| Cooper Kupp | SEA | 61 | 50 | 50 | +11 | +11 | 0% | NONE | 41 | +9 |
| Chris Godwin Jr. | TB | 62 | 34 | 34 | +28 | +28 | 0% | MANUAL_REVIEW_REQUIRED | 35 | -1 |
| Devaughn Vele | NO | 63 | 83 | 83 | -20 | -20 | 0% | MANUAL_REVIEW_REQUIRED | 77 | +6 |
| Jalen McMillan | TB | 64 | 60 | 60 | +4 | +4 | 0% | NONE | 56 | +4 |
| Marquise Brown | PHI | 65 | 59 | 59 | +6 | +6 | 0% | NONE | 64 | -5 |
| Van Jefferson | WAS | 66 | 99 | 66 | -33 | 0 | 0% | MODEL_DISAGREEMENT_LOCK, CURRENT_PIGSKIN_ANCHOR | 121 | -22 |
| Xavier Legette | CAR | 67 | 79 | 79 | -12 | -12 | 0% | NONE | 81 | -2 |
| Jayden Higgins | HOU | 68 | 68 | 68 | 0 | 0 | 0% | PROSPECT_HISTORY, MANUAL_REVIEW_REQUIRED | 67 | +1 |
| Adonai Mitchell | NYJ | 69 | 96 | 69 | -27 | 0 | 5% | MODEL_DISAGREEMENT_LOCK, CURRENT_PIGSKIN_ANCHOR | 126 | -30 |
| DJ Moore | BUF | 70 | 23 | 23 | +47 | +47 | 0% | MANUAL_REVIEW_REQUIRED | 24 | -1 |
| Andrei Iosivas | CIN | 71 | 82 | 71 | -11 | 0 | 0% | MODEL_DISAGREEMENT_LOCK, CURRENT_PIGSKIN_ANCHOR | 105 | -23 |
| Tyquan Thornton | KC | 72 | 110 | 110 | -38 | -38 | 0% | MANUAL_REVIEW_REQUIRED | 108 | +2 |
| Theo Wease Jr. | MIA | 73 | 100 | 73 | -27 | 0 | 5% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 70 | +30 |
| Olamide Zaccheaus | ATL | 74 | 114 | 114 | -40 | -40 | 0% | MANUAL_REVIEW_REQUIRED | 113 | +1 |
| Chimere Dike | TEN | 75 | 69 | 69 | +6 | +6 | 0% | PROSPECT_HISTORY | 79 | -10 |
| Malik Washington | MIA | 76 | 93 | 76 | -17 | 0 | 0% | MODEL_DISAGREEMENT_LOCK, CURRENT_PIGSKIN_ANCHOR | 118 | -25 |
| Ryan Flournoy | DAL | 77 | 109 | 109 | -32 | -32 | 0% | MANUAL_REVIEW_REQUIRED | 122 | -13 |
| Kendrick Bourne | ARI | 78 | 78 | 78 | 0 | 0 | 0% | NONE | 71 | +7 |
| Calvin Austin III | NYG | 79 | 91 | 91 | -12 | -12 | 0% | NONE | 91 | 0 |
| Pat Bryant | DEN | 80 | 119 | 119 | -39 | -39 | 0% | PROSPECT_HISTORY | 116 | +3 |
| Dontayvion Wicks | PHI | 81 | 71 | 71 | +10 | +10 | 0% | NONE | 73 | -2 |
| Xavier Hutchinson | HOU | 82 | 121 | 121 | -39 | -39 | 0% | MANUAL_REVIEW_REQUIRED | 117 | +4 |
| Rashod Bateman | BAL | 83 | 65 | 65 | +18 | +18 | 0% | MANUAL_REVIEW_REQUIRED | 66 | -1 |
| Matthew Golden | GB | 84 | 77 | 77 | +7 | +7 | 5% | PROSPECT_HISTORY | 78 | -1 |
| Jalen Nailor | LV | 85 | 90 | 90 | -5 | -5 | 0% | NONE | 92 | -2 |
| Tory Horton | SEA | 86 | 86 | 86 | 0 | 0 | 15% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 82 | +4 |
| Tez Johnson | TB | 87 | 81 | 81 | +6 | +6 | 5% | PROSPECT_HISTORY | 85 | -4 |
| DeMario Douglas | NE | 88 | 76 | 76 | +12 | +12 | 0% | NONE | 74 | +2 |
| Christian Kirk | SF | 89 | 57 | 57 | +32 | +32 | 0% | MANUAL_REVIEW_REQUIRED | 58 | -1 |
| Luther Burden III | CHI | 90 | 70 | 70 | +20 | +20 | 0% | PROSPECT_HISTORY | 57 | +13 |
| Isaiah Bond | CLE | 91 | 111 | 111 | -20 | -20 | 0% | PROSPECT_HISTORY | 123 | -12 |
| Treylon Burks | WAS | 92 | 117 | 117 | -25 | -25 | 0% | MANUAL_REVIEW_REQUIRED | 124 | -7 |
| Tre Harris | LAC | 93 | 95 | 95 | -2 | -2 | 5% | PROSPECT_HISTORY | 96 | -1 |
| Isaac TeSlaa | DET | 94 | 87 | 87 | +7 | +7 | 0% | PROSPECT_HISTORY | 87 | 0 |
| Marquez Valdes-Scantling | DAL | 95 | 98 | 98 | -3 | -3 | 0% | NONE | 93 | +5 |
| Casey Washington | ATL | 96 | 160 | 96 | -64 | 0 | 10% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 163 | -3 |
| Jalen Tolbert | MIA | 97 | 102 | 102 | -5 | -5 | 0% | NONE | 107 | -5 |
| Cedric Tillman | CLE | 98 | 89 | 89 | +9 | +9 | 0% | NONE | 100 | -11 |
| Devontez Walker | BAL | 99 | 139 | 99 | -40 | 0 | 15% | LOW_HISTORY, CURRENT_PIGSKIN_ANCHOR | 141 | -2 |
| John Metchie III | CAR | 100 | 116 | 116 | -16 | -16 | 0% | MANUAL_REVIEW_REQUIRED | 99 | +17 |

#### Movement Tables (WR)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| DJ Moore | BUF | 70 | 23 | +47 | WOPR: 0.50, Target Share: 0.22 |
| Michael Pittman | PIT | 55 | 14 | +41 | WOPR: 0.55, Target Share: 0.25 |
| Christian Kirk | SF | 89 | 57 | +32 | WOPR: 0.43, Target Share: 0.18 |
| Chris Godwin Jr. | TB | 62 | 34 | +28 | WOPR: 0.47, Target Share: 0.21 |
| Calvin Ridley | TEN | 46 | 24 | +22 | WOPR: 0.55, Target Share: 0.21 |
| Luther Burden III | CHI | 90 | 70 | +20 | WOPR: 0.30, Target Share: 0.14 |
| Rashod Bateman | BAL | 83 | 65 | +18 | WOPR: 0.36, Target Share: 0.13 |
| DK Metcalf | PIT | 35 | 18 | +17 | WOPR: 0.55, Target Share: 0.21 |
| Josh Downs | IND | 59 | 43 | +16 | WOPR: 0.42, Target Share: 0.20 |
| Marvin Harrison | ARI | 34 | 21 | +13 | WOPR: 0.56, Target Share: 0.20 |
| Malik Nabers | NYG | 18 | 6 | +12 | WOPR: 0.80, Target Share: 0.32 |
| Tee Higgins | CIN | 23 | 11 | +12 | WOPR: 0.54, Target Share: 0.20 |
| Jerry Jeudy | CLE | 42 | 30 | +12 | WOPR: 0.54, Target Share: 0.21 |
| DeMario Douglas | NE | 88 | 76 | +12 | WOPR: 0.30, Target Share: 0.14 |
| CeeDee Lamb | DAL | 14 | 3 | +11 | WOPR: 0.66, Target Share: 0.28 |

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|
| Olamide Zaccheaus | ATL | 74 | 114 | -40 | WOPR: 0.17, Target Share: 0.08 |
| Pat Bryant | DEN | 80 | 119 | -39 | WOPR: 0.18, Target Share: 0.08 |
| Xavier Hutchinson | HOU | 82 | 121 | -39 | WOPR: 0.23, Target Share: 0.10 |
| Tyquan Thornton | KC | 72 | 110 | -38 | WOPR: 0.25, Target Share: 0.08 |
| Ricky Pearsall | SF | 41 | 73 | -32 | WOPR: 0.33, Target Share: 0.13 |
| Ryan Flournoy | DAL | 77 | 109 | -32 | WOPR: 0.16, Target Share: 0.07 |
| Troy Franklin | DEN | 43 | 74 | -31 | WOPR: 0.37, Target Share: 0.14 |
| Rashee Rice | KC | 7 | 36 | -29 | WOPR: 0.47, Target Share: 0.24 |
| Christian Watson | GB | 32 | 61 | -29 | WOPR: 0.39, Target Share: 0.15 |
| Treylon Burks | WAS | 92 | 117 | -25 | WOPR: 0.26, Target Share: 0.10 |
| Tetairoa McMillan | CAR | 16 | 38 | -22 | WOPR: 0.57, Target Share: 0.22 |
| Rome Odunze | CHI | 19 | 41 | -22 | WOPR: 0.49, Target Share: 0.19 |
| Quentin Johnston | LAC | 30 | 52 | -22 | WOPR: 0.43, Target Share: 0.18 |
| Wan'Dale Robinson | TEN | 17 | 37 | -20 | WOPR: 0.50, Target Share: 0.24 |
| Jameson Williams | DET | 29 | 49 | -20 | WOPR: 0.40, Target Share: 0.13 |

---

### TE Board — Status: **Held behind Current Pigskin**

- **Finalist Model**: `ranking_bqml_v2_adv_gng_keeper_te_logistic_bust_advanced_v0`

#### Guardrail Summary

| Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Locked | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

| Player | Team | Current Pigskin Rank | Raw Finalist Rank | Guarded Review Rank | Delta Before | Delta After | Missingness | Applied Guardrail Labels |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Trey McBride | ARI | 1 | 1 | 1 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Brock Bowers | LV | 2 | 2 | 2 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Tucker Kraft | GB | 3 | 27 | 3 | -24 | 0 | 0% | HELD_BOARD_ANCHOR |
| George Kittle | SF | 4 | 5 | 4 | -1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Kyle Pitts | ATL | 5 | 7 | 5 | -2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Tyler Warren | IND | 6 | 4 | 6 | +2 | 0 | 0% | HELD_BOARD_ANCHOR |
| Sam LaPorta | DET | 7 | 8 | 7 | -1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dallas Goedert | PHI | 8 | 15 | 8 | -7 | 0 | 0% | HELD_BOARD_ANCHOR |
| Travis Kelce | KC | 9 | 3 | 9 | +6 | 0 | 0% | HELD_BOARD_ANCHOR |
| Hunter Henry | NE | 10 | 10 | 10 | 0 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dalton Schultz | HOU | 11 | 16 | 11 | -5 | 0 | 0% | HELD_BOARD_ANCHOR |
| Juwan Johnson | NO | 12 | 13 | 12 | -1 | 0 | 0% | HELD_BOARD_ANCHOR |
| Colston Loveland | CHI | 13 | 6 | 13 | +7 | 0 | 0% | HELD_BOARD_ANCHOR |
| Jake Ferguson | DAL | 14 | 11 | 14 | +3 | 0 | 0% | HELD_BOARD_ANCHOR |
| Brenton Strange | JAX | 15 | 33 | 15 | -18 | 0 | 0% | HELD_BOARD_ANCHOR |
| Harold Fannin Jr. | CLE | 16 | 9 | 16 | +7 | 0 | 0% | HELD_BOARD_ANCHOR |
| Cade Otton | TB | 17 | 21 | 17 | -4 | 0 | 0% | HELD_BOARD_ANCHOR |
| Theo Johnson | NYG | 18 | 23 | 18 | -5 | 0 | 0% | HELD_BOARD_ANCHOR |
| Mason Taylor | NYJ | 19 | 22 | 19 | -3 | 0 | 0% | HELD_BOARD_ANCHOR |
| Oronde Gadsden II | LAC | 20 | 28 | 20 | -8 | 0 | 0% | HELD_BOARD_ANCHOR |
| AJ Barner | SEA | 21 | 30 | 21 | -9 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dalton Kincaid | BUF | 22 | 18 | 22 | +4 | 0 | 0% | HELD_BOARD_ANCHOR |
| Mark Andrews | BAL | 23 | 17 | 23 | +6 | 0 | 0% | HELD_BOARD_ANCHOR |
| T.J. Hockenson | MIN | 24 | 12 | 24 | +12 | 0 | 0% | HELD_BOARD_ANCHOR |
| Drake Dabney | GB | 25 | 32 | 25 | -7 | 0 | 25% | HELD_BOARD_ANCHOR |
| Jake Tonges | SF | 26 | 46 | 26 | -20 | 0 | 0% | HELD_BOARD_ANCHOR |
| Albert Okwuegbunam | LV | 27 | 79 | 27 | -52 | 0 | 5% | HELD_BOARD_ANCHOR |
| Greg Dulcich | MIA | 28 | 56 | 28 | -28 | 0 | 0% | HELD_BOARD_ANCHOR |
| David Njoku | LAC | 29 | 14 | 29 | +15 | 0 | 0% | HELD_BOARD_ANCHOR |
| Colby Parkinson | LAR | 30 | 38 | 30 | -8 | 0 | 0% | HELD_BOARD_ANCHOR |
| Darnell Washington | PIT | 31 | 51 | 31 | -20 | 0 | 0% | HELD_BOARD_ANCHOR |
| Pat Freiermuth | PIT | 32 | 24 | 32 | +8 | 0 | 0% | HELD_BOARD_ANCHOR |
| Dawson Knox | BUF | 33 | 39 | 33 | -6 | 0 | 0% | HELD_BOARD_ANCHOR |
| Cole Kmet | CHI | 34 | 19 | 34 | +15 | 0 | 0% | HELD_BOARD_ANCHOR |
| Evan Engram | DEN | 35 | 29 | 35 | +6 | 0 | 0% | HELD_BOARD_ANCHOR |

#### Movement Tables (TE)

##### Top 15 Risers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|

##### Top 15 Fallers (After Guardrails)

| Player | Team | Pigskin Rank | Guarded Rank | Delta | Key Explanation |
|---|---|---|---|---|---|

---## Phase 33.28 Refined RB Top-100 Rebuild Note

Phase 33.28 keeps the Phase 33.26C calibrated weighted hybrid position-pull sequence and swaps only the RB queue to the Phase 33.27 `anchored_blend_tripwire` review queue. This fixes Jahmyr Gibbs inside RB3 and top 7 overall across all profiles, but the result remains review-only because Current Pigskin and market tripwires still require owner judgment.

Stable constraints:

- Do not write this prototype to `analytics_pigskin_rankings`.
- Do not activate formula champions from this phase.
- Keep Half PPR TE, PPR TE, GNG Keeper QB, and GNG Keeper TE held behind Current Pigskin.
- Treat Jeremiyah Love as a market-only prospect tripwire until the player appears in a source-backed active ranking or approved prospect lane.
- Treat Half PPR Breece Hall as a current-state drift warning because live Current Pigskin now lists him RB6 while the Phase 33.27 evidence used an older RB18 context.
- Route metrics remain blocked/null.

## Phase 33.29 Refined Top-100 Owner Review Decision

Final decision: `REFINED TOP-100 READY FOR OWNER REVIEW WITH TRIPWIRES`.

Phase 33.29 accepts the Phase 33.28 refined top-100 prototype for owner review only. It does not approve live ranking writes, champion activation, production exposure, or deployment.

Owner-review findings:

- Gibbs is fixed at RB3 and inside the top 24 overall in every scoring profile.
- Achane and Chase Brown are not buried outside RB24.
- Omarion Hampton and Cam Skattebo remain manual-review prospect-history cases.
- Jeremiyah Love remains a market-only tripwire and needs a prospect lane or explicit owner rejection before live use.
- Half PPR Breece Hall is stale Current Pigskin context: Phase 33.27 evidence used RB18, while the current active table now lists RB6.
- Patrick Mahomes is an interleaver warning. The prototype pushes elite QBs too low for live use without backtest support.
- Rashee Rice is a WR position-board warning. The guarded WR queue disagrees sharply with Current Pigskin.

Next required gate: bounded historical backtest before any live top-100 decision.

## Phase 33.30 Bounded Backtest And Tripwire Cleanup Decision

Final decision: `REFINED TOP-100 NEEDS TARGETED QB/WR CLEANUP`.

Phase 33.30 ran a bounded proxy backtest against `ranking_backtest_feature_mart` using target seasons 2024 and 2025, target week 18, all four scoring profiles, and no 2026 outcomes. The exact 2026 owner-review queues do not exist historically, so the test used source-window feature proxies and the Phase 33.26C position-pull sequence.

Decision summary:

- The refined RB queue remains useful for owner review and fixes 2026 Gibbs sanity.
- The refined top-100 does not cleanly beat the Current Pigskin proxy on points/VOR capture.
- QB tripwires, especially Patrick Mahomes, point to an interleaver anchor/cap problem.
- WR tripwires, especially Rashee Rice, point to a WR position-board or elite-anchor problem.
- Jeremiyah Love requires a prospect lane or explicit owner rejection of market-only prospect influence.
- Half PPR Breece Hall requires stale-context refresh before live approval.
- Current Pigskin holds for live use.

Next gate: targeted QB/WR tripwire cleanup before another owner-review top-100 pass.

## Phase 33.33 RB STD GPT 5.5 v1.0 Board Status

No owner-review board was generated. The formula hit a required metric stop before scoring: RB receiving YAC above expectation has no source-backed rows in the required 2020-2024 history. Current Pigskin remains the Standard RB board. `RB STD GPT 5.5 v1.0` must not appear as a challenger until the missing lane is built or the formula is explicitly revised by the owner.

## Phase 33.35 RB v1.0A Board Decision

The rushing-only and EPA revisions were generated for dry-run review only. Neither is approved for the owner-review challenger set. Current Pigskin wins the corrected full-season comparison. Keep both candidate boards out of live and owner-selection surfaces until stale workload and availability penalties are redesigned.
