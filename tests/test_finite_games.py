"""Small regression tests, including rejecting altered finite evidence."""
import copy
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import unittest
from src.finite_games import (posterior_success,tree_case,tree_leaves,public_framing_case,shares_case,
                             prefix_cases,mask_identity_count,negative_controls,future_target_case)
from src.sequential_bounds import (single_session_guess,fresh_lifetime_formula,
    fresh_lifetime_enumeration,persistent_target_formula,persistent_target_enumeration,
    rollback_case,sequential_cases,reduction_loss_cases)
from src.entropy_ratchet import (extractor_case,joint_distance_for_flat_source,
    xor_ratchet_case,entropy_budget_case,entropy_barrier_case,ratchet_loss_case,
    ratchet_negative_controls)
from verify import (tree_histogram, public_framing_summary_second, control_values, check,
                    extractor_summary_second, ratchet_controls_second)


class ModelTests(unittest.TestCase):
    def test_empty_mass_rejected(self):
        with self.assertRaises(ValueError): posterior_success(Counter())
    def test_invalid_mass_rejected(self):
        with self.assertRaises(ValueError): posterior_success(Counter({(0,()):0}))
    def test_no_observation(self):
        self.assertEqual(posterior_success(Counter((s,()) for s in range(4))),Fraction(1,4))
    def test_full_observation(self):
        self.assertEqual(posterior_success(Counter((s,(s,)) for s in range(4))),Fraction(1))
    def test_tree_address(self):
        self.assertEqual([tree_leaves(s,(10,12,12),2) for s in range(4)],[0,2,1,3])
    def test_tree_recurrence(self):
        self.assertEqual(tree_case(2,2)['histogram'],tree_histogram(4,2))
    def test_public_framing_leaf_sampler(self):
        row=public_framing_case(4)
        self.assertEqual(row,public_framing_summary_second(4))
        self.assertEqual(row['public_tree_shapes'],677)
        self.assertEqual(row['strict_improvement_trees'],672)
        self.assertEqual(row['maximum_local_over_leaf_ratio'],'16/5')
        self.assertEqual(row['leaf_uniform_failures'],0)
    def test_future_target(self):
        self.assertEqual(future_target_case()["reconstructed_paths"],262144)
        with self.assertRaises(ValueError):future_target_case(3,2)
    def test_domain_guards(self):
        for action in [lambda:tree_case(4,4),lambda:public_framing_case(5),lambda:shares_case(3,3,True),lambda:prefix_cases(11),lambda:mask_identity_count(7)]:
            with self.assertRaises(ValueError):action()
    def test_fresh_and_restored_masks(self):
        self.assertEqual(shares_case(1,2,True)['max_guess_success'],'1/2')
        self.assertEqual(shares_case(1,2,False)['max_guess_success'],'1/1')
    def test_controls_agree(self):
        values=control_values()
        for row in negative_controls():
            self.assertEqual((row['actual'],row['false_upper_bound']),values[row['name']])

    def test_fresh_sequence_formula_and_enumeration(self):
        self.assertEqual(fresh_lifetime_formula(4,1,4),Fraction(1695,4096))
        self.assertEqual(fresh_lifetime_enumeration(4,1,4),Fraction(1695,4096))
        self.assertEqual(single_session_guess(4,1),Fraction(1,8))

    def test_persistent_accumulation(self):
        self.assertEqual(persistent_target_formula(4,1,4),Fraction(1))
        self.assertEqual(persistent_target_enumeration(4,1,4),Fraction(1))
        self.assertEqual(persistent_target_formula(5,1,3),Fraction(7,16))

    def test_rollback_semantic_freshness(self):
        row=rollback_case(4)
        self.assertEqual(row['fresh_regeneration_success'],'1/16')
        self.assertEqual(row['restored_target_success'],'1/1')

    def test_reduction_arithmetic(self):
        row=reduction_loss_cases([{'epsilon':'1/256','leakage_bits':[0,1,2,3]}])[0]
        self.assertEqual(row['total_upper_bound'],'15/256')

    def test_affine_flat_source_distance(self):
        self.assertEqual(joint_distance_for_flat_source((0,1,2,4),3,1),Fraction(3,16))
        row=extractor_case(3,2,1)
        self.assertEqual(row['maximum_distance'],'3/16')
        self.assertEqual(row,extractor_summary_second(3,2,1))

    def test_extractor_domain_guards(self):
        with self.assertRaises(ValueError): extractor_case(5,3,1)
        with self.assertRaises(ValueError): joint_distance_for_flat_source((),3,1)
        with self.assertRaises(ValueError): joint_distance_for_flat_source((0,0),3,1)

    def test_exact_xor_ratchet(self):
        row=xor_ratchet_case(2,2,3)
        self.assertEqual(row['conditional_distance'],'0/1')
        self.assertEqual(row['enumerated_points'],192)

    def test_entropy_budget_replaces_observation(self):
        a=entropy_budget_case(4,2,0,6)
        b=entropy_budget_case(4,2,2,8)
        c=entropy_budget_case(4,2,4,10)
        self.assertEqual({a['distance_bound'],b['distance_bound'],c['distance_bound']},{'1/8'})
        self.assertEqual([a['required_fresh_entropy_at_this_slack'],
                          b['required_fresh_entropy_at_this_slack'],
                          c['required_fresh_entropy_at_this_slack']],[6,8,10])

    def test_entropy_support_barrier(self):
        self.assertEqual(entropy_barrier_case(1,2)['distance_lower_bound'],'1/2')
        self.assertEqual(entropy_barrier_case(2,4)['distance_lower_bound'],'3/4')
        with self.assertRaises(ValueError): entropy_barrier_case(2,2)

    def test_ratchet_loss_arithmetic(self):
        row=ratchet_loss_case({'anchor_failure':'1/65536',
          'extractor_errors':['1/32768']*4,'soundness_errors':['1/65536']*4,
          'leakage_bits':[2,2,2,2]})
        self.assertEqual(row['total_upper_bound'],'25/65536')

    def test_ratchet_controls_agree(self):
        values=ratchet_controls_second()
        for row in ratchet_negative_controls():
            self.assertEqual((row['actual'],row['false_upper_bound']),values[row['name']])

    def test_mutated_histogram_rejected(self):
        path=Path(__file__).resolve().parents[1]/'results/expected/exact-results.json'
        data=json.loads(path.read_text())
        data['trees'][0]['histogram']={'1/1':1}
        with self.assertRaises(AssertionError):check(data)
    def test_mutated_extractor_evidence_rejected(self):
        path=Path(__file__).resolve().parents[1]/'results/expected/exact-results.json'
        data=json.loads(path.read_text())
        if 'entropy_ratchet' not in data:
            self.skipTest('expected result has not yet been refreshed')
        data['entropy_ratchet']['extractor'][0]['maximum_distance']='0/1'
        with self.assertRaises(AssertionError):check(data)

    def test_mutated_public_framing_rejected(self):
        path=Path(__file__).resolve().parents[1]/'results/expected/exact-results.json'
        data=json.loads(path.read_text())
        data['public_framing']['maximum_local_over_leaf_ratio']='1/1'
        with self.assertRaises(AssertionError):check(data)

    def test_duplicate_domain_rejected(self):
        path=Path(__file__).resolve().parents[1]/'results/expected/exact-results.json'
        data=json.loads(path.read_text()); data['trees'].append(copy.deepcopy(data['trees'][0]))
        with self.assertRaises(AssertionError):check(data)

if __name__=='__main__':unittest.main()
