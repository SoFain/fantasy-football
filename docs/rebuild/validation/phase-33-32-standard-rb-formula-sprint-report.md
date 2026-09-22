# Phase 33.32 Standard RB Formula Sprint Report

Final decision: **STANDARD RB FORMULA EPISODE-READY ONLY**

Phase 33.32 tested transparent Standard-scoring RB formulas against the Current Pigskin Standard RB proxy. The best discussion candidate is `standard_rb_elite_receiving_back_protection_v0`. It improves 2024 validation top-12 hit rate and pairwise draft win rate while keeping elite RB misses flat, but it does not beat Current Pigskin on 2025 holdout NDCG or pairwise rate. Current Pigskin still holds for live use.

## Files Changed

- `docs/rebuild/validation/phase-33-32-standard-rb-formula-sprint-report.md`
- `docs/rebuild/standard-rb-formula-sprint-board.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/advanced-bqml-v2-owner-review-boards.md`

Evidence artifact:

- `output/phase-33-32-standard-rb-formula-sprint-evidence.json`

## Git State

The worktree was already dirty with staged and untracked Phase 33 artifacts before this phase. Phase 33.32 did not stage, commit, deploy, or revert prior work.

## Source Field Coverage

Rows evaluated: `307` Standard RB source-window-safe rows.

Available target seasons in the source-window-safe Standard RB slice: `2021, 2022, 2023, 2024, 2025`.

The requested 2017-2023 context is only partially available. `ranking_backtest_feature_mart` currently has source-window-safe Standard RB rows for 2021-2023 context, 2024 validation, and a thin 2025 holdout slice. I did not force 2017-2020 rows because they are not present under the leakage-safe rule.

Unavailable requested fields:

- rushing yards: No approved column in ranking_backtest_feature_mart.
- rushing touchdowns: No approved column in ranking_backtest_feature_mart.
- receptions: No approved column in ranking_backtest_feature_mart.
- receiving touchdowns: No approved column in ranking_backtest_feature_mart.

Fields with material missingness:

- target share (`target_share_slope_3yr`): missing rate 0.238.
- carry share (`carry_share_slope_3yr`): missing rate 0.238.
- NGS rushing efficiency (`ngs_rushing_efficiency_score_3yr`): missing rate 0.212.
- NGS rush yards over expected (`ngs_rush_yards_over_expected_score_3yr`): missing rate 0.212.
- NGS box resilience (`ngs_box_resilience_score_3yr`): missing rate 0.212.
- availability score (`availability_score_3yr`): missing rate 0.459.
- injury burden / missed-time risk (`missed_time_risk_score_3yr`): missing rate 0.459.


Leakage policy:

- `source_window_end_season < target_season` passed for every evaluated row.
- No 2026 outcomes were used.
- No market data was used as a training target.
- Sleeper current context was not used as historical input.
- Blocked route metrics were absent from formula definitions.

## Formula Definitions

- `standard_rb_pigskin_opportunity_blend_v0`: 55% Current Pigskin proxy, 20% weighted opportunity per game, 10% high-value opportunity/xFP, 7.5% red-zone/goal-line, 5% NGS rushing efficiency/RYOE, 2.5% availability.
- `standard_rb_receiving_aware_v0`: 45% Current Pigskin proxy, 20% weighted opportunity per game, 15% receiving value, 10% rushing volume, 5% red-zone/goal-line, 5% availability/snap stability.
- `standard_rb_high_value_opportunity_v0`: 35% weighted opportunity per game, 20% high-value xFP, 15% red-zone/goal-line, 10% rushing efficiency/NGS RYOE, 10% receiving value, 5% snap stability, 5% availability.
- `standard_rb_conservative_anchor_v0`: 70% Current Pigskin proxy, 12.5% weighted opportunity per game, 7.5% receiving value, 5% red-zone/goal-line, 2.5% NGS rushing efficiency, 2.5% availability.
- `standard_rb_elite_receiving_back_protection_v0`: 50% Current Pigskin proxy, 20% weighted opportunity per game, 15% receiving value, 7.5% high-value opportunity, 5% snap share/role stability, 2.5% availability.
- `standard_rb_source_only_v0`: 25% weighted opportunity per game, 20% Standard production, 15% rushing volume, 15% receiving value, 10% red-zone/goal-line, 10% NGS rushing efficiency/RYOE, 5% availability.

No optional sweep was run. The prompt allowed it only if time permitted, and the source-slice limitation made a small fixed set more defensible.

