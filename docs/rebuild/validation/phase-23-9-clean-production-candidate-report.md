# Phase 23.9 Clean Production Candidate Report

Date: 2026-06-19

## Final Decision

`CLEAN PRODUCTION CANDIDATE BUILT WITH WARNINGS`

A new immutable production-candidate image was built and verified. No production deploy, staging deploy, Cloud Run Job trigger, Scheduler job, LLM call, scrape, or Firebase artifact creation was performed.

Primary warning:

- The source tree is still dirty and contains modified plus untracked release files. Phase 23.1 classified the package as `RELEASE PACKAGE READY WITH WARNINGS`, and this Phase 23.9 prompt requested a build from that reviewed release state. The image is therefore digest-pinned and verified, but its provenance is a reviewed dirty worktree rather than a clean Git commit.

## Source State

| Item | Result |
| --- | --- |
| Git short SHA | `ce0eb82eef63` |
| Git status | dirty, reviewed release package with warnings |
| Tracked modified files | 9 |
| Untracked release candidates | present |
| Generated artifacts in Cloud Build upload preview | none matched `output/`, `node_modules`, or `pipeline_execution.log` |
| Cloud Build upload preview file count | 493 |
| `.gcloudignore` | not present |

Tracked modified files:

```text
.gitignore
app.py
docs/rebuild/compatibility-contracts.md
docs/rebuild/table-classification.md
docs/rebuild/ui-query-debt-register.md
src/compat_flags.py
src/load.py
src/pipeline.py
tests/test_streamlit_compat_rollout.py
```

Important untracked release files include:

```text
src/trade_player_scores.py
src/ui_data_guards.py
tests/test_pipeline_plan.py
tests/test_staging_ui_warning_fixes.py
tests/test_trade_player_scores.py
bigquery/migrations/0025__trade_analyzer_score_v0.sql
bigquery/views/trade_player_scores_current.sql
bigquery/views/compat_trade_player_scores_current.sql
bigquery/contracts/*.md
bigquery/validations/150_trade_player_scores_grain.sql through 160_trade_player_scores_identity_coverage.sql
docs/rebuild/validation/phase-17-*.md through phase-23-8-*.md
```

Owner acceptance basis:

- Phase 23.1 classified the package as ready with warnings.
- This Phase 23.9 instruction requested a build from the reviewed release state.
- Generated artifacts remain excluded from the build upload preview.

## Pre-Build Checks

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

| Check | Result |
| --- | --- |
| Deployment safety | pass |
| Unit tests | pass, 343 tests |
| `app.py` compile | pass |
| `src` and `scripts` compile | pass |
| Pending migrations | none |
| Validation dry-run | pass, 160 validation files discovered |

Safety checker details:

| Check | Result |
| --- | --- |
| No Firebase artifacts | pass |
| No tracked secret files | pass |
| No detected secret content | pass |
| Required files exist | pass |
| Feature flags default off | pass |
| Pigskin `execute_bigquery_sql` absent | pass |
| `app.py` compiles | pass |
| `src` and `scripts` compile | pass |

Migration note:

- Phase 22 expected migration `0025` to be pending if intentionally not applied.
- Current Phase 23.9 check shows no pending migrations, which is consistent with Phase 23.2 having applied migration `0025`.

## Image Tag

Generated command:

```powershell
.\venv\Scripts\python.exe scripts\build_image_tag.py --channel prod-candidate
```

Generated tag:

```text
prod-candidate-ce0eb82eef63-20260619T041320Z
```

## Build Command

Command run:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit --project=fantasy-football-498121 --config=cloudbuild.yaml --substitutions="_IMAGE_TAG=prod-candidate-ce0eb82eef63-20260619T041320Z,_COMMIT_HASH=ce0eb82eef63,_VERSION_LABEL=prod-candidate-ce0eb82eef63-20260619T041320Z" .
```

Build log was written locally to:

```text
output/phase-23-9-cloudbuild.log
```

This is a generated local log and is not a commit candidate.

## Build Result

| Field | Value |
| --- | --- |
| Build ID | `4158cf71-6fbe-4a19-9252-0b8c0dc59cff` |
| Build status | `SUCCESS` |
| Source SHA label | `ce0eb82eef63` |
| Image tag | `prod-candidate-ce0eb82eef63-20260619T041320Z` |
| Image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260619T041320Z` |
| Digest | `sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |
| Build create time | `2026-06-19T04:13:36.420067626Z` |
| Build finish time | `2026-06-19T04:16:01.711995Z` |

Artifact Registry verification:

```json
{
  "digest": "sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b",
  "fully_qualified_digest": "us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b"
}
```

## Runtime Flag Defaults

Feature flag implementation confirms default false behavior:

```python
return str(env.get(flag_name, "false")).strip().lower() in TRUE_VALUES
```

Default-off flags include:

- `USE_TRADE_ANALYZER_SCORE_V0`
- `USE_COMPAT_TRADE_PLAYER_SCORE`
- `USE_COMPAT_TRADE_PLAYER_HISTORY`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS`
- `DATA_OPS_ALLOW_JOB_TRIGGER`

## Deployment Status

Read-only service checks after the build:

| Service | Revision | Image |
| --- | --- | --- |
| production `nfl-studio-dashboard` | `nfl-studio-dashboard-00074-26x` | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| staging `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00018-cpz` | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:1fe0253f07332361a5f54e1a654477920de7ad4b0813cef2806acd5be4f4ebc2` |

No Cloud Run service was deployed or updated.

## Warnings

| Warning | Impact |
| --- | --- |
| Source tree is dirty | Candidate is verified and digest-pinned, but not reproducible from only the committed Git SHA. |
| Untracked source and validation files are part of the reviewed release package | Commit or stage review should happen before a final release PR or future clean rebuild. |
| `.gcloudignore` is absent | `gcloud meta list-files-for-upload` did not show generated `output/` artifacts, but adding an explicit `.gcloudignore` would make future build context behavior clearer. |
| Build uses mutable source context plus immutable output tag | The output image is immutable by digest, but source provenance should be called out in release notes. |

## Acceptance Criteria

| Criterion | Status |
| --- | --- |
| no deployment | pass |
| candidate immutable and digest-pinned | pass |
| candidate source reviewed | pass with dirty-worktree warning |
| tests and safety pass | pass |
| no Firebase artifacts | pass |
