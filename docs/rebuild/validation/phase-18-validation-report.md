# Phase 18 Validation Report

Date: 2026-06-16

Final decision: GO WITH WARNINGS

Production status: PRODUCTION CANDIDATE READY, NOT DEPLOYED

No production deploy was run. No migrations were applied. No Cloud Run Jobs were triggered. No LLM calls were made. No scraping occurred. No Firebase artifacts were created.

## Scope

Validated Phase 18:

- immutable production-candidate image
- production service baseline capture
- staging QA warning fixes
- live `validate-warehouse` Cloud Run Job proof
- modern 2025/2026 source data restoration
- current-season Fraud Watch materialization
- real claims and real trade inputs
- limited production candidate plan or deploy

## Command Results

Repo and safety:

```text
git status --short:
  M app.py
  M src/pipeline.py
  untracked Phase 17 and Phase 18 validation reports
  untracked src/ui_data_guards.py
  untracked tests/test_pipeline_plan.py
  untracked tests/test_staging_ui_warning_fixes.py

git diff --stat:
  app.py          | 34 changed
  src/pipeline.py | 79 changed

deployment safety: pass
```

Compile and tests:

```text
app.py compile: pass
src and scripts compile: pass
unit tests: 298 passed
```

Migration and validation:

```text
pending migrations: none
validation dry-run: pass, 149 validation files discovered
compat_trade_player_history: 6 passed, 0 failed, 1 informational warning with missing_identity_rate=0.0
cloud_run_job: 8 passed, 0 failed
content_brief: 11 passed, 0 failed
claim: 17 passed, 0 failed, expected informational warnings for draft/demo claim state
market: 9 passed, 0 failed
backtest: 11 passed, 0 failed, 2 informational dashboard rows
```

## Required Reports

All required Phase 18 reports exist:

| Report | Status |
|---|---|
| `phase-18-1-production-candidate-image-report.md` | present |
| `phase-18-2-production-baseline-report.md` | present |
| `phase-18-3-staging-ui-warning-fix-report.md` | present |
| `phase-18-4-live-validate-warehouse-job-report.md` | present |
| `phase-18-5-modern-source-data-report.md` | present |
| `phase-18-6-current-season-fraud-watch-materialization-report.md` | present |
| `phase-18-7-real-inputs-report.md` | present |
| `phase-18-8-limited-production-candidate-report.md` | present |

## Hard Safety Checks

Status: pass

- Pigskin arbitrary SQL remains absent.
- `execute_bigquery_sql` is not Pigskin-visible.
- Pigskin prompt contains the context tool protocol.
- Raw/source table names remain blocked in Pigskin schema, not exposed as allowed tools.
- No Firebase artifacts were detected by the deployment safety checker.
- No tracked secrets were detected.
- Production risk flags are unset in the production baseline, which is safe because defaults are false.
- No scheduler jobs were created.
- Cloud Run Jobs are not triggerable by default.
- Demo claims remain draft-only.
- Historical Fraud Watch was not presented as current-season content.

Static note:

- `app.py` still contains legacy UI references to raw/source tables, including `weekly_metrics`, by design. The hard gate here is Pigskin/LLM exposure, and Pigskin safety tests pass.

## Production Image Status

Status: pass

Immutable production-candidate image:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260616T181911Z
```

Digest:

```text
sha256:6d26118c3fdf3ce10d1983a8cfddb05956f65c34463d4ef02bcce47cb37f25c4
```

Build result:

```text
build ID: c81856f3-1b16-4585-a92a-4d507d6d5e1a
status: SUCCESS
```

No Cloud Run service was updated by the image build.

## Production Baseline Status

Status: pass

Current production service:

```text
service: nfl-studio-dashboard
project: fantasy-football-498121
region: us-central1
current revision: nfl-studio-dashboard-00074-26x
current image: us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2
traffic: 100 percent to nfl-studio-dashboard-00074-26x
service account: nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

Production risk flags:

```text
all unset
```

Rollback command is documented in `phase-18-2-production-baseline-report.md` and repeated in `phase-18-8-limited-production-candidate-report.md`.

## Staging UI Status

Status: clean locally, browser QA still pending

Phase 18.3 fixed the known staging UI warnings locally:

- Player Profiles missing `pos_abb`
- Versus Finder inherited `pos_abb` issue
- Show Prep Sleeper Watch missing `rolling_3_week_ppr`
- Trade Lab Side B summary behavior

Tests added:

- `tests/test_staging_ui_warning_fixes.py`

Current warning:

