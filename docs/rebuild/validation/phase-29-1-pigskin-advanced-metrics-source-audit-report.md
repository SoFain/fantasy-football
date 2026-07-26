# Phase 29.1 Pigskin Advanced Metrics Source Audit Report

Date: 2026-06-29

Final decision: PIGSKIN ADVANCED METRICS FOUNDATION READY WITH WARNINGS

## Scope

Phase 29.1 was a read-only audit and design pass for a Pigskin Advanced Metrics Foundation. No BigQuery rows were written, no migrations or tables were created, no ingestion or materialization ran, no Cloud Run Jobs were triggered, no Scheduler jobs were created, no deploy occurred, no feature flags were changed, no LLM-backed action or Pigskin prompt was submitted, no scraping or external fetch occurred, and no Firebase artifacts were created.

The goal is to precompute reusable football evidence in BigQuery so Pigskin can answer player questions, compare players, explain rankings, and support show prep from stable marts and compatibility views. Pigskin should not calculate WOPR, EPA, CPOE, opportunity, or rolling metrics at answer time.

Owner addendum applied: the foundation should prioritize a 10-plus-season nflverse historical feature warehouse and cheap weekly refreshes over repairing stale internal slices. Sleeper remains useful later for league-specific current-season context, but nflverse-backed historical player, team, game, play, roster, schedule, and fantasy context is the immediate priority.

## Authorization Gate State

All checked gates were unset in the local command process:

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Git State

Latest commit:

```text
a73656c Document draft pick score release package
```

Recent Phase 28 package commits are present:

```text
a73656c Document draft pick score release package
6e4b565 Draft pick score lane and staging UI
6158549 Document Trade Score v1 Track A closeout
3268a5a Document Trade Score v1 UI polish package
9ec04f3 Polish Trade Score v1 staging UI
aa543d0 Document Phase 26 evidence commit
251fd18 Document Phase 25 production closeout
b3b0ec1 Document Data Ops hardening production rollout
```

No files were staged before this report was created. The worktree contains the expected untracked historical validation backlog from Phase 17 through Phase 28, plus this Phase 29.1 report after creation. No generated output, env file, log, or secret file was staged.

## Deployment State

Read-only Cloud Run describe was run for production and staging.

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

`.\venv\Scripts\python.exe scripts\check_deployment_safety.py` passed:

| Check | Result |
| --- | --- |
| no Firebase artifacts | pass |
| no tracked secret files | pass |
| no secret content | pass |
| required files exist | pass |
| feature flags default off | pass |
| Pigskin has no `execute_bigquery_sql` | pass |
| `app.py` compiles | pass |
| `src` and `scripts` compile | pass |

## Candidate Source Inventory

Dataset: `fantasy-football-498121.fantasy_football_brain`

The metadata search found 77 candidate source, mart, compatibility, and output objects. The most relevant objects for Pigskin advanced metrics are below.

| Object | Type | Rows | Coverage | Relevant fields | Classification and Pigskin safety |
| --- | ---: | ---: | --- | --- | --- |
| `play_by_play` | table | 48,771 | 2025 weeks 1-22 | `game_id`, `season`, `week`, `posteam`, `defteam`, `yardline_100`, `game_seconds_remaining`, `score_differential`, `epa`, `success`, `qb_epa`, `pass_attempt`, `rush_attempt`, `sack`, `qb_scramble`, `cpoe`, `xpass`, `pass_oe`, `air_yards`, `yards_after_catch`, `passer_player_id`, `receiver_player_id`, `rusher_player_id`, `spread_line`, `total_line`, `roof`, `surface`, `temp`, `wind` | raw/source. Not safe for direct Pigskin/UI. Strong base for marts. |
| `weekly_metrics` | table | 19,421 | 2025 weeks 1-22 | `player_id`, `game_id`, `team`, `opponent_team`, passing/rushing/receiving box stats, `passing_epa`, `rushing_epa`, `receiving_epa`, `passing_cpoe`, `target_share`, `air_yards_share`, `wopr` | raw/source. Not safe directly. Good weekly player source. |
| `analytics_player_weekly_truth` | table | 18,539 | 2025 weeks 1-18 | `player_id`, `player_name`, `position`, `team`, `targets`, `receptions`, `carries`, `target_share`, `air_yards_share`, `wopr`, `passing_epa`, `rushing_epa`, `receiving_epa`, `total_epa`, `team_carries`, `team_pass_attempts`, `carry_share`, `red_zone_targets`, `red_zone_carries`, `red_zone_touches`, `offense_snaps`, `offense_pct`, `avg_separation`, rolling 3-week fields, role and fraud flags | derived analytics. Currently in Pigskin allowed schema, but advanced work should prefer packets/compat views. |
| `analytics_player_fantasy_points_by_profile` | table | 55,617 | 2025 weeks 1-18 | scoring-profile fantasy points and component points | output/mart. Safe source for scoring context. |
| `weekly_snap_counts` | table | 26,612 | 2025 weeks 1-22 | `game_id`, `player`, `pfr_player_id`, `position`, `team`, `offense_snaps`, `offense_pct`, `defense_snaps`, `st_snaps` | raw/source. Not safe directly. Useful for snap share. No route data. |
| `ngs_passing` | table | 605 | 2025 weeks 0-23 | `player_gsis_id`, `team_abbr`, `attempts`, `expected_completion_percentage`, air-yards fields | raw/source. Not safe directly. Useful for CPOE-style QB context. |
| `ngs_rushing` | table | 648 | 2025 weeks 0-23 | `player_gsis_id`, `rush_attempts`, `expected_rush_yards`, `rush_yards_over_expected`, `rush_yards_over_expected_per_att`, `rush_pct_over_expected`, stacked-box rate | raw/source. Not safe directly. Useful for RYOE and rushing efficiency. |
| `ngs_receiving` | table | 1,402 | 2025 weeks 0-23 | `player_gsis_id`, `targets`, `avg_separation`, `avg_intended_air_yards`, `percent_share_of_intended_air_yards`, `avg_expected_yac` | raw/source. Not safe directly. Useful for separation and target depth context. |
| `ftn_charting` | table | 47,316 | 2025 weeks 1-22 | `nflverse_game_id`, `season`, `week`, `n_offense_backfield`, `is_screen_pass`, `n_pass_rushers`, `is_qb_fault_sack` | raw/source. Not safe directly. Useful for screen-pass, pass-rusher, and QB-fault sack context. Does not provide broad pressure fields. |
| `analytics_game_environment` | table | 272 | 2025 weeks 1-18 | `game_id`, `stadium`, `roof`, `surface`, `temp_f`, `wind_mph`, `weather_text`, environment flags and buckets | analytics table. Safe after contract review. Useful for weather/stadium context. |
| `injury_reports` | table | 6,068 | 2025 weeks 1-22 | `gsis_id`, `team`, `position`, report and practice injury fields | raw/source. Not safe directly. Use through mart/context packet. |
| `depth_charts` | table | 554,215 | 2025 season | `team`, `player_name`, `gsis_id`, `pos_rank`, `season` | raw/source. Not safe directly. Use through role mart. |
| `player_identity_bridge` | table | 11,212 | current bridge | `player_id_internal`, `gsis_id`, `sleeper_player_id`, `current_team`, freshness and missing flags | feature-like mart. Safe identity foundation. |
| `source_freshness_snapshots` | table | 4 | metadata | freshness lineage | safe metadata. Needed for source freshness in packets. |
| `analytics_player_qb_weekly` | table | 4,529 | 2025 weeks 1-18 | receiver-by-QB weekly targets, air yards, red-zone targets, EPA per target, CPOE | derived analytics. Safe after contract review. |
| `analytics_player_qb_splits` | table | 918 | 2025 season | receiver-by-QB season splits | derived analytics. Safe after contract review. |
| `mart_player_profiles_current` | table | 27,864 | current profiles | last-3 snap share, target share, rush share, air-yards share, red-zone opportunities, high-value touches, yards per carry/target, EPA summary, freshness, missing flags | feature mart. Safe through `compat_player_profiles_current`. |
| `projections_player_weekly` | table | 650 | 2025 weeks 1 and 18 | projection JSON, confidence, risk, role, trend, fraud, breakout, freshness | output. Safe after bounded materialization checks. |
| `projection_rankings_current` | table | 650 | 2025 weeks 1 and 18 | rank, projected points/value, confidence, risk | output. Safe after context review. |
| `analytics_pigskin_rankings` | table | 285 | 2026 active rankings | active Pigskin ranks, rank rationale, risk flags, EPA and WOPR summaries | output. Safe. Warning: active rows are 2026, not 2025 current-week evidence. |
| `trade_player_scores_current` | view | 77 current rows | 2025 week 18 | player trade scores | output view. Safe through compatibility view. |
| `compat_trade_player_scores_current` | view | 33 fields | 2025 week 18 | player score, components, confidence, freshness, missing flags | safe compatibility view. |
| `trade_pick_scores_current` | view | 64 current rows | pick score v0 | draft-pick scores | output view. Safe through compatibility view. |
| `compat_trade_pick_scores_current` | view | 29 fields | pick score v0 | pick score, components, confidence, freshness, missing flags | safe compatibility view. |
| `llm_player_context_packet` | view | packet view | current packet | packet JSON/text, source freshness, missing flags | safe Pigskin context contract. |
| `mart_llm_player_context_packet` | table | 9,340 | materialized packet table | same packet fields | safe packet backing table. |

