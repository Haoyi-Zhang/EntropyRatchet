"""Exact finite games for semantic freshness, lifetime leakage, and rollback.

The models are deliberately elementary and entirely classical.  They corroborate
closed-form probabilities used in the manuscript; they do not implement a
quantum-verification protocol or replace the general reductions.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import product


def rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def single_session_guess(bits: int, leakage_bits: int) -> Fraction:
    """Optimal guessing probability for a uniform target after prefix leakage."""
    if bits < 1 or not 0 <= leakage_bits <= bits:
        raise ValueError("require bits >= 1 and 0 <= leakage_bits <= bits")
    return Fraction(1, 1 << (bits - leakage_bits))


def fresh_lifetime_formula(bits: int, leakage_bits: int, sessions: int) -> Fraction:
    """Probability of at least one success for independent session targets."""
    if sessions < 1:
        raise ValueError("sessions must be positive")
    p = single_session_guess(bits, leakage_bits)
    return 1 - (1 - p) ** sessions


def fresh_lifetime_enumeration(bits: int, leakage_bits: int, sessions: int) -> Fraction:
    """Directly enumerate independent targets and a canonical optimal guesser."""
    if bits > 5 or sessions > 5:
        raise ValueError("enumeration exceeds the frozen finite domain")
    size = 1 << bits
    suffix_mask = (1 << (bits - leakage_bits)) - 1
    wins = 0
    points = 0
    # The view exposes the high-order leakage_bits coordinates.  For each view,
    # guessing the all-zero hidden suffix is optimal by uniformity.
    for targets in product(range(size), repeat=sessions):
        points += 1
        wins += int(any((target & suffix_mask) == 0 for target in targets))
    return Fraction(wins, points)


def union_bound(bits: int, leakage_bits: int, sessions: int) -> Fraction:
    return min(Fraction(1), sessions * single_session_guess(bits, leakage_bits))


def persistent_final_only_formula(bits: int, leakage_per_session: int, sessions: int) -> Fraction:
    """One final guess, with no earlier guesses or rejection feedback."""
    if bits < 1 or not 0 <= leakage_per_session <= bits or sessions < 1:
        raise ValueError("invalid final-only parameters")
    return Fraction(1, 1 << max(bits - leakage_per_session * sessions, 0))


def persistent_target_formula(bits: int, leakage_per_session: int, sessions: int) -> Fraction:
    """Coordinate-query lifetime optimum, including one guess per session.

    At most 2**(j*L) new secrets can be won in session j.  The full prefix
    query tree attains the sum until saturation (proof P11).  This expression
    is checked against an unrestricted coordinate-policy Bellman search.
    """
    if bits < 1 or not 0 <= leakage_per_session <= bits or sessions < 1:
        raise ValueError("invalid lifetime parameters")
    wins = sum(1 << min(bits, j * leakage_per_session)
               for j in range(1, sessions + 1))
    return Fraction(min(1 << bits, wins), 1 << bits)


def persistent_policy_search(bits: int, leakage_per_session: int, sessions: int) -> tuple[Fraction, int]:
    """Exhaust legal actions with memoization, over uniform posterior sets.

    State = (remaining candidates, known coordinate mask, sessions left,
    queries left before the current guess).  Rejection removes the guessed
    candidate.  Classical leakage reads individual coordinates, not arbitrary
    Boolean functions.  The maximum is attained by a deterministic strategy.
    """
    if not (1 <= bits <= 5 and 0 <= leakage_per_session <= bits and 1 <= sessions <= 5):
        raise ValueError("policy search exceeds the frozen finite domain")
    masks = tuple(sum(1 << x for x in range(1 << bits) if (x >> i) & 1)
                  for i in range(bits))

    @lru_cache(maxsize=None)
    def value(candidates: int, known: int, remaining: int, queries: int) -> int:
        count = candidates.bit_count()
        if not count or not remaining:
            return 0
        # Repeated distinct guesses alone cover this posterior.
        if remaining >= count:
            return count
        best = 0
        if queries:
            for i, mask in enumerate(masks):
                if known & (1 << i):
                    continue
                left = candidates & mask
                right = candidates ^ left
                if not left or not right:
                    continue  # a constant answer is dominated by not querying
                candidate = (value(left, known | (1 << i), remaining, queries - 1)
                             + value(right, known | (1 << i), remaining, queries - 1))
                best = max(best, candidate)
                if best == count:
                    return best
        # Stopping the query phase is legal, including when queries==0.
        options = candidates
        while options:
            guess = options & -options
            options ^= guess
            best = max(best, 1 + value(candidates ^ guess, known, remaining - 1,
                                       leakage_per_session))
            if best == count:
                return best
        return best

    wins = value((1 << (1 << bits)) - 1, 0, sessions, leakage_per_session)
    return Fraction(wins, 1 << bits), value.cache_info().currsize


def persistent_target_enumeration(bits: int, leakage_per_session: int, sessions: int) -> Fraction:
    """Exact full-policy recursion for the any-session success event."""
    return persistent_policy_search(bits, leakage_per_session, sessions)[0]


def rollback_case(bits: int) -> dict:
    """Compare fresh regeneration with restoring a previously exposed target."""
    if not 1 <= bits <= 12:
        raise ValueError("bits outside the frozen finite domain")
    size = 1 << bits
    fresh_wins = 0
    restored_wins = 0
    points = 0
    for old in range(size):
        # The completed-session target is fully exposed.  Under fresh
        # regeneration the new target is independent; under rollback it equals
        # the exposed target.
        for new in range(size):
            points += 1
            fresh_wins += int(old == new)
        restored_wins += 1
    fresh = Fraction(fresh_wins, points)
    restored = Fraction(restored_wins, size)
    assert fresh == Fraction(1, size)
    assert restored == 1
    return {
        "bits": bits,
        "old_target_fully_exposed": True,
        "fresh_regeneration_success": rational(fresh),
        "restored_target_success": rational(restored),
        "fresh_points": points,
        "restored_points": size,
    }


def sequential_cases(configs: list[dict]) -> list[dict]:
    out: list[dict] = []
    for cfg in configs:
        bits = int(cfg["bits"])
        leakage = int(cfg["leakage_bits"])
        sessions = int(cfg["sessions"])
        fresh_exact = fresh_lifetime_enumeration(bits, leakage, sessions)
        fresh_closed = fresh_lifetime_formula(bits, leakage, sessions)
        persistent_exact, policy_states = persistent_policy_search(bits, leakage, sessions)
        persistent_closed = persistent_target_formula(bits, leakage, sessions)
        assert fresh_exact == fresh_closed
        assert persistent_exact == persistent_closed
        out.append({
            "bits": bits,
            "leakage_bits_per_session": leakage,
            "sessions": sessions,
            "single_session_success": rational(single_session_guess(bits, leakage)),
            "fresh_targets_lifetime_success": rational(fresh_exact),
            "union_bound": rational(union_bound(bits, leakage, sessions)),
            "persistent_target_success": rational(persistent_exact),
            "persistent_final_only_no_feedback": rational(persistent_final_only_formula(bits, leakage, sessions)),
            "event": "any session guess correct; public rejection after each wrong guess",
            "persistent_policy_states": policy_states,
            "fresh_target_tuples": (1 << bits) ** sessions,
            "persistent_targets": 1 << bits,
        })
    return out


def reduction_loss_cases(configs: list[dict]) -> list[dict]:
    """Exact arithmetic for sum_j 2^{L_j} epsilon_j plus freshness failure."""
    out: list[dict] = []
    for cfg in configs:
        eps = Fraction(cfg["epsilon"])
        leakage = [int(value) for value in cfg["leakage_bits"]]
        freshness_failure = Fraction(cfg.get("freshness_failure", "0/1"))
        per_session = [min(Fraction(1), (1 << ell) * eps) for ell in leakage]
        total = min(Fraction(1), freshness_failure + sum(per_session, Fraction(0)))
        out.append({
            "epsilon": rational(eps),
            "leakage_bits": leakage,
            "freshness_failure": rational(freshness_failure),
            "per_session_terms": [rational(value) for value in per_session],
            "total_upper_bound": rational(total),
        })
    return out
