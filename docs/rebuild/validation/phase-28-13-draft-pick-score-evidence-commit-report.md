# Phase 28.13 Draft-Pick Score Evidence Commit Report

Date: 2026-06-28

Final decision: DRAFT PICK SCORE EVIDENCE COMMIT COMPLETE

## Scope

Phase 28.13 created an evidence-only commit for the Phase 28.11 release package review and Phase 28.12 package commit report. No code, warehouse files, generated browser evidence, historical Phase 17 through Phase 27 backlog, logs, env files, cache files, or secrets were staged.

No staging deploy, production deploy, BigQuery write, score materialization, Cloud Run Job trigger, Scheduler job, ingestion, LLM-backed action, Pigskin prompt, scrape, external fetch, Firebase artifact, or production flag change occurred.

## Authorization Gate State

All checked gates were unset:

| Gate | State |
| --- | --- |
| ALLOW_TRADE_PICK_SCORE_MATERIALIZATION | unset |
| ALLOW_TRADE_SCORE_MATERIALIZATION | unset |
| ALLOW_PROJECTION_CONTEXT_REFRESH | unset |
| ALLOW_LIMITED_PRODUCTION_DEPLOY | unset |
| ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST | unset |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | unset |

## Staged Files

Exactly two evidence reports were staged:

```text
docs/rebuild/validation/phase-28-11-draft-pick-score-release-package-review.md
docs/rebuild/validation/phase-28-12-draft-pick-score-package-commit-report.md
```

Staged-file verification:

| Check | Result |
| --- | --- |
| Expected staged count | 2 |
| Actual staged count | 2 |
| Missing expected files | none |
| Extra staged files | none |
| Excluded path scan | no matches |

## Excluded File Confirmation

Confirmed not staged:

```text
output/
output/playwright/
screenshots
proxy logs
proxy PID files
.env
.env.*
pipeline_execution.log
*.log
.codex-remote-attachments/
.codex-tools/
node_modules/
cache files
secret JSON files
historical Phase 17 through Phase 27 validation backlog
code files
warehouse files
generated browser evidence
```

## Staged Diff Summary

`git diff --cached --stat`:

```text
docs/rebuild/validation/phase-28-11-draft-pick-score-release-package-review.md | 377 +++++++++++++++++++++
docs/rebuild/validation/phase-28-12-draft-pick-score-package-commit-report.md | 214 ++++++++++++
2 files changed, 591 insertions(+)
```

`git diff --cached --check`: pass.

## Checks Run

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | pass |
| `py_compile app.py` | pass |
| `py_compile src\trade_pick_scores.py` | pass |
| `compileall -q src scripts` | pass |

## Commit Result

Commit created:

```text
a73656c Document draft pick score release package
```

Commit summary:

```text
2 files changed, 591 insertions(+)
```

## Post-Commit Git Status

Post-commit:

| Check | Result |
| --- | --- |
| HEAD | `a73656c Document draft pick score release package` |
| Prior package commit | `6e4b565 Draft pick score lane and staging UI` |
| staged files | none |
| generated evidence | still untracked or ignored |
| historical Phase 17 through Phase 27 backlog | still untracked |

Recent commits:

```text
a73656c Document draft pick score release package
6e4b565 Draft pick score lane and staging UI
6158549 Document Trade Score v1 Track A closeout
3268a5a Document Trade Score v1 UI polish package
9ec04f3 Polish Trade Score v1 staging UI
aa543d0 Document Phase 26 evidence commit
```

## Production Untouched Confirmation

Read-only production describe confirmed:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00077-2jp` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Traffic | `nfl-studio-dashboard-00077-2jp:100` |
| USE_TRADE_PICK_SCORE_V0 | unset |
| USE_COMPAT_TRADE_PICK_SCORE | unset |
| USE_TRADE_ANALYZER_SCORE_V0 | `false` |
| USE_COMPAT_TRADE_PLAYER_SCORE | `false` |
| USE_COMPAT_TRADE_PLAYER_HISTORY | `false` |
| USE_CLOUD_RUN_JOBS_FOR_DATA_OPS | `false` |
| DATA_OPS_ALLOW_JOB_TRIGGER | `false` |
| USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS | `false` |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | `false` |

No production deployment occurred.

## Remaining Warnings

- Historical Phase 17 through Phase 27 validation backlog remains untracked for owner review.
- This Phase 28.13 report was created after the evidence commit and remains untracked for a later closeout decision.
- Phase 28.10 staging QA had accepted warnings documented in the committed Phase 28.10 and Phase 28.12 reports.

## Recommended Next Phase

Phase 28.14 should either commit this Phase 28.13 report as final evidence, or leave it untracked with the historical backlog if no further Phase 28 evidence commits are desired.

## Final Decision

DRAFT PICK SCORE EVIDENCE COMMIT COMPLETE
