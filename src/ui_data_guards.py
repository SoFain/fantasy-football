"""Small UI data guards for legacy Streamlit paths."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
import re
import unicodedata

import pandas as pd


def ensure_player_profile_display_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure Player Profiles legacy data has columns expected by profile UIs."""
    if df is None or df.empty:
        return df

    out = df.copy()
    if "position" not in out.columns:
        out["position"] = pd.NA

    if "depth_position" not in out.columns:
        out["depth_position"] = out["position"]
        return out

    depth_position = out["depth_position"]
    missing_depth_position = depth_position.isna() | depth_position.astype(str).str.strip().eq("")
    out.loc[missing_depth_position, "depth_position"] = out.loc[missing_depth_position, "position"]
    return out


def ensure_sleeper_watch_display_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure Sleeper Watch display columns exist even when older marts lack aliases."""
    if df is None or df.empty:
        return df

    out = df.copy()

    if "rolling_3_week_ppr" not in out.columns:
        if "fantasy_points_last_3" in out.columns:
            out["rolling_3_week_ppr"] = _numeric_series(out, "fantasy_points_last_3") / 3.0
        elif "fantasy_points_per_game" in out.columns:
            out["rolling_3_week_ppr"] = _numeric_series(out, "fantasy_points_per_game")
        else:
            out["rolling_3_week_ppr"] = 0.0
    else:
        out["rolling_3_week_ppr"] = _numeric_series(out, "rolling_3_week_ppr")

    numeric_defaults = {
        "roster_pct": 0.0,
        "snap_share": 0.0,
        "targets_3w": 0.0,
        "carries_3w": 0.0,
        "wopr": 0.0,
        "epa": 0.0,
        "opp_def_rank": 0.0,
        "sleeper_score": 0.0,
    }
    for column, default in numeric_defaults.items():
        if column not in out.columns:
            out[column] = default
        else:
            out[column] = _numeric_series(out, column, default)

    return out


def collect_selected_trade_assets(
    selected_labels: Sequence[str],
    player_map: Mapping[str, Any],
    empty_asset_label: str,
) -> list[Any]:
    """Return assets selected by display label, ignoring blanks and stale labels."""
    assets: list[Any] = []
    for label in selected_labels:
        if not label or label == empty_asset_label:
            continue
        asset = _resolve_trade_asset_label(label, player_map)
        if asset is not None:
            assets.append(asset)
    return assets


def unresolved_trade_asset_labels(
    selected_labels: Sequence[str],
    player_map: Mapping[str, Any],
    empty_asset_label: str,
) -> list[str]:
    """Return selected labels that could not be resolved to a trade asset."""
    unresolved: list[str] = []
    for label in selected_labels:
        if not label or label == empty_asset_label:
            continue
        if _resolve_trade_asset_label(label, player_map) is None:
            unresolved.append(label)
    return unresolved


def attach_trade_scores_to_assets(
    assets: Sequence[Any],
    score_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Attach current Trade Analyzer score rows to selected trade assets."""
    score_index = _build_trade_score_index(score_rows)
    attached: list[dict[str, Any]] = []
    for asset in assets:
        score = _resolve_trade_score_for_asset(asset, score_index)
        attached.append({"asset": asset, "score": score})
    return attached


