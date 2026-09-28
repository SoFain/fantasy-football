# Phase 30.18 Staging Historical Packet Tool Exposure Report

## Final Decision

STAGING HISTORICAL PACKET TOOL READY WITH GUARDRAILS

## Gate State

Local process gates were unset before deploy:

- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: unset
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`: unset
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`: unset
- `DATA_OPS_ALLOW_JOB_TRIGGER`: unset

Production remained disabled:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: `nfl-studio-dashboard-00077-2jp:100`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: absent
- `DATA_OPS_ALLOW_JOB_TRIGGER`: `false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`: `false`

Staging before deploy:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Traffic: `nfl-studio-dashboard-staging-00029-jtb:100`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: absent
- `DATA_OPS_ALLOW_JOB_TRIGGER`: `false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`: `false`

## Git State

Code and tests were committed before staging deploy:

- Commit: `616d067 Expose historical packet tool behind staging flag`
- Prior checkpoint: `143fd2d Tighten Pigskin current-source exposure readiness`

Files changed in the committed package:

- `src/pigskin_context_tools.py`
- `src/pigskin_current_roster_merge.py`
- `src/pigskin_identity_bridge.py`
- `src/pigskin_packet_guardrails.py`
- `tests/test_pigskin_current_roster_merge.py`
- `tests/test_pigskin_identity_bridge.py`
- `tests/test_pigskin_packet_tool_guardrails.py`

The remaining untracked files are historical validation backlog and owner-review artifacts.

## Local Checks

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_packet_tool_guardrails`
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_context_qa`
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_current_roster_lookup`
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_current_roster_merge`
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_identity_bridge`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

Results:

- Full test suite: `598` tests passed.
- Pending migrations: none.
- BigQuery validation dry-run: catalog discovered through validation `200`.

## Default-Off Proof

Local/default tool visibility:

- `get_pigskin_context_tool_declarations()` excludes `get_historical_pigskin_packet_context` by default.
- `get_historical_packet_tool_declarations(enabled=False)` returns `[]`.
- With `USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true`, declarations include `get_historical_pigskin_packet_context`.
- With the flag enabled, `execute_bigquery_sql` remains absent.

Enabled declaration probe:

- `historical_visible=True`
- `execute_bigquery_sql_visible=False`
- Tool count: `8`
- Visible tools included existing tools plus `get_historical_pigskin_packet_context`.

## Staging Deployment

Build:

- Cloud Build ID: `14d5b969-6c0e-4f19-b757-5195763a563b`
- Build status: `SUCCESS`
- Image tag: `staging-616d0677085d-20260702T110500Z`
- Digest-pinned image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:0b3129b3f30c8b6b43d064bd2b03d0d4af0d1b385452a7f529e94aaf4cdfab19`

Deploy:

- Target service: `nfl-studio-dashboard-staging`
- New revision: `nfl-studio-dashboard-staging-00030-l9d`
- Traffic: `nfl-studio-dashboard-staging-00030-l9d:100`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: `true`
- `DATA_OPS_ALLOW_JOB_TRIGGER`: `false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`: `false`

Note: the PowerShell wrapper reported a nonzero exit because `gcloud` emitted progress on stderr, but the Cloud Run deployment completed successfully and read-back verification confirmed the new revision.

Staging health:

- Authenticated `/_stcore/health`: `200 ok`

## Staging Smoke Results

No Pigskin prompt or LLM call was made. Smoke used deterministic internal helper calls and read-only BigQuery access through the guarded retrieval path.

Positive cases:

- Patrick Mahomes, `season=2025`, `week=15`, `player_name=Patrick Mahomes`, `player_id_internal=00-0033873`
  - Historical packet found: yes
  - Historical team: `KC`
  - Current roster source: `sleeper_players_current`
  - Current roster status: `Active`
  - Current team: `KC`
  - Identity status: `identity_match`

- Tyreek Hill, `season=2025`, `week=4`, `player_name=Tyreek Hill`, `player_id_internal=00-0033040`
  - Historical packet found: yes
  - Historical team: `MIA`
  - Current roster source: `sleeper_players_current`
  - Current roster status: `Active`
  - Current team: `null`
  - Identity status: `identity_match`
  - Result confirms current team was not inferred from the historical Miami packet.

Negative and guardrail cases:

- `sql` argument rejected with `blocked_reason=arbitrary_sql_not_allowed`.
- Team/position-only request rejected with `blocked_reason=missing_current_roster_identity`.
- Week 22 request without postseason inclusion returned `blocked_reason=historical_packet_unavailable`.
- Blocked metrics policy returned: `Blocked metrics are unavailable, not zero.`
- Historical packet output strips `current_team` from packet structures.

Compact-name behavior:

- Compact names such as `P.Mahomes` and `T.Hill` can return historical packets while current roster lookup may remain unavailable.
- The live compact-name search did not produce an ambiguity case during this smoke. Ambiguity handling remains covered by unit tests and mocked QA paths.

## Production Untouched Proof

Production after staging deploy:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: `nfl-studio-dashboard-00077-2jp:100`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: absent
- `DATA_OPS_ALLOW_JOB_TRIGGER`: `false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`: `false`

No production deploy occurred.

## No-State-Change Confirmation

This phase did not:

- write BigQuery rows
- run materializations
- run Sleeper ingestion
- call live Sleeper API
- submit Pigskin prompts
- call LLM-backed actions
- trigger Cloud Run Jobs
- create Scheduler jobs
- create Firebase artifacts
- enable the historical packet tool in production

## Remaining Warnings

- The live compact-name smoke did not surface an ambiguity candidate. Unit tests still cover safe ambiguity preservation.
- Compact packet names can resolve historical context while current roster source remains unavailable. This is expected and reported as a source gap, not inferred from historical team.
- Staging now exposes the tool only because `USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true` is set on staging.

## Recommended Next Phase

Owner review of the staging historical packet tool, focused on:

- controlled Pigskin UI review without LLM credit burn where possible
- deciding whether a read-only QA UI should expose packet/current roster context
- current-source remediation for Tyreek current-team status
- separate production exposure decision only after owner approval
