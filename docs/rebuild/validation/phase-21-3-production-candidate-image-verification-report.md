# Phase 21.3 Production Candidate Image Verification Report

## Final Decision

`NEW PRODUCTION CANDIDATE BUILT`

The existing Phase 20.8 production candidate could not be verified as the release image because it predated the Phase 20.2B staging image that proved the Trade Lab summary-card fix. A new immutable production-candidate image was built from the current local source tree and verified in Artifact Registry.

No production deploy, staging deploy, Cloud Run Job trigger, Scheduler creation, LLM call, scrape, Firebase artifact creation, or runtime flag change was performed.

## Current Source State

| Item | Value |
| --- | --- |
| Git short SHA | `ce0eb82eef63` |
| Source tree state | dirty |
| Modified tracked files | `.gitignore`, `app.py`, `pipeline_execution.log`, `src/pipeline.py` |
| Runtime-critical untracked file | `src/ui_data_guards.py` |
| Test files untracked | `tests/test_pipeline_plan.py`, `tests/test_staging_ui_warning_fixes.py` |
| Release evidence untracked | Phase 17 through Phase 21 validation docs |

Release-critical file status:

| File | Tracked | Status | Runtime impact |
| --- | --- | --- | --- |
| `app.py` | yes | modified | yes |
| `src/ui_data_guards.py` | no | untracked | yes |
| `src/pipeline.py` | yes | modified | yes for pipeline CLI, not Streamlit startup |
| `tests/test_staging_ui_warning_fixes.py` | no | untracked | test only |
| `tests/test_pipeline_plan.py` | no | untracked | test only |

The Dockerfile copies `app.py`, `src/`, and `data/`. There is no `.gcloudignore`. `.dockerignore` does not exclude `app.py`, `src/`, or `data/`, so the Cloud Build source context for this local submit included the current app and `src` tree. Because the source tree is dirty, this image is tied to the local reviewed working tree rather than a clean commit state.

## Existing Candidate Assessment

Known Phase 20.8 production candidate:

| Field | Value |
| --- | --- |
| Tag | `prod-candidate-ce0eb82eef63-20260616T181911Z` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:6d26118c3fdf3ce10d1983a8cfddb05956f65c34463d4ef02bcce47cb37f25c4` |
| Build ID | `c81856f3-1b16-4585-a92a-4d507d6d5e1a` |

Assessment:

- It is immutable and digest-pinned.
- It shares the current HEAD prefix `ce0eb82eef63`.
- It predates the Phase 20.2B staging image that verified the Trade Lab summary-card fix.
- It has a different digest from the verified Phase 20.2B staging image.
- The current source tree contains uncommitted runtime changes and an untracked runtime helper file.

Decision: the existing candidate is not accepted as the current reviewed release candidate.

## Staging Image Comparison

Phase 20.2B staging evidence:

| Field | Value |
| --- | --- |
| Git short SHA | `ce0eb82eef63` |
| Staging image tag | `staging-ce0eb82eef63-20260617T021501Z` |
| Staging digest | `sha256:a669cb2d28d65a9aa14a9a008bf4a8c3754e9a2abb2c6e0d4345e79276752ce8` |
| Staging deployed image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:a669cb2d28d65a9aa14a9a008bf4a8c3754e9a2abb2c6e0d4345e79276752ce8` |
| Build ID | `e97627b2-5a23-4335-9ba1-214bcf9e98ec` |
| Final staging revision | `nfl-studio-dashboard-staging-00015-dcc` |
| QA status | `TRADE LAB SUMMARY STAGING QA PASS` |

The Phase 20.2B staging image is the proof image for the Trade Lab summary-card fix. The Phase 20.8 production candidate was built earlier, so it was superseded.

## Pre-Build Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | pass |
| `python -m unittest discover tests` | pass, 309 tests |
| `python -m py_compile app.py` | pass |
| `python -m compileall -q src scripts` | pass |
| `scripts/run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | pass, 149 validation files discovered |

Gcloud status:

| Item | Value |
| --- | --- |
| `gcloud` on PATH | no |
| Full path used | `C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd` |
| SDK version | `572.0.0` |
| Active account | `sofain@gmail.com` |
| Active project | `fantasy-football-498121` |

## Build Command

Generated tag:

```powershell
.\venv\Scripts\python.exe scripts\build_image_tag.py --channel prod-candidate
```

Output:

```text
prod-candidate-ce0eb82eef63-20260617T033954Z
```

Build command run:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit `
  --project=fantasy-football-498121 `
  --config=cloudbuild.yaml `
  --substitutions="_IMAGE_TAG=prod-candidate-ce0eb82eef63-20260617T033954Z,_COMMIT_HASH=ce0eb82eef63,_VERSION_LABEL=prod-candidate-ce0eb82eef63-20260617T033954Z" `
  .
```

