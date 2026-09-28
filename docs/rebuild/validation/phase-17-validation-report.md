# Phase 17 Validation Report

Date: 2026-06-16

Final decision: PR/STAGING ONLY

Production readiness: not approved

## Scope

Validated Phase 17:

- PR artifact readiness
- authenticated staging browser QA
- immutable image tagging
- live `validate-warehouse` Cloud Run Job proof
- real claim intake
- real trade-review packets
- current-season Fraud Watch source status
- limited production candidate plan

No production deploy was run. No migrations were applied. No Cloud Run Jobs were triggered. No LLM calls were made. No scraping occurred. No Firebase artifacts were created.

## Command Results

Repo and safety:

```text
git status --short: clean
git diff --stat: clean
scripts/check_deployment_safety.py: pass
```

Compile and tests:

```text
app.py compile: pass
src and scripts compile: pass
unit tests: 290 passed
```

Migration and validation:

```text
run_bigquery_migrations.py --list-pending: No pending migrations.
run_bigquery_validations.py --dry-run: pass, 149 validation files discovered.
compat_trade_player_history: 6 passed, 0 failed, 1 informational warning with missing_identity_rate=0.0.
cloud_run_job: 8 passed, 0 failed.
content_brief: 11 passed, 0 failed.
claim: 17 passed, 0 failed, expected informational warnings for draft/demo claim state.
```

## Required Reports

All required Phase 17 reports exist:

| Report | Status |
|---|---|
| `phase-17-1-pr-artifact-readiness-report.md` | present |
| `phase-17-2-authenticated-staging-qa-report.md` | present |
| `phase-17-3-immutable-image-tagging-report.md` | present |
| `phase-17-4-live-validate-warehouse-job-report.md` | present |
| `phase-17-5-real-claims-ready-report.md` | present |
| `phase-17-6-real-trade-review-packet-report.md` | present |
| `phase-17-7-current-season-fraud-watch-report.md` | present |
| `phase-17-8-production-candidate-plan.md` | present |

## Blockers

These block production promotion:

1. Production-candidate image was planned but not built because `gcloud` is missing from PATH.
2. Current production service state and previous production revision were not captured because `gcloud` is unavailable.
3. Live `validate-warehouse` Cloud Run Job proof remains not authorized and not executed.
4. Real claims remain blocked by missing operator-supplied exact claim text.
5. Real Trade Review packets remain blocked by missing operator/viewer trade sides.
6. Current-season Fraud Watch remains blocked because current warehouse `analytics_player_weekly_truth`, `weekly_metrics`, and `play_by_play` do not contain 2025 or 2026 source rows.
7. Staging browser QA passed with warnings in legacy Player Profiles, Versus Finder, Show Prep Sleeper Watch, and Trade Lab Side B display behavior.

## Warnings

- `compat_trade_player_history` validation includes an informational identity coverage row, but missing identity rate is `0.0`.
- Claim validations include expected informational warnings from draft/demo claim data.
- Historical Fraud Watch packets exist and are valid as historical proof, but they are not current-week production content.
- The production-candidate plan is prepared, but final recommendation remains `NOT READY` until the immutable image is built and recorded.
- Demo claims and packet examples must remain excluded from public content.

## Staging QA Status

Status: pass with warnings.

Evidence:

- Staging service loaded.
- Authenticated browser QA was completed.
- Pigskin Studio rendered without exposing arbitrary SQL.
- Data Ops rendered with Cloud Run Jobs disabled.
- Trade Lab staging compat path was validated, but Trade History remains staging-only.

Remaining staging warnings:

- Player Profiles legacy path has a missing `pos_abb` issue.
- Versus Finder inherits the same legacy profile issue.
- Show Prep Sleeper Watch legacy path has a missing `rolling_3_week_ppr` issue.
- Trade Lab Side B display behavior needs follow-up.

## Live Job Status

Status: not authorized.

`phase-17-4-live-validate-warehouse-job-report.md` shows:

- `gcloud` missing from PATH.
- authorization env vars missing.
- explicit service account or waiver missing.
- dry-run deploy preview and narrow execute preview succeeded.
- no live deploy or trigger was run.

Cloud Run Job validations passed:

```text
8 passed, 0 failed
```

Cloud Run Jobs remain not triggerable by default.

## Real Claim Status

Status: blocked.

`data/real_claim_import_template.csv` is header-only. No operator-supplied real claim rows exist.

Existing claim state:

- 3 claims
- all draft
- 0 claim grades
- demo/sample claims remain draft-only

No scraping, LLM calls, or fabricated claims occurred.

## Trade Packet Status

Status: blocked.

No operator or viewer trade sides were supplied. `trade_review_packets` remains empty.

Supporting compat data exists:

- `compat_trade_assets_current`: 1,383 rows
- `compat_trade_player_history`: 55,617 rows
- `compat_player_profiles_current`: 27,864 rows

No fake trade inputs or demo trade packets were created.

## Current Fraud Watch Status

Status: blocked for current-season production content.

Current state:

- `analytics_fraud_watch` has rows only for 2014 through 2016.
- `analytics_player_weekly_truth` has rows only for 2014 through 2016.
- `weekly_metrics` and `play_by_play` have no 2025 or 2026 source rows in the current warehouse state.
- Existing `fraud_watch_packets` are historical-only: 2016 week 17.

Production suitability:

```text
historical-only
```

Historical Fraud Watch must not be presented as current-week production content.

## Immutable Image Status

Status: ready at build-process level.

`cloudbuild.yaml` now publishes only explicit `_IMAGE_TAG`. It no longer publishes container-image `latest`.

Planned production candidate tag from Phase 17.8:

```text
prod-candidate-57ab102c8656-20260616T165242Z
```

Registry URI:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-57ab102c8656-20260616T165242Z
```

Build status:

```text
not built
```

Reason: `gcloud` unavailable in this shell.

## Production Candidate Status

Classification: not ready.

The production candidate plan exists and uses all risk flags off, but the candidate image was not built and production state was not captured.

Required production flag state remains:

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

Do not approve:

- production with `USE_COMPAT_TRADE_PLAYER_HISTORY=true`
- production with job triggers enabled
- production with unreviewed claims or packets presented as public content

## Hard Safety Checks

| Gate | Status |
|---|---|
| Pigskin arbitrary SQL absent | pass |
| `execute_bigquery_sql` absent from Pigskin-visible code | pass |
| Raw/source tables blocked from Pigskin schema | pass |
| Production flags safe in plan | pass |
| No tracked secrets | pass |
| No Firebase artifacts | pass |
| No scheduler jobs created | pass |
| Cloud Run Jobs not triggerable by default | pass |
| Demo claims/packets excluded from public content | pass |
| Production deploy without authorization | pass, no production deploy occurred |

## Recommended Phase 18 Work

1. Install or expose `gcloud`, authenticate to `fantasy-football-498121`, and build the immutable production-candidate image.
2. Capture current production service metadata and previous production revision before any deploy.
3. Decide whether to keep production at staging-only or approve a limited production deploy with all risk flags off.
4. Fix staging QA warnings in legacy Player Profiles, Versus Finder, Sleeper Watch, and Trade Lab Side B display.
5. Run an authorized live `validate-warehouse` Cloud Run Job proof, or explicitly defer it for production.
6. Ingest or restore modern `weekly_metrics` and `play_by_play` rows so current-season Fraud Watch can be built honestly.
7. Add operator-supplied real claims and real trade inputs.
8. Keep Trade History compatibility staging-only until production promotion is separately approved.

## Final Decision

PR/STAGING ONLY

Phase 17 is safe for PR and continued staging work. It is not ready for production promotion because the production-candidate image was not built, live job proof is deferred, real content inputs are missing, and current-season Fraud Watch source data is unavailable.
