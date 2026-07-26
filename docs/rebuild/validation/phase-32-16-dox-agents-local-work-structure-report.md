# Phase 32.16 - DOX AGENTS Local Work Structure Report

Final decision: DOX AGENTS STRUCTURE IMPLEMENTED WITH WARNINGS

## Files Changed

Committed AGENTS/DOX package:

- `AGENTS.md`
- `bigquery/AGENTS.md`
- `docs/rebuild/AGENTS.md`
- `src/AGENTS.md`
- `tests/AGENTS.md`

Report created after the AGENTS commit:

- `docs/rebuild/validation/phase-32-16-dox-agents-local-work-structure-report.md`

## Commits Created

- `facfa18 phase 32.15 add pbp ffopportunity splits`
- `31fc88c adopt dox agents local work structure`

## Git State Before

Before Phase 32.16 edits:

- Phase 32.15 package was already committed as `facfa18`.
- Root `AGENTS.md` was modified locally with the intended DOX rules.
- No child `AGENTS.md` files existed.
- Historical validation backlog reports remained untracked.

## Git State After

After AGENTS/DOX commit:

- Root `AGENTS.md` is committed.
- Four child `AGENTS.md` files are committed.
- Phase 32.15 remains preserved in its own commit.
- Historical validation backlog files remain untracked and out of scope.
- This Phase 32.16 report is intentionally not included in the AGENTS-only commit.

## Phase 32.15 Package Status

Phase 32.15 is preserved in a separate commit:

- `facfa18 phase 32.15 add pbp ffopportunity splits`

No Phase 32.15 code, migration, validation, or report files were mixed into the AGENTS/DOX adoption commit.

## Root AGENTS Adoption Summary

Root `AGENTS.md` now includes:

- operating principles
- context discipline
- byte-capped command-output expectations
- code change rules
- DOX framework
- patterns to avoid
- validation discipline
- subagent guidance
- communication guidance
- child DOX index

The root child index now lists only created child files:

- `bigquery/AGENTS.md`
- `docs/rebuild/AGENTS.md`
- `src/AGENTS.md`
- `tests/AGENTS.md`

## Child AGENTS Files

Created:

- `bigquery/AGENTS.md`: BigQuery migrations, validations, views, warehouse SQL contracts, write-gate discipline, no global truncates, summary-first SQL-native evidence, and neutral aliases such as `row_count`.
- `src/AGENTS.md`: Python orchestration rules, BigQuery-heavy execution, no old Python full tournament path, missing metrics flagged rather than fabricated, and explicit phase approval for live rankings or champions.
- `tests/AGENTS.md`: Focused test placement, write-gate and no-live-output coverage, byte-capped output examples, and full discovery only when risk warrants it.
- `docs/rebuild/AGENTS.md`: Rebuild report and scorecard standards, evidence-first reporting, stable source matrix policy, and no implied champion or production activation.

Skipped:

- No other child AGENTS files were created. Additional boundaries can be added later when a folder gains durable local workflow rules.

## DOX Pass Result

Pass.

Checked:

- child docs do not weaken root rules
- child docs are concise and operational
- root child index matches the files created
- no stale contradiction found in the new DOX structure
- historical backlog files were not staged
- Phase 32.15 package stayed separate

## Checks Run

- Read root `AGENTS.md` fully.
- Inspected existing `AGENTS.md` files.
- `git diff --check -- AGENTS.md bigquery/AGENTS.md src/AGENTS.md tests/AGENTS.md docs/rebuild/AGENTS.md`
- `git diff --cached --name-only`
- `git diff --cached --stat`

Result:

- No whitespace errors printed.
- Git printed LF-to-CRLF working-copy warnings for AGENTS files on Windows. No content blocker.

## Files Intentionally Not Staged

- Historical Phase 17 through Phase 31 validation backlog reports.
- Existing untracked owner-review artifacts.
- Phase 32.16 report, because the AGENTS/DOX adoption commit was intentionally limited to root and child AGENTS files.

## No-Live-Change Confirmation

- No deployment.
- No live ranking regeneration.
- No champion formula activation.
- No Pigskin chat call.
- No Gemini or LLM-backed ranking generation.
- No live Sleeper API call.
- No old Python full tournament run.
- No BigQuery write.

## Remaining Warnings

- Historical validation backlog remains untracked by design.
- Git line-ending warnings appeared for AGENTS files on Windows.
- This Phase 32.16 report remains uncommitted unless the owner later wants it packaged.

## Recommended Next Phase

Phase 32.17 - fast RB/WR formula refinement with PBP xFP and Stats02 ideal fields.
