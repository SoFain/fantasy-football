# Phase 30.23 Public App Login Report

## Final Decision

PUBLIC APP LOGIN COMPLETE WITH WARNINGS

Production is publicly reachable and protected by an app-level Streamlit login gate. Both configured usernames authenticate against PBKDF2-SHA256 hashes stored in the production environment. The raw passwords were not committed, written to this report, or printed in validation output.

Warning:

- The first production auth deploy used a comma-delimited `APP_AUTH_USERS` value and Cloud Run env parsing retained only the first malformed user entry. The parser was updated to also accept semicolon delimiters, the auth commit was amended, a new image was built, and production was redeployed with a semicolon-delimited hashed user list. Final production verification passes for both users.

## Commit

- Commit: `aef3fde Add app login gate for public Cloud Run access`
- Files committed:
  - `app.py`
  - `src/app_auth.py`
  - `tests/test_app_auth.py`

## Build

- Final image tag: `prod-candidate-aef3fde3d16b-20260702T124945Z`
- Final build ID: `b1c820e4-54f8-4489-a8a5-cbb32a29b9db`
- Final digest-pinned image:
  `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:51470773b5185de1455f2af99d1f27f5322354cc0c375354cbd00ba0aed1ec1e`

Superseded interim image:

- `sha256:02236d04d3435ac79ca80fdb7542bbe3c394f9106dc0845d9453d5d7fc94349b`
- Superseded because the first env-var delimiter attempt did not preserve both users correctly.

## Production Deploy

- Service: `nfl-studio-dashboard`
- Project: `fantasy-football-498121`
- Region: `us-central1`
- Previous production revision before this phase: `nfl-studio-dashboard-00078-4bf`
- Final production revision: `nfl-studio-dashboard-00081-bwr`
- Traffic: `nfl-studio-dashboard-00081-bwr=100`
- Production URL: `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`
- Deploy output URL: `https://nfl-studio-dashboard-583607027760.us-central1.run.app`

Interim revisions:

- `nfl-studio-dashboard-00079-pfv`: first private app-auth deploy with comma-delimited env value
- `nfl-studio-dashboard-00080-gpn`: env-only retry, still malformed
- `nfl-studio-dashboard-00081-bwr`: final corrected image and semicolon-delimited user value

## Public Access Status

Cloud Run public invoker access was granted after authenticated/private health and flag verification:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services add-iam-policy-binding nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --member=allUsers `
  --role=roles/run.invoker
```

Final public checks:

- Public `/_stcore/health`: `200 ok`
- Public `/`: `200`, Streamlit shell present, no Cloud Run `403`
- Browser pre-login page showed `Data Studio Login`
- Browser pre-login page did not show `Data Ops`

## App Auth Status

Environment state after final deploy:

- `APP_AUTH_ENABLED=true`
- `APP_AUTH_USERS`: present
- Parsed usernames: `sofain`, `racehorse`
- `sofain` hash verification: passed
- `racehorse` hash verification: passed

Users configured:

- `sofain`
- `racehorse`

Raw passwords are intentionally omitted.

## Production Flags

Set:

- `USE_PIGSKIN_PACKET_QA_UI=true`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

Intentionally absent or unset:

- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`

Confirmed:

- Production model-visible historical packet tool remains off.
- Data Ops Cloud Run job trigger flag remains false.
- Data Ops local subprocess trigger flag remains false.

## Browser Smoke

Browser smoke used public production URL without Cloud Run identity headers.

Results:

- Public unauthenticated page loads with HTTP 200.
- App content is hidden before login.
- `sofain` login: passed.
- `racehorse` login: passed.
- After login, `Data Ops` is available.
- After login, `Pigskin Packet QA` is visible.
- No `Traceback` was visible.

## Tyreek QA Smoke

UI smoke submitted the Tyreek Hill read-only QA form after login. The production UI rendered the QA panel and result markers including `MIA` and `sleeper_players_current`.

The deterministic helper was also run locally for exact result capture, without Pigskin prompts, LLM calls, live Sleeper API calls, BigQuery writes, or materialization:

- season: `2025`
- week: `4`
- player_name: `Tyreek Hill`
- player_id_internal: `00-0033040`
- limit: `5`
- status: `ok`
- historical_team: `MIA`
- current_team: `null`
- current roster source: `sleeper_players_current`

The helper did not infer Miami as the current team.

## Checks Run

Local checks:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed
- `.\venv\Scripts\python.exe -m compileall -q src scripts`: passed
- `.\venv\Scripts\python.exe -m unittest tests.test_app_auth`: passed
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_packet_qa_ui`: passed
- `.\venv\Scripts\python.exe -m unittest discover tests`: passed, 616 tests
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: discovered 200 validation files

No broad validation patterns were run.

## No-State-Change Confirmation

Confirmed for this phase:

- No BigQuery rows were written.
- No materializations were run.
- No live Sleeper API call was run.
- No Pigskin prompt was submitted.
- No LLM-backed test was run.
- No Cloud Run Job was triggered.
- No Scheduler job was created.
- `DATA_OPS_ALLOW_JOB_TRIGGER` was not enabled.
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` was not enabled.
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` was not enabled.
- Raw passwords were not committed or reported.

## Rollback

Rollback was not needed.

If the login screen fails to protect the app, first remove public invoker access:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services remove-iam-policy-binding nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --member=allUsers `
  --role=roles/run.invoker
```

If the app revision must also be rolled back:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00078-4bf=100
```

## Remaining Warnings

- `APP_AUTH_USERS` is an environment variable, not Secret Manager. It stores salted PBKDF2 hashes, not raw passwords.
- The public Cloud Run surface is now intentionally open at the IAM layer. App-level login is the active access control.
- The QA UI is production-visible after login because `USE_PIGSKIN_PACKET_QA_UI=true`.

## Recommended Next Action

Owner should manually open the production URL and sign in with both accounts. Then review `Data Ops -> Pigskin Packet QA` using the Tyreek Hill case and any other owner-selected read-only cases.
