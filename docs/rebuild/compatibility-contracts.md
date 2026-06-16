# Compatibility Contracts

This document indexes the compatibility-contract layer created from the rebuild audit.

Most contracts are documentation and placeholder DDL only. `compat_trade_player_history`, `compat_player_profiles_current`, `compat_sleeper_watch_candidates`, `compat_trade_assets_current`, `compat_viewer_team_context`, `llm_player_context_packet`, trade review packet tables, and segment packet tables have been promoted to production compatibility objects. Selected Streamlit reads are now wired behind default-off compatibility flags. Default runtime behavior is unchanged.

Streamlit rollout details live in [docs/rebuild/streamlit-compat-rollout.md](streamlit-compat-rollout.md).

## Contract Index

| Object | Contract | Placeholder SQL | Replaces |
| --- | --- | --- | --- |
| `compat_player_profiles_current` | [contract](../../bigquery/contracts/compat_player_profiles_current.md) | [view](../../bigquery/views/compat_player_profiles_current.sql), [migration](../../bigquery/migrations/0008__promote_compat_player_profiles_current.sql) | `fetch_player_profiles_data`, `app.py:1090-1275` |
| `compat_sleeper_watch_candidates` | [contract](../../bigquery/contracts/compat_sleeper_watch_candidates.md) | [view](../../bigquery/views/compat_sleeper_watch_candidates.sql), [migration](../../bigquery/migrations/0011__promote_compat_sleeper_watch_candidates.sql) | `render_sleeper_watch_segment`, `app.py:788-918` |
| `compat_trade_assets_current` | [contract](../../bigquery/contracts/compat_trade_assets_current.md) | [view](../../bigquery/views/compat_trade_assets_current.sql), [migration](../../bigquery/migrations/0010__promote_compat_trade_assets_current.sql) | `render_value_analyzer.load_market_players`, `app.py:2761-2769` |
| `compat_trade_player_history` | [contract](../../bigquery/contracts/compat_trade_player_history.md) | [view](../../bigquery/views/compat_trade_player_history.sql), [migration](../../bigquery/migrations/0007__promote_compat_trade_player_history.sql) | `render_value_analyzer.query_player_history`, `app.py:3147-3155` |
| `compat_viewer_team_context` | [contract](../../bigquery/contracts/compat_viewer_team_context.md) | [view](../../bigquery/views/compat_viewer_team_context.sql), [migration](../../bigquery/migrations/0014__extend_compat_viewer_team_context_packet.sql), [migration](../../bigquery/migrations/0015__filter_compat_viewer_team_context_packets.sql) | `get_sleeper_viewer_team_context`, `app.py:3390-3570` |
| `llm_player_context_packet` | [contract](../../bigquery/contracts/llm_player_context_packet.md) | [view](../../bigquery/views/llm_player_context_packet.sql), [migration](../../bigquery/migrations/0009__build_llm_player_context_packet.sql) | Pigskin SQL tool path, `app.py:2525-2796` |
| `analytics_pigskin_rankings` and `analytics_pigskin_rankings_history` | [contract](../../bigquery/contracts/analytics_pigskin_rankings.md) | [migration](../../bigquery/migrations/0004__add_model_run_id_to_pigskin_rankings.sql) | current and historical Pigskin ranking outputs |
| `player_identity_bridge` | [contract](../../bigquery/contracts/player_identity_bridge.md) | [migration](../../bigquery/migrations/0005__player_identity_bridge.sql) | canonical player ID bridge for future marts |
| `dim_players_current` | [contract](../../bigquery/contracts/dim_players_current.md) | [migration](../../bigquery/migrations/0005__player_identity_bridge.sql) | current player dimension for UI and evidence packets |
| `player_identity_overrides` | [contract](../../bigquery/contracts/player_identity_overrides.md) | [migration](../../bigquery/migrations/0005__player_identity_bridge.sql) | manual player identity corrections |
| `analytics_player_fantasy_points_by_profile` | [contract](../../bigquery/contracts/analytics_player_fantasy_points_by_profile.md) | [migration](../../bigquery/migrations/0006__scoring_profile_fantasy_points.sql) | scoring-profile-aware player-week fantasy point output |
| `model_runs` | [contract](../../bigquery/contracts/model_runs.md) | [migration](../../bigquery/migrations/0002__create_model_runs.sql) | future ranking/projection run metadata |
| `scoring_profiles` | [contract](../../bigquery/contracts/scoring_profiles.md) | [migration](../../bigquery/migrations/0003__model_run_config_foundation.sql) | scoring context for generated outputs |
| `league_types` | [contract](../../bigquery/contracts/league_types.md) | [migration](../../bigquery/migrations/0003__model_run_config_foundation.sql) | league context for generated outputs |
| `roster_formats` | [contract](../../bigquery/contracts/roster_formats.md) | [migration](../../bigquery/migrations/0003__model_run_config_foundation.sql) | roster context for generated outputs |
| `feature_config_versions` | [contract](../../bigquery/contracts/feature_config_versions.md) | [migration](../../bigquery/migrations/0003__model_run_config_foundation.sql) | versioned feature and weighting configs |
| `source_freshness_snapshots` | [contract](../../bigquery/contracts/source_freshness_snapshots.md) | [migration](../../bigquery/migrations/0003__model_run_config_foundation.sql) | source freshness lineage for model runs |
| `trade_review_requests` | [contract](../../bigquery/contracts/trade_review_requests.md) | [migration](../../bigquery/migrations/0016__create_trade_review_packets.sql) | future Trade Lab and Pigskin trade review request ledger |
| `trade_review_packets` | [contract](../../bigquery/contracts/trade_review_packets.md) | [migration](../../bigquery/migrations/0016__create_trade_review_packets.sql) | future deterministic trade review packet output |
| `trade_review_packet_players` | [contract](../../bigquery/contracts/trade_review_packet_players.md) | [migration](../../bigquery/migrations/0016__create_trade_review_packets.sql) | player-level evidence rows for trade packets |
| `fraud_watch_packets` | [contract](../../bigquery/contracts/fraud_watch_packets.md) | [migration](../../bigquery/migrations/0017__create_fraud_breakout_packets.sql) | future deterministic Fraud Watch packet output |
| `sleeper_breakout_packets` | [contract](../../bigquery/contracts/sleeper_breakout_packets.md) | [migration](../../bigquery/migrations/0017__create_fraud_breakout_packets.sql) | future deterministic Sleeper Breakout packet output |
| `projections_player_weekly` | [contract](../../bigquery/contracts/projections_player_weekly.md) | [migration](../../bigquery/migrations/0018__create_projection_outputs.sql) | versioned weekly projection output |
| `projections_player_ros` | [contract](../../bigquery/contracts/projections_player_ros.md) | [migration](../../bigquery/migrations/0018__create_projection_outputs.sql) | versioned rest-of-season projection output |
| `projections_player_dynasty` | [contract](../../bigquery/contracts/projections_player_dynasty.md) | [migration](../../bigquery/migrations/0018__create_projection_outputs.sql) | versioned dynasty projection output |
| `projection_rankings_current` | [contract](../../bigquery/contracts/projection_rankings_current.md) | [migration](../../bigquery/migrations/0018__create_projection_outputs.sql) | current projection ranking output by horizon |
| `backtest_runs` | [contract](../../bigquery/contracts/backtest_runs.md) | [migration](../../bigquery/migrations/0020__create_backtest_framework.sql) | deterministic projection backtest run ledger |
| `backtest_result_player_week` | [contract](../../bigquery/contracts/backtest_result_player_week.md) | [migration](../../bigquery/migrations/0020__create_backtest_framework.sql) | player-week projection error output |
| `backtest_result_summary` | [contract](../../bigquery/contracts/backtest_result_summary.md) | [migration](../../bigquery/migrations/0020__create_backtest_framework.sql) | aggregate projection quality output |
| `backtest_calibration_bins` | [contract](../../bigquery/contracts/backtest_calibration_bins.md) | [migration](../../bigquery/migrations/0020__create_backtest_framework.sql) | projected-point calibration output |
| `market_consensus_sources` | [contract](../../bigquery/contracts/market_consensus_sources.md) | [migration](../../bigquery/migrations/0021__create_market_consensus_baselines.sql) | source registry for market and consensus baselines |
| `market_consensus_snapshots` | [contract](../../bigquery/contracts/market_consensus_snapshots.md) | [migration](../../bigquery/migrations/0021__create_market_consensus_baselines.sql) | imported baseline snapshot ledger |
| `market_consensus_player_values` | [contract](../../bigquery/contracts/market_consensus_player_values.md) | [migration](../../bigquery/migrations/0021__create_market_consensus_baselines.sql) | normalized player-level market baseline rows |
| `market_consensus_baseline_current` | [contract](../../bigquery/contracts/market_consensus_baseline_current.md) | [migration](../../bigquery/migrations/0021__create_market_consensus_baselines.sql) | current market baseline rows for backtests |
| `claim_sources` | [contract](../../bigquery/contracts/claim_sources.md) | [migration](../../bigquery/migrations/0022__create_meatbag_claim_ledger.sql) | manual source registry for Meatbag claims |
| `fantasy_claims` | [contract](../../bigquery/contracts/fantasy_claims.md) | [migration](../../bigquery/migrations/0022__create_meatbag_claim_ledger.sql) | manual claim ledger for future grading |
| `fantasy_claim_players` | [contract](../../bigquery/contracts/fantasy_claim_players.md) | [migration](../../bigquery/migrations/0022__create_meatbag_claim_ledger.sql) | player-level participants for claims |
| `claim_evaluation_windows` | [contract](../../bigquery/contracts/claim_evaluation_windows.md) | [migration](../../bigquery/migrations/0022__create_meatbag_claim_ledger.sql) | grading window metadata for claims |
| `claim_grading_runs` | [contract](../../bigquery/contracts/claim_grading_runs.md) | [migration](../../bigquery/migrations/0023__create_claim_grading.sql) | deterministic claim grading run ledger |
| `claim_grades` | [contract](../../bigquery/contracts/claim_grades.md) | [migration](../../bigquery/migrations/0023__create_claim_grading.sql) | one deterministic grade per claim per run |
| `claim_source_scorecards` | [contract](../../bigquery/contracts/claim_source_scorecards.md) | [migration](../../bigquery/migrations/0023__create_claim_grading.sql) | source-level accountability scoreboards |
| `content_brief_runs` | [contract](../../bigquery/contracts/content_brief_runs.md) | [migration](../../bigquery/migrations/0024__create_content_briefs.sql) | deterministic show brief run ledger |
| `content_briefs` | [contract](../../bigquery/contracts/content_briefs.md) | [migration](../../bigquery/migrations/0024__create_content_briefs.sql) | compact show-ready content briefs |
| `content_brief_items` | [contract](../../bigquery/contracts/content_brief_items.md) | [migration](../../bigquery/migrations/0024__create_content_briefs.sql) | ordered evidence items inside each brief |

