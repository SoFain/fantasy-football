# Ranking Formula Backtest Foundation

## Scope

Phase 31.1 adds the contract and dry-run runner foundation for position-specific ranking formulas. It does not expose formulas to Pigskin chat and does not deploy.

## Tables

- `ranking_formula_candidates`
- `ranking_backtest_runs`
- `ranking_backtest_results`
- `ranking_backtest_candidate_summaries`
- `ranking_formula_champions`
- `ranking_formula_sets`

## Formula JSON

Required shape:

```json
{
  "version": "ranking_formula_v0",
  "position": "QB",
  "score_expression": "weighted_linear",
  "features": ["epa_per_play", "success_rate"],
  "weights": {"epa_per_play": 0.6, "success_rate": 0.4},
  "normalization": {"method": "position_percentile"}
}
```

The runner only accepts named features from position allowlists. It rejects SQL text, table names, executable code, and unknown features.

## Feature Allowlist

Initial common allowed feature families:

- fantasy points and actual weekly truth
- EPA and success rate from curated advanced metrics
- usage volume from curated historical player/week marts
- Pigskin packet numeric signals already materialized as safe packet context

Blocked until source flags prove availability:

- route share
- YPRR
- first-read share
- true pressure
- contact yards
- alignment

## Targets

Initial target definitions are deterministic:

- `top_12_position`: player finishes inside position top 12 that week
- `top_24_position`: player finishes inside position top 24 that week
- `beat_position_median`: player beats median same-position weekly points

Win rate is `target_hit_count / evaluated_player_week_count`.

## Candidate Summaries

`ranking_backtest_candidate_summaries` stores candidate-level aggregate evidence by run, candidate, position, scoring profile, league type, roster format, and target. It is the comparison surface for later champion selection.

Initial dry-runs produce summary-shaped rows with `sample_size=0` and metric fields empty. Real metrics are reserved for a bounded backtest phase after migration apply.

## Write Gate

Live writes require:

`ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`

Dry-run mode is default and non-mutating.

## Production Exposure

No production exposure is added in Phase 31.1. Pigskin chat remains unable to write arbitrary SQL or access this lane directly.
