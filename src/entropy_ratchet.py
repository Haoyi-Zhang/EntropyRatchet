"""Exact finite checks for an entropy-ratcheted sequential key source.

This module only checks small classical distributions and exact rational
identities.  The general quantum-side-information extractor theorem is proved
in the accompanying proof note and cited from the literature; no finite check
is presented as a quantum-security experiment.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import comb


def rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def parity(value: int) -> int:
    return value.bit_count() & 1


def affine_hash(x: int, rows: tuple[int, ...], offset: int) -> int:
    """Evaluate y = A x + b over GF(2), little-endian by output row."""
    y = offset
    for index, row in enumerate(rows):
        y ^= parity(row & x) << index
    return y


def affine_seeds(input_bits: int, output_bits: int):
    """Enumerate the full affine two-universal family."""
    for rows in product(range(1 << input_bits), repeat=output_bits):
        for offset in range(1 << output_bits):
            yield rows, offset


def joint_distance_for_flat_source(
    source: tuple[int, ...], input_bits: int, output_bits: int
) -> Fraction:
    """Exact TV distance of (seed, h_seed(X)) from (seed, U_m)."""
    if not source:
        raise ValueError("flat source must be nonempty")
    if len(set(source)) != len(source):
        raise ValueError("flat source support must not contain duplicates")
    if any(not 0 <= x < (1 << input_bits) for x in source):
        raise ValueError("source element outside input domain")
    seed_count = 1 << (input_bits * output_bits + output_bits)
    output_count = 1 << output_bits
    source_count = len(source)
    numerator = 0
    for rows, offset in affine_seeds(input_bits, output_bits):
        bins = [0] * output_count
        for x in source:
            bins[affine_hash(x, rows, offset)] += 1
        # |c/(|D||S|) - 1/(|D|2^m)| with a common denominator.
        numerator += sum(abs(c * output_count - source_count) for c in bins)
    return Fraction(numerator, 2 * seed_count * source_count * output_count)


def extractor_case(input_bits: int, entropy_bits: int, output_bits: int) -> dict:
    """Exhaust all flat sources for one small affine-hash parameter set."""
    allowed = {(3, 2, 1), (4, 2, 1), (4, 3, 1)}
    if (input_bits, entropy_bits, output_bits) not in allowed:
        raise ValueError("case exceeds the frozen extractor domain")
    support = 1 << entropy_bits
    sources = combinations(range(1 << input_bits), support)
    maximum = Fraction(0)
    total = Fraction(0)
    witness: tuple[int, ...] | None = None
    count = 0
    for source in sources:
        distance = joint_distance_for_flat_source(source, input_bits, output_bits)
        total += distance
        count += 1
        if distance > maximum:
            maximum = distance
            witness = source
    assert count == comb(1 << input_bits, support)
    # Squared form of 1/2 sqrt(2^{m-k}), avoiding floating point.
    bound_squared = Fraction(1 << output_bits, 4 * (1 << entropy_bits))
    assert maximum * maximum <= bound_squared
    seed_count = 1 << (input_bits * output_bits + output_bits)
    return {
        "input_bits": input_bits,
        "entropy_bits": entropy_bits,
        "output_bits": output_bits,
        "flat_sources": count,
        "affine_seeds": seed_count,
        "source_seed_pairs": count * seed_count,
        "maximum_distance": rational(maximum),
        "mean_distance": rational(total / count),
        "lhl_bound_squared": rational(bound_squared),
        "maximum_distance_squared": rational(maximum * maximum),
        "witness_support": list(witness or ()),
    }


def xor_ratchet_case(retained_bits: int, session_bits: int, session_ids: int) -> dict:
    """Check that a uniform post-exposure pad gives exact conditional freshness."""
    if (retained_bits, session_bits, session_ids) not in {(2, 2, 3), (3, 2, 4)}:
        raise ValueError("case exceeds the frozen XOR-ratchet domain")
    output_bits = retained_bits + session_bits
    output_count = 1 << output_bits
    old_count = 1 << retained_bits
    joint = Counter()
    points = 0
    for old in range(old_count):
        for sid in range(session_ids):
            # Any public deterministic offset works; this one mixes old state
            # and the public session identifier without claiming cryptographic
            # strength.  Uniform new material one-time-pads the full output.
            offset = ((old * 5) ^ (sid * 3) ^ (old << session_bits)) & (output_count - 1)
            for fresh in range(output_count):
                out = fresh ^ offset
                joint[(old, sid, out)] += 1
                points += 1
    for old in range(old_count):
        for sid in range(session_ids):
            assert {joint[(old, sid, out)] for out in range(output_count)} == {1}
    return {
        "retained_bits": retained_bits,
        "session_bits": session_bits,
        "session_ids": session_ids,
        "old_states": old_count,
        "outputs_per_condition": output_count,
        "enumerated_points": points,
        "conditional_distance": "0/1",
        "old_state_fully_exposed": True,
    }


def entropy_budget_case(retained_bits: int, session_bits: int, observation_bits: int,
                        fresh_entropy_bits: int) -> dict:
    """One-step ideal-hybrid entropy ledger and leftover-hash error."""
    if not (0 <= observation_bits <= retained_bits and fresh_entropy_bits >= 0):
        raise ValueError("invalid entropy budget")
    output_bits = retained_bits + session_bits
    input_entropy = retained_bits - observation_bits + fresh_entropy_bits
    exponent = output_bits - input_entropy
    bound_squared = Fraction(2 ** exponent, 4) if exponent >= 0 else Fraction(1, 4 * (2 ** (-exponent)))
    # The configured cases have an even entropy slack, so the bound is rational.
    slack = input_entropy - output_bits
    if slack < 0 or slack % 2:
        bound = None
    else:
        bound = Fraction(1, 2 ** (slack // 2 + 1))
        assert bound * bound == bound_squared
    required_fresh_for_same_error = session_bits + observation_bits + max(slack, 0)
    return {
        "retained_bits": retained_bits,
        "session_bits": session_bits,
        "observation_support": 1 << observation_bits,
        "observation_bits": observation_bits,
        "fresh_entropy_bits": fresh_entropy_bits,
        "extractor_input_min_entropy": input_entropy,
        "extractor_output_bits": output_bits,
        "entropy_slack": slack,
        "distance_bound": rational(bound) if bound is not None else None,
        "distance_bound_squared": rational(bound_squared),
        "required_fresh_entropy_at_this_slack": required_fresh_for_same_error,
    }


def entropy_barrier_case(source_entropy_bits: int, output_bits: int) -> dict:
    """Support lower bound for any public-seeded deterministic extractor.

    For every fixed public seed, an output generated from a source supported on
    at most 2^k points has support at most 2^k.  Uniform mass outside that support
    gives TV distance at least 1-2^{k-m} when k < m.
    """
    if not (0 <= source_entropy_bits < output_bits <= 12):
        raise ValueError("require 0 <= k < m <= 12")
    lower = 1 - Fraction(1 << source_entropy_bits, 1 << output_bits)
    return {
        "source_entropy_bits": source_entropy_bits,
        "output_bits": output_bits,
        "maximum_output_support": 1 << source_entropy_bits,
        "uniform_domain_size": 1 << output_bits,
        "distance_lower_bound": rational(lower),
    }


def ratchet_loss_case(config: dict) -> dict:
    """Exact arithmetic for anchor, extractor, and leakage/soundness losses."""
    anchor = Fraction(config.get("anchor_failure", "0/1"))
    extractor = [Fraction(x) for x in config["extractor_errors"]]
    epsilon = [Fraction(x) for x in config["soundness_errors"]]
    leakage = [int(x) for x in config["leakage_bits"]]
    if not (len(extractor) == len(epsilon) == len(leakage)):
        raise ValueError("per-session arrays must have equal length")
    leakage_terms = [min(Fraction(1), (1 << ell) * eps)
                     for ell, eps in zip(leakage, epsilon)]
    per_session = [d + s for d, s in zip(extractor, leakage_terms)]
    total = min(Fraction(1), anchor + sum(per_session, Fraction(0)))
    return {
        "anchor_failure": rational(anchor),
        "extractor_errors": [rational(x) for x in extractor],
        "soundness_errors": [rational(x) for x in epsilon],
        "leakage_bits": leakage,
        "leakage_soundness_terms": [rational(x) for x in leakage_terms],
        "per_session_terms": [rational(x) for x in per_session],
        "total_upper_bound": rational(total),
    }


def all_ratchet_cases(config: dict) -> dict:
    return {
        "extractor": [extractor_case(**case) for case in config["extractor_cases"]],
        "xor_refresh": [xor_ratchet_case(**case) for case in config["xor_ratchet_cases"]],
        "entropy_budgets": [entropy_budget_case(**case) for case in config["entropy_budget_cases"]],
        "entropy_barriers": [entropy_barrier_case(**case) for case in config["entropy_barrier_cases"]],
        "lifetime_bounds": [ratchet_loss_case(case) for case in config["ratchet_loss_cases"]],
    }


def ratchet_negative_controls() -> list[dict]:
    """Analytic expected-value fixtures for four ratchet counterexamples."""
    rows = [
        {
            "name": "extract_more_uniform_bits_than_entropy",
            "actual": "1/2",
            "false_upper_bound": "0/1",
            "detected": True,
            "explanation": "A one-bit flat source mapped to two output bits misses at least half of the uniform domain for every public seed.",
        },
        {
            "name": "preloaded_randomness_is_post_exposure_fresh",
            "actual": "1/1",
            "false_upper_bound": "1/4",
            "detected": True,
            "explanation": "If a two-bit future source is already present when the snapshot is exposed, the restored execution reveals the future target exactly.",
        },
        {
            "name": "rollback_without_monotone_anchor",
            "actual": "1/1",
            "false_upper_bound": "1/4",
            "detected": True,
            "explanation": "Restoring a fully exposed two-bit retained state makes the next deterministic state known unless restoration is detected or new entropy is injected.",
        },
        {
            "name": "unchecked_domain_tag_blocks_replay",
            "actual": "1/1",
            "false_upper_bound": "1/2",
            "detected": True,
            "explanation": "A public label that is not included in the accepted relation does not prevent a transcript valid in one mode from being replayed in another.",
        },
    ]
    for row in rows:
        assert Fraction(row["actual"]) > Fraction(row["false_upper_bound"])
    return rows
