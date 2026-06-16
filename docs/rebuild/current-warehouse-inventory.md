# Current Warehouse Inventory

Source docs:

- [docs/CODEX_PROJECT_CONTEXT.md](../CODEX_PROJECT_CONTEXT.md)
- [docs/rebuild/audit-and-rebuild-plan.md](audit-and-rebuild-plan.md)
- [docs/rebuild/cloud-run-operating-model.md](cloud-run-operating-model.md)

Scope: every BigQuery table name referenced by `app.py` and `src/`. This is a repo inventory only. No runtime behavior changes were made.

Architecture note: future rebuild sprints should follow the Cloud Run operating model. Firebase is not the target architecture unless the project explicitly reopens that decision.

The active dataset used by the app and pipeline is `fantasy_football_brain`. `src/load.py:10-17` pins the default project to `fantasy-football-498121`, and `src/load.py:31-47` creates the dataset if missing.

## Inventory Summary

| Group | Tables | Current state |
| --- | ---: | --- |
| Raw/source nflreadpy tables | 13 | Loaded by `src/pipeline.py` with season range partitioning through `src/load.py:54-101`. |
| Sleeper source snapshots | 8 | Appended by `src/ingest_sleeper_league.py:323-340`; no partitioning is configured there. |
| Sleeper global/news snapshots | 2 | Written with `WRITE_TRUNCATE` by `src/ingest_news.py:139-185`; no partitioning is configured. |
| External/context tables | 4 | Mixed admin, context, and staging use. Some are LLM-safe only as cited evidence. |
| Current analytics marts | 7 | Created mostly by `src/materialize.py`; these are the safest current UI/LLM tables. |
| Output tables | 12 | Pigskin rankings, Fraud Watch, trade review packets, segment packets, and versioned projection outputs are current or planned show-facing outputs. |
| Cloud Run Job metadata | 1 | Created by `bigquery/migrations/0019__cloud_run_job_runs.sql`; written by `src/job_runner.py`. |
| Model-run metadata/config tables | 6 | Created by migrations and used by future ranking/projection lineage helpers. |
| Player identity foundation | 3 | Created by `0005__player_identity_bridge.sql`; materialized by `src/build_player_identity.py`. |
| Scoring profile outputs | 1 | Created by `0006__scoring_profile_fantasy_points.sql`; materialized by `src/materialize_fantasy_points.py`. |
| Deprecated/unknown prompt references | 2 | Present in Pigskin schema text, but no writer was found in `app.py` or `src/`. |

## Table Inventory

