# Pigskin Documentation Index

Pigskin is a cost-conscious, data-backed fantasy football projection and ranking platform: weekly projections, rest-of-season and dynasty rankings, trade reviews, fraud watch, sleeper breakouts, team reviews, and evidence packets for the show's writing AI.

Start here: [CODEX_PROJECT_CONTEXT.md](CODEX_PROJECT_CONTEXT.md) is the architectural source of truth. Every other document defers to it.

## Runtime

Pigskin is a **Cloud Run Jobs workload with no service and no UI**. The Streamlit admin app was retired. `src/job_runner.py` is the single entrypoint:

```bash
python -m src.job_runner --help
python -m src.job_runner --job-name materialize-analytics --season 2026
```

Warehouse migrations and validations run from `scripts/`:

```bash
python scripts/run_bigquery_migrations.py --list-pending
python scripts/run_bigquery_validations.py --run --pattern claim
```

## Naming

- **Pigskin** is the platform and the on-air analytical co-host persona.
- **meatbag** is domain vocabulary for a human analyst. It is deliberately retained in the Meatbag Claim Ledger, the `meatbag_accountability_show` brief type, and the `meatbag_delta` columns, where it means "the human's claim" and not "the platform".

## Architecture and Operating Model

| Document | Purpose |
| --- | --- |
| [CODEX_PROJECT_CONTEXT.md](CODEX_PROJECT_CONTEXT.md) | Architectural source of truth: target stack and the twelve hard architectural rules. |
| [rebuild/audit-and-rebuild-plan.md](rebuild/audit-and-rebuild-plan.md) | Repository audit, the Cloud Run architecture decision record, and the phased rebuild plan. |
| [rebuild/cloud-run-operating-model.md](rebuild/cloud-run-operating-model.md) | Long-term operating model. Cloud Run Jobs only: no service, no Firebase. |
| [rebuild/cloud-run-jobs.md](rebuild/cloud-run-jobs.md) | Job-ready path for long-running warehouse work. |
| [rebuild/cloud-scheduler-plan.md](rebuild/cloud-scheduler-plan.md) | Planned Cloud Scheduler triggers. No live scheduler resources yet. |
| [rebuild/data-ops-cloud-run-jobs-rollout.md](rebuild/data-ops-cloud-run-jobs-rollout.md) | The default-off live Cloud Run Jobs dispatch path. |
| [../deploy_guide.md](../deploy_guide.md) | Building the image and deploying each Cloud Run Job. |

## Warehouse

| Document | Purpose |
| --- | --- |
| [rebuild/bigquery-migration-process.md](rebuild/bigquery-migration-process.md) | How to write and run forward-only numbered migrations. |
| [rebuild/bigquery-validation-process.md](rebuild/bigquery-validation-process.md) | How to write and run the validation queries that gate activation. |
| [rebuild/bigquery-query-guardrails.md](rebuild/bigquery-query-guardrails.md) | Query cost and safety guardrails. |
| [rebuild/current-warehouse-inventory.md](rebuild/current-warehouse-inventory.md) | Every table, its classification, and who reads it. |
| [rebuild/table-classification.md](rebuild/table-classification.md) | Raw / staging / mart classification and what is safe to expose. |
| [rebuild/compatibility-contracts.md](rebuild/compatibility-contracts.md) | Index of the compatibility-object layer. |
| [../bigquery/contracts/](../bigquery/contracts) | One contract per warehouse object. 48 contracts. |

## Daily Player Watch

Runs at 07:00 America/New_York, then 07:15 for the detection pass. Confirms team, status, injury, depth chart, and age from Sleeper; records what changed; pulls team beat coverage for changes worth investigating.

| Document | Purpose |
| --- | --- |
| [../bigquery/contracts/sleeper_players_history.md](../bigquery/contracts/sleeper_players_history.md) | Append-only snapshot history. Without it, change detection is impossible. |
| [../bigquery/contracts/player_status_changes.md](../bigquery/contracts/player_status_changes.md) | One row per changed field, and which changes warrant a news lookup. |
| [../bigquery/contracts/team_news_items.md](../bigquery/contracts/team_news_items.md) | Beat-writer items for teams that had a triggering change. |
| [../bigquery/contracts/player_news_matches.md](../bigquery/contracts/player_news_matches.md) | Links an item to the changed player it mentions. |
| [rebuild/cloud-scheduler-plan.md](rebuild/cloud-scheduler-plan.md) | The 7 AM Eastern triggers, with the time-zone rule. |

```bash
python -m src.job_runner --job-name ingest-sleeper-news
python -m src.job_runner --job-name detect-player-changes --dry-run
```

Team feeds are commentary, not an authoritative injury source. Sleeper's `status` and `injury_status` are the flag; the feed is context for investigating it.

