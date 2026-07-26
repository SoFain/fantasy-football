# Purpose

Python orchestration, ingestion helpers, SQL builders, and application support code.

# Ownership

This subtree owns runtime and orchestration behavior. Keep Python focused on control flow, validation, command dispatch, and BigQuery job submission.

# Local Contracts

- Python orchestrates BigQuery. BigQuery does heavy set operations.
- Do not revive the old Python tournament result-row path for official ranking research.
- No Python loops over full player/candidate/week tournament rows for the official path.
- No pandas or DataFrame full-tournament loads for summary paths.
- External or public data ingestion should reuse existing repo patterns where practical.
- Missing metrics must be flagged, not fabricated or silently zero-filled.
- Live rankings and champions are not touched without explicit phase approval.
- LLM ranking overlays must preserve the deterministic candidate score, use a bounded adjustment code, and reject unsourced injury games-missed claims before writes.
- Cloud ranking prompts and stored outputs are scientific only. Site personality must never enter ranking calculations, provenance fields, or `rank_rationale`.
- Injury and suspension movement requires a source-backed regular-season games-missed estimate. The final `rank_rationale` must preserve the formula explanation and append the event type, expected games missed, evidence, candidate-to-final movement, and confirmation that the formula score did not change.
- Sleeper status refreshes update display context only. New OUT or IR transitions create an auditable pending review and never change ranks automatically.
- GNG current-board Sleeper safety uses bounded depth-chart adjustments. Teamless players are structurally unranked; inactive, injury, unknown-depth, and rookie states produce review flags rather than automatic status-based rank changes.
- Future Fable board builders must consume `fantasy_football_advanced_metrics.v_ranking_post_formula_safety` after formula scoring instead of copying current-status rules into each promotion path.
- Durable owner-approved ranking exceptions live in `src/ranking_owner_decisions.py`; current-board builders must import them instead of keeping divergent local name lists.
- Player Profiles `ALL` boards and Pigskin `ALL` context must use `unified_draft_rankings_current`; positional scores must never be re-sorted into a substitute overall board.
- Player-facing adjustment labels must explain the effect in plain language while preserving the stored adjustment code for audit.
- Write paths require phase-specific gates and must fail closed.
- Current-source archive builders should fetch once, write the dated snapshot idempotently, and derive current context from the newest completed snapshot.

# Work Guidance

Prefer direct functions and local patterns over new frameworks. Keep SQL builders deterministic and testable. Avoid wrappers that only call one other function.

# Verification

- Run focused unit tests for edited modules.
- Compile edited modules when possible.
- Run full test discovery only for high-risk source changes or explicit request.

# Child DOX Index

No child AGENTS.md files exist yet.
