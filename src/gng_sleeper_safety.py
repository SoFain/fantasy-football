"""Deterministic Sleeper context layer for current GNG candidate boards only."""
from __future__ import annotations

from typing import Any


ACTIVE_STATUSES = {"Active", "ACT"}


def apply_sleeper_safety(row: dict[str, Any]) -> dict[str, Any]:
    """Return current-board eligibility, bounded role adjustment, and review flags."""
    active = row.get("sleeper_active") is True
    team = row.get("sleeper_team")
    status = row.get("sleeper_status")
    depth_order = row.get("sleeper_depth_chart_order")
    injury_status = row.get("sleeper_injury_status")
    context_active = active and bool(team) and status in ACTIVE_STATUSES
    role_adjustment = 0.0
    if context_active and depth_order == 1:
        role_adjustment = 0.02
    elif context_active and isinstance(depth_order, int) and depth_order >= 3:
        role_adjustment = -0.04
    flags = []
    if not context_active:
        flags.append("SLEEPER_ROSTER_REVIEW")
    if context_active and depth_order is None:
        flags.append("DEPTH_CHART_UNKNOWN")
    if injury_status:
        flags.append("INJURY_UNCERTAIN")
    if row.get("sleeper_years_exp") == 0:
        flags.append("ROOKIE_CONTEXT_REQUIRED")
    return {
        **row,
        "sleeper_hard_review": not context_active,
        "sleeper_role_adjustment": role_adjustment,
        "sleeper_review_flags": flags,
    }