Important source-freshness finding: raw/source tables do not carry `source_freshness_json` or `missing_data_flags` columns. The identity bridge, promoted compatibility views, profile mart, trade scores, pick scores, and context packets do. Future advanced metric marts must add freshness and missing flags instead of passing raw table uncertainty to Pigskin.

## Owner Addendum Priority Model

Phase 29 should use this source priority order:

1. nflverse historical data for long-term player, team, play, game, roster, schedule, and fantasy metrics.
2. Existing BigQuery curated tables only when they are clean, complete, current, and cheap to use.
3. Sleeper for league-specific current-season rosters, ownership, matchups, and app integration later.
4. Manual or derived tables only when nflverse does not provide the needed data.

This changes the practical route. Missing or stale current warehouse coverage is not automatically a blocker if nflverse can provide the source. The default should be replacement or refresh from nflverse, not a long repair project on questionable internal tables.

## Replacement-Over-Repair Classification

| Table or object | Classification | Reason | Phase 29 action |
| --- | --- | --- | --- |
| `play_by_play` | keep but refresh from nflverse | Current rows cover only 2025 in this warehouse, while Pigskin needs 10-plus seasons. | Create `raw_nflverse_pbp`, backfill historical seasons, keep existing table as reference until migrated. |
| `weekly_metrics` | keep but refresh from nflverse | Current rows cover 2025 only. Source maps to `nflreadpy.load_player_stats`. | Create `raw_nflverse_weekly`, backfill historical weekly player stats, then stage into canonical player-week stats. |
| `player_rosters` | replace with nflverse source | Existing `player_rosters` naming is current-table-specific and direct UI debt exists. | Use `nflreadpy.load_rosters`, `load_rosters_weekly`, `load_players`, and `load_ff_playerids` into raw/staging identity tables. |
| `team_descriptions` | keep but refresh from nflverse | Useful team metadata, low complexity. | Rebuild from `nflreadpy.load_teams`; feed canonical team dimension. |
| `draft_picks` | keep and use | nflverse-backed and useful for rookie/draft context. | Keep as draft/rookie source, but expose only through feature marts and pick-score lane. |
| `college_player_stats` | keep but isolate | Unique college context, not core nflverse weekly football evidence. | Keep for rookie context. Do not let it block the nflverse advanced metric warehouse. |
| `ngs_passing` | keep but refresh from nflverse | Useful source available through `load_nextgen_stats`. | Backfill supported seasons, stage into QB/team/player advanced metrics. |
| `ngs_rushing` | keep but refresh from nflverse | Useful RYOE context, nflverse source available. | Backfill supported seasons and include in rushing feature marts. |
| `ngs_receiving` | keep but refresh from nflverse | Useful separation and intended air yards context. | Backfill supported seasons and include in receiver feature marts. |
| `ftn_charting` | keep but refresh from nflverse | Useful charting fields, limited historical range. | Backfill supported seasons, flag missing seasons rather than repairing old gaps. |
| `weekly_snap_counts` | keep but refresh from nflverse | Snap counts source exists and supports role metrics. | Backfill supported seasons through `load_snap_counts`. |
| `injury_reports` | keep but refresh from nflverse | Injury loader exists. | Backfill available seasons and expose through context marts only. |
| `depth_charts` | keep but refresh from nflverse | Depth chart loader exists with long range. | Backfill available seasons and expose through role context. |
| `analytics_player_weekly_truth` | keep as derived output, do not repair as source | Useful current mart but should not be the source of historical truth. | Rebuild from raw/staging nflverse sources after backfill. |
| `analytics_player_qb_weekly` | keep as derived output | Useful derived split, but should be rebuilt from PBP source. | Rebuild after raw historical PBP exists. |
| `analytics_game_environment` | keep as derived output | Useful curated game context, but should be rebuilt from schedules/PBP environment fields. | Add schedule source and rebuild canonical `stg_game_context`. |
| `mart_player_profiles_current` | keep as current consumer mart | Useful UI/output mart, not a historical source. | Rebuild from advanced feature marts and identity. |
| `llm_player_context_packet` and `mart_llm_player_context_packet` | keep as packet contract | Correct consumption pattern for Pigskin. | Rebuild packet contents after advanced metrics exist. |
| Sleeper league and roster snapshots | keep for later | Lower priority for the historical evidence warehouse. | Defer to league-specific current-season integration phases. |
| `active_league_rosters` and `historical_player_metrics` aliases | ignore/deprecate | Inventory already classifies these as unsafe or deprecated/unknown. | Do not repair. Replace with curated marts and compatibility views. |
| `market_values` | keep only as controlled source | Not nflverse and not core advanced football evidence. | Use only through trade assets and market contexts, not as Pigskin metric foundation. |

