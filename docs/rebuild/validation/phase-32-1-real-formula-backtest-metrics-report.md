# Phase 32.1 Real Formula Backtest Metrics Report

Final decision: **REAL FORMULA BACKTEST METRICS READY WITH WARNINGS**

Phase 32.1 computed real no-lookahead backtest metrics for all 12 seeded ranking formulas across PPR, Half PPR, Standard, and GNG Keeper. The controlled write was run behind `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`, then the gate was removed in the same PowerShell command process.

No production or staging deploy occurred. No Pigskin chat prompt was run. No LLM-backed ranking generation ran. No Cloud Run Job or Scheduler job was triggered. Active Pigskin rankings were not overwritten. No rows were written to `ranking_formula_champions`.

## Git State

Latest committed history before this phase included:

- `69d1505 Document Player Profiles multi-profile UI smoke`
- `02f09b8 Document generated multi-profile Pigskin rankings`
- `e8270c6 Fix Pigskin ranking write schema alignment`

Files changed for this phase:

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/validation/phase-32-1-real-formula-backtest-metrics-report.md`

Commit hash: recorded in the final Codex response after commit. A commit cannot contain its own final hash without changing that hash.

## Warehouse State Before Write

| Table | Before row count |
| --- | ---: |
| `ranking_formula_candidates` | 12 |
| `ranking_formula_sets` | 1 |
| `ranking_backtest_runs` | 0 |
| `ranking_backtest_results` | 0 |
| `ranking_backtest_candidate_summaries` | 0 |
| `ranking_formula_champions` | 0 |

No pending migrations were present before the write.

## Target Availability

`analytics_player_fantasy_points_by_profile` has 2025 target rows for all four scoring profiles and offensive positions.

| Profile | Season | QB | RB | WR | TE |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ppr` | 2025 | 664 | 1,578 | 2,500 | 1,301 |
| `half_ppr` | 2025 | 664 | 1,578 | 2,500 | 1,301 |
| `standard` | 2025 | 664 | 1,578 | 2,500 | 1,301 |
| `gng_keeper` | 2025 | 664 | 1,578 | 2,500 | 1,301 |

2025 is the only complete scoring-profile target season found for the four requested profiles.

## Source Feature Availability

The source feature season is 2024. `player_week_advanced_metrics` has a PPR-scoped offensive source lane, so the runner treats that source lane as scoring-profile-neutral feature input and evaluates profile-specific 2025 targets separately.

| Position | Source rows | Players |
| --- | ---: | ---: |
| QB | 697 | 79 |
| RB | 1,597 | 148 |
| WR | 2,542 | 235 |
| TE | 1,287 | 129 |

Feature classification for seeded formula fields:

| Feature | Status |
| --- | --- |
| `passing_success_rate` | available through `success_rate` |
| `cpoe` | available |
| `usage_volume` | available through `opportunities` |
| `rush_success_rate` | available through `success_rate` |
| `receiving_usage` | available through `targets` |
| `epa_per_play` | available through `epa_per_opportunity` |
| `success_rate` | available |
| `carries` | available |
| `targets` | available |
| `recent_points_avg` | missing in the 2024 source-profile join |
| `passing_epa_per_play` | missing from joined 2024 truth source |
| `dropbacks` | missing from joined 2024 truth source |
| `rushing_attempts` | missing from joined 2024 truth source |
| `team_epa_per_play` | missing |
| `goal_line_opportunities` | missing |
| `air_yards` | missing from joined 2024 truth source |
| `receiving_epa` | missing from joined 2024 truth source |
| `red_zone_targets` | missing |
| `receiving_yards` | missing from joined 2024 truth source |
| `team_pass_rate` | missing |
| `pigskin_context_score` | missing |

Missing features are recorded in `missing_flags_json`. They are not treated as zero.

## Implementation Summary

`src/ranking_formula_backtests.py` now supports:

- no-lookahead source and target separation
- source season, target season, target week-start, and target week-end CLI options
- all-profile and all-position execution
- seeded formula set loading from BigQuery
- profile-specific target fantasy points
- source and target player-id normalization for `gsis:` prefixes
- default-context handling for target rows with null `league_type_id` or `roster_format_id`
- result rows for `ranking_backtest_results`
- candidate summaries for `ranking_backtest_candidate_summaries`
- controlled writes only to `ranking_backtest_runs`, `ranking_backtest_results`, and `ranking_backtest_candidate_summaries`
- champion recommendations without active champion selection

