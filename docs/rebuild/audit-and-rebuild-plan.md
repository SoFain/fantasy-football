# Audit and Rebuild Plan

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

Tracked repository files are currently a compact Python application and ETL stack:

```text
.
├── AGENTS.md
├── AI_VS_VIBES_ANALYTICS_PLAN.md
├── Dockerfile
├── Launch_Studio.bat
├── app.py
├── bootstrap.py
├── cloudbuild.yaml
├── data/
│   ├── context_events.csv
│   └── sample_rookie_scouting.csv
├── deploy_guide.md
├── requirements.txt
├── src/
│   ├── extract.py
│   ├── fetch_market_values.py
│   ├── generate_pigskin_rankings.py
│   ├── ingest_college_data.py
│   ├── ingest_context_events.py
│   ├── ingest_news.py
│   ├── ingest_sleeper_league.py
│   ├── load.py
│   ├── materialize.py
│   ├── pipeline.py
│   ├── setup_college_tables.py
│   ├── transform.py
│   └── verify_player_context.py
└── validate.py
```

Important local or generated items are present but are not part of the tracked app contract: `build/`, `dist/`, `venv/`, `__pycache__/`, `.codex-remote-attachments/`, `.codex-tools/`, `AI_vs_Vibes_Project_Resume_Report.md`, `partner_github_workflow_rules.md`, and the local service account JSON file.

The current runtime is Streamlit on Cloud Run. `Dockerfile:34` exposes port 8501 and `Dockerfile:37` starts `streamlit run app.py`. `requirements.txt:7` pins Streamlit as a dependency. `deploy_guide.md:91-107` documents Cloud Run deployment with BigQuery, Secret Manager, Gemini, and Vertex AI Search environment settings.

No Firebase implementation exists in the tracked repository. That is now an explicit platform decision, not a gap to fill.

## 2. Existing Cloud Runtime, Admin Routes, UI Pages, Scheduled Jobs, and Data-Access Patterns

### Cloud Runtime

The current runtime is a single Streamlit service on Cloud Run. No Cloud Run Jobs or Cloud Scheduler triggers are currently defined in the tracked repository.

### Admin and UI Routes

There are no web routes in a conventional Flask/FastAPI/Next sense. The admin panel is a single Streamlit app in [app.py](../../app.py).

Current authentication is a basic Streamlit session gate using `DASHBOARD_USERNAME` and `DASHBOARD_PASSWORD` in `app.py:28-29`.

Current top-level tabs are defined in `app.py:3319`:

- Pigskin Studio
- Show Prep
- Player Profiles
- Versus Finder
- Viewer Team Lab
- Trade Lab
- Data Ops

Notable UI sections and functions:

- Runtime status: `app.py:444-457`, `app.py:562-627`, and `app.py:632`.
- Fraud Watch segment: `app.py:733`.
- Sleeper Watch segment: `app.py:788`.
- Player Profiles: `app.py:1475`.
- Versus Finder: `app.py:2071`.
- Reddit topic scout: `app.py:2458`.
- Pigskin chat/cohost: `app.py:2506`.
- Trade and value analyzer: `app.py:2860`.
- Sleeper viewer team context and console: `app.py:3390`, `app.py:3618`, and `app.py:3679`.
- Data Ops admin controls: `app.py:3743-4025`.

### Scheduled Jobs

No scheduled job definitions were found in the repo. There is no Cloud Scheduler config, GitHub Actions schedule, cron file, or equivalent scheduled worker.

Current ingestion and admin jobs are manually triggered from Streamlit Data Ops or run as CLI modules. `app.py:3358` runs subprocesses from the UI, and Data Ops invokes modules such as `src.ingest_news`, `src.ingest_context_events`, `src.fetch_market_values`, `src.verify_player_context`, `src.ingest_college_data`, `src.pipeline`, and `src.generate_pigskin_rankings` in `app.py:3767-3941`.

### Data-Access Patterns

BigQuery is accessed directly from `app.py` through a cached query helper at `app.py:656`. Pigskin previously exposed a model tool named `execute_bigquery_sql`; the chat path now uses named context tools in `src/pigskin_context_tools.py`.

The app includes defensive SQL repair logic around `app.py:666-697`, including repairs for `analytics_player_weekly_truth`, `weekly_metrics`, NGS tables, and `market_values`. That repair layer helps with bad model SQL, but it also confirms the UI and writing AI are currently too close to raw warehouse schema details.