## Historical nflverse Backfill Requirement

The foundation should support at least 10-plus seasons of analysis. The installed `nflreadpy` package exposes these relevant loaders locally:

| Need | Preferred nflreadpy source | Existing repo status | Notes |
| --- | --- | --- | --- |
| play-by-play | `load_pbp` | wired in `src.extract.get_pbp_data` and `src.pipeline` | Primary historical source for EPA, success, CPOE, WOPR components, team tendencies, and game context. |
| weekly player stats | `load_player_stats`, `load_stats` | `load_player_stats` wired as `weekly_metrics` | Primary weekly player stat and fantasy scoring input. |
| rosters and player IDs | `load_rosters`, `load_rosters_weekly`, `load_players`, `load_ff_playerids` | `load_players` wired, weekly rosters and fantasy IDs not yet wired | Add raw/staging identity sources early. |
| schedules | `load_schedules` | not wired in current extractor/pipeline | Add this before building game-context and backtesting features. |
| injuries | `load_injuries` | wired | Backfill supported seasons and expose via context marts. |
| depth charts | `load_depth_charts` | wired | Backfill supported seasons and stage role context. |
| snap counts | `load_snap_counts` | wired | Supports snap share and role stability. |
| participation | `load_participation` | not wired | Add if it includes route or participation context. Validate before naming fields route share. |
| team context | `load_teams`, `load_team_stats`, schedule/PBP aggregations | `load_teams` wired, `load_team_stats` not wired | Add team stats if it reduces PBP scan cost. |
| NGS | `load_nextgen_stats` | wired for passing, rushing, receiving | Supports expected completion, RYOE, separation, expected YAC. |
| FTN charting | `load_ftn_charting` | wired | Supports screen/pass-rusher/QB-fault sack context, not true pressure share. |
| draft and rookie context | `load_draft_picks`, college stat table | draft wired, college table exists | Useful but not the first historical weekly metric dependency. |

What can be calculated immediately from nflverse-backed data:

- WOPR, target share, air-yards share, aDOT, RACR, weighted opportunity, red-zone role, rolling 3/5/8 usage, EPA, success rate, CPOE, QB form, team EPA, team success rate, pace, pass rate over expected, opponent defensive EPA allowed, snap share, NGS separation/RYOE context, and schedule/weather/stadium context once schedules are wired.

What should not be represented as ready until source is validated:

- true route participation, yards per route run, targets per route run, first-read share, true pressure-to-sack rate, yards before contact, yards after contact, inline/blocking penalty, and alignment splits.

## BigQuery Layering Recommendation

Use a simple layered structure. Keep raw historical facts separate from canonical staging and feature marts.

### Raw/Landing

| Proposed table | Source | Partitioning and clustering |
| --- | --- | --- |
| `raw_nflverse_pbp` | `nflreadpy.load_pbp` | Partition by `season` or `game_date`; cluster by `season`, `week`, `game_id`, `posteam`, `defteam`. |
| `raw_nflverse_weekly` | `load_player_stats` or `load_stats` | Partition by `season`; cluster by `season`, `week`, `player_id`, `team`, `position`. |
| `raw_nflverse_rosters` | `load_rosters`, `load_rosters_weekly` | Partition by `season`; cluster by `season`, `week`, `player_id`, `team`, `position`. |
| `raw_nflverse_schedules` | `load_schedules` | Partition by `season` or `game_date`; cluster by `season`, `week`, `game_id`, `home_team`, `away_team`. |
| `raw_nflverse_players` | `load_players`, `load_ff_playerids` | Cluster by player IDs, name, team, position. |
| `raw_nflverse_injuries` | `load_injuries` | Partition by `season`; cluster by `season`, `week`, `gsis_id`, `team`. |
| `raw_nflverse_snap_counts` | `load_snap_counts` | Partition by `season`; cluster by `season`, `week`, `player`, `team`, `position`. |
| `raw_nflverse_participation` | `load_participation` | Partition by `season`; cluster by `season`, `week`, `game_id`, `player_id` when available. |
| `raw_nflverse_depth_charts` | `load_depth_charts` | Partition by `season`; cluster by `team`, `gsis_id`, `pos_rank`. |
| `raw_nflverse_ngs_passing`, `raw_nflverse_ngs_rushing`, `raw_nflverse_ngs_receiving` | `load_nextgen_stats` | Partition by `season`; cluster by `season`, `week`, `player_gsis_id`, `team_abbr`. |
| `raw_nflverse_ftn_charting` | `load_ftn_charting` | Partition by `season`; cluster by `season`, `week`, `nflverse_game_id`. |

### Staging/Canonical

| Proposed table | Purpose |
| --- | --- |
| `stg_player_week_stats` | Canonical player-week stat row with consistent IDs, team, position, scoring inputs, and source flags. |
| `stg_team_week_stats` | Team weekly offensive and defensive context from PBP/team stats. |
| `stg_game_context` | One row per game with schedule, stadium, roof, weather, betting-line metadata where available, teams, and game IDs. |
| `stg_player_identity` | Canonical ID bridge across nflverse, Sleeper, fantasy IDs, internal IDs, and name normalization. |
| `stg_play_player_events` | Play-level player event grain for targets, carries, pass attempts, red-zone touches, EPA attribution, and team context. |

### Feature Marts

| Proposed table | Purpose |
| --- | --- |
| `player_week_advanced_metrics` | Historical player-week advanced metrics. |
| `player_recent_advanced_metrics_current` | Current rolling 3/5/8, season-to-date, sample flags, and current role form. |
| `team_week_context_metrics` | Team pace, pass rate, EPA, success, scoring environment, and opponent context. |
| `player_role_usage_metrics_current` | Stable role context for Pigskin and UI. |
| `pigskin_player_context_packet_current` | Compact current Pigskin evidence packet. |
| `compat_pigskin_player_context_current` | UI and Pigskin safe compatibility view. |

