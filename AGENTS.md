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

- Daily ranking automation: `PigskinDailyPublishImport` runs at 07:30 and 12:30 ET with two 30-minute retries. Rebuild Standard WR safety candidates before promotion, compare their source snapshot against current safety context, and fail the task on every unsuccessful refresh or import. See `docs/rankings-production-runbook.md`.
- Current-season weekly stats refresh uses `scripts/refresh_current_season_stats.py --season <year>` (dry-run) and `--apply` (transactional single-season replacement). See `docs/current-season-stats-refresh.md`. Report incomplete game coverage; never treat fresh stats ingestion as a ranking formula change.
- Separate in-season candidate research lives in `scripts/inseason_rankings.py` and `docs/inseason-rankings-baseline.md`. Keep its per-appearance, availability, scoring-completeness, and held-out validation limits visible; it must not overwrite Fable ranking provenance.
- Exact GNG in-season scoring reconstruction and ambiguity checks live in `scripts/inseason_gng_scoring.py` and `docs/inseason-gng-scoring-audit.md`. Null reviewed scores must not be silently replaced by partial reconstructions.

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
- Never add a player-specific exception to a gate. Judgment trace codes are review-only by code, and Sleeper hard reviews and QB cutline crossings are logged, not blocking. See "Owner Rules Removed 2026-09-27".
- Dry GNG promote validates the review tables left by the last apply run.
- Public `pigskin_verdict` text must explain the rank with concrete formula inputs, tradeoffs, or risk. A sentence that only repeats the player and positional rank is invalid.
- Every identity repair, qualification fallback, guardrail, or manual adjustment that changes player coverage or order must persist a human-readable explanation in `rank_rationale` and granular warehouse evidence in `llm_adjustment_evidence`. The explanation must name the applicable source season, threshold, raw score, formula change status, and post-formula movement. Verify that both fields survive public JSON publication and the IONOS rankings import so Pigskin can defend the number. A phase report alone is not enough.
- Cloud ranking data is strictly scientific. Do not put Pigskin's site personality, roasts, slang, or show copy into formulas, warehouse evidence, model-run metadata, or `rank_rationale`. The GNG site prompt owns personality at response time.
- A formula change must register a new formula or ranking version, preserve the prior active rows in history, identify the changed metrics or weights and approved backtest, and state the per-player effect in `rank_rationale` when it materially changes coverage or order. `model_run_id`, `rank_source`, `model_name`, raw score, candidate rank, and final rank must remain traceable.
- Injury and suspension designations are context, not automatic penalties. Rank movement requires source-backed expected regular-season games missed. Store the event type, source, evidence timestamp, estimated games missed, adjustment code, formula-to-final rank movement, and unchanged formula score in the warehouse provenance fields. Carry a concise scientific explanation into `rank_rationale`. Unconfirmed missed time gets a visible review flag and zero absence movement.
- Current positional row counts may vary when a formula-qualified player gains or loses a team. Keep exact contracts where the candidate pool is fixed; use a documented bounded integrity range for Standard RB and continue to fail on duplicates, teamless rows, missing verdicts, or non-contiguous ranks.
- GNG public `context` is a separate presentation field. Build it from the active formula inputs with `scripts/build_gng_rank_context.py`; select a metric-driven player archetype instead of rotating generic templates, include GNG scoring effects, name metric gaps, and never change rank order while generating it.
- Raw formula scores belong in provenance fields. Public RB, WR, and TE `ranking_score` values must be normalized to `50-99`; never write a raw formula value directly into the public score field.
- Normal production publication must include Standard, PPR, Half-PPR, and GNG Keeper together, with exactly 150 overall players per profile. A profile subset replaces rather than merges the manifest.
- Missing positional context must remain null with a named warning. Never borrow stale context or fabricate a public verdict.
- The feed contract and consumer instructions live in `docs/public-rankings-json-feed.md`.

## Owner Rules Removed 2026-09-27

Owner directive: "Remove any of my handwritten rules. Period. I want to start fresh."

Standing rule: no player-specific hand rules anywhere in the ranking pipeline. No name lists, pins, exclusions, floors, forced orders, or per-player gate exceptions. An uncertain judgment is left as the formula produced it and logged, never hard-coded, and never allowed to fail the daily cron. Those judgments will come from the AI decision layer (`docs/ai-decision-layer.md`) once each decision family is backtested.

Removed:

- `src/ranking_owner_decisions.py` (deleted): `STANDARD_WR_ELITE_ORDER` (plus its reorder in `build_standard_wr_fable_v1_safety_review.py` and the ASSERT in `promote_standard_fable_v1_positional.py`), `GNG_WATCHLIST_NAMES`, `COVERAGE_GATE_REVIEW_ONLY_DECISIONS` (Theo Wease, MarShawn Lloyd), and `GNG_INJURED_STARTER_HARD_REVIEW_DECISIONS` (Caleb Williams) with `is_owner_approved_injured_starter()`.
- The July PPR/Half `DECISIONS` pins and exclusions (`scripts/publish_ppr_fable_v1_candidate_boards.py`, deleted) and the `recommended_rank` override. `promote_ppr_fable_v1_positional.py` now rebuilds its candidates on every run from the approved formula views through `reception_candidates_sql()`; the static `ppr_fable_rankings_current` and `half_ppr_fable_rankings_current` tables are no longer read.
- GNG unified name and slot floors (Jeremiyah Love, QB4) in `build_unified_gng_2026_top100.py`.
- GNG WR live-rank continuity protection in `build_gng_2026_candidate_boards.py` (a floor anchored to yesterday's board, not part of any approved formula spec).

Kept, because they are facts or backtested formula, not opinions: the Marvin Harrison Jr identity override, the three documented GNG Sleeper identity aliases, `player_identity_overrides`, `manual_market_values`, `data/coaching_staff.csv`, and the Situation v1 `EFFECTS` and `WINPCT_2025` coefficients.

Gate behavior:

- Coverage gate blocks only on pipeline loss of an established player: `FABLE_FORMULA_TRANSFORM_DROPOUT`, `IDENTITY_BRIDGE_COLLISION`, `IDENTITY_BRIDGE_UNMAPPED`, `NOT_IN_RECEPTION_CANDIDATE_TABLES`. Judgment codes are review-only: `NO_2025_SITUATIONAL_SOURCE_ROW`, `BELOW_2025_FABLE_QUALIFICATION_THRESHOLD` (thin samples and depth-chart slot conflicts), `ROOKIE_SYSTEM_REQUIRED`, `QB_COVERAGE_REVIEW`, `POSITIONAL_PROMOTION_OR_BOARD_CUTOFF`.
- A Sleeper hard review (QB depth over 1, injury-driven depth drop, IR or another non-Active status) no longer blocks the GNG promote preflight or the Standard WR preflight. The player stays on the board with his flags.
- A Standard QB6/QB24 cutline crossing is recorded in `rank_rationale` and provenance (`CUTLINE_CROSSING_RECORDED`); the guarded formula rank stands. `--acknowledge-crossings` is gone.
- Every review-only case is appended to `output/review-log/<gate>.jsonl` through `src/review_log.py`.
- Structural gates are unchanged and still fail closed: row contracts, teamless players, missing Sleeper context, contiguity, queue mismatches, SHA and version checks, and zero-warning feed validation.

## Ranking Backtests

- Standard WR preseason formula comparisons use a fixed eligible Week 1 roster universe and next-season Standard total points as the primary objective. Keep six-game PPG results only as continuity evidence.
- Unknown advanced inputs use input-season neutral imputation with named missing counts. Structural source absence uses a source-backed fallback when available; encode zero only when its meaning is verified, and retain an explicit flag and method.

## AI Decision Layer

- Owner rulings and the as-built availability pilot live in `docs/ai-decision-layer.md`. Decisions are context only until backtested: they never move a rank, board, candidate, unified, or safety row.
- The availability stage runs in the daily chain after `inseason-ranking-horizons` and before the dataset uploads and publish, inside try/catch with a 15-minute bound. It covers every currently injured player at every position (Sleeper for QB/RB/WR/TE/K/DEF; the official report and weekly roster reserve lists for positions the Sleeper snapshot does not store). It must never fail the chain or change the four profiles: on any failure the `availability` dataset is skipped and the publisher carries the previous object forward.
- The availability pilot (`src/availability_*.py`, `scripts/*availability*.py`) writes only `availability_*` tables in `fantasy_football_brain`; `src/availability_bq.py` enforces the prefix. Below a question's confidence threshold the field stays NULL and the miss is logged in `availability_decision_misses`; never guess, and never hand-write player rules.
- The public `availability` dataset (`src/availability_feed.py`, schema `availability-1.0`) is fixed: the site importer rejects the whole object on any violation. Validate before writing, keep `base_rate` and all eight `text` keys present for every player, keep text null when blank or textless, and add fields only with an explicit contract update in `docs/public-rankings-json-feed.md`.
- Jev (TypeSafe) gets only code-built facts: code does every date, schedule, count, and probability and writes them into the state as plain text. Base-rate priors come from the versioned artifacts `docs/availability-base-rates-v1.json` (QB/RB/WR/TE), `docs/availability-base-rates-other-v1.json` (every other position), and `docs/availability-next-buckets-v1.json` (feed-only next-game buckets); refitting any of them is a new version. Read the key from `TYPESAFE_API_KEY` or `E:\cbs-league-history\.secrets\typesafe-ai-api.txt`; never print, log, or commit it.

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
