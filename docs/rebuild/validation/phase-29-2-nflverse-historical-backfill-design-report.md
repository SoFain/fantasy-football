# Phase 29.2 nflverse Historical Backfill Design Report

Date: 2026-06-29

Final decision: NFLVERSE HISTORICAL BACKFILL DESIGN READY WITH WARNINGS

## Scope

Phase 29.2 was a read-only design and inspection phase for nflverse historical source acquisition and BigQuery backfill planning. No BigQuery rows were written, no migrations or tables were created, no ingestion or backfill was run, no Cloud Run Jobs were triggered, no Scheduler jobs were created, no deploy occurred, no feature flags were changed, no LLM-backed action or Pigskin prompt was submitted, no scraping or external fetch occurred, and no Firebase artifacts were created.

This design is meant to move directly into additive contracts and migrations in Phase 29.3.

## Authorization Gate State

All checked gates were unset:

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

Future Phase 29 gates are proposed later in this report. None were set in this phase.

## Git State

Latest commit:

```text
a73656c Document draft pick score release package
```

Recent commits:

```text
a73656c Document draft pick score release package
6e4b565 Draft pick score lane and staging UI
6158549 Document Trade Score v1 Track A closeout
3268a5a Document Trade Score v1 UI polish package
9ec04f3 Polish Trade Score v1 staging UI
aa543d0 Document Phase 26 evidence commit
251fd18 Document Phase 25 production closeout
b3b0ec1 Document Data Ops hardening production rollout
22e3256 Gate Data Ops local subprocess controls
63149aa Clean up production warning noise
```

Phase 28 commits are present. `docs/rebuild/validation/phase-29-1-pigskin-advanced-metrics-source-audit-report.md` remains untracked. No files were staged before this report was created. The untracked backlog is still mostly historical Phase 17 through Phase 28 validation reports plus Phase 29.1.

## Deployment State

Read-only Cloud Run describe was run.

### Production

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Revision | `nfl-studio-dashboard-00077-2jp` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Traffic | `nfl-studio-dashboard-00077-2jp:100` |
| Ingress | `all` |

Production flags:

| Flag | Value |
| --- | --- |
| `USE_TRADE_PICK_SCORE_V0` | unset |
| `USE_COMPAT_TRADE_PICK_SCORE` | unset |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |

### Staging

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard-staging` |
| URL | `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app` |
| Revision | `nfl-studio-dashboard-staging-00029-jtb` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` |
| Traffic | `nfl-studio-dashboard-staging-00029-jtb:100` |
| Ingress | `all` |

Staging flags:

| Flag | Value |
| --- | --- |
| `USE_TRADE_PICK_SCORE_V0` | `true` |
| `USE_COMPAT_TRADE_PICK_SCORE` | `true` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `true` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `true` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `true` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |

## Safety Check

`.\venv\Scripts\python.exe scripts\check_deployment_safety.py` passed. The checker confirmed no Firebase artifacts, no tracked secrets, default-off feature flags, no Pigskin `execute_bigquery_sql`, and compile health for `app.py`, `src`, and `scripts`.

## Current Warehouse Coverage Snapshot

Read-only BigQuery metadata and count checks show the current historical coverage is not enough for the owner goal:

| Table | Rows | Current coverage |
| --- | ---: | --- |
| `play_by_play` | 48,771 | 2025 weeks 1-22 |
| `weekly_metrics` | 19,421 | 2025 weeks 1-22 |
| `team_descriptions` | 36 | 2025 |
| `draft_picks` | 257 | 2025 |
| `player_rosters` | 25,040 | 2025 |
| `ngs_passing` | 605 | 2025 weeks 0-23 |
| `ngs_rushing` | 648 | 2025 weeks 0-23 |
| `ngs_receiving` | 1,402 | 2025 weeks 0-23 |
| `ftn_charting` | 47,316 | 2025 weeks 1-22 |
| `weekly_snap_counts` | 26,612 | 2025 weeks 1-22 |
| `injury_reports` | 6,068 | 2025 weeks 1-22 |
| `depth_charts` | 554,215 | 2025 |
| `analytics_player_weekly_truth` | 18,539 | 2025 weeks 1-18 |
| `analytics_player_qb_weekly` | 4,529 | 2025 weeks 1-18 |
| `analytics_game_environment` | 272 | 2025 weeks 1-18 |
| `mart_player_profiles_current` | 27,864 | 2025 week 18 |
| `mart_llm_player_context_packet` | 9,340 | 2025 week 18 |

Conclusion: the current warehouse can prove the concept, but it is a 2025 slice. It should not be treated as the long-term historical source of truth.

## nflverse Loader Wiring Audit

Local inspection of installed `nflreadpy` names and signatures was performed without fetching data. The repo currently imports `nflreadpy` in `src/extract.py` and calls a subset of available loaders.

