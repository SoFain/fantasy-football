# Phase 33.35 - RB STD GPT 5.5 v1.0A Formula Dry-Run

## Final Decision

`CURRENT PIGSKIN STILL HOLDS FOR STANDARD RB`

Neither v1.0A variant beats the Current Pigskin Standard RB proxy. Both are source-backed and reproducible on eligible rows, but they rank historical workloads too aggressively and lose important ordering quality in 2023 and 2024. The EPA revision barely changes the board.

Neither variant is episode-ready or owner-review ready as a ranking challenger.

## Files Changed

- `bigquery/rb_std_gpt_5_5_v1_0a_dry_run.sql`
- `tests/test_rb_std_gpt_5_5_v1_0a_sql.py`
- `docs/rebuild/validation/phase-33-35-rb-std-gpt-5-5-v1-0a-dry-run-report.md`
- `docs/rebuild/rb-std-gpt-5-5-v1-0a-top25-board.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/advanced-bqml-v2-owner-review-boards.md`

Generated local evidence:

- `output/phase-33-35-rb-std-gpt-5-5-v1-0a-detail.json`
- `output/phase-33-35-rb-std-gpt-5-5-v1-0a-evidence.json`

## Git State

The worktree was already dirty with staged, modified, and untracked Phase 33 work. Phase 33.35 preserved those changes. Nothing was staged or committed.

## Formula Revision Decision

The original v1.0 formula was not tested. RB receiving YAC above expectation remains unavailable.

Two approved revisions were tested:

```text
Efficiency_Score_v1_0a =
  0.4375 * RYOE_Per_Attempt_Modifier
  + 0.3125 * NGS_Rushing_Efficiency_Modifier
  + 0.2500 * Box_Resilience_Modifier
```

```text
Efficiency_Score_v1_0a_EPA =
  0.35 * RYOE_Per_Attempt_Modifier
  + 0.25 * NGS_Rushing_Efficiency_Modifier
  + 0.20 * Box_Resilience_Modifier
  + 0.20 * Receiving_EPA_Per_Target_Modifier
```

The EPA form is a concept revision. It is not presented as a YAC-AOE substitute.

Both variants use:

```text
Final_RB_Standard_Points =
(
  Base_RB_Standard_xFP
  * Role_Stability_Multiplier
  * Efficiency_Multiplier
  * Availability_Multiplier
)
- Fumble_Lost_Penalty
```

The team environment multiplier is omitted. Projected team RB xFP pools already carry team environment, so a separate multiplier would double count it.

## Standard xFP Implementation

The raw ffopportunity payload contains `receptions_exp`. Standard receiving xFP is calculated as:

```text
Receiving_xFP_Standard = rec_fantasy_points_exp - receptions_exp
```

Player and team RB rushing/receiving xFP are projected with 60/30/10 prior-season weights. Team pools are regressed 75% to the weighted team history and 25% to the league-average team RB pool. Player shares use the same leakage-safe source years.

## Missing-Data Policy

No required candidate input is zero-filled.

Rushing-only eligibility requires:

- source-backed projected rushing and Standard receiving xFP;
- all four role-share components;
- RYOE per attempt, NGS rushing efficiency, and box resilience;
- birth date and target-season age factor;
- prior-season snap-game history;
- fumbles lost rate and touch projection.

EPA eligibility requires every rushing-only field plus receiving EPA per target with targets greater than zero.

| Target | Universe | Rushing-only eligible | Missing rate | EPA eligible | Missing rate |
|---|---:|---:|---:|---:|---:|
| 2023 | 72 | 56 | 22.2% | 55 | 23.6% |
| 2024 | 67 | 54 | 19.4% | 54 | 19.4% |
| 2025 | 19 | 10 | 47.4% | 10 | 47.4% |

The 2025 cohort is too thin for a standalone approval decision.

## Leakage And Outcome Contract

