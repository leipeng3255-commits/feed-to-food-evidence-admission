# Validation design addendum: readiness, prediction and decision reliability

Version: `AFFT_VALIDATION_ADDENDUM_V1_20260923`.
Status: implemented clarification of decision order; empirical validation remains unperformed.
This is a dated, post-pilot amendment. The frozen `AFFT_PROTOCOL_V0_1_20260922` and its historical NO-GO findings are unchanged. This document is not a preregistration and cannot make already inspected cases prospective.

## Defect repaired

The manuscript combined the availability of independent validation data with successful prediction validation under one gate. This allowed a circular reading: a model could not be fitted until it had already passed validation. The original protocol itself orders prediction before comparison; this addendum makes that order explicit in the executable decision.

The earlier statement that only a complete feed-to-human positive pathway could strengthen the paper was too restrictive. Three different claims require different validation designs. None substitutes for the others.

| Claim | Evidence that tests it | Evidence that does not establish it |
|---|---|---|
| The admission rule is implemented correctly | Documented examples and software tests, including changes to one essential input | Correct scientific judgments about real source compatibility |
| Independent analysts can apply the rule reliably | Blinded re-extraction and decisions on source dossiers, with disagreements and reasons retained | Repeated outputs from the same analyst or AI session |
| A specified transfer model predicts external animal-food residues | Locked predictions evaluated on independent, compatible observations with predeclared criteria | In-sample fit, regulatory MRL agreement, or consumption data alone |
| A bounded human exposure is identifiable | Validated transfer/occurrence chain plus suitable individual diet and body weight, sampling design and uncertainty | Validation of transfer alone or a regional food-supply average |

An externally validated transfer model can be studied before human diet data are available under a separately declared transfer-only estimand. Such work must be reported as a separate substudy; it does not reopen the frozen human-exposure pilot. A prospective full-chain case would test the broadest claim, but its absence does not prevent testing the narrower claims.

## Stage order implemented now

1. **Data readiness.** For the original full Module A estimand, retain every original evidence requirement. `validation_dataset` is a renamed, clarified gate: accessible, compatible independent data plus a documented unit-of-separation and an enforceable holdout plan. A held-out row from the same animal/farm used in calibration is not independent just because its row number differs. Before this passes, the custodian must confirm the validation data can actually be obtained and used; a promised future download does not pass.
2. **Model design and locked prediction.** All readiness gates must pass to enter full-chain model design. The analysis plan records the prediction target, chemical/residue expression, species/tissue, dose validity, censoring method, competing exposure routes, grouping for validation, loss function, baseline comparator and success criteria. Save criteria and predictions before validation outcomes are revealed. No result is yet eligible for exposure reporting.
3. **Prediction assessment.** Evaluate the frozen predictions, not a retuned model. A failed or incomplete assessment keeps the exposure result on hold. Report calibration/bias and prediction error with uncertainty, censoring-aware agreement and the predeclared comparator; a non-significant difference alone is not evidence of adequate prediction. No universal numerical accuracy threshold is imposed here: tolerances must be justified from analytical uncertainty and the decision the estimate will support, and fixed before outcomes are viewed. A case with criteria still unset cannot pass validation readiness.
4. **Exposure review.** Successful prediction assessment plus the complete diet/occurrence evidence chain permits review of bounded exposure estimates. It does not establish feed-origin identifiability, global representativeness, disease burden or submission approval. Those claims retain their separate restrictions.

Implementation: `05_code/evaluate_admission.py` now reports both `decision` (readiness) and `exposure_state`. An all-ready software fixture enters design while remaining `HOLD_VALIDATION_NOT_COMPLETED`. A failed prediction stays `HOLD_PREDICTION_VALIDATION_FAILED`. Documented successful validation is only `ELIGIBLE_FOR_BOUNDED_EXPOSURE_REVIEW`.

The existing Luxembourg pilot and retrospective JMPR challenge remain stopped. No new empirical positive case, model fit, validation result or exposure estimate has been created by this amendment.

## A feasible independent reassessment

The next practical task is source-based re-extraction, not construction of an entire new multinational study. A residue scientist and a second trained analyst can independently assess the same documentary cases. The assessor must not have authored the current gate labels. Provide the source documents and this rulebook without our filled gate matrix, manuscript conclusion, expected decision or test outputs. Publicly visible source conclusions cannot be made unseen; record prior familiarity and any unblinding. Call this *blinded to our adjudications*, not blind to all published outcomes.

For each case, record the source/page/table for every judgment, missing fields, residue-definition compatibility, sampling target, confounding routes, intended estimand and decision. Submit the signed/dated record before seeing our labels. Preserve the first decisions. Adjudicate disagreement afterwards; report both pre-adjudication and consensus results. When the source is ambiguous, the reference label is `UNKNOWN`, rather than forcing consensus.

The two current cases are training/development cases for the present AI-assisted implementation because their outcomes have already been seen. An assessor can independently reproduce them, but they cannot be called untouched prospective test cases. A later benchmark must choose new cases on metadata availability before examining the model's admission decision, and lock their identifiers and hashes. Stratify real dossiers from deliberately constructed deletion/compatibility challenges; never combine their performance denominators.

Report agreement at the dossier decision and gate levels, the reference-STOP cases incorrectly admitted, and the reference-ADMIT cases incorrectly stopped. Use the dossier as the independent unit; nine gates from one dossier are not nine independent validation subjects. Always show the number of eligible positive and negative cases, unknown-reference cases and source retrieval failures. If no real full-chain reference-ADMIT case exists in the test set, the false-stop rate for that estimand is **not estimable**. High agreement on all-negative cases does not close the positive-control gap. Sample size must follow the precision desired for these rates, not a convenient count of papers.

## Data compatibility, not identical ownership

The required layers need not originate from one study or one institution. Individual consumers need not be linked to the IDs of the cows producing their food. They must represent an explicitly compatible target population and food form, with justified geography/time alignment and sampling weights. Conversely, mixing unrelated feed trials, milk monitoring and consumption surveys does not create a valid pathway simply because the chemical names agree. Feed attribution requires an identifiable exposure route and control of direct treatment/environmental alternatives. Fix compatibility tolerances before outcome inspection; document every bridge.

## Minimum delivery from a data collaborator

- Source files and reuse terms, sample/animal/farm identifiers and dates, every tested sample-analyte result and its detection/quantification limit.
- Feed form, dry-matter basis, measured ration or intake, species and production stage; chemical and metabolite/residue definitions across layers.
- Feeding-study dose and time course, valid range, tissue basis and uncertainty; independent monitoring design and units reserved for validation.
- For the human-exposure stage, a compatible person-day food amount, body weight, survey design/weight and food-form mapping. These can come from a separate suitable survey.
- Data custodian declaration of what outcomes were withheld, from whom, and until which prediction lock; separate confirmation by the independent assessor.

No invitation, data request or message has been sent. The assessor receives only `independent_assessor_instructions.md`, `independent_assessment_form.csv`, and the original source documents/archive manifest. This addendum, the manuscript, test code and filled challenge JSON contain our judgments and must be held back until the assessor deposits the completed form. A coordinator must enforce and document that separation; these files alone do not establish that a blinded assessment occurred.

## Source basis and design ownership

[OECD Guidance Document 73](https://doi.org/10.1787/74878553-en) provides the technical context for livestock dietary burden, feeding dose selection and interpretation. [EFSA methodology guidance](https://www.efsa.europa.eu/en/topics/topic/methodology) stresses defining the assessment question and making evidence decisions traceable and repeatable. The staged implementation and proposed assessor study above are our design choices; these sources are not claimed to mandate our exact gate set or validate the present framework.