## New Candidate Image

| Field | Value |
| --- | --- |
| Image tag | `prod-candidate-ce0eb82eef63-20260617T033954Z` |
| Image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260617T033954Z` |
| Digest | `sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31` |
| Build ID | `84ab90b6-97d4-4e8f-8a1a-9b3028380b86` |
| Build status | `SUCCESS` |
| Build create time | `2026-06-17T03:40:08.984260548Z` |
| Build finish time | `2026-06-17T03:42:40.244143Z` |
| Build service account | `projects/fantasy-football-498121/serviceAccounts/583607027760-compute@developer.gserviceaccount.com` |
| Supersedes Phase 20.8 candidate | yes |

Artifact Registry verification:

```json
{
  "digest": "sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31",
  "fully_qualified_digest": "us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31"
}
```

## Current Source Hashes

These hashes identify the reviewed local source files used for this candidate assessment:

| File | SHA256 |
| --- | --- |
| `app.py` | `5a4b1d172f09562048cb35acfae48ce85315d142e60229d85f11e937ccee3a88` |
| `src/pipeline.py` | `26853a94565343361a9908d37873fb87720aeea1c0b40f1026e7f5b3219eda99` |
| `src/ui_data_guards.py` | `e86739d4b0a6016810b7dff4d51d5765eed3cd57b35bedb241fd0706dd9abe97` |
| `tests/test_pipeline_plan.py` | `1ebed064d91541c6b96e53095781d1e6dd24a8302cf532b01d6a198e66977b83` |
| `tests/test_staging_ui_warning_fixes.py` | `1016a2324a021012c3b139fa3d124bda7bf415ec00347e63a4511889b18cdb6c` |
| `cloudbuild.yaml` | `415fddce71c2f92f77cb2c5564e0797e57c565d7f314b8859b3d3d0bdde91774` |
| `Dockerfile` | `c27059ccb995175c134daa3f95d276c731859ec1ae71ce93fade13ace54810f5` |

## Trade Lab Fix Inclusion

The current local source includes the Phase 20 Trade Lab summary-card fix:

- `app.py` imports `collect_selected_trade_assets`, `unresolved_trade_asset_labels`, `ensure_player_profile_display_columns`, and `ensure_sleeper_watch_display_columns` from `src.ui_data_guards`.
- `app.py` applies Side A and Side B asset collection through the shared guard helpers.
- `app.py` renders Side B Summary from resolved Side B assets and reports unresolved labels cleanly.
- `app.py` still shows the staging-only marker `Trade player history source: compat_trade_player_history` when that flag is enabled.
- `tests/test_staging_ui_warning_fixes.py` covers Side A, Side B, missing `pos_abb`, missing `rolling_3_week_ppr`, and feature flag defaults.

Because the image was built from the local source tree after those files were present, this candidate supersedes the old Phase 20.8 candidate for future deploy preview work.

## Warnings

| Warning | Impact |
| --- | --- |
| Source tree was dirty at build time | The image includes the current local reviewed source, but its tag references `ce0eb82eef63` while release-critical changes are not fully committed. Rebuild after commit if clean commit provenance is required. |
| `pipeline_execution.log` remains tracked and modified | It is excluded from future ignore patterns, but because it is already tracked it still needs restore, untrack, or explicit owner review before merge. |
| Production deploy remains blocked | Phase 20.8 still says `PRODUCTION DEPLOY BLOCKED`, and this build does not authorize production deployment. |
| Live validate-warehouse proof remains unresolved | Phase 21.1 still says `LIVE VALIDATE-WAREHOUSE STILL BLOCKED`. |

## Production Safety

| Safety item | Status |
| --- | --- |
| Production deploy | not run |
| Staging deploy | not run |
| Cloud Run Jobs | not triggered |
| Scheduler jobs | not created |
| LLM calls | not run |
| Scraping | not run |
| Firebase artifacts | none created |
| `latest` image tag | not used |
| Immutable tag | used |
| Digest-pinned image | recorded |

## Next Step

Use this digest for the next limited production deploy preview only after the release package is reviewed:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31
```

Before any production deploy, resolve or explicitly accept:

1. Dirty-tree provenance warning.
2. `pipeline_execution.log` tracked diff.
3. Live validate-warehouse proof blocker or formal waiver.
4. Explicit `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` authorization.
