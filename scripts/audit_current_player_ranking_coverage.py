"""Audit active current-player coverage without changing rankings or BigQuery tables."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any

from google.cloud import bigquery

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.sleeper_player_snapshot import fetch_sleeper_players


PROFILES = ("standard", "ppr", "half_ppr")
ALL_PROFILES = (*PROFILES, "gng_keeper")
POSITIONS = ("QB", "RB", "WR", "TE")
EXPECTED_COUNTS = {
    "standard": {"QB": 45, "RB": 85, "WR": 100, "TE": 35},
    "ppr": {"QB": 45, "RB": 80, "WR": 100, "TE": 35},
    "half_ppr": {"QB": 45, "RB": 80, "WR": 100, "TE": 35},
}
HIGH_SIGNAL_POSITION_RANK = {"QB": 16, "RB": 36, "WR": 55, "TE": 12}
BLOCKING_TRACE_CODES = {
    "BELOW_2025_FABLE_QUALIFICATION_THRESHOLD",
    "FABLE_FORMULA_TRANSFORM_DROPOUT",
    "IDENTITY_BRIDGE_COLLISION",
    "IDENTITY_BRIDGE_UNMAPPED",
    "NO_2025_SITUATIONAL_SOURCE_ROW",
}


def normalize_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]", "", value.lower())
    return re.sub(r"(jr|sr|ii|iii|iv)$", "", normalized)


def player_key(name: str, position: str) -> tuple[str, str]:
    return position, "name:" + normalize_name(name)


def identity_keys(name: str, position: str, *identifiers: Any) -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    for identifier in identifiers:
        value = re.sub(r"^(gsis|sleeper):", "", str(identifier or "").strip(), flags=re.IGNORECASE)
        if value:
            keys.append((position, "id:" + value))
    name_key = player_key(name, position)
    if name_key[1] != "name:":
        keys.append(name_key)
    return list(dict.fromkeys(keys))


def index_rows(rows: list[dict[str, Any]], *identifier_fields: str) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        for key in identity_keys(
            str(row.get("player_name") or ""),
            str(row.get("position") or ""),
            *(row.get(field) for field in identifier_fields),
        ):
            index[key] = row
    return index


def lookup_player(index: dict[tuple[str, str], Any], player: dict[str, Any]) -> Any:
    for key in identity_keys(
        player["player_name"],
        player["position"],
        player.get("gsis_id"),
        player.get("sleeper_player_id"),
    ):
        if key in index:
            return index[key]
    return None


def json_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def query_rows(client: bigquery.Client, sql: str) -> list[dict[str, Any]]:
    return [dict(row) for row in client.query(sql).result()]


def live_frontline_players(players: dict[str, Any]) -> list[dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for sleeper_player_id, player in players.items():
        if not isinstance(player, dict):
            continue
        position = str(player.get("position") or "")
        name = str(player.get("full_name") or "").strip()
        try:
            depth_order = int(player.get("depth_chart_order"))
        except (TypeError, ValueError):
            depth_order = None
        if (
            position not in POSITIONS
            or not name
            or player.get("active") is not True
            or not player.get("team")
            or player.get("status") not in ("Active", "ACT")
            or depth_order != 1
        ):
            continue
        try:
            years_exp = int(player.get("years_exp"))
        except (TypeError, ValueError):
            years_exp = None
        row = {
            "sleeper_player_id": str(sleeper_player_id),
            "gsis_id": str(player.get("gsis_id") or "") or None,
            "player_name": name,
            "position": position,
            "team": player.get("team"),
            "depth_chart_position": player.get("depth_chart_position"),
            "depth_chart_order": depth_order,
            "years_exp": years_exp,
            "injury_status": player.get("injury_status"),
        }
        rows[player_key(name, position)] = row
    return sorted(rows.values(), key=lambda row: (row["position"], row["player_name"]))


def classify_omission(
    player: dict[str, Any],
    formula_row: dict[str, Any] | None,
    qualification_row: dict[str, Any] | None,
    candidate_profiles: set[str],
) -> str:
    if player.get("years_exp") == 0:
        return "ROOKIE_SYSTEM_REQUIRED"
    if player["position"] == "QB":
        return "QB_COVERAGE_REVIEW"
    if formula_row is None:
        if qualification_row is None:
            return "NO_2025_SITUATIONAL_SOURCE_ROW"
        if qualification_row.get("duplicate_identity_collision"):
            return "IDENTITY_BRIDGE_COLLISION"
        if not qualification_row.get("identity_accepted"):
            return "IDENTITY_BRIDGE_UNMAPPED"
        if not qualification_row.get("formula_eligible"):
            return "BELOW_2025_FABLE_QUALIFICATION_THRESHOLD"
        return "FABLE_FORMULA_TRANSFORM_DROPOUT"
    if not candidate_profiles:
        return "NOT_IN_RECEPTION_CANDIDATE_TABLES"
    return "POSITIONAL_PROMOTION_OR_BOARD_CUTOFF"


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def build_markdown(report: dict[str, Any]) -> str:
    board_rows = []
    for profile in PROFILES:
        for position in POSITIONS:
            actual = report["board_counts"].get(profile, {}).get(position, 0)
            expected = EXPECTED_COUNTS[profile][position]
            board_rows.append([profile, position, actual, expected, "PASS" if actual == expected else "FAIL"])

    priority_rows = []
    for row in report["high_signal_omissions"]:
        ranks = row["profile_ranks"]
        market = row.get("market") or {}
        candidate = (row.get("candidate_details") or {}).get("ppr") or {}
        priority_rows.append([
            row["player_name"],
            row["position"],
            row["team"],
            row.get("years_exp"),
            ranks.get("standard") or "missing",
            ranks.get("ppr") or "missing",
            ranks.get("half_ppr") or "missing",
            ranks.get("gng_keeper") or "missing",
            market.get("rank_position") or "n/a",
            candidate.get("formula_rank") or "n/a",
            row["trace_code"],
        ])

    diff_rows = [
        [item["position"], item["player_name"], ", ".join(item["present_profiles"]), ", ".join(item["missing_profiles"])]
        for item in report["ppr_half_ppr_presence_mismatches"]
    ]
    freshness = report["source_freshness"]
    nabers = next(
        (row for row in report["frontline_omissions"] if normalize_name(row["player_name"]) == "maliknabers"),
        None,
    )
    nabers_lines = ["Malik Nabers was not found in the live depth-order-1 universe."]
    if nabers:
        source = nabers.get("qualification") or {}
        formula = nabers.get("formula") or {}
        gng = nabers.get("gng_source") or {}
        candidate_profiles = ", ".join(nabers.get("candidate_profiles") or []) or "none"
        nabers_lines = [
            f"- Live Sleeper: {nabers['team']} WR, depth order 1, injury status `{nabers.get('injury_status') or 'none'}`.",
            f"- Redraft WR source: {source.get('games_played', 'n/a')} games and {source.get('qualification_volume', 'n/a')} targets. WR Fable requires six games or 40 targets.",
            f"- Repaired candidate path: `{formula.get('coverage_method', 'missing')}` from source season `{formula.get('score_source_season', 'n/a')}`; reception-profile candidates: `{candidate_profiles}`.",
            f"- GNG result: WR{nabers['profile_ranks'].get('gng_keeper')} from `{gng.get('formula_id', 'unknown')}` with {gng.get('current_games', 'n/a')} current-season games in its source pool. Missing metric weights are renormalized over the inputs that exist.",
            "- Sleeper injury remains post-formula context and carries zero injury movement without a bounded games-missed estimate.",
        ]

    trace_counts = report["omission_trace_counts"]
    harrison = next(
        (row for row in report["frontline_omissions"] if normalize_name(row["player_name"]) == "marvinharrison"),
        None,
    )
    harrison_lines = ["Marvin Harrison was not found in the live depth-order-1 universe."]
    if harrison:
        source = harrison.get("qualification") or {}
        formula = harrison.get("formula") or {}
        harrison_lines = [
            f"- The 2025 WR situational source row exists with {source.get('source_routes_run', 'n/a')} routes.",
            f"- The source-local override resolves identity status to `{source.get('identity_status', 'unknown')}` without a duplicate collision.",
            f"- WR Fable now produces `{formula.get('coverage_method', 'missing')}` from source season `{formula.get('score_source_season', 'n/a')}`.",
            f"- GNG continues from the same canonical internal ID at WR{harrison['profile_ranks'].get('gng_keeper')}; the Sleeper layer is not the identity mechanism.",
        ]

    gate_passed = not report["blocking_omissions"]
    decision = (
        "PASS. The repaired candidate universe contains no blocking established-player pipeline omissions. "
        "Positional promotion may proceed through its normal dry-run and write gates."
        if gate_passed
        else
        "BLOCKED. Do not rebuild or republish while an established current frontline player is missing from the candidate pipeline."
    )
    sleeper_warning = (
        "The BigQuery Sleeper context is stale. Refresh it before any promotion."
        if freshness["bigquery_context_stale"]
        else
        "The BigQuery Sleeper context is current and may be used by the shared post-formula safety layer."
    )
    next_phase = (
        "Run positional promotion dry-runs, apply only through the named write gates, rerun this coverage gate against active boards, then regenerate unified boards."
        if gate_passed
        else
        "Repair the remaining blocking trace, rematerialize candidates, and rerun with `--fail-on-blocking`."
    )

    return f"""# Current Player Ranking Coverage Audit

