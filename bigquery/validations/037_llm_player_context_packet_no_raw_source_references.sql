-- Validation helper. Render placeholders before running manually.
-- Expected result: raw_source_reference_count = 0.

SELECT
    'llm_player_context_packet_no_raw_source_references' AS validation_name,
    COUNTIF(REGEXP_CONTAINS(
        LOWER(view_definition),
        r'\b(weekly_metrics|play_by_play|player_rosters|player_contracts|depth_charts|team_descriptions|ngs_passing|ngs_rushing|ngs_receiving|ftn_charting|weekly_snap_counts|injury_reports)\b'
    )) AS raw_source_reference_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.VIEWS`
WHERE table_name = 'llm_player_context_packet';
