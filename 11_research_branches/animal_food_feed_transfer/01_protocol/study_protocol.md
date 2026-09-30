# Frozen Stage 1 protocol: animal-food feed transfer

Version: `AFFT_PROTOCOL_V0_1_20260922`

## Research question

For animal-source foods with compatible feed occurrence, feed-use, livestock transfer, animal-food monitoring and consumption evidence, how much pesticide dietary exposure can be traced to feed pathways, and where do observed tissue residues disagree with transfer-model predictions?

A separate secondary question describes veterinary-drug residue exposure using treatment-specific marker residues and health-based guidance values. It does not attribute veterinary drugs to feed pesticide transfer.

## Scope

Primary animal foods are milk, eggs, muscle, fat, liver, kidney and farmed fish. Species and tissues remain explicit. Honey and wild game are secondary because their exposure pathways and sampling frames differ.

## Module A estimand: pesticide feed transfer

1. Estimate livestock dietary burden from admitted feed-commodity residues, country feed allocation and species-specific ration fractions.
2. Apply only chemical-, species- and tissue-specific transfer functions supported by livestock metabolism/feeding studies within their valid dose range.
3. Compare predicted tissue/milk/egg residues with independent monitoring observations.
4. Combine validated animal-food occurrence with individual consumption and body weight to estimate chemical-specific dietary intake.

No generic bioconcentration factor is transferable across chemicals, species or tissues. Lipophilicity is a prior/context variable, not a substitute for a feeding study.

## Module B estimand: veterinary drugs

Estimate marker-residue intake separately by drug, species, tissue and food form using complete monitoring denominators and applicable ADI or microbiological ADI. Withdrawal periods, MRLs and non-compliance are regulatory context, not measured occurrence values.

## Hypotheses

1. Feed-trade origin and feed-use allocation explain part of the between-country variation in selected pesticide residues in animal foods.
2. Species/tissue-specific transfer models outperform models based only on logKow or feed concentration.
3. Observed monitoring discrepancies identify missing direct-treatment, environmental or husbandry pathways rather than being silently absorbed into a transfer coefficient.

## Mandatory admission gates

1. Feed residue data contain a complete tested denominator and censoring limits.
2. Feed commodity, processing by-product and dry-matter basis are resolved.
3. Feed use is distinguished from food, seed, processing, loss and export.
4. Species- and production-stage ration evidence is available; national feed totals alone do not define individual-animal dose.
5. Feeding/metabolism studies match chemical residue definition, species and tissue and cover the modelled dietary burden.
6. Animal-food monitoring preserves species, tissue, domestic/import status, sampling programme, result and analytical scope.
7. Consumption data preserve tissue/food identity and body weight.
8. Pesticide and veterinary-drug modules use separate HBGVs and are not summed across unrelated mechanisms.
9. Model predictions are tested against held-out animal-food monitoring data.

## Falsification tests

- Failure of predicted tissue residues to reproduce held-out monitoring within prespecified uncertainty rejects the corresponding transfer model.
- If feed-origin attribution is not identifiable because of compound feed mixing or re-export, results remain scenario bounds.
- A veterinary-drug signal must not be described as feed-mediated without pathway evidence.
- Positive-only or violation-only surveillance cannot estimate ordinary market occurrence.

## Stop rules

- No global animal-food exposure claim until feed, transfer and tissue-monitoring coverage all pass.
- No extrapolation from MRLs or withdrawal periods to concentrations.
- No universal lipid-normalisation across chemicals.
- No pooling of milk, eggs, muscle, fat or offal.
- No disease burden calculation under this protocol.
