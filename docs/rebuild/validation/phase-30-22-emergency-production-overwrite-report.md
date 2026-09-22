# Phase 30.22 Emergency Production Overwrite Report

## Final Decision

PRODUCTION OVERWRITE COMPLETE WITH WARNINGS

The emergency production overwrite was executed with the exact Phase 30.21 staging image digest. Production is serving the new revision and authenticated health returns `200 ok`.

Warnings remain:

- Public unauthenticated access to `/` and `/_stcore/health` still returns Cloud Run `403 Forbidden`, so the service remains private at the Cloud Run layer.
- Headless browser smoke with an identity-token header loaded the Streamlit shell with HTTP 200, but the page stayed in Streamlit `CONNECTING` state. Browser-click visibility of the `Pigskin Packet QA` UI was not fully proven in production.
- The focused QA UI unittest reported `OK`, but PowerShell recorded exit code 1 because unittest progress/logging was emitted on stderr. The test result itself was pass.

Rollback was not performed because the new production revision passed authenticated health, the service describe shows the requested image and flags, and no app traceback was observed in the lightweight smoke.

## Production Deploy Details

- Service: `nfl-studio-dashboard`
- Project: `fantasy-football-498121`
- Region: `us-central1`
- Previous production revision: `nfl-studio-dashboard-00077-2jp`
- New production revision: `nfl-studio-dashboard-00078-4bf`
- Production URL from service describe: `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`
- Deploy output URL: `https://nfl-studio-dashboard-583607027760.us-central1.run.app`
- Traffic after deploy: `nfl-studio-dashboard-00078-4bf=100`

## Image

- Requested Phase 30.21 staging image digest:
  `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:8f6134e7e7fe8bda59f382a938662ecd6b9c68912988ff1d3f1a6a64cbfff0e6`
- Production image after deploy:
  `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:8f6134e7e7fe8bda59f382a938662ecd6b9c68912988ff1d3f1a6a64cbfff0e6`
- Source commit expected by phase: `7b6138c Add read-only Pigskin packet QA UI`

## Pre-Deploy Baseline

### Production

- Revision: `nfl-studio-dashboard-00077-2jp`
- Image:
  `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: `nfl-studio-dashboard-00077-2jp=100`
- `USE_PIGSKIN_PACKET_QA_UI`: absent
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: absent
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

### Staging

- Revision: `nfl-studio-dashboard-staging-00031-79n`
- Image:
  `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:8f6134e7e7fe8bda59f382a938662ecd6b9c68912988ff1d3f1a6a64cbfff0e6`
- Traffic: `nfl-studio-dashboard-staging-00031-79n=100`
- `USE_PIGSKIN_PACKET_QA_UI=true`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

## Local Checks

Only lightweight checks were run. No broad validation patterns were run.

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed
- `.\venv\Scripts\python.exe -m compileall -q src scripts`: passed
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_packet_qa_ui`: unittest output reported `Ran 9 tests ... OK`; PowerShell wrapper returned exit code 1 due stderr output handling

## Deploy Command

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:8f6134e7e7fe8bda59f382a938662ecd6b9c68912988ff1d3f1a6a64cbfff0e6 `
  --update-env-vars=USE_PIGSKIN_PACKET_QA_UI=true,DATA_OPS_ALLOW_JOB_TRIGGER=false,DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false `
  --quiet
```

The `gcloud` process emitted progress on stderr and PowerShell recorded exit code 1, but Cloud Run reported:

- Deployment succeeded
- New revision: `nfl-studio-dashboard-00078-4bf`
- Serving 100 percent traffic

## Production Flags After Deploy

Set:

- `USE_PIGSKIN_PACKET_QA_UI=true`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

Intentionally absent or unset:

- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`

Preserved policy:

- No production model-visible historical packet tool exposure was enabled.
- Data Ops job trigger flags remained false.
- Data Ops local subprocess trigger flag remained false.

## Health Result

- Public unauthenticated `/_stcore/health`: `403 Forbidden`
- Authenticated `/_stcore/health` with identity token: `200 ok`
- Public unauthenticated `/`: `403 Forbidden`
- Authenticated browser shell load: HTTP 200, Streamlit shell present, no `Traceback`, but page remained in `CONNECTING` state in headless smoke

## QA UI Visibility Result

Production configuration confirms `USE_PIGSKIN_PACKET_QA_UI=true`.

Browser-click visibility of `Pigskin Packet QA` was not fully proven in production because the authenticated headless Streamlit page did not complete its websocket connection. The likely blocker is Cloud Run private access interacting with Streamlit websocket auth in the headless smoke path.

The deterministic QA helper path was checked without Pigskin prompts, LLM calls, BigQuery writes, materializations, or live Sleeper API calls.

Tyreek Hill case:

- season: `2025`
- week: `4`
- player_name: `Tyreek Hill`
- player_id_internal: `00-0033040`
- limit: `5`
- status: `ok`
- historical_team: `MIA`
- current_team: `null`
- current_roster_source: `sleeper_players_current`
- warning posture: current roster state remains separate from historical packet team

The helper did not infer Miami as the current team.

## No-State-Change Confirmation

Confirmed for this phase:

- No BigQuery writes were run.
- No materializations were run.
- No live Sleeper API call was run.
- No Pigskin prompt was submitted.
- No LLM-backed test was run.
- No broad validation pattern was run.
- No Cloud Run Job was triggered.
- No Scheduler job was created.
- `DATA_OPS_ALLOW_JOB_TRIGGER` was not enabled.
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` was not enabled.

## Rollback

Rollback was not needed during this phase.

Rollback command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00077-2jp=100
```

## Recommended Next Action

Decide how the owner should access production:

- Keep Cloud Run private and use authenticated access or `gcloud run services proxy`.
- Or explicitly approve public Cloud Run invoker access for the production service, with the app login/session gate still protecting the Streamlit UI.

After the access method is decided, run a browser-click owner smoke focused only on `Data Ops -> Pigskin Packet QA` and the Tyreek Hill case.
