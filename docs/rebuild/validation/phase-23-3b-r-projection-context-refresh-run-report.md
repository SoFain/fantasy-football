# Phase 23.3B-R Projection Context Refresh Run Report

Date: 2026-06-18

## Final Decision

`PROJECTION CONTEXT READY WITH WARNINGS`

The bounded deterministic projection refresh for `2025` week `18`, `ppr`, `redraft`, `one_qb`, limit `100`, completed successfully under explicit one-step authorization. The authorization gate was removed after the refresh.

Projection context is now available for the target slice:

- `projection_rankings_current`: 100 rows
- `projections_player_weekly`: 100 rows
- `model_runs`: 1 complete weekly projection run

Trade Analyzer score materialization is still not recommended. The follow-up score run was dry-run only and improved model-run coverage, but the score output still has low confidence, 48 rows with `missing_model_run_id`, 1 row with `stale_projection_context`, and heavy `temporary_name_join_identity` usage.

No Trade Analyzer score rows were written. No deployment, feature flag enablement, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, Firebase artifact creation, or production change was performed.

## Authorization

| Check | Result |
| --- | --- |
| Required gate | `ALLOW_PROJECTION_CONTEXT_REFRESH=true` |
| Gate status during refresh | set by operator for the bounded command |
| Gate status after refresh | removed |
| Score materialization gate | unset |

The current environment after the run shows:

| Variable | Value |
| --- | --- |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |

## Preflight

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 334 tests |
| `.\venv\Scripts\python.exe -m py_compile src\projection_engine.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |

Safety checker confirmed no Firebase artifacts, no tracked secret files, no secret content, default-off feature flags, Pigskin SQL safety, app compile, and `src` plus `scripts` compile.

## Before Projection Coverage

Before the authorized refresh, Phase 23.3B documented:

| Object | Target coverage before refresh |
| --- | ---: |
| `projection_rankings_current` 2025 week 18 PPR redraft one-QB | 0 |
| `projections_player_weekly` 2025 week 18 PPR redraft one-QB | 0 |
| `model_runs` 2025 week 18 weekly projection | 0 |

The score dry-run before projection refresh had:

| Metric | Before refresh |
| --- | ---: |
| `missing_model_run_id` | 98 |
| `stale_projection_context` | 2 |
| confidence min | 36.5 |
| confidence max | 57.0 |
| confidence avg | 51.8061 |
| rows with confidence >= 70 | 0 |
| trade score min | 9.2092 |
| trade score max | 65.0709 |
| trade score avg | 34.3197 |
| `missing_fraud_context` | 45 |
| nonzero `fraud_score` rows | 55 |

## Projection Refresh Command

The bounded refresh command was:

```powershell
$env:ALLOW_PROJECTION_CONTEXT_REFRESH = "true"
.\venv\Scripts\python.exe -m src.projection_engine --horizon weekly --season 2025 --week 18 --scoring-profile ppr --league-type redraft --roster-format one_qb --limit 100
Remove-Item Env:\ALLOW_PROJECTION_CONTEXT_REFRESH
```

Result:

| Metric | Value |
| --- | --- |
| exit code | 0 |
| model_run_id | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` |
| feature_config_version_id | `baseline_weekly_v1` |
| source_freshness_snapshot_id | `freshness-20260618T044025Z-bd445907` |
| projection rows written | 100 |
| ranking rows written | 100 |

No `src.generate_pigskin_rankings` command was run.

## Projection Output Verification

Read-only verification after refresh:

| Metric | Value |
| --- | ---: |
| `projection_rankings_current` target rows | 100 |
| `projection_rankings_current` distinct model runs | 1 |
| `projections_player_weekly` target rows | 100 |
| `projections_player_weekly` distinct model runs | 1 |
| target `model_runs` rows | 1 |
| ranking duplicate grain groups | 0 |
| weekly projection duplicate grain groups | 0 |

Model run:

