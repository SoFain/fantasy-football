# Phase 32.30: Live 2026 Review-Board Generation

Final decision: **LIVE 2026 REVIEW BOARDS READY WITH WARNINGS**

## Scope

Generated review-only live 2026 boards. This phase did not deploy, regenerate live rankings, activate champions, train BQML models, ingest sources, call live Sleeper, call Pigskin chat, call Gemini, write to `analytics_pigskin_rankings`, write to `ranking_formula_champions`, write detail backtest rows, or globally truncate any table.

## Files Changed

| File | Change |
|---|---|
| `docs/rebuild/live-2026-ranking-review-boards.md` | PPR owner-review boards, movement tables, position boards capped at TE35, and cutline crossings. |
| `docs/rebuild/validation/phase-32-30-live-2026-review-board-report.md` | Phase report and owner decision summary. |
| `docs/rebuild/ranking-algorithm-scorecard.md` | Phase 32.30 scorecard note. |
| `docs/rebuild/ranking-opportunity-metrics-matrix.md` | Live review input coverage note. |
| `docs/rebuild/formula-ranking-owner-review-index.md` | Link and owner action choices for Phase 32.30. |

Commit hash: not committed at report-generation time.

## Safety And No-Change Verification

| Check | Result |
|---|---:|
| Active live ranking rows | 1140 |
| `ranking_formula_champions` total rows | 0 |
| Active champion rows | 0 |
| Sleeper current context rows | 12200 |
| Sleeper latest snapshot | `2026-07-05 17:52:48.174830+00:00` |
| `ranking_backtest_feature_mart` 2026 rows | 0 |
| `ranking_backtest_feature_mart` 2026 labeled rows | 0 |

Active live ranking shape remains unchanged:

| Profile | Position | Active rows |
| --- | --- | --- |
| gng_keeper | QB | 45 |
| gng_keeper | RB | 80 |
| gng_keeper | TE | 60 |
| gng_keeper | WR | 100 |
| half_ppr | QB | 45 |
| half_ppr | RB | 80 |
| half_ppr | TE | 60 |
| half_ppr | WR | 100 |
| ppr | QB | 45 |
| ppr | RB | 80 |
| ppr | TE | 60 |
| ppr | WR | 100 |
| standard | QB | 45 |
| standard | RB | 80 |
| standard | TE | 60 |
| standard | WR | 100 |

Latest active ranking versions:

| Profile | Version | Latest generated at |
| --- | --- | --- |
| gng_keeper | pigskin-llm-20260704072119 | 2026-07-04 07:29:22.569631+00:00 |
| half_ppr | pigskin-llm-20260704070315 | 2026-07-04 07:13:52.254000+00:00 |
| ppr | pigskin-llm-20260703061257 | 2026-07-03 06:21:06.236702+00:00 |
| standard | pigskin-llm-20260704071412 | 2026-07-04 07:21:00.762852+00:00 |

2026 candidate universe:

| Profile | Position | Candidate rows |
| --- | --- | --- |
| ppr | QB | 128 |
| ppr | RB | 202 |
| ppr | TE | 213 |
| ppr | WR | 393 |

## Production Generator Audit

`src/generate_pigskin_rankings.py` is not safe for review-only board generation because it reads `analytics_pigskin_rankings_candidates`, requires `GEMINI_API_KEY`, calls Gemini, and writes `analytics_pigskin_rankings` plus history through `write_rankings`. Phase 32.30 did not invoke that module.

## 2026 Prediction Input Method

- Review version: `phase32_30_live_2026_ppr_review_20260706`.
- Grain: one row per `scoring_profile_id`, `league_type_id`, `roster_format_id`, `position`, and `player_id_internal`.
- Available live candidate slice: PPR only, 936 rows.
- Input source: 2026 PPR candidate universe, joined to latest pre-2026 compatible `ranking_backtest_feature_mart` predictor fields where available.
- Labels and outcomes excluded: `target_fantasy_points`, `actual_position_rank`, `actual_overall_rank`, `value_over_replacement`, elite labels, starter labels, and pick-band labels were not selected into the prediction input.
- `pigskin_context_score` was not required or fabricated.
- Non-PPR BQML boards were not generated. There is no silent PPR fallback.

Owner-review scoring interpretation rule:

- Display Standard first when all four scoring systems are available.
- Scoring profile display order should be `standard`, `half_ppr`, `ppr`, `gng_keeper`.
- Do not recommend one global winner averaged across all four scoring systems.
- Classify the best challenger separately by scoring profile.
- All-profile aggregate is stability and context only, not the champion-selection decision.

Phase 32.30 scoring-profile result:

| Scoring profile | Board status | Best review-only challenger | Reason |
|---|---|---|---|
| `standard` | blocked | not selected | 2026 candidate input is not available for Standard. |
| `half_ppr` | blocked | not selected | 2026 candidate input is not available for Half PPR. |
| `ppr` | generated with warnings | `ranking_bqml_enriched_logistic_elite_v1` | Linear points was too volatile on sparse live input. Logistic is better for owner inspection, not promotion. |
| `gng_keeper` | blocked | not selected | 2026 candidate input is not available for GNG Keeper. |

Feature family coverage across the PPR input:

| Feature family | Populated values | Possible values | Coverage |
| --- | --- | --- | --- |
| baseline_candidate_proxies | 3090 | 5616 | 55.0% |
| trend_proxies | 523 | 4680 | 11.2% |
| ideal_xfp | 428 | 3744 | 11.4% |
| pbp_xfp_first_downs | 416 | 5616 | 7.4% |
| ngs_direct | 236 | 7488 | 3.2% |
| injury_availability | 484 | 5616 | 8.6% |

## Model Prediction Method

