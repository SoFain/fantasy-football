# UI Query Debt Register

Source docs:

- [docs/CODEX_PROJECT_CONTEXT.md](../CODEX_PROJECT_CONTEXT.md)
- [docs/rebuild/audit-and-rebuild-plan.md](audit-and-rebuild-plan.md)
- [docs/rebuild/current-warehouse-inventory.md](current-warehouse-inventory.md)
- [docs/rebuild/table-classification.md](table-classification.md)
- [docs/rebuild/cloud-run-operating-model.md](cloud-run-operating-model.md)
- [docs/rebuild/streamlit-compat-rollout.md](streamlit-compat-rollout.md)

Scope: `app.py` BigQuery reads and model paths that can generate or execute SQL. This is documentation only.

Architecture note: future rebuild sprints should follow the Cloud Run operating model. Firebase is not the target architecture unless the project explicitly reopens that decision.

## Current BigQuery Access Pattern

`app.py` accesses BigQuery directly from Streamlit:

- Cached SQL execution helper: `app.py:656-659`.
- SQL repair layer for generated SQL: `app.py:663-697`.
- Direct `client.query` calls in Player Profiles, Trade Lab, Viewer Team Lab, and admin job metadata.
- Pigskin context tool declarations: `src/pigskin_context_tools.py`.

This violates the project context rule that admin panel views should read from precomputed marts or backend APIs, not ad hoc raw-table scans.

## Raw/Source UI Query Debt

| Debt ID | Location | Raw/source tables | Current purpose | Risk | Minimum compatibility target |
| --- | --- | --- | --- | --- | --- |
| UI-001 | `render_sleeper_watch_segment`, `app.py:788-918` | `weekly_metrics`, `sleeper_rosters`, `sleeper_roster_players` | Builds sleeper/streamer board and opponent fantasy points allowed. | Streamlit now has `USE_COMPAT_SLEEPER_WATCH=false` wiring to `src/sleeper_watch.py`. Default behavior is unchanged. The old direct UI query path remains available until live validation promotes the flag. | `compat_sleeper_watch_candidates`, feature-flagged default off. |
| UI-002 | `fetch_player_profiles_data`, `app.py:1090-1275` | `player_rosters`, `player_contracts`, `depth_charts`, `college_player_stats`, `rookie_scouting_metrics` | Builds Player Profiles table by joining raw and feature data. | Streamlit now has `USE_COMPAT_PLAYER_PROFILES=false` wiring to `src/player_profiles.py`. Default behavior is unchanged. The compat branch normalizes contract, depth, college, and scouting JSON into the legacy UI shape. | `compat_player_profiles_current`, feature-flagged default off. |
| UI-003 | `render_value_analyzer.load_market_players`, `app.py:2761-2769` | `market_values` | Loads FantasyCalc assets for Trade Lab. | Streamlit now has `USE_COMPAT_TRADE_ASSETS=false` wiring to `src/trade_assets.py`. Default behavior is unchanged. If the flag is enabled and compat data is empty or unavailable, the view shows a warning before falling back to legacy. | `compat_trade_assets_current`, feature-flagged default off. |
| UI-004 | `render_value_analyzer.query_player_history`, `app.py:3147-3155` | `weekly_metrics` | Provides recent stats for AI trade outlook. | Streamlit now has `USE_COMPAT_TRADE_PLAYER_HISTORY=false` wiring to `src/trade_history.py`. Phase 13.6 selected this as the first staged rollout flag after readiness and validation passed. Production default remains unchanged. If the flag is enabled and compat data fails, the view shows a warning before falling back to legacy. | `compat_trade_player_history`, enable in staging with `USE_COMPAT_TRADE_PLAYER_HISTORY=true`. |
| UI-004A | future Trade Review packet path | none yet | Future Trade Lab/Pigskin should read saved deterministic trade review packets instead of rebuilding trade evidence in Streamlit. | Packet infrastructure exists, but no runtime wiring is enabled. | `trade_review_packets` plus `trade_review_packet_players`, feature-flagged default off. |
| UI-004B | future Fraud Watch packet path | none yet | Future Segment/Pigskin Fraud Watch reads should consume saved deterministic packets instead of rebuilding claims in Streamlit or chat. | Packet infrastructure exists, but no runtime wiring is enabled. | `fraud_watch_packets`, feature-flagged default off. |
| UI-004C | future Sleeper Breakout packet path | none yet | Future Segment/Pigskin breakout reads should consume saved deterministic packets instead of raw Sleeper or weekly scans. | Packet infrastructure exists, but no runtime wiring is enabled. | `sleeper_breakout_packets`, feature-flagged default off. |
| UI-004D | future projection consumers | none yet | Future rankings, trade reviews, viewer-team advice, and show packets should consume versioned projection outputs instead of ad hoc projection math in Streamlit. | Projection output infrastructure exists, but no runtime wiring or backtesting is enabled. | `projections_player_weekly`, `projections_player_ros`, `projections_player_dynasty`, and `projection_rankings_current`, feature-flagged default off. |
| UI-004E | `render_backtest_dashboard`, Phase 13.3 | none | Read-only review of backtest accuracy outputs. | Streamlit now has `USE_BACKTEST_DASHBOARD=false` wiring to `src/backtest_readers.py`. The tab is absent by default and reads only backtest output tables when enabled. | `backtest_runs`, `backtest_result_summary`, `backtest_result_player_week`, `backtest_calibration_bins`. |
| UI-005 | `get_sleeper_viewer_team_context`, `app.py:3390-3570` | `sleeper_viewer_team_snapshots`, `sleeper_roster_players`, `sleeper_lineups`, `sleeper_available_players` | Builds terminal-style viewer-team context. | Streamlit now has `USE_COMPAT_VIEWER_TEAM_CONTEXT=false` wiring to `src/viewer_team_context.py`. Default behavior is unchanged. When the flag is enabled, the console uses only the compatibility packet and does not mix legacy raw joins. | `compat_viewer_team_context`, feature-flagged default off. |
| UI-006 | `render_ai_cohost` Pigskin context tools | Previously exposed `weekly_metrics`, `play_by_play`, NGS, FTN, snap, injury, and team source tables through prompt/schema patterns. | Pigskin chat now receives parameterized context tools instead of a general SQL tool. | Context quality now depends on materialized marts and evidence packets. Missing packets should be surfaced honestly instead of hidden by ad hoc SQL. | Continue expanding `llm_player_context_packet` and tool coverage. |
| UI-007 | `render_ai_cohost` prompt schema | Previously exposed `active_league_rosters`. | Deprecated prompt-only roster reference has been removed. | Runtime SQL guardrails still need to reject invented deprecated table names. | `compat_viewer_team_context`. |
| UI-008 | `render_ai_cohost` prompt schema | Previously exposed `historical_player_metrics` alias. | Deprecated raw-table alias has been removed. | Runtime SQL guardrails still need to reject invented deprecated table names. | `analytics_player_weekly_truth` or future player context packet. |
| UI-009 | Rookie scouting CSV upload, `app.py:3945-4025` | `rookie_scouting_metrics` | Admin upload of manual scouting data. | This is a legitimate source write, but it is happening in the Streamlit process and lacks a formal migration/data dictionary workflow. | Keep admin upload temporarily, add schema doc and ingestion job wrapper. |

