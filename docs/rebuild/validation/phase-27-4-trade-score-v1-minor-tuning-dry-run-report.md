# Phase 27.4 Trade Score V1 Minor Tuning Dry-Run Report

## Final Decision

TRADE SCORE V1 READY FOR STAGING MATERIALIZATION WITH WARNINGS

The v1 tuning pass fixed the three narrow issues from Phase 27.3 without writing score rows. Role-source gaps are no longer universally punitive when usable alternate role context exists. Team-context mismatches are visible in `missing_flags_json` and `component_json.team_context`. Raw projection freshness gaps are visible again instead of being hidden by fallback `season` and `week` values.

Do not treat this as production approval. The next safe step is a separate, explicitly authorized bounded staging materialization for 2025 week 18 only.

## Scope

This phase changed local code, tests, and this report only. No deployment, production feature flag change, Cloud Run Job trigger, Scheduler job, ingestion, score materialization, LLM action, Pigskin prompt, scrape, Firebase artifact, authorization gate, or commit occurred.

## Files Changed

| File | Change |
| --- | --- |
| `src/trade_player_scores.py` | Added team-context source fields, team alias normalization, team mismatch warning output, raw projection freshness fields, and refined role-source gap status handling. |
| `tests/test_trade_player_scores.py` | Added focused v1 tests for team mismatch warnings, `LA` to `LAR` alias handling, role-source suppression, role penalties, QB route handling, and raw projection freshness warnings. |
| `docs/rebuild/validation/phase-27-4-trade-score-v1-minor-tuning-dry-run-report.md` | Added this dry-run evidence report. |

During the first CLI dry-run, the source query exposed two query-shape defects from the new fields: duplicated `projection_team` in the projection CTE and missing `fraud_team` pass-through in `fraud_match`. Both were fixed before the final dry-run.

## Safety State

All checked authorization gates were unset before and after the dry-run:

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Checks Run

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass, 36 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 363 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 of 11 |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 of 2 |

The full test suite prints mocked pipeline, load, and ranking logs from existing tests. This phase did not run live ingestion, materialization, Cloud Run Jobs, or LLM-backed actions.

## Team-Context Warning Behavior

The source query now carries team context from:

- `compat_trade_assets_current.team`
- `compat_trade_player_history.team`
- `analytics_player_fantasy_points_by_profile.team`
- `analytics_player_weekly_truth.team`
- `analytics_player_weekly_truth.current_team`
- `projection_rankings_current.team`
- `analytics_fraud_watch.team`
- `analytics_fraud_watch.current_team`

Known aliases are normalized before comparison. `LA` and `LAR` are treated as the same team. `JAC` and `JAX` are also normalized.

Dry-run result:

| Metric | Value |
| --- | ---: |
| `team_context_mismatch_warning` rows | 5 |
| Puka Nacua alias-only mismatch | no warning |
| A.J. Brown current-team versus history/projection mismatch | warning present |

Rows with team-context mismatch warnings:

| Player | Asset team | Score | Confidence | Notes |
| --- | --- | ---: | ---: | --- |
| Kenneth Walker | KC | 57.91 | 79.20 | Historical and projection context show SEA. |
| A.J. Brown | NE | 57.11 | 76.78 | History, fantasy, projection, and Fraud Watch team show PHI. Fraud current team supports NE. |
| Travis Etienne | NO | 46.45 | 79.53 | Historical and projection context show JAX. |
| Jaylen Waddle | DEN | 26.48 | 77.32 | Historical and projection context show MIA. |
| David Montgomery | HOU | 22.90 | 78.41 | Historical and projection context show DET. |

The warning is explainability metadata only. It does not block materialization by itself.

## Role-Source Gap Tuning

`role_source_gap` still appears in 100 rows because role-source flags still flow from the current source slice, but it is no longer a universal confidence penalty.

| Role decision | Rows | Penalty |
| --- | ---: | --- |
| `suppressed_due_to_alternate_context` | 68 | 0 |
| `warning_only` | 3 | 0 |
| `penalty` | 29 | 3 |

