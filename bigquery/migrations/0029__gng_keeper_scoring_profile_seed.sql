-- Additive scoring profile seed for GNG Keeper.
-- No player-week rows, rankings, backtests, or model outputs are written.

MERGE `{{PROJECT_ID}}.{{DATASET_ID}}.scoring_profiles` target
USING (
    SELECT
        'gng_keeper' AS scoring_profile_id,
        'GNG Keeper' AS display_name,
        '{"settings":{"bonuses":{},"dst":{},"fumbles_lost":0.0,"interceptions":-2.0,"kicker":{},"passing_2pt_conversions":2.0,"passing_tds":5.0,"passing_yards":0.02,"receiving_2pt_conversions":2.0,"receiving_tds":6.0,"receiving_yards":0.04,"receptions":0.1,"return_tds":0.0,"rushing_2pt_conversions":2.0,"rushing_tds":6.0,"rushing_yards":0.04},"source_metadata":{"season":2026,"source":"owner-supplied Sleeper league report","source_league_id":"1369406895588143104"},"unmapped_settings":{"bonus_pass_cmp_25":1.0,"bonus_pass_yd_300":1.0,"bonus_pass_yd_400":2.0,"bonus_rec_te":0.2,"bonus_rec_wr":0.1,"bonus_rec_yd_100":1.0,"bonus_rec_yd_200":2.0,"bonus_rush_att_20":1.0,"bonus_rush_rec_yd_200":1.0,"bonus_rush_yd_100":1.0,"bonus_rush_yd_200":2.0,"pass_cmp_40p":0.5,"pass_int_td":-4.0,"pass_sack":-1.0,"pass_td_50p":0.5,"rec_40p":0.5,"rec_fd":0.1,"rec_td_50p":0.5,"rush_40p":1.0,"rush_fd":0.1,"rush_td_50p":1.0}}' AS scoring_json_text
) source
ON target.scoring_profile_id = source.scoring_profile_id
WHEN MATCHED THEN
    UPDATE SET
        scoring_json = PARSE_JSON(source.scoring_json_text),
        display_name = source.display_name,
        updated_at = CURRENT_TIMESTAMP(),
        active = TRUE
WHEN NOT MATCHED THEN
    INSERT (
        scoring_profile_id,
        display_name,
        scoring_json,
        created_at,
        updated_at,
        active
    )
    VALUES (
        source.scoring_profile_id,
        source.display_name,
        PARSE_JSON(source.scoring_json_text),
        CURRENT_TIMESTAMP(),
        CURRENT_TIMESTAMP(),
        TRUE
    );
