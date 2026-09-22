import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.publish_ppr_fable_v1_candidate_boards import DECISIONS, WRITE_GATE, reviewed_rows


class PublishPprFableV1CandidateBoardsTest(unittest.TestCase):
    def test_decisions_cover_approved_review_list(self):
        self.assertEqual(len(DECISIONS), 7)
        self.assertEqual(DECISIONS["DK Metcalf"][1], "ACCEPT_FABLE")
        self.assertEqual(DECISIONS["Stefon Diggs"][1], "EXCLUDE_UNSIGNED")
        self.assertFalse(DECISIONS["Zach Charbonnet"][2])

    def test_write_gate_is_scoped(self):
        self.assertEqual(WRITE_GATE, "ALLOW_PPR_FABLE_CANDIDATE_PUBLISH")

    def test_formula_default_does_not_freeze_pre_safety_rank(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "board.json"
            path.write_text(json.dumps([{"player_name": "Example", "formula_rank": 12}]), encoding="utf-8")
            row = reviewed_rows(path)[0]
        self.assertIsNone(row["recommended_rank"])
        self.assertEqual(row["decision_code"], "FORMULA_DEFAULT")


if __name__ == "__main__":
    unittest.main()
