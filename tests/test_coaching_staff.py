import json
import unittest

from src import coaching_staff as cs


class TeamAndRoleConstantsTest(unittest.TestCase):
    def test_thirty_two_teams(self):
        self.assertEqual(len(cs.NFL_TEAMS), 32)

    def test_eight_canonical_roles(self):
        self.assertEqual(len(cs.CANONICAL_ROLES), 8)
        self.assertEqual(cs.ROLE_KEYS[0], "head_coach")

    def test_role_ranks_unique_and_ordered(self):
        ranks = [rank for _, _, rank in cs.CANONICAL_ROLES]
        self.assertEqual(ranks, sorted(ranks))
        self.assertEqual(len(set(ranks)), len(ranks))

    def test_team_abbrs_match_news_feed_layer(self):
        from src.team_news_feeds import TEAM_FEEDS

        self.assertEqual(set(cs.NFL_TEAMS), set(TEAM_FEEDS))


class NormalizeRoleTest(unittest.TestCase):
    def test_canonical_key_passthrough(self):
        self.assertEqual(cs.normalize_role("offensive_coordinator"), "offensive_coordinator")

    def test_wikipedia_labels(self):
        self.assertEqual(cs.normalize_role("Quarterbacks"), "quarterbacks_coach")
        self.assertEqual(cs.normalize_role("Offensive line"), "offensive_line_coach")
        self.assertEqual(cs.normalize_role("Head coach"), "head_coach")

    def test_senior_assistant_variants_collapse(self):
        # A senior assistant on one team is an assistant head coach on another.
        self.assertEqual(cs.normalize_role("Senior assistant"), "senior_assistant")
        self.assertEqual(cs.normalize_role("Assistant head coach"), "senior_assistant")

    def test_unknown_label(self):
        self.assertIsNone(cs.normalize_role("Special teams coordinator"))
        self.assertIsNone(cs.normalize_role(None))


class PrepareRowsTest(unittest.TestCase):
    def test_empty_csv_still_emits_full_grid(self):
        rows = cs.prepare_rows([], snapshot_at="2026-07-24T00:00:00Z", source_url="u")
        self.assertEqual(len(rows), 32 * 8)
        self.assertTrue(all(r["is_vacant"] for r in rows))

    def test_populated_row_lands(self):
        csv_rows = [{"team_abbr": "KC", "role": "head_coach", "coach_name": "Andy Reid", "verification_status": "verified"}]
        rows = cs.prepare_rows(csv_rows, snapshot_at="t", source_url="u")
        kc_hc = next(r for r in rows if r["team_abbr"] == "KC" and r["role"] == "head_coach")
        self.assertEqual(kc_hc["coach_name"], "Andy Reid")
        self.assertFalse(kc_hc["is_vacant"])
        self.assertEqual(kc_hc["verification_status"], "verified")
        self.assertEqual(json.loads(kc_hc["missing_fields_json"]), [])

    def test_role_alias_from_csv(self):
        csv_rows = [{"team_abbr": "BUF", "role": "Quarterbacks", "coach_name": "Coach X"}]
        rows = cs.prepare_rows(csv_rows, snapshot_at="t", source_url="u")
        buf_qb = next(r for r in rows if r["team_abbr"] == "BUF" and r["role"] == "quarterbacks_coach")
        self.assertEqual(buf_qb["coach_name"], "Coach X")

    def test_vacant_row_flagged_missing(self):
        rows = cs.prepare_rows([], snapshot_at="t", source_url="u")
        any_row = rows[0]
        self.assertIn("missing_coach_name", json.loads(any_row["missing_fields_json"]))

    def test_filled_but_pending_flagged_unverified(self):
        csv_rows = [{"team_abbr": "SF", "role": "head_coach", "coach_name": "Coach Y", "verification_status": "pending"}]
        rows = cs.prepare_rows(csv_rows, snapshot_at="t", source_url="u")
        sf_hc = next(r for r in rows if r["team_abbr"] == "SF" and r["role"] == "head_coach")
        self.assertIn("unverified", json.loads(sf_hc["missing_fields_json"]))
        self.assertNotIn("missing_coach_name", json.loads(sf_hc["missing_fields_json"]))

    def test_unknown_team_raises(self):
        with self.assertRaisesRegex(ValueError, "unknown team_abbr"):
            cs.prepare_rows([{"team_abbr": "XXX", "role": "head_coach"}], snapshot_at="t", source_url="u")

    def test_unknown_role_raises(self):
        with self.assertRaisesRegex(ValueError, "unknown role"):
            cs.prepare_rows([{"team_abbr": "KC", "role": "General manager"}], snapshot_at="t", source_url="u")

    def test_duplicate_team_role_raises(self):
        csv_rows = [
            {"team_abbr": "KC", "role": "head_coach", "coach_name": "A"},
            {"team_abbr": "KC", "role": "Head coach", "coach_name": "B"},
        ]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            cs.prepare_rows(csv_rows, snapshot_at="t", source_url="u")

    def test_invalid_verification_status_raises(self):
        csv_rows = [{"team_abbr": "KC", "role": "head_coach", "coach_name": "A", "verification_status": "maybe"}]
        with self.assertRaisesRegex(ValueError, "verification_status"):
            cs.prepare_rows(csv_rows, snapshot_at="t", source_url="u")

    def test_lowercases_team_abbr(self):
        rows = cs.prepare_rows([{"team_abbr": "kc", "role": "head_coach", "coach_name": "A"}], snapshot_at="t", source_url="u")
        self.assertTrue(any(r["team_abbr"] == "KC" and r["coach_name"] == "A" for r in rows))