## Pigskin Chat Context Tool Status

Context-tool containment has been applied for `render_ai_cohost`.

- Model-visible tool declarations live in `src/pigskin_context_tools.py`.
- Pigskin can no longer call a general SQL tool.
- Tool arguments are passed as BigQuery query parameters.
- Raw/source and deprecated table names remain in blocked-table tests for the legacy SQL guardrail layer.
- The old SQL guardrail helper remains available for server-side compatibility, but it is not registered with the Gemini chat model.

## Acceptable Current UI/Mart Reads

These are acceptable for compatibility while the new mart layer is introduced:

- `analytics_fraud_watch` in `render_fraud_watch_segment`, `app.py:733-771`.
- `analytics_player_weekly_truth` in Player Profiles, weekly history, season ranking helpers, and viewer context, `app.py:1124`, `app.py:1153`, `app.py:1359`, `app.py:1381`, `app.py:3457`, and `app.py:3527`.
- `analytics_pigskin_rankings` in `fetch_pigskin_rankings_data`, `app.py:1280-1330`.
- `analytics_external_context_search_results` in Trade Lab, `app.py:3157-3167`, with the caveat that it is stored external search context, not verified truth by itself.
- `dashboard_job_runs` in Data Ops run status, `app.py:562-627`.
- Future `cloud_run_job_runs` reads for Cloud Run Job status, after `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false` is intentionally enabled.
- Warehouse table metadata via `client.list_tables` and `table.num_bytes`, `app.py:444-457`.

## Model and LLM SQL Paths

### Path LLM-001: Pigskin Context Tools

References:

- `get_pigskin_context_tool_declarations`, `src/pigskin_context_tools.py`.
- `execute_pigskin_context_tool`, `src/pigskin_context_tools.py`.
- `create_gemini_model` attaches fixed context tools, `app.py`.
- Pigskin chat dispatches model function calls through the context dispatcher, `app.py::render_ai_cohost`.

Risk:

- The model can still choose the wrong tool or omit a tool call.
- Context quality depends on materialized marts, identity bridge coverage, and source freshness.
- Missing packets must be surfaced clearly so Pigskin does not fill gaps with generic model memory.