| Table | Class | Read refs | Write refs | Known grain | Partition behavior | Safe for UI/LLM |
| --- | --- | --- | --- | --- | --- | --- |
| `INFORMATION_SCHEMA.TABLES` | admin metadata | `src/materialize.py:get_existing_tables`, `src/materialize.py:6-9` | BigQuery system table | one row per dataset table | system metadata | Safe for admin diagnostics only. |
| `dashboard_job_runs` | admin metadata | `app.py:get_persisted_last_success`, `app.py:601-617` | `app.py:mark_successful_run`, `app.py:562-587` | one job completion event | no partitioning configured | Safe for admin UI, not useful for Pigskin analysis. |
| `cloud_run_job_runs` | admin metadata | future dashboard/job-status readers; validation queries `bigquery/validations/096-100` | migration `bigquery/migrations/0019__cloud_run_job_runs.sql`; `src/job_runner.py:start_job_run` and `src/job_runner.py:finish_job_run` | one Cloud Run Job execution | partition by `DATE(started_at)`; cluster by job name, status, season, week | Safe for admin job status and lineage metadata. Not player evidence. |
| `play_by_play` | raw/source | `src/materialize.py:35`, `src/materialize.py:293`, `src/materialize.py:1271`; prompt exposure `app.py:2630` | `src/pipeline.py:128` | one NFL play | range partition by `season`, `src/load.py:54-101` | Not safe for UI/LLM except through curated marts. |
| `weekly_metrics` | raw/source | UI debt at `app.py:814` and `app.py:3150`; `src/materialize.py:280`; prompt exposure `app.py:2606` | `src/pipeline.py:137` | one player-season-week stat row | range partition by `season`, `src/load.py:54-101` | Not safe for direct UI/LLM. |
| `team_descriptions` | raw/source | prompt exposure `app.py:2684` | `src/pipeline.py:146` | one team-season row after replication | range partition by `season`, `src/load.py:54-101`; replicated in `src/transform.py:83-101` | Not safe directly. Use a team dimension mart. |
| `draft_picks` | raw/source | no direct read found in `app.py`; extraction path in `src/extract.py:162-168` | `src/pipeline.py:155` | one NFL draft pick | range partition by `season`, `src/load.py:54-101`; filtered in `src/transform.py:107-126` | Not currently UI/LLM-facing. |
| `player_rosters` | raw/source | `app.py:1095`, `app.py:1116`; `src/materialize.py:224`, `src/materialize.py:714`, `src/materialize.py:754` | `src/pipeline.py:164` | one player-season roster row after replication | range partition by `season`, `src/load.py:54-101`; replicated in `src/transform.py:129-148` | Not safe directly. Needs player identity bridge. |
| `player_contracts` | raw/source | `app.py:1165` | `src/pipeline.py:173` | one contract row per replicated season | range partition by `season`, `src/load.py:54-101`; replicated in `src/transform.py:151-170` | Not safe directly. Use profile/evidence mart. |
| `ngs_passing` | raw/source | prompt exposure `app.py:2638`; repair list `app.py:696-697` | `src/pipeline.py:178` | one player-season/week NGS passing row, inferred | range partition by `season`, `src/load.py:54-101` | Not safe directly. |
| `ngs_rushing` | raw/source | prompt exposure `app.py:2673`; repair list `app.py:696-697` | `src/pipeline.py:179` | one player-season/week NGS rushing row, inferred | range partition by `season`, `src/load.py:54-101` | Not safe directly. |
| `ngs_receiving` | raw/source | `src/materialize.py:150`; prompt exposure `app.py:2675`; repair list `app.py:696-697` | `src/pipeline.py:180` | one player-season/week NGS receiving row, inferred | range partition by `season`, `src/load.py:54-101` | Not safe directly. |
| `ftn_charting` | raw/source | prompt exposure `app.py:2677` | `src/pipeline.py:181` | one charting row, likely play/player-level | range partition by `season`, `src/load.py:54-101` | Not safe directly. |
| `weekly_snap_counts` | raw/source | `src/materialize.py:123`; prompt exposure `app.py:2679` | `src/pipeline.py:184` | one player-team-week snap row | range partition by `season`, `src/load.py:54-101` | Not safe directly. |
| `injury_reports` | raw/source | `src/materialize.py:177`; prompt exposure `app.py:2681` | `src/pipeline.py:185` | one player-team-week injury report row | range partition by `season`, `src/load.py:54-101` | Not safe directly. Use injury context mart. |
| `depth_charts` | raw/source | `app.py:1180` | `src/pipeline.py:188` | one player-team-date depth chart row, inferred | range partition by `season`, `src/load.py:54-101`; filtered in `src/transform.py:195-214` | Not safe directly. Use current role mart. |
| `sleeper_players_current` | raw/source snapshot | `src/materialize.py:718`, `src/materialize.py:736`; prompt exposure `app.py:2644` | `src/ingest_news.py:139-161` | one fantasy player per Sleeper snapshot | `WRITE_TRUNCATE`, no partitioning configured | Safe only as source to identity/ranking marts. |
| `realtime_player_news` | staging/source | `src/materialize.py:201`; prompt exposure `app.py:2641` | `src/ingest_news.py:179-185` | one trending add/drop row per player/trend refresh | `WRITE_TRUNCATE`, no partitioning configured | Not safe as final evidence without context wrapper. |
| `sleeper_leagues` | raw/source snapshot | prompt exposure `app.py:2656` | schema `src/ingest_sleeper_league.py:18`; rows `src/ingest_sleeper_league.py:312`; load `src/ingest_sleeper_league.py:366` | one league per snapshot/week | `WRITE_APPEND`, no partitioning configured | Not safe directly. |
| `sleeper_league_users` | raw/source snapshot | prompt exposure `app.py:2656` | schema `src/ingest_sleeper_league.py:24`; rows `src/ingest_sleeper_league.py:313`; load `src/ingest_sleeper_league.py:366` | one user per league snapshot/week | `WRITE_APPEND`, no partitioning configured | Not safe directly. |
| `sleeper_rosters` | raw/source snapshot | `app.py:806`, `app.py:845`; prompt exposure `app.py:2656` | schema `src/ingest_sleeper_league.py:29`; rows `src/ingest_sleeper_league.py:314`; load `src/ingest_sleeper_league.py:366` | one roster per league snapshot/week | `WRITE_APPEND`, no partitioning configured | Not safe directly. |
| `sleeper_roster_players` | raw/source snapshot | `app.py:839`, `app.py:3438`, `app.py:3481`; prompt exposure `app.py:2650` | schema `src/ingest_sleeper_league.py:37`; rows `src/ingest_sleeper_league.py:315`; load `src/ingest_sleeper_league.py:366` | one roster-player per league snapshot/week | `WRITE_APPEND`, no partitioning configured | Not safe directly. |
| `sleeper_matchups` | raw/source snapshot | prompt exposure `app.py:2656` | schema `src/ingest_sleeper_league.py:44`; rows `src/ingest_sleeper_league.py:316`; load `src/ingest_sleeper_league.py:366` | one roster matchup per league/week snapshot | `WRITE_APPEND`, no partitioning configured | Not safe directly. |
| `sleeper_lineups` | raw/source snapshot | `app.py:3483`; prompt exposure `app.py:2653` | schema `src/ingest_sleeper_league.py:49`; rows `src/ingest_sleeper_league.py:317`; load `src/ingest_sleeper_league.py:366` | one lineup-player per league/week snapshot | `WRITE_APPEND`, no partitioning configured | Not safe directly. |
| `sleeper_available_players` | raw/source snapshot | `app.py:3509`, `app.py:3549` | schema `src/ingest_sleeper_league.py:56`; rows `src/ingest_sleeper_league.py:318`; load `src/ingest_sleeper_league.py:366` | one unrostered player per league/week snapshot | `WRITE_APPEND`, no partitioning configured | Not safe directly. |
| `sleeper_viewer_team_snapshots` | staging/source snapshot | `app.py:3420`; prompt exposure `app.py:2647` | schema `src/ingest_sleeper_league.py:62`; rows `src/ingest_sleeper_league.py:319`; load `src/ingest_sleeper_league.py:366` | one viewer-team summary per ingest | `WRITE_APPEND`, no partitioning configured | Not safe directly. |
| `market_values` | raw/source snapshot | legacy direct UI debt at `app.py:2761-2769`; repair list `app.py:707-708`; controlled mart read in `src/materialize_trade_assets.py` | `src/fetch_market_values.py:11`, `src/fetch_market_values.py:67-97` | one FantasyCalc player value row | table is deleted and recreated, no partitioning configured | Not safe directly. Use `compat_trade_assets_current`. |
| `college_player_stats` | raw/source | `app.py:1198`; prompt exposure `app.py:2693` | schema `src/setup_college_tables.py:14-29`; load `src/ingest_college_data.py:133-172` | one college player-season stat row | range partition by `season`, `src/setup_college_tables.py:51-67` | Not safe directly. Use prospect feature mart. |
| `rookie_scouting_metrics` | staging/source, manual | `app.py:1213`; prompt exposure `app.py:2689` | schema `src/setup_college_tables.py:32-49`; UI load `app.py:4018-4023` | one rookie/player scouting row | range partition by `season`, `src/setup_college_tables.py:51-67` | Not safe directly. Use prospect feature mart. |
| `analytics_context_events` | feature-like mart | prompt exposure `app.py:2664`, guidance `app.py:2719-2733` | `src/ingest_context_events.py:62-69` | one curated context event | `WRITE_TRUNCATE`, no partitioning configured | Safe for LLM as labeled context. |
| `analytics_external_context_search_results` | feature-like mart | `app.py:3161`; prompt exposure `app.py:2667`, guidance `app.py:2720` | schema `src/verify_player_context.py:63-81`; load `src/verify_player_context.py:283-287` | one search result per player/query/result rank | no partitioning configured | Safe for LLM only as stored external lead, not as verified fact by itself. |
| `analytics_api_usage_daily` | admin metadata | `src/verify_player_context.py:89` | `src/verify_player_context.py:53`, `src/verify_player_context.py:106` | one service-day usage counter | no partitioning configured | Safe for admin only. |
| `analytics_game_environment` | feature-like mart | prompt exposure `app.py:2670`; guidance `app.py:2717` | `src/materialize.py:16-105` | one game-season-week | range partition by `season`; cluster by teams and environment categories | Safe for UI/LLM. |
| `analytics_player_qb_weekly` | feature-like mart | `src/materialize.py:253`, `src/materialize.py:1388`; prompt exposure `app.py:2661` | `src/materialize.py:1249-1348` | one receiver-QB-season-week-team split | range partition by `season`; cluster by player, QB, team | Safe for UI/LLM with sample-size caveats. |
| `analytics_player_qb_splits` | feature-like mart | prompt exposure `app.py:2658`; guidance `app.py:2716` | `src/materialize.py:1350-1395` | one receiver-QB-season split | range partition by `season`; cluster by player, QB, team | Safe for UI/LLM with sample-size caveats. |
| `analytics_player_weekly_truth` | feature-like mart | `app.py:802`, `app.py:872`, `app.py:1124`, `app.py:1153`, `app.py:1359`, `app.py:1381`, `app.py:3457`, `app.py:3527`; `src/materialize.py:646`, `src/materialize.py:805`, `src/materialize.py:844`, `src/materialize.py:866`; prompt exposure `app.py:2583` | `src/materialize.py:274` | one player-season-week analytical row | range partition by `season`; see `src/materialize.py:274` | Safe current mart, but should become an input to more specific compatibility marts. |
| `analytics_fraud_watch` | output | `app.py:737`, `app.py:740`, `app.py:762`; prompt exposure `app.py:2602` | `src/materialize.py:591-704` | one fraud candidate per player-week | range partition by `season`; cluster by label, position, player | Safe show-facing output. |
| `analytics_pigskin_rankings_candidates` | feature-like mart | `src/generate_pigskin_rankings.py:49`; prompt exposure `app.py:2594` | `src/materialize.py:703-1142` | one player-rank candidate per season/position/ranking run | range partition by `season`; cluster by position, rank, player | Safe for backend ranking evidence, not final UI rank truth. |
| `analytics_pigskin_rankings` | output | `app.py:1325`; prompt exposure `app.py:2589`; `src/materialize.py:1150`, `src/materialize.py:1238` | `src/generate_pigskin_rankings.py` writes current rows through `write_rankings` | one active Pigskin ranking row per player/position | no explicit partition in DataFrame load | Safe canonical current ranking output. New rows include `model_run_id`; older rows may be NULL. |
| `analytics_pigskin_rankings_history` | output | prompt exposure `app.py:2598`; `src/materialize.py:1241` | `src/materialize.py:1146-1241`; `src/generate_pigskin_rankings.py` appends history rows through `write_rankings` | one ranking row per `ranking_version` and player/position | materialize DDL partitions by `season`, but DataFrame-created table may depend on creation order | Safe historical ranking output. New rows include `model_run_id`; older rows may be NULL. |
| `player_identity_bridge` | feature-like mart | future compatibility marts; validation queries `bigquery/validations/009-016` | `src/build_player_identity.py`; migration `0005__player_identity_bridge.sql` | one current canonical player identity per `player_id_internal` | partition by `DATE(updated_at)`; cluster by position, current team, internal ID | Safe as identity bridge. Use for downstream joins instead of fragile names. |
| `dim_players_current` | feature-like mart | future UI, ranking, projection, trade, and evidence packet consumers | `src/build_player_identity.py`; migration `0005__player_identity_bridge.sql` | one current player dimension row per `player_id_internal` | partition by `DATE(updated_at)`; cluster by position, current team, internal ID | Safe current player dimension. |
| `player_identity_overrides` | admin metadata | `src/build_player_identity.py:fetch_overrides` | migration `0005__player_identity_bridge.sql`; manual/admin writes | one manual source ID override | partition by `DATE(created_at)`; cluster by active, source, source player ID | Safe admin correction table, not an analytics feature. |
| `analytics_player_fantasy_points_by_profile` | feature-like mart | future trade, profile, projection, ranking, and evidence-packet marts; validation queries `bigquery/validations/017-021` | `src/materialize_fantasy_points.py`; migration `0006__scoring_profile_fantasy_points.sql` | one player-week per scoring profile and player identity/source key | range partition by `season`; cluster by identity, scoring profile, position, team | Safe scoring foundation. Use instead of raw `weekly_metrics` for profile-aware fantasy point totals. |
| `mart_player_profiles_current` | feature-like mart | future Player Profiles helper `src/player_profiles.py`; validation queries `bigquery/validations/028-034` | migration `0008__promote_compat_player_profiles_current.sql`; materialized by `src/materialize_player_profiles.py` | one current player profile per scoring profile and as-of season/week | partition by `DATE(refreshed_at)`; cluster by identity, position, team, scoring profile | Safe backing mart after materialization. Hides raw profile source joins behind a curated profile packet. |
| `compat_player_profiles_current` | feature-like mart | future Player Profiles helper `src/player_profiles.py`; validation queries `bigquery/validations/028-034` | migration `0008__promote_compat_player_profiles_current.sql`; view template `bigquery/views/compat_player_profiles_current.sql` | one current player profile per scoring profile and as-of season/week | view over `mart_player_profiles_current` | Safe for UI/LLM consumption after feature-flagged app wiring. Replaces raw profile joins with identity, scoring, role, EPA, Pigskin ranking, and profile summary context. |
| `mart_llm_player_context_packet` | output | future Pigskin packet helper `src/llm_context_packets.py`; validation queries `bigquery/validations/035-042` | migration `0009__build_llm_player_context_packet.sql`; materialized by `src/materialize_llm_packets.py` | one LLM player packet per player, scoring profile, league type, roster format, model run, and as-of season/week | partition by `DATE(updated_at)`; cluster by identity, scoring profile, position, team, model run | Safe backing packet mart after materialization. Precomputes bounded LLM evidence packets from compatibility objects and allowed analytics outputs. |
| `llm_player_context_packet` | output | future Pigskin packet helper `src/llm_context_packets.py`; validation queries `bigquery/validations/035-042` | migration `0009__build_llm_player_context_packet.sql`; view template `bigquery/views/llm_player_context_packet.sql` | one LLM player packet per player, scoring profile, league type, roster format, model run, and as-of season/week | view over `mart_llm_player_context_packet` | Safe for UI/LLM consumption after feature-flagged chat wiring. Replaces arbitrary raw-table SQL with bounded packet context. |
| `compat_trade_player_history` | feature-like mart | future Trade Lab helper `src/trade_history.py`; validation queries `bigquery/validations/022-027` | migration `0007__promote_compat_trade_player_history.sql`; view template `bigquery/views/compat_trade_player_history.sql` | one player-week per scoring profile and player identity/source key | view over partitioned/scored marts; bounded helper queries by season window and limit | Safe for UI/LLM consumption after feature-flagged app wiring. Replaces raw `weekly_metrics` history with scoring, EPA, QB split, ranking, identity, and game environment context. |
| `mart_trade_assets_current` | feature-like mart | future Trade Lab helper `src/trade_assets.py`; validation queries `bigquery/validations/043-050` | migration `0010__promote_compat_trade_assets_current.sql`; materialized by `src/materialize_trade_assets.py` | one current trade asset per identity/source key, scoring profile, league type, roster format, and market snapshot date | partition by `market_snapshot_date`; cluster by identity, position, team, scoring profile | Safe backing mart after materialization. Uses controlled `market_values`, identity, Pigskin ranking, recent history, and fraud context. |
| `compat_trade_assets_current` | feature-like mart | future Trade Lab helper `src/trade_assets.py`; validation queries `bigquery/validations/043-050` | migration `0010__promote_compat_trade_assets_current.sql`; view template `bigquery/views/compat_trade_assets_current.sql` | one current trade asset per identity/source key, scoring profile, league type, roster format, and market snapshot date | view over `mart_trade_assets_current` | Safe for UI/LLM consumption after feature-flagged app wiring. Replaces direct `market_values` reads with normalized asset context. |
| `trade_review_requests` | admin metadata | future Trade Lab or Pigskin helper `src/trade_review_packets.py` | migration `0016__create_trade_review_packets.sql`; helper `src/trade_review_packets.py` | one trade review request per `trade_review_id` | partition by `DATE(created_at)`; cluster by scoring, league type, roster format, status | Safe request ledger. No Streamlit wiring yet. |
| `trade_review_packets` | output | future Trade Lab, Pigskin, and show-writing tools through `src/trade_review_packets.py` | migration `0016__create_trade_review_packets.sql`; helper `src/trade_review_packets.py` | one deterministic packet per `trade_review_id` | partition by `DATE(updated_at)`; cluster by scoring, league type, roster format, winner | Safe deterministic trade review output after packets are saved. |
| `trade_review_packet_players` | output | future packet detail reads through `src/trade_review_packets.py` | migration `0016__create_trade_review_packets.sql`; helper `src/trade_review_packets.py` | one player or asset per trade side per `trade_review_id` | partition by `DATE(created_at)`; cluster by review ID, side, player, position | Safe player-level evidence output after packets are saved. |
| `fraud_watch_packets` | output | future Segments, Pigskin, and show-writing tools through `src/segment_packets.py`; validation queries `bigquery/validations/074-078` and `084` | migration `0017__create_fraud_breakout_packets.sql`; helper `src/segment_packets.py` | one deterministic packet per player, model run, scoring profile, league type, roster format, season, and week | range partition by `season`; cluster by identity, position, scoring profile, week | Safe deterministic Fraud Watch packet output after packets are saved. No Streamlit wiring yet. |
| `sleeper_breakout_packets` | output | future Segments, Pigskin, and show-writing tools through `src/segment_packets.py`; validation queries `bigquery/validations/079-084` | migration `0017__create_fraud_breakout_packets.sql`; helper `src/segment_packets.py` | one deterministic packet per player, model run, scoring profile, league type, roster format, season, and week | range partition by `season`; cluster by identity, position, scoring profile, week | Safe deterministic Sleeper Breakout packet output after packets are saved. No Streamlit wiring yet. |
| `projections_player_weekly` | output | future projection consumers through `src/projection_engine.py`; validation queries `bigquery/validations/085`, `088-091`, and `095` | migration `0018__create_projection_outputs.sql`; helper `src/projection_engine.py` | one weekly projection per player, season, week, scoring profile, league type, roster format, and model run | range partition by `season`; cluster by model run, scoring profile, roster format, position | Safe versioned weekly projection output. No Streamlit wiring yet. |
| `projections_player_ros` | output | future projection consumers through `src/projection_engine.py`; validation queries `bigquery/validations/086`, `088-091`, and `095` | migration `0018__create_projection_outputs.sql`; helper `src/projection_engine.py` | one ROS projection per player, as-of season/week, scoring profile, league type, roster format, and model run | range partition by `as_of_season`; cluster by model run, scoring profile, roster format, position | Safe versioned rest-of-season projection output. No Streamlit wiring yet. |
| `projections_player_dynasty` | output | future projection consumers through `src/projection_engine.py`; validation queries `bigquery/validations/087-091` and `095` | migration `0018__create_projection_outputs.sql`; helper `src/projection_engine.py` | one dynasty projection per player, as-of season/week, scoring profile, league type, roster format, and model run | range partition by `as_of_season`; cluster by model run, scoring profile, roster format, position | Safe versioned dynasty projection output. No Streamlit wiring yet. |
| `projection_rankings_current` | output | future projection ranking consumers through `src/projection_engine.py`; validation queries `bigquery/validations/088-090`, `092-094` | migration `0018__create_projection_outputs.sql`; helper `src/projection_engine.py` | one ranking row per projection output player, horizon, scoring profile, league type, roster format, and model run | partition by `DATE(created_at)`; cluster by model run, scoring profile, roster format, position | Safe current projection ranking output by model run and horizon. Does not replace Pigskin rankings UI yet. |
| `model_runs` | admin metadata | `src/model_runs.py:get_model_run`, `src/model_runs.py:153`; `src/model_runs.py:get_latest_model_run`, `src/model_runs.py:175` | `bigquery/migrations/0002__create_model_runs.sql`; additive migration `bigquery/migrations/0003__model_run_config_foundation.sql`; `src/model_runs.py:create_model_run`, `src/model_runs.py:46`; status updates at `src/model_runs.py:100` and `src/model_runs.py:125` | one generated model/projection/ranking/backtest run | partition by `created_at`; base cluster by run/status fields | Safe as lineage metadata. Not player evidence by itself. |
| `scoring_profiles` | admin metadata | no runtime reader yet | `bigquery/migrations/0003__model_run_config_foundation.sql` | one scoring profile | partition by `created_at`; cluster by active/profile ID | Safe config metadata. |
| `league_types` | admin metadata | no runtime reader yet | `bigquery/migrations/0003__model_run_config_foundation.sql` | one league type | partition by `created_at`; cluster by active/league type ID | Safe config metadata. |
| `roster_formats` | admin metadata | no runtime reader yet | `bigquery/migrations/0003__model_run_config_foundation.sql` | one roster format | partition by `created_at`; cluster by active/roster format ID | Safe config metadata. |
| `feature_config_versions` | admin metadata | no runtime reader yet | `bigquery/migrations/0003__model_run_config_foundation.sql` | one feature config version | partition by `created_at`; cluster by active/config/horizon | Safe config metadata. |
| `source_freshness_snapshots` | admin metadata | `model_runs` rows reference `source_freshness_snapshot_id`; no UI reader yet | `bigquery/migrations/0003__model_run_config_foundation.sql`; `src/model_runs.py:create_source_freshness_snapshot`, `src/model_runs.py:218` | one source freshness snapshot | partition by `created_at`; cluster by snapshot ID | Safe lineage metadata. |
| `active_league_rosters` | deprecated/unknown | prompt exposure only, `app.py:2623` | no writer found | unknown | unknown | Not safe. Remove from prompt or replace with Sleeper marts. |
| `historical_player_metrics` | deprecated/unknown alias | prompt text says alias for `weekly_metrics`, `app.py:2606` | no writer found | unknown alias | unknown | Not safe. Replace with `analytics_player_weekly_truth` or future feature mart. |

