# Phase 32.14 Stats02 Ideal Formulas Report

Final decision: **IDEAL STATS SHOW SIGNAL BUT NEED SECOND PASS**

## Scope

Phase 32.14 used Phase 32.13 ideal-stat columns from `ranking_backtest_feature_mart` to test position-specific, scoring-profile-aware Stats02 formula candidates through the SQL-native summary evaluator.

No deploy occurred. No live rankings were regenerated. No champion formula was activated. No Pigskin chat, Gemini, Sleeper API, or old Python full tournament path was used.

## Git State

Before Phase 32.14 implementation, Phase 32.13 work was uncommitted. It was preserved first:

- Commit: `345fcb3 phase 32.13 ingest nflverse ideal stats`
- Staged only Phase 32.13 files.
- Historical validation backlog files remained untracked.

Known unrelated local change during Phase 32.14:

- `AGENTS.md` was already modified and was not staged or edited for this phase.

Phase 32.14 commit:

- Not created in this phase. The implementation, docs, tests, and report remain unstaged for owner/package review.

## Files Changed

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/validation/phase-32-14-stats02-ideal-formulas-report.md`

## Feature Coverage

Read-only coverage query:

- Table: `ranking_backtest_feature_mart`
- Seasons: 2024 validation, 2025 holdout
- Profiles: `ppr`, `half_ppr`, `standard`, `gng_keeper`
- Positions: QB, RB, WR, TE
- Query job: `16d24a6d-b1c4-4b0b-9a75-88a0b1ddb1ac`
- Bytes processed: 2,910,437
- Slot ms: 313

Coverage summary:

| Position | 2024 usable ideal coverage | 2025 usable ideal coverage | Notes |
|---|---:|---:|---|
| QB | 100 percent for QB xFP, snap, rushing leverage, team environment, QB efficiency proxy | 100 percent | RB and receiving-role fields are position-irrelevant and null. |
| RB | 99.61 percent for xFP/snap ideal fields, 100 percent for RB opportunity and team environment | 100 percent | Red-zone and goal-line scores are present but min/max were 0. |
| WR | 99.65 to 99.75 percent for xFP/snap ideal fields, 100 percent for receiving role and team environment | 99.69 percent for xFP/snap ideal fields | Cleanest useful signal. |
| TE | 99.08 to 99.17 percent for xFP/snap ideal fields, 100 percent for receiving role and team environment | 99.23 percent for xFP/snap ideal fields | Useful, but rank correlation remains mixed. |

Deferred fields remain deferred:

- `injury_risk_score_3yr`
- `depth_chart_role_score_3yr`
- PBP ffopportunity pass/rush splits
- true route share, first-read share, YPRR, end-zone targets

## Formula Definitions

Candidate family: `stats02_ideal_v0`

Candidates:

- `stats02_qb_ideal_rushing_xfp_v0`
- `stats02_rb_ideal_high_value_xfp_v0`
- `stats02_wr_ideal_receiving_dominance_v0`
- `stats02_te_ideal_receiving_role_v0`
- `stats02_position_specific_ideal_v0`
- `stats02_position_specific_ideal_availability_multiplier_v0`

Normalization method:

- SQL-native bounded 0 to 100 feature scoring.
- Missing feature values remain null and reduce available weight.
- No missing ideal stats were zero-filled.

Profile weighting:

- PPR, Half PPR, Standard, and GNG Keeper weights are emitted into SQL as separate weight columns.
- The SQL evaluator selects `effective_weight` by `scoring_profile_id`.
- PPR weights lean more toward xFP share and receiving-role xFP for RB/WR/TE.
- Standard weights lean more toward red-zone, goal-line, team environment, and efficiency where supported.

Availability multiplier:

- Candidate: `stats02_position_specific_ideal_availability_multiplier_v0`
- Applied in BigQuery only.
- Formula shape: base score multiplied by a bounded snap/role stability factor.
- Result: helped some TE and WR slices, but did not improve the aggregate enough for champion consideration.

## SQL-Native Dry Run

Version: `ranking_backtest_sql_native_stats02_ideal_v0`

| Item | Value |
|---|---:|
| Candidate rows | 12 |
| Unique candidate IDs | 6 |
| Target seasons | 2017-2025 |
| Scoring profiles | 4 |
| Positions | 4 |
| Expected detail rows | 0 |
| Estimated bytes | 71,838,149 |

Dry-run passed after two SQL generation fixes:

- Projected profile-specific weight columns from `formula_weights`.
- Defined `effective_weight` in the official tournament summary SQL block.

## Controlled Summary Write

Authorization:

- Summary write used the existing `ALLOW_RANKING_FORMULA_BACKTEST_WRITE` gate through the write helper environment mapping.
- The process environment was verified unset after the run.

Write result:

- Write job ID: `f92d682a-b23d-4011-93a9-38367625cdbd`
- Run rows written: 4
- Summary rows written: 48
- Detail rows written: 0

Persisted profile summary:

| Profile | Run rows | Summary rows | Sample total | Avg top-N | Avg captured points | Avg missing |
|---|---:|---:|---:|---:|---:|---:|
| `gng_keeper` | 1 | 12 | 117,183 | 0.5192 | 0.6588 | 0.0115 |
| `half_ppr` | 1 | 12 | 117,183 | 0.5402 | 0.7219 | 0.0113 |
| `ppr` | 1 | 12 | 117,183 | 0.5481 | 0.7332 | 0.0118 |
| `standard` | 1 | 12 | 117,183 | 0.5300 | 0.7006 | 0.0101 |

Write boundaries verified:

- `ranking_backtest_results`: 0 Stats02 rows
- `ranking_formula_champions`: 0 active champions
- `analytics_pigskin_rankings_candidates`: 0 Stats02 rows
- `analytics_pigskin_rankings`: not targeted

## Results

Read-only comparison jobs:

- 2024 validation leaderboard: `2d22ba6f-0e12-49f4-a512-8b6b42e09172`
- 2025 holdout leaderboard: `197bbf26-b83d-452a-864a-3af8239305b2`
- 2017-2025 aggregate leaderboard: `0d52e7dd-14c7-4e42-a45d-f48b7db58779`
- Position/profile detail: `6ae7785c-fe00-41d1-8b69-714db9d53d53`, `4cb16767-f987-493f-baf5-2d2a1b5f4647`

2024 validation highlights:

- QB: Stats02 slightly beat current Pigskin on PPR, Half PPR, and Standard top-N, captured points, VOR, and NDCG.
- RB: current Pigskin remained better in PPR, Half PPR, and Standard. Stats02 was roughly tied in GNG Keeper top-N and slightly better on GNG Keeper VOR.
- WR: Stats02 beat current Pigskin in all four profiles on top-N, captured points, VOR, NDCG, and bust rate. Rank correlation was slightly weaker.
- TE: Stats02 improved top-N in all four profiles, but rank correlation was weaker than current Pigskin.

2025 holdout highlights:

- QB: Stats02 improved top-N slightly in several profiles, but captured points and VOR did not consistently improve.
- RB: Stats02 tied top-N at 1.0000 across profiles, but current Pigskin was generally stronger on rank correlation.
- WR: Stats02 improved top-N, captured points, VOR, and rank correlation across all four profiles.
- TE: Stats02 improved most top-N, captured points, VOR, rank correlation, NDCG, and bust-rate measures.

2017-2025 aggregate context:

- Current Pigskin family baseline remains stronger than `stats02_position_specific_ideal_v0` on broad top-N and captured points.
- `stats02_position_specific_ideal_v0`: top-N 0.5263, captured points 0.6952, VOR captured 0.5789, missing 0.0126.
- Current Pigskin baseline from the existing scorecard: top-N 0.5400, captured points 0.7123, VOR captured 0.5981, missing 0.0032.

## Owner-Review Recommendation

Do not activate a champion.

Stats02 should remain a challenger lane. It is most promising for WR and TE, but the aggregate position-specific candidate does not clear the owner-review threshold against current Pigskin. It does not beat baseline by 1.5 percentage points on primary draft utility, and the 2025 holdout strength is not broad enough across QB/RB.

## Weakest Gaps

- RB validation still favors current Pigskin, opportunity diagnostic, or scarcity-adjusted baselines.
- Red-zone and goal-line usage fields are present but weak in the current feature mart, often with zero-valued min/max in validation and holdout.
- Direct injury and depth scoring remain unavailable.
- PBP ffopportunity pass/rush splits are still missing.
- TE role improved, but route/participation quality remains the likely next ceiling.

## Scorecard And Matrix Updates

Updated:

- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

The scorecard records the Stats02 formulas, dry-run/write stats, persisted summary rows, validation and holdout read, and no-champion decision.

The matrix records which ideal stats are used, which showed signal, and which remain deferred or weak.

## Checks Run

Local checks:

- `.\venv\Scripts\python.exe -m py_compile src\ranking_formula_backtests.py`: PASS
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`: PASS, 90 tests
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: PASS
- `.\venv\Scripts\python.exe -m compileall -q src scripts`: PASS
- `.\venv\Scripts\python.exe -m unittest discover tests`: PASS, 753 tests
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: PASS, no pending migrations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: PASS

Focused BigQuery validations:

- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest`: PASS, 3 passed
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_formula`: PASS, 6 passed
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ideal`: PASS, 6 passed
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ffopportunity`: PASS, 2 passed

## Remaining Warnings

- The summary write succeeded, but the wrapper command emitted PowerShell parsing noise after the write. Follow-up read-backs verified the intended state: 4 runs, 48 summaries, 0 detail rows, and the write gate unset.
- `AGENTS.md` has an unrelated local modification and remains outside this phase package.
- Historical validation backlog files remain untracked.

## Recommended Next Phase

Phase 32.15 should be one of:

- Add PBP-level ffopportunity pass/rush.
- Add injury/depth role scoring.
- Run a fast second-pass Stats02 refinement only for WR and TE.
- Retrain BQML with ideal stats after the source gaps are understood.

Do not proceed to champion activation without owner review.
