"""Small computational safeguards, not scientific validation."""
import unittest
from pathlib import Path
from audit_pilot_semantics import finite_numeric
from build_reproducibility_bundle import SCIENCE_FILES, sanitise_paths
from harmonise_pilot import classify


class ReleaseAuditTests(unittest.TestCase):
    def test_finite_numeric(self):
        for value in ('0', '0.05', '-1', '1e-4'):
            self.assertTrue(finite_numeric(value))
        for value in ('', 'N_A', 'nan', 'inf', '<0.1', None):
            self.assertFalse(finite_numeric(value))

    def test_candidate_boundary(self):
        self.assertEqual(classify('Eggplant'), 'other')
        self.assertEqual(classify('Plant-based milk'), 'other')
        self.assertEqual(classify('Milk'), 'animal_food_candidate')
        self.assertEqual(classify('Fish feed'), 'feed_candidate')

    def test_release_excludes_administrative_and_nested_archives(self):
        self.assertEqual(len(SCIENCE_FILES), len(set(SCIENCE_FILES)))
        self.assertTrue(all(not name.startswith('09_submission/') and not name.endswith(('.zip', '.xlsx')) for name in SCIENCE_FILES))

    def test_sanitisation_retains_verification_time(self):
        root = Path('/') / 'Volumes' / 'test'
        source = ('{"generated_utc":"2026-09-30T02:01:00Z","path":"' + str(root / 'a') + '"}').encode()
        clean = sanitise_paths(source, {'data_root': root})
        self.assertIn(b'2026-09-30T02:01:00Z', clean)
        self.assertNotIn(b'/Volumes/', clean)
        with self.assertRaises(ValueError):
            sanitise_paths(str(Path('/') / 'Users' / 'unknown' / 'private').encode(), {})


if __name__ == '__main__':
    unittest.main()