Current views should stay separate from historical fact tables. Pigskin and Streamlit should read only current/compatibility views or parameterized helpers. No UI should query raw PBP.

## Weekly Update Design

During the NFL season, the refresh flow should be incremental:

1. Refresh nflverse current-season source data for PBP, weekly player stats, rosters, schedules, team stats, injuries, snap counts, participation if wired, depth charts, NGS, and FTN.
2. Recompute only impacted weeks and any dependent current-season rows.
3. Recompute rolling 3/5/8 week features for affected players and teams.
4. Recompute `player_recent_advanced_metrics_current`, `player_role_usage_metrics_current`, and current Pigskin context packets.
5. Run validation patterns for source coverage, grain uniqueness, metric ranges, identity coverage, freshness, and compatibility-view raw-source dependency checks.
6. Update current compatibility views or their backing marts.
7. Leave Pigskin reading compact context packets and metric leader helpers, not raw tables.

Operational rules:

- Keep `feature_run_id` or `source_refresh_id` on every raw load, staging transform, and feature mart.
- Prefer append plus idempotent merge over truncation.
- Keep historical backfill jobs separate from weekly refresh jobs.
- Use season/week bounds for reruns.
- Avoid spending time repairing stale internal tables when fresh nflverse reload is cheaper and cleaner.

## Backtesting Design

The feature warehouse should let BigQuery answer these questions without asking GenAI to calculate metrics live:

- What metrics predicted breakout wide receivers over the last 10 years?
- How often does rising WOPR predict fantasy spike weeks?
- Which running back opportunity metrics best predict next-week points?
- Which team environment metrics matter most for quarterbacks?
- How do rookie usage signals translate to future fantasy value?
- Which metrics identify fraud players who are scoring without stable usage?

Backtesting design requirements:

- Store one historical player-week row per metric version and scoring profile where relevant.
- Store forward-looking labels separately, for example next-week points, next-3-week points, rest-of-season points, injury inactive flags, and role-change flags.
- Store raw metric values and percentiles, not just ranks.
- Preserve source refresh IDs so backtests can be reproduced.
- Do not create hard-coded Pigskin rankings in this phase. Rankings can consume this evidence later.

## Metric Readiness Matrix

### Passing and QB Metrics

| Metric | Readiness | Evidence | Notes |
| --- | --- | --- | --- |
| EPA per dropback | ready now | `play_by_play.epa`, `pass_attempt`, `sack`, `qb_scramble`, `passer_player_id` | Build from play-level rows, grouped by QB/season/week. Dropback denominator should include pass attempts, sacks, and scrambles where QB attribution is reliable. |
| passing EPA | ready now | `play_by_play.epa`, `weekly_metrics.passing_epa`, `analytics_player_weekly_truth.passing_epa` | Prefer play-level for canonical mart, use weekly/truth as validation. |
| success rate | ready now | `play_by_play.success`, `epa` | Use `success` when present, else `epa > 0` fallback in builder. |
| CPOE | ready now | `play_by_play.cpoe`, `weekly_metrics.passing_cpoe`, `ngs_passing.expected_completion_percentage` | Use nflverse CPOE for weekly player metric. NGS expected completion can enrich QB context. |
| completion percentage over expected | ready now | `play_by_play.cpoe`, `weekly_metrics.passing_cpoe` | Same as CPOE in existing source naming. |
| air yards per attempt | ready now | `play_by_play.air_yards`, `pass_attempt`, `weekly_metrics.passing_air_yards`, `attempts` | Null when attempts are zero. |
| average depth of target | ready now | `air_yards`, targets or pass attempts depending entity | QB aDOT uses pass attempts with air yards. Receiver aDOT uses targets. |
| sack rate | ready now | `play_by_play.sack`, dropback fields, `weekly_metrics.sacks_suffered` | Prefer play-level denominator. |
| pressure-to-sack rate | needs source contract | `ftn_charting.n_pass_rushers`, `is_qb_fault_sack` exist, but no true pressure column was found | Do not label this as pressure-to-sack until pressure/hurry source exists. |
| scramble rate | ready now | `play_by_play.qb_scramble` | Denominator should be dropbacks. |
| designed rush share | likely ready but needs validation | `play_by_play.rush_attempt`, `qb_scramble`, rusher fields | Designed QB rush can be inferred as QB rush attempt where `qb_scramble` is false, but this needs validation. |
| red-zone pass rate | ready now | `play_by_play.yardline_100`, `pass_attempt`, `posteam` | Use plays with `yardline_100 <= 20`. |
| deep attempt rate | ready now | `play_by_play.air_yards`, `pass_attempt` | Use attempts with `air_yards >= 20`. |
| turnover-worthy proxy | likely ready but needs validation | interceptions and fumbles exist; no true TWP source found | Name it turnover-event proxy, not turnover-worthy play. |
| rolling 3/5/8 week QB form | ready now | weekly QB rows from `weekly_metrics` or play-level aggregations | Requires a mart window function and sample-size flags. |

### Receiving WR/TE Metrics

| Metric | Readiness | Evidence | Notes |
| --- | --- | --- | --- |
| target share | ready now | `weekly_metrics.target_share`, `analytics_player_weekly_truth.target_share`, play-level receiver targets | Prefer play-level or truth denominator. |
| air yards share | ready now | `weekly_metrics.air_yards_share`, `analytics_player_weekly_truth.air_yards_share` | Validate team denominator from play-level team air yards. |
| WOPR | ready now | `weekly_metrics.wopr`, `analytics_player_weekly_truth.wopr` | Recompute in canonical mart for formula control. |
| aDOT | ready now | `analytics_player_qb_weekly.adot`, play-level air yards/targets | Use target denominator. |
| yards per route run | blocked by missing data | no true routes or routes-run column found | `compat_trade_player_history.routes_proxy` is a proxy, not source data. |
| targets per route run | blocked by missing data | no true route denominator found | Requires route participation source. |
| yards per target | ready now | `weekly_metrics.receiving_yards`, `targets`; `analytics_player_qb_weekly.yards_per_target` | Null when targets are zero. |
| RACR | ready now | receiving yards and air yards exist | Guard zero or negative air yards. |
| end-zone target share | likely ready but needs validation | `play_by_play.yardline_100`, receiver target fields | End-zone target definition should be documented before use. |
| red-zone target share | ready now | `analytics_player_weekly_truth.red_zone_targets`, `analytics_player_qb_weekly.red_zone_targets`, play-level yardline | Use team red-zone pass targets as denominator. |
| first-read target share | blocked by missing data | no first-read column found | Requires charting source. |
| explosive reception rate | ready now | `play_by_play.receiving_yards`, `complete_pass`, receiver id | Define explosive as 20-plus receiving yards unless changed. |
| weighted opportunity | ready now | targets, carries, red-zone fields | Store formula version. |
| rolling 3/5/8 receiving usage | ready now | weekly truth and play-level targets/carries | Existing truth has rolling 3 fields. Add 5 and 8. |

