# UI Query Debt Register (Closed)

Status: **closed**. The debt this register tracked was direct raw/source BigQuery reads from the Streamlit UI and its chat surface. The Streamlit app was retired, so those read paths no longer exist. The app remains available as a local studio surface (`Launch_Studio.bat`); its compat feature flags stay default-off and it is not deployed anywhere.

Source docs:

- [docs/CODEX_PROJECT_CONTEXT.md](../CODEX_PROJECT_CONTEXT.md)
- [docs/rebuild/audit-and-rebuild-plan.md](audit-and-rebuild-plan.md)
- [docs/rebuild/current-warehouse-inventory.md](current-warehouse-inventory.md)
- [docs/rebuild/table-classification.md](table-classification.md)
- [docs/rebuild/cloud-run-operating-model.md](cloud-run-operating-model.md)

This document is kept for two reasons: it records how each debt item was resolved, and its compatibility-object table is still the read contract that any future consumer surface must follow.

## How Each Item Closed

| Debt ID | What it was | Resolution |
| --- | --- | --- |
| UI-001 | Sleeper Watch read `weekly_metrics`, `sleeper_rosters`, `sleeper_roster_players` directly. | Backend module `src/sleeper_watch.py` is now the only path. UI retired. |
| UI-002 | Player Profiles joined `player_rosters`, `player_contracts`, `depth_charts`, `college_player_stats`, `rookie_scouting_metrics`. | Backend module `src/player_profiles.py` is now the only path. UI retired. |
| UI-003 | Trade Lab read `market_values` directly. | Backend module `src/trade_assets.py` is now the only path. UI retired. |
| UI-004 | Trade AI outlook read `weekly_metrics` directly. | Backend module `src/trade_history.py` is now the only path. UI retired. |
| UI-004A | Trade review evidence rebuilt per request. | `trade_review_packets` plus `trade_review_packet_players` exist with `src/trade_review_packets.py`. No consumer yet. |
| UI-004B | Fraud Watch claims rebuilt per request. | `fraud_watch_packets` exists with `src/segment_packets.py`. No consumer yet. |
| UI-004C | Sleeper breakout scans hit raw Sleeper and weekly tables. | `sleeper_breakout_packets` exists with `src/segment_packets.py`. No consumer yet. |
| UI-004D | Ad hoc projection math in the UI. | Versioned projection outputs exist with `src/projection_engine.py`. No consumer yet. |
| UI-005 | Viewer Team console joined four raw Sleeper tables. | Backend module `src/viewer_team_context.py` is now the only path. UI retired. |
| UI-006 | Chat exposed raw tables through prompt and schema patterns. | Arbitrary SQL was removed in 7.2C; the chat surface itself is now retired. `src/pigskin_context_tools.py` remains the curated tool layer for any future surface. |
| UI-007 | Prompt exposed deprecated `active_league_rosters`. | Prompt retired with the chat surface. Name stays in the blocked-table tests. |
| UI-008 | Prompt exposed deprecated `historical_player_metrics` alias. | Prompt retired with the chat surface. Name stays in the blocked-table tests. |
| UI-009 | Rookie scouting CSV uploaded through the Streamlit process. | Replaced by the `ingest-rookie-scouting` job in `src/job_runner.py`, backed by `src/ingest_rookie_scouting.py`. The interactive column mapper is gone; the CSV must use canonical column names. |

## Remaining Work

All thirteen items are closed. Twelve closed by retiring the UI; UI-009 closed by replacing the CSV uploader with a job.

Everything that was "pending app wiring" is now simply "pending a consumer". The packets, projections, and compatibility objects exist and are validated; nothing reads them yet.

## Read Contract For Future Consumers

Any future consumer surface reads these objects, never the raw tables they replaced. This is the durable output of the compatibility work.

| Compatibility object | Replaces | Backend helper |
| --- | --- | --- |
| `compat_player_profiles_current` | direct Player Profiles joins | `src/player_profiles.py` |
| `compat_sleeper_watch_candidates` | direct Sleeper Watch scans | `src/sleeper_watch.py` |
| `compat_trade_assets_current` | direct `market_values` reads | `src/trade_assets.py` |
| `compat_trade_player_history` | direct `weekly_metrics` reads | `src/trade_history.py` |
| `compat_viewer_team_context` | four-way raw Sleeper joins | `src/viewer_team_context.py` |
| `llm_player_context_packet` | model-generated SQL | `src/pigskin_context_tools.py` |
| `trade_review_packets`, `trade_review_packet_players` | per-request trade evidence | `src/trade_review_packets.py` |
| `fraud_watch_packets` | per-request fraud claims | `src/segment_packets.py` |
| `sleeper_breakout_packets` | per-request breakout scans | `src/segment_packets.py` |
| `projections_player_weekly`, `projections_player_ros`, `projections_player_dynasty` | ad hoc projection math | `src/projection_engine.py` |
| `projection_rankings_current` | ad hoc ranking math | `src/projection_engine.py` |
| `model_runs` | unversioned generated output | `src/model_runs.py` |

Full column-level definitions are in [bigquery/contracts](../../bigquery/contracts). The compatibility layer is indexed in [compatibility-contracts.md](compatibility-contracts.md).

## Live LLM Paths

One LLM path survives the UI retirement.

### Pigskin Ranking Generator

- `src/generate_pigskin_rankings.py:fetch_candidates` reads `analytics_pigskin_rankings_candidates`.
- `src/generate_pigskin_rankings.py:build_prompt` builds the prompt.
- `src/generate_pigskin_rankings.py:call_gemini` calls Gemini.
- `src/generate_pigskin_rankings.py:normalize_model_rankings` validates JSON output.
- `src/generate_pigskin_rankings.py:write_rankings` writes active and history rankings.

This path never lets the model generate SQL. It reads a candidate mart, sends fixed context, and validates the JSON that comes back. It is governed by `model_run_id` through `src/model_runs.py`.

Risk to watch as ranking work resumes: context quality depends on materialized marts, identity bridge coverage, and source freshness. Missing packets should be surfaced honestly rather than filled in from model memory.

## Retired LLM Paths

These were fixed-context Gemini text generators embedded in UI views. They were deleted with the UI and have no backend equivalent: player profile scouting report, Versus Finder comparison, viewer team console narrative, and the Gemini connection test. The Sleeper Watch verdict and Trade Lab outlook generators survive inside `src/sleeper_watch.py` and `src/trade_assets.py`.
