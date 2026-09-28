"""Structured base-rate model for the availability pilot (no language model).

Hierarchically smoothed empirical rates. Each lane has a backoff chain of
feature tuples, from the global rate down to the most specific cell. A cell's
estimate is (successes + k * parent) / (n + k), so sparse cells shrink toward
their parent. The artifact stores raw counts, so every probability can be
recomputed and explained by hand.

Lanes:
  play_this_game     P(took a snap in the reported game | report features)
  bucket_this_game   distribution over MISSED_BUCKETS for the reported game
  play_next_game     P(snap in the team's next game | this week's report, this game's outcome)
  roster_next_game   P(snap in the next team game | weekly roster status, not on the report)
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence

from src.availability_labels import MISSED_BUCKETS

MODEL_VERSION = "availability_base_rates_v1"
ARTIFACT_PATH = Path(__file__).resolve().parents[1] / "docs" / "availability-base-rates-v1.json"
# Every position that is not QB/RB/WR/TE (K, P, LS, offensive line, defense): same
# estimator, chains, fit and holdout seasons, and history table as the skill artifact.
OTHER_MODEL_VERSION = "availability_base_rates_other_v1"
OTHER_ARTIFACT_PATH = Path(__file__).resolve().parents[1] / "docs" / "availability-base-rates-other-v1.json"
# Games-missed distributions counted from the NEXT team game, for the lanes whose
# target game has no official report yet (feed context only; not in the Jev state).
NEXT_BUCKETS_VERSION = "availability_next_buckets_v1"
NEXT_BUCKETS_PATH = Path(__file__).resolve().parents[1] / "docs" / "availability-next-buckets-v1.json"
POPULATIONS: dict[str, dict[str, Any]] = {
    "skill": {
        "model_version": MODEL_VERSION,
        "path": ARTIFACT_PATH,
        "population": "QB/RB/WR/TE, REG, official report entry, excluded_from_fit = FALSE",
    },
    "other": {
        "model_version": OTHER_MODEL_VERSION,
        "path": OTHER_ARTIFACT_PATH,
        "population": "every position except QB/RB/WR/TE, REG, official report entry, excluded_from_fit = FALSE",
    },
}

PLAY_CHAIN: tuple[tuple[str, ...], ...] = (
    (),
    ("report_status",),
    ("report_status", "practice_status"),
    ("report_status", "practice_status", "prev_week_state"),
    ("report_status", "practice_status", "prev_week_state", "body_part_group"),
)
NEXT_CHAIN: tuple[tuple[str, ...], ...] = (
    (),
    ("report_status",),
    ("report_status", "practice_status"),
    ("report_status", "practice_status", "played_this_game"),
)
ROSTER_CHAIN: tuple[tuple[str, ...], ...] = ((), ("roster_status",))
STATUS_ONLY_CHAIN = PLAY_CHAIN[:2]
EPS = 1e-6


def cell_key(row: dict, fields: Sequence[str]) -> str:
    return "|".join(str(row.get(f)) for f in fields) or "ALL"


def count_binary(rows: Iterable[dict], chain: Sequence[Sequence[str]], target: str) -> dict[str, dict[str, list[int]]]:
    """Per level, per cell: [n, successes]."""
    tables: dict[str, dict[str, list[int]]] = {"/".join(level) or "ALL": {} for level in chain}
    for row in rows:
        value = row.get(target)
        if value is None:
            continue
        for level in chain:
            cell = tables["/".join(level) or "ALL"].setdefault(cell_key(row, level), [0, 0])
            cell[0] += 1
            cell[1] += int(bool(value))
    return tables


def count_buckets(rows: Iterable[dict], chain: Sequence[Sequence[str]]) -> dict[str, dict[str, list[int]]]:
    """Per level, per cell: counts in MISSED_BUCKETS order."""
    tables: dict[str, dict[str, list[int]]] = {"/".join(level) or "ALL": {} for level in chain}
    for row in rows:
        bucket = row.get("missed_bucket")
        if bucket is None:
            continue
        for level in chain:
            cell = tables["/".join(level) or "ALL"].setdefault(cell_key(row, level), [0] * len(MISSED_BUCKETS))
            cell[MISSED_BUCKETS.index(bucket)] += 1
    return tables


def predict_binary(tables: dict, chain: Sequence[Sequence[str]], k: float, row: dict, depth: int | None = None) -> float:
    levels = chain if depth is None else chain[: depth + 1]
    estimate = 0.5
    for level in levels:
        n, hits = tables["/".join(level) or "ALL"].get(cell_key(row, level), [0, 0])
        estimate = (hits + k * estimate) / (n + k) if level else (hits + 1.0) / (n + 2.0)
    return estimate


def predict_buckets(tables: dict, chain: Sequence[Sequence[str]], k: float, row: dict, depth: int | None = None) -> list[float]:
    levels = chain if depth is None else chain[: depth + 1]
    estimate = [1.0 / len(MISSED_BUCKETS)] * len(MISSED_BUCKETS)
    for level in levels:
        counts = tables["/".join(level) or "ALL"].get(cell_key(row, level), [0] * len(MISSED_BUCKETS))
        n = sum(counts)
        weight = k if level else 1.0
        estimate = [(c + weight * p) / (n + weight) for c, p in zip(counts, estimate)]
    return estimate


def brier(probs: Sequence[float], outcomes: Sequence[int]) -> float:
    return sum((p - y) ** 2 for p, y in zip(probs, outcomes)) / max(len(probs), 1)


def log_loss(probs: Sequence[float], outcomes: Sequence[int]) -> float:
    total = 0.0
    for p, y in zip(probs, outcomes):
        p = min(max(p, EPS), 1 - EPS)
        total -= math.log(p) if y else math.log(1 - p)
    return total / max(len(probs), 1)


def multiclass_scores(dists: Sequence[Sequence[float]], labels: Sequence[int]) -> dict[str, float]:
    n = max(len(dists), 1)
    ll = -sum(math.log(max(d[y], EPS)) for d, y in zip(dists, labels)) / n
    br = sum(sum((p - (1.0 if i == y else 0.0)) ** 2 for i, p in enumerate(d)) for d, y in zip(dists, labels)) / n
    return {"log_loss": round(ll, 4), "brier": round(br, 4)}


def calibration_table(probs: Sequence[float], outcomes: Sequence[int], edges: Sequence[float] = (0, 0.05, 0.2, 0.4, 0.6, 0.8, 0.95, 1.0001)) -> list[dict]:
    table = []
    for low, high in zip(edges[:-1], edges[1:]):
        members = [(p, y) for p, y in zip(probs, outcomes) if low <= p < high]
        if not members:
            continue
        table.append(
            {
                "bin": f"{low:.2f}-{min(high, 1):.2f}",
                "n": len(members),
                "mean_predicted": round(sum(p for p, _ in members) / len(members), 4),
                "observed_rate": round(sum(y for _, y in members) / len(members), 4),
            }
        )
    return table


def load_artifact(path: Path = ARTIFACT_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class BaseRateModel:
    """Read-only predictor over a saved artifact."""

    def __init__(self, artifact: dict[str, Any], next_buckets: dict[str, Any] | None = None):
        self.artifact = artifact
        self.version = artifact["model_version"]
        self.k = float(artifact["k"])
        self.next_buckets = next_buckets

    @classmethod
    def load(cls, path: Path = ARTIFACT_PATH) -> "BaseRateModel":
        return cls(load_artifact(path))

    @classmethod
    def load_population(cls, population: str) -> "BaseRateModel":
        """Population artifact plus its next-game bucket lanes."""
        spec = POPULATIONS[population]
        next_artifact = load_artifact(NEXT_BUCKETS_PATH)
        lanes = next_artifact["populations"][population]
        if lanes["base_artifact"] != spec["model_version"]:
            raise ValueError(f"{NEXT_BUCKETS_PATH.name} was fit against {lanes['base_artifact']}, not {spec['model_version']}")
        return cls(load_artifact(spec["path"]), {"version": next_artifact["model_version"], "k": float(lanes["k"]), **lanes["tables"]})

    def buckets_next_game(self, features: dict) -> dict[str, float]:
        """Missed-bucket distribution from the next game, given this week's report and whether he played."""
        nb = self.next_buckets
        depth = None if features.get("played_this_game") is not None else len(NEXT_CHAIN) - 2
        return dict(zip(MISSED_BUCKETS, predict_buckets(nb["bucket_next_game"], NEXT_CHAIN, nb["k"], features, depth)))

    def roster_buckets_next_game(self, roster_status: str) -> dict[str, float]:
        nb = self.next_buckets
        dist = predict_buckets(nb["roster_bucket_next_game"], ROSTER_CHAIN, nb["k"], {"roster_status": roster_status})
        return dict(zip(MISSED_BUCKETS, dist))

    def play_this_game(self, features: dict) -> float:
        return predict_binary(self.artifact["tables"]["play_this_game"], PLAY_CHAIN, self.k, features)

    def buckets_this_game(self, features: dict) -> dict[str, float]:
        dist = predict_buckets(self.artifact["tables"]["bucket_this_game"], PLAY_CHAIN, self.k, features)
        return dict(zip(MISSED_BUCKETS, dist))

    def play_next_game(self, features: dict) -> float:
        # "played_this_game" unknown (outcome not loaded yet) stops the chain one level early.
        depth = None if features.get("played_this_game") is not None else len(NEXT_CHAIN) - 2
        return predict_binary(self.artifact["tables"]["play_next_game"], NEXT_CHAIN, self.k, features, depth)

    def roster_next_game(self, roster_status: str) -> float:
        return predict_binary(self.artifact["tables"]["roster_next_game"], ROSTER_CHAIN, self.k, {"roster_status": roster_status})