## Compatibility Layer Proposal

The minimum compatibility layer should preserve existing function names and visual behavior while moving the SQL source behind them.

1. `compat_player_profiles_current`
   - Replaces raw reads in `fetch_player_profiles_data`, `app.py:1090-1275`.
   - Inputs: `dim_players_current`, `player_identity_bridge`, `analytics_player_weekly_truth`, `analytics_player_fantasy_points_by_profile`, `analytics_pigskin_rankings`, and optional controlled materializer reads from contract, depth, college, and rookie source tables.
   - Grain: one current fantasy-relevant player per scoring profile and as-of season/week.
   - Runtime status: production mart, view, materializer, and helper exist, but `app.py` remains unchanged until feature-flagged wiring.

2. `compat_sleeper_watch_candidates`
   - Replaces `render_sleeper_watch_segment`, especially raw `weekly_metrics` at `app.py:814` and raw Sleeper roster counts at `app.py:839-845`.
   - Inputs: `analytics_player_weekly_truth`, `analytics_player_fantasy_points_by_profile`, `analytics_pigskin_rankings`, `analytics_fraud_watch`, `analytics_game_environment`, `dim_players_current`, `player_identity_bridge`, controlled Sleeper snapshots, and `realtime_player_news`.
   - Grain: one player candidate per canonical or temporary source key, league/global context, scoring profile, league type, roster format, season, and week.
   - Runtime status: production mart, view, materializer, and helper exist, but `app.py` remains unchanged until feature-flagged wiring.