## Compatibility Rules

1. Existing tables are not renamed.
2. Current Streamlit behavior is unchanged unless a default-off compatibility flag is explicitly enabled.
3. Compatibility objects should hide raw/source tables from the UI and LLM.
4. `ranking_version` remains available until the UI fully migrates to `model_run_id`.
5. Every compatibility object must include `source_freshness_json` or a TODO placeholder.
6. Every compatibility object must include `missing_data_flags` or a TODO placeholder.
7. Temporary nulls are acceptable only when they are clearly flagged.
8. Do not introduce fragile name joins unless the output explicitly flags them as temporary.

## Placeholder Status

`compat_player_profiles_current` is now promoted to a production compatibility object.

It uses a backing table:

- `mart_player_profiles_current`

The mart is refreshed by [src/materialize_player_profiles.py](../../src/materialize_player_profiles.py). It uses:

- `dim_players_current`
- `player_identity_bridge`
- `analytics_player_weekly_truth`
- `analytics_player_fantasy_points_by_profile`
- `analytics_pigskin_rankings`
- optional controlled materializer reads from `player_contracts`, `depth_charts`, `college_player_stats`, and `rookie_scouting_metrics`

It does not expose raw profile source rows to the UI or Pigskin. Runtime wiring into Player Profiles is available behind `USE_COMPAT_PLAYER_PROFILES=false`.

