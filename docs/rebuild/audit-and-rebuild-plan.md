# Audit and Rebuild Plan

Status: **historical, partially superseded.** This document audited the repository as a single Streamlit application and laid out a phased plan to move data access and job orchestration out of the UI. Phases 1 through 12 delivered the warehouse and job layers; the UI was then retired outright rather than migrated.

Sections 1 through 3 have been updated to describe the current repository. Sections 4 onward are preserved as the original audit record: they describe problems in code that no longer exists, and their remediation roadmap is largely complete by deletion. Read them for the reasoning, not the current state.

Current state lives in [docs/README.md](../README.md), [cloud-run-operating-model.md](cloud-run-operating-model.md), and [ui-query-debt-register.md](ui-query-debt-register.md).

Source of truth: [docs/CODEX_PROJECT_CONTEXT.md](../CODEX_PROJECT_CONTEXT.md)

This audit is repository-based. It does not change runtime behavior.

## Architecture Decision Record: Cloud Run Operating Model

Decision: stay on Cloud Run for the admin/UI app and Python job execution.

Rationale:

- The current repo already deploys Streamlit on Cloud Run.
- No Firebase implementation exists in the tracked repository.
- Cloud Run Jobs are a better fit for the existing Python ETL, materialization, ranking, evidence packet, and backtest jobs.
- Staying on Cloud Run reduces migration risk and keeps the rebuild focused on BigQuery contracts, job isolation, and model-run governance.

Consequences:

- Future sprints should not create Firebase, Firestore, Firebase Functions, or Firebase Hosting artifacts unless the user explicitly requests a new platform decision.
- Long-running work should move from the Streamlit request process to Cloud Run Jobs.
- Scheduled work should use Cloud Scheduler triggers.
- Operational metadata should stay in BigQuery admin tables unless a future migration introduces a dedicated metadata store.
- Future sprint docs should point to [docs/rebuild/cloud-run-operating-model.md](cloud-run-operating-model.md).

## 1. Current Repository Structure

The original audit described a compact single-app ETL stack. Phases 1 through 12 added a warehouse contract layer, a job layer, and a test suite. The tracked repository is now as follows, abbreviated to directories and primary entrypoints:

```text
.
├── AGENTS.md                     agent working rules
├── Dockerfile                    Cloud Run Jobs image
├── cloudbuild.yaml               Cloud Build deploy config
├── validate.py                   standalone validation sweep
├── requirements.txt
├── bigquery/
│   ├── contracts/                44 table contracts, one per warehouse object
│   ├── migrations/               24 numbered forward-only DDL migrations
│   ├── validations/              138 validation queries
│   └── views/                    6 view definitions
├── data/                         sample CSV fixtures
├── docs/
│   ├── CODEX_PROJECT_CONTEXT.md  architectural source of truth
│   └── rebuild/                  phase design docs and validation reports
├── scripts/
│   ├── check_doc_refs.py         verifies doc code references still resolve
│   ├── run_bigquery_migrations.py
│   └── run_bigquery_validations.py
├── src/                          46 modules: ingest, materialize, projections,
│                                 packets, claims, backtests, job runner
└── tests/                        24 unittest modules
```

See [docs/README.md](../README.md) for an index of the documentation set.

Untracked local or generated items include `build/`, `dist/`, `venv/`, `__pycache__/`, `.codex-remote-attachments/`, `.codex-tools/`, and the local service account JSON file. Note that `AI_vs_Vibes_Project_Resume_Report.md` and `partner_github_workflow_rules.md` are tracked, contrary to the original audit.

The runtime is Cloud Run Jobs. `Dockerfile` builds a jobs image whose entrypoint is `src/job_runner.py`; it has no HTTP listener and exposes no port. [deploy_guide.md](../../deploy_guide.md) documents deployment with BigQuery, Secret Manager, Gemini, and Vertex AI Search environment settings.

No Firebase implementation exists in the tracked repository. That is now an explicit platform decision, not a gap to fill.