| Source family | Installed loader | Current repo wiring | Season-range support | Week-bound support | Phase 29 decision |
| --- | --- | --- | --- | --- | --- |
| play-by-play | `load_pbp(seasons)` | wired as `get_pbp_data`, loaded to `play_by_play` | yes | no | keep loader, move target to `raw_nflverse_pbp` |
| weekly player stats | `load_player_stats(seasons, summary_level='week')` | wired as `get_weekly_data`, loaded to `weekly_metrics` | yes | no | keep loader, move target to `raw_nflverse_weekly` |
| generic stats | `load_stats` | installed, not wired | likely yes, signature unavailable | unknown | inspect in Phase 29.3 only if it adds useful fields |
| rosters | `load_rosters(seasons)` | installed, not wired | yes | no | add extractor |
| weekly rosters | `load_rosters_weekly(seasons)` | installed, not wired | yes | likely season-level load with week rows | add extractor |
| players | `load_players()` | wired as `get_players_data`, replicated into `player_rosters` | static | not applicable | split into `raw_nflverse_players` |
| fantasy player IDs | `load_ff_playerids()` | installed, not wired | static | not applicable | add extractor, use in identity staging |
| schedules | `load_schedules(seasons)` | installed, not wired | yes | schedule rows include week | add extractor early |
| injuries | `load_injuries(seasons)` | wired as `get_injury_reports_data` | yes | no | keep loader, move target to `raw_nflverse_injuries` |
| depth charts | `load_depth_charts(seasons)` | wired as `get_depth_charts_data` | yes | no | keep loader, move target to raw depth table |
| snap counts | `load_snap_counts(seasons)` | wired as `get_snap_counts_data` | yes | no | keep loader, move target to raw snap table |
| participation | `load_participation(seasons)` | installed, not wired | yes | unknown | add extractor, validate columns before route claims |
| teams | `load_teams()` | wired as `get_team_data`, replicated into `team_descriptions` | static | not applicable | split into `raw_nflverse_teams` |
| team stats | `load_team_stats(seasons, summary_level='week')` | installed, not wired | yes | no | add extractor if it reduces PBP scan cost |
| NGS passing | `load_nextgen_stats(seasons, stat_type='passing')` | wired | yes, code filters 2016-current | no | keep, move to raw NGS passing |
| NGS rushing | `load_nextgen_stats(seasons, stat_type='rushing')` | wired | yes, code filters 2016-current | no | keep, move to raw NGS rushing |
| NGS receiving | `load_nextgen_stats(seasons, stat_type='receiving')` | wired | yes, code filters 2016-current | no | keep, move to raw NGS receiving |
| FTN charting | `load_ftn_charting(seasons)` | wired | yes, code filters 2022-current | no | keep, move to raw FTN charting |
| draft picks | `load_draft_picks(seasons)` | wired as all draft picks filtered in transform | yes | not applicable | keep, move to raw draft picks |

Current pipeline behavior:

- `src.pipeline` supports `--plan-only`, `--ingest-only`, explicit `--seasons`, `--write-disposition WRITE_APPEND`, and `--allow-full-refresh`.
- It rejects `--week-start` and `--week-end`: week bounds are not supported by the current nflreadpy ingestion path.
- It writes directly to existing legacy source table names, not to new raw `raw_nflverse_*` tables.
- It uses `WRITE_APPEND` by default, but does not implement row-level idempotent merge for historical fact tables.
- `src.load.load_df_to_partitioned_table` range partitions by integer `season` and performs schema-aware append when target schema exists.
- The existing Cloud Run `ingest-nflverse` job exists, but its dry-run path says `src.pipeline has no dry-run mode`, and its live path calls `run_pipeline` with season and write disposition only. It is not ready for Phase 29 historical backfill as-is.

Safety conclusion: reuse extraction patterns and schema-coercion helpers, not the current table names or live job contract.

## Target Historical Season Ranges

Default backfill target: 2014 through the latest completed or available nflverse season, with source-specific extensions when cheap. This gives the requested 10-plus seasons while avoiding a first pass that is too broad.

| Source family | Target range | Priority | Notes |
| --- | --- | --- | --- |
| play-by-play | 2014-current available | backfill required now | Core source for EPA, success, CPOE, team context, WOPR components, and backtests. |
| weekly player stats | 2014-current available | backfill required now | Core source for fantasy and player weekly stats. |
| schedules | 2014-current available | backfill required now | Needed for game context, teams, dates, weather/stadium, and weekly refresh boundaries. |
| rosters | 2014-current available | backfill required now | Needed for identity and current team context. |
| weekly rosters | 2014-current available if supported | backfill required now | Needed for historical team/position/status context. |
| players | all available snapshot | backfill required now | Static identity source. |
| fantasy player IDs | all available snapshot | backfill required now | Critical for joining nflverse and fantasy platforms. |
| team metadata | current plus historical team aliases | backfill required now | Static dimension, cheap. |
| team stats | 2014-current available | backfill useful but lower priority | Add if it materially reduces PBP scans. |
| injuries | 2014-current available | backfill useful but lower priority | Useful for context and inactive status. |
| depth charts | 2014-current available if reliable | backfill useful but lower priority | Role context, but not first blocker. |
| snap counts | 2014-current available, code supports from 2012 | backfill required now | Needed for snap share and role stability. |
| participation | 2014-current if supported | source not wired yet | Validate columns before route or participation claims. |
| NGS passing | 2016-current, per current code guard | limited years expected | Tier 2 enrichment. |
| NGS rushing | 2016-current, per current code guard | limited years expected | Tier 2 enrichment. |
| NGS receiving | 2016-current, per current code guard | limited years expected | Tier 2 enrichment. |
| FTN charting | 2022-current, per current code guard | limited years expected | Tier 2 enrichment. |
| draft picks | 2014-current plus older if cheap | useful but lower priority | Rookie/draft context, not weekly advanced metric blocker. |

