# Phase 31.16 Production Player Profiles Scoring Dropdown Deploy Report

Date: 2026-07-04

Final decision: **PLAYER PROFILES SCORING DROPDOWN DEPLOYED WITH WARNINGS**

## Scope

Phase 31.16 deployed the already-verified Player Profiles scoring dropdown to production.

No rankings were regenerated. No Pigskin chat prompt, LLM-backed ranking generation, candidate materialization, ranking formula/backtest write, live Sleeper API call, Cloud Run Job trigger, Scheduler job creation, broad validation pattern, or Data Ops trigger flag change was performed.

## Pre-Deploy State

Git:

- HEAD before deploy: `69d1505 Document Player Profiles multi-profile UI smoke`
- tracked source diff before deploy: none

Production baseline:

- service: `nfl-studio-dashboard`
- previous revision: `nfl-studio-dashboard-00081-bwr`
- previous image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:51470773b5185de1455f2af99d1f27f5322354cc0c375354cbd00ba0aed1ec1e`
- previous traffic: `nfl-studio-dashboard-00081-bwr=100`
- previous URL: `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`
- service account: `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com`

Production safety flags before deploy:

- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`
- `USE_BACKTEST_DASHBOARD=false`
- `USE_CLAIM_LEDGER_UI=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `USE_COMPAT_PLAYER_PROFILES=false`
- `USE_COMPAT_SLEEPER_WATCH=false`
- `USE_COMPAT_TRADE_ASSETS=false`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`
- `USE_CONTENT_BRIEF_REVIEW_UI=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `USE_TRADE_ANALYZER_SCORE_V0=false`

Existing production QA flag preserved:

- `USE_PIGSKIN_PACKET_QA_UI=true`

## Pre-Deploy Checks

Commands run:

```powershell
git status --short --untracked-files=no
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src
.\venv\Scripts\python.exe -m unittest tests.test_player_profile_ranking_profiles tests.test_pigskin_rankings_model_runs tests.test_pigskin_rankings_materialize_identity
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
```

Results:

- tracked source diff: none
- safety checker: pass
- `app.py` compile: pass
- `src` compile: pass
- focused tests: `24` passed
- pending migrations: none

Full test suite and broad validation patterns were not run because no source changed after Phase 31.15.

## Build

Build command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit `
  --project=fantasy-football-498121 `
  --config=cloudbuild.yaml `
  --substitutions="_IMAGE_TAG=prod-69d1505fa321-phase31.16,_COMMIT_HASH=69d1505fa321,_VERSION_LABEL=prod-69d1505fa321-phase31.16" `
  .
```

Build result:

- build ID: `9364433b-cd41-46a6-8b1c-6285e1483eb9`
- status: `SUCCESS`
- duration: `2M29S`
- image tag: `prod-69d1505fa321-phase31.16`
- digest-pinned image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:c675aa578b218581c4a9253e6bd5ceefc6da3ee0198dcb7cb9b98e3c541442e6`

Build log confirmed the container includes:

- `app.py`
- `src/`
- `scripts/run_bigquery_validations.py`
- `bigquery/validations/`

## Deploy

Deploy command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:c675aa578b218581c4a9253e6bd5ceefc6da3ee0198dcb7cb9b98e3c541442e6 `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars=DATA_OPS_ALLOW_JOB_TRIGGER=false,DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false `
  --quiet
```

Access policy was not changed.

Deploy result:

