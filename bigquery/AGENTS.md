# Purpose

BigQuery migrations, validations, views, and warehouse SQL contracts.

# Ownership

This subtree owns warehouse shape and SQL verification. Keep changes additive and scoped to the object, season, source, version, or run ID named by the phase.

# Local Contracts

- Prefer additive migrations. Do not use destructive DDL unless the owner explicitly approves that phase.
- No global truncates.
- Use bounded delete/insert or merge keys by season, source, version, model version, or run ID.
- Production ranking, champion, and live-output writes require an explicit owner-approved phase.
- Ranking overlay provenance must persist candidate rank, final rank delta, adjustment code, evidence, and any source-backed injury games-missed estimate.
- Sleeper injury review queues must retain status transitions and review state, and must not imply an automatic ranking adjustment.
- Write gates must fail closed and be unset after use.
- Validation files should match table grain, ranges, missing flags, provenance, and source exposure contracts.
- SQL-native tournament evidence stays summary-first unless an official detail snapshot is explicitly requested.
- Avoid BigQuery aliases such as `rows`; use neutral aliases like `row_count`, `source_count`, or `candidate_count`.
- Current-source snapshot archives are append-only and idempotent at their documented date-and-source grain. Historical backtests may use them only when a dated snapshot matches the prediction boundary.

# Work Guidance

Keep SQL readable and direct. Put heavy set operations in BigQuery, not Python. Do not expose raw/source tables to Pigskin-facing compatibility views unless a phase explicitly changes that contract.

# Verification

- For migration changes, run `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`.
- For changed tables, run focused validation patterns only.
- Run ranking backtest or formula validations only when those contracts changed.

# Child DOX Index

No child AGENTS.md files exist yet.
