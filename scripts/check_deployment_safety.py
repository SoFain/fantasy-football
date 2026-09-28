#!/usr/bin/env python
"""Local deployment safety checks for Cloud Run rebuild phases."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SECRET_FILE_RE = re.compile(
    r"(^|[/\\])(\.env|.*service[-_]?account.*\.json|.*credential.*\.json|.*private.*key.*|.*\.pem|.*\.p12)$",
    re.IGNORECASE,
)
SECRET_CONTENT_RE = re.compile(
    r"(-----BEGIN [A-Z ]*PRIVATE KEY-----|\"private_key\"\s*:|AIza[0-9A-Za-z_-]{20,})",
    re.IGNORECASE,
)
FIREBASE_ARTIFACTS = {
    "firebase.json",
    ".firebaserc",
}
REQUIRED_FILES = (
    "src/job_runner.py",
    "src/cloud_run_jobs.py",
    "scripts/run_bigquery_validations.py",
    "scripts/deploy_cloud_run_jobs.ps1",
    "scripts/deploy_cloud_run_jobs.sh",
    "docs/rebuild/secret-manager-plan.md",
    "docs/rebuild/iam-hardening-plan.md",
    "docs/rebuild/cloud-scheduler-plan.md",
    "docs/rebuild/deployment-readiness-checklist.md",
)


def main() -> None:
    results: list[dict[str, object]] = []
    tracked_files = _tracked_files()

    _check(results, "no_firebase_artifacts", not _firebase_artifacts(tracked_files), _firebase_artifacts(tracked_files))
    _check(results, "no_tracked_secret_files", not _tracked_secret_files(tracked_files), _tracked_secret_files(tracked_files))
    _check(results, "no_secret_content", not _tracked_secret_content(tracked_files), _tracked_secret_content(tracked_files))
    _check(results, "required_files_exist", not _missing_required_files(), _missing_required_files())
    _check(results, "feature_flags_default_off", _feature_flags_default_off(), [])
    _check(results, "pigskin_no_execute_bigquery_sql", _pigskin_sql_tool_removed(), [])
    _check(results, "app_py_compiles", _run([sys.executable, "-m", "py_compile", "app.py"]), [])
    _check(results, "src_scripts_compile", _run([sys.executable, "-m", "compileall", "-q", "src", "scripts"]), [])

    print(json.dumps({"checks": results}, indent=2, sort_keys=True))
    if any(not item["passed"] for item in results):
        raise SystemExit(1)


def _check(results: list[dict[str, object]], name: str, passed: bool, details: object) -> None:
    results.append({"name": name, "passed": passed, "details": details})


def _tracked_files() -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _firebase_artifacts(paths: list[str]) -> list[str]:
    matches = []
    for path in paths:
        name = Path(path).name.lower()
        parts = {part.lower() for part in Path(path).parts}
        if name in FIREBASE_ARTIFACTS or "functions" in parts and name == "package.json":
            matches.append(path)
    return matches


def _tracked_secret_files(paths: list[str]) -> list[str]:
    return [path for path in paths if SECRET_FILE_RE.search(path.replace("\\", "/"))]


def _tracked_secret_content(paths: list[str]) -> list[str]:
    matches = []
    for path in paths:
        if path.replace("\\", "/") == "scripts/check_deployment_safety.py":
            continue
        full_path = REPO_ROOT / path
        if not full_path.is_file() or full_path.stat().st_size > 2_000_000:
            continue
        try:
            text = full_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if SECRET_CONTENT_RE.search(text):
            matches.append(path)
    return matches


def _missing_required_files() -> list[str]:
    return [path for path in REQUIRED_FILES if not (REPO_ROOT / path).exists()]


def _feature_flags_default_off() -> bool:
    from src import cloud_run_jobs

    return (
        not cloud_run_jobs.cloud_run_jobs_feature_enabled({})
        and not cloud_run_jobs.data_ops_job_trigger_allowed({})
        and not cloud_run_jobs.should_use_cloud_run_jobs_for_data_ops({})
    )


def _pigskin_sql_tool_removed() -> bool:
    schema_path = REPO_ROOT / "src" / "pigskin_chat_schema.py"
    app_path = REPO_ROOT / "app.py"
    text = ""
    if schema_path.exists():
        text += schema_path.read_text(encoding="utf-8")
    text += app_path.read_text(encoding="utf-8")
    return "execute_bigquery_sql" not in text


def _run(command: list[str]) -> bool:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stdout[-4000:])
        sys.stderr.write(completed.stderr[-4000:])
    return completed.returncode == 0


if __name__ == "__main__":
    main()
