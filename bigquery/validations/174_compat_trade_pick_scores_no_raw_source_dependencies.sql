-- Validation helper. Render placeholders before running manually.
-- Expected result: raw_source_dependency_count = 0

SELECT COUNT(*) AS raw_source_dependency_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.VIEWS`
WHERE table_name IN (
        'trade_pick_scores_current',
        'compat_trade_pick_scores_current'
    )
    AND REGEXP_CONTAINS(
        LOWER(view_definition),
        r'\b(from|join)\s+`?[^`\s]*(draft_picks|college_player_stats|rookie_scouting_metrics|source_[a-z0-9_]*|raw_[a-z0-9_]*)`?'
    );
