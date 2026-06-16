from __future__ import annotations

import unittest
from pathlib import Path

from src import content_brief_review
from src.compat_flags import USE_CONTENT_BRIEF_REVIEW_UI, compat_flag_enabled


class FakeJob:
    def __init__(self, rows=None, affected_rows=None):
        self.rows = rows or []
        self.num_dml_affected_rows = affected_rows

    def result(self):
        return self.rows


class FakeClient:
    project = "test-project"

    def __init__(self, rows=None, query_results=None):
        self.rows = rows or []
        self.query_results = list(query_results or [])
        self.query_calls = []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        if self.query_results:
            result = self.query_results.pop(0)
            if isinstance(result, FakeJob):
                return result
            return FakeJob(result)
        return FakeJob(self.rows)


RAW_SOURCE_TERMS = (
    "weekly_metrics",
    "play_by_play",
    "ngs_passing",
    "ngs_rushing",
    "ngs_receiving",
    "ftn_charting",
    "weekly_snap_counts",
    "injury_reports",
    "player_rosters",
    "player_contracts",
    "depth_charts",
    "market_values",
    "sleeper_viewer_team_snapshots",
    "sleeper_roster_players",
    "sleeper_lineups",
    "sleeper_available_players",
)


class ContentBriefReviewTests(unittest.TestCase):
    def test_feature_flag_defaults_false(self):
        self.assertFalse(compat_flag_enabled(USE_CONTENT_BRIEF_REVIEW_UI, {}))
        self.assertTrue(
            compat_flag_enabled(
                USE_CONTENT_BRIEF_REVIEW_UI,
                {USE_CONTENT_BRIEF_REVIEW_UI: "true"},
            )
        )

    def test_list_runs_query_uses_parameters_and_output_table(self):
        sql, job_config = content_brief_review.build_list_content_brief_runs_query(
            project_id="test-project",
            dataset_id="test_dataset",
            brief_type="fraud_watch_show",
            status="completed",
            limit=9999,
        )

        self.assertIn("content_brief_runs", sql)
        self._assert_no_raw_source_terms(sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["brief_type"], "fraud_watch_show")
        self.assertEqual(params["status"], "completed")
        self.assertEqual(params["limit"], content_brief_review.MAX_LIMIT)

    def test_list_briefs_query_uses_parameters_and_output_table(self):
        sql, job_config = content_brief_review.build_list_content_briefs_query(
            project_id="test-project",
            dataset_id="test_dataset",
            review_status="approved",
            season=2026,
            week=1,
            model_run_id="model_1",
        )

        self.assertIn("content_briefs", sql)
        self._assert_no_raw_source_terms(sql)
        self.assertIn("@review_status", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["review_status"], "approved")
        self.assertEqual(params["season"], 2026)
        self.assertEqual(params["week"], 1)
        self.assertEqual(params["model_run_id"], "model_1")

    def test_detail_helper_returns_brief_and_items(self):
        brief = {
            "content_brief_id": "brief_1",
            "title": "Fraud Watch",
            "brief_text": "Read this.",
            "brief_json": "{}",
            "review_status": "draft",
        }
        item = {
            "content_brief_id": "brief_1",
            "item_id": "brief_1:01",
            "item_order": 1,
            "title": "Item",
        }
        client = FakeClient(query_results=[[brief], [item]])

        detail = content_brief_review.get_content_brief_detail(
            "brief_1",
            client=client,
            dataset_id="test_dataset",
        )

        self.assertFalse(detail["empty"])
        self.assertEqual(detail["brief"]["content_brief_id"], "brief_1")
        self.assertEqual(detail["items"][0]["item_id"], "brief_1:01")

    def test_empty_detail_response_is_clean(self):
        client = FakeClient(query_results=[[]])

        detail = content_brief_review.get_content_brief_detail(
            "missing",
            client=client,
            dataset_id="test_dataset",
        )

        self.assertTrue(detail["empty"])
        self.assertIsNone(detail["brief"])
        self.assertEqual(detail["items"], [])

    def test_status_validation_rejects_unknown_value(self):
        with self.assertRaises(ValueError):
            content_brief_review.validate_review_status("publish_now")

    def test_update_status_uses_parameterized_dml(self):
        client = FakeClient(query_results=[FakeJob([], affected_rows=1)])

        result = content_brief_review.update_content_brief_review_status(
            "brief_1",
            "reviewed",
            reviewer_notes="good to use",
            client=client,
            dataset_id="test_dataset",
        )

        sql, job_config = client.query_calls[0]
        self.assertIn("UPDATE `test-project.test_dataset.content_briefs`", sql)
        self.assertIn("@review_status", sql)
        self._assert_no_raw_source_terms(sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["content_brief_id"], "brief_1")
        self.assertEqual(params["review_status"], "reviewed")
        self.assertTrue(result["reviewer_notes_ignored"])

    def test_export_markdown_includes_items_and_status(self):
        brief = {
            "content_brief_id": "brief_1",
            "content_brief_run_id": "run_1",
            "brief_type": "fraud_watch_show",
            "title": "Fraud Watch",
            "season": 2026,
            "week": 1,
            "model_run_id": "model_1",
            "brief_text": "Main read.",
            "brief_json": '{"llm_prompt_payload_json":{"title":"Fraud Watch"}}',
            "token_estimate": 500,
            "source_freshness_json": "{}",
            "missing_data_flags": "[]",
            "review_status": "draft",
        }
        item = {
            "content_brief_id": "brief_1",
            "item_order": 1,
            "item_type": "player",
            "title": "Player miss",
            "claim": "This player is overvalued.",
            "evidence_summary": "Evidence text.",
            "counterargument": "Counter text.",
            "snark_hook": "Snark text.",
            "confidence_score": 0.8,
            "missing_data_flags": "[]",
        }
        client = FakeClient(query_results=[[brief], [item]])

        markdown = content_brief_review.export_content_brief_markdown(
            "brief_1",
            client=client,
            dataset_id="test_dataset",
        )

        self.assertIn("Fraud Watch", markdown)
        self.assertIn("review_status", markdown)
        self.assertIn("Player miss", markdown)
        self.assertIn("Show Writer Payload", markdown)

    def test_generation_preview_command_is_dry_run(self):
        command = content_brief_review.build_content_brief_generation_preview_command(
            brief_type="fraud_watch_show",
            season=2026,
            week=1,
            model_run_id="model_1",
        )

        self.assertEqual(command[0], r".\venv\Scripts\python.exe")
        self.assertIn("--dry-run", command)
        self.assertIn("--model-run-id", command)

    def test_query_builders_do_not_reference_raw_sources(self):
        queries = [
            content_brief_review.build_list_content_brief_runs_query(
                project_id="test-project",
                dataset_id="test_dataset",
            )[0],
            content_brief_review.build_list_content_briefs_query(
                project_id="test-project",
                dataset_id="test_dataset",
            )[0],
            content_brief_review.build_get_content_brief_detail_query(
                project_id="test-project",
                dataset_id="test_dataset",
                content_brief_id="brief_1",
            )[0],
            content_brief_review.build_list_content_brief_items_query(
                project_id="test-project",
                dataset_id="test_dataset",
                content_brief_id="brief_1",
            )[0],
            content_brief_review.build_update_content_brief_review_status_query(
                project_id="test-project",
                dataset_id="test_dataset",
                content_brief_id="brief_1",
                review_status="approved",
            )[0],
        ]
        for sql in queries:
            self._assert_no_raw_source_terms(sql)

    def test_helper_source_does_not_call_llms_or_fetch_urls(self):
        source = Path("src/content_brief_review.py").read_text(encoding="utf-8")

        for forbidden in ("google.genai", "openai", "requests.", "generate_content"):
            self.assertNotIn(forbidden, source)

    def test_app_compiles_with_default_off_content_brief_tab(self):
        app_source = Path("app.py").read_text(encoding="utf-8")

        self.assertIn("USE_CONTENT_BRIEF_REVIEW_UI", app_source)
        self.assertIn("use_content_brief_review_ui()", app_source)
        self.assertIn("render_content_brief_review_ui()", app_source)

    def _assert_no_raw_source_terms(self, sql: str):
        for raw_term in RAW_SOURCE_TERMS:
            self.assertNotIn(raw_term, sql)


if __name__ == "__main__":
    unittest.main()