The model now stores the role decision under `component_json.confidence_breakdown.penalty_categories` with:

- `status`
- `alternate_context`
- `relevant_flags`

Examples:

| Player | Role status | Role penalty | Note |
| --- | --- | ---: | --- |
| Bijan Robinson | `suppressed_due_to_alternate_context` | 0 | Snap and usage context exists. |
| Ja'Marr Chase | `suppressed_due_to_alternate_context` | 0 | Target and snap context exists. |
| Puka Nacua | `suppressed_due_to_alternate_context` | 0 | `LA` team alias is normalized and role context exists. |
| Josh Allen | `suppressed_due_to_alternate_context` | 0 | QB routes are not treated as a core blocker when other role context exists. |
| Malik Nabers | `penalty` | 3 | No recent history, fantasy profile, or truth context in the target slice. |

This resolves the Phase 27.3 complaint that role gaps were too noisy. It does not pretend the source is complete.

## Projection Freshness Warning Behavior

The source query now preserves raw projection metadata:

- `projection_raw_as_of_season`
- `projection_raw_as_of_week`

It also keeps fallback effective values:

- `projection_as_of_season`
- `projection_as_of_week`

`source_freshness_json.sources.projection_rankings_current` now includes both raw and effective fields. If raw metadata is missing and a projection model run exists, v1 emits `projection_freshness_metadata_missing`.

Dry-run result:

| Metric | Value |
| --- | ---: |
| rows with raw projection freshness missing | 100 |
| rows with `projection_freshness_metadata_missing` | 77 |
| materialization blocker | no |

The count is 77 rather than 100 because only rows with attached projection context emit the warning. Rows without model-run context already carry materialization exclusions such as `missing_model_run_id`.

## Draft-Pick Preview Behavior

Draft picks remain diagnostic-only in the v1 dry-run.

| Metric | Value |
| --- | ---: |
| preview PICK rows | 13 |
| materializable PICK rows | 0 |
| excluded PICK rows | 13 |
| required pick flag | `draft_pick_score_lane_pending` present |

No `trade_pick_scores` object was created. The UI should continue to show score unavailable or market-only context for picks until a separate pick lane exists.

