import argparse
import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from urllib.parse import urlparse

import pandas as pd
import google.auth
from google.auth.transport.requests import AuthorizedSession
from google.cloud import bigquery

from src.load import get_bigquery_project


logger = logging.getLogger("verify_player_context")

USAGE_SERVICE = "external_verification_search"
DEFAULT_PROVIDER = "vertex_ai_search"
DEFAULT_DAILY_LIMIT = 25
HARD_DAILY_LIMIT = 99
DEFAULT_MAX_RESULTS = 3
HARD_MAX_RESULTS = 5


def bounded_int_env(name, default_value, min_value, max_value):
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default_value
    try:
        parsed_value = int(raw_value)
    except ValueError:
        logger.warning("Ignoring invalid integer env %s=%r. Using %s.", name, raw_value, default_value)
        return default_value
    return max(min_value, min(parsed_value, max_value))


def get_daily_limit():
    return bounded_int_env("EXTERNAL_SEARCH_DAILY_LIMIT", DEFAULT_DAILY_LIMIT, 0, HARD_DAILY_LIMIT)


def get_default_max_results():
    return bounded_int_env("EXTERNAL_SEARCH_MAX_RESULTS", DEFAULT_MAX_RESULTS, 1, HARD_MAX_RESULTS)


def get_provider():
    return os.environ.get("EXTERNAL_SEARCH_PROVIDER", DEFAULT_PROVIDER).strip().lower()


def ensure_usage_table(client, dataset_name):
    client.query(f"""
        CREATE TABLE IF NOT EXISTS `{client.project}.{dataset_name}.analytics_api_usage_daily` (
            usage_date DATE NOT NULL,
            service STRING NOT NULL,
            request_count INT64 NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
    """).result()


def ensure_results_table(client, dataset_name):
    table_id = f"{client.project}.{dataset_name}.analytics_external_context_search_results"
    client.query(f"""
        CREATE TABLE IF NOT EXISTS `{table_id}` (
            search_id STRING NOT NULL,
            searched_at TIMESTAMP NOT NULL,
            usage_date DATE NOT NULL,
            player_name STRING NOT NULL,
            query STRING NOT NULL,
            result_rank INT64 NOT NULL,
            title STRING,
            link STRING,
            display_link STRING,
            snippet STRING,
            source_type STRING NOT NULL
        )
    """).result()
    client.query(f"ALTER TABLE `{table_id}` ADD COLUMN IF NOT EXISTS provider STRING").result()
    client.query(f"ALTER TABLE `{table_id}` ADD COLUMN IF NOT EXISTS source_name STRING").result()
    client.query(f"ALTER TABLE `{table_id}` ADD COLUMN IF NOT EXISTS raw_result_json STRING").result()


def get_request_count(client, dataset_name, service, usage_date):
    ensure_usage_table(client, dataset_name)
    rows = list(client.query(
        f"""
        SELECT request_count
        FROM `{client.project}.{dataset_name}.analytics_api_usage_daily`
        WHERE usage_date = @usage_date AND service = @service
        """,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("usage_date", "DATE", usage_date),
                bigquery.ScalarQueryParameter("service", "STRING", service),
            ]
        ),
    ).result())
    return rows[0].request_count if rows else 0


def increment_request_count(client, dataset_name, service, usage_date):
    ensure_usage_table(client, dataset_name)
    client.query(
        f"""
        MERGE `{client.project}.{dataset_name}.analytics_api_usage_daily` target
        USING (
            SELECT
                @usage_date AS usage_date,
                @service AS service,
                1 AS request_count,
                CURRENT_TIMESTAMP() AS updated_at
        ) source
        ON target.usage_date = source.usage_date AND target.service = source.service
        WHEN MATCHED THEN
            UPDATE SET
                request_count = target.request_count + 1,
                updated_at = source.updated_at
        WHEN NOT MATCHED THEN
            INSERT (usage_date, service, request_count, updated_at)
            VALUES (source.usage_date, source.service, source.request_count, source.updated_at)
        """,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("usage_date", "DATE", usage_date),
                bigquery.ScalarQueryParameter("service", "STRING", service),
            ]
        ),
    ).result()


