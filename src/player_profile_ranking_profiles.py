"""Player Profiles ranking scoring-profile helpers."""

from __future__ import annotations

from google.cloud import bigquery


PLAYER_PROFILE_SCORING_PROFILE_OPTIONS = (
    {"label": "Standard", "scoring_profile_id": "standard"},
    {"label": "Half PPR", "scoring_profile_id": "half_ppr"},
    {"label": "PPR", "scoring_profile_id": "ppr"},
    {"label": "GNG Keeper", "scoring_profile_id": "gng_keeper"},
)
PLAYER_PROFILE_SCORING_PROFILE_DEFAULT = "standard"
PLAYER_PROFILE_DEFAULT_BOARD = "ALL"
PLAYER_PROFILE_POSITION_OPTIONS = ("ALL", "QB", "RB", "WR", "TE")
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


def normalize_player_profile_board(board_or_position):
    value = str(board_or_position or PLAYER_PROFILE_DEFAULT_BOARD).strip().upper()
    if value == "ALL":
        return "ALL"
    if value in PLAYER_PROFILE_POSITION_DEPTH_LIMITS:
        return value
    return PLAYER_PROFILE_DEFAULT_BOARD


def sort_player_profile_board(df, selected_board=PLAYER_PROFILE_DEFAULT_BOARD):
    """Sort Player Profiles rows with the same contract used by the live UI."""

    import pandas as pd

    board = normalize_player_profile_board(selected_board)
    out = df.copy()
    if board != "ALL":
        out = out[out["position"] == board]

    out["display_rank_sort"] = pd.to_numeric(out["display_rank"], errors="coerce").fillna(9999)
    out["display_score_sort"] = pd.to_numeric(out["display_score"], errors="coerce").fillna(0)
    if board == "ALL":
        if "unified_overall_rank" in out.columns and out["unified_overall_rank"].notna().any():
            out = out[out["unified_overall_rank"].notna()].copy()
            out["board_rank"] = pd.to_numeric(out["unified_overall_rank"], errors="coerce")
            out = out.sort_values(by=["board_rank", "player_display_name"], ascending=[True, True])
        else:
            out = out.sort_values(
                by=["display_score_sort", "display_rank_sort", "position", "player_display_name"],
                ascending=[False, True, True, True],
            )
            out["board_rank"] = range(1, len(out) + 1)
    else:
        out = out.sort_values(
            by=["display_rank_sort", "display_score_sort", "player_display_name"],
            ascending=[True, False, True],
        )
        out["board_rank"] = out["display_rank"]
    return out


def format_adjustment_label(code, rank_delta=None):
    value = str(code or "").strip().upper()
    try:
        delta = int(rank_delta) if rank_delta is not None else 0
    except (TypeError, ValueError):
        delta = 0
    movement = f" {delta:+d}" if delta else ""
    labels = {
        "": "Formula rank",
        "NO_ADJUSTMENT": "Formula rank",
        "CURRENT_ROLE_UPGRADE": f"Role upgrade{movement}",
        "CURRENT_ROLE_DOWNGRADE": f"Role downgrade{movement}",
        "ROOKIE_CONTEXT": f"Rookie context{movement}",
        "INJURY_UNCERTAIN": "Injury noted, no move",
        "SUSPENSION_UNCERTAIN": "Suspension review, no move",
        "ORDER_REBALANCE": f"Queue reorder{movement}",
    }
    if value.startswith("INJURY_"):
        return labels.get(value, f"Injury adjustment{movement}")
    if value.startswith("SUSPENSION_"):
        return labels.get(value, f"Suspension adjustment{movement}")
    return labels.get(value, value.replace("_", " ").title() + movement)


def build_unified_rankings_query(project_id, dataset_id, scoring_profile_id):
    sql_query = f"""
    SELECT player_id, position, overall_rank AS unified_overall_rank,
        board_version AS unified_board_version, replacement_rank AS unified_replacement_rank,
        position_source_version, position_rank_source
    FROM `{project_id}.{dataset_id}.unified_draft_rankings_current`
    WHERE scoring_profile_id = @scoring_profile_id
    """
    return sql_query, bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("scoring_profile_id", "STRING", scoring_profile_id)
    ])