### Rushing and RB Metrics

| Metric | Readiness | Evidence | Notes |
| --- | --- | --- | --- |
| carry share | ready now | `analytics_player_weekly_truth.carry_share`, team carries | Recompute and validate. |
| rush attempt share | ready now | same as carry share | Use consistent naming. |
| opportunity share | ready now | targets, carries, team pass attempts, team carries | Define denominator per position. |
| weighted opportunity | ready now | carries and targets | Use v0 formula below. |
| high-value touches | ready now | red-zone targets, red-zone carries, inside-10/inside-5 derivable from `yardline_100` | Avoid double counting or store components separately. |
| targets and target share | ready now | weekly/truth/play-level | Safe after mart. |
| route participation | blocked by missing data | no routes-run source found | Do not infer from snaps as real route participation. |
| red-zone touches | ready now | `analytics_player_weekly_truth.red_zone_touches` and play-level yardline | Validate with play-level. |
| inside-10 carries | ready now | `analytics_player_qb_weekly.inside_10_targets`; play-level `yardline_100` and rusher fields for carries | Build from play-level. |
| inside-5 carries | ready now | play-level `yardline_100` and rusher fields | Build from play-level. |
| rushing EPA | ready now | `play_by_play.epa`, `weekly_metrics.rushing_epa`, truth rushing EPA | Prefer play-level. |
| rushing success rate | ready now | `play_by_play.success`, `rush_attempt` | Group by rusher. |
| yards before contact | blocked by missing data | no yards-before-contact column found | Requires source. |
| yards after contact | blocked by missing data | no yards-after-contact column found | NGS RYOE can supplement, not replace contact yards. |
| explosive rush rate | ready now | play-level `rushing_yards`, `rush_attempt` | Define explosive as 10-plus or 15-plus yards and store formula version. |
| rolling 3/5/8 week usage | ready now | weekly truth and play-level | Existing rolling 3, add 5 and 8. |

### TE-Specific Metrics

| Metric | Readiness | Evidence | Notes |
| --- | --- | --- | --- |
| route participation | blocked by missing data | no true routes source | Needs route-source contract. |
| target share | ready now | weekly/truth | Same as WR. |
| air yards share | ready now | weekly/truth | Same as WR. |
| WOPR | ready now | weekly/truth | Same as WR. |
| red-zone target share | ready now | truth/QB weekly/play-level | Same as WR. |
| inline/blocking penalty | blocked by missing data | no inline/blocking alignment found | Requires charting or alignment source. |
| slot/wide alignment | blocked by missing data | no slot/wide alignment columns found | Requires charting or alignment source. |

### Team and Game Environment Metrics

| Metric | Readiness | Evidence | Notes |
| --- | --- | --- | --- |
| plays per game | ready now | `play_by_play` team offensive plays | Exclude penalties/no-plays as defined by nflverse flags. |
| seconds per play or pace | ready now | `game_seconds_remaining`, team plays | Needs garbage-time and drive-state policy. |
| neutral-script pass rate | ready now | `score_differential`, `pass_attempt`, `rush_attempt`, `game_seconds_remaining` | Define neutral as absolute score differential <= 7 and first three quarters unless changed. |
| pass rate over expected | ready now | `play_by_play.xpass`, `pass_oe` | Source exists. Store xpass and pass_oe aggregates. |
| team EPA per play | ready now | `play_by_play.epa`, `posteam` | Straight team/week aggregation. |
| team success rate | ready now | `play_by_play.success` | Same team/week aggregation. |
| offensive touchdown rate | ready now | touchdown fields and plays | Store pass/rush components. |
| red-zone pass/rush rates | ready now | `yardline_100`, play type flags | Team and opponent versions. |
| scoring environment | ready now | scores, `total_line`, `spread_line`, weather/stadium fields | Betting lines exist in `play_by_play`; treat odds lineage as nflverse game metadata, not current sportsbook data. |
| opponent defensive EPA allowed | ready now | `play_by_play.defteam`, `epa` | Split pass/rush. |
| opponent pass/rush funnel indicators | ready now | opponent EPA allowed, pass rate allowed, rush success allowed | Needs stable formula and percentiles. |
| implied total | likely ready but needs validation | `play_by_play.total_line`, `spread_line` | Validate line semantics before using as betting-derived implied total. No live odds source. |
| weather/stadium context | ready now | `analytics_game_environment` and play-level weather fields | Use analytics game environment in packets. |

### Player Context and Reliability

| Metric | Readiness | Evidence | Notes |
| --- | --- | --- | --- |
| games played | ready now | weekly truth, player profiles | Existing profile mart has current-season games. |
| snap share | ready now | `weekly_snap_counts`, truth `offense_pct`, profile mart `snap_share_last_3` | Use truth/profile outputs. |
| route share | blocked by missing data | no true routes source | Do not use snap share as route share. |
| injury status | ready now | `injury_reports`, `sleeper_players_current`, truth injury fields | Must be funneled through mart. |
| depth chart role | ready now | `depth_charts`, profile mart depth summary | Needs identity bridge. |
| team changes | ready now | player identity/profile fields | Truth already has `team_changed_since_stats`. |
| rookie/draft context | ready now | `draft_picks`, `college_player_stats`, pick score lane | Use through separate rookie/draft context mart, not raw tables. |
| source freshness | ready now | `source_freshness_snapshots`, compatibility outputs | Add required freshness JSON to new marts. |
| missing data flags | ready now | existing compatibility pattern | Add required missing flags to new marts. |
| identity confidence | likely ready but needs validation | `player_identity_bridge`, overrides | Add explicit confidence or match-status fields if not already present. |

## Formula Definitions

All formulas should store raw numerator, denominator, metric value, percentile, sample size, `feature_run_id`, `metric_version`, `source_freshness_json`, and `missing_data_flags` where practical.

### WOPR

```text
target_share = player_targets / team_targets
air_yards_share = player_air_yards / team_air_yards
wopr = 1.5 * target_share + 0.7 * air_yards_share
```

Preferred denominator:

- Receiver and TE: team targets from pass attempts with receiver attribution.
- If team target denominator is unavailable, use team pass attempts and flag `target_denominator_pass_attempts`.
- If team air yards is null or zero, set `air_yards_share` null and add `missing_team_air_yards`.

