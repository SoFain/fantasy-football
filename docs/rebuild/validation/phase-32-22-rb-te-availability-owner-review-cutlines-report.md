# Phase 32.22: RB/TE Availability Modifier Owner-Review Cutline Analysis

Final decision: AVAILABILITY MODIFIER SHOULD REMAIN RISK FLAG

## Scope

Phase 32.22 converted the Phase 32.21 low-weight injury and availability signal into owner-readable RB and TE cutline evidence.

This was not a live ranking phase. No production deploy occurred. No live rankings were regenerated. No champion formulas were activated. No Pigskin chat, Gemini, LLM ranking generation, live Sleeper API, materialization, old Python tournament path, persistent detail rows, or global truncation occurred.

## Git State

Before analysis:

- Latest relevant commit: `a9240fe phase 32.21 test injury availability modifiers`.
- Working tree had only the known untracked historical validation backlog.

After analysis:

- Changed files are limited to scorecard, matrix, and this report.
- Historical validation backlog remains untracked and unstaged.

## Evidence Rows Verified

Run prefix: `ranking_backtest_sql_native_injury_availability_modifier_v0`

| Check | Expected | Actual |
|---|---:|---:|
| `ranking_backtest_runs` | 4 | 4 |
| `ranking_backtest_candidate_summaries` | 284 | 284 |
| New injury-availability summary rows | 60 | 60 |
| `ranking_backtest_results` for this run prefix | 0 | 0 |
| `ranking_formula_champions` | 0 | 0 |

## Candidates Evaluated

Primary owner-review candidates:

- RB: `rb_current_pigskin_pbp_availability_blend_v0`
- TE: `te_current_pigskin_stats02_availability_blend_v0`

Context only:

- `current_pigskin_availability_blend_03_v0`
- `current_pigskin_injury_penalty_cap_v0`

Rejected for owner-review in this phase:

- `current_pigskin_availability_blend_05_v0`, rejected as default due to over-penalization risk.
- WR availability modifiers, rejected because pairwise remained fragile.

## RB Cutline Results

Profile-average deltas versus current Pigskin:

| Slice | Cutline | Pairwise delta | High-conf delta | Top-N delta | Captured delta | Bust delta | Regret delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2017-2025 aggregate | RB6 | -0.0022 | +0.0009 | +0.0021 | -0.0006 | +0.0026 | +12.05 |
| 2017-2025 aggregate | RB12 | -0.0029 | +0.0005 | -0.0011 | -0.0012 | +0.0028 | -2.97 |
| 2017-2025 aggregate | RB24 | -0.0025 | +0.0009 | -0.0015 | -0.0019 | +0.0015 | +49.57 |
| 2024 validation | RB6 | -0.0082 | -0.0045 | -0.0116 | -0.0168 | +0.0139 | +30.98 |
| 2024 validation | RB12 | -0.0075 | -0.0035 | -0.0058 | -0.0042 | +0.0069 | +3.79 |
| 2024 validation | RB24 | -0.0067 | -0.0021 | -0.0093 | -0.0122 | +0.0081 | +45.64 |
| 2025 holdout | RB6 | -0.0007 | +0.0131 | +0.0023 | -0.0005 | +0.0023 | 0.00 |
| 2025 holdout | RB12 | +0.0003 | +0.0105 | -0.0012 | -0.0007 | 0.0000 | 0.00 |
| 2025 holdout | RB24 | -0.0007 | +0.0115 | 0.0000 | 0.0000 | 0.0000 | 0.00 |

Read: RB does not pass position-cutline owner-review threshold. The 2024 validation slice weakens pairwise, captured points, and bust rate. The 2025 holdout is acceptable but not enough to override validation damage.

## TE Cutline Results

Profile-average deltas versus current Pigskin:

