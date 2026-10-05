"""Regression diagnostics, not a machine-checked smooth quantum proof."""
from fractions import Fraction
import json
from pathlib import Path
import unittest
from src.extractor_contract import (budget_case, contract_checks,
    optimized_marginal_diagnostic, cq_smoothing_diagnostic,
    xor_independence_controls, retired_input_recomputation)
from src.sequential_bounds import (persistent_policy_search,
    persistent_target_formula, persistent_final_only_formula,
    fresh_lifetime_formula, fresh_lifetime_enumeration)
from verify import (persistent_prefix_second, verify_extractor_interface)
BASE=Path(__file__).resolve().parents[1]
CONFIG=json.loads((BASE/'inputs/instances.json').read_text())
class ContractTests(unittest.TestCase):
    def test_nonzero_smoothing_pays_both_costs(self):
        row=budget_case(2,6,'1/64')
        self.assertEqual(row['fixed_marginal_bound'],'5/32')
        self.assertEqual(row['output_smoothing_cost'],'1/64')
        self.assertEqual(row['marginal_restoration_cost'],'1/64')
    def test_zero_smoothing_recovers_hash_term(self):
        row=budget_case(2,6,'0')
        self.assertEqual(row['fixed_marginal_bound'],row['hashing_term'])
    def test_invalid_contract_parameters_rejected(self):
        for args in [(2,6,'-1/64'),(2,6,'1'),(2,1,'0'),(2,5,'0')]:
            with self.assertRaises(ValueError):budget_case(*args)
    def test_optimized_side_is_not_actual_side(self):
        row=optimized_marginal_diagnostic()
        self.assertEqual(row['fixed_distance'],'3/16')
        self.assertEqual(row['optimized_distance'],'1/8')
        self.assertNotEqual(row['actual_side_marginal'],row['optimizing_side_marginal'])
    def test_cq_witness_has_nonzero_smoothing_and_commutator(self):
        row=cq_smoothing_diagnostic()
        self.assertEqual(row['purified_distance'],'1/4')
        self.assertEqual(row['witness_trace'],'15/16')
        self.assertEqual(row['commutator_squared_hilbert_schmidt_norm'],'1/32')
        self.assertFalse(row['renormalized'])
        self.assertAlmostEqual(row['output_smoothing_distance'],1/32)
        self.assertAlmostEqual(row['marginal_restoration_distance'],1/32)
    def test_second_interface_calculation(self):
        row=contract_checks(CONFIG['contract_budget_cases'])
        result=verify_extractor_interface(row,CONFIG['contract_budget_cases'])
        self.assertEqual(result['retired_input_recomputations'],2048)
    def test_single_eta_mutation_rejected(self):
        row=contract_checks(CONFIG['contract_budget_cases'])
        case=row['budgets'][1]
        case['fixed_marginal_bound']=str(Fraction(case['smoothing'])+Fraction(case['hashing_term']))
        with self.assertRaises(AssertionError):
            verify_extractor_interface(row,CONFIG['contract_budget_cases'])
    def test_smoothing_renormalization_mutation_rejected(self):
        row=contract_checks(CONFIG['contract_budget_cases'])
        row['nonzero_smoothing_cq']['renormalized']=True
        with self.assertRaises(AssertionError):
            verify_extractor_interface(row,CONFIG['contract_budget_cases'])
    def test_xor_joint_independence_controls(self):
        row=xor_independence_controls()
        self.assertEqual(row['correlated_source_joint_distance'],'1/2')
        self.assertEqual(row['independent_source_joint_distance'],'0/1')
        self.assertEqual(row['correlated_output_support'],[0,2])
    def test_retired_input_recomputed_not_rollback(self):
        row=retired_input_recomputation()
        self.assertEqual(row['public_seeds'],256)
        self.assertEqual(row['recomputed_points'],2048)
        self.assertEqual(row['mismatches'],0)
        self.assertEqual(row['image_size_histogram'],{'1':4,'2':84,'4':168})
    def test_retired_input_mutation_rejected(self):
        row=contract_checks(CONFIG['contract_budget_cases'])
        row['retired_input']['mismatches']=1
        with self.assertRaises(AssertionError):
            verify_extractor_interface(row,CONFIG['contract_budget_cases'])
    def test_lifetime_counterexamples(self):
        for triple,expected in [((3,1,2),Fraction(3,4)),((5,1,3),Fraction(7,16))]:
            self.assertEqual(persistent_policy_search(*triple)[0],expected)
            self.assertEqual(persistent_prefix_second(*triple),expected)
            self.assertGreater(expected,persistent_final_only_formula(*triple))
    def test_lifetime_no_leakage_repeated_guesses(self):
        self.assertEqual(persistent_policy_search(3,0,3)[0],Fraction(3,8))
        self.assertEqual(persistent_prefix_second(3,0,3),Fraction(3,8))
        self.assertEqual(persistent_final_only_formula(3,0,3),Fraction(1,8))
    def test_lifetime_single_session_and_saturation(self):
        for bits in range(1,5):
            for leakage in range(bits+1):
                self.assertEqual(persistent_policy_search(bits,leakage,1)[0],
                                 fresh_lifetime_formula(bits,leakage,1))
            self.assertEqual(persistent_policy_search(bits,bits,1)[0],1)
        self.assertEqual(persistent_policy_search(2,0,4)[0],1)
    def test_complete_small_policy_grid(self):
        points=0
        for bits in range(1,4):
            for leakage in range(bits+1):
                for sessions in range(1,5):
                    triple=(bits,leakage,sessions)
                    first=persistent_policy_search(*triple)[0]
                    self.assertEqual(first,persistent_prefix_second(*triple))
                    self.assertEqual(first,persistent_target_formula(*triple))
                    points+=1
        self.assertEqual(points,36)
    def test_fresh_small_boundary_grid(self):
        for bits in range(1,4):
            for leakage in range(bits+1):
                for sessions in range(1,4):
                    self.assertEqual(fresh_lifetime_enumeration(bits,leakage,sessions),
                                     fresh_lifetime_formula(bits,leakage,sessions))
if __name__=='__main__':unittest.main()