### RACR

```text
racr = receiving_yards / receiving_air_yards
```

If receiving air yards is null, zero, or negative, set `racr` null and add `invalid_air_yards_denominator`. Negative-air-yard targets should still be kept in raw fields.

### aDOT

```text
adot = receiving_air_yards / targets
```

If targets are zero, set null and add `zero_targets`.

### Target Share

```text
target_share = player_targets / team_targets
```

Use team targets as the default denominator. Store `target_share_denominator_type = team_targets`.

### Air Yards Share

```text
air_yards_share = player_air_yards / team_air_yards
```

If team air yards is zero or unavailable, set null and flag it. Do not force zero.

### Weighted Opportunity

Position-aware v0:

```text
weighted_opportunity = rush_attempts + 2.5 * targets
```

For QBs, keep separate QB rushing opportunity fields instead of blending dropbacks into this skill-player formula.

### High-Value Touches

Recommended component storage:

```text
high_value_touch_components = {
  "targets": targets,
  "red_zone_touches": red_zone_targets + red_zone_carries,
  "inside_10_carries": inside_10_carries,
  "inside_5_carries": inside_5_carries
}
```

Recommended rollup:

```text
high_value_touches = targets + red_zone_touches + inside_10_carries + inside_5_carries
```

This intentionally rewards stacked leverage. If the owner wants non-overlap later, add `unique_high_value_touch_count` separately.

### EPA

QB:

```text
epa_per_dropback = SUM(epa where dropback) / COUNT(dropbacks)
passing_epa = SUM(epa where passer_player_id = player and dropback)
```

Receiver:

```text
receiving_epa = SUM(epa where receiver_player_id = player and pass attempt with target)
epa_per_target = receiving_epa / targets
```

Rusher:

```text
rushing_epa = SUM(epa where rusher_player_id = player and rush_attempt = 1)
epa_per_rush = rushing_epa / rush_attempts
```

Team:

```text
team_epa_per_play = SUM(epa where posteam = team) / offensive_play_count
```

### Success Rate

Default:

```text
success_rate = COUNTIF(success = 1) / COUNT(eligible_plays)
```

Fallback if `success` is missing:

```text
success_rate = COUNTIF(epa > 0) / COUNT(eligible_plays)
```

Store `success_definition = nflverse_success` or `success_definition = epa_gt_zero`.

### Rolling Metrics

For each player/team metric, calculate:

- season to date through the target week;
- last 3 games;
- last 5 games;
- last 8 games;
- optional exponentially weighted trailing form after v0.

Add sample-size flags:

- `sample_lt_3_games`
- `sample_lt_5_games`
- `sample_lt_8_games`
- `missing_recent_weeks`

### Percentiles

Calculate percentiles by:

- position;
- season;
- week;
- scoring profile where fantasy scoring affects the metric;
- minimum sample bucket where needed.

Store percentile columns separately from raw metrics. Do not overwrite raw metric values.

## Pigskin Retrieval Audit

Current model-visible Pigskin tools in `src/pigskin_context_tools.py`:

| Tool | Current backing path | Notes |
| --- | --- | --- |
| `get_player_context_packet` | `src.llm_context_packets.get_player_context_packet` over `llm_player_context_packet` | Lookup by player name or `player_id_internal`, scoped by scoring, league, roster format, optional model run. |
| `search_players` | context packet search | Resolves player names and IDs through packet rows. |
| `get_rankings_slice` | `analytics_pigskin_rankings` | Returns active Pigskin ranks and rationale. |
| `get_fraud_watch_candidates` | `analytics_fraud_watch` | Curated Fraud Watch candidates. |
| `get_trade_player_history` | `compat_trade_player_history` through `src.trade_history` | Capped history, default limit 24. |
| `compare_players` | repeated player context packet lookups | Up to 6 players. |
| `get_context_event_leads` | `analytics_context_events` and stored external lead table | Does not scrape. Stored leads are marked as leads. |

Pigskin Studio status:

- `execute_bigquery_sql` is absent from the model-visible tool declarations.
- `src.pigskin_chat_schema.PIGSKIN_CHAT_BLOCKED_TABLES` blocks raw/source objects including `weekly_metrics`, `play_by_play`, `ngs_*`, `ftn_charting`, `weekly_snap_counts`, `injury_reports`, and Sleeper raw tables.
- The Context Tool Protocol in `app.py` tells Pigskin not to write or execute SQL, not to request table access, and to stop if a curated context tool fails.
- The query helpers use `maximum_bytes_billed` and parameterized queries.

Remaining retrieval debt:

- The allowed schema still names selected analytics tables, including `analytics_player_weekly_truth`. That is safer than raw/source exposure, but the better future contract is `pigskin_player_context_packet_current` plus `compat_pigskin_player_context_current`.
- Some non-Pigskin UI code still has raw/source legacy reads or fallback paths. The notable example is the Trade Lab AI outlook block containing a `weekly_metrics` fallback, but that action is hidden unless local admin subprocess controls are explicitly enabled. It should be replaced with compatibility reads before any broader exposure.
- Existing context packets have sections for `usage_summary`, `efficiency_summary`, `game_environment`, `qb_and_team_context`, `fraud_watch_context`, `trade_context`, `external_context`, `source_metadata`, and warnings. Advanced metrics should populate those sections rather than making Pigskin compute them live.

## Proposed Advanced Metric Marts

### A. `player_week_advanced_metrics`

Purpose: one row per player, season, week, scoring profile where relevant, with raw and advanced player metrics.

Grain:

```text
metric_version, season, week, player_id_internal, scoring_profile_id, league_type_id, roster_format_id
```

Source dependencies:

- `play_by_play`
- `weekly_metrics`
- `analytics_player_weekly_truth`
- `weekly_snap_counts`
- NGS tables
- FTN charting where validated
- `player_identity_bridge`
- `source_freshness_snapshots`

Required fields:

- identity: `player_id_internal`, `source_player_key`, `gsis_id`, `sleeper_player_id`, `player_name`, `position`, `team`, `current_team`;
- usage: targets, carries, pass attempts, routes if future source exists, snaps, snap share, target share, carry share, opportunity share;
- efficiency: EPA, EPA per opportunity, success rate, CPOE, aDOT, RACR, yards per target, yards per carry, RYOE fields;
- leverage: red-zone targets, red-zone carries, inside-10 carries, inside-5 carries, high-value touches;
- reliability: games played, injury status, depth chart role, team change flags;
- metadata: `feature_run_id`, `metric_version`, `source_freshness_json`, `missing_data_flags`, `created_at`.

Pigskin/UI safe: no direct exposure. Read through current and compatibility views.

