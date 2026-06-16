import unittest

from scripts import build_image_tag


class BuildImageTagTests(unittest.TestCase):
    def test_staging_tag_uses_short_sha_and_timestamp(self) -> None:
        tag = build_image_tag.build_image_tag(
            "staging",
            "ABCDEF1234567890",
            timestamp="20260616T120000Z",
        )

        self.assertEqual(tag, "staging-abcdef123456-20260616T120000Z")
        self.assertNotIn("latest", tag)

    def test_prod_candidate_tag_uses_timestamp(self) -> None:
        tag = build_image_tag.build_image_tag(
            "prod-candidate",
            "1234567890abcdef",
            timestamp="20260616T120000Z",
        )

        self.assertEqual(tag, "prod-candidate-1234567890ab-20260616T120000Z")

    def test_prod_tag_requires_release_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "release-id"):
            build_image_tag.build_image_tag("prod", "abcdef1234567890")

    def test_prod_tag_uses_release_id(self) -> None:
        tag = build_image_tag.build_image_tag(
            "prod",
            "abcdef1234567890",
            release_id="r2026.06.16",
        )

        self.assertEqual(tag, "prod-abcdef123456-r2026.06.16")

    def test_rejects_invalid_sha(self) -> None:
        with self.assertRaisesRegex(ValueError, "SHA"):
            build_image_tag.build_image_tag("staging", "not-a-sha")


if __name__ == "__main__":
    unittest.main()