## 2024 Validation Metrics

| Formula | Top6 | Top12 | Top24 | Points | VOR | NDCG | Pairwise | Elite miss | Regret |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `current_pigskin_standard_rb_proxy` | 0.333 | 0.417 | 0.542 | 0.815 | 0.861 | 0.725 | 0.630 | 3 | 15.361 |
| `standard_rb_pigskin_opportunity_blend_v0` | 0.333 | 0.417 | 0.542 | 0.818 | 0.861 | 0.722 | 0.622 | 3 | 15.083 |
| `standard_rb_receiving_aware_v0` | 0.333 | 0.417 | 0.542 | 0.816 | 0.861 | 0.708 | 0.632 | 3 | 15.250 |
| `standard_rb_high_value_opportunity_v0` | 0.333 | 0.417 | 0.542 | 0.816 | 0.861 | 0.643 | 0.624 | 3 | 15.250 |
| `standard_rb_conservative_anchor_v0` | 0.333 | 0.417 | 0.542 | 0.816 | 0.861 | 0.710 | 0.629 | 3 | 15.361 |
| `standard_rb_elite_receiving_back_protection_v0` | 0.333 | 0.500 | 0.542 | 0.816 | 0.861 | 0.717 | 0.643 | 3 | 15.083 |
| `standard_rb_source_only_v0` | 0.333 | 0.417 | 0.542 | 0.816 | 0.861 | 0.716 | 0.629 | 3 | 15.250 |

## 2025 Holdout Metrics

| Formula | Top6 | Top12 | Top24 | Points | VOR | NDCG | Pairwise | Elite miss | Regret |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `current_pigskin_standard_rb_proxy` | 0.500 | 0.833 | 0.792 | 1.000 | n/a | 0.843 | 0.716 | 0 | 3.579 |
| `standard_rb_pigskin_opportunity_blend_v0` | 0.500 | 0.833 | 0.792 | 1.000 | n/a | 0.835 | 0.693 | 0 | 3.895 |
| `standard_rb_receiving_aware_v0` | 0.500 | 0.833 | 0.792 | 1.000 | n/a | 0.780 | 0.687 | 0 | 4.000 |
| `standard_rb_high_value_opportunity_v0` | 0.500 | 0.833 | 0.792 | 1.000 | n/a | 0.781 | 0.687 | 0 | 4.105 |
| `standard_rb_conservative_anchor_v0` | 0.500 | 0.833 | 0.792 | 1.000 | n/a | 0.837 | 0.693 | 0 | 3.789 |
| `standard_rb_elite_receiving_back_protection_v0` | 0.500 | 0.833 | 0.792 | 1.000 | n/a | 0.783 | 0.687 | 0 | 3.895 |
| `standard_rb_source_only_v0` | 0.500 | 0.833 | 0.792 | 1.000 | n/a | 0.781 | 0.681 | 0 | 4.000 |

2025 holdout warning: `value_over_replacement` is null in the thin 19-row holdout slice, so VOR captured is not available for that split.

## 2021-2025 Context Metrics

| Formula | Top6 | Top12 | Top24 | Points | VOR | NDCG | Pairwise | Elite miss | Regret |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `current_pigskin_standard_rb_proxy` | 0.267 | 0.550 | 0.625 | 0.823 | 0.822 | 0.738 | 0.647 | 2.200 | 14.188 |
| `standard_rb_pigskin_opportunity_blend_v0` | 0.267 | 0.517 | 0.617 | 0.830 | 0.825 | 0.739 | 0.631 | 2.200 | 14.201 |
| `standard_rb_receiving_aware_v0` | 0.267 | 0.517 | 0.608 | 0.827 | 0.825 | 0.722 | 0.638 | 2.400 | 14.344 |
| `standard_rb_high_value_opportunity_v0` | 0.267 | 0.517 | 0.600 | 0.834 | 0.833 | 0.707 | 0.625 | 2.600 | 14.515 |
| `standard_rb_conservative_anchor_v0` | 0.267 | 0.533 | 0.617 | 0.827 | 0.824 | 0.739 | 0.639 | 2.200 | 14.136 |
| `standard_rb_elite_receiving_back_protection_v0` | 0.267 | 0.533 | 0.608 | 0.832 | 0.832 | 0.725 | 0.634 | 2.400 | 14.218 |
| `standard_rb_source_only_v0` | 0.267 | 0.533 | 0.608 | 0.831 | 0.833 | 0.727 | 0.628 | 2.400 | 14.494 |

