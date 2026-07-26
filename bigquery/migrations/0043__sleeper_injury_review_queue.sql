-- Auditable OUT/IR transitions from Sleeper. These records never change rankings automatically.

CREATE TABLE IF NOT EXISTS `fantasy-football-498121.fantasy_football_brain.sleeper_injury_review_queue` (
  event_id STRING NOT NULL,
  sleeper_player_id STRING NOT NULL,
  player_name STRING,
  team STRING,
  position STRING,
  previous_injury_status STRING,
  injury_status STRING NOT NULL,
  detected_at TIMESTAMP NOT NULL,
  source_name STRING NOT NULL,
  review_status STRING NOT NULL,
  requires_pigskin_investigation BOOL NOT NULL,
  ranking_action STRING NOT NULL,
  reviewed_at TIMESTAMP,
  review_source_url STRING,
  estimated_regular_season_games_missed INT64,
  review_confidence STRING,
  review_notes STRING
)
PARTITION BY DATE(detected_at)
CLUSTER BY review_status, injury_status, sleeper_player_id;
