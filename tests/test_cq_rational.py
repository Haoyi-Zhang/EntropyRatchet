"""Independent determinant/squared-norm oracle and bounded finite controls."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.cq_rational import check_sqrt, sqrt_bounds, norm_bounds, compare_leq, cq_smoothing_enclosure
from src import cq_rational


class RationalCQTests(unittest.TestCase):
    def test_sqrt_certificates_and_exact_roots(self):
        for value in (F(0),F(1),F(1,4),F(2),F(1,3),F(10**30,7),F(1,10**30)):
            for bits in (4,16,64):
                lower,upper = sqrt_bounds(value,bits)
                self.assertLessEqual(lower*lower,value)
                self.assertLessEqual(value,upper*upper)
                self.assertLessEqual(upper-lower,F(1,1 << bits))
        self.assertEqual(sqrt_bounds(F(1,4)),(F(1,2),F(1,2)))
        for row in ((F(2),F(2),F(3)),(F(2),F(-1),F(2)),(F(2),F(1),F(1))):
            with self.assertRaises(ValueError): check_sqrt(*row)

    def test_norm_independent_determinant_identity(self):
        matrices = [(x,y,y,w) for x,y,w in product((F(-2),F(-1,3),F(0),F(1,3),F(2)),repeat=3)]
        matrices += [(F(10**20),F(1,10**20),F(1,10**20),F(-10**20)),
                     (F(1,4),)*4,(F(1),F(0),F(0),F(1))]
        for x,y,z,w in matrices:
            (lower,upper),certificate = norm_bounds((x,y,z,w),32)
            # For a symmetric matrix, norm^2=tr(A^2)+2|det(A)|.
            squared = x*x+w*w+2*y*y+2*abs(x*w-y*y)
            self.assertLessEqual(lower*lower,squared)
            self.assertLessEqual(squared,upper*upper)
            self.assertTrue(check_sqrt(*certificate))

    def test_witness_directional_claims_and_no_renormalization(self):
        row = cq_smoothing_enclosure(4,128)
        self.assertEqual(row['status'],'proved')
        self.assertEqual(row['witness_trace'],F(15,16))
        self.assertEqual(row['purified_distance_squared'],F(1,16))
        self.assertEqual(row['generalized_trace_distance'],F(1,16))
        self.assertFalse(row['renormalized'])
        self.assertEqual(row['commutator_squared_hilbert_schmidt_norm'],F(1,32))
        self.assertEqual(row['output_smoothing_distance'],(F(1,32),)*2)
        self.assertEqual(row['marginal_restoration_distance'],(F(1,32),)*2)
        self.assertLessEqual(row['actual_fixed_marginal_distance'][1],row['three_term_bound'][0])
        self.assertLessEqual(row['witness_own_marginal_distance'][1],row['witness_hash_bound'][0])
        for certificate in row['sqrt_certificates']: self.assertTrue(check_sqrt(*certificate))

    def test_overlap_and_precision_cap_do_not_become_success(self):
        self.assertEqual(compare_leq((F(0),F(2)),(F(1),F(3))),'inconclusive')
        self.assertEqual(compare_leq((F(2),F(3)),(F(0),F(1))),'disproved')
        self.assertEqual(compare_leq((F(1),F(1)),(F(1),F(1))),'proved')
        row = cq_smoothing_enclosure(4,4)
        self.assertEqual(len(row['attempts']),1)
        self.assertIn(row['status'],('proved','inconclusive'))
        if row['status'] == 'inconclusive':
            self.assertIn('inconclusive',row['attempts'][-1]['comparisons'].values())
        # Inject an owned sqrt(2) interval compared with itself to exercise the
        # cap, not to fabricate a successful witness or replace the real run.
        def straddling(bits):
            interval = sqrt_bounds(F(2),bits)
            return dict(actual_fixed_marginal_distance=interval, three_term_bound=interval,
                        witness_own_marginal_distance=interval, witness_hash_bound=interval)
        with patch.object(cq_rational,'_witness',side_effect=straddling):
            capped = cq_smoothing_enclosure(4,16)
        self.assertEqual(capped['status'],'inconclusive')
        self.assertEqual([a['bits'] for a in capped['attempts']],[4,8,16])

    def test_invalid_exact_inputs_and_budgets(self):
        for value,bits in ((F(-1),16),(True,16),(0.5,16),(F(1),True),(F(1),3),(F(1),257)):
            with self.assertRaises(ValueError): sqrt_bounds(value,bits)
        with self.assertRaises(ValueError): norm_bounds((F(0),F(1),F(0),F(0)))
        for budget in ((3,128),(16,8),(16,257),(True,64)):
            with self.assertRaises(ValueError): cq_smoothing_enclosure(*budget)


if __name__ == '__main__': unittest.main()