- Authenticated staging browser QA after these local fixes has not been rerun because staging deployment was not authorized in Phase 18.3.

## Live Job Status

Status: not authorized

`validate-warehouse` live Cloud Run Job proof remains deferred:

- dry-run deploy preview exists
- narrow trigger preview exists
- no live job was deployed
- no live job was triggered
- required authorization environment was missing

Cloud Run Job metadata validations passed:

```text
8 passed, 0 failed
```

## Modern Data Status

Status: blocked

Phase 18.5 confirmed modern source coverage is partial:

- `analytics_player_fantasy_points_by_profile` has 2025 weeks 1-18 rows
- `projection_rankings_current` has 2025 week 1 rows
- `compat_sleeper_watch_candidates` returns 2025 rows
- `play_by_play` has 0 rows for 2025/2026
- `weekly_metrics` has 0 rows for 2025/2026
- `analytics_player_weekly_truth` has 0 rows for 2025/2026
- `analytics_fraud_watch` has 0 rows for 2025/2026

The pipeline now has a non-mutating `--plan-only` mode, but no ingestion writes were run.

## Fraud Watch Status

Status: blocked

Phase 18.6 confirmed:

- `analytics_fraud_watch` has 0 rows for 2025/2026
- `analytics_player_weekly_truth` has 0 rows for 2025/2026
- `fraud_watch_packets` has 0 rows for 2025/2026
- `content_briefs` with `brief_type='fraud_watch_show'` has 0 rows for 2025/2026

No packet dry-run was run because there was no current-season source slice. No historical row was used as current content.

## Real Input Status

Status: blocked

Phase 18.7 confirmed:

- no operator-supplied real claim CSV exists
- `data/real_claim_import_template.csv` is header-only
- no operator/viewer trade sides were supplied
- `fantasy_claims` has 3 draft rows
- `fantasy_claim_players` has 1 unresolved draft player row
- `claim_grades` has 0 rows
- `trade_review_packets` has 0 rows
- `trade_review_show` content briefs have 0 rows

No claims or trade inputs were fabricated.

## Production Candidate Status

Status: preview only

Phase 18.8 prepared a digest-pinned production deploy command with all risk flags false:

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

Authorization state:

```text
ALLOW_LIMITED_PRODUCTION_DEPLOY=<unset>
```

No production deploy occurred.

## Blockers

These block production deployment approval:

1. `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is not set.
2. Authenticated staging browser QA must be rerun after the Phase 18.3 UI fixes.
3. Live `validate-warehouse` Cloud Run Job proof is still not authorized.
4. Modern 2025/2026 raw source rows are missing from `play_by_play`, `weekly_metrics`, `analytics_player_weekly_truth`, and `analytics_fraud_watch`.
5. Current-season Fraud Watch cannot be materialized honestly until modern source rows exist.
6. Real claim grading and Trade Review content remain blocked by missing operator-supplied real inputs.

## Warnings

1. `gcloud` is installed but not on PATH. The full `gcloud.cmd` path works.
2. Artifact Registry reports `slsa_build_level: unknown`.
3. Claim validation has expected informational warnings for draft/demo data and one unresolved draft claim-player row.
4. Backtest validation has informational dashboard availability rows.
5. `compat_trade_player_history` identity coverage warning reports missing identity rate `0.0`.
6. `git diff --stat` reports line-ending warnings for `app.py` and `src/pipeline.py` in this Windows checkout.
7. The worktree contains untracked Phase 17 and Phase 18 reports that should be committed or classified before merge.

## Recommended Phase 19 Work

1. Deploy the Phase 18.3 UI fixes to staging and repeat authenticated browser QA.
2. Decide whether to authorize the limited production deploy with all risk flags off.
3. If production is authorized, deploy only the digest-pinned candidate image and keep all risk flags false.
4. Add an ingest-only mode before restoring 2025 source rows.
5. Restore or ingest 2025 source data, then rebuild `analytics_player_weekly_truth` and `analytics_fraud_watch`.
6. Ask the operator for a real claim CSV and real trade sides, then run preview-only imports first.
7. Optionally authorize the live `validate-warehouse` Cloud Run Job proof with the required environment variables.
8. Classify and commit Phase 17 and Phase 18 reports and helper files.

## Final Decision

```text
GO WITH WARNINGS
```

Production classification:

```text
PRODUCTION CANDIDATE READY, NOT DEPLOYED
```

This means the immutable candidate image and deployment preview are ready, but production deployment remains gated by explicit operator authorization and the unresolved blockers above.
