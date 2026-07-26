from __future__ import annotations

import unittest
from pathlib import Path

from src.compat_flags import (
    DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER,
    USE_COMPAT_TRADE_PLAYER_HISTORY,
    USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS,
    USE_TRADE_ANALYZER_SCORE_V0,
    USE_COMPAT_TRADE_PLAYER_SCORE,
    USE_TRADE_PICK_SCORE_V0,
    USE_COMPAT_TRADE_PICK_SCORE,
    compat_flag_enabled,
)
from src import cloud_run_jobs


APP_SOURCE = Path("app.py").read_text(encoding="utf-8")


class DataOpsLocalControlTests(unittest.TestCase):
    def test_local_subprocess_flags_default_false(self):
        empty_env = {}

        self.assertFalse(compat_flag_enabled(USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS, empty_env))
        self.assertFalse(compat_flag_enabled(DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER, empty_env))
        self.assertTrue(
            compat_flag_enabled(
                USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS,
                {USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS: "true"},
            )
        )
        self.assertTrue(
            compat_flag_enabled(
                DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER,
                {DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER: "true"},
            )
        )

    def test_existing_risk_flags_stay_default_false(self):
        self.assertFalse(compat_flag_enabled(USE_COMPAT_TRADE_PLAYER_HISTORY, {}))
        self.assertFalse(compat_flag_enabled(USE_TRADE_ANALYZER_SCORE_V0, {}))
        self.assertFalse(compat_flag_enabled(USE_COMPAT_TRADE_PLAYER_SCORE, {}))
        self.assertFalse(compat_flag_enabled(USE_TRADE_PICK_SCORE_V0, {}))
        self.assertFalse(compat_flag_enabled(USE_COMPAT_TRADE_PICK_SCORE, {}))

    def test_data_ops_local_buttons_are_disabled_by_local_gate(self):
        expected_button_snippets = (
            'st.button("🔍 Run Validation Sweep", type="secondary", disabled=not local_controls_can_run)',
            'st.button("🚀 Ingest Realtime Player News", type="secondary", disabled=not local_controls_can_run)',
            'st.button("🧠 Load Context Event Ledger", type="secondary", disabled=not local_controls_can_run)',
            'st.button("📊 Ingest FantasyCalc Market Values", type="secondary", disabled=not local_controls_can_run)',
            'st.button("🔎 Verify Player Context", type="secondary", disabled=not local_controls_can_run)',
            'st.button("🚀 Ingest CFBD College Stats", type="secondary", disabled=not local_controls_can_run)',
            'st.button("🚀 Run Ingestion Pipeline", type="primary", disabled=not local_controls_can_run)',
            'st.button("🏆 Generate Pigskin Rankings", type="secondary", disabled=not local_controls_can_run)',
            'st.button("📤 Upload and Import Scouting Metrics", type="primary", disabled=not local_controls_can_run)',
        )

        self.assertIn("local_controls_visible, local_controls_can_run = render_data_ops_local_subprocess_gate()", APP_SOURCE)
        self.assertIn("disabled=not local_controls_can_run", APP_SOURCE)
        self.assertIn("if local_controls_can_run:\n            scouting_file = st.file_uploader", APP_SOURCE)
        self.assertIn("Scouting CSV upload is disabled until local subprocess controls", APP_SOURCE)
        for snippet in expected_button_snippets:
            self.assertIn(snippet, APP_SOURCE)

    def test_trade_lab_llm_action_is_disabled_by_local_gate(self):
        self.assertIn("trade_ai_controls_visible = use_data_ops_local_subprocess_controls()", APP_SOURCE)
        self.assertIn("trade_ai_controls_can_run = data_ops_local_subprocess_controls_enabled()", APP_SOURCE)
        self.assertIn(
            'st.button(f"🧠 Run AI {projection_years}-Year Outlook Analysis", type="primary", disabled=not trade_ai_controls_can_run)',
            APP_SOURCE,
        )

    def test_cloud_run_job_gate_remains_separate(self):
        self.assertFalse(cloud_run_jobs.should_use_cloud_run_jobs_for_data_ops({}))
        self.assertFalse(cloud_run_jobs.data_ops_job_trigger_allowed({}))
        self.assertIn("USE_CLOUD_RUN_JOBS_FOR_DATA_OPS", APP_SOURCE)
        self.assertIn("DATA_OPS_ALLOW_JOB_TRIGGER", APP_SOURCE)
        self.assertIn("USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS", APP_SOURCE)
        self.assertIn("DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER", APP_SOURCE)
        self.assertIn(
            "trigger_disabled = bool(preview_error) or not use_cloud_jobs or not trigger_allowed or not confirmed",
            APP_SOURCE,
        )

    def test_pigskin_sql_tool_stays_absent(self):
        self.assertNotIn('"name": "execute_bigquery_sql"', APP_SOURCE)


if __name__ == "__main__":
    unittest.main()