3. `compat_trade_assets_current`
   - Replaces direct `market_values` reads in `app.py:2761-2769`.
   - Inputs: controlled `market_values`, identity bridge, current player dimension, rankings, recent trade history, fraud context, current team, age, scoring profile, league type, roster format, and source freshness.
   - Grain: one current trade asset per identity/source key, scoring profile, league type, roster format, and market snapshot date.
   - Runtime status: production mart, view, materializer, and helper exist, but `app.py` remains unchanged until feature-flagged wiring.

4. `compat_trade_player_history`
   - Replaces raw `weekly_metrics` history in `app.py:3147-3155`.
   - Inputs: `analytics_player_fantasy_points_by_profile`, `analytics_player_weekly_truth`, `player_identity_bridge`, `analytics_pigskin_rankings`, and `analytics_game_environment`.
   - Grain: one player-week per scoring profile, capped by helper queries for UI.
   - Runtime status: production view and helper exist, but `app.py` remains unchanged until feature-flagged wiring.

5. `trade_review_packets`
   - New deterministic packet output for future Trade Lab, Pigskin, and show-writing tools.
   - Inputs: `compat_trade_assets_current`, `compat_trade_player_history`, `compat_player_profiles_current`, optional request context, and model-run lineage when available.
   - Grain: one packet per `trade_review_id`, plus one player row per side asset.
   - Runtime status: schema, helper, contracts, and validations exist, but `app.py` remains unchanged until feature-flagged wiring.

