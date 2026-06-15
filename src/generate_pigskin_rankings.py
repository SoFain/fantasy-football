import argparse
import json
import logging
import os
import re
import time
from datetime import datetime, timezone

import pandas as pd
from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.ingest_news import load_realtime_news
from src.load import get_bigquery_project
from src.materialize import materialize_pigskin_rankings


logger = logging.getLogger("generate_pigskin_rankings")

DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
DEFAULT_POSITION_LIMITS = {
    "QB": 45,
    "RB": 80,
    "WR": 100,
    "TE": 60,
}
VALID_POSITIONS = tuple(DEFAULT_POSITION_LIMITS)


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


def fetch_candidates(client, dataset_id, position, limit):
    query = f"""
    SELECT
        *
    FROM `{client.project}.{dataset_id}.analytics_pigskin_rankings_candidates`
    WHERE position = @position
    ORDER BY rank ASC, ranking_score DESC, sleeper_search_rank ASC
    LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("position", "STRING", position),
        bigquery.ScalarQueryParameter("limit", "INT64", int(limit)),
    ])
    return client.query(query, job_config=job_config).result().to_dataframe()


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
                f"raw_score={format_num(row.raw_ranking_score)}",
                f"depth_penalty={format_num(row.depth_chart_penalty)}",
                f"ppr_pg={format_num(row.avg_ppr)}",
                f"grade={format_num(row.avg_grade)}",
                f"opp={format_num(row.avg_opportunity)}",
                f"eff={format_num(row.avg_efficiency)}",
                f"epa_per_opp={format_num(row.avg_epa_per_opportunity, 3)}",
                f"season_epa={format_num(row.season_total_epa)}",
                f"role_quality={format_num(row.avg_role_quality)}",
                f"fragility={format_num(row.avg_role_fragility)}",
                f"wopr={format_num(row.avg_wopr, 3)}",
                f"target_share={format_num(row.avg_target_share, 3)}",
                f"carry_share={format_num(row.avg_carry_share, 3)}",
                f"risk={row.risk_flags}",
            ])
        )
    return "\n".join(lines)


def build_prompt(position, df, ranking_version):
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
You are generating the official 2026 PPR {position} rankings for the show.

This is not a vibes list and not a popularity list. Use the candidate board as evidence, not as an order you must obey.
The SQL rank is only `candidate_rank`. It is not your final ranking.
Your job is to adjudicate the board with deeper analytics: opportunity quality, EPA, WOPR or target share, carry share, role quality, role fragility, current Sleeper team, current Sleeper depth chart, and whether the prior fantasy output is sustainable.

Hard rules:
1. Rank every listed player exactly once.
2. Use each `id` exactly as provided.
3. Return ranks 1 through {player_count} with no gaps and no ties.
4. Current Sleeper role is a hard constraint. If `sleeper_active` is false, `sleeper_team` is null, or status is not Active/ACT, bury the player as watchlist material and flag the stale roster problem.
5. Do not rank a backup QB as a normal QB1. If `depth` is greater than 1, the player must be a backup or handcuff and should rank behind every current QB1 with a credible sample unless the evidence contains an obvious current starter path.
6. Do not put backup QBs in elite QB1 or QB1 tiers. A player can be talented and still be a fantasy bench stash if the role says bench.
7. Penalize players with no stable current role, high fragility, bad EPA, or volume that looks like box-score cosplay.
8. Prefer repeatable role and efficiency over touchdown spikes.
9. For WR and TE, WOPR and target share matter. For RB, carry share and pass-game role matter. For QB, rushing role, EPA, depth chart, and volume matter.
10. Be ruthless, but do not invent facts not present in the evidence.

Allowed tiers for {position}: {tier_contract}.

Return strict JSON only. Do not include markdown. The JSON shape must be:
{{
  "ranking_version": "{ranking_version}",
  "position": "{position}",
  "rankings": [
    {{
      "player_id": "exact id from evidence",
      "rank": 1,
      "tier": "one allowed tier",
      "ranking_score": 0.0,
      "pigskin_verdict": "one sharp sentence",
      "rank_rationale": "one or two evidence-heavy sentences citing the strongest metrics",
      "risk_flags": "semicolon-separated analytical risks, or no major Pigskin ranking flag",
      "what_would_change_mind": "specific evidence that would move the rank"
    }}
  ]
}}

Use ranking_score as your final 0-100 conviction score after your adjudication, not the candidate score.

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


def normalize_model_rankings(position, candidates_df, model_payload, ranking_version, model_name):
    candidate_by_id = {str(row.player_id): row for row in candidates_df.itertuples(index=False)}
    model_rows = model_payload.get("rankings") or []
    seen = set()
    normalized = []

    for item in sorted(model_rows, key=lambda row: safe_int(row.get("rank"))):
        player_id = str(item.get("player_id", "")).strip()
        if player_id not in candidate_by_id:
            raise ValueError(f"{position} model returned unknown player_id {player_id!r}.")
        if player_id in seen:
            raise ValueError(f"{position} model returned duplicate player_id {player_id!r}.")
        seen.add(player_id)
        candidate = candidate_by_id[player_id]._asdict()
        normalized.append(build_final_row(candidate, item, ranking_version, model_name))

    missing_ids = [str(row.player_id) for row in candidates_df.itertuples(index=False) if str(row.player_id) not in seen]
    if missing_ids:
        raise ValueError(f"{position} model omitted {len(missing_ids)} candidates: {', '.join(missing_ids[:8])}")

    if len(normalized) != len(candidates_df):
        raise ValueError(f"{position} model returned {len(normalized)} rows for {len(candidates_df)} candidates.")

    for index, row in enumerate(normalized, start=1):
        row["rank"] = index
        row["is_active"] = True

    return normalized


def generate_position_rows(api_key, model_name, position, candidates_df, ranking_version):
    prompt = build_prompt(position, candidates_df, ranking_version)
    last_error = None
    for attempt in range(1, 4):
        try:
            payload = call_gemini(api_key, model_name, prompt)
            return normalize_model_rankings(position, candidates_df, payload, ranking_version, model_name)
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


def build_final_row(candidate, model_item, ranking_version, model_name):
    adjudicated_at = datetime.now(timezone.utc)
    row = dict(candidate)
    row["candidate_rank"] = candidate.get("rank")
    row["candidate_ranking_score"] = candidate.get("ranking_score")
    row["rank"] = safe_int(model_item.get("rank"), 999999)
    row["ranking_version"] = ranking_version
    row["generated_at"] = adjudicated_at
    row["ranking_score"] = safe_float(model_item.get("ranking_score"), safe_float(candidate.get("ranking_score")))
    row["tier"] = str(model_item.get("tier") or candidate.get("tier") or "watchlist")
    row["pigskin_verdict"] = str(model_item.get("pigskin_verdict") or candidate.get("pigskin_verdict") or "")
    row["rank_rationale"] = str(model_item.get("rank_rationale") or candidate.get("rank_rationale") or "")
    row["risk_flags"] = str(model_item.get("risk_flags") or candidate.get("risk_flags") or "")
    row["what_would_change_mind"] = str(
        model_item.get("what_would_change_mind") or candidate.get("what_would_change_mind") or ""
    )
    row["model_name"] = model_name
    row["prompt_version"] = "pigskin-rankings-llm-v2"
    row["rank_source"] = "llm_pigskin_adjudicated"
    row["adjudicated_at"] = adjudicated_at
    row["data_snapshot_label"] = f"{candidate.get('data_snapshot_label')}_llm"
    return row


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


def write_rankings(client, dataset_id, rows):
    if not rows:
        raise RuntimeError("No Pigskin ranking rows were generated.")

    df = pd.DataFrame(rows)
    final_table_id = f"{client.project}.{dataset_id}.analytics_pigskin_rankings"
    history_table_id = f"{client.project}.{dataset_id}.analytics_pigskin_rankings_history"

    final_job = client.load_table_from_dataframe(
        df,
        final_table_id,
        job_config=bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE),
    )
    final_job.result()

    ensure_history_table(client, final_table_id, history_table_id)
    history_job = client.load_table_from_dataframe(
        df,
        history_table_id,
        job_config=bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND),
    )
    history_job.result()
    logger.info("Loaded %s LLM-authored Pigskin ranking rows.", len(df))


def generate_rankings(
    dataset_id=DEFAULT_DATASET,
    project_id=None,
    model_name=DEFAULT_MODEL,
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
    materialize_pigskin_rankings(client, dataset_id=dataset_id, dry_run=False)

    ranking_version = f"pigskin-llm-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    final_rows = []
    for position in positions or list(VALID_POSITIONS):
        limit = get_position_limit(position, position_limit)
        candidates_df = fetch_candidates(client, dataset_id, position, limit)
        if candidates_df.empty:
            logger.warning("No candidate rows found for %s.", position)
            continue

        logger.info("Generating %s rankings for %s candidates with %s.", position, len(candidates_df), model_name)
        final_rows.extend(generate_position_rows(api_key, model_name, position, candidates_df, ranking_version))

    if dry_run:
        logger.info("Dry run generated %s ranking rows. BigQuery final tables were not changed.", len(final_rows))
        return ranking_version, len(final_rows)

    write_rankings(client, dataset_id, final_rows)
    logger.info("Pigskin LLM rankings generated. ranking_version=%s", ranking_version)
    return ranking_version, len(final_rows)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="Generate LLM-authored Pigskin rankings from BigQuery candidate evidence.")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="BigQuery dataset name.")
    parser.add_argument("--project", default=get_bigquery_project(), help="BigQuery project ID.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini model name.")
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
        positions=parse_positions(args.positions),
        position_limit=args.position_limit,
        refresh_sleeper=args.refresh_sleeper,
        dry_run=args.dry_run,
    )
    print(f"Generated {row_count} LLM-authored Pigskin rankings. ranking_version={version}")


if __name__ == "__main__":
    main()