Warehouse metrics are read by listing BigQuery tables and summing table bytes in `app.py:444-457`.

Job-success metadata is stored in BigQuery table `dashboard_job_runs` from `app.py:562-627`. This is consistent with the current decision to store operational metadata in BigQuery admin tables unless a later migration introduces a dedicated metadata store.

## 3. Existing BigQuery Datasets, Tables, Queries, and Migrations Found

Default dataset name is `fantasy_football_brain`. The BigQuery project is intended to be `fantasy-football-498121`, and `src/load.py:54-101` loads DataFrames to partitioned tables using range partitioning on `season`.

### Raw and Source-Like Tables

The main NFL pipeline is `src/pipeline.py:29`. It extracts, transforms, loads, then calls `materialize_all` in `src/pipeline.py:191`.

Tables loaded by the main pipeline include:

- `play_by_play`, `src/pipeline.py:128`.
- `weekly_metrics`, `src/pipeline.py:137`.
- `team_descriptions`, `src/pipeline.py:146`.
- `draft_picks`, `src/pipeline.py:155`.
- `player_rosters`, `src/pipeline.py:164`.
- `player_contracts`, `src/pipeline.py:173`.
- `ngs_passing`, `ngs_rushing`, `ngs_receiving`, `ftn_charting`, `weekly_snap_counts`, `injury_reports`, and `depth_charts`, `src/pipeline.py:178-188`.

### Analytics and Evidence Marts

`src/materialize.py` creates current analytics marts:

- `analytics_game_environment`, `src/materialize.py:16`.
- `analytics_player_weekly_truth`, `src/materialize.py:274`.
- `analytics_fraud_watch`, `src/materialize.py:591`.
- `analytics_pigskin_rankings_candidates`, `src/materialize.py:703`.
- `analytics_pigskin_rankings_history`, `src/materialize.py:1146`.
- `analytics_player_qb_weekly`, `src/materialize.py:1249`.
- `analytics_player_qb_splits`, `src/materialize.py:1350`.

`src/generate_pigskin_rankings.py` reads candidates from `analytics_pigskin_rankings_candidates` at `src/generate_pigskin_rankings.py:49`, then writes:

- `analytics_pigskin_rankings`, `src/generate_pigskin_rankings.py:325-331`.
- `analytics_pigskin_rankings_history`, `src/generate_pigskin_rankings.py:326-339`.

### External Context, News, and Market Tables

- `analytics_api_usage_daily`, `src/verify_player_context.py:53`.
- `analytics_external_context_search_results`, `src/verify_player_context.py:63` and `src/verify_player_context.py:283-287`.
- `sleeper_players_current`, `src/ingest_news.py:139-161`.
- `realtime_player_news`, `src/ingest_news.py:179-185`.
- `market_values`, `src/fetch_market_values.py:11` and `src/fetch_market_values.py:97`.
- `analytics_context_events`, `src/ingest_context_events.py:62-69`.
- `college_player_stats`, `src/setup_college_tables.py:14-15` and `src/ingest_college_data.py:13`.
- `rookie_scouting_metrics`, `src/setup_college_tables.py:32-33`, with UI CSV loading in `app.py:4018-4025`.

### Sleeper League Tables

`src/ingest_sleeper_league.py:17-62` defines schemas for:

- `sleeper_leagues`
- `sleeper_league_users`
- `sleeper_rosters`
- `sleeper_roster_players`
- `sleeper_matchups`
- `sleeper_lineups`
- `sleeper_available_players`
- `sleeper_viewer_team_snapshots`

Rows are assembled into those tables in `src/ingest_sleeper_league.py:312-319` and appended to BigQuery in `src/ingest_sleeper_league.py:331-340`.

### Migrations and Schema Governance

No conventional migration directory was found. There are inline `CREATE TABLE`, `CREATE OR REPLACE TABLE`, `MERGE`, and load-job schemas inside Python modules. This is workable for the prototype, but it is not enough for the source-of-truth requirements in `docs/CODEX_PROJECT_CONTEXT.md:24-29`, especially versioned runs, repeatability, validation, and data dictionaries.

`validate.py` provides partition and dry-run validation utilities at `validate.py:17-27` and `validate.py:57-151`, but it does not validate every transformation or all analytics mart invariants.

## 4. Current Data Ingestion Paths for nflverse and Sleeper

### nflverse and nflreadpy