6. `fraud_watch_packets`
   - New deterministic packet output for future Fraud Watch segments, Pigskin, and show-writing tools.
   - Inputs: `analytics_fraud_watch`, `compat_trade_assets_current`, `compat_player_profiles_current`, and model-run lineage when available.
   - Grain: one packet per player, model run, scoring profile, league type, roster format, season, and week.
   - Runtime status: schema, helper, contracts, and validations exist, but `app.py` remains unchanged until feature-flagged wiring.

7. `sleeper_breakout_packets`
   - New deterministic packet output for future Sleeper Breakout segments, Pigskin, and show-writing tools.
   - Inputs: `compat_sleeper_watch_candidates` and model-run lineage when available.
   - Grain: one packet per player, model run, scoring profile, league type, roster format, season, and week.
   - Runtime status: schema, helper, contracts, and validations exist, but `app.py` remains unchanged until feature-flagged wiring.

8. Projection outputs
   - New deterministic weekly, ROS, dynasty, and projection-ranking outputs.
   - Inputs: `compat_trade_player_history`, `compat_player_profiles_current`, `compat_trade_assets_current`, `fraud_watch_packets`, `sleeper_breakout_packets`, and model-run/source-freshness metadata.
   - Grain: one projection row per player, horizon, scoring profile, league type, roster format, as-of context, and model run.
   - Runtime status: schema, helper, contracts, docs, and validations exist, but `app.py` remains unchanged until feature-flagged wiring.

