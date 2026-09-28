# Phase 23.3F-R Projection Limit 500 Refresh Report

Date: 2026-06-18

## Final Decision

`PROJECTION LIMIT 500 READY WITH WARNINGS`

The limit 500 projection context is present in the warehouse and materially improves Trade Analyzer projection/model-run coverage. The latest verified model run is:

`weekly_projection-2025-18-20260618T152142Z-6752df98`

It contains 500 weekly projection rows and 500 projection ranking rows for:

- season: `2025`
- week: `18`
- scoring profile: `ppr`
- league type: `redraft`
- roster format: `one_qb`

Important authorization note: `ALLOW_PROJECTION_CONTEXT_REFRESH` was unset in the Codex process when checked. Because of that, Codex did not run another projection write command in this phase. Read-only verification found that the limit 500 refresh had already been applied to the warehouse before verification. No additional projection rows were written by Codex in this phase.

No Trade Analyzer score rows were written. `ALLOW_TRADE_SCORE_MATERIALIZATION` remained unset. No deployment, feature flag enablement, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, Firebase artifact creation, or production change was performed.

## Authorization

| Gate | State |
| --- | --- |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset when checked by Codex |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |

Blocked action:

```powershell
.\venv\Scripts\python.exe -m src.projection_engine --horizon weekly --season 2025 --week 18 --scoring-profile ppr --league-type redraft --roster-format one_qb --limit 500
```

Codex did not run that write command because the authorization gate was not present in the current process.

## Preflight

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass, 22 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 340 tests |
| `.\venv\Scripts\python.exe -m py_compile src\projection_engine.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |

Safety checker confirmed no Firebase artifacts, no tracked secret files, no secret content, safe default feature flags, Pigskin SQL safety, app compile, and `src` plus `scripts` compile.

## Before State From Phase 23.3F

Phase 23.3F recorded the following state before the limit 500 refresh existed:

| Metric | Value |
| --- | ---: |
| `projection_rankings_current` 2025 week 18 target rows | 100 |
| `projections_player_weekly` 2025 week 18 target rows | 100 |
| model runs | 1 |
| materializable Trade Analyzer candidates | 87 |
| materializable candidates covered by projection context | 51 |
| score dry-run `missing_model_run_id` | 48 |
| score dry-run `stale_projection_context` | 1 |
| score dry-run `temporary_name_join_identity` | 35 |

## Verified Projection Output

Read-only warehouse verification showed:

| Object | Rows |
| --- | ---: |
| `projection_rankings_current` 2025 week 18 PPR redraft one-QB | 600 |
| `projections_player_weekly` 2025 week 18 PPR redraft one-QB | 600 |
| `model_runs` 2025 week 18 weekly projection | 2 |
| `trade_player_scores` | 0 |

Rows by model run:

| Model run | Projection rows | Ranking rows | Status |
| --- | ---: | ---: | --- |
| `weekly_projection-2025-18-20260618T152142Z-6752df98` | 500 | 500 | complete |
| `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | 100 | 100 | complete |

Latest model run metadata:

| Field | Value |
| --- | --- |
| model_run_id | `weekly_projection-2025-18-20260618T152142Z-6752df98` |
| status | `complete` |
| feature_config_version_id | `baseline_weekly_v1` |
| source_freshness_snapshot_id | `freshness-20260618T152130Z-743ead9a` |
| created_at | `2026-06-18 15:21:43.042559+00:00` |
| completed_at | `2026-06-18 15:21:55.266347+00:00` |
| error_message | `None` |
| notes | `{"projection_rows": 500, "ranking_rows": 500}` |

## Candidate Overlap After Refresh

Read-only overlap against the Trade Analyzer top 100:

| Metric | Count |
| --- | ---: |
| Trade Analyzer candidates | 100 |
| materializable player candidates | 87 |
| draft-pick candidates | 13 |
| latest projection unique players | 500 |
| materializable overlap by `source_player_key` | 76 |
| materializable overlap by `player_id_internal` | 77 |
| materializable overlap by `gsis_id` | 76 |