`src/extract.py:7` imports `nflreadpy as nfl`. Current extractors cover:

- Play-by-play, `src/extract.py:83-88`.
- Weekly player stats, `src/extract.py:118-126`.
- Teams, draft picks, players, and contracts, `src/extract.py:154-190`.
- NGS passing, rushing, and receiving, `src/extract.py:207-241`.
- FTN charting, `src/extract.py:258-260`.
- Snap counts, `src/extract.py:275-277`.
- Injuries, `src/extract.py:292-294`.
- Depth charts, `src/extract.py:309-313`.

The end-to-end pipeline is `src/pipeline.py:29`, with extracts imported at `src/pipeline.py:6`, transforms imported at `src/pipeline.py:7`, and materialization imported at `src/pipeline.py:9`.

### Sleeper API

Sleeper global player and trending data is loaded by `src/ingest_news.py`.

- The Sleeper throttle is set to `SLEEPER_MAX_CALLS_PER_MINUTE = 900` in `src/ingest_news.py:14`.
- Sleeper API calls use `sleeper_get` in `src/ingest_news.py:18-34`.
- Global player map is fetched from `/players/nfl` at `src/ingest_news.py:41`.
- Trending adds and drops are fetched at `src/ingest_news.py:46-47`.
- Current player metadata is written to `sleeper_players_current` at `src/ingest_news.py:139-161`.
- Trending records are written to `realtime_player_news` at `src/ingest_news.py:179-185`.

Sleeper league and viewer-team snapshots are loaded by `src/ingest_sleeper_league.py`.

- The base URL is defined at `src/ingest_sleeper_league.py:15`.
- API calls reuse `sleeper_get` at `src/ingest_sleeper_league.py:9` and `src/ingest_sleeper_league.py:72`.
- The CLI entrypoint is defined at `src/ingest_sleeper_league.py:378-388`.
- The Streamlit Viewer Team Lab calls this module in `app.py:3679-3728`.

### Other Adapters

- FantasyCalc market values: `src/fetch_market_values.py:11-23`, loaded via `insert_rows_json` at `src/fetch_market_values.py:97`.
- CFBD college stats: `src/ingest_college_data.py:13-32`, loaded at `src/ingest_college_data.py:172`.
- User or manually curated context events: `src/ingest_context_events.py:62-69`.
- External verification through Vertex AI Search: `src/verify_player_context.py:146-251`, with daily usage limits enforced in `src/verify_player_context.py:293-316`.

## 5. Current Projection and Ranking Logic

### Pigskin Rankings

The ranking flow is now partially LLM-authored:

1. `src/materialize.py:703` creates `analytics_pigskin_rankings_candidates`.
2. `src/generate_pigskin_rankings.py:49` fetches candidates.
3. `src/generate_pigskin_rankings.py:129-178` builds the Pigskin prompt.
4. The prompt explicitly says the SQL rank is evidence, not the final ranking, and tells the model to adjudicate using opportunity quality, split EPA, WOPR history, target-share history, carry-share history, role quality, role fragility, current Sleeper team, current Sleeper depth chart, and sustainability.
5. `src/generate_pigskin_rankings.py:199-212` calls Gemini with `google-genai`.
6. `src/generate_pigskin_rankings.py:227-254` validates the model output against the candidate set and fails if candidates are missing, duplicated, or unknown.
7. `src/generate_pigskin_rankings.py:325-339` writes active and history tables.

This is directionally correct for the Pigskin identity. The major gap is that the version key is `ranking_version`, generated in `src/generate_pigskin_rankings.py:368`, not a full `model_run_id` with source freshness, feature config version, scoring profile, league type, roster format, and creation timestamp.

### Player Profiles

Player Profiles read several warehouse tables directly, including:

- `player_rosters`, `app.py:1095` and `app.py:1116`.
- `analytics_player_weekly_truth`, `app.py:1124`, `app.py:1153`, `app.py:1359`, and `app.py:1381`.
- `player_contracts`, `app.py:1165`.
- `depth_charts`, `app.py:1180`.
- `college_player_stats`, `app.py:1198`.
- `rookie_scouting_metrics`, `app.py:1213`.
- `analytics_pigskin_rankings`, `app.py:1325`.

The UI caption says canonical Pigskin rankings are loaded from `analytics_pigskin_rankings` in `app.py:1552`.

### Pigskin Chat

