"""Build read-only PPR Fable positional review boards against the active PPR baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from google.cloud import bigquery


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--metrics-dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--scoring-profile", choices=("ppr","half_ppr"), default="ppr")
    parser.add_argument("--json-output", type=Path, default=Path("output/ppr-fable-v1-review-boards.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("docs/rebuild/ppr-fable-v1-review-boards.md"))
    args = parser.parse_args()
    client = bigquery.Client(project=args.project)
    sql = f"""
WITH live_ppr AS (
  SELECT player_id, position, rank AS live_ppr_rank, current_team, risk_flags
  FROM `{args.project}.{args.dataset}.analytics_pigskin_rankings`
  WHERE is_active AND scoring_profile_id='{args.scoring_profile}'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY position, player_id ORDER BY generated_at DESC)=1
),
formula_rows AS (
  SELECT candidate_internal_player_id AS player_id, player_name, 'RB' AS position,
    rb_fable_01_score + 0.02*z_target_share - 0.02*z_ngt_tpg AS score, team
  FROM `{args.project}.{args.metrics_dataset}.v_rb_fable_01_scored_seasons` WHERE season=2025 AND rb_fable_01_score IS NOT NULL
  UNION ALL
  SELECT candidate_internal_player_id, player_name, 'WR', wr_fable_v1_score, team
  FROM `{args.project}.{args.metrics_dataset}.v_wr_fable_v1_current_candidates` WHERE wr_fable_v1_score IS NOT NULL
  UNION ALL
  SELECT candidate_internal_player_id, player_name, 'TE', te_fable_v1a_no_man_score, team
  FROM `{args.project}.{args.metrics_dataset}.v_te_fable_v1a_scored_seasons` WHERE season=2025 AND te_fable_v1a_no_man_score IS NOT NULL
), ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY position ORDER BY score DESC, player_name) AS formula_rank
  FROM formula_rows
)
SELECT ranked.player_id, ranked.player_name, ranked.position, ranked.formula_rank, ranked.score,
  live_ppr.live_ppr_rank, live_ppr.live_ppr_rank-ranked.formula_rank AS rank_delta,
  COALESCE(live_ppr.current_team, CASE ranked.team WHEN 'LA' THEN 'LAR' WHEN 'HST' THEN 'HOU' WHEN 'BLT' THEN 'BAL' WHEN 'CLV' THEN 'CLE' WHEN 'ARZ' THEN 'ARI' ELSE ranked.team END) AS current_team,
  live_ppr.risk_flags
FROM ranked LEFT JOIN live_ppr USING(player_id,position)
ORDER BY position, formula_rank
"""
    rows = [dict(row) for row in client.query(sql).result()]
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(rows, indent=2, default=str)+"\n", encoding="utf-8")
    lines = [
        f"# {args.scoring_profile.upper()} Fable v1 Positional Review Boards", "",
        "> Review-only. RB uses the selected 2% target-share shift. WR and TE transfer their locked Fable scores unchanged. QB remains the guarded Standard queue because QB scoring is identical.", "",
    ]
    for position, limit in (("RB", 40), ("WR", 50), ("TE", 25)):
        lines.extend([f"## {position}", "", "| Fable | Live PPR | Delta | Player | Team | Score | Risk flags |", "|---:|---:|---:|---|---|---:|---|"])
        for row in [item for item in rows if item["position"] == position and item["formula_rank"] <= limit]:
            live = row.get("live_ppr_rank") or "—"
            delta = row.get("rank_delta") if row.get("rank_delta") is not None else "—"
            flags = str(row.get("risk_flags") or "").replace("|", "/")
            lines.append(f"| {row['formula_rank']} | {live} | {delta} | {row['player_name']} | {row.get('current_team') or ''} | {row['score']:.3f} | {flags} |")
        lines.append("")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({position: sum(row["position"] == position for row in rows) for position in ("RB","WR","TE")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
