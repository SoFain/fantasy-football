# Current season stats refresh

Run `venv\Scripts\python.exe scripts\refresh_current_season_stats.py --season 2026` to inspect the current nflverse source and warehouse schema without writing. Add `--apply` to refresh the requested season in `weekly_metrics`.

The refresh uses the existing weekly stats schema, preserves upstream team rows with null player IDs, and reports extra source columns excluded from that schema. It stages a complete season snapshot, refuses to remove any existing player/week/team key, and replaces only that season inside a transaction. Historical seasons and all ranking tables remain untouched. Temporary tables expire after two hours and are deleted after each run.

Coverage is per week, with game and team counts. Completed schedule games absent from the stats source appear in `completed_games_awaiting_source_stats`. Partial current-week source coverage can be loaded, but must remain visible in reports; it is not evidence of complete week coverage. Re-running picks up delayed games and stat corrections without appending duplicates.

Current-season evidence belongs in a separate public `current_season` context block. Keep preseason formula metrics and their season attribution intact. Loading these stats does not approve or implement an in-season ranking formula.

The publisher queries the refreshed warehouse stats for every profile and adds schema 1.4 `current_season` blocks. These contain `season`, the player's observed `through_week` and `games`, aggregate `stats`, `source`, and `coverage_caveat`. Players without observed rows receive null coverage and empty stats, never invented zero production. Completed games missing from source are named in every block. Publication fails if current stats cannot be loaded. Original `metrics` and `situation.metric_basis` remain the preseason inputs.
