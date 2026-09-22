# Phase 32.32: Non-PPR 2026 Review Candidate Universe

Final decision: **SCORING PROFILE REVIEW BOARDS READY WITH WARNINGS**

## Scope

This phase filled the missing non-PPR owner-review candidate universe with CTE-only SQL. It did not deploy, regenerate live rankings, activate champions, train BQML models, call Gemini, call Pigskin chat, call live Sleeper, write to `analytics_pigskin_rankings`, overwrite `analytics_pigskin_rankings_candidates`, write to `ranking_formula_champions`, write detail rows to `ranking_backtest_results`, or globally truncate any table.

## Files Changed

| File | Change |
|---|---|
| docs/rebuild/validation/phase-32-32-non-ppr-review-candidate-universe-report.md | Phase report and evidence. |
| docs/rebuild/live-2026-ranking-review-boards.md | Rebuilt with Standard, Half PPR, PPR, and GNG Keeper review boards. |
| docs/rebuild/formula-ranking-owner-review-index.md | Phase 32.32 owner-review status and next action. |
| docs/rebuild/ranking-algorithm-scorecard.md | Phase 32.32 scoring-profile review status. |
| docs/rebuild/ranking-opportunity-metrics-matrix.md | Profile-specific live review input coverage note. |

Commit hash before Phase 32.32 work: `ef99436 phase 32.31 audit scoring profile review inputs`.

## Git State

Before Phase 32.32 work, Phase 32.31 files were uncommitted. They were checked, staged explicitly, and committed as `ef99436 phase 32.31 audit scoring profile review inputs`.

After Phase 32.32 work, retained changes are docs-only:

