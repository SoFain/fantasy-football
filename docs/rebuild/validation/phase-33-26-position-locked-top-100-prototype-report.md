# Validation Report — Phase 33.26B Position-Locked Top-100 Calibration

## 1. Final Decision

`TOP-100 PROTOTYPE CALIBRATED FOR POSITION MIX`

---

## 2. WR-Overpull Diagnosis

- **Scale Mismatch**: WR model family uses `logistic_elite` (probability 0-100%, max score ~52.2), while RB model family uses `linear_points` but scales to a standardized z-score/points ratio (max score ~15.3). This created a 5x scale difference in raw scores.
- **Replacement Baseline Impact**: Retaining a deep WR baseline (WR55) pushed the WR replacement score very low (15.4), inflating WR VOR to 36.8, whereas RB VOR was capped at 6.95. This caused the interleaver to draft 12-22 WRs sequentially in the top 24.
- **Calibration Fix**: Implemented Min-Max within-position scaling combined with look-ahead anti-monopoly constraints and elite-RB protection guardrails. Option 2 baseline (QB12/RB30/WR42/TE12) successfully controls WR VOR inflation.

---

## 3. Best Setup Selected

- **Replacement Baseline**: Option 2 (QB12/RB30/WR42/TE12)
- **Queue Selection Strategy**: prototype_v2_mix_guarded_hybrid (Guarded Hybrid with Min-Max VOR, Scarcity, Anchor, and Look-Ahead Sanity Gates)

---

## 4. Key Review Summaries (2026 Calibrated Hybrid)

### Profile: STANDARD

- **Positional Mix in Top 12**: QB: 1, RB: 6, WR: 3, TE: 2
- **Positional Mix in Top 24**: QB: 3, RB: 8, WR: 10, TE: 3
- **Positional Mix in Top 50**: QB: 8, RB: 19, WR: 15, TE: 8
- **Positional Mix in Top 100**: QB: 13, RB: 36, WR: 24, TE: 27

#### Top 10 Risers vs Current Pigskin:
- Dameon Pierce (RB): Current Pigskin 96 -> Prototype 40 (+56)
- Derrick Henry (RB): Current Pigskin 20 -> Prototype 8 (+12)
- Saquon Barkley (RB): Current Pigskin 9 -> Prototype 2 (+7)
- Chuba Hubbard (RB): Current Pigskin 42 -> Prototype 36 (+6)
- Ja'Marr Chase (WR): Current Pigskin 4 -> Prototype 1 (+3)
- Breece Hall (RB): Current Pigskin 18 -> Prototype 16 (+2)
- Tee Higgins (WR): Current Pigskin 24 -> Prototype 23 (+1)
- Malik Nabers (WR): Current Pigskin 18 -> Prototype 17 (+1)
- Ashton Jeanty (RB): Current Pigskin 12 -> Prototype 12 (+0)
- CeeDee Lamb (WR): Current Pigskin 14 -> Prototype 15 (+-1)

#### Top 10 Fallers vs Current Pigskin:
- Tucker Kraft (TE): Current Pigskin 3 -> Prototype 90 (-87)
- Dalton Schultz (TE): Current Pigskin 11 -> Prototype 93 (-82)
- Kyler Murray (QB): Current Pigskin 18 -> Prototype 100 (-82)
- Theo Johnson (TE): Current Pigskin 18 -> Prototype 97 (-79)
- Jake Ferguson (TE): Current Pigskin 15 -> Prototype 92 (-77)
- Cade Otton (TE): Current Pigskin 17 -> Prototype 94 (-77)
- Dallas Goedert (TE): Current Pigskin 8 -> Prototype 84 (-76)
- Hunter Henry (TE): Current Pigskin 10 -> Prototype 86 (-76)
- Oronde Gadsden II (TE): Current Pigskin 20 -> Prototype 96 (-76)
- Juwan Johnson (TE): Current Pigskin 12 -> Prototype 85 (-73)

---

### Profile: HALF_PPR

- **Positional Mix in Top 12**: QB: 1, RB: 7, WR: 2, TE: 2
- **Positional Mix in Top 24**: QB: 2, RB: 7, WR: 11, TE: 4
- **Positional Mix in Top 50**: QB: 8, RB: 18, WR: 14, TE: 10
- **Positional Mix in Top 100**: QB: 20, RB: 32, WR: 22, TE: 26

#### Top 10 Risers vs Current Pigskin:
- Dameon Pierce (RB): Current Pigskin 96 -> Prototype 36 (+60)
- Derrick Henry (RB): Current Pigskin 20 -> Prototype 7 (+13)
- Saquon Barkley (RB): Current Pigskin 8 -> Prototype 2 (+6)
- Chuba Hubbard (RB): Current Pigskin 43 -> Prototype 40 (+3)
- Tee Higgins (WR): Current Pigskin 24 -> Prototype 22 (+2)
- Ja'Marr Chase (WR): Current Pigskin 3 -> Prototype 1 (+2)
- Malik Nabers (WR): Current Pigskin 18 -> Prototype 17 (+1)
- CeeDee Lamb (WR): Current Pigskin 14 -> Prototype 15 (+-1)
- Ashton Jeanty (RB): Current Pigskin 11 -> Prototype 12 (+-1)
- Amon-Ra St. Brown (WR): Current Pigskin 4 -> Prototype 5 (+-1)

