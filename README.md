# Feed-to-food evidence admission

Code, frozen protocols, aggregate audit outputs and source manifests for a **bounded evidence-admission audit** of feed-to-animal-food pesticide assessment. Veterinary-drug monitoring is a separate descriptive comparison. This is not a validated exposure model, a consumer-risk estimate, or a claim that the wider field is infeasible.

## What is and is not validated

The documented empirical dossiers remain stopped for the full-chain estimand. Synthetic full-pass cases test software logic only. The post-pilot claim map is a methodological proposal applied retrospectively to two development dossiers, not eight independent validation subjects. Non-blinded review does not establish blinded adjudication reliability or prediction accuracy. Numeric-bearing rows include some LOQ-coded observations and are not all quantified concentrations. Keyword-selected foods include ambiguous mixed foods and are candidates, not expert-validated animal-food classifications.

## Quick start: no source downloads required

The [3 October claim-specific extension](extensions/claim_contracts_20261003/README.md) adds four executable claim contracts, synthetic repair-set tests and the aggregate data/editable SVG for classification disagreement. It does not revise the frozen pilot or establish independent scientific validation. Follow its separate commands to test and render the extension; the historical release QA below concerns the earlier release.

Python 3.11 or newer is recommended; the release test environment is recorded in `RELEASE_QA.json`, not asserted to be the historical analysis environment.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-core.txt
.venv/bin/python -m unittest discover -s 11_research_branches/animal_food_feed_transfer/05_code -p 'test_*.py' -v
.venv/bin/python 11_research_branches/animal_food_feed_transfer/05_code/evaluate_admission.py
.venv/bin/python scripts/verify_release.py
```

These commands verify the published files and the decision logic; they do not empirically validate the framework. Aggregate results are in `derived/`; source links and checksums are included, but no raw records or third-party PDFs are redistributed.

## Reproduce the raw-source audit separately

An explicit, existing data directory outside this checkout is required. No download falls back to the system disk. Configure it using an absolute path chosen by you:

```sh
.venv/bin/python scripts/configure_paths.py --data-root /absolute/path/to/your/data
.venv/bin/python 05_code/utilities/check_paths.py
```

`00_admin/paths.yaml` is generated locally and ignored by Git. Raw files use `02_raw_data/branches/animal_food_feed_transfer`; new intermediate/processed/output files use a separate `public_reproduction` subtree. Existing source files are reused only under the acquisition/checksum rules. For a frozen-source reproduction, obtain the exact versions in `derived/raw_source_manifest.csv` and run:

```sh
.venv/bin/python 11_research_branches/animal_food_feed_transfer/05_code/audit_acquired_sources.py
.venv/bin/python 11_research_branches/animal_food_feed_transfer/05_code/harmonise_pilot.py
.venv/bin/python 11_research_branches/animal_food_feed_transfer/05_code/audit_pilot_semantics.py
```

Compare numeric/category summaries with `derived/`, allowing local path fields or generation timestamps to differ. The diagnostic audit uses exclusive creation: it refuses to overwrite an existing report. For another run, explicitly choose a new output directory in the ignored local configuration; do not delete frozen reports. Internal `verify_branch.py` checks private project/manuscript materials and is intentionally not distributed; public file integrity is checked by `scripts/verify_release.py`. Live source downloads may change and cannot be described as reproducing a historical snapshot without matching its hashes. Optional acquisition (network and source terms apply):

```sh
.venv/bin/python 11_research_branches/animal_food_feed_transfer/05_code/acquire_official_sources.py
.venv/bin/python 11_research_branches/animal_food_feed_transfer/05_code/acquire_validation_source.py --source jmpr
```

Source inspection, sample counts and concentration validity are distinct checks. Result rows are not independent subjects; no LOD/2 or zero substitution, dose-response modelling, exposure estimation or burden estimation is performed. Historical frozen labels are retained; dated clarifications distinguish data not acquired after an upstream stop from assessed incompatibility.

## Literature and figures

The curated nearest-neighbour map, PubMed query script/log/23-record metadata export, and expanded-query script/log/165-candidate metadata export are included. The expanded log records a pre-threshold count of 718; the full pre-threshold records and ranking abstracts were not saved. Exact historical score recomputation is therefore unavailable. The open-index search requests only the first 100 records per query/database without pagination; it is not a systematic review or an exhaustive novelty search. No new search has been substituted for missing historical records. Live search scripts write to their original output filenames: run them only in a separate disposable checkout and preserve the dated release snapshot. Figure generation additionally requires `requirements-figures.txt`.

`08_review/primary_source_reconciliation_20260923.md` and its linked completion assessment are dated scientific history supporting the companion CSV's source locators. Their historical workflow/test counts are not current release status; consult `RELEASE_QA.json` and the dated clarifications. They do not constitute human-review certification.

## Release scope and provenance

The nested branch layout is intentional: it preserves source-relative imports and path configuration without requiring the private parent project. `RELEASE_MANIFEST.json` records every published research file's SHA-256. Public JSON copies replace private local path strings with logical tokens; original evidence timestamps are preserved. Those redactions do not imply that the files are byte-identical to private originals. `derived/PUBLIC_PROVENANCE.json` records original and public hashes for these copies.

No manuscript, author contact list, internal correspondence, unconfirmed author-contribution draft, historical submission ZIP, raw monitoring data or third-party full text is included. Manuscript authorship approval and journal submission are separate from this code release. AI assisted development and auditing; executable code and disclosed limitations, not AI authority, define the reproducible record.

## Licenses and citation

Original code: MIT (`LICENSE`). Original protocol/method documentation: CC BY 4.0 (`LICENSE-DOCUMENTATION.md`). Aggregate data and third-party rights: see `DATA_RIGHTS.md`; no blanket relicensing of source material. Cite the repository URL and exact commit used. There is no repository DOI or accepted-paper citation at this release.

## 8 October reporting-information extension

See [fixed rules, NP sensitivity, temporal repetition and target-specific reporting statistics](extensions/reporting_information_20261008/README.md). These are conditional arithmetic results, not exposure or full-chain validation.

## 9 October reproducibility and reporting revision

See [synthetic counterexamples, explicit frozen-source rerun and Figure1-4 reproduction](extensions/reporting_revision_20261009/README.md). Source reproduction is restricted to the USDA core and does not silently claim that contextual transcriptions were rerun.
