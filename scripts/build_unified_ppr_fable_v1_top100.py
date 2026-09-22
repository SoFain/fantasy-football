"""Build a unified PPR or Half-PPR overall board from active positional queues."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

from google.cloud import bigquery

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from scripts.build_unified_fable_v1_top100 import OVERALL_BOARD_SIZE, fit_log_curve, interleave


PPR_REPLACEMENT = {"QB": 13, "RB": 30, "WR": 44, "TE": 9}
HALF_PPR_REPLACEMENT = {"QB": 13, "RB": 34, "WR": 42, "TE": 9}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--scoring-profile",choices=("ppr","half_ppr"),default="ppr")
    parser.add_argument("--json-output", type=Path, default=Path("output/unified-ppr-fable-v1-top150.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("docs/rebuild/unified-ppr-fable-v1-top150.md"))
    args = parser.parse_args()
    replacement_ranks=PPR_REPLACEMENT if args.scoring_profile=="ppr" else HALF_PPR_REPLACEMENT
    client = bigquery.Client(project=args.project)
    historical = [dict(row) for row in client.query(f"""
WITH seasons AS (
  SELECT season, position, source_player_key player_id, COUNT(*) games_played,
    SAFE_DIVIDE(SUM(total_fantasy_points),COUNT(*)) ppg
  FROM `{args.project}.{args.dataset}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id='{args.scoring_profile}' AND position IN ('QB','RB','WR','TE') AND season BETWEEN 2022 AND 2025 AND week BETWEEN 1 AND 18
  GROUP BY season,position,player_id HAVING games_played>=6
)
SELECT *, ROW_NUMBER() OVER(PARTITION BY season,position ORDER BY ppg DESC,player_id) position_rank FROM seasons
""").result()]
    active = [dict(row) for row in client.query(f"""
SELECT player_id,player_name,current_team,position,rank position_rank,ranking_version,rank_source,risk_flags
FROM `{args.project}.{args.dataset}.analytics_pigskin_rankings`
WHERE is_active AND scoring_profile_id='{args.scoring_profile}' AND position IN ('QB','RB','WR','TE')
QUALIFY ROW_NUMBER() OVER(PARTITION BY position,player_id ORDER BY generated_at DESC)=1
ORDER BY position,rank
""").result()]
    queues = {
        position: sorted(
            (row for row in active if row["position"] == position),
            key=lambda row: (row["position_rank"], row["player_name"]),
        )
        for position in ("QB", "RB", "WR", "TE")
    }
    for position, queue in queues.items():
        ranks = [row["position_rank"] for row in queue]
        if ranks != list(range(1, len(ranks) + 1)):
            raise ValueError(f"{position} active ranks are not contiguous")
        if len(queue) < replacement_ranks[position]:
            raise ValueError(f"{position} active queue has only {len(queue)} rows")
    curves = {}
    availability = {}
    for position in ("QB","RB","WR","TE"):
        replacement=replacement_ranks[position]
        rows=[row for row in historical if row["position"]==position and row["position_rank"]<=max(replacement+12,24)]
        curves[position]=fit_log_curve([(row["position_rank"],row["ppg"]) for row in rows])
        cohort=[row for row in historical if row["position"]==position and row["position_rank"]<=replacement]
        availability[position]=sum(min(row["games_played"]/17,1) for row in cohort)/len(cohort)
    board=interleave(queues,curves,availability,replacement_rank=replacement_ranks)
    metadata={
        "curves":{position:{"a":curves[position][0],"b":curves[position][1]} for position in curves},
        "availability":availability,"replacement_rank":replacement_ranks,
        "composition":dict(Counter(row["position"] for row in board)),
    }
    args.json_output.parent.mkdir(parents=True,exist_ok=True)
    args.json_output.write_text(json.dumps({"metadata":metadata,"board":board},indent=2,default=str)+"\n",encoding="utf-8")
    profile_label = "PPR" if args.scoring_profile == "ppr" else "Half-PPR"
    lines=[f"# Unified {profile_label} Fable v1 Top-{OVERALL_BOARD_SIZE} Review Board","","> Uses the active positional queues. The interleaver cannot reorder players within a position.","","## Model","","| Position | Curve | Replacement | Availability | Count |","|---|---|---:|---:|---:|"]
    counts=Counter(row["position"] for row in board)
    for position in ("QB","RB","WR","TE"):
        a,b=curves[position]
        lines.append(f"| {position} | {a:.3f} - {b:.3f} ln(rank) | {replacement_ranks[position]} | {availability[position]:.3f} | {counts[position]} |")
    lines.extend(["","## Board","","| Ovr | Player | Team | Pos | Pos rank | PPG | Adj VORP | Decision |","|---:|---|---|---|---:|---:|---:|---|"])
    for row in board:
        lines.append(f"| {row['overall_rank']} | {row['player_name']} | {row.get('current_team') or ''} | {row['position']} | {row['position_rank']} | {row['projected_ppg']:.2f} | {row['adjusted_vorp']:.2f} | {row.get('rank_source') or ''} |")
    args.markdown_output.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(metadata,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
