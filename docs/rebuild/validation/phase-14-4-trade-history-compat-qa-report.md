# Phase 14.4 Trade History Compat QA Report

Final recommendation: promote to staging only

## Scope

This QA pass tested only:

- `USE_COMPAT_TRADE_PLAYER_HISTORY=true`

All other compatibility flags remained false.

Production defaults were not changed.

## Feature Flag Defaults

With all related environment variables unset:

| Flag | Default |
| --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | false |
| `USE_COMPAT_SLEEPER_WATCH` | false |
| `USE_COMPAT_TRADE_ASSETS` | false |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | false |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | false |

With the QA environment scoped to only `USE_COMPAT_TRADE_PLAYER_HISTORY=true`:

| Flag | QA value |
| --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | false |
| `USE_COMPAT_SLEEPER_WATCH` | false |
| `USE_COMPAT_TRADE_ASSETS` | false |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | true |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | false |

## Readiness Check

Command:

```powershell
.\venv\Scripts\python.exe -m src.compat_rollout --check USE_COMPAT_TRADE_PLAYER_HISTORY
```

Result:

- Object: `fantasy-football-498121.fantasy_football_brain.compat_trade_player_history`
- Type: `VIEW`
- Row count: 55,617
- Required columns: pass
- `source_freshness_json` missing rate in bounded sample: 0.0
- `missing_data_flags` missing rate in bounded sample: 0.0
- Validation files discovered: 6
- Ready: true

## Validation Result

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_history
```

Result:

- 6 passed
- 0 failed
- `026_compat_trade_player_history_identity_coverage.sql` returned an informational warning row with `missing_identity_rate = 0.0`

## Manual UI QA

Local Streamlit was started with an environment-scoped flag:

```powershell
$env:USE_COMPAT_TRADE_PLAYER_HISTORY = "true"
.\venv\Scripts\python.exe -m streamlit run app.py --server.port 8502 --server.headless true
```

Observed:

- Login worked locally with the configured local defaults.
- Trade Lab loaded.
- Trade Assets remained on the legacy warehouse path.
- Trade Player History showed: `Data path: Trade Player History is using the compatibility contract path.`
- `weekly_metrics` was not shown in the UI while the compat path was active.
- Two known active players were visible in the Trade Lab selectors:
  - Ja'Marr Chase
  - Justin Jefferson

Local Gemini was not configured, so the AI outlook button was not run and no LLM call was made.

## Bounded History Payload Check

Because the local AI outlook was gated by missing Gemini configuration, the recent-history payload was tested directly through `src.trade_history`.

Players checked:

- Ja'Marr Chase
- Justin Jefferson

Result:

- Each player returned 10 recent rows.
- Returned columns included scoring, role, EPA summary, QB split, ranking context, `source_freshness_json`, and `missing_data_flags`.
- Query SQL used `compat_trade_player_history`.
- Query SQL did not reference `weekly_metrics`.
- Query parameters were used for scoring profile, seasons back, player ID, player name, normalized name, and limit.

## Static Safety

Confirmed:

- `app.py` calls `query_compat_trade_player_history()` when `use_compat_trade_player_history()` is true.
- `query_compat_trade_player_history()` delegates to `src.trade_history.get_trade_player_history()`.
- `src.trade_history` reads `compat_trade_player_history`.
- `src.trade_history` does not query `weekly_metrics`.
- Legacy fallback still exists in `app.py` when the flag is false or the compat path errors.
- Pigskin prompt/schema was not changed.
- `execute_bigquery_sql` remains absent from Pigskin-visible schema tests.

## Rollback Check

The local Streamlit process was restarted with all compatibility flags unset.

Observed:

- Trade Lab loaded.
- Trade Player History showed: `Data path: Trade Player History is using the legacy warehouse path.`
- Legacy fallback remains available.

## Issues Found

No blocker was found for the trade-history compatibility path.

Known limitation:

- The local Gemini key was not configured, so this pass did not execute the full AI outlook request path. The bounded history context that would feed that path was verified directly through the helper.

## Recommendation

Promote `USE_COMPAT_TRADE_PLAYER_HISTORY=true` to staging only.

Do not enable it as a production default yet. After staging verifies the AI outlook flow with configured Gemini credentials, this flag can be considered for production environment enablement.

Do not enable any other compatibility flags until this staged rollout is observed.
