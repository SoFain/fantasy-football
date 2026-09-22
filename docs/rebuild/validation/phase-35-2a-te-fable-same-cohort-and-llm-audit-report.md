# Phase 35.2A TE Fable Same-Cohort And LLM Audit

## Final Decision

`TE FABLE V1.0A NO-MAN WINS SAME-COHORT REVIEW; LLM LAYER NOT AUDITABLE`

TE Fable v1.0a no-man beats Current Pigskin candidate score v1 on most decision metrics when both formulas are evaluated on exactly the same TE player-season rows. Current Pigskin has a small aggregate Spearman advantage caused by the 2023 to 2024 fold. Fable wins aggregate pairwise ordering, top-6 and top-12 precision, points captured, NDCG, band regret, and bust control.

The production LLM adjudication layer cannot be evaluated. It changes ranks but has no persisted adjustment codes, deltas, details, evidence, or estimated games missed on the active Standard TE board.

No Gemini call, ranking write, champion activation, or deployment occurred.

## Exact Cohort Contract

Both formulas used the same rows after requiring:

- TE Fable primary qualification: at least four input-season games and 100 routes.
- A target-season Standard outcome.
- A non-null TE Fable v1.0a no-man score.
- A non-null Current Pigskin candidate score v1 from `ranking_backtest_feature_mart`.

Current Pigskin candidate score v1 was reconstructed from its documented weights:

```text
0.55 analytical_grade_proxy
+ 0.15 opportunity_score_proxy
+ 0.10 efficiency_score_proxy
+ 0.10 role_stability_score
+ 0.10 profile_points_score
```

Feature-mart predictor values were verified as constant across weekly rows for each player and target season before collapsing to one player-season score.

## Same-Cohort Aggregate

| Metric | TE Fable no-man | Current Pigskin | Winner |
|---|---:|---:|---|
| Complete rows | 146 | 146 | tied |
| Spearman | 0.693 | **0.695** | Current Pigskin, narrow |
| Pairwise win rate | **0.761** | 0.752 | TE Fable |
| Top-6 precision | **0.611** | 0.444 | TE Fable |
| Top-12 precision | **0.667** | 0.639 | TE Fable |
| Points captured at 12 | **0.868** | 0.843 | TE Fable |
| NDCG at 12 | **0.872** | 0.861 | TE Fable |
| Band regret | **0.303** | 0.366 | TE Fable |
| Top-12 busts | **0** | 1 | TE Fable |

## Same-Cohort Folds

| Fold | Rows | Fable Spearman | Pigskin Spearman | Fable pairwise | Pigskin pairwise | Fable Top 12 | Pigskin Top 12 | Fable Points@12 | Pigskin Points@12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 to 2023 | 60 | 0.623 | **0.635** | **0.732** | 0.731 | 0.583 | 0.583 | **0.822** | 0.784 |
| 2023 to 2024 | 61 | 0.633 | **0.702** | 0.720 | **0.750** | 0.583 | 0.583 | **0.796** | 0.768 |
| 2024 to 2025 | 25 | **0.822** | 0.748 | **0.830** | 0.777 | **0.833** | 0.750 | **0.987** | 0.977 |

Current Pigskin has only 25 comparable 2024 to 2025 holdout players. It is missing for 42 of the 67 Fable-qualified holdout rows. Fable's broader holdout remains 67 rows, where it recorded 0.742 Spearman and 0.772 pairwise.

## LLM Adjustment Audit

Active production Standard TE board:

- Rows: 35.
- Candidate rank equals final rank: 7.
- Rows moved by adjudication: 28.
- Average absolute movement: 2.6 ranks.
- Maximum movement: 6 ranks.
- Players moved at least five ranks: 6.
- Rows with `llm_adjustment_code`: 0.
- Rows with persisted `llm_rank_delta`: 0.
- Rows with adjustment detail or evidence: 0.
- Rows with `llm_estimated_games_missed`: 0.

Largest derived movements:

| Player | Candidate | Final | Movement |
|---|---:|---:|---:|
| Mark Andrews | 23 | 17 | up 6 |
| T.J. Hockenson | 24 | 18 | up 6 |
| Dalton Kincaid | 21 | 16 | up 5 |
| Brenton Strange | 14 | 19 | down 5 |
| Chig Okonkwo | 39 | 34 | up 5 |
| Mike Gesicki | 40 | 35 | up 5 |

Sam LaPorta moved from candidate TE7 to final TE4 while carrying a current `Questionable` tag. Because the adjustment record is empty, there is no evidence showing whether injury, role, market context, or another reason caused that movement.

## Interpretation

TE Fable no-man is the stronger deterministic candidate on the controlled cohort. It materially improves the newest holdout and most owner-facing draft metrics. Current Pigskin's only aggregate win is a 0.003 Spearman edge.

The LLM layer may contain useful judgment, but the current production records do not prove that. Rank changes without reason codes are unreviewable and cannot be historically backtested.

## Recommendation

1. Advance TE Fable v1.0a no-man as the deterministic Standard TE owner-review candidate.
2. Do not apply an unrestricted LLM reorder.
3. Require every non-zero LLM movement to persist an approved adjustment code, signed rank delta, concise evidence, source freshness, and estimated games missed when injury is involved.
4. Keep preseason `Questionable` status display-only with zero rank effect.
5. Permit injury movement only for `OUT`, `IR`, suspension, or source-backed expected regular-season missed time, within owner-approved movement caps.
6. Backtest the LLM layer only after historical adjustment records exist or a separately authorized historical replay is designed.
