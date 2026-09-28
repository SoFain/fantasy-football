# TE Fable v1.0a Ranking Formula: Standard Scoring

**Goal:** Predict next-season Standard fantasy PPG from prior-season data, using `te_situational.db` (2022–2025, about 130 TEs per season) plus point-in-time NFLverse stats. Backtest folds: 2022 to 2023, 2023 to 2024, and an untouched 2024 to 2025 holdout.

**Available fields (verified in the DB):** `Routes Run, Receptions, Rec. Yards, Target Share, Touchdowns, YAC, ADoT, Catch %, Total EPA, Targets/Route Run (TPRR), YPRR` — each under 8 splits: `standard, red_zone, non_garbage_time, when_leading, when_trailing, late_down, vs_man, vs_zone`.

---

## Core Principle

TE is the most **role-gated** position in fantasy. Three facts drive the weights:

1. **Routes are the gateway.** A TE who blocks on 60% of snaps cannot score regardless of talent. Route volume is the single biggest separator between fantasy-relevant and irrelevant TEs, and it's the leading indicator of a breakout — routes almost always spike *before* production does.
2. **TPRR is the premier TE talent metric.** Targets per route run measures target *earning*, is highly stable year over year, and predicts future target share growth. For TEs specifically it outperforms raw target share as a forward-looking signal, because so many TEs are one route-share bump away from a different tier.
3. **Standard-scoring TE value is TD-driven — which makes TDs the biggest trap.** Outside the top 3–4, TEs are separated almost entirely by touchdowns, and TE TD rates regress violently. The formula must score *expected* TDs from red-zone usage, not actual ones, or it will chase last year's TD-luck outliers every single fold.

The database also permits a useful hypothesis test: production against man coverage may carry player-specific separation signal. Treat `vs_man` YPRR as an ablation candidate, not as an established sticky metric, until the forward folds support it.

---

## Derived Fields Needed

The DB has no raw targets, games, air yards, or end-zone targets. Derive:

```
Targets            = Routes Run × TPRR                [any split]
RZ Targets         = red_zone.Routes Run × red_zone.TPRR
Approx Air Yards   = ADoT × Targets                   [if needed]
Games Played       = pull from point-in-time NFLverse data [required for per-game rates]
Age                = calculate from birth date at the prediction boundary
```

If the point-in-time games join is unavailable, do not silently mix route-normalized and per-game results. Run a separately labeled route-normalized variant or block the primary formula until games are available.

---

## Preprocessing

1. Compute rate metrics **per game** (or per route, see fallback above).
2. Primary-board qualification threshold: **4+ games and 100+ routes** in the input season. Players below either threshold may appear only in a separately labeled short-sample review lane and must not affect primary-board z-scores.
3. **Z-score each metric across the qualified TE pool within each season.**
4. Compute age, games, team, and every predictor as known at the prediction boundary. Current roster state must not overwrite historical state.

---

## The Formula

```
TE_SCORE =
  # OPPORTUNITY — 50%
  0.22 × z(routes run/gm)                      [standard split — route volume]
  0.16 × z(target share)                       [standard split]
  0.12 × z(RZ targets/gm)                      [red_zone: Routes × TPRR]

  # EFFICIENCY / TALENT — 30% (each shrunk, see below)
  0.12 × z(TPRR)                               [standard split — target earning]
  0.08 × z(YPRR)                               [standard split]
  0.05 × z(vs_man YPRR)                        [vs_man split — separation talent]
  0.05 × z(EPA per target)                     [Total EPA / derived Targets]

  # SCORING — 10%
  0.10 × z(blended TD/gm) where
         blended TD = 0.7 × xTD + 0.3 × actual TD
         xTD/gm = fold-specific RZ conversion coefficient × RZ targets/gm
         The coefficient must be fitted only on the training seasons for
         each fold, or frozen before holdout evaluation. Never fit it using
         the target season. Use 0.14 only as the initial predeclared value.

  # AGE & AVAILABILITY — 10%
  0.04 × z(breakout-window bonus)              [+1 if boundary age 24–27, 0 otherwise]
  0.03 × z(−max(0, age − 30))                  [flat through 30, linear penalty after]
  0.03 × z(games played / 17)                  [NFLverse]
```

### Shrinkage on the efficiency block

Multiply each efficiency z-score by:

```
shrink = n / (n + 70)
```

where `n` = targets for TPRR/EPA-per-target, routes for YPRR, and **vs_man routes** for the man-coverage term. The vs_man split has small samples for most TEs. A 40-route vs_man sample keeps about 36% of its signal. This controls variance but does not prove predictive value, so the primary report must include results with and without this term.

---

## Weight Summary

