# Phase 32.5 Rolling Algorithm Tournament Scorecard Report

Final decision: **ROLLING ALGORITHM TOURNAMENT READY WITH WARNINGS**

Phase 32.5 added a controlled tournament family to the ranking formula backtest runner, dry-ran rolling 2017 through 2025 tournament coverage, wrote bounded tournament evidence to the ranking backtest evidence tables, and created the permanent ranking algorithm scorecard. No deployment occurred. No live rankings were regenerated. No champion formulas were activated. No Gemini, Pigskin chat, live Sleeper API, Cloud Run Job, Scheduler, ingestion, or materialization action was run.

## Git State

Files changed:

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/validation/phase-32-5-rolling-algorithm-tournament-scorecard-report.md`

Commit hash: this report is part of the final Phase 32.5 package commit. Use `git log -1 --oneline` for the exact repository hash after commit creation.

The historical validation backlog remains untracked and was not staged.

## Algorithms Tested

Tournament version:

- `ranking_backtest_tournament_v0_rolling_2017_2025`

Families evaluated:

- `current_pigskin_candidate_score_v1`
- seeded v0 weighted formulas
- v1 improved mapping formulas
- v2 trend-aware formulas
- equal-weight normalized blend
- value-over-replacement baseline
- scarcity-adjusted draft value baseline
- simple projection points baseline

Skipped:

- `current_pigskin_llm_final_v3`: documented only. Historical replay would require LLM calls.
- ML baselines: `scikit-learn` was not installed. No packages were installed.

## Season Coverage

Target seasons:

- 2017
- 2018
- 2019
- 2020
- 2021
- 2022
- 2023
- 2024
- 2025

Each run used a three-year prior source window when available and excluded target-season features.

Profiles:

- `ppr`
- `half_ppr`
- `standard`
- `gng_keeper`

Positions:

- QB
- RB
- WR
- TE

## Dry-Run Result

Dry-runs passed for every target season. No writes occurred in dry-run mode.

Per target season:

- candidate count: 48
- backtest run rows planned: 4
- candidate summary rows planned: 192

Result-shaped rows by target season:

| Target season | Result-shaped rows |
|---:|---:|
| 2017 | 217,968 |
| 2018 | 205,296 |
| 2019 | 210,864 |
| 2020 | 222,480 |
| 2021 | 237,552 |
| 2022 | 233,184 |
| 2023 | 230,352 |
| 2024 | 236,064 |
| 2025 | 81,168 |

The 2025 target row count is smaller because the current-season source slice is smaller than completed historical seasons.

## Controlled Write Result

`ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` was set only inside the PowerShell write process and removed in `finally`. It was confirmed empty afterward.

Rows written:

| Table | Row count |
|---|---:|
| `ranking_backtest_runs` | 36 |
| `ranking_backtest_results` | 1,874,928 |
| `ranking_backtest_candidate_summaries` | 1,728 |

Tables intentionally not written:

- `ranking_formula_champions`
- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_candidates`

`ranking_formula_champions` remains at 0 rows.

## Baseline Score

Family-level current Pigskin deterministic candidate baseline:

| Metric | Value |
|---|---:|
| pairwise win rate | 0.6697 |
| high-confidence pairwise win rate | 0.7575 |
| top-N hit rate | 0.5400 |
| VOR captured rate | 0.5981 |
| actual points captured rate | 0.7123 |
| missing-input rate | 0.0032 |

The baseline proxy uses deterministic candidate-score weights from `src/materialize.py`. Live Sleeper eligibility and depth-chart penalties were documented as unavailable for historical replay and were not zero-filled.

## Challenger Scores

Aggregate by family:

| Family | Pairwise | High-confidence | Top-N | VOR captured | Captured points | Missing |
|---|---:|---:|---:|---:|---:|---:|
| simple projection points | 0.6728 | 0.7364 | 0.5387 | 0.5956 | 0.7115 | 0.0006 |
| current Pigskin candidate | 0.6697 | 0.7575 | 0.5400 | 0.5981 | 0.7123 | 0.0032 |
| scarcity adjusted draft value | 0.6660 | 0.7394 | 0.5374 | 0.5900 | 0.7094 | 0.0365 |
| value over replacement | 0.6601 | 0.7265 | 0.5223 | 0.5651 | 0.6928 | 0.0004 |
| equal weight blend | 0.6577 | 0.7299 | 0.5185 | 0.5541 | 0.6858 | 0.0018 |
| v1 improved mappings | 0.6496 | 0.7261 | 0.5134 | 0.5488 | 0.6819 | 0.1110 |
| seeded v0 | 0.6353 | 0.6968 | 0.4859 | 0.5228 | 0.6479 | 0.4314 |
| v2 trend aware | 0.5491 | 0.5630 | 0.3919 | 0.3887 | 0.5402 | 0.1157 |

## Baseline Versus Challenger Comparison

No challenger beat the current deterministic baseline clearly across profiles and positions. The simple projection baseline produced the best family-level pairwise score, but its edge over the current baseline was about 0.003. That is an approximate tie, not a replacement signal.

Best profile-position leaders:

- GNG Keeper QB: current Pigskin baseline wins.
- PPR RB and Standard RB: simple projection points leads by less than 0.005 pairwise.
- TE and WR leaders often came from seeded v0, but their missing-input rates were high because `pigskin_context_score` is unavailable in the historical feature path.
- v2 trend-aware candidates underperformed after full historical target coverage was added.

Classification:

- current Pigskin baseline: still viable
- simple projection: owner-review challenger, not activation-ready
- scarcity-adjusted draft value: useful secondary baseline
- seeded v0 TE/WR winners: insufficient evidence due missing-input rates
- v2 trend-aware: needs feature work

## Overall Draft-Value Results

Partial only. The current backtest runner ranks within position and does not yet produce true cross-position draft-order scoring by pick band. The scorecard documents this as a gap.

Available VOR-captured family leaders:

- current Pigskin candidate: 0.5981
- simple projection points: 0.5956
- scarcity adjusted draft value: 0.5900

## Scorecard Update

Created:

- `docs/rebuild/ranking-algorithm-scorecard.md`

The scorecard includes:

- purpose
- current live ranking algorithm
- LLM final baseline documentation
- accuracy target
- scoring profiles and seasons covered
- algorithm registry
- Phase 32.5 tournament history
- position/profile leaderboards
- partial draft-value leaderboard
- baseline and challenger scores
- rejected, pending, and next-experiment lists

## Live Ranking No-Change

Active `analytics_pigskin_rankings` row counts were verified unchanged:

| Profile | QB | RB | WR | TE |
|---|---:|---:|---:|---:|
| `ppr` | 45 | 80 | 100 | 60 |
| `half_ppr` | 45 | 80 | 100 | 60 |
| `standard` | 45 | 80 | 100 | 60 |
| `gng_keeper` | 45 | 80 | 100 | 60 |

No champion activation occurred.

## Pigskin Isolation

Formula and backtest tables remain outside Pigskin-visible tool declarations. The focused tests still assert that app and Pigskin tool files do not expose:

- `ranking_formula_candidates`
- `ranking_backtest_results`
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE`

## Tests And Checks

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile app.py`
- `.\venv\Scripts\python.exe -m py_compile src\ranking_formula_backtests.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_formula`

Validation results:

- Full test discovery passed: 704 tests.
- No pending migrations.
- Validation dry-run discovered ranking formula and backtest validations through `209_ranking_backtest_candidate_summaries_grain_and_ranges.sql`.
- `ranking_backtest` validations passed: 3 passed, 0 failed.
- `ranking_formula` validations passed: 6 passed, 0 failed.

## Remaining Warnings

- Overall draft-order and pick-band regret metrics are not implemented yet.
- Seeded v0 WR/TE leaders have high missing-input rates.
- The live deterministic baseline includes roster/depth-chart behavior that cannot be fully replayed historically in this runner.
- ML baselines were skipped because dependencies were unavailable.
- The generated backtest run IDs contain a repeated `ranking_backtest_` prefix because the supplied version string already includes that prefix. The run IDs are valid and bounded, but the naming is noisy.

## Recommended Next Phase

Phase 32.6: owner review of algorithm scorecard, then choose one:

- build a formula comparison dashboard
- add cross-position draft-order metrics
- improve challenger algorithms and rerun
- generate formula-driven candidate rankings only after owner approval
