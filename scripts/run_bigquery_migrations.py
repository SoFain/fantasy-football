#!/usr/bin/env python
"""Run BigQuery schema migrations for the existing fantasy warehouse."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import os
import socket
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_DATASET = "fantasy_football_brain"
LEDGER_TABLE = "schema_migrations"
RUNNER_VERSION = "2026-06-15"


@dataclass(frozen=True)
class Migration:
    migration_id: str
    description: str
    path: Path
    sql: str
    checksum: str


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def get_configured_project() -> str:
    try:
        from src.load import get_bigquery_project

        return get_bigquery_project()
    except Exception:
        return (
            os.environ.get("BQ_PROJECT")
            or os.environ.get("GCP_PROJECT")
            or os.environ.get("GOOGLE_CLOUD_PROJECT")
            or DEFAULT_PROJECT
        )


def get_bigquery_module():
    try:
        from google.cloud import bigquery
    except ImportError as exc:
        raise SystemExit(
            "google-cloud-bigquery is required for live migration modes. "
            "Install requirements or run --dry-run for offline planning."
        ) from exc
    return bigquery


def read_migrations(migrations_dir: Path) -> list[Migration]:
    migrations = []
    for path in sorted(migrations_dir.glob("*.sql")):
        stem = path.stem
        if "__" in stem:
            migration_id, description = stem.split("__", 1)
        else:
            migration_id, description = stem, stem
        sql = path.read_text(encoding="utf-8")
        migrations.append(
            Migration(
                migration_id=migration_id,
                description=description.replace("_", " "),
                path=path,
                sql=sql,
                checksum=hashlib.sha256(sql.encode("utf-8")).hexdigest(),
            )
        )
    return migrations


def render_sql(sql: str, project_id: str, dataset_id: str) -> str:
    return (
        sql.replace("{{PROJECT_ID}}", project_id)
        .replace("{{DATASET_ID}}", dataset_id)
        .replace("{{LEDGER_TABLE}}", LEDGER_TABLE)
    )


def has_executable_sql(sql: str) -> bool:
    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        return True
    return False


def ledger_table_id(project_id: str, dataset_id: str) -> str:
    return f"{project_id}.{dataset_id}.{LEDGER_TABLE}"


def ensure_ledger_table(client, dataset_id: str) -> None:
    from src.load import create_dataset_if_not_exists

    create_dataset_if_not_exists(client, dataset_name=dataset_id)
    sql = f"""
    CREATE TABLE IF NOT EXISTS `{ledger_table_id(client.project, dataset_id)}` (
        migration_id STRING NOT NULL,
        description STRING,
        checksum STRING NOT NULL,
        source_path STRING,
        applied_at TIMESTAMP NOT NULL,
        applied_by STRING,
        runner_version STRING
    )
    PARTITION BY DATE(applied_at)
    CLUSTER BY migration_id
    """
    client.query(sql).result()


def fetch_applied_migration_ids(client, dataset_id: str) -> set[str]:
    sql = f"""
    SELECT migration_id
    FROM `{ledger_table_id(client.project, dataset_id)}`
    """
    return {row.migration_id for row in client.query(sql).result()}


def record_applied_migration(
    client,
    dataset_id: str,
    migration: Migration,
) -> None:
    bigquery = get_bigquery_module()
    sql = f"""
    MERGE `{ledger_table_id(client.project, dataset_id)}` target
    USING (
        SELECT
            @migration_id AS migration_id,
            @description AS description,
            @checksum AS checksum,
            @source_path AS source_path,
            CURRENT_TIMESTAMP() AS applied_at,
            @applied_by AS applied_by,
            @runner_version AS runner_version
    ) source
    ON target.migration_id = source.migration_id
    WHEN NOT MATCHED THEN
        INSERT (
            migration_id,
            description,
            checksum,
            source_path,
            applied_at,
            applied_by,
            runner_version
        )
        VALUES (
            source.migration_id,
            source.description,
            source.checksum,
            source.source_path,
            source.applied_at,
            source.applied_by,
            source.runner_version
        )
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("migration_id", "STRING", migration.migration_id),
            bigquery.ScalarQueryParameter("description", "STRING", migration.description),
            bigquery.ScalarQueryParameter("checksum", "STRING", migration.checksum),
            bigquery.ScalarQueryParameter("source_path", "STRING", str(migration.path.relative_to(REPO_ROOT))),
            bigquery.ScalarQueryParameter("applied_by", "STRING", f"{getpass.getuser()}@{socket.gethostname()}"),
            bigquery.ScalarQueryParameter("runner_version", "STRING", RUNNER_VERSION),
        ]
    )
    client.query(sql, job_config=job_config).result()