Minimum compatibility fix:

- Add more context tools only when backed by compatibility contracts.
- Wire viewer-team packets once `compat_viewer_team_context` has real rows.
- Continue moving upstream UI context builders to compatibility marts.

### Path LLM-002: Pigskin Ranking Generator

References:

- `src/generate_pigskin_rankings.py:45-58` reads `analytics_pigskin_rankings_candidates`.
- `src/generate_pigskin_rankings.py:129-178` builds the prompt.
- `src/generate_pigskin_rankings.py:199-212` calls Gemini.
- `src/generate_pigskin_rankings.py:227-254` validates JSON output.
- `src/generate_pigskin_rankings.py:325-339` writes active and history rankings.

Risk:

- This path does not let the model generate SQL. It is safer than Pigskin chat.
- It still lacks `model_run_id`, scoring profile abstraction, and source freshness metadata.

Minimum compatibility fix:

- Add `model_runs`.
- Preserve `ranking_version` for existing UI.
- Add `model_run_id` to both active and history ranking outputs.

### Path LLM-003: Fixed-Context Gemini Text Generation

References:

- Sleeper Watch verdict, `app.py:1050-1081`.
- Player profile scouting report, `app.py:1821-1855`.
- Versus Finder comparison, `app.py:2287-2322`.
- Trade Lab AI outlook, `app.py:3204-3226`.
- Viewer Team console, `app.py:3653-3658`.
- Gemini connection test, `app.py:3278-3279`.

Risk:

- These paths do not generate SQL directly.
- Their input context can still be built from raw/source UI queries, especially Trade Lab and Viewer Team Lab.

Minimum compatibility fix:

- Keep the text-generation calls.
- Replace upstream context builders with compatibility marts.

## Minimum Compatibility Layer

The smallest safe transition keeps Streamlit functions in place and changes their table source later.

| Compatibility object | Replaces | Required columns or payload |
| --- | --- | --- |
| `compat_player_profiles_current` | `fetch_player_profiles_data`, `app.py:1090-1275` | current player ID, display name, position, current team, age inputs, scoring-profile fantasy totals, recent role metrics, EPA summary, Pigskin rank context, contract summary, depth summary, college/prospect summary, source freshness, missing flags. Production mart/view exists. App wiring is available behind `USE_COMPAT_PLAYER_PROFILES=false`. |
| `compat_sleeper_watch_candidates` | `render_sleeper_watch_segment`, `app.py:788-918` | player identity, league/global context, rostered rate, league availability, recent usage, scoring-profile points, Pigskin rank context, fraud/regression context, matchup/environment context, streamer score, breakout score, evidence text, freshness, missing flags. Production mart/view/helper exist. App wiring is available behind `USE_COMPAT_SLEEPER_WATCH=false`. |
| `compat_trade_assets_current` | `load_market_players`, `app.py:2761-2769` | player asset ID, name, position, team, market value, age, scoring profile, league type, roster format, source freshness, Pigskin rank/tier, recent usage context, risk-adjusted trade value, missing flags. Production mart/view/helper exist. App wiring is available behind `USE_COMPAT_TRADE_ASSETS=false`. |
| `compat_trade_player_history` | `query_player_history`, `app.py:3147-3155` | player, identity bridge keys, season, week, scoring-profile-aware fields, split EPA, QB splits, role metrics, Pigskin rank context, game environment, source freshness. Production view exists. App wiring is available behind `USE_COMPAT_TRADE_PLAYER_HISTORY=false`. |
| `trade_review_packets` | future Trade Lab and Pigskin trade review reads | deterministic verdict, values by side, short-term/ROS/dynasty context, player evidence, counterarguments, show framing, source freshness, and missing flags. Packet tables and helper exist. App wiring remains pending and should be default-off. |
| `fraud_watch_packets` | future Segment and Pigskin Fraud Watch reads | deterministic fraud score, actual versus expected production, usage, role stability, touchdown dependency, market hype, counterargument, show framing, source freshness, and missing flags. Packet table and helper exist. App wiring remains pending and should be default-off. |
| `sleeper_breakout_packets` | future Segment and Pigskin Sleeper Breakout reads | deterministic breakout score, role growth, usage trend, opportunity, underperformance, availability, matchup, market discount, counterargument, show framing, source freshness, and missing flags. Packet table and helper exist. App wiring remains pending and should be default-off. |
| `projections_player_weekly` | future weekly projection consumers | model-run governed weekly mean, median, floor, ceiling, stat JSON, usage JSON, efficiency JSON, touchdown JSON, confidence, risk, role, trend, fraud risk, breakout score, replacement value, source freshness, and missing flags. App wiring remains pending and should be default-off. |
| `projections_player_ros` | future rest-of-season projection consumers | model-run governed total, per-game, floor, ceiling, games played, value JSON, confidence, risk, role, trend, replacement value, source freshness, and missing flags. App wiring remains pending and should be default-off. |
| `projections_player_dynasty` | future dynasty projection consumers | model-run governed year-one, year-two, year-three, total dynasty value, age curve, lifecycle, prospect, stability adjustments, confidence, risk, source freshness, and missing flags. App wiring remains pending and should be default-off. |
| `projection_rankings_current` | future projection ranking consumers | horizon-aware projection ranks and tiers by model run, scoring profile, league type, and roster format. Does not replace Pigskin rankings UI yet. |
| `compat_viewer_team_context` | `get_sleeper_viewer_team_context`, `app.py:3390-3570` | one viewer-team packet with league context, team context, roster rows, lineup rows, bench rows, waiver rows, strengths, weaknesses, recommendations, evidence metadata, freshness, and missing flags. Production mart/view/helper exist. App wiring is available behind `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`. |
| `llm_player_context_packet` | Pigskin chat SQL tool, `app.py:2525-2796` | bounded packet JSON/text with identity, ranking context, recent fantasy production, usage, efficiency, fraud/trade context, QB context, external leads, counterarguments, snark hooks, source freshness, and missing flags. Production mart/view exists. Chat wiring remains pending. |
| `model_runs` | all generated projection/ranking outputs | `model_run_id`, run type, model name, prompt version, code version, source freshness, feature config version, scoring profile, league type, roster format, created timestamp, status. |

