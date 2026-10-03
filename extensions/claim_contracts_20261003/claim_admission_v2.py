"""Post-pilot claim contracts, 2026-10-03. Logic demonstration, not validation.

No scientific data are loaded. A supported item requires a source locator;
the program cannot verify the truth or sufficiency of an assessor's judgment.
Frozen evaluate_admission.py and its cases are deliberately unchanged.
"""
from itertools import combinations

# Each tuple is one alternative complete route. Keys are scientific judgments,
# not mere presence checks for files or columns. See supplement S3.
OCCURRENCE = frozenset({"sample_scope", "matrix_identity", "residue_definition",
                        "measurement_semantics"})
TRANSFER = frozenset({"animal_dose", "species_tissue_time", "residue_definition",
                     "transfer_relation", "applicability"})
INTAKE = frozenset({"food_concentrations", "food_consumption", "body_weight",
                   "food_form_link", "residue_definition", "population_time_link",
                   "censoring_uncertainty"})
CONTRACTS = {
    "sample_occurrence": (OCCURRENCE,),
    "conditional_tissue": (TRANSFER,),
    "food_intake": (INTAKE,),
    "feed_attributed_intake": (
        INTAKE | TRANSFER | {"feed_occurrence", "ration_link", "other_source_control"},
        INTAKE | {"source_specific_measurement", "source_design_identification"},
    ),
}
STATES = {"supported", "not_searched", "not_found_in_scope", "incompatible",
          "conflicting", "uncertain", "not_applicable"}
KEYS = frozenset().union(*(route for routes in CONTRACTS.values() for route in routes))


def evaluate(claim, evidence):
    routes = CONTRACTS[claim]  # Unknown claims fail loudly.
    if not isinstance(evidence, dict):
        raise ValueError("Evidence must be an item-keyed dictionary")
    if set(evidence) - KEYS:
        raise ValueError("Unknown evidence key")
    for item in evidence.values():
        if not isinstance(item, dict):
            raise ValueError("Each evidence judgment must be a dictionary")
        if not isinstance(item.get("state"), str) or item["state"] not in STATES:
            raise ValueError("Unknown evidence state")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            raise ValueError("Every judgment requires a reason")
        if item["state"] == "supported" and (not isinstance(item.get("source"), str) or not item["source"].strip()):
            raise ValueError("Supported evidence requires a source locator")
    assessed = []
    for index, route in enumerate(routes):
        blockers = {key: evidence.get(key, {"state": "not_searched",
                    "reason": "No judgment supplied"}) for key in sorted(route)
                    if evidence.get(key, {}).get("state") != "supported"}
        assessed.append({"route": index + 1, "blockers": blockers})
    admitted = any(not route["blockers"] for route in assessed)
    return {"version": "post_pilot_20261003", "claim": claim,
            "decision": "ELIGIBLE_FOR_TARGET_REVIEW" if admitted else "HOLD_TARGET",
            "routes": assessed, "prediction_validation": "NOT_ASSESSED",
            "warning": "Conditional on assessor judgments and contract adequacy; not an exposure estimate, scientific validation, source-truth check or release approval."}


def minimal_repairs(claim, evidence, candidates):
    """Enumerate inclusion-minimal hypothetical repairs over a supplied finite set.

    Each candidate means successful scientific resolution, not acquisition of a
    file. No probabilities or costs, and no assertion that resolution is possible.
    """
    if not isinstance(candidates, (list, tuple, set, frozenset)) or any(
            not isinstance(key, str) for key in candidates):
        raise ValueError("Candidates must be a finite collection of evidence-key strings")
    candidates = sorted(set(candidates))
    if len(candidates) > 16 or set(candidates) - KEYS:
        raise ValueError("At most 16 known candidate items are permitted")
    evaluate(claim, evidence)
    found = []
    for size in range(len(candidates) + 1):
        for subset in combinations(candidates, size):
            if any(set(prior).issubset(subset) for prior in found):
                continue
            trial = {**evidence, **{key: {"state": "supported",
                     "source": "SYNTHETIC successful-repair assumption",
                     "reason": "Hypothetical resolution, not acquired evidence"} for key in subset}}
            if evaluate(claim, trial)["decision"] == "ELIGIBLE_FOR_TARGET_REVIEW":
                found.append(list(subset))
    return found
