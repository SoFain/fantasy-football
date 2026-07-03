from __future__ import annotations

import unittest
from pathlib import Path


class ScoringProfileSeedTests(unittest.TestCase):
    def test_gng_keeper_seed_is_present_and_preserves_te_premium(self):
        sql = Path("bigquery/migrations/0029__gng_keeper_scoring_profile_seed.sql").read_text(encoding="utf-8")

        self.assertIn("'gng_keeper'", sql)
        self.assertIn("'GNG Keeper'", sql)
        self.assertIn('"source_league_id":"1369406895588143104"', sql)
        self.assertIn('"bonus_rec_te":0.2', sql)
        self.assertIn('"bonus_rec_wr":0.1', sql)


if __name__ == "__main__":
    unittest.main()