If a source supports fewer years, the backfill should store available seasons, add missing-source flags, and keep moving.

## Common Raw Load Metadata

Every raw `raw_nflverse_*` table should add:

| Field | Purpose |
| --- | --- |
| `source_system` | Literal `nflverse`. |
| `source_loader` | Loader name, for example `nflreadpy.load_pbp`. |
| `source_version` | `nflreadpy` package version if available, plus optional nflverse data release label. |
| `source_season` | Source season used for extraction. |
| `source_week` | Nullable week when the row has week grain. |
| `source_refresh_id` | Stable ID for one source acquisition run. |
| `loaded_at` | BigQuery load timestamp. |
| `loaded_by` | Runner identity, for example `local_plan`, `cloud_run_job`, or service name. |
| `row_hash` | Hash over natural key and source row payload for idempotency and drift detection. |
| `raw_payload_json` | Optional. Use only when practical and not too expensive. Prefer explicit typed passthrough columns. |

Raw retention policy:

- Keep historical raw rows indefinitely unless storage cost becomes material.
- Preserve raw facts by `source_refresh_id` only if the owner wants audit snapshots. Otherwise merge into the current raw fact table and keep refresh metadata.
- Do not expose raw tables to Pigskin or Streamlit.

## Raw nflverse Landing Table Contracts