`compat_sleeper_watch_candidates` is now promoted to a production compatibility object.

It uses a backing table:

- `mart_sleeper_watch_candidates`

The mart is refreshed by [src/materialize_sleeper_watch.py](../../src/materialize_sleeper_watch.py). It uses:

- `analytics_player_weekly_truth`
- `analytics_player_fantasy_points_by_profile`
- `analytics_pigskin_rankings`
- `analytics_fraud_watch`
- `analytics_game_environment`
- `dim_players_current`
- `player_identity_bridge`
- Sleeper snapshots only inside the controlled materializer layer
- `realtime_player_news`

Helper access lives in [src/sleeper_watch.py](../../src/sleeper_watch.py). Streamlit wiring is available behind `USE_COMPAT_SLEEPER_WATCH=false`.

The compatibility view does not expose direct raw `weekly_metrics`, `sleeper_rosters`, or `sleeper_roster_players` access to UI or Pigskin.

`compat_trade_assets_current` is now promoted to a production compatibility object.

It uses a backing table:

- `mart_trade_assets_current`

The mart is refreshed by [src/materialize_trade_assets.py](../../src/materialize_trade_assets.py). It uses:

- `market_values`, only inside the controlled mart-building layer
- `dim_players_current`
- `player_identity_bridge`
- `analytics_pigskin_rankings`
- `compat_trade_player_history`
- `analytics_fraud_watch`

