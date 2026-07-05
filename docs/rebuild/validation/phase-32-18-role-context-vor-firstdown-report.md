# Phase 32.18 Role Context, First-Down Proxy, Weighted Opportunity, and VOR Report

Final decision: FIRST DOWN PBP PROXIES READY, DEEP VOR BASELINE SENSITIVITY READY, RB WEIGHTED OPPORTUNITY DIAGNOSTIC READY, INJURY DEPTH SOURCES INSUFFICIENT, NO ROLE CONTEXT CANDIDATE BEATS BASELINE

## Scope

This report regenerates Phase 32.18 after the revised prompt added exact policy names and the explicit PPR-only RB weighted-opportunity diagnostic.

No production deploy, staging deploy, Pigskin chat, Gemini or LLM ranking generation, live Sleeper API call, live ranking regeneration, champion activation, global truncate, or detail-row tournament write occurred.

The earlier report `phase-32-18-role-context-vor-sensitivity-report.md` is superseded by this file because it used the older five-candidate scope and older VOR policy names.

## Git State

Before the addendum, implementation commit `db9023ccce25 Add first down proxy ranking diagnostics` existed and the historical validation backlog remained untracked.

Additional uncommitted files now belong to this addendum:

- `bigquery/migrations/0035__ranking_feature_mart_rb_weighted_opportunity.sql`
- `bigquery/validations/231_ranking_feature_mart_rb_weighted_opportunity.sql`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/validation/phase-32-18-role-context-vor-firstdown-report.md`
- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`

No unrelated historical validation backlog files were staged.

## Prompt Deltas Found

The revised prompt changed the completed work in four ways:

- It banned the earlier shorthand label for the deep replacement-baseline policy.
- It required exact VOR policy ids:
  - `current_sql_vorp_qb12_rb24_wr24_te12`
  - `deep_vorp_qb15_rb36_wr55_te12`
  - `middle_vorp_qb12_rb30_wr42_te12`
- It required an explicit PPR-only RB weighted-opportunity diagnostic:
  - `gemini31_rb_weighted_opportunity_ppr_v0`
- It requested the report filename:
  - `docs/rebuild/validation/phase-32-18-role-context-vor-firstdown-report.md`

The code, tests, scorecard, matrix, and persisted summary-only run were updated to match those changes.

## Injury and Depth Source Audit

| Source | Row count | Status |
|---|---:|---|
| `raw_nflverse_injuries` | 0 | Not usable for scoring |
| `raw_nflverse_depth_charts` | 0 | Not usable for scoring |

The source tables exist, but they contain no historical rows. Injury burden, missed-time risk, starter role, and depth competition were not fabricated. Existing feature mart fields remain missing-input diagnostics until the source lane is remediated.

## First-Down PBP Proxy Implementation

Migration `0034__first_down_pbp_proxy_features.sql` remains applied.

Derived PBP fields:

- `receiving_first_down_exp_pbp`
- `rushing_first_down_exp_pbp`
- `passing_first_down_exp_pbp`
- `high_value_first_down_opportunity_score`
- `receiving_chain_mover_score`
- `rushing_chain_mover_score`

Feature mart fields:

- `receiving_first_down_exp_pbp_3yr`
- `rushing_first_down_exp_pbp_3yr`
- `passing_first_down_exp_pbp_3yr`
- `high_value_first_down_opportunity_score_3yr`
- `receiving_chain_mover_score_3yr`
- `rushing_chain_mover_score_3yr`

These are first-down expectation proxies. They are not `1D/RR`, `TPRR`, `YPRR`, route share, or first-read share.

## RB Weighted Opportunity Implementation

Migration `0035__ranking_feature_mart_rb_weighted_opportunity.sql` was applied.

New feature mart fields:

- `red_zone_carries`
- `outside_red_zone_targets`
- `outside_red_zone_carries`
- `gemini31_rb_weighted_opportunity_ppr`

The explicit PPR formula is:

```text
weighted_opportunity =
  0.47 * outside_red_zone_carries
+ 1.28 * red_zone_carries
+ 1.54 * outside_red_zone_targets
+ 2.39 * red_zone_targets
```

Red zone is `yardline_100 <= 20` in the upstream opportunity lane. This diagnostic is PPR-only. It was not applied to Standard, Half PPR, or GNG Keeper.

## Feature Mart Refresh

After migration 0035, the PPR QB/RB/WR/TE feature mart slice was refreshed for target seasons 2017 through 2025.

