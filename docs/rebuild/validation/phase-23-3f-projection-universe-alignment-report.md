# Phase 23.3F Projection Universe Alignment Report

Date: 2026-06-18

## Final Decision

`PROJECTION LIMIT EXPANSION BLOCKED`

The current mismatch is a candidate-universe coverage issue. The deterministic projection engine currently ranks players by recent production from the projection feature universe, while the Trade Analyzer score builder uses the top 100 market-value assets from `compat_trade_assets_current`. The existing week 18 projection refresh at limit 100 covers only 51 of 87 materializable Trade Analyzer player candidates.

Dry-run limit expansion improves coverage:

- limit 250 covers 73 of 87 materializable Trade Analyzer player candidates
- limit 500 covers 77 of 87 materializable Trade Analyzer player candidates

Selected path: `A. Larger bounded projection refresh is sufficient`.

No projection write was run because `ALLOW_PROJECTION_CONTEXT_REFRESH` is unset. No Trade Analyzer score rows were written. No deployment, feature flag enablement, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, Firebase artifact creation, or production change was performed.

## Authorization

| Gate | State |
| --- | --- |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |

Because the projection refresh gate is unset, this phase stayed dry-run and read-only except for local report creation.

## Candidate Universe Comparison

Target:

| Field | Value |
| --- | --- |
| season | `2025` |
| week | `18` |
| scoring_profile_id | `ppr` |
| league_type_id | `redraft` |
| roster_format_id | `one_qb` |
| model_version | `trade_score_v0_2025_001` |

Current universe counts:

| Metric | Count |
| --- | ---: |
| Trade Analyzer candidate assets | 100 |
| materializable player candidates | 87 |
| draft-pick candidates | 13 |
| current `projection_rankings_current` rows | 100 |
| current `projections_player_weekly` rows | 100 |

Current overlap with the Trade Analyzer top 100:

| Join strategy | Matched candidates |
| --- | ---: |
| `source_player_key` | 51 |
| `player_id_internal` | 51 |
| `gsis_id` | 51 |
| exact name + position + team | 47 |
| materializable `source_player_key` | 51 |
| materializable `player_id_internal` | 51 |

Projection rows not in the top 100 Trade Analyzer candidate set: 49.

Examples include projection-ranked quarterbacks and lower-market assets such as Philip Rivers, Tyrod Taylor, Quinn Ewers, Michael Penix, Shedeur Sanders, Kirk Cousins, Geno Smith, and other players outside the top 100 market-value score universe.

## Missing Top Market Candidates

Top market candidates missing current week 18 projection context include:

| Rank | Player | Pos | Team | Player ID | Source key | Market value |
| ---: | --- | --- | --- | --- | --- | ---: |
| 7 | Jeremiyah Love | RB | ARI | `sleeper:13287` | `LOV121782` | 7373 |
| 15 | CeeDee Lamb | WR | DAL | `sleeper:6786` | `00-0036358` | 6295 |
| 17 | Drake London | WR | ATL | `sleeper:8112` | `00-0037238` | 5892 |
| 22 | Tetairoa McMillan | WR | CAR | `sleeper:12526` | `00-0040124` | 4811 |
| 25 | Emeka Egbuka | WR | TB | `sleeper:12514` | `00-0040129` | 4625 |
| 27 | Breece Hall | RB | NYJ | `sleeper:8155` | `00-0038120` | 4495 |
| 29 | Carnell Tate | WR | TEN | `sleeper:13279` | `TAT143045` | 4409 |
| 31 | Tyler Warren | TE | IND | `sleeper:12518` | `00-0040128` | 4341 |
| 32 | Quinshon Judkins | RB | CLE | `sleeper:12512` | `00-0040784` | 4338 |
| 35 | Garrett Wilson | WR | NYJ | `sleeper:8146` | `00-0037740` | 4148 |
| 36 | TreVeyon Henderson | RB | NE | `sleeper:12529` | `00-0040734` | 4105 |
| 38 | Ladd McConkey | WR | LAC | `sleeper:11635` | `00-0039915` | 3984 |
| 43 | Jordyn Tyson | WR | NO | `sleeper:13281` | `TYS405541` | 3836 |
| 46 | Jadarian Price | RB | SEA | `sleeper:13286` | `PRI206342` | 3767 |
| 50 | Rome Odunze | WR | CHI | `sleeper:11620` | `00-0039919` | 3652 |

## Larger Projection Limit Dry-Runs

The projection engine supports larger bounded limits:

- default limit: 250
- max limit: 1000

Dry-run commands:

```powershell
.\venv\Scripts\python.exe -m src.projection_engine --horizon weekly --season 2025 --week 18 --scoring-profile ppr --league-type redraft --roster-format one_qb --limit 250 --dry-run
.\venv\Scripts\python.exe -m src.projection_engine --horizon weekly --season 2025 --week 18 --scoring-profile ppr --league-type redraft --roster-format one_qb --limit 500 --dry-run
```

Dry-run results:

| Limit | Exit | Projection rows | Ranking rows | Materializable candidates covered | Expected missing materializable candidates |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 250 | 0 | 250 | 250 | 73 of 87 | 14 |
| 500 | 0 | 500 | 500 | 77 of 87 | 10 |

The CLI dry-runs were non-mutating.

## Limit 250 Coverage

Expected materializable candidates still missing after a limit 250 refresh:

| Rank | Player | Pos | Team | Player ID | Source key |
| ---: | --- | --- | --- | --- | --- |
| 7 | Jeremiyah Love | RB | ARI | `sleeper:13287` | `LOV121782` |
| 25 | Emeka Egbuka | WR | TB | `sleeper:12514` | `00-0040129` |
| 29 | Carnell Tate | WR | TEN | `sleeper:13279` | `TAT143045` |
| 43 | Jordyn Tyson | WR | NO | `sleeper:13281` | `TYS405541` |
| 46 | Jadarian Price | RB | SEA | `sleeper:13286` | `PRI206342` |
| 56 | Makai Lemon | WR | PHI | `sleeper:13294` | `LEM694125` |
| 58 | Marvin Harrison | WR | ARI | `sleeper:11628` | `00-0007024` |
| 75 | KC Concepcion | WR | CLE | `sleeper:13298` | `CON046719` |
| 84 | Kenyon Sadiq | TE | NYJ | `sleeper:13330` | `SAD482340` |
| 88 | David Montgomery | RB | HOU | `gsis:00-0035685` | `00-0035685` |
| 90 | Omar Cooper | WR | NYJ | `sleeper:13276` | `COO816508` |
| 96 | Jonah Coleman | RB | DEN | `sleeper:13345` | `COL293648` |
| 97 | Chuba Hubbard | RB | CAR | `sleeper:7594` | `00-0036555` |
| 98 | Denzel Boston | WR | CLE | `sleeper:13346` | `BOS677861` |

## Limit 500 Coverage

Expected materializable candidates still missing after a limit 500 refresh:

| Rank | Player | Pos | Team | Player ID | Source key |
| ---: | --- | --- | --- | --- | --- |
| 7 | Jeremiyah Love | RB | ARI | `sleeper:13287` | `LOV121782` |
| 29 | Carnell Tate | WR | TEN | `sleeper:13279` | `TAT143045` |
| 43 | Jordyn Tyson | WR | NO | `sleeper:13281` | `TYS405541` |
| 46 | Jadarian Price | RB | SEA | `sleeper:13286` | `PRI206342` |
| 56 | Makai Lemon | WR | PHI | `sleeper:13294` | `LEM694125` |
| 75 | KC Concepcion | WR | CLE | `sleeper:13298` | `CON046719` |
| 84 | Kenyon Sadiq | TE | NYJ | `sleeper:13330` | `SAD482340` |
| 90 | Omar Cooper | WR | NYJ | `sleeper:13276` | `COO816508` |
| 96 | Jonah Coleman | RB | DEN | `sleeper:13345` | `COL293648` |
| 98 | Denzel Boston | WR | CLE | `sleeper:13346` | `BOS677861` |

The remaining gap is concentrated in future rookies or players without enough projection feature coverage in the current deterministic source universe.

## Selected Path

Selected path: `A. Larger bounded projection refresh is sufficient`.

Reason:

- Limit 250 materially improves materializable player coverage from 51 to 73.
- Limit 500 improves materializable player coverage from 51 to 77.
- The remaining 10 after limit 500 appear to require richer projection inputs or a trade-candidate universe mode that can handle sparse rookie and future-asset data.
- Path B is not required before trying the larger bounded refresh, but it remains a future design option if the operator wants every top market asset covered.

Status:

- Write authorization is unset.
- No projection rows were written in this phase.
- No score rows were written in this phase.

Recommended authorized command if the operator approves path A:

```powershell
$env:ALLOW_PROJECTION_CONTEXT_REFRESH = "true"
.\venv\Scripts\python.exe -m src.projection_engine --horizon weekly --season 2025 --week 18 --scoring-profile ppr --league-type redraft --roster-format one_qb --limit 500
Remove-Item Env:\ALLOW_PROJECTION_CONTEXT_REFRESH
```

## Score Dry-Run Status

Because no larger projection refresh was written, the score dry-run remains at the Phase 23.3E baseline.

Command:

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v0_2025_001 --dry-run
```

Result:

| Metric | Value |
| --- | ---: |
| wrote | `false` |
| score row count | 100 |
| materializable player row count | 87 |
| excluded pick count | 13 |
| written row count | 0 |
| trade score min | 11.5784 |
| trade score max | 55.2387 |
| trade score avg | 33.9620 |
| confidence min | 28.66 |
| confidence max | 57.0 |
| confidence avg | 48.7489 |
| confidence >= 70 | 0 |
| `missing_model_run_id` | 48 |
| `stale_projection_context` | 1 |
| `temporary_name_join_identity` | 35 |
| `missing_fraud_context` | 45 |
| dry-run duplicate grain count | 0 |

Projection join distribution:

| Strategy | Rows |
| --- | ---: |
| `source_player_key` | 52 |
| none | 48 |

## Row Count Verification

Read-only warehouse check after this phase:

| Object | Rows |
| --- | ---: |
| `trade_player_scores` | 0 |
| `projection_rankings_current` 2025 week 18 PPR redraft one-QB | 100 |
| `projections_player_weekly` 2025 week 18 PPR redraft one-QB | 100 |

## Local Checks

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass, 22 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 340 tests |
| `.\venv\Scripts\python.exe -m py_compile src\projection_engine.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 passed, 0 failed |

## Materialization Recommendation

Do not materialize Trade Analyzer score rows yet.

Recommended next step:

1. Authorize a bounded projection refresh at `limit=500` if the operator accepts path A.
2. Rerun the Trade Analyzer score dry-run.
3. Expect `missing_model_run_id` to improve materially, likely from 48 to about 23 total rows including 13 draft picks and 10 missing materializable players.
4. If those remaining 10 are unacceptable, design path B with a projection `trade_assets` candidate-source mode.
5. Keep `ALLOW_TRADE_SCORE_MATERIALIZATION` unset until a separate score-write approval.

Final decision: `PROJECTION LIMIT EXPANSION BLOCKED`.