Remaining materializable candidates without latest projection context:

| Rank | Player | Pos | Team | Player ID | Source key | Market value |
| ---: | --- | --- | --- | --- | --- | ---: |
| 7 | Jeremiyah Love | RB | ARI | `sleeper:13287` | `LOV121782` | 7373 |
| 29 | Carnell Tate | WR | TEN | `sleeper:13279` | `TAT143045` | 4409 |
| 43 | Jordyn Tyson | WR | NO | `sleeper:13281` | `TYS405541` | 3836 |
| 46 | Jadarian Price | RB | SEA | `sleeper:13286` | `PRI206342` | 3767 |
| 56 | Makai Lemon | WR | PHI | `sleeper:13294` | `LEM694125` | 3432 |
| 75 | KC Concepcion | WR | CLE | `sleeper:13298` | `CON046719` | 2916 |
| 84 | Kenyon Sadiq | TE | NYJ | `sleeper:13330` | `SAD482340` | 2608 |
| 90 | Omar Cooper | WR | NYJ | `sleeper:13276` | `COO816508` | 2386 |
| 96 | Jonah Coleman | RB | DEN | `sleeper:13345` | `COL293648` | 2301 |
| 98 | Denzel Boston | WR | CLE | `sleeper:13346` | `BOS677861` | 2264 |

## Top 25 Latest Projection Rankings

| Rank | Player | Pos | Team | Projected value | Confidence | Risk |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 | Chris Olave | WR | NO | 42.5390 | 71.40 | 37.00 |
| 2 | Chase Brown | RB | CIN | 41.0330 | 72.10 | 37.00 |
| 3 | Derrick Henry | RB | BAL | 41.0150 | 71.63 | 37.72 |
| 4 | Bijan Robinson | RB | ATL | 40.7870 | 72.10 | 37.00 |
| 5 | Brock Purdy | QB | SF | 39.8250 | 58.28 | 44.26 |
| 6 | Christian McCaffrey | RB | SF | 39.5170 | 72.10 | 37.00 |
| 7 | Trevor Lawrence | QB | JAX | 39.2800 | 48.54 | 67.86 |
| 8 | Drake Maye | QB | NE | 38.9800 | 64.65 | 43.08 |
| 9 | Matthew Stafford | QB | LA | 38.3570 | 46.33 | 71.25 |
| 10 | Rhamondre Stevenson | RB | NE | 38.1710 | 67.88 | 40.26 |
| 11 | Ja'Marr Chase | WR | CIN | 37.4760 | 71.40 | 37.00 |
| 12 | Puka Nacua | WR | LA | 36.3680 | 65.45 | 37.00 |
| 13 | Zay Flowers | WR | BAL | 35.6680 | 70.81 | 38.98 |
| 14 | Joe Burrow | QB | CIN | 35.5170 | 40.65 | 70.31 |
| 15 | Parker Washington | WR | JAX | 33.1880 | 71.20 | 37.30 |
| 16 | Josh Allen | QB | BUF | 32.9620 | 65.88 | 40.11 |
| 17 | Jaxon Smith-Njigba | WR | SEA | 32.4130 | 72.10 | 37.00 |
| 18 | Patrick Mahomes | QB | KC | 32.3370 | 62.69 | 42.87 |
| 19 | George Kittle | TE | SF | 32.1780 | 66.77 | 38.74 |
| 20 | Caleb Williams | QB | CHI | 32.1360 | 49.62 | 66.20 |
| 21 | Cam Skattebo | RB | NYG | 31.8860 | 64.07 | 39.66 |
| 22 | Justin Herbert | QB | LAC | 31.5960 | 64.04 | 42.94 |
| 23 | Tucker Kraft | TE | GB | 31.4820 | 63.74 | 40.17 |
| 24 | Zach Charbonnet | RB | SEA | 30.9840 | 71.30 | 37.15 |
| 25 | Jahmyr Gibbs | RB | DET | 30.7740 | 72.10 | 37.00 |

