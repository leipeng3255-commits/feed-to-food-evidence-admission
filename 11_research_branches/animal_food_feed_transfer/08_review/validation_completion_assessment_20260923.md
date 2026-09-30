# Validation completion assessment and targeted revision

Date: 2026-09-23. Target: Food Control position-paper draft.
Mode: targeted author-requested revision, not an independent peer-review decision.
Overall: `TECHNICAL_CHECKS_PASS; EMPIRICAL_VALIDATION_NOT_COMPLETED; NOT_SUBMITTED`.

## What changed

The previous publisher access problem was partly resolved through the author's institutional repository. The Li, Xiong and Fantke (2022) publisher PDF was acquired from [DTU](https://backend.orbit.dtu.dk/ws/portalfiles/portal/276005666/d1em00454a.pdf); Section 3.3 reports literature comparisons with performance calculated for lipophilicity-bin means. This is useful screening evidence, not a new independent dataset validating our admission rule. Supplementary XLSX/PDF files remain unacquired. Original study identifiers and calibration/evaluation reuse still require audit before a benchmark can be admitted.

Archive: `validation_sources/Li_Xiong_Fantke_2022.pdf` under the configured animal-food raw root. SHA-256: `7ed6578ced6ed9e65416dbb173a04408ad64cf72388cccc1c0002405589737fa`. Acquisition URL, timestamp and bytes are preserved in `li2022_source_manifest_20260923.json` under the configured branch output root. The frozen 16-file pilot manifest is unchanged. The publisher and frontend institutional URLs returned HTTP 403; the publicly indexed institutional document endpoint succeeded. No credential or paywall bypass was used.

## Claim-specific completion contract

| Claim | Current evidence | Evidence required to close | Current status |
|---|---|---|---|
| Files and software behave as documented | Hash checks, preserved denominators, admission-logic tests | Reproducible technical checks only | Verified within the checks' scope |
| Source judgments are reproducible between analysts | AI-assisted extraction; prepared blank assessment forms | A qualified analyst's dated independent extraction before seeing our labels, prior-familiarity disclosure, preserved disagreements | Not performed |
| Rule distinguishes answerable from unanswerable dossiers | Both empirical development cases stop | New real reference-ADMIT and reference-STOP dossiers; independent reference adjudication; locked selection and comparator | Not established; false-stop rate not estimable |
| Tissue predictions generalise | No admitted empirical prediction run | Reconciled source values, genuinely separate compatible validation observations, locked model and tolerances, censoring-aware assessment | Not performed |
| Feed-attributed human intake is supported | Complete compatible pathway unavailable | Transfer evidence plus population occurrence, diet/body weight and justified attribution; a specified independent reference for any claim of intake validation | Not established |

Neither a successful archive check nor expert consensus establishes predictive accuracy. A diet survey supplies an exposure-model input, not an independent measurement of actual pesticide intake. The end-to-end validation reference must therefore be explicitly named rather than implied by the presence of consumption data.

## Socratic stress test

1. **Would stopping every case look successful?** Yes, on the present negative-only development set. We cannot claim discrimination, practical superiority or a low false-stop rate. Section 4.3 now says this explicitly.
2. **Are full-chain requirements appropriate for every scientific question?** No. Transfer-only or screening questions can be studied under a separate, narrower protocol. This does not change the frozen pilot's estimand or result.
3. **Can published model agreement close our gap?** Not without matching the evaluation unit, checking original-study reuse and specifying what is being validated. Grouped performance cannot stand in for individual dossier or tissue prediction accuracy.
4. **Can we call a new extraction blind after reading the outcomes?** No. Our current work is retrospective. Another analyst may be blinded to our labels, but their prior exposure to sources must be recorded. AI agents are not independent human investigators.
5. **What would actually permit completion?** For documentary reproducibility: recruit the independent assessor and collect deposited judgments. For predictive validation: obtain accessible study-level data, resolve dose/residue conflicts, document independence, then lock and test a compatible pathway. Current public records do not satisfy those conditions.

## Revision tracking

No external journal referee comments are implied. These are internal author-requested quality issues.

| Issue | Type | Change/location | Status |
|---|---|---|---|
| Feed-form gate omitted from the displayed summary table | Reporting | Added explicit feed-form row in Table 1, consistent with existing protocol/code | RESOLVED |
| Validation types could be conflated | Major | Section 4.2 now separates technical, adjudication, prediction and intake-reference claims | RESOLVED for reporting only |
| A universal STOP rule could be mistaken for a validated decision aid | Major | Section 4.3 adds the strongest counterargument and need for positive dossiers/comparator | RESOLVED for reporting; empirical test remains pending |
| Full-chain gates could unnecessarily block narrower research | Major | Section 4.3 explicitly allows separately protocolled transfer-only screening | RESOLVED for scope clarification |
| True independent validation absent | Major | Sections 4.1–4.3 and completion contract state exact missing evidence | ACKNOWLEDGED_LIMITATION / PENDING_EXTERNAL_EVIDENCE |

The pending status is retained rather than calling the gap permanently unresolvable or claiming that wording has repaired missing evidence. No new performance estimate, model fit, human assessor signature, author declaration or submission was generated.

## Verification

The branch verifier passed 25 checks, including both supplemental PDF hashes and the existing six admission-logic tests. These counts are technical checks only. Manuscript DOCX/PDF and raw-data-free reproducibility package are rebuilt after the revision. Numerical predictive tolerances remain unset until a specific pathway and analytical uncertainty justify them; no arbitrary pass threshold has been invented.

## Immediate external dependency

The existing source-clarification letter remains an unsent draft. A coordinator needs to identify a qualified independent assessor and arrange lawful access to the study-level records/supplements. No contact has been made and no response assumed. Until these inputs exist, repeated internal rewriting cannot complete independent validation.
