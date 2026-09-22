# Phase 17.3 Immutable Image Tagging Report

Date: 2026-06-16

Final decision: IMAGE TAGGING READY

## Purpose

Split staging release artifacts away from the shared `latest` image tag and prepare future production releases to use immutable image tags.

No production deployment was run. No Cloud Run Jobs were triggered. No Firebase artifacts were created. No app runtime behavior was changed.

## Current Tag Behavior Before This Phase

`cloudbuild.yaml` previously built and pushed two tags:

- `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:${_IMAGE_TAG}`
- `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:latest`

Phase 16 staging deployed an explicit staging tag, but Cloud Build also refreshed `latest`. That made `latest` a misleading shared artifact even though production was not deployed.

## Changes Made

- Updated `cloudbuild.yaml` so Cloud Build tags, pushes, and records only `${_IMAGE_TAG}`.
- Added `scripts/build_image_tag.py` to generate immutable image tags.
- Added `tests/test_build_image_tag.py`.
- Updated `deploy_guide.md` with staging, production candidate, and production release tagging commands.
- Updated `docs/rebuild/release-checklist.md` with immutable image rules and release recording requirements.
- Added a Phase 17.3 image tagging addendum to `docs/rebuild/validation/phase-16-production-readiness-decision.md`.

## Tag Patterns

Staging:

```text
staging-<short_sha>-<timestamp>
```

Production candidate:

```text
prod-candidate-<short_sha>-<timestamp>
```

Production release:

```text
prod-<short_sha>-<release_id>
```

## Helper Commands

```powershell
.\venv\Scripts\python.exe scripts\build_image_tag.py --channel staging
.\venv\Scripts\python.exe scripts\build_image_tag.py --channel prod-candidate
.\venv\Scripts\python.exe scripts\build_image_tag.py --channel prod --release-id <release_id>
```

## Latest Status

`latest` is no longer produced by `cloudbuild.yaml`.

Existing historical `latest` tags may remain in Artifact Registry, but they are non-authoritative and must not be used for future deploy commands.

## How To Avoid Deploying Latest

1. Generate a tag with `scripts/build_image_tag.py`.
2. Build with `cloudbuild.yaml` and pass `_IMAGE_TAG=<generated_tag>`.
3. Deploy Cloud Run using the exact generated tag.
4. Record the image digest and Cloud Run revision in the phase report.
5. Roll back by moving traffic to the previous revision or redeploying the previous immutable tag.

## Validation

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
```

Results:

- Deployment safety checker: pass.
- Unit tests: 290 tests passed.
- `app.py` compile: pass.
- `src` and `scripts` compile: pass.
- Helper smoke check: `scripts\build_image_tag.py --channel staging --sha abcdef1234567890 --timestamp 20260616T120000Z` returned `staging-abcdef123456-20260616T120000Z`.

## Remaining Warnings

- Production remains unauthorized.
- Future staging and production reports must record the immutable tag, digest, service, revision, region, and rollback target.
- Artifact Registry may still contain old `latest` history. That is acceptable as long as deploy commands do not use it.
