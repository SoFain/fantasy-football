# Phase 23.3G Trade Score Materialization Policy Report

Date: 2026-06-18

## Final Decision

`MATERIALIZATION POLICY READY WITH WARNINGS`

The Trade Analyzer score v0 builder now has an explicit staging-review materialization policy. Future score writes will include only materializable rows by default. Diagnostic rows remain visible in dry-run output, but are excluded from the write set.

No score rows were written in this phase. `ALLOW_TRADE_SCORE_MATERIALIZATION` remained unset. No deployment, feature flag change, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, Firebase artifact creation, or production change was performed.

## Selected Policy

Policy version: `trade_score_v0_staging_review_policy`

A row is materializable only when all of the following are true:

- `position` is not `PICK`.
- `draft_pick_score_lane_pending` is not present.
- `model_run_id` is present.
- `stale_projection_context` is not present.
- `player_id` is present and is not an unresolved placeholder.
- `missing_player_id` is not present.
- `trade_score` is present and between 0 and 100.
- `confidence_score` is present.

Confidence below 70 does not block dry-run or staging-review eligibility in v0. It is surfaced as an explicit warning. No override was added in this phase.

## Code Changes

Updated `src/trade_player_scores.py`:

- Added `MATERIALIZATION_POLICY_VERSION` and `LOW_CONFIDENCE_THRESHOLD`.
- Added `is_materializable_trade_score_row(row)`.
- Added `materialization_exclusion_reasons(row)`.
- Added `build_materialization_policy_summary(rows)`.
- Updated `_materializable_score_rows(rows)` to use the full policy instead of pick-only filtering.
- Added policy diagnostics to the `build_trade_player_scores()` result.
- Preserved the existing bounded write path, but future writes now receive only policy-materializable rows.

Updated `tests/test_trade_player_scores.py`:

- Added policy eligibility coverage for projection-covered player rows.
- Added exclusion coverage for picks, missing model runs, stale projection context, and unresolved identity.
- Added summary coverage for exclusion counts and low-confidence warnings.
- Updated the write-path test to confirm only policy-materializable rows are staged.

## Local Checks

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass, 25 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 343 tests |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 of 11 |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 of 2 |

Safety checker confirmed:

- no Firebase artifacts
- no tracked secret files
- no detected secret content
- feature flags default off
- Pigskin `execute_bigquery_sql` absent
- app and `src` plus `scripts` compile

## Dry-Run Command

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v0_2025_001 --dry-run
```

No `--write` flag was passed.

## Dry-Run Summary

| Metric | Value |
| --- | ---: |
| source rows | 100 |
| score rows | 100 |
| materializable rows | 77 |
| excluded rows | 23 |
| excluded pick rows | 13 |
| written rows | 0 |
| dry-run | true |
| warehouse `trade_player_scores` row count after dry-run | 0 |

Exclusion reason counts are non-exclusive.

| Reason | Count |
| --- | ---: |
| `missing_model_run_id` | 23 |
| `pick_row` | 13 |
| `draft_pick_score_lane_pending` | 13 |
| `stale_projection_context` | 0 |
| `missing_identity` | 0 |
| `invalid_trade_score` | 0 |
| `missing_confidence_score` | 0 |

## Materializable Score Distribution

| Metric | Value |
| --- | ---: |
| rows | 77 |
| trade score min | 7.9352 |
| trade score max | 60.0659 |
| trade score avg | 33.2663 |
| confidence min | 28.66 |
| confidence max | 51.41 |
| confidence avg | 46.3644 |
| confidence >= 70 | 0 |
| low-confidence materializable rows | 77 |

Warning emitted:

`all_materializable_rows_below_confidence_70`

## Top Materializable Examples

| Rank | Player | Pos | Team | Trade score | Confidence |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | Bijan Robinson | RB | ATL | 60.0659 | 50.53 |
| 2 | Ja'Marr Chase | WR | CIN | 55.7722 | 49.35 |
| 3 | Jahmyr Gibbs | RB | DET | 55.3984 | 50.53 |
| 4 | Puka Nacua | WR | LAR | 54.3830 | 43.72 |
| 5 | Jaxon Smith-Njigba | WR | SEA | 53.3932 | 50.53 |
| 6 | De'Von Achane | RB | MIA | 51.7125 | 49.35 |
| 7 | Amon-Ra St. Brown | WR | DET | 51.6068 | 50.53 |
| 8 | Christian McCaffrey | RB | SF | 51.2452 | 50.53 |
| 9 | Drake Maye | QB | NE | 50.4203 | 43.66 |
| 10 | Ashton Jeanty | RB | LV | 49.2474 | 50.53 |

## Bottom Materializable Examples

| Rank | Player | Pos | Team | Trade score | Confidence |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | Chuba Hubbard | RB | CAR | 7.9352 | 47.02 |
| 2 | Bhayshul Tuten | RB | JAX | 10.6040 | 45.93 |
| 3 | David Montgomery | RB | HOU | 12.6693 | 49.41 |
| 4 | Marvin Harrison | WR | ARI | 14.5610 | 40.63 |
| 5 | Jaylen Waddle | WR | DEN | 15.2744 | 48.32 |
| 6 | Quentin Johnston | WR | LAC | 16.6338 | 44.96 |
| 7 | Bo Nix | QB | DEN | 17.0614 | 44.12 |
| 8 | Jalen Hurts | QB | PHI | 18.4702 | 42.20 |
| 9 | Christian Watson | WR | GB | 18.6211 | 41.24 |
| 10 | Brian Thomas | WR | JAX | 19.4932 | 45.42 |

## Materialization Recommendation

Bounded materialization is policy-safe for staging review only if explicitly authorized later with `ALLOW_TRADE_SCORE_MATERIALIZATION=true`.

It is not recommended for production use yet. The reason is confidence, not row safety: every materializable row is still below the v0 confidence threshold of 70. The next scoring iteration should reduce missing-data penalties where source coverage is known acceptable, improve position/team identity sanity, and define a clearer staging acceptance threshold.

## Remaining Warnings

- 23 diagnostic rows remain excluded due to missing model-run context.
- 13 of those excluded rows are draft-pick rows and remain pending a separate pick-score lane.
- 77 materializable rows are all low-confidence.
- The v0 score layer remains default-off and should stay staging-review-only until the confidence story improves.
