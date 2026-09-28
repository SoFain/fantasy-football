# Validation Report — Phase 33.26C Weighting Calibration

## 1. Final Decision

`TOP-100 PROTOTYPE WEIGHTS CALIBRATED`

---

## 2. current 33.26B problems & Diagnosis

- **Overcorrection**: In Phase 33.26B, hard Look-Ahead constraints forced RBs and TEs too early, resulting in Trey McBride at 3 and Brock Bowers at 5 in standard, which was unrealistic.
- **Component Score Contribution**: In early rounds, raw VOR mismatch favored WR, while look-ahead min-gates overcompensated for RBs/TEs. Transitioning to soft penalties and draft-band movement caps resolves the abrupt position pockets.

---

## 3. Best Setup Selected

- **Replacement Baseline**: Option 2 (QB12/RB30/WR42/TE12)
- **Queue Selection Strategy**: prototype_v3_balanced (Guarded Hybrid with Min-Max VOR, Scarcity, Anchor, and Soft Penalties/Movement Caps)

---

## 4. Key Review Summaries (2026 Calibrated Weight Hybrid)

### Profile: STANDARD

- **Positional Mix in Top 12**: QB: 1, RB: 5, WR: 4, TE: 2
- **Positional Mix in Top 24**: QB: 3, RB: 8, WR: 10, TE: 3
- **Positional Mix in Top 50**: QB: 5, RB: 20, WR: 18, TE: 7
- **Positional Mix in Top 100**: QB: 13, RB: 38, WR: 35, TE: 14

#### Top 10 Risers vs Current Pigskin:
- Brandon Aiyuk (WR): Current Pigskin 172 -> Prototype 91 (+81)
- Dameon Pierce (RB): Current Pigskin 96 -> Prototype 40 (+56)
- Derrick Henry (RB): Current Pigskin 20 -> Prototype 6 (+14)
- Chuba Hubbard (RB): Current Pigskin 42 -> Prototype 31 (+11)
- Saquon Barkley (RB): Current Pigskin 9 -> Prototype 2 (+7)
- Tee Higgins (WR): Current Pigskin 24 -> Prototype 20 (+4)
- CeeDee Lamb (WR): Current Pigskin 14 -> Prototype 10 (+4)
- Breece Hall (RB): Current Pigskin 18 -> Prototype 15 (+3)
- Ja'Marr Chase (WR): Current Pigskin 4 -> Prototype 1 (+3)
- Malik Nabers (WR): Current Pigskin 18 -> Prototype 16 (+2)

#### Top 10 Fallers vs Current Pigskin:
- Rashee Rice (WR): Current Pigskin 7 -> Prototype 96 (-89)
- Brock Purdy (QB): Current Pigskin 4 -> Prototype 78 (-74)
- Trevor Lawrence (QB): Current Pigskin 6 -> Prototype 79 (-73)
- Caleb Williams (QB): Current Pigskin 9 -> Prototype 82 (-73)
- Jaylen Waddle (WR): Current Pigskin 22 -> Prototype 95 (-73)
- Hunter Henry (TE): Current Pigskin 10 -> Prototype 81 (-71)
- Alec Pierce (WR): Current Pigskin 23 -> Prototype 94 (-71)
- Kyler Murray (QB): Current Pigskin 18 -> Prototype 88 (-70)
- Chris Olave (WR): Current Pigskin 8 -> Prototype 75 (-67)
- Dak Prescott (QB): Current Pigskin 13 -> Prototype 80 (-67)

---

### Profile: HALF_PPR

- **Positional Mix in Top 12**: QB: 1, RB: 5, WR: 5, TE: 1
- **Positional Mix in Top 24**: QB: 1, RB: 7, WR: 12, TE: 4
- **Positional Mix in Top 50**: QB: 5, RB: 16, WR: 21, TE: 8
- **Positional Mix in Top 100**: QB: 13, RB: 34, WR: 38, TE: 15

#### Top 10 Risers vs Current Pigskin:
- Tank Dell (WR): Current Pigskin 204 -> Prototype 97 (+107)
- Brandon Aiyuk (WR): Current Pigskin 172 -> Prototype 89 (+83)
- Dameon Pierce (RB): Current Pigskin 96 -> Prototype 40 (+56)
- Michael Pittman (WR): Current Pigskin 52 -> Prototype 35 (+17)
- Derrick Henry (RB): Current Pigskin 20 -> Prototype 5 (+15)
- Malik Nabers (WR): Current Pigskin 18 -> Prototype 11 (+7)
- CeeDee Lamb (WR): Current Pigskin 14 -> Prototype 8 (+6)
- Saquon Barkley (RB): Current Pigskin 8 -> Prototype 2 (+6)
- Tee Higgins (WR): Current Pigskin 24 -> Prototype 21 (+3)
- Chuba Hubbard (RB): Current Pigskin 43 -> Prototype 41 (+2)

#### Top 10 Fallers vs Current Pigskin:
- Rashee Rice (WR): Current Pigskin 7 -> Prototype 92 (-85)
- Tetairoa McMillan (WR): Current Pigskin 17 -> Prototype 100 (-83)
- Wan'Dale Robinson (WR): Current Pigskin 16 -> Prototype 96 (-80)
- Brock Purdy (QB): Current Pigskin 4 -> Prototype 77 (-73)
- Trevor Lawrence (QB): Current Pigskin 6 -> Prototype 79 (-73)
- Caleb Williams (QB): Current Pigskin 9 -> Prototype 81 (-72)
- Jakobi Meyers (WR): Current Pigskin 27 -> Prototype 99 (-72)
- Chase Brown (RB): Current Pigskin 6 -> Prototype 76 (-70)
- Alec Pierce (WR): Current Pigskin 23 -> Prototype 93 (-70)
- Jaylen Warren (RB): Current Pigskin 19 -> Prototype 88 (-69)