Helper access lives in [src/trade_assets.py](../../src/trade_assets.py). Streamlit wiring is available behind `USE_COMPAT_TRADE_ASSETS=false`.

The compatibility view does not expose direct raw `market_values` access to UI or Pigskin.

`compat_trade_player_history` is now promoted to a production compatibility view.

It uses:

- `analytics_player_fantasy_points_by_profile`
- `analytics_player_weekly_truth`
- `player_identity_bridge`
- `analytics_pigskin_rankings`
- `analytics_game_environment`

It does not expose raw `weekly_metrics`. Runtime wiring into Trade Lab history is available behind `USE_COMPAT_TRADE_PLAYER_HISTORY=false`.

`compat_viewer_team_context` is now promoted to a production compatibility object.

It uses a backing table:

- `mart_viewer_team_context`

The mart is refreshed by [src/materialize_viewer_team_context.py](../../src/materialize_viewer_team_context.py). It uses raw Sleeper snapshots and the current Sleeper player map only inside the controlled materializer layer, then enriches roster packets with:

- `dim_players_current`
- `player_identity_bridge`
- `analytics_pigskin_rankings`
- `compat_trade_assets_current`
- `compat_sleeper_watch_candidates`
- `compat_player_profiles_current`
- `compat_trade_player_history`
- `llm_player_context_packet`

Helper access lives in [src/viewer_team_context.py](../../src/viewer_team_context.py). Streamlit wiring is available behind `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`.

The compatibility view only exposes materialized packet rows where `packet_json IS NOT NULL`; older legacy rows can remain in the backing mart until a future cleanup migration.

The compatibility view does not expose direct raw Sleeper snapshot access to UI or Pigskin.

`llm_player_context_packet` is now promoted to a production compatibility object.

It uses a backing table:

- `mart_llm_player_context_packet`

The mart is refreshed by [src/materialize_llm_packets.py](../../src/materialize_llm_packets.py). It uses:

- `compat_player_profiles_current`
- `compat_trade_player_history`
- `model_runs`
- optional allowed context marts including fraud watch, ranking history, QB splits, context events, and external context leads

It does not read raw/source tables directly. Runtime wiring into Pigskin chat is still pending and should be feature-flagged with the default set to off.

Trade review packet infrastructure is now documented:

- `trade_review_requests` records the requested sides and scoring context.
- `trade_review_packets` stores deterministic verdict, evidence, counterarguments, source freshness, and show framing.
- `trade_review_packet_players` stores one player evidence row per trade side.
- The helper lives in [src/trade_review_packets.py](../../src/trade_review_packets.py).

The helper reads only curated compatibility objects:

- `compat_trade_assets_current`
- `compat_trade_player_history`
- `compat_player_profiles_current`

It does not call the LLM, does not wire Streamlit, and does not expose raw market, raw weekly, or raw Sleeper sources.