| Raw table | Purpose | Loader | Grain | Required columns | Idempotency key | Partition and clustering | Refresh strategy | Replaces |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `raw_nflverse_pbp` | Historical play facts for player/team/game metrics. | `load_pbp` | one play row | `season`, `week`, `game_id`, `play_id`, teams, play type flags, player IDs, EPA, success, CPOE, air yards, yardline, game clock, weather/line fields where present | `season`, `game_id`, `play_id` | partition by `season` or `game_date`; cluster by `season`, `week`, `game_id`, `posteam`, `defteam` | season-batched historical merge; current-season impacted-week merge | `play_by_play` as source |
| `raw_nflverse_weekly` | Weekly player stats and fantasy inputs. | `load_player_stats` | one player, season, week, team | `season`, `week`, `player_id`, name, team, opponent, position, passing/rushing/receiving stats, targets, air yards, fantasy components | `season`, `week`, `player_id`, `team`, `position` | partition by `season`; cluster by `week`, `player_id`, `team`, `position` | season-batched merge; impacted-week current merge | `weekly_metrics` as source |
| `raw_nflverse_rosters` | Seasonal roster identity and metadata. | `load_rosters` | one player roster row per season/team | `season`, `player_id`, `gsis_id`, name, team, position, status where available | `season`, `player_id`, `team` | partition by `season`; cluster by `player_id`, `team`, `position` | season merge | legacy `player_rosters` source role |
| `raw_nflverse_rosters_weekly` | Weekly roster/team/status identity. | `load_rosters_weekly` | one player, season, week, team | `season`, `week`, player IDs, name, team, position, status where available | `season`, `week`, `player_id`, `team` | partition by `season`; cluster by `week`, `player_id`, `team`, `position` | impacted-week merge | missing today |
| `raw_nflverse_players` | Static player dimension. | `load_players` | one player | player IDs, normalized/display names, position, latest team, physical/profile fields where present | strongest available player ID | no partition required; cluster by player IDs, name | full snapshot merge | current replicated `player_rosters` misuse |
| `raw_nflverse_ff_playerids` | Fantasy-platform ID bridge. | `load_ff_playerids` | one player identity mapping | nflverse IDs, fantasy IDs, Sleeper IDs where present, names | strongest available player ID plus platform ID | cluster by player IDs and platform IDs | full snapshot merge | missing today |
| `raw_nflverse_schedules` | Game schedule and environment seed. | `load_schedules` | one game | `season`, `week`, `game_id`, game date, home/away teams, stadium/roof/surface/weather/line fields where present | `season`, `week`, `game_id` | partition by `season` or `game_date`; cluster by `week`, `game_id`, `home_team`, `away_team` | season merge; current impacted-week merge | current derived game environment source |
| `raw_nflverse_teams` | Team metadata and aliases. | `load_teams` | one team row | team abbreviation, names, conference/division, colors/logos where present | team abbreviation plus source version | cluster by team | full snapshot merge | `team_descriptions` |
| `raw_nflverse_team_stats` | Weekly team stats if useful. | `load_team_stats` | one team, season, week | `season`, `week`, team, offense/defense team metrics from source | `season`, `week`, `team` | partition by `season`; cluster by `week`, `team` | season merge | not wired today |
| `raw_nflverse_injuries` | Injury report source. | `load_injuries` | one report row | `season`, `week`, team, player IDs, position, report/practice injury fields | `season`, `week`, `team`, `gsis_id`, injury fields hash | partition by `season`; cluster by `week`, `gsis_id`, `team` | impacted-week merge | `injury_reports` |
| `raw_nflverse_depth_charts` | Depth and role source. | `load_depth_charts` | one player/team/depth row | `season`, team, player, `gsis_id`, position, position rank, date/week if present | `season`, team, `gsis_id`, position, rank, date if present | partition by `season`; cluster by team, `gsis_id`, position | season or current snapshot merge | `depth_charts` |
| `raw_nflverse_snap_counts` | Snap count source. | `load_snap_counts` | one player, team, game/week | `season`, `week`, `game_id`, player, team, position, offensive/defensive/ST snaps and pct | `season`, `week`, `game_id`, player ID or name/team | partition by `season`; cluster by `week`, player/team/position | impacted-week merge | `weekly_snap_counts` |
| `raw_nflverse_participation` | Participation source. | `load_participation` | inspect in Phase 29.3 | source player/game/team/participation fields | source natural key after schema inspection | partition by `season`; cluster by `week`, `game_id`, player/team | add as source validation first | missing today |
| `raw_nflverse_ngs_passing` | NGS QB passing context. | `load_nextgen_stats(..., passing)` | one QB, season, week | `season`, `week`, `player_gsis_id`, team, attempts, expected completion, air-yards fields | `season`, `week`, `player_gsis_id`, team | partition by `season`; cluster by `week`, `player_gsis_id`, team | season merge | `ngs_passing` |
| `raw_nflverse_ngs_rushing` | NGS rushing context. | `load_nextgen_stats(..., rushing)` | one rusher, season, week | `season`, `week`, `player_gsis_id`, team, attempts, expected yards, RYOE, stacked-box rate | `season`, `week`, `player_gsis_id`, team | partition by `season`; cluster by `week`, `player_gsis_id`, team | season merge | `ngs_rushing` |
| `raw_nflverse_ngs_receiving` | NGS receiving context. | `load_nextgen_stats(..., receiving)` | one receiver, season, week | `season`, `week`, `player_gsis_id`, team, targets, separation, intended air yards, expected YAC | `season`, `week`, `player_gsis_id`, team | partition by `season`; cluster by `week`, `player_gsis_id`, team | season merge | `ngs_receiving` |
| `raw_nflverse_ftn_charting` | FTN play/charting context. | `load_ftn_charting` | one charting row, likely play-level | `season`, `week`, game IDs, play IDs where present, screen/pass-rusher/QB-fault fields | `season`, `week`, `nflverse_game_id`, play key if present | partition by `season`; cluster by `week`, game/play IDs | season merge | `ftn_charting` |
| `raw_nflverse_draft_picks` | Draft context. | `load_draft_picks` | one drafted player | `season`, team, player IDs, position, draft round/pick, college stats if present | `season`, draft team, player ID or pick number | partition by `season`; cluster by player ID, team, position | season merge | `draft_picks` |

## Canonical Staging Table Contracts

### `stg_player_identity`

Purpose: canonical identity bridge across nflverse IDs, GSIS, Sleeper, fantasy IDs, normalized names, team, and position.

| Attribute | Design |
| --- | --- |
| Grain | one row per `player_id_internal` plus source aliases; current snapshot and optionally season/week-valid rows |
| Sources | `raw_nflverse_players`, `raw_nflverse_ff_playerids`, `raw_nflverse_rosters`, `raw_nflverse_rosters_weekly`, existing Sleeper identity only later |
| Keys | `player_id_internal`, `gsis_id`, `nflverse_player_id`, fantasy IDs, Sleeper ID when available |
| Required fields | normalized name, display name, position, current team, historical team, roster status, source IDs |
| Freshness | source freshness JSON by source family |
| Missing flags | missing ID, conflicting team, ambiguous name, missing position |
| Partitioning | no partition for current bridge; optional history table partitioned by `season` |
| Clustering | player IDs, normalized name, team, position |
| Validations | uniqueness by internal ID, no duplicate active strongest ID, identity coverage for weekly/PBP players |

### `stg_game_context`

Purpose: one row per game with schedule, teams, stadium, roof, surface, weather, spread/total if available, and game metadata.

