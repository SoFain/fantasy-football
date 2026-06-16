-- Compatibility view for Trade Lab assets.
-- Backing table is populated by src/materialize_trade_assets.py.

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_assets_current` AS
SELECT *
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.mart_trade_assets_current`;