Segment packet infrastructure is now documented:

- `fraud_watch_packets` stores deterministic Fraud Watch claims, evidence, counterarguments, source freshness, missing flags, and show framing.
- `sleeper_breakout_packets` stores deterministic Sleeper Breakout claims, role-growth evidence, counterarguments, source freshness, missing flags, and show framing.
- The helper lives in [src/segment_packets.py](../../src/segment_packets.py).

The helper reads only curated compatibility objects:

- `analytics_fraud_watch`
- `compat_trade_assets_current`
- `compat_player_profiles_current`
- `compat_sleeper_watch_candidates`
- `model_runs`

It does not call the LLM, does not wire Streamlit, and does not expose raw weekly, play, NGS, FTN, snap, injury, or raw Sleeper sources.

Projection output infrastructure is now documented:

- `projections_player_weekly` stores versioned deterministic weekly projections.
- `projections_player_ros` stores versioned deterministic rest-of-season projections.
- `projections_player_dynasty` stores versioned deterministic dynasty values.
- `projection_rankings_current` stores generated ranks by projection horizon and context.
- The helper lives in [src/projection_engine.py](../../src/projection_engine.py).
- The operating model is documented in [docs/rebuild/projection-engine-v1.md](projection-engine-v1.md).

The helper reads only curated compatibility objects and packet outputs. It does not call the LLM, does not wire Streamlit, and does not expose raw weekly, play, NGS, FTN, snap, injury, or raw Sleeper sources.

Meatbag Claim Ledger infrastructure is now documented:

- `claim_sources` stores manual source metadata.
- `fantasy_claims` stores claim-level text, context, source, horizon, and model or market snapshot fields.
- `fantasy_claim_players` stores player-level claim participants resolved through `player_identity_bridge` when possible.
- `claim_evaluation_windows` stores the future grading window for each claim.
- The helper lives in [src/claim_ledger.py](../../src/claim_ledger.py).
- The operating model is documented in [docs/rebuild/meatbag-claim-ledger.md](meatbag-claim-ledger.md).

The helper is manual-entry only. It does not call the LLM, scrape media, wire Streamlit, or expose Pigskin SQL access.

Claim Grading V1 infrastructure is now documented:

- `claim_grading_runs` stores one run row per grading execution.
- `claim_grades` stores deterministic claim-level outcomes.
- `claim_source_scorecards` stores accountability summaries by source.
- The helper lives in [src/claim_grading.py](../../src/claim_grading.py).
- The operating model is documented in [docs/rebuild/claim-grading-v1.md](claim-grading-v1.md).

The helper reads only curated outputs and marts. It does not call the LLM, scrape media, wire Streamlit, or expose raw source tables.

Content Brief Orchestrator infrastructure is now documented:

- `content_brief_runs` stores one run row per brief execution.
- `content_briefs` stores compact show prep briefs with bounded text and deterministic writer payloads.
- `content_brief_items` stores ordered item summaries with confidence, evidence, counterarguments, hooks, freshness, and flags.
- The helper lives in [src/content_briefs.py](../../src/content_briefs.py).
- The operating model is documented in [docs/rebuild/content-brief-orchestrator.md](content-brief-orchestrator.md).

The helper reads only curated packets and outputs. It does not call the LLM, wire Streamlit, create Firebase artifacts, or expose source tables.

`model_runs` is a table migration.

It is safe metadata only and does not backfill existing ranking rows.

The config tables added in `0003__model_run_config_foundation.sql` are safe metadata tables. Seed rows are inserted with `MERGE` and are idempotent.

Helper functions live in [src/model_runs.py](../../src/model_runs.py):

- `create_model_run()`
- `mark_model_run_complete()`
- `mark_model_run_failed()`
- `get_model_run()`
- `get_latest_model_run()`
- `create_source_freshness_snapshot()`

They follow the existing project/dataset environment pattern and can be tested with mocked BigQuery clients.

During migration, `ranking_version` remains a display label while `model_run_id` becomes the authoritative lineage key for new generated outputs. Existing rankings are not backfilled by this step.

Pigskin ranking generation now creates a `model_runs` row before LLM adjudication and writes model-run lineage columns into new active and historical ranking rows. Existing pre-migration rows may keep `NULL` `model_run_id`.

