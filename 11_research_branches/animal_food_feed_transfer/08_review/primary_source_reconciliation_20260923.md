# Primary-source reconciliation of the transfer challenge

Date: 2026-09-23. Current decision: `TRANSFER_EVIDENCE_PRESENT; QUANTITATIVE_TRANSFER_PARTIAL; FULL_CHAIN_STOP`.

This record supersedes the earlier transfer `Pass` in the component challenge. The prior assessment established that a feeding study existed, but promoted that fact too far: a quantitatively usable transfer function additionally requires reconciled dose, outcome and study identity. The correction follows primary-source inspection, not a change to the desired result.

## Source findings

The [JMPR summary](https://www.fao.org/4/a0209e/a0209e0d.htm) gives a middle dose of 100 ppm. The [full evaluation](https://www.fao.org/fileadmin/templates/agphome/documents/Pests_Pesticides/JMPR/Evaluation05/2005_Glyphosate1.pdf), printed pp. 466–467, describes 40/120/400 ppm and identifies Manning and Wilson 1987, MSL6729. Table 124 notes 160 ppm in week two for the middle group. Its high-dose day-7 kidney cells are 0.05/0.07 mg/kg (glyphosate/AMPA), whereas adjacent prose gives 0.13/0.08. The primary PDF page was visually checked. These inconsistencies remain unresolved; neither version is silently selected. The summary and evaluation are representations of one study, not independent validation cohorts.

The study's existence remains confirmed. Dose-response calibration and clearance estimation are on hold pending the original report or an authoritative reconciliation. The original bounded pilot and full-chain stop decision remain unchanged.

## Other candidates checked

[von Soosten et al. (2016)](https://doi.org/10.3168/jds.2015-10585) reports feed intake and milk assays, with milk results below quantification. It cannot validate this kidney endpoint. Even a milk-specific analysis would need explicit censoring, valid dose-range comparison and verified study independence; two series of non-detects do not demonstrate accurate prediction of a transfer slope.

The [Li, Xiong and Fantke (2022) publisher record](https://doi.org/10.1039/D1EM00454A) lists XLSX/PDF supplements. Publisher full-text access returned HTTP 403. A subsequent retrieval obtained the publisher PDF from DTU's public institutional document endpoint; see `validation_completion_assessment_20260923.md`. Supplement access and study-level calibration/validation separation remain unresolved. The earlier full-text access status is superseded; no scientific exclusion follows from an access failure.

Exact candidate statuses are recorded in `02_literature/transfer_validation_source_audit_20260923.csv`. This was a targeted source investigation, not an exhaustive search. All viewed records are now retrospective/development evidence for this analyst.

## Reproducibility and concrete next evidence

The full 198-page JMPR PDF was archived on the configured external drive without changing the existing 16 pilot artifacts. Its SHA-256 is `df185cd2c8d53f0516bf5acaac2089b9fe0ef76aae169f056f67b3268e535fd1`; the separate `validation_source_manifest_20260923.json` records URL, acquisition time, bytes and path. The branch verifier checks that file in addition to the frozen pilot manifest.

To reopen quantitative use, obtain the original MSL6729 report or an authoritative correction specifying: (1) nominal and achieved dose by animal/week, on a common dry-matter and active-substance basis; (2) correct day-7 kidney values and sample identifiers; (3) explanation of the summary's middle dose; (4) individual outcome and analytical-limit records. Then select a genuinely distinct study with a compatible endpoint and valid dose range for external testing. Public availability of another document describing MSL6729 does not satisfy that requirement.

No exposure calculation or transfer regression was run, and no independent human assessment has been claimed.
