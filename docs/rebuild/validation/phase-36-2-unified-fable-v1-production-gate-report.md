# Phase 36.2 Unified Fable v1 Production Gate Report

## Final Decision

`GO FOR GUARDED PRODUCTION MATERIALIZATION; DO NOT REPLACE POSITIONAL RANKS`

The unified Standard top-100 passed the available historical cross-position gate. It should be published as a new overall-board artifact with its own version and rollback history. It must not overwrite the positional `rank` values in `analytics_pigskin_rankings`.

The remaining evidence gaps are disclosed below. They do not block an additive overall board, but they do block claiming that every live positional source was tested in one perfectly matched preseason tournament.

## Forward-Fold Results

Selected replacement setup: QB13 / RB34 / WR40 / TE9.

| Fold | Qualified pool | VORP Spearman | Positive VORP captured at 100 | Top 24 hit | Top 50 hit | Top 100 hit | Mix QB/RB/WR/TE |
|---|---:|---:|---:|---:|---:|---:|---|
| 2022 to 2023 | 260 | 0.664 | 0.934 | 0.458 | 0.640 | 0.760 | 13/36/42/9 |
| 2023 to 2024 | 268 | 0.693 | 0.859 | 0.500 | 0.560 | 0.700 | 13/35/43/9 |
| 2024 to 2025 | 265 | 0.722 | 0.885 | 0.667 | 0.600 | 0.750 | 13/35/43/9 |
| Average | — | **0.693** | **0.893** | **0.542** | **0.600** | **0.737** | stable |

The latest fold is the strongest ordering result. Composition is stable rather than being manufactured by a single season.

## Replacement Sensitivity

| Setup | VORP Spearman | VORP captured | Top 24 | Top 50 | Top 100 |
|---|---:|---:|---:|---:|---:|
| RB34 / TE9 selected | 0.693 | **0.893** | 0.542 | 0.600 | **0.737** |
| RB32 / TE9 | 0.686 | 0.888 | **0.556** | 0.587 | 0.730 |
| RB36 / TE9 | **0.697** | 0.890 | 0.542 | **0.633** | 0.733 |
| RB34 / TE10 | 0.688 | 0.883 | 0.542 | 0.600 | 0.730 |
| RB34 / TE11 | 0.685 | 0.883 | 0.542 | 0.593 | 0.727 |

No adjacent baseline causes a collapse. RB34/TE9 remains the balanced choice because it has the best VORP capture and top-100 coverage while retaining strong correlation.

## Test Coverage

- Fitted curves use only seasons available through each input-season boundary during the forward folds.
- Actual replacement PPG is calculated from the target season at the selected replacement ranks.
- Ideal top-100 comparisons use the full qualified pool, not the selected 100.
- Positional queue order is structural and unit-tested.
- Skip-ahead inside a position raises an error.
- Current board contains exactly 100 unique player IDs.
- Current and historical SQL is read-only.
- No 2026 outcome enters the curve fit or backtest.
- Replacement sensitivity covers RB32/RB34/RB36 and TE9/TE10/TE11.

## Disclosed Gaps

### QB proxy

The active Standard QB queue is guarded BQML 75/25. Its historical evidence is weekly and covers 2024-2025, not the same three prior-season folds used by the Fable position views. The unified three-fold test therefore uses the leakage-safe QB Fable v1 prior-season queue as its QB proxy.

The active guarded QB board has already passed its separate owner-review and promotion checks. This proxy mismatch should remain visible in production metadata.

### Draft-slot simulation

No historical point-in-time ADP series is available for the three folds, so a 12-team snake simulation against historical ADP cannot be run honestly. Current ADP must not be backfilled as a historical opponent.

### Missing source seasons

Returning-player formulas cannot rank a player without a qualified input season. The production board must expose source and warning fields and retain a manual-review lane for missing rookies or other unrankable players. No market splice was invented here.

## Production Contract

The production artifact should be additive and contain:

- `overall_rank`
- `player_id`
- `player_name`
- `current_team`
- `position`
- frozen `position_rank`
- `projected_ppg`
- `replacement_rank` and `replacement_ppg`
- `vorp` and `adjusted_vorp`
- availability and onesie multipliers
- positional source version
- risk flags
- unified board version and generated timestamp

Archive the prior unified version before replacement. Fail closed on duplicate IDs, non-contiguous positional ranks, row count other than 100, or any within-position inversion.

## Checks

- Five focused unit tests passed across the board builder and pooled backtest.
- Deployment safety script passed all checks.
- `git diff --check` passed for the unified files.
- No live table, champion, application service, or scheduler changed in this phase.

## Files

- `scripts/build_unified_fable_v1_top100.py`
- `scripts/run_unified_fable_v1_top100_backtest.py`
- `tests/test_unified_fable_v1_top100.py`
- `tests/test_unified_fable_v1_top100_backtest.py`
- `docs/rebuild/unified-fable-v1-standard-top100.md`
- `output/unified-fable-v1-standard-top100.json` (local evidence)
- `output/unified-fable-v1-standard-top100-backtest.json` (local evidence)
- this report

## Rollout Recommendation

Create a separately versioned unified Standard board and expose it as a new production view. Keep the existing positional boards unchanged. Roll back by restoring the prior unified version only; do not touch the QB, RB, WR, or TE champion rows.
