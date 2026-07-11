import argparse
import json
import logging
import math
import os
import re
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.ingest_news import load_realtime_news
from src.load import get_bigquery_project
from src.materialize import materialize_pigskin_rankings
from src.model_runs import (
    create_model_run,
    create_source_freshness_snapshot,
    mark_model_run_complete,
    mark_model_run_failed,
)


logger = logging.getLogger("generate_pigskin_rankings")

DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
DEFAULT_MODEL_VERSION = os.environ.get("PIGSKIN_RANKINGS_MODEL_VERSION", "v1")
DEFAULT_PROMPT_VERSION = os.environ.get("PIGSKIN_RANKINGS_PROMPT_VERSION", "pigskin-rankings-llm-v3")
DEFAULT_SCORING_PROFILE_ID = os.environ.get("PIGSKIN_SCORING_PROFILE_ID", "ppr")
DEFAULT_LEAGUE_TYPE_ID = os.environ.get("PIGSKIN_LEAGUE_TYPE_ID", "redraft")
DEFAULT_ROSTER_FORMAT_ID = os.environ.get("PIGSKIN_ROSTER_FORMAT_ID", "one_qb")
DEFAULT_FEATURE_CONFIG_VERSION_ID = os.environ.get("PIGSKIN_FEATURE_CONFIG_VERSION_ID") or None
DEFAULT_POSITION_LIMITS = {
    "QB": 45,
    "RB": 80,
    "WR": 100,
    "TE": 35,
}
VALID_POSITIONS = tuple(DEFAULT_POSITION_LIMITS)
RANKING_SOURCE_TABLES = (
    "analytics_pigskin_rankings_candidates",
    "analytics_player_weekly_truth",
    "player_rosters",
    "sleeper_players_current",
    "analytics_pigskin_rankings",
    "analytics_pigskin_rankings_history",
)
RANKING_MAX_VALUE_TABLES = (
    "analytics_pigskin_rankings_candidates",
    "analytics_player_weekly_truth",
)
SCORING_PROFILE_LABELS = {
    "ppr": "PPR",
    "standard": "Standard",
    "gng_keeper": "GNG Keeper",
}
LLM_ADJUSTMENT_RULES = {
    "NO_ADJUSTMENT": {"max_movement": 0},
    "CURRENT_ROLE_UPGRADE": {"min_movement": 1, "max_movement": 3},
    "CURRENT_ROLE_DOWNGRADE": {"min_movement": -8, "max_movement": -1},
    "ROOKIE_CONTEXT": {"min_movement": -3, "max_movement": 3},
    "INJURY_1_2": {"min_movement": -2, "max_movement": -1, "games_min": 1, "games_max": 2},
    "INJURY_3_5": {"min_movement": -5, "max_movement": -1, "games_min": 3, "games_max": 5},
    "INJURY_6_8": {"min_movement": -10, "max_movement": -1, "games_min": 6, "games_max": 8},
    "INJURY_9_PLUS": {"min_movement": -15, "max_movement": -1, "games_min": 9, "games_max": 17},
    "INJURY_UNCERTAIN": {"max_movement": 0},
    "ORDER_REBALANCE": {"min_movement": -15, "max_movement": 15, "application_only": True},
}
MAX_ADJUSTMENT_SHARE = 0.15
MAX_TOTAL_REQUESTED_MOVEMENT = 12


def scoring_profile_label(scoring_profile_id):
    return SCORING_PROFILE_LABELS.get(str(scoring_profile_id), str(scoring_profile_id).replace("_", " ").title())


def parse_positions(value):
    positions = [item.strip().upper() for item in value.split(",") if item.strip()]
    invalid = [position for position in positions if position not in VALID_POSITIONS]
    if invalid:
        raise ValueError(f"Unsupported positions: {', '.join(invalid)}")
    return positions or list(VALID_POSITIONS)


def get_position_limit(position, override):
    if override:
        return int(override)
    return DEFAULT_POSITION_LIMITS[position]