| Slice | Cutline | Pairwise delta | High-conf delta | Top-N delta | Captured delta | Bust delta | Regret delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2017-2025 aggregate | TE3 | +0.0015 | +0.0003 | -0.0185 | -0.0112 | +0.0095 | +78.75 |
| 2017-2025 aggregate | TE6 | +0.0014 | -0.0006 | -0.0011 | -0.0001 | -0.0047 | +5.81 |
| 2017-2025 aggregate | TE12 | +0.0020 | +0.0009 | +0.0024 | +0.0041 | -0.0057 | -27.46 |
| 2024 validation | TE3 | +0.0032 | +0.0042 | 0.0000 | +0.0142 | -0.0278 | -15.10 |
| 2024 validation | TE6 | +0.0007 | -0.0033 | -0.0185 | -0.0169 | 0.0000 | +28.13 |
| 2024 validation | TE12 | -0.0137 | -0.0106 | -0.0208 | -0.0220 | +0.0220 | +26.78 |
| 2025 holdout | TE3 | +0.0145 | +0.0164 | -0.0370 | -0.0084 | +0.0046 | +6.87 |
| 2025 holdout | TE6 | +0.0082 | +0.0087 | +0.0093 | +0.0108 | -0.0116 | -12.97 |
| 2025 holdout | TE12 | +0.0025 | +0.0030 | -0.0035 | +0.0021 | 0.0000 | -3.42 |

Read: TE has a better owner-review story than RB, especially at TE6 and TE12 in aggregate and 2025 holdout. It still fails a clean challenger threshold because 2024 TE12 weakened and TE3 is unstable.

## Overall Cutlines

Profile-average deltas versus current Pigskin:

| Slice | Candidate | Overall cutline | Overall pairwise delta | Top-N delta | Captured delta | Bust delta | Regret delta |
|---|---|---:|---:|---:|---:|---:|---:|
| 2017-2025 aggregate | RB modifier | top 24 | +0.0115 | +0.0243 | +0.0299 | -0.0340 | -394.88 |
| 2017-2025 aggregate | RB modifier | top 50 | +0.0080 | +0.0128 | +0.0160 | -0.0181 | -290.26 |
| 2017-2025 aggregate | RB modifier | top 100 | +0.0036 | +0.0040 | +0.0029 | -0.0008 | +346.22 |
| 2024 validation | RB modifier | top 24 | +0.0078 | +0.0203 | +0.0273 | -0.0347 | -79.24 |
| 2025 holdout | RB modifier | top 24 | +0.0090 | 0.0000 | +0.0040 | -0.0098 | -53.23 |
| 2017-2025 aggregate | TE modifier | top 24 | +0.0007 | 0.0000 | -0.0001 | -0.0001 | +6.45 |
| 2024 validation | TE modifier | top 24 | +0.0018 | 0.0000 | 0.0000 | 0.0000 | 0.00 |
| 2025 holdout | TE modifier | top 24 | -0.0002 | -0.0017 | -0.0016 | +0.0012 | +10.64 |

Read: RB is more interesting as an overall draft-board nudge than as an RB-only board. TE is mostly neutral in overall cuts because TE movement rarely changes the top of the full board.

## Player Movement Examples

Examples are read-only snapshots from 2024 validation and 2025 holdout. Explanations use only available fields.

| Case | Player | Slice | Movement | Actual read | Factual reason |
|---|---|---|---|---|---|
| RB useful riser | Kenneth Walker | 2024 PPR | RB14 to RB12 | actual RB2 in sampled row | Strong `high_value_rush_xfp_score_3yr` at 4.28. Injury fields missing, so this is mostly PBP xFP movement. |
| RB harmful faller | Brian Robinson | 2024 PPR | RB12 to RB16 | actual RB4 in sampled row | RB xFP 1.61. Injury fields missing, so the modifier pushed down a real hit without injury support. |
| RB holdout riser | Kareem Hunt | 2025 PPR | RB13 to RB12 | actual RB12 or RB14 in examples | Availability 97.5, burden 8.7, rush xFP 3.24. This is explainable. |
| RB holdout hit lost | Bam Knight | 2025 PPR | RB12 to RB13 | actual RB4 in examples | Availability 55.0 and burden 18.0 penalized a player who hit. This is the clearest caution. |
| TE useful riser | Dallas Goedert | 2025 PPR | TE7 to TE6 | actual TE2 and TE3 examples | Availability 96.8, burden 9.3, receiving role xFP 26.42. |
| TE useful riser | David Njoku | 2025 PPR | TE7 to TE6 | actual TE4 example | Availability 87.1, burden 11.6, receiving role xFP 29.20. |
| TE harmful faller | Taysom Hill | 2025 PPR | TE5 to TE8 | mixed, including actual TE15 and one TE2 example | Availability 90.8, burden 10.3, receiving role xFP 16.42. Movement is not consistently right. |
| TE bust avoided | Jake Ferguson | 2024 GNG/Standard | TE11 or TE12 to TE18/TE19 | actual TE26 to TE32 examples | Receiving role xFP 15.60, injury fields missing. Avoided bust rows, but also had hit-lost Ferguson rows. |
| TE false negative | Noah Gray | 2024 Half/GNG/Standard | TE29 to TE36 | actual TE3 examples | Injury fields missing, receiving role xFP 8.07. Modifier missed a spike. |
| TE false positive | Tyler Conklin | 2024 PPR/Half | TE17 or TE18 to TE11/TE12 | actual TE30 or TE38 | Availability 92.5, burden 9.7, receiving role xFP 21.57. Safe-looking context did not prevent a miss. |

