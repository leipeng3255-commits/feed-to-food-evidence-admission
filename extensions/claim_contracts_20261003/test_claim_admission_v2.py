import unittest
import copy
from itertools import combinations
from claim_admission_v2 import CONTRACTS, STATES, evaluate, minimal_repairs


def supported(keys):
    return {key: {"state": "supported", "source": "SYNTHETIC fixture",
                  "reason": "Assumed solely for a logic test"} for key in keys}


class ClaimContracts(unittest.TestCase):
    def test_malformed_containers_fail_explicitly(self):
        for evidence in [None, [], "supported", {"sample_scope": None},
                         {"sample_scope": {"state": []}}]:
            with self.assertRaises(ValueError):
                evaluate("sample_occurrence", evidence)
        for candidates in [None, "body_weight", [None], [1], {"body_weight": True}]:
            with self.assertRaises(ValueError):
                minimal_repairs("sample_occurrence", {}, candidates)

    def test_alternative_repairs_of_different_sizes_both_retained(self):
        # Inclusion-minimal is not the same as minimum-cardinality.
        claim = "feed_attributed_intake"
        first, second = CONTRACTS[claim]
        common = first & second
        evidence = supported(common)
        candidates = sorted((first | second) - common)
        expected = {frozenset(first - common), frozenset(second - common)}
        repairs = minimal_repairs(claim, evidence, candidates)
        self.assertEqual({frozenset(r) for r in repairs}, expected)
        self.assertGreater(len({len(r) for r in repairs}), 1)
        for repair in repairs:
            for key in repair:
                trial = {**evidence, **supported(set(repair) - {key})}
                self.assertEqual(evaluate(claim, trial)["decision"], "HOLD_TARGET")

    def test_enumerator_matches_direct_route_oracle(self):
        # Independent implementation of the Boolean-route mathematics, not an
        # independent scientific reference standard. Exhaust all candidate subsets.
        claim = "feed_attributed_intake"
        first, second = CONTRACTS[claim]
        evidence = supported(first & second)
        missing_routes = [route - evidence.keys() for route in (first, second)]
        pool = sorted((first | second) - evidence.keys())
        for size in range(len(pool) + 1):
            for candidate_tuple in combinations(pool, size):
                candidates = set(candidate_tuple)
                possible = [r for r in missing_routes if r <= candidates]
                expected = {frozenset(r) for r in possible if not any(t < r for t in possible)}
                actual = minimal_repairs(claim, evidence, candidate_tuple)
                self.assertEqual({frozenset(r) for r in actual}, expected)

    def test_evaluation_and_repair_do_not_mutate_inputs(self):
        evidence = supported({"sample_scope", "matrix_identity"})
        before = copy.deepcopy(evidence)
        candidates = ["residue_definition", "measurement_semantics", "residue_definition"]
        original_candidates = list(candidates)
        evaluate("sample_occurrence", evidence)
        minimal_repairs("sample_occurrence", evidence, candidates)
        self.assertEqual(evidence, before)
        self.assertEqual(candidates, original_candidates)

    def test_same_evidence_different_claims(self):
        evidence = supported(CONTRACTS["sample_occurrence"][0])
        self.assertEqual(evaluate("sample_occurrence", evidence)["decision"], "ELIGIBLE_FOR_TARGET_REVIEW")
        for claim in list(CONTRACTS)[1:]:
            self.assertEqual(evaluate(claim, evidence)["decision"], "HOLD_TARGET")

    def test_all_routes_and_single_item_ablation(self):
        for claim, routes in CONTRACTS.items():
            for route in routes:
                evidence = supported(route)
                self.assertEqual(evaluate(claim, evidence)["decision"], "ELIGIBLE_FOR_TARGET_REVIEW")
                for key in route:
                    for state in STATES - {"supported"}:
                        trial = {**evidence, key: {"state": state, "reason": "Test ablation"}}
                        self.assertEqual(evaluate(claim, trial)["decision"], "HOLD_TARGET")

    def test_minimal_repairs_and_deletion(self):
        claim = "sample_occurrence"
        evidence = supported({"sample_scope", "matrix_identity"})
        repairs = minimal_repairs(claim, evidence, ["residue_definition", "measurement_semantics", "body_weight"])
        self.assertEqual(repairs, [["measurement_semantics", "residue_definition"]])
        for key in repairs[0]:
            trial = {**evidence, **supported(set(repairs[0]) - {key})}
            self.assertEqual(evaluate(claim, trial)["decision"], "HOLD_TARGET")

    def test_alternative_routes_and_empty_repair(self):
        claim = "feed_attributed_intake"
        evidence = supported(CONTRACTS[claim][0])
        self.assertEqual(minimal_repairs(claim, evidence, []), [[]])
        self.assertEqual(minimal_repairs(claim, {}, ["body_weight"]), [])

    def test_fail_closed(self):
        for evidence in [{"typo": {}}, {"sample_scope": {"state": "pass", "reason": "x"}},
                         {"sample_scope": {"state": "supported", "reason": "x"}},
                         {"sample_scope": {"state": "uncertain"}},
                         {"sample_scope": {"state": "supported", "source": None, "reason": "x"}}]:
            with self.assertRaises(ValueError):
                evaluate("sample_occurrence", evidence)
        with self.assertRaises(KeyError):
            evaluate("unknown_claim", {})

    def test_missing_is_not_searched_not_incompatibility(self):
        result = evaluate("sample_occurrence", {})
        self.assertEqual({x["state"] for x in result["routes"][0]["blockers"].values()}, {"not_searched"})
        self.assertEqual(result["prediction_validation"], "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()
