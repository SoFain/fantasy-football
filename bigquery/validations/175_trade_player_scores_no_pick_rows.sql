-- Validation helper. Render placeholders before running manually.
-- Expected result: pick_player_score_rows = 0

SELECT COUNT(*) AS pick_player_score_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_player_scores`
WHERE UPPER(position) = 'PICK'
    OR REGEXP_CONTAINS(LOWER(missing_flags_json), r'draft_pick_score_lane_pending|draft_pick_asset');
