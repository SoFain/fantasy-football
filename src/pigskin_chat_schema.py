"""Pigskin chat schema containment helpers."""

PIGSKIN_CHAT_ALLOWED_TABLES = (
    "analytics_player_weekly_truth",
    "analytics_fraud_watch",
    "analytics_pigskin_rankings",
    "analytics_pigskin_rankings_history",
    "analytics_game_environment",
    "analytics_player_qb_weekly",
    "analytics_player_qb_splits",
    "analytics_context_events",
    "analytics_external_context_search_results",
)

PIGSKIN_CHAT_BLOCKED_TABLES = (
    "weekly_metrics",
    "play_by_play",
    "player_rosters",
    "player_contracts",
    "depth_charts",
    "team_descriptions",
    "ngs_passing",
    "ngs_rushing",
    "ngs_receiving",
    "ftn_charting",
    "weekly_snap_counts",
    "injury_reports",
    "sleeper_leagues",
    "sleeper_league_users",
    "sleeper_rosters",
    "sleeper_roster_players",
    "sleeper_matchups",
    "sleeper_lineups",
    "sleeper_available_players",
    "sleeper_viewer_team_snapshots",
    "active_league_rosters",
    "historical_player_metrics",
    "market_values",
    "sleeper_players_current",
    "realtime_player_news",
)


