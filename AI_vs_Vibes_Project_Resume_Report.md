# AI vs Vibes Fantasy Football Analytics Platform

## Project Summary

Built and deployed a cloud-hosted fantasy football analytics platform for the AI vs Vibes YouTube show concept. The product combines NFL data ingestion, BigQuery warehousing, Streamlit dashboard workflows, Gemini-powered analysis, Sleeper league analysis, player profile scouting tools, and show segment preparation features.

The core goal was to create a data-first fantasy football analysis engine that separates real role quality from box-score noise, challenges weak fantasy narratives, and produces show-ready analysis with a distinctive AI co-host voice.

## Resume Positioning

**Founder and Lead Developer, AI vs Vibes Fantasy Football Analytics Platform**
Designed, built, and deployed an end-to-end fantasy football analytics application using Python, Streamlit, Google Cloud Run, BigQuery, Gemini, Sleeper APIs, and automated data pipelines.

## Key Accomplishments

- Built a production Streamlit dashboard deployed on Google Cloud Run with version metadata, Cloud Run revision visibility, BigQuery warehouse status, and production Secret Manager integration.
- Designed and implemented an NFL data ingestion pipeline using `nflreadpy`, pandas, and BigQuery to load play-by-play, weekly player metrics, rosters, contracts, draft data, NGS data, FTN charting, snap counts, injury reports, depth charts, and other fantasy-relevant datasets.
- Created derived analytics tables including `analytics_player_weekly_truth`, `analytics_fraud_watch`, `analytics_player_qb_weekly`, `analytics_player_qb_splits`, `analytics_game_environment`, and context-event tables for more rigorous player analysis.
- Developed Pigskin, a Gemini-powered AI fantasy football co-host with strict system instructions, BigQuery tool calling, error-safe query handling, script mode, and a custom analytical voice.
- Migrated the AI layer from the deprecated `google-generativeai` package to the modern `google-genai` SDK, including manual function-calling support for BigQuery queries.
- Built a Fraud Watch segment that ranks weekly fantasy point spikes against underlying role quality, target share, snap trust, touchdown dependence, and usage stability.
- Built a Sleeper Viewer Team Analysis workflow that loads public Sleeper league and roster snapshots into BigQuery and enables AI-driven roster audits for viewer teams.
- Added a terminal-style Team Review Console for show-ready Sleeper roster analysis with waiver context, starter checks, bench surplus analysis, and Pigskin-style commentary.
- Built Sleeper Watch Search to identify under-rostered sleepers and streamers using roster percentage, recent volume, WOPR, snap share, EPA, carry and target volume, and matchup defensive context.
- Added Reddit Topic Scout to scan fantasy football Reddit RSS feeds and surface popular weekly discussion topics for show planning.
- Built Player Profiles, a searchable player directory with physical profile data, contracts, draft history, depth chart context, season history, weekly logs, advanced scouting metrics, run/pass opportunity splits, AI scouting reports, and position rankings.
- Built a Versus Finder and player comparison workflow for side-by-side statistical player comparisons with Gemini-generated synthesis.
- Added a Trade and Value Analyzer that uses FantasyCalc market values, age curves, positional projections, and AI analysis to compare player and pick packages across multi-year windows.
- Integrated real-time and external context workflows, including Sleeper add/drop trends, Vertex AI Search-backed external verification, CollegeFootballData imports, rookie scouting CSV uploads, and context event ledgers.
- Implemented data quality safeguards in the AI workflow so Pigskin stops and reports failed BigQuery queries instead of generating fake data-backed answers.
- Added SQL repair logic and schema guidance to prevent repeated model-generated query failures, including fixes for missing `epa_per_play` and incorrect NGS player name columns.
- Added responsive dashboard navigation, tab bookmarks, grouped data operations, runtime status cards, logo hosting via external web server assets, and a branded footer link.
- Established a GitHub collaboration workflow with feature branches, pull requests, conflict repair, admin merge bypass when appropriate, and repeated Cloud Run deployment cycles.

## Technical Stack

- **Frontend and App Framework:** Streamlit, Python, pandas, Altair
- **Cloud Platform:** Google Cloud Run, Google Cloud Build, Artifact Registry, Secret Manager
- **Data Warehouse:** Google BigQuery
- **AI and LLM:** Google Gemini, `google-genai`, manual function calling, system prompting
- **Data Sources:** nflreadpy, Sleeper API, FantasyCalc API, Reddit RSS, CollegeFootballData, uploaded scouting CSVs, Vertex AI Search context
- **DevOps and Collaboration:** GitHub, GitHub CLI, pull requests, branch protection workflows, Cloud Run deployments
- **Data Engineering:** partitioned BigQuery tables, derived analytical tables, materialized SQL models, schema-aware query repair

## Major Product Areas Built

### 1. NFL Data Warehouse

Created a BigQuery-backed football warehouse with historical and current-season NFL data. The pipeline supports ingestion and transformation for:

- Play-by-play data
- Weekly player statistics
- Player rosters
- Player contracts
- Team metadata
- Draft picks
- NGS passing, rushing, and receiving
- FTN charting
- Snap counts
- Injury reports
- Depth charts
- College and rookie scouting imports
- Sleeper roster and lineup snapshots
- Market value data
- External context and event ledgers

### 2. Analytical Truth Tables

Built derived analytical layers to make the AI more trustworthy than a standard fantasy chatbot. These tables support role-based reasoning instead of simple box-score summaries:

