# WR Fable v1 — Results at a Glance

WR Fable v1 predicts next-season Standard WR PPG from prior-season data: 52% opportunity (WOPR, non-garbage-time targets, red-zone targets), 28% shrunk efficiency (YPRR, EPA/target, YAC/reception, aDOT-adjusted catch rate), 10% TD blend (red-zone-based expected TDs — end-zone data doesn't exist, so this is the owner-approved fallback), 10% age and availability (breakout bonus 22-25, decline after 29, games rate).

## Backtest (2022→23, 2023→24, 2024→25)

| Metric | Average | Design target |
|---|---:|---|
| Spearman rank correlation | **0.738** | 0.60-0.68 ceiling — beaten |
| Top-12 precision | 0.639 | — |
| Points captured in top 12 | 0.917 | — |
| Pairwise draft win rate | 0.769 | — |
| Predicted top-12 busts | 2 in 36 picks | — |
| Elite misses (top-12 finishers ranked 25+) | 8 | all role-change cases |

The thesis held: WR is more predictable than RB. Every headline number beats the RB Fable equivalents on a deeper pool.

The two busts were Keenan Allen 2024 (team change at 31) and Michael Pittman 2024 (QB collapse). The misses (Nico Collins '23, Godwin/Higgins '24, Olave/Watson '25...) are all breakout or role-shift players — the same known blindness as RB Fable: the formula only sees last season's role.

## Current Top 15 (2025 metrics) vs Standard board

1. Amon-Ra St. Brown (Std 3) · 2. Jaxon Smith-Njigba (1) · 3. Puka Nacua (2) · 4. Rashee Rice (8, Questionable) · 5. Ja'Marr Chase (4) · 6. **Davante Adams (13)** · 7. Drake London (5) · 8. Chris Olave (6) · 9. George Pickens (11) · 10. Nico Collins (15) · 11. CeeDee Lamb (14) · 12. Zay Flowers (12) · 13. Justin Jefferson (9) · 14. Garrett Wilson (10) · 15. **A.J. Brown (7 — now on NE, scored on PHI data)**

## Talking points

- **Davante Adams at 6 is the Derrick Henry of this board**: massive red-zone role (2.3 RZ targets/gm, best TD blend in the pool) versus an age-32 discount the formula applies but doesn't let bury him.
- **DK Metcalf +15 (Fable 19 vs Std 34)** is the biggest disagreement — WOPR and air yards love him in Standard scoring.
- **Possession receivers get correctly punished**: Jakobi Meyers -10, Jordan Addison -9 — catches without depth don't score in Standard.
- **Watch-outs**: A.J. Brown's rank is stale (team change), Malik Nabers (Std 18) can't be ranked (injury-shortened 2025), and Diggs/Deebo/Keenan Allen appear only on the Fable list — verify their roster situations manually.

## Status

Research-only. No live board changed; Current Standard WR still holds. Recommendation: **WR FABLE V1 READY FOR OWNER APPROVAL**, with explicit owner rulings needed on A.J. Brown, the Nabers gap, and the three Fable-only veterans.