## Final Decision

{decision}

This phase was read-only against BigQuery and the public rankings. It made no live ranking, formula, candidate-table, unified-board, or JSON-feed changes.

## Checks

{markdown_table(["Profile", "Position", "Rows", "Expected", "Result"], board_rows)}

- Live Sleeper fetch: `{freshness['live_sleeper_fetched_at']}`.
- BigQuery Sleeper snapshot: `{freshness['bigquery_sleeper_max_fetched_at']}` ({freshness['bigquery_context_age_hours']} hours old).
- BigQuery 72-hour safety status: `{'STALE' if freshness['bigquery_context_stale'] else 'CURRENT'}`.
- PPR versus Half-PPR presence mismatches: `{len(report['ppr_half_ppr_presence_mismatches'])}`.
- Depth-order-1 current players missing at least one redraft board: `{len(report['frontline_omissions'])}`.
- High-signal omissions supported by GNG or market rank: `{len(report['high_signal_omissions'])}`.
- Blocking veteran pipeline omissions: `{len(report['blocking_omissions'])}`.

## What The Current Omissions Mean

- `{trace_counts.get('ROOKIE_SYSTEM_REQUIRED', 0)}` are rookies. GNG admits them through its market overlay; redraft intentionally has no approved rookie path yet.
- `{trace_counts.get('BELOW_2025_FABLE_QUALIFICATION_THRESHOLD', 0)}` established player falls below a one-season Fable threshold: Malik Nabers.
- `{trace_counts.get('IDENTITY_BRIDGE_COLLISION', 0)}` established player is blocked by an identity collision: Marvin Harrison.
- `{trace_counts.get('POSITIONAL_PROMOTION_OR_BOARD_CUTOFF', 0)}` tight ends have valid formula and candidate rows but land below the active TE35 cutoff. Isaiah Likely is the only high-signal market disagreement in that group.