### B. `player_recent_advanced_metrics_current`

Purpose: current rolling 3/5/8 week form, season-to-date rates, sample-size flags, and source freshness.

Grain:

```text
metric_version, as_of_season, as_of_week, player_id_internal, scoring_profile_id, league_type_id, roster_format_id
```

Required fields:

- rolling targets, carries, opportunities, fantasy points, EPA, success rates;
- rolling target share, air-yards share, WOPR, aDOT, RACR;
- rolling snap share and high-value touches;
- trend labels and sample-size flags.

Pigskin/UI safe: through compatibility view only.

### C. `team_week_context_metrics`

Purpose: team pace, pass rate, EPA, success rate, red-zone tendencies, opponent context, and environment.

Grain:

```text
metric_version, season, week, team
```

Required fields:

- plays per game, seconds per play, neutral pass rate, pass rate over expected, xpass, pass_oe;
- team EPA per play, pass EPA per play, rush EPA per play;
- team success rate, red-zone pass/rush rate;
- opponent EPA allowed and pass/rush funnel indicators;
- `game_environment_json`, source freshness, missing flags.

### D. `qb_week_environment_metrics`

Purpose: QB-specific passing/rushing environment and efficiency context.

Grain:

```text
metric_version, season, week, qb_player_id_internal
```

Required fields:

- dropbacks, pass attempts, sacks, scrambles, designed rushes;
- EPA/dropback, CPOE, aDOT, deep attempt rate, sack rate, scramble rate;
- pass rate over expected context;
- receiving target distribution summary;
- matchup and environment metadata.

### E. `player_role_usage_metrics_current`

Purpose: compact stable role fields for Pigskin and Streamlit.

Grain:

```text
metric_version, as_of_season, as_of_week, player_id_internal
```

Required fields:

- snap share, route share if available, target share, air-yards share, WOPR, carry share, opportunity share;
- red-zone role, high-value touches, trend direction, role volatility;
- injury/depth summary, team-change flags, freshness and missing flags.

Warning: route fields must stay null with `missing_route_source` until a true route source exists.

### F. `pigskin_player_context_packet_current`

Purpose: compact packet for Pigskin, show prep, and player comparison. This should replace prompt-time metric computation.

Grain:

```text
packet_version, player_id_internal, scoring_profile_id, league_type_id, roster_format_id
```

Required fields:

- identity block;
- ranking context;
- projection context;
- recent usage summary;
- advanced efficiency summary;
- QB/team/game environment;
- Fraud Watch and risk context;
- trade player score and draft pick context where applicable;
- source freshness and missing-data warnings;
- compact `packet_text` and `packet_json`.

### G. `compat_pigskin_player_context_current`

Purpose: UI-safe and Pigskin-safe compatibility view over the packet and advanced marts.

Rules:

- No raw/source dependencies in the view definition.
- It may read only output marts, current views, compatibility views, and identity/freshness metadata.
- Must include `source_freshness_json` and `missing_data_flags`.
- Must support lookup by player name, `player_id_internal`, Sleeper ID, team, position, and metric leader queries.

## Proposed Compatibility Contracts

Add docs and views later for:

- `player_week_advanced_metrics_current`
- `player_recent_advanced_metrics_current`
- `team_week_context_metrics_current`
- `qb_week_environment_metrics_current`
- `player_role_usage_metrics_current`
- `pigskin_player_context_packet_current`
- `compat_pigskin_player_context_current`

Contract requirements:

- grain stated in docs and tested by validations;
- no raw/source tables exposed in compatibility views;
- explicit source dependencies listed;
- source freshness JSON present;
- missing-data flags present;
- identity fields present;
- metric version and feature run ID present;
- no request-time writes;
- no LLM dependency.

## Pigskin Fast Retrieval Contract

Future helpers should return compact structured data. They must not run GenAI or calculate metrics from raw play rows at answer time.

Suggested helper interfaces:

```python
get_pigskin_player_context(
    player_query,
    scoring_profile_id="ppr",
    league_type_id="redraft",
    roster_format_id="one_qb",
)
```

```python
get_pigskin_player_compare_context(
    player_queries,
    scoring_profile_id="ppr",
    league_type_id="redraft",
    roster_format_id="one_qb",
)
```

```python
get_pigskin_metric_leaders(
    metric_name,
    position=None,
    window="last_3",
    scoring_profile_id="ppr",
    limit=25,
)
```

Required lookup support:

- player name;
- `player_id_internal`;
- Sleeper ID;
- team and position;
- top-N by metric;
- compare two or more players;
- explain why a player ranks above another;
- trend up/down;
- undervalued candidates using precomputed market, ranking, and projection fields;
- source freshness and missing-data warnings.

Response shape:

```json
{
  "found": true,
  "player": {},
  "advanced_metrics": {},
  "recent_form": {},
  "team_context": {},
  "ranking_context": {},
  "projection_context": {},
  "trade_context": {},
  "warnings": [],
  "source_freshness": {},
  "missing_data_flags": []
}
```

## Front-End Needs

Current working surfaces:

- Production and staging Cloud Run services exist and describe cleanly.
- Pigskin Studio uses parameterized context tools.
- Player Profiles can read profile/ranking evidence.
- Trade Lab can show Trade Score and Pick Score in staging through compatibility views.
- Data Ops Cloud Run and local subprocess controls remain gated.

Minimum future dashboard work after marts exist:

1. Pigskin question answering: keep the current context-tool loop, add advanced metric context tools.
2. Player search: use `compat_pigskin_player_context_current`, not raw player tables.
3. Player cards: add advanced metric bands, rolling usage, source warnings, and current-team/stat-week team distinction.
4. Advanced metric tables: top-N leaders by metric, position, season/week, and window.
5. Comparison view: side-by-side player context packets and differences.
6. Ranking/evidence view: show rank, why, recent form, role, efficiency, market/projection context.
7. YouTube/show prep view: compact script-ready evidence cards, Fraud Watch, risers/fallers, and player-vs-player debate packets.

Access note: Cloud Run describe reports `ingress=all` for production and staging. This is not a permission change. Auth and app login behavior were not tested in this phase because browser QA was out of scope.

## Cost and Performance Plan

Controls for future phases:

- Never scan `play_by_play` from Streamlit or Pigskin request paths.
- Precompute advanced metric tables by bounded season/week.
- Partition large marts by `season` and `week`.
- Cluster player-level marts by `player_id_internal`, `position`, `team`, and scoring context.
- Add `feature_run_id` and `metric_version` to every advanced metrics table.
- Use dry-run query-cost checks in builders before writes.
- Add validation SQL before materialization.
- Keep `source_freshness_json` and `missing_data_flags` first-class fields.
- Keep Pigskin packets compact and capped for context size.
- Keep raw/source dependencies in materializers only, never compatibility views.
- Add sample-size flags so Pigskin can explain thin data without pretending confidence.

