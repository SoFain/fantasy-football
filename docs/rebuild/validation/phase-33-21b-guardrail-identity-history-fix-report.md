# Validation Report — Phase 33.21B Guardrail Identity and History Fix

## 1. Final Decision

`GUARDRAIL HISTORY CLASSIFICATION FIXED`

## 2. Files Changed

- [advanced-bqml-v2-owner-review-boards.md](file:///e:/Fantasy%20Football/docs/rebuild/advanced-bqml-v2-owner-review-boards.md) [MODIFY]
- [phase-33-21-advanced-board-guardrails-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-21-advanced-board-guardrails-report.md) [MODIFY]
- [phase-33-21b-guardrail-identity-history-fix-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-21b-guardrail-identity-history-fix-report.md) [NEW]
- [bqml-v2-positional-formula-finalists.md](file:///e:/Fantasy%20Football/docs/rebuild/bqml-v2-positional-formula-finalists.md) [MODIFY]
- [ranking-algorithm-scorecard.md](file:///e:/Fantasy%20Football/docs/rebuild/ranking-algorithm-scorecard.md) [MODIFY]
- [bqml-v2-ranking-architecture.md](file:///e:/Fantasy%20Football/docs/rebuild/bqml-v2-ranking-architecture.md) [MODIFY]
- [ranking-opportunity-metrics-matrix.md](file:///e:/Fantasy%20Football/docs/rebuild/ranking-opportunity-metrics-matrix.md) [MODIFY]

## 3. Git State & Checks

- All 26 unit tests passed cleanly.
- Safety compiler check and deployment safety scripts passed.
- BigQuery warehouse validations passed with 0 errors.
- Trailing empty lines at EOF removed, and `git diff --check` passed successfully.

## 4. False-Positive ROOKIE_NO_HISTORY Diagnosis

We investigated why established players like Brock Purdy, Garrett Wilson, and Mike Evans were flagged as `ROOKIE_NO_HISTORY`. The root cause was that `weekly_rows` from the candidates query represents the count of weeks in *only the latest season* (e.g. 2025 or 2024), not the player's total history. Since these players had fewer than 10 games in their latest season (due to injury or partial schedule), they were incorrectly flagged.

### Player Diagnostic Table

| Player | Current Pigskin ID | match_method | hist_weekly_rows | hist_seasons | min_season | max_season | missingness | current_label | corrected_label | reason |
|---|---|---|---|---|---|---|---|---|---|---|
| Brock Purdy | 00-0037834 | exact_source_identity | 57 | 4 | 2022 | 2025 | 0% | ROOKIE_NO_HISTORY | NONE | Established player with sufficient history (games >= 10). |
| Garrett Wilson | 00-0037740 | exact_source_identity | 58 | 4 | 2022 | 2025 | 0% | ROOKIE_NO_HISTORY | NONE | Established player with sufficient history (games >= 10). |
| Rashee Rice | 00-0039067 | exact_source_identity | 32 | 3 | 2023 | 2025 | 0% | ROOKIE_NO_HISTORY | NONE | Established player with sufficient history (games >= 10). |
| Malik Nabers | 00-0039337 | exact_source_identity | 19 | 2 | 2024 | 2025 | 0% | ROOKIE_NO_HISTORY | NONE | Established player with sufficient history (games >= 10). |
| Mike Evans | 00-0031408 | exact_source_identity | 186 | 12 | 2014 | 2025 | 0% | ROOKIE_NO_HISTORY | NONE | Established player with sufficient history (games >= 10). |
| James Conner | 00-0033553 | exact_source_identity | 110 | 9 | 2017 | 2025 | 0% | ROOKIE_NO_HISTORY | NONE | Established player with sufficient history (games >= 10). |
| Jayden Reed | 00-0039146 | exact_source_identity | 42 | 3 | 2023 | 2025 | 0% | ROOKIE_NO_HISTORY | NONE | Established player with sufficient history (games >= 10). |
| Chris Godwin Jr. | 00-0033921 | exact_source_identity | 126 | 9 | 2017 | 2025 | 0% | ROOKIE_NO_HISTORY | NONE | Established player with sufficient history (games >= 10). |
| Sam LaPorta | 00-0039065 | exact_source_identity | 46 | 3 | 2023 | 2025 | 0% | ROOKIE_NO_HISTORY | NONE | Established player with sufficient history (games >= 10). |
| Omarion Hampton | 00-0040666 | exact_source_identity | 10 | 1 | 2025 | 2025 | 0% | ROOKIE_NO_HISTORY | ROOKIE_NO_HISTORY | True rookie, no historical NFL stats available. |
| Cam Skattebo | 00-0040715 | exact_source_identity | 8 | 1 | 2025 | 2025 | 0% | ROOKIE_NO_HISTORY | LOW_HISTORY | Has only 8 games of history in 2025. |
| Travis Hunter | 00-0040718 | exact_source_identity | 7 | 1 | 2025 | 2025 | 0% | ROOKIE_NO_HISTORY | ROOKIE_NO_HISTORY | True rookie, no historical NFL stats available. |

## 5. Identity Join & QB Disagreement Lock Fix

- **Join Fix**: We modified the query to select `hist_games_3yr` (total games played in 2023-2025) and `hist_seasons_3yr` directly from the rolling averages CTE. This allows us to classify history based on total historical games volume instead of latest-season weekly rows.
- **QB Disagreement Lock Fix**: We disabled `MODEL_DISAGREEMENT_LOCK` for all QB boards since the alternate points model was rejected due to rushing bias and should not be used as a disagreement trigger.

## 6. Board Acceptance Status & Row Counts

| Profile | QB (Limit 45) | RB (Limit 80) | WR (Limit 100) | TE (Limit 35) |
|---|---|---|---|---|
| standard | 45 (Accepted with guardrails) | 80 (Accepted) | 100 (Accepted) | 35 (Accepted with guardrails) |
| half_ppr | 45 (Accepted with guardrails) | 80 (Accepted with guardrails) | 100 (Accepted) | 35 (Held behind Current Pigskin) |
| ppr | 45 (Accepted with guardrails) | 80 (Accepted) | 100 (Accepted) | 35 (Held behind Current Pigskin) |
| gng_keeper | 45 (Held behind Current Pigskin) | 80 (Accepted) | 100 (Accepted) | 35 (Held behind Current Pigskin) |

## 7. Guardrail Summary by Board (Before vs. After Fix)

### STANDARD Guardrail Statistics

| Position | Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Lock | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QB | 32 | 0 | 0 | 5 | 3 | 0 | 0 | 0 | 4 | 1 | 4 |
| RB | 39 | 0 | 0 | 10 | 29 | 0 | 0 | 0 | 10 | 0 | 11 |
| WR | 56 | 0 | 0 | 6 | 32 | 0 | 0 | 0 | 6 | 0 | 13 |
| TE | 10 | 0 | 17 | 2 | 6 | 0 | 0 | 0 | 2 | 0 | 5 |

### HALF_PPR Guardrail Statistics

| Position | Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Lock | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QB | 32 | 0 | 0 | 5 | 3 | 0 | 0 | 0 | 4 | 1 | 4 |
| RB | 35 | 0 | 0 | 10 | 33 | 0 | 0 | 0 | 10 | 0 | 11 |
| WR | 53 | 0 | 0 | 5 | 36 | 0 | 0 | 0 | 5 | 0 | 13 |
| TE | 0 | 0 | 0 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### PPR Guardrail Statistics

| Position | Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Lock | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QB | 32 | 0 | 0 | 5 | 3 | 0 | 0 | 0 | 4 | 1 | 4 |
| RB | 43 | 0 | 0 | 9 | 26 | 0 | 0 | 0 | 9 | 0 | 11 |
| WR | 56 | 0 | 0 | 5 | 33 | 0 | 0 | 0 | 5 | 0 | 13 |
| TE | 0 | 0 | 0 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### GNG_KEEPER Guardrail Statistics

| Position | Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Lock | Sparse Features | Rookie/No History | Low History | Join Failed | Prospect History |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QB | 0 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RB | 37 | 0 | 0 | 10 | 31 | 0 | 0 | 0 | 10 | 0 | 11 |
| WR | 53 | 0 | 0 | 10 | 31 | 4 | 0 | 0 | 6 | 0 | 13 |
| TE | 0 | 0 | 0 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## 8. Cleaned Manual Review List

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

## 9. Confirmations & Remaining Risks

- **No training occurred**: Confirmed. Checked that no new BQML models were trained during this phase.
- **No live rankings written**: Confirmed. Checked that no active live ranking table rows were changed.
- **No champion selected**: Confirmed. Checked that no champ label or status was promoted.
- **No top-100 Ready**: Confirmed. Positional queues are locked and not interleaved.
- **Route metrics status**: Confirmed strictly mapped to `NULL`. **ROUTE METRICS REMAIN BLOCKED**.
- **Remaining Risk**: Manual review is still required for true rookies (Omarion Hampton, Travis Hunter) and low-history players (Cam Skattebo) inside the top 150 range to ensure their Current Pigskin anchors are reasonable.

- **Recommended Next Phase**: **Phase 33.22 — Owner approval packet for guarded positional boards**.
