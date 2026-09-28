"""Statistical player comparison ("comps").

Ranks same-position players by similarity to a target player across a fixed
feature set, and reports similarity as a 0-100 match percentage.

Method: min-max normalize each feature across the position cohort including the
target, take the Euclidean distance between the target vector and each
candidate, then scale by the maximum possible distance in the unit hypercube
(sqrt(n_features)) so the result is comparable across positions and cohorts.

This was extracted from the retired Streamlit app so the algorithm survives the
UI. It has no UI, warehouse, or LLM dependencies: it takes a DataFrame in and
returns plain dictionaries out.
"""

from __future__ import annotations

from typing import Any

COMP_FEATURES = (
    "avg_ppr",
    "avg_opportunity",
    "avg_efficiency",
    "avg_grade",
    "avg_snap_share",
)

# Columns echoed back on each comp row for display or downstream packets.
COMP_OUTPUT_COLUMNS = (
    "player_id",
    "player_display_name",
    "position",
    "team",
    "avg_grade",
    "avg_ppr",
    "headshot",
)

DEFAULT_LIMIT = 5


def calculate_player_comps(
    player_row: Any,
    df: Any,
    limit: int = DEFAULT_LIMIT,
    features: tuple[str, ...] = COMP_FEATURES,
) -> list[dict[str, Any]]:
    """Return the `limit` most similar same-position players to `player_row`.

    Args:
        player_row: mapping or Series for the target player. Must carry
            `position`, `player_id`, and every feature in `features`.
        df: DataFrame of candidate players.
        limit: maximum comps to return.
        features: numeric columns to compare on.

    Returns:
        Comp dictionaries sorted by `match_pct` descending. Empty when the
        position cohort has no other players.
    """
    import numpy as np
    import pandas as pd

    position = player_row["position"]
    cohort = df[df["position"] == position].copy()
    cohort = cohort[cohort["player_id"] != player_row["player_id"]]
    if cohort.empty:
        return []

    feature_list = list(features)
    # Coerce first: these columns arrive from BigQuery and may be object dtype
    # with None in them, which makes a bare fillna downcast unpredictably.
    for name in feature_list:
        cohort[name] = pd.to_numeric(cohort[name], errors="coerce").fillna(0.0)
    target_features = pd.Series(
        {name: pd.to_numeric(player_row[name], errors="coerce") for name in feature_list},
        dtype="float64",
    ).fillna(0.0)

    # Normalize the target alongside the cohort so both share a scale.
    combined = pd.concat([cohort, pd.DataFrame([target_features])], ignore_index=True)
    target_index = len(cohort)

    norm_columns = []
    for name in feature_list:
        norm_name = f"{name}_norm"
        norm_columns.append(norm_name)
        low = combined[name].min()
        high = combined[name].max()
        if pd.isna(low) or pd.isna(high) or high == low:
            # A feature with no spread carries no signal; treat it as constant.
            combined[norm_name] = 0.0
        else:
            combined[norm_name] = (combined[name] - low) / (high - low)

    target_vector = combined.iloc[target_index][norm_columns].values.astype(float)
    max_distance = np.sqrt(len(feature_list))

    comps: list[dict[str, Any]] = []
    for index in range(len(cohort)):
        row = combined.iloc[index]
        candidate = row[norm_columns].values.astype(float)
        distance = np.sqrt(np.sum((target_vector - candidate) ** 2))

        match_pct = max(0.0, 100.0 * (1.0 - (distance / max_distance)))
        if pd.isna(match_pct):
            match_pct = 0.0

        comp = {column: row.get(column) for column in COMP_OUTPUT_COLUMNS}
        comp["match_pct"] = match_pct
        comps.append(comp)

    comps.sort(key=lambda comp: comp["match_pct"], reverse=True)
    return comps[:limit]
