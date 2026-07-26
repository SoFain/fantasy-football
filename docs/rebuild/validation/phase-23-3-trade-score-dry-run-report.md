# Phase 23.3 Trade Score Dry-Run Report

Date: 2026-06-17

## Final Decision

`TRADE SCORE DRY-RUN PASS WITH WARNINGS`

The bounded deterministic Trade Analyzer score builder ran successfully for 2025 week 18 PPR redraft one-QB and produced 100 candidate score rows without writing data. The score table remained empty before and after the dry-run.

Materialization is not recommended for user-facing use yet. A bounded test materialization can be considered only after operator review accepts the warnings below.

No score rows were written. No deployment, feature flag enablement, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, Firebase artifact creation, or production change was performed.

## Target

| Field | Value |
| --- | --- |
| season | `2025` |
| week | `18` |
| scoring_profile_id | `ppr` |
| league_type_id | `redraft` |
| roster_format_id | `one_qb` |
| model_version | `trade_score_v0_2025_001` |

## Preflight

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |

Safety checker result:

- no Firebase artifacts
- no tracked secret files
- no secret content
- required files exist
- feature flags default off
- Pigskin `execute_bigquery_sql` remains absent
- `app.py` compiles
- `src` and `scripts` compile

## Object Availability

Read-only checks confirmed that migration `0025` objects exist.

| Object | Type | Schema fields | Row count |
| --- | --- | ---: | ---: |
| `trade_player_scores` | table | 33 | 0 |
| `trade_player_scores_current` | view | 33 | 0 |
| `compat_trade_player_scores_current` | view | 33 | 0 |

The zero row count is expected because Phase 23.3 was dry-run only.

## Source Availability

Read-only source counts for the bounded target window:

| Source | Filter | Rows | Distinct players | Week range |
| --- | --- | ---: | ---: | --- |
| `compat_trade_assets_current` | PPR redraft one-QB | 461 | not queried | current |
| `compat_trade_player_history` | 2025 weeks 14 to 18, PPR | 5,257 | 1,611 | 14 to 18 |
| `analytics_player_weekly_truth` | 2025 weeks 14 to 18, QB/RB/WR/TE | 1,735 | 497 | 14 to 18 |
| `analytics_player_fantasy_points_by_profile` | 2025 weeks 14 to 18, PPR | 5,257 | 1,611 | 14 to 18 |
| `analytics_fraud_watch` | 2025 weeks 1 to 18 | 1,218 | 342 | 1 to 18 |
| `projection_rankings_current` | 2025 PPR redraft one-QB, week <= 18 | 50 | 25 | 1 to 1 |

Source warning: `projection_rankings_current` has only week 1 context for this target, so projection context is stale relative to week 18.