**Sleeper API discipline.** The `/v1/players/` map is ~5MB and Sleeper limits it to once per day, so `ingest-sleeper-news` is its only caller, fetches it with `?active=true`, and skips if today's snapshot already exists (`--force` overrides). Every other job — including on-demand `ingest-sleeper-league` — reads the saved `sleeper_players_current` snapshot rather than calling the endpoint again. Per-league endpoints (`/league`, `/rosters`, `/matchups`) have no such limit and stay live. Run `ingest-sleeper-news` before `ingest-sleeper-league`, or the league job errors that the snapshot is empty.

## Coaching Staff

First coaching layer: current staff for all 32 teams across eight roles, for agent context. Curated from the Wikipedia current-staffs page via a reviewed CSV; coaching styles and historical records are later layers.

| Document | Purpose |
| --- | --- |
| [rebuild/coaching-staff-layer.md](rebuild/coaching-staff-layer.md) | The layer: table, curation, and feed integration. |
| [../bigquery/contracts/coaching_staff_current.md](../bigquery/contracts/coaching_staff_current.md) | The `coaching_staff_current` table. |

```bash
python -m src.job_runner --job-name ingest-coaching-staff
python -m src.job_runner --job-name coaching-staff-feed
```

The public feed is JSON, content-addressed, published to a Cloud Storage bucket the ranking project owns (`.../v1/manifest.json`). The coaching-staff-feed job emits an immutable dataset object plus a manifest entry; the ranking project's `publish_public_rankings.py` merges that entry, since it is the single writer of the mutable manifest.

## Situation Layer

Team/QB/coaching/age context per player — what production metrics can't see. Facts and flags only; rank adjustments are Phase 3, gated on the BQML effect study. Boards are schema 1.3 with per-player `situation` + `metrics` blocks; the manifest carries `datasets.player_situation`; the daily chain writes an owner-review queue of flagged ranked players.

| Document | Purpose |
| --- | --- |
| [rebuild/situation-layer.md](rebuild/situation-layer.md) | The layer: table, feed, review queue, ML study results. |

```bash
python -m src.job_runner --job-name build-situation-layer
python -m src.job_runner --job-name situation-feed
python scripts/run_situation_ml_study.py --report-only
```

## Modeling and Evidence

| Document | Purpose |
| --- | --- |
| [rebuild/projection-engine-v1.md](rebuild/projection-engine-v1.md) | Deterministic weekly, rest-of-season, and dynasty projection layer. |
| [rebuild/backtesting-v1.md](rebuild/backtesting-v1.md) | Projection-evaluation framework and calibration bins. |
| [rebuild/market-consensus-baselines.md](rebuild/market-consensus-baselines.md) | Source-agnostic outside-baseline layer. |
| [rebuild/meatbag-claim-ledger.md](rebuild/meatbag-claim-ledger.md) | Manual-entry layer tracking human analyst claims. |
| [rebuild/claim-grading-v1.md](rebuild/claim-grading-v1.md) | Turns ledger entries into deterministic accountability rows. |
| [rebuild/content-brief-orchestrator.md](rebuild/content-brief-orchestrator.md) | Assembles evidence-backed show prep briefs. |

## Retired UI Layer

The Streamlit app and its chat surface were retired. These documents record what existed, how each read path was resolved, and what a future consumer surface must follow.

| Document | Purpose |
| --- | --- |
| [rebuild/ui-query-debt-register.md](rebuild/ui-query-debt-register.md) | **Closed register.** How each UI read path resolved, plus the read contract for future consumers. |
| [rebuild/streamlit-compat-rollout.md](rebuild/streamlit-compat-rollout.md) | **Retired.** The flag-gated migration that the UI retirement completed. |
| [rebuild/pigskin-context-tools.md](rebuild/pigskin-context-tools.md) | The parameterized context tools that replaced arbitrary model SQL. No consumer yet. |

## Validation Reports

Point-in-time gate records. They are historical: they are not updated after the fact, and each is stamped with the date it was run.

| Report | Date | Outcome |
| --- | --- | --- |
| [rebuild/validation/phase-12-validation-report.md](rebuild/validation/phase-12-validation-report.md) | 2026-06-16 | GO WITH WARNINGS |
| [rebuild/validation/phase-8-11-final-green-gate.md](rebuild/validation/phase-8-11-final-green-gate.md) | 2026-06-16 | Green gate |
| [rebuild/validation/phase-8-11-validation-report.md](rebuild/validation/phase-8-11-validation-report.md) | 2026-06-16 | Phase 8-11 detail |
| [rebuild/validation/7.2C-go-no-go.md](rebuild/validation/7.2C-go-no-go.md) | Prompt 7.2C | Go/No-Go on replacing arbitrary SQL |
| [rebuild/validation/7.2C-validation-report.md](rebuild/validation/7.2C-validation-report.md) | Prompt 7.2C | Security and architecture detail |

## Conventions

Documents cite code by symbol, not by line number:

```text
`src/job_runner.py:dispatch_run_projections`   good, survives edits to the file
`src/job_runner.py:211`                        bad, silently rots
```

Verify every citation still resolves:

```bash
python scripts/check_doc_refs.py
```

The check fails if a cited symbol no longer exists, and reports any line-number citations that have crept back in. Validation reports are skipped: they are frozen records and may cite code that has since been removed.
