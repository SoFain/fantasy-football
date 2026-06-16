from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from src import claim_import
from src.compat_flags import USE_CLAIM_LEDGER_UI, compat_flag_enabled


CSV_HEADER = ",".join(claim_import.CSV_COLUMNS)
SAMPLE_CLAIM_IMPORT_PATH = Path("tests/fixtures/sample_claim_import.csv")


def csv_row(**overrides):
    row = {
        "source_name": "Analyst X",
        "source_type": "youtube",
        "person_name": "Analyst X",
        "show_name": "Fantasy Show",
        "source_url": "https://example.com/watch",
        "episode_or_video_title": "Week 1 Takes",
        "published_at": "2026-08-01T12:00:00Z",
        "claimed_at": "2026-08-01T12:05:00Z",
        "claim_text": "A.J. Brown is a league winner",
        "claim_type": "breakout",
        "claim_direction": "positive",
        "time_horizon": "season",
        "season": "2026",
        "week": "1",
        "scoring_profile_id": "ppr",
        "league_type_id": "redraft",
        "roster_format_id": "one_qb",
        "player_names": "A.J. Brown",
        "team_names": "",
        "claimed_rank": "12",
        "claimed_projection": "18.5",
        "claimed_value": "42",
        "notes": "Manual test row",
    }
    row.update(overrides)
    return ",".join(f'"{row[column]}"' for column in claim_import.CSV_COLUMNS)


def identity_row(**overrides):
    row = {
        "player_id_internal": "pid_1",
        "normalized_name": "ajbrown",
        "display_name": "A.J. Brown",
        "full_name": "A.J. Brown",
        "position": "WR",
        "current_team": "PHI",
    }
    row.update(overrides)
    return row


def sample_identity_rows():
    return [
        identity_row(
            player_id_internal="pid_chase",
            normalized_name="jamarrchase",
            display_name="Ja'Marr Chase",
            full_name="Ja'Marr Chase",
            position="WR",
            current_team="CIN",
        ),
        identity_row(
            player_id_internal="pid_jefferson",
            normalized_name="justinjefferson",
            display_name="Justin Jefferson",
            full_name="Justin Jefferson",
            position="WR",
            current_team="MIN",
        ),
    ]


