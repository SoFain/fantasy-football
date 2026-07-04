"""Scoring-profile-aware fantasy point calculation helpers."""

from __future__ import annotations

import copy
import json
import math
from typing import Any

from google.cloud import bigquery

from src.bigquery_guardrails import query_to_dataframe


DEFAULT_SCORING_SETTINGS = {
    "passing_yards": 0.04,
    "passing_tds": 4.0,
    "interceptions": -2.0,
    "passing_2pt_conversions": 2.0,
    "rushing_yards": 0.1,
    "rushing_tds": 6.0,
    "rushing_2pt_conversions": 2.0,
    "receptions": 0.0,
    "receiving_yards": 0.1,
    "receiving_tds": 6.0,
    "receiving_2pt_conversions": 2.0,
    "fumbles_lost": -2.0,
    "return_tds": 6.0,
    "bonuses": {},
    "kicker": {},
    "dst": {},
}

DEFAULT_PROFILE_RECEPTION_POINTS = {
    "standard": 0.0,
    "half_ppr": 0.5,
    "ppr": 1.0,
}

GNG_KEEPER_SOURCE_METADATA = {
    "source": "owner-supplied Sleeper league report",
    "source_league_id": "1369406895588143104",
    "season": 2026,
    "league_status_at_retrieval": "pre_draft",
}

GNG_KEEPER_SLEEPER_SCORING_SETTINGS = {
    "pass_yd": 0.02,
    "pass_td": 5.0,
    "pass_td_40p": 0.0,
    "pass_td_50p": 0.5,
    "pass_2pt": 2.0,
    "pass_int": -2.0,
    "pass_int_td": -4.0,
    "pass_sack": -1.0,
    "pass_cmp_40p": 0.5,
    "bonus_pass_cmp_25": 1.0,
    "bonus_pass_yd_300": 1.0,
    "bonus_pass_yd_400": 2.0,
    "rush_yd": 0.04,
    "rush_td": 6.0,
    "rush_td_40p": 0.0,
    "rush_td_50p": 1.0,
    "rush_40p": 1.0,
    "rush_fd": 0.1,
    "rush_2pt": 2.0,
    "bonus_rush_att_20": 1.0,
    "bonus_rush_yd_100": 1.0,
    "bonus_rush_yd_200": 2.0,
    "bonus_rush_rec_yd_200": 1.0,
    "rec": 0.1,
    "bonus_rec_wr": 0.1,
    "bonus_rec_te": 0.2,
    "rec_yd": 0.04,
    "rec_td": 6.0,
    "rec_td_40p": 0.0,
    "rec_td_50p": 0.5,
    "rec_40p": 0.5,
    "rec_fd": 0.1,
    "rec_2pt": 2.0,
    "bonus_rec_yd_100": 1.0,
    "bonus_rec_yd_200": 2.0,
    "fgm": 3.0,
    "fgm_0_19": 0.0,
    "fgm_20_29": 0.0,
    "fgm_30_39": 0.0,
    "fgm_40_49": 0.0,
    "fgm_50_59": 1.0,
    "fgm_60p": 2.0,
    "fgmiss": -1.0,
    "fgmiss_0_19": -4.0,
    "fgmiss_20_29": -3.0,
    "fgmiss_30_39": -2.0,
    "fgmiss_40_49": -1.0,
    "fgmiss_50_59": 0.0,
    "fgmiss_50p": 0.0,
    "fgmiss_60p": 0.0,
    "xpm": 1.0,
    "xpmiss": -2.0,
    "sack": 1.0,
    "int": 2.0,
    "fum_rec": 2.0,
    "ff": 0.0,
    "safe": 4.0,
    "blk_kick": 1.0,
    "def_td": 6.0,
    "def_st_td": 6.0,
    "def_st_ff": 1.0,
    "def_st_fum_rec": 1.0,
    "def_3_and_out": 0.5,
    "def_4_and_stop": 1.0,
    "tkl_loss": 0.0,
    "pts_allow_0": 8.0,
    "pts_allow_1_6": 6.0,
    "pts_allow_7_13": 4.0,
    "pts_allow_14_20": 2.0,
    "pts_allow_21_27": 0.0,
    "pts_allow_28_34": -3.0,
    "pts_allow_35p": -6.0,
    "yds_allow_0_100": 2.0,
    "yds_allow_100_199": 1.0,
    "yds_allow_300_349": -1.0,
    "yds_allow_350_399": -2.0,
    "yds_allow_400_449": -4.0,
    "yds_allow_450_499": -5.0,
    "yds_allow_500_549": -6.0,
    "yds_allow_550p": -7.0,
    "st_td": 6.0,
    "st_ff": 1.0,
    "st_fum_rec": 1.0,
    "kr_yd": 0.05,
    "pr_yd": 0.1,
    "fum": 0.0,
    "fum_lost": -2.0,
    "fum_rec_td": 6.0,
}