| Block | Metric | Weight | Source |
|---|---|---|---|
| Opportunity | Routes run/gm | 0.22 | `standard` |
| Opportunity | Target share | 0.16 | `standard` |
| Opportunity | RZ targets/gm | 0.12 | `red_zone` (Routes × TPRR) |
| Efficiency | TPRR | 0.12 | `standard` |
| Efficiency | YPRR | 0.08 | `standard` |
| Efficiency | vs_man YPRR | 0.05 | `vs_man` |
| Efficiency | EPA per target | 0.05 | `standard` (derived) |
| Scoring | Blended TD/gm (0.7 xTD / 0.3 actual) | 0.10 | `red_zone` + totals |
| Age | Breakout-window bonus (24–27) | 0.04 | NFLverse |
| Age | Decline penalty (after 30) | 0.03 | NFLverse |
| Availability | Games played / 17 | 0.03 | NFLverse |

---

## Rationale for Each Piece

**Routes run/gm (0.22)** — The role gate. This is route volume, not route participation or route share. Do not describe it as participation unless a source-backed team dropback denominator is added.

**Target share (0.16)** — Still the bread-and-butter volume signal, and stickier at TE than WR because TE target trees change less with personnel churn.

**RZ targets/gm (0.12)** — The expected-TD engine, and proportionally more important at TE than WR: TEs get a larger share of their fantasy value from TDs in standard scoring, and RZ targets are the stable input behind them.

**TPRR (0.12)** — The marquee TE talent metric and the top slot in the efficiency block. It identifies TEs who will *grow into* volume — exactly the players a next-season model must catch before the market does.

**YPRR (0.08)** — Complements TPRR by folding in depth (ADoT) and YAC. A TE can post a strong TPRR on 4-yard dumpoffs; YPRR sorts those out.

**vs_man YPRR (0.05)** — A testable individual-skill hypothesis. Keep the term only if forward-fold and untouched-holdout evidence improves enough to justify its small-sample risk. Always report the no-man-split ablation.

**EPA per target (0.05)** — Situational value (conversions, leverage) that yardage misses. The `late_down` split could substitute here if EPA proves noisy — late-down targets proxy QB trust.

**TD blend (0.7 expected / 0.3 actual)** — The single biggest edge at this position. Every season produces a TE who scores 8+ TDs on thin RZ usage and gets drafted a round too early the next year; this term systematically fades him and promotes the TE with heavy RZ work and 3 scores.

**Age structure** — The proposed bonus window is ages 24–27 and the decline penalty starts at 30. Historical age must be calculated at each prediction boundary. Current age is prohibited in historical folds.

---

## Standard-Scoring Adjustments Baked In

- **No reception term.** Catch volume only counts via yardage — YPRR and target share carry it.
- **RZ usage weighted proportionally higher than the WR model** (0.12 + the whole scoring block keyed off it), because TD share of total fantasy value is highest at TE.
- **Catch % deliberately excluded as a raw input** — it mostly measures ADoT. If you want it, use the residual after regressing on ADoT, as in the WR model; at TE the marginal value is small.

---

## Backtesting Protocol

**Metrics:**
- Spearman rank correlation: `TE_SCORE(year N)` vs `standard PPG(year N+1)`.
- Pairwise win rate and NDCG.
- Captured Standard fantasy points.
- Top-6 and top-12 precision.
- Bust rate and TE6, TE12, and TE18 cutline crossings.
- Report primary qualifiers separately from short-sample review players.

**Folds:** 2022 to 2023 and 2023 to 2024 are development evidence. The 2024 to 2025 fold is the untouched final holdout.

**Realistic ceiling:** Spearman ~0.55–0.65 overall, but expect it to look better at the top (the elite tier is very stable) and worse in the TE8–TE20 mush, where outcomes are TD-coinflips even after luck correction.

**Tuning:** First run the fixed v1.0a weights and focused ablations, including removal of `vs_man` YPRR. Any block-weight tuning must use only the first two folds. Do not select weights from the 2024 to 2025 holdout, and do not tune all 11 individual weights on three folds.

**Required benchmarks:** Compare v1.0a against the live Current Pigskin TE ordering, prior-year Standard PPG or a simple projection baseline, and the existing Standard TE BQML finalists. No formula earns promotion from standalone metrics.

**Output boundary:** Owner-review output is capped at TE35. Formula testing does not authorize a live ranking write, champion activation, Gemini adjustment, or deployment.

---

## Upgrades Worth Testing

1. **Two-season blend** (~70/30) — helps injury-shortened years, and TE roles are stable enough that the older season carries real signal.
2. **Route-share trend term:** routes/gm in the season's second half minus first half (needs weekly NFLverse data). Late-season route growth is the classic TE breakout tell.
3. **`when_trailing` TPRR** as a QB-trust proxy — TEs who get fed in comeback mode have safer target floors.
4. **Team TE-target concentration:** a strong TE2 on the same roster (committee) caps the ceiling; flag rosters where two TEs both clear 15 routes/gm.

---

## Known Limitations

- **Returning players only** — rookies and players without the required prior-season sample need a separately labeled review path. Do not infer their ranking from this formula.
- **Team changes and current injuries** — keep these out of historical predictors unless point-in-time sources exist. They may be shown as current owner-review context after the deterministic score is calculated.
- **No games-played field in the DB** — the per-game normalization depends on the NFLverse join. Verify that join early; it's the most likely silent data bug in the pipeline.