Write mode remains fail-closed unless `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`.

## Dry Run

Command:

```powershell
.\venv\Scripts\python.exe -m src.ranking_formula_backtests --from-bigquery-candidates --formula-set-id ranking_formula_set_v0_2026_001 --source-season 2024 --target-season 2025 --target-week-start 1 --target-week-end 18 --all-scoring-profiles --all-positions --status draft --dry-run
```

Dry-run summary:

| Field | Value |
| --- | ---: |
| Backtest runs planned | 4 |
| Seeded candidates evaluated | 12 |
| Result-shaped rows | 19,140 |
| Summary-shaped rows | 48 |
| Champion recommendations | 16 |

Position input counts per scoring profile:

| Position | Input rows per profile |
| --- | ---: |
| QB | 294 |
| RB | 347 |
| WR | 575 |
| TE | 379 |

## Controlled Write

Gate behavior:

- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` was set only inside the write command process.
- The gate was removed in `finally`.
- Post-command environment state: unset.

Write command:

```powershell
.\venv\Scripts\python.exe -m src.ranking_formula_backtests --from-bigquery-candidates --formula-set-id ranking_formula_set_v0_2026_001 --source-season 2024 --target-season 2025 --target-week-start 1 --target-week-end 18 --all-scoring-profiles --all-positions --status draft --write
```

Write summary:

| Target table | Row count written |
| --- | ---: |
| `ranking_backtest_runs` | 4 |
| `ranking_backtest_results` | 19,140 |
| `ranking_backtest_candidate_summaries` | 48 |

Backtest run IDs:

- `ranking_backtest_v0_2024_to_2025_ppr`
- `ranking_backtest_v0_2024_to_2025_half_ppr`
- `ranking_backtest_v0_2024_to_2025_standard`
- `ranking_backtest_v0_2024_to_2025_gng_keeper`

## Warehouse State After Write

| Table | After row count |
| --- | ---: |
| `ranking_formula_candidates` | 12 |
| `ranking_formula_sets` | 1 |
| `ranking_backtest_runs` | 4 |
| `ranking_backtest_results` | 19,140 |
| `ranking_backtest_candidate_summaries` | 48 |
| `ranking_formula_champions` | 0 |

Result counts by profile and position:

| Profile | QB | RB | WR | TE |
| --- | ---: | ---: | ---: | ---: |
| `ppr` | 882 | 1,041 | 1,725 | 1,137 |
| `half_ppr` | 882 | 1,041 | 1,725 | 1,137 |
| `standard` | 882 | 1,041 | 1,725 | 1,137 |
| `gng_keeper` | 882 | 1,041 | 1,725 | 1,137 |

Each profile and position evaluated three seeded candidates.

## Metric Validity

Read-only quality checks:

| Check | Issue count |
| --- | ---: |
| Duplicate result grain | 0 |
| Invalid result score or win-rate ranges | 0 |
| Duplicate summary grain | 0 |
| Invalid summary metric ranges | 0 |

Focused validations:

- `ranking_backtest`: 3 passed, 0 failed
- `ranking_formula`: 6 passed, 0 failed

Broad `ranking` validation warning:

- `093_projection_rankings_rank_order.sql` failed with `bad_rank_rows=12`.
- This is an existing projection ranking validation outside the Phase 32.1 backtest tables. The new ranking formula and backtest validations passed.

## Champion Recommendations

Recommendations are advisory only. No rows were inserted into `ranking_formula_champions`.

| Profile | Position | Recommended candidate | Pairwise win rate | Captured points rate | Top-N hit rate | Missing input rate |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `ppr` | QB | `ranking_formula_qb_volume_v0_2026_001` | 0.5692 | 0.8307 | 0.7870 | 0.8000 |
| `ppr` | RB | `ranking_formula_rb_balanced_v0_2026_001` | 0.7452 | 1.0000 | 1.0000 | 0.4046 |
| `ppr` | WR | `ranking_formula_wr_volume_v0_2026_001` | 0.7024 | 0.9150 | 0.8611 | 0.6000 |
| `ppr` | TE | `ranking_formula_te_balanced_v0_2026_001` | 0.6973 | 0.8560 | 0.7731 | 0.8000 |
| `half_ppr` | QB | `ranking_formula_qb_volume_v0_2026_001` | 0.5696 | 0.8308 | 0.7870 | 0.8000 |
| `half_ppr` | RB | `ranking_formula_rb_balanced_v0_2026_001` | 0.7517 | 1.0000 | 1.0000 | 0.4046 |
| `half_ppr` | WR | `ranking_formula_wr_volume_v0_2026_001` | 0.6986 | 0.9150 | 0.8588 | 0.6000 |
| `half_ppr` | TE | `ranking_formula_te_balanced_v0_2026_001` | 0.6966 | 0.8483 | 0.7639 | 0.8000 |
| `standard` | QB | `ranking_formula_qb_volume_v0_2026_001` | 0.5696 | 0.8308 | 0.7870 | 0.8000 |
| `standard` | RB | `ranking_formula_rb_balanced_v0_2026_001` | 0.7516 | 1.0000 | 1.0000 | 0.4046 |
| `standard` | WR | `ranking_formula_wr_volume_v0_2026_001` | 0.6917 | 0.9140 | 0.8565 | 0.6000 |
| `standard` | TE | `ranking_formula_te_balanced_v0_2026_001` | 0.6875 | 0.8329 | 0.7639 | 0.8000 |
| `gng_keeper` | QB | `ranking_formula_qb_volume_v0_2026_001` | 0.5541 | 0.8121 | 0.7731 | 0.8000 |
| `gng_keeper` | RB | `ranking_formula_rb_balanced_v0_2026_001` | 0.7430 | 1.0000 | 1.0000 | 0.4046 |
| `gng_keeper` | WR | `ranking_formula_wr_volume_v0_2026_001` | 0.6963 | 0.9207 | 0.8588 | 0.6000 |
| `gng_keeper` | TE | `ranking_formula_te_balanced_v0_2026_001` | 0.6932 | 0.8304 | 0.7731 | 0.8000 |

Selection rule:

1. Highest `pairwise_win_rate`
2. Higher `actual_points_captured_rate`
3. Higher `top_n_hit_rate`
4. Lower `missing_input_rate`

## Production Rankings No-Change Confirmation

`analytics_pigskin_rankings` remains intact:

- Active preseason rows: 1,140
- PPR, Half PPR, Standard, and GNG Keeper all still have QB 45, RB 80, WR 100, TE 60
- Trey McBride remains TE rank 1 in all four profiles
- No ranking generation ran in this phase

## Pigskin Isolation

Searched:

- `app.py`
- `src/pigskin_context_tools.py`
- `src/pigskin_packet_guardrails.py`
- `src/pigskin_context_qa.py`

Terms:

- `ranking_formula`
- `ranking_backtest`
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE`
- `execute_bigquery_sql`

