# Phase 32.21: Low-Weight Injury Availability Modifier Sprint

Final decision: LOW WEIGHT AVAILABILITY SHOWS SIGNAL

## Scope

Phase 32.21 tested small injury-availability modifiers inside the SQL-native ranking backtest path. The work stayed in research mode.

No production deploy occurred. No live rankings were regenerated. No champion formulas were activated. No Pigskin chat, Gemini, live Sleeper API, materialization, or old Python full tournament path was used.

## Starting State

- Starting checkpoint commit: `bd8155a phase 32.20 integrate injury context features`.
- Phase 32.20 feature mart injury fields were present.
- Historical depth chart role remains blocked because no approved historical season/week source exists.
- Sleeper current roster context was not used as historical backtest input.

## Source Coverage

Availability coverage by feature-mart slice:

| Slice | QB | RB | WR | TE |
|---|---:|---:|---:|---:|
| 2017-2025 aggregate | 0.7152 | 0.7137 | 0.7344 | 0.7012 |
| 2024 validation | 0.5079 | 0.3378 | 0.3895 | 0.3707 |
| 2025 holdout | 0.8983 | 0.8716 | 0.8652 | 0.9796 |

All checked slices had non-null injury missing flags. Availability ranged from 30 to 100. Injury burden ranged from 8 to 28. Missed-time risk was sparse, with non-zero maxima only in TE and WR aggregate coverage.

## Candidate Family

Added `injury_availability_modifier_tournament_candidates()` in `src/ranking_formula_backtests.py`.

Candidate IDs:

- `current_pigskin_availability_blend_03_v0`
- `current_pigskin_availability_blend_05_v0`
- `current_pigskin_injury_penalty_cap_v0`
- `rb_current_pigskin_pbp_availability_blend_v0`
- `wr_current_pigskin_stats02_availability_blend_v0`
- `te_current_pigskin_stats02_availability_blend_v0`

Design:

- 3 percent availability blend as the safer generic modifier.
- 5 percent availability blend as an upper-bound check.
- Capped injury penalty using inverted risk fields at 2.5 percent each.
- RB-specific blend using high-value rush xFP plus 3 percent availability.
- WR/TE-specific blends using receiving role dominance xFP plus 3 percent availability.

## SQL-Native Dry Run

Dry-run command used the SQL-native summary evaluator and did not write rows.

Dry-run result:

```json
{
  "comparison_candidate_rows": 71,
  "dry_run": true,
  "estimated_bytes_processed": 94995749,
  "expected_detail_rows": 0,
  "expected_run_rows": 4,
  "expected_summary_rows": 284,
  "new_candidate_rows": 15,
  "version": "ranking_backtest_sql_native_injury_availability_modifier_v0"
}
```

## Summary-Only Write

The summary write was explicitly gated with `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` inside the same PowerShell command process and removed afterward.

Write result:

```json
{
  "detail_rows_written": 0,
  "job_id": "7850598c-c8dd-4256-bffd-39999400ff4b",
  "summary_only": true,
  "write": true
}
```

Persisted row checks:

| Check | Row count |
|---|---:|
| `ranking_backtest_runs` rows for this run prefix | 4 |
| `ranking_backtest_candidate_summaries` rows for this run prefix | 284 |
| New injury-availability summary rows | 60 |
| `ranking_backtest_results` rows for this run prefix | 0 |
| `ranking_formula_champions` rows | 0 |

## Results

2017-2025 aggregate:

- QB: tiny or negative movement versus current Pigskin. GNG Keeper had a tiny capped-penalty positive read.
- RB: `rb_current_pigskin_pbp_availability_blend_v0` improved pairwise across profiles, but captured points usually slipped slightly.
- WR: fragile. Pairwise weakened versus current Pigskin.
- TE: clearest aggregate signal. PPR pairwise improved by about 0.0039 and captured points by about 0.0028 versus current Pigskin.

2025 holdout:

- QB capped penalty improved pairwise and captured points across PPR, Half PPR, and Standard.
- RB special blend improved pairwise by about 0.010 to 0.013 across profiles, with captured points already maxed at 1.0000.
- WR remained mixed and weak on pairwise.
- TE improved pairwise in most profiles, but captured points were mixed.

2024 validation:

- QB capped penalty improved pairwise, but captured points often fell.
- RB special blend improved pairwise, but captured points fell.
- TE special blend improved pairwise in most profiles, but 2024 captured points dropped materially.
- WR remained below current Pigskin on pairwise.

Stored BQML comparison rows were unavailable for this run: `bqml_summary_rows = 0`.

## Safety Decisions

- Do not promote any injury-availability candidate to champion.
- Do not use the generic 5 percent availability blend as a default.
- Treat RB and TE low-weight availability as owner-review challenger concepts only.
- Keep WR out of owner-review challenger status until it protects current Pigskin pairwise strength.
- Keep depth role context blocked.
- Keep Sleeper current roster context out of historical backtests.
- Do not tune on 2025 holdout.

## Files Changed

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/validation/phase-32-21-injury-availability-modifier-report.md`

## Checks

Passed:

- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`
- `.\venv\Scripts\python.exe -m py_compile src\ranking_formula_backtests.py tests\test_ranking_formula_backtests.py`
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest_candidate_summaries`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_formula`

Validation result:

- Dry-run discovery found 240 validation files.
- `ranking_backtest_candidate_summaries` validation passed.
- Six `ranking_formula` validations passed.
- No pending migrations.

## Commit Status

Phase 32.20 was committed as `bd8155a`.

Phase 32.21 source, tests, docs, and this report are ready for a focused commit if final review passes.

## Recommended Next Phase

Phase 32.22 should compare the best RB and TE low-weight modifiers against owner-readable draft utility cuts, without activating champions. WR needs a narrower blend that preserves current Pigskin pairwise before further owner review.
