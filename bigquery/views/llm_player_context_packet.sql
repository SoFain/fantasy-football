-- Production compatibility view for Pigskin and writing-AI player context.
-- Backing table is refreshed by src/materialize_llm_packets.py.
-- Replaces future arbitrary SQL access from render_ai_cohost, app.py:2525-2796.

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.llm_player_context_packet` AS
SELECT *
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.mart_llm_player_context_packet`;
