#!/usr/bin/env python3
"""Reproduce a conjunctive admission decision from explicitly adjudicated gates.

This checks decision logic, not the truth of the underlying scientific judgments.
Missing/partial gates never become passes. No exposure values are calculated.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_A = (
    "feed_occurrence", "feed_form", "feed_use", "ration", "transfer",
    "animal_occurrence", "residue_definition", "human_diet", "validation_dataset",
)
ALLOWED = {"pass", "partial", "fail", "unknown"}


def evaluate(case: dict) -> dict:
    gates = case["gates"]
    if set(gates) != set(REQUIRED_A):
        raise ValueError(f"Expected exactly Module A gates: {sorted(REQUIRED_A)}")
    if any(state not in ALLOWED for state in gates.values()):
        raise ValueError("Gate state must be pass, partial, fail, or unknown")
    blocked = [gate for gate in REQUIRED_A if gates[gate] != "pass"]
    validation = case.get("prediction_validation", {"status": "not_evaluated"})
    validation_status = validation["status"]
    if validation_status not in {"not_evaluated", "pass", "fail"}:
        raise ValueError("Prediction validation must be not_evaluated, pass, or fail")
    if validation_status != "not_evaluated":
        if blocked:
            raise ValueError("A completed validation cannot release an inadmissible evidence chain")
        if not all(isinstance(validation.get(key), str) and validation[key].strip()
                   for key in ("criteria_lock_ref", "prediction_lock_ref", "assessment_ref")):
            raise ValueError("Completed validation requires criteria, prediction-lock and assessment references")
        if validation.get("predictions_locked_before_unblinding") is not True:
            raise ValueError("Validation cannot be independent without a prediction lock before unblinding")
    exposure_state = {
        "not_evaluated": "HOLD_VALIDATION_NOT_COMPLETED",
        "fail": "HOLD_PREDICTION_VALIDATION_FAILED",
        "pass": "ELIGIBLE_FOR_BOUNDED_EXPOSURE_REVIEW",
    }[validation_status]
    if blocked:
        exposure_state = "HOLD_DATA_NOT_READY"
    return {
        "id": case["id"],
        "decision": "ADMIT_FOR_MODEL_DESIGN" if not blocked else "STOP_BEFORE_EXPOSURE_MODEL",
        "blocked_gates": blocked,
        "passed_gates": [gate for gate in REQUIRED_A if gates[gate] == "pass"],
        "prediction_validation": validation_status,
        "exposure_state": exposure_state,
        "warning": "Evidence judgments and referenced locks require source review; this function cannot establish their truth or assessor independence. Reported non-blinded review is distinct from blinded adjudication reliability and predictive validation. ADMIT permits model design; it does not establish validation, global inference or submission approval.",
    }


def main() -> int:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "01_protocol/admission_challenge_cases.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    for case in data["cases"]:
        print(json.dumps(evaluate(case), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