## 2. Runtime, Entrypoints, Scheduled Jobs, and Data-Access Patterns

### Runtime

The runtime is Cloud Run Jobs. There is no service, no web routes, and no UI.

The Streamlit admin app described by the original audit was retired. Its seven tabs (Pigskin Studio, Show Prep, Player Profiles, Versus Finder, Viewer Team Lab, Trade Lab, Data Ops) no longer exist. What each tab did is recorded in [ui-query-debt-register.md](ui-query-debt-register.md) along with the backend module that now owns the equivalent read.

Authentication is no longer relevant: there is no interactive surface to gate. `DASHBOARD_USERNAME` and `DASHBOARD_PASSWORD` are unused.

### Entrypoints

`src/job_runner.py` is the single entrypoint. It accepts `--job-name` from a fixed list and dispatches to a module:

- `ingest-nflverse`, `ingest-sleeper-news`, `ingest-sleeper-league`, `ingest-context-events`, `ingest-market-values`, `ingest-college-stats`, `ingest-rookie-scouting`
- `materialize-analytics`
- `generate-pigskin-rankings`, `generate-evidence-packets`
- `run-projections`, `run-backtests`
- `validate-warehouse`, `verify-external-context`

Every execution records a row in `cloud_run_job_runs` through `src/cloud_run_jobs.py`.

Two supporting scripts run outside the job runner: `scripts/run_bigquery_migrations.py` and `scripts/run_bigquery_validations.py`.

### Scheduled Jobs

No scheduled job definitions exist in the repo. There is no Cloud Scheduler config, GitHub Actions schedule, cron file, or equivalent scheduled worker. [cloud-scheduler-plan.md](cloud-scheduler-plan.md) describes the intended triggers.

Jobs are currently invoked manually through the CLI. Live Cloud Run Job dispatch exists in `src/cloud_run_jobs.py` but stays behind `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` and `DATA_OPS_ALLOW_JOB_TRIGGER`, both default false.

### Data-Access Patterns

All BigQuery access is server-side, in `src/`, through `src/bigquery_guardrails.py`.

The request-time patterns the original audit flagged are gone with the UI: the cached query helper, the defensive SQL-repair layer for model-generated SQL, the warehouse-metrics table scan, and the `dashboard_job_runs` admin writes. `cloud_run_job_runs` supersedes `dashboard_job_runs` for job metadata.

Pigskin previously exposed a model tool named `execute_bigquery_sql`. That was removed in 7.2C in favor of parameterized declarations in `src/pigskin_context_tools.py`, and the chat surface that would have registered them is itself now retired. No LLM path can generate SQL.

## 3. Existing BigQuery Datasets, Tables, Queries, and Migrations Found

Default dataset name is `fantasy_football_brain`. The BigQuery project is intended to be `fantasy-football-498121`, and `src/load.py:load_df_to_partitioned_table` loads DataFrames to partitioned tables using range partitioning on `season`.

### Raw and Source-Like Tables

The main NFL pipeline is `src/pipeline.py:run_pipeline`. It extracts, transforms, loads, then calls `materialize_all` in `src/pipeline.py:run_pipeline`.

Tables loaded by the main pipeline include:

- `play_by_play`, `src/pipeline.py:run_pipeline`.
- `weekly_metrics`, `src/pipeline.py:run_pipeline`.
- `team_descriptions`, `src/pipeline.py:run_pipeline`.
- `draft_picks`, `src/pipeline.py:run_pipeline`.
- `player_rosters`, `src/pipeline.py:run_pipeline`.
- `player_contracts`, `src/pipeline.py:run_pipeline`.
- `ngs_passing`, `ngs_rushing`, `ngs_receiving`, `ftn_charting`, `weekly_snap_counts`, `injury_reports`, and `depth_charts`, `src/pipeline.py:run_pipeline`.

### Analytics and Evidence Marts

`src/materialize.py` creates current analytics marts:

