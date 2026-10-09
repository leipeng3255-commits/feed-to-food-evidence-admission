# Portable S4/S5 supplementary checks

The supplied journal S4/S5 reproduction ZIPs now include verify_supplement_bundle.py at their root. Extract a ZIP into a separate folder, then run from that folder:

```sh
python3 -I -S verify_supplement_bundle.py
```

The same original checker is published in the branch's 05_code directory. From this repository, choose the extracted bundle explicitly:

```sh
python3 -I -S 11_research_branches/animal_food_feed_transfer/05_code/verify_supplement_bundle.py --bundle /absolute/path/to/extracted/S4-or-S5
```

Only Python's standard library is used. No project paths.yaml, PyYAML, raw monitoring records or network are read. S4 checks all manifest-listed hashes, four retained histogram levels and full-denominator enclosures for490 source cells. S5 checks manifest hashes,3425 NP mean/fixed-threshold rows, four2010 histogram levels and the two labelled synthetic collisions. Arithmetic checks use explicit exceptions rather than assert, including under optimization. CSV infinity remains infinity; empty working-cell values are not silently zero-filled.

The older S5-only script also supports an explicit aggregate folder without project imports:

```sh
python3 -I -S 11_research_branches/animal_food_feed_transfer/05_code/verify_np_aggregates.py --aggregates /absolute/path/to/extracted/S5/aggregates
```

Its default mode still requires project configuration. The complete raw-source analysis remains the separate, explicitly configured workflow documented in the prior reporting revision. None of these checks establishes laboratory validity, independent human adjudication, biological prediction or framework superiority. An in-ZIP manifest alone does not authenticate its origin; compare trusted external hashes where available.

Six portable-verifier regression tests cover correct arithmetic, infinity/NaN handling, wrong endpoints/identities/denominators/counts, changed file hashes and paths leaving the bundle. They are synthetic software checks, not new empirical cases. Run them without third-party modules:

```sh
python3 -S -m unittest discover -s 11_research_branches/animal_food_feed_transfer/05_code -p test_supplement_verifier.py
```

Original code: MIT. Original documentation and eligible derived aggregates: CC BY4.0 subject to DATA_RIGHTS.md. No manuscript, author files, raw monitoring rows or third-party full text are added by this update.
