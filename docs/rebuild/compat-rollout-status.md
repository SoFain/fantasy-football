# Compatibility Rollout Status

Phase 13.6 begins retiring legacy Streamlit raw reads by enabling one compatibility path at a time.

## Rollout Rule

Do not enable every compatibility flag at once. Evaluate all candidates, enable or recommend only the lowest-risk ready flag, then run manual QA before moving to the next flag.

## Readiness Checker

Helper:

- [src/compat_rollout.py](../../src/compat_rollout.py)

Commands:

```powershell
.\venv\Scripts\python.exe -m src.compat_rollout --check USE_COMPAT_TRADE_PLAYER_HISTORY
.\venv\Scripts\python.exe -m src.compat_rollout --recommend-next
```

The checker verifies:

- compatibility object exists
- row count is greater than zero
- required rollout columns exist
- `source_freshness_json` is populated in a bounded sample
- `missing_data_flags` is populated in a bounded sample
- validation SQL files exist for the object

## Live Readiness Results

Checked against:

- Project: `fantasy-football-498121`
- Dataset: `fantasy_football_brain`

| Flag | Object | Ready | Rows | Required columns | Sample freshness missing rate | Sample missing-flags missing rate | Validation files | UI impact |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `compat_trade_player_history` | yes | 55,617 | pass | 0.0 | 0.0 | 6 | Low |
| `USE_COMPAT_TRADE_ASSETS` | `compat_trade_assets_current` | yes | 1,383 | pass | 0.0 | 0.0 | 8 | Medium |
| `USE_COMPAT_PLAYER_PROFILES` | `compat_player_profiles_current` | yes | 27,864 | pass | 0.0 | 0.0 | 7 | High |
| `USE_COMPAT_SLEEPER_WATCH` | `compat_sleeper_watch_candidates` | yes | 1,652 | pass | 0.0 | 0.0 | 8 | Medium |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `compat_viewer_team_context` | yes | 10 | pass | 0.0 | 0.0 | 8 | High |

All candidates passed automated readiness checks, but only the first low-risk candidate is selected for rollout.

## Selected Flag

Selected for staging or local enablement:

- `USE_COMPAT_TRADE_PLAYER_HISTORY=true`

Reason:

- It is first in the rollout order.
- It passed live readiness checks.
- It replaces a capped Trade Lab history lookup, not a broad dashboard surface.
- Live validation passed with no failures.

Do not enable the remaining flags until Trade Lab staged QA is complete.

## Validation Result

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_history
```

Result:

- `022_compat_trade_player_history_grain.sql`: pass
- `023_compat_trade_player_history_no_raw_weekly_metrics_reference.sql`: pass
- `024_compat_trade_player_history_recent_rows_exist.sql`: pass, `recent_row_count = 55617`
- `025_compat_trade_player_history_scoring_profiles_exist.sql`: pass
- `026_compat_trade_player_history_identity_coverage.sql`: informational warning, `missing_identity_rate = 0.0`
- `027_compat_trade_player_history_no_absurd_scores.sql`: pass

Overall: 6 passed, 0 failed.

## Enablement

Local staging:

```powershell
$env:USE_COMPAT_TRADE_PLAYER_HISTORY = "true"
.\venv\Scripts\python.exe -m streamlit run app.py
```

Cloud Run staging service:

```powershell
gcloud run services update <staging-service-name> --region <region> --set-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY=true
```

Production default remains unchanged until manual QA passes and production enablement is explicitly approved.

## Rollback

Unset the flag and restart Streamlit or Cloud Run:

```powershell
Remove-Item Env:\USE_COMPAT_TRADE_PLAYER_HISTORY
```

Cloud Run rollback:

```powershell
gcloud run services update <service-name> --region <region> --remove-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY
```

No migration rollback is required. Legacy code paths remain in place.

## Manual QA Checklist

Run with only `USE_COMPAT_TRADE_PLAYER_HISTORY=true`.

1. Open Trade Lab.
2. Select two known players.
3. Confirm recent history loads.
4. Confirm source freshness and missing flags display if present.
5. Run the AI trade outlook and confirm it receives history context.
6. Confirm no `weekly_metrics` query is used in the compat path.
7. Disable the flag and confirm the legacy path still works.

Manual browser QA was run in Phase 14.4. See [Phase 14.4 Trade History Compat QA Report](validation/phase-14-4-trade-history-compat-qa-report.md).

Result:

- Trade Lab loaded with only `USE_COMPAT_TRADE_PLAYER_HISTORY=true`.
- Trade Player History displayed the compatibility contract path.
- Trade Assets stayed on the legacy warehouse path.
- Ja'Marr Chase and Justin Jefferson were visible in the Trade Lab selectors.
- `src.trade_history` returned 10 bounded recent-history rows for both players.
- The helper SQL used `compat_trade_player_history` and did not reference `weekly_metrics`.
- Local Gemini was not configured, so the AI outlook button was not run.
- Rollback was verified by restarting Streamlit with all compatibility flags unset. Trade Player History returned to the legacy warehouse path.

Recommendation:

- Promote `USE_COMPAT_TRADE_PLAYER_HISTORY=true` to staging only.
- Do not make it a production default yet.
- Do not enable any other compatibility flag until staging observes this path with configured Gemini credentials.

## Next Flag Recommendation

Next candidate after Trade History QA:

- `USE_COMPAT_TRADE_ASSETS`

Do not enable it until Trade History has passed staging QA with the AI outlook flow exercised.
