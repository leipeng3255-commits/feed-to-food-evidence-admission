# Reporting-information extension, 8 October 2026

Original frozen-rule code, protocols, editable Figures 6-7 and aggregate sufficient statistics for Supplements S4-S5. NP caps of 1,2,5,10 times recorded LOD are assumptions, not validated analytical upper bounds. The 2010 catfish application repeats reporting-information arithmetic after converting source ppm to ppb; matched codes/names do not establish laboratory/residue-definition equivalence. No biological accuracy, dietary intake, risk trend, independent human adjudication or full-chain prediction is established.

## Portable verification: no source data or path configuration needed

Run from the repository root:

```sh
python3 scripts/verify_release.py
python3 extensions/reporting_information_20261008/verify_extension.py
```

The second command is a release-relative integrity/arithmetic utility, not a raw-data analysis. It checks every extension manifest hash and reconstructs 3425 mean/threshold rows and both years' saved interval histograms. Infinity is an unbounded endpoint; empty working-cell entries are not zeros. Thresholds 2,10,20 ppb are illustrative, not safety limits.

## Full source rerun

Original scripts are in `11_research_branches/animal_food_feed_transfer/05_code/`. They require the project layout, PyYAML, Poppler and the ignored local `00_admin/paths.yaml` configuration, plus the exact USDA originals and acquisition receipts documented in aggregate summaries. Run `05_code/utilities/check_paths.py` first. Do not alter raw files or silently replace an unavailable external data store. Reproduce S4 before S5; S5 compares its fresh 2009 recomputation with the S4 aggregate table. Copy the delivered aggregate folders to the explicit configured output root to run raw-data-free aggregate tests, without interpreting those tests as independent validation. Figure scripts additionally need numpy and matplotlib; they load configured aggregate paths. Portable verification above does not need these libraries.

No raw individual analytical records, third-party PDFs, manuscripts, authorship drafts, contact details or full acquisition ledger are redistributed. Original code: MIT; original documentation and eligible derived aggregates: CC BY 4.0, subject to DATA_RIGHTS.md and source-provider rights. Protocol dates and hashes describe a post-pilot exploratory extension, not a preregistered original study. AI-assisted development/review is not human certification. Cite the exact commit used.
