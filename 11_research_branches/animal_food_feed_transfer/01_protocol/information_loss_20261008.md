# Same-source information removal: locked execution specification

Date: 2026-10-08. This is a post-pilot, exploratory extension, not preregistration. The source, commodity counts and ND/NP/O counts were inspected in the preceding inventory. Concentration-specific results of the transformations have not yet been computed. An AI-assisted design review informed this specification; no independent human review is claimed.

## Target and universe

Use the acquired USDA PDP 2009 archive, all BA (beef adipose), BM (beef muscle) and FC (catfish) records and every analyte code present. Never select chemicals based on detection or effect size. Unit: commodity–analyte cell; the finite-record descriptive mean is assessed within cells, never averaged across chemicals as an exposure metric. BA/BM samples may be paired animal tissues; no independent-animal inference is made. No population weighting, dietary intake, regulatory compliance, disease burden or feed attribution is estimated.

## Semantics and fixed transformations

Decode the archive's own dictionary and reference tables. B=ppb. O is a reported detection (original extraction value); ND is validated well-recovered non-detection; NP is marginal-performing non-detection. A finite nonnegative O value is treated as a point for this reporting-information experiment, not as error-free biological truth. A finite positive ND LOD defines a conditional interval [0,LOD]. Invalid rows are excluded from the ND/O working subset, counted and kept in the all-record uncertainty assessment. NP never receives an LOD upper bound. Removal of NP changes the target subset and is not evidence that all records are quantitatively admissible.

R0 retains reported O values and individual ND limits. R1 removes sample IDs and replaces O values by fixed closed bin envelopes [0,1], [1,10], [10,100], [100,1000], [1000,infinity] ppb, using left-closed/right-open bin membership. ND count-by-LOD is retained without sample IDs. This isolates concentration rounding, without also discarding censoring information. R2 retains only counts of ND/O (and a separately reported NP count); all magnitudes and detection limits are withheld, yielding [0,infinity] for each nonnegative concentration. Open-endpoint distinctions are conservatively enclosed, so no claim of universally sharp bounds is made.

Negative control: lossless, unlinked exact-value/LOD histograms must reproduce R0 marginal bounds exactly; identifiers are unnecessary for this marginal target, although their removal prevents reconstruction of within-sample joint occurrence. Sensitivity: nested coarser bins [0,10], [10,1000], [1000,infinity] must weakly widen R1 bounds. NP sensitivity: retain the original full denominator and assign NP/invalid rows [0,infinity], explicitly reporting the consequent infinite upper bound where applicable.

## Outcomes and assertions

For each nonempty ND/O cell calculate lower/upper finite-record mean bounds, their width, and lower/upper fractions above illustrative thresholds 2,10,20 ppb. These thresholds are not MRLs or health-based values. Bounds are arithmetic endpoints, not confidence or prediction intervals. Exceedance lower count uses lower>threshold; upper count uses upper>threshold. No imputation, p-values, bootstrap or independence-based standard error is used.

Require fixed denominators across R0/R1/R2, R0 contained in R1 contained in R2, coarse-bin containment, exact-histogram equality, sample–analyte uniqueness, correct joins, positive finite LODs, expected flag interpretation, count conservation, and raw file SHA-256 agreement before/after. Report every cell, including all-nondetect and unchanged cells. Infinite upper bounds remain infinite and are never capped at an observed maximum. Summaries across cells describe the audit universe, not independent replications or equally important hazards.

## Contextual source cases

Audit the acquired Australian NRS hen-egg 2023–24 report for analyte-specific tested counts and reporting-limit bands; audit Finland's 2012 feed report pages44–46 and existing literal transcription for qualitative ND and absent verified numerical limits. These are format contrasts, not matched replications, national comparisons or a combined exposure chain. Include only data actually verified in the sources, preserving compound-group labels and distinguishing PCB entries from pesticide labels.

## Deliverables and stopping condition

Reproducible code, all-cell aggregate tables, source hashes, automated checks, one quantitative multi-panel editable SVG/PDF figure, an S4 supplement, concise Methods/Results/Discussion updates, and a new dated Word submission-format package. Retain historical releases and red hypothetical CRediT; do not claim that approval of the earlier manuscript proves approval of substantive new results. This extension finishes when calculations, bounds, sources, figures and package checks pass. Independent human adjudication and full-chain external validation remain separate uncompleted scientific tasks.