| Target season | PPR rows | Weighted rows | RB weighted rows | RB weighted min | RB weighted max | RB weighted avg |
|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 4,541 | 4,541 | 1,147 | 0.1185 | 18.2447 | 7.5774 |
| 2018 | 4,277 | 4,277 | 1,069 | 0.0000 | 16.5503 | 7.9133 |
| 2019 | 4,393 | 4,393 | 1,173 | 0.0000 | 21.0167 | 7.6911 |
| 2020 | 4,635 | 4,635 | 1,199 | 0.0000 | 18.5670 | 7.3286 |
| 2021 | 4,949 | 4,949 | 1,237 | 0.0000 | 19.8210 | 7.3012 |
| 2022 | 4,858 | 4,858 | 1,248 | 0.0000 | 18.9206 | 7.5927 |
| 2023 | 4,799 | 4,799 | 1,254 | 0.1567 | 16.9106 | 7.1827 |
| 2024 | 9,836 | 9,836 | 2,552 | 0.0000 | 16.2256 | 7.2788 |
| 2025 | 3,382 | 3,382 | 732 | 0.4083 | 16.3441 | 7.6150 |

## Diagnostic Family

Backtest version:

- `ranking_backtest_sql_native_role_context_vor_firstdown_v0`

Candidate family:

- `role_context_vor_firstdown_v0`

Candidates:

| Candidate | Position | Purpose |
|---|---|---|
| `injury_depth_role_diagnostic_v0` | RB | Tests role-context missing-input behavior. |
| `first_down_pbp_proxy_diagnostic_v0` | WR | Tests first-down PBP proxy signal. |
| `deep_vorp_qb15_rb36_wr55_te12_diagnostic_v0` | QB | Marker candidate for VOR policy sensitivity, paired with read-only VOR SQL. |
| `gemini31_rb_weighted_opportunity_ppr_v0` | RB | Tests explicit PPR weighted-opportunity multipliers. |
| `rb_role_pbp_context_blend_v0` | RB | Blends current RB PBP signal with role context where populated. |
| `wr_chain_mover_context_blend_v0` | WR | Blends WR PBP first-down proxy with current WR context. |

Dry-run evidence:

| Slice | Candidate count | Estimated bytes |
|---|---:|---:|
| 2024 PPR | 6 | 14,219,506 |
| 2025 PPR | 6 | 5,020,013 |
| 2017-2025 PPR | 6 | 92,734,051 |
| VOR sensitivity, 2024-2025 PPR | 3 policies | 4,010,223 |

Controlled summary-only write:

| Item | Result |
|---|---|
| BigQuery job ID | `39e46dfc-9f1d-425a-9955-c8d79f378384` |
| Backtest run ID | `ranking_backtest_sql_native_role_context_vor_firstdown_v0_ppr` |
| Run rows | 1 |
| Candidate summary rows | 6 |
| Detail rows for this run | 0 |
| Write gate after run | unset |

## Results

2024 validation, PPR:

| Candidate | Position | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| `deep_vorp_qb15_rb36_wr55_te12_diagnostic_v0` | QB | 0.6924 | 0.5278 | 0.7649 | 0.0000 |
| `gemini31_rb_weighted_opportunity_ppr_v0` | RB | 0.7829 | 0.6227 | 0.7761 | 0.3707 |
| `injury_depth_role_diagnostic_v0` | RB | 0.7680 | 0.6389 | 0.7857 | 0.5000 |
| `rb_role_pbp_context_blend_v0` | RB | 0.7705 | 0.6343 | 0.7819 | 0.1263 |
| `first_down_pbp_proxy_diagnostic_v0` | WR | 0.7400 | 0.4444 | 0.6755 | 0.0020 |
| `wr_chain_mover_context_blend_v0` | WR | 0.7354 | 0.4468 | 0.6802 | 0.0626 |

2025 holdout, PPR:

| Candidate | Position | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| `deep_vorp_qb15_rb36_wr55_te12_diagnostic_v0` | QB | 0.6951 | 0.8380 | 0.8862 | 0.0000 |
| `gemini31_rb_weighted_opportunity_ppr_v0` | RB | 0.8183 | 1.0000 | 1.0000 | 0.3707 |
| `injury_depth_role_diagnostic_v0` | RB | 0.7943 | 1.0000 | 1.0000 | 0.5000 |
| `rb_role_pbp_context_blend_v0` | RB | 0.8146 | 1.0000 | 1.0000 | 0.1226 |
| `first_down_pbp_proxy_diagnostic_v0` | WR | 0.7489 | 0.8333 | 0.8891 | 0.0018 |
| `wr_chain_mover_context_blend_v0` | WR | 0.7441 | 0.8403 | 0.8984 | 0.0621 |

