# NP assumed upper bounds, temporal application and reporting sufficiency

Locked before the new concentration calculations on 8 October 2026. Post-pilot exploratory extension; not preregistered, blinded or independently human-adjudicated. Previously inspected: 2009 results and 2010 schema, dictionary and sample-code counts (384 FC; no BA/BM). Other project activities may have accessed these archives; a never-seen holdout is not claimed.

## 1. NP sensitivity: same complete denominator

Use every commodity–analyte cell in the original2009 BA/BM/FC source and the2010 FC source. Keep eligible detection and ND intervals fixed. ND requires a positive finite LOD and no numerical detection value. O, A and R are the dictionary-defined detection states, represented as their reported nonnegative finite values; any absent or invalid magnitude is unknown [0,infinity]. The2009 selected source contains only O/ND/NP. Preserve every unknown/invalid row in the full denominator.

For NP, compare [0,k*recorded LOD] with k=1,2,5,10 and [0,infinity]. Finite NP scenarios require a positive finite recorded LOD; invalid/missing limits remain infinite at every k. These are assumed numerical upper bounds, not evidence that marginal-method results are quantitatively valid, that the cap contains true concentrations, or that any k is biologically plausible. k=1 does not relabel NP as validated ND. No scenario is designated the preferred estimate. All full-cell rows and denominators remain identical across scenarios; lower means are fixed and upper means/strict-threshold fractions must be monotone. NP-free cells must remain exactly invariant.

## 2. Temporal application of the frozen reporting transformations

Read each archive's dictionary and tables; retain original result code and concentration basis. Convert M(ppm),B(ppb),T(ppt) to ppb only using the documented unit codes. Require unique sample keys, consistent sample-result joins and sample–analyte uniqueness. Unexpected states or duplicates trigger explicit failure rather than silent resolution. Report actual row exclusions and status counts.

Apply the existing R0/R1/R2 and nested coarse grid, with unchanged thresholds2/10/20ppb, to all2010 FC ND/detection working cells. Do not fit or tune anything on2010 outcomes. Compare descriptive cell counts, finite bounds, widened/unchanged intervals and threshold uncertainty with2009 FC. Also export shared analyte-code+normalised-name rows, retaining unmatched/renamed cells. Normalisation removes whitespace/case differences only. Code/name agreement is a label link, not proof of analytical residue-definition or method equivalence. No annual risk trend, population inference, paired-animal model or biological validation is estimated.

## 3. Reporting sufficiency for declared marginal outputs

Export a machine-readable reporting template with schema/source version, year, matrix, analyte identity/definition locator, unit, target frame, total/eligible/NP/invalid counts, scenario, interval sums and threshold endpoint counts. Check that sums/counts reconstruct every full-cell mean interval and threshold-fraction interval exactly. This numerical sufficiency does not guarantee that the source covers a scientifically appropriate sampling frame.

For a fixed interval mean, n and sum(lower)/sum(upper) are sufficient statistics once intervals and scope are justified. For fixed strict-threshold fractions, n and counts(lower>t)/counts(upper>t) suffice. For arbitrary later thresholds, retain endpoint distributions or suitable threshold-resolved counts; one summed LOD cannot answer all exceedance questions. For joint occurrence retain sample identifiers and within-sample analyte pairing; marginal statistics alone cannot recover it. This is a target-specific candidate reporting set, not a universal metadata minimum or a proposed regulatory standard.

## 4. Deliverables

All-cell NP sensitivity,2010 retained histograms and working-cell results, all shared/unmatched labels, threshold-sufficient aggregate statistics, a filled reporting template, assertions and tests, an editable four-panel Figure7, S5, concise manuscript updates, and a new submission-format package. Existing input/results/releases remain traceable. Unknown author contributions and declarations are not inferred from computing success. Completion of this extension does not close human reference adjudication or same-pathway external prediction.