Pigskin chat has a detailed schema and behavioral prompt in `app.py:2579-2733`. It instructs the model to query `analytics_pigskin_rankings` first for ranking questions, to use `analytics_pigskin_rankings_history` for older ranking calls, and to prefer `analytics_player_weekly_truth` for non-ranking player analysis.

The model no longer receives a general SQL execution tool. It now calls fixed context tools backed by curated marts and compatibility objects. The remaining risk is incomplete mart coverage, not arbitrary model-written SQL.

### Trade Lab

Trade Lab still has legacy direct `market_values` reads in `app.py:2761-2769` and runs local value/projection logic in the Streamlit app. `compat_trade_assets_current` now provides a production mart/view/helper path for future default-off wiring. Its AI outlook still has separate query debt around weekly history and external leads.

There is no model-runed projection system for trade values, rest-of-season rankings, dynasty rankings, best ball rankings, or weekly projections yet.

## 6. Current Admin Panel Capabilities

The Streamlit admin panel currently supports:

- Basic login through environment variables, `app.py:28-29`.
- Warehouse status cards based on `client.list_tables` and `table.num_bytes`, `app.py:444-457`.
- Last successful run display using `dashboard_job_runs`, `app.py:562-627`.
- Validation sweep, `app.py:3767-3776`, running `validate.py`.
- Realtime Sleeper/news ingest, `app.py:3786-3795`, running `src.ingest_news`.
- Context event ledger ingest, `app.py:3799-3808`, running `src.ingest_context_events`.
- FantasyCalc market values ingest, `app.py:3810-3824`, running `src.fetch_market_values`.
- External player context verification, `app.py:3828-3862`, running `src.verify_player_context`.
- CFBD college stats ingest, `app.py:3864-3884`, running `src.ingest_college_data`.
- Main NFL statistics ingestion, `app.py:3893-3926`, running `src.pipeline`.
- Pigskin ranking generation, `app.py:3930-3941`, running `src.generate_pigskin_rankings`.
- Rookie scouting CSV upload to BigQuery, `app.py:3945-4025`.
- Viewer team load and console from Sleeper, `app.py:3679-3740`.
- Show Prep with Fraud Watch, Sleeper Watch, and Reddit topic scout, `app.py:4033-4059`.

This is useful for an early operating console, but it combines UI, job orchestration, warehouse mutation, BigQuery querying, and LLM workflows in one large file.

## 7. Current Anti-Patterns and Gaps

### Raw BigQuery Scans From UI/Admin

Present.

Examples:

- Sleeper Watch uses raw `weekly_metrics` in the UI query, `app.py:814`.
  - Rebuild status: `compat_sleeper_watch_candidates` now has a production backing mart, view, materializer, helper, and validations. `app.py` is intentionally not wired yet and should use `USE_COMPAT_SLEEPER_WATCH=false` when wiring begins.
- Player Profiles read source-like `player_rosters`, `player_contracts`, `depth_charts`, `college_player_stats`, and `rookie_scouting_metrics` directly, `app.py:1095-1213`.
- Trade AI context reads raw `weekly_metrics`, `app.py:3150`.
- Viewer Team Lab builds ad hoc joins across Sleeper tables and `analytics_player_weekly_truth` from UI code, `app.py:3420-3549`.
- Pigskin chat exposes arbitrary BigQuery SQL execution through a model tool, `app.py:508` and `app.py:2782-2796`.

This violates the project context rule that UI and writing AI should read precomputed player, team, projection, ranking, and content evidence marts instead of raw source tables.

### Unversioned Projections

Present.

Pigskin rankings have `ranking_version`, but there is no full `model_run_id` table and no required run metadata package. Trade Lab projections are local app logic and are not versioned as model outputs.

### Missing Player ID Bridge

Partially present, but not canonical.

The repo uses Sleeper IDs, GSIS IDs, names, and team fallbacks. Examples include Sleeper schemas with `sleeper_player_id` in `src/ingest_sleeper_league.py:37-58`, Pigskin chat guidance to join viewer teams by `gsis_id` with fallback to name plus team in `app.py:2710`, and Player Profiles joining depth charts on `gsis_id` in `app.py:1270`.

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
- UI-triggered subprocess jobs: `app.py:3358` launches ingestion modules from the web process.
- Raw table awareness in Pigskin prompt: `app.py:2606-2630` includes `weekly_metrics` and `play_by_play`, increasing the risk of schema drift and expensive or invalid queries.
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
