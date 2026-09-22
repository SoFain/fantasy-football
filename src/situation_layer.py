"""Build the player situation layer: team/QB/coaching/age context per season.

One deterministic SQL build populates analytics_player_situation with:

  * Historical transition rows (2016-2025): each player-season pair from the
    profile-aware points history (2015-2025, standard scoring), with the
    next-season outcome attached. This is the ML training set for estimating
    situation effect sizes.
  * Current rows (2026): the same shape for the upcoming season, where
    team_to comes from today's Sleeper snapshot, qb_to from the platform's own
    active standard QB board, and coaching from coaching_staff_current.
    ppg_next is NULL until the season is played.

QB quality is always the QB's PRIOR-season standard PPG: what was knowable at
decision time. The situation layer never moves a ranking; it produces facts,
flags, and training data. Adjustment magnitudes come later, from the BQML
study over the historical rows, and require owner review per the runbook.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("situation_layer")

TABLE_NAME = "analytics_player_situation"
FIRST_TRANSITION_SEASON = 2016
CURRENT_SEASON = 2026
STATS_SEASON = 2025
MIN_GAMES_PREV = 1

# Flag thresholds, v0. Editorial knobs surfaced as constants so the owners can
# tune them; the ML study informs whether these bands are the right ones.
QB_UPGRADE_MAJOR_PPG = 4.0
QB_UPGRADE_PPG = 1.5
AGE_CLIFF = {"RB": 28.0, "WR": 30.0, "TE": 31.0, "QB": 37.0}

# Sleeper team code -> nflverse mart team code, for the one franchise the two
# sources spell differently. Audited 2026-07-25: LA/LAR was the only alias pair
# among the season's team-change rows (13 false Rams movers before the fix).
TEAM_ALIASES = {"LAR": "LA"}


def _team_alias_case(column: str) -> str:
    whens = " ".join(f"WHEN '{src}' THEN '{dst}'" for src, dst in TEAM_ALIASES.items())
    return f"CASE {column} {whens} ELSE {column} END"


def build_situation_sql(project_id: str, dataset_id: str) -> str:
    age_cliff_sql = " ".join(
        f"WHEN e.position = '{pos}' AND e.age_at_season >= {age} THEN 'AGE_CLIFF'"
        for pos, age in AGE_CLIFF.items()
    )
    team_alias_case = _team_alias_case("sleeper_now.team")
    return f"""
BEGIN TRANSACTION;

TRUNCATE TABLE `{project_id}.{dataset_id}.{TABLE_NAME}`;

INSERT INTO `{project_id}.{dataset_id}.{TABLE_NAME}`
  (situation_for_season, stats_season, player_id_internal, gsis_id, sleeper_player_id,
   player_name, position, team_from, team_to, team_changed, games_prev, ppg_prev, ppg_next,
   qb_from, qb_to, qb_quality_from, qb_quality_to, qb_quality_delta, qb_changed,
   age_at_season, head_coach, offensive_coordinator, flags_json, metric_basis, created_at,
   hc_changed, oc_changed,
   gng_ppg_prev, gng_ppg_next, qb_quality_from_gng, qb_quality_to_gng, qb_quality_delta_gng)