- `analytics_game_environment`, `src/materialize.py:build_game_environment_sql`.
- `analytics_player_weekly_truth`, `src/materialize.py:build_player_weekly_truth_sql`.
- `analytics_fraud_watch`, `src/materialize.py:build_fraud_watch_sql`.
- `analytics_pigskin_rankings_candidates`, `src/materialize.py:build_pigskin_rankings_sql`.
- `analytics_pigskin_rankings_history`, `src/materialize.py:build_pigskin_rankings_history_create_sql`.
- `analytics_player_qb_weekly`, `src/materialize.py:build_player_qb_weekly_sql`.
- `analytics_player_qb_splits`, `src/materialize.py:build_player_qb_splits_sql`.

`src/generate_pigskin_rankings.py` reads candidates from `analytics_pigskin_rankings_candidates` at `src/generate_pigskin_rankings.py:fetch_candidates`, then writes:

- `analytics_pigskin_rankings`, `src/generate_pigskin_rankings.py:write_rankings`.
- `analytics_pigskin_rankings_history`, `src/generate_pigskin_rankings.py:write_rankings`.

### External Context, News, and Market Tables

- `analytics_api_usage_daily`, `src/verify_player_context.py:ensure_usage_table`.
- `analytics_external_context_search_results`, `src/verify_player_context.py:ensure_results_table` and `src/verify_player_context.py:store_results`.
- `sleeper_players_current`, `src/ingest_news.py:load_realtime_news`.
- `realtime_player_news`, `src/ingest_news.py:load_realtime_news`.
- `market_values`, `src/fetch_market_values.py:TABLE_ID` and `src/fetch_market_values.py:upload_to_bigquery`.
- `analytics_context_events`, `src/ingest_context_events.py:load_context_events`.
- `college_player_stats`, `src/setup_college_tables.py:create_college_tables` and `src/ingest_college_data.py:TABLE_ID`.
- `rookie_scouting_metrics`, `src/setup_college_tables.py:create_college_tables`, loaded by the `ingest-rookie-scouting` job via `src/ingest_rookie_scouting.py:load_rookie_scouting`.

### Sleeper League Tables

`src/ingest_sleeper_league.py:SLEEPER_TABLE_SCHEMAS` defines schemas for:

- `sleeper_leagues`
- `sleeper_league_users`
- `sleeper_rosters`
- `sleeper_roster_players`
- `sleeper_matchups`
- `sleeper_lineups`
- `sleeper_available_players`
- `sleeper_viewer_team_snapshots`

Rows are assembled into those tables in `src/ingest_sleeper_league.py:build_records` and appended to BigQuery in `src/ingest_sleeper_league.py:load_rows`.

### Migrations and Schema Governance

No conventional migration directory was found. There are inline `CREATE TABLE`, `CREATE OR REPLACE TABLE`, `MERGE`, and load-job schemas inside Python modules. This is workable for the prototype, but it is not enough for the source-of-truth requirements in `docs/CODEX_PROJECT_CONTEXT.md:24-29`, especially versioned runs, repeatability, validation, and data dictionaries.

`validate.py` provides partition and dry-run validation utilities at `validate.py:run_dry_run` and `validate.py:validate_pipeline_upload`, but it does not validate every transformation or all analytics mart invariants.

## 4. Current Data Ingestion Paths for nflverse and Sleeper

### nflverse and nflreadpy

the `nflreadpy` import in `src/extract.py` imports `nflreadpy as nfl`. Current extractors cover:

- Play-by-play, `src/extract.py:get_pbp_data`.
- Weekly player stats, `src/extract.py:get_weekly_data`.
- Teams, draft picks, players, and contracts, `src/extract.py:get_team_data`.
- NGS passing, rushing, and receiving, `src/extract.py:get_ngs_passing_data`.
- FTN charting, `src/extract.py:get_ftn_charting_data`.
- Snap counts, `src/extract.py:get_snap_counts_data`.
- Injuries, `src/extract.py:get_injury_reports_data`.
- Depth charts, `src/extract.py:get_depth_charts_data`.

