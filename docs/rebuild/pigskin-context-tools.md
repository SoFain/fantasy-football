# Pigskin Context Tools

Source of truth: `docs/CODEX_PROJECT_CONTEXT.md`.

Pigskin chat no longer receives a general SQL execution tool. The model-facing interface is now a fixed set of parameterized context tools in `src/pigskin_context_tools.py`.

## Goal

Pigskin should answer from curated marts, compatibility objects, and evidence packets. It should not compose arbitrary warehouse queries, scan raw source tables, or recover from missing curated data by guessing.

## Model-Visible Tools

The model can call only these tools:

| Tool | Purpose | Primary safe source |
| --- | --- | --- |
| `get_player_context_packet` | Load one player evidence packet with ranking, role, source freshness, and missing-data flags. | `llm_player_context_packet` |
| `search_players` | Resolve ambiguous player names or IDs. | `llm_player_context_packet` |
| `get_rankings_slice` | Load Pigskin-owned active rankings. | `analytics_pigskin_rankings` |
| `get_fraud_watch_candidates` | Load curated Fraud Watch candidates. | `analytics_fraud_watch` |
| `get_trade_player_history` | Load capped player-week trade history. | `compat_trade_player_history` |
| `compare_players` | Compare players using player context packets. | `llm_player_context_packet` |
| `get_context_event_leads` | Load curated context events and stored external verification leads. | `analytics_context_events`, `analytics_external_context_search_results` |

## Guardrails

The tool layer enforces:

- No user-supplied SQL.
- No user-supplied table names.
- Trusted project and dataset identifiers only.
- BigQuery query parameters for user inputs.
- Hard result limits per tool.
- `maximum_bytes_billed` from `PIGSKIN_CONTEXT_MAX_BYTES_BILLED`, defaulting to `1 GB`.
- Tool-call logging with tool name, sanitized arguments, and row counts.
- JSON-safe output for Streamlit and Gemini function responses.

## Failure Contract

If a context tool fails, the chat UI stops and shows the failed tool call plus the error. Pigskin should not answer from memory after a tool failure.

If a context tool returns no rows, Pigskin should say the curated data is unavailable and identify the missing materialization or identity mapping needed.

## Runtime Wiring

Current wiring:

- Tool declarations: `src/pigskin_context_tools.py::get_pigskin_context_tool_declarations`
- Dispatcher: `src/pigskin_context_tools.py::execute_pigskin_context_tool`
- Chat registration: `app.py::create_gemini_model`
- Manual tool loop: `app.py::render_ai_cohost`

The old SQL guardrail module still exists for server-side compatibility and admin paths, but it is no longer the Pigskin model-facing tool surface.

## Tests

Covered by:

- `tests/test_pigskin_context_tools.py`
- `tests/test_pigskin_chat_schema.py`

Recommended scoped checks:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_pigskin_context_tools tests.test_pigskin_chat_schema
.\venv\Scripts\python.exe -m py_compile app.py src\pigskin_context_tools.py src\llm_context_packets.py src\trade_history.py
```
