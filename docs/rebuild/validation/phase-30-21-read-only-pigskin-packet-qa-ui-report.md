# Phase 30.21 Read-Only Pigskin Packet QA UI Report

## Final Decision

READ ONLY QA UI READY WITH WARNINGS

## Gate And Flag State

Local process gates checked at phase start:

- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: unset
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`: unset
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`: unset
- `DATA_OPS_ALLOW_JOB_TRIGGER`: unset

Staging before deploy:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00030-l9d`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:0b3129b3f30c8b6b43d064bd2b03d0d4af0d1b385452a7f529e94aaf4cdfab19`
- Traffic: `nfl-studio-dashboard-staging-00030-l9d:100`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true`
- `USE_PIGSKIN_PACKET_QA_UI`: absent

Production before deploy:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: `nfl-studio-dashboard-00077-2jp:100`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: absent
- `USE_PIGSKIN_PACKET_QA_UI`: absent

## Git State

Starting checkpoint:

- `616d067 Expose historical packet tool behind staging flag`

Committed package:

- Commit: `7b6138c Add read-only Pigskin packet QA UI`
- Staged files:
  - `app.py`
  - `src/compat_flags.py`
  - `src/pigskin_packet_qa_ui.py`
  - `tests/test_pigskin_packet_qa_ui.py`

Unrelated historical validation backlog remained untracked and was not staged.

## Files Changed

- `src/compat_flags.py`
  - Added default-off `USE_PIGSKIN_PACKET_QA_UI`.

- `src/pigskin_packet_qa_ui.py`
  - Added pure helper functions for read-only QA request splitting, deterministic lookup execution, and safe display summarization.
  - Rejects SQL/query-like inputs before helper execution.
  - Keeps historical packet `team` and `position` out of the current roster request.
  - Preserves warnings, identity diagnostics, candidate lists, blocked metrics, source freshness, missing flags, and raw structured JSON.

- `app.py`
  - Added `use_pigskin_packet_qa_ui()`.
  - Added a Data Ops read-only QA panel hidden behind `USE_PIGSKIN_PACKET_QA_UI`.
  - Panel calls `run_pigskin_packet_qa_lookup`, which uses `build_historical_packet_current_roster_context`.
  - Panel does not call Pigskin chat, Gemini, live Sleeper APIs, subprocesses, materializers, or write paths.

- `tests/test_pigskin_packet_qa_ui.py`
  - Added focused flag, source, request, summary, ambiguity, Week 22, and blocked-metric coverage.

## Local Checks

Passed:

- `.\venv\Scripts\python.exe -m py_compile app.py src\pigskin_packet_qa_ui.py src\compat_flags.py`
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_packet_qa_ui`
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_context_qa tests.test_pigskin_current_roster_lookup tests.test_pigskin_current_roster_merge tests.test_pigskin_identity_bridge tests.test_pigskin_packet_tool_guardrails tests.test_pigskin_packet_qa_ui`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

Results:

- Focused UI tests: `9` tests passed.
- Focused Pigskin plus UI tests: `108` tests passed.
- Full suite: `607` tests passed.
- Pending migrations: none.
- BigQuery validation dry-run: catalog discovered through validation `200`.

Notes:

- PowerShell surfaced native-command warnings when unittest and Cloud Build wrote progress or logs to stderr. Unittest reported `OK`.
- A first `py_compile` attempt hit a transient Windows `__pycache__` rename lock. Rerun passed.

## UI Behavior Summary

The QA UI:

- is hidden unless `USE_PIGSKIN_PACKET_QA_UI=true`;
- lives in the Data Ops tab as `Pigskin Packet QA`;
- is read-only;
- calls deterministic internal helper paths only;
- does not expose arbitrary SQL;
- does not call Pigskin chat or LLM-backed generation;
- does not call live Sleeper APIs;
- labels `historical_team` and `current_team` separately;
- shows current roster source and as-of fields when present;
- shows warnings, blocked reasons, identity diagnostics, candidate lists, blocked metrics, source freshness, missing flags, and raw structured JSON;
- states that blocked metrics are unavailable, not zero.

## Local Deterministic Smoke

Smoke used `run_pigskin_packet_qa_lookup` and mocked only the ambiguity case because the live cheap 2025 sample did not surface an ambiguous compact-name match.

| Case | Status | Historical team | Current team | Current source | Wording safe |
| --- | --- | --- | --- | --- | --- |
| Patrick Mahomes, 2025 week 15 | `ok` | `KC` | `KC` | `sleeper_players_current` | yes |
| Tyreek Hill, 2025 week 4 | `ok` | `MIA` | `null` | `sleeper_players_current` | yes, current team not inferred |
| Missing current roster, compact Mahomes | `current_roster_unavailable` | `KC` | `null` | `null` | yes |
| Week 22 postseason excluded | `not_found` | `null` | `null` | `null` | yes |
| Blocked metric policy | `ok` | `KC` | `KC` | `sleeper_players_current` | yes |
| Ambiguous compact-name mocked path | `needs_identity_confirmation` | `null` | `null` | `null` | yes, candidates preserved |

Observed policy text:

- `Read-only QA only. Historical packet team is historical_team, not current_team. Current roster status must come from approved current roster sources.`
- `Blocked metrics are unavailable, not zero.`

## Staging Deploy Details

Build:

- Image tag: `staging-7b6138cc5e8f-20260702T113721Z`
- Cloud Build ID: `906f4b89-6b11-4ec0-96c9-e969ec711f06`
- Build status: `SUCCESS`
- Digest-pinned image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:8f6134e7e7fe8bda59f382a938662ecd6b9c68912988ff1d3f1a6a64cbfff0e6`

