# Phase 24.1A Validate-Warehouse Image Path Fix Report

Validation date: 2026-06-19

## Final Decision

`VALIDATE-WAREHOUSE IMAGE PATH FIX READY WITH WARNINGS`

The container packaging issue that caused Phase 24.1 to fail has been fixed in the Dockerfile and a new digest-pinned production candidate image has been built. The new image includes `scripts/run_bigquery_validations.py` and `bigquery/validations/` at the paths expected by `src.job_runner.dispatch_validate_warehouse`.

Warning: the live `validate-warehouse` proof was not rerun in this phase by design. Phase 24.1B or the next live-proof phase still needs to deploy/update only `validate-warehouse` with the new image and execute one narrow proof.

No production deploy, staging deploy, Cloud Run Job trigger, Scheduler job creation, IAM change, LLM call, scrape, ingestion, materialization, Firebase artifact creation, or production feature flag change was performed.

## Root Cause

Phase 24.1 failed because the Cloud Run Job ran this path inside the container:

```text
/app/scripts/run_bigquery_validations.py
```

The digest-pinned image from Phase 23.9 did not contain that file. The Dockerfile copied:

```dockerfile
COPY app.py validate.py ./
COPY src/ ./src/
COPY data/ ./data/
```

It did not copy `scripts/` or `bigquery/validations/`.

`src.job_runner.dispatch_validate_warehouse` correctly invoked:

```python
cmd = [
    sys.executable,
    "scripts/run_bigquery_validations.py",
    "--project",
    args.project,
    "--dataset",
    args.dataset,
]
```

The image layout was incomplete for Cloud Run Jobs. The app runtime could start, but the `validate-warehouse` worker path was missing its validation runner and SQL assets.

## Fix

Changed `Dockerfile` to package the exact runtime assets required by `validate-warehouse`:

```dockerfile
COPY scripts/run_bigquery_validations.py ./scripts/run_bigquery_validations.py
COPY bigquery/validations/ ./bigquery/validations/
```

No job runner bypass was added. The live proof requirement remains intact.

## Files Changed

| File | Change |
| --- | --- |
| `Dockerfile` | Copies `scripts/run_bigquery_validations.py` and `bigquery/validations/` into `/app`. |
| `tests/test_validate_warehouse_image_packaging.py` | Adds packaging and dispatcher path regression tests. |
| `tests/test_cloud_run_jobs.py` | Adds a dry-run command test for `validate-warehouse` with narrow `model_runs` pattern. |

## Tests Added

New test coverage proves:

- the Dockerfile packages `scripts/run_bigquery_validations.py`;
- the Dockerfile packages `bigquery/validations/`;
- `dispatch_validate_warehouse` still invokes the packaged script path;
- the validation pattern is passed through as a bounded pattern;
- the Cloud Run Job dry-run command for `validate-warehouse` includes `--pattern,model_runs`;
- no run-after-deploy path appears in that dry-run command.

Existing tests continue to cover:

- Cloud Run Job triggers are default off;
- live triggers require explicit flags and confirmation;
- sensitive environment overrides are rejected;
- Pigskin arbitrary SQL remains absent;
- feature flags remain default off.

## Local Check Results

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_validate_warehouse_image_packaging tests.test_cloud_run_jobs tests.test_job_runner` | pass, 34 tests |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 346 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass, validation discovery completed |

## Build

Command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit `
  --project=fantasy-football-498121 `
  --config=cloudbuild.yaml `
  --substitutions="_IMAGE_TAG=prod-candidate-ce0eb82eef63-20260619T171558Z,_COMMIT_HASH=ce0eb82eef63,_VERSION_LABEL=prod-candidate-ce0eb82eef63-20260619T171558Z" `
  .
```

Build result:

| Field | Value |
| --- | --- |
| Build ID | `4b53f49e-90ca-4f1e-ba76-530fef1fee98` |
| Build status | `SUCCESS` |
| Build created | `2026-06-19T17:16:01Z` |
| Build finished | `2026-06-19T17:18:00Z` |
| Source SHA | `ce0eb82eef63` |
| Image tag | `prod-candidate-ce0eb82eef63-20260619T171558Z` |
| Image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260619T171558Z` |
| New digest | `sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| Old failing digest | `sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |
| New digest differs from old | yes |

The local command surfaced PowerShell stderr handling as a local output issue, but Cloud Build itself completed successfully and Artifact Registry verification confirmed the pushed image digest.

## Image Path Evidence

Cloud Build logs show the Dockerfile copy steps:

```text
Step #0: Step 8/16 : COPY scripts/run_bigquery_validations.py ./scripts/run_bigquery_validations.py
Step #0: Step 9/16 : COPY bigquery/validations/ ./bigquery/validations/
Step #0: Successfully tagged us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260619T171558Z
Step #1: prod-candidate-ce0eb82eef63-20260619T171558Z: digest: sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29 size: 3044
```

This is sufficient evidence that the expected script and validation SQL directory are included in the new image layers.

## Production Impact

| Item | Result |
| --- | --- |
| Production service deploy | not run |
| Staging service deploy | not run |
| Cloud Run Job trigger | not run |
| Scheduler job creation | not run |
| IAM change | not run |
| Production feature flags | unchanged |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | not set |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | not set |
| Firebase artifacts | none created |

## Remaining Warning

The image was built from the current reviewed dirty worktree, consistent with prior Phase 23 candidate builds. Release provenance should still be handled by the release package cleanup and commit process.

The live `validate-warehouse` proof remains required before production deploy can be approved. Use the new digest-pinned image in the next proof:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29
```