def fetch_candidates(client, dataset_id, position, limit, scoring_profile_id=DEFAULT_SCORING_PROFILE_ID):
    query = f"""
    SELECT
        *
    FROM `{client.project}.{dataset_id}.analytics_pigskin_rankings_candidates`
    WHERE position = @position
      AND scoring_profile_id = @scoring_profile_id
    ORDER BY rank ASC, ranking_score DESC, sleeper_search_rank ASC
    LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("position", "STRING", position),
        bigquery.ScalarQueryParameter("scoring_profile_id", "STRING", scoring_profile_id),
        bigquery.ScalarQueryParameter("limit", "INT64", int(limit)),
    ])
    return client.query(query, job_config=job_config).result().to_dataframe()


def fetch_generation_context(client, dataset_id):
    query = f"""
    SELECT
        MAX(season) AS season
    FROM `{client.project}.{dataset_id}.analytics_pigskin_rankings_candidates`
    """
    row = next(iter(client.query(query).result()), None)
    return {
        "season": getattr(row, "season", None) if row else None,
        "week": None,
    }


def get_code_version():
    for env_name in ("GIT_SHA", "COMMIT_SHA", "CODE_VERSION"):
        value = os.environ.get(env_name)
        if value:
            return value
    try:
        repo_root = Path(__file__).resolve().parents[1]
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            text=True,
            timeout=5,
        ).strip()
    except Exception:
        return "unknown"


def format_num(value, digits=2):
    if pd.isna(value):
        return "null"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "null"


def safe_float(value, fallback=0.0):
    if pd.isna(value):
        return fallback
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def safe_int(value, fallback=999999):
    if pd.isna(value):
        return fallback
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return fallback


def build_evidence_lines(df):
    lines = []
    for row in df.itertuples(index=False):
        lines.append(
            " | ".join([
                f"id={row.player_id}",
                f"name={row.player_name}",
                f"team={row.current_team}",
                f"sleeper_team={row.sleeper_team}",
                f"sleeper_active={row.sleeper_active}",
                f"sleeper_status={row.sleeper_status}",
                f"depth_position={row.sleeper_depth_chart_position}",
                f"depth={row.sleeper_depth_chart_order}",
                f"candidate_rank={row.rank}",
                f"candidate_score={format_num(row.ranking_score)}",
                f"candidate_rationale={getattr(row, 'rank_rationale', '')}",
                f"raw_score={format_num(row.raw_ranking_score)}",
                f"depth_penalty={format_num(row.depth_chart_penalty)}",
                f"profile_pts_pg={format_num(getattr(row, 'avg_profile_points', row.avg_ppr))}",
                f"ppr_pg={format_num(row.avg_ppr)}",
                f"grade={format_num(row.avg_grade)}",
                f"opp={format_num(row.avg_opportunity)}",
                f"eff={format_num(row.avg_efficiency)}",
                f"epa_per_opp={format_num(row.avg_epa_per_opportunity, 3)}",
                f"season_epa={format_num(row.season_total_epa)}",
                f"season_pass_epa={format_num(row.season_passing_epa)}",
                f"season_rush_epa={format_num(row.season_rushing_epa)}",
                f"season_rec_epa={format_num(row.season_receiving_epa)}",
                f"role_quality={format_num(row.avg_role_quality)}",
                f"fragility={format_num(row.avg_role_fragility)}",
                f"wopr={format_num(row.avg_wopr, 3)}",
                f"wopr_hist={format_num(row.latest_season_wopr, 3)}/{format_num(row.previous_season_wopr, 3)}/{format_num(row.two_years_ago_wopr, 3)}",
                f"target_share={format_num(row.avg_target_share, 3)}",
                f"target_share_hist={format_num(row.latest_season_target_share, 3)}/{format_num(row.previous_season_target_share, 3)}",
                f"carry_share={format_num(row.avg_carry_share, 3)}",
                f"carry_share_hist={format_num(row.latest_season_carry_share, 3)}/{format_num(row.previous_season_carry_share, 3)}",
                f"ppr_hist={format_num(row.latest_season_ppr)}/{format_num(row.previous_season_ppr)}",
                f"risk={row.risk_flags}",
            ])
        )
    return "\n".join(lines)


def build_prompt(position, df, ranking_version, scoring_profile_id=DEFAULT_SCORING_PROFILE_ID):
    profile_label = scoring_profile_label(scoring_profile_id)
    tier_contract = {
        "QB": "elite QB1, QB1, QB2 or streamer, backup or handcuff, bench or watchlist",
        "RB": "elite, front-line starter, starter, flex or matchup, deep or watchlist",
        "WR": "elite, front-line starter, starter, flex or matchup, deep or watchlist",
        "TE": "elite, front-line starter, starter, flex or matchup, deep or watchlist",
    }[position]
    evidence = build_evidence_lines(df)
    player_count = len(df)
    return f"""
