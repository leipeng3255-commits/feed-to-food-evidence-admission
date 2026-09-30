# Post-pilot computational audit — 30 September 2026

This is a diagnostic re-read of the two original raw CSV archives and the configured 2026 DCF catalogue. It does not replace the frozen protocol, classifications, summaries or admission judgments. Raw files were opened read-only; all project path checks passed.

| Check | Luxembourg pesticide candidates | Belgium veterinary-drug candidates |
|---|---:|---:|
| All archive result rows | 346,652 | 375,640 |
| Keyword candidate result rows | 12,824 | 239,803 |
| Candidate unique samples | 56 | 8,270 |
| Frozen legacy quantitative-flag rows | 22 | 39 |
| Finite numeric-bearing result rows | 22 | 39 |
| Numeric-bearing rows coded VAL | 21 | 35 |
| Numeric-bearing rows coded LOQ | 1 | 4 |
| Flagged rows lacking numeric value/unit | 0 / 0 | 0 / 0 |
| Exact full-row duplicate excess | 0 | 0 |
| Repeated sample–analyte groups | 0 | 0 |
| Missing candidate sample identifiers | 0 | 0 |

The legacy flag counts every VAL row or populated non-N_A resVal. Consequently 22 and 39 are **numeric-bearing rows under that flag**, not counts of independently demonstrated quantified detections: one and four respectively remain LOQ-coded. Units are consistently G061A and G050A within the flagged subsets, but this code-level check does not establish compatible chemical/residue definitions or validate a concentration conversion. No censored value was recoded as zero or as a quantified measurement.

The keyword screen contains an explicit false-positive warning: 3,912 Luxembourg rows are labelled “Simple cereals which have to be reconstituted with milk or other appropriate nutritious liquids” (A03QY; six samples, all rows LOQ-coded, all ST10A, zero numeric-bearing results). Matching the word milk is not evidence that the observed commodity is an animal-derived food. Frozen candidate totals remain as historical screen results, not corrected animal-food counts. The full candidate/noncandidate matrix frequency tables in the diagnostic JSON allow an expert code-list review without quietly changing eligibility. No validated replacement classifier is claimed.

Duplicate checks apply to candidate rows only. The sample–analyte key uses sampId_A and paramCode.base.param. Absence of repeated keys does not establish independent sampling, independent farms or representativeness; exact-row hashes test duplicate records, not biological independence.

Execution: `python3 05_code/audit_pilot_semantics.py` from this branch's script layout. Output is the configured animal_food_outputs_root / `pilot_semantics_audit_20260930.json`. Only aggregates are exported; no individual identifiers or raw values are written. Script output creation is exclusive, protecting the dated report from accidental overwrite.

Code safeguards added: configured 2026 catalogue must exist (no hidden legacy fallback); gate warnings no longer imply that reported non-blinded review has not happened; release snapshots use a fixed scientific-file allowlist, exclude nested archives and author-administrative materials, and redact machine locations without falsifying event timestamps. These safeguards do not constitute blinded scientific adjudication or empirical prediction validation.

Verification on this date: Python 3.14.4, PyYAML 6.0.3; 12 unit tests passed (eight admission-logic tests and four release/semantics safeguards). The branch verifier passed 32 checks, including the frozen protocol/case/blank-form hashes and all 16 pilot raw-artifact hashes. The legacy whole-branch audit and harmonisation scripts were not rerun, so frozen summaries were not overwritten. The optional legacy-catalogue metadata path now requires explicit configuration and a fresh file hash; absent configuration reports NOT_ASSESSED.
