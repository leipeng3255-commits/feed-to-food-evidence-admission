"""Synthetic arithmetic and source-receipt fail-closed regression tests."""
import tempfile
import unittest
from pathlib import Path
from reporting_counterexamples import examples, interval_summary, paired_summary
from reporting_reproduction import source_receipt, output_root
from information_loss_20261008 import paths

class TestReportingRevision(unittest.TestCase):
    def test_same_mean_different_threshold(self):
        a,b=examples()['same_mean_different_threshold']['cases']
        self.assertEqual((a['n'],a['mean_lower'],a['mean_upper']),(b['n'],b['mean_lower'],b['mean_upper']))
        self.assertEqual((a['fraction_upper'],b['fraction_upper']),(.5,0))
    def test_same_marginals_different_joint(self):
        a,b=examples()['same_marginals_different_joint']['cases']
        for k in ['n','marginal_A','marginal_B','A_above','B_above']:self.assertEqual(a[k],b[k])
        self.assertEqual((a['joint_above'],b['joint_above']),(.5,0))
    def test_strict_threshold_and_invalid_pairing(self):
        self.assertEqual(interval_summary([(10,10)],10)['fraction_upper'],0)
        with self.assertRaises(AssertionError):paired_summary([3,1],[3],2)
    def test_public_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'usda_pdp/2009PDPDatabase.zip'
            source.parent.mkdir();source.write_bytes(b'NOT_A_FROZEN_ARCHIVE')
            with self.assertRaises(AssertionError):source_receipt(source,{'raw_data_root':root},True)
    def test_project_mode_does_not_use_public_receipt_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'unknown.zip';source.write_bytes(b'SYNTHETIC')
            with self.assertRaises((AssertionError,FileNotFoundError)):source_receipt(source,{'raw_data_root':root},False)
    def test_output_is_separate_and_configured(self):
        c=paths()
        self.assertEqual(output_root(c),c['animal_food_outputs_root'])
        self.assertEqual(output_root(c,True).parent,c['animal_food_outputs_root'])
        self.assertNotEqual(output_root(c,True),output_root(c))

if __name__ == '__main__':unittest.main()
