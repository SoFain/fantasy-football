"""Owner-approved ranking exceptions shared by current-board builders."""

STANDARD_WR_ELITE_ORDER = (
    "A.J. Brown",
    "Justin Jefferson",
    "Garrett Wilson",
)

GNG_WATCHLIST_NAMES = frozenset((
    "Stefon Diggs",
    "Deebo Samuel",
    "Deebo Samuel Sr.",
    "Keenan Allen",
    "Hunter Renfrow",
    "Gabe Davis",
    "Sterling Shepard",
    "Tyreek Hill",
    "Zach Ertz",
))

# Sleeper's slot-specific WR depth order can conflict with the team's published
# depth chart. This exception is intentionally narrow and expires when any
# identity, team, experience, or usage bound changes.
COVERAGE_GATE_REVIEW_ONLY_DECISIONS = {
    ("WR", "Theo Wease"): {
        "team": "MIA",
        "years_exp": 1,
        "max_games_played": 3,
        "max_qualification_volume": 10.0,
        "reason": (
            "Sleeper labeled Theo Wease as RWR depth-order 1, but Miami's published depth chart "
            "placed him in the third column and his 2025 sample was only 3 games and 10 targets."
        ),
        "evidence_checked_at": "2026-08-07",
    },
}
