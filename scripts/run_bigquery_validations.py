#!/usr/bin/env python
"""Run BigQuery warehouse validations and sanity checks."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_DATASET = "fantasy_football_brain"


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
            "google-cloud-bigquery is required for running validations. "
            "Install requirements or run --dry-run."
        ) from exc
    return bigquery


def render_sql(sql: str, project_id: str, dataset_id: str) -> str:
    return (
        sql.replace("{{PROJECT_ID}}", project_id)
        .replace("{{DATASET_ID}}", dataset_id)
    )


def parse_expectation(sql: str) -> tuple[str, str, Any]:
    """Parse validation SQL comments to determine the expected query result.

    Returns:
        tuple (type, target_field, target_value)
        types: 'zero_rows', 'equal', 'greater', 'informational'
    """
    for line in sql.splitlines():
        line = line.strip()
        if not line.startswith("--"):
            continue

        # Match "Expected result: zero rows"
        if re.search(r"expected\s+result:\s*zero\s+rows", line, re.IGNORECASE):
            return "zero_rows", "", 0

        # Match "Expected result: column = value"
        eq_match = re.search(r"expected\s+result:\s*(\w+)\s*=\s*(\d+)", line, re.IGNORECASE)
        if eq_match:
            return "equal", eq_match.group(1).lower(), int(eq_match.group(2))

        # Match "Expected result: column > value"
        gt_match = re.search(r"expected\s+result:\s*(\w+)\s*>\s*(\d+)", line, re.IGNORECASE)
        if gt_match:
            return "greater", gt_match.group(1).lower(), int(gt_match.group(2))

        # Match "should be low" or "reviewed" (informational/warning grain)
        info_match = re.search(r"expected\s+result:\s*(\w+)\s*(?:should|stay)\s*(?:be|stay)\s*(?:low|reviewed)", line, re.IGNORECASE)
        if info_match:
            return "informational", info_match.group(1).lower(), None

        if "expected result:" in line.lower() and "review" in line.lower():
            return "informational", "review", None

    return "zero_rows", "", 0


def run_validation(client: Any, dataset_id: str, path: Path, dry_run: bool = False) -> bool:
    """Run a single validation query and assert the expectation."""
    sql_raw = path.read_text(encoding="utf-8")
    sql = render_sql(sql_raw, client.project, dataset_id)
    exp_type, field, val = parse_expectation(sql_raw)

    print(f"Validation: {path.name}")
    if exp_type == "zero_rows":
        print(f"  Expectation: Zero rows returned")
    elif exp_type == "equal":
        print(f"  Expectation: {field} = {val}")
    elif exp_type == "greater":
        print(f"  Expectation: {field} > {val}")
    else:
        print(f"  Expectation: Informational/Review query")

    if dry_run:
        print("  Dry run: Skipped execution")
        return True

    try:
        # Run BQ query
        job = client.query(sql)
        rows = list(job.result())
        row_count = len(rows)
        print(f"  Result: {row_count} rows returned")

        # Evaluate based on expectation type
        if exp_type == "zero_rows":
            if row_count == 0:
                print("  Status: PASS")
                return True
            else:
                print(f"  Status: FAIL (Returned {row_count} rows. First row: {dict(rows[0])})")
                return False

        elif exp_type == "equal":
            if row_count == 0:
                print("  Status: FAIL (No rows returned)")
                return False
            row = dict(rows[0])
            actual_val = row.get(field)
            if actual_val is None:
                # Try case insensitive fallback
                actual_val = next((v for k, v in row.items() if k.lower() == field), None)

            if actual_val == val:
                print(f"  Status: PASS ({field} = {actual_val})")
                return True
            else:
                print(f"  Status: FAIL ({field} expected {val}, got {actual_val})")
                return False

        elif exp_type == "greater":
            if row_count == 0:
                print("  Status: FAIL (No rows returned)")
                return False
            row = dict(rows[0])
            actual_val = row.get(field)
            if actual_val is None:
                actual_val = next((v for k, v in row.items() if k.lower() == field), None)

            try:
                is_greater = actual_val > val
            except TypeError:
                is_greater = False

            if is_greater:
                print(f"  Status: PASS ({field} = {actual_val} > {val})")
                return True
            else:
                print(f"  Status: FAIL ({field} expected > {val}, got {actual_val})")
                return False

        elif exp_type == "informational":
            if row_count > 0:
                print(f"  Status: WARNING (Needs review, returned {row_count} rows. First row: {dict(rows[0])})")
            else:
                print("  Status: PASS (No review rows returned)")
            return True

    except Exception as exc:
        print(f"  Status: ERROR ({exc})")
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run BigQuery warehouse validations.")
    parser.add_argument("--project", default=get_configured_project(), help="BigQuery project ID.")
    parser.add_argument("--dataset", default=get_bigquery_dataset(), help="BigQuery dataset name.")
    parser.add_argument(
        "--validations-dir",
        default=str(REPO_ROOT / "bigquery" / "validations"),
        help="Directory containing validation SQL files.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print validations list without executing.")
    parser.add_argument("--run", action="store_true", help="Execute the validations.")
    parser.add_argument("--pattern", help="Regex pattern of file names to run.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validations_dir = Path(args.validations_dir)
    sql_files = sorted(validations_dir.glob("*.sql"))
    if not sql_files:
        raise SystemExit(f"No validation SQL files found in {validations_dir}")

    # Filter by pattern if specified
    if args.pattern:
        pattern_re = re.compile(args.pattern, re.IGNORECASE)
        sql_files = [f for f in sql_files if pattern_re.search(f.name)]
        if not sql_files:
            print(f"No validation files matched pattern: {args.pattern}")
            return

    print(f"Project: {args.project}")
    print(f"Dataset: {args.dataset}")
    print(f"Validations dir: {validations_dir}")
    print(f"Total validation files: {len(sql_files)}")
    print("-" * 50)

    if args.dry_run or not args.run:
        for f in sql_files:
            sql_raw = f.read_text(encoding="utf-8")
            exp_type, field, val = parse_expectation(sql_raw)
            print(f"- {f.name} (Expectation: {exp_type} {field}={val if val is not None else ''})")
        return

    client = get_bigquery_module().Client(project=args.project)

    passed = 0
    failed = 0

    for f in sql_files:
        success = run_validation(client, args.dataset, f)
        if success:
            passed += 1
        else:
            failed += 1
        print("-" * 50)

    print(f"Validation Run Completed: {passed} passed, {failed} failed.")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
