# Player Situation Layer

Status 2026-07-24: **Phases 1 and 2 live.** Phase 3 (rank adjustments) awaits owner policy informed by the BQML study below.

The layer exists because rankings and articles were blind to context their metrics don't carry: D.J. Moore ranked WR50 on 2025 Chicago numbers while being Buffalo's WR1 under Josh Allen — and the generated article never mentioned any of it. 57 of 264 standard-board players carried a team change their metrics didn't know about.

Doctrine (mirrors the runbook's injury contract): **facts → flags → owner-gated bounded adjustments.** Nothing in this layer moves a ranking.

## Pieces

| Piece | Location |
| --- | --- |
| Table | `analytics_player_situation` — migrations 0046/0047/0048. One table, two slices: 2016–2025 transitions with outcomes (ML training set), and the 2026 slice (live context). |
| Builder | [src/situation_layer.py](../../src/situation_layer.py), job `build-situation-layer` |
| Public dataset | `datasets.player_situation` in the feed manifest — [src/situation_feed.py](../../src/situation_feed.py), job `situation-feed` |
| Board blocks | Schema **1.3**: every board player may carry `situation` + `metrics` objects (publisher `fetch_player_context`, main checkout) |
| Coaching baseline | `coaching_staff_history` (2025 head coaches from Wikipedia season pages) — [scripts/populate_coaching_staff_2025_csv.py](../../scripts/populate_coaching_staff_2025_csv.py), loaded via `ingest-coaching-staff --history-season 2025` |
| Review queue | `output\daily-publish\situation-review-<date>.md`, written by the daily board-refresh chain |
| ML study | [scripts/run_situation_ml_study.py](../../scripts/run_situation_ml_study.py) → models `situation_effect_v0[_gng]_{wr,rb,te}` in the metrics dataset (both scoring scales) |
| Backtest | [scripts/backtest_situation_effects.py](../../scripts/backtest_situation_effects.py) — walk-forward (fit ≤S−1, predict S), read-only, local OLS → `build/situation-study/situation_backtest_report.json` |
| Validations | 156–160 |

## What a `situation` block says

```json
{"team": "BUF", "team_2025": "CHI", "team_changed": true,
 "qb": "Josh Allen", "qb_2025": "Caleb Williams",
 "qb_quality_delta_ppg": 4.87, "qb_quality_delta_gng_ppg": 4.13,
 "head_coach": "Joe Brady", "hc_changed": true, "age": 29.4,
 "flags": ["NEW_TEAM", "QB_CHANGED", "QB_UPGRADE_MAJOR", "NEW_HC"],
 "metric_basis": "2025_CHI"}
```

`metric_basis` is the honesty field: it names the team-season every metric describes. Article rules in the GNG repo's AGENTS.md require stating changes and attributing metrics to their basis.

QB quality convention: a QB's quality entering season S+1 is his season-S PPG (knowable at decision time). `qb_to` is the platform's own board QB1 for the player's current team.

## GNG parity (owner rule)

**GNG rankings are included in anything Standard Scoring is included in.** Unsuffixed columns/fields are standard scoring; the `_gng` suffix is GNG Keeper. In this layer that means: `gng_ppg_prev/next` and `qb_quality_*_gng` on the table (migration 0048), `gng_ppg` in the `metrics` block and `qb_quality_delta_gng_ppg` in the `situation` block (dataset schema 1.1, boards 1.3), a GNG rank column plus std/gng QB deltas in the review queue, and a full `_gng` model set in the study. The two scales can disagree usefully — Kyler Murray is QB7 standard but QB20 GNG, so a WR inheriting him reads +2.0 std / +0.5 gng.

## Daily flow

The 07:30 chain rebuilds the layer after boards promote (stage 8.5), emits fresh dataset artifacts (8.6), writes the review queue (8.7-equivalent), and the wrapper uploads the immutable object and passes `--dataset-entry` to the publisher. On gate-tripped days the publisher carries the prior dataset forward.

## The ML study (Phase-3 input)

Linear models per position **and per scoring scale** over 2016–2025 transitions (n=3,362, 925 movers), controlling for prior PPG, games, and age. First results (r² 0.48–0.57; standard / gng):

| Effect | WR | RB | TE |
| --- | --- | --- | --- |
| Team change (avg) | −0.78 / −0.56 PPG | −0.59 / −0.33 | −0.42 / −0.33 |
| Per +1.0 PPG QB upgrade | +0.02 / +0.02 | +0.06 / +0.06 | +0.02 / +0.01 |
| Age per year | −0.02 / −0.01 | −0.22 / −0.15 | −0.03 / −0.02 |

Read: movers mildly underperform on average, QB upgrades claw back only a fraction, the RB age cliff is real — and both scales agree on direction, with GNG magnitudes proportionally smaller (its scoring compresses skill-player PPG).

### Walk-forward backtest (out-of-sample check)

The table above is in-sample. The backtest fits only on seasons before each holdout year (2020–2025) and predicts forward — the situation the 2026 board is actually in. Results, both scales:

- **On movers — the only players an adjustment would touch — the situation model beat the baseline in 22 of 24 position/scale/year cells** (WR and RB: 6/6 years in both scales), cutting mover error ~4–8% (e.g. WR standard MAE 1.96 → 1.84 PPG).
- Overall error never got worse on average; rank order (Spearman) improved slightly for WR/RB, flat for TE.
- Coefficient signs held in **all 36 training windows** (team change always negative, QB delta always positive) — the effects are stable, not artifacts of one fit.

This is the Phase-3 evidence bar: the findings generalize forward, so small bounded mover adjustments are justified; TE is the weakest case. Board-level backtests (would the *ranks* have been better) can't reach before 2026 — no historical fable boards exist — but the content-addressed feed archives every published board from launch onward, so a true board backtest accrues one season per year from here. Candidate magnitudes are small and mostly conservative. Phase 3 converts these into a bounded, coded post-formula adjustment policy (same `llm_adjustment_*` provenance and cutline guards as the acknowledged-crossing machinery) after owner sign-off; v1 study ideas: interaction terms (qb_delta × prior target share), boosted trees, quantile effects.

## Known limits

- Coaching change detection is head-coach-only; season infoboxes don't carry coordinators, so `oc_changed` stays NULL until a coordinator baseline is curated.
- Rookies and players without a 2025 stats season have no situation row (2 board players as of launch); absence of the block is itself signal.
- The profile points mart's `player_id_internal` scheme split (bare gsis vs `gsis:`-prefixed) is worked around here via `source_player_key`; a mart-side fix is tracked separately.
