-- GNG parity for the situation layer.
--
-- Additive migration. No existing table is renamed or dropped.
--
-- Owner rule: GNG rankings and scoring are included in anything Standard
-- scoring is included in. The situation layer's PPG facts, QB-quality
-- measures, and the ML training outcomes were standard-only; these columns
-- carry the same facts in GNG Keeper scoring from the same profile-aware
-- points history. Unsuffixed columns remain standard scoring; _gng columns
-- are GNG Keeper. Flag thresholds (QB_UPGRADE bands) stay defined on the
-- standard delta; both deltas are stored so either scale can be cited.

ALTER TABLE `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_situation`
    ADD COLUMN IF NOT EXISTS gng_ppg_prev FLOAT64,
    ADD COLUMN IF NOT EXISTS gng_ppg_next FLOAT64,
    ADD COLUMN IF NOT EXISTS qb_quality_from_gng FLOAT64,
    ADD COLUMN IF NOT EXISTS qb_quality_to_gng FLOAT64,
    ADD COLUMN IF NOT EXISTS qb_quality_delta_gng FLOAT64;
