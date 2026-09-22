-- Additive scoring profile seed for GNG Keeper.
-- No player-week rows, rankings, backtests, or model outputs are written.

MERGE `{{PROJECT_ID}}.{{DATASET_ID}}.scoring_profiles` target
USING (
    SELECT
        'gng_keeper' AS scoring_profile_id,
        'GNG Keeper' AS display_name,
        '{"settings":{"bonuses":{},"dst":{},"fumbles_lost":-2.0,"interceptions":-2.0,"kicker":{},"passing_2pt_conversions":2.0,"passing_tds":5.0,"passing_yards":0.02,"receiving_2pt_conversions":2.0,"receiving_tds":6.0,"receiving_yards":0.04,"receptions":0.1,"return_tds":6.0,"rushing_2pt_conversions":2.0,"rushing_tds":6.0,"rushing_yards":0.04},"sleeper_scoring_settings":{"blk_kick":1.0,"bonus_pass_cmp_25":1.0,"bonus_pass_yd_300":1.0,"bonus_pass_yd_400":2.0,"bonus_rec_te":0.2,"bonus_rec_wr":0.1,"bonus_rec_yd_100":1.0,"bonus_rec_yd_200":2.0,"bonus_rush_att_20":1.0,"bonus_rush_rec_yd_200":1.0,"bonus_rush_yd_100":1.0,"bonus_rush_yd_200":2.0,"def_3_and_out":0.5,"def_4_and_stop":1.0,"def_st_ff":1.0,"def_st_fum_rec":1.0,"def_st_td":6.0,"def_td":6.0,"ff":0.0,"fgm":3.0,"fgm_0_19":0.0,"fgm_20_29":0.0,"fgm_30_39":0.0,"fgm_40_49":0.0,"fgm_50_59":1.0,"fgm_60p":2.0,"fgmiss":-1.0,"fgmiss_0_19":-4.0,"fgmiss_20_29":-3.0,"fgmiss_30_39":-2.0,"fgmiss_40_49":-1.0,"fgmiss_50_59":0.0,"fgmiss_50p":0.0,"fgmiss_60p":0.0,"fum":0.0,"fum_lost":-2.0,"fum_rec":2.0,"fum_rec_td":6.0,"int":2.0,"kr_yd":0.05,"pass_2pt":2.0,"pass_cmp_40p":0.5,"pass_int":-2.0,"pass_int_td":-4.0,"pass_sack":-1.0,"pass_td":5.0,"pass_td_40p":0.0,"pass_td_50p":0.5,"pass_yd":0.02,"pr_yd":0.1,"pts_allow_0":8.0,"pts_allow_14_20":2.0,"pts_allow_1_6":6.0,"pts_allow_21_27":0.0,"pts_allow_28_34":-3.0,"pts_allow_35p":-6.0,"pts_allow_7_13":4.0,"rec":0.1,"rec_2pt":2.0,"rec_40p":0.5,"rec_fd":0.1,"rec_td":6.0,"rec_td_40p":0.0,"rec_td_50p":0.5,"rec_yd":0.04,"rush_2pt":2.0,"rush_40p":1.0,"rush_fd":0.1,"rush_td":6.0,"rush_td_40p":0.0,"rush_td_50p":1.0,"rush_yd":0.04,"sack":1.0,"safe":4.0,"st_ff":1.0,"st_fum_rec":1.0,"st_td":6.0,"tkl_loss":0.0,"xpm":1.0,"xpmiss":-2.0,"yds_allow_0_100":2.0,"yds_allow_100_199":1.0,"yds_allow_300_349":-1.0,"yds_allow_350_399":-2.0,"yds_allow_400_449":-4.0,"yds_allow_450_499":-5.0,"yds_allow_500_549":-6.0,"yds_allow_550p":-7.0},"source_metadata":{"league_status_at_retrieval":"pre_draft","season":2026,"source":"owner-supplied Sleeper league report","source_league_id":"1369406895588143104"},"unmapped_settings":{"blk_kick":1.0,"bonus_pass_cmp_25":1.0,"bonus_pass_yd_300":1.0,"bonus_pass_yd_400":2.0,"bonus_rec_te":0.2,"bonus_rec_wr":0.1,"bonus_rec_yd_100":1.0,"bonus_rec_yd_200":2.0,"bonus_rush_att_20":1.0,"bonus_rush_rec_yd_200":1.0,"bonus_rush_yd_100":1.0,"bonus_rush_yd_200":2.0,"def_3_and_out":0.5,"def_4_and_stop":1.0,"def_st_ff":1.0,"def_st_fum_rec":1.0,"def_st_td":6.0,"def_td":6.0,"ff":0.0,"fgm":3.0,"fgm_0_19":0.0,"fgm_20_29":0.0,"fgm_30_39":0.0,"fgm_40_49":0.0,"fgm_50_59":1.0,"fgm_60p":2.0,"fgmiss":-1.0,"fgmiss_0_19":-4.0,"fgmiss_20_29":-3.0,"fgmiss_30_39":-2.0,"fgmiss_40_49":-1.0,"fgmiss_50_59":0.0,"fgmiss_50p":0.0,"fgmiss_60p":0.0,"fum":0.0,"fum_rec":2.0,"fum_rec_td":6.0,"int":2.0,"kr_yd":0.05,"pass_cmp_40p":0.5,"pass_int_td":-4.0,"pass_sack":-1.0,"pass_td_40p":0.0,"pass_td_50p":0.5,"pr_yd":0.1,"pts_allow_0":8.0,"pts_allow_14_20":2.0,"pts_allow_1_6":6.0,"pts_allow_21_27":0.0,"pts_allow_28_34":-3.0,"pts_allow_35p":-6.0,"pts_allow_7_13":4.0,"rec_40p":0.5,"rec_fd":0.1,"rec_td_40p":0.0,"rec_td_50p":0.5,"rush_40p":1.0,"rush_fd":0.1,"rush_td_40p":0.0,"rush_td_50p":1.0,"sack":1.0,"safe":4.0,"st_ff":1.0,"st_fum_rec":1.0,"tkl_loss":0.0,"xpm":1.0,"xpmiss":-2.0,"yds_allow_0_100":2.0,"yds_allow_100_199":1.0,"yds_allow_300_349":-1.0,"yds_allow_350_399":-2.0,"yds_allow_400_449":-4.0,"yds_allow_450_499":-5.0,"yds_allow_500_549":-6.0,"yds_allow_550p":-7.0}}' AS scoring_json_text
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
