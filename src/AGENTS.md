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
- Sleeper status refreshes update display context only. New OUT or IR transitions create an auditable pending review and never change ranks automatically.
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