| Attribute | Design |
| --- | --- |
| Grain | `season`, `week`, `game_id` |
| Sources | `raw_nflverse_schedules`, PBP game-level fields, `raw_nflverse_teams` |
| Keys | game ID, home team, away team |
| Required fields | game date, season type, team keys, stadium, roof, surface, temp, wind, total line, spread line where present |
| Freshness | schedule and PBP source freshness |
| Missing flags | missing schedule, missing weather, missing betting line, team alias mismatch |
| Partitioning | `season` or `game_date` |
| Clustering | `season`, `week`, `game_id`, teams |
| Validations | one row per game, team coverage, game date present, no duplicate game IDs |

### `stg_player_week_stats`

Purpose: one row per player, season, week, team, position with weekly stat inputs and fantasy scoring inputs.

| Attribute | Design |
| --- | --- |
| Grain | `season`, `week`, `player_id_internal`, `team`, `position` |
| Sources | `raw_nflverse_weekly`, `stg_player_identity`, roster sources |
| Required fields | passing, rushing, receiving stats, targets, air yards, sacks, turnovers, fantasy inputs, team/opponent, position |
| Freshness | weekly stats and identity freshness |
| Missing flags | missing identity, missing team, missing position, missing opponent, missing stat source |
| Partitioning | `season` |
| Clustering | `week`, `player_id_internal`, `team`, `position` |
| Validations | grain uniqueness, identity coverage, scoring stat sanity, week coverage |

### `stg_team_week_stats`

Purpose: one row per team, season, week with offensive and defensive team context.

| Attribute | Design |
| --- | --- |
| Grain | `season`, `week`, `team` |
| Sources | `raw_nflverse_pbp`, `raw_nflverse_team_stats`, `stg_game_context` |
| Required fields | plays, pass attempts, rush attempts, EPA, success, pace, red-zone plays, defensive EPA allowed, opponent, game IDs |
| Freshness | PBP, team stats, schedule freshness |
| Missing flags | missing team stats source, missing PBP source, schedule mismatch |
| Partitioning | `season` |
| Clustering | `week`, `team` |
| Validations | 32-team coverage where appropriate, team/game consistency, metric ranges |

### `stg_play_player_events`

Purpose: normalized play-level player event rows for targets, rushes, pass attempts, red-zone touches, EPA attribution, and team context.

| Attribute | Design |
| --- | --- |
| Grain | one row per player-event per play, for example passer, receiver, rusher event rows from the same play |
| Sources | `raw_nflverse_pbp`, `stg_player_identity`, `stg_game_context` |
| Required fields | season, week, game ID, play ID, event type, player ID, team, opponent, yardline, EPA, success, target/rush/pass flags |
| Freshness | PBP and identity freshness |
| Missing flags | missing identity, unknown event type, missing EPA, missing yardline |
| Partitioning | `season` or game date |
| Clustering | `season`, `week`, `game_id`, `player_id_internal`, `event_type` |
| Validations | no duplicate event rows, event count matches PBP source within tolerance, EPA attribution sanity |

### `stg_participation_context`

Purpose: snap and participation context. Do not call anything route share unless a true route field exists.

| Attribute | Design |
| --- | --- |
| Grain | player, team, game/week participation row |
| Sources | `raw_nflverse_snap_counts`, `raw_nflverse_participation`, rosters |
| Required fields | season, week, game ID, player ID, team, offense snaps, offense pct, participation fields after inspection |
| Freshness | snap and participation freshness |
| Missing flags | missing snap source, missing participation source, no true route source |
| Partitioning | `season` |
| Clustering | `week`, `player_id_internal`, `team`, `position` |
| Validations | snap pct range, no route share populated without true route column, identity coverage |

## Replacement-Over-Repair Mapping

| Existing object | Decision | Reason |
| --- | --- | --- |
| `play_by_play` | keep but refresh from nflverse | Current table is 2025 only. Use as reference, not historical source. |
| `weekly_metrics` | keep but refresh from nflverse | Current table is 2025 only. Replace source role with `raw_nflverse_weekly`. |
| `player_rosters` | replace with nflverse raw/staging source | Current use mixes static player load and season replication. Prefer rosters, weekly rosters, players, and fantasy IDs. |
| `team_descriptions` | keep but refresh from nflverse | Cheap team dimension, source from `load_teams`. |
| `draft_picks` | keep and use | nflverse-backed and useful for draft/rookie context. |
| `college_player_stats` | defer | Useful only for rookie context, not core nflverse weekly feature warehouse. |
| `ngs_passing` | keep but refresh from nflverse | Useful Tier 2 source, limited historical range. |
| `ngs_rushing` | keep but refresh from nflverse | Useful Tier 2 source, limited historical range. |
| `ngs_receiving` | keep but refresh from nflverse | Useful Tier 2 source, limited historical range. |
| `ftn_charting` | keep but refresh from nflverse | Useful limited-range charting source. |
| `weekly_snap_counts` | keep but refresh from nflverse | Needed for snap share and role stability. |
| `injury_reports` | keep but refresh from nflverse | Use through context marts only. |
| `depth_charts` | keep but refresh from nflverse | Use through role context, not UI raw. |
| `analytics_player_weekly_truth` | keep as derived output only | Rebuild after raw/staging historical sources exist. |
| `analytics_player_qb_weekly` | keep as derived output only | Rebuild from historical PBP. |
| `analytics_game_environment` | keep as derived output only | Rebuild from schedules/PBP game context. |
| `mart_player_profiles_current` | keep as derived output only | Rebuild from advanced metrics and identity. |
| `llm_player_context_packet` | keep as packet contract | Correct Pigskin access pattern. Refresh after metrics. |
| `mart_llm_player_context_packet` | keep as packet backing table | Rebuild after metrics. |
| `active_league_rosters` | ignore/deprecate | Deprecated or unknown alias. Do not repair. |
| `historical_player_metrics` | ignore/deprecate | Deprecated alias for old source path. Replace with advanced marts. |

