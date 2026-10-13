"""Portable negative fixtures. Set DAIRY_EGG_TEST_ASSETS to aggregate directory."""
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('verify_dairy_egg_bundle.py')
spec = importlib.util.spec_from_file_location('dairy_verifier', SCRIPT)
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class DairyBundleTests(unittest.TestCase):
    def setUp(self):
        source = Path(os.environ.get('DAIRY_EGG_TEST_ASSETS', SCRIPT.parent))
        if not (source/'all_cells.csv').is_file():
            self.skipTest('Set DAIRY_EGG_TEST_ASSETS to aggregate-only directory')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in verifier.REQUIRED:
            shutil.copyfile(source/name, self.root/name)
        for name in ('coverage.csv','coverage_and_units.json'):
            if (source/name).is_file():
                shutil.copyfile(source/name,self.root/name)
        self.manifest()

    def manifest(self):
        entries = [{'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                   for p in sorted(self.root.iterdir()) if p.is_file() and p.name!='MANIFEST.json']
        (self.root/'MANIFEST.json').write_text(json.dumps({'files':entries}))

    def edit(self, name, mutate):
        with (self.root/name).open(newline='') as handle:
            reader = csv.DictReader(handle); fields=reader.fieldnames; data=list(reader)
        mutate(data)
        with (self.root/name).open('w',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(data)
        self.manifest()  # Rehash: failures must come from arithmetic, not digest mismatch.

    def rejected(self):
        with self.assertRaises(ValueError):
            verifier.verify(self.root)

    def test_valid_standard_and_isolated_optimized(self):
        self.assertEqual(verifier.verify(self.root)['working_cells'],1257)
        for options in [('-I','-S'),('-I','-S','-O')]:
            result=subprocess.run([sys.executable,*options,str(SCRIPT),'--bundle',str(self.root)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_rehashed_endpoint_tamper(self):
        self.edit('retained_histograms.csv',lambda data:data[0].update(upper_ppb='21'))
        self.rejected()
        result=subprocess.run([sys.executable,'-I','-S','-O',str(SCRIPT),'--bundle',str(self.root)],capture_output=True)
        self.assertNotEqual(result.returncode,0)

    def test_rehashed_missing_histogram(self):
        self.edit('retained_histograms.csv',lambda data:data.pop(0))
        self.rejected()

    def test_rehashed_denominator_tamper(self):
        self.edit('all_cells.csv',lambda data:data[0].update(n_all=str(int(data[0]['n_all'])+1)))
        self.rejected()

    def test_rehashed_strict_threshold_tamper(self):
        self.edit('filled_reporting_statistics.csv',lambda data:data[0].update(count_upper_above_20='1'))
        self.rejected()

    def test_rehashed_stratum_tamper(self):
        self.edit('stratum_summary.csv',lambda data:data[0].update(working_cells='0'))
        self.rejected()

    def test_manifest_escape(self):
        manifest=json.loads((self.root/'MANIFEST.json').read_text())
        manifest['files'].append({'path':'../outside.csv','sha256':'0'*64})
        (self.root/'MANIFEST.json').write_text(json.dumps(manifest))
        self.rejected()

    def test_rehashed_coverage_tamper(self):
        if not (self.root/'coverage.csv').is_file():
            self.skipTest('Coverage extension not present')
        self.edit('coverage.csv',lambda data:data[0].update(coverage_fraction='0'))
        self.rejected()

    def test_rehashed_unit_factor_tamper(self):
        target=self.root/'coverage_and_units.json'
        if not target.is_file():
            self.skipTest('Unit extension not present')
        data=json.loads(target.read_text());data['unit_evidence'][0]['M_factor']=1
        target.write_text(json.dumps(data));self.manifest();self.rejected()

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as external:
            outside=Path(external)/'outside.csv';outside.write_text('not allowed')
            (self.root/'escape.csv').symlink_to(outside)
            self.manifest();self.rejected()


if __name__ == '__main__':
    unittest.main()