def build_default_query(player_name, team=None, season=None):
    parts = [
        f'"{player_name}"',
        "NFL",
        "(injury OR injured OR trade OR roster OR quarterback OR coordinator OR offensive line)",
    ]
    if team:
        parts.append(team)
    if season:
        parts.append(str(season))
    return " ".join(parts)


def build_vertex_serving_config(project_id):
    explicit_serving_config = os.environ.get("VERTEX_AI_SEARCH_SERVING_CONFIG")
    if explicit_serving_config:
        return explicit_serving_config.strip()

    engine_id = os.environ.get("VERTEX_AI_SEARCH_ENGINE_ID")
    if not engine_id:
        raise RuntimeError(
            "External verification is configured for Vertex AI Search, but VERTEX_AI_SEARCH_SERVING_CONFIG "
            "or VERTEX_AI_SEARCH_ENGINE_ID is missing."
        )

    location = os.environ.get("VERTEX_AI_SEARCH_LOCATION", "global")
    collection_id = os.environ.get("VERTEX_AI_SEARCH_COLLECTION", "default_collection")
    serving_config_id = os.environ.get("VERTEX_AI_SEARCH_SERVING_CONFIG_ID", "default_search")
    return (
        f"projects/{project_id}/locations/{location}/collections/{collection_id}"
        f"/engines/{engine_id}/servingConfigs/{serving_config_id}"
    )


def first_value(*values):
    for value in values:
        if value:
            return value
    return None


def first_snippet(derived_data):
    snippets = derived_data.get("snippets") or []
    if snippets:
        return first_value(snippets[0].get("snippet"), snippets[0].get("htmlSnippet"))

    extractive_answers = derived_data.get("extractive_answers") or derived_data.get("extractiveAnswers") or []
    if extractive_answers:
        return first_value(extractive_answers[0].get("content"), extractive_answers[0].get("pageContent"))

    return first_value(derived_data.get("snippet"), derived_data.get("description"))


def display_link_from_url(url):
    if not url:
        return None
    return urlparse(url).netloc or None


def normalize_vertex_result(result):
    document = result.get("document") or {}
    derived_data = document.get("derivedStructData") or {}
    struct_data = document.get("structData") or {}
    link = first_value(
        derived_data.get("link"),
        derived_data.get("uri"),
        struct_data.get("link"),
        struct_data.get("uri"),
        document.get("uri"),
    )
    title = first_value(
        derived_data.get("title"),
        derived_data.get("htmlTitle"),
        struct_data.get("title"),
        document.get("id"),
        document.get("name"),
    )
    return {
        "title": title,
        "link": link,
        "display_link": display_link_from_url(link),
        "snippet": first_snippet(derived_data),
        "source_name": document.get("name"),
        "raw_result_json": json.dumps(result, ensure_ascii=True, sort_keys=True)[:60000],
    }


def search_vertex_ai(query, max_results, project_id):
    serving_config = build_vertex_serving_config(project_id)
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    session = AuthorizedSession(credentials)
    response = session.post(
        f"https://discoveryengine.googleapis.com/v1/{serving_config}:search",
        json={
            "query": query,
            "pageSize": max_results,
            "safeSearch": True,
            "userPseudoId": "ai-vs-vibes-dashboard",
            "contentSearchSpec": {
                "snippetSpec": {
                    "returnSnippet": True
                }
            },
        },
        timeout=30,
    )
    response.raise_for_status()
    return [normalize_vertex_result(result) for result in response.json().get("results", [])]