9. `compat_viewer_team_context`
   - Replaces raw Sleeper joins in `get_sleeper_viewer_team_context`, `app.py:3390-3570`.
   - Inputs: controlled Sleeper snapshots, current Sleeper player map, identity bridge, current player dimension, Pigskin rankings, trade assets, Sleeper Watch candidates, player profiles, trade history, and LLM context packets.
   - Grain: one packet per league, roster, manager, season, week, scoring profile, league type, roster format, and latest snapshot.
   - Runtime status: production mart, filtered packet view, materializer, and helper exist, but `app.py` remains unchanged until feature-flagged wiring.
   - The compatibility view exposes only materialized packet rows where `packet_json IS NOT NULL`; older legacy mart rows may remain in the backing table until cleanup.

10. `llm_player_context_packet`
   - Replaces arbitrary Pigskin chat access to raw tables.
   - Inputs: `compat_player_profiles_current`, `compat_trade_player_history`, `model_runs`, fraud watch, ranking history, QB splits, context events, and external verification leads.
   - Grain: one player, scoring profile, league type, roster format, model run, and as-of season/week.
   - Runtime status: production mart, view, materializer, and helper exist, but Pigskin chat remains unchanged until feature-flagged wiring.

11. `model_runs`
   - Adds the required compatibility metadata for generated outputs.
   - Existing `ranking_version` remains as display compatibility until the UI is migrated.