## Best Formula

Best episode discussion formula: `standard_rb_elite_receiving_back_protection_v0`.

Why:

- 2024 validation top-12 hit improves from 0.417 to 0.500.
- 2024 validation pairwise draft win rate improves from 0.630 to 0.643.
- 2024 elite miss count stays flat at 3.
- 2025 holdout top-12, top-24, points capture, and elite miss count tie Current Pigskin.

Why it is not owner-review ready yet:

- 2025 holdout NDCG falls from 0.843 to 0.783.
- 2025 holdout pairwise draft win rate falls from 0.716 to 0.687.
- The 2025 holdout slice has only 19 RB rows and no VOR denominator.
- The requested Gibbs/Achane/Chase Brown current-player read cannot be fully validated in this historical feature slice because those current board rows are absent from the 2024/2025 backtest rows used here.

## Rejected Formulas

- `standard_rb_high_value_opportunity_v0`: stronger 2021-2025 VOR context, but weaker 2024 NDCG and more elite misses.
- `standard_rb_source_only_v0`: useful diagnostic, but no 2024 top-12 lift and weaker pairwise than the selected formula.
- `standard_rb_conservative_anchor_v0`: stable and close to Current Pigskin, but does not create a strong episode point.
- `standard_rb_pigskin_opportunity_blend_v0`: modest points lift, but no top-12 or pairwise advantage in 2024.
- `standard_rb_receiving_aware_v0`: small 2024 pairwise lift, but weaker than the selected elite receiving-back formula for the stated Gibbs/Achane protection theme.

## Player-Level Audit

The required current-player audit is partly blocked by the historical feature slice. Most named 2026 players are not present in the 2024 validation or 2025 holdout rows. Available player-level rows:

| Season | Player | Current proxy RB rank | Candidate RB rank | Actual finish | Delta | Reason | Manual review |
|---|---|---:|---:|---:|---:|---|---|
| 2025 | Christian McCaffrey | 2 | 1 | 7 | -1 | receiving value, weighted opportunity, red-zone/goal-line | False |
| 2025 | Derrick Henry | 1 | 2 | 2 | 1 | weighted opportunity, red-zone/goal-line | False |

Named audit players absent from the available validation/holdout feature slice:

- Ashton Jeanty
- Bijan Robinson
- Breece Hall
- Cam Skattebo
- Chase Brown
- Christian McCaffrey
- De'Von Achane
- Derrick Henry
- Jahmyr Gibbs
- Jaylen Warren
- Jonathan Taylor
- Josh Jacobs
- Kyren Williams
- Omarion Hampton
- Saquon Barkley


## Gibbs/Achane/Chase Brown Read

The selected formula is directionally built for Gibbs/Achane protection because it keeps 50% Current Pigskin anchor, 20% weighted opportunity, and 15% receiving value. However, this phase cannot claim a verified Gibbs, Achane, or Chase Brown historical finish read because those players are absent from the available 2024/2025 Standard RB feature slice used for the sprint audit.

Episode-safe wording: this formula is a transparent receiving-back protection concept that tested better than Current Pigskin on 2024 top-12 hit and pairwise rate, not a live RB board replacement.

## Current Pigskin Status

Current Pigskin still holds for Standard RB live use.

The selected formula is episode-ready only. It is not owner-review ready and not live-ready.

## No-Live-Change Confirmations

- No live rankings were written.
- No champion was activated.
- No deployment occurred.
- No model was trained.
- No Gemini or Pigskin chat call occurred.
- No top-100 board was built.
- No 2026 outcomes were used.
- Route metrics remain blocked.

## Checks

Passed:

- `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract`: 26 tests passed.
- `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py`: passed.
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: passed, 251 validation files discovered.
- Focused Standard RB formula check: passed.
- Focused leakage check: passed.
- Focused route-metrics blocked check: passed.
- `git diff --check`: passed with CRLF warnings on existing docs.

## Remaining Warnings

- Source-window-safe Standard RB rows begin at 2021, not 2017.
- 2025 holdout has only 19 RB rows and no VOR captured metric.
- The formula board is latest historical-review evidence, not a live 2026 board.
- Required current-player audit names are mostly absent from the available validation/holdout feature slice.

## Recommended Next Phase

Phase 33.33 should run a Standard WR or Standard QB formula sprint, or hold an owner review of the Standard RB episode concept with the source-slice warnings above.