#### Top 10 Fallers vs Current Pigskin:
- Daniel Jones (QB): Current Pigskin 7 -> Prototype 94 (-87)
- Jordan Love (QB): Current Pigskin 15 -> Prototype 100 (-85)
- Justin Herbert (QB): Current Pigskin 11 -> Prototype 95 (-84)
- Jared Goff (QB): Current Pigskin 17 -> Prototype 98 (-81)
- Chris Olave (WR): Current Pigskin 8 -> Prototype 86 (-78)
- Chase Brown (RB): Current Pigskin 6 -> Prototype 83 (-77)
- Nico Collins (WR): Current Pigskin 15 -> Prototype 90 (-75)
- Kyler Murray (QB): Current Pigskin 18 -> Prototype 93 (-75)
- Joe Burrow (QB): Current Pigskin 24 -> Prototype 99 (-75)
- Baker Mayfield (QB): Current Pigskin 23 -> Prototype 97 (-74)

---

### Profile: PPR

- **Positional Mix in Top 12**: QB: 1, RB: 7, WR: 2, TE: 2
- **Positional Mix in Top 24**: QB: 2, RB: 9, WR: 9, TE: 4
- **Positional Mix in Top 50**: QB: 6, RB: 22, WR: 12, TE: 10
- **Positional Mix in Top 100**: QB: 13, RB: 38, WR: 22, TE: 27

#### Top 10 Risers vs Current Pigskin:
- Derrick Henry (RB): Current Pigskin 20 -> Prototype 11 (+9)
- Saquon Barkley (RB): Current Pigskin 8 -> Prototype 3 (+5)
- Chuba Hubbard (RB): Current Pigskin 43 -> Prototype 40 (+3)
- Ashton Jeanty (RB): Current Pigskin 11 -> Prototype 8 (+3)
- Ja'Marr Chase (WR): Current Pigskin 3 -> Prototype 1 (+2)
- Jonathan Taylor (RB): Current Pigskin 5 -> Prototype 4 (+1)
- Breece Hall (RB): Current Pigskin 18 -> Prototype 18 (+0)
- Bijan Robinson (RB): Current Pigskin 2 -> Prototype 2 (+0)
- Tee Higgins (WR): Current Pigskin 23 -> Prototype 24 (+-1)
- CeeDee Lamb (WR): Current Pigskin 13 -> Prototype 15 (+-2)

#### Top 10 Fallers vs Current Pigskin:
- Kyler Murray (QB): Current Pigskin 18 -> Prototype 100 (-82)
- Chris Olave (WR): Current Pigskin 8 -> Prototype 86 (-78)
- George Pickens (WR): Current Pigskin 10 -> Prototype 84 (-74)
- Nico Collins (WR): Current Pigskin 15 -> Prototype 89 (-74)
- Albert Okwuegbunam (TE): Current Pigskin 25 -> Prototype 97 (-72)
- Jake Tonges (TE): Current Pigskin 26 -> Prototype 98 (-72)
- Greg Dulcich (TE): Current Pigskin 27 -> Prototype 99 (-72)
- Zay Flowers (WR): Current Pigskin 12 -> Prototype 83 (-71)
- DeVonta Smith (WR): Current Pigskin 20 -> Prototype 88 (-68)
- Courtland Sutton (WR): Current Pigskin 24 -> Prototype 91 (-67)

---

### Profile: GNG_KEEPER

- **Positional Mix in Top 12**: QB: 1, RB: 7, WR: 2, TE: 2
- **Positional Mix in Top 24**: QB: 2, RB: 8, WR: 10, TE: 4
- **Positional Mix in Top 50**: QB: 8, RB: 19, WR: 13, TE: 10
- **Positional Mix in Top 100**: QB: 31, RB: 32, WR: 13, TE: 24

#### Top 10 Risers vs Current Pigskin:
- Dameon Pierce (RB): Current Pigskin 96 -> Prototype 40 (+56)
- Derrick Henry (RB): Current Pigskin 20 -> Prototype 7 (+13)
- Chuba Hubbard (RB): Current Pigskin 42 -> Prototype 36 (+6)
- Saquon Barkley (RB): Current Pigskin 8 -> Prototype 2 (+6)
- Ja'Marr Chase (WR): Current Pigskin 3 -> Prototype 1 (+2)
- Malik Nabers (WR): Current Pigskin 18 -> Prototype 19 (+-1)
- CeeDee Lamb (WR): Current Pigskin 14 -> Prototype 15 (+-1)
- Ashton Jeanty (RB): Current Pigskin 11 -> Prototype 12 (+-1)
- Amon-Ra St. Brown (WR): Current Pigskin 2 -> Prototype 3 (+-1)
- Kyren Williams (RB): Current Pigskin 9 -> Prototype 11 (+-2)

#### Top 10 Fallers vs Current Pigskin:
- Chase Brown (RB): Current Pigskin 6 -> Prototype 87 (-81)
- Cam Skattebo (RB): Current Pigskin 15 -> Prototype 86 (-71)
- Kyler Murray (QB): Current Pigskin 19 -> Prototype 88 (-69)
- C.J. Stroud (QB): Current Pigskin 20 -> Prototype 89 (-69)
- Bryce Young (QB): Current Pigskin 21 -> Prototype 90 (-69)
- Tyler Shough (QB): Current Pigskin 22 -> Prototype 91 (-69)
- Baker Mayfield (QB): Current Pigskin 23 -> Prototype 92 (-69)
- Joe Burrow (QB): Current Pigskin 24 -> Prototype 93 (-69)
- Malik Willis (QB): Current Pigskin 25 -> Prototype 94 (-69)
- Jacoby Brissett (QB): Current Pigskin 26 -> Prototype 95 (-69)

---

## 5. Safety Confirmations

- **No model training occurred**: Confirmed.
- **No active overall rankings written to database**: Confirmed.
- **No champions activated**: Confirmed.
- **Route metrics status**: Strictly mapped to `NULL` (Blocked).
- **No fabrication of NGS/advanced metrics occurred**: Confirmed.

---

## 6. Recommended Next Phase

- **Phase 33.27 — Owner review of calibrated top-100 prototype**
