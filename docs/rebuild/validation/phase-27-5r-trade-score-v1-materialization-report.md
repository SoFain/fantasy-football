# Phase 27.5R Trade Score V1 Materialization Report

## Final Decision

TRADE SCORE V1 MATERIALIZED WITH WARNINGS

The retry corrected the Phase 27.5 authorization flow. `ALLOW_TRADE_SCORE_MATERIALIZATION` was unset before the phase, set only inside the same-session write wrapper, then removed immediately afterward. The bounded write materialized the 77 policy-materializable v1 player rows for staging review.

No production deploy occurred. Production score flags remain false.

## Scope

This phase wrote only bounded Trade Analyzer score v1 rows for staging review:

| Field | Value |
| --- | --- |
| model version | `trade_score_v1_2025_001` |
| season | 2025 |
| week | 18 |
| scoring profile | `ppr` |
| league type | `redraft` |
| roster format | `one_qb` |

No deployment, production feature flag change, Cloud Run Job trigger, Scheduler job, ingestion, LLM action, Pigskin prompt, scrape, Firebase artifact, draft-pick materialization, or commit occurred.

## Authorization Flow

The starting state was expected to be unset. The write wrapper was the authorization source of truth.

| Moment | `ALLOW_TRADE_SCORE_MATERIALIZATION` |
| --- | --- |
| before write wrapper | unset |
| inside write wrapper | `true` |
| after write wrapper | unset |

The write command was run inside:

```powershell
try {
$env:ALLOW_TRADE_SCORE_MATERIALIZATION = "true"

echo "ALLOW_TRADE_SCORE_MATERIALIZATION=$env:ALLOW_TRADE_SCORE_MATERIALIZATION"

.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v1_2025_001 --write

} finally {
Remove-Item Env:\ALLOW_TRADE_SCORE_MATERIALIZATION -ErrorAction SilentlyContinue
}
```

Execution note: the Python write completed successfully and reported `written_row_count=77`. A local transcript-capture redirection wrapper emitted a PowerShell warning after the command output. The environment gate was verified unset afterward and BigQuery verification confirmed the write.

## Preflight Results

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass, 36 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 363 tests |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |

The full test suite emits mocked pipeline, load, and ranking logs from existing tests. This phase did not run live ingestion or LLM-backed actions.

## Pre-Existing Table State

Before write:

| Metric | Value |
| --- | ---: |
| total `trade_player_scores` rows | 77 |
| `trade_score_v0_2025_001` rows | 77 |
| all `trade_score_v1_2025_001` rows | 0 |
| target v1 rows | 0 |
| target duplicate grains | 0 |
| target PICK rows | 0 |
| target missing model-run rows | 0 |
| target unresolved identity rows | 0 |

The save path uses a staging table plus `MERGE` on the score grain:

`model_version, season, week, scoring_profile_id, league_type_id, roster_format_id, player_id`

Because the target v1 slice was empty, this run inserted 77 rows. The merge path is idempotent for this grain.

## Final Dry-Run Summary

