# Phase 34.2B RB Fable 01 Metric Build Report

## Final Decision

`RB FABLE 01 BACKTEST HARNESS READY`

The source-backed metric layer and leakage-safe fold preparation are ready. The next phase can evaluate RB Fable 01 against next-season Standard outcomes. Historical Current Pigskin and the named prior episode formula are unavailable, so those comparisons remain explicit warnings.

## Files Changed

- `bigquery/views/situational_identity_bridge_review.sql`
- `bigquery/views/v_rb_fable_01_situational_splits.sql`
- `bigquery/views/v_rb_fable_01_metric_inputs.sql`
- `bigquery/views/v_rb_fable_01_backtest_prep.sql`
- `scripts/build_rb_fable_01_metric_layer.py`
- `tests/test_rb_fable_01_metric_sql.py`
- `docs/rebuild/rb-fable-01-metric-contract.md`
- `docs/rebuild/rb-fable-01-backtest-harness.md`
- this report

## Metric Availability

All eleven formula inputs can be derived from source-backed data. Standard, non-garbage-time, red-zone, and stacked-box splits are available for 2022-2025. Regular-season games and birth date come from the existing NFLverse/basic identity layer. Standard next-season points are available for 2023-2025.

RB yards after contact is used only for `yac_per_rush`. Raw receiving `yac` is not used as YAC above expectation. Broken tackles and YAC above expectation are absent. Market and subjective ranking fields are absent.

Box-adjusted YPC uses a source-backed eight-plus-box YPC when the split has at least 20 carries. Fallback rows use a within-season YPC residual against average box defenders. Counts by season:

| Season | Qualified | Stacked-box method | Residual method |
|---:|---:|---:|---:|
| 2022 | 101 | 58 | 43 |
| 2023 | 101 | 60 | 41 |
| 2024 | 99 | 61 | 38 |
| 2025 | 94 | 62 | 32 |

## Identity Status

| Status | RB identities | Collisions |
|---|---:|---:|
| `EXACT_SLUG_MATCH` | 231 | 0 |
| `NAME_TEAM_SEASON_MATCH` | 3 | 0 |
| `UNMAPPED` | 2 | 0 |

Only collision-free exact or high-confidence name-team-season matches enter the metric layer. Unmapped players remain excluded. No source-local situational ID was treated as an official ID.

## Derived Metrics And Formula Status

The views create all specified per-game touch fields, YAC per rush, EPA per touch, actual/expected/blended TD rates, age penalty, availability rate, and box-adjusted YPC. Z-scores are partitioned by input season. All five efficiency components apply `n / (n + 125)` shrinkage using the required carry, touch, or box sample.

The formula score is implemented in `v_rb_fable_01_backtest_prep`. It is a research score only. No rank is written.

## Backtest Eligibility

| Fold | Qualified inputs | Target available | Complete score and target |
|---|---:|---:|---:|
| 2022 to 2023 | 101 | 72 | 66 |
| 2023 to 2024 | 101 | 75 | 73 |
| 2024 to 2025 | 99 | 67 | 65 |

Leakage checks found zero wrong-fold rows, zero input seasons outside 2022-2024, and zero target seasons outside 2023-2025.

## Missingness And Blockers

Opportunity and efficiency metrics are complete in the qualified metric layer. Missing red-zone count splits leave the blended TD component null for 10 rows in 2022, five in 2023, and eight in 2024. Age is missing for one row in 2022 and one in 2023. These rows remain visible but do not receive a complete score.

Historical Current Pigskin Standard rankings are unavailable for 2023-2025. The active rankings table contains only the current 2026 board. The prep view records this as `UNAVAILABLE_HISTORICAL_BASELINE`. It does not use current rankings as a historical proxy. The prior formula `standard_rb_elite_receiving_back_protection_v0` is not registered in `ranking_formula_candidates`.

These warnings do not block direct outcome evaluation in Phase 34.3. They do block the two requested baseline comparisons until valid historical evidence is supplied.

## Checks

- Metric-layer script compile: pass.
- Four focused SQL contract tests: pass.
- Template dry-run: pass.
- Four BigQuery research views created: pass.
- Identity status and collision query: pass.
- Metric availability and missingness query: pass.
- Fold eligibility query: pass.
- No-leakage query: pass.
- No invented metrics test: pass.
- `scripts/import_situational_advanced_metrics.py` and `scripts/build_rb_fable_01_metric_layer.py` compile: pass.
- `scripts/check_deployment_safety.py`: all checks passed.
- `scripts/run_bigquery_validations.py --dry-run`: discovery passed through validation 245.
- Deployed view-definition audit: no 2026, market-value, broken-tackle, or YAC-above-expectation references.
- `git diff --check`: pass. Existing line-ending warnings are informational.

## Safety Confirmation

- No live ranking was generated or written.
- No champion was activated.
- No model was trained.
- No deployment occurred.
- No Gemini or Pigskin chat call occurred.
- No market target or 2026 outcome was used.
- Existing ranking and feature-mart tables were not changed.

## Recommended Next Phase

`Phase 34.3 - Backtest RB Fable 01`. The evaluator should run read-only over `v_rb_fable_01_backtest_prep`, calculate the requested fold and aggregate metrics, and keep unavailable baseline comparisons labeled as unavailable.
