# Phase 18.1 Production Candidate Image Report

Date: 2026-06-16

Final decision: IMAGE BUILD PASS

## Scope

Resolved local `gcloud` tooling access, verified the active Google Cloud project, ran pre-build safety checks, built one immutable production-candidate image, and verified the Artifact Registry digest.

No production deploy was run. No staging deploy was run. No Cloud Run Jobs were triggered. No Cloud Scheduler jobs were created. No LLM calls were made. No scraping occurred. No Firebase artifacts were created. No production risk flags were changed.

## GCloud Tooling

`gcloud` is installed but not on PATH in this shell.

Path used:

```text
C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd
```

Version:

```text
Google Cloud SDK 572.0.0
bq 2.1.32
core 2026.06.05
gcloud-crc32c 1.0.0
gsutil 5.37
```

Active account:

```text
sofain@gmail.com
```

Active project:

```text
fantasy-football-498121
```

Target region:

```text
us-central1
```

## Pre-Build Checks

Commands run with the repo venv:

```text
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

```text
deployment safety: pass
unit tests: 290 passed
app.py compile: pass
src and scripts compile: pass
pending migrations: none
validation dry-run: pass, 149 validation files discovered
```

Safety checks passed:

- no Firebase artifacts
- no tracked secret files
- no secret content
- required files exist
- feature flags default off
- Pigskin arbitrary SQL remains absent
- `app.py`, `src`, and `scripts` compile

## Image Tag

Git SHA:

```text
ce0eb82eef63
```

Immutable image tag:

```text
prod-candidate-ce0eb82eef63-20260616T181911Z
```

Image URI:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260616T181911Z
```

Fully qualified digest:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:6d26118c3fdf3ce10d1983a8cfddb05956f65c34463d4ef02bcce47cb37f25c4
```

Digest:

```text
sha256:6d26118c3fdf3ce10d1983a8cfddb05956f65c34463d4ef02bcce47cb37f25c4
```

## Build Command

Command run:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit `
  --project=fantasy-football-498121 `
  --config=cloudbuild.yaml `
  --substitutions="_IMAGE_TAG=prod-candidate-ce0eb82eef63-20260616T181911Z,_COMMIT_HASH=ce0eb82eef63,_VERSION_LABEL=prod-candidate-ce0eb82eef63-20260616T181911Z" `
  .
```

Build result:

```text
build ID: c81856f3-1b16-4585-a92a-4d507d6d5e1a
status: SUCCESS
duration: 2M23S
```

Cloud Build pushed only the explicit immutable tag from `cloudbuild.yaml`. The build did not publish `latest`.

## Artifact Verification

Verification command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' artifacts docker images describe `
  'us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260616T181911Z' `
  --project=fantasy-football-498121 `
  --format=json
```

Result:

```text
registry: us-central1-docker.pkg.dev
repository: nfl-studio-repo
digest: sha256:6d26118c3fdf3ce10d1983a8cfddb05956f65c34463d4ef02bcce47cb37f25c4
slsa_build_level: unknown
```

## No-Deploy Confirmation

No `gcloud run deploy`, `gcloud run services update`, or `gcloud run jobs execute` command was run.

Read-only service checks after the build:

Production service:

```text
service: nfl-studio-dashboard
latest ready revision: nfl-studio-dashboard-00074-26x
image: us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2
url: https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app
```

Staging service:

```text
service: nfl-studio-dashboard-staging
latest ready revision: nfl-studio-dashboard-staging-00009-zkq
image: us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-81ed959
url: https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app
```

The new production-candidate image is built and available, but neither Cloud Run service currently uses it.

## Warnings

1. `gcloud` is still not on PATH. The full `gcloud.cmd` path works and was used for all Google Cloud commands.
2. The local worktree contains an untracked Phase 17 validation report. It is documentation-only and was not part of this build decision, but it should be committed or classified before any release PR is finalized.
3. Artifact Registry reports `slsa_build_level: unknown`.

## Final Decision

IMAGE BUILD PASS

The immutable production-candidate image was built and verified. This does not approve production deployment. A separate production deploy authorization and smoke-test plan are still required before the candidate image can be used.
