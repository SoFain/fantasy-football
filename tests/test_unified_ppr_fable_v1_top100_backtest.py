import unittest

from scripts.run_unified_ppr_fable_v1_top100_backtest import HALF_VARIANTS, VARIANTS


class UnifiedPprFableV1Top100BacktestTest(unittest.TestCase):
    def test_selected_and_sensitivity_variants_are_bounded(self):
        self.assertEqual(VARIANTS["selected_rb30_wr44_te9"], {"QB":13,"RB":30,"WR":44,"TE":9})
        self.assertEqual(len(VARIANTS), 6)
        self.assertEqual(HALF_VARIANTS["selected_rb32_wr42_te9"],{"QB":13,"RB":32,"WR":42,"TE":9})


if __name__=="__main__":
    unittest.main()