Pigskin chat context-tool containment is now in place:

- The prompt tells Pigskin to use named context tools, not SQL.
- Model-visible tool declarations live in [src/pigskin_context_tools.py](../../src/pigskin_context_tools.py).
- Raw/source and deprecated table names are no longer shown to the chat model.
- The legacy SQL guardrail layer still exists for server-side compatibility in [src/bigquery_guardrails.py](../../src/bigquery_guardrails.py), but it is not the chat model interface.
- Runtime wiring into Pigskin chat now uses `llm_player_context_packet`, `analytics_pigskin_rankings`, `analytics_fraud_watch`, `compat_trade_player_history`, `analytics_context_events`, and `analytics_external_context_search_results` through parameterized context tools.

Player identity foundation is now documented:

- `player_identity_bridge` is the canonical cross-source player ID bridge.
- `dim_players_current` is the current player dimension future UI and marts should use.
- `player_identity_overrides` gives active manual corrections priority over automated matching.
- The builder lives in [src/build_player_identity.py](../../src/build_player_identity.py).
- Future compatibility marts should join on `player_id_internal` instead of raw names.

Scoring-profile-aware fantasy points are now documented:

- `analytics_player_fantasy_points_by_profile` stores standard, half-PPR, and PPR player-week outputs by `scoring_profile_id`.
- The scoring engine lives in [src/fantasy_scoring.py](../../src/fantasy_scoring.py).
- The materializer lives in [src/materialize_fantasy_points.py](../../src/materialize_fantasy_points.py).
- Future trade history, player profile, projection, ranking, and evidence-packet marts should consume this table or downstream marts instead of raw `weekly_metrics`.

## Wiring Sequence

1. Apply the migration framework and create `model_runs`.
2. Build or promote `compat_trade_player_history`, because it has the lowest dependency risk.
3. Build `player_identity_bridge`.
4. Build `analytics_player_fantasy_points_by_profile`.
5. Promote `compat_trade_player_history`.
6. Promote `compat_player_profiles_current`.
7. Promote `compat_sleeper_watch_candidates`.
8. Validate and gradually enable `compat_sleeper_watch_candidates` in Sleeper Watch.
9. Validate and gradually enable `compat_trade_assets_current` and `compat_trade_player_history` in Trade Lab.
10. Validate and gradually enable `compat_viewer_team_context` in Viewer Team Lab.
11. Build and validate deterministic `trade_review_packets` before Trade Lab or Pigskin wiring.
12. Build and validate deterministic `fraud_watch_packets` and `sleeper_breakout_packets` before Segment or Pigskin wiring.
13. Build and validate deterministic weekly, ROS, and dynasty projection outputs before replacing any ranking, trade, viewer-team, or segment context.
14. Wire `llm_player_context_packet` into Pigskin behind a default-off flag.
15. Replace Pigskin arbitrary SQL with allowlisted context access.

## Prioritized Migration-Debt List

1. P0: Apply `model_runs` and begin writing `model_run_id` in new generated outputs.
2. P0: Replace Pigskin arbitrary SQL with parameterized `llm_player_context_packet` helper calls behind a default-off flag.
3. P0: Validate and gradually enable Trade Lab history `compat_trade_player_history`.
4. P1: Build player identity and source freshness infrastructure.
5. P1: Validate and gradually enable Player Profiles `compat_player_profiles_current`.
6. P1: Validate and gradually enable Sleeper Watch `compat_sleeper_watch_candidates`.
7. P1: Validate and gradually enable Trade Lab market reads through `compat_trade_assets_current`.
8. P1: Validate and gradually enable Viewer Team Lab `compat_viewer_team_context`.
9. P1: Wire Trade Lab to consume saved `trade_review_packets` only after packet validation and a default-off flag.
10. P1: Wire Segment and Pigskin reads to saved `fraud_watch_packets` and `sleeper_breakout_packets` only after packet validation and default-off flags.
11. P1: Generate and backtest `projections_player_weekly`, `projections_player_ros`, and `projections_player_dynasty` before public confidence claims.
12. P2: Move remaining placeholder compatibility objects to tested production marts where query cost or reliability requires it.