## Weekly In-Season Refresh Flow

Requirements: bounded, cheap, idempotent, rerunnable by season/week, and isolated from Pigskin/UI raw table access.

1. Determine target season and impacted week set from schedule/PBP availability and operator override. Do not infer from memory.
2. Run dry-run plan for `season`, `week_start`, `week_end`, and source families.
3. Refresh raw nflverse source families for impacted weeks or season slice:
   - PBP;
   - weekly player stats;
   - schedules;
   - weekly rosters;
   - injuries;
   - snap counts;
   - participation if wired;
   - NGS/FTN where available.
4. Merge impacted raw partitions by natural key and `row_hash`. Do not blindly append duplicate weeks.
5. Rebuild staging rows for impacted weeks.
6. Rebuild feature mart rows for impacted weeks.
7. Rebuild rolling 3/5/8 windows for affected players and teams. A corrected Week 7 can affect current rolling windows, so recompute from the earliest impacted week through the current week.
8. Rebuild current context packets and current compatibility backing tables.
9. Run validation patterns for raw coverage, staging grain, metric ranges, source freshness, packet availability, and no raw-source dependencies in compatibility views.
10. Publish only compact current marts and compatibility views to Pigskin/UI.

Rerun behavior for corrected weeks:

- accept an explicit impacted week window;
- mark a new `source_refresh_id`;
- merge raw rows by natural key plus source hash;
- recompute staging/features from `min_impacted_week` through current week for rolling metrics;
- preserve previous `feature_run_id` lineage where useful, but expose only latest current outputs.

## Historical Backfill Execution Plan

No historical backfill was run in this phase. Future execution should use this design:

1. Backfill in season batches, for example 2014-2016, 2017-2019, 2020-2022, then 2023-current.
2. Backfill source-family batches in this order:
   - schedules, teams, players, fantasy IDs;
   - rosters and weekly rosters;
   - weekly player stats;
   - PBP;
   - snap counts and participation;
   - injuries and depth charts;
   - NGS and FTN enrichments.
3. For each batch, generate a dry-run plan with expected tables, season list, write disposition, partitions, and estimated query costs for downstream transforms.
4. Load raw data through BigQuery load jobs into raw tables, not legacy source tables.
5. Use idempotent merge into raw/staging/feature tables. The merge key must be table-specific and null-safe where applicable.
6. Avoid repeated full PBP scans by building `stg_play_player_events`, `stg_team_week_stats`, and `player_week_advanced_metrics` incrementally by season/week.
7. Record `source_refresh_id` for raw loads and `feature_run_id` for staging/feature outputs.
8. Pause/resume by batch ledger:
   - source family;
   - season;
   - status;
   - row count;
   - validation result;
   - error message.
9. Recover failed seasons by rerunning only the failed source family and season window.
10. Validate each season before moving to the next batch.
11. Keep production and staging UI isolated during backfill by leaving Pigskin/UI on existing current compatibility views until new current views pass staging QA.

## First Metrics to Build After Backfill

Tier 1 metrics should come first because they are high-value for Pigskin and supported by nflverse-backed sources.

| Metric | Source raw/staging tables |
| --- | --- |
| target share | `stg_play_player_events`, `stg_team_week_stats`, `stg_player_week_stats` |
| air-yards share | `stg_play_player_events`, `stg_team_week_stats` |
| WOPR | target share and air-yards share fields |
| aDOT | `stg_play_player_events`, `stg_player_week_stats` |
| RACR | `stg_player_week_stats`, `stg_play_player_events` |
| weighted opportunity | `stg_player_week_stats`, `stg_play_player_events` |
| carry share | `stg_player_week_stats`, `stg_team_week_stats` |
| opportunity share | `stg_player_week_stats`, `stg_team_week_stats` |
| red-zone targets | `stg_play_player_events` |
| red-zone carries | `stg_play_player_events` |
| high-value touches | `stg_play_player_events`, red-zone and inside-10/inside-5 event fields |
| EPA per player opportunity | `stg_play_player_events` |
| success rate | `stg_play_player_events`, `stg_team_week_stats` |
| CPOE | `raw_nflverse_pbp`, `raw_nflverse_ngs_passing`, `stg_player_week_stats` |
| explosive rush/reception rate | `stg_play_player_events` |
| rolling 3/5/8 usage | `player_week_advanced_metrics` |
| rolling 3/5/8 efficiency | `player_week_advanced_metrics` |
| team EPA | `stg_team_week_stats`, `stg_play_player_events` |
| team success rate | `stg_team_week_stats` |
| team pace | `stg_game_context`, `stg_team_week_stats`, PBP clock fields |
| neutral-script pass rate | `stg_play_player_events`, `stg_team_week_stats` |
| pass rate over expected | `raw_nflverse_pbp`, `stg_team_week_stats` |
| opponent defensive EPA allowed | `stg_team_week_stats`, `stg_play_player_events` |
| snap share | `stg_participation_context` |
| injury/depth context | `raw_nflverse_injuries`, `raw_nflverse_depth_charts`, `stg_player_identity` |