Deploy:

- Target service: `nfl-studio-dashboard-staging`
- New revision: `nfl-studio-dashboard-staging-00031-79n`
- Traffic: `nfl-studio-dashboard-staging-00031-79n:100`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true`
- `USE_PIGSKIN_PACKET_QA_UI=true`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

Staging health:

- Authenticated `/_stcore/health`: `200 ok`

Note: the PowerShell wrapper reported nonzero status for Cloud Build/deploy progress because `gcloud` wrote progress to stderr. Cloud Build and Cloud Run read-back both confirmed success.

## Staging Smoke Results

Verified:

- Staging revision and digest read back correctly.
- `USE_PIGSKIN_PACKET_QA_UI=true` in staging.
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true` remains enabled in staging.
- Data Ops Cloud Run and local subprocess trigger flags remain false.
- Authenticated health endpoint returns `200 ok`.

Not run:

- Browser-click UI smoke was not run in this phase.
- No Pigskin prompt or LLM-backed test was run.

The UI visibility behavior is covered by source-gated tests and staging flag read-back, not by a browser screenshot.

## Production Untouched Proof

Production after staging deploy:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: `nfl-studio-dashboard-00077-2jp:100`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: absent
- `USE_PIGSKIN_PACKET_QA_UI`: absent
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

No production deploy occurred.

## No-State-Change Confirmation

This phase did not:

- write BigQuery rows;
- run materializations;
- run Sleeper ingestion;
- call live Sleeper APIs;
- call Pigskin prompts;
- call LLM-backed actions;
- trigger Cloud Run Jobs;
- create Scheduler jobs;
- create Firebase artifacts;
- run rankings;
- change production flags.

## Credit-Conscious Validation Policy Used

- Used focused helper/UI tests.
- Ran the full suite because code changed.
- Ran deployment safety, pending migrations, and validation dry-run.
- Avoided broad live validation patterns.
- Avoided browser prompt tests and LLM credit use.

## Remaining Warnings

- Browser-click QA of the staging panel was not run.
- Ambiguity was verified through a mocked helper path because the cheap live sample did not produce an ambiguous compact-name match.
- Tyreek Hill current team remains `null` in the approved current roster source. The UI preserves that state instead of inferring Miami from historical packet context.

## Recommended Next Phase

Recommended:

- Owner review of QA UI.

Other valid next phases:

- QA UI wording fixes.
- Current-source remediation for Tyreek current-team status.
- Production exposure decision, only after explicit owner approval.
- Pause agent work.
