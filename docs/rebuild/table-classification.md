# Table Classification

This file classifies every BigQuery table referenced by `app.py` and `src/`. It is documentation only.

Architecture note: future rebuild sprints should follow [docs/rebuild/cloud-run-operating-model.md](cloud-run-operating-model.md). Firebase is not the target architecture unless the project explicitly reopens that decision.

Classification values:

- `raw/source`: direct external or low-level source data.
- `staging`: intermediate, append snapshot, or narrow source-refresh table.
- `feature-like mart`: derived analytical context that can support decisions.
- `output`: user-facing or show-facing generated result.
- `admin metadata`: operational state or BigQuery metadata.
- `deprecated/unknown`: referenced, but no current writer or clear contract was found.

## Current Classification Map

| Table | Classification | Rationale | UI/LLM status |
| --- | --- | --- | --- |
| `INFORMATION_SCHEMA.TABLES` | admin metadata | Used by `src/materialize.py:get_existing_tables`, `src/materialize.py:6-9`, to inspect table existence. | Admin only. |
| `dashboard_job_runs` | admin metadata | App stores last run status with `app.py:mark_successful_run`, `app.py:562-587`, and reads with `app.py:get_persisted_last_success`, `app.py:601-617`. | Admin UI only. |
| `cloud_run_job_runs` | admin metadata | Created by `bigquery/migrations/0019__cloud_run_job_runs.sql`; written by `src/job_runner.py` to track Cloud Run Job start, success, failure, model run linkage, and runtime context. | Admin job status only. |
| `play_by_play` | raw/source | Loaded from nflreadpy by `src/pipeline.py:128`; read by `src/materialize.py:35`, `src/materialize.py:293`, and `src/materialize.py:1271`. | Not safe directly. |
| `weekly_metrics` | raw/source | Loaded by `src/pipeline.py:137`; read by UI at `app.py:814` and `app.py:3150`; read by mart builder at `src/materialize.py:280`. | Not safe directly. |
| `team_descriptions` | raw/source | Loaded by `src/pipeline.py:146`; replicated by `src/transform.py:83-101`; exposed in prompt at `app.py:2684`. | Not safe directly. |
| `draft_picks` | raw/source | Loaded by `src/pipeline.py:155`; extracted in `src/extract.py:162-168`; filtered by `src/transform.py:107-126`. | Not currently UI-facing. |
| `player_rosters` | raw/source | Loaded by `src/pipeline.py:164`; read directly in Player Profiles at `app.py:1095` and `app.py:1116`; read in marts at `src/materialize.py:224`, `src/materialize.py:714`, and `src/materialize.py:754`. | Not safe directly. |
| `player_contracts` | raw/source | Loaded by `src/pipeline.py:173`; read directly by Player Profiles at `app.py:1165`. | Not safe directly. |
| `ngs_passing` | raw/source | Loaded by `src/pipeline.py:178`; exposed in prompt at `app.py:2638`. | Not safe directly. |
| `ngs_rushing` | raw/source | Loaded by `src/pipeline.py:179`; exposed in prompt at `app.py:2673`. | Not safe directly. |
| `ngs_receiving` | raw/source | Loaded by `src/pipeline.py:180`; read by `src/materialize.py:150`; exposed in prompt at `app.py:2675`. | Not safe directly. |
| `ftn_charting` | raw/source | Loaded by `src/pipeline.py:181`; exposed in prompt at `app.py:2677`. | Not safe directly. |
| `weekly_snap_counts` | raw/source | Loaded by `src/pipeline.py:184`; read by `src/materialize.py:123`; exposed in prompt at `app.py:2679`. | Not safe directly. |
| `injury_reports` | raw/source | Loaded by `src/pipeline.py:185`; read by `src/materialize.py:177`; exposed in prompt at `app.py:2681`. | Not safe directly. |
| `depth_charts` | raw/source | Loaded by `src/pipeline.py:188`; read directly by Player Profiles at `app.py:1180`. | Not safe directly. |
| `sleeper_players_current` | staging | Current Sleeper player snapshot written by `src/ingest_news.py:139-161`; read by ranking candidates at `src/materialize.py:718` and `src/materialize.py:736`. | Safe only behind identity/ranking marts. |
| `realtime_player_news` | staging | Sleeper add/drop snapshot written by `src/ingest_news.py:179-185`; read by `src/materialize.py:201`. | Safe only as signal after wrapping. |
| `sleeper_leagues` | raw/source | Schema in `src/ingest_sleeper_league.py:18`; rows assembled at `src/ingest_sleeper_league.py:312`; prompt reference at `app.py:2656`. | Not safe directly. |
| `sleeper_league_users` | raw/source | Schema in `src/ingest_sleeper_league.py:24`; rows assembled at `src/ingest_sleeper_league.py:313`; prompt reference at `app.py:2656`. | Not safe directly. |
| `sleeper_rosters` | raw/source | Schema in `src/ingest_sleeper_league.py:29`; rows assembled at `src/ingest_sleeper_league.py:314`; read directly at `app.py:806` and `app.py:845`. | Not safe directly. |
| `sleeper_roster_players` | raw/source | Schema in `src/ingest_sleeper_league.py:37`; rows assembled at `src/ingest_sleeper_league.py:315`; read directly at `app.py:839`, `app.py:3438`, and `app.py:3481`. | Not safe directly. |
| `sleeper_matchups` | raw/source | Schema in `src/ingest_sleeper_league.py:44`; rows assembled at `src/ingest_sleeper_league.py:316`; prompt reference at `app.py:2656`. | Not safe directly. |
| `sleeper_lineups` | raw/source | Schema in `src/ingest_sleeper_league.py:49`; rows assembled at `src/ingest_sleeper_league.py:317`; read directly at `app.py:3483`. | Not safe directly. |
| `sleeper_available_players` | raw/source | Schema in `src/ingest_sleeper_league.py:56`; rows assembled at `src/ingest_sleeper_league.py:318`; read directly at `app.py:3509` and `app.py:3549`. | Not safe directly. |
| `sleeper_viewer_team_snapshots` | staging | Schema in `src/ingest_sleeper_league.py:62`; rows assembled at `src/ingest_sleeper_league.py:319`; read directly at `app.py:3420`. | Not safe directly. |
| `market_values` | staging | FantasyCalc table recreated by `src/fetch_market_values.py:67-97`; legacy direct UI debt remains in `app.py:2761-2769`; controlled mart read exists in `src/materialize_trade_assets.py`. | Not safe directly. |
| `college_player_stats` | raw/source | Schema in `src/setup_college_tables.py:14-29`; loaded by `src/ingest_college_data.py:133-172`; read directly at `app.py:1198`. | Not safe directly. |
| `rookie_scouting_metrics` | staging | Schema in `src/setup_college_tables.py:32-49`; loaded from UI CSV at `app.py:4018-4023`; read directly at `app.py:1213`. | Not safe directly. |
| `analytics_context_events` | feature-like mart | Curated context loaded by `src/ingest_context_events.py:62-69`; prompt guidance at `app.py:2719-2733`. | Safe if source status is labeled. |
| `analytics_external_context_search_results` | feature-like mart | Created and loaded by `src/verify_player_context.py:63-81` and `src/verify_player_context.py:283-287`; read by Trade Lab at `app.py:3161`. | Safe as stored search leads, not final truth. |
| `analytics_api_usage_daily` | admin metadata | Created/read/merged by `src/verify_player_context.py:53`, `src/verify_player_context.py:89`, and `src/verify_player_context.py:106`. | Admin only. |
| `analytics_game_environment` | feature-like mart | Built from `play_by_play` by `src/materialize.py:16-105`; prompt guidance at `app.py:2717`. | Safe. |
| `analytics_player_qb_weekly` | feature-like mart | Built from `play_by_play` by `src/materialize.py:1249-1348`; read by `analytics_player_weekly_truth` at `src/materialize.py:253`. | Safe with sample caveat. |
| `analytics_player_qb_splits` | feature-like mart | Built from `analytics_player_qb_weekly` by `src/materialize.py:1350-1395`; prompt guidance at `app.py:2716`. | Safe with sample caveat. |
| `analytics_player_weekly_truth` | feature-like mart | Built by `src/materialize.py:274`; read throughout UI and mart code, including `app.py:802`, `app.py:1124`, `app.py:1359`, `app.py:3457`, and `src/materialize.py:646`. | Safe current default table. |
| `analytics_fraud_watch` | output | Built by `src/materialize.py:591-704`; read by `app.py:737`, `app.py:740`, and `app.py:762`. | Safe show output. |
| `analytics_pigskin_rankings_candidates` | feature-like mart | Built by `src/materialize.py:703-1142`; read by ranking generator at `src/generate_pigskin_rankings.py:49`. | Safe for backend ranking evidence, not final ranking truth. |
| `analytics_pigskin_rankings` | output | Written by `src/generate_pigskin_rankings.py`; read by Player Profiles at `app.py:1325` and prompt at `app.py:2589`. | Safe canonical ranking output. New rows include `model_run_id`; older rows may be NULL. |
| `analytics_pigskin_rankings_history` | output | Written by `src/materialize.py:1146-1241` and `src/generate_pigskin_rankings.py`; prompt reference at `app.py:2598`. | Safe historical ranking output. New rows include `model_run_id`; older rows may be NULL. |
| `player_identity_bridge` | feature-like mart | Created by `0005__player_identity_bridge.sql`; materialized by `src/build_player_identity.py`. Canonical bridge across nflverse, Sleeper, Pigskin, market, and roster sources. | Safe identity foundation for marts. |
| `dim_players_current` | feature-like mart | Created by `0005__player_identity_bridge.sql`; derived from `player_identity_bridge` by `src/build_player_identity.py`. | Safe current player dimension. |
| `player_identity_overrides` | admin metadata | Created by `0005__player_identity_bridge.sql`; used by `src/build_player_identity.py` so manual corrections win over automated matches. | Admin only. |
| `analytics_player_fantasy_points_by_profile` | feature-like mart | Created by `0006__scoring_profile_fantasy_points.sql`; materialized by `src/materialize_fantasy_points.py` from `analytics_player_weekly_truth` when available. | Safe scoring foundation for downstream marts. |
| `mart_player_profiles_current` | feature-like mart | Created by `0008__promote_compat_player_profiles_current.sql`; materialized by `src/materialize_player_profiles.py`. Uses identity, scoring, weekly truth, rankings, and optional controlled profile-source summaries. | Safe backing mart for Player Profiles after materialization. |
| `compat_player_profiles_current` | feature-like mart | Created by `0008__promote_compat_player_profiles_current.sql`; helper access lives in `src/player_profiles.py`. View over `mart_player_profiles_current`. | Safe Player Profiles contract after feature-flagged app wiring. Does not expose raw profile source tables. |
| `mart_llm_player_context_packet` | output | Created by `0009__build_llm_player_context_packet.sql`; materialized by `src/materialize_llm_packets.py`. Uses promoted compatibility objects and allowed analytics outputs. | Safe packet backing table for Pigskin and writing-AI context after materialization. |
| `llm_player_context_packet` | output | Created by `0009__build_llm_player_context_packet.sql`; helper access lives in `src/llm_context_packets.py`. View over `mart_llm_player_context_packet`. | Safe LLM packet contract after feature-flagged chat wiring. Does not expose raw source tables. |
| `compat_trade_player_history` | feature-like mart | Created by `0007__promote_compat_trade_player_history.sql`; helper access lives in `src/trade_history.py`. Uses scoring-profile fantasy points, weekly truth, identity, Pigskin rankings, and game environment. | Safe Trade Lab history contract after feature-flagged app wiring. Does not expose raw `weekly_metrics`. |
| `mart_trade_assets_current` | feature-like mart | Created by `0010__promote_compat_trade_assets_current.sql`; materialized by `src/materialize_trade_assets.py` from controlled market, identity, ranking, recent history, and fraud context sources. | Safe backing mart for Trade Lab assets after materialization. |
| `compat_trade_assets_current` | feature-like mart | Created by `0010__promote_compat_trade_assets_current.sql`; helper access lives in `src/trade_assets.py`. View over `mart_trade_assets_current`. | Safe Trade Lab asset contract after feature-flagged app wiring. |
| `trade_review_requests` | admin metadata | Created by `0016__create_trade_review_packets.sql`; written by `src/trade_review_packets.py` when packets are saved. | Safe request ledger. Not wired to Streamlit. |
| `trade_review_packets` | output | Created by `0016__create_trade_review_packets.sql`; deterministic packets are built and saved by `src/trade_review_packets.py`. | Safe Trade Review packet output for future Trade Lab, Pigskin, and show-writing tools. |
| `trade_review_packet_players` | output | Created by `0016__create_trade_review_packets.sql`; one evidence row per side asset. | Safe player-level trade evidence output. |
| `fraud_watch_packets` | output | Created by `0017__create_fraud_breakout_packets.sql`; deterministic packets are built and saved by `src/segment_packets.py` from curated Fraud Watch and compatibility objects. | Safe Fraud Watch packet output for future Segment, Pigskin, and show-writing tools. Not wired to Streamlit. |
| `sleeper_breakout_packets` | output | Created by `0017__create_fraud_breakout_packets.sql`; deterministic packets are built and saved by `src/segment_packets.py` from `compat_sleeper_watch_candidates`. | Safe Sleeper Breakout packet output for future Segment, Pigskin, and show-writing tools. Not wired to Streamlit. |
| `projections_player_weekly` | output | Created by `0018__create_projection_outputs.sql`; deterministic rows are built and saved by `src/projection_engine.py`. | Safe versioned weekly projection output. Not wired to Streamlit. |
| `projections_player_ros` | output | Created by `0018__create_projection_outputs.sql`; deterministic rows are built and saved by `src/projection_engine.py`. | Safe versioned rest-of-season projection output. Not wired to Streamlit. |
| `projections_player_dynasty` | output | Created by `0018__create_projection_outputs.sql`; deterministic rows are built and saved by `src/projection_engine.py`. | Safe versioned dynasty projection output. Not wired to Streamlit. |
| `projection_rankings_current` | output | Created by `0018__create_projection_outputs.sql`; ranking rows are built by `src/projection_engine.py` from projection outputs. | Safe projection ranking output. Does not replace Pigskin rankings UI yet. |
| `mart_sleeper_watch_candidates` | feature-like mart | Created or extended by `0011__promote_compat_sleeper_watch_candidates.sql`; materialized by `src/materialize_sleeper_watch.py` from safe analytics marts and controlled Sleeper snapshots. | Safe backing mart for Sleeper Watch after materialization. |
| `compat_sleeper_watch_candidates` | feature-like mart | Created by `0011__promote_compat_sleeper_watch_candidates.sql`; helper access lives in `src/sleeper_watch.py`. View over `mart_sleeper_watch_candidates`. | Safe Sleeper Watch contract after feature-flagged app wiring. |
| `mart_viewer_team_context` | output | Created by `0012__promote_compat_viewer_team_context.sql` and extended by `0014__extend_compat_viewer_team_context_packet.sql`; materialized by `src/materialize_viewer_team_context.py` from controlled Sleeper snapshots and compatibility marts. | Safe backing packet mart for Viewer Team Lab after materialization. Legacy rows may remain until cleanup. |
| `compat_viewer_team_context` | output | Created by `0014__extend_compat_viewer_team_context_packet.sql` and filtered by `0015__filter_compat_viewer_team_context_packets.sql`; helper access lives in `src/viewer_team_context.py`. View over `mart_viewer_team_context`. | Safe viewer-team packet contract after feature-flagged app wiring. Exposes only rows with `packet_json IS NOT NULL`. |
| `model_runs` | admin metadata | Created by `0002__create_model_runs.sql` and extended by `0003__model_run_config_foundation.sql`; helper writes and reads live in `src/model_runs.py:46`, `src/model_runs.py:100`, `src/model_runs.py:125`, `src/model_runs.py:153`, and `src/model_runs.py:175`. | Safe lineage metadata. |
| `scoring_profiles` | admin metadata | Created and seeded idempotently by `0003__model_run_config_foundation.sql`. | Safe config metadata. |
| `league_types` | admin metadata | Created and seeded idempotently by `0003__model_run_config_foundation.sql`. | Safe config metadata. |
| `roster_formats` | admin metadata | Created and seeded idempotently by `0003__model_run_config_foundation.sql`. | Safe config metadata. |
| `feature_config_versions` | admin metadata | Created by `0003__model_run_config_foundation.sql` for future versioned feature configs. | Safe config metadata. |
| `source_freshness_snapshots` | admin metadata | Created by `0003__model_run_config_foundation.sql`; helper writer is `src/model_runs.py:create_source_freshness_snapshot`, `src/model_runs.py:218`. | Safe lineage metadata. |
| `active_league_rosters` | deprecated/unknown | Prompt reference only at `app.py:2623`; no writer found in `app.py` or `src/`. | Not safe. |
| `historical_player_metrics` | deprecated/unknown | Prompt alias text at `app.py:2606`; no writer found in `app.py` or `src/`. | Not safe. |