The end-to-end pipeline is `src/pipeline.py:run_pipeline`, with extracts imported at the `src.extract`, `src.transform`, `src.load`, and `src.materialize` imports in `src/pipeline.py`, transforms imported at the `src.extract`, `src.transform`, `src.load`, and `src.materialize` imports in `src/pipeline.py`, and materialization imported at the `src.extract`, `src.transform`, `src.load`, and `src.materialize` imports in `src/pipeline.py`.

### Sleeper API

Sleeper global player and trending data is loaded by `src/ingest_news.py`.

- The Sleeper throttle is set to `SLEEPER_MAX_CALLS_PER_MINUTE = 900` in `src/ingest_news.py:SLEEPER_MAX_CALLS_PER_MINUTE`.
- Sleeper API calls use `sleeper_get`.
- Global player map is fetched from `/players/nfl` at `src/ingest_news.py:load_realtime_news`.
- Trending adds and drops are fetched at `src/ingest_news.py:load_realtime_news`.
- Current player metadata is written to `sleeper_players_current` at `src/ingest_news.py:load_realtime_news`.
- Trending records are written to `realtime_player_news` at `src/ingest_news.py:load_realtime_news`.

Sleeper league and viewer-team snapshots are loaded by `src/ingest_sleeper_league.py`.

- The base URL is defined at `src/ingest_sleeper_league.py:SLEEPER_TABLE_SCHEMAS`.
- API calls reuse `sleeper_get` at `src/ingest_sleeper_league.py:SLEEPER_TABLE_SCHEMAS` and `src/ingest_sleeper_league.py:fetch_json`.
- The CLI entrypoint is defined at `src/ingest_sleeper_league.py:main`.
- The retired Viewer Team Lab called this module; `src/viewer_team_context.py` is the current consumer.

### Other Adapters

- FantasyCalc market values: `src/fetch_market_values.py:TABLE_ID`, loaded via `insert_rows_json` at `src/fetch_market_values.py:upload_to_bigquery`.
- CFBD college stats: `src/ingest_college_data.py:TABLE_ID`, loaded at `src/ingest_college_data.py:upload_to_bigquery`.
- User or manually curated context events: `src/ingest_context_events.py:load_context_events`.
- External verification through Vertex AI Search: `src/verify_player_context.py:build_vertex_serving_config`, with daily usage limits enforced in `src/verify_player_context.py:verify_player_context`.

## 5. Current Projection and Ranking Logic

### Pigskin Rankings

The ranking flow is now partially LLM-authored:

1. `src/materialize.py:build_pigskin_rankings_sql` creates `analytics_pigskin_rankings_candidates`.
2. `src/generate_pigskin_rankings.py:fetch_candidates` fetches candidates.
3. `src/generate_pigskin_rankings.py:build_prompt` builds the Pigskin prompt.
4. The prompt explicitly says the SQL rank is evidence, not the final ranking, and tells the model to adjudicate using opportunity quality, split EPA, WOPR history, target-share history, carry-share history, role quality, role fragility, current Sleeper team, current Sleeper depth chart, and sustainability.
5. `src/generate_pigskin_rankings.py:call_gemini` calls Gemini with `google-genai`.
6. `src/generate_pigskin_rankings.py:normalize_model_rankings` validates the model output against the candidate set and fails if candidates are missing, duplicated, or unknown.
7. `src/generate_pigskin_rankings.py:write_rankings` writes active and history tables.

This is directionally correct for the Pigskin identity. The major gap is that the version key is `ranking_version`, generated in `src/generate_pigskin_rankings.py:generate_rankings`, not a full `model_run_id` with source freshness, feature config version, scoring profile, league type, roster format, and creation timestamp.

### Player Profiles

Player Profiles read several warehouse tables directly, including:

- `player_rosters`, `src/player_profiles.py`.
- `analytics_player_weekly_truth`, `src/player_profiles.py`.
- `player_contracts`, `src/player_profiles.py`.
- `depth_charts`, `src/player_profiles.py`.
- `college_player_stats`, `src/player_profiles.py`.
- `rookie_scouting_metrics`, `src/player_profiles.py`.
- `analytics_pigskin_rankings`, written by `src/generate_pigskin_rankings.py`.

Canonical Pigskin rankings live in `analytics_pigskin_rankings`, with history in `analytics_pigskin_rankings_history`.

### Pigskin Chat

Pigskin chat has a detailed schema and behavioral prompt in `src/pigskin_context_tools.py`. It instructs the model to query `analytics_pigskin_rankings` first for ranking questions, to use `analytics_pigskin_rankings_history` for older ranking calls, and to prefer `analytics_player_weekly_truth` for non-ranking player analysis.

The model no longer receives a general SQL execution tool. It now calls fixed context tools backed by curated marts and compatibility objects. The remaining risk is incomplete mart coverage, not arbitrary model-written SQL.

### Trade Lab

The retired Trade Lab read `market_values` directly and ran local value/projection logic in the app process. `compat_trade_assets_current` now provides a production mart/view/helper path for future default-off wiring. Its AI outlook still has separate query debt around weekly history and external leads.

There is no model-runed projection system for trade values, rest-of-season rankings, dynasty rankings, best ball rankings, or weekly projections yet.

## 6. Current Admin Panel Capabilities

The retired Streamlit admin panel supported the following. Each Data Ops control below now corresponds to a job name in `src/job_runner.py`; the status and upload surfaces have no replacement.

- Basic login through environment variables. No replacement; there is no interactive surface.
- Warehouse status cards based on `client.list_tables` and `table.num_bytes`. No replacement.
- Last successful run display using `dashboard_job_runs`. Superseded by `cloud_run_job_runs` via `src/cloud_run_jobs.py`.
- Validation sweep, the "Run Validation Sweep" control, running `validate.py`.
- Realtime Sleeper/news ingest, the "Ingest Realtime Player News" control, running `src.ingest_news`.
- Context event ledger ingest, the "Load Context Event Ledger" control, running `src.ingest_context_events`.
- FantasyCalc market values ingest, the "Ingest FantasyCalc Market Values" control, running `src.fetch_market_values`.
- External player context verification, the "Verify Player Context" control, running `src.verify_player_context`.
- CFBD college stats ingest, the "Ingest CFBD College Stats" control, running `src.ingest_college_data`.
- Main NFL statistics ingestion, the "Run Ingestion Pipeline" control, running `src.pipeline`.
- Pigskin ranking generation, the "Generate Pigskin Rankings" control, running `src.generate_pigskin_rankings`.
- Rookie scouting CSV upload to BigQuery, the `scouting_csv_uploader` file uploader and its "Upload and Import Scouting Metrics" control.
- Viewer team load and console from Sleeper. Backend read survives in `src/viewer_team_context.py`; the console does not.
- Show Prep with Fraud Watch, Sleeper Watch, and Reddit topic scout. Fraud and sleeper reads survive in `src/segment_packets.py` and `src/sleeper_watch.py`; the Reddit scout does not.

The control names above are historical. Use `python -m src.job_runner --help` for the current job list.

This is useful for an early operating console, but it combines UI, job orchestration, warehouse mutation, BigQuery querying, and LLM workflows in one large file.

## 7. Current Anti-Patterns and Gaps

### Raw BigQuery Scans From UI/Admin

Present.

Examples:

- Sleeper Watch uses raw `weekly_metrics` in the UI query, `src/sleeper_watch.py`.
  - Rebuild status: `compat_sleeper_watch_candidates` has a production backing mart, view, materializer, helper, and validations. `src/sleeper_watch.py` is now the only read path.
