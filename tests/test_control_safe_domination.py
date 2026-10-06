"""Finite regressions for the proof's positive-block inclusion, not a QPT proof."""
from fractions import Fraction
from itertools import product
from collections import Counter
import unittest
from src.finite_games import posterior_success


class ControlSafeDominationTests(unittest.TestCase):
    def test_all_two_session_monitor_and_acceptance_tables(self):
        # Four equiprobable owned histories. cutoff=0,1,2 allows that many
        # sessions before a proof-only rejection. No detector is run by the
        # unmonitored extension; it retains the ordinary acceptance table.
        configurations = 0
        for cutoffs in product(range(3), repeat=4):
            for table in range(1 << 8):
                for session in range(2):
                    safe_first = extension_current = 0
                    for history in range(4):
                        accepts = [(table >> (2*history+j)) & 1 for j in range(2)]
                        safe_first += int(session < cutoffs[history]
                                          and accepts[session]
                                          and not any(accepts[:session]))
                        extension_current += accepts[session]
                    self.assertLessEqual(safe_first, extension_current)
                configurations += 1
        self.assertEqual(configurations, 20736)

    def test_safety_postselection_would_inflate_the_event(self):
        # Acceptance and safety coincide on one of four histories. Filtering
        # without renormalization costs 1/4; conditioning would incorrectly
        # ask the base theorem to bound probability one.
        actual = Fraction(1,4)
        safe_mass = Fraction(1,4)
        postselected = safe_mass / Fraction(1,4)
        self.assertLessEqual(safe_mass, actual)
        self.assertGreater(postselected, actual)

    def test_prior_bad_paths_need_not_be_detected(self):
        # A reduction may simulate an earlier false acceptance without knowing
        # statement truth: all current bad paths still dominate first-bad ones.
        accepts = [(1,0),(1,1),(0,1),(0,0)]
        first_at_second = sum(not a and b for a,b in accepts)
        all_at_second = sum(b for _,b in accepts)
        self.assertEqual((first_at_second, all_at_second), (1,2))

    def test_abort_flag_belongs_to_retained_entropy_support(self):
        # A two-bit uniform retained state with no payload observations still
        # loses one bit of min-entropy if a public abort says whether C==0.
        # Pricing the abort's probability does not erase its entropy cost.
        initial = posterior_success(Counter((c,()) for c in range(4)))
        observed = posterior_success(Counter((c,(c==0,)) for c in range(4)))
        self.assertEqual(initial,Fraction(1,4))
        self.assertEqual(observed,Fraction(1,2))
        self.assertGreater(observed,initial)  # invalid J=1 accounting
        self.assertLessEqual(observed,2*initial)  # complete transcript J=2


if __name__ == '__main__':
    unittest.main()
