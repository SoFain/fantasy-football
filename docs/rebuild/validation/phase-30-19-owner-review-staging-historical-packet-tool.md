# Phase 30.19 Owner Review: Staging Historical Packet Tool

## Final Decision

OWNER REVIEW READY FOR PRODUCTION DECISION

## Scope

This was a lightweight owner-review pass for the staging-only historical Pigskin packet/current-roster context tool.

No production deploy, BigQuery write, materialization, Sleeper API call, Cloud Run Job trigger, Scheduler change, broad validation pattern, or broad LLM prompt test was run.

## Current Service State

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00030-l9d`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:0b3129b3f30c8b6b43d064bd2b03d0d4af0d1b385452a7f529e94aaf4cdfab19`
- Traffic: `nfl-studio-dashboard-staging-00030-l9d:100`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true`
- Authenticated health check: `200 ok`

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: `nfl-studio-dashboard-00077-2jp:100`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: absent

## Checks Run

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m unittest tests.test_pigskin_packet_tool_guardrails tests.test_pigskin_context_qa tests.test_pigskin_current_roster_lookup tests.test_pigskin_current_roster_merge tests.test_pigskin_identity_bridge`

Results:

- Deployment safety: pass.
- Focused Pigskin tests: `99` tests passed.
- No full test suite was run because no code changes were made.
- No broad warehouse validation patterns were run because no warehouse SQL, compatibility view, materializer, or packet SQL changed.

Note: PowerShell surfaced the focused unittest command as a native-command warning because output was written to stderr, but unittest reported `Ran 99 tests ... OK`.

## Review Cases

### Patrick Mahomes Historical Packet Plus Current Roster

Request:

```json
{"season": 2025, "week": 15, "player_name": "Patrick Mahomes", "player_id_internal": "00-0033873", "limit": 5}
```

Result:

- Status: `ok`
- Historical team: `KC`
- Current team: `KC`
- Current roster source: `sleeper_players_current`
- Warnings:
  - Historical packet evidence and current roster state are retrieved through separate bounded helpers.
  - Historical nflverse packet context only.
  - Current roster/free-agent status must come from Sleeper/current roster source.
  - Packet team is never current team.
- Safe for model-visible use: yes.
- Wording or UX concern: none blocking. The blocked-metric warning is visible and correctly says unavailable, not zero.

### Tyreek Hill Historical Packet Plus Current Roster

Request:

```json
{"season": 2025, "week": 4, "player_name": "Tyreek Hill", "player_id_internal": "00-0033040", "limit": 5}
```

Result:

- Status: `ok`
- Historical team: `MIA`
- Current team: `null`
- Current roster source: `sleeper_players_current`
- Warnings:
  - Historical packet evidence and current roster state are retrieved through separate bounded helpers.
  - Historical nflverse packet context only.
  - Current roster/free-agent status must come from Sleeper/current roster source.
  - Packet team is never current team.
- Safe for model-visible use: yes.
- Wording or UX concern: current-team null is safe, but it may look odd in UX because the current source matched the player without a current team value. Do not infer Miami from the historical packet.

### Ambiguous Compact-Name Case

Request:

```json
{"season": 2025, "week": 4, "player_name": "T.Hill", "limit": 5}
```

Result source: mocked guardrail path from the focused QA tests. The live 2025 sample did not surface a real compact-name ambiguity cheaply.

Result:

- Status: `needs_identity_confirmation`
- Blocked reason: `packet_ambiguous`
- Historical team: `null`
- Current team: `null`
- Current roster source: `null`
- Warnings:
  - Player-name lookup matched multiple historical packet identities.
  - Historical nflverse packet context only.
  - Current roster/free-agent status must come from Sleeper/current roster source.
  - Packet team is historical_team. It is never current_team.
- Safe for model-visible use: yes, as a refusal/clarification result.
- Wording or UX concern: the response should ask for stable player identity before taking a data-backed position.

### Missing Current Roster Source

Request:

```json
{"season": 2025, "week": 15, "player_name": "P.Mahomes", "player_id_internal": "00-0033873", "limit": 5}
```

Result:

- Status: `current_roster_unavailable`
- Historical team: `KC`
- Current team: `null`
- Current roster source: `null`
- Warnings:
  - Historical packet evidence and current roster state are retrieved through separate bounded helpers.
  - Historical nflverse packet context only.
  - Current roster/free-agent status must come from Sleeper/current roster source.
  - Packet team is never current team.
- Safe for model-visible use: yes.
- Wording or UX concern: the tool should say the current roster source did not resolve the compact-name request. It must not imply current team from `KC`.

### Week 22/Postseason Case

Request:

```json
{"season": 2025, "week": 22, "player_name": "Patrick Mahomes", "player_id_internal": "00-0033873", "limit": 5}
```

Result:

- Status: `not_found`
- Blocked reason: `historical_packet_unavailable`
- Historical team: `null`
- Current team: `null`
- Current roster source: `null`
- Warnings:
  - Historical packet evidence and current roster state are retrieved through separate bounded helpers.
  - Historical nflverse packet context only.
  - Current roster/free-agent status must come from Sleeper/current roster source.
  - Postseason packet rows are excluded by the regular-season cutoff rule.
- Safe for model-visible use: yes.
- Wording or UX concern: no fallback packet should be shown. The missing slice is explicit.

### Blocked-Metric Case

Request:

```json
{"season": 2025, "week": 15, "player_name": "Patrick Mahomes", "player_id_internal": "00-0033873", "limit": 5}
```

Result:

- Status: `ok`
- Historical team: `KC`
- Current team: `KC`
- Current roster source: `sleeper_players_current`
- Blocked metric policy: `Blocked metrics are unavailable, not zero.`
- Warnings:
  - Historical packet evidence and current roster state are retrieved through separate bounded helpers.
  - Historical nflverse packet context only.
  - Current roster/free-agent status must come from Sleeper/current roster source.
  - Packet team is never current team.
- Safe for model-visible use: yes.
- Wording or UX concern: none blocking. The blocked metrics are explicit and should remain visible to the model.

## Owner-Review Summary

The staging tool is safe enough for a production exposure decision:

- The tool is still absent in production.
- Staging exposes the tool only through `USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true`.
- Historical team and current team stay separate.
- Missing current roster source is not papered over.
- Week 22/postseason behavior refuses rather than substituting a regular-season packet.
- Blocked metrics are unavailable, not zero.
- Arbitrary SQL exposure remains absent.

The main owner decision is product posture, not a code blocker.

## Remaining Warnings

- Tyreek Hill currently resolves with historical team `MIA` and current team `null`. That is safe, but current-source remediation would improve user confidence.
- The live compact-name sample did not produce a real ambiguity case. The ambiguity behavior is covered by focused tests and mocked guardrail review.
- A read-only QA UI would make owner review easier before a broader production exposure.

## Recommended Next Phase

Recommended path:

- Production exposure decision, with the flag still default-off and production deployment handled in a separate phase.

Useful alternatives:

- Read-only QA UI for historical packet plus current roster context.
- Current-source remediation for Tyreek current-team status.
- Wording/UX fixes only if owner wants clearer copy around source gaps.
