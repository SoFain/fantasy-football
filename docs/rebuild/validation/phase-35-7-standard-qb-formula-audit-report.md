# Phase 35.7: Standard QB Formula Audit

## Final decision

**STANDARD QB CAPPED COMPOSITE REJECTED; GUARDED BQML BLEND TEST REQUIRED**

Do not promote an existing QB lane yet. The advanced models outperform the generic Pigskin candidate formula historically, but the 2026 owner-review evidence still shows excessive upward movement for rushing quarterbacks with weak passing evidence.

## Scope

Read-only review of the active Standard QB board, its deterministic candidate input, existing Standard QB backtests, BQML weights, and the prior 2026 owner-review board. No model was trained. No ranking row, champion, feature flag, or production service was changed.

## Live Standard QB control

- Active ranking version: `pigskin-llm-20260704071412`
- Model: `gemini-3.5-flash`
- Rows: 45
- Candidate rows moved by the old LLM pass: 41 of 45
- Mean absolute movement: 3.96 ranks
- Maximum movement: 10 ranks
- Candidate-to-live rank correlation: 0.9353
- Adjustment codes: absent because this board predates the bounded Pigskin adjustment contract

Largest upward moves include Jordan Love QB15 to QB5, Jameis Winston QB44 to QB34, Fernando Mendoza QB41 to QB32, Dak Prescott QB13 to QB6, and Matthew Stafford QB10 to QB4. The changes are not auditable under the current adjustment-code policy.

The live board should be treated as a control board, not as a formula champion.

## Current deterministic candidate formula

`src/materialize.py` builds one generic position candidate score:

- 55 percent analytical grade
- 15 percent opportunity
- 10 percent efficiency
- 10 percent inverse role fragility
- 10 percent profile fantasy points, capped through `LEAST(100, avg_profile_points * 4)`

QB depth-chart penalties are applied after scoring. This is not a QB-specific formula and does not explicitly balance passing volume, passing efficiency, or a capped rushing floor.

## Historical candidate comparison

The following metrics are read directly from `ranking_backtest_candidate_summaries`. Advanced BQML rows use the combined 2024-2025 Standard QB run with 868 samples. Older baselines use the rolling 2017-2025 run with 4,646 samples, so the values are directional rather than a claim of identical evaluation windows.

| Candidate | Pairwise win rate | Top-N hit rate | Rank correlation | Captured points | Regret |
|---|---:|---:|---:|---:|---:|
| Advanced logistic bust | 0.6971 | 0.6944 | **0.5543** | 0.8286 | **863.16** |
| Advanced linear points | **0.8476** | 0.6944 | 0.5503 | **0.8292** | 865.30 |
| Current Pigskin candidate score | 0.6924 | 0.5781 | 0.4392 | 0.7910 | 4250.82 |
| Simple projection baseline | 0.6874 | 0.5754 | 0.4524 | 0.7904 | 4252.02 |
| Stats02 QB ideal rushing xFP | 0.7243 | 0.5796 | 0.4455 | 0.7886 | 4300.38 |

The advanced lanes are clearly stronger than the generic candidate score on their bounded 2024-2025 evidence. Logistic bust has the best correlation and regret. Linear points dominates pairwise comparisons and narrowly leads captured points.

## Rushing-bias finding

The previous package labeled advanced linear points as the rushing-biased alternate, but the selected logistic-bust 2026 review board also shows the problem:

- Justin Fields: Current Pigskin QB32 to raw finalist QB16, despite passing EPA per dropback of -0.16 and CPOE of -15.33
- Lamar Jackson: QB14 to QB2
- Jayden Daniels: QB12 to QB3
- Jaxson Dart: QB16 to QB7
- Kyler Murray: QB18 to QB13 with a rushing-bias warning

The logistic model's `ML.WEIGHTS` include `adv_qb_rushing_baseline_3yr`, `adv_carries_3yr`, `adv_rushing_epa_3yr`, and `adv_rushing_yards_3yr`. Its passing inputs are also highly correlated, and raw coefficient magnitude is not a stable importance measure without accounting for feature scaling. The model cannot be called rushing-safe based only on its family name.

The advanced linear-points coefficients also contain suspicious directions, including negative recent-points and passing-EPA-per-attempt weights. This is consistent with multicollinearity and is another reason not to promote it directly.

