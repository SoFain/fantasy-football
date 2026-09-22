# Phase 25.5 Production Candidate Warning Cleanup Report

Final decision: WARNING CLEANUP PRODUCTION CANDIDATE READY

## Scope

Phase 25.5 built a clean immutable production-candidate image from the committed warning-cleanup release.

No production deploy was run. No staging deploy was run. No production feature flags were changed. No Cloud Run Jobs were triggered. No Scheduler jobs were created. No ingestion, score materialization, LLM-backed action, Pigskin prompt, scraping, Firebase artifact creation, authorization gate change, or commit was performed.

## Authorization Gates

Checked before build work:

| Gate | State |
| --- | --- |
| ALLOW_LIMITED_PRODUCTION_DEPLOY | unset |
| ALLOW_TRADE_SCORE_MATERIALIZATION | unset |
| ALLOW_PROJECTION_CONTEXT_REFRESH | unset |
| ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST | unset |

## Git State

Latest commit:

```text
63149aa Clean up production warning noise
```

Previous commit:

```text
0001f47 Add Trade Analyzer score v0 and safe production rollout
```

Source hash:

```text
63149aa3d8167ed3434a0ea02b8800c475c9dd5a
```

The working tree still contains untracked historical validation reports retained for owner review. This is allowed by the Phase 25.5 prompt. The Dockerfile copies only `app.py`, `validate.py`, `src/`, `scripts/run_bigquery_validations.py`, `bigquery/validations/`, `data/`, and `requirements.txt`, so those untracked reports are not part of the runtime image.

## Pre-build Checks

All required checks passed with process exit code 0:

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 346 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |

Note: the unit tests printed expected mocked job and pipeline logs. The test process exited 0. No live ingestion or materialization command was run.

## Cleanup Source Verification

| Check | Result |
| --- | --- |
| `rg -n "use_container_width" app.py src tests requirements.txt` | no matches |
| `requirements.txt` includes `google-cloud-bigquery-storage>=2.24.0` | yes, line 4 |

## Image Tag

Tag generated with the repo-supported script:

```powershell
.\venv\Scripts\python.exe scripts\build_image_tag.py --channel prod-candidate
```

Generated tag:

```text
prod-candidate-63149aa3d816-20260626T040202Z
```

## Build Result

Build command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit --project=fantasy-football-498121 --config=cloudbuild.yaml --substitutions="_IMAGE_TAG=prod-candidate-63149aa3d816-20260626T040202Z,_COMMIT_HASH=63149aa3d816,_VERSION_LABEL=prod-candidate-63149aa3d816-20260626T040202Z" .
```

| Field | Value |
| --- | --- |
| Build ID | `407ecdb8-1ace-42ff-9693-d36de93037ff` |
| Build status | `SUCCESS` |
| Build create time | `2026-06-26T04:02:20.795937803Z` |
| Build finish time | `2026-06-26T04:04:17.877233Z` |
| Image tag | `prod-candidate-63149aa3d816-20260626T040202Z` |
| Image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-63149aa3d816-20260626T040202Z` |
| Digest | `sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |
| Digest-pinned image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |

## Artifact Registry Verification

Artifact Registry describe confirmed:

| Field | Value |
| --- | --- |
| Registry | `us-central1-docker.pkg.dev` |
| Repository | `nfl-studio-repo` |
| Digest | `sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |
| Fully qualified digest | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |

## Packaging Verification

Cloud Build output and Dockerfile inspection confirmed:

| Item | Evidence |
| --- | --- |
| BigQuery Storage package installed | Cloud Build installed `google-cloud-bigquery-storage-2.39.0` from `requirements.txt` |
| validate-warehouse script path included | Docker build step copied `scripts/run_bigquery_validations.py` to `./scripts/run_bigquery_validations.py` |
| validation SQL included | Docker build step copied `bigquery/validations/` to `./bigquery/validations/` |
| app runtime source included | Docker build copied `app.py`, `validate.py`, `src/`, and `data/` |
| image version args set | Cloud Build used `COMMIT_HASH=63149aa3d816` and `VERSION_LABEL=prod-candidate-63149aa3d816-20260626T040202Z` |

## Production Untouched Verification

Read-only production describe confirmed the expected production state after the build:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Current revision | `nfl-studio-dashboard-00075-x7p` |
| Traffic | 100 percent to `nfl-studio-dashboard-00075-x7p` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

Production flag state:

| Flag | Value |
| --- | --- |
| USE_COMPAT_PLAYER_PROFILES | `false` |
| USE_COMPAT_SLEEPER_WATCH | `false` |
| USE_COMPAT_TRADE_ASSETS | `false` |
| USE_COMPAT_TRADE_PLAYER_HISTORY | `false` |
| USE_COMPAT_VIEWER_TEAM_CONTEXT | `false` |
| USE_BACKTEST_DASHBOARD | `false` |
| USE_CLAIM_LEDGER_UI | `false` |
| USE_CONTENT_BRIEF_REVIEW_UI | `false` |
| USE_CLOUD_RUN_JOBS_FOR_DATA_OPS | `false` |
| DATA_OPS_ALLOW_JOB_TRIGGER | `false` |
| USE_TRADE_ANALYZER_SCORE_V0 | `false` |
| USE_COMPAT_TRADE_PLAYER_SCORE | `false` |

## Remaining Warnings

1. The working tree still has untracked historical validation reports retained for owner review.
2. Cloud Build output includes normal Debian noninteractive frontend warnings and pip root-user notices during image construction. The build succeeded.
3. This image has not been deployed to production. A separate gate phase is still required before any production cleanup deploy.

## Next Step

The production deploy gate may be run next for an all-flags-off production cleanup deploy decision, using the digest-pinned image:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4
```
