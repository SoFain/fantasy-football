# Phase 32.31: Scoring-Profile-Specific 2026 Review Inputs

Final decision: **NON-PPR REVIEW INPUTS BLOCKED**

## Scope

This phase audited the 2026 owner-review input path after Phase 32.30 produced PPR-only review boards. It did not deploy, regenerate live rankings, activate champions, train BQML models, call Gemini, call Pigskin chat, call live Sleeper, write to `analytics_pigskin_rankings`, write to `ranking_formula_champions`, write to `ranking_backtest_results`, or globally truncate any table.

## Phase 32.30 Bookkeeping

Phase 32.30 files were uncommitted at the start of this phase. The scoped check passed with only Git LF-to-CRLF warnings, then the Phase 32.30 package was committed.

Commit: `91f0dda phase 32.30 generate ppr live review boards`

Committed files:

- `docs/rebuild/live-2026-ranking-review-boards.md`
- `docs/rebuild/validation/phase-32-30-live-2026-review-board-report.md`
- `docs/rebuild/formula-ranking-owner-review-index.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

## Candidate Universe Audit

`analytics_pigskin_rankings_candidates` currently contains one 2026 candidate slice.

| Season | Scoring profile | League | Roster | Candidate rows | Generated at |
|---:|---|---|---|---:|---|
| 2026 | `ppr` | `redraft` | `one_qb` | 936 | `2026-07-04 07:29:40.020998+00:00` |

Position shape:

| Scoring profile | Position | Candidate rows | Min rank | Max rank |
|---|---|---:|---:|---:|
| `ppr` | QB | 128 | 1 | 128 |
| `ppr` | RB | 202 | 1 | 202 |
| `ppr` | TE | 213 | 1 | 213 |
| `ppr` | WR | 393 | 1 | 393 |

Candidate ranking version:

| Scoring profile | Ranking version | Candidate rows |
|---|---|---:|
| `ppr` | `pigskin-20260704072940` | 936 |

There are no `standard`, `half_ppr`, or `gng_keeper` rows in `analytics_pigskin_rankings_candidates`.

## Why The Candidate Table Is PPR-Only

The source path is single-profile and table-replacing.

- `src/materialize.py` defines `build_pigskin_rankings_sql(..., scoring_profile_id="ppr", ...)`.
- That SQL uses `CREATE OR REPLACE TABLE analytics_pigskin_rankings_candidates`.
- `materialize_pigskin_rankings(...)` also defaults `scoring_profile_id="ppr"`.
- `src/generate_pigskin_rankings.py` defaults `DEFAULT_SCORING_PROFILE_ID` to `PIGSKIN_SCORING_PROFILE_ID` or `ppr`.

Result: the transient candidate table reflects the last materialized scoring profile. Right now that profile is PPR. It is not a multi-profile candidate store.

## Active Ranking Audit

Active final rankings exist for all four scoring profiles. These are valid live baselines, but they do not provide a safe non-PPR BQML review candidate universe by themselves.

| Profile | Position | Active rows | Rank range | Ranking version |
|---|---|---:|---|---|
| `standard` | QB | 45 | 1-45 | `pigskin-llm-20260704071412` |
| `standard` | RB | 80 | 1-80 | `pigskin-llm-20260704071412` |
| `standard` | TE | 60 | 1-60 | `pigskin-llm-20260704071412` |
| `standard` | WR | 100 | 1-100 | `pigskin-llm-20260704071412` |
| `half_ppr` | QB | 45 | 1-45 | `pigskin-llm-20260704070315` |
| `half_ppr` | RB | 80 | 1-80 | `pigskin-llm-20260704070315` |
| `half_ppr` | TE | 60 | 1-60 | `pigskin-llm-20260704070315` |
| `half_ppr` | WR | 100 | 1-100 | `pigskin-llm-20260704070315` |
| `ppr` | QB | 45 | 1-45 | `pigskin-llm-20260703061257` |
| `ppr` | RB | 80 | 1-80 | `pigskin-llm-20260703061257` |
| `ppr` | TE | 60 | 1-60 | `pigskin-llm-20260703061257` |
| `ppr` | WR | 100 | 1-100 | `pigskin-llm-20260703061257` |
| `gng_keeper` | QB | 45 | 1-45 | `pigskin-llm-20260704072119` |
| `gng_keeper` | RB | 80 | 1-80 | `pigskin-llm-20260704072119` |
| `gng_keeper` | TE | 60 | 1-60 | `pigskin-llm-20260704072119` |
| `gng_keeper` | WR | 100 | 1-100 | `pigskin-llm-20260704072119` |

Total active rows remain 1,140.

## Fantasy Point Availability

Fantasy point profiles exist and are active. The blocker is not scoring-profile availability. The blocker is the missing non-PPR 2026 candidate universe.

Recent profile row counts:

| Season | Profile | Weekly profile rows | Players | Week range |
|---:|---|---:|---:|---|
| 2025 | `standard` | 18,539 | 1,729 | 1-18 |
| 2025 | `half_ppr` | 18,539 | 1,729 | 1-18 |
| 2025 | `ppr` | 18,539 | 1,729 | 1-18 |
| 2025 | `gng_keeper` | 18,539 | 1,729 | 1-18 |
| 2024 | `standard` | 5,848 | 588 | 1-18 |
| 2024 | `half_ppr` | 5,848 | 588 | 1-18 |
| 2024 | `ppr` | 5,848 | 588 | 1-18 |
| 2024 | `gng_keeper` | 5,848 | 588 | 1-18 |

## Profile-Specific Input Classification

Review display order is Standard, Half PPR, PPR, then GNG Keeper. No PPR fallback is allowed.

| Scoring profile | Candidate rows | Active baseline rows | Status | Blocker |
|---|---:|---:|---|---|
| `standard` | 0 | 285 | blocked | No 2026 Standard candidate input in `analytics_pigskin_rankings_candidates`. |
| `half_ppr` | 0 | 285 | blocked | No 2026 Half PPR candidate input in `analytics_pigskin_rankings_candidates`. |
| `ppr` | 936 | 285 | ready with warnings | Phase 32.30 already generated PPR review boards. Missing feature rate remains high. |
| `gng_keeper` | 0 | 285 | blocked | No 2026 GNG Keeper candidate input in `analytics_pigskin_rankings_candidates`. |

Standard-first output is blocked. Building it from PPR candidates would silently fall back to PPR, which is explicitly disallowed.

## BQML Prediction Decision

No new `ML.PREDICT` job was run in Phase 32.31.

Reason: Phase 32.30 already generated PPR predictions from the only safe 2026 candidate input. Phase 32.31 found no safe non-PPR candidate input, so rerunning PPR would not answer the Standard-first requirement.

Phase 32.30 PPR prediction evidence remains the only generated 2026 review board:

- Review version: `phase32_30_live_2026_ppr_review_20260706`
- `ML.PREDICT` job ID: `3037784f-1163-47c6-9955-73543299a6f8`
- Bytes processed: `5,538,179`
- Required models run: `ranking_bqml_enriched_logistic_elite_v1`, `ranking_bqml_enriched_linear_points_v1`
- Optional context models run: `ranking_bqml_ngs_logistic_elite_v1`, `ranking_bqml_ngs_linear_points_v1`

## Profile Challenger Decision

Do not recommend one global winner averaged across all scoring systems. All-profile aggregate evidence is context only.

| Scoring profile | Best review-only challenger | Decision |
|---|---|---|
| `standard` | not selected | Blocked until Standard review input exists. |
| `half_ppr` | not selected | Blocked until Half PPR review input exists. |
| `ppr` | `ranking_bqml_enriched_logistic_elite_v1` | Owner-review only, not a champion. |
| `gng_keeper` | not selected | Blocked until GNG Keeper review input exists. |

## Warnings And Guardrails

- TE owner-review output remains capped at TE35. Live ranking tables still have TE60 per scoring profile and were not changed.
- PPR Phase 32.30 input had average missing feature rate of 77.9%.
- PPR Phase 32.30 Sleeper current team was null for 797 logistic-board rows after candidate ID joins to both `player_id` and `sleeper_player_id` style IDs. Nulls must display as unknown, not stale identity teams.
- `ranking_backtest_feature_mart` has 0 rows for `target_season=2026`, so 2026 review inputs must stay outcome-free and must not use target labels.
- `ranking_backtest_results` currently has 1,933,500 rows from prior research. Phase 32.31 did not write to it.
- `ranking_formula_champions` remains empty with 0 active champions.

## Read-Only Audit Jobs

| Check | Job ID | Bytes processed |
|---|---|---:|
| Candidate profile counts | `b08b6ddf-b48b-4f07-8b0c-6ef999ea3e6d` | 0 |
| Candidate 2026 position counts | `23888f07-695d-4168-9a4f-dbb4e24a340a` | 34,511 |
| Candidate versions | `38b6ef86-17e3-4153-8127-ef5eb0326d0a` | 42,120 |
| Active ranking profile-position counts | `f5823c0c-2689-4272-a101-86e618a5f50e` | 99,461 |
| Active ranking versions | `f7ffb086-100c-4e7f-8023-fc23db72ce6b` | 52,725 |
| Safety state counts | `e743cdbf-71d1-44d5-9da5-25c3a6a82a6e` | 0 |
| Fantasy profile availability | `b4e58e87-9271-47b8-b7d0-e150e6eefe93` | 11,274,824 |
| Profile readiness | `0cda8010-2c0c-41cf-9ce6-25fd4d2c60c5` | 68,265 |

## Checks

No source code changed. Focused docs validation:

- `git diff --check`

## Recommended Next Phase

Recommended next phase: **Phase 32.32 fill non-PPR candidate universe**.

The next implementation should create a review-only, outcome-free 2026 input path that can produce Standard, Half PPR, PPR, and GNG Keeper candidate slices without calling Gemini, writing live rankings, activating champions, or using PPR as fallback.

The formula comparison dashboard should wait until non-PPR inputs exist. Otherwise it will still be PPR-only decision evidence.
