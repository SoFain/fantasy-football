# Phase 15.3 Trade History Staging Promotion Report

Date: 2026-06-16

Decision: GO for staging only

## Scope

Phase 15.3 promotes only `USE_COMPAT_TRADE_PLAYER_HISTORY=true` to staging. Production defaults remain false, all other `USE_COMPAT_*` flags remain false, and the legacy Trade Lab fallback remains in place.

## Readiness Check

Command:

```powershell
.\venv\Scripts\python.exe -m src.compat_rollout --check USE_COMPAT_TRADE_PLAYER_HISTORY
```

Result:

- `compat_trade_player_history` exists.
- Object type: `VIEW`.
- Row count: `55,617`.
- Required columns: pass.
- Source freshness sampled missing rate: `0.0`.
- Missing-data flags sampled missing rate: `0.0`.
- Validation files discovered: 6.
- Recommendation: enable for low-impact staged rollout.

## Staging Configuration

Enable only on the staging Cloud Run service:

```powershell
gcloud run services update <staging-service-name> --region <region> --set-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY=true
```

Do not set this variable on production until a separate production promotion is approved.

All other compatibility flags remain unset or false:

- `USE_COMPAT_PLAYER_PROFILES=false`
- `USE_COMPAT_SLEEPER_WATCH=false`
- `USE_COMPAT_TRADE_ASSETS=false`
- `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`

## Rollback

Remove the staging flag and restart the service:

```powershell
gcloud run services update <staging-service-name> --region <region> --remove-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY
```

Local rollback:

```powershell
Remove-Item Env:\USE_COMPAT_TRADE_PLAYER_HISTORY
```

No migration rollback is required because this rollout changes only the read path selected by the environment flag.

## UI Marker

When `USE_COMPAT_TRADE_PLAYER_HISTORY=true`, Trade Lab now shows:

```text
Trade player history source: compat_trade_player_history
```

When recent history is loaded for a selected player, Trade Lab also displays source freshness or missing-data flags when those columns are present in the compatibility rows.

## Manual QA Checklist

Run in staging with only `USE_COMPAT_TRADE_PLAYER_HISTORY=true`.

1. Confirm the staging Cloud Run service includes only this compatibility flag.
2. Open Trade Lab.
3. Select at least two known active players.
4. Run the AI outlook.
5. Confirm the Trade Lab marker says `Trade player history source: compat_trade_player_history`.
6. Confirm recent player history rows load and match the existing prompt shape.
7. Confirm source freshness or missing-data flags display when populated.
8. Confirm the AI trade outlook receives bounded recent history context.
9. Confirm the compat path uses `src.trade_history`.
10. Confirm the compat path does not query raw `weekly_metrics`.
11. Remove the flag and confirm the legacy fallback still works.

## Validation

Commands:

```powershell
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_history
```

Results:

- Unit tests: 285 passed.
- `app.py` compile: pass.
- `src` and `scripts` compile: pass.
- `compat_trade_player_history` validation: 6 passed, 0 failed.
- Informational warning remains: `026_compat_trade_player_history_identity_coverage.sql` returned `missing_identity_rate = 0.0`, which confirms no missing identities in the current validation output.

## Safety Status

- No Firebase artifacts were created.
- No production defaults changed.
- No other compatibility flags were promoted.
- No legacy fallback path was removed.
- No raw/source table access was added to the compatibility path.
- No migrations were applied.
- No LLM calls were made.

## Final Recommendation

Promote `USE_COMPAT_TRADE_PLAYER_HISTORY=true` to staging only. Keep production unchanged until staging manual QA signs off.