PROFILE_SETTING_ALIASES = {
    "reception": "receptions",
    "passing_td": "passing_tds",
    "rushing_td": "rushing_tds",
    "receiving_td": "receiving_tds",
    "pass_yd": "passing_yards",
    "pass_td": "passing_tds",
    "pass_int": "interceptions",
    "rush_yd": "rushing_yards",
    "rush_td": "rushing_tds",
    "rec": "receptions",
    "rec_yd": "receiving_yards",
    "rec_td": "receiving_tds",
    "fum_lost": "fumbles_lost",
}

STAT_ALIASES = {
    "passing_yards": ("passing_yards", "pass_yd", "pass_yds", "pass_yards"),
    "passing_tds": ("passing_tds", "passing_touchdowns", "pass_td", "pass_tds"),
    "interceptions": ("interceptions", "passing_interceptions", "interception", "ints", "int"),
    "passing_2pt_conversions": ("passing_2pt_conversions", "passing_2pt", "pass_2pt"),
    "rushing_yards": ("rushing_yards", "rush_yd", "rush_yds", "rush_yards"),
    "rushing_tds": ("rushing_tds", "rushing_touchdowns", "rush_td", "rush_tds"),
    "rushing_2pt_conversions": ("rushing_2pt_conversions", "rushing_2pt", "rush_2pt"),
    "receptions": ("receptions", "rec", "receiving_receptions"),
    "receiving_yards": ("receiving_yards", "rec_yd", "rec_yds", "receiving_yds"),
    "receiving_tds": ("receiving_tds", "receiving_touchdowns", "rec_td", "rec_tds"),
    "receiving_2pt_conversions": ("receiving_2pt_conversions", "receiving_2pt", "rec_2pt"),
    "fumbles_lost": ("fumbles_lost", "lost_fumbles", "fum_lost"),
    "return_tds": ("return_tds", "return_touchdowns", "st_td"),
}

SLEEPER_SCORING_KEY_MAP = {
    "pass_yd": "passing_yards",
    "pass_td": "passing_tds",
    "pass_int": "interceptions",
    "pass_2pt": "passing_2pt_conversions",
    "rush_yd": "rushing_yards",
    "rush_td": "rushing_tds",
    "rush_2pt": "rushing_2pt_conversions",
    "rec": "receptions",
    "rec_yd": "receiving_yards",
    "rec_td": "receiving_tds",
    "rec_2pt": "receiving_2pt_conversions",
    "fum_lost": "fumbles_lost",
    "st_td": "return_tds",
}


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    try:
        if isinstance(value, float) and math.isnan(value):
            return True
    except TypeError:
        return False
    return False


def _as_float(value: Any) -> float:
    if _is_missing(value):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _settings_from_profile(scoring_profile: dict[str, Any]) -> dict[str, Any]:
    settings = scoring_profile.get("settings") or scoring_profile.get("scoring_json") or scoring_profile
    merged = copy.deepcopy(DEFAULT_SCORING_SETTINGS)
    for raw_key, value in dict(settings).items():
        key = PROFILE_SETTING_ALIASES.get(raw_key, raw_key)
        if key in ("bonuses", "kicker", "dst", "unmapped_settings"):
            merged[key] = value or {}
        else:
            merged[key] = _as_float(value)
    return merged


def get_default_scoring_profile(profile_id: str) -> dict[str, Any]:
    """Return the local copy of the BigQuery seed scoring profile for offline use."""

    if profile_id == "gng_keeper":
        return get_gng_keeper_scoring_profile()
    if profile_id not in DEFAULT_PROFILE_RECEPTION_POINTS:
        raise ValueError(f"Unknown default scoring profile: {profile_id}")
    settings = copy.deepcopy(DEFAULT_SCORING_SETTINGS)
    settings["receptions"] = DEFAULT_PROFILE_RECEPTION_POINTS[profile_id]
    return {
        "scoring_profile_id": profile_id,
        "display_name": {
            "standard": "Standard",
            "half_ppr": "Half PPR",
            "ppr": "PPR",
        }[profile_id],
        "settings": settings,
        "unmapped_settings": {},
    }


def get_gng_keeper_scoring_profile() -> dict[str, Any]:
    """Return the owner-approved GNG Keeper Sleeper scoring profile."""

    profile = build_scoring_profile_from_sleeper_settings(GNG_KEEPER_SLEEPER_SCORING_SETTINGS)
    profile["scoring_profile_id"] = "gng_keeper"
    profile["display_name"] = "GNG Keeper"
    profile["source_metadata"] = dict(GNG_KEEPER_SOURCE_METADATA)
    profile["sleeper_scoring_settings"] = dict(GNG_KEEPER_SLEEPER_SCORING_SETTINGS)
    return profile


def _parse_profile_json(value: Any) -> dict[str, Any]:
    if _is_missing(value):
        return {}
    if isinstance(value, dict):
        return value
    text = str(value).strip()
    if not text:
        return {}
    return json.loads(text)


