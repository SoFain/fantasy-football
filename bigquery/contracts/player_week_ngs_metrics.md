# player_week_ngs_metrics Contract

Purpose: derived weekly nflverse Next Gen Stats metrics for ranking research.

Grain:

- `source_version`
- `season`
- `week`
- `player_id_internal`
- `position`

Source tables:

- `raw_nflverse_ngs_receiving`
- `raw_nflverse_ngs_rushing`
- `raw_nflverse_ngs_passing`

Identity:

- `player_id_internal` is the nflverse GSIS player id without a synthetic prefix.
- `player_gsis_id` preserves the raw GSIS id.

Missing-data policy:

- Missing NGS inputs remain null.
- `ngs_missing_flags_json` must explain unsupported or missing fields.
- nflverse receiving does not provide expected catch percentage or catch-over-expected in the current public source. Those fields stay null with explicit unavailable flags.

Leakage policy:

- The table stores source-season weekly facts.
- `ranking_backtest_feature_mart` may consume these rows only where the NGS source season is less than the target season.
- No target-season NGS predictors are allowed in ranking backtests.

Write policy:

- Writes are bounded by `source_version` and season range.
- The materialization gate is `ALLOW_NFLVERSE_NGS_METRICS_MATERIALIZATION=true`.
- No global truncate is allowed.
