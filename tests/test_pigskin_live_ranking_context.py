from __future__ import annotations

import unittest

from src.pigskin_live_ranking_context import (
    build_live_ranking_context_request,
    format_live_ranking_context_for_prompt,
)


OBSERVED_STANDARD_TOP_TEN = [
    "Jaxon Smith-Njigba",
    "Puka Nacua",
    "Josh Allen",
    "Christian McCaffrey",
    "Trey McBride",
    "Amon-Ra St. Brown",
    "Ja'Marr Chase",
    "Drake London",
    "Drake Maye",
    "Bijan Robinson",
]


class PigskinLiveRankingContextTests(unittest.TestCase):
    def test_top_ten_standard_overall_request_defaults_to_live_all_board(self):
        request = build_live_ranking_context_request(
            "Can you go thru your top 10 overall players for the 2026 season in Standard Scoring?"
        )

        self.assertEqual(
            request,
            {"scoring_profile_id": "standard", "board": "ALL", "limit": 10},
        )

    def test_unqualified_top_players_request_uses_standard_all_defaults(self):
        request = build_live_ranking_context_request("Who are your top players right now?")

        self.assertEqual(request["scoring_profile_id"], "standard")
        self.assertEqual(request["board"], "ALL")
        self.assertEqual(request["limit"], 10)

    def test_formatted_context_preserves_exact_board_order(self):
        rankings = [
            {
                "board_rank": index,
                "player_name": name,
                "position": "WR",
                "team": "TST",
                "position_rank": index,
                "pigskin_score": 101 - index,
                "tier": "T1",
                "rank_rationale": f"{name} rationale",
                "risk_flags": "",
            }
            for index, name in enumerate(OBSERVED_STANDARD_TOP_TEN, start=1)
        ]

        context = format_live_ranking_context_for_prompt(
            rankings,
            scoring_profile_id="standard",
            board="ALL",
            requested_limit=10,
        )

        previous_index = -1
        for player_name in OBSERVED_STANDARD_TOP_TEN:
            current_index = context.find(player_name)
            self.assertGreater(current_index, previous_index)
            previous_index = current_index

        self.assertIn("Active source: Current Pigskin live rows from analytics_pigskin_rankings.", context)
        self.assertIn("Preserve this exact board order.", context)
        self.assertIn("Do not claim BQML, NGS, Stats02, PBP, injury, availability, or a formula champion is active.", context)
        self.assertIn("do not use bracketed stage directions", context)

    def test_empty_context_fails_closed_instead_of_guessing(self):
        context = format_live_ranking_context_for_prompt(
            [],
            scoring_profile_id="standard",
            board="ALL",
            requested_limit=10,
        )

        self.assertIn("not available", context)
        self.assertIn("Do not guess", context)


if __name__ == "__main__":
    unittest.main()
