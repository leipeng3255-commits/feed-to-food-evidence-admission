"""Portable-verifier regression fixtures; no project or raw-data dependencies."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from verify_supplement_bundle import equal,file_hashes,np_rows,full_denominator

def fixture():
    r={'year':'2010','commodity':'FC','analyte':'TOY','factor':'1','n_all':'2','lower':'2','upper':'3'}
    s={'year':'2010','commodity':'FC','analyte':'TOY','NP_assumed_factor':'1','n':'2','sum_lower_ppb':'4','sum_upper_ppb':'6'}
    for t in (2,10,20):
        for end in ('lower','upper'):
            count=1 if t==2 and end=='upper' else 0
            r[f'above_{t}_{end}']=str(count/2);s[f'count_{end}_above_{t}']=str(count)
    return r,s

class PortableVerifier(unittest.TestCase):
    def test_mean_and_strict_threshold_reconstruction(self):
        r,s=fixture();self.assertEqual(np_rows([r],[s]),1)
        equal(float('inf'),float('inf'))
        with self.assertRaises(ValueError):equal(float('nan'),0)
        full_denominator([{'n_all':'2','n_working':'1','n_NP':'1','n_invalid':'0',
            'R0_lower':'4','R0_upper':'4','full_lower':'2','full_upper':'inf'}])
    def test_changed_endpoint_rejected(self):
        r,s=fixture();s['sum_upper_ppb']='8'
        with self.assertRaises(ValueError):np_rows([r],[s])
    def test_wrong_identity_rejected(self):
        r,s=fixture();s['analyte']='OTHER'
        with self.assertRaises(ValueError):np_rows([r],[s])
    def test_denominator_and_count_rejected(self):
        r,s=fixture();s['n']='0'
        with self.assertRaises(ValueError):np_rows([r],[s])
        r,s=fixture();s['count_upper_above_2']='3'
        with self.assertRaises(ValueError):np_rows([r],[s])
    def test_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'a').write_bytes(b'changed')
            (p/'MANIFEST.json').write_text(json.dumps({'a':hashlib.sha256(b'original').hexdigest()}))
            with self.assertRaises(ValueError):file_hashes(p)
    def test_outside_manifest_path_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'MANIFEST.json').write_text(json.dumps({'../outside':'0'*64}))
            with self.assertRaises(ValueError):file_hashes(p)

if __name__=='__main__':unittest.main()