## Read-only deterministic composite test

The audit ran a bounded SQL-native Standard QB formula sprint. No summary row was persisted.

Initial broad composite:

| Component | Weight |
|---|---:|
| Standard profile points | 20% |
| Passing xFP | 15% |
| NGS QB efficiency | 20% |
| Expected passing first downs | 10% |
| Team environment | 10% |
| QB rushing leverage | 10% |
| Snap-role stability | 10% |
| Availability | 5% |

Result: rejected. It improved pairwise win rate to 0.7203 but fell behind the current candidate and simple projection on top-N hit rate, captured points, and regret.

A smaller grid then tested projection-anchored variants. The best balanced candidate was `standard_qb_projection_ngs_85_10_v0`:

| Component | Test weight | Rule |
|---|---:|---|
| Standard profile points | 85% | Stable projection anchor |
| NGS QB passing efficiency | 10% | Source-backed passing signal |
| Rushing floor | 5% | Bounded 0-100 feature; cannot add more than five formula points |

Same-job comparison against the current Pigskin candidate and simple projection:

| Split | Candidate | Pairwise | Top-N | Correlation | Captured points | Regret |
|---|---|---:|---:|---:|---:|---:|
| 2024 validation | Current candidate | 0.6920 | **0.5231** | 0.4274 | **0.7647** | 572.34 |
| 2024 validation | Simple projection | 0.6970 | 0.5185 | 0.4507 | 0.7572 | **565.62** |
| 2024 validation | 85/10/5 composite | **0.7004** | 0.5139 | **0.4531** | 0.7593 | 574.96 |
| 2025 holdout | Current candidate | **0.6951** | 0.8380 | **0.4470** | **0.8866** | **306.24** |
| 2025 holdout | Simple projection | 0.6643 | **0.8426** | 0.4253 | 0.8822 | 309.42 |
| 2025 holdout | 85/10/5 composite | 0.6723 | **0.8426** | 0.4236 | 0.8831 | 317.04 |

The 85/10/5 candidate is not promotion-ready. It adds useful 2024 ordering signal but does not improve the untouched 2025 holdout. Further weight tuning against 2025 would be holdout leakage and was not performed.

BigQuery jobs used for read-only evidence:

- Initial broad composite: `79964ea8-5bbc-44d1-a82c-2d5a5be6c689`
- Projection-anchored grid: `7899b23f-bbc3-4b43-879c-48bd1cf7ca65`
- Light-overlay grid: `83c84e45-49b4-4f63-9fb3-f2255510921b`
- Same-job 2024 comparison: `baab6822-146d-48e8-892d-6441d98dfe74`
- Same-job 2025 comparison: `baea1b74-57e5-4b35-b4d4-6955e3f8a505`

## Required next test

Do not tune another raw weighted formula against the 2025 holdout. Test the already-trained advanced models as bounded signals around a deterministic anchor:

1. Current Pigskin candidate score as the control.
2. Simple projection as the calibration floor.
3. Advanced logistic-bust signal, capped to move a player no more than five ranks from the control.
4. Advanced linear-points signal, capped to five ranks and blocked from promoting a QB on rushing evidence alone.
5. Consensus lane that moves a player only when both advanced models agree on direction.

Required cutline checks: QB6, QB12, and QB24. Report passing-efficiency exceptions, rushing-only risers, rookies without NFL history, current backups, and every player moved more than three ranks. The 2025 split remains evaluation-only.

## Pigskin role

After a QB formula is selected, Pigskin should use the same bounded exception contract now enforced for TE:

- formula owns rank, score, tier, rationale, and verdict
- Pigskin may request only coded current-role, rookie, or injury changes
- maximum substantive adjustments and total movement remain bounded
- every applied change must display its adjustment code and source-backed evidence

## Checks

- Production and BigQuery inspection: read-only
- `scripts/check_deployment_safety.py`: pass
- No broad validation run
- No LLM call
- No live Sleeper call
- No model training
- No ranking or champion write
- No deployment

## Recommended next phase

**Phase 35.8: Standard QB guarded BQML blend and movement-cap dry-run.**

Use the deterministic control as the anchor and the existing BQML models only as bounded signals. Produce 2024 validation, untouched 2025 holdout, and 2026 owner-review movement tables. Promotion remains blocked until the lane clears the simple projection floor without creating rushing-only QB risers.