Event counts:

| Slice | Position | Event | Count |
|---|---|---|---:|
| 2024 validation | RB | crossed into RB12 | 36 |
| 2024 validation | RB | crossed out of RB12 | 36 |
| 2024 validation | RB | false positive candidate | 133 |
| 2024 validation | RB | hit lost starter | 22 |
| 2024 validation | TE | bust avoided starter | 45 |
| 2024 validation | TE | crossed into TE6 | 18 |
| 2024 validation | TE | crossed out of TE6 | 18 |
| 2024 validation | TE | false positive candidate | 257 |
| 2025 holdout | RB | crossed into RB12 | 14 |
| 2025 holdout | RB | crossed out of RB12 | 14 |
| 2025 holdout | TE | crossed into TE6 | 7 |
| 2025 holdout | TE | crossed out of TE6 | 7 |
| 2025 holdout | TE | false positive candidate | 4 |
| 2025 holdout | TE | hit lost starter | 5 |

## Owner-Review Recommendation

Status labels:

- RB modifier: `use as risk flag only`.
- TE modifier: `use as risk flag only`.
- WR modifier: `reject`.
- Generic 5 percent availability blend: `reject as default`.

Reason: neither RB nor TE passes the full owner-review challenger threshold. Both are explainable as small risk-adjustment signals, but not stable enough for champion selection or live ranking activation.

## Files Changed

- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/validation/phase-32-22-rb-te-availability-owner-review-cutlines-report.md`

## Checks Run

- Read-only BigQuery evidence count checks.
- Read-only SQL-native cutline analysis for RB6/RB12/RB18/RB24/RB36, TE3/TE6/TE12/TE18, top 24/top 50/top 100.
- Read-only player movement event queries for 2024 validation and 2025 holdout.
- `git diff --check`

No source code changed, so no Python tests were required for this docs and read-only SQL phase.

## Scorecard And Matrix Updates

Scorecard update:

- Added Phase 32.22 owner-review cutline section.
- Added RB and TE cutline result tables.
- Added validation and holdout separation.
- Added player movement summary and decision status.
- Confirmed no champion active.

Matrix update:

- Added usage read for availability, injury burden, missed-time risk, RB xFP, TE receiving role xFP, depth, and Sleeper current context.
- Classified RB and TE availability as risk flags only.
- Reconfirmed depth remains blocked.

## Remaining Warnings

- RB movement is partly an xFP story, not a pure injury-availability story.
- TE movement is useful around TE6/TE12, but top-end TE3 and 2024 TE12 are unstable.
- Several movement examples have missing injury fields. The system does not fabricate those values.
- Overall draft-board gains for RB do not translate into clean RB position-board gains.

## Recommended Next Phase

Recommended next phase: Phase 32.23, build an owner-review formula comparison dashboard or report view that shows current Pigskin, RB risk flag, TE risk flag, and movement explanations side by side.

Alternative: Phase 32.23, BQML retrain with ideal, PBP, injury, and role context if the owner wants a model lane before dashboard work.