- `docs/rebuild/validation/phase-32-32-non-ppr-review-candidate-universe-report.md`
- `docs/rebuild/live-2026-ranking-review-boards.md`
- `docs/rebuild/formula-ranking-owner-review-index.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

The temporary helper `scripts/phase32_32_review_boards_tmp.py` was removed after generation and is not part of the retained worktree.

## Candidate Generator Audit

`src/materialize.py` still owns the production candidate SQL. `build_pigskin_rankings_sql()` defaults `scoring_profile_id` to `ppr` and emits `CREATE OR REPLACE TABLE analytics_pigskin_rankings_candidates`. `materialize_pigskin_rankings()` passes that SQL through unchanged. `src/generate_pigskin_rankings.py` reads that transient table, defaults to PPR unless overridden, calls Gemini during generation, and writes active plus history ranking tables. None of those production paths were invoked.

For Phase 32.32, the `CREATE OR REPLACE TABLE` wrapper was removed in memory and the remaining `WITH ... SELECT` was used as a CTE. That produces the same candidate shape for a requested profile without replacing the production candidate table.

## Production Candidate Table State

Before review work:
| Profile | Position | Candidate rows | Version | Generated at |
|---|---|---|---|---|
| ppr | QB | 128 | pigskin-20260704072940 | 2026-07-04 07:29:40.020998+00:00 |
| ppr | RB | 202 | pigskin-20260704072940 | 2026-07-04 07:29:40.020998+00:00 |
| ppr | TE | 213 | pigskin-20260704072940 | 2026-07-04 07:29:40.020998+00:00 |
| ppr | WR | 393 | pigskin-20260704072940 | 2026-07-04 07:29:40.020998+00:00 |

After review work:
| Profile | Position | Candidate rows | Version | Generated at |
|---|---|---|---|---|
| ppr | QB | 128 | pigskin-20260704072940 | 2026-07-04 07:29:40.020998+00:00 |
| ppr | RB | 202 | pigskin-20260704072940 | 2026-07-04 07:29:40.020998+00:00 |
| ppr | TE | 213 | pigskin-20260704072940 | 2026-07-04 07:29:40.020998+00:00 |
| ppr | WR | 393 | pigskin-20260704072940 | 2026-07-04 07:29:40.020998+00:00 |

The production candidate table remained PPR-only and unchanged in row shape. This phase did not overwrite it.

## Review-Only Candidate Universe Method

The review universe is not persisted. It is built from per-profile candidate SELECT CTEs, joined to the latest compatible pre-2026 `ranking_backtest_feature_mart` predictor row where available, and joined to active current Pigskin rankings only as baseline display context. Sleeper current team is shown only from Sleeper current fields. Nulls remain unknown; no stale identity-team fallback is used.

Required exclusions were kept out of the model input: `target_fantasy_points`, actual ranks, VOR labels, elite labels, starter labels, pick-band labels, 2026 outcomes, and `pigskin_context_score`.

## Standard-First Result

Standard succeeded first. The Standard CTE generated QB128, RB202, WR393, and TE213 candidate rows, which clears the owner-review target shape of QB45, RB80, WR100, and TE35. Standard `ML.PREDICT` then succeeded before the remaining profiles were run.

Standard first smoke job: `2b0a88db-2d3f-43b3-80f7-c4cde27239a7`, bytes processed `109,430,633`, logistic predictions `936`, average missing feature rate `69.0%`.

## Profile-Specific Candidate Coverage

| Profile | Position | Candidates | Rank range | Missing ID | Missing score | Profile points missing | Grade missing |
|---|---|---|---|---|---|---|---|
| standard | QB | 128 | 1-128 | 0 | 0 | 43.0% | 43.0% |
| standard | RB | 202 | 1-202 | 0 | 0 | 40.6% | 40.6% |
| standard | TE | 213 | 1-213 | 0 | 0 | 42.7% | 42.7% |
| standard | WR | 393 | 1-393 | 0 | 0 | 49.1% | 49.1% |
| half_ppr | QB | 128 | 1-128 | 0 | 0 | 43.0% | 43.0% |
| half_ppr | RB | 202 | 1-202 | 0 | 0 | 40.6% | 40.6% |
| half_ppr | TE | 213 | 1-213 | 0 | 0 | 42.7% | 42.7% |
| half_ppr | WR | 393 | 1-393 | 0 | 0 | 49.1% | 49.1% |
| ppr | QB | 128 | 1-128 | 0 | 0 | 43.0% | 43.0% |
| ppr | RB | 202 | 1-202 | 0 | 0 | 40.6% | 40.6% |
| ppr | TE | 213 | 1-213 | 0 | 0 | 42.7% | 42.7% |
| ppr | WR | 393 | 1-393 | 0 | 0 | 49.1% | 49.1% |
| gng_keeper | QB | 128 | 1-128 | 0 | 0 | 43.0% | 43.0% |
| gng_keeper | RB | 202 | 1-202 | 0 | 0 | 40.6% | 40.6% |
| gng_keeper | TE | 213 | 1-213 | 0 | 0 | 42.7% | 42.7% |
| gng_keeper | WR | 393 | 1-393 | 0 | 0 | 49.1% | 49.1% |

## BQML Input Compatibility

Both required enriched models accepted the CTE-only review input for all four scoring profiles. Categorical predictors were supplied once as `scoring_profile_id` and `position`. Numeric predictors used the same coalesced value plus missing-flag shape as training. Labels were not supplied or required by `ML.PREDICT`.

| Profile | Step | Job ID | Bytes processed |
|---|---|---|---|
| standard | candidate_coverage | 003bb113-48a3-4eec-a7d8-7aab71bfa9d5 | 20874476 |
| standard | prediction_dry_run | dry_run | 109630689 |
| standard | prediction | 65cad6a4-65fe-4c20-b9da-2573526258c3 | 109630689 |
| half_ppr | candidate_coverage | 7c4ff546-5b65-47be-89f1-56de48fb0c62 | 20874476 |
| half_ppr | prediction_dry_run | dry_run | 109594823 |
| half_ppr | prediction | f4f51194-7580-4d3f-af3d-5392ef4685e3 | 109594823 |
| ppr | candidate_coverage | 20b87c2b-be62-4cbb-8896-c78b8c6f4987 | 20874476 |
| ppr | prediction_dry_run | dry_run | 109594823 |
| ppr | prediction | 189596b2-141f-477a-98b1-255e3cba1706 | 109594823 |
| gng_keeper | candidate_coverage | 879a5a6b-3e93-4a5a-baa5-ab2353ec901a | 20874476 |
| gng_keeper | prediction_dry_run | dry_run | 109594823 |
| gng_keeper | prediction | 46097431-50f9-48e0-88b4-0ac6278e772f | 109594823 |

## Model Summary

| Profile | Model | Predictions | Min | Max | Avg | Missing % | QBs in top 50 |
|---|---|---|---|---|---|---|---|
| standard | enriched_logistic | 936 | 4.13 | 99.79 | 18.19 | 69.0% | 7 |
| standard | enriched_linear_points | 936 | -23.10 | 849.07 | 67.54 | 69.0% | 0 |
| half_ppr | enriched_logistic | 936 | 4.11 | 99.79 | 18.27 | 69.0% | 6 |
| half_ppr | enriched_linear_points | 936 | -22.90 | 852.23 | 68.19 | 69.0% | 0 |
| ppr | enriched_logistic | 936 | 4.07 | 99.80 | 18.44 | 68.3% | 6 |
| ppr | enriched_linear_points | 936 | -22.81 | 855.78 | 68.86 | 68.3% | 0 |
| gng_keeper | enriched_logistic | 936 | 4.18 | 99.77 | 18.04 | 69.0% | 6 |
| gng_keeper | enriched_linear_points | 936 | -26.80 | 845.95 | 66.35 | 69.0% | 0 |

## Feature Missingness By Profile

| Profile | Family | Missing rate | Possible values |
|---|---|---|---|
| standard | baseline_candidate_proxies | 61.2% | 5616 |
| standard | ideal_xfp | 61.7% | 6552 |
| standard | pbp_first_downs | 69.6% | 14976 |
| standard | ngs_direct | 89.6% | 7488 |
| standard | injury_availability | 90.2% | 4680 |
| half_ppr | baseline_candidate_proxies | 61.2% | 5616 |
| half_ppr | ideal_xfp | 61.7% | 6552 |
| half_ppr | pbp_first_downs | 69.6% | 14976 |
| half_ppr | ngs_direct | 89.6% | 7488 |
| half_ppr | injury_availability | 90.2% | 4680 |
| ppr | baseline_candidate_proxies | 61.2% | 5616 |
| ppr | ideal_xfp | 61.7% | 6552 |
| ppr | pbp_first_downs | 69.6% | 14976 |
| ppr | ngs_direct | 89.6% | 7488 |
| ppr | injury_availability | 90.2% | 4680 |
| gng_keeper | baseline_candidate_proxies | 61.2% | 5616 |
| gng_keeper | ideal_xfp | 61.7% | 6552 |
| gng_keeper | pbp_first_downs | 69.6% | 14976 |
| gng_keeper | ngs_direct | 89.6% | 7488 |
| gng_keeper | injury_availability | 90.2% | 4680 |

## Scoring-Profile Decision Table

| scoring profile | board status | best challenger | decision |
|---|---|---|---|
| standard | ready with warnings | ranking_bqml_enriched_logistic_elite_v1 | Current Pigskin holds. Logistic is bounded owner-review challenger. Linear points is context only. |
| half_ppr | ready with warnings | ranking_bqml_enriched_logistic_elite_v1 | Current Pigskin holds. Logistic is bounded owner-review challenger. Linear points is context only. |
| ppr | ready with warnings | ranking_bqml_enriched_logistic_elite_v1 | Current Pigskin holds. Logistic is bounded owner-review challenger. Linear points is context only. |
| gng_keeper | ready with warnings | ranking_bqml_enriched_logistic_elite_v1 | Current Pigskin holds. Logistic is bounded owner-review challenger. Linear points is context only. |

No global winner was selected. All-profile aggregate remains context only. Current Pigskin should hold for every profile until an owner-approved champion-selection and live-ranking generation phase exists.

## Risk Notes

| Profile | Model | WR moves over 20 | Active moves over 20 | Null current teams | Injury-status rows | Top 100 from outside live depth |
|---|---|---|---|---|---|---|
| standard | enriched_logistic | 74 | 235 | 0 | 70 | 1 |
| standard | enriched_linear_points | 77 | 243 | 0 | 70 | 0 |
| half_ppr | enriched_logistic | 74 | 234 | 0 | 70 | 1 |
| half_ppr | enriched_linear_points | 72 | 245 | 0 | 70 | 0 |
| ppr | enriched_logistic | 67 | 222 | 0 | 70 | 1 |
| ppr | enriched_linear_points | 79 | 244 | 0 | 70 | 0 |
| gng_keeper | enriched_logistic | 75 | 230 | 0 | 70 | 1 |
| gng_keeper | enriched_linear_points | 85 | 243 | 0 | 70 | 0 |

Main warnings:

- Missing feature rates remain high for ideal, PBP, NGS, and injury families. This is owner-review evidence, not a promotion signal.
- Linear points has wide unbounded scores. It is useful context, but the bounded logistic board is the better owner-review challenger lane.
- Some model top-100 rows enter from outside active current Pigskin depth. They should be treated as review prompts, not rank changes.
- TE output is capped at TE35. TE6, TE12, and TE18 cutlines are still shown in the board file.

## No-Live-Change Confirmation

| Table | Row count |
|---|---|
| ranking_formula_champions_active | 0 |
| analytics_pigskin_rankings_active | 1140 |
| ranking_formula_champions | 0 |
| ranking_backtest_results | 1933500 |

`analytics_pigskin_rankings` remained at 1,140 active rows. `ranking_formula_champions` remained empty. Existing `ranking_backtest_results` rows were not changed by this phase.

## Checks Run

- Read-only candidate coverage SQL for Standard, Half PPR, PPR, and GNG Keeper.
- Read-only `ML.PREDICT` dry run and execution for each profile.
- Post-run read-only production candidate table count.
- `git diff --check` after docs were generated.

## Recommended Next Phase

Recommended next phase: **Phase 32.33 - Formula comparison dashboard in app, read-only**.

Alternate owner path: Phase 32.33 owner selection by scoring profile. Live ranking generation should wait for explicit owner approval.
