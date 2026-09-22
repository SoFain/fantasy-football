# Ranking Research North Star

Last updated: 2026-07-04

## Position

Fantasy draft prediction is a top-heavy, scarcity-aware ranking problem. It is not a raw point-projection problem.

The useful question is not only "who scores the most points?" It is "who helps a drafter capture scarce value at the right position and pick band while avoiding avoidable busts?"

## What Matters

- NDCG@K: top-ranked players matter more than back-end ordering.
- Value captured and VOR captured: the board should capture useful draft value, not just total points.
- Elite recall: missing a top QB, RB, WR, or TE is more costly than swapping two low-end options.
- Tier accuracy: players should land in the right practical draft bucket.
- Bust rate: top recommendations should avoid severe miss outcomes.
- Pick-band regret: a ranking can be right directionally and still waste draft capital.
- Pairwise win rate: strong rank gaps should usually pick the better actual outcome.

## Feature Direction

Expected opportunity matters more than last year's raw points. Usage, role stability, red-zone opportunity, availability, and trend context should carry more weight than trailing production alone.

The current feature mart is good enough for bounded research. It still needs better route, alignment, pressure, first-read, and contact-yard inputs before those concepts can become official predictors. Until source flags prove those metrics exist, they stay blocked.

## Model Direction

The likely winner is an ensemble, not one magic formula.

Current Pigskin remains the live baseline. Simple projection and BigQuery ML baselines are useful challengers, but neither should replace the baseline without owner review and a clear holdout win. Future research should compare constrained ensembles through the SQL-native evaluator and keep champion activation separate from experimentation.

## Phase 32.11 Ensemble Finding

The first constrained ensemble prototype did not produce a replacement signal.

It proved the SQL-native evaluator can blend normalized current Pigskin, simple projection, scarcity-adjusted draft value, BQML logistic elite, and BQML linear points without reviving the old Python tournament path. It also showed the current ingredients are too correlated. Reweighting them helped some top-N slices, but it weakened high-confidence and overall pairwise behavior.

Next useful work is feature work, not more tiny weight-grid tuning. The warehouse needs better opportunity and route-level signals before another ensemble pass is likely to matter.

## Phase 32.12 Feature Direction

The first feature-work pass added real opportunity and role inputs from approved warehouse sources:

- QB rushing leverage from carries, carry share, red-zone carries, and inside-five carries.
- RB high-value opportunity from red-zone touches, high-value touches, target share, and opportunity share.
- WR and TE dominance from target share, air-yards share, WOPR, and red-zone targets.
- Team environment from plays, EPA per play, and neutral pass rate.
- Ceiling and bust history from profile fantasy point outcomes.

This is now a better research base than more weight-grid tuning. The next comparison should test whether these features improve multi-year SQL-native summaries against current Pigskin, simple projection, and the BQML challengers.

Still blocked: first-read share, true route share as a reliable feature, YPRR without route source proof, and end-zone targets. Missing flags are part of the feature contract.

## Safety Rules

- No live ranking regeneration during research phases.
- No formula champion activation without a separate owner-approved phase.
- No random train/test split as primary evidence.
- No target-season outcome columns as predictors.
- No Pigskin exposure for formula or backtest tables.
- No old Python full-tournament path for official evidence.
