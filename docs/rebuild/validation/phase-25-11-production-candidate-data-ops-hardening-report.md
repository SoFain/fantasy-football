# Phase 25.11 Production Candidate Data Ops Hardening Report

Date: 2026-06-26

Final decision: DATA OPS HARDENING PRODUCTION CANDIDATE READY WITH WARNINGS

## Scope

Phase 25.11 built a production-candidate image from the committed Data Ops local-control hardening release.

No production deploy occurred. No staging deploy occurred. No production feature flags changed. No Cloud Run Jobs were triggered. No Scheduler jobs were created. No ingestion, score materialization, LLM-backed action, Pigskin prompt, scrape, or Firebase artifact was created.

## Authorization Gates

Checked process environment gates:

| Gate | State |
|---|---|
| ALLOW_LIMITED_PRODUCTION_DEPLOY | unset |
| ALLOW_TRADE_SCORE_MATERIALIZATION | unset |
| ALLOW_PROJECTION_CONTEXT_REFRESH | unset |
| ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST | unset |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | unset |

No authorization gate was set during this phase.

## Git State

Latest commits:

```text
22e3256 Gate Data Ops local subprocess controls
63149aa Clean up production warning noise
0001f47 Add Trade Analyzer score v0 and safe production rollout
```

Source commit:

| Field | Value |
|---|---|
| Short commit | `22e32569c50d` |
| Full commit | `22e32569c50d7493891c133d561cb4e4f16a569a` |

The working tree was not fully clean because historical validation reports remain untracked for owner review. The Cloud Build source was created from a clean `git archive HEAD` extraction at:

```text
C:\Users\So Fain\AppData\Local\Temp\phase25_11_prod_candidate_src
```

The clean archive contained tracked source only:

| Check | Result |
|---|---|
| Tracked files extracted | 443 |
| `.git` directory included | No |
| untracked Phase 17 validation report included | No |
| untracked Phase 25.10A commit report included | No |
| `app.py` included | Yes |

## Pre-Build Checks

| Command | Result |
|---|---|
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS |
| `.\venv\Scripts\python.exe -m py_compile app.py` | PASS |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | PASS |
| `.\venv\Scripts\python.exe -m unittest discover tests` | PASS, 352 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | PASS, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | PASS, 160 validation files discovered |

## Hardening Source Verification

Verified in the committed source and clean build context:

| Check | Result |
|---|---|
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` exists and defaults false | PASS |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` exists and defaults false | PASS |
| Data Ops local buttons are gated by both local flags | PASS |
| Cloud Run Job buttons remain gated separately by `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` and `DATA_OPS_ALLOW_JOB_TRIGGER` | PASS |
| Trade Lab AI outlook action is gated by local admin controls | PASS |
| Scouting CSV uploader is hidden unless local gates are enabled | PASS |
| `execute_bigquery_sql` absent from runtime source files | PASS |
| `rg -n "use_container_width" app.py src tests requirements.txt` has no runtime matches | PASS |
| `requirements.txt` includes `google-cloud-bigquery-storage>=2.24.0` | PASS |

The string `execute_bigquery_sql` remains present only in tests that assert it is not exposed.

## Image Tag

Generated with:

```text
.\venv\Scripts\python.exe scripts\build_image_tag.py --channel prod-candidate
```

Image tag:

```text
prod-candidate-22e32569c50d-20260626T104302Z
```

## Build Result

Cloud Build command was run from the clean archive directory:

```text
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit --project=fantasy-football-498121 --config=cloudbuild.yaml --substitutions="_IMAGE_TAG=prod-candidate-22e32569c50d-20260626T104302Z,_COMMIT_HASH=22e3256,_VERSION_LABEL=prod-candidate-22e32569c50d-20260626T104302Z" .
```

| Field | Value |
|---|---|
| Build ID | `6abd92f7-b008-4320-ba55-7a7944a69cd3` |
| Build status | SUCCESS |
| Build create time | `2026-06-26T10:44:02.128284601Z` |
| Build finish time | `2026-06-26T10:45:54.349164Z` |
| Image tag | `prod-candidate-22e32569c50d-20260626T104302Z` |
| Image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-22e32569c50d-20260626T104302Z` |
| Digest | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Digest-pinned image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |

Build substitutions from Cloud Build describe:

```text
_COMMIT_HASH=22e3256
_IMAGE_TAG=prod-candidate-22e32569c50d-20260626T104302Z
_VERSION_LABEL=prod-candidate-22e32569c50d-20260626T104302Z
```

## Artifact Registry Verification

Artifact Registry describe confirmed:

| Field | Value |
|---|---|
| Image exists | PASS |
| Digest exists | PASS |
| Digest | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |

## Packaging Verification

Verified from the clean source context and Dockerfile:

| Check | Result |
|---|---|
| `requirements.txt` includes `google-cloud-bigquery-storage>=2.24.0` | PASS |
| `Dockerfile` installs `requirements.txt` | PASS |
| `scripts/run_bigquery_validations.py` exists in build context | PASS |
| `Dockerfile` copies `scripts/run_bigquery_validations.py` into the image | PASS |
| `bigquery/validations/` exists in build context | PASS |
| `Dockerfile` copies `bigquery/validations/` into the image | PASS |
| Dockerfile sets `APP_COMMIT=$COMMIT_HASH` | PASS |

Local Docker is not installed, so direct `docker run` inspection of the built image was not possible in this environment. This is the only warning.

## Production Untouched Verification

Read-only production describe confirmed:

| Field | State |
|---|---|
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00076-p6s` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |
| Traffic | `100%` to `nfl-studio-dashboard-00076-p6s` |
| Trade History compatibility | false |
| Trade Analyzer score UI | false |
| Trade score compatibility | false |
| Data Ops Cloud Run job trigger flag | false |
| New local Data Ops flags | unset or false |

## Remaining Warnings

- The local working tree still has many untracked historical validation reports. They were excluded from the build by using a clean `git archive HEAD` source directory.
- Local Docker is unavailable, so packaging was verified through source context, Dockerfile copy/install rules, Cloud Build success, and Artifact Registry digest verification rather than by running the image locally.

## Next Step

The production deploy gate may be run next using this digest-pinned candidate, with all production risk flags false and both Data Ops trigger gates false.