## Dry-Run Command

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v1_2025_001 --dry-run
```

Result:

| Metric | Value |
| --- | ---: |
| `dry_run` | true |
| `wrote` | false |
| `written_row_count` | 0 |
| source rows | 100 |
| score rows | 100 |
| materializable player rows | 77 |
| excluded rows | 23 |
| excluded pick rows | 13 |
| duplicate dry-run grain rows | 0 |
| score run id | `trade-score-trade_score_v1_2025_001-2025-w18-d688691f667a` |

No `--write` flag was passed.

## Tuned V1 Results

| Metric | Value |
| --- | ---: |
| trade score min | 15.93 |
| trade score max | 88.93 |
| trade score avg | 51.55 |
| trade score stddev | 15.53 |
| confidence min | 44.86 |
| confidence max | 79.53 |
| confidence avg | 68.18 |
| confidence stddev | 11.20 |
| source stability avg | 87.00 |
| risk adjustment avg | -2.75 |

Confidence buckets:

| Bucket | Rows |
| --- | ---: |
| `70-79` | 57 |
| `60-69` | 10 |
| `50-59` | 29 |
| `<50` | 4 |

Tier distribution:

| Tier | Rows |
| --- | ---: |
| elite | 1 |
| strong | 10 |
| starter | 15 |
| flex | 38 |
| depth | 31 |
| avoid | 5 |

Position distribution:

| Position | Rows |
| --- | ---: |
| QB | 13 |
| RB | 29 |
| WR | 36 |
| TE | 9 |
| PICK | 13 |

## Comparison Against Phase 27.2

| Metric | Phase 27.2 v1 | Tuned v1 |
| --- | ---: | ---: |
| source rows | 100 | 100 |
| score rows | 100 | 100 |
| materializable player rows | 77 | 77 |
| excluded rows | 23 | 23 |
| excluded pick rows | 13 | 13 |
| trade score min | 15.93 | 15.93 |
| trade score max | 88.93 | 88.93 |
| trade score avg | 51.55 | 51.55 |
| trade score stddev | 15.53 | 15.53 |
| confidence min | 46.86 | 44.86 |
| confidence max | 78.53 | 79.53 |
| confidence avg | 66.48 | 68.18 |
| confidence stddev | 9.95 | 11.20 |
| confidence >= 70 | 46 | 57 |
| confidence 60 to 69 | 21 | 10 |
| `role_source_gap` rows | 100 | 100 |
| role warning or suppressed rows | not separated | 71 |
| role penalty rows | 100 effectively punitive | 29 |
| projection freshness warnings | hidden | 77 |
| team-context mismatch warnings | absent | 5 |

Tier distribution stayed stable because this pass changed confidence and explainability, not the score formula.

## Player Sanity Examples

Top examples:

| Player | Pos | Team | Score | Confidence | Tier | Note |
| --- | --- | --- | ---: | ---: | --- | --- |
| Bijan Robinson | RB | ATL | 88.93 | 79.53 | elite | Role gap suppressed due alternate role context. |
| Ja'Marr Chase | WR | CIN | 83.35 | 78.35 | strong | Clean team context. |
| Puka Nacua | WR | LAR | 82.96 | 72.72 | strong | `LA` to `LAR` alias does not warn. |
| Jahmyr Gibbs | RB | DET | 81.91 | 79.53 | strong | Role gap suppressed. |
| Jaxon Smith-Njigba | WR | SEA | 79.88 | 79.53 | strong | Role gap suppressed. |
| Drake Maye | QB | NE | 77.74 | 68.66 | strong | One-QB QB context remains visible. |
| Josh Allen | QB | BUF | 74.86 | 67.97 | strong | QB routes are not a core blocker. |

Review examples:

| Player | Result |
| --- | --- |
| A.J. Brown | Score 57.11, confidence 76.78, team `NE`, warning `team_context_mismatch_warning`. Current team context supports NE while history, fantasy, projection, and Fraud Watch team show PHI. |
| Malik Nabers | Score 63.92, confidence 44.86, role penalty remains because recent history, fantasy profile, and truth context are missing. |
| Marvin Harrison | Score 23.50, confidence 69.63, no team mismatch. Low score still needs source review before treating it as true downside. |
| 2026 picks | Preview-scored but excluded from player materialization through `draft_pick_score_lane_pending`. |

High-market low-score rows with market score >= 85 and trade score < 45: none.

Low-market high-score rows with market score < 40 and trade score >= 70: none.

## Materialization Readiness

Decision: V1 is ready for a bounded staging materialization with warnings, if and only if a later phase explicitly sets `ALLOW_TRADE_SCORE_MATERIALIZATION=true` and writes only the bounded 2025 week 18 PPR redraft one-QB slice.

Reasons to proceed to staging review:

- Score shape remains sane.
- No score rows were written in this phase.
- Materializable rows exclude picks and missing model-run rows.
- Role-source penalties are no longer universal.
- Team-context mismatches and projection metadata gaps are now visible.

Warnings to carry forward:

- Projection raw `as_of_*` metadata is missing on the target source rows. It is visible now, but the source contract still needs cleanup.
- Five team-context mismatch rows need human review before public use.
- Malik Nabers and Marvin Harrison remain useful review cases for source coverage and calibration.
- Draft picks need a separate score lane.

## Recommended Next Phase

Run a separate Phase 27.5 bounded staging materialization only if explicitly authorized. That phase should:

- set `ALLOW_TRADE_SCORE_MATERIALIZATION=true` only inside the command process;
- materialize only `trade_score_v1_2025_001`, season 2025 week 18, PPR redraft one-QB;
- validate `trade_player_scores` and `compat_trade_player_scores`;
- keep production score flags false;
- use staging review only.