class BuildDatasetTest(unittest.TestCase):
    def _rows(self):
        csv_rows = [
            {"team_abbr": "KC", "role": "head_coach", "coach_name": "Andy Reid", "verification_status": "verified"},
        ]
        return cs.prepare_rows(csv_rows, snapshot_at="t", source_url="u")

    def test_dataset_shape(self):
        ds = cs.build_dataset(self._rows(), source_generated_at="2026-07-24T00:00:00Z", source_url="u")
        self.assertEqual(ds["dataset"], "coaching_staff")
        self.assertEqual(ds["team_count"], 32)
        self.assertEqual(len(ds["teams"]), 32)
        self.assertEqual(len(ds["roles"]), 8)

    def test_team_has_eight_roles_in_rank_order(self):
        ds = cs.build_dataset(self._rows(), source_generated_at="t", source_url="u")
        kc = next(t for t in ds["teams"] if t["team_abbr"] == "KC")
        self.assertEqual([c["rank"] for c in kc["coaches"]], [1, 2, 3, 4, 5, 6, 7, 8])
        hc = next(c for c in kc["coaches"] if c["role"] == "head_coach")
        self.assertEqual(hc["coach_name"], "Andy Reid")
        self.assertFalse(hc["vacant"])

    def test_vacant_and_pending_counts(self):
        csv_rows = [
            {"team_abbr": "KC", "role": "head_coach", "coach_name": "Andy Reid", "verification_status": "verified"},
            {"team_abbr": "SF", "role": "head_coach", "coach_name": "Coach Y", "verification_status": "pending"},
        ]
        ds = cs.build_dataset(cs.prepare_rows(csv_rows, snapshot_at="t", source_url="u"),
                              source_generated_at="t", source_url="u")
        # 256 total roles, 2 filled, so 254 vacant; 1 filled-but-pending.
        self.assertEqual(ds["vacant_count"], 254)
        self.assertEqual(ds["pending_count"], 1)

    def test_special_characters_survive_json(self):
        csv_rows = [{"team_abbr": "KC", "role": "head_coach", "coach_name": "A & B <x> \"q\""}]
        ds = cs.build_dataset(cs.prepare_rows(csv_rows, snapshot_at="t", source_url="u"),
                              source_generated_at="t", source_url="u")
        content = cs.canonical_json_bytes(ds)
        reparsed = json.loads(content)
        kc = next(t for t in reparsed["teams"] if t["team_abbr"] == "KC")
        hc = next(c for c in kc["coaches"] if c["role"] == "head_coach")
        self.assertEqual(hc["coach_name"], "A & B <x> \"q\"")


class ContentAddressingTest(unittest.TestCase):
    def test_canonical_bytes_are_deterministic(self):
        rows = cs.prepare_rows([], snapshot_at="fixed", source_url="u")
        ds = cs.build_dataset(rows, source_generated_at="fixed", source_url="u")
        self.assertEqual(cs.canonical_json_bytes(ds), cs.canonical_json_bytes(ds))

    def test_sha256_matches_bytes(self):
        import hashlib

        content = b'{"a":1}\n'
        self.assertEqual(cs.sha256_hex(content), hashlib.sha256(content).hexdigest())


class ManifestEntryTest(unittest.TestCase):
    def _entry(self):
        rows = cs.prepare_rows([], snapshot_at="t", source_url="u")
        ds = cs.build_dataset(rows, source_generated_at="2026-07-24T05:00:00Z", source_url="u")
        content = cs.canonical_json_bytes(ds)
        return cs.manifest_entry(
            content=content,
            object_name="v1/datasets/coaching_staff/sha256-abc.json",
            url="https://example/abc.json",
            source_generated_at="2026-07-24T05:00:00Z",
            dataset=ds,
        )

    def test_entry_is_field_compatible_with_board_entries(self):
        entry = self._entry()
        # These are the fields the live manifest's board entries carry.
        for key in ("sha256", "bytes", "object", "url", "source_generated_at", "warnings"):
            self.assertIn(key, entry)
        self.assertEqual(entry["dataset"], "coaching_staff")

    def test_sha256_and_bytes_describe_the_object(self):
        rows = cs.prepare_rows([], snapshot_at="t", source_url="u")
        ds = cs.build_dataset(rows, source_generated_at="2026-07-24T05:00:00Z", source_url="u")
        content = cs.canonical_json_bytes(ds)
        entry = cs.manifest_entry(content=content, object_name="o", url="u",
                                  source_generated_at="2026-07-24T05:00:00Z", dataset=ds)
        self.assertEqual(entry["sha256"], cs.sha256_hex(content))
        self.assertEqual(entry["bytes"], len(content))

    def test_dataset_version_is_stable_and_tagged(self):
        v = cs.dataset_version("2026-07-24T05:00:00Z")
        self.assertTrue(v.startswith("coaching_staff-1.0-"))


if __name__ == "__main__":
    unittest.main()
