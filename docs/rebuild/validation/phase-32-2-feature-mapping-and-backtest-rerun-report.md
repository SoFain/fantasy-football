# Phase 32.2 Feature Mapping and Backtest Rerun Report

Final decision: **BACKTEST FEATURE MAPPING IMPROVED WITH WARNINGS**

Phase 32.2 improved deterministic no-lookahead source mappings and wrote a new bounded v1 backtest set for 2024-to-2025 across PPR, Half PPR, Standard, and GNG Keeper. No champions were activated. No production ranking rows were regenerated. No deploy, Pigskin chat call, LLM ranking generation, live Sleeper API call, Cloud Run Job trigger, Scheduler job creation, or Pigskin formula/table exposure occurred.

## Scope

Target backtest run IDs:

- `ranking_backtest_v1_2024_to_2025_ppr`
- `ranking_backtest_v1_2024_to_2025_half_ppr`
- `ranking_backtest_v1_2024_to_2025_standard`
- `ranking_backtest_v1_2024_to_2025_gng_keeper`

Changed files:

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/validation/phase-32-2-feature-mapping-and-backtest-rerun-report.md`

## Feature Mapping Changes

New or improved deterministic mappings:

- `rushing_attempts` now uses `player_week_advanced_metrics.carries` instead of unavailable 2024 truth carries.
- `air_yards` now uses `player_week_advanced_metrics.air_yards_share` as a share proxy, with share-aware score normalization.
- `team_epa_per_play` now maps from `pigskin_player_context_packet_current.team_context_json.team_epa_per_play`.
- `team_pass_rate` falls back to `pigskin_player_context_packet_current.team_context_json.neutral_pass_rate`.
- v1 backtest IDs are versioned through `--backtest-version v1`.
- Candidate summary JSON now records expected feature count, available feature count, missing feature count, missing feature names, and top missing features.

2024 packet context currently exists in the PPR source lane only. The v1 backtest uses that PPR packet context as source-season-neutral context for all scoring profiles. This is intentional for Phase 32.2 and remains documented as a warning.

## Still Unavailable

These features remain missing instead of being zero-filled:

- `recent_points_avg`: no approved 2024 profile-specific historical points source in the no-lookahead input set.
- `dropbacks`: no approved 2024 dropback/pass-attempt source in the current backtest feature query.
- `passing_epa_per_play`: no approved 2024 passing-specific EPA source in the current backtest feature query.
- `receiving_yards`: no approved 2024 receiving-yard source in the current backtest feature query.
- `receiving_epa`: no approved 2024 receiving EPA source in the current backtest feature query.
- `red_zone_targets`: column exists in advanced metrics, but 2024 coverage is effectively unavailable.
- `goal_line_opportunities`: inside-5 source exists, but 2024 coverage is effectively unavailable.
- `pigskin_context_score`: packet context has JSON/text context, but no numeric score field.

## Dry Run

Command shape:

```powershell
.\venv\Scripts\python.exe -m src.ranking_formula_backtests --from-bigquery-candidates --formula-set-id ranking_formula_set_v0_2026_001 --source-season 2024 --target-season 2025 --target-week-start 1 --target-week-end 18 --positions QB,RB,WR,TE --scoring-profile-id ppr,half_ppr,standard,gng_keeper --league-type-id redraft --roster-format-id one_qb --backtest-version v1 --dry-run
```

Dry-run summary:

- backtest run count: 4
- candidate count: 12
- result-shaped rows: 19,140
- candidate summary-shaped rows: 48
- champion recommendations: 16
- write: false

## Controlled Write

The bounded write was run with `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` set only inside the command process and removed afterward. The gate was confirmed unset after the write.

Written v1 evidence:

- `ranking_backtest_runs`: 4 v1 rows
- `ranking_backtest_results`: 19,140 v1 rows
- `ranking_backtest_candidate_summaries`: 48 v1 rows
- `ranking_formula_champions`: 0 rows, unchanged

Total table state after Phase 32.2:

| Table | Row count |
|---|---:|
| `ranking_backtest_candidate_summaries` | 96 |
| `ranking_backtest_results` | 38,280 |
| `ranking_backtest_runs` | 8 |
| `ranking_formula_candidates` | 12 |
| `ranking_formula_champions` | 0 |
| `ranking_formula_sets` | 1 |

## V1 Result Counts

Each profile/position has the expected three candidate formulas:

| Profile | QB | RB | WR | TE |
|---|---:|---:|---:|---:|
| `ppr` | 882 | 1,041 | 1,725 | 1,137 |
| `half_ppr` | 882 | 1,041 | 1,725 | 1,137 |
| `standard` | 882 | 1,041 | 1,725 | 1,137 |
| `gng_keeper` | 882 | 1,041 | 1,725 | 1,137 |

Integrity checks:

- duplicate v1 result grain groups: 0
- invalid v1 score rows: 0
- invalid v1 summary rows: 0

## Recommendation Comparison

Recommended formula by profile and position, using summary ranking order:

| Profile | Position | v0 candidate | v0 missing | v1 candidate | v1 missing |
|---|---|---|---:|---|---:|
| `ppr` | QB | `ranking_formula_qb_volume_v0_2026_001` | 0.800000 | `ranking_formula_qb_volume_v0_2026_001` | 0.600000 |
| `ppr` | RB | `ranking_formula_rb_balanced_v0_2026_001` | 0.404611 | `ranking_formula_rb_balanced_v0_2026_001` | 0.404611 |
| `ppr` | WR | `ranking_formula_wr_volume_v0_2026_001` | 0.600000 | `ranking_formula_wr_volume_v0_2026_001` | 0.400000 |
| `ppr` | TE | `ranking_formula_te_balanced_v0_2026_001` | 0.800000 | `ranking_formula_te_volume_v0_2026_001` | 0.404222 |
| `half_ppr` | QB | `ranking_formula_qb_volume_v0_2026_001` | 0.800000 | `ranking_formula_qb_volume_v0_2026_001` | 0.600000 |
| `half_ppr` | RB | `ranking_formula_rb_balanced_v0_2026_001` | 0.404611 | `ranking_formula_rb_balanced_v0_2026_001` | 0.404611 |
| `half_ppr` | WR | `ranking_formula_wr_volume_v0_2026_001` | 0.600000 | `ranking_formula_wr_volume_v0_2026_001` | 0.400000 |
| `half_ppr` | TE | `ranking_formula_te_balanced_v0_2026_001` | 0.800000 | `ranking_formula_te_volume_v0_2026_001` | 0.404222 |
| `standard` | QB | `ranking_formula_qb_volume_v0_2026_001` | 0.800000 | `ranking_formula_qb_volume_v0_2026_001` | 0.600000 |
| `standard` | RB | `ranking_formula_rb_balanced_v0_2026_001` | 0.404611 | `ranking_formula_rb_balanced_v0_2026_001` | 0.404611 |
| `standard` | WR | `ranking_formula_wr_volume_v0_2026_001` | 0.600000 | `ranking_formula_wr_volume_v0_2026_001` | 0.400000 |
| `standard` | TE | `ranking_formula_te_balanced_v0_2026_001` | 0.800000 | `ranking_formula_te_volume_v0_2026_001` | 0.404222 |
| `gng_keeper` | QB | `ranking_formula_qb_volume_v0_2026_001` | 0.800000 | `ranking_formula_qb_volume_v0_2026_001` | 0.600000 |
| `gng_keeper` | RB | `ranking_formula_rb_balanced_v0_2026_001` | 0.404611 | `ranking_formula_rb_balanced_v0_2026_001` | 0.404611 |
| `gng_keeper` | WR | `ranking_formula_wr_volume_v0_2026_001` | 0.600000 | `ranking_formula_wr_volume_v0_2026_001` | 0.400000 |
| `gng_keeper` | TE | `ranking_formula_te_balanced_v0_2026_001` | 0.800000 | `ranking_formula_te_volume_v0_2026_001` | 0.404222 |

V1 moved TE recommendations from balanced to volume across all four profiles. QB and WR missing rates improved. RB was unchanged because the remaining missing features are `pigskin_context_score` and `recent_points_avg`.

No v1 recommendation is clean enough for automatic champion activation. Every recommended formula still has `missing_input_rate > 0.30`.

## Production Ranking No-Change Check

Active final rankings remain intact:

- expected active final ranking rows: 1,140
- each scoring profile has QB 45, RB 80, WR 100, TE 60
- Trey McBride remains TE rank 1 for PPR, Half PPR, Standard, and GNG Keeper
- transient candidate table remains PPR-only with 936 rows

No final Pigskin rankings were regenerated.

## Pigskin Isolation

Targeted source search found no Pigskin-visible references to ranking backtest or formula tables in:

- `app.py`
- `src/pigskin_context_tools.py`
- `src/pigskin_packet_guardrails.py`
- `src/pigskin_context_qa.py`

Only the existing historical packet tool flag name was present in guardrail code.

## Checks Run

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\ranking_formula_backtests.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`
- `.\venv\Scripts\python.exe -m unittest tests.test_seed_ranking_formula_candidates`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_formula`

Validation results:

- `ranking_backtest`: 3 passed, 0 failed
- `ranking_formula`: 6 passed, 0 failed
- pending migrations: none

## Warnings

- Recommended v1 formulas still exceed the missing-input activation threshold.
- The PPR packet-context lane is reused for all scoring profiles because 2024 packet context is currently PPR-only.
- `pigskin_context_score` remains unavailable as a numeric source.
- `recent_points_avg` remains unavailable for the 2024 source season in the approved no-lookahead input set.
- Red-zone and goal-line coverage remains insufficient for some candidate formulas.
- Git reported LF-to-CRLF warnings for touched Python files on Windows.

## Recommended Next Phase

Phase 32.3 should improve formula candidates before champion activation. The highest-return path is to revise or add candidate formulas that avoid currently unavailable features, especially `pigskin_context_score`, `recent_points_avg`, `dropbacks`, red-zone targets, and goal-line opportunity features unless those sources are first backfilled with real data.
