from __future__ import annotations

import unittest

from src.bigquery_guardrails import (
    DEFAULT_MAX_BYTES_BILLED,
    PigskinQueryRejected,
    extract_bigquery_table_references,
    run_bigquery_query,
    validate_pigskin_sql,
)
from src.pigskin_chat_schema import (
    PIGSKIN_CHAT_ALLOWED_TABLES,
    PIGSKIN_CHAT_BLOCKED_TABLES,
)


class FakeQueryJob:
    total_bytes_processed = 1234
    cache_hit = False

    def __init__(self):
        self.result_called = False

    def result(self):
        self.result_called = True
        return self


class FakeBigQueryClient:
    def __init__(self):
        self.sql_query = None
        self.job_config = None
        self.job = FakeQueryJob()

    def query(self, sql_query, job_config=None):
        self.sql_query = sql_query
        self.job_config = job_config
        return self.job


class BigQueryGuardrailTests(unittest.TestCase):
    def test_extracts_backticked_full_table_names(self):
        refs = extract_bigquery_table_references(
            "SELECT * FROM `fantasy-football-498121.fantasy_football_brain.weekly_metrics`",
            known_tables=PIGSKIN_CHAT_ALLOWED_TABLES + PIGSKIN_CHAT_BLOCKED_TABLES,
        )

        self.assertIn("weekly_metrics", refs)

    def test_extracts_bare_blocked_table_names(self):
        refs = extract_bigquery_table_references(
            "SELECT player_name FROM weekly_metrics WHERE season = 2025",
            known_tables=PIGSKIN_CHAT_ALLOWED_TABLES + PIGSKIN_CHAT_BLOCKED_TABLES,
        )

        self.assertIn("weekly_metrics", refs)

    def test_allowed_pigskin_query_passes(self):
        result = validate_pigskin_sql(
            """
            SELECT player_name, total_epa
            FROM fantasy_football_brain.analytics_player_weekly_truth
            LIMIT 10
            """
        )

        self.assertEqual(result.blocked_tables, ())
        self.assertEqual(result.non_allowed_tables, ())
        self.assertIn("analytics_player_weekly_truth", result.referenced_tables)

    def test_blocked_pigskin_query_is_rejected(self):
        with self.assertLogs("src.bigquery_guardrails", level="WARNING"):
            with self.assertRaises(PigskinQueryRejected) as ctx:
                validate_pigskin_sql(
                    """
                    SELECT player_name, fantasy_points_ppr
                    FROM fantasy_football_brain.weekly_metrics
                    LIMIT 10
                    """
                )

        self.assertIn("weekly_metrics", ctx.exception.policy_result.blocked_tables)

    def test_non_allowed_unknown_table_is_rejected(self):
        with self.assertLogs("src.bigquery_guardrails", level="WARNING"):
            with self.assertRaises(PigskinQueryRejected) as ctx:
                validate_pigskin_sql(
                    """
                    SELECT *
                    FROM fantasy_football_brain.random_projection_table
                    """
                )

        self.assertIn(
            "random_projection_table",
            ctx.exception.policy_result.non_allowed_tables,
        )

    def test_wrapper_applies_maximum_bytes_billed(self):
        client = FakeBigQueryClient()

        run_bigquery_query(
            client,
            "SELECT 1",
            component="unit_test",
            query_name="guardrail_config",
        )

        self.assertEqual(
            client.job_config.maximum_bytes_billed,
            DEFAULT_MAX_BYTES_BILLED,
        )
        self.assertEqual(client.job_config.labels["app"], "ai-vs-meatbags")
        self.assertTrue(client.job.result_called)

    def test_wrapper_supports_dry_run(self):
        client = FakeBigQueryClient()

        run_bigquery_query(
            client,
            "SELECT 1",
            component="unit_test",
            query_name="guardrail_dry_run",
            dry_run=True,
        )

        self.assertTrue(client.job_config.dry_run)
        self.assertFalse(client.job.result_called)


if __name__ == "__main__":
    unittest.main()