12. Model-run config tables
   - `scoring_profiles`, `league_types`, `roster_formats`, `feature_config_versions`, and `source_freshness_snapshots` support reproducible model context.
   - These are admin/config metadata, not direct player evidence.

## Prioritized Migration-Debt List

1. P0: Wire `render_sleeper_watch_segment` to `compat_sleeper_watch_candidates` and Trade Lab to `compat_trade_player_history` behind default-off flags.
2. P0: Add `model_runs` and write `model_run_id` into Pigskin rankings while preserving `ranking_version`.
3. P0: Build `player_identity_bridge` so Player Profiles and rankings stop joining by fragile names.
4. P0: Replace `active_league_rosters` and `historical_player_metrics` prompt references.
5. P1: Move Player Profiles onto `compat_player_profiles_current`.
6. P1: Replace Pigskin arbitrary SQL with `llm_player_context_packet` helper calls behind a default-off flag.
7. P1: Move Viewer Team Lab onto `compat_viewer_team_context` behind `USE_COMPAT_VIEWER_TEAM_CONTEXT=false` after packet validation.
7. P1: Wire market values through `compat_trade_assets_current` after live validation.
8. P1: Wire Trade Lab and Pigskin to `trade_review_packets` behind a default-off feature flag after packet validation.
9. P1: Wire Segment pages and Pigskin to `fraud_watch_packets` and `sleeper_breakout_packets` behind default-off flags after packet validation.
10. P1: Generate and validate baseline projection outputs before wiring rankings, trade, viewer-team, segment, or Pigskin consumers.
11. P1: Add partitioning or replacement marts for append-only Sleeper tables.
12. P2: Restrict Pigskin chat to allowlisted context packet APIs instead of arbitrary SQL.
