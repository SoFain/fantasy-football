-- Validation helper. Render placeholders before running manually.
-- The 2026 slice should cover most of the active standard board; large gaps
-- mean identity joins regressed.
-- Expected result: uncovered_board_players should be low

SELECT COUNT(*) AS uncovered_board_players
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings` r
WHERE r.is_active AND r.scoring_profile_id = 'standard'
  AND r.position IN ('RB','WR','TE')
  AND NOT EXISTS (
    SELECT 1 FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_situation` s
    WHERE s.situation_for_season = 2026 AND s.player_id_internal = r.player_id
  );