- Player Profiles read source-like `player_rosters`, `player_contracts`, `depth_charts`, `college_player_stats`, and `rookie_scouting_metrics` directly, `src/player_profiles.py`.
- Trade AI context reads raw `weekly_metrics`, `src/trade_history.py`.
- Viewer Team Lab builds ad hoc joins across Sleeper tables and `analytics_player_weekly_truth` from UI code, `src/viewer_team_context.py`.
- Pigskin chat previously exposed arbitrary BigQuery SQL execution through a model tool. This has since been resolved: the `get_bigquery_tool_declaration` and `execute_bigquery_sql` pair was removed from `app.py`, and `src/pigskin_context_tools.py` now registers only the parameterized declarations in `src/pigskin_context_tools.py`. See UI-006 in [ui-query-debt-register.md](ui-query-debt-register.md).

This violates the project context rule that UI and writing AI should read precomputed player, team, projection, ranking, and content evidence marts instead of raw source tables.

### Unversioned Projections

Present.

Pigskin rankings have `ranking_version`, but there is no full `model_run_id` table and no required run metadata package. Trade Lab projections are local app logic and are not versioned as model outputs.

### Missing Player ID Bridge

Partially present, but not canonical.

The repo uses Sleeper IDs, GSIS IDs, names, and team fallbacks. Examples include Sleeper schemas with `sleeper_player_id` in `src/ingest_sleeper_league.py:SLEEPER_TABLE_SCHEMAS`, Pigskin chat guidance to join viewer teams by `gsis_id` with fallback to name plus team in `src/pigskin_context_tools.py`, and Player Profiles joining depth charts on `gsis_id` in `src/player_profiles.py`.

There is no single canonical `player_identity_bridge` mart with source IDs, name aliases, active status, team history, confidence, and reconciliation timestamps.

### Missing Scoring Profile Abstraction

Present.

Most logic assumes PPR or hard-coded fantasy fields such as `fantasy_points_ppr`. No scoring profile table or config object was found for PPR, half-PPR, standard, TE premium, best ball bonuses, or custom league settings.

### App Memory or Streamlit State Used for Large Analytical Data

No large analytical data should be stored in app memory or ad hoc Streamlit state. Large analytical data belongs in BigQuery or Cloud Storage.

Current small admin state such as job metadata lives in BigQuery (`dashboard_job_runs`), which is acceptable under the Cloud Run operating model.

### No Model Run Tracking

Present.

There is no `model_runs` or `projection_runs` table. Current `ranking_version` does not store source freshness, feature config version, scoring profile, league type, roster format, and creation timestamp as a first-class run record.

### No Feature Marts

Partially present.

`analytics_player_weekly_truth`, `analytics_player_qb_splits`, `analytics_game_environment`, `analytics_fraud_watch`, and `analytics_pigskin_rankings_candidates` are feature-like marts. But there is not yet a stable feature-mart layer for:

- player season features
- player rolling features
- player role features
- team offensive environment
- offensive line and protection context
- coaching/play-calling context
- injury-adjusted opportunity
- weather and stadium conditions
- scoring-profile-specific fantasy outputs
- viewer-team roster evaluation
- projection inputs by run
- content evidence packets by segment

### No Backtesting

Present.

No backtesting module, historical holdout runner, prediction error table, calibration table, or leaderboard against market/consensus was found.

### No Claim Tracking

Present.

There is no durable claim ledger for Pigskin takes, rankings, show scripts, fraud labels, trade recommendations, or later grading. The existing `analytics_context_events` table is context input, not output claim tracking.

### Other Operational Gaps

- Monolithic Streamlit app: `app.py` handles UI, auth, jobs, SQL, AI prompts, data repair, and admin workflows.
- Inline schemas and migrations: BigQuery schema is spread across Python modules rather than migration files and data dictionaries.
- UI-triggered subprocess jobs: `src/job_runner.py` launches ingestion modules from the web process.
- Raw table awareness in Pigskin prompt: `src/pigskin_context_tools.py` includes `weekly_metrics` and `play_by_play`, increasing the risk of schema drift and expensive or invalid queries.
- Broad IAM direction in deploy docs: `deploy_guide.md:66-68` recommends BigQuery Admin for the Cloud Run service account, which is expedient but too broad for a mature setup.
- Validation is narrow: `validate.py` covers partitioning and dry-run costs, not semantic invariants for every transformation.

