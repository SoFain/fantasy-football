-- Player situation layer: team/QB/coaching/age context per player per season.
--
-- Additive migration. No existing table is renamed or dropped.
--
-- One table serves two purposes at different season slices:
--   * situation_for_season = 2026 rows are the LIVE situation layer: the
--     context the boards and articles were blind to (D.J. Moore ranked on
--     2025-CHI metrics while Sleeper says BUF WR1; 57 of 264 standard-board
--     players carry team_changed_since_stats).
--   * situation_for_season <= 2025 rows are the ML TRAINING SET: historical
--     transitions (2016-2025 from the profile-aware points history) with
--     next-season outcomes, used by BigQuery ML to estimate how much a team
--     change or QB-quality delta actually moves next-season scoring. Those
--     coefficients become the candidate Phase-3 adjustment magnitudes for
--     owner review; nothing here moves a ranking by itself.
--
-- QB quality convention: a QB's quality entering season S+1 is his season-S
-- standard PPG (information available at decision time). qb_to is the person
-- who actually led the team in S+1 (known in the offseason), valued at his
-- season-S PPG; a rookie QB has NULL prior quality and is flagged.
--
-- Written by src/situation_layer.py via the build-situation-layer job.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_situation` (
    situation_for_season INT64 NOT NULL,
    stats_season INT64 NOT NULL,
    player_id_internal STRING NOT NULL,
    gsis_id STRING,
    sleeper_player_id STRING,
    player_name STRING,
    position STRING NOT NULL,
    team_from STRING,
    team_to STRING,
    team_changed BOOL,
    games_prev INT64,
    ppg_prev FLOAT64,
    ppg_next FLOAT64,
    qb_from STRING,
    qb_to STRING,
    qb_quality_from FLOAT64,
    qb_quality_to FLOAT64,
    qb_quality_delta FLOAT64,
    qb_changed BOOL,
    age_at_season FLOAT64,
    head_coach STRING,
    offensive_coordinator STRING,
    flags_json STRING,
    metric_basis STRING,
    created_at TIMESTAMP NOT NULL
)
CLUSTER BY situation_for_season, position;