- Read-only `ML.PREDICT` dry-run bytes: `5538179`.
- Read-only `ML.PREDICT` job ID: `3037784f-1163-47c6-9955-73543299a6f8`.
- Read-only `ML.PREDICT` bytes processed: `5538179`.
- Required models run: `ranking_bqml_enriched_logistic_elite_v1`, `ranking_bqml_enriched_linear_points_v1`.
- Context models run because the same input was cheap: `ranking_bqml_ngs_logistic_elite_v1`, `ranking_bqml_ngs_linear_points_v1`.

| Model | Rows | Score min | Score max | Score avg | Avg missing % |
| --- | --- | --- | --- | --- | --- |
| enriched_logistic | 936 | 0.66 | 99.80 | 15.47 | 77.9 |
| enriched_linear_points | 936 | -340.08 | 620.70 | 24.55 | 77.9 |
| ngs_logistic_context | 936 | 0.67 | 99.71 | 15.25 | 77.9 |
| ngs_linear_points_context | 936 | -147.96 | 22766.48 | 1544.69 | 77.9 |

## Current Pigskin Baseline Join

- BQML PPR prediction rows: 936.
- Rows missing from active current PPR baseline: 651.
- Missing baseline rows are outside the current live top-depth board and are shown as missing rather than assigned fake current ranks.

## Sleeper Live Context

- Sleeper context was joined for display only using candidate ID to `player_id_internal` and `gsis_id`.
- Null Sleeper current teams were displayed as `unknown`; identity team fallback was not used.
- Sleeper current context was not used as historical training or backtest input.
- Sleeper freshness: `2026-07-05 17:52:48.174830+00:00`.

## Board Output

Full PPR owner-review boards are in `docs/rebuild/live-2026-ranking-review-boards.md`.

Standard, Half PPR, and GNG Keeper are blocked for Phase 32.30 review-board generation because the available 2026 candidate slice is PPR-only. This is the main limitation of the phase.

## Risk Notes

| Risk check | Result |
| --- | --- |
| WR movement greater than 20 ranks, logistic | 74 |
| WR movement greater than 20 ranks, linear points | 86 |
| Rows with null Sleeper current team in logistic board | 797 |
| Rows with notable Sleeper status or injury status in logistic board | 6 |
| Average missing feature rate | 77.9% |

QB concentration:

| Board | QB in top 24 | QB in top 50 |
| --- | --- | --- |
| Current Pigskin | 6 | 14 |
| BQML logistic | 0 | 3 |
| BQML linear points | 0 | 0 |

Top null-team examples, logistic board:

| Rank | Player | Pos | Score | Current rank |
| --- | --- | --- | --- | --- |
| 1 | Bijan Robinson | RB | 99.80 | 9 |
| 2 | Jonathan Taylor | RB | 99.79 | 19 |
| 3 | James Cook | RB | 99.51 | 27 |
| 4 | Jahmyr Gibbs | RB | 99.37 | 15 |
| 5 | De'Von Achane | RB | 99.04 | 21 |
| 6 | Kyren Williams | RB | 98.83 | 33 |
| 7 | Chase Brown | RB | 98.63 | 47 |
| 8 | Travis Etienne | RB | 98.51 | 62 |
| 9 | Javonte Williams | RB | 98.30 | 52 |
| 10 | Ashton Jeanty | RB | 98.27 | 79 |
| 11 | Breece Hall | RB | 97.56 | 69 |
| 12 | Rico Dowdle | RB | 97.37 | 98 |

Top injury/status examples, logistic board:

| Rank | Player | Pos | Status | Injury | Sleeper team |
| --- | --- | --- | --- | --- | --- |
| 49 | James Conner | RB | Active | Questionable | ARI |
| 55 | George Kittle | TE | Active | Questionable | SF |
| 60 | Patrick Mahomes | QB | Active | Questionable | KC |
| 98 | Dak Prescott | QB | Active | Questionable | DAL |
| 704 | Trevor Siemian | QB | Active | Questionable | ATL |
| 868 | Michael Woods | WR | Inactive | Questionable | unknown |

## Owner Decision Summary

| Lane | Label | Decision |
|---|---|---|
| Current Pigskin | live baseline | Keep live. |
| Enriched BQML logistic elite v1 | review-only challenger | Useful for owner inspection, not a champion. |
| Enriched BQML linear points v1 | review-only challenger | Useful but volatile for promotion on this sparse input. |
| BQML NGS | context only | Adds context but missing NGS coverage keeps it out of promotion. |
| NGS direct diagnostics | component signal | Keep as explanatory context. |
| Injury and availability | risk flag only | Show as warnings, not formula weights. |
| Sleeper current context | display only | Fresh live context, not a historical input. |
| Historical depth | blocked | Still not available as a trusted historical role source. |

## Recommendation

Hold current Pigskin as the live baseline. Use the PPR review boards for owner inspection only. The next useful phase is **Phase 32.31 - Formula comparison dashboard in app, read-only**, unless the owner prefers to stop and hold current Pigskin.

Future owner-approved live-ranking depth change: reduce TE from 60 to 35.

## Checks Run

```powershell
git status --short
git diff --check
read-only BigQuery safety queries for live ranking counts, champions, Sleeper freshness, candidates, and feature mart 2026 count
read-only BigQuery ML.PREDICT against required enriched models and optional NGS context models
```

## Remaining Warnings

- BQML boards are PPR-only because the 2026 candidate table currently has PPR rows only.
- Average missing feature rate is high, about 77.9%.
- Linear points produces extreme scores on sparse live input. Treat it as an ordering diagnostic, not a live candidate.
- NGS and injury feature families are mostly missing in the live 2026 input. Keep them as context or risk flags.
- No persistent review table was created. Markdown output is enough for this review-only phase.
