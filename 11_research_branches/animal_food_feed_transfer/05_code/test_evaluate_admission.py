#!/usr/bin/env python3
"""Decision-logic tests only; a synthetic full-pass case is not empirical evidence."""

import json
import unittest
from pathlib import Path

from evaluate_admission import REQUIRED_A, evaluate


SOURCE = Path(__file__).resolve().parents[1] / "01_protocol/admission_challenge_cases.json"


class AdmissionTests(unittest.TestCase):
    def test_documented_cases(self):
        cases = json.loads(SOURCE.read_text(encoding="utf-8"))["cases"]
        self.assertEqual({case["id"] for case in cases}, {"bounded_pilot", "jmpr_2005_glyphosate_cattle_kidney"})
        for case in cases:
            self.assertEqual(evaluate(case)["decision"], "STOP_BEFORE_EXPOSURE_MODEL")
        external = next(case for case in cases if case["id"] == "jmpr_2005_glyphosate_cattle_kidney")
        self.assertEqual(external["transfer_evidence_presence"], "confirmed")
        self.assertEqual(external["gates"]["transfer"], "partial")
        self.assertIn("transfer", evaluate(external)["blocked_gates"])

    def test_each_single_missing_gate_blocks(self):
        baseline = {gate: "pass" for gate in REQUIRED_A}
        self.assertEqual(evaluate({"id": "synthetic", "gates": baseline})["decision"], "ADMIT_FOR_MODEL_DESIGN")
        for gate in REQUIRED_A:
            for state in ("partial", "fail", "unknown"):
                with self.subTest(gate=gate, state=state):
                    gates = baseline | {gate: state}
                    decision = evaluate({"id": "synthetic", "gates": gates})
                    self.assertEqual(decision["decision"], "STOP_BEFORE_EXPOSURE_MODEL")
                    self.assertEqual(decision["blocked_gates"], [gate])

    def test_extra_or_missing_gate_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({"id": "bad", "gates": {}})
        with self.assertRaises(ValueError):
            evaluate({"id": "bad", "gates": dict.fromkeys(REQUIRED_A, "pass") | {"extra": "pass"}})

    def test_unknown_state_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({"id": "bad", "gates": dict.fromkeys(REQUIRED_A, "PASS")})

    def test_review_warning_does_not_infer_validation(self):
        result = evaluate({"id": "synthetic", "gates": dict.fromkeys(REQUIRED_A, "pass")})
        self.assertNotIn("await human confirmation", result["warning"])
        self.assertIn("cannot establish", result["warning"])
        self.assertEqual(result["prediction_validation"], "not_evaluated")

    def test_ready_data_can_enter_design_before_validation(self):
        result = evaluate({"id": "synthetic", "gates": dict.fromkeys(REQUIRED_A, "pass")})
        self.assertEqual(result["decision"], "ADMIT_FOR_MODEL_DESIGN")
        self.assertEqual(result["exposure_state"], "HOLD_VALIDATION_NOT_COMPLETED")

    def test_failed_prediction_cannot_release_exposure(self):
        validation = {
            "status": "fail", "criteria_lock_ref": "synthetic-criteria",
            "prediction_lock_ref": "synthetic-predictions", "assessment_ref": "synthetic-result",
            "predictions_locked_before_unblinding": True,
        }
        case = {"id": "synthetic", "gates": dict.fromkeys(REQUIRED_A, "pass"), "prediction_validation": validation}
        self.assertEqual(evaluate(case)["exposure_state"], "HOLD_PREDICTION_VALIDATION_FAILED")
        validation["status"] = "pass"
        self.assertEqual(evaluate(case)["exposure_state"], "ELIGIBLE_FOR_BOUNDED_EXPOSURE_REVIEW")
        validation["predictions_locked_before_unblinding"] = False
        with self.assertRaises(ValueError):
            evaluate(case)

    def test_validation_claim_requires_documentation_and_ready_data(self):
        case = {"id": "synthetic", "gates": dict.fromkeys(REQUIRED_A, "pass"),
                "prediction_validation": {"status": "pass"}}
        with self.assertRaises(ValueError):
            evaluate(case)
        case["gates"]["feed_occurrence"] = "fail"
        with self.assertRaises(ValueError):
            evaluate(case)


if __name__ == "__main__":
    unittest.main()