2017-2025 aggregate, PPR:

| Candidate | Position | Pairwise | Top-N | Captured points | Missing |
|---|---|---:|---:|---:|---:|
| `deep_vorp_qb15_rb36_wr55_te12_diagnostic_v0` | QB | 0.6923 | 0.5781 | 0.7909 | 0.0022 |
| `gemini31_rb_weighted_opportunity_ppr_v0` | RB | 0.7477 | 0.6226 | 0.7625 | 0.3708 |
| `injury_depth_role_diagnostic_v0` | RB | 0.7332 | 0.6321 | 0.7704 | 0.5000 |
| `rb_role_pbp_context_blend_v0` | RB | 0.7342 | 0.6210 | 0.7598 | 0.1366 |
| `first_down_pbp_proxy_diagnostic_v0` | WR | 0.7456 | 0.5181 | 0.7259 | 0.0098 |
| `wr_chain_mover_context_blend_v0` | WR | 0.7395 | 0.5133 | 0.7212 | 0.0716 |

## VOR Baseline Sensitivity

2024-2025 PPR:

| Policy | VOR captured | Top-24 hit | Top-50 hit | Top-100 hit | Pick-band regret | Pairwise |
|---|---:|---:|---:|---:|---:|---:|
| `current_sql_vorp_qb12_rb24_wr24_te12` | 0.6911 | 0.2095 | 0.3133 | 0.4371 | 4448.12 | 0.5737 |
| `middle_vorp_qb12_rb30_wr42_te12` | 0.6690 | 0.2095 | 0.3133 | 0.4371 | 7116.72 | 0.5737 |
| `deep_vorp_qb15_rb36_wr55_te12` | 0.6370 | 0.2095 | 0.3133 | 0.4371 | 10343.76 | 0.5737 |

The deep replacement baseline `QB15/RB36/WR55/TE12` did not improve the tested slice. It lowered VOR captured and increased pick-band regret. Stored VOR semantics were not changed.

## Interpretation

- Injury/depth data does not exist in usable historical form.
- Injury/depth role scoring did not improve any position because the source rows are absent.
- First-down PBP proxies are valid component inputs, but they did not beat current Pigskin on aggregate or pairwise.
- The deep replacement baseline did not change the production decision. It made the VOR sensitivity read worse.
- The explicit PPR RB weighted-opportunity diagnostic helped 2025 holdout, but the aggregate pairwise and captured-points results remain below the current Pigskin baseline.
- No Phase 32.18 candidate is worth owner-review challenger status yet.

## Validation

Checks run:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: pass
- `.\venv\Scripts\python.exe -m py_compile src\ranking_formula_backtests.py`: pass
- `.\venv\Scripts\python.exe -m compileall -q src scripts`: pass
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`: 100 tests, OK
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests tests.test_nflverse_ideal_stats`: 115 tests, OK
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: 231 validations discovered
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern pbp`: 8 passed, 0 failed
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_feature_mart`: 8 passed, 0 failed

Known warning from the earlier full ranking pattern remains:

- `093_projection_rankings_rank_order.sql` failed with `bad_rank_rows = 12`.
- The failure is outside the Phase 32.18 formula/feature mart changes.

## Safety Confirmation

- SQL-native summary evaluator used.
- Old Python full tournament path was not used.
- No Python player/candidate/week result-row builder was used for the official path.
- `ranking_backtest_results` detail rows written: 0.
- `ranking_formula_champions` rows: 0.
- `analytics_pigskin_rankings` active rows remained 1,140.
- No champion formula activated.
- No live ranking regenerated.
- No deployment.
- No Pigskin chat call.
- No Gemini or LLM ranking generation.
- No live Sleeper API call.
- No raw/source table exposure to Pigskin added.

## Recommendation

Do not promote any Phase 32.18 candidate. Keep first-down proxies and the explicit PPR RB weighted-opportunity feature as research inputs.

Recommended next phase:

- Phase 32.19: Direct NGS receiving/rushing ingest if source coverage is real.
- Phase 32.19: Current injury/depth source remediation.
- Phase 32.19: Narrow WR/TE first-down proxy refinement that preserves current Pigskin pairwise strength.
