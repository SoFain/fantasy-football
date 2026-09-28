# Phase 33.9 Standard BQML V2 Original vs Patched Owner-Review Report

Final decision: STANDARD OVERALL BOARD RULE NEEDED

## Scope

Phase 33.9 compared the original 41-predictor Standard BQML v2 model set against the patched 47-predictor Standard BQML v2 model set at the owner-review board level.

This phase did not train models, create BQML models, deploy, write live rankings, activate champions, call Gemini, call Pigskin chat, call Sleeper, run source ingest, write `ranking_backtest_results`, write `analytics_pigskin_rankings`, overwrite `analytics_pigskin_rankings_candidates`, or write `ranking_formula_champions`.

## Git State

Phase 33.8 was already committed before this phase:

- `f4517ef phase 33.8 retrain patched standard bqml v2`

Remaining untracked files before and after this phase were the known historical validation backlog and owner-review artifacts. Generated evidence was kept under `output/` and not staged.

## Evidence Verification

Read-only BigQuery checks:

| Check | Rows |
|---|---:|
| Original Standard v2 `ranking_backtest_runs` | 2 |
| Original Standard v2 `ranking_backtest_candidate_summaries` | 32 |
| Original Standard v2 `ranking_backtest_results` | 0 |
| Patched Standard v2 `ranking_backtest_runs` | 2 |
| Patched Standard v2 `ranking_backtest_candidate_summaries` | 32 |
| Patched Standard v2 `ranking_backtest_results` | 0 |
| `ranking_formula_champions` | 0 |
| Patched formula rows in `analytics_pigskin_rankings` | 0 |

Generated local evidence:

- `output/phase-33-9-original-vs-patched-evidence.md`
- Prediction rows read: 5,778
- Board metric rows: 46
- Cutline rows: 96
- Movement sections: 24

The generated evidence file is local only and should not be committed.

## Summary Metric Decision

Persisted summary evidence remains the main decision source. The generated boards are useful for movement checks, but the 2025 board slice is thin or rank-collapsed for several positions.

