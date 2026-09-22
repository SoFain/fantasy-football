# Phase 35.8: Standard QB Guarded BQML and QB Fable v1 Review

## Final decision

**GUARDED BQML 80/20 READY FOR OWNER-REVIEW BOARD; QB FABLE V1 NOT READY TO REPLACE LIVE FORMULA**

No ranking rows were written. No model was trained. No champion was activated. No deployment, LLM call, Pigskin prompt, Sleeper API call, ingestion, or materialization occurred.

## Scope

This phase tested two Standard QB challenger paths:

- a guarded blend of the current deterministic Pigskin candidate with existing advanced BQML signals;
- the owner-supplied QB Fable v1 formula, copied to `docs/rebuild/qb_fable_v1_ranking_formula.md` and implemented as a read-only historical backtest.

The live Standard QB board was not changed. It remains the older Flash-generated board documented in Phase 35.7.

## Source mapping for QB Fable v1

The backtest uses source-backed fields from `raw_nflverse_pbp.raw_payload_json`:

| Formula input | Source-backed implementation |
|---|---|
| Rush attempts per game | QB rush attempts excluding kneels |
| Non-garbage dropbacks | `qb_dropback=1` with win probability from 5% through 95% |
| Red-zone rush attempts | QB rushes at or inside the opponent 20 |
| EPA per dropback | `qb_epa`, including sacks and interceptions |
| CPOE | `cpoe` on pass attempts |
| Inverse sack rate | Negative sacks per dropback |
| Rush yards per attempt | QB rushing yards divided by non-kneel attempts |
| Passing TD regression | Attempts, red-zone attempts, and observed passing touchdowns |
| Rushing TD regression | Goal-to-go attempts and observed rushing touchdowns |
| Age | `player_rosters.birth_date` |
| Availability | Games with recorded QB dropbacks divided by 17 |
| Standard target | `analytics_player_fantasy_points_by_profile`, `standard` |

Verified starts were not available in the audited source path. The test therefore uses the formula's alternative qualification of at least 200 input-season dropbacks. Target seasons require at least six scored games. The availability term is a games-active proxy, not verified starts.

## QB Fable v1 backtest

Query job: `95ac6100-5a57-4811-8666-390e31a0bd1e`

Each fold compares QB Fable v1 with prior-year Standard points per game on the exact same qualified cohort.

| Input -> target | Candidate | QBs | Spearman | Top 5 | Top 12 | Top-12 points captured | Mean rank error |
|---|---|---:|---:|---:|---:|---:|---:|
| 2022 -> 2023 | Prior-year PPG | 25 | 0.4985 | 0.40 | 0.5833 | 0.9161 | 5.68 |
| 2022 -> 2023 | QB Fable v1 | 25 | 0.5131 | 0.60 | 0.6667 | 0.9358 | 5.68 |
| 2023 -> 2024 | Prior-year PPG | 27 | 0.4664 | 0.60 | 0.5000 | 0.8697 | 6.07 |
| 2023 -> 2024 | QB Fable v1 | 27 | 0.5519 | 0.60 | 0.5000 | 0.8756 | 5.85 |
| 2024 -> 2025 | Prior-year PPG | 29 | 0.3305 | 0.20 | 0.5833 | 0.9308 | 8.00 |
| 2024 -> 2025 | QB Fable v1 | 29 | 0.2901 | 0.20 | 0.5000 | 0.9195 | 8.07 |

QB Fable v1 adds value in the first two folds. It fails the most recent holdout. The 2025 fold is worse than the simple same-cohort control in correlation, top-12 precision, captured points, and mean rank error.

The formula also assigns roughly 39% of its positive weight to rushing-linked inputs. That construction needs an explicit rushing-bias tripwire in any later revision. The exact formula is not a promotion candidate.

## Guarded BQML blend

The guarded runner uses the existing advanced Standard QB linear-points and logistic-bust models. It ranks their SQL predictions and blends those ranks with the current deterministic Pigskin candidate. Heavy set operations remain in BigQuery.

Tested weights:

| Candidate | Correlation | Top 12 | Captured points | VOR captured | Regret | Pairwise | Max move | Moves over 3 | Rushing-only risers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Current Pigskin candidate | 0.5217 | 0.6806 | 0.8189 | 0.7597 | 878.58 | 0.6404 | 0 | 0 | 0 |
| Guarded consensus 90/10 | 0.5257 | 0.6782 | 0.8181 | not improved | 890.06 | 0.6424 | 2 | 0 | 0 |
| Guarded consensus 85/15 | 0.5280 | 0.6806 | 0.8208 | 0.7590 | 881.14 | 0.6428 | 3 | 0 | 0 |
| Guarded consensus 80/20 | **0.5335** | **0.6852** | **0.8241** | **0.7640** | **862.90** | **0.6454** | 3 | 0 | 0 |

The `80/20` consensus is the best guarded option tested. Relative to the control, it improves correlation by 0.0119, top-12 hit rate by 0.0046, captured points by 0.0053, VOR captured by 0.0043, and regret by 15.68 points. Every move remains within three ranks. No rushing-only riser was detected.

Relevant `80/20` jobs:

- summary: `ae3d4eec-9e28-470d-ad6f-fa6b8664d662`
- movement: `aa9877f1-4299-462c-ad80-c3d10c272d2d`

The raw BQML models have higher aggregate correlations near 0.55, but move players by as many as 17 ranks. They remain unsuitable as direct ranking replacements.

## Files added or changed

- `docs/rebuild/qb_fable_v1_ranking_formula.md`
- `scripts/run_qb_fable_v1_backtest.py`
- `scripts/run_standard_qb_guarded_bqml_blend.py`
- `tests/test_qb_fable_v1.py`
- `tests/test_standard_qb_guarded_bqml_blend.py`
- `docs/rebuild/validation/phase-35-7-standard-qb-formula-audit-report.md`
- `docs/rebuild/validation/phase-35-8-standard-qb-guarded-bqml-and-fable-v1-report.md`

## Recommendation

Build one read-only 2026 Standard QB owner-review board using `guarded_consensus_80_20`. Show the deterministic control rank, proposed rank, movement, linear signal, logistic signal, passing EPA, CPOE, and rushing baseline. Keep a hard movement cap of three ranks.

Retain QB Fable v1 as a research lane. A later v1.0a should reduce the direct rushing allocation and test whether EPA, CPOE, sack avoidance, and TD regression improve the guarded consensus. Do not promote QB Fable v1 or either raw BQML model.
