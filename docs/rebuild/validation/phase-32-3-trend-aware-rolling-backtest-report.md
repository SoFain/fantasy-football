# Phase 32.3 Trend-Aware Rolling Backtest Report

Final decision: **TREND AWARE ROLLING BACKTEST READY WITH WARNINGS**

Phase 32.3 added deterministic trend-aware formula candidates and multi-year source-window feature generation. A bounded v2 backtest was dry-run and then written for the only currently valid target pair: 2024 source window to 2025 target. No champion formulas were activated. No final Pigskin rankings were regenerated. No deploy, Pigskin chat call, LLM ranking generation, live Sleeper API call, Cloud Run Job trigger, Scheduler job creation, or Pigskin formula/table exposure occurred.

## Git State

Changed files:

- `src/ranking_formula_backtests.py`
- `scripts/seed_ranking_formula_candidates.py`
- `tests/test_ranking_formula_backtests.py`
- `tests/test_seed_ranking_formula_candidates.py`
- `docs/rebuild/validation/phase-32-3-trend-aware-rolling-backtest-report.md`

Commit hash: recorded in the final response after commit.

The existing untracked historical validation backlog remains outside this package.

## Historical Target Coverage

Coverage audit for 2014 through 2025:

- `player_week_advanced_metrics`: PPR source rows exist for 2014 through 2025 across QB/RB/WR/TE.
- `pigskin_player_context_packet_current`: PPR packet rows exist for 2014 through 2025, with uneven coverage in some seasons.
- `analytics_player_weekly_truth`: QB/RB/WR/TE rows exist only for 2025.
- `analytics_player_fantasy_points_by_profile`: PPR, Half PPR, Standard, and GNG Keeper rows exist only for 2025.

Historical profile fantasy point materialization was not run. The required historical truth source rows for 2014 through 2024 are not present in `analytics_player_weekly_truth`, and `player_week_advanced_metrics` does not contain enough raw stat columns to calculate full profile fantasy points. A safe historical target backfill needs a real historical stat source first.

Valid rolling target pairs now:

| Source window | Target season | Status |
|---|---:|---|
| 2022-2024 | 2025 | tested and written as v2 |

Blocked pairs:

- 2014 to 2015 through 2023 to 2024 are blocked because target fantasy-point rows do not exist for 2015 through 2024.

## Trend Features Implemented

The no-lookahead feature query now supports multi-year source windows and explicitly filters out target-season data:

- `metrics.season BETWEEN @source_window_start AND @source_season`
- `metrics.season < @target_season`

New trend features:

- `points_per_game_slope_3yr`
- `total_points_slope_3yr`
- `opportunity_slope_3yr`
- `target_share_slope_3yr`
- `carry_share_slope_3yr`
- `receiving_usage_slope_3yr`
- `wopr_slope_3yr`
- `epa_slope_3yr`
- `efficiency_slope_3yr`
- `availability_rate_3yr`
- `weekly_volatility_3yr`
- `improving_3yr`
- `declining_3yr`
- `breakout_trajectory_3yr`

Fantasy-point trend fields are implemented but remain mostly unavailable until historical profile fantasy points are backfilled. The v2 candidates avoid those fields.

Age or experience buckets were not implemented because no approved age/experience source was present in the allowed input set for this backtest path.

## V2 Formula Candidates

Added 12 deterministic v2 candidates in code:

- QB: trend balanced, trend opportunity, trend efficiency
- RB: trend balanced, trend opportunity, trend risk adjusted
- WR: trend balanced, trend breakout, trend risk adjusted
- TE: trend balanced, trend breakout, trend efficiency

The candidates avoid known unavailable or blocked features:

- `pigskin_context_score`
- red-zone and goal-line fields
- `dropbacks`
- `receiving_yards`
- `receiving_epa`
- route share, YPRR, first-read share, true pressure, contact yards, alignment

The seed script now supports a dry-runable v2 package:

```powershell
.\venv\Scripts\python.exe scripts\seed_ranking_formula_candidates.py --candidate-family trend_v2
```

This was run in dry-run mode only. No v2 candidate rows were written to `ranking_formula_candidates`.

## Dry Run

Command shape:

```powershell
.\venv\Scripts\python.exe -m src.ranking_formula_backtests --from-bigquery-candidates --formula-set-id ranking_formula_set_v0_2026_001 --source-season 2024 --target-season 2025 --target-week-start 1 --target-week-end 18 --all-positions --all-scoring-profiles --league-type-id redraft --roster-format-id one_qb --backtest-version v2_trend_rolling --source-window-years 3 --candidate-family trend_v2 --dry-run
```

Dry-run result:

- backtest run count: 4
- candidate count: 12
- candidate summaries: 48
- result-shaped rows: 20,292
- source window: 2022-2024
- target season: 2025
- scoring profiles: PPR, Half PPR, Standard, GNG Keeper
- positions: QB, RB, WR, TE
- write: false

