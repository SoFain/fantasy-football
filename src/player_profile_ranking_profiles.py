"""Player Profiles ranking scoring-profile helpers."""

from __future__ import annotations

from google.cloud import bigquery


PLAYER_PROFILE_SCORING_PROFILE_OPTIONS = (
    {"label": "PPR", "scoring_profile_id": "ppr"},
    {"label": "Half PPR", "scoring_profile_id": "half_ppr"},
    {"label": "Standard", "scoring_profile_id": "standard"},
    {"label": "GNG Keeper", "scoring_profile_id": "gng_keeper"},
)
PLAYER_PROFILE_SCORING_PROFILE_DEFAULT = "ppr"
PLAYER_PROFILE_RANKINGS_MISSING_MESSAGE = "Rankings for this scoring system have not been generated yet."
PLAYER_PROFILE_POSITION_DEPTH_LIMITS = {
    "QB": 45,
    "RB": 80,
    "WR": 100,
    "TE": 35,
}


def get_player_profile_scoring_profile_options():
    return PLAYER_PROFILE_SCORING_PROFILE_OPTIONS


def resolve_player_profile_scoring_profile(label_or_id):
    value = str(label_or_id or PLAYER_PROFILE_SCORING_PROFILE_DEFAULT).strip()
    for option in PLAYER_PROFILE_SCORING_PROFILE_OPTIONS:
        if value == option["label"] or value == option["scoring_profile_id"]:
            return option
    return PLAYER_PROFILE_SCORING_PROFILE_OPTIONS[0]


def build_pigskin_rankings_query(project_id, dataset_id, scoring_profile_id):
    sql_query = f"""
    SELECT
        player_id,
        position,
        scoring_profile_id,
        rank AS pigskin_rank,
        tier AS pigskin_tier,
        ranking_score AS pigskin_ranking_score,
        confidence_score AS pigskin_confidence_score,
        sleeper_team,
        sleeper_status,
        sleeper_depth_chart_position,
        sleeper_depth_chart_order,
        raw_ranking_score,
        depth_chart_penalty,
        avg_passing_epa,
        season_passing_epa,
        avg_rushing_epa,
        season_rushing_epa,
        avg_receiving_epa,
        season_receiving_epa,
        latest_season_wopr,
        previous_season_wopr,
        two_years_ago_wopr,
        latest_season_target_share,
        previous_season_target_share,
        latest_season_carry_share,
        previous_season_carry_share,
        candidate_rank,
        candidate_ranking_score,
        rank_source,
        adjudicated_at,
        ranking_eligibility,
        pigskin_verdict,
        rank_rationale,
        risk_flags,
        what_would_change_mind,
        ranking_version,
        generated_at AS ranking_generated_at,
        model_name AS ranking_model_name,
        prompt_version AS ranking_prompt_version,
        data_snapshot_label AS ranking_data_snapshot
    FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings`
    WHERE is_active = TRUE
      AND scoring_profile_id = @scoring_profile_id
      AND rank <= CASE position
        WHEN 'QB' THEN {PLAYER_PROFILE_POSITION_DEPTH_LIMITS["QB"]}
        WHEN 'RB' THEN {PLAYER_PROFILE_POSITION_DEPTH_LIMITS["RB"]}
        WHEN 'WR' THEN {PLAYER_PROFILE_POSITION_DEPTH_LIMITS["WR"]}
        WHEN 'TE' THEN {PLAYER_PROFILE_POSITION_DEPTH_LIMITS["TE"]}
        ELSE 0
      END
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("scoring_profile_id", "STRING", scoring_profile_id)
        ]
    )
    return sql_query, job_config