def load_scoring_profiles(
    client: bigquery.Client,
    dataset_id: str,
    profile_ids: list[str] | tuple[str, ...] | None = None,
) -> dict[str, dict[str, Any]]:
    """Load active scoring profiles from BigQuery."""

    filters = ["active IS TRUE"]
    query_parameters = []
    if profile_ids:
        filters.append("scoring_profile_id IN UNNEST(@profile_ids)")
        query_parameters.append(
            bigquery.ArrayQueryParameter("profile_ids", "STRING", list(profile_ids))
        )
    sql = f"""
    SELECT
        scoring_profile_id,
        display_name,
        TO_JSON_STRING(scoring_json) AS scoring_json_text
    FROM `{client.project}.{dataset_id}.scoring_profiles`
    WHERE {" AND ".join(filters)}
    ORDER BY scoring_profile_id
    """
    frame = query_to_dataframe(
        client,
        sql,
        component="fantasy_scoring",
        query_name="load_scoring_profiles",
        query_parameters=query_parameters,
    )
    profiles: dict[str, dict[str, Any]] = {}
    for row in frame.to_dict("records"):
        scoring_json = _parse_profile_json(row.get("scoring_json_text"))
        profiles[row["scoring_profile_id"]] = {
            "scoring_profile_id": row["scoring_profile_id"],
            "display_name": row.get("display_name"),
            "settings": scoring_json.get("settings", scoring_json),
            "unmapped_settings": scoring_json.get("unmapped_settings", {}),
        }
    return profiles


def build_scoring_profile_from_sleeper_settings(scoring_settings: dict[str, Any]) -> dict[str, Any]:
    """Convert Sleeper league scoring settings into the internal profile shape."""

    settings = {key: 0.0 for key in DEFAULT_SCORING_SETTINGS if key not in ("bonuses", "kicker", "dst")}
    settings["bonuses"] = {}
    settings["kicker"] = {}
    settings["dst"] = {}
    unmapped_settings = {}
    for sleeper_key, value in sorted((scoring_settings or {}).items()):
        internal_key = SLEEPER_SCORING_KEY_MAP.get(sleeper_key)
        if internal_key:
            settings[internal_key] = _as_float(value)
        else:
            unmapped_settings[sleeper_key] = value
    return {
        "scoring_profile_id": "sleeper_custom",
        "display_name": "Sleeper Custom",
        "settings": settings,
        "unmapped_settings": unmapped_settings,
    }


def normalize_stat_row(stat_row: dict[str, Any]) -> dict[str, Any]:
    """Normalize supported stat fields and record missing source fields."""

    normalized = {}
    missing_flags = []
    for canonical_field, aliases in STAT_ALIASES.items():
        found = False
        for alias in aliases:
            if alias in stat_row and not _is_missing(stat_row.get(alias)):
                normalized[canonical_field] = _as_float(stat_row.get(alias))
                found = True
                break
        if not found:
            normalized[canonical_field] = 0.0
            missing_flags.append(f"missing_{canonical_field}")
    normalized["missing_data_flags"] = missing_flags
    return normalized


def calculate_fantasy_breakdown(
    stat_row: dict[str, Any],
    scoring_profile: dict[str, Any],
) -> dict[str, Any]:
    normalized_stats = normalize_stat_row(stat_row)
    settings = _settings_from_profile(scoring_profile)

    passing_points = (
        normalized_stats["passing_yards"] * settings["passing_yards"]
        + normalized_stats["passing_tds"] * settings["passing_tds"]
        + normalized_stats["passing_2pt_conversions"] * settings["passing_2pt_conversions"]
    )
    rushing_points = (
        normalized_stats["rushing_yards"] * settings["rushing_yards"]
        + normalized_stats["rushing_tds"] * settings["rushing_tds"]
        + normalized_stats["rushing_2pt_conversions"] * settings["rushing_2pt_conversions"]
    )
    receiving_points = (
        normalized_stats["receiving_yards"] * settings["receiving_yards"]
        + normalized_stats["receiving_tds"] * settings["receiving_tds"]
        + normalized_stats["receiving_2pt_conversions"] * settings["receiving_2pt_conversions"]
    )
    reception_points = normalized_stats["receptions"] * settings["receptions"]
    turnover_points = (
        normalized_stats["interceptions"] * settings["interceptions"]
        + normalized_stats["fumbles_lost"] * settings["fumbles_lost"]
    )
    bonus_points = normalized_stats["return_tds"] * settings["return_tds"]
    kicker_points = 0.0
    dst_points = 0.0
    total = (
        passing_points
        + rushing_points
        + receiving_points
        + reception_points
        + turnover_points
        + bonus_points
        + kicker_points
        + dst_points
    )
    return {
        "passing_points": passing_points,
        "rushing_points": rushing_points,
        "receiving_points": receiving_points,
        "reception_points": reception_points,
        "turnover_points": turnover_points,
        "bonus_points": bonus_points,
        "kicker_points": kicker_points,
        "dst_points": dst_points,
        "total_fantasy_points": total,
        "source_stats": {key: normalized_stats[key] for key in STAT_ALIASES},
        "missing_data_flags": list(normalized_stats["missing_data_flags"]),
    }


def calculate_fantasy_points(
    stat_row: dict[str, Any],
    scoring_profile: dict[str, Any],
) -> float:
    return calculate_fantasy_breakdown(stat_row, scoring_profile)["total_fantasy_points"]