The final dry-run before write used:

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v1_2025_001 --dry-run
```

Result:

| Metric | Value |
| --- | ---: |
| source rows | 100 |
| score rows | 100 |
| materializable player rows | 77 |
| excluded rows | 23 |
| excluded pick rows | 13 |
| duplicate dry-run grain rows | 0 |
| materializable PICK rows | 0 |
| `projection_freshness_metadata_missing` rows | 77 |
| `team_context_mismatch_warning` rows | 5 |
| `role_source_gap` penalty rows | 29 in dry-run, 6 after materializable filtering |
| written rows | 0 |
| `wrote` | false |

The dry-run confirmed draft picks were excluded and no rows missing materialization policy were eligible.

## Write Result

The write command reported:

| Metric | Value |
| --- | ---: |
| dry run | false |
| `wrote` | true |
| `written_row_count` | 77 |
| source rows | 100 |
| score rows | 100 |
| materializable player rows | 77 |
| excluded rows | 23 |
| excluded pick rows | 13 |

Excluded reason counts:

| Reason | Rows |
| --- | ---: |
| `missing_model_run_id` | 23 |
| `pick_row` | 13 |
| `draft_pick_score_lane_pending` | 13 |

## Post-Write Verification

After write:

| Metric | Value |
| --- | ---: |
| total `trade_player_scores` rows | 154 |
| v0 rows still present | 77 |
| all v1 rows | 77 |
| target v1 rows | 77 |
| target duplicate grains | 0 |
| target PICK rows | 0 |
| target rows missing `model_run_id` | 0 |
| target unresolved identity rows | 0 |
| target stale projection rows | 0 |
| target invalid `trade_score` rows | 0 |
| target missing `confidence_score` rows | 0 |
| target missing `component_json` rows | 0 |
| target missing `missing_flags_json` rows | 0 |
| target missing `source_freshness_json` rows | 0 |
| target `projection_freshness_metadata_missing` rows | 77 |
| target `team_context_mismatch_warning` rows | 5 |

Acceptance checks passed: no PICK rows, no missing model-run rows, no unresolved identity rows, no duplicate grains.

## Score Distribution

Materialized v1 target rows only:

| Metric | Value |
| --- | ---: |
| rows | 77 |
| trade score min | 15.93 |
| trade score max | 88.93 |
| trade score avg | 51.76 |
| trade score stddev | 16.59 |
| confidence min | 44.86 |
| confidence max | 79.53 |
| confidence avg | 72.53 |
| confidence stddev | 8.83 |
| risk adjustment min | -6.00 |
| risk adjustment max | -2.22 |
| risk adjustment avg | -3.22 |
| source stability min | 80.00 |
| source stability max | 100.00 |
| source stability avg | 98.44 |

Confidence buckets:

| Bucket | Rows |
| --- | ---: |
| `70-79` | 57 |
| `60-69` | 10 |
| `50-59` | 6 |
| `<50` | 4 |

Tier distribution:

| Tier | Rows |
| --- | ---: |
| elite | 1 |
| strong | 9 |
| starter | 11 |
| flex | 27 |
| depth | 24 |
| avoid | 5 |

Position distribution:

| Position | Rows |
| --- | ---: |
| QB | 13 |
| RB | 26 |
| TE | 8 |
| WR | 30 |

Role-source status in written rows:

| Status | Rows |
| --- | ---: |
| `suppressed_due_to_alternate_context` | 68 |
| `warning_only` | 3 |
| `penalty` | 6 |

## Top 25

| Player | Pos | Team | Score | Confidence | Tier |
| --- | --- | --- | ---: | ---: | --- |
| Bijan Robinson | RB | ATL | 88.93 | 79.53 | elite |
| Ja'Marr Chase | WR | CIN | 83.35 | 78.35 | strong |
| Puka Nacua | WR | LAR | 82.96 | 72.72 | strong |
| Jahmyr Gibbs | RB | DET | 81.91 | 79.53 | strong |
| Jaxon Smith-Njigba | WR | SEA | 79.88 | 79.53 | strong |
| Amon-Ra St. Brown | WR | DET | 78.71 | 79.53 | strong |
| Drake Maye | QB | NE | 77.74 | 68.66 | strong |
| Christian McCaffrey | RB | SF | 77.53 | 79.53 | strong |
| De'Von Achane | RB | MIA | 76.99 | 78.35 | strong |
| Josh Allen | QB | BUF | 74.86 | 67.97 | strong |
| Ashton Jeanty | RB | LV | 72.70 | 79.53 | starter |
| Chase Brown | RB | CIN | 72.36 | 79.53 | starter |
| Chris Olave | WR | NO | 71.05 | 78.35 | starter |
| Brock Bowers | TE | LV | 67.01 | 73.23 | starter |
| Omarion Hampton | RB | LAC | 66.09 | 70.12 | starter |
| Colston Loveland | TE | CHI | 66.04 | 78.29 | starter |
| James Cook | RB | BUF | 64.75 | 78.90 | starter |
| Malik Nabers | WR | NYG | 63.92 | 44.86 | starter |
| Jonathan Taylor | RB | IND | 63.57 | 79.53 | starter |
| Justin Jefferson | WR | MIN | 62.27 | 79.53 | starter |
| Nico Collins | WR | HOU | 62.22 | 76.30 | starter |
| Caleb Williams | QB | CHI | 59.55 | 64.91 | flex |
| Trey McBride | TE | ARI | 59.33 | 72.72 | flex |
| Saquon Barkley | RB | PHI | 59.31 | 78.35 | flex |
| George Pickens | WR | DAL | 59.10 | 78.64 | flex |

## Bottom 25

| Player | Pos | Team | Score | Confidence | Tier |
| --- | --- | --- | ---: | ---: | --- |
| Chuba Hubbard | RB | CAR | 15.93 | 76.02 | avoid |
| Bhayshul Tuten | RB | JAX | 20.69 | 74.93 | avoid |
| David Montgomery | RB | HOU | 22.90 | 78.41 | avoid |
| Marvin Harrison | WR | ARI | 23.50 | 69.63 | avoid |
| Jaylen Waddle | WR | DEN | 26.48 | 77.32 | avoid |
| Bo Nix | QB | DEN | 30.99 | 69.12 | depth |
| Brian Thomas | WR | JAX | 31.22 | 74.42 | depth |
| Quentin Johnston | WR | LAC | 32.32 | 73.96 | depth |
| Jalen Hurts | QB | PHI | 32.87 | 67.20 | depth |
| Christian Watson | WR | GB | 34.17 | 70.24 | depth |
| Josh Jacobs | RB | GB | 35.02 | 76.56 | depth |
| Terry McLaurin | WR | WAS | 35.26 | 70.85 | depth |
| Jaxson Dart | QB | NYG | 35.83 | 71.09 | depth |
| Jayden Daniels | QB | WAS | 35.86 | 57.04 | depth |
| D'Andre Swift | RB | CHI | 36.16 | 78.16 | depth |
| Bucky Irving | RB | TB | 36.87 | 71.30 | depth |
| RJ Harvey | RB | DEN | 37.62 | 79.53 | depth |
| Sam LaPorta | TE | DET | 37.97 | 50.41 | depth |
| Rome Odunze | WR | CHI | 38.51 | 54.27 | depth |
| DeVonta Smith | WR | PHI | 39.11 | 78.69 | depth |
| Javonte Williams | RB | DAL | 39.25 | 77.89 | depth |
| Ladd McConkey | WR | LAC | 39.67 | 77.32 | depth |
| Alec Pierce | WR | IND | 40.52 | 76.26 | depth |
| Emeka Egbuka | WR | TB | 40.53 | 77.96 | depth |
| Tyler Warren | TE | IND | 40.92 | 79.19 | depth |

## Warning Rows

Projection freshness:

| Warning | Rows |
| --- | ---: |
| `projection_freshness_metadata_missing` | 77 |

Team-context mismatch rows:

| Player | Team | Score | Confidence |
| --- | --- | ---: | ---: |
| Kenneth Walker | KC | 57.91 | 79.20 |
| A.J. Brown | NE | 57.11 | 76.78 |
| Travis Etienne | NO | 46.45 | 79.53 |
| Jaylen Waddle | DEN | 26.48 | 77.32 |
| David Montgomery | HOU | 22.90 | 78.41 |

Role-source penalty rows:

| Player | Score | Confidence | Penalty |
| --- | ---: | ---: | ---: |
| Malik Nabers | 63.92 | 44.86 | 3.0 |
| Tucker Kraft | 56.13 | 49.44 | 3.0 |
| Cam Skattebo | 50.22 | 49.52 | 3.0 |
| Garrett Wilson | 46.56 | 48.76 | 3.0 |
| Rome Odunze | 38.51 | 54.27 | 3.0 |
| Sam LaPorta | 37.97 | 50.41 | 3.0 |

High-market low-score rows with market score >= 85 and trade score < 45: none.

## Validation Results

| Pattern | Result |
| --- | --- |
| `trade_player_scores` | pass, 11 of 11 |
| `compat_trade_player_scores` | pass, 2 of 2 |
| `market` | pass, 9 of 9 |
| `content_brief` | pass, 11 of 11 |

## Production Untouched Confirmation

Read-only Cloud Run service describe confirmed:

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard` |
| latest ready revision | `nfl-studio-dashboard-00077-2jp` |
| traffic | `nfl-studio-dashboard-00077-2jp:100` |
| image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |

No deploy command was run. No production flag command was run.

## Remaining Warnings

- This is staging-review data. Production score flags remain false.
- Projection raw `as_of_*` metadata is still missing across the v1 target rows. The warning is visible and should remain visible until the projection source contract is cleaned up.
- Five team-context mismatch rows need human review before public score exposure.
- Draft picks remain diagnostic-only and are not materialized into player score rows.
- The score table now contains both v0 and v1 rows. Downstream staging UI must select the intended model version.

## Recommended Next Phase

Proceed to staging UI validation only. Keep production flags false.

Recommended Phase 27.6:

- deploy or verify staging uses score flags only in staging;
- confirm `compat_trade_player_scores_current` surfaces the v1 rows expected for review;
- validate Trade Lab selected-player score cards;
- verify pick rows still show score unavailable or market-only context;
- confirm production remains disabled.