def print_plan(migrations: list[Migration], applied_ids: set[str] | None = None) -> list[Migration]:
    applied_ids = applied_ids or set()
    pending = [migration for migration in migrations if migration.migration_id not in applied_ids]
    if not pending:
        print("No pending migrations.")
        return []

    print("Pending migrations:")
    for migration in pending:
        statement_count = "sql" if has_executable_sql(migration.sql) else "no-op"
        print(f"- {migration.migration_id}: {migration.description} ({statement_count})")
    return pending


def print_discovered_migrations(migrations: list[Migration]) -> list[Migration]:
    print("Dry run mode: local discovery only. This does not connect to BigQuery or read the schema_migrations ledger.")
    print("Use --list-pending for ledger-aware pending migration status.")
    print("Discovered migration files:")
    for migration in migrations:
        statement_count = "sql" if has_executable_sql(migration.sql) else "no-op"
        print(f"- {migration.migration_id}: {migration.description} ({statement_count})")
    return migrations


def build_client(project_id: str):
    bigquery = get_bigquery_module()
    return bigquery.Client(project=project_id)


def find_migration(migrations: list[Migration], migration_id: str) -> Migration:
    for migration in migrations:
        if migration.migration_id == migration_id:
            return migration
    raise SystemExit(f"Migration not found: {migration_id}")


def apply_migrations(client, dataset_id: str, migrations: list[Migration]) -> None:
    ensure_ledger_table(client, dataset_id)
    pending = print_plan(migrations, fetch_applied_migration_ids(client, dataset_id))
    for migration in pending:
        rendered_sql = render_sql(migration.sql, client.project, dataset_id)
        if has_executable_sql(rendered_sql):
            print(f"Applying {migration.migration_id}: {migration.description}")
            client.query(rendered_sql).result()
        else:
            print(f"Recording no-op {migration.migration_id}: {migration.description}")
        record_applied_migration(client, dataset_id, migration)
    if pending:
        print(f"Applied {len(pending)} migration(s).")


def list_pending(client, dataset_id: str, migrations: list[Migration]) -> None:
    ensure_ledger_table(client, dataset_id)
    print_plan(migrations, fetch_applied_migration_ids(client, dataset_id))


def record_only(client, dataset_id: str, migrations: list[Migration], migration_id: str) -> None:
    ensure_ledger_table(client, dataset_id)
    migration = find_migration(migrations, migration_id)
    record_applied_migration(client, dataset_id, migration)
    print(f"Recorded {migration.migration_id}: {migration.description}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run BigQuery schema migrations.")
    parser.add_argument("--project", default=get_configured_project(), help="BigQuery project ID.")
    parser.add_argument("--dataset", default=get_bigquery_dataset(), help="BigQuery dataset name.")
    parser.add_argument(
        "--migrations-dir",
        default=str(REPO_ROOT / "bigquery" / "migrations"),
        help="Directory containing migration SQL files.",
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="List discovered local migration files without connecting to BigQuery.")
    mode.add_argument("--apply", action="store_true", help="Apply pending migrations and record them.")
    mode.add_argument("--list-pending", action="store_true", help="List migrations not recorded in the ledger.")
    mode.add_argument("--record", help="Record a migration ID as applied without executing SQL.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    migrations_dir = Path(args.migrations_dir)
    migrations = read_migrations(migrations_dir)
    if not migrations:
        raise SystemExit(f"No migration SQL files found in {migrations_dir}")

    print(f"Project: {args.project}")
    print(f"Dataset: {args.dataset}")
    print(f"Migrations dir: {migrations_dir}")

    if args.dry_run or not any([args.apply, args.list_pending, args.record]):
        print_discovered_migrations(migrations)
        return

    client = build_client(args.project)
    if args.apply:
        apply_migrations(client, args.dataset, migrations)
    elif args.list_pending:
        list_pending(client, args.dataset, migrations)
    elif args.record:
        record_only(client, args.dataset, migrations, args.record)


if __name__ == "__main__":
    main()
