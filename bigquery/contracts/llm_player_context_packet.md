# llm_player_context_packet Contract

SQL:

- [bigquery/migrations/0009__build_llm_player_context_packet.sql](../migrations/0009__build_llm_player_context_packet.sql)
- [bigquery/views/llm_player_context_packet.sql](../views/llm_player_context_packet.sql)

Materializer:

- [src/materialize_llm_packets.py](../../src/materialize_llm_packets.py)

Helper:

- [src/llm_context_packets.py](../../src/llm_context_packets.py)

## Purpose

Production compatibility layer for Pigskin chat and the future writing AI.

This packet is the future replacement for arbitrary model-generated SQL in `render_ai_cohost`, `app.py:2525-2796`. It gives Pigskin a compact, bounded, source-attributed player evidence packet instead of letting the model inspect raw tables.

`app.py` is not wired to this object by default yet. Current Pigskin chat behavior remains unchanged until a later default-off feature flag migration.

## Backing Object

`llm_player_context_packet` is a view over:

- `mart_llm_player_context_packet`

The backing table is refreshed by `src/materialize_llm_packets.py`.

This mart-backed approach is intentional. LLM context should be precomputed, compact, and bounded instead of assembled from many tables during a chat request.

## Grain

One row per:

- `COALESCE(player_id_internal, source_player_key)`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `model_run_id`
- `as_of_season`
- `as_of_week`

If `model_run_id` is unavailable, the packet keeps `NULL` and records `missing_model_run_id` in `missing_data_flags`.

## Top-Level Fields

- `packet_id`
- `model_run_id`
- `ranking_version`
- `player_id_internal`
- `source_player_key`
- `display_name`
- `position`
- `team`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `as_of_season`
- `as_of_week`
- `packet_json`
- `packet_text`
- `token_estimate`
- `source_freshness_json`
- `missing_data_flags`
- `created_at`
- `updated_at`

`packet_json` is stored as a string for compatibility with the current warehouse conventions.

## Packet JSON Structure

Required packet sections:

- `identity`
- `ranking_context`
- `recent_fantasy_summary`
- `usage_summary`
- `efficiency_summary`
- `game_environment`
- `qb_and_team_context`
- `fraud_watch_context`
- `trade_context`
- `external_context`
- `counterarguments`
- `snark_hooks`
- `source_metadata`

## Source Rules

Allowed construction sources:

- `compat_player_profiles_current`
- `compat_trade_player_history`
- `model_runs`
- `analytics_fraud_watch`
- `analytics_pigskin_rankings_history`
- `analytics_player_qb_splits`
- `analytics_context_events`
- `analytics_external_context_search_results`

The promoted profile and trade compatibility objects already carry:

- identity
- profile-aware scoring
- weekly evidence
- Pigskin ranking context
- game environment context

Disallowed direct packet sources:

- `weekly_metrics`
- `play_by_play`
- `player_rosters`
- `player_contracts`
- `depth_charts`
- `team_descriptions`
- `ngs_passing`
- `ngs_rushing`
- `ngs_receiving`
- `ftn_charting`
- `weekly_snap_counts`
- `injury_reports`
- raw Sleeper snapshot tables

If a disallowed table is needed, do not use it directly. Build or promote a compat object first and record a missing flag until then.

## Size Bounds

- Recent trade/game rows are capped to 8.
- Ranking history rows are capped to 5.
- Fraud context rows are capped to 5.
- QB split rows are capped to 5.
- Context events are capped to 5.
- External leads are capped to 5.
- `packet_text` is capped at 8,000 characters.
- `token_estimate` is computed from `packet_text`.

## Missing Data Rules

Missing evidence must be flagged instead of replaced with generic model knowledge.

Expected flags include:

- `missing_model_run_id`
- `missing_player_id_internal`
- `missing_source_player_key`
- `missing_trade_history_context`
- `missing_fraud_watch_context`
- `missing_qb_context`
- `missing_ranking_history`
- `missing_context_events`
- `missing_external_leads`
- `missing_analytics_fraud_watch_source`
- `missing_analytics_pigskin_rankings_history_source`
- `missing_analytics_player_qb_splits_source`
- `missing_analytics_context_events_source`
- `missing_analytics_external_context_search_results_source`
- `temporary_name_join_external_leads`

External search leads are supporting context only. They are not verified truth by themselves.

## Validation Set

- [035 grain](../validations/035_llm_player_context_packet_grain.sql)
- [036 recent rows exist](../validations/036_llm_player_context_packet_recent_rows_exist.sql)
- [037 no raw source references](../validations/037_llm_player_context_packet_no_raw_source_references.sql)
- [038 required JSON keys](../validations/038_llm_player_context_packet_required_json_keys.sql)
- [039 size bounds](../validations/039_llm_player_context_packet_size_bounds.sql)
- [040 model run join](../validations/040_llm_player_context_packet_model_run_join.sql)
- [041 identity coverage](../validations/041_llm_player_context_packet_identity_coverage.sql)
- [042 missing flags exist](../validations/042_llm_player_context_packet_missing_flags_exist.sql)

## Helper Contract

`src/llm_context_packets.py` exposes:

- `get_player_context_packet()`
- `search_player_context_packets()`
- `get_ranked_context_packets()`
- `normalize_packet_for_llm()`

Rules:

- Query only `llm_player_context_packet`.
- Pass lookup values, scoring profile, league type, roster format, and model run ID as BigQuery parameters.
- Build table identifiers only from trusted project and dataset config.
- Cap limits at `100`.
- Return a clean missing-packet response instead of fabricating context.

## Pigskin Usage

Pigskin should use this packet as the first source for:

- defending rankings
- explaining player profiles
- trade analysis
- fraud watch calls
- segment writing
- counterarguments and confidence caveats

Pigskin should not treat external leads as truth by themselves. The packet explicitly labels those as leads.

## Runtime Status

Not wired into `app.py` by default.

Future chat migration should use a default-off flag such as `USE_LLM_CONTEXT_PACKET=false`, then replace arbitrary SQL with parameterized packet functions after validation.
