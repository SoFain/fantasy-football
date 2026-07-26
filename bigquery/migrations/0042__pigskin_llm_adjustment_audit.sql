-- Preserve the bounded LLM overlay separately from deterministic Pigskin candidate scores.

ALTER TABLE `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings`
ADD COLUMN IF NOT EXISTS llm_adjustment_code STRING;

ALTER TABLE `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings`
ADD COLUMN IF NOT EXISTS llm_adjustment_detail STRING;

ALTER TABLE `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings`
ADD COLUMN IF NOT EXISTS llm_adjustment_evidence STRING;

ALTER TABLE `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings`
ADD COLUMN IF NOT EXISTS llm_estimated_games_missed INT64;

ALTER TABLE `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings`
ADD COLUMN IF NOT EXISTS llm_rank_delta INT64;

ALTER TABLE `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings_history`
ADD COLUMN IF NOT EXISTS llm_adjustment_code STRING;

ALTER TABLE `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings_history`
ADD COLUMN IF NOT EXISTS llm_adjustment_detail STRING;

ALTER TABLE `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings_history`
ADD COLUMN IF NOT EXISTS llm_adjustment_evidence STRING;

ALTER TABLE `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings_history`
ADD COLUMN IF NOT EXISTS llm_estimated_games_missed INT64;

ALTER TABLE `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings_history`
ADD COLUMN IF NOT EXISTS llm_rank_delta INT64;