## Compatibility Classification

Tables that can remain visible to UI/LLM during the transition:

- `analytics_player_weekly_truth`
- `analytics_fraud_watch`
- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_history`
- `analytics_game_environment`
- `analytics_player_qb_weekly`
- `analytics_player_qb_splits`
- `analytics_context_events`
- `analytics_external_context_search_results`, with source caveat
- `player_identity_bridge`
- `dim_players_current`
- `analytics_player_fantasy_points_by_profile`
- `mart_player_profiles_current`
- `compat_player_profiles_current`
- `mart_llm_player_context_packet`
- `llm_player_context_packet`
- `compat_trade_player_history`
- `mart_trade_assets_current`
- `compat_trade_assets_current`
- `trade_review_packets`
- `trade_review_packet_players`
- `fraud_watch_packets`
- `sleeper_breakout_packets`
- `projections_player_weekly`
- `projections_player_ros`
- `projections_player_dynasty`
- `projection_rankings_current`

Tables that should be hidden behind compatibility marts before new UI work:

- `weekly_metrics`
- `player_rosters`
- `player_contracts`
- `depth_charts`
- `market_values`
- `college_player_stats`
- `rookie_scouting_metrics`
- all `sleeper_*` source snapshot tables
- all raw nflreadpy source tables

Tables to remove from Pigskin schema text:

- `active_league_rosters`
- `historical_player_metrics`

## Prioritized Migration-Debt List

1. P0: Create `model_runs` and add `model_run_id` to ranking outputs.
2. P0: Materialize `player_identity_bridge` and migrate joins away from names.
3. P0: Materialize `analytics_player_fantasy_points_by_profile` and deploy `compat_trade_player_history`.
4. P0: Replace direct `weekly_metrics` reads in `app.py:814` and wire `app.py:3150` to `compat_trade_player_history` under a default-off flag.
5. P0: Validate `trade_review_packets` and use them as the future Trade Lab/Pigskin trade-review output contract.
5. P0: Remove prompt references to `active_league_rosters`, `historical_player_metrics`, `weekly_metrics`, and `play_by_play`.
6. P1: Wire Player Profiles to `compat_player_profiles_current` under a default-off flag after mart validation passes.
7. P1: Replace Pigskin arbitrary SQL with `llm_player_context_packet` helper calls behind a default-off flag.
8. P1: Replace Viewer Team Lab raw joins with `compat_viewer_team_context` behind `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`.
9. P1: Replace raw Sleeper reads with compatibility marts. Sleeper Watch now has `compat_sleeper_watch_candidates`, but Streamlit wiring remains pending.
10. P1: Validate and wire `fraud_watch_packets` and `sleeper_breakout_packets` behind default-off segment and Pigskin context flags.
11. P1: Generate and backtest projection outputs before wiring them into rankings, trade, viewer-team, segment, or Pigskin consumers.
12. P2: Add partitioning or replacement marts for append-only Sleeper snapshots.
