"""Copy the active guarded Standard QB queue to PPR and half-PPR with archive safety."""
from __future__ import annotations
import os
from google.cloud import bigquery

GATE="ALLOW_GUARDED_QB_RECEPTION_PROFILE_PROMOTION"

def main()->int:
    if os.environ.get(GATE,"").lower()!="true": raise RuntimeError(f"{GATE}=true is required")
    project="fantasy-football-498121"; dataset="fantasy_football_brain"
    live=f"`{project}.{dataset}.analytics_pigskin_rankings`"; history=f"`{project}.{dataset}.analytics_pigskin_rankings_history`"
    sql=f"""
INSERT INTO {history} SELECT old.* FROM {live} old
WHERE old.is_active AND old.position='QB' AND old.scoring_profile_id IN ('ppr','half_ppr')
AND NOT EXISTS(SELECT 1 FROM {history} h WHERE h.ranking_version=old.ranking_version AND h.player_id=old.player_id AND h.position=old.position);
UPDATE {live} SET is_active=FALSE WHERE is_active AND position='QB' AND scoring_profile_id IN ('ppr','half_ppr');
INSERT INTO {live}
SELECT standard.* REPLACE(
  CONCAT(profile,'-guarded-qb-75-25-20260711') AS ranking_version,
  CURRENT_TIMESTAMP() AS generated_at,
  profile AS scoring_profile_id,
  CONCAT('guarded-qb-',profile,'-',FORMAT_TIMESTAMP('%Y%m%dT%H%M%SZ',CURRENT_TIMESTAMP())) AS model_run_id
)
FROM {live} standard CROSS JOIN UNNEST(['ppr','half_ppr']) profile
WHERE standard.is_active AND standard.scoring_profile_id='standard' AND standard.position='QB';
"""
    client=bigquery.Client(project=project); client.query(sql).result()
    print([dict(r) for r in client.query(f"SELECT scoring_profile_id,COUNT(*) row_count,MIN(rank) min_rank,MAX(rank) max_rank FROM {live} WHERE is_active AND position='QB' AND scoring_profile_id IN ('ppr','half_ppr') GROUP BY scoring_profile_id ORDER BY scoring_profile_id").result()]); return 0

if __name__=="__main__": raise SystemExit(main())