WITH player_season AS (
  -- Identity note: player_id_internal changed schemes mid-history in the
  -- profile points mart (2015-2024 rows use bare gsis, 2025 rows use
  -- 'gsis:'-prefixed ids), which silently breaks cross-season joins. The
  -- normalized gsis key below is the stable identity; it also matches
  -- player_identity_bridge.gsis_id directly.
  --
  -- GNG parity: standard and GNG Keeper PPG come from the same pass. The
  -- unsuffixed ppg stays standard scoring; gng_ppg is the owners' league.
  SELECT
    COALESCE(source_player_key, REGEXP_REPLACE(player_id_internal, r'^gsis:', '')) AS player_id_internal,
    season,
    ANY_VALUE(player_display_name) AS player_name,
    ANY_VALUE(position) AS position,
    APPROX_TOP_COUNT(team, 1)[OFFSET(0)].value AS team,
    COUNT(DISTINCT week) AS games,
    ROUND(AVG(IF(scoring_profile_id = 'standard', total_fantasy_points, NULL)), 2) AS ppg,
    ROUND(AVG(IF(scoring_profile_id = 'gng_keeper', total_fantasy_points, NULL)), 2) AS gng_ppg
  FROM `{project_id}.{dataset_id}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id IN ('standard', 'gng_keeper')
    AND position IN ('QB', 'RB', 'WR', 'TE')
  GROUP BY 1, 2
),
team_qb AS (
  -- The QB who led each team-season, with his PPG that season as the quality
  -- measure other seasons reference.
  SELECT season, team, player_id_internal AS qb_id, player_name AS qb_name,
         ppg AS qb_ppg, gng_ppg AS qb_gng_ppg
  FROM player_season
  WHERE position = 'QB'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY season, team ORDER BY games DESC, ppg DESC) = 1
),
bridge AS (
  -- Keyed by gsis so it joins the normalized player_season identity.
  SELECT gsis_id,
         ANY_VALUE(sleeper_player_id) AS sleeper_player_id,
         ANY_VALUE(birth_date) AS birth_date
  FROM `{project_id}.{dataset_id}.player_identity_bridge`
  WHERE gsis_id IS NOT NULL
  GROUP BY gsis_id
),
historical AS (
  SELECT
    nxt.season AS situation_for_season,
    prev.season AS stats_season,
    prev.player_id_internal,
    prev.player_name,
    prev.position,
    prev.team AS team_from,
    nxt.team AS team_to,
    prev.team != nxt.team AS team_changed,
    prev.games AS games_prev,
    prev.ppg AS ppg_prev,
    nxt.ppg AS ppg_next,
    prev.gng_ppg AS gng_ppg_prev,
    nxt.gng_ppg AS gng_ppg_next,
    qb_prev.qb_name AS qb_from,
    qb_next_person.qb_name AS qb_to,
    qb_prev.qb_ppg AS qb_quality_from,
    qb_next_prior.ppg AS qb_quality_to,
    qb_prev.qb_gng_ppg AS qb_quality_from_gng,
    qb_next_prior.gng_ppg AS qb_quality_to_gng,
    qb_next_person.qb_id AS qb_to_id
  FROM player_season prev
  JOIN player_season nxt
    ON nxt.player_id_internal = prev.player_id_internal
   AND nxt.season = prev.season + 1
  LEFT JOIN team_qb qb_prev
    ON qb_prev.season = prev.season AND qb_prev.team = prev.team
  LEFT JOIN team_qb qb_next_person
    ON qb_next_person.season = nxt.season AND qb_next_person.team = nxt.team
  LEFT JOIN player_season qb_next_prior
    ON qb_next_prior.player_id_internal = qb_next_person.qb_id
   AND qb_next_prior.season = prev.season
  WHERE nxt.season BETWEEN {FIRST_TRANSITION_SEASON} AND {STATS_SEASON}
    AND prev.games >= {MIN_GAMES_PREV}
),
board_qb AS (
  -- The platform's own view of each team's 2026 QB1: best-ranked active
  -- standard-board QB per current team.
  SELECT current_team AS team, player_name AS qb_name, player_id AS qb_gsis
  FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings`
  WHERE is_active AND scoring_profile_id = 'standard' AND position = 'QB'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY current_team ORDER BY rank) = 1
),
staff AS (
  SELECT team_abbr,
         MAX(IF(role = 'head_coach', coach_name, NULL)) AS head_coach,
         MAX(IF(role = 'offensive_coordinator', coach_name, NULL)) AS offensive_coordinator
  FROM `{project_id}.{dataset_id}.coaching_staff_current`
  GROUP BY team_abbr
),
staff_prev AS (
  -- Prior-season head coach baseline (head-coach-only; see migration 0047).
  -- Mid-season changes carry both names, so the change test asks whether the
  -- current head coach appears anywhere in the baseline string.
  SELECT team_abbr, coach_name AS hc_prev
  FROM `{project_id}.{dataset_id}.coaching_staff_history`
  WHERE season = {STATS_SEASON} AND role = 'head_coach'
),
sleeper_now AS (
  SELECT sleeper_player_id, team
  FROM `{project_id}.{dataset_id}.sleeper_players_current`
  WHERE snapshot_at = (SELECT MAX(snapshot_at) FROM `{project_id}.{dataset_id}.sleeper_players_current`)
    AND team IS NOT NULL
),
current_rows AS (
  SELECT
    {CURRENT_SEASON} AS situation_for_season,
    prev.season AS stats_season,
    prev.player_id_internal,
    prev.player_name,
    prev.position,
    prev.team AS team_from,
    sleeper_now.team AS team_to,
    -- Sleeper and the nflverse mart disagree on one franchise code (Sleeper
    -- LAR vs mart LA); compare on the normalized code or every Rams player is
    -- a false mover. team_to keeps the Sleeper code for display and joins.
    prev.team != {team_alias_case} AS team_changed,
    prev.games AS games_prev,
    prev.ppg AS ppg_prev,
    CAST(NULL AS FLOAT64) AS ppg_next,
    prev.gng_ppg AS gng_ppg_prev,
    CAST(NULL AS FLOAT64) AS gng_ppg_next,
    qb_prev.qb_name AS qb_from,
    board_qb.qb_name AS qb_to,
    qb_prev.qb_ppg AS qb_quality_from,
    qb_now_prior.ppg AS qb_quality_to,
    qb_prev.qb_gng_ppg AS qb_quality_from_gng,
    qb_now_prior.gng_ppg AS qb_quality_to_gng,
    CAST(NULL AS STRING) AS qb_to_id
  FROM player_season prev
  JOIN bridge b ON b.gsis_id = prev.player_id_internal
  JOIN sleeper_now ON sleeper_now.sleeper_player_id = b.sleeper_player_id
  LEFT JOIN team_qb qb_prev
    ON qb_prev.season = prev.season AND qb_prev.team = prev.team
  LEFT JOIN board_qb ON board_qb.team = sleeper_now.team
  LEFT JOIN player_season qb_now_prior
    ON qb_now_prior.player_id_internal = board_qb.qb_gsis
   AND qb_now_prior.season = prev.season
  WHERE prev.season = {STATS_SEASON}
    AND prev.games >= {MIN_GAMES_PREV}
),
unioned AS (
  SELECT * FROM historical
  UNION ALL
  SELECT * FROM current_rows
),
enriched AS (
  SELECT
    u.*,
    u.player_id_internal AS gsis_id,
    b.sleeper_player_id,
    ROUND(u.qb_quality_to - u.qb_quality_from, 2) AS qb_quality_delta,
    ROUND(u.qb_quality_to_gng - u.qb_quality_from_gng, 2) AS qb_quality_delta_gng,
    COALESCE(u.qb_to != u.qb_from, FALSE) AS qb_changed_calc,
    ROUND(SAFE_DIVIDE(DATE_DIFF(DATE(u.situation_for_season, 9, 1), b.birth_date, DAY), 365.25), 1) AS age_at_season,
    IF(u.situation_for_season = {CURRENT_SEASON}, staff.head_coach, NULL) AS head_coach_now,
    IF(u.situation_for_season = {CURRENT_SEASON}, staff.offensive_coordinator, NULL) AS oc_now,
    IF(
      u.situation_for_season = {CURRENT_SEASON}
        AND staff.head_coach IS NOT NULL AND staff_prev.hc_prev IS NOT NULL,
      STRPOS(staff_prev.hc_prev, staff.head_coach) = 0,
      NULL
    ) AS hc_changed_calc
  FROM unioned u
  LEFT JOIN bridge b ON b.gsis_id = u.player_id_internal
  LEFT JOIN staff ON u.situation_for_season = {CURRENT_SEASON} AND staff.team_abbr = u.team_to
  LEFT JOIN staff_prev ON u.situation_for_season = {CURRENT_SEASON} AND staff_prev.team_abbr = u.team_to
)
SELECT
  e.situation_for_season,
  e.stats_season,
  e.player_id_internal,
  e.gsis_id,
  e.sleeper_player_id,
  e.player_name,
  e.position,
  e.team_from,
  e.team_to,
  e.team_changed,
  e.games_prev,
  e.ppg_prev,
  e.ppg_next,
  e.qb_from,
  e.qb_to,
  e.qb_quality_from,
  e.qb_quality_to,
  e.qb_quality_delta,
  e.qb_changed_calc AS qb_changed,
  e.age_at_season,
  e.head_coach_now AS head_coach,
  e.oc_now AS offensive_coordinator,
  TO_JSON_STRING(ARRAY(
    SELECT flag FROM UNNEST([
      IF(e.team_changed, 'NEW_TEAM', NULL),
      IF(e.qb_changed_calc AND e.position != 'QB', 'QB_CHANGED', NULL),
      IF(e.position != 'QB' AND e.qb_quality_delta >= {QB_UPGRADE_MAJOR_PPG}, 'QB_UPGRADE_MAJOR',
        IF(e.position != 'QB' AND e.qb_quality_delta >= {QB_UPGRADE_PPG}, 'QB_UPGRADE', NULL)),
      IF(e.position != 'QB' AND e.qb_quality_delta <= -{QB_UPGRADE_MAJOR_PPG}, 'QB_DOWNGRADE_MAJOR',
        IF(e.position != 'QB' AND e.qb_quality_delta <= -{QB_UPGRADE_PPG}, 'QB_DOWNGRADE', NULL)),
      IF(e.position != 'QB' AND e.qb_to IS NOT NULL AND e.qb_quality_to IS NULL, 'QB_NO_PRIOR_SEASON', NULL),
      IF(e.hc_changed_calc IS TRUE, 'NEW_HC', NULL),
      CASE
        {age_cliff_sql}
        ELSE NULL
      END
    ]) AS flag WHERE flag IS NOT NULL
  )) AS flags_json,
  CONCAT(CAST(e.stats_season AS STRING), '_', COALESCE(e.team_from, 'UNK')) AS metric_basis,
  CURRENT_TIMESTAMP() AS created_at,
  e.hc_changed_calc AS hc_changed,
  CAST(NULL AS BOOL) AS oc_changed,
  e.gng_ppg_prev,
  e.gng_ppg_next,
  e.qb_quality_from_gng,
  e.qb_quality_to_gng,
  e.qb_quality_delta_gng
FROM enriched e;

COMMIT TRANSACTION;
"""


def build_situation_layer(
    project_id: str = "fantasy-football-498121",
    dataset_id: str = "fantasy_football_brain",
    client: Any | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    if client is None:
        from google.cloud import bigquery

        from src.load import get_bigquery_project

        client = bigquery.Client(project=get_bigquery_project())

    sql = build_situation_sql(project_id or client.project, dataset_id)
    if dry_run:
        return {"row_count": 0, "dry_run": True, "sql_bytes": len(sql)}

    client.query(sql).result()
    summary_sql = f"""
    SELECT situation_for_season, COUNT(*) AS n, COUNTIF(team_changed) AS moved
    FROM `{project_id}.{dataset_id}.{TABLE_NAME}`
    GROUP BY situation_for_season ORDER BY situation_for_season
    """
    seasons = {int(r["situation_for_season"]): {"rows": int(r["n"]), "moved": int(r["moved"])}
               for r in client.query(summary_sql).result()}
    total = sum(v["rows"] for v in seasons.values())
    logger.info("Situation layer built: %s rows across %s seasons.", total, len(seasons))
    return {"row_count": total, "seasons": seasons}
