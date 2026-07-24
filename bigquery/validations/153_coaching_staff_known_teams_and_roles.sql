-- Validation helper. Render placeholders before running manually.
-- Every row must use a known team and a canonical role.
-- Expected result: zero rows

SELECT team_abbr, role
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.coaching_staff_current`
WHERE team_abbr NOT IN ('ARI','ATL','BAL','BUF','CAR','CHI','CIN','CLE','DAL','DEN','DET','GB','HOU','IND','JAX','KC','LAC','LAR','LV','MIA','MIN','NE','NO','NYG','NYJ','PHI','PIT','SEA','SF','TB','TEN','WAS')
   OR role NOT IN ('head_coach','senior_assistant','offensive_coordinator','defensive_coordinator','quarterbacks_coach','running_backs_coach','wide_receivers_coach','offensive_line_coach')
GROUP BY team_abbr, role;
