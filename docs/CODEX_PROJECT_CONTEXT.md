You are working on the AI vs. Meatbags fantasy football intelligence platform.

Project goal:
Build a cost-conscious, data-backed fantasy football projection/ranking system that supports weekly projections, rest-of-season rankings, dynasty rankings, best ball rankings, trade reviews, fraud watch, sleeper breakouts, team reviews, and content evidence packets for a YouTube writing AI.

Current and target stack:
- Cloud Run is the runtime platform.
- The current UI/admin app is Streamlit on Cloud Run.
- BigQuery is the analytical warehouse and source of truth for historical/statistical data, feature marts, projections, rankings, backtests, claim tracking, and evidence packets.
- Cloud Run Jobs should be used for ingestion, materialization, ranking generation, evidence packet generation, backtests, and other long-running or scheduled jobs.
- Cloud Scheduler may trigger Cloud Run Jobs.
- Cloud Storage may store large artifacts, exports, logs, and packet archives when BigQuery is not the right storage layer.
- Secret Manager stores API keys and secrets.
- Firebase is not part of the current target architecture.

Hard architectural rules:
1. Do not query raw play-by-play or raw source tables directly from the user-facing UI or the writing AI.
2. Precompute player, team, projection, ranking, and content evidence marts in BigQuery.
3. Store large analytical data in BigQuery or Cloud Storage, not Streamlit state or local files.
4. Every projection/ranking output must be versioned by model_run_id.
5. Every model run must store source freshness, feature config version, scoring profile, league type, roster format, and creation timestamp.
6. All ETL/materialization jobs must be idempotent.
7. All BigQuery tables should be partitioned and clustered where appropriate.
8. Streamlit admin views should read from precomputed marts or backend helper functions, not ad hoc raw-table scans.
9. Long-running jobs should move out of the Streamlit request process and into Cloud Run Jobs.
10. Add tests or validation queries for every transformation.
11. Prefer small, reviewable pull requests.
12. Do not remove existing behavior unless the task explicitly asks for a migration/removal plan.