## Dry-Run Command

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v0_2025_001 --dry-run
```

Dry-run result:

| Metric | Value |
| --- | ---: |
| source rows | 100 |
| candidate score rows | 100 |
| wrote | `false` |
| `trade_player_scores` rows before | 0 |
| `trade_player_scores` rows after | 0 |
| score run id | `trade-score-trade_score_v0_2025_001-2025-w18-7379b96970df` |

## Score Distribution

| Metric | Min | Max | Avg |
| --- | ---: | ---: | ---: |
| `trade_score` | 12.3592 | 65.0709 | 36.6446 |
| `confidence_score` | 37.5 | 57.0 | 51.7661 |
| `market_score` | 1.39 | 98.61 | 50.0 |
| `projection_score` | 1.39 | 98.61 | 50.0 |
| `recent_production_score` | 1.85 | 98.15 | 47.1 |
| `role_usage_score` | 14.31 | 82.18 | 48.2481 |
| `positional_scarcity_score` | 76.37 | 100.0 | 97.8049 |
| `efficiency_score` | 37.96 | 100.0 | 63.3847 |
| `normalized_risk_score` | 0.175 | 0.6025 | 0.249 |
| `fraud_score` | 0.0 | 0.0 | 0.0 |

All `trade_score` values are within `0` to `100`.

All `confidence_score` values are within `0` to `100`, but all 100 rows are below `70`. This is not a validation failure because the v0 contract allows `0` to `100`, but it is a readiness warning.

## Position And Tier Distribution

| Position | Rows |
| --- | ---: |
| WR | 36 |
| RB | 29 |
| QB | 13 |
| PICK | 13 |
| TE | 9 |

| Tier | Rows |
| --- | ---: |
| avoid | 37 |
| depth | 35 |
| flex | 23 |
| starter | 5 |

Top 25 QB count: 2. The dry-run does not show all-QB domination.

## Missing Flags

Top missing flag counts:

| Flag | Rows |
| --- | ---: |
| `missing_fraud_context` | 100 |
| `missing_model_run_id` | 98 |
| `temporary_name_join_identity` | 87 |
| `missing_fumbles_lost` | 71 |
| `missing_interceptions` | 71 |
| `missing_passing_2pt_conversions` | 71 |
| `missing_receiving_2pt_conversions` | 71 |
| `missing_return_tds` | 71 |
| `missing_routes_proxy` | 71 |
| `missing_rushing_2pt_conversions` | 71 |
| `missing_snaps` | 71 |
| `scoring_missing_data_flags_present` | 71 |
| `missing_snaps_last_3` | 32 |
| `efficiency_fallback_used` | 29 |
| `missing_recent_trade_history` | 29 |
| `role_usage_fallback_used` | 29 |
| `missing_pigskin_ranking_context` | 27 |
| `missing_age` | 13 |
| `missing_gsis_id` | 13 |
| `missing_player_id_internal` | 13 |

Warning: every row has `missing_fraud_context` even though `analytics_fraud_watch` has 2025 rows through week 18. This needs follow-up before score materialization is treated as review-ready.

## Source Freshness Summary

Every candidate row carried source entries for:

- `compat_trade_assets_current`
- `compat_trade_player_history`
- `analytics_player_fantasy_points_by_profile`
- `analytics_fraud_watch`
- `projection_rankings_current`

`analytics_fraud_watch` source freshness pointed to 2025 week 18 for all 100 rows, but the rows still flagged `missing_fraud_context`, which indicates the source exists but the row-level fraud match did not attach to the candidates.

## Top 25 By Trade Score

| Rank | Player | Pos | Team | Score | Tier | Confidence | Market score | Risk |
| ---: | --- | --- | --- | ---: | --- | ---: | ---: | ---: |
| 1 | Bijan Robinson | RB | ATL | 65.0709 | starter | 55.5 | 98.28 | 0.25 |
| 2 | Ja'Marr Chase | WR | CIN | 62.5188 | starter | 54.5 | 98.61 | 0.25 |
| 3 | Puka Nacua | WR | LAR | 62.3546 | starter | 57.0 | 93.06 | 0.25 |
| 4 | Jahmyr Gibbs | RB | DET | 61.3680 | starter | 55.5 | 94.83 | 0.25 |
| 5 | Jaxon Smith-Njigba | WR | SEA | 60.8804 | starter | 55.5 | 95.83 | 0.25 |
| 6 | Amon-Ra St. Brown | WR | DET | 59.5784 | flex | 55.5 | 90.28 | 0.25 |
| 7 | Josh Allen | QB | BUF | 58.7678 | flex | 49.5 | 96.15 | 0.25 |
| 8 | De'Von Achane | RB | MIA | 57.1991 | flex | 54.5 | 84.48 | 0.25 |
| 9 | Trey McBride | TE | ARI | 56.4998 | flex | 57.0 | 83.33 | 0.25 |
| 10 | Drake Maye | QB | NE | 55.6703 | flex | 50.5 | 88.46 | 0.25 |
| 11 | Ashton Jeanty | RB | LV | 54.5590 | flex | 55.5 | 91.38 | 0.25 |
| 12 | Christian McCaffrey | RB | SF | 54.3168 | flex | 55.5 | 70.69 | 0.25 |
| 13 | Brock Bowers | TE | LV | 52.1619 | flex | 50.5 | 94.44 | 0.25 |
| 14 | James Cook | RB | BUF | 51.2054 | flex | 55.5 | 74.14 | 0.25 |
| 15 | Justin Jefferson | WR | MIN | 51.0720 | flex | 55.5 | 87.50 | 0.25 |
| 16 | CeeDee Lamb | WR | DAL | 50.6964 | flex | 51.5 | 81.94 | 0.25 |
| 17 | Jonathan Taylor | RB | IND | 50.4553 | flex | 55.5 | 77.59 | 0.25 |
| 18 | Omarion Hampton | RB | LAC | 50.0482 | flex | 47.5 | 81.03 | 0.25 |
| 19 | Malik Nabers | WR | NYG | 49.4704 | flex | 41.5 | 84.72 | 0.175 |
| 20 | Jeremiyah Love | RB | ARI | 48.5240 | flex | 52.0 | 87.93 | 0.20 |
| 21 | 2026 Pick 1.01 | PICK |  | 48.0620 | flex | 49.0 | 96.15 | 0.25 |
| 22 | Nico Collins | WR | HOU | 47.6284 | flex | 53.5 | 68.06 | 0.25 |
| 23 | Chris Olave | WR | NO | 47.2979 | flex | 54.5 | 56.94 | 0.25 |
| 24 | 2026 Pick 1.02 | PICK |  | 45.9088 | flex | 49.0 | 88.46 | 0.25 |
| 25 | George Pickens | WR | DAL | 45.8335 | flex | 55.5 | 73.61 | 0.25 |

## Bottom 25 By Trade Score

| Rank | Player | Pos | Team | Score | Tier | Confidence | Market score | Risk |
| ---: | --- | --- | --- | ---: | --- | ---: | ---: | ---: |
| 1 | Chuba Hubbard | RB | CAR | 12.3592 | avoid | 53.5 | 5.17 | 0.25 |
| 2 | Denzel Boston | WR | CLE | 15.6198 | avoid | 52.0 | 4.17 | 0.20 |
| 3 | Jonah Coleman | RB | DEN | 16.2148 | avoid | 52.0 | 8.62 | 0.20 |
| 4 | Bhayshul Tuten | RB | JAX | 16.3370 | avoid | 53.5 | 18.97 | 0.25 |
| 5 | Quentin Johnston | WR | LAC | 17.6053 | avoid | 51.5 | 1.39 | 0.25 |
| 6 | Kenyon Sadiq | TE | NYJ | 18.3806 | avoid | 52.0 | 5.56 | 0.20 |
| 7 | David Montgomery | RB | HOU | 18.6249 | avoid | 55.5 | 15.52 | 0.25 |
| 8 | Omar Cooper | WR | NYJ | 19.3676 | avoid | 52.0 | 15.28 | 0.20 |
| 9 | RJ Harvey | RB | DEN | 19.4460 | avoid | 55.5 | 1.72 | 0.25 |
| 10 | Bo Nix | QB | DEN | 19.9833 | avoid | 50.5 | 11.54 | 0.25 |
| 11 | Alec Pierce | WR | IND | 20.5373 | avoid | 53.5 | 6.94 | 0.25 |
| 12 | 2026 Pick 1.11 | PICK |  | 20.5639 | avoid | 49.0 | 3.85 | 0.25 |
| 13 | D'Andre Swift | RB | CHI | 21.0140 | avoid | 54.5 | 12.07 | 0.25 |
| 14 | KC Concepcion | WR | CLE | 21.2968 | avoid | 52.0 | 18.06 | 0.20 |
| 15 | Brock Purdy | QB | SF | 21.5589 | avoid | 42.5 | 3.85 | 0.25 |
| 16 | Marvin Harrison | WR | ARI | 22.0952 | avoid | 57.0 | 34.72 | 0.25 |
| 17 | Christian Watson | WR | GB | 22.3156 | avoid | 48.5 | 9.72 | 0.25 |
| 18 | 2026 Pick 1.10 | PICK |  | 22.9229 | avoid | 49.0 | 11.54 | 0.25 |
| 19 | Jalen Hurts | QB | PHI | 23.7202 | avoid | 49.5 | 26.92 | 0.25 |
| 20 | Terry McLaurin | WR | WAS | 24.7866 | avoid | 48.5 | 12.50 | 0.25 |
| 21 | 2026 Pick 1.09 | PICK |  | 25.3071 | avoid | 49.0 | 19.23 | 0.25 |
| 22 | Jaylen Waddle | WR | DEN | 25.4440 | avoid | 54.5 | 23.61 | 0.25 |
| 23 | Josh Jacobs | RB | GB | 25.8048 | avoid | 53.5 | 22.41 | 0.25 |
| 24 | Brian Thomas | WR | JAX | 26.3155 | avoid | 52.5 | 31.94 | 0.25 |
| 25 | Tucker Kraft | TE | GB | 26.4509 | avoid | 41.61 | 50.00 | 0.6025 |

## High Market Value With Low Confidence

Examples with `market_score >= 70` and `confidence_score < 60`:

| Player | Pos | Team | Score | Confidence | Market score | Risk |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Ja'Marr Chase | WR | CIN | 62.5188 | 54.5 | 98.61 | 0.25 |
| Bijan Robinson | RB | ATL | 65.0709 | 55.5 | 98.28 | 0.25 |
| 2026 Pick 1.01 | PICK |  | 48.0620 | 49.0 | 96.15 | 0.25 |
| Josh Allen | QB | BUF | 58.7678 | 49.5 | 96.15 | 0.25 |
| Jaxon Smith-Njigba | WR | SEA | 60.8804 | 55.5 | 95.83 | 0.25 |
| Jahmyr Gibbs | RB | DET | 61.3680 | 55.5 | 94.83 | 0.25 |
| Brock Bowers | TE | LV | 52.1619 | 50.5 | 94.44 | 0.25 |
| Puka Nacua | WR | LAR | 62.3546 | 57.0 | 93.06 | 0.25 |
| Ashton Jeanty | RB | LV | 54.5590 | 55.5 | 91.38 | 0.25 |
| Amon-Ra St. Brown | WR | DET | 59.5784 | 55.5 | 90.28 | 0.25 |

## High Risk Penalty Examples

| Player | Pos | Team | Score | Confidence | Market score | Risk | Fraud score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Tucker Kraft | TE | GB | 26.4509 | 41.61 | 50.00 | 0.6025 | 0.0 |
| Garrett Wilson | WR | NYJ | 29.3951 | 40.5 | 62.50 | 0.5985 | 0.0 |

Risk adjustment is visible in the calculated rows through `normalized_risk_score`, but `fraud_score` is `0.0` for all 100 rows because fraud context did not attach.

## Sanity Review

| Check | Result |
| --- | --- |
| Scores between 0 and 100 | pass |
| Confidence within 0 to 100 | pass |
| Confidence in ready range | warning, all 100 rows are below 70 |
| Duplicate player/context rows | pass, 0 duplicate grain rows |
| Null player names | pass, 0 rows |
| Null teams | warning, 13 draft-pick rows have null team |
| Top names plausible | pass with warning, top players are plausible but confidence is low |
| All-QB domination | pass, only 2 QBs in top 25 |
| Risk adjustment visible | pass |
| Missing data surfaced | pass |
| Score rows written | pass, 0 rows before and after |

## Materialization Recommendation

Do not materialize for review-ready staging yet.

Before score writes, investigate:

1. Why all 100 candidate rows flag `missing_fraud_context` despite 2025 week 18 Fraud Watch source availability.
2. Whether `projection_rankings_current` should be rebuilt for week 18 before scoring, because current projection context only covers week 1.
3. Whether confidence should remain below 70 for all rows or whether missing-data penalties are too aggressive for the initial v0 dry-run.
4. Whether draft-pick assets should be included in `trade_player_scores` or split into a separate pick-score lane.

If the operator accepts these warnings, a bounded test materialization could be run later with separate explicit authorization. Do not materialize without `ALLOW_TRADE_SCORE_MATERIALIZATION=true`.

Final decision: `TRADE SCORE DRY-RUN PASS WITH WARNINGS`.