Tier 2 metrics can follow:

- NGS separation;
- NGS expected YAC;
- RYOE;
- stacked-box rate;
- FTN screen-pass context;
- QB-fault sack proxy;
- weather/stadium scoring environment.

Blocked or deferred:

- route participation;
- yards per route run;
- targets per route run;
- first-read share;
- true pressure-to-sack;
- yards before contact;
- yards after contact;
- slot/wide/inline alignment.

## Partitioning and Clustering Plan

| Table class | Partition | Cluster | Expected query pattern | Current materialization |
| --- | --- | --- | --- | --- |
| raw PBP | `season` or `game_date` | `season`, `week`, `game_id`, `posteam`, `defteam` | season/week backfill, play-event staging | no current view |
| raw weekly stats | `season` | `week`, `player_id`, `team`, `position` | player/week metric staging | no current view |
| raw rosters and weekly rosters | `season` | `week`, player IDs, team, position | identity and team history | current identity view separate |
| raw schedules | `season` or `game_date` | `week`, `game_id`, teams | game context and weekly refresh bounds | current game context separate |
| raw injuries/snap/participation | `season` | `week`, player/team/position | role and availability context | current role mart separate |
| raw NGS/FTN | `season` | `week`, player/game IDs | enrichment metrics | current metric fields separate |
| staging player identity | no partition or `season` for history | player IDs, normalized name, team | point lookup and joins | current bridge separate |
| staging game context | `season` or `game_date` | `week`, `game_id`, teams | team/game joins | current game context table |
| staging player-week stats | `season` | `week`, `player_id_internal`, team, position | player metric aggregation | no UI direct |
| staging team-week stats | `season` | `week`, team | team/opponent context | no UI direct |
| staging play-player events | `season` or `game_date` | `week`, `game_id`, `player_id_internal`, event type | feature mart build only | no UI direct |
| feature player-week advanced | `season` | `week`, `player_id_internal`, position, team | backtests and player lookup | current view/table needed |
| feature recent/current metrics | `as_of_season` | `as_of_week`, player, position, team | Pigskin/UI current context | materialize current table |
| context packet current | `as_of_season` or `created_at` | player, scoring profile, team, position | Pigskin tool lookup | materialize current table and compatibility view |

Compatibility views must not directly read raw PBP or other raw nflverse landing tables.

## Phase 29.3 Validation Suite Proposal

Suggested validation files:

| File pattern | Purpose |
| --- | --- |
| `180_raw_nflverse_pbp_exists.sql` | raw PBP object exists |
| `181_raw_nflverse_weekly_exists.sql` | raw weekly object exists |
| `182_raw_nflverse_schedule_roster_identity_exists.sql` | schedules, rosters, players, fantasy IDs exist |
| `183_raw_nflverse_season_week_coverage.sql` | source coverage by season/week |
| `184_raw_nflverse_row_hash_metadata.sql` | `source_refresh_id`, `loaded_at`, `row_hash` present |
| `185_stg_player_identity_grain.sql` | identity grain and active ID uniqueness |
| `186_stg_game_context_grain.sql` | one row per game |
| `187_stg_player_week_stats_grain.sql` | one player/team/week row |
| `188_stg_team_week_stats_grain.sql` | one team/week row |
| `189_stg_play_player_events_grain.sql` | no duplicate player event rows |
| `190_player_identity_coverage.sql` | player-week and PBP players map to identity |
| `191_game_team_coverage.sql` | game/team keys map cleanly |
| `192_advanced_metrics_denominator_nulls.sql` | zero denominators become null plus flags |
| `193_advanced_metrics_range_sanity.sql` | rates and percentiles are in expected range |
| `194_rolling_window_consistency.sql` | rolling windows match available source weeks |
| `195_sample_size_warnings.sql` | sample warnings present where needed |
| `196_source_freshness_present.sql` | freshness JSON present in staging/feature outputs |
| `197_compat_no_raw_dependencies.sql` | compatibility views do not read raw/source tables |
| `198_pigskin_no_request_time_write.sql` | Pigskin helpers remain read-only |
| `199_no_route_metrics_without_source.sql` | route metrics null/flagged until true source exists |
| `200_no_pressure_metrics_without_source.sql` | pressure metrics not mislabeled from proxy fields |

