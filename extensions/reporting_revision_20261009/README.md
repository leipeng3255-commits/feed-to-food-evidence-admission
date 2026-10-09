# Reporting revision: 9 October 2026

Two elementary, synthetic summary-collision examples explain why mean-preserving summaries need not preserve threshold or joint computations. These are neither new empirical cases nor a new identification theorem. The original 2009/2010 calculations are unchanged. Figure1-4 rendering code, original aggregate data, SVG and dated layout checks are also included in the branch layout. Original code: MIT; original documentation/eligible aggregates: CC BY 4.0 subject to DATA_RIGHTS.md. No raw records, third-party PDFs, manuscript or author files are redistributed.

## No-source integrity and arithmetic checks

```sh
python3 scripts/verify_release.py
python3 extensions/reporting_information_20261008/verify_extension.py
python3 extensions/reporting_revision_20261009/verify_extension.py
```

The first release remains archived at its exact commit. Root manifests verify current code; historical extension manifests retain their original artifact checks.

## Explicit frozen-PDP core source rerun

Install requirements-core.txt (PyYAML), plus Poppler pdftotext. Choose an existing writable absolute external data root. Do not use the checkout or silently redirect an unavailable data store. Run scripts/configure_paths.py --data-root /absolute/path/to/data and 05_code/utilities/check_paths.py. Place the official hash-matching 2009PDPDatabase.zip and 2010PDPDatabase.zip at raw_data_root/usda_pdp; links and study-source hashes are in 01_protocol/pdp_source_receipts_20261009.json under the branch. These hashes identify the archived study versions; they are not represented as provider-published SHA256 checksums. A different version must fail, not be silently substituted.

```sh
python3 11_research_branches/animal_food_feed_transfer/05_code/information_loss_20261008.py --public-reproduction
python3 11_research_branches/animal_food_feed_transfer/05_code/np_temporal_20261008.py --public-reproduction
```

This explicitly selected mode does not read the private acquisition ledger or Finnish transcription. It writes fresh stage directories under animal_food_outputs_root/public_reporting_reproduction_20261009 and refuses overwrite. The separate Finland/Australia context checks are marked NOT_RUN_PDP_ONLY; their original results remain historical, not silently rerun. Eleven core artifacts matched original output bytes in the recorded check. No source files are changed. This is core computational reproducibility, not human adjudication or biological/predictive validation.

## Render Figures1-4 from original aggregates

Install requirements-figures.txt (numpy, matplotlib); DejaVu Sans preserves the original appearance. In a separate disposable checkout, run:

```sh
python3 11_research_branches/animal_food_feed_transfer/05_code/publication_figures.py
python3 11_research_branches/animal_food_feed_transfer/05_code/test_multipanel_figures.py
```

Rendering creates PDF/PNG counterparts and updates SVG/layout files from supplied data; it changes public file hashes, so verify the unmodified release first. Figures2-3 show bounded screening/reporting diagnostics. Figure4 transcribes a disputed study record; rendering cannot resolve that scientific conflict. The included 30 September reference-audit JSON is a dated artifact needed by its historical figure tests, not a newly performed citation review or current manuscript count. Synthetic regression tests use the explicit local path configuration; they do not increase empirical sample size.