You are Pigskin, the analytical co-host for AI vs Vibes.
    You are generating the official 2026 {profile_label} {position} rankings for the show.

This is not a vibes list and not a popularity list. The candidate board is the default order.
You are an exception-repair layer, not a second ranking formula. The candidate board is authoritative. Request a movement only when current source-backed context identifies something the deterministic formula cannot know, such as a verified current-role change, a rookie-context exception, or expected regular-season games missed.

Hard rules:
1. Rank every listed player exactly once.
2. Use each `id` exactly as provided.
3. Return ranks 1 through {player_count} with no gaps and no ties.
4. Current Sleeper role is a hard constraint. If `sleeper_active` is false, `sleeper_team` is null, or status is not Active/ACT, bury the player as watchlist material and flag the stale roster problem.
5. Do not rank a backup QB as a normal QB1. If `depth` is greater than 1, the player must be a backup or handcuff and should rank behind every current QB1 with a credible sample unless the evidence contains an obvious current starter path.
6. Do not put backup QBs in elite QB1 or QB1 tiers. A player can be talented and still be a fantasy bench stash if the role says bench.
7. Do not reinterpret formula metrics, sustainability, efficiency, touchdown regression, age, or opportunity. The deterministic formula already owns those judgments.
8. Valid model adjustment codes are: NO_ADJUSTMENT, CURRENT_ROLE_UPGRADE, CURRENT_ROLE_DOWNGRADE, ROOKIE_CONTEXT, INJURY_1_2, INJURY_3_5, INJURY_6_8, INJURY_9_PLUS, INJURY_UNCERTAIN. ORDER_REBALANCE is application-only and must never be returned.
9. Current-role upgrades are limited to three ranks. Current-role downgrades are limited to eight. Rookie context is limited to three ranks in either direction. Injury adjustments can only lower a player: one to two estimated missed regular-season games permits two ranks, three to five permits five, six to eight permits ten, and nine or more permits fifteen.
10. Request no more than {max(3, math.ceil(player_count * MAX_ADJUSTMENT_SHARE))} substantive adjustments. The sum of absolute requested movements cannot exceed {MAX_TOTAL_REQUESTED_MOVEMENT}.
13. Use an injury adjustment only when the supplied evidence explicitly states an estimated regular-season games-missed count. A Sleeper injury status alone is not enough. If injury information is unresolved, use INJURY_UNCERTAIN and do not move the player for injury.
12. Preseason Questionable status alone has zero rank effect. Use INJURY_UNCERTAIN with requested_rank_delta 0 if it deserves a visible warning.
13. NO_ADJUSTMENT and INJURY_UNCERTAIN require requested_rank_delta 0. Every other request must have non-empty adjustment detail and evidence copied from supplied fields.

Allowed tiers for {position}: {tier_contract}.

Return strict JSON only. Do not include markdown. The JSON shape must be:
{{
  "ranking_version": "{ranking_version}",
  "position": "{position}",
  "rankings": [
    {{
      "player_id": "exact id from evidence",
      "requested_rank_delta": 0,
      "tier": "one allowed tier",
      "adjustment_code": "one approved code",
      "adjustment_detail": "brief source-backed explanation of the movement, or no adjustment",
      "adjustment_evidence": "specific supplied metrics or current-role fields used",
      "estimated_regular_season_games_missed": null,
      "pigskin_verdict": "one sharp sentence",
      "rank_rationale": "one or two evidence-heavy sentences citing the strongest metrics",
      "risk_flags": "semicolon-separated analytical risks, or no major Pigskin ranking flag",
      "what_would_change_mind": "specific evidence that would move the rank"
    }}
  ]
}}

Do not replace the candidate score. The application preserves it as the deterministic score and records your rank overlay separately.

