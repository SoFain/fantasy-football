# RB Fable 01 Backtest Harness

## Warehouse Objects

- `fantasy_football_advanced_metrics.situational_identity_bridge_review`
- `fantasy_football_advanced_metrics.v_rb_fable_01_situational_splits`
- `fantasy_football_advanced_metrics.v_rb_fable_01_metric_inputs`
- `fantasy_football_advanced_metrics.v_rb_fable_01_backtest_prep`

The prep view calculates season-local z-scores, applies efficiency shrinkage, calculates `rb_fable_01_score`, and joins only the next season's Standard outcome. It does not evaluate or write a ranking.

## Fold Availability

| Input to target | Qualified inputs | Target available | Complete score and target |
|---|---:|---:|---:|
| 2022 to 2023 | 101 | 72 | 66 |
| 2023 to 2024 | 101 | 75 | 73 |
| 2024 to 2025 | 99 | 67 | 65 |

Identity review contains 231 unique exact-name/GSIS matches, three high-confidence name-team-season matches, and two unmapped RBs. Collision count is zero.

## Comparison Availability

Actual Standard points and Standard PPG are available for all 204 complete fold rows. Target Standard RB rank is calculated among target players with at least six games.

Historical Current Pigskin Standard rows do not exist for the three target seasons. The active table contains the current 2026 Standard board only. The prep view reports `UNAVAILABLE_HISTORICAL_BASELINE`; it does not backfill that comparison with current rankings or market data.

`standard_rb_elite_receiving_back_protection_v0` is not present in `ranking_formula_candidates`, so prior-episode comparison is also marked unavailable.

## Known Limitations

- Missing red-zone splits prevent a complete TD component for 10 input rows in 2022, five in 2023, and eight in 2024.
- One qualified input lacks age in 2022 and one in 2023.
- Returning-player evaluation excludes players without prior-season situational data.
- Weekly target row count is the available regular-season games proxy in the Standard points table.
- The eight-plus-box split uses a 20-carry threshold. Lower-volume rows use a within-season box-context residual.

## Next Backtest Command

Phase 34.3 should implement a read-only evaluator over the prep view, then run it with an explicit dry-run command such as:

```powershell
.\venv\Scripts\python.exe scripts\run_rb_fable_01_backtest.py --project fantasy-football-498121 --dataset fantasy_football_advanced_metrics --dry-run
```

That evaluator does not exist in Phase 34.2B. Do not run the command until Phase 34.3 creates and reviews it.