class ClaimImportTests(unittest.TestCase):
    def test_feature_flag_defaults_false(self):
        self.assertFalse(compat_flag_enabled(USE_CLAIM_LEDGER_UI, {}))
        self.assertTrue(compat_flag_enabled(USE_CLAIM_LEDGER_UI, {USE_CLAIM_LEDGER_UI: "true"}))

    def test_csv_parse_valid_file(self):
        rows = claim_import.parse_claim_csv(CSV_HEADER + "\n" + csv_row())

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_name"], "Analyst X")
        self.assertEqual(rows[0]["claim_type"], "breakout")

    def test_csv_parse_missing_required_columns(self):
        with self.assertRaisesRegex(ValueError, "Missing required CSV columns"):
            claim_import.parse_claim_csv("source_name,claim_text\nAnalyst X,Take")

    def test_claim_type_validation(self):
        rows = claim_import.parse_claim_csv(CSV_HEADER + "\n" + csv_row(claim_type="nonsense"))
        preview = claim_import.validate_claim_import_rows(rows)

        self.assertIn("invalid claim_type", preview[0]["validation_errors"][0])
        self.assertFalse(preview[0]["can_write"])

    def test_claim_direction_validation(self):
        rows = claim_import.parse_claim_csv(CSV_HEADER + "\n" + csv_row(claim_direction="moon"))
        preview = claim_import.validate_claim_import_rows(rows)

        self.assertTrue(any("invalid claim_direction" in error for error in preview[0]["validation_errors"]))

    def test_player_name_resolution_exact_match(self):
        preview = claim_import.build_claim_import_preview(
            CSV_HEADER + "\n" + csv_row(),
            identity_rows=[identity_row()],
        )

        self.assertEqual(preview[0]["player_resolution_status"], "resolved")
        self.assertEqual(preview[0]["resolved_players"][0]["player_id_internal"], "pid_1")
        self.assertTrue(preview[0]["can_write"])

    def test_ambiguous_player_resolution_flagged(self):
        preview = claim_import.build_claim_import_preview(
            CSV_HEADER + "\n" + csv_row(player_names="Mike Williams"),
            identity_rows=[
                identity_row(
                    player_id_internal="pid_2",
                    normalized_name="mikewilliams",
                    display_name="Mike Williams",
                    current_team="LAC",
                ),
                identity_row(
                    player_id_internal="pid_3",
                    normalized_name="mikewilliams",
                    display_name="Mike Williams",
                    current_team="PIT",
                ),
            ],
        )

        self.assertEqual(preview[0]["player_resolution_status"], "ambiguous")
        self.assertIn("ambiguous_player_identity", preview[0]["missing_data_flags"])
        self.assertTrue(preview[0]["can_write"])

    def test_unresolved_player_imported_only_as_draft(self):
        row = csv_row()
        csv_text = CSV_HEADER + ",review_status\n" + row + ',"ready_to_grade"'
        preview = claim_import.build_claim_import_preview(csv_text, identity_rows=[])

        self.assertEqual(preview[0]["player_resolution_status"], "unresolved")
        self.assertFalse(preview[0]["can_write"])
        self.assertTrue(any("can only be imported as draft" in error for error in preview[0]["validation_errors"]))

    def test_row_limit_enforced(self):
        content = CSV_HEADER + "\n" + "\n".join([csv_row(), csv_row()])

        with self.assertRaisesRegex(ValueError, "row limit exceeded"):
            claim_import.parse_claim_csv(content, max_rows=1)

    def test_no_network_call_dependencies(self):
        source = Path("src/claim_import.py").read_text(encoding="utf-8")

        self.assertNotIn("requests", source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("httpx", source)

    def test_helper_writes_through_claim_ledger_functions(self):
        preview = claim_import.build_claim_import_preview(
            CSV_HEADER + "\n" + csv_row(),
            identity_rows=[identity_row()],
        )

        with patch("src.claim_import.claim_ledger.register_claim_source") as source_mock, patch(
            "src.claim_import.claim_ledger.create_fantasy_claim",
            return_value={"claim": {"claim_id": "claim_1"}},
        ) as claim_mock:
            result = claim_import.write_claim_import_rows(preview, dry_run=True)

        self.assertEqual(result["written_count"], 1)
        source_mock.assert_called_once()
        claim_mock.assert_called_once()
        self.assertEqual(claim_mock.call_args.kwargs["review_status"], "draft")
        self.assertEqual(claim_mock.call_args.kwargs["identity_rows"], [])

    def test_export_errors_csv(self):
        rows = claim_import.validate_claim_import_rows(
            [{"row_number": 2, "source_name": "", "claim_text": "", "claim_type": "bad"}]
        )

        output = claim_import.export_claim_import_errors(rows)

        self.assertIn("row_number", output)
        self.assertIn("source_name is required", output)

    def test_sample_claim_fixture_is_draft_only_and_labeled_demo(self):
        rows = claim_import.parse_claim_csv(SAMPLE_CLAIM_IMPORT_PATH.read_text(encoding="utf-8"))

        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertEqual(row["review_status"], "draft")
            self.assertIn("DEMO CLAIM - DO NOT USE FOR PUBLIC CONTENT", row["claim_text"])
            self.assertIn("DEMO CLAIM - DO NOT USE FOR PUBLIC CONTENT", row["notes"])

    def test_sample_claim_fixture_preview_resolves_and_flags_unresolved(self):
        preview = claim_import.build_claim_import_preview(
            SAMPLE_CLAIM_IMPORT_PATH.read_text(encoding="utf-8"),
            identity_rows=sample_identity_rows(),
        )

        statuses = [row["player_resolution_status"] for row in preview]
        self.assertEqual(statuses.count("resolved"), 2)
        self.assertEqual(statuses.count("unresolved"), 1)
        self.assertTrue(all(row["claim"]["review_status"] == "draft" for row in preview))
        unresolved = [row for row in preview if row["player_resolution_status"] == "unresolved"][0]
        self.assertTrue(unresolved["can_write"])
        self.assertIn("missing_player_id_internal", unresolved["missing_data_flags"])

    def test_sample_claim_fixture_does_not_include_urls_to_fetch(self):
        rows = claim_import.parse_claim_csv(SAMPLE_CLAIM_IMPORT_PATH.read_text(encoding="utf-8"))

        self.assertTrue(all(not row["source_url"] for row in rows))


if __name__ == "__main__":
    unittest.main()
