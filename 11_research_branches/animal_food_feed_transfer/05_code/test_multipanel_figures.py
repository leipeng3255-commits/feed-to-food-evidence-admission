"""Aggregate identities, frozen-count reconciliation and SVG structure checks."""
import json
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT/'06_outputs/figures/multipanel_calculation_data.json').read_text())

class FigureAudit(unittest.TestCase):
    def test_histogram_sample_and_row_totals(self):
        for key in ('pesticide','veterinary_drug'):
            d=DATA[key]; h=d['rows_per_sample_histogram']
            self.assertEqual(sum(h.values()),d['candidate_samples'])
            self.assertEqual(sum(int(k)*n for k,n in h.items()),d['candidate_rows'])

    def test_original_result_codes_partition_rows(self):
        for key in ('pesticide','veterinary_drug'):
            d=DATA[key]
            self.assertEqual(sum(d['result_types'].values()),d['candidate_rows'])
            self.assertEqual(sum(d['strategy_samples'].values()),d['candidate_samples'])
            for code,n in d['numeric_types'].items(): self.assertLessEqual(n,d['result_types'][code])

    def test_frozen_counts(self):
        self.assertEqual((DATA['pesticide']['all_rows'],DATA['pesticide']['all_samples']),(346652,710))
        self.assertEqual((DATA['veterinary_drug']['all_rows'],DATA['veterinary_drug']['all_samples']),(375640,11573))
        self.assertEqual(DATA['pesticide']['numeric_types'],{'VAL':21,'LOQ':1})
        self.assertEqual(DATA['veterinary_drug']['numeric_types'],{'VAL':35,'LOQ':4})

    def test_false_positive_denominators(self):
        d=DATA['pesticide']
        self.assertEqual((d['cereal_samples'],d['cereal_rows']),(6,3912))
        self.assertAlmostEqual(100*d['cereal_samples']/d['candidate_samples'],10.714285714)
        self.assertAlmostEqual(100*d['cereal_rows']/d['candidate_rows'],30.505302558)

    def test_source_identity(self):
        expected=['33c131512de84343939916ab315646d46aafaae27467d6ee05d0eaf89e0ff416',
                  'b2c3ff872060439de3f44d006881bd67697c32dd5bad59ae6e13031bf141fb7d',
                  '3f97cc55e08f27e6d9d118771cc0cc2ac06ab050500b7a938d570624b0766f1b',
                  'df185cd2c8d53f0516bf5acaac2089b9fe0ef76aae169f056f67b3268e535fd1']
        self.assertEqual(set(DATA['provenance'].values()),set(expected))

    def test_vector_panel_structure(self):
        ns={'s':'http://www.w3.org/2000/svg'}
        for number,stem,n in [(2,'selection_diagnostics',4),(3,'result_semantics',4),(4,'source_discrepancies',3)]:
            root=ET.parse(ROOT/f'06_outputs/figures/figure{number}_{stem}.svg').getroot()
            groups=root.findall('.//s:g',ns)
            self.assertEqual(sum(g.get('id','').startswith('axes_') for g in groups),n)
            self.assertFalse(root.findall('.//s:image',ns))
            self.assertGreaterEqual(len(root.findall('.//s:text',ns)),20)

    def test_publication_typography(self):
        files=list((ROOT/'06_outputs/figures').glob('figure*_layout_qa.json'))
        self.assertEqual(len(files),4)
        for path in files:
            qa=json.loads(path.read_text())
            self.assertFalse(qa['canvas_overflow'])
            self.assertFalse(qa['text_box_collisions'])
            self.assertGreaterEqual(qa['minimum_at_6_5_inch_width_pt'],8)

    def test_reference_targets(self):
        qa=json.loads((ROOT/'08_review/reference_count_and_citation_audit_20260930.json').read_text())
        self.assertGreaterEqual(qa['total_references'],35)
        self.assertGreaterEqual(qa['recent_references'],25)
        self.assertGreaterEqual(qa['recent_journal_articles_excluding_supporting_reports_and_datasets'],25)
        self.assertFalse(qa['orphan_references'])
        self.assertFalse(qa['orphan_intext_keys'])

if __name__=='__main__': unittest.main()
