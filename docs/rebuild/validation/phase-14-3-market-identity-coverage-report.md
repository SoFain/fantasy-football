# Phase 14.3 Market Identity Coverage Report

Final decision: GO

## Purpose

Phase 14.3 investigated the Phase 13 market identity warning:

- Market baseline total rows: 461.
- Rows missing `player_id_internal`: 64.
- Overall identity missing rate: `0.13882863340563992`.

The goal was to reduce unresolved market identity rows where possible and create a clean workflow for remaining unresolved rows without scraping, LLM calls, or fabricated player IDs.

## Starting State

Bounded warehouse checks showed all 64 unresolved rows came from:

- `source_id`: `manual_market_values`
- `position`: `PICK`
- `team`: null
- `snapshot_id`: `manual_market_values_compat_trade_assets_current_2026_ppr_redraft_one_qb`
- Asset type: draft picks, not NFL players

These rows should not resolve to `player_identity_bridge` or `dim_players_current`, because they are market assets rather than players.

All rows carry the same final non-player identity flags:

```text
non_player_market_asset
player_identity_not_applicable
```

Bounded unresolved row report:

| source_player_key | display_name | rank_overall | rank_position | market_value |
| --- | --- | ---: | ---: | ---: |
| `fantasycalc:2026pick101:PICK:UNK` | 2026 Pick 1.01 | 11 | 1 | 7084.0 |
| `fantasycalc:2026pick102:PICK:UNK` | 2026 Pick 1.02 | 32 | 2 | 4233.0 |
| `fantasycalc:2026pick103:PICK:UNK` | 2026 Pick 1.03 | 46 | 3 | 3751.0 |
| `fantasycalc:2026pick104:PICK:UNK` | 2026 Pick 1.04 | 50 | 4 | 3574.0 |
| `fantasycalc:2026pick105:PICK:UNK` | 2026 Pick 1.05 | 56 | 5 | 3376.0 |
| `fantasycalc:2026pick106:PICK:UNK` | 2026 Pick 1.06 | 59 | 6 | 3183.0 |
| `fantasycalc:20261st:PICK:UNK` | 2026 1st | 64 | 7 | 3073.0 |
| `fantasycalc:2026pick107:PICK:UNK` | 2026 Pick 1.07 | 67 | 8 | 2963.0 |
| `fantasycalc:20271st:PICK:UNK` | 2027 1st | 70 | 9 | 2843.0 |
| `fantasycalc:2026pick108:PICK:UNK` | 2026 Pick 1.08 | 71 | 10 | 2772.0 |
| `fantasycalc:2026pick109:PICK:UNK` | 2026 Pick 1.09 | 75 | 11 | 2604.0 |
| `fantasycalc:2026pick110:PICK:UNK` | 2026 Pick 1.10 | 76 | 12 | 2455.0 |
| `fantasycalc:2026pick111:PICK:UNK` | 2026 Pick 1.11 | 81 | 13 | 2322.0 |
| `fantasycalc:2026pick112:PICK:UNK` | 2026 Pick 1.12 | 89 | 14 | 2203.0 |
| `fantasycalc:2026pick201:PICK:UNK` | 2026 Pick 2.01 | 94 | 15 | 2095.0 |
| `fantasycalc:20281st:PICK:UNK` | 2028 1st | 95 | 16 | 2085.0 |
| `fantasycalc:2026pick202:PICK:UNK` | 2026 Pick 2.02 | 105 | 17 | 1998.0 |
| `fantasycalc:20291st:PICK:UNK` | 2029 1st | 110 | 18 | 1927.0 |
| `fantasycalc:2026pick203:PICK:UNK` | 2026 Pick 2.03 | 113 | 19 | 1909.0 |
| `fantasycalc:2026pick204:PICK:UNK` | 2026 Pick 2.04 | 123 | 20 | 1828.0 |
| `fantasycalc:2026pick205:PICK:UNK` | 2026 Pick 2.05 | 128 | 21 | 1753.0 |
| `fantasycalc:2026pick206:PICK:UNK` | 2026 Pick 2.06 | 133 | 22 | 1684.0 |
| `fantasycalc:20262nd:PICK:UNK` | 2026 2nd | 137 | 23 | 1653.0 |
| `fantasycalc:2026pick207:PICK:UNK` | 2026 Pick 2.07 | 137 | 24 | 1621.0 |
| `fantasycalc:2026pick208:PICK:UNK` | 2026 Pick 2.08 | 143 | 25 | 1562.0 |
| `fantasycalc:20272nd:PICK:UNK` | 2027 2nd | 149 | 26 | 1532.0 |
| `fantasycalc:2026pick209:PICK:UNK` | 2026 Pick 2.09 | 152 | 27 | 1507.0 |
| `fantasycalc:2026pick210:PICK:UNK` | 2026 Pick 2.10 | 162 | 28 | 1456.0 |
| `fantasycalc:2026pick211:PICK:UNK` | 2026 Pick 2.11 | 162 | 29 | 1408.0 |
| `fantasycalc:2026pick212:PICK:UNK` | 2026 Pick 2.12 | 166 | 30 | 1363.0 |
| `fantasycalc:2026pick301:PICK:UNK` | 2026 Pick 3.01 | 170 | 31 | 1321.0 |
| `fantasycalc:20282nd:PICK:UNK` | 2028 2nd | 178 | 32 | 1289.0 |
| `fantasycalc:2026pick302:PICK:UNK` | 2026 Pick 3.02 | 179 | 33 | 1282.0 |
| `fantasycalc:2026pick303:PICK:UNK` | 2026 Pick 3.03 | 186 | 34 | 1245.0 |
| `fantasycalc:2026pick304:PICK:UNK` | 2026 Pick 3.04 | 191 | 35 | 1210.0 |
| `fantasycalc:20292nd:PICK:UNK` | 2029 2nd | 192 | 36 | 1206.0 |
| `fantasycalc:2026pick305:PICK:UNK` | 2026 Pick 3.05 | 193 | 37 | 1177.0 |
| `fantasycalc:2026pick306:PICK:UNK` | 2026 Pick 3.06 | 196 | 38 | 1145.0 |
| `fantasycalc:20263rd:PICK:UNK` | 2026 3rd | 199 | 39 | 1130.0 |
| `fantasycalc:2026pick307:PICK:UNK` | 2026 Pick 3.07 | 199 | 40 | 1115.0 |
| `fantasycalc:2026pick308:PICK:UNK` | 2026 Pick 3.08 | 201 | 41 | 1087.0 |
| `fantasycalc:2026pick309:PICK:UNK` | 2026 Pick 3.09 | 202 | 42 | 1060.0 |
| `fantasycalc:2026pick310:PICK:UNK` | 2026 Pick 3.10 | 204 | 43 | 1035.0 |
| `fantasycalc:20273rd:PICK:UNK` | 2027 3rd | 204 | 44 | 1022.0 |
| `fantasycalc:2026pick311:PICK:UNK` | 2026 Pick 3.11 | 205 | 45 | 1010.0 |
| `fantasycalc:2026pick312:PICK:UNK` | 2026 Pick 3.12 | 207 | 46 | 987.0 |
| `fantasycalc:2026pick401:PICK:UNK` | 2026 Pick 4.01 | 210 | 47 | 965.0 |
| `fantasycalc:20283rd:PICK:UNK` | 2028 3rd | 211 | 48 | 957.0 |
| `fantasycalc:20293rd:PICK:UNK` | 2029 3rd | 212 | 49 | 954.0 |
| `fantasycalc:2026pick402:PICK:UNK` | 2026 Pick 4.02 | 213 | 50 | 944.0 |
| `fantasycalc:2026pick403:PICK:UNK` | 2026 Pick 4.03 | 216 | 51 | 924.0 |
| `fantasycalc:2026pick404:PICK:UNK` | 2026 Pick 4.04 | 216 | 52 | 904.0 |
| `fantasycalc:2026pick405:PICK:UNK` | 2026 Pick 4.05 | 219 | 53 | 885.0 |
| `fantasycalc:2026pick406:PICK:UNK` | 2026 Pick 4.06 | 221 | 54 | 868.0 |
| `fantasycalc:20264th:PICK:UNK` | 2026 4th | 226 | 55 | 859.0 |
| `fantasycalc:2026pick407:PICK:UNK` | 2026 Pick 4.07 | 228 | 56 | 850.0 |
| `fantasycalc:2026pick408:PICK:UNK` | 2026 Pick 4.08 | 231 | 57 | 834.0 |
| `fantasycalc:2026pick409:PICK:UNK` | 2026 Pick 4.09 | 232 | 58 | 818.0 |
| `fantasycalc:20274th:PICK:UNK` | 2027 4th | 232 | 59 | 818.0 |
| `fantasycalc:2026pick410:PICK:UNK` | 2026 Pick 4.10 | 235 | 60 | 803.0 |
| `fantasycalc:2026pick411:PICK:UNK` | 2026 Pick 4.11 | 235 | 61 | 788.0 |
| `fantasycalc:2026pick412:PICK:UNK` | 2026 Pick 4.12 | 235 | 64 | 774.0 |
| `fantasycalc:20284th:PICK:UNK` | 2028 4th | 235 | 63 | 780.0 |
| `fantasycalc:20294th:PICK:UNK` | 2029 4th | 235 | 62 | 784.0 |

