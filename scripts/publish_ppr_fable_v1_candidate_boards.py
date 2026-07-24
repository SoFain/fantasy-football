"""Publish reviewed PPR Fable positional candidates without replacing live PPR rankings."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from google.cloud import bigquery


WRITE_GATE = "ALLOW_PPR_FABLE_CANDIDATE_PUBLISH"
BOARD_VERSION = "ppr-fable-v1-review-20260711"
DECISIONS = {
    "Colby Parkinson": (22, "HOLD_ROLE_VERIFY", False, "Verify preseason first-team route share and receiving-TE role."),
    "DK Metcalf": (19, "ACCEPT_FABLE", True, "Healthy Pittsburgh WR1; accept Fable WR19."),
    "Zach Charbonnet": (31, "INJURY_ANCHOR", False, "ACL recovery; require PUP clearance, contact clearance, and credible Week 1 availability."),
    "Kimani Vidal": (32, "ACCEPT_FABLE_PROVISIONAL", True, "Official Chargers depth chart supports the Fable rise; verify preseason first-team snaps."),
    "Stefon Diggs": (None, "EXCLUDE_UNSIGNED", False, "Released by New England; require official signing and role."),
    "Deebo Samuel": (None, "EXCLUDE_UNSIGNED", False, "No current team; require official signing and role."),
    "Keenan Allen": (None, "EXCLUDE_UNSIGNED", False, "Unrestricted free agent; require official signing and starting role."),
}


def reviewed_rows(path: Path) -> list[dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    output = []
    for row in rows:
        recommended_rank, code, eligible, note = DECISIONS.get(
            row["player_name"],
            (None, "FORMULA_DEFAULT", True, "No manual exception."),
        )
        output.append({
            **row,
            "recommended_rank": recommended_rank,
            "decision_code": code,
            "promotion_eligible": eligible,
            "decision_note": note,
        })
    return output


def schema() -> list[bigquery.SchemaField]:
    return [
        bigquery.SchemaField("board_version", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("generated_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("scoring_profile_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("player_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("player_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("current_team", "STRING"),
        bigquery.SchemaField("position", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("formula_rank", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("recommended_rank", "INT64"),
        bigquery.SchemaField("live_ppr_rank", "INT64"),
        bigquery.SchemaField("formula_score", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("decision_code", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("promotion_eligible", "BOOL", mode="REQUIRED"),
        bigquery.SchemaField("decision_note", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("risk_flags", "STRING"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--input", type=Path, default=Path("output/ppr-fable-v1-review-boards.json"))
    parser.add_argument("--scoring-profile", choices=("ppr","half_ppr"), default="ppr")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    rows = reviewed_rows(args.input)
    if not args.apply:
        print(json.dumps({"rows": len(rows), "decisions": len(DECISIONS), "writes": False}, indent=2))
        return 0
    if os.environ.get(WRITE_GATE, "").lower() != "true":
        raise RuntimeError(f"{WRITE_GATE}=true is required")
    client = bigquery.Client(project=args.project)
    table_prefix = "ppr_fable" if args.scoring_profile=="ppr" else "half_ppr_fable"
    board_version = BOARD_VERSION if args.scoring_profile=="ppr" else "half-ppr-fable-v1-review-20260711"
    current_id = f"{args.project}.{args.dataset}.{table_prefix}_rankings_current"
    history_id = f"{args.project}.{args.dataset}.{table_prefix}_rankings_history"
    client.create_table(bigquery.Table(current_id, schema=schema()), exists_ok=True)
    client.create_table(bigquery.Table(history_id, schema=schema()+[bigquery.SchemaField("archived_at", "TIMESTAMP", mode="REQUIRED")]), exists_ok=True)
    client.query(f"""
INSERT INTO `{history_id}`
SELECT live_rows.*, CURRENT_TIMESTAMP() FROM `{current_id}` live_rows
WHERE NOT EXISTS (SELECT 1 FROM `{history_id}` history
  WHERE history.board_version=live_rows.board_version AND history.player_id=live_rows.player_id)
""").result()
    client.query(f"DELETE FROM `{current_id}` WHERE scoring_profile_id='{args.scoring_profile}'").result()
    now = datetime.now(timezone.utc).isoformat()
    payload = [{
        "board_version": board_version, "generated_at": now, "scoring_profile_id": args.scoring_profile,
        "player_id": row["player_id"], "player_name": row["player_name"], "current_team": row.get("current_team"),
        "position": row["position"], "formula_rank": row["formula_rank"], "recommended_rank": row.get("recommended_rank"),
        "live_ppr_rank": row.get("live_ppr_rank"), "formula_score": row["score"], "decision_code": row["decision_code"],
        "promotion_eligible": row["promotion_eligible"], "decision_note": row["decision_note"], "risk_flags": row.get("risk_flags"),
    } for row in rows]
    errors = client.insert_rows_json(current_id, payload)
    if errors:
        raise RuntimeError(errors)
    count = next(iter(client.query(f"SELECT COUNT(*) row_count FROM `{current_id}` WHERE board_version='{board_version}'").result()))["row_count"]
    print(json.dumps({"rows": count, "decisions": len(DECISIONS), "writes": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
