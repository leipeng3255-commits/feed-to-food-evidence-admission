"""Synthetic boundary tests plus independent reconstruction of real aggregates."""
import csv
import math
import unittest
from collections import defaultdict
from information_loss_20261008 import envelope, metrics, finite, paths, THRESHOLDS

class TestBoundaries(unittest.TestCase):
    def test_bin_edges(self):
        self.assertEqual(envelope(0), (0,1))
        self.assertEqual(envelope(1), (1,10))
        self.assertEqual(envelope(10), (10,100))
        self.assertEqual(envelope(1000), (1000,math.inf))
    def test_invalid(self):
        for v in ('','nan','inf','-1'):
            self.assertIsNone(finite(v))
        self.assertIsNone(finite('0',True))
    def test_strict_threshold(self):
        m=metrics({(0,10):1,(10,10):1,(20,20):1})
        self.assertEqual(m['above_10_lower'],1/3)
        self.assertEqual(m['above_10_upper'],1/3)
    def test_unknown_is_unbounded(self):
        self.assertTrue(math.isinf(metrics({(0,math.inf):1})['upper']))
    def test_real_histograms(self):
        out=paths()['animal_food_outputs_root']/'information_loss_20261008'
        with (out/'all_cells.csv').open() as f:
            cells={(r['commodity'],r['analyte']):r for r in csv.DictReader(f)}
        hs=defaultdict(list)
        with (out/'retained_interval_histograms.csv').open() as f:
            for r in csv.DictReader(f):
                hs[(r['commodity'],r['analyte'],r['level'])].append((float(r['lower_ppb']),float(r['upper_ppb']),int(r['count'])))
        self.assertEqual(len(cells),490)
        self.assertEqual(sum(int(r['n_all']) for r in cells.values()),192170)
        self.assertEqual(sum(int(r['n_NP']) for r in cells.values()),13965)
        self.assertEqual(sum(int(r['n_working']) for r in cells.values()),178205)
        for (c,a,level),rows in hs.items():
            r=cells[(c,a)];n=sum(k for lo,hi,k in rows)
            self.assertEqual(n,int(r['n_working']))
            # Reconstruct without calling the analysis metrics routine.
            for end,pos in [('lower',0),('upper',1)]:
                value=sum(x[pos]*x[2] for x in rows)/n
                self.assertAlmostEqual(value,float(r[f'{level}_{end}']))
                for t in THRESHOLDS:
                    fraction=sum(x[2] for x in rows if x[pos]>t)/n
                    self.assertAlmostEqual(fraction,float(r[f'{level}_above_{t:g}_{end}']))
        for r in cells.values():
            if int(r['n_NP']): self.assertTrue(math.isinf(float(r['full_upper'])))
            if int(r['n_working']):
                for lower,upper in [('R0','R1'),('R1','R2'),('R1','R1_coarse')]:
                    self.assertLessEqual(float(r[upper+'_lower']),float(r[lower+'_lower'])+1e-10)
                    self.assertGreaterEqual(float(r[upper+'_upper'])+1e-10,float(r[lower+'_upper']))

if __name__=='__main__': unittest.main()
