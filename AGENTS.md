# Coding Agent Instructions

## Operating Principles

Keep it simple. Simple is better than complex.
Assume the user is a principal engineer.
Make the smallest maintainable change that solves the actual request.
Prefer existing patterns over new abstractions.
Avoid broad refactors, speculative helpers, and clever architecture unless clearly justified.
Use judgment. Read enough surrounding code to understand the existing pattern, then avoid unnecessary exploration.
Optimize for correctness, speed, judgment, and token efficiency.
Correct the user when appropriate.
Prefer FAANG-level code quality: clear naming, strong types, simple control flow, minimal mutation, focused functions, pure functions/components where practical, and no unnecessary abstraction.

## Context Discipline

Protect context aggressively.

Answer the narrow question first. Inspect the smallest relevant file, symbol, route, component, diff, log, or test output.

Prefer targeted searches, focused file sections, nearby call sites, capped logs, and scoped validation. Avoid running validation commands like `npm run build`, `npm run test`, or `npm run lint` unless absolutely necessary. Use normal scoped commands like `rg`, with a byte cap when needed.

Avoid dumping full files, full logs, unrelated directories, broad repo searches, large diffs, or generated output after the relevant code is found.

Do not byte-cap instruction files, skill files, tool docs, or agent policy files. Read the whole relevant file unless it is unexpectedly huge.

## Command Output

Protect context usage. **Any command with unknown or potentially large output must be scoped and byte-capped.**

Byte-cap unknown or potentially large output. Line caps alone are unsafe because a single line can be huge.

```bash
COMMAND 2>&1 | head -c 4000
COMMAND 2>&1 | tail -c 4000
```

### Good Byte Capping Examples

```bash
rg -n -m 20 'functionName|ComponentName|routeName' src 2>&1 | head -c 200
bash -o pipefail -c 'npm run type-check 2>&1 | tail -c 500'
bash -o pipefail -c 'npm run test 2>&1 | tail -c 2000'
bash -o pipefail -c 'npm run build 2>&1 | tail -c 500'
rg -l "SEARCH_TERM" src 2>&1 | head -c 4000
```

Do not rely on `head -n`, `tail -n`, or `sed -n` as the only cap.

Scope before printing content: list files first, search specific paths, count matches when useful, and avoid reading generated, binary, minified, database, or huge JSON/JSONL files unless required.

Preserve exit codes when needed:

```bash
tmp="$(mktemp)"
COMMAND >"$tmp" 2>&1
status=$?
tail -c 5000 "$tmp"
rm -f "$tmp"
exit "$status"
```

Avoid unbounded `cat`, broad `rg`, `find`, `ls -R`, `git diff`, tests, builds, and `select *`.

If capped output is insufficient, narrow the command before increasing the cap.

## Code Changes

Prefer direct edits with the available patch tool.
Patch the narrow failing path first.
Avoid unrelated cleanup.
Do not add helpers, wrappers, maps, files, abstractions, or validation layers unless they clearly reduce complexity.

## DOX Framework

Use the DOX AGENTS.md hierarchy pattern from https://github.com/agent0ai/dox.

AGENTS.md files are binding work contracts for their subtrees.
Before editing, read the root AGENTS.md, identify the paths you expect to touch, then walk from the repo root to each target path and read every AGENTS.md found along that route.
The nearest AGENTS.md controls local details. Parent files still control repo-wide rules.
If docs conflict, the closer doc controls local work details, but child docs may not weaken root-level quality, safety, or workflow rules.

After meaningful changes, do a DOX pass before closing the task.
Update the closest owning AGENTS.md when a change affects durable structure, responsibilities, workflow, required inputs or outputs, permissions, constraints, artifacts, user preferences, or quality standards.
Update parent docs when parent-level structure, workflow, or the child index changes.
Remove stale or contradictory text instead of explaining history.
Small edits that do not change behavior or contracts may leave docs unchanged, but the DOX pass still applies.

Child AGENTS.md files should use this section order when created:

- Purpose
- Ownership
- Local Contracts
- Work Guidance
- Verification
- Child DOX Index

Keep DOX docs concise, current, and operational.
Document stable contracts, not diary entries.
Put broad rules in parent docs and concrete local rules in child docs.

## Patterns to Avoid

Avoid single-use abstractions.

Prefer inline types and direct logic when a helper, wrapper, map, or named type is used only once.

Avoid wrapper functions that simply call another function.

## Validation

Match validation to risk.

Skip validation for low-risk changes and say so plainly.
Use the cheapest useful check for risky changes.
Do not run full test suites or full builds unless risk justifies it or the user asks.

## Subagents

Use subagents only when they save context, save time, or materially improve output quality.

For research, review, and exploration tasks, avoid confirmation bias. Do not pass a preferred conclusion. Ask the subagent to investigate, compare, or verify, and require evidence, tradeoffs, uncertainty, and better alternatives.

Prefer subagents for:

- documentation/API checks
- web research
- non-trivial copywriting/content generation

