from __future__ import annotations

import unittest
from pathlib import Path
import re

from src.pigskin_chat_schema import (
    PIGSKIN_CHAT_ALLOWED_TABLES,
    PIGSKIN_CHAT_BLOCKED_TABLES,
    render_pigskin_chat_schema,
)
from src.pigskin_context_tools import get_pigskin_context_tool_declarations


EXTRA_FORBIDDEN_SCHEMA_TERMS = (
    "rookie_scouting_metrics",
    "college_player_stats",
    "realtime_player_news",
    "sleeper_players_current",
)


class PigskinChatSchemaTests(unittest.TestCase):
    def test_allowed_table_list_is_explicit(self):
        self.assertEqual(
            PIGSKIN_CHAT_ALLOWED_TABLES,
            (
                "analytics_player_weekly_truth",
                "analytics_fraud_watch",
                "analytics_pigskin_rankings",
                "analytics_pigskin_rankings_history",
                "analytics_game_environment",
                "analytics_player_qb_weekly",
                "analytics_player_qb_splits",
                "analytics_context_events",
                "analytics_external_context_search_results",
            ),
        )

    def test_rendered_schema_contains_allowed_tables(self):
        schema = render_pigskin_chat_schema()

        for table_name in PIGSKIN_CHAT_ALLOWED_TABLES:
            self.assertIn(f"fantasy_football_brain.{table_name}", schema)

    def test_rendered_schema_does_not_contain_blocked_tables(self):
        schema = render_pigskin_chat_schema()

        for table_name in PIGSKIN_CHAT_BLOCKED_TABLES + EXTRA_FORBIDDEN_SCHEMA_TERMS:
            self.assertNotIn(table_name, schema)

    def test_app_prompt_uses_context_tool_protocol(self):
        app_source = Path("app.py").read_text(encoding="utf-8")
        self.assertIn("### Context Tool Protocol ###", app_source)
        self.assertIn("You cannot write or execute SQL", app_source)
        self.assertNotIn('"name": "execute_bigquery_sql"', app_source)
        match = re.search(
            r"### Context Tool Protocol ###(.*?)### Causal Claim Protocol ###",
            app_source,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        prompt_segment = match.group(1)

        for table_name in PIGSKIN_CHAT_BLOCKED_TABLES + EXTRA_FORBIDDEN_SCHEMA_TERMS:
            self.assertNotIn(table_name, prompt_segment)

    def test_context_tool_declarations_replace_sql_tool(self):
        declarations = get_pigskin_context_tool_declarations()
        names = {declaration["name"] for declaration in declarations}

        self.assertEqual(
            names,
            {
                "get_player_context_packet",
                "search_players",
                "get_rankings_slice",
                "get_fraud_watch_candidates",
                "get_trade_player_history",
                "compare_players",
                "get_context_event_leads",
            },
        )
        self.assertNotIn("execute_bigquery_sql", names)


if __name__ == "__main__":
    unittest.main()