Result:

- No Pigskin-visible formula or backtest write tool was found.
- No arbitrary SQL path was added.
- No Streamlit request-time formula or backtest write path was added.

## Checks Run

Passed:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m py_compile src\ranking_formula_backtests.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests
.\venv\Scripts\python.exe -m unittest tests.test_seed_ranking_formula_candidates
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_formula
```

Full unit suite result:

- 683 tests passed

Migration result:

- No pending migrations

Safety checker:

- Passed

## Remaining Warnings

- Some seeded features remain unavailable in 2024 source data. This is recorded as missing input, not zero-filled.
- The 2024 advanced metric source lane is PPR-scoped, while target scoring is profile-specific. The current runner treats source advanced metrics as scoring-profile-neutral and evaluates the separate 2025 profile targets.
- Broad `ranking` validation still has an unrelated projection-ranking rank-order failure in `093_projection_rankings_rank_order.sql`.
- Champion recommendations are statistically thin for some positions because only one source-to-target season pair is currently available.

## Recommended Next Phase

Recommended next phase: **Phase 32.2 - Owner review and select champion formulas**.

Before activating champions, review the missing-input rates and decide whether to:

- accept v0 recommendations as first champion candidates
- improve feature mappings and rerun the backtest
- build a formula comparison dashboard before selection
