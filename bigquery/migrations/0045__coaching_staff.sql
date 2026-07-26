-- Current NFL coaching staff, the first coaching layer.
--
-- Additive migration. No existing table is renamed or dropped.
--
-- One row per team per canonical role, for all 32 teams and 8 roles (256 rows
-- when fully populated). Written by src/ingest_coaching_staff.py from the
-- curated data/coaching_staff.csv, which is sourced from the Wikipedia
-- "List of current NFL staffs" page.
--
-- Current staff only. Coaching styles and historical records are later layers
-- and are intentionally not modeled here.
--
-- WRITE_TRUNCATE on each refresh: this is a small current-state reference, not
-- a history table. snapshot_at is present so a history table can be added later
-- without reshaping this one.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.coaching_staff_current` (
    snapshot_at TIMESTAMP NOT NULL,
    team_abbr STRING NOT NULL,
    team_name STRING NOT NULL,
    conference STRING,
    division STRING,
    role STRING NOT NULL,
    role_title STRING NOT NULL,
    role_rank INT64 NOT NULL,
    coach_name STRING,
    raw_title STRING,
    is_vacant BOOL NOT NULL,
    verification_status STRING NOT NULL,
    source STRING,
    source_url STRING,
    notes STRING,
    missing_fields_json STRING
)
CLUSTER BY team_abbr, role_rank;