## 8. Recommended Migration Plan by Sprint

### Sprint 0: Freeze the Contract and Inventory the Warehouse

Goal: make the rebuild safe before moving code.

- Add a tracked data dictionary for every current BigQuery table.
- Add a generated warehouse inventory snapshot command or script that records table names, row counts, partitioning, clustering, and last modified time.
- Document which tables are raw/source, staging, marts, outputs, and admin metadata.
- Mark all UI queries as either acceptable mart reads or migration debt.
- Add a formal `docs/rebuild/` decision log.

Complexity: Small.

### Sprint 1: Add Model Run and Config Foundations

Goal: make every generated output defendable and reproducible.

- Add `model_runs` with `model_run_id`, run type, model name, prompt version, code version, source freshness, feature config version, scoring profile, league type, roster format, created timestamp, and status.
- Add `scoring_profiles`.
- Add `feature_config_versions`.
- Add `source_freshness_snapshots`.
- Update Pigskin ranking generation to create a `model_run_id` and write it to active and history tables.
- Keep `ranking_version` temporarily as a compatibility label.

Complexity: Medium.

### Sprint 2: Build the Canonical Player Identity Bridge

Goal: stop rankings and analysis from breaking on player name, team, or source-ID drift.

- Add `dim_players_current` and `player_identity_bridge`.
- Reconcile Sleeper ID, GSIS ID, ESPN ID if available, Sportradar-style IDs if added later, nflverse player IDs, normalized names, aliases, active status, current team, previous team, and confidence.
- Create validation queries for duplicate active identities, retired players in top rankings, conflicting current teams, and unresolved top-300 players.
- Migrate UI and marts to use canonical player IDs first, names only as display fields.

Complexity: Large.

### Sprint 3: Create Feature Marts

Goal: turn raw football data into stable analytical inputs.

- Create player-week, player-season, rolling-role, team-offense, QB-environment, receiver-usage, RB-usage, TE-usage, offensive-line, coaching/play-calling, injury-context, and game-environment marts.
- Include PPR, half-PPR, standard, and configurable scoring fields.
- Partition by season and cluster by canonical player ID, team, position, and week where useful.
- Add validation queries for every transformation.
- Make `analytics_player_weekly_truth` a downstream mart, not the only truth layer.

Complexity: XL.

### Sprint 4: Projection and Ranking Outputs

Goal: make Pigskin rankings and projections unified.

- Add output tables for weekly projections, rest-of-season rankings, redraft rankings, dynasty rankings, best ball rankings, trade values, and segment-specific boards.
- Require every output row to include `model_run_id`, scoring profile, league type, roster format, projection horizon, rank source, and confidence.
- Generate evidence packets alongside outputs so Pigskin chat defends the same rankings the UI shows.
- Move Pigskin chat to query output and evidence marts through safe backend APIs instead of arbitrary SQL.

Complexity: Large.

### Sprint 5: Admin and API Split

Goal: stop the Streamlit UI from being the data-access and job-orchestration layer.

- Introduce backend APIs for read-only marts, job kickoff, job status, and Pigskin chat context.
- Keep operational metadata in BigQuery admin tables unless a later migration introduces a dedicated metadata store.
- Move long-running jobs to Cloud Run Jobs triggered manually or by Cloud Scheduler.
- Keep Streamlit on Cloud Run, but make the UI a client of stable BigQuery marts or optional internal APIs.

Complexity: Large.

### Sprint 6: Backtesting, Calibration, and Claim Tracking

Goal: prove the system is better than the market and make show takes accountable.

- Add historical backtest tables by model run, position, scoring profile, and horizon.
- Compare against ADP, consensus rankings, sportsbook props, and prior Pigskin ranks when sources are available.
- Add a claim ledger for show takes, rankings, trade calls, fraud calls, and sleeper calls.
- Add grading jobs and dashboards for hit rate, calibration, regret, and model drift.