## Controlled Write

The bounded v2 write was run with `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` set only inside the PowerShell command process. The gate was removed in a `finally` block and confirmed unset afterward.

Written run IDs:

- `ranking_backtest_v2_trend_rolling_2024_to_2025_ppr`
- `ranking_backtest_v2_trend_rolling_2024_to_2025_half_ppr`
- `ranking_backtest_v2_trend_rolling_2024_to_2025_standard`
- `ranking_backtest_v2_trend_rolling_2024_to_2025_gng_keeper`

Rows written:

- `ranking_backtest_runs`: 4 v2 rows
- `ranking_backtest_results`: 20,292 v2 rows
- `ranking_backtest_candidate_summaries`: 48 v2 rows

Tables not written:

- `ranking_formula_champions`
- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_candidates`

## Warehouse State After Write

| Table | Row count |
|---|---:|
| `ranking_backtest_candidate_summaries` | 144 |
| `ranking_backtest_results` | 58,572 |
| `ranking_backtest_runs` | 12 |
| `ranking_formula_candidates` | 12 |
| `ranking_formula_champions` | 0 |
| `ranking_formula_sets` | 1 |

V2 result counts:

| Profile | QB | RB | WR | TE |
|---|---:|---:|---:|---:|
| `ppr` | 885 | 1,098 | 1,914 | 1,176 |
| `half_ppr` | 885 | 1,098 | 1,914 | 1,176 |
| `standard` | 885 | 1,098 | 1,914 | 1,176 |
| `gng_keeper` | 885 | 1,098 | 1,914 | 1,176 |

V2 validation checks:

- duplicate result grain groups: 0
- invalid score rows: 0
- invalid summary rows: 0

## V0/V1/V2 Comparison

Best v2 recommendations by profile and position:

| Profile | Position | Candidate | Pairwise | High-confidence pairwise | Top-N | Captured points | VOR captured | Missing |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `ppr` | QB | `ranking_formula_qb_trend_efficiency_v2_trend_2026_001` | 0.546114 | 0.621528 | 0.773148 | 0.821436 | 0.778177 | 0.000678 |
| `ppr` | RB | `ranking_formula_rb_trend_opportunity_v2_trend_2026_001` | 0.652610 | 0.705212 | 1.000000 | 1.000000 | null | 0.004918 |
| `ppr` | WR | `ranking_formula_wr_trend_breakout_v2_trend_2026_001` | 0.580730 | 0.607811 | 0.726852 | 0.793730 | 0.794523 | 0.024451 |
| `ppr` | TE | `ranking_formula_te_trend_breakout_v2_trend_2026_001` | 0.523367 | 0.562410 | 0.587963 | 0.656519 | 0.587949 | 0.016327 |
| `half_ppr` | QB | `ranking_formula_qb_trend_efficiency_v2_trend_2026_001` | 0.545687 | 0.621528 | 0.773148 | 0.821370 | 0.778048 | 0.000678 |
| `half_ppr` | RB | `ranking_formula_rb_trend_opportunity_v2_trend_2026_001` | 0.656232 | 0.707403 | 1.000000 | 1.000000 | null | 0.004918 |
| `half_ppr` | WR | `ranking_formula_wr_trend_breakout_v2_trend_2026_001` | 0.574871 | 0.600295 | 0.731481 | 0.792881 | 0.794578 | 0.024451 |
| `half_ppr` | TE | `ranking_formula_te_trend_breakout_v2_trend_2026_001` | 0.524001 | 0.563492 | 0.587963 | 0.656883 | 0.596669 | 0.016327 |
| `standard` | QB | `ranking_formula_qb_trend_efficiency_v2_trend_2026_001` | 0.545687 | 0.621528 | 0.773148 | 0.821305 | 0.777918 | 0.000678 |
| `standard` | RB | `ranking_formula_rb_trend_opportunity_v2_trend_2026_001` | 0.652862 | 0.701624 | 1.000000 | 1.000000 | null | 0.004918 |
| `standard` | WR | `ranking_formula_wr_trend_breakout_v2_trend_2026_001` | 0.571981 | 0.597401 | 0.726852 | 0.790508 | 0.794116 | 0.024451 |
| `standard` | TE | `ranking_formula_te_trend_breakout_v2_trend_2026_001` | 0.524785 | 0.563114 | 0.601852 | 0.655295 | 0.609777 | 0.016327 |
| `gng_keeper` | QB | `ranking_formula_qb_trend_efficiency_v2_trend_2026_001` | 0.552991 | 0.623264 | 0.773148 | 0.810131 | 0.774214 | 0.000678 |
| `gng_keeper` | RB | `ranking_formula_rb_trend_opportunity_v2_trend_2026_001` | 0.651003 | 0.701969 | 1.000000 | 1.000000 | null | 0.004918 |
| `gng_keeper` | WR | `ranking_formula_wr_trend_breakout_v2_trend_2026_001` | 0.570743 | 0.594344 | 0.729167 | 0.791003 | 0.791883 | 0.024451 |
| `gng_keeper` | TE | `ranking_formula_te_trend_breakout_v2_trend_2026_001` | 0.527743 | 0.566174 | 0.587963 | 0.660735 | 0.621048 | 0.016327 |

Compared with v1, v2 sharply reduced missing-input rates. Pairwise performance regressed for WR and TE versus v1. RB remained below the strongest v0/v1 pairwise scores, but high-confidence RB pairwise reached the 70% target in every profile.

## Trend-Specific Findings

Young ascending and breakout-style cases:

- WR and TE breakout formulas became the v2 recommendations in every profile.
- Missing rates for breakout formulas were low because target share, WOPR, availability, and source-window flags are available from advanced metrics.

Declining veteran and risk cases:

- Decline flags are implemented and tested.
- Risk-adjusted candidates did not win in this run, which suggests the current decline/volatility penalty may be too blunt or less predictive than raw trend opportunity.

Low-volume efficiency traps:

- QB efficiency won all profiles but did not reach the 70% pairwise target.
- TE efficiency did not beat TE breakout, which is consistent with TE target share being more useful than pure efficiency in this dataset.

High-volume inefficient players:

- RB trend opportunity won despite not explicitly penalizing inefficiency heavily. This needs owner review before champion activation.

## 70% Target Assessment

Closest to 70%:

- RB high-confidence pairwise: 0.701624 to 0.707403 across profiles.
- RB top-N hit rate and captured points: 1.000000 across profiles.

Still below 70%:

- QB high-confidence pairwise: about 0.62.
- WR high-confidence pairwise: about 0.59 to 0.61.
- TE high-confidence pairwise: about 0.56.

Likely improvements:

- Backfill historical target fantasy points for 2015-2024 to test more than one target season.
- Add real historical points trends once target/profile fantasy points exist.
- Improve TE formula features. TE v2 trend formulas lost too much top-N and captured-points performance.
- Add replacement-aware and scarcity-aware metrics before overall draft-board work.

## Live 2026 Source Policy

For live 2026 rankings:

- Use completed 2025 data.
- Use 2023-2025 trend windows where available.
- Use current 2026 roster, depth, team, injury, and context only when those sources are available and explicitly current.
- Do not use actual 2026 outcomes as predictors.
- Keep scoring profile selected by the user.
- Keep formula/backtest tables out of Pigskin chat until a separate exposure decision.

## Draft Board Implications

Trend-aware position formulas can feed a future overall board through:

- projection value by scoring profile
- value over replacement
- positional scarcity
- tier cliffs
- risk and volatility
- draft opportunity cost

They are not ready to drive an overall draft board yet. The position formulas need broader multi-year target coverage first.

## Production Ranking No-Change

Active final rankings remain unchanged:

- expected active final ranking rows: 1,140
- each scoring profile has QB 45, RB 80, WR 100, TE 60
- Trey McBride remains TE rank 1 in PPR, Half PPR, Standard, and GNG Keeper
- transient candidate table remains PPR-only with 936 rows

No final Pigskin rankings were regenerated.

## Champion Activation

No champion formulas were activated.

`ranking_formula_champions` row count remains 0.

## Pigskin Isolation

Targeted search found no Pigskin-facing references to ranking formula or ranking backtest tables in:

- `app.py`
- `src/pigskin_context_tools.py`
- `src/pigskin_packet_guardrails.py`
- `src/pigskin_context_qa.py`

No `execute_bigquery_sql` exposure was added.

## Checks Run

Passed or reported OK:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\ranking_formula_backtests.py scripts\seed_ranking_formula_candidates.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`
- `.\venv\Scripts\python.exe -m unittest tests.test_seed_ranking_formula_candidates`
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests tests.test_seed_ranking_formula_candidates`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_formula`

Validation results after v2 write:

- `ranking_backtest`: 3 passed, 0 failed
- `ranking_formula`: 6 passed, 0 failed
- pending migrations: none

PowerShell surfaced unittest output as a native-command warning because output was written through stderr, but the unittest runner reported `OK`.

## Remaining Warnings

- True rolling multi-season target testing is blocked until 2015-2024 profile fantasy-point targets exist.
- V2 candidate rows were not written to `ranking_formula_candidates`; they are code-defined and dry-runable through the seed script.
- Fantasy-points trend fields are implemented but unavailable for historical source windows until profile fantasy points are backfilled.
- V2 greatly improves missing-input rates, but v2 does not dominate v1/v0 on pairwise performance.
- TE trend-aware formulas need revision.
- RB high-confidence pairwise reaches the target, but only on one target season. Do not activate a champion from one-season evidence.

## Recommended Next Phase

Phase 32.4 should be one of:

- Owner review of trend-aware formula leaderboard
- Build a historical fantasy-point target backfill from a real stat source
- Formula comparison dashboard
- Improve TE and WR trend formulas and rerun