- new revision: `nfl-studio-dashboard-00082-7bf`
- traffic: `nfl-studio-dashboard-00082-7bf=100`
- status URL: `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`
- deploy output URL: `https://nfl-studio-dashboard-583607027760.us-central1.run.app`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:c675aa578b218581c4a9253e6bd5ceefc6da3ee0198dcb7cb9b98e3c541442e6`
- service account: `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com`

Production safety flags after deploy:

- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`
- `USE_BACKTEST_DASHBOARD=false`
- `USE_CLAIM_LEDGER_UI=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `USE_COMPAT_PLAYER_PROFILES=false`
- `USE_COMPAT_SLEEPER_WATCH=false`
- `USE_COMPAT_TRADE_ASSETS=false`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`
- `USE_CONTENT_BRIEF_REVIEW_UI=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `USE_TRADE_ANALYZER_SCORE_V0=false`

Existing production QA flag after deploy:

- `USE_PIGSKIN_PACKET_QA_UI=true`

## Production Smoke

HTTP checks:

- `/_stcore/health` on deploy output URL: `200 ok`
- `/_stcore/health` on status URL: `200 ok`
- `/` on deploy output URL: `200`
- Streamlit shell present: yes
- traceback in root response: no

Browser smoke:

- production URL opened successfully
- Streamlit login gate rendered
- login gate text observed: `Data Studio Login`, `Sign in to continue.`, `Username`, `Password`, `Log in`
- traceback observed in browser text: no
- screenshot captured locally under `output/playwright/phase-31-16/production-root-smoke.png`

Authenticated post-login UI smoke:

- not completed in this command session
- blocker: no app-level username/password was available to this shell or Playwright session
- no credential bypass, password guessing, or app-auth mutation was attempted

Rollback decision:

- rollback not required
- app health passed
- Streamlit shell loaded
- login gate rendered
- no traceback appeared
- production safety flags remained false

## Ranking Data No-Change Confirmation

Post-deploy read-only verification:

- active final rankings: `1,140`
- candidate table: `ppr` only
- candidate table row count: `936`
- no ranking formula/backtest rows were written

Active final rankings by profile:

| scoring_profile_id | QB | RB | WR | TE |
| --- | ---: | ---: | ---: | ---: |
| `ppr` | 45 | 80 | 100 | 60 |
| `half_ppr` | 45 | 80 | 100 | 60 |
| `standard` | 45 | 80 | 100 | 60 |
| `gng_keeper` | 45 | 80 | 100 | 60 |

Trey McBride:

| scoring_profile_id | player_id | position | rank |
| --- | --- | --- | ---: |
| `ppr` | `00-0037744` | TE | 1 |
| `half_ppr` | `00-0037744` | TE | 1 |
| `standard` | `00-0037744` | TE | 1 |
| `gng_keeper` | `00-0037744` | TE | 1 |

Ja'Marr Chase no-fallback check:

| scoring_profile_id | position | rank |
| --- | --- | ---: |
| `ppr` | WR | 3 |
| `half_ppr` | WR | 3 |
| `standard` | WR | 4 |
| `gng_keeper` | WR | 4 |

The Ja'Marr Chase rank difference between PPR/Half PPR and Standard/GNG Keeper confirms the profile data remains distinct.

Ranking formula/backtest counts after deploy:

| table | row_count |
| --- | ---: |
| `ranking_formula_candidates` | 12 |
| `ranking_formula_sets` | 1 |
| `ranking_backtest_runs` | 0 |
| `ranking_backtest_results` | 0 |
| `ranking_backtest_candidate_summaries` | 0 |
| `ranking_formula_champions` | 0 |

## Pigskin Formula Exposure Check

Search paths:

- `app.py`
- `src/pigskin_context_tools.py`
- `src/pigskin_packet_guardrails.py`
- `src/pigskin_context_qa.py`

Search terms:

- `ranking_formula`
- `ranking_backtest`
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE`
- `execute_bigquery_sql`

Result:

- no matches in searched Pigskin-visible paths
- no arbitrary SQL path added
- no ranking formula/backtest tool exposure found

## Logs

Cloud Run ERROR log check for `nfl-studio-dashboard-00082-7bf`:

- no ERROR entries returned during the post-deploy window checked

## Rollback

Rollback was not used.

Rollback command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00081-bwr=100
```

## Warnings

- Authenticated post-login Player Profiles browser clicks were not completed because app credentials were not available in this command session.
- The deployed app reached the login gate successfully, so this was not treated as a rollback condition.
- The report file is intentionally left uncommitted unless the owner requests an evidence commit.

## Recommended Next Phase

Stop UI work and move to:

- **Phase 32.1 — Real formula backtest metrics and champion selection path**