Avoid subagents for trivial work the main agent can finish faster.

When using a subagent, assign a narrow task and require:

- findings
- files inspected
- files changed, if any
- validation run, if any
- risks or uncertainty

You own final judgment and integration.

## Public Rankings Publication

- The canonical release procedure is `docs/rankings-production-runbook.md`. Follow its ordered dry-run, promotion, verification, and all-profile publication gates.
- Public ranking feeds come from `unified_draft_rankings_current` plus active `analytics_pigskin_rankings` rows.
- Use `scripts/publish_public_rankings.py`. Run without `--publish` first; external writes require the explicit flag.
- Versioned board objects are content-addressed and create-only. Update `v1/manifest.json` last, after every immutable object succeeds.
- Unified Top 150 boards must preserve each active positional queue. Promotion must reject any player whose positional rank or source version differs from the active board. Expanding the board must preserve the prior Top 100 as an exact prefix unless a separately approved ranking change is included.
- Unified-board replacements must use committed BigQuery load jobs rather than streaming inserts so later profile promotions are not blocked by a streaming buffer.
- Teamless players are unranked. Candidate builders must move them to a watchlist, and public feed publication must fail closed if an overall or positional row has no current team.
- Rebuild Standard RB, WR, and TE together with `scripts/promote_standard_fable_v1_positional.py`; run it without `--apply` before opening the write gate.
- Current redraft WR candidates come from `v_wr_fable_v1_current_candidates`: preserve every qualified WR Fable v1 score exactly, allow only the documented prior-qualified veteran carry-forward when the latest season misses the volume threshold, and never admit a rookie through that fallback. Apply Sleeper status only afterward through `v_ranking_post_formula_safety`.
- Run `scripts/audit_current_player_ranking_coverage.py --fail-on-blocking` after candidate materialization and again after positional promotion. Do not build unified boards while it reports a blocking established-player omission.
- Public `pigskin_verdict` text must explain the rank with concrete formula inputs, tradeoffs, or risk. A sentence that only repeats the player and positional rank is invalid.
- Every identity repair, qualification fallback, guardrail, or manual adjustment that changes player coverage or order must persist a human-readable explanation in `rank_rationale` and granular warehouse evidence in `llm_adjustment_evidence`. The explanation must name the applicable source season, threshold, raw score, formula change status, and post-formula movement. Verify that both fields survive public JSON publication and the IONOS rankings import so Pigskin can defend the number. A phase report alone is not enough.
- Cloud ranking data is strictly scientific. Do not put Pigskin's site personality, roasts, slang, or show copy into formulas, warehouse evidence, model-run metadata, or `rank_rationale`. The GNG site prompt owns personality at response time.
- A formula change must register a new formula or ranking version, preserve the prior active rows in history, identify the changed metrics or weights and approved backtest, and state the per-player effect in `rank_rationale` when it materially changes coverage or order. `model_run_id`, `rank_source`, `model_name`, raw score, candidate rank, and final rank must remain traceable.
- Injury and suspension designations are context, not automatic penalties. Rank movement requires source-backed expected regular-season games missed. Store the event type, source, evidence timestamp, estimated games missed, adjustment code, formula-to-final rank movement, and unchanged formula score in the warehouse provenance fields. Carry a concise scientific explanation into `rank_rationale`. Unconfirmed missed time gets a visible review flag and zero absence movement.
- GNG public `context` is a separate presentation field. Build it from the active formula inputs with `scripts/build_gng_rank_context.py`; select a metric-driven player archetype instead of rotating generic templates, include GNG scoring effects, name metric gaps, and never change rank order while generating it.
- Raw formula scores belong in provenance fields. Public RB, WR, and TE `ranking_score` values must be normalized to `50-99`; never write a raw formula value directly into the public score field.
- Normal production publication must include Standard, PPR, Half-PPR, and GNG Keeper together, with exactly 150 overall players per profile. A profile subset replaces rather than merges the manifest.
- Missing positional context must remain null with a named warning. Never borrow stale context or fabricate a public verdict.
- The feed contract and consumer instructions live in `docs/public-rankings-json-feed.md`.

## Ranking Backtests

- Standard WR preseason formula comparisons use a fixed eligible Week 1 roster universe and next-season Standard total points as the primary objective. Keep six-game PPG results only as continuity evidence.
- Unknown advanced inputs use input-season neutral imputation with named missing counts. Structural source absence uses a source-backed fallback when available; encode zero only when its meaning is verified, and retain an explicit flag and method.

## Communication

Before editing, state the approach only for non-trivial tasks.

During complex work, keep updates short:

- what was found
- what changed
- what risk remains

After work, summarize:

- what changed
- files touched
- validation run, or why skipped
- remaining risk

Keep summaries short. Do not explain obvious edits.

## Child DOX Index

- `bigquery/AGENTS.md`
- `docs/rebuild/AGENTS.md`
- `src/AGENTS.md`
- `tests/AGENTS.md`
- `SumerStats/AGENTS.md`

Oververbosity:low
