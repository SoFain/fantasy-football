# Phase 24.3 Production Deploy and Smoke Report

Validation date: 2026-06-25

## Final Decision

`PRODUCTION DEPLOY BLOCKED`

Production deploy was not run.

The Phase 24.3 prompt required deploy approval from `docs/rebuild/validation/phase-24-2-production-deploy-gate-report.md`, but that report says:

```text
PRODUCTION DEPLOY BLOCKED
```

The prompt also supplied this candidate image:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b
```

That is the old failed digest documented in Phase 24.1B. It was explicitly avoided by the successful live validate-warehouse proof. The fixed candidate approved by the rerun gate is:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29
```

Because this is a production deploy phase, the conflict is blocking. No deploy command was executed.

## Authorization State

`ALLOW_LIMITED_PRODUCTION_DEPLOY` was not set to `true` because the approval and image checks failed before the deploy block.

Post-check state:

```text
ALLOW_LIMITED_PRODUCTION_DEPLOY=
```

The requested final state is effectively false or unset. No production deploy authorization remains active from this phase.

## Approval Check

| Check | Result |
| --- | --- |
| `phase-24-2-production-deploy-gate-report.md` final decision | `PRODUCTION DEPLOY BLOCKED` |
| `phase-24-2r-production-deploy-gate-report.md` final decision | `APPROVED FOR PRODUCTION DEPLOY ALL FLAGS OFF` |
| Prompt-supplied candidate image | old failed `sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |
| Fixed approved candidate image | `sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| Deploy allowed from this prompt | no |

## Pre-Deploy Baseline

No production baseline was recaptured in this phase because deployment stopped at the approval gate. The latest captured baseline in the approved rerun gate is:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Current serving revision | `nfl-studio-dashboard-00074-26x` |
| Traffic split | `nfl-studio-dashboard-00074-26x:100%` |
| Current image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret reference | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |

## Deploy Command

No deploy command was run.

The command in the prompt was not run because it used the old failed digest. The safe deploy command should be regenerated from `docs/rebuild/validation/phase-24-2r-production-deploy-gate-report.md` and must use:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29
```

## Smoke Test

Smoke testing was not run because no production deploy occurred.

## Rollback

Rollback was not needed because production was not changed.

If a future deploy is approved and fails, the rollback baseline from the rerun gate remains:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00074-26x=100
```

## Production Final State

| Item | Result |
| --- | --- |
| Production deploy | not run |
| Production traffic | unchanged |
| Production feature flags | unchanged |
| Trade History compatibility in production | not enabled |
| Trade Analyzer score flags in production | not enabled |
| Data Ops job trigger flags in production | not enabled |
| Scheduler jobs | not created |
| Cloud Run Jobs | not triggered |
| LLM calls | not run |
| Scrape | not run |
| Firebase artifacts | none created |

## Required Correction

Rerun Phase 24.3 with the approved rerun gate report and fixed image:

- approval source: `docs/rebuild/validation/phase-24-2r-production-deploy-gate-report.md`;
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29`;
- all production risk flags and score flags set to `false`;
- `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` scoped only inside the deploy command session.