def search_external_context(query, max_results, project_id):
    provider = get_provider()
    if provider == "disabled":
        raise RuntimeError("External verification is disabled by EXTERNAL_SEARCH_PROVIDER=disabled.")
    if provider == "google_custom_search":
        raise RuntimeError("The legacy search provider is deprecated for this project. Use Vertex AI Search instead.")
    if provider != "vertex_ai_search":
        raise RuntimeError(f"Unsupported external verification provider: {provider}")

    return provider, search_vertex_ai(query, max_results=max_results, project_id=project_id)


def store_results(client, dataset_name, provider, player_name, query, items):
    ensure_results_table(client, dataset_name)
    searched_at = datetime.now(timezone.utc)
    query_hash = hashlib.sha256(f"{player_name}|{query}|{provider}".encode("utf-8")).hexdigest()[:12]
    search_id = f"{searched_at.strftime('%Y%m%dT%H%M%S')}_{query_hash}"
    rows = []
    for index, item in enumerate(items, start=1):
        rows.append({
            "search_id": search_id,
            "searched_at": searched_at,
            "usage_date": searched_at.date(),
            "player_name": player_name,
            "query": query,
            "result_rank": index,
            "title": item.get("title"),
            "link": item.get("link"),
            "display_link": item.get("display_link"),
            "snippet": item.get("snippet"),
            "source_type": provider,
            "provider": provider,
            "source_name": item.get("source_name"),
            "raw_result_json": item.get("raw_result_json"),
        })

    if not rows:
        logger.info("No external verification results returned for query: %s", query)
        return 0

    df = pd.DataFrame(rows)
    table_id = f"{client.project}.{dataset_name}.analytics_external_context_search_results"
    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND),
    )
    job.result()
    return len(rows)


def verify_player_context(player_name, query=None, team=None, season=None, max_results=None, dataset_name="fantasy_football_brain"):
    client = bigquery.Client(project=get_bigquery_project())
    daily_limit = get_daily_limit()
    if daily_limit <= 0:
        raise RuntimeError("External verification daily limit is 0. Set EXTERNAL_SEARCH_DAILY_LIMIT above 0 to enable it.")

    usage_date = datetime.now(timezone.utc).date()
    current_count = get_request_count(client, dataset_name, USAGE_SERVICE, usage_date)
    if current_count >= daily_limit:
        raise RuntimeError(
            f"External verification daily limit reached: {current_count}/{daily_limit} requests used today."
        )

    final_max_results = max(1, min(max_results or get_default_max_results(), HARD_MAX_RESULTS))
    final_query = query or build_default_query(player_name, team=team, season=season)
    logger.info(
        "External verification usage before request: %s/%s. Max results: %s. Query: %s",
        current_count,
        daily_limit,
        final_max_results,
        final_query,
    )

    provider, items = search_external_context(final_query, max_results=final_max_results, project_id=client.project)
    increment_request_count(client, dataset_name, USAGE_SERVICE, usage_date)
    stored_count = store_results(client, dataset_name, provider, player_name, final_query, items)
    logger.info(
        "Stored %s search results from %s. External verification usage is now %s/%s.",
        stored_count,
        provider,
        current_count + 1,
        daily_limit,
    )
    return stored_count


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="Verify player context through a cost-capped external search provider and store results in BigQuery.")
    parser.add_argument("--player", required=True, help="Player name to verify.")
    parser.add_argument("--query", help="Explicit search query. Defaults to a player-focused context query.")
    parser.add_argument("--team", help="Optional team/context keyword.")
    parser.add_argument("--season", type=int, help="Optional season/context keyword.")
    parser.add_argument("--max-results", type=int, help=f"Number of results to store. Hard max: {HARD_MAX_RESULTS}.")
    parser.add_argument("--dataset", default="fantasy_football_brain", help="BigQuery dataset name.")
    args = parser.parse_args()

    verify_player_context(
        args.player,
        query=args.query,
        team=args.team,
        season=args.season,
        max_results=args.max_results,
        dataset_name=args.dataset,
    )


if __name__ == "__main__":
    main()
