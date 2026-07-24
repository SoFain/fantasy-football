You are working on the Pigskin fantasy football intelligence platform.

Project goal:
Build a cost-conscious, data-backed fantasy football projection/ranking system that supports weekly projections, rest-of-season rankings, dynasty rankings, best ball rankings, trade reviews, fraud watch, sleeper breakouts, team reviews, and content evidence packets for a YouTube writing AI.

Current and target stack:
- Cloud Run Jobs are the runtime platform. There is no long-running service and no UI.
- The Streamlit admin app was retired. `src/job_runner.py` is the single entrypoint; every capability is a named job invoked from the CLI or a Cloud Run Job execution.
- BigQuery is the analytical warehouse and source of truth for historical/statistical data, feature marts, projections, rankings, backtests, claim tracking, and evidence packets.
- Cloud Run Jobs should be used for ingestion, materialization, ranking generation, evidence packet generation, backtests, and other long-running or scheduled jobs.
- Cloud Scheduler may trigger Cloud Run Jobs.
- Cloud Storage may store large artifacts, exports, logs, and packet archives when BigQuery is not the right storage layer.
- Secret Manager stores API keys and secrets.
- Firebase is not part of the current target architecture.

Hard architectural rules:
1. Do not query raw play-by-play or raw source tables directly from the writing AI or any future consumer surface.
2. Precompute player, team, projection, ranking, and content evidence marts in BigQuery.
3. Store large analytical data in BigQuery or Cloud Storage, not local files.
4. Every projection/ranking output must be versioned by model_run_id.
5. Every model run must store source freshness, feature config version, scoring profile, league type, roster format, and creation timestamp.
6. All ETL/materialization jobs must be idempotent.
7. All BigQuery tables should be partitioned and clustered where appropriate.
8. Consumers read precomputed marts, compatibility objects, or backend helper functions in `src/`, never ad hoc raw-table scans.
9. Every capability is a named job in `src/job_runner.py`. Do not add a web service or UI without an explicit platform decision.
10. Add tests or validation queries for every transformation.
11. Prefer small, reviewable pull requests.
12. Do not remove existing behavior unless the task explicitly asks for a migration/removal plan.
13. Only Sleeper-active players may appear in rankings. A player without an `active` tag in the Sleeper snapshot is never rankable. The Sleeper players endpoint is fetched with `?active=true`, so non-active players are absent from `sleeper_players_current` entirely, and the ranking candidate mart additionally filters `active IS TRUE`. Enforced by validations 148-150.
14. Rankings run once per day, and the daily Sleeper pull runs first. The snapshot defines the eligible pool, so `generate-pigskin-rankings` refuses to run without a current-day `sleeper_players_current` snapshot.
15. Current depth chart position comes from Sleeper. nflreadpy `depth_charts` is a historical seasonal archive, not a current source; do not treat it as current depth. Rankings already use `sleeper_depth_chart_position` / `sleeper_depth_chart_order`.

Sleeper API discipline:

- `/v1/players/` is ~5MB and rate-limited by Sleeper to once per day. `src/ingest_news.py` is its only caller; it fetches with `?active=true` and skips if today's snapshot already exists. Every other job reads the saved `sleeper_players_current` snapshot, never the endpoint.
- All other Sleeper endpoints (trending, league, rosters, matchups) have no such limit and may be called live.
- Always honor the published Sleeper API rules at https://docs.sleeper.com/.

Documentation rules:

1. Cite code by symbol, never by line number. Line numbers rot silently and the docs have already drifted once this way.

```text
`src/job_runner.py:dispatch_run_projections`   cite the symbol
`src/job_runner.py:211`                        never cite the line
```

2. Run `python scripts/check_doc_refs.py` after changing docs or renaming a cited symbol. It fails if a citation no longer resolves.
3. Index new documents in [README.md](README.md).
4. Validation reports under `docs/rebuild/validation/` are point-in-time records. Do not edit them after the fact; write a new report instead.

Naming:

- "Pigskin" is the platform and the on-air co-host persona.
- "meatbag" is domain vocabulary for a human analyst. Keep it where it means the human's claim, such as the Meatbag Claim Ledger, the `meatbag_accountability_show` brief type, and the `meatbag_delta` columns. Do not rename those to Pigskin; it would invert the meaning.