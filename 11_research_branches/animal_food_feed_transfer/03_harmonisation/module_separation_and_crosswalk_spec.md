# Module separation and crosswalk specification

Version: `AFFT_HARMONISATION_V1_20260922`

## Non-negotiable separation

Module A contains pesticide residues that may reach animal foods through feed, direct livestock treatment, premises treatment or environmental pathways. Module B contains pharmacologically active veterinary substances and their marker residues. The modules may reuse sampling, food-classification and consumption infrastructure, but they must never share residue definitions, HBGVs, transfer functions or a combined hazard index.

## Module A keys

The analytical key is:

`chemical_residue_definition × feed_commodity × processing_form × dry_matter_basis × origin × year × species × production_stage × tissue_or_food × analytical_result_definition`

Required crosswalks are:

1. FAOSTAT item to a precisely described feed material, retaining processing by-product and dry-matter basis.
2. Feed occurrence analyte to the JMPR/OECD livestock dietary-burden residue definition.
3. Country feed use to species- and production-stage ration fractions and dry-matter intake.
4. Feeding-study dose to the modelled dietary burden, without out-of-range or cross-species substitution.
5. Feeding-study tissue to monitoring FoodEx2 matrix, preserving muscle, fat, liver, kidney, milk and egg separately.
6. Monitoring residue definition to the toxicological residue definition used for dietary exposure.
7. Animal-food matrix to individual consumption amount and body weight for the same food form.

An observed animal-food pesticide result is not classified as feed-mediated unless the feed pathway is identifiable. Direct treatment, premises use and environmental deposition remain competing pathways.

## Module B keys

The analytical key is:

`drug × marker_residue × species × tissue_or_food × treatment_or_control_plan × sampling_strategy × result_definition × HBGV_version`

The module must preserve:

- authorised, unauthorised and prohibited substance status;
- marker residue and target tissue;
- sampling plan (objective, selective/risk-based, suspect, import);
- numerical concentration, binary result or decision-limit result type;
- CCα, CCβ, LOD, LOQ, unit and legal-limit evaluation;
- ADI or microbiological ADI provenance and version;
- food form and individual consumption amount.

`J002A` means at or below the applicable maximum permissible quantity; `J003A` means clearly above it; `J029A` means not evaluated. These regulatory evaluations are not concentration values. `NEG` is not replaced by zero.

## Censoring

Non-detects remain censored observations. No silent zero-fill is permitted. Lower-bound and upper-bound substitutions may be used only in a prespecified sensitivity analysis after compatibility gates pass. Binary negative results cannot be converted to concentrations.

## Current FoodEx2 screen

The pilot code decodes `sampMatCode.base.building` using the 2026 EFSA DCF catalogue and applies a transparent keyword screen for animal foods and feed. This is a feasibility classifier, not the final crosswalk. Final modelling requires expert-reviewed FoodEx2 code lists with explicit species and tissue fields.

## Output firewall

Every processed table must carry a `module` field. Pesticide and veterinary-drug rows may be displayed side by side as separate monitoring streams, but numeric exposures or regulatory ratios are never added across modules.

