# Phase 33.12 Standard Overlay Calibration Report

Final decision: STANDARD OVERLAY CONSERVATIVE ANCHOR READY

## Scope

Phase 33.12 calibrated the Phase 33.11 Standard BQML v2 conservative overlay. This phase used read-only BigQuery queries and existing trained Standard BQML v2 models.

No BQML model was trained. No model was created. No live ranking row changed. No champion was activated. No Gemini, Pigskin chat, Sleeper API, source ingest, production ranking generation, deployment, or materialization ran.

## Git State

Phase 33.11 was already committed before calibration:

- `afef1fb phase 33.11 generate standard overlay review board`
- `6d94036 phase 33.11 record overlay package evidence`

Known untracked files remain historical validation backlog and owner-review artifacts. Generated evidence under `output/` was not staged.

Package commit: `69126d2 phase 33.12 calibrate standard overlay guardrails`

## Movement Diagnosis

The Phase 33.11 overlay moved too aggressively because cross-position BQML VOR outputs are not calibrated to the same live 2026 board scale.

Read-only 2026 diagnostics:

| Position | VOR norm avg | VOR norm max | Finalist avg | Avg original rank delta |
|---|---:|---:|---:|---:|
| QB | 0.239 | 1.000 | 0.369 | -8.7 |
| RB | 0.167 | 0.502 | 0.385 | -9.4 |
| WR | 0.049 | 0.153 | 0.158 | 9.6 |
| TE | 0.052 | 0.106 | 0.327 | 5.3 |

QB and RB VOR distributions sit above WR and TE on the global normalized scale. That pushes mobile or high-VOR quarterbacks upward and suppresses early WR/TE names even when Current Pigskin strongly prefers them.

Major original-overlay movers:

| Player | Position | Current rank | Original rank | 80/15/5 rank | Cause |
|---|---|---:|---:|---:|---|
| Jalen Hurts | QB | 34 | 2 | 3 | Maximum VOR and finalist signal. |
| Lamar Jackson | QB | 76 | 22 | 39 | Strong VOR and bust-inverse signal. |
| Daniel Jones | QB | 43 | 12 | 18 | Strong VOR signal relative to Current Pigskin. |
| Kyler Murray | QB | 100 | 48 | 65 | VOR and finalist signal overpower weak current anchor. |
| Saquon Barkley | RB | 49 | 10 | 20 | Strong RB VOR and safety signal. |
| Josh Jacobs | RB | 64 | 26 | 38 | Strong RB VOR and safety signal. |
| Derrick Henry | RB | 91 | 42 | 58 | Strong RB VOR and safety signal. |
| Jaxon Smith-Njigba | WR | 1 | 24 | 13 | Weak WR VOR scale despite top current rank. |
| Drake London | WR | 8 | 29 | 19 | Weak WR VOR scale against stronger current rank. |
| Brock Bowers | TE | 11 | 44 | 31 | Missing feature row and no TE VOR lift. |
| Rashee Rice | WR | 15 | 34 | 23 | WR VOR scale below QB/RB signal. |
| Garrett Wilson | WR | 18 | 31 | 27 | WR VOR scale below QB/RB signal. |

## Calibration Candidates

Family: `standard_bqml_v2_overlay_calibration_v0`.

| Rule | Formula | Read |
|---|---|---|
| `overlay_70_20_10_original_v0` | 70 percent Current Pigskin, 20 percent BQML VOR, 10 percent finalist signal. | Baseline. Too aggressive. |
| `overlay_80_15_5_anchor_v0` | 80 percent Current Pigskin, 15 percent BQML VOR, 5 percent finalist signal. | Best balance in this pass. |
| `overlay_85_10_5_anchor_v0` | 85 percent Current Pigskin, 10 percent BQML VOR, 5 percent finalist signal. | Safest movement, but nearly a Current Pigskin hold. |
| `overlay_rank_delta_cap_20_v0` | Original overlay with movement cap. | Hard to explain because reranking after caps still creates edge cases. |
| `overlay_missingness_gate_v0` | 80/15/5 with high-missingness upward movement capped. | Useful guardrail, but not enough as the whole rule. |
| `overlay_vor_percentile_calibrated_v0` | 80 percent Current Pigskin, 15 percent position-percentile VOR, 5 percent finalist signal. | Fixes QB overload but overcorrects toward WR. |

## 2026 Candidate Comparison

| Rule | Top 24 mix | Top 50 mix | Delta >20 | QB top24 | WR/TE top24 exits | Top24 overlap |
|---|---|---|---:|---:|---:|---:|
| `overlay_70_20_10_original_v0` | QB8, RB8, WR6, TE2 | QB14, RB14, WR15, TE7 | 58 | 8 | 7 | 15 |
| `overlay_80_15_5_anchor_v0` | QB6, RB7, WR9, TE2 | QB13, RB13, WR16, TE8 | 21 | 6 | 4 | 18 |
| `overlay_85_10_5_anchor_v0` | QB5, RB6, WR10, TE3 | QB11, RB12, WR19, TE8 | 10 | 5 | 2 | 21 |
| `overlay_missingness_gate_v0` | QB6, RB7, WR9, TE2 | QB11, RB11, WR20, TE8 | 8 | 6 | 4 | 19 |
| `overlay_vor_percentile_calibrated_v0` | QB3, RB6, WR12, TE3 | QB10, RB12, WR22, TE6 | 71 | 3 | 3 | 19 |

