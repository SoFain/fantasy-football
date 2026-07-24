-- Season coaching baseline + coaching-change columns on the situation layer.
--
-- Additive migration. No existing table is renamed or dropped.
--
-- coaching_staff_history holds per-season staff baselines so the situation
-- layer can detect coaching changes. The 2025 seed is head-coach-only: the
-- Wikipedia season pages record the head coach in their infobox, and no
-- equally reliable per-season source exists yet for coordinators. A team with
-- a mid-season change carries both names ('A; B').
--
-- Written by src/ingest_coaching_staff.py (load_coaching_history) from
-- data/coaching_staff_2025.csv.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.coaching_staff_history` (
    season INT64 NOT NULL,
    team_abbr STRING NOT NULL,
    role STRING NOT NULL,
    coach_name STRING NOT NULL,
    verification_status STRING,
    source STRING,
    notes STRING,
    loaded_at TIMESTAMP NOT NULL
)
CLUSTER BY season, team_abbr;

-- Coaching-change facts on the situation layer. hc_changed compares the
-- current head coach against the prior-season baseline; oc_changed stays NULL
-- until a coordinator baseline exists.
ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_situation`
    ADD COLUMN IF NOT EXISTS hc_changed BOOL,
    ADD COLUMN IF NOT EXISTS oc_changed BOOL;
