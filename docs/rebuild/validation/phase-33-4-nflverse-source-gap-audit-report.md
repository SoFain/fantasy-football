# Phase 33.4 nflverse Source-Gap Audit

Final decision: NFLVERSE SOURCE GAP AUDIT COMPLETE

## Scope

Phase 33.4 audited only the seven zero-coverage Standard BQML v2 fields deferred in Phase 33.3:

- `passing_epa_per_play`
- `red_zone_opportunities`
- `goal_line_opportunities`
- `receiving_yards`
- `receiving_epa`
- `red_zone_targets`
- `ngs_catch_over_expected_score_3yr`

No BQML model was trained. No BigQuery write, feature-mart refresh, live ranking write, champion activation, Gemini call, Pigskin chat, Sleeper API call, deploy, broad ingest, or materialization occurred.

Phase 33.3 was preserved before this audit in commit `edf43e9 phase 33.3 validate standard bqml v2 dataset`.

## Source Evidence

Read-only source and warehouse probes showed:

| Source | Evidence |
|---|---|
| `nflreadpy.load_player_stats` | Exposes `passing_epa`, `receiving_yards`, `receiving_epa`, `targets`, `target_share`, `air_yards_share`, and `wopr`. |
| `nflreadpy.load_pbp` | Exposes `yardline_100`, `play_type`, `epa`, `pass_attempt`, `rush_attempt`, `passer_player_id`, `receiver_player_id`, and `rusher_player_id`. |
| `nflreadpy.load_nextgen_stats:receiving` | Exposes `avg_separation`, `catch_percentage`, `avg_expected_yac`, and `avg_yac_above_expectation`; it does not expose expected catch percentage or catch-over-expected in the loaded lane. |
| `stg_player_week_stats` | `receiving_yards` and `targets` are populated for QB/RB/WR/TE. |
| `player_week_opportunity_metrics` | `receiving_yards` is populated, while red-zone and goal-line columns remain null. |
| `stg_play_player_events` | Has populated `yardline_100` and EPA event rows. Existing `red_zone_flag` and `inside_5_flag` are not populated. |
| `raw_nflverse_pbp` | Has yardline-derived red-zone and inside-five opportunity evidence. |
| `player_week_ngs_metrics` | Has NGS receiving efficiency rows for WR/TE, but expected catch and catch-over-expected fields have zero non-null rows. |

## Warehouse Probe Summary

Current Standard BQML v2 feature mart coverage remains zero for all seven audited fields:

| Position | Feature mart rows | Audited fields populated |
|---|---:|---:|
| QB | 4,646 | 0 |
| RB | 9,969 | 0 |
| WR | 15,988 | 0 |
| TE | 8,458 | 0 |

Recoverable event/source counts:

| Probe | Count |
|---|---:|
| `stg_play_player_events` passer EPA events, 2014-2025 | 242,829 |
| `stg_play_player_events` receiver EPA events, 2014-2025 | 219,876 |
| Raw PBP red-zone target events by `yardline_100 <= 20` | 29,600 |
| Raw PBP red-zone rush events by `yardline_100 <= 20` | 28,712 |
| Raw PBP inside-five rush events by `yardline_100 <= 5` | 8,916 |
| Staging red-zone target events by `yardline_100 <= 20` | 29,600 |
| Staging red-zone rusher events by `yardline_100 <= 20` | 29,386 |
| Staging inside-five rusher events by `yardline_100 <= 5` | 9,056 |

Flag caution:

- `red_zone_flag` and `inside_5_flag` both showed 0 true rows in the checked raw and staging tables.
- Red-zone and goal-line recovery should use `yardline_100` directly, with a clearly documented rule.

## Field Decisions

| Field | Classification | Decision |
|---|---|---|
| `passing_epa_per_play` | recoverable from existing warehouse and nflverse player stats | Defer to additive feature-mart patch. Source exists as weekly `passing_epa` and passer EPA events. |
| `receiving_yards` | recoverable from existing warehouse and nflverse player stats | Defer to additive feature-mart patch. Source is already populated in `stg_player_week_stats` and `player_week_opportunity_metrics`. |
| `receiving_epa` | recoverable from nflverse player stats and staging events | Defer to additive feature-mart patch. Source exists in weekly player stats and receiver EPA events. |
| `red_zone_targets` | recoverable from PBP yardline derivation | Defer to additive feature-mart patch using `yardline_100 <= 20`. Do not use the currently empty flags. |
| `red_zone_opportunities` | recoverable from PBP yardline derivation | Defer to additive feature-mart patch using target plus rusher opportunities and source-window bounds. |
| `goal_line_opportunities` | recoverable from PBP yardline derivation | Defer to additive feature-mart patch using `yardline_100 <= 5` unless owner approves a broader rule. |
| `ngs_catch_over_expected_score_3yr` | unavailable in current public loaded NGS lane | Keep deferred. Do not fabricate catch-over-expected from catch percentage, YAC, or expected YAC fields. |

## Training Impact

The Standard BQML v2 training dataset should remain on the Phase 33.3 predictor set:

- 41 Standard training predictors
- zero missing predictor columns
- zero duplicate grain rows
- zero leakage window rows

The six recoverable fields are feature-mart work, not blockers for first Standard BQML v2 training. `ngs_catch_over_expected_score_3yr` remains blocked until a real source field is added.

## Files Updated

- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/validation/phase-33-4-nflverse-source-gap-audit-report.md`

## Checks

Passed:

- `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract`: 18 tests passed.
- `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py`: passed.
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed.
- `git diff --check`: passed with line-ending warnings only.

No migrations or validation SQL were added, so migration list/dry-run checks were not required for this phase.

## Remaining Warnings

- Red-zone and goal-line features require an additive feature-mart patch and a leakage-safe rolling window before model use.
- `ngs_catch_over_expected_score_3yr` remains blocked by source availability.
- The Phase 17 through Phase 30 historical validation backlog remains untracked owner-review material and was not touched.

## Recommended Next Phase

Proceed with Standard-only BQML v2 training only if the owner accepts that the first model will exclude these seven zero-coverage fields. Separately plan an additive feature-mart patch for EPA, receiving yards, and yardline-derived red-zone/goal-line signals.