| Field | Value |
| --- | --- |
| model_run_id | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` |
| status | `complete` |
| feature_config_version_id | `baseline_weekly_v1` |
| source_freshness_snapshot_id | `freshness-20260618T044025Z-bd445907` |
| created_at | `2026-06-18 04:40:39.881208+00:00` |
| completed_at | `2026-06-18 04:40:49.720807+00:00` |
| error_message | `None` |

Projection metadata:

| Check | Result |
| --- | --- |
| `source_freshness_json` present | yes |
| `missing_data_flags` present | yes |

Sample missing flags from a weekly projection row:

```text
["asset_missing_flags_present", "missing_breakout_packet", "missing_fraud_packet", "profile_missing_flags_present"]
```

## Top 25 Projection Rankings

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

| Metric | After refresh |
| --- | ---: |
| exit code | 0 |
| wrote | `false` |
| score row count | 100 |
| score_run_id | `trade-score-trade_score_v0_2025_001-2025-w18-7379b96970df` |
| trade score min | 11.5784 |
| trade score max | 55.2387 |
| trade score avg | 33.9357 |
| confidence min | 28.66 |
| confidence max | 57.0 |
| confidence avg | 48.5489 |
| rows with confidence >= 70 | 0 |
| nonzero `fraud_score` rows | 55 |
| `missing_model_run_id` | 48 |
| `stale_projection_context` | 1 |
| `missing_fraud_context` | 45 |
| `temporary_name_join_identity` | 87 |
| draft pick assets | 13 |
| `missing_pigskin_ranking_context` | 27 |
| `missing_recent_trade_history` | 29 |

Position distribution:

| Position | Rows |
| --- | ---: |
| RB | 29 |
| WR | 36 |
| QB | 13 |
| PICK | 13 |
| TE | 9 |

Tier distribution:

| Tier | Rows |
| --- | ---: |
| flex | 16 |
| depth | 47 |
| avoid | 37 |

## Trade Score Comparison

| Metric | Before refresh | After refresh | Result |
| --- | ---: | ---: | --- |
| `missing_model_run_id` | 98 | 48 | improved |
| `stale_projection_context` | 2 | 1 | improved |
| confidence min | 36.5 | 28.66 | declined |
| confidence max | 57.0 | 57.0 | unchanged |
| confidence avg | 51.8061 | 48.5489 | declined |
| rows with confidence >= 70 | 0 | 0 | unchanged |
| trade score min | 9.2092 | 11.5784 | improved |
| trade score max | 65.0709 | 55.2387 | declined |
| trade score avg | 34.3197 | 33.9357 | slightly declined |
| `missing_fraud_context` | 45 | 45 | unchanged |
| nonzero `fraud_score` rows | 55 | 55 | unchanged |

Projection model-run coverage improved materially, but confidence did not improve because the remaining source and identity gaps still dominate v0 confidence scoring.

## Top 25 Trade Score Dry-Run Rows

| Rank | Player | Pos | Team | Score | Confidence | Fraud | Model run | Tier |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 1 | Bijan Robinson | RB | ATL | 55.2387 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 2 | Jeremiyah Love | RB | ARI | 52.8696 | 52.00 | 0.00 |  | flex |
| 3 | Jahmyr Gibbs | RB | DET | 50.5711 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 4 | Ja'Marr Chase | WR | CIN | 50.5418 | 49.35 | 60.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 5 | Drake Maye | QB | NE | 50.4203 | 43.66 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 6 | CeeDee Lamb | WR | DAL | 49.6311 | 51.50 | 43.00 |  | flex |
| 7 | Puka Nacua | WR | LAR | 49.3276 | 43.72 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 8 | Josh Allen | QB | BUF | 49.2100 | 42.97 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 9 | Jaxon Smith-Njigba | WR | SEA | 48.1628 | 50.53 | 65.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 10 | 2026 Pick 1.01 | PICK |  | 48.0620 | 49.00 | 0.00 |  | flex |
| 11 | Drake London | WR | ATL | 47.0918 | 50.50 | 0.00 |  | flex |
| 12 | De'Von Achane | RB | MIA | 46.8853 | 49.35 | 0.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 13 | Amon-Ra St. Brown | WR | DET | 46.5500 | 50.53 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 14 | Christian McCaffrey | RB | SF | 46.4166 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | flex |
| 15 | 2026 Pick 1.02 | PICK |  | 45.9088 | 49.00 | 0.00 |  | flex |
| 16 | Breece Hall | RB | NYJ | 45.0541 | 54.50 | 0.00 |  | flex |
| 17 | Ashton Jeanty | RB | LV | 44.2452 | 50.53 | 25.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | depth |
| 18 | Tetairoa McMillan | WR | CAR | 43.8477 | 55.50 | 50.00 |  | depth |
| 19 | 2026 Pick 1.03 | PICK |  | 43.7556 | 49.00 | 0.00 |  | depth |
| 20 | Carnell Tate | WR | TEN | 43.0738 | 52.00 | 0.00 |  | depth |
| 21 | Chase Brown | RB | CIN | 41.7102 | 50.53 | 0.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | depth |
| 22 | 2026 Pick 1.04 | PICK |  | 41.6024 | 49.00 | 0.00 |  | depth |
| 23 | Trey McBride | TE | ARI | 41.4666 | 43.72 | 35.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | depth |
| 24 | Quinshon Judkins | RB | CLE | 40.7715 | 52.50 | 0.00 |  | depth |
| 25 | Brock Bowers | TE | LV | 40.6903 | 44.23 | 78.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | depth |

## Bottom 25 Trade Score Dry-Run Rows

| Rank | Player | Pos | Team | Score | Confidence | Fraud | Model run | Tier |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 1 | Quentin Johnston | WR | LAC | 11.5784 | 44.96 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | avoid |
| 2 | RJ Harvey | RB | DEN | 15.1620 | 50.53 | 85.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | avoid |
| 3 | Chuba Hubbard | RB | CAR | 16.4500 | 53.50 | 45.00 |  | avoid |
| 4 | Alec Pierce | WR | IND | 16.8427 | 47.26 | 85.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | avoid |
| 5 | Bo Nix | QB | DEN | 16.8864 | 44.12 | 75.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | avoid |
| 6 | D'Andre Swift | RB | CHI | 16.8910 | 49.16 | 0.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | avoid |
| 7 | Bhayshul Tuten | RB | JAX | 18.3278 | 53.50 | 85.00 |  | avoid |
| 8 | Jalen Hurts | QB | PHI | 18.4702 | 42.20 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | avoid |
| 9 | 2026 Pick 1.11 | PICK |  | 20.5639 | 49.00 | 0.00 |  | avoid |
| 10 | David Montgomery | RB | HOU | 21.1841 | 55.50 | 60.00 |  | avoid |
| 11 | Jaxson Dart | QB | NYG | 21.3500 | 46.09 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | avoid |
| 12 | Sam LaPorta | TE | DET | 21.4172 | 47.41 | 53.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | avoid |
| 13 | Denzel Boston | WR | CLE | 21.8414 | 52.00 | 0.00 |  | avoid |
| 14 | Christian Watson | WR | GB | 22.5102 | 48.50 | 95.00 |  | avoid |
| 15 | 2026 Pick 1.10 | PICK |  | 22.9229 | 49.00 | 0.00 |  | avoid |
| 16 | Jayden Daniels | QB | WAS | 22.9821 | 30.04 | 80.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | avoid |
| 17 | Jonah Coleman | RB | DEN | 23.9400 | 52.00 | 0.00 |  | avoid |
| 18 | Jaylen Waddle | WR | DEN | 25.2101 | 54.50 | 70.00 |  | avoid |
| 19 | Tee Higgins | WR | CIN | 25.2325 | 47.24 | 55.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | avoid |
| 20 | 2026 Pick 1.09 | PICK |  | 25.3071 | 49.00 | 0.00 |  | avoid |
| 21 | Omar Cooper | WR | NYJ | 25.5906 | 52.00 | 0.00 |  | avoid |
| 22 | Kenyon Sadiq | TE | NYJ | 26.1576 | 52.00 | 0.00 |  | avoid |
| 23 | Cam Skattebo | RB | NYG | 26.7722 | 46.52 | 70.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | avoid |
| 24 | Harold Fannin | TE | CLE | 26.7809 | 48.14 | 100.00 | `weekly_projection-2025-18-20260618T044039Z-e3978cd6` | avoid |
| 25 | KC Concepcion | WR | CLE | 27.1306 | 52.00 | 0.00 |  | avoid |

## Validations

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market` | pass, 9 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 passed, 0 failed |

## Materialization Recommendation

Do not materialize Trade Analyzer score rows yet.

Reasons:

- `missing_model_run_id` improved from 98 to 48, but 48 percent of the dry-run rows still lack model-run context.
- `stale_projection_context` improved from 2 to 1, but is not fully cleared.
- Confidence did not improve. Average confidence declined from 51.8061 to 48.5489.
- No rows reached confidence 70.
- `temporary_name_join_identity` remains high at 87 rows.
- Draft-pick assets still need a separate score lane or product decision.

Recommended next step:

1. Investigate why 48 dry-run rows still lack `model_run_id` after the week 18 projection refresh.
2. Reduce temporary name-based identity joins before score write approval.
3. Decide whether v0 can intentionally ship as low-confidence review-only output.
4. Keep `ALLOW_TRADE_SCORE_MATERIALIZATION` unset until explicit approval.

Final decision: `PROJECTION CONTEXT READY WITH WARNINGS`.
