# QB Ranking Formula — Standard Scoring Fantasy Football

**Goal:** Predict next-season standard-scoring fantasy PPG from prior-season data. No QB situational DB was provided, so this maps to **NFLverse** fields (play-by-play gives everything needed: dropbacks, EPA, CPOE, sacks, rushing, red-zone plays). If you have a `qb_situational.db` with splits like the other positions, the doc notes where each split would slot in.

**Assumed scoring:** 0.04/pass yd, **4 pt pass TD**, −2 INT, 0.1/rush yd, 6 pt rush TD. (A 6-pt-pass-TD adjustment is given at the end — it materially changes the weights.)

---

## Core Principle

QB is different from every other position in two ways that drive this formula:

1. **Rushing is the cheat code.** A rushing yard is worth 2.5× a passing yard, and a rushing TD is worth 1.5× a passing TD in 4-pt leagues. QB rush volume is also one of the stickiest stats in fantasy — designed QB runs are a coaching commitment, not a weekly accident. The difference between a top-5 QB and a QB12 is almost always legs, not arm.
2. **QB is the one position where efficiency IS the skill.** For RBs and WRs, per-touch efficiency regresses hard. For QBs, EPA/dropback and CPOE are genuinely stable, because the QB touches the ball on every play — samples are huge and the QB *causes* most of his own efficiency. So the efficiency block gets its largest weight of any position here.

And the usual rule still applies: **TD rate lies.** Passing TD rate regresses toward ~4.5% of attempts every year. A QB who threw 38 TDs on a 7% rate is a fade; one who threw 22 on 3.5% with healthy volume is a buy.

---

## Preprocessing

1. Compute everything **per game** (NFLverse has games directly).
2. Qualification: **6+ starts or 200+ dropbacks** in the input season.
3. **Z-score across the qualified QB pool within each season** (~32–38 QBs/yr — thin pool, so expect noisier z-scores than the other positions).

---

## The Formula

```
QB_SCORE =
  # OPPORTUNITY / ROLE — 40%
  0.20 × z(rush attempts/gm)                   [designed runs + scrambles;
                                                exclude kneels — NFLverse qb_kneel flag]
  0.12 × z(dropbacks/gm, non-garbage-time)     [win prob 5–95% filter in pbp]
  0.08 × z(RZ + goal-to-go rush attempts/gm)   [yardline_100 <= 20 in pbp]

  # EFFICIENCY / TALENT — 35% (shrunk, see below)
  0.13 × z(EPA per dropback)                   [includes sacks & INTs in the denominator —
                                                this term already prices turnovers]
  0.09 × z(CPOE)                               [completion % over expected]
  0.07 × z(−sack rate)                         [sacks / dropbacks, inverted —
                                                sack avoidance is a sticky QB skill]
  0.06 × z(rush yards per attempt)             [kneels excluded]

  # SCORING — 15%
  0.10 × z(blended pass TD/gm) where
         blended = 0.7 × xPassTD + 0.3 × actual
         xPassTD/gm ≈ 0.045 × attempts/gm + 0.09 × RZ pass attempts/gm
  0.05 × z(blended rush TD/gm) where
         blended = 0.7 × xRushTD + 0.3 × actual
         xRushTD/gm ≈ 0.20 × goal-to-go rush attempts/gm

  # AGE & AVAILABILITY — 10%
  0.04 × z(games started / 17)
  0.03 × z(dual-threat age penalty)            [−max(0, age − 28) × rush_share,
                                                where rush_share = rushing fantasy pts /
                                                total fantasy pts — legs age first]
  0.03 × z(−max(0, age − 33))                  [general late-career cliff]
```

### Shrinkage

- **Passing efficiency terms** (EPA/dropback, CPOE, sack rate): multiply z by `n / (n + 200)` where n = dropbacks. QB passing metrics stabilize fast, so a full-season starter (~600 dropbacks) keeps 75% of signal.
- **Rushing efficiency** (rush yds/att): `n / (n + 40)` where n = rush attempts.

No INT term appears explicitly — **EPA/dropback already prices interceptions**, and residual INT rate beyond that is nearly pure noise year over year. Adding a separate INT input double-counts the signal and imports the luck.

---

## Weight Summary

| Block | Metric | Weight | NFLverse source |
|---|---|---|---|
| Opportunity | Rush attempts/gm | 0.20 | pbp rusher plays, kneels excluded |
| Opportunity | Non-garbage dropbacks/gm | 0.12 | pbp, WP 5–95% |
| Opportunity | RZ/goal-to-go rush att/gm | 0.08 | pbp yardline filter |
| Efficiency | EPA per dropback | 0.13 | pbp `qb_epa` |
| Efficiency | CPOE | 0.09 | pbp `cpoe` |
| Efficiency | Sack rate (inverted) | 0.07 | pbp |
| Efficiency | Rush yards/attempt | 0.06 | pbp |
| Scoring | Blended pass TD/gm | 0.10 | derived |
| Scoring | Blended rush TD/gm | 0.05 | derived |
| Availability | Games started / 17 | 0.04 | rosters/schedules |
| Age | Dual-threat penalty (28+, scaled by rush share) | 0.03 | rosters |
| Age | General penalty (33+) | 0.03 | rosters |