def build_pigskin_rankings_query(project_id, dataset_id, scoring_profile_id):
    sql_query = f"""
    WITH latest_sleeper_status AS (
        SELECT sleeper_player_id, injury_status
        FROM `{project_id}.{dataset_id}.sleeper_players_current`
    )
    SELECT
        rankings.player_id,
        rankings.position,
        rankings.scoring_profile_id,
        rankings.rank AS pigskin_rank,
        rankings.tier AS pigskin_tier,
        rankings.ranking_score AS pigskin_ranking_score,
        rankings.confidence_score AS pigskin_confidence_score,
        rankings.sleeper_team,
        rankings.sleeper_status,
        COALESCE(latest_sleeper_status.injury_status, rankings.sleeper_injury_status) AS sleeper_injury_status,
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
        llm_adjustment_code,
        llm_adjustment_detail,
        llm_adjustment_evidence,
        llm_estimated_games_missed,
        llm_rank_delta,
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
    FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings` rankings
    LEFT JOIN latest_sleeper_status
      ON rankings.sleeper_player_id = latest_sleeper_status.sleeper_player_id
    WHERE rankings.is_active = TRUE
      AND rankings.scoring_profile_id = @scoring_profile_id
      AND rankings.rank <= CASE rankings.position
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


def build_live_ranking_context_query(
    project_id,
    dataset_id,
    scoring_profile_id=PLAYER_PROFILE_SCORING_PROFILE_DEFAULT,
    board=PLAYER_PROFILE_DEFAULT_BOARD,
    limit=10,
):
    normalized_board = normalize_player_profile_board(board)
    position_filter = None if normalized_board == "ALL" else normalized_board
    sql_query = f"""
    WITH active_rankings AS (
        SELECT
            model_run_id,
            ranking_version,
            scoring_profile_id,
            generated_at,
            adjudicated_at,
            season,
            ranking_phase,
            format,
            position,
            `rank` AS position_rank,
            tier,
            player_id,
            player_name,
            COALESCE(current_team, sleeper_team) AS team,
            current_team,
            roster_status,
            sleeper_player_id,
            sleeper_team,
            sleeper_active,
            sleeper_status,
            ranking_eligibility,
            rank_source,
            ranking_score AS pigskin_score,
            confidence_score,
            avg_ppr,
            avg_opportunity,
            avg_efficiency,
            avg_total_epa,
            avg_passing_epa,
            avg_rushing_epa,
            avg_receiving_epa,
            avg_wopr,
            latest_season_wopr,
            previous_season_wopr,
            pigskin_verdict,
            rank_rationale,
            risk_flags,
            what_would_change_mind,
            data_snapshot_label
            ,unified.overall_rank AS unified_overall_rank
        FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings` rankings
        LEFT JOIN (
          SELECT scoring_profile_id AS unified_profile_id, player_id AS unified_player_id,
            position AS unified_position, overall_rank
          FROM `{project_id}.{dataset_id}.unified_draft_rankings_current`
        ) unified
          ON unified.unified_profile_id = rankings.scoring_profile_id
         AND unified.unified_player_id = rankings.player_id
         AND unified.unified_position = rankings.position
        WHERE rankings.is_active = TRUE
          AND rankings.scoring_profile_id = @scoring_profile_id
          AND (@position IS NULL OR rankings.position = @position)
          AND rankings.`rank` <= CASE rankings.position
            WHEN 'QB' THEN {PLAYER_PROFILE_POSITION_DEPTH_LIMITS["QB"]}
            WHEN 'RB' THEN {PLAYER_PROFILE_POSITION_DEPTH_LIMITS["RB"]}
            WHEN 'WR' THEN {PLAYER_PROFILE_POSITION_DEPTH_LIMITS["WR"]}
            WHEN 'TE' THEN {PLAYER_PROFILE_POSITION_DEPTH_LIMITS["TE"]}
            ELSE 0
          END
    ),
    ordered_rankings AS (
        SELECT
            ROW_NUMBER() OVER (
                ORDER BY
                    CASE WHEN @position IS NULL AND unified_overall_rank IS NULL THEN 1 ELSE 0 END ASC,
                    CASE WHEN @position IS NULL THEN unified_overall_rank END ASC,
                    CASE WHEN @position IS NULL AND unified_overall_rank IS NULL THEN pigskin_score END DESC,
                    position_rank ASC,
                    position ASC,
                    player_name ASC
            ) AS board_rank,
            *
        FROM active_rankings
    )
    SELECT *
    FROM ordered_rankings
    ORDER BY board_rank
    LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("scoring_profile_id", "STRING", scoring_profile_id or PLAYER_PROFILE_SCORING_PROFILE_DEFAULT),
            bigquery.ScalarQueryParameter("position", "STRING", position_filter),
            bigquery.ScalarQueryParameter("limit", "INT64", int(limit or 10)),
        ]
    )
    return sql_query, job_config
