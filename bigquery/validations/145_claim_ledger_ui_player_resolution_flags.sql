-- Validation helper. Render placeholders before running manually.
-- Expected result: non_draft_unresolved_player_rows = 0

SELECT COUNT(*) AS non_draft_unresolved_player_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.fantasy_claim_players` players
JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.fantasy_claims` claims
  ON players.claim_id = claims.claim_id
WHERE claims.review_status IN ('reviewed', 'ready_to_grade', 'graded')
  AND players.player_id_internal IS NULL;
