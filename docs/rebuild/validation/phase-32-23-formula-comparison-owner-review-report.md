# Phase 32.23: Formula Comparison Owner-Review Report

Final decision: FORMULA COMPARISON OWNER REVIEW READY WITH WARNINGS

## Scope

Phase 32.23 created a lightweight owner-review formula comparison view from existing SQL-native summary evidence and bounded read-only BigQuery queries.

No production deploy occurred. No live rankings were regenerated. No champion formulas were activated. No Pigskin chat, Gemini, LLM-backed ranking generation, live Sleeper API, materialization, old Python full tournament path, persistent detail rows, global truncation, source ingest, or weight tuning occurred.

## Git State

Before this phase:

- Latest commit: `c89ddb1 phase 32.22 document availability cutlines`
- Worktree: only the standing untracked historical validation backlog was present.

After this phase:

- Files changed:
  - `docs/rebuild/validation/phase-32-23-formula-comparison-owner-review-report.md`
  - `docs/rebuild/ranking-algorithm-scorecard.md`
  - `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- Commit hash: recorded after commit if this report is committed.

## Candidate Groups Reviewed

| Group | Status label | Read |
|---|---|---|
| Current Pigskin candidate score v1 | live baseline | Remains the live deterministic baseline. |
| Simple projection | strong challenger | Useful and low-missing, but no longer beats current Pigskin on the latest aggregate summary. |
| BQML logistic elite | strong challenger | Best BQML top-N/VOR challenger in Phase 32.10, not a champion. |
| BQML linear points | strong challenger | Strong high-confidence and overall pairwise BQML lane, not a champion. |
| Scarcity adjusted draft value | context only | Helpful context, weaker than current Pigskin on latest aggregate. |
| Value over replacement baseline | context only | Stable context, not a replacement signal. |
| Stats02 WR/TE ideal lanes | owner-review concept | WR and TE have position-specific signal, but current Pigskin still protects more aggregate utility. |
| PBP RB/WR refined lanes | owner-review concept | RB shows useful short-window signal. WR helps captured points in places but hurts pairwise. |
| RB availability modifier | risk flag only | Explains risk and can move cutlines, but Phase 32.22 failed owner-review challenger threshold. |
| TE availability modifier | risk flag only | Better than RB on selected TE cutlines, still unstable. |
| WR availability modifier | deferred | Pairwise fragility keeps it out of owner-review challenger status. |
| Generic 5 percent availability blend | rejected | Rejected as default due to over-penalization risk. |
| Trend-aware v2, broad ensembles, injury-only candidates, deep VOR policy | rejected or context only | Not activation-ready. |
| Historical depth role context | blocked | No approved historical depth source exists yet. |
| Sleeper current context | context only | Live display aid only. Not historical backtest input. |

## Aggregate Comparison

Latest stored SQL-native summary evidence, averaged across available profile-position rows. These are not new tournament writes.

Metric sanity addendum:

| Report metric | Extraction path used | Verification read |
|---|---|---|
| Pairwise win rate | `ranking_backtest_candidate_summaries.pairwise_win_rate` | Correct for the stored summary contract. For SQL-native Phase 32.21/32.23 rows, this top-level field is populated from the high-confidence pairwise calculation. |
| High-confidence pairwise win rate | `JSON_VALUE(metric_json, '$.high_confidence_pairwise_win_rate')` | Correct. Identical values versus top-level pairwise are expected for the sampled SQL-native rows because both fields are sourced from the same pairwise CTE. |
| Overall pairwise draft win rate | `JSON_VALUE(metric_json, '$.overall_pairwise_draft_win_rate')` | Correct. Present in sampled rows. |
| Top-N hit rate | `ranking_backtest_candidate_summaries.top_n_hit_rate` | Correct top-level column. |
| Captured points | `ranking_backtest_candidate_summaries.actual_points_captured_rate` | Correct top-level column. |
| VOR captured | `JSON_VALUE(metric_json, '$.value_over_replacement_captured_rate')` | Correct. Present in sampled rows. |
| NDCG@K | `JSON_VALUE(metric_json, '$.ndcg_at_k')` | Correct. Present in sampled rows. |
| Bust rate | `JSON_VALUE(metric_json, '$.bust_rate')` | Correct. Present in sampled rows. |
| Missing-input rate | `ranking_backtest_candidate_summaries.missing_input_rate` | Correct top-level column. |

Read-only verification sampled the latest current Pigskin, Stats02, RB availability, and TE availability summary rows. Result: 40 of 40 sampled rows had top-level `pairwise_win_rate` equal to `metric_json.high_confidence_pairwise_win_rate`, and all sampled rows had overall pairwise, VOR captured, NDCG@K, and bust rate populated. That means the Phase 32.23 table paths are valid, but top-level pairwise and high-confidence pairwise should not be treated as independent signals for these SQL-native stored summaries.

| Candidate | Status | Evidence rows | Positions | Profiles | Pairwise | High-conf | Overall pairwise | Top-N | Captured | VOR captured | NDCG | Tier acc | Bust | Missing |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Current Pigskin | live baseline | 16 | QB/RB/TE/WR | all four | 0.7385 | 0.7385 | 0.7455 | 0.5411 | 0.7132 | 0.6007 | 0.6578 | 0.4307 | 0.1592 | 0.0050 |
| Simple projection | strong challenger | 16 | QB/RB/TE/WR | all four | 0.7238 | 0.7238 | 0.7262 | 0.5399 | 0.7121 | 0.5970 | 0.6587 | 0.4353 | 0.1601 | 0.0000 |
| Stats02 position ideal | owner-review concept | 16 | QB/RB/TE/WR | all four | 0.7372 | 0.7372 | 0.5577 | 0.5357 | 0.7047 | 0.5840 | 0.6477 | 0.4306 | 0.1642 | 0.0112 |
| Stats02 WR ideal | owner-review concept | 4 | WR | all four | 0.7596 | 0.7596 | 0.7470 | 0.4937 | 0.6807 | 0.5668 | 0.6188 | 0.3699 | 0.2220 | 0.0125 |
| Stats02 TE ideal | owner-review concept | 4 | TE | all four | 0.7326 | 0.7326 | 0.7500 | 0.4577 | 0.6301 | 0.5211 | 0.5846 | 0.4190 | 0.2673 | 0.0192 |
| PBP RB refined | owner-review concept | 4 | RB | all four | 0.7263 | 0.7263 | 0.7307 | 0.6059 | 0.7317 | 0.6210 | 0.6559 | 0.4035 | 0.0963 | 0.0226 |
| PBP WR dominance blend | owner-review concept | 4 | WR | all four | 0.7393 | 0.7393 | 0.7297 | 0.4901 | 0.6761 | 0.5594 | 0.6136 | 0.3656 | 0.2247 | 0.0154 |
| RB availability modifier | risk flag only | 4 | RB | all four | 0.7505 | 0.7505 | 0.7550 | 0.6152 | 0.7423 | 0.6336 | 0.6654 | 0.4136 | 0.0838 | 0.0174 |
| TE availability modifier | risk flag only | 4 | TE | all four | 0.7536 | 0.7536 | 0.7808 | 0.4672 | 0.6441 | 0.5496 | 0.6027 | 0.4267 | 0.2602 | 0.0166 |
| WR availability modifier | deferred | 4 | WR | all four | 0.7664 | 0.7664 | 0.7624 | 0.5030 | 0.6940 | 0.5923 | 0.6333 | 0.3735 | 0.2117 | 0.0163 |
| Availability 5 percent blend | rejected | 16 | QB/RB/TE/WR | all four | 0.7344 | 0.7344 | 0.4884 | 0.5363 | 0.7078 | 0.5922 | 0.6546 | 0.4293 | 0.1625 | 0.0197 |

Read: the latest persisted aggregate summary does not support replacing current Pigskin. Simple projection is still a clean challenger lane, but current Pigskin is ahead on pairwise, high-confidence, overall pairwise, captured points, and VOR captured.

## 2024 Validation Window

| Lane | 2024 validation read |
|---|---|
| BQML logistic elite | Top-N 0.5165, captured 0.7073, VOR 0.5888, high-confidence 0.7445, overall pairwise 0.5096, NDCG 0.6501, bust 0.1641. Strong enough for review, weak on overall pairwise. |
| BQML linear points | Top-N 0.5120, captured 0.7035, VOR 0.5839, high-confidence 0.9245, overall pairwise 0.6914, NDCG 0.6471, bust 0.1671. Best BQML high-confidence read. |
| RB PBP refined | Phase 32.17 improved RB pairwise in PPR, Half PPR, and GNG Keeper, but aggregate 2017-2025 later weakened versus current Pigskin. |
| WR PBP refined | Phase 32.17 improved captured points in places, but pairwise weakened across profiles. |
| RB availability | Phase 32.22 showed validation cutline damage: RB6 pairwise -0.0082, RB12 -0.0075, RB24 -0.0067 versus current Pigskin. |
| TE availability | Phase 32.22 showed mixed validation: TE3 +0.0032, TE6 +0.0007, TE12 -0.0137. |

Read: validation is the reason availability stays out of formula-default status. BQML has the cleaner challenger story, but it is not enough to replace the baseline.

## 2025 Holdout Window

| Lane | 2025 holdout read |
|---|---|
| BQML logistic elite | Top-N 0.8558, captured 0.9030, VOR 0.8555, high-confidence 0.7492, overall pairwise 0.7715, NDCG 0.7814, tier accuracy 0.7060, bust 0.0012. |
| BQML linear points | Top-N 0.8510, captured 0.8973, VOR 0.8461, high-confidence 0.8927, overall pairwise 0.9441, NDCG 0.7709, tier accuracy 0.6990, bust 0.0012. |
| RB PBP refined | Phase 32.17 improved RB pairwise in all four profiles, but 2017-2025 aggregate did not hold. |
| WR PBP refined | Phase 32.17 improved WR captured points, but pairwise stayed weaker than current Pigskin. |
| RB availability | Phase 32.22 holdout was acceptable but not enough to override validation damage: RB12 pairwise +0.0003, RB18 captured +0.0025, RB24 flat. |
| TE availability | Phase 32.22 holdout looked useful at TE cutlines: TE3 +0.0145, TE6 +0.0082, TE12 +0.0025. Overall draft-board TE deltas were slightly weaker. |

Read: 2025 is tempting for BQML and TE availability, but this project should not tune to the 2025 holdout. The owner-review table keeps validation and holdout separate for that reason.

## Position Views

### QB

| Candidate | Status | Pairwise | Top-N | Captured | VOR captured | NDCG | Bust | Missing | Read |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Current Pigskin | live baseline | 0.6871 | 0.5765 | 0.7703 | 0.6237 | 0.7259 | 0.0819 | 0.0022 | Baseline remains acceptable. |
| Stats02 position ideal | owner-review concept | 0.7172 | 0.5795 | 0.7686 | 0.6202 | 0.7280 | 0.0833 | 0.0002 | Strong pairwise signal. Needs owner review before any formula work. |
| PBP QB diagnostic | context only | 0.7012 | 0.5746 | 0.7669 | 0.6192 | 0.7291 | 0.0821 | 0.0018 | Useful context, not a direct champion lane. |
| Simple projection | strong challenger | 0.6815 | 0.5730 | 0.7680 | 0.6186 | 0.7273 | 0.0783 | 0.0000 | Clean but not better than current Pigskin. |

### RB

| Candidate | Status | Pairwise | Top-N | Captured | VOR captured | NDCG | Bust | Missing | Read |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Current Pigskin | live baseline | 0.7485 | 0.6167 | 0.7440 | 0.6358 | 0.6654 | 0.0823 | 0.0054 | Baseline remains strong. |
| Simple projection | strong challenger | 0.7413 | 0.6234 | 0.7500 | 0.6454 | 0.6805 | 0.0812 | 0.0000 | Helps captured/VOR, slightly weaker pairwise. |
| RB availability modifier | risk flag only | 0.7505 | 0.6152 | 0.7423 | 0.6336 | 0.6654 | 0.0838 | 0.0174 | Risk flag only because validation cutlines were weaker. |
| PBP RB diagnostic | context only | 0.7510 | 0.6170 | 0.7448 | 0.6390 | 0.6713 | 0.0864 | 0.0221 | Good component evidence, not elevated. |
| PBP RB refined | owner-review concept | 0.7263 | 0.6059 | 0.7317 | 0.6210 | 0.6559 | 0.0963 | 0.0226 | Useful short-window evidence, weak aggregate. |
| Scarcity adjusted | context only | 0.7343 | 0.6259 | 0.7542 | 0.6463 | 0.6738 | 0.0709 | 0.0303 | Context, not a champion. |

### WR

| Candidate | Status | Pairwise | Top-N | Captured | VOR captured | NDCG | Bust | Missing | Read |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Current Pigskin | live baseline | 0.7680 | 0.5066 | 0.6978 | 0.5971 | 0.6371 | 0.2068 | 0.0069 | Baseline clearly protects pairwise. |
| Stats02 WR ideal | owner-review concept | 0.7596 | 0.4937 | 0.6807 | 0.5668 | 0.6188 | 0.2220 | 0.0125 | Useful signal, not better than current. |
| PBP WR dominance blend | owner-review concept | 0.7393 | 0.4901 | 0.6761 | 0.5594 | 0.6136 | 0.2247 | 0.0154 | Pairwise too weak for activation. |
| WR availability modifier | deferred | 0.7664 | 0.5030 | 0.6940 | 0.5923 | 0.6333 | 0.2117 | 0.0163 | Close to baseline, still deferred by Phase 32.22 policy. |
| Simple projection | strong challenger | 0.7396 | 0.4979 | 0.6907 | 0.5877 | 0.6306 | 0.2149 | 0.0000 | Clean but weaker. |

### TE

| Candidate | Status | Pairwise | Top-N | Captured | VOR captured | NDCG | Bust | Missing | Read |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Current Pigskin | live baseline | 0.7505 | 0.4648 | 0.6405 | 0.5463 | 0.6026 | 0.2658 | 0.0057 | Baseline remains the formula default. |
| TE availability modifier | risk flag only | 0.7536 | 0.4672 | 0.6441 | 0.5496 | 0.6027 | 0.2602 | 0.0166 | Useful risk signal, not stable enough for default ranking. |
| Stats02 TE ideal | owner-review concept | 0.7326 | 0.4577 | 0.6301 | 0.5211 | 0.5846 | 0.2673 | 0.0192 | Useful context, weaker than current. |
| PBP TE diagnostic | context only | 0.7291 | 0.4570 | 0.6318 | 0.5274 | 0.5793 | 0.2715 | 0.0195 | Context only. |
| Simple projection | strong challenger | 0.7326 | 0.4652 | 0.6398 | 0.5362 | 0.5964 | 0.2661 | 0.0000 | Clean but weaker. |

## Overall Draft Board

| Candidate | Status | Owner read |
|---|---|---|
| Current Pigskin | live baseline | Best current default because it remains broadly strong and already powers live rankings. |
| Simple projection | strong challenger | Keep in the comparison set. It is clean and low-missing but does not separate enough. |
| Scarcity adjusted draft value | context only | Helpful for selected RB/QB slices and draft-value thinking. Not a default. |
| BQML logistic elite | strong challenger | Best model challenger for top-N, VOR, NDCG, tier accuracy, and bust rate over 2024-2025. Needs retrain with newer ideal/PBP/injury context. |
| BQML linear points | strong challenger | Best BQML overall pairwise/high-confidence read. Worth review after retrain. |
| Deep VOR baseline | context only | Useful policy lens, not a champion path. |

## Movement Examples

| Signal | Example movement read |
|---|---|
| RB availability risk flag | Phase 32.22 moved Kenneth Walker into a 2024 RB12 cutline in a helpful example, but also moved Brian Robinson and James Cook down in validation-hurting cases. |
| TE availability risk flag | Phase 32.22 moved Dallas Goedert and David Njoku into 2025 TE6 examples, but also pushed Taysom Hill out in mixed cases and kept false negatives such as Anthony Firkser. |
| WR PBP/Stats02 | Phase 32.17 improved WR captured points in multiple 2024 and 2025 slices, but weakened pairwise. That is a component signal, not a ranking-default signal. |
| RB PBP | Phase 32.17 improved 2025 RB pairwise in all four profiles, but the 2017-2025 aggregate stayed below current Pigskin. Treat as a future component lane. |

These are evidence summaries from prior phase reports. No new detail rows were written.

## Risk Flags, Not Ranking Formula Defaults

Availability belongs beside rankings before it belongs inside default rankings.

Risk flag candidates:

- `availability_score_3yr`
- `injury_status_score_3yr`
- `injury_burden_score_3yr`
- `missed_time_risk_score_3yr`
- RB availability modifier, risk flag only
- TE availability modifier, risk flag only

Rejected or blocked as formula defaults:

- Generic 5 percent availability blend: rejected as default.
- WR availability modifier: rejected or deferred until it preserves current Pigskin pairwise.
- Historical depth chart role: blocked until a real historical source exists.
- Sleeper current context: live-only display context, not a historical feature.

## Owner Decision Summary

Answers:

- Live baseline: current Pigskin candidate score v1 remains the live baseline.
- Owner-review candidates: BQML logistic elite, BQML linear points, Stats02 WR/TE, QB Stats02, and selected RB/PBP component lanes.
- Useful but not activation-ready: simple projection, scarcity adjusted value, PBP RB/WR, TE availability, RB availability.
- Rejected: generic 5 percent availability default, v2 trend-aware direct champion path, broad ensembles from Phase 32.11, injury-only candidates, historical LLM replay.
- Risk flags only: RB and TE availability, injury burden, missed-time risk.
- Blocked: historical depth context.

Recommended next technical phase:

1. Phase 32.24: BQML retrain with ideal, PBP, injury, and role context.
2. Alternative: direct NGS receiving/rushing ingest if the owner wants source work before model retraining.
3. Alternative: owner review of the strongest challenger lanes before more engineering.

No champion activation is supported by this phase.

## Checks Run

- Read-only BigQuery summary query over `ranking_backtest_candidate_summaries`.
- Read-only metric-path sanity query over sampled latest summary rows.
- Read-only BigQuery confirmation:
  - `ranking_formula_champions`: 0 rows.
  - active `analytics_pigskin_rankings`: 1,140 rows.
- `git diff --check` after documentation edits.

## Remaining Warnings

- BQML evidence is from Phase 32.10, not a retrain with the newer injury/PBP/Stats02 feature refreshes.
- Availability metrics show useful movement, but Phase 32.22 found validation and cutline instability.
- Historical depth remains blocked.
- Current Sleeper context is not a historical backtest source.
- The standing untracked historical validation backlog remains intentionally untouched.