- Target 2023 features use 2020-2022 only.
- Target 2024 features use 2021-2023 only.
- Target 2025 features use 2022-2024 only.
- Full target-season Standard points and season ranks are joined after formula scoring for evaluation only.
- No 2026 outcome, current Sleeper context, market target, Current Pigskin score, or target-season result enters either candidate formula.

The first draft exposed an inherited evaluation problem: the feature mart's `target_week=18` outcome is Week 18, not a full-season finish. Phase 33.35 corrected evaluation to aggregate weeks 1-18 from `analytics_player_fantasy_points_by_profile`. The report does not mislabel weekly ranks as season finishes.

## 2023 Results

Matched rushing-only cohort: 56 players.

| Formula | Top 6 | Top 12 | Top 24 | Top 36 | Points | VOR | NDCG | Pairwise | Regret | Elite misses | Extreme moves |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Current Pigskin proxy | 0.500 | 0.500 | 0.708 | 0.806 | 0.788 | 0.708 | 0.935 | 0.734 | 11.071 | 2 | 0 |
| v1.0A rushing-only | 0.167 | 0.417 | 0.667 | 0.806 | 0.771 | 0.686 | 0.910 | 0.708 | 11.643 | 2 | 8 |

Matched EPA cohort: 55 players. v1.0A-EPA records NDCG 0.910, pairwise 0.707, and regret 11.382. Current Pigskin records 0.935, 0.733, and 10.836 on that cohort.

## 2024 Results

Matched cohort: 54 players for both variants.

| Formula | Top 6 | Top 12 | Top 24 | Top 36 | Points | VOR | NDCG | Pairwise | Regret | Elite misses | Extreme moves |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Current Pigskin proxy | 0.500 | 0.750 | 0.750 | 0.806 | 0.889 | 0.895 | 0.948 | 0.770 | 9.222 | 0 | 0 |
| v1.0A rushing-only | 0.333 | 0.583 | 0.792 | 0.833 | 0.881 | 0.832 | 0.863 | 0.738 | 10.185 | 1 | 4 |
| v1.0A-EPA | 0.333 | 0.583 | 0.792 | 0.833 | 0.881 | 0.832 | 0.863 | 0.737 | 10.148 | 1 | 4 |

The candidates gain one top-24 and top-36 hit, but lose top-6/top-12 quality, VOR, NDCG, pairwise accuracy, and regret. That is not a baseline win.

## 2025 Results

Matched cohort: 10 players.

| Formula | Top 6 | Top 12 | Points | VOR | NDCG | Pairwise | Regret |
|---|---:|---:|---:|---:|---:|---:|---:|
| Current Pigskin proxy | 1.000 | 1.000 | 1.000 | 1.000 | 0.977 | 0.956 | 0.400 |
| v1.0A rushing-only | 1.000 | 1.000 | 1.000 | 1.000 | 0.915 | 0.867 | 1.200 |
| v1.0A-EPA | 1.000 | 1.000 | 1.000 | 1.000 | 0.915 | 0.867 | 1.200 |

The identical cutline metrics are an artifact of a 10-player eligible cohort. Current Pigskin still orders that cohort better.

## Comparison To Prior Episode Formula

`standard_rb_elite_receiving_back_protection_v0` remains an episode discussion concept from Phase 33.32. Its published 2024 Week 18 proxy improved top-12 hit and pairwise rate versus that phase's baseline, but Phase 33.35 discovered that those target labels were weekly, not full-season outcomes. Those metrics are not directly comparable to the corrected full-season evaluation here.

The prior formula also includes Current Pigskin as a 50% input, which v1.0A explicitly forbids. It is retained as historical context, not treated as a clean independent challenger.

## Player-Level Explanation