## Trade Analyzer Score Dry-Run

Command:

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v0_2025_001 --dry-run
```

Result:

| Metric | After 23.3F | After limit 500 | Result |
| --- | ---: | ---: | --- |
| wrote | `false` | `false` | unchanged |
| score row count | 100 | 100 | unchanged |
| materializable player row count | 87 | 87 | unchanged |
| excluded pick count | 13 | 13 | unchanged |
| written row count | 0 | 0 | unchanged |
| trade score min | 11.5784 | 7.9352 | declined |
| trade score max | 55.2387 | 60.0659 | improved |
| trade score avg | 33.9620 | 33.7807 | slightly declined |
| confidence min | 28.66 | 28.66 | unchanged |
| confidence max | 57.0 | 52.0 | declined |
| confidence avg | 48.7489 | 47.2706 | declined |
| confidence >= 70 | 0 | 0 | unchanged |
| nonzero `fraud_score` rows | 55 | 55 | unchanged |
| `missing_model_run_id` | 48 | 23 | improved |
| `stale_projection_context` | 1 | 0 | cleared |
| `temporary_name_join_identity` | 35 | 10 | improved |
| `missing_fraud_context` | 45 | 45 | unchanged |
| dry-run duplicate grain count | 0 | 0 | unchanged |

Projection join distribution:

| Strategy | Rows |
| --- | ---: |
| `source_player_key` | 76 |
| `player_id_internal` | 1 |
| none | 23 |

## Top 25 Trade Score Dry-Run Rows

| Rank | Player | Pos | Team | Score | Confidence | Fraud | Model run | Join strategy | Tier |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | Bijan Robinson | RB | ATL | 60.0659 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | starter |
| 2 | Ja'Marr Chase | WR | CIN | 55.7722 | 49.35 | 60.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | flex |
| 3 | Jahmyr Gibbs | RB | DET | 55.3984 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | flex |
| 4 | Puka Nacua | WR | LAR | 54.3830 | 43.72 | 100.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | flex |
| 5 | Jaxon Smith-Njigba | WR | SEA | 53.3932 | 50.53 | 65.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | flex |
| 6 | Jeremiyah Love | RB | ARI | 52.8696 | 52.00 | 0.00 |  |  | flex |
| 7 | De'Von Achane | RB | MIA | 51.7125 | 49.35 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | flex |
| 8 | Amon-Ra St. Brown | WR | DET | 51.6068 | 50.53 | 100.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | flex |
| 9 | Christian McCaffrey | RB | SF | 51.2452 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | flex |
| 10 | Drake Maye | QB | NE | 50.4203 | 43.66 | 100.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | flex |
| 11 | Ashton Jeanty | RB | LV | 49.2474 | 50.53 | 25.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | flex |
| 12 | Josh Allen | QB | BUF | 49.2100 | 42.97 | 100.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | flex |
| 13 | 2026 Pick 1.01 | PICK |  | 48.0620 | 49.00 | 0.00 |  |  | flex |
| 14 | Carnell Tate | WR | TEN | 46.5738 | 52.00 | 0.00 |  |  | flex |
| 15 | Chase Brown | RB | CIN | 46.5374 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | flex |
| 16 | 2026 Pick 1.02 | PICK |  | 45.9088 | 49.00 | 0.00 |  |  | flex |
| 17 | Chris Olave | WR | NO | 45.6053 | 49.35 | 60.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | flex |
| 18 | Omarion Hampton | RB | LAC | 44.5617 | 41.12 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | depth |
| 19 | Malik Nabers | WR | NYG | 44.3408 | 41.86 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | depth |
| 20 | Brock Bowers | TE | LV | 43.8011 | 44.23 | 78.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | depth |
| 21 | 2026 Pick 1.03 | PICK |  | 43.7556 | 49.00 | 0.00 |  |  | depth |
| 22 | James Cook | RB | BUF | 43.5172 | 49.90 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | depth |
| 23 | Colston Loveland | TE | CHI | 43.4487 | 49.29 | 43.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | depth |
| 24 | Jonathan Taylor | RB | IND | 42.5551 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | depth |
| 25 | Justin Jefferson | WR | MIN | 42.4340 | 50.53 | 35.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | depth |

## Bottom 25 Trade Score Dry-Run Rows

| Rank | Player | Pos | Team | Score | Confidence | Fraud | Model run | Join strategy | Tier |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | Chuba Hubbard | RB | CAR | 7.9352 | 47.02 | 45.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 2 | Bhayshul Tuten | RB | JAX | 10.6040 | 45.93 | 85.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 3 | David Montgomery | RB | HOU | 12.6693 | 49.41 | 60.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 4 | Marvin Harrison | WR | ARI | 14.5610 | 40.63 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `player_id_internal` | avoid |
| 5 | Jaylen Waddle | WR | DEN | 15.2744 | 48.32 | 70.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 6 | Quentin Johnston | WR | LAC | 16.6338 | 44.96 | 100.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 7 | Bo Nix | QB | DEN | 17.0614 | 44.12 | 75.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 8 | Jalen Hurts | QB | PHI | 18.4702 | 42.20 | 100.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 9 | Christian Watson | WR | GB | 18.6211 | 41.24 | 95.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 10 | Brian Thomas | WR | JAX | 19.4932 | 45.42 | 53.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 11 | RJ Harvey | RB | DEN | 19.9892 | 50.53 | 85.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 12 | 2026 Pick 1.11 | PICK |  | 20.5639 | 49.00 | 0.00 |  |  | avoid |
| 13 | Terry McLaurin | WR | WAS | 21.0081 | 41.85 | 35.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 14 | D'Andre Swift | RB | CHI | 21.2366 | 49.16 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 15 | Jaxson Dart | QB | NYG | 21.3500 | 46.09 | 100.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 16 | Josh Jacobs | RB | GB | 21.5005 | 47.56 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 17 | Alec Pierce | WR | IND | 21.8981 | 47.26 | 85.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 18 | 2026 Pick 1.10 | PICK |  | 22.9229 | 49.00 | 0.00 |  |  | avoid |
| 19 | Jayden Daniels | QB | WAS | 22.9821 | 30.04 | 80.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 20 | Bucky Irving | RB | TB | 23.6254 | 42.30 | 0.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 21 | DeVonta Smith | WR | PHI | 24.5245 | 49.69 | 63.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 22 | Sam LaPorta | TE | DET | 24.7030 | 51.41 | 53.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 23 | Javonte Williams | RB | DAL | 24.7859 | 48.89 | 30.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 24 | Kyle Pitts | TE | ATL | 25.0302 | 50.38 | 93.00 | `weekly_projection-2025-18-20260618T152142Z-6752df98` | `source_player_key` | avoid |
| 25 | 2026 Pick 1.09 | PICK |  | 25.3071 | 49.00 | 0.00 |  |  | avoid |

## Validations

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market` | pass, 9 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 passed, 0 failed |

## Materialization Recommendation

Do not materialize Trade Analyzer score rows yet.

Reasons:

- `missing_model_run_id` improved from 48 to 23, but 23 rows still lack model-run context.
- Remaining missing rows include 13 draft-pick rows and 10 materializable player rows without projection coverage.
- Confidence did not improve. Average confidence declined from 48.7489 to 47.2706.
- No rows reached confidence 70.
- Draft-pick score handling remains diagnostic only.

Recommended next step:

1. Decide whether the remaining 10 materializable missing projection rows are acceptable for a low-confidence staging-only v0.
2. If they are not acceptable, design `src.projection_engine` trade-candidate universe mode so projection rows are built directly from `compat_trade_assets_current`.
3. Keep `ALLOW_TRADE_SCORE_MATERIALIZATION` unset until explicit score-write approval.

Final decision: `PROJECTION LIMIT 500 READY WITH WARNINGS`.
