"""Pure label logic for the availability decision pilot.

Every date, schedule, and count used by the availability pilot is computed here
in code. Nothing in this module calls BigQuery or a model; the build script
fetches compact extracts and passes them in.

Grain of a label row: one official injury report entry per player, season,
week, and team for a regular-season game.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

SKILL_POSITIONS = ("QB", "RB", "WR", "TE")
REPORT_STATUSES = ("Out", "Doubtful", "Questionable", "Probable")
PRACTICE_CODES = {
    "did not participate in practice": "DNP",
    "limited participation in practice": "LP",
    "full participation in practice": "FP",
    "out (definitely will not play)": "DNP",
}
REPORT_SEVERITY = {"Out": 4, "Doubtful": 3, "Questionable": 2, "Probable": 1, "NONE": 0}
MISSED_BUCKETS = ("0", "1", "2_4", "5_plus_or_season")
# Keyword groups for the body part feature. Order matters: the first match wins,
# so "not injury related" is checked before any anatomical word it may contain.
BODY_PART_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("not_injury", ("not injury related", "resting", "rest", "personal", "coach's decision")),
    ("illness", ("illness",)),
    ("concussion", ("concussion", "head")),
    ("knee", ("knee", "acl", "mcl", "patella")),
    ("ankle", ("ankle",)),
    ("hamstring", ("hamstring",)),
    ("foot", ("foot", "toe", "heel", "achilles", "plantar")),
    ("groin_hip", ("groin", "hip", "core", "abdomen", "oblique", "hernia", "pelvis", "glute")),
    ("leg_muscle", ("calf", "quad", "thigh", "shin", "fibula", "tibia", "lower leg")),
    ("upper_body", ("shoulder", "pectoral", "chest", "rib", "collarbone", "biceps", "triceps", "tricep", "elbow", "forearm", "neck", "back", "stinger")),
    ("hand_wrist", ("hand", "wrist", "finger", "thumb")),
)
NOT_INJURY_MARKERS = ("not injury related", "resting", "personal", "coach's decision")


def normalize_report_status(value: str | None) -> str:
    text = (value or "").strip()
    return text if text in REPORT_STATUSES else "NONE"


def normalize_practice_status(value: str | None) -> str:
    return PRACTICE_CODES.get((value or "").strip().lower(), "NONE")


def body_part_group(primary: str | None) -> str:
    text = (primary or "").strip().lower()
    if not text:
        return "unknown"
    for group, words in BODY_PART_GROUPS:
        if any(word in text for word in words):
            return group
    return "other"


def is_not_injury_related(*parts: str | None) -> bool:
    text = " ".join((part or "").lower() for part in parts)
    return any(marker in text for marker in NOT_INJURY_MARKERS)


def position_group(position: str | None) -> str:
    value = (position or "").upper()
    return value if value in SKILL_POSITIONS else "OTHER"


def missed_bucket(games_missed: int) -> str:
    if games_missed <= 0:
        return "0"
    if games_missed == 1:
        return "1"
    if games_missed <= 4:
        return "2_4"
    return "5_plus_or_season"


def resolve_bucket(games_missed: int, censor_reason: str | None) -> str | None:
    """Return the missed bucket, or None when censoring leaves it ambiguous.

    A season-end censor with two or more games missed is a rest-of-season
    absence, which is the literal meaning of the top bucket. A data-horizon
    censor (games not yet played) resolves only once five games are missed.
    """
    if censor_reason is None:
        return missed_bucket(games_missed)
    if games_missed >= 5:
        return "5_plus_or_season"
    if censor_reason == "season_end" and games_missed >= 2:
        return "5_plus_or_season"
    return None


@dataclass(frozen=True)
class TeamGame:
    season: int
    team: str
    week: int
    game_id: str


@dataclass(frozen=True)
class InjuryRow:
    season: int
    week: int
    team: str
    gsis_id: str
    player_name: str
    position: str
    report_status: str | None
    practice_status: str | None
    primary_injury: str | None
    secondary_injury: str | None


def team_schedule(games: Iterable[TeamGame]) -> dict[tuple[int, str], list[TeamGame]]:
    """Regular-season games per team-season in week order. Byes are simply absent."""
    by_team: dict[tuple[int, str], list[TeamGame]] = {}
    for game in games:
        by_team.setdefault((game.season, game.team), []).append(game)
    for key in by_team:
        by_team[key].sort(key=lambda g: g.week)
    return by_team


def dedupe_injury_rows(rows: Iterable[InjuryRow]) -> list[InjuryRow]:
    """Keep the most severe entry per player, season, week, and team."""
    best: dict[tuple[str, int, int, str], InjuryRow] = {}
    for row in rows:
        key = (row.gsis_id, row.season, row.week, row.team)
        current = best.get(key)
        rank = (
            REPORT_SEVERITY[normalize_report_status(row.report_status)],
            {"DNP": 3, "LP": 2, "FP": 1, "NONE": 0}[normalize_practice_status(row.practice_status)],
        )
        if current is None:
            best[key] = row
            continue
        current_rank = (
            REPORT_SEVERITY[normalize_report_status(current.report_status)],
            {"DNP": 3, "LP": 2, "FP": 1, "NONE": 0}[normalize_practice_status(current.practice_status)],
        )
        if rank > current_rank:
            best[key] = row
    return sorted(best.values(), key=lambda r: (r.gsis_id, r.season, r.week))


def build_label_rows(
    injury_rows: Iterable[InjuryRow],
    schedule: Mapping[tuple[int, str], list[TeamGame]],
    played: Mapping[tuple[str, int, int], str],
    roster_status: Mapping[tuple[str, int, int], tuple[str | None, str | None]],
    last_observed_week: Mapping[int, int] | None = None,
) -> list[dict]:
    """Compute features and labels for each report row.

    ``played`` maps (gsis_id, season, week) to the team he took a snap for.
    ``roster_status`` maps (gsis_id, season, week) to (team, weekly status).
    ``last_observed_week`` caps a season whose later games have no outcome yet;
    games after that week are a data horizon, not missed games.
    """
    rows = dedupe_injury_rows(injury_rows)
    horizon = dict(last_observed_week or {})
    by_player: dict[tuple[str, int], list[InjuryRow]] = {}
    for row in rows:
        by_player.setdefault((row.gsis_id, row.season), []).append(row)

    out: list[dict] = []
    for (gsis_id, season), player_rows in by_player.items():
        previous: tuple[str, int, str] | None = None  # (team, index, report status)
        episode_start_week = 0
        weeks_in_episode = 0
        for row in player_rows:
            games = schedule.get((season, row.team), [])
            weeks = [g.week for g in games]
            if row.week not in weeks or row.week > horizon.get(season, 99):
                continue
            index = weeks.index(row.week)
            observed = [g for g in games if g.week <= horizon.get(season, 99)]

            consecutive = previous is not None and previous[0] == row.team and index == previous[1] + 1
            if consecutive:
                weeks_in_episode += 1
                prev_played = (gsis_id, season, games[index - 1].week) in played
                prev_state = "LISTED_PLAYED" if prev_played else "LISTED_MISSED"
                prev_status = previous[2]
            else:
                episode_start_week = row.week
                weeks_in_episode = 1
                prev_state = "NOT_LISTED"
                prev_status = "NOT_LISTED"

            games_missed = 0
            return_week: int | None = None
            return_team: str | None = None
            censor_reason: str | None = None
            for later in observed[index:]:
                team_played = played.get((gsis_id, season, later.week))
                if team_played is not None:
                    return_week = later.week
                    return_team = team_played
                    break
                games_missed += 1
            if return_week is None:
                season_complete = len(observed) == len(games)
                censor_reason = "season_end" if season_complete else "data_horizon"

            end_week = return_week if return_week is not None else (observed[-1].week if observed else row.week)
            between = [
                roster_status.get((gsis_id, season, week), (None, None))
                for week in range(row.week, end_week + 1)
            ]
            team_changed = (return_team is not None and return_team != row.team) or any(
                team is not None and team != row.team for team, _ in between
            )
            was_cut = any(status == "CUT" for _, status in between)

            next_game = games[index + 1] if index + 1 < len(games) else None
            played_next: bool | None = None
            if next_game is not None and next_game.week <= horizon.get(season, 99):
                played_next = (gsis_id, season, next_game.week) in played

            primary = row.primary_injury
            label_bucket = resolve_bucket(games_missed, censor_reason)
            this_team, this_roster_status = roster_status.get((gsis_id, season, row.week), (None, None))
            not_injury = is_not_injury_related(primary, row.secondary_injury)
            out.append(
                {
                    "gsis_id": gsis_id,
                    "season": season,
                    "week": row.week,
                    "team": row.team,
                    "game_id": games[index].game_id,
                    "player_name": row.player_name,
                    "position": row.position,
                    "position_group": position_group(row.position),
                    "report_status": normalize_report_status(row.report_status),
                    "practice_status": normalize_practice_status(row.practice_status),
                    "primary_body_part": primary,
                    "secondary_body_part": row.secondary_injury,
                    "body_part_group": body_part_group(primary),
                    "prev_week_state": prev_state,
                    "prev_week_status": prev_status,
                    "episode_id": f"{gsis_id}-{season}-w{episode_start_week:02d}",
                    "weeks_in_episode": weeks_in_episode,
                    "team_game_index": index + 1,
                    "team_games_in_season": len(games),
                    "games_remaining": len(games) - index,
                    "roster_status": this_roster_status,
                    "era_pre_2016": season <= 2015,
                    "played_this_game": (gsis_id, season, row.week) in played,
                    "played_next_game": played_next,
                    "games_missed_until_return": games_missed,
                    "return_week": return_week,
                    "censored": censor_reason is not None,
                    "censor_reason": censor_reason,
                    "missed_bucket": label_bucket,
                    "flag_team_change": team_changed,
                    "flag_cut": was_cut,
                    "flag_not_injury_related": not_injury,
                    "excluded_from_fit": team_changed or was_cut or not_injury,
                }
            )
            previous = (row.team, index, normalize_report_status(row.report_status))
    out.sort(key=lambda r: (r["season"], r["week"], r["team"], r["gsis_id"]))
    return out


BUCKET_MAX_GAMES = {"0": 0, "1": 1, "2_4": 4, "5_plus_or_season": 10_000}


def consistent_buckets(games_missed: int, resolved: str | None) -> list[str]:
    """Buckets still possible given what has been observed so far."""
    if resolved is not None:
        return [resolved]
    return [b for b in MISSED_BUCKETS if b != "0" and BUCKET_MAX_GAMES[b] >= games_missed]


def game_outcome(
    team_game_ids: list[str],
    played_game_ids: set[str],
    loaded_game_ids: set[str],
    season_complete: bool,
) -> dict | None:
    """Outcome from the target game onward, using only games whose snap counts are loaded.

    ``team_game_ids`` are the team's regular-season games from the target game
    to the end of the season, in order. Returns None while the target game has
    no snap data yet.
    """
    if not team_game_ids or team_game_ids[0] not in loaded_game_ids:
        return None
    games_missed = 0
    returned = False
    for game_id in team_game_ids:
        if game_id not in loaded_game_ids:
            break
        if game_id in played_game_ids:
            returned = True
            break
        games_missed += 1
    all_loaded = all(g in loaded_game_ids for g in team_game_ids)
    censor_reason = None if returned else ("season_end" if season_complete and all_loaded else "data_horizon")
    resolved = resolve_bucket(games_missed, censor_reason)
    return {
        "played": team_game_ids[0] in played_game_ids,
        "games_missed": games_missed,
        "censor_reason": censor_reason,
        "bucket": resolved,
        "possible_buckets": consistent_buckets(games_missed, resolved),
    }