| Season | Player | Current cohort rank | v1.0A rank | Actual finish | Base xFP | Role | Efficiency | Availability | Fumble | Risk | Read |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2023 | Austin Ekeler | 5 | 3 | 31 | 223.2 | 1.023 | 0.995 | 0.930 | 5.19 | yes | Prior workload remains too powerful. |
| 2023 | Leonard Fournette | 13 | 7 | 116 | 187.6 | 1.013 | 0.998 | 0.897 | 0.00 | yes | Stale role history creates a severe false positive. |
| 2023 | Derrick Henry | 1 | 9 | 5 | 220.2 | 1.032 | 1.005 | 0.728 | 3.61 | yes | Availability curve over-penalizes an elite result. |
| 2024 | Travis Etienne | 7 | 2 | 39 | 210.9 | 1.034 | 1.002 | 0.990 | 2.17 | no | Team-pool/share projection overstates the outcome. |
| 2024 | Jahmyr Gibbs | 8 | 11 | 3 | 200.5 | 1.005 | 0.992 | 0.741 | 2.00 | yes | Availability/short history holds down an elite finish. |
| 2024 | Jonathan Taylor | 4 | 23 | 8 | 147.6 | 1.025 | 1.006 | 0.644 | 2.00 | yes | Availability multiplier is too punitive. |
| 2025 | Christian McCaffrey | 2 | 6 | 2 | 125.8 | 1.019 | 1.000 | 0.579 | 4.34 | yes | Missed-time history overwhelms elite role value. |

## Top-25 Boards

Full Current Pigskin, rushing-only, and EPA boards are in `docs/rebuild/rb-std-gpt-5-5-v1-0a-top25-board.md`.

The candidate boards contain eligible rows only. The 2025 board has 10 rows, not 25, because the phase does not fabricate or impute missing NGS/history inputs.

## Formula Assessment

- v1.0A rushing-only does not beat Pigskin.
- v1.0A-EPA does not beat Pigskin.
- EPA provides almost no rank separation from rushing-only under a 3% capped efficiency multiplier.
- Both candidates reduce receiving-back misses in 2023, but at the cost of worse overall ordering and eight extreme movements.
- The projected team-pool xFP base needs stronger recency/role-loss protection.
- The availability multiplier is too punitive when multiplied directly into the full projection.

Current Pigskin still holds for Standard RB.

## Dry-Run Execution

- BigQuery job ID: `ebc14fc2-fff0-4e85-9076-993049265710`
- Bytes processed: `254,542,822`
- Detail rows: `158`
- Rushing-only eligible rows across all targets: `120`
- BigQuery writes: `0`

## Checks

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract` | PASS, 26 tests |
| `.\venv\Scripts\python.exe -m unittest tests.test_rb_std_gpt_5_5_v1_0a_sql` | PASS, 6 tests |
| `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py` | PASS |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS, all checks true |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | PASS, 251 files discovered |
| BigQuery formula query dry run | PASS, 254,542,822 bytes processed |
| Focused fumble projection assertion | PASS, 0 null penalties among eligible rows |
| Focused availability assertion | PASS, 0 null multipliers among eligible rows |
| Focused leakage assertion | PASS, 0 leaked rows |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern route_metrics` | PASS, 2 validations |
| `git diff --check` | PASS with preexisting LF-to-CRLF warnings on four tracked research docs |

## No-Live-Change Confirmation

- No live rankings written.
- No champion activated.
- No model trained.
- No deployment.
- No top-100 build.
- No Gemini, Pigskin chat, or Sleeper API call.
- No BigQuery DDL or DML.
- No 2026 outcomes used.
- Raw YAC, YPRR, TPRR, true route share, first-read share, broken tackles, and `pigskin_context_score` are absent.

## Warnings

- Strict eligibility removes 19-47% of the target universe.
- The 2025 cohort is only 10 players.
- Phase 33.32's prior episode metrics used Week 18 outcomes and should not be presented as season-finish evidence.
- Fumble-rate projection has no small-sample shrinkage. That decision remains owner-controlled.

## Recommended Next Phase

`Phase 33.36 - refine Standard RB team-pool recency and availability treatment`

Do not advance either v1.0A variant to owner review. The next revision should reduce stale-workload persistence and test availability as a bounded penalty rather than a full multiplicative haircut.