def render_pigskin_chat_schema(dataset_name: str = "fantasy_football_brain") -> str:
    """Return the curated schema Pigskin is allowed to see in chat."""

    table = lambda name: f"`{dataset_name}.{name}`"
    return f"""
    ### Allowed Pigskin Chat Tables ###
    Pigskin chat may query only the curated mart/output tables listed below. Do not query raw/source tables, deprecated aliases, or tables that are not listed here. If curated data is unavailable, say the curated data is unavailable instead of inventing facts or falling back to raw/source tables.

    Allowed tables:
    - {table("analytics_player_weekly_truth")}
    - {table("analytics_fraud_watch")}
    - {table("analytics_pigskin_rankings")}
    - {table("analytics_pigskin_rankings_history")}
    - {table("analytics_game_environment")}
    - {table("analytics_player_qb_weekly")}
    - {table("analytics_player_qb_splits")}
    - {table("analytics_context_events")}
    - {table("analytics_external_context_search_results")}

    - Table: {table("analytics_player_weekly_truth")} (PRIMARY PLAYER EVIDENCE TABLE)
      Description: Derived AI vs Vibes player truth table with fantasy output, usage, red-zone role, EPA, recent trend, opportunity scoring, efficiency scoring, and criticism-ready flags.
      Columns include: `season`, `week`, `player_id`, `player_name`, `player_full_name`, `position`, `team`, `current_team`, `roster_status`, `team_changed_since_stats`, `primary_qb_name`, `primary_qb_epa_per_target`, `primary_qb_target_share`, `qbs_targeted_by`, `opponent_team`, `fantasy_points_ppr`, `targets`, `receptions`, `carries`, `target_share`, `air_yards_share`, `wopr`, `passing_epa`, `rushing_epa`, `receiving_epa`, `total_epa`, `red_zone_targets`, `red_zone_carries`, `red_zone_touches`, `prior_week_ppr`, `ppr_delta`, `rolling_3_week_ppr`, `rolling_3_week_targets`, `rolling_3_week_carries`, `opportunity_score`, `efficiency_score`, `role_quality_score`, `points_over_role_score`, `role_fragility_score`, `analytical_grade`, `touchdown_dependent`, `box_score_trap`, `target_earner`, `empty_volume`, `usage_warning`, `points_outran_role`, `thin_role_big_week`, `fragile_role`, `role_backed_production`, and `analytical_verdict`.
      `team` is the historical team for that stat week. `current_team` is the latest known roster team. If `team_changed_since_stats` is true, do not describe the player as currently on `team`.

    - Table: {table("analytics_pigskin_rankings")}
      Description: Canonical active Pigskin rankings used by Player Profiles and chat. This is the source of truth for Pigskin-owned player ranks.
      Columns include: `model_run_id`, `ranking_version`, `generated_at`, `adjudicated_at`, `season`, `ranking_phase`, `format`, `position`, `rank`, `tier`, `player_id`, `player_name`, `current_team`, `roster_status`, `sleeper_player_id`, `sleeper_team`, `sleeper_active`, `sleeper_status`, `sleeper_depth_chart_position`, `sleeper_depth_chart_order`, `ranking_eligibility`, `candidate_rank`, `candidate_ranking_score`, `raw_ranking_score`, `depth_chart_penalty`, `ranking_score`, `rank_source`, `avg_ppr`, `avg_opportunity`, `avg_efficiency`, `avg_total_epa`, `season_total_epa`, `avg_epa_per_opportunity`, `avg_passing_epa`, `season_passing_epa`, `avg_rushing_epa`, `season_rushing_epa`, `avg_receiving_epa`, `season_receiving_epa`, `avg_role_quality`, `avg_role_fragility`, `avg_grade`, `avg_wopr`, `avg_target_share`, `avg_carry_share`, `latest_season_wopr`, `previous_season_wopr`, `two_years_ago_wopr`, `latest_season_target_share`, `previous_season_target_share`, `latest_season_carry_share`, `previous_season_carry_share`, `confidence_score`, `pigskin_verdict`, `rank_rationale`, `risk_flags`, `what_would_change_mind`, `model_name`, `prompt_version`, `data_snapshot_label`, and `is_active`.
      If this table says a player is ranked at a position, that is Pigskin's current owned ranking. Do not deny it. Defend it, critique the risk, or explain what would change it.

    - Table: {table("analytics_pigskin_rankings_history")}
      Description: Append-only history of Pigskin ranking publications. Use it when the user asks how a ranking changed across versions or asks about an older call.
      Columns match the active ranking table, with one snapshot per `ranking_version`.

    - Table: {table("analytics_fraud_watch")}
      Description: Show-facing Fraud Watch output for identifying fantasy box scores that outran the player's actual role quality.
      Columns include: `season`, `week`, `player_name`, `position`, `team`, `current_team`, `fantasy_points_ppr`, `skill_player_opportunities`, `target_share`, `wopr`, `offense_pct`, `touchdowns`, `touchdown_dependency_rate`, `role_quality_score`, `points_over_role_score`, `role_fragility_score`, `fraud_score`, `fraud_label`, `fraud_case`, and `what_would_change_mind`.

    - Table: {table("analytics_player_qb_splits")}
      Description: Season-level receiver-by-QB split table. Use this before making claims about QB-driven receiver changes.
      Columns include: `season`, `posteam`, `player_id`, `player_name`, `qb_id`, `qb_name`, `weeks_with_targets`, `first_week_with_qb`, `last_week_with_qb`, `targets`, `receptions`, `catch_rate`, `receiving_yards`, `yards_per_target`, `adot`, `touchdowns`, `red_zone_targets`, `total_epa`, `epa_per_target`, `target_share_from_qb`, `team_target_share`, and `sample_label`.

    - Table: {table("analytics_player_qb_weekly")}
      Description: Weekly receiver-by-QB split table. Use this to test before/after QB changes, injury effects, and whether a receiver's role changed or only target quality changed.
      Columns include: `season`, `week`, `posteam`, `defteam`, `player_id`, `player_name`, `qb_id`, `qb_name`, `targets`, `receptions`, `catch_rate`, `receiving_yards`, `yards_per_target`, `adot`, `touchdowns`, `red_zone_targets`, `total_epa`, `epa_per_target`, `target_share_from_qb`, and `team_target_share`.

    - Table: {table("analytics_context_events")}
      Description: Curated event ledger for causal context such as QB injuries, QB changes, offensive line injuries, coaching/play-caller changes, training camp reports/reps, usage split trends, weather, and other fantasy-relevant situational events.
      Columns include: `event_id`, `season`, `start_week`, `end_week`, `team`, `event_type`, `subject_player_id`, `subject_name`, `subject_position`, `affected_player_id`, `affected_player_name`, `affected_unit`, `causal_status`, `confidence_score`, `source_type`, `source_label`, `source_url`, `summary`, `analysis_instruction`, and `active`.

    - Table: {table("analytics_external_context_search_results")}
      Description: Stored external verification search results. Use these rows as leads or supporting context, not as verified truth by themselves unless the linked source clearly supports the claim.
      Columns include: `searched_at`, `player_name`, `query`, `result_rank`, `title`, `link`, `display_link`, `snippet`, `source_type`, `provider`, and `source_name`.

    - Table: {table("analytics_game_environment")}
      Description: One row per regular-season game with stadium, roof, surface, temperature, wind, weather text, and fantasy-relevant environment flags.
      Columns include: `season`, `week`, `game_id`, `game_date`, `home_team`, `away_team`, `stadium`, `historical_stadium_name`, `stadium_id`, `roof`, `surface`, `temp_f`, `wind_mph`, `weather_text`, `is_indoor_or_closed`, `roof_category`, `surface_category`, `precipitation_or_storm_flag`, `snow_or_freezing_flag`, `temperature_bucket`, `wind_bucket`, `environment_risk_level`, and `fantasy_environment_note`.
    """
