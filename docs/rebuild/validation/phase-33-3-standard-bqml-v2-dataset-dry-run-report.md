# Phase 33.3 Standard BQML V2 Dataset Dry Run Report

Final decision: STANDARD BQML V2 DATASET READY WITH WARNINGS

## Scope

Phase 33.3 used the Phase 33.2 BQML v2 feature contract to validate the Standard-only training dataset shape before any BQML model training.

No model was trained. No BigQuery ML model was created. No live ranking table changed. No champion was activated. No Gemini, Pigskin chat, Sleeper API, source ingest, materialization, deployment, or write path was used.

## Phase 33.2 Commit Result

Phase 33.2 was committed first as required:

- `88963a3 phase 33.2 add bqml v2 feature contract`

Committed Phase 33.2 files:

- `src/bqml_v2_feature_contract.py`
- `tests/test_bqml_v2_feature_contract.py`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/validation/phase-33-2-bqml-v2-feature-contract-report.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

The historical validation backlog remained untracked and unstaged.

## Files Changed In Phase 33.3

| File | Change |
|---|---|
| `src/bqml_v2_feature_contract.py` | Added Standard readiness thresholds, integrity query, bounded sample query, model SQL template builder, and Standard training predictor deferral for zero-coverage fields. |
| `tests/test_bqml_v2_feature_contract.py` | Added tests for integrity query, bounded sample query, model templates, readiness thresholds, and deferred zero-coverage predictors. |
| `docs/rebuild/bqml-v2-ranking-architecture.md` | Added Standard dataset readiness result and training-template policy. |
| `docs/rebuild/ranking-algorithm-scorecard.md` | Added Phase 33.3 readiness evidence. |
| `docs/rebuild/ranking-opportunity-metrics-matrix.md` | Added Phase 33.3 coverage and deferred-field status. |
| `docs/rebuild/validation/phase-33-3-standard-bqml-v2-dataset-dry-run-report.md` | Added this report. |

Phase 33.3 changes are not committed in this report.

## Git State

Before Phase 33.3 work:

- Phase 33.2 files were modified or untracked.
- Historical validation backlog files remained untracked.

After Phase 33.2 preservation:

- Phase 33.2 package committed as `88963a3`.

After Phase 33.3:

- Phase 33.3 files are modified or untracked for owner review.
- Historical validation backlog remains untracked.
- No unrelated historical backlog files were staged.

## Dataset SQL Inspection

Dataset version:

- `bqml_v2_standard_training_dataset_v0`

Confirmed included:

- `scoring_profile_id = 'standard'`
- target seasons 2017 through 2025
- QB, RB, WR, TE
- split labels: train 2017-2023, validation 2024, holdout 2025
- `source_window_start_season`
- `source_window_end_season`
- `source_window_end_season < target_season`
- `league_type_id`
- `roster_format_id`
- `player_id_internal`
- `position`
- Standard training predictors only
- labels separated from predictors
- missing flags

Confirmed excluded from predictors:

- `target_fantasy_points`
- `value_over_replacement`
- `actual_position_rank`
- `actual_overall_rank`
- `replacement_points`
- pick-band outcomes
- 2026 outcomes
- Sleeper current context
- `pigskin_context_score`
- blocked route metrics
- `depth_chart_role_score_3yr`

## Column Existence And Type Audit

Allowed Standard training predictors:

- Count: 41
- Missing columns: 0
- Type count: 41 `FLOAT`

Zero-coverage fields deferred from the initial Standard training dataset:

| Field | Reason |
|---|---|
| `passing_epa_per_play` | 0 Standard non-null rows in the Phase 33.3 audit. |
| `red_zone_opportunities` | 0 Standard non-null rows in the Phase 33.3 audit. |
| `goal_line_opportunities` | 0 Standard non-null rows in the Phase 33.3 audit. |
| `receiving_yards` | 0 Standard non-null rows in the Phase 33.3 audit. |
| `receiving_epa` | 0 Standard non-null rows in the Phase 33.3 audit. |
| `red_zone_targets` | 0 Standard non-null rows in the Phase 33.3 audit. |
| `ngs_catch_over_expected_score_3yr` | 0 Standard non-null rows in the Phase 33.3 audit. |

These fields remain future-eligible in the broader source-backed allowlist, but the Standard training SQL and model templates do not use them until coverage exists.

## Dry-Run Bytes

| Query | Estimated bytes |
|---|---:|
| Standard training dataset | 1,201,855,586 |
| Standard coverage aggregation | 26,143,117 |

The training-query estimate matches the Phase 33.2 order of magnitude.

## Aggregate Row Counts

Rows by split:

| Split | Rows |
|---|---:|
| train | 32,452 |
| validation | 4,918 |
| holdout | 1,691 |

Rows by target season:

| Season | Rows |
|---|---:|
| 2017 | 4,541 |
| 2018 | 4,277 |
| 2019 | 4,393 |
| 2020 | 4,635 |
| 2021 | 4,949 |
| 2022 | 4,858 |
| 2023 | 4,799 |
| 2024 | 4,918 |
| 2025 | 1,691 |

Rows by position:

| Position | Rows |
|---|---:|
| QB | 4,646 |
| RB | 9,969 |
| WR | 15,988 |
| TE | 8,458 |

Rows by league and roster:

| League / roster | Rows |
|---|---:|
| `redraft/one_qb` | 39,061 |

Integrity counts:

| Check | Count |
|---|---:|
| Duplicate grain rows | 0 |
| Missing player IDs | 0 |
| Missing scoring profiles | 0 |
| Missing target labels | 0 |
| Leakage window rows | 0 |

Source-gap probe:

| Field group | Non-null rows |
|---|---:|
| `depth_chart_role_score_3yr` | 0 |
| `injury_risk_score_3yr` | 0 |

## Sample Validation

The bounded sample query returned 5 QB, 5 RB, 5 WR, and 5 TE rows. Sample rows carried:

- identifiers
- split
- target season
- source window
- selected predictor examples
- label examples
- missing flags

Representative sample names:

| Position | Sample players |
|---|---|
| QB | Aaron Rodgers, Joe Flacco, Josh Johnson, Matthew Stafford, Kirk Cousins |
| RB | Ameer Abdullah, Derrick Henry, Christian McCaffrey, Samaje Perine, Dare Ogunbowale |
| WR | Adam Thielen, Keenan Allen, DeAndre Hopkins, Mike Evans, Stefon Diggs |
| TE | Travis Kelce, Chris Manhertz, Austin Hooper, Hunter Henry, Tyler Higbee |

The sample query was bounded by `ROW_NUMBER() OVER (PARTITION BY position)` with a limit of 5 per position.

## Leakage Checks

Passed:

- every dataset row enforces `source_window_end_season < target_season`
- no target fantasy points in predictor lists
- no VOR in predictor lists
- no actual ranks in predictor lists
- no blocked route metrics in the Standard training SQL
- no Sleeper current context in the Standard training SQL
- no `pigskin_context_score`
- no `depth_chart_role_score_3yr`
- no 2026 outcomes

## Missingness And Readiness Thresholds

Thresholds used:

| Feature family | Threshold |
|---|---:|
| Baseline Pigskin proxies | 95% |
| Opportunity | 95% |
| Ideal xFP | 90% |
| PBP xFP | 90% |
| First-down proxies | 90% |
| NGS | 70% |
| Role history | 90% |

Injury and depth are not required for the first Standard v2 training dataset.

Feature-family coverage:

| Family | Populated rows | Possible rows |
|---|---:|---:|
| Baseline | 39,033 | 39,061 |
| Opportunity | 39,061 | 39,061 |
| Ideal xFP | 38,321 | 39,061 |
| PBP xFP | 38,321 | 39,061 |
| First-down proxy | 38,321 | 39,061 |
| NGS | 32,436 | 39,061 |
| Role history | 38,650 | 39,061 |

## Readiness By Position

| Position | Predictor count | Minimum feature coverage | Status |
|---|---:|---:|---|
| QB | 11 | 96.3% | ready |
| RB | 19 | 62.0% | ready with warnings |
| WR | 19 | 77.0% | ready with warnings |
| TE | 23 | 71.9% | ready with warnings |

Warning details:

| Position | Low-coverage features |
|---|---|
| RB | `target_share_slope_3yr`, `carry_share_slope_3yr`, `ngs_box_resilience_score_3yr`, `ngs_rushing_efficiency_score_3yr`, `ngs_rush_yards_over_expected_score_3yr` |
| WR | `wopr_slope_3yr`, `target_share_slope_3yr`, `ngs_receiving_efficiency_score_3yr`, `ngs_separation_score_3yr`, `ngs_yac_over_expected_score_3yr` |
| TE | `wopr_slope_3yr`, `target_share_slope_3yr`, `ngs_receiving_efficiency_score_3yr`, `ngs_separation_score_3yr`, `ngs_yac_over_expected_score_3yr` |

## Model SQL Templates Prepared

Prepared but not executed:

- Standard QB linear points
- Standard QB linear VOR
- Standard QB logistic elite
- Standard QB logistic bust
- Standard RB linear points
- Standard RB linear VOR
- Standard RB logistic elite
- Standard RB logistic bust
- Standard WR linear points
- Standard WR linear VOR
- Standard WR logistic elite
- Standard WR logistic bust
- Standard TE linear points
- Standard TE linear VOR
- Standard TE logistic elite
- Standard TE logistic bust

Template policy:

- model suffix: `bqml_v2_standard_v0`
- `LINEAR_REG` for points and VOR
- `LOGISTIC_REG` for elite and bust
- `data_split_method = 'NO_SPLIT'`
- train rows only for model creation
- validation and holdout rows reserved for later prediction and evaluation
- no 2025 holdout tuning
- no boosted tree templates in this phase

## Checks Run

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract` | Pass, 18 tests |
| BigQuery Standard training dataset dry-run | Pass |
| BigQuery Standard coverage aggregation | Pass |
| BigQuery Standard integrity query | Pass |
| BigQuery bounded sample query | Pass |

Final local checks are recorded after this report in the phase closeout.

## No-Change Confirmation

- No BQML models trained.
- No BigQuery ML models created.
- No live rankings changed.
- No champion activated.
- No writes to `analytics_pigskin_rankings`.
- No writes to `analytics_pigskin_rankings_candidates`.
- No writes to `ranking_formula_champions`.
- No writes to `ranking_backtest_results`.
- No Gemini call.
- No Pigskin chat call.
- No Sleeper API call.
- No source ingest.
- No deployment.

## Warnings

- RB, WR, and TE are ready with warnings because selected NGS and role-history fields sit below 90 percent coverage.
- Seven zero-coverage fields were deferred from the initial Standard training query.
- Legacy injury and historical depth remain excluded.
- The Standard training dry-run estimate is 1.20 GB.
- Phase 33.3 changes are not committed in this report.

## Recommended Next Phase

Phase 33.4: Standard-only BQML v2 linear/logistic training, only if the owner accepts:

- the 1.20 GB training-query dry-run estimate
- warning-level NGS and role-history coverage
- zero-coverage field deferral
- no injury/depth predictors in the first Standard v2 training run
