# Phase 30.20 Owner Production Exposure Decision Package

## Final Recommendation

BUILD QA UI FIRST

The staging tool is technically ready for a production exposure decision, but the lowest-friction owner path is a read-only admin QA UI before model-visible production exposure. That gives the owner a direct way to inspect historical packet plus current roster context without spending LLM credits and without turning the tool on for production Pigskin prompts.

If owner appetite is higher, a later production exposure phase is reasonable. It should remain separate, explicit, and rollback-ready.

## Current Staging And Production State

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00030-l9d`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:0b3129b3f30c8b6b43d064bd2b03d0d4af0d1b385452a7f529e94aaf4cdfab19`
- Traffic: `nfl-studio-dashboard-staging-00030-l9d:100`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Traffic: `nfl-studio-dashboard-00077-2jp:100`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: absent
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

Git:

- Latest exposure commit: `616d067 Expose historical packet tool behind staging flag`
- Phase 30.18 decision: `STAGING HISTORICAL PACKET TOOL READY WITH GUARDRAILS`
- Phase 30.19 decision: `OWNER REVIEW READY FOR PRODUCTION DECISION`
- The historical validation backlog and Phase 30.18/30.19 reports remain untracked owner-review artifacts.

## Tool Declaration Check

Read-only local declaration probe:

- Default context declarations include historical packet tool: `False`
- Default direct historical declaration count: `0`
- Enabled context declarations include historical packet tool: `True`
- Enabled direct historical declaration count: `1`
- `execute_bigquery_sql` visible: `False`

This matches the intended posture: default-off, flag-gated, no arbitrary SQL exposure.

## Credit-Conscious Validation Policy

Validation was intentionally minimal:

- Inspected git state.
- Read Phase 30.17, 30.18, and 30.19 reports.
- Read staging and production Cloud Run service state.
- Ran a tiny local declaration probe.
- Did not run focused tests because no source file changed in this phase.
- Did not run the full suite.
- Did not run broad warehouse validations.
- Did not run LLM or Pigskin prompt tests.

No runtime settings were changed.

## Decision Options

### Option 1: Keep Staging Only

Benefit:

- Lowest operational risk.
- No production deploy.
- No owner-facing runtime change.
- Keeps historical packet tool available for manual/admin staging review.

Risk:

- Decision drifts. The tool can sit in staging without forcing a production posture.
- Owner confidence may not increase much unless review steps are repeated manually.

Cost and credit impact:

- Lowest cost.
- No LLM credit use required.
- No deploy cost beyond existing staging runtime.

Required next action:

- Pause agent work until owner wants another review pass or asks for a production decision.

Needs deploy:

- No.

Needs owner approval:

- No new approval needed to remain staged.

Best when:

- Owner wants more time and no new surface area.

### Option 2: Build Read-Only QA UI

Benefit:

- Gives admins a visible, deterministic inspection path for historical packet plus current roster context.
- Avoids model-visible production exposure while still improving review quality.
- Helps validate wording for historical team, current team, missing current source, Week 22/postseason exclusion, ambiguity, and blocked metrics.

Risk:

- Adds UI surface and requires a staging deploy.
- Needs careful admin-only gating so it does not become accidental public feature exposure.

Cost and credit impact:

- Low to moderate engineering cost.
- No LLM credit use required if the QA UI calls the same deterministic helper.
- One staging deploy and targeted QA.

Required next action:

- Implement a read-only admin/staging QA panel for the existing guarded helper.
- Keep production disabled.
- Do not call LLMs from the QA UI.

Needs deploy:

- Yes, staging deploy.
- Production deploy only if owner later approves.

Needs owner approval:

- Yes, owner should approve adding an admin QA UI.

Best when:

- Owner wants more confidence before model-visible production exposure.

### Option 3: Approve Production Exposure Phase

Benefit:

- Moves the completed staging work toward production.
- Keeps the tool flag-gated, so production can still deploy with the flag explicitly controlled.
- Lets Pigskin use approved historical packet context under the same no-SQL guardrails.

Risk:

- Model-visible production exposure is a higher bar than deterministic staging helper calls.
- Tyreek current team remains unknown in approved current roster source. That is safe, but user-facing wording must remain clear.
- Compact-name ambiguity was proven by tests and mocked guardrail paths, not by a cheap live warehouse case in Phase 30.19.

Cost and credit impact:

- Moderate operational cost.
- Requires a production candidate, deploy gate, smoke checklist, and rollback plan.
- LLM prompt tests should stay narrow and owner-approved.

Required next action:

- Run a separate production exposure phase only after owner approval.
- Build or verify a production candidate from reviewed source.
- Deploy with `USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true` only if explicitly approved.
- Smoke test with no broad prompt burn.
- Keep rollback command ready.

Needs deploy:

- Yes, production deploy.

Needs owner approval:

- Yes, explicit approval required.

Best when:

- Owner accepts the remaining source warnings and wants the model-visible tool in production.

## Risk Table

| Path | Benefit | Main risk | Cost/credit impact | Deploy needed | Owner approval needed |
| --- | --- | --- | --- | --- | --- |
| Keep staging-only | No new production risk | Review can stall | Lowest, no LLM credits | No | No |
| Build read-only QA UI | Better owner inspection without model exposure | Adds admin UI surface | Low to moderate, no LLM credits required | Staging yes, production no | Yes |
| Approve production exposure | Moves tool to production behind a flag | Model-visible behavior needs careful smoke | Moderate, narrow LLM only if approved | Production yes | Yes |

## Recommended Next Prompt

Recommended:

`Phase 30.21 — Build read-only QA UI`

Use this if the owner wants to inspect historical packet/current roster context directly before production exposure.

Alternative if owner approves production:

`Phase 30.21 — Production historical packet tool exposure, owner-approved`

That prompt should explicitly authorize production exposure, require a rollback plan, preserve all non-target production flags, and keep prompt testing narrow.

If owner wants no further movement:

`Pause agent work until owner decision`

## Acceptance Criteria Confirmation

- No BigQuery rows were written.
- No materializations were run.
- No deployment occurred.
- No production flag changed.
- No broad validation pattern was run.
- No broad LLM prompt test was run.
- No staging or production runtime setting changed.

## Final Decision

BUILD QA UI FIRST
