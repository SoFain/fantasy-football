# Phase 18.2 Production Baseline Report

Captured at: 2026-06-16T18:29:24Z

Final decision: BASELINE CAPTURE PASS

## Scope

Captured read-only production Cloud Run service metadata for the current `nfl-studio-dashboard` production baseline before any future production-candidate deploy.

No deploy was run. No production service update was run. No traffic change was made. No IAM change was made. No Cloud Run Jobs were triggered. No Cloud Scheduler jobs were created. No LLM calls were made. No Firebase artifacts were created.

## GCloud Context

`gcloud` is installed but is not on PATH in this shell.

Path used:

```text
C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd
```

Active account:

```text
sofain@gmail.com
```

Active project:

```text
fantasy-football-498121
```

## Service Identity

```text
project: fantasy-football-498121
region: us-central1
service: nfl-studio-dashboard
url: https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app
```

Runtime service account:

```text
nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

## Current Serving Revision

Current ready revision:

```text
nfl-studio-dashboard-00074-26x
```

Latest created revision:

```text
nfl-studio-dashboard-00074-26x
```

Current configured image tag:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2
```

Current revision digest observed from revision list:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:6447b6f175c1aa2613907b630afeb40d56368ec99210abafacf82d5a94eca57e
```

Nearest previous ready revision observed:

```text
nfl-studio-dashboard-00073-9wp
```

Previous revision digest:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:bcdc9645ff688b4e9b8fed581eaa3de580e7d39b501ba39cb944436f77a60427
```

Recent ready revisions:

| Revision | Created | Ready |
|---|---:|---|
| `nfl-studio-dashboard-00074-26x` | 2026-06-15T19:56:06.727044Z | True |
| `nfl-studio-dashboard-00073-9wp` | 2026-06-15T18:52:09.964959Z | True |
| `nfl-studio-dashboard-00072-sjb` | 2026-06-15T17:20:58.764533Z | True |
| `nfl-studio-dashboard-00071-8l5` | 2026-06-15T16:19:19.679733Z | True |
| `nfl-studio-dashboard-00070-hbt` | 2026-06-11T18:06:04.010107Z | True |
| `nfl-studio-dashboard-00069-4dl` | 2026-06-11T15:36:18.667563Z | True |
| `nfl-studio-dashboard-00068-gjd` | 2026-06-10T19:51:50.835333Z | True |
| `nfl-studio-dashboard-00067-2pp` | 2026-06-10T19:51:38.179224Z | True |

## Traffic Baseline

Current traffic split:

| Revision | Percent | Latest revision |
|---|---:|---|
| `nfl-studio-dashboard-00074-26x` | 100 | true |

## Runtime Configuration

| Setting | Value |
|---|---|
| CPU | `2` |
| Memory | `8Gi` |
| Container concurrency | `80` |
| Timeout | `3600` seconds |
| Min instances | unset |
| Max instances | `20` |
| Ingress | `all` |
| Ingress status | `all` |
| Public invoker IAM binding | true |
| All authenticated users invoker binding | false |

Labels:

```text
cloud.googleapis.com/location=us-central1
```

Service annotation keys captured:

```text
run.googleapis.com/client-name
run.googleapis.com/client-version
run.googleapis.com/ingress
run.googleapis.com/ingress-status
run.googleapis.com/maxScale
run.googleapis.com/operation-id
run.googleapis.com/urls
serving.knative.dev/creator
serving.knative.dev/lastModifier
```

Template annotation keys captured:

```text
autoscaling.knative.dev/maxScale
run.googleapis.com/client-name
run.googleapis.com/client-version
run.googleapis.com/startup-cpu-boost
```

## Environment Variables

Plain environment variables are listed with non-secret operational values. No secret values were printed.

| Name | Value |
|---|---|
| `BQ_PROJECT` | `fantasy-football-498121` |
| `EXTERNAL_SEARCH_PROVIDER` | `vertex_ai_search` |
| `EXTERNAL_SEARCH_DAILY_LIMIT` | `10` |
| `EXTERNAL_SEARCH_MAX_RESULTS` | `3` |
| `VERTEX_AI_SEARCH_ENGINE_ID` | `fantasy-football-search-engine` |
| `GEMINI_MODEL` | `gemini-3.5-flash` |

Secret-backed environment variables:

| Env var | Secret | Version/key |
|---|---|---|
| `GEMINI_API_KEY` | `GEMINI_API_KEY` | `latest` |

No secret values were captured in this report.

## Production Risk Flag State

All risk flags are unset in production. This is safe because the application defaults these flags to false.

| Flag | Production state |
|---|---|
| `USE_COMPAT_PLAYER_PROFILES` | unset |
| `USE_COMPAT_SLEEPER_WATCH` | unset |
| `USE_COMPAT_TRADE_ASSETS` | unset |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | unset |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | unset |
| `USE_BACKTEST_DASHBOARD` | unset |
| `USE_CLAIM_LEDGER_UI` | unset |
| `USE_CONTENT_BRIEF_REVIEW_UI` | unset |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | unset |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | unset |

Blocker status:

```text
no production risk flags are true
```

## Rollback Commands

Rollback to the current production revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions nfl-studio-dashboard-00074-26x=100
```

Fallback rollback to the nearest previous ready revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions nfl-studio-dashboard-00073-9wp=100
```

Risk-flag cleanup command if a future deploy accidentally enables production risk flags:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --remove-env-vars USE_COMPAT_PLAYER_PROFILES,USE_COMPAT_SLEEPER_WATCH,USE_COMPAT_TRADE_ASSETS,USE_COMPAT_TRADE_PLAYER_HISTORY,USE_COMPAT_VIEWER_TEAM_CONTEXT,USE_BACKTEST_DASHBOARD,USE_CLAIM_LEDGER_UI,USE_CONTENT_BRIEF_REVIEW_UI,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS,DATA_OPS_ALLOW_JOB_TRIGGER
```

These commands were documented only. They were not executed.

## Commands Run

Read-only commands:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' auth list --filter=status:ACTIVE --format='value(account)'
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' config get-value project
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services describe nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --format=json
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run revisions list --service=nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --limit=8 --format=json
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services get-iam-policy nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --format=json
```

## Warnings

1. `gcloud` is installed but not on PATH. The full `gcloud.cmd` path works.
2. Production is publicly invokable through `allUsers` with ingress `all`. This appears to be the current intentional public dashboard setting, but it should be confirmed before production release.
3. The current production service still runs image tag `1a2dfe2`; it has not been moved to the Phase 18.1 immutable production-candidate image.

## Final Decision

BASELINE CAPTURE PASS

The current production service metadata and rollback baseline are captured. Production risk flags are unset, no secret values were exposed, and no production changes were made.
