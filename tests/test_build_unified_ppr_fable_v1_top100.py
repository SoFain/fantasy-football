import unittest

from scripts.build_unified_ppr_fable_v1_top100 import HALF_PPR_REPLACEMENT, PPR_REPLACEMENT


class BuildUnifiedPprFableV1Top100Test(unittest.TestCase):
    def test_ppr_replacement_contract_is_separate_from_standard(self):
        self.assertEqual(PPR_REPLACEMENT, {"QB": 13, "RB": 30, "WR": 44, "TE": 9})
        self.assertEqual(HALF_PPR_REPLACEMENT,{"QB":13,"RB":34,"WR":42,"TE":9})


if __name__ == "__main__":
    unittest.main()