---

## Rationale for Each Piece

**Rush attempts/gm (0.20)** — The largest single weight in any of your four positional models, and it's earned. Rushing volume converts to fantasy points at a much higher rate than passing volume, and it's a *scheme commitment* that persists across seasons. This single term does more to separate the QB1 tier than everything else combined.

**Non-garbage dropbacks (0.12)** — Volume still matters, but note it's barely half the rushing weight despite passing being most of a QB's raw production. That's because pass attempts are heavily game-script-driven and *negatively* correlated with team quality — bad teams throw more. The garbage-time filter removes the worst of it.

**RZ/goal-to-go rushes (0.08)** — Goal-line QB sneaks and designed runs are 6-point plays with extreme stickiness (it's a play-calling identity). This is the cheapest expected-TD signal in football.

**EPA/dropback (0.13)** — The best single QB quality metric, and unlike other positions, it's stable enough to trust at this weight. It also quietly handles turnovers and sacks, keeping the formula compact.

**CPOE (0.09)** — Accuracy over expectation is the most QB-isolated skill metric available (mostly strips out receivers and scheme). The EPA+CPOE pair is the standard composite in QB stability research; both terms together outperform either alone.

**Sack rate inverted (0.07)** — Sack avoidance belongs mostly to the QB, not the line, and it's sticky. It protects passing volume (drives sustain) and in leagues with sack penalties it's direct points.

**TD blends** — Pass TD rate regresses to ~4.5% relentlessly; the 0.7/0.3 blend anchored on attempts and RZ pass volume fades the TD-luck seasons that wreck naive QB rankings. Rush xTD keys on goal-to-go carries, which are far more stable than the TDs themselves.

**Dual-threat age penalty** — Rushing production is the first thing to decay, typically from age 28–29, and it decays fastest for the QBs who depend on it most. Scaling the penalty by rushing's share of the QB's fantasy value targets it correctly: a pocket passer at 30 is fine; a legs-dependent QB at 30 is a known landmine.

---

## If You Have a `qb_situational.db`

Slot the splits in as follows: `non_garbage_time` → the dropback term; `red_zone` → both xTD inputs; `when_trailing` dropbacks → optional volume-floor bonus (QBs on bad teams keep passing volume); `late_down` EPA → optional substitute for part of the EPA term (third-down performance is QB-driven); pressure or `vs_blitz` splits, if present, would slot next to sack rate.

---

## Backtesting Protocol

**Metrics:**
- Spearman: `QB_SCORE(N)` vs standard PPG(N+1), QBs with 6+ starts both years.
- **Top-5 and top-12 precision.** Fantasy QB is about hitting the elite tier; QB13–QB24 accuracy barely matters in 1-QB leagues.

**Folds:** 2022→23, 2023→24, 2024→25.

**Realistic ceiling:** Spearman ~0.60–0.70 among *returning starters* — the highest of your four positions, because QB efficiency is real and roles don't split. But the qualifier is doing heavy lifting: benchings, rookie takeovers, and injuries remove more of the QB pool year-over-year than any other position, and none of that is in the inputs.

**Tuning:** Grid-search the four block weights in 5% steps. With only ~30 qualified QBs per fold, this is your most overfit-prone model — resist touching individual weights entirely.

---

## 6-pt Pass TD Adjustment

If the league awards 6 per passing TD, passing value rises ~20% relative to rushing. Shift:

- Rush attempts/gm: 0.20 → **0.16**
- Non-garbage dropbacks: 0.12 → **0.14**
- Blended pass TD: 0.10 → **0.13**
- RZ rush attempts: 0.08 → **0.07**

Everything else holds. The rushing edge shrinks but never disappears — legs still win.

---

## Known Limitations

- **Returning starters only.** Rookie QBs and new starters are a bigger share of the QB pool than any other position's equivalent problem — in a typical year, 8–12 of 32 Week 1 starters weren't full-time starters the prior season. This formula simply cannot see them.
- **Team context churn:** a new offensive coordinator changes designed-rush volume (the model's biggest input) more than any player-level stat predicts. A manual OC-change flag is worth more here than at any other position.
- **Thin pool:** ~30 qualified QBs means every z-score is noisy and one outlier season can visibly bend a fold. Read the backtest at the tier level, not the individual-rank level.