| Position | Finalist | Label | Rationale |
|---|---|---|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | original Standard v2 finalist | Original still leads the 2025 holdout on top-N, captured points, VOR, and NDCG. Patched QB adds `passing_epa_per_play`, but the board remains noisy and does not improve enough. |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | original Standard v2 finalist | Patched logistic elite improves 2024 top-N and points, but original bust inverse keeps stronger 2024 VOR/NDCG and the 2025 RB VOR denominator is not usable. |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` | original Standard v2 finalist | Patched bust inverse improves 2025 points/VOR, but original logistic elite retains 2025 top-N/NDCG and stronger 2024 VOR/NDCG. |
| TE | `bqml_v2_standard_te_logistic_bust_inverse_v0` | original Standard v2 finalist, with patched as component signal | Patched bust inverse improves 2025, but original TE linear points still wins 2024. Original bust inverse remains the safer review finalist because the earlier TE owner-review cut preferred risk-aware output over linear-only output. |

## Original vs Patched Side-by-Side Reads

| Slice | Best patched read | Counterweight |
|---|---|---|
| 2024 QB | Patched linear points slightly improved points and VOR. | Original retained top-N and NDCG edge. |
| 2024 RB | Patched logistic elite top-N 0.644 and points 0.797. | Original bust inverse had VOR 0.736 and NDCG 0.730. |
| 2024 WR | Patched linear points led top-N and points. | Original logistic elite retained VOR and NDCG edge. |
| 2024 TE | No patched winner. | Original TE linear points led top-N, points, VOR, and NDCG. |
| 2025 QB | No patched winner. | Original logistic bust inverse led top-N 0.852, points 0.890, VOR 0.851, NDCG 0.832. |
| 2025 RB | All reviewed lanes tied on top-N/points in the generated board slice. | Original linear points retained the best summary NDCG. |
| 2025 WR | Patched bust inverse led points 0.888 and VOR 0.888. | Original logistic elite retained top-N and NDCG. |
| 2025 TE | Patched bust inverse led top-N 0.764, points 0.848, VOR 0.843, NDCG 0.712. | 2024 still favors original TE linear points. |

## Board Generation Method

The board query:

- Used existing original and patched Standard BQML v2 models.
- Used read-only `ML.PREDICT`.
- Joined actual ranks back from `ranking_backtest_feature_mart` after prediction. Actual ranks were not used as predictors.
- Built Standard-only 2024 validation and 2025 holdout position boards.
- Capped position output at QB45, RB80, WR100, TE35.
- Included a deterministic Current Pigskin proxy from `ranking_backtest_feature_mart`.

No provisional production overall board was created. That rule does not exist yet.

## Cutline and Movement Audit

Cutline review covered:

- QB6, QB12
- RB6, RB12, RB18, RB24, RB36
- WR12, WR24, WR36, WR48
- TE3, TE6, TE12, TE18, TE35

Findings:

- QB original and patched bust-inverse boards had almost identical cutline behavior. Both moved Lamar Jackson, Kyler Murray, and Justin Fields into the 2024 QB6 over Dak Prescott, Brock Purdy, and C.J. Stroud. That is aggressive and needs owner review before any activation.
- RB patched logistic elite moved Breece Hall into the 2024 RB6 over Joe Mixon. It also moved James Cook into RB24 over David Montgomery. These are defensible but not automatic.
- WR patched-vs-original cutlines moved Chris Godwin over Calvin Ridley at WR24 and moved Adam Thielen/Rashee Rice over Marquise Brown/Zay Flowers at WR36 in the 2024 slice. That is a movement-risk warning, not a rejection by itself.
- TE patched-vs-original movement was smaller than WR/RB, but 2024 TE summary metrics still favor the original model family.

Movement warnings:

- Some generated historical boards contain odd or low-volume names near the top 12 or cutlines. Example: Kendall Wilkerson appears high in WR boards. That is a board-quality warning for owner review.
- The 2025 generated board slice is partially collapsed across candidates for QB/RB/WR. Do not overclaim 2025 movement from generated board ranks alone.
- RB 2025 VOR is zero/null in the generated board slice, matching the earlier Phase 33.8 warning.

## Feature Signal Comparison

Selected `ML.WEIGHTS` evidence:

| Position | Original signal | Patched signal | Read |
|---|---|---|---|
| QB | Original bust leaned on `rushing_xfp_share_pbp_3yr`, volatility, team environment, rushing attempts, and passing xFP. | Patched bust still leaned on rushing share and added `passing_epa_per_play`, but only at modest magnitude. | QB remains noisy. |
| RB | Original bust leaned on `target_share_slope_3yr`, `xfp_share_3yr`, and `carry_share_slope_3yr`. | Patched elite leaned on the same role fields plus `red_zone_opportunities` and `receiving_xfp_pbp_3yr`. | Patched RB fields help as component evidence. |
| WR | Original elite leaned on `target_share_slope_3yr`, `wopr_slope_3yr`, `xfp_share_3yr`, `air_yards`, and receiving xFP share. | Patched bust kept those role fields and added `receiving_epa`. | Useful, but movement risk remains. |
| TE | Original bust leaned on target-share, xFP share, WOPR, air yards, and receiving xFP share. | Patched bust keeps that same shape with `receiving_epa` visible. | Patched TE is useful component evidence, not a replacement yet. |

Blocked fields remain blocked:

- `ngs_catch_over_expected_score_3yr`
- unsupported route-derived metrics
- historical depth
- `pigskin_context_score`
- Sleeper current context as a historical predictor

## Overall-Board Gap

Standard BQML v2 is not ready for live activation because there is no approved overall draft-board construction rule.

Required next design work:

- profile-specific VOR as the main cross-position spine
- scarcity and cutline context
- bust inverse or safety context
- deterministic tie-breakers
- movement review against Current Pigskin
- explicit handling for thin or null VOR denominators

## Owner-Review Recommendation

Position finalists are ready for owner review:

- QB: original logistic bust inverse
- RB: original logistic bust inverse, with patched logistic elite as component evidence
- WR: original logistic elite, with patched bust inverse as component evidence
- TE: original logistic bust inverse, with patched bust inverse and original linear points as component evidence

Do not activate a champion. Do not replace Current Pigskin. The next useful phase is Standard overall-board rule design.

Recommended next phase:

- Phase 33.10: Define Standard BQML v2 overall-board rule

## Checks

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract` | PASS, 19 tests |
| `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py` | PASS |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS |
| `git diff --check` | PASS, with Git LF-to-CRLF working-copy warnings only |

## Files Changed

- `docs/rebuild/validation/phase-33-9-standard-bqml-v2-original-vs-patched-owner-review-report.md`
- `docs/rebuild/standard-bqml-v2-owner-review-boards.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

Commit hash: recorded after commit in final response.