## Matching Methods

The market resolver now supports deterministic matching in this order:

1. Existing `player_id_internal`.
2. Non-player market asset classification.
3. Manual overrides by trusted source and player key.
4. Exact source IDs.
5. Known aliases.
6. Exact normalized name plus position plus team.
7. Exact normalized name plus position when unique.
8. Unresolved with explicit missing-data flags.

Unsafe fuzzy auto-matching was not added.

## Overrides Added

No manual overrides were added.

The missing rows were not unresolved NFL players, so adding overrides would have been wrong. They were classified as non-player assets instead.

## Warehouse Update

Dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.market_consensus --classify-non-player-assets --dry-run
```

Dry-run result:

```text
market_consensus_baseline_current: 64 rows to classify
market_consensus_player_values: 64 rows to classify
```

Materialization command:

```powershell
.\venv\Scripts\python.exe -m src.market_consensus --classify-non-player-assets
```

Materialization result:

```text
market_consensus_baseline_current: 64 rows updated
market_consensus_player_values: 64 rows updated
```

The update is additive/idempotent. It does not drop, truncate, rename, or backfill unrelated production tables.

## Final State

Post-update coverage:

- Total market baseline rows: 461.
- Player rows: 397.
- Non-player market asset rows: 64.
- Rows missing `player_id_internal`: 64.
- Unresolved player rows: 0.
- Unresolved non-player asset rows: 64.
- Player identity missing rate: `0.0`.
- Overall identity null rate: `0.13882863340563992`.
- Rows marked `player_identity_not_applicable`: 64.
- Rows still marked `missing_player_id_internal`: 0.

Sample classified rows:

| source_id | source_player_key | display_name | position | match_method |
| --- | --- | --- | --- | --- |
| `manual_market_values` | `fantasycalc:20261st:PICK:UNK` | `2026 1st` | `PICK` | `non_player_asset` |
| `manual_market_values` | `fantasycalc:20262nd:PICK:UNK` | `2026 2nd` | `PICK` | `non_player_asset` |
| `manual_market_values` | `fantasycalc:20263rd:PICK:UNK` | `2026 3rd` | `PICK` | `non_player_asset` |

Classified rows carry both:

- `non_player_market_asset`
- `player_identity_not_applicable`

They no longer carry `missing_player_id_internal`.

## Validation Result

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
```

Result:

```text
Validation Run Completed: 9 passed, 0 failed.
```

`113_market_identity_coverage.sql` now validates player identity coverage separately from overall null identity rate.

## Remaining Manual Cleanup

There is no remaining manual cleanup for current player identity coverage.

Future true player rows that fail deterministic resolution should remain unresolved until one of these is reviewed and added:

- a trusted source ID bridge row
- a deterministic alias
- an audited `player_identity_overrides` row

Draft-pick assets should continue to keep `player_id_internal` null by design.

## Constraints Verified

- No scraping.
- No LLM calls.
- No Firebase artifacts.
- No fabricated player IDs.
- No raw/source table exposure to UI or Pigskin.