## Validation Plan

Future validation SQL should cover:

- object existence;
- grain uniqueness;
- row counts by season/week;
- metric ranges and null sanity;
- denominator-zero handling;
- sample-size warnings present;
- source freshness present;
- missing flags present;
- identity coverage against `player_identity_bridge`;
- player/team/week coverage against source tables;
- no raw/source dependencies in compatibility views;
- no request-time writes;
- no Pigskin arbitrary SQL;
- metric leader sanity checks;
- position-specific field checks;
- route metrics remain null/flagged until route source exists;
- pressure-to-sack remains unavailable until true pressure source exists;
- no pick-score/player-score lane contamination.

Suggested validation patterns:

- `advanced_metrics`
- `pigskin_context_packet`
- `compat_pigskin_context`
- `team_context_metrics`
- `qb_environment_metrics`

## Recommended Implementation Phases

1. Phase 29.2: nflverse historical source acquisition and BigQuery backfill design.
2. Phase 29.3: create additive raw, staging, mart, current-view, compatibility-view, and validation contracts.
3. Phase 29.4: ingest or refresh nflverse historical data into raw and staging tables, only if explicitly authorized.
4. Phase 29.5: build dry-run SQL for core advanced metrics, no writes.
5. Phase 29.6: materialize `player_week_advanced_metrics` for historical seasons, only after bounded authorization.
6. Phase 29.7: materialize rolling/current metrics and `pigskin_player_context_packet_current`.
7. Phase 29.8: add Pigskin parameterized retrieval helpers, no LLM calls.
8. Phase 29.9: add dashboard player search, metric tables, comparison view, and show-prep view.
9. Phase 29.10: authenticated staging QA and release package review.
10. Separate Access Track: fix stable browser URL/access so the dashboard is usable.

## Blockers

No blocker prevents starting Phase 29.2 dry-run builders.

Metric-specific blockers:

- true route participation, yards per route run, and targets per route run need a route source;
- first-read target share needs a charting source;
- true pressure-to-sack rate needs pressure/hurry data, not just pass-rusher count or QB-fault sack flags;
- yards before contact and yards after contact need a contact-yard source;
- inline/blocking penalty and slot/wide alignment need alignment data;
- live/current sportsbook implied totals are not present. `spread_line` and `total_line` exist in `play_by_play`, but lineage should be validated before calling them current odds.

## Warnings

- `analytics_pigskin_rankings` currently has active 2026 rows, while the modern weekly source/mart coverage audited here is 2025.
- Raw/source tables do not carry source freshness or missing-data flags. New marts must add them.
- `analytics_player_weekly_truth` is curated, but it is still a table name shown in Pigskin's allowed schema text. The future advanced metrics path should shift to packet and compatibility helpers.
- The Trade Lab AI outlook block still contains a raw `weekly_metrics` fallback, though the control is hidden unless local admin subprocess gates are enabled.
- An exploratory read-only count query initially failed because `ROWS` was used as a BigQuery alias. The corrected table-level coverage query passed.

## Recommended Next Phase

Proceed to Phase 29.2 with nflverse historical source acquisition and BigQuery backfill design. Phase 29.2 should answer:

- exact historical season range, with a minimum target of 10-plus seasons where nflverse supports it;
- which `nflreadpy` loaders are already wired and which need to be added, especially `load_schedules`, `load_rosters`, `load_rosters_weekly`, `load_ff_playerids`, `load_participation`, and `load_team_stats`;
- raw landing table contracts for nflverse sources;
- staging table contracts for identity, player-week stats, team-week stats, game context, and play-player events;
- partitioning and clustering choices for cheap weekly refreshes;
- idempotent refresh strategy for current-season impacted weeks;
- validation patterns for historical backfill coverage and raw-source isolation.

Phase 29.2 should not create tables, apply migrations, ingest data, or write rows. The fastest safe path to a working Pigskin evidence database is:

1. design the nflverse raw/staging contracts;
2. backfill historical nflverse facts once authorized;
3. build feature marts from those facts;
4. generate compact Pigskin context packets;
5. wire Pigskin and UI helpers to packets and compatibility views.

## Owner Questions Answered

| Question | Answer |
| --- | --- |
| What can we calculate immediately from nflverse-backed data? | EPA, success rate, CPOE, WOPR, target share, air-yards share, aDOT, RACR, weighted opportunity, red-zone role, high-value touches, rolling 3/5/8 form, team EPA, team success, pace, pass rate over expected, opponent defensive EPA allowed, snap share, injury/depth context, NGS separation/RYOE context, and weather/stadium context once schedules are wired. |
| What existing warehouse tables should be replaced instead of repaired? | Treat `play_by_play`, `weekly_metrics`, roster/player identity inputs, NGS, FTN, snap, injury, depth, and game context sources as refresh/backfill candidates from nflverse. Ignore or deprecate `active_league_rosters` and `historical_player_metrics`. Keep curated marts as consumers, not historical source of truth. |
| What raw nflverse tables/files do we need first? | PBP, weekly player stats, rosters, weekly rosters, players, fantasy player IDs, schedules, team stats, snap counts, participation, injuries, depth charts, NGS, FTN charting. |
| What BigQuery tables should be created first? | `raw_nflverse_pbp`, `raw_nflverse_weekly`, `raw_nflverse_rosters`, `raw_nflverse_schedules`, `raw_nflverse_players`, `raw_nflverse_injuries`, `raw_nflverse_snap_counts`, `raw_nflverse_participation`, then `stg_player_week_stats`, `stg_team_week_stats`, `stg_game_context`, `stg_player_identity`, and `stg_play_player_events`. |
| What metrics should be precomputed first for maximum Pigskin value? | Player opportunity and efficiency metrics: WOPR, target share, air-yards share, aDOT, RACR, weighted opportunity, red-zone/high-value usage, EPA, success rate, CPOE, rolling form, snap share, team pace, team EPA, opponent funnel context, and source warnings. |
| What can wait until Sleeper/current-season integration? | League rosters, ownership, matchups, available players, viewer-team context, and league-specific weekly advice can wait behind the historical nflverse feature warehouse. |
| What is the fastest safe path? | Design nflverse raw/staging contracts, backfill historical facts, build historical feature marts, produce current Pigskin packets, then wire Pigskin/UI retrieval to compact compatibility views. Do not start with hard-coded rankings. |

## Final Decision

PIGSKIN ADVANCED METRICS FOUNDATION READY WITH WARNINGS
