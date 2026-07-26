-- Validation helper. Render placeholders before running manually.
-- Every fetched team must be one of the 32 configured feeds.
-- Expected result: zero rows

SELECT team, COUNT(*) AS row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.team_news_items`
WHERE team NOT IN (
    'ARI','ATL','BAL','BUF','CAR','CHI','CIN','CLE','DAL','DEN','DET','GB',
    'HOU','IND','JAX','KC','LAC','LAR','LV','MIA','MIN','NE','NO','NYG',
    'NYJ','PHI','PIT','SEA','SF','TB','TEN','WAS'
)
GROUP BY team;
