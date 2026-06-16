-- Validation helper. Render placeholders before running manually.
-- Expected result: zero rows.

SELECT
    'llm_player_context_packet_grain' AS validation_name,
    COALESCE(player_id_internal, source_player_key) AS player_key,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    model_run_id,
    as_of_season,
    as_of_week,
    COUNT(*) AS row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.llm_player_context_packet`
GROUP BY player_key, scoring_profile_id, league_type_id, roster_format_id, model_run_id, as_of_season, as_of_week
HAVING COUNT(*) > 1;