The 80/15/5 anchor is the preferred owner-review rule because it cuts the original movement problem without turning the board into a pure Current Pigskin copy.

The missingness gate is required as a future refinement if this path moves toward champion-selection review. In this pass it reduced extreme movement, but it still needs a cleaner implementation and owner-facing explanation.

## Historical Validation And Holdout

The historical check used 2024 validation and 2025 holdout rows from `ranking_backtest_feature_mart`. It was read-only.

Important caveat: historical Current Pigskin live boards are not available in the same cross-position shape, so `profile_points_score` was used as a Current Pigskin-like proxy. That proxy ranks QBs across the entire top 24 in both 2024 and 2025. It is useful for directional regression checks, not champion-selection proof.

| Year | Rule | Top24 | Top50 | Top100 | Points cap100 | VOR cap100 |
|---:|---|---:|---:|---:|---:|---:|
| 2024 | `current_pigskin_proxy_v0` | 0.708 | 0.900 | 0.980 | 1.000 | 1.000 |
| 2025 | `current_pigskin_proxy_v0` | 0.875 | 1.000 | 1.000 | 1.000 | 1.000 |
| 2024 | `overlay_70_20_10_original_v0` | 0.667 | 0.900 | 0.960 | 0.995 | 1.002 |
| 2025 | `overlay_70_20_10_original_v0` | 0.875 | 1.000 | 1.000 | 0.956 | 0.564 |
| 2024 | `overlay_80_15_5_anchor_v0` | 0.708 | 0.900 | 0.960 | 0.995 | 1.002 |
| 2025 | `overlay_80_15_5_anchor_v0` | 0.875 | 1.000 | 1.000 | 0.968 | 0.747 |
| 2024 | `overlay_85_10_5_anchor_v0` | 0.708 | 0.900 | 0.960 | 0.995 | 1.002 |
| 2025 | `overlay_85_10_5_anchor_v0` | 0.875 | 1.000 | 1.000 | 0.961 | 0.739 |

The 80/15/5 anchor does not create a clear historical regression against the proxy, but the proxy is too QB-heavy to support champion activation.

## 2026 Calibrated Board Summary

Durable board:

- `docs/rebuild/standard-bqml-v2-overlay-calibration.md`

Selected rule: `overlay_80_15_5_anchor_v0`.

Top 24 includes QB6, RB7, WR9, TE2. The early board is safer than Phase 33.11 because elite WRs and Trey McBride remain near the top. Jalen Hurts, Daniel Jones, Saquon Barkley, Josh Jacobs, Lamar Jackson, Travis Etienne, Breece Hall, and Justin Herbert still move more than 20 spots.

The calibrated board is owner-review ready, not champion-selection ready.

## Position Balance And Missingness

Position balance improved materially:

- Original overlay top 24: QB8, RB8, WR6, TE2.
- 80/15/5 top 24: QB6, RB7, WR9, TE2.

Missingness remains a blocker for activation:

- Many active 2026 players carry high predictor missingness because the review board joins active 2026 Current Pigskin rows to latest pre-2026 feature rows.
- High-missingness risers remain present under 80/15/5.
- A future champion-selection candidate should include a formal missingness gate: high-missingness rows cannot rise more than 10 spots unless manually approved.

## Owner Recommendation

Hold Current Pigskin for Standard.

Use `overlay_80_15_5_anchor_v0` as the next owner-review board if the owner wants to inspect a safer BQML-informed Standard board. Do not activate a champion from this phase.

Recommended next phase:

- Phase 33.13: Generate calibrated Standard 2026 review board for dashboard.

Alternate next phase:

- Phase 33.13: Hold Current Pigskin for Standard and move to contract/AAV feature integration.

## Files Changed

- `docs/rebuild/standard-bqml-v2-overlay-calibration.md`
- `docs/rebuild/validation/phase-33-12-standard-overlay-calibration-report.md`
- `docs/rebuild/standard-bqml-v2-2026-conservative-overlay-review-board.md`
- `docs/rebuild/standard-bqml-v2-overall-board-rules.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

## Checks

- `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract`: passed, 19 tests.
- `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py`: passed.
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed.
- `git diff --check`: passed. Git reported LF-to-CRLF working-copy warnings only.

No full test suite was run. This phase changed owner-review docs only and used read-only BigQuery checks.

## No-Live-Change Confirmation

No live ranking rows changed. No champion row was written. No production ranking generation ran. No model was trained.
