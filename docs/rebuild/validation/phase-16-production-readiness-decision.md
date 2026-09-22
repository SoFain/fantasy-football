# Phase 16 Production Readiness Decision

Date: 2026-06-16

Decision: STAGING ONLY

This decision does not authorize a production deployment. Production remains untouched until the operator explicitly approves a separate production release.

## Rationale

The rebuild is healthy enough to keep validating in staging, but it is not ready for production.

The hard safety gates are clean: tests pass, the app compiles, migrations have no pending work, key validation patterns pass, Pigskin arbitrary SQL remains absent, raw/source tables remain blocked from Pigskin-visible paths, no tracked secrets were detected, no Firebase artifacts were introduced, and production feature flags remain default false.

The remaining release gaps are operational rather than code blockers:

- Staging deployed successfully, but only basic health and server-side checks were completed.
- Trade History compat is explicitly recommended to stay in staging.
- Authenticated browser-click QA for Trade Lab was not completed.
- The live `validate-warehouse` Cloud Run Job path was not authorized or proven.
- Real claim data was not supplied, so claim grading and Meatbag Accountability remain demo/draft or empty-state workflows.
- Real packet expansion improved with Fraud Watch, but current production-ready segment coverage still needs more source-data work.

## Hard Gate Review

| Gate | Status | Evidence |
|---|---:|---|
| Tests pass | Pass | `.\venv\Scripts\python.exe -m unittest discover tests`: 285 tests passed |
| App compiles | Pass | `.\venv\Scripts\python.exe -m py_compile app.py`: pass |
| `src` and `scripts` compile | Pass | `.\venv\Scripts\python.exe -m compileall -q src scripts`: pass |
| Migrations pending | Pass | `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations |
| Validation dry-run | Pass | `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: pass |
| Backtest validations | Pass | 11 passed, 0 failed |
| Market validations | Pass | 9 passed, 0 failed |
| Claim validations | Pass with expected info warnings | 17 passed, 0 failed; demo/draft warnings remain expected |
| Content brief validations | Pass | 11 passed, 0 failed |
| Cloud Run job validations | Pass | 8 passed, 0 failed |
| Trade History compat validations | Pass | 6 passed, 0 failed |
| Pigskin arbitrary SQL absent | Pass | Safety checker passed |
| Raw/source tables blocked from Pigskin | Pass | Safety checker and Pigskin tests remain green |
| Tracked secrets | Pass | Safety checker found no tracked secret files or secret content |
| Firebase artifacts | Pass | Safety checker found none |
| Production feature defaults | Pass | Risk flags remain default false |
| Staging rollback | Pass | `USE_COMPAT_TRADE_PLAYER_HISTORY` rollback was tested in staging |
| Live Cloud Run Job path | Deferred | `validate-warehouse` live test was not authorized |

## Blockers

These block production promotion:

- Authenticated staging UI QA is incomplete. Health checks passed, but full browser-click QA for Trade Lab and related tabs was not completed.
- `USE_COMPAT_TRADE_PLAYER_HISTORY=true` is only cleared for staging. It is not cleared for production.
- The live `validate-warehouse` Cloud Run Job deploy/trigger path remains unproven because authorization and required environment variables were missing.
- Real reviewed claims were not provided, so claim grading and Meatbag Accountability cannot be production-signaled yet.
- Real trade-review inputs were not provided, so trade-review packets remain blocked.

## Warnings

- Staging build/deploy reported a shared `latest` image tag warning. Production release should use an explicit immutable image tag.
- One old local dry-run `validate-warehouse` metadata row remains documented as a dry-run artifact, not a live Cloud Run execution.
- Claim tables contain demo/draft sample rows, including one intentionally unresolved draft row. These must not be used for public content.
- Fraud Watch packet materialization now has a real historical source slice, but it is not a current-week production content source.
- Content brief review has deterministic inputs, but the show-writing layer should not treat draft briefs as approved.

## Allowed Actions