The existing validation runner supports `--dry-run`, `--run`, and `--pattern`, which is sufficient for the Phase 29.3 validation file family.

## Future Authorization Gates

Do not use trade-score or pick-score gates for this lane.

Proposed future gates:

| Gate | Scope |
| --- | --- |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL=true` | historical source acquisition and raw/staging backfill |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH=true` | bounded current-season weekly source refresh |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION=true` | feature mart writes |
| `ALLOW_PIGSKIN_PACKET_REFRESH=true` | context packet writes |

Rules:

- Gates must be same-session only.
- Remove the gate immediately after the authorized command.
- Commands must still require explicit season and week bounds where relevant.
- UI request-time writes are never allowed.
- Dry-run or plan mode must not require the write gate.

## Future Cloud Run Job and Data Ops Design

No Cloud Run Jobs were created or triggered in this phase.

The existing `ingest-nflverse` job is too broad for Phase 29 historical backfill. Future job definitions should be split or extended:

| Job | Inputs | Dry-run behavior | Live bounds | Output report |
| --- | --- | --- | --- | --- |
| `backfill-nflverse-historical` | source families, `season-start`, `season-end`, optional batch size | list source tables, target partitions, estimated downstream query cost | requires `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`, max bounded season range | source row counts, refresh ID, validation status |
| `refresh-nflverse-weekly` | season, `week-start`, `week-end`, source families | plan impacted raw/staging/feature partitions | requires `ALLOW_NFLVERSE_WEEKLY_REFRESH`, explicit weeks | impacted weeks, refresh ID, validations |
| `materialize-advanced-metrics` | season range or season/week, metric families, `feature_run_id` | validate SQL and estimate bytes | requires `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | row counts, bytes processed, metric validations |
| `refresh-pigskin-packets` | season, week, scoring profile, packet version | plan packet count and source dependencies | requires `ALLOW_PIGSKIN_PACKET_REFRESH` | packet counts, missing flags, freshness |

Expected env vars:

- `BQ_PROJECT`
- `BQ_DATASET`
- `NFLVERSE_SOURCE_CACHE_DIR` if local cache is used in a job image
- explicit authorization gate for the job type
- `LOG_LEVEL`

Logging requirements:

- source family;
- season/week window;
- source refresh ID;
- feature run ID;
- row counts by table;
- validation pattern results;
- skipped sources and why;
- error message without secrets.

Scheduler use:

- Scheduler remains disabled by default.
- Manual Cloud Run Job runs must pass first.
- Create Scheduler jobs paused only after a separate authorized rollout.

## Access Track Note

Dashboard access and stable URL/browser flow should remain a separate track.

| Service | URL | Ingress | Note |
| --- | --- | --- | --- |
| Production | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` | `all` | Service describe shows ingress all. IAM or app login can still block browser access. |
| Staging | `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app` | `all` | Service describe shows ingress all. Browser auth should be validated in a separate QA/access phase. |

No Cloud Run auth, ingress, IAM, or URL setting was changed.

## Blockers

No blocker prevents Phase 29.3 contract and migration design.

Write-phase blockers to resolve before any historical backfill:

- add extractor functions for `load_schedules`, `load_rosters`, `load_rosters_weekly`, `load_ff_playerids`, `load_participation`, and `load_team_stats`;
- create raw/staging contracts and migrations first;
- replace broad legacy `ingest-nflverse` behavior with source-family and season/week bounded dry-run planning;
- add idempotent merge strategy and batch ledger;
- add validations before materializing advanced metrics.

## Warnings

- Current warehouse source coverage is mostly 2025 only.
- Current `src.pipeline` rejects week bounds, so it cannot perform cheap current-season weekly refreshes as-is.
- Current pipeline writes to legacy source names, not `raw_nflverse_*` contracts.
- Existing `ingest-nflverse` Cloud Run job design is too coarse and its dry-run response says the old pipeline has no dry-run mode.
- Route metrics, true pressure metrics, first-read share, contact yards, and alignment splits remain blocked until a true source is inspected.
- Sleeper should stay lower priority for this lane.

## Recommended Next Phase

Phase 29.3 should create additive contracts, migrations, views, and validations for the nflverse historical feature warehouse. It should still not ingest data.

Minimum Phase 29.3 deliverables:

- raw `raw_nflverse_*` contracts;
- staging contracts for identity, game context, player-week stats, team-week stats, play-player events, and participation context;
- feature mart contracts for advanced metrics and current Pigskin packets;
- validation SQL patterns 180 through 200 or similar;
- documented dry-run command shapes for future backfill and weekly refresh jobs.

## Final Decision

NFLVERSE HISTORICAL BACKFILL DESIGN READY WITH WARNINGS