Complexity: Large.

### Sprint 7: Content Evidence Packets

Goal: make YouTube output fast, sourced, and consistent with the model.

- Create segment-specific evidence packet tables for Fraud Watch, Sleeper Watch, Trade Review, Viewer Team Audit, Rankings Debate, and Weekly Start/Sit.
- Each packet should include claim, evidence rows, counterargument, confidence, freshness, and recommended script framing.
- Pigskin script mode should read packet evidence rather than re-derive facts from raw tables.

Complexity: Medium.

## 9. Risk List and Estimated Implementation Complexity by Area

| Area | Risk | Complexity | Notes |
| --- | --- | --- | --- |
| Player identity bridge | High | Large | Incorrect player matching can corrupt every ranking, projection, and show claim. |
| Model run tracking | High | Medium | Without this, Pigskin cannot consistently defend rankings over time. |
| Scoring profiles | High | Medium | Rankings are not portable across league formats until this exists. |
| Feature marts | High | XL | This is the analytical core and should be implemented in small, validated slices. |
| Raw SQL in Pigskin chat | High | Medium | Current model-generated SQL can fail, scan raw data, or contradict canonical rankings. |
| UI direct BigQuery reads | Medium | Large | Works now, but it ties UX to warehouse schema and makes refactors risky. |
| Job orchestration from Streamlit | Medium | Medium | Long-running warehouse writes inside the app process are fragile on Cloud Run. |
| Inline migrations | Medium | Medium | Schema drift is already likely because DDL lives across multiple Python modules. |
| Cloud Run Jobs absence | Medium | Medium | Long-running jobs are still invoked from Streamlit instead of isolated job runtimes. |
| Backtesting absence | High | Large | The platform cannot prove it beats consensus without this. |
| Claim tracking absence | Medium | Medium | The show cannot grade or revisit Pigskin takes reliably. |
| IAM breadth | Medium | Small | BigQuery Admin is useful for bootstrap, but production runtime should be narrower. |
| Validation coverage | High | Medium | Partition validation exists, semantic validation does not. |

## Prioritized Backlog

1. P0: Add BigQuery data dictionary docs for every current table and classify each table as source, staging, mart, output, or admin metadata.
2. P0: Add `model_runs`, `scoring_profiles`, `feature_config_versions`, and `source_freshness_snapshots` schemas.
3. P0: Update Pigskin ranking generation to create and persist `model_run_id` while preserving existing `ranking_version` compatibility.
4. P0: Build `player_identity_bridge` and `dim_players_current`, then validate retired, duplicate, unresolved, and team-conflicted players.
5. P0: Replace Player Profiles and Pigskin ranking chat reads with canonical ranking and evidence marts.
6. P1: Create scoring-profile-aware player-week and player-season feature marts.
7. P1: Create team, QB, coaching, offensive-line, injury, stadium, and weather feature marts.
8. P1: Wire Viewer Team Lab to `compat_viewer_team_context` after live packet validation.
9. P1: Replace direct raw `weekly_metrics` reads in Show Prep and Trade Lab with feature marts.
10. P1: Add semantic validation queries for every mart and run them from Data Ops.
11. P1: Add backtest tables and first ranking/projection evaluation job.
12. P1: Add claim ledger tables for rankings, trade calls, show takes, fraud calls, and sleeper calls.
13. P2: Split job orchestration out of Streamlit into Cloud Run Jobs or scheduled workers.
14. P2: Add optional internal APIs on Cloud Run for stable mart reads if Streamlit query code remains too large.
15. P2: Reduce Cloud Run runtime IAM from broad BigQuery Admin to least-privilege roles after migrations stabilize.
16. P2: Build segment evidence packet outputs for Fraud Watch, Sleeper Watch, Viewer Team Audit, Trade Review, and Rankings Debate.
17. P2: After live validation, wire Sleeper Watch to `compat_sleeper_watch_candidates` behind a default-off flag and remove direct UI reads from raw Sleeper snapshots.