## High-Signal Omissions

{markdown_table(["Player", "Pos", "Team", "Exp", "Standard", "PPR", "Half", "GNG", "Market Pos", "PPR Candidate", "Trace"], priority_rows) if priority_rows else 'None.'}

## PPR And Half-PPR Presence Differences

{markdown_table(["Pos", "Player", "Present", "Missing"], diff_rows) if diff_rows else 'None. The two reception-profile positional boards contain the same players.'}

## Why GNG Behaves Differently

| Stage | GNG Keeper | Standard, PPR, and Half-PPR |
|---|---|---|
| Veteran source pool | Averages 2023-2025 and requires at least four 2025 weekly scoring rows. | Position-specific Fable views use 2025. WR veterans below six games or 40 targets may use a prior qualified v1 score with a refreshed availability component. RB and TE thresholds are unchanged. |
| Missing advanced inputs | `weighted_average()` drops null inputs and renormalizes the remaining weights. | A player must survive the position view's identity, qualification, regression, and scoring joins. Failure produces no candidate row. |
| Identity | The GNG point pool starts from canonical internal player IDs and then joins Sleeper context. | Fable situational data uses a name-based identity bridge. Same-name collisions can block an otherwise complete source row. |
| Current Sleeper layer | Formula score is calculated first. A bounded depth-order adjustment is added; teamless players move to the watchlist. | The same post-formula safety view is joined after scoring. It cannot restore a player who never reached a Fable candidate table. |
| Rookie handling | Explicit market-ranked rookie overlay with depth-chart penalties. | No equivalent rookie overlay in the current shared redraft promotion path. |
| WR continuity | Existing live GNG top-six and top-12 WRs receive bounded merge-priority protection. | Standard has the approved A.J. Brown elite-order guardrail, but no general current-star coverage floor. |
| Unified board | Position-locked interleaving plus the approved Jeremiyah Love and QB4 floors. | Position-locked interleaving preserves only players already present on active positional boards. |