- `analytics_player_weekly_truth`
- `analytics_fraud_watch`
- `analytics_player_qb_weekly`
- `analytics_player_qb_splits`
- `analytics_game_environment`
- `analytics_context_events`
- `analytics_external_context_search_results`

These tables help the model reason about role quality, opportunity, quarterback context, weather and stadium conditions, team changes, injury context, roster status, and whether fantasy production was supported by usage.

### 3. Pigskin AI Co-host

Developed Pigskin as a custom AI persona for fantasy football show analysis. Pigskin is configured to:

- Query BigQuery before making analytical claims.
- Prioritize `analytics_player_weekly_truth`.
- Separate historical team stats from current roster team.
- Use QB split tables before blaming a receiver.
- Check contextual event tables before making causal claims about injuries, coaching, or play calling.
- Report query failures instead of hallucinating.
- Produce script-mode output with voice-only performance cues for TTS and voice actor use.
- Deliver analysis in a ruthless, skeptical, show-ready style.

### 4. Show Prep and Segment Tools

Built show segment tooling to turn the analytics platform into actual YouTube production workflows:

- **Fraud Watch:** identifies players whose fantasy production outran role quality.
- **Sleeper Watch Search:** ranks under-rostered players and potential streamers.
- **Reddit Topic Scout:** finds popular fantasy football discussion topics for episode planning.
- **Player Profiles:** builds player scouting pages with analytics, contract data, depth chart status, scouting metrics, and AI reports.
- **Versus Finder:** compares players head-to-head with data and AI synthesis.

### 5. Viewer Team Analysis

Created a workflow for analyzing viewer Sleeper teams:

- Loads public Sleeper league and roster snapshots.
- Resolves viewer teams by league ID, roster ID, username, team name, or display name.
- Stores roster, lineup, matchup, and available player context in BigQuery.
- Provides terminal-style AI roster audits.
- Supports show-ready critique of starters, bench construction, tradeable surplus, waiver needs, and fragile roster builds.

### 6. Trade and Market Value Analysis

Built a trade analyzer using FantasyCalc market values and projection logic:

- Supports multi-asset trade comparison.
- Compares current value and projected future value.
- Includes age and positional longevity adjustments.
- Uses AI synthesis for multi-year outlooks.
- Supports player and draft pick packages.

### 7. Cloud Deployment and Operations

Set up and maintained production deployment workflows:

- Container builds through Google Cloud Build.
- Image publishing to Artifact Registry.
- Cloud Run deployment with environment variables and Secret Manager.
- Runtime version metadata surfaced in the UI.
- BigQuery warehouse status surfaced in dashboard runtime cards.
- Public dashboard URL smoke checks after deployment.
- GitHub pull request based collaboration with partner branches.

## Selected Engineering Challenges Solved

- Fixed incorrect BigQuery project configuration by pinning `BQ_PROJECT=fantasy-football-498121`.
- Added public Cloud Run access after locked-out deployment states.
- Hardened Gemini API handling with Secret Manager and model configuration checks.
- Migrated from deprecated Gemini SDK to `google-genai`.
- Prevented model hallucinations by stopping responses when BigQuery queries fail.
- Repaired model-generated SQL for known schema mistakes.
- Resolved multiple PR merge conflicts while preserving existing dashboard and Pigskin work.
- Hosted responsive logo assets externally and linked them from Cloud Run.
- Filtered invalid player names to fix Player Profiles sorting errors.
- Added 2026/2027 season support and active-roster profile logic.
- Added depth chart ingestion and player run/pass opportunity splits.

## Resume Bullet Options

- Architected and deployed a Google Cloud Run fantasy football analytics dashboard using Python, Streamlit, BigQuery, Gemini, and automated NFL data ingestion pipelines.
- Built BigQuery analytical models that transform raw NFL play-by-play and player metrics into role-quality, opportunity, efficiency, QB-context, and fraud-detection tables.
- Developed a Gemini-powered AI co-host with manual BigQuery function calling, strict system instructions, query failure safeguards, and show-ready script generation.
- Integrated Sleeper league data to support viewer team analysis, roster audits, waiver context, and fantasy football show segments.
- Designed production workflows for fantasy content creation, including Fraud Watch, Sleeper Watch, Player Profiles, Reddit Topic Scout, Versus Finder, and Trade Analyzer modules.
- Migrated an AI application from deprecated `google-generativeai` to `google-genai`, preserving manual tool-calling behavior and production Cloud Run deployment.
- Implemented GitHub PR-based collaboration, conflict resolution, Cloud Build image pipelines, Secret Manager configuration, and repeatable Cloud Run deployments.

## Current Production State

- **Production app:** `https://nfl-studio-dashboard-583607027760.us-central1.run.app`
- **Cloud Run service:** `nfl-studio-dashboard`
- **BigQuery project:** `fantasy-football-498121`
- **Primary dataset:** `fantasy_football_brain`
- **Current AI SDK:** `google-genai`
- **Primary Gemini model env var:** `GEMINI_MODEL=gemini-3.5-flash`

## Best Short Resume Version

**AI vs Vibes Fantasy Football Analytics Platform**
Built and deployed a Google Cloud Run fantasy football analytics platform using Python, Streamlit, BigQuery, Gemini, and automated NFL data pipelines. Developed custom BigQuery truth tables for player role quality, fraud detection, QB splits, roster context, weather and game environment, and viewer Sleeper team analysis. Integrated Gemini with manual BigQuery tool calling to power a show-ready AI co-host that produces data-backed fantasy analysis, trade evaluations, player profiles, sleeper searches, and weekly show segment ideas.