---

### Profile: PPR

- **Positional Mix in Top 12**: QB: 0, RB: 4, WR: 7, TE: 1
- **Positional Mix in Top 24**: QB: 1, RB: 7, WR: 12, TE: 4
- **Positional Mix in Top 50**: QB: 5, RB: 16, WR: 21, TE: 8
- **Positional Mix in Top 100**: QB: 13, RB: 33, WR: 40, TE: 14

#### Top 10 Risers vs Current Pigskin:
- Tank Dell (WR): Current Pigskin 204 -> Prototype 97 (+107)
- Brandon Aiyuk (WR): Current Pigskin 172 -> Prototype 88 (+84)
- Michael Pittman (WR): Current Pigskin 51 -> Prototype 42 (+9)
- Chuba Hubbard (RB): Current Pigskin 43 -> Prototype 34 (+9)
- Malik Nabers (WR): Current Pigskin 18 -> Prototype 11 (+7)
- CeeDee Lamb (WR): Current Pigskin 13 -> Prototype 7 (+6)
- Saquon Barkley (RB): Current Pigskin 8 -> Prototype 3 (+5)
- Derrick Henry (RB): Current Pigskin 20 -> Prototype 17 (+3)
- Tee Higgins (WR): Current Pigskin 23 -> Prototype 21 (+2)
- Tony Pollard (RB): Current Pigskin 32 -> Prototype 31 (+1)

#### Top 10 Fallers vs Current Pigskin:
- Rashee Rice (WR): Current Pigskin 7 -> Prototype 89 (-82)
- Tetairoa McMillan (WR): Current Pigskin 17 -> Prototype 99 (-82)
- Wan'Dale Robinson (WR): Current Pigskin 16 -> Prototype 91 (-75)
- Brock Purdy (QB): Current Pigskin 4 -> Prototype 75 (-71)
- Trevor Lawrence (QB): Current Pigskin 6 -> Prototype 77 (-71)
- Caleb Williams (QB): Current Pigskin 9 -> Prototype 78 (-69)
- Alec Pierce (WR): Current Pigskin 25 -> Prototype 94 (-69)
- Jaylen Warren (RB): Current Pigskin 19 -> Prototype 87 (-68)
- Jaylen Waddle (WR): Current Pigskin 22 -> Prototype 90 (-68)
- Jakobi Meyers (WR): Current Pigskin 27 -> Prototype 95 (-68)

---

### Profile: GNG_KEEPER

- **Positional Mix in Top 12**: QB: 1, RB: 5, WR: 5, TE: 1
- **Positional Mix in Top 24**: QB: 3, RB: 8, WR: 10, TE: 3
- **Positional Mix in Top 50**: QB: 8, RB: 15, WR: 19, TE: 8
- **Positional Mix in Top 100**: QB: 15, RB: 33, WR: 38, TE: 14

#### Top 10 Risers vs Current Pigskin:
- Tank Dell (WR): Current Pigskin 203 -> Prototype 95 (+108)
- Brandon Aiyuk (WR): Current Pigskin 171 -> Prototype 90 (+81)
- Dameon Pierce (RB): Current Pigskin 96 -> Prototype 40 (+56)
- Michael Pittman (WR): Current Pigskin 55 -> Prototype 39 (+16)
- Derrick Henry (RB): Current Pigskin 20 -> Prototype 5 (+15)
- Saquon Barkley (RB): Current Pigskin 8 -> Prototype 2 (+6)
- Chuba Hubbard (RB): Current Pigskin 42 -> Prototype 37 (+5)
- CeeDee Lamb (WR): Current Pigskin 14 -> Prototype 9 (+5)
- Ja'Marr Chase (WR): Current Pigskin 3 -> Prototype 1 (+2)
- Breece Hall (RB): Current Pigskin 18 -> Prototype 18 (+0)

#### Top 10 Fallers vs Current Pigskin:
- Rashee Rice (WR): Current Pigskin 7 -> Prototype 98 (-91)
- Tetairoa McMillan (WR): Current Pigskin 16 -> Prototype 100 (-84)
- Wan'Dale Robinson (WR): Current Pigskin 17 -> Prototype 99 (-82)
- Chase Brown (RB): Current Pigskin 6 -> Prototype 82 (-76)
- Nico Collins (WR): Current Pigskin 15 -> Prototype 88 (-73)
- Jaylen Waddle (WR): Current Pigskin 22 -> Prototype 94 (-72)
- Jakobi Meyers (WR): Current Pigskin 27 -> Prototype 97 (-70)
- Jake Ferguson (TE): Current Pigskin 14 -> Prototype 83 (-69)
- Alec Pierce (WR): Current Pigskin 24 -> Prototype 91 (-67)
- Cam Skattebo (RB): Current Pigskin 15 -> Prototype 81 (-66)

---

## 5. Safety Confirmations

- **No model training occurred**: Confirmed.
- **No active overall rankings written to database**: Confirmed.
- **No champions activated**: Confirmed.
- **Route metrics status**: Strictly mapped to `NULL` (Blocked).
- **No fabrication of NGS/advanced metrics occurred**: Confirmed.

---

## 6. Recommended Next Phase

- **Phase 33.27 — Owner review of weighted calibrated top-100 prototype**