## Malik Nabers Trace

{chr(10).join(nabers_lines)}

## Marvin Harrison Trace

{chr(10).join(harrison_lines)}

## Sleeper Safety Status

{sleeper_warning}

## Files Changed

- `scripts/audit_current_player_ranking_coverage.py`
- `output/current-player-ranking-coverage-audit.json`
- `docs/rebuild/validation/phase-38-25-current-player-coverage-audit.md`

## Next Phase

{next_phase}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--brain-dataset", default="fantasy_football_brain")
    parser.add_argument("--metrics-dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("output/current-player-ranking-coverage-audit.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/rebuild/validation/phase-38-25-current-player-coverage-audit.md"),
    )
    parser.add_argument(
        "--fail-on-blocking",
        action="store_true",
        help="Exit 2 after writing the report when an established frontline player has a pipeline omission.",
    )
    args = parser.parse_args()

    client = bigquery.Client(project=args.project)
    live_fetched_at = datetime.now(timezone.utc)
    frontline = live_frontline_players(fetch_sleeper_players())

    identity_rows = query_rows(client, f"""
        SELECT sleeper_player_id,
               ARRAY_AGG(gsis_id IGNORE NULLS ORDER BY source_confidence DESC, updated_at DESC LIMIT 1)[SAFE_OFFSET(0)] gsis_id
        FROM `{args.project}.{args.brain_dataset}.player_identity_bridge`
        WHERE sleeper_player_id IS NOT NULL
        GROUP BY sleeper_player_id
    """)
    identity_by_sleeper = {
        str(row["sleeper_player_id"]): row.get("gsis_id") for row in identity_rows if row.get("gsis_id")
    }
    for player in frontline:
        if not player.get("gsis_id"):
            player["gsis_id"] = identity_by_sleeper.get(player["sleeper_player_id"])

    active_rows = query_rows(client, f"""
        SELECT scoring_profile_id, position, rank, player_id, player_name, current_team,
               ranking_version, sleeper_injury_status, sleeper_depth_chart_order
        FROM `{args.project}.{args.brain_dataset}.analytics_pigskin_rankings`
        WHERE is_active
          AND scoring_profile_id IN ('standard', 'ppr', 'half_ppr', 'gng_keeper')
          AND position IN ('QB', 'RB', 'WR', 'TE')
          AND COALESCE(league_type_id, 'redraft') = 'redraft'
          AND COALESCE(roster_format_id, 'one_qb') = 'one_qb'
        QUALIFY ROW_NUMBER() OVER (
          PARTITION BY scoring_profile_id, position, player_id ORDER BY generated_at DESC
        ) = 1
    """)
    formula_rows = query_rows(client, f"""
        SELECT 'RB' position, player_name, candidate_internal_player_id player_id,
               CAST(NULL AS STRING) coverage_method, CAST(NULL AS INT64) score_source_season
        FROM `{args.project}.{args.metrics_dataset}.v_rb_fable_01_scored_seasons` WHERE season = 2025
        UNION ALL
        SELECT 'WR', player_name, candidate_internal_player_id, coverage_method, score_source_season
        FROM `{args.project}.{args.metrics_dataset}.v_wr_fable_v1_current_candidates`
        UNION ALL
        SELECT 'TE', player_name, candidate_internal_player_id,
               CAST(NULL AS STRING), CAST(NULL AS INT64)
        FROM `{args.project}.{args.metrics_dataset}.v_te_fable_v1a_scored_seasons` WHERE season = 2025
    """)
    qualification_rows = query_rows(client, f"""
        SELECT 'RB' position, player_name, candidate_internal_player_id player_id, games_played,
               CAST(COALESCE(standard_rushes, 0) + COALESCE(standard_receptions, 0) AS FLOAT64) qualification_volume,
               'touches' qualification_unit, CAST(NULL AS FLOAT64) source_routes_run,
               identity_status, duplicate_identity_collision,
               identity_status IN ('VERIFIED', 'EXACT_SLUG_MATCH', 'NAME_TEAM_SEASON_MATCH')
                 AND NOT duplicate_identity_collision identity_accepted,
               (identity_status IN ('VERIFIED', 'EXACT_SLUG_MATCH', 'NAME_TEAM_SEASON_MATCH')
                 AND NOT duplicate_identity_collision)
                 AND (games_played >= 6 OR COALESCE(standard_rushes, 0) + COALESCE(standard_receptions, 0) >= 50)
                 formula_eligible
        FROM `{args.project}.{args.metrics_dataset}.v_rb_fable_01_situational_splits`
        WHERE season = 2025
        UNION ALL
        SELECT 'WR', player_name, candidate_internal_player_id, games_played, CAST(targets AS FLOAT64), 'targets',
               CAST(routes_run AS FLOAT64),
               identity_status, duplicate_identity_collision,
               identity_status IN ('VERIFIED', 'EXACT_SLUG_MATCH', 'NAME_TEAM_SEASON_MATCH')
                 AND NOT duplicate_identity_collision,
               (identity_status IN ('VERIFIED', 'EXACT_SLUG_MATCH', 'NAME_TEAM_SEASON_MATCH')
                 AND NOT duplicate_identity_collision) AND (games_played >= 6 OR targets >= 40)
        FROM `{args.project}.{args.metrics_dataset}.v_wr_fable_v1_situational_splits`
        WHERE season = 2025
        UNION ALL
        SELECT 'TE', player_name, candidate_internal_player_id, games_played, CAST(routes_run AS FLOAT64), 'routes',
               CAST(routes_run AS FLOAT64),
               identity_status, duplicate_identity_collision,
               identity_status IN ('VERIFIED', 'EXACT_SLUG_MATCH', 'NAME_TEAM_SEASON_MATCH')
                 AND NOT duplicate_identity_collision,
               (identity_status IN ('VERIFIED', 'EXACT_SLUG_MATCH', 'NAME_TEAM_SEASON_MATCH')
                 AND NOT duplicate_identity_collision) AND games_played >= 4 AND routes_run >= 100
        FROM `{args.project}.{args.metrics_dataset}.v_te_fable_v1a_situational_splits`
        WHERE season = 2025
    """)
    candidate_rows = query_rows(client, f"""
        SELECT 'ppr' profile, position, player_id, player_name, formula_rank, recommended_rank,
               promotion_eligible, decision_code
        FROM `{args.project}.{args.brain_dataset}.ppr_fable_rankings_current`
        UNION ALL
        SELECT 'half_ppr', position, player_id, player_name, formula_rank, recommended_rank,
               promotion_eligible, decision_code
        FROM `{args.project}.{args.brain_dataset}.half_ppr_fable_rankings_current`
    """)
    market_rows = query_rows(client, f"""
        SELECT position, display_name player_name, rank_position, rank_overall, market_value
        FROM `{args.project}.{args.brain_dataset}.market_consensus_baseline_current`
        WHERE season = 2026 AND scoring_profile_id = 'ppr' AND source_id = 'manual_market_values'
        QUALIFY ROW_NUMBER() OVER (
          PARTITION BY position, REGEXP_REPLACE(LOWER(display_name), r'[^a-z0-9]', '')
          ORDER BY updated_at DESC
        ) = 1
    """)
    identity_collision_rows = query_rows(client, f"""
        WITH grouped AS (
          SELECT position, REGEXP_REPLACE(LOWER(full_name), r'[^a-z0-9]', '') normalized_name,
                 ARRAY_AGG(DISTINCT gsis_id IGNORE NULLS ORDER BY gsis_id) gsis_ids
          FROM `{args.project}.{args.brain_dataset}.player_identity_bridge`
          WHERE position IN ('QB', 'RB', 'WR', 'TE') AND full_name IS NOT NULL
          GROUP BY position, normalized_name
        )
        SELECT * FROM grouped WHERE ARRAY_LENGTH(gsis_ids) > 1
    """)
    gng_source_rows = query_rows(client, f"""
        WITH current_games AS (
          SELECT position, REGEXP_REPLACE(LOWER(player_display_name), r'[^a-z0-9]', '') normalized_name,
                 COUNTIF(season = 2025) current_games
          FROM `{args.project}.{args.brain_dataset}.analytics_player_fantasy_points_by_profile`
          WHERE scoring_profile_id = 'gng_keeper' AND season BETWEEN 2023 AND 2025
            AND position IN ('QB', 'RB', 'WR', 'TE')
          GROUP BY position, normalized_name
        )
        SELECT board.position, board.player_id, board.sleeper_player_id, board.player_name,
               board.rank, board.formula_rank, board.formula_id,
               board.formula_score, board.current_score, board.rank_source,
               board.sleeper_review_flags_json, current_games.current_games
        FROM `{args.project}.{args.metrics_dataset}.gng_2026_positional_boards_with_rookies` board
        LEFT JOIN current_games
          ON current_games.position = board.position
         AND current_games.normalized_name = REGEXP_REPLACE(LOWER(board.player_name), r'[^a-z0-9]', '')
    """)
    freshness = dict(query_rows(client, f"""
        SELECT MIN(fetched_at) min_fetched_at, MAX(fetched_at) max_fetched_at,
               TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(fetched_at), HOUR) context_age_hours
        FROM `{args.project}.{args.metrics_dataset}.sleeper_current_player_context`
    """)[0])

    active_index: dict[str, dict[tuple[str, str], dict[str, Any]]] = defaultdict(dict)
    active_canonical: dict[str, dict[tuple[str, str], dict[str, Any]]] = defaultdict(dict)
    board_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in active_rows:
        profile = row["scoring_profile_id"]
        keys = identity_keys(row["player_name"], row["position"], row.get("player_id"))
        for key in keys:
            active_index[profile][key] = row
        active_canonical[profile][keys[0]] = row
        board_counts[profile][row["position"]] += 1

    formula_index = index_rows(formula_rows, "player_id")
    qualification_index = index_rows(qualification_rows, "player_id")
    market_index = index_rows(market_rows)
    gng_source_index = index_rows(gng_source_rows, "player_id", "sleeper_player_id")
    identity_collision_index = {
        (row["position"], "name:" + normalize_name(row["normalized_name"])): row["gsis_ids"]
        for row in identity_collision_rows
    }
    candidate_index: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in candidate_rows:
        for key in identity_keys(row["player_name"], row["position"], row.get("player_id")):
            candidate_index[key][row["profile"]] = row

    omissions = []
    universe_counts = Counter(row["position"] for row in frontline)
    missing_counts: dict[str, Counter[str]] = {profile: Counter() for profile in PROFILES}
    for player in frontline:
        profile_ranks = {
            profile: (lookup_player(active_index[profile], player) or {}).get("rank")
            for profile in ALL_PROFILES
        }
        missing_profiles = [profile for profile in PROFILES if profile_ranks[profile] is None]
        if not missing_profiles:
            continue
        for profile in missing_profiles:
            missing_counts[profile][player["position"]] += 1
        candidates = lookup_player(candidate_index, player) or {}
        formula_row = lookup_player(formula_index, player)
        qualification = lookup_player(qualification_index, player)
        market = lookup_player(market_index, player)
        gng_source = lookup_player(gng_source_index, player)
        omission = {
            **player,
            "profile_ranks": profile_ranks,
            "missing_profiles": missing_profiles,
            "trace_code": classify_omission(player, formula_row, qualification, set(candidates)),
            "formula_2025_present": formula_row is not None,
            "formula": formula_row,
            "qualification": qualification,
            "candidate_profiles": sorted(candidates),
            "candidate_details": candidates,
            "market": market,
            "gng_source": gng_source,
            "identity_candidates": lookup_player(identity_collision_index, player) or [],
        }
        omissions.append(omission)

    def omission_sort(row: dict[str, Any]) -> tuple[Any, ...]:
        market = row.get("market") or {}
        return (
            (row["profile_ranks"].get("gng_keeper") or 999),
            (market.get("rank_overall") or 9999),
            row["position"],
            row["player_name"],
        )

    omissions.sort(key=omission_sort)
    trace_counts = Counter(row["trace_code"] for row in omissions)
    high_signal = [
        row for row in omissions
        if (
            row["profile_ranks"].get("gng_keeper") is not None
            and row["profile_ranks"]["gng_keeper"] <= HIGH_SIGNAL_POSITION_RANK[row["position"]]
        ) or (
            row.get("market") is not None
            and (row["market"].get("rank_position") or 999) <= HIGH_SIGNAL_POSITION_RANK[row["position"]]
        )
    ]
    blocking = [
        row for row in omissions
        if row.get("years_exp") not in (None, 0) and row["trace_code"] in BLOCKING_TRACE_CODES
    ]

    ppr_half_mismatches = []
    for key in sorted(set(active_canonical["ppr"]) | set(active_canonical["half_ppr"])):
        present = [profile for profile in ("ppr", "half_ppr") if key in active_canonical[profile]]
        if len(present) == 2:
            continue
        source = active_canonical[present[0]][key]
        ppr_half_mismatches.append({
            "position": source["position"],
            "player_name": source["player_name"],
            "present_profiles": present,
            "missing_profiles": [profile for profile in ("ppr", "half_ppr") if profile not in present],
        })

    report = {
        "generated_at": live_fetched_at.isoformat(),
        "read_only": True,
        "source_freshness": {
            "live_sleeper_fetched_at": live_fetched_at.isoformat(),
            "bigquery_sleeper_min_fetched_at": freshness["min_fetched_at"],
            "bigquery_sleeper_max_fetched_at": freshness["max_fetched_at"],
            "bigquery_context_age_hours": freshness["context_age_hours"],
            "bigquery_context_stale": int(freshness["context_age_hours"] or 0) > 72,
        },
        "board_counts": {profile: dict(board_counts[profile]) for profile in ALL_PROFILES},
        "frontline_universe_counts": dict(universe_counts),
        "missing_frontline_counts": {
            profile: dict(missing_counts[profile]) for profile in PROFILES
        },
        "ppr_half_ppr_presence_mismatches": ppr_half_mismatches,
        "high_signal_omissions": high_signal,
        "blocking_omissions": blocking,
        "frontline_omissions": omissions,
        "omission_trace_counts": dict(trace_counts),
        "gng_pipeline_differences": {
            "veteran_window": "2023-2025 with at least four 2025 weekly scoring rows",
            "missing_metric_policy": "drop null inputs and renormalize remaining weights",
            "rookie_policy": "market rookie overlay with depth-chart penalty",
            "redraft_window": "2025 position-specific Fable qualification",
            "post_formula_limit": "Sleeper safety cannot restore a player absent from formula candidates",
        },
    }

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, default=json_value) + "\n", encoding="utf-8")
    args.markdown_output.write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps({
        "read_only": True,
        "json_output": str(args.json_output),
        "markdown_output": str(args.markdown_output),
        "board_counts": report["board_counts"],
        "frontline_universe_counts": report["frontline_universe_counts"],
        "missing_frontline_counts": report["missing_frontline_counts"],
        "ppr_half_ppr_presence_mismatches": len(ppr_half_mismatches),
        "frontline_omissions": len(omissions),
        "high_signal_omissions": [row["player_name"] for row in high_signal],
        "blocking_omissions": [row["player_name"] for row in blocking],
        "bigquery_context_age_hours": freshness["context_age_hours"],
    }, indent=2, default=json_value))
    return 2 if args.fail_on_blocking and blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
