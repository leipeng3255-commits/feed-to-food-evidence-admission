"""Check assumed-cap algebra and independently reconstruct delivered statistics."""
import csv
import math
import unittest
from collections import defaultdict
from np_temporal_20261008 import np_hist,sufficient,base_interval,paths,THRESHOLDS,in_ppb,envelope
from information_loss_20261008 import metrics

class TestNPSensitivity(unittest.TestCase):
    def test_ppm_converts_before_binning(self):
        self.assertEqual(in_ppb(.02,'M'),20)
        self.assertEqual(in_ppb(.005,'M'),5)
        self.assertEqual(envelope(in_ppb(.02,'M')),(10,100))
        self.assertEqual(in_ppb(20,'B'),20)
    def test_np_changes_only_cap(self):
        rs=[{'state':'O','value':10,'lod':1,'raw_value_blank':False},
            {'state':'ND','value':None,'lod':2,'raw_value_blank':True},
            {'state':'NP','value':None,'lod':3,'raw_value_blank':True}]
        for k in (1,2,5,10):
            m=metrics(np_hist(rs,k));self.assertEqual(m['n'],3)
            self.assertAlmostEqual(m['lower'],10/3)
            self.assertAlmostEqual(m['upper'],(12+3*k)/3)
        self.assertTrue(math.isinf(metrics(np_hist(rs,math.inf))['upper']))
    def test_np_missing_not_dropped(self):
        r={'state':'NP','value':None,'lod':None,'raw_value_blank':True}
        s=sufficient(np_hist([r],1));self.assertEqual(s['n'],1)
        self.assertEqual(s['n_unbounded'],1);self.assertTrue(math.isinf(s['sum_upper_ppb']))
    def test_nonNP_invariance(self):
        rs=[{'state':'R','value':10,'lod':1,'raw_value_blank':False}]
        self.assertEqual(np_hist(rs,1),np_hist(rs,math.inf))
    def test_conflicting_ND_is_unknown(self):
        r={'state':'ND','value':3,'lod':1,'raw_value_blank':False}
        self.assertIsNone(base_interval(r))
        self.assertTrue(math.isinf(metrics(np_hist([r],1))['upper']))
    def test_real_sufficient_statistics(self):
        p=paths()['animal_food_outputs_root']/'np_temporal_20261008'
        with (p/'NP_scenarios_all_cells.csv').open() as f:rs=list(csv.DictReader(f))
        with (p/'filled_reporting_template.csv').open() as f:stats=list(csv.DictReader(f))
        self.assertEqual(len(rs),3425);self.assertEqual(len(stats),3425)
        by=defaultdict(list)
        for r,s in zip(rs,stats):
            self.assertEqual((r['year'],r['commodity'],r['analyte'],r['factor']),(s['year'],s['commodity'],s['analyte'],s['NP_assumed_factor']))
            self.assertEqual(int(r['n_all']),int(s['n']))
            for end in ['lower','upper']:
                self.assertAlmostEqual(float(r[end]),float(s[f'sum_{end}_ppb'])/int(s['n']))
                for t in THRESHOLDS:
                    self.assertAlmostEqual(float(r[f'above_{t:g}_{end}']),int(s[f'count_{end}_above_{t:g}'])/int(s['n']))
            by[(r['year'],r['commodity'],r['analyte'])].append(r)
        for group in by.values():
            self.assertEqual(len({r['n_all'] for r in group}),1)
            self.assertEqual(len({r['lower'] for r in group}),1)
            for a,b in zip(group,group[1:]):self.assertLessEqual(float(a['upper']),float(b['upper']))
            if group[0]['n_NP']=='0':self.assertEqual(len({r['upper'] for r in group}),1)
            else:
                u1,u10=float(group[0]['upper']),float(group[3]['upper'])
                if math.isfinite(u10) and u1>0:
                    self.assertGreaterEqual(u10/u1,1-1e-12);self.assertLessEqual(u10/u1,10+1e-12)
    def test_temporal_saved_histograms(self):
        p=paths()['animal_food_outputs_root']/'np_temporal_20261008'
        with (p/'catfish_2010_cells.csv').open() as f:cells={r['analyte']:r for r in csv.DictReader(f)}
        h=defaultdict(list)
        with (p/'catfish_2010_histograms.csv').open() as f:
            for r in csv.DictReader(f):h[(r['analyte'],r['level'])].append(r)
        self.assertEqual(len(cells),195)
        self.assertEqual(sum(int(r['n_all']) for r in cells.values()),73433)
        for (a,l),rows in h.items():
            n=sum(int(r['count']) for r in rows)
            self.assertEqual(n,int(cells[a]['n_working']))
            for end in ['lower','upper']:
                value=sum(float(r[end+'_ppb'])*int(r['count']) for r in rows)/n
                self.assertAlmostEqual(value,float(cells[a][l+'_'+end]))
                for t in THRESHOLDS:
                    fraction=sum(int(r['count']) for r in rows if float(r[end+'_ppb'])>t)/n
                    self.assertAlmostEqual(fraction,float(cells[a][f'{l}_above_{t:g}_{end}']))

if __name__=='__main__':unittest.main()