## Migration Sequence

1. Add table/view DDL docs for the compatibility objects, no app code change.
2. Create `model_runs` and add `model_run_id` to ranking writes.
3. Build `player_identity_bridge`.
4. `compat_player_profiles_current` is wired behind `USE_COMPAT_PLAYER_PROFILES=false`.
5. `compat_sleeper_watch_candidates` is wired behind `USE_COMPAT_SLEEPER_WATCH=false`.
6. `compat_trade_assets_current` and `compat_trade_player_history` are wired behind `USE_COMPAT_TRADE_ASSETS=false` and `USE_COMPAT_TRADE_PLAYER_HISTORY=false`.
7. `compat_viewer_team_context` is wired behind `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`.
8. Create and validate deterministic `trade_review_packets` before replacing Trade Lab trade review output.
9. Create and validate deterministic `fraud_watch_packets` and `sleeper_breakout_packets` before replacing segment or Pigskin packet output.
10. Create, validate, and backtest projection outputs before replacing any ranking, trade, viewer-team, segment, or Pigskin projection context.
11. Expose backtest outputs through `USE_BACKTEST_DASHBOARD=false` so admins can review accuracy without raw table reads.
9. Add runtime BigQuery query guardrails for Pigskin SQL calls.
10. Replace Pigskin chat SQL tool with allowlisted context functions.

## Prioritized Migration-Debt List

1. P0: Add runtime allowlist guardrails to stop Pigskin SQL execution from reaching raw/source tables.
2. P0: Replace arbitrary model-generated SQL with allowlisted context functions.
3. P0: Move `app.py:814` and `app.py:3150` off `weekly_metrics`.
4. P0: Add `model_run_id` and `model_runs` before any new ranking/projection output.
5. P0: Add `player_identity_bridge` before more player-profile or ranking work.
6. P1: Validate and gradually enable Player Profiles `compat_player_profiles_current` wiring.
7. P1: Replace Pigskin arbitrary SQL with `llm_player_context_packet` helper calls behind a default-off flag.
7. P1: Validate and gradually enable Sleeper Watch `compat_sleeper_watch_candidates` wiring.
8. P1: Validate and gradually enable Viewer Team Lab `compat_viewer_team_context` wiring.
8. P1: Enable and QA Trade Lab `compat_trade_player_history` wiring in staging first, then evaluate `compat_trade_assets_current`.
9. P1: Move Trade Lab/Pigskin trade-review reads to `trade_review_packets` behind a default-off flag after packet validation.
10. P1: Move Segment/Pigskin fraud and breakout reads to `fraud_watch_packets` and `sleeper_breakout_packets` behind default-off flags after packet validation.
11. P1: Move future projection consumers to `projections_player_weekly`, `projections_player_ros`, `projections_player_dynasty`, and `projection_rankings_current` only after validation and backtesting.
12. P1: Validate and gradually enable `USE_BACKTEST_DASHBOARD` after Phase 13.2 has materialized representative backtest rows.
10. P1: Add source freshness fields to external context, market, Sleeper, and ranking outputs.
11. P2: Move admin write jobs out of the Streamlit process and into explicit Cloud Run Jobs using `src/job_runner.py` and `cloud_run_job_runs`.
