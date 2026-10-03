# Claim-specific extension — 3 October 2026

This post-pilot implementation is separate from the frozen full-chain rule. It is **not empirically validated**. Four targets and five Boolean evidence routes allow a narrower claim to remain eligible for review when a stronger claim is held. Eligibility is conditional on truthful, adequate scientific judgments; it does not authorize automatic release of exposure estimates.

## Reproduce without raw data or network access

From the repository root, using Python 3.11 or newer:

```sh
python3 -m unittest discover -s extensions/claim_contracts_20261003 -p 'test_*.py' -v
python3 scripts/verify_release.py
```

Ten synthetic test methods check all routes, item ablations, malformed inputs, immutable inputs, alternative repair sets and exhaustive candidate-subset comparison against a direct route-set calculation. These are not ten independent scientific validation cases.

For Figure 5, install the existing optional figure requirements, then run:

```sh
python3 extensions/claim_contracts_20261003/render_figure5.py
```

This reads only `classification_summary.json` and writes SVG, PDF, PNG and geometry/provenance reports to `rendered/`. The published SVG retains editable text. Re-rendered SVG bytes may vary with fonts, library versions, timestamps or SVG identifiers; compare numerical counts and check the geometry report rather than require byte identity of regenerated images. The stored SVG has its own integrity hash.

## Scientific scope

The targets are bounded sample occurrence, tissue concentration conditional on animal dose, body-weight-normalised chronic food intake, and feed-attributed intake. The last target has a chain-reconstruction route with other-source control, or a source-specific measurement route with an identifying design. Trade attribution, acute exposure and disease burden are not implemented.

Each evidence item needs a state and reason; supported items additionally need a source locator. Missing items are `not_searched`, not proof of global absence. `not_found_in_scope`, `incompatible`, `conflicting`, `uncertain` and `not_applicable` remain distinguishable. A required item marked not applicable does not bypass a contract. Source locators are not automatically verified. Dose, species, tissue, duration, food form, residue definition, population, period, uncertainty and sampling design require human scientific appraisal before support can be assigned.

Repair enumeration assumes a fixed monotone Boolean specification and successful hypothetical resolution. For each route R and supported set S, a missing set R minus S can be repaired only if all missing items are among the candidates. Retain feasible missing sets containing no strictly smaller feasible missing set. Different-sized inclusion-minimal sets may both be valid; neither minimum cost nor real acquisition feasibility is established. Newly contradictory evidence requires re-adjudication, not merely adding a supported item. Synthetic fixtures never replace empirical judgments.

## Aggregate classification evidence

The source audit covers 230 module-by-code items, 218 distinct codes. Twelve codes occur in both modules and must not be counted as independent new validation subjects. Pesticide selections: both rules 50 samples, keywords only 6, hierarchy only 14, neither 640 (710 total). Veterinary-drug selections: both 8,270, keywords only 0, hierarchy only 330, neither 2,973 (11,573 total). Code and result-row counts are retained in the JSON.

The hierarchy uses five post-hoc FoodEx2 anchors: A0BXF, A0BXZ, A031E, A033J and A02PR. It is not an independent gold standard. Hierarchy-only selections are unresolved candidates, not confirmed false negatives; accuracy and superiority are not estimated. Figure 5 displays the selection union with separate module scales, not the full denominators or a country-level risk comparison.

Original code and documentation follow the repository licences. The aggregate JSON and SVG contain no sample/person identifiers or raw monitoring records. Its upstream aggregate-source hash is provenance, not a claim that underlying third-party material is redistributed. Independent classification labels, positive-case benchmarking, comparative utility and external prediction validation remain unavailable in this release.
