# Scientific admission report

Decision date: 2026-09-22

**Historical-record note added 2026-09-28:** The original decisions and text below are retained for traceability. The validation-row rationale is superseded by `01_protocol/validation_design_addendum_20260923.md`: validation-data readiness is assessed before fitting, and prediction performance afterwards. The frozen Module B HBGV requirement is an operational rule, not a universal prerequisite for intake arithmetic; see manuscript Table 3 and its following paragraph. Later retrospective case mapping is in Supplement S2. None of these clarifications changes the original bounded STOP or descriptive-only decisions, or forbids a separately protocolled narrower study.

## Executive decision

`MODULE_A_FEED_TRANSFER = SCIENTIFIC_NO_GO_FOR_EXPOSURE_MODEL`

`MODULE_B_VETERINARY_DRUG = LIMITED_DESCRIPTIVE_MONITORING_ONLY`

`GLOBAL_ANIMAL_FOOD_EXPOSURE = NO_GO`

`DISEASE_BURDEN = PROHIBITED_BY_PROTOCOL`

The current evidence supports a reproducible feasibility and data-admission audit. It does not support a global feed-attributed pesticide exposure estimate, a representative veterinary-drug intake estimate or a combined pesticide-veterinary-drug risk metric.

## Gate matrix

| Layer | Module A | Module B | Decision basis |
|---|---|---|---|
| Feed use | Limited pass | Not applicable | FAOSTAT feed totals retain commodity, country, year and flag but not species allocation |
| Feed occurrence | Fail | Not applicable | No admitted complete feed sample-analyte occurrence dataset matched to the seven FAOSTAT commodities |
| Species-stage ration | Fail | Not applicable | No country-specific ration fractions and dry-matter intake |
| Chemical-specific transfer | Fail | Not applicable | OECD method obtained, but no selected chemical-specific feeding/metabolism study matched to dose, species and tissue |
| Animal-food occurrence | Partial | Partial | Complete SSD2 structures available for one country per module; selection and geographic coverage are limited |
| Residue definition | Fail | Fail | No end-to-end feed-monitoring-toxicology definition crosswalk for Module A; no drug-marker-HBGV crosswalk for Module B |
| Consumption and body weight | Fail | Fail | No country-year-tissue matched individual consumption dataset admitted |
| Held-out validation | Fail | Not applicable | No fitted transfer model exists to validate |
| Global inference | Fail | Fail | One-country pilots and non-probability sampling cannot identify global ordinary-market distributions |

## Bounded technical findings

The FAOSTAT pilot contains 16,606 rows for barley, maize, oats, rapeseed/mustardseed, soyabeans, sunflower seed and wheat across 178 countries from 2010 through 2023. These values quantify national feed allocation in thousands of tonnes. They do not identify the species consuming the feed or an individual-animal dietary burden.

The Luxembourg 2024 pesticide archive contains 710 unique samples and 346,652 sample-analyte rows. A current FoodEx2 keyword screen identified 56 animal-food candidate samples, 12,824 result rows and 22 quantitative rows. Forty-seven candidate samples were selective (`ST20A`) and nine were objective (`ST10A`); three result rows were coded above the applicable maximum permissible quantity (`J003A`). These counts describe the pilot archive, not prevalence, dietary exposure or feed attribution.

The Belgium 2024 VMPR archive contains 11,573 unique samples and 375,640 result rows. The keyword screen identified 8,270 animal-food candidate samples with 239,803 result rows. Of those samples, 8,087 were selective and 183 objective; 39 rows contained a numerical result value, 8,948 populated binary results were negative, seven rows were coded above the applicable maximum permissible quantity and 41,482 were not evaluated. These regulatory and analytical counts cannot be converted into intake without marker-residue, unit, censoring, HBGV and consumption compatibility.

## Why the prespecified cattle-milk or poultry-egg pilot did not proceed

The protocol requires overlap of feed residue, feed use, ration, transfer-study, animal-food monitoring and consumption evidence before choosing a pathway. Only feed use and limited animal-food monitoring were acquired. Choosing a chemical or species now would be result-driven and would invert the frozen order of operations. No cattle-milk or poultry-egg exposure calculation was therefore run.

## Permitted interpretation

The data demonstrate that technically rich official monitoring archives exist and that sample-analyte denominators can be reconstructed. They also show that risk-based sampling is common, which limits ordinary-market inference. The negative result is methodological: the evidence layers needed for causal feed attribution do not overlap yet.

## Reopening criteria

Module A may be reopened only when at least one chemical-feed-species-tissue pathway has:

1. complete feed sample-analyte denominators and censoring limits;
2. resolved feed form and dry-matter basis;
3. species-stage ration and dry-matter intake;
4. a compatible feeding/metabolism study spanning the dietary burden;
5. independent animal-food monitoring with compatible residue definition;
6. individual consumption and body weight; and
7. a prespecified held-out validation set.

Module B may progress to intake estimation only after an objective or design-weighted monitoring subset is linked to drug-specific marker residues, current HBGVs and compatible consumption data. MRL compliance alone is insufficient.

## Dated clarification: assessment coverage and computational counts (2026-09-30)

The historical labels and counts above are preserved, not newly adjudicated. `Fail` records unmet requirements in the acquired dossier; it must not be interpreted as proof that relevant evidence does not exist. Feed-use and animal-food files were acquired and assessed. Compatible feed-occurrence/ration and end-to-end residue linkages were not established; chemical-specific transfer, HBGV and individual-consumption files were not acquired for the original pilot after upstream failure. The statement that layers “do not overlap yet” therefore describes this dossier, not an exhaustive worldwide overlap analysis. Manuscript Table 1 now makes this assessment coverage explicit.

The original candidate `quantified_rows` count flagged `resType == VAL` or nonempty `resVal` other than `N_A`; it was not a validated numeric or censoring-consistency classification. The 22 and 39 candidate counts are retained as flagged result rows. Original archive row totals involved no row-level deduplication, and unique sample IDs are not proof of a complete duplicate-free tested sample-by-analyte denominator. These clarifications neither create new measurements nor support an exposure estimate. See manuscript Methods 2.2–2.8 and Supplement S1 for the exact operational definitions.

Revision tracking: ambiguity between unavailable-in-dossier and universally unavailable evidence is RESOLVED in the current manuscript; classification reliability and independent empirical positive-case validation remain acknowledged limitations requiring additional assessment or a new study. No frozen protocol, original challenge labels or raw observations have been changed.

The separate diagnostic re-read documented in `computational_audit_20260930.md` confirmed finite numeric values for the 22/39 flagged rows, comprising 21/35 VAL-coded and 1/4 LOQ-coded records. Candidate subsets had no repeated sample–analyte keys, exact-row duplicate excess or missing sample IDs under the new checks. The Luxembourg keyword screen includes code A03QY (cereals reconstituted with milk), six samples/3,912 rows and no numeric-bearing flagged rows. This is a documented false-positive selection, not evidence that 56 is a validated animal-food count; no corrected eligibility set has been silently substituted.
