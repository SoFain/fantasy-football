-- Daily player status watch: snapshot history, change detection, team news.
--
-- Additive migration. No existing table is renamed or dropped.
--
-- sleeper_players_current stays exactly as it is, written WRITE_TRUNCATE with
-- the latest snapshot, so every existing consumer is unaffected. The new
-- sleeper_players_history table is append-only and is what makes day-over-day
-- change detection possible at all; the truncating table cannot support it
-- because yesterday's rows are gone by the time today's run reads them.
--
-- Written by src/ingest_news.py, src/player_status_changes.py, and
-- src/team_news_feeds.py via the detect-player-changes job.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_players_history` (
    snapshot_at TIMESTAMP NOT NULL,
    sleeper_player_id STRING NOT NULL,
    gsis_id STRING,
    player_name STRING,
    position STRING,
    team STRING,
    active BOOL,
    status STRING,
    injury_status STRING,
    injury_body_part STRING,
    injury_notes STRING,
    practice_participation STRING,
    fantasy_positions_json STRING,
    depth_chart_position STRING,
    depth_chart_order INT64,
    search_rank INT64,
    years_exp INT64,
    birth_date DATE,
    age FLOAT64,
    number INT64,
    height STRING,
    weight STRING,
    college STRING
)
PARTITION BY DATE(snapshot_at)
CLUSTER BY sleeper_player_id, team, position;

-- Sleeper carries birth_date and the injury detail fields, but the original
-- ingest dropped them. Age was therefore only as fresh as the seasonal
-- nflreadpy roster load, leaving rookies and mid-season signings with a null
-- age feeding the age-curve formulas.
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_players_current`
    ADD COLUMN IF NOT EXISTS birth_date DATE,
    ADD COLUMN IF NOT EXISTS age FLOAT64,
    ADD COLUMN IF NOT EXISTS injury_body_part STRING,
    ADD COLUMN IF NOT EXISTS injury_notes STRING,
    ADD COLUMN IF NOT EXISTS practice_participation STRING,
    ADD COLUMN IF NOT EXISTS number INT64,
    ADD COLUMN IF NOT EXISTS height STRING,
    ADD COLUMN IF NOT EXISTS weight STRING,
    ADD COLUMN IF NOT EXISTS college STRING;

-- One row per player per changed field, per detection run.
CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.player_status_changes` (
    detected_at TIMESTAMP NOT NULL,
    sleeper_player_id STRING NOT NULL,
    gsis_id STRING,
    player_name STRING,
    position STRING,
    team STRING,
    previous_team STRING,
    field_name STRING NOT NULL,
    old_value STRING,
    new_value STRING,
    triggers_news_check BOOL NOT NULL,
    previous_snapshot_at TIMESTAMP,
    current_snapshot_at TIMESTAMP
)
PARTITION BY DATE(detected_at)
CLUSTER BY field_name, team, sleeper_player_id;

-- Team beat-writer items pulled only for teams that had a triggering change.
-- These are commentary, not an authoritative injury source. Treat them as
-- context for investigating a flag, never as the flag itself.
CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.team_news_items` (
    fetched_at TIMESTAMP NOT NULL,
    team STRING NOT NULL,
    feed_url STRING,
    item_url STRING,
    title STRING,
    summary STRING,
    author STRING,
    published_at TIMESTAMP,
    matched_player_count INT64
)
PARTITION BY DATE(fetched_at)
CLUSTER BY team, published_at;

-- Which changed players a news item mentions. Full-name matches only; last
-- name alone produces too many false positives on a team blog.
CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.player_news_matches` (
    fetched_at TIMESTAMP NOT NULL,
    team STRING NOT NULL,
    item_url STRING,
    title STRING,
    published_at TIMESTAMP,
    sleeper_player_id STRING NOT NULL,
    gsis_id STRING,
    player_name STRING,
    position STRING,
    trigger_field STRING,
    trigger_old_value STRING,
    trigger_new_value STRING
)
PARTITION BY DATE(fetched_at)
CLUSTER BY team, sleeper_player_id;
