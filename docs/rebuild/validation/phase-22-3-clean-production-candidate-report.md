# Phase 22.3 Clean Production Candidate Report

## Final Decision

`PRODUCTION CANDIDATE BLOCKED`

No production-candidate image was built in Phase 22.3.

The code and validation checks pass, and `pipeline_execution.log` is no longer modified. However, the source tree is still dirty and contains release-critical modified and untracked files that Phase 22.1 explicitly classified as needing human review before commit. Building now would produce another candidate tied to an uncommitted local source tree rather than a clean release commit.

## Scope

Phase 22.3 was build/verify only.

Not performed:

- no production deploy;
- no staging deploy;
- no Cloud Run Job trigger;
- no Scheduler job creation;
- no LLM call;
- no scraping;
- no Firebase artifact creation;
- no Cloud Build image build;
- no Artifact Registry image mutation.

## Source State

Command results:

| Command | Result |
| --- | --- |
| `git rev-parse --short=12 HEAD` | `ce0eb82eef63` |
| `git status --short` | dirty |
| `git diff --stat` | modified tracked files present |
| `git ls-files --others --exclude-standard` | untracked release docs, source helper, and tests present |

Tracked modifications:

| File | Status | Release impact |
| --- | --- | --- |
| `.gitignore` | modified | release packaging cleanup |
| `app.py` | modified | runtime UI fixes |
| `src/load.py` | modified | source ingest schema hardening |
| `src/pipeline.py` | modified | plan-only and ingest-only safety behavior |

Release-critical untracked files:

| File | Status | Release impact |
| --- | --- | --- |
| `src/ui_data_guards.py` | untracked | required by current `app.py` imports and UI fixes |
| `tests/test_pipeline_plan.py` | untracked | tests source restore and schema hardening behavior |
| `tests/test_staging_ui_warning_fixes.py` | untracked | tests staging UI warning fixes |
| `docs/rebuild/modern-source-data-restore.md` | untracked | operational source restore docs |
| `docs/rebuild/trade-analyzer-scoring-model-v0.md` | untracked | Phase 21.8 spec |
| Phase 17 through Phase 22 validation reports | untracked | full audit trail docs |

Generated artifact status:

| Artifact | Status |
| --- | --- |
| `pipeline_execution.log` | not modified |
| `output/` | ignored and not returned by `git ls-files --others --exclude-standard` |
| `*.log` files | ignored |

## Clean Provenance Decision

The tree is not clean and is not staged into a reviewed release commit.

Phase 22.1 classified the package as `RELEASE PACKAGE CLEAN WITH WARNINGS`, with these relevant warnings:

- source and test changes are classified but still need human review;
- Phase 17 through Phase 21 validation docs remain untracked and should be reviewed before commit;
- no commit was created;
- a clean candidate should be rebuilt after the release package is committed if clean provenance is required.

Decision:

- Do not build a new candidate from the current dirty tree.
- Do not accept the existing Phase 21.3 candidate as a clean-provenance candidate.
- Keep the Phase 21.3 image as a preview artifact only.

## Build Context Review

`cloudbuild.yaml` builds and pushes:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:${_IMAGE_TAG}
```

`Dockerfile` copies:

```text
app.py
validate.py
src/
data/
```

Build context notes:

- There is no `.gcloudignore`.
- `.dockerignore` excludes virtualenvs, caches, logs, `pipeline_execution.log`, `*.json`, build outputs, `.git`, and IDE folders.
- `app.py` imports `src.ui_data_guards`, so a build must include the untracked `src/ui_data_guards.py`.
- A local `gcloud builds submit .` would likely include the current untracked source helper unless ignored, but the image would still be tied to uncommitted local state.

## Pre-Build Checks

Safe pre-build checks were run even though the image build was blocked.

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 314 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass, validation catalog discovered |

Safety checker details:

| Check | Result |
| --- | --- |
| No Firebase artifacts | pass |
| No tracked secret files | pass |
| No secret content | pass |
| Required files exist | pass |
| Feature flags default off | pass |
| Pigskin `execute_bigquery_sql` absent | pass |
| `app.py` compiles | pass |
| `src` and `scripts` compile | pass |

## Image Tag

No image tag was generated.

Reason:

- source provenance gate failed before the image-tag step;
- generating a tag without building would create unnecessary release noise.

Expected future command after a clean release commit:

```powershell
.\venv\Scripts\python.exe scripts\build_image_tag.py --channel prod-candidate
```

## Build Command

Cloud Build was not run.

Expected future command after clean release state:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit `
  --project=fantasy-football-498121 `
  --config=cloudbuild.yaml `
  --substitutions="_IMAGE_TAG=<tag>,_COMMIT_HASH=<short_sha>,_VERSION_LABEL=<tag>" `
  .
```

## Artifact Registry Verification

No new image was built, so no new Artifact Registry verification was performed.

Latest existing candidate from Phase 21.3 remains:

| Field | Value |
| --- | --- |
| Image tag | `prod-candidate-ce0eb82eef63-20260617T033954Z` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31` |
| Build ID | `84ab90b6-97d4-4e8f-8a1a-9b3028380b86` |
| Build status | `SUCCESS` |
| Status | preview artifact only, not clean provenance |

## Warnings

| Warning | Impact |
| --- | --- |
| Source tree is dirty | Blocks clean production-candidate rebuild |
| Release-critical source helper is untracked | A clean commit is needed before build provenance is acceptable |
| Release-critical tests are untracked | Test provenance is not tied to commit |
| Phase validation docs are untracked | Release evidence still needs human review and commit decision |
| Existing Phase 21.3 image was built from dirty local source | Keep as preview only unless explicitly accepted |

## Required Next Step

To build a clean production candidate:

1. Human-review the Phase 22.1 release package.
2. Stage and commit the approved source, tests, docs, and `.gitignore` changes.
3. Confirm `git status --short` is clean or only contains intentionally ignored local files.
4. Re-run Phase 22.3.
5. Build a new immutable `prod-candidate-<short_sha>-<timestamp>` image from that clean commit.

## Production Status

Production remains untouched.

No deploy, trigger, Scheduler job, LLM call, scrape, Firebase artifact, or production flag change occurred in this phase.
