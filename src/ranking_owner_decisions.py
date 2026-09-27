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

# Sleeper depth order can put a player in the coverage-gate frontline universe
# when his omission is correct (a slot-specific depth conflict, or a temporary
# promotion of a player with no formula-season sample). Each exception is
# intentionally narrow and expires when any identity, team, experience, trace
# code, or usage bound changes.
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
    # A correct formula non-qualification, not a pipeline loss: bound to the
    # missing-source trace code and a zero 2025 sample, so any 2025 row, team
    # change, or experience rollover removes the exemption.
    ("RB", "MarShawn Lloyd"): {
        "team": "GB",
        "years_exp": 2,
        "trace_code": "NO_2025_SITUATIONAL_SOURCE_ROW",
        "max_games_played": 0,
        "max_qualification_volume": 0.0,
        "reason": (
            "MarShawn Lloyd recorded no 2025 regular-season games: weekly_metrics, "
            "player_season_advanced_metrics, and rb_situational_metrics have no 2025 rows for "
            "00-0039811 (2024 was 1 game and 7 touches), so no RB Fable 01 2025 qualification row "
            "exists. His identity bridge is an accepted EXACT_SLUG_MATCH. Sleeper moved him to GB RB "
            "depth order 1 while Josh Jacobs is listed NA (Personal) at depth order 4."
        ),
        "evidence_checked_at": "2026-09-27",
    },
}