Evidence:
{evidence}
"""


def extract_json_object(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def call_gemini(api_key, model_name, prompt):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        temperature=0.15,
        response_mime_type="application/json",
    )
    last_error = None
    for attempt in range(1, 4):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            return extract_json_object(response.text)
        except Exception as ex:
            last_error = ex
            if attempt == 3:
                break
            sleep_for = 5 * attempt
            logger.warning("Gemini ranking call failed on attempt %s. Retrying in %s seconds. Error: %s", attempt, sleep_for, ex)
            time.sleep(sleep_for)
    raise last_error


def normalize_model_rankings(position, candidates_df, model_payload, ranking_version, model_name, run_metadata):
    candidate_by_id = {str(row.player_id): row for row in candidates_df.itertuples(index=False)}
    model_rows = model_payload.get("rankings") or []
    returned_ids = [str(item.get("player_id", "")).strip() for item in model_rows]
    missing_ids = [player_id for player_id in candidate_by_id if player_id not in returned_ids]
    if missing_ids:
        raise ValueError(f"{position} model omitted {len(missing_ids)} candidates: {', '.join(missing_ids[:8])}")
    seen = set()
    normalized = []

    for item in model_rows:
        player_id = str(item.get("player_id", "")).strip()
        if player_id not in candidate_by_id:
            raise ValueError(f"{position} model returned unknown player_id {player_id!r}.")
        if player_id in seen:
            raise ValueError(f"{position} model returned duplicate player_id {player_id!r}.")
        seen.add(player_id)
        candidate = candidate_by_id[player_id]._asdict()
        row = build_final_row(candidate, item, ranking_version, model_name, run_metadata)
        row["_requested_rank_delta"] = safe_int(item.get("requested_rank_delta"), 0)
        row["llm_rank_delta"] = row["_requested_rank_delta"]
        validate_adjustment(row, requested=True)
        normalized.append(row)

    if len(normalized) != len(candidates_df):
        raise ValueError(f"{position} model returned {len(normalized)} rows for {len(candidates_df)} candidates.")

    substantive = [row for row in normalized if row["llm_adjustment_code"] not in {"NO_ADJUSTMENT", "INJURY_UNCERTAIN"}]
    max_adjustments = max(3, math.ceil(len(normalized) * MAX_ADJUSTMENT_SHARE))
    if len(substantive) > max_adjustments:
        raise ValueError(f"{position} model requested {len(substantive)} adjustments; maximum is {max_adjustments}.")
    total_requested = sum(abs(row["_requested_rank_delta"]) for row in substantive)
    if total_requested > MAX_TOTAL_REQUESTED_MOVEMENT:
        raise ValueError(
            f"{position} model requested {total_requested} total ranks of movement; "
            f"maximum is {MAX_TOTAL_REQUESTED_MOVEMENT}."
        )

    normalized.sort(key=lambda row: (
        safe_int(row.get("candidate_rank")) - row["_requested_rank_delta"],
        safe_int(row.get("candidate_rank")),
    ))
    for index, row in enumerate(normalized, start=1):
        row["rank"] = index
        row["llm_rank_delta"] = safe_int(row.get("candidate_rank")) - index
        if row["llm_adjustment_code"] in {"NO_ADJUSTMENT", "INJURY_UNCERTAIN"} and row["llm_rank_delta"] != 0:
            row["llm_adjustment_code"] = "ORDER_REBALANCE"
            row["llm_adjustment_detail"] = "Mechanical displacement caused by a separate coded repair."
            row["llm_adjustment_evidence"] = "application deterministic reorder"
        validate_adjustment(row)
        row.pop("_requested_rank_delta", None)
        row["is_active"] = True

    return normalized


def generate_position_rows(api_key, model_name, position, candidates_df, ranking_version, run_metadata):
    prompt = build_prompt(position, candidates_df, ranking_version, run_metadata["scoring_profile_id"])
    last_error = None
    for attempt in range(1, 4):
        try:
            payload = call_gemini(api_key, model_name, prompt)
            return normalize_model_rankings(position, candidates_df, payload, ranking_version, model_name, run_metadata)
        except Exception as ex:
            last_error = ex
            if attempt == 3:
                break
            sleep_for = 5 * attempt
            logger.warning(
                "%s ranking adjudication failed on attempt %s. Retrying in %s seconds. Error: %s",
                position,
                attempt,
                sleep_for,
                ex,
            )
            time.sleep(sleep_for)
    raise last_error


def build_final_row(candidate, model_item, ranking_version, model_name, run_metadata):
    adjudicated_at = datetime.now(timezone.utc)
    row = dict(candidate)
    row["model_run_id"] = run_metadata["model_run_id"]
    row["scoring_profile_id"] = run_metadata["scoring_profile_id"]
    row["league_type_id"] = run_metadata["league_type_id"]
    row["roster_format_id"] = run_metadata["roster_format_id"]
    row["feature_config_version_id"] = run_metadata["feature_config_version_id"]
    row["source_freshness_snapshot_id"] = run_metadata["source_freshness_snapshot_id"]
    row["candidate_rank"] = candidate.get("rank")
    row["candidate_ranking_score"] = candidate.get("ranking_score")
    row["rank"] = safe_int(candidate.get("rank"), 999999)
    row["ranking_version"] = ranking_version
    row["generated_at"] = adjudicated_at
    row["ranking_score"] = safe_float(candidate.get("ranking_score"))
    row["tier"] = str(model_item.get("tier") or candidate.get("tier") or "watchlist")
    row["pigskin_verdict"] = str(model_item.get("pigskin_verdict") or candidate.get("pigskin_verdict") or "")
    row["rank_rationale"] = str(model_item.get("rank_rationale") or candidate.get("rank_rationale") or "")
    row["risk_flags"] = str(model_item.get("risk_flags") or candidate.get("risk_flags") or "")
    row["what_would_change_mind"] = str(
        model_item.get("what_would_change_mind") or candidate.get("what_would_change_mind") or ""
    )
    row["model_name"] = model_name
    row["prompt_version"] = run_metadata["prompt_version"]
    row["rank_source"] = "llm_pigskin_adjudicated"
    row["llm_adjustment_code"] = str(model_item.get("adjustment_code") or "").strip().upper()
    row["llm_adjustment_detail"] = str(model_item.get("adjustment_detail") or "").strip()
    row["llm_adjustment_evidence"] = str(model_item.get("adjustment_evidence") or "").strip()
    row["llm_estimated_games_missed"] = parse_optional_int(model_item.get("estimated_regular_season_games_missed"))
    row["llm_rank_delta"] = safe_int(model_item.get("requested_rank_delta"), 0)
    row["adjudicated_at"] = adjudicated_at
    row["data_snapshot_label"] = f"{candidate.get('data_snapshot_label')}_llm"
    return row


def parse_optional_int(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError("estimated_regular_season_games_missed must be an integer or null.")


def validate_adjustment(row, *, requested=False):
    code = row.get("llm_adjustment_code")
    if code not in LLM_ADJUSTMENT_RULES:
        raise ValueError(f"Unsupported LLM adjustment code: {code!r}.")

    movement = row["llm_rank_delta"]
    rule = LLM_ADJUSTMENT_RULES[code]
    if requested and rule.get("application_only"):
        raise ValueError(f"{code} is application-only.")
    min_movement = rule.get("min_movement", 0)
    max_movement = rule["max_movement"]
    if not min_movement <= movement <= max_movement:
        raise ValueError(
            f"{code} permits rank movement from {min_movement} through {max_movement}; got {movement}."
        )

    games_missed = row.get("llm_estimated_games_missed")
    if "games_min" in rule:
        if games_missed is None or not rule["games_min"] <= games_missed <= rule["games_max"]:
            raise ValueError(
                f"{code} requires estimated_regular_season_games_missed from "
                f"{rule['games_min']} through {rule['games_max']}."
            )
    elif games_missed is not None:
        raise ValueError(f"{code} cannot include an estimated games-missed value.")

    injury_status = str(row.get("sleeper_injury_status") or "").strip().lower()
    if injury_status == "questionable" and code.startswith("INJURY_") and code != "INJURY_UNCERTAIN":
        raise ValueError("Preseason Questionable status cannot move a rank.")

    if code not in {"NO_ADJUSTMENT", "INJURY_UNCERTAIN"} and (
        not row.get("llm_adjustment_detail") or not row.get("llm_adjustment_evidence")
    ):
        raise ValueError(f"{code} requires adjustment detail and evidence.")


def ensure_history_table(client, final_table_id, history_table_id):
    final_table = client.get_table(final_table_id)
    try:
        history_table = client.get_table(history_table_id)
    except NotFound:
        table = bigquery.Table(history_table_id, schema=final_table.schema)
        client.create_table(table)
        return

    existing = {field.name for field in history_table.schema}
    missing_fields = [field for field in final_table.schema if field.name not in existing]
    if missing_fields:
        history_table.schema = list(history_table.schema) + missing_fields
        client.update_table(history_table, ["schema"])


def ranking_load_schema(client, final_table_id, history_table_id):
    for table_id in (history_table_id, final_table_id):
        try:
            table = client.get_table(table_id)
        except NotFound:
            continue
        if table.schema:
            return list(table.schema)
    return None


def write_rankings(client, dataset_id, rows):
    if not rows:
        raise RuntimeError("No Pigskin ranking rows were generated.")

    df = pd.DataFrame(rows)
    final_table_id = f"{client.project}.{dataset_id}.analytics_pigskin_rankings"
    history_table_id = f"{client.project}.{dataset_id}.analytics_pigskin_rankings_history"
    staging_table_id = f"{client.project}.{dataset_id}.analytics_pigskin_rankings_staging_{uuid.uuid4().hex}"
    load_schema = ranking_load_schema(client, final_table_id, history_table_id)
    positions = sorted({str(row["position"]) for row in rows if row.get("position")})
    scoring_profile_ids = sorted({str(row["scoring_profile_id"]) for row in rows if row.get("scoring_profile_id")})
    league_type_ids = sorted({str(row["league_type_id"]) for row in rows if row.get("league_type_id")})
    roster_format_ids = sorted({str(row["roster_format_id"]) for row in rows if row.get("roster_format_id")})
    if not positions or not scoring_profile_ids or not league_type_ids or not roster_format_ids:
        raise RuntimeError("Pigskin ranking rows must include position and profile scope fields.")
    if load_schema:
        df = df.reindex(columns=[field.name for field in load_schema])

    staging_job = client.load_table_from_dataframe(
        df,
        staging_table_id,
        job_config=bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_EMPTY,
            schema=load_schema,
        ),
    )
    staging_job.result()

    delete_sql, insert_sql = build_profile_aware_rankings_replace_sql(client.project, dataset_id, staging_table_id.split(".")[-1])
    query_parameters = [
        bigquery.ArrayQueryParameter("scoring_profile_ids", "STRING", scoring_profile_ids),
        bigquery.ArrayQueryParameter("league_type_ids", "STRING", league_type_ids),
        bigquery.ArrayQueryParameter("roster_format_ids", "STRING", roster_format_ids),
        bigquery.ArrayQueryParameter("positions", "STRING", positions),
    ]
    query_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
    try:
        client.query(delete_sql, job_config=query_config).result()
        client.query(insert_sql).result()
    finally:
        client.delete_table(staging_table_id, not_found_ok=True)

    ensure_history_table(client, final_table_id, history_table_id)
    history_job = client.load_table_from_dataframe(
        df,
        history_table_id,
        job_config=bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema=load_schema,
        ),
    )
    history_job.result()
    logger.info("Loaded %s LLM-authored Pigskin ranking rows.", len(df))


def build_profile_aware_rankings_replace_sql(project_id, dataset_id, staging_table_name):
    """Return a future-safe selected-profile replace plan for active rankings."""

    final_table_id = f"`{project_id}.{dataset_id}.analytics_pigskin_rankings`"
    staging_table_id = f"`{project_id}.{dataset_id}.{staging_table_name}`"
    delete_sql = f"""
    DELETE FROM {final_table_id} target_board
    WHERE EXISTS (
        SELECT 1
        FROM {staging_table_id} source_board
        WHERE target_board.scoring_profile_id = source_board.scoring_profile_id
          AND target_board.league_type_id = source_board.league_type_id
          AND target_board.roster_format_id = source_board.roster_format_id
          AND target_board.position = source_board.position
          AND target_board.scoring_profile_id IN UNNEST(@scoring_profile_ids)
          AND target_board.league_type_id IN UNNEST(@league_type_ids)
          AND target_board.roster_format_id IN UNNEST(@roster_format_ids)
          AND target_board.position IN UNNEST(@positions)
    )
    """.strip()
    insert_sql = f"""
    INSERT INTO {final_table_id}
    SELECT *
    FROM {staging_table_id}
    """.strip()
    return delete_sql, insert_sql


def build_candidate_historical_metrics_gap_query(project_id, dataset_id, scoring_profile_id=DEFAULT_SCORING_PROFILE_ID):
    return f"""
    SELECT
        candidate.position,
        candidate.player_id,
        candidate.player_name,
        candidate.current_team,
        candidate.sleeper_player_id,
        candidate.weekly_rows,
        COUNT(DISTINCT CONCAT(CAST(metrics.season AS STRING), '-', CAST(metrics.week AS STRING))) AS metric_week_count
    FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings_candidates` candidate
    JOIN `{project_id}.{dataset_id}.player_week_advanced_metrics` metrics
        ON metrics.player_id_internal = candidate.player_id
    WHERE candidate.scoring_profile_id = @scoring_profile_id
      AND COALESCE(candidate.weekly_rows, 0) = 0
    GROUP BY
        candidate.position,
        candidate.player_id,
        candidate.player_name,
        candidate.current_team,
        candidate.sleeper_player_id,
        candidate.weekly_rows
    HAVING metric_week_count > 0
    ORDER BY metric_week_count DESC, candidate.position, candidate.player_name
    """.strip()


def generate_rankings(
    dataset_id=DEFAULT_DATASET,
    project_id=None,
    model_name=DEFAULT_MODEL,
    model_version=DEFAULT_MODEL_VERSION,
    prompt_version=DEFAULT_PROMPT_VERSION,
    scoring_profile_id=DEFAULT_SCORING_PROFILE_ID,
    league_type_id=DEFAULT_LEAGUE_TYPE_ID,
    roster_format_id=DEFAULT_ROSTER_FORMAT_ID,
    feature_config_version_id=DEFAULT_FEATURE_CONFIG_VERSION_ID,
    positions=None,
    position_limit=None,
    refresh_sleeper=False,
    dry_run=False,
):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required to generate LLM-authored Pigskin rankings.")

    project_id = project_id or get_bigquery_project()
    client = bigquery.Client(project=project_id)

    if refresh_sleeper:
        logger.info("Refreshing Sleeper current player map before ranking generation.")
        load_realtime_news()

    logger.info("Materializing Pigskin ranking candidate evidence.")
    materialize_pigskin_rankings(
        client,
        dataset_id=dataset_id,
        dry_run=False,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )

    ranking_version = f"pigskin-llm-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    generation_context = fetch_generation_context(client, dataset_id)
    model_run_id = None
    try:
        try:
            source_freshness_snapshot_id = create_source_freshness_snapshot(
                client=client,
                dataset_id=dataset_id,
                source_table_names=RANKING_SOURCE_TABLES,
                max_value_table_names=RANKING_MAX_VALUE_TABLES,
            )
        except Exception as ex:
            raise RuntimeError(
                "Failed to create Pigskin rankings source freshness snapshot. "
                "Confirm BigQuery migrations through 0003 have been applied."
            ) from ex

        try:
            model_run_id = create_model_run(
                client=client,
                dataset_id=dataset_id,
                run_type="pigskin_rankings",
                model_name=model_name,
                model_version=model_version,
                prompt_version=prompt_version,
                code_version=get_code_version(),
                season=generation_context.get("season"),
                week=generation_context.get("week"),
                scoring_profile_id=scoring_profile_id,
                league_type_id=league_type_id,
                roster_format_id=roster_format_id,
                feature_config_version_id=feature_config_version_id,
                source_freshness_snapshot_id=source_freshness_snapshot_id,
                created_by="generate_pigskin_rankings",
                notes=f"ranking_version={ranking_version}",
            )
        except Exception as ex:
            raise RuntimeError(
                "Failed to create Pigskin ranking model_run. "
                "Confirm BigQuery migrations through 0003 have been applied."
            ) from ex

        run_metadata = {
            "model_run_id": model_run_id,
            "scoring_profile_id": scoring_profile_id,
            "league_type_id": league_type_id,
            "roster_format_id": roster_format_id,
            "feature_config_version_id": feature_config_version_id,
            "source_freshness_snapshot_id": source_freshness_snapshot_id,
            "prompt_version": prompt_version,
        }

        final_rows = []
        for position in positions or list(VALID_POSITIONS):
            limit = get_position_limit(position, position_limit)
            candidates_df = fetch_candidates(client, dataset_id, position, limit, scoring_profile_id=scoring_profile_id)
            if candidates_df.empty:
                logger.warning("No candidate rows found for %s.", position)
                continue

            logger.info("Generating %s rankings for %s candidates with %s.", position, len(candidates_df), model_name)
            final_rows.extend(generate_position_rows(api_key, model_name, position, candidates_df, ranking_version, run_metadata))

        if dry_run:
            logger.info("Dry run generated %s ranking rows. BigQuery final tables were not changed.", len(final_rows))
            mark_model_run_complete(
                model_run_id,
                client=client,
                dataset_id=dataset_id,
                notes=f"dry_run=true; ranking_version={ranking_version}; row_count={len(final_rows)}",
            )
            return ranking_version, len(final_rows)

        write_rankings(client, dataset_id, final_rows)
        mark_model_run_complete(
            model_run_id,
            client=client,
            dataset_id=dataset_id,
            notes=f"ranking_version={ranking_version}; row_count={len(final_rows)}",
        )
        logger.info("Pigskin LLM rankings generated. ranking_version=%s model_run_id=%s", ranking_version, model_run_id)
        return ranking_version, len(final_rows)
    except Exception as ex:
        if model_run_id:
            try:
                mark_model_run_failed(
                    model_run_id,
                    str(ex),
                    client=client,
                    dataset_id=dataset_id,
                    notes=f"ranking_version={ranking_version}",
                )
            except Exception:
                logger.exception("Failed to mark Pigskin ranking model_run failed.")
        raise


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="Generate LLM-authored Pigskin rankings from BigQuery candidate evidence.")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="BigQuery dataset name.")
    parser.add_argument("--project", default=get_bigquery_project(), help="BigQuery project ID.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini model name.")
    parser.add_argument("--model-version", default=DEFAULT_MODEL_VERSION, help="Pigskin ranking model version label.")
    parser.add_argument("--prompt-version", default=DEFAULT_PROMPT_VERSION, help="Pigskin ranking prompt version label.")
    parser.add_argument("--scoring-profile-id", default=DEFAULT_SCORING_PROFILE_ID, help="Scoring profile ID for model_run metadata.")
    parser.add_argument("--league-type-id", default=DEFAULT_LEAGUE_TYPE_ID, help="League type ID for model_run metadata.")
    parser.add_argument("--roster-format-id", default=DEFAULT_ROSTER_FORMAT_ID, help="Roster format ID for model_run metadata.")
    parser.add_argument("--feature-config-version-id", default=DEFAULT_FEATURE_CONFIG_VERSION_ID, help="Feature config version ID for model_run metadata.")
    parser.add_argument("--positions", default="QB,RB,WR,TE", help="Comma-separated positions to generate.")
    parser.add_argument("--position-limit", type=int, help="Override candidate limit per position.")
    parser.add_argument(
        "--refresh-sleeper",
        action="store_true",
        help="Refresh Sleeper current player status before generating rankings.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run candidate materialization and Gemini adjudication without writing final ranking tables.",
    )
    args = parser.parse_args()

    version, row_count = generate_rankings(
        dataset_id=args.dataset,
        project_id=args.project,
        model_name=args.model,
        model_version=args.model_version,
        prompt_version=args.prompt_version,
        scoring_profile_id=args.scoring_profile_id,
        league_type_id=args.league_type_id,
        roster_format_id=args.roster_format_id,
        feature_config_version_id=args.feature_config_version_id,
        positions=parse_positions(args.positions),
        position_limit=args.position_limit,
        refresh_sleeper=args.refresh_sleeper,
        dry_run=args.dry_run,
    )
    print(f"Generated {row_count} LLM-authored Pigskin rankings. ranking_version={version}")


if __name__ == "__main__":
    main()