- Open or merge the rebuild PR after human review.
- Keep the rebuild branch deployed to staging.
- Keep `USE_COMPAT_TRADE_PLAYER_HISTORY=true` enabled in staging only.
- Continue deterministic staging QA for Trade Lab, content brief review, claim ledger, and packet workflows.
- Run additional validations from the local venv.
- Prepare a future production deploy plan with all risk flags off.

## Disallowed Actions

- Do not deploy to production from this decision.
- Do not enable `USE_COMPAT_TRADE_PLAYER_HISTORY=true` in production.
- Do not enable any other compatibility flag in production.
- Do not enable Cloud Run Job triggers in production.
- Do not create scheduler jobs.
- Do not publish demo claims, demo packets, or draft content briefs.
- Do not auto-grade demo claims.
- Do not call LLMs as part of release validation unless explicitly authorized.

## Feature Flag State

Recommended production state today:

```text
USE_COMPAT_PLAYER_PROFILES=false
USE_COMPAT_SLEEPER_WATCH=false
USE_COMPAT_TRADE_ASSETS=false
USE_COMPAT_TRADE_PLAYER_HISTORY=false
USE_COMPAT_VIEWER_TEAM_CONTEXT=false
USE_BACKTEST_DASHBOARD=false
USE_CLAIM_LEDGER_UI=false
USE_CONTENT_BRIEF_REVIEW_UI=false
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

Recommended staging state for continued QA:

```text
USE_COMPAT_TRADE_PLAYER_HISTORY=true
all other risk flags=false
```

## Rollback Plan

Staging Trade History compat rollback:

```powershell
gcloud run services update nfl-studio-dashboard-staging `
  --region us-central1 `
  --project fantasy-football-498121 `
  --remove-env-vars USE_COMPAT_TRADE_PLAYER_HISTORY
```

Staging service rollback:

```powershell
gcloud run services update-traffic nfl-studio-dashboard-staging `
  --region us-central1 `
  --project fantasy-football-498121 `
  --to-revisions <previous-stable-revision>=100
```

Future production rollback, if a later production release is approved:

- Keep all risk flags false.
- Move traffic back to the previous production revision.
- Revert to the previous immutable image tag.
- Keep Cloud Run Job trigger flags disabled.
- Do not roll forward compat flags during incident response.

## Next Production Step

The next production candidate should be a limited production deploy with all flags off, not a Trade History flag deploy.

Before that production candidate:

1. Complete authenticated staging browser QA.
2. Use an immutable image tag instead of relying on `latest`.
3. Decide whether the live `validate-warehouse` Cloud Run Job test is required before production, or explicitly defer it.
4. Confirm staging rollback one more time after the final image is selected.
5. Re-run safety, tests, migrations, and validation dry-run immediately before release.

## Phase 17 Backlog

1. Complete authenticated staging UI QA for Pigskin Studio, Show Prep, Player Profiles, Trade Lab, and Data Ops.
2. Prove the live `validate-warehouse` Cloud Run Job path with required authorization and explicit image/service account configuration.
3. Add operator-supplied real claims and move reviewed claims toward `ready_to_grade`.
4. Add real viewer/operator trade inputs so `trade_review_packets` can materialize without demo data.
5. Materialize current-season Fraud Watch source rows or document the current-season dependency.
6. Split staging release artifacts from shared `latest` tagging.
7. Clean or close the old dry-run Cloud Run job metadata artifact if mutation becomes safe.
8. Continue one-flag-at-a-time compatibility rollout after staging QA evidence is captured.

## Phase 17.3 Image Tagging Addendum

Phase 17.3 closes the shared `latest` warning by making Cloud Build publish only the explicit `_IMAGE_TAG` image. The release process now requires immutable tags:

- Staging: `staging-<short_sha>-<timestamp>`
- Production candidate: `prod-candidate-<short_sha>-<timestamp>`
- Production release: `prod-<short_sha>-<release_id>`

Production remains unauthorized by this addendum. Future production work must build and deploy a reviewed immutable production candidate or production release tag, not a mutable staging or `latest` tag.