def summarize_trade_score_side(attached_assets: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize Trade Analyzer score rows for one selected trade side."""
    scores = [
        _numeric_value((item.get("score") or {}).get("trade_score"), None)
        for item in attached_assets
        if item.get("score")
    ]
    scores = [score for score in scores if score is not None]
    missing_count = sum(1 for item in attached_assets if item.get("score") is None)
    total_score = round(sum(scores), 2)
    average_score = round(total_score / len(scores), 2) if scores else None
    return {
        "asset_count": len(attached_assets),
        "scored_count": len(scores),
        "missing_count": missing_count,
        "total_trade_score": total_score,
        "average_trade_score": average_score,
    }


def _resolve_trade_asset_label(label: str, player_map: Mapping[str, Any]) -> Any | None:
    asset = player_map.get(label)
    if asset is not None:
        return asset

    normalized_label = _normalize_trade_asset_label(label)
    for candidate_label, candidate_asset in player_map.items():
        if _normalize_trade_asset_label(candidate_label) == normalized_label:
            return candidate_asset

    parsed = _parse_trade_asset_label(label)
    if not parsed["name"]:
        return None

    normalized_name = _normalize_trade_asset_label(parsed["name"])
    for candidate_asset in player_map.values():
        candidate_name = _normalize_trade_asset_label(_asset_field(candidate_asset, "player_display_name"))
        if candidate_name != normalized_name:
            continue

        candidate_position = _normalize_trade_asset_label(_asset_field(candidate_asset, "position"))
        candidate_team = _normalize_trade_asset_label(_asset_field(candidate_asset, "team"))
        label_position = _normalize_trade_asset_label(parsed["position"])
        label_team = _normalize_trade_asset_label(parsed["team"])
        if label_position and candidate_position and label_position != candidate_position:
            continue
        if label_team and candidate_team and label_team != candidate_team:
            continue
        return candidate_asset

    return None


def _build_trade_score_index(score_rows: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    index: dict[str, Mapping[str, Any]] = {}
    for row in score_rows:
        for key in _score_row_keys(row):
            index.setdefault(key, row)
    return index


def _resolve_trade_score_for_asset(asset: Any, score_index: Mapping[str, Mapping[str, Any]]) -> Mapping[str, Any] | None:
    for key in _asset_score_keys(asset):
        score = score_index.get(key)
        if score is not None:
            return score
    return None


def _score_row_keys(row: Mapping[str, Any]) -> list[str]:
    values = [
        row.get("player_id"),
        row.get("player_id_internal"),
        row.get("player_name"),
        row.get("normalized_name"),
    ]
    return [_score_lookup_key(value) for value in values if _score_lookup_key(value)]


def _asset_score_keys(asset: Any) -> list[str]:
    values = [
        _asset_field(asset, "player_id_internal"),
        _asset_field(asset, "source_player_key"),
        _asset_field(asset, "player_id"),
        _asset_field(asset, "player_display_name"),
        _asset_field(asset, "display_name"),
        _asset_field(asset, "market_player_name"),
        _asset_field(asset, "normalized_name"),
    ]
    return [_score_lookup_key(value) for value in values if _score_lookup_key(value)]


def _score_lookup_key(value: Any) -> str:
    if value is None or value == "":
        return ""
    return _normalize_trade_asset_label(value)


def _parse_trade_asset_label(label: str) -> dict[str, str]:
    cleaned = label.strip()
    cleaned = re.sub(r"^[^\w]+", "", cleaned, flags=re.UNICODE).strip()
    match = re.match(
        r"^(?P<name>.+?)\s+\((?P<position>[^()\-]+)\s+-\s+(?P<team>[^()]+)\)\s+\(Value:\s*[^)]*\)$",
        cleaned,
    )
    if match:
        return {key: value.strip() for key, value in match.groupdict().items()}

    pick_match = re.match(r"^(?P<name>.+?)\s+\(Value:\s*[^)]*\)$", cleaned)
    if pick_match:
        return {"name": pick_match.group("name").strip(), "position": "", "team": ""}

    return {"name": cleaned, "position": "", "team": ""}


def _asset_field(asset: Any, field: str) -> str:
    if isinstance(asset, Mapping):
        value = asset.get(field, "")
    else:
        try:
            value = asset[field]
        except Exception:
            value = ""
    if value is None or pd.isna(value):
        return ""
    return str(value)


def _normalize_trade_asset_label(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    text = text.replace("’", "'").replace("`", "'")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _numeric_series(df: pd.DataFrame, column: str, default: float = 0.0) -> pd.Series:
    return pd.to_numeric(df[column], errors="coerce").fillna(default)


def _numeric_value(value: Any, default: float | None = 0.0) -> float | None:
    try:
        numeric = pd.to_numeric(value, errors="coerce")
    except Exception:
        return default
    if pd.isna(numeric):
        return default
    return float(numeric)
