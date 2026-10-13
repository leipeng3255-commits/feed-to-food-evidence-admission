# Dairy/egg reporting extension (13 October 2026)

This post-pilot extension supplies aggregate reporting diagnostics and original code. It is not population exposure estimation, feed attribution or independent predictive validation. Original admission decisions remain unchanged. The public bundle contains no raw analytical rows, manuscript, author contact list, private download ledger or third-party full-text articles.

## Aggregate-only reproduction (standard library; no raw files required)

From any working directory, substitute your checkout path:

```sh
python3 -I -S /path/to/checkout/extensions/dairy_egg_reporting_20261013/verify_dairy_egg_bundle.py --bundle /path/to/checkout/extensions/dairy_egg_reporting_20261013
python3 -I -S -O /path/to/checkout/extensions/dairy_egg_reporting_20261013/verify_dairy_egg_bundle.py --bundle /path/to/checkout/extensions/dairy_egg_reporting_20261013
python3 -I -S /path/to/checkout/extensions/dairy_egg_reporting_20261013/test_dairy_egg_verifier.py
```

The tests default to this directory for assets. Verification checks declared aggregate arithmetic and file integrity, not scientific validity or independently regenerated raw-source results. Original code remains auditable under source_project. Figure 8 is a text-editable, aggregate-derived SVG; layout QA is computational, not a substitute for human visual review.

## Raw-source analysis is a separate configured workflow

It has NOT been demonstrated here as a standalone raw-data reproduction from this public bundle. The raw archives and private download ledger are intentionally excluded. Do not treat the aggregate checker as that demonstration.

Use source_project as a separate project root. Install PyYAML for analysis and matplotlib for plotting. Create its 00_admin/paths.yaml with absolute paths project_root (the source_project directory), data_root, raw_data_root and animal_food_outputs_root referring to your own lawful external data location. Add any additional paths requested by the included check_paths.py. Run that checker before analysis. Do not use another user's paths or alter source archives.

Acquire official USDA PDP annual source archives using URLs and hashes in source_receipts.json, preserving each relative_raw_path. Source years 2011–2024 are audited, including absent milk/egg years; the analysis checks all listed archives, not only years with selected commodities. Create YOUR OWN 00_admin/download_manifest.csv with columns local_file_path, sha256, official_url, with absolute local_file_path referring to those verified copies. It must match actual archive hashes; the public receipt file is not silently substituted for this ledger. Then run source_project/11_research_branches/animal_food_feed_transfer/05_code/dairy_egg_reporting_20261013.py --output-name dairy_egg_reporting_rechecked_20261013. Run plot_dairy_egg_20261013.py only after the aggregates exist at the configured output location. Verify source paths against the protocol and script before executing. This workflow needs no private author data.

The source_project layout is deliberate: the original scripts resolve a project-relative configuration and their sibling helper modules. information_loss_20261008.py imports reporting_reproduction.py; both are included. Do not run the analysis scripts as isolated copies from this bundle root. No source-script changes, synthetic data substitution or inferred missing records are used in this release.
