-- Validation helper. Render placeholders before running manually.
-- Expected result: raw_source_dependency_count = 0

SELECT COUNT(*) AS raw_source_dependency_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.VIEWS`
WHERE table_name IN (
        'content_brief_runs',
        'content_briefs',
        'content_brief_items'
    )
    AND REGEXP_CONTAINS(
        LOWER(view_definition),
        r'\b(weekly_metrics|play_by_play|ngs_passing|ngs_rushing|ngs_receiving|ftn_charting|weekly_snap_counts|injury_reports|player_rosters|player_contracts|depth_charts|market_values|sleeper_viewer_team_snapshots|sleeper_roster_players|sleeper_lineups|sleeper_available_players)\b'
    );
