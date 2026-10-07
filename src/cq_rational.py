"""Separate exact rational enclosures for the owned real-symmetric qubit witness.

Does not alter the retained binary64 diagnostic, optimize entropy, or prove the
general quantum extractor theorem. All bounds are finite rational arithmetic.
"""
from fractions import Fraction
from itertools import product
from math import isqrt


def exact(value):
    if type(value) not in (int, Fraction):
        raise ValueError('rational or integer required; no float/bool conversion')
    return Fraction(value)


def check_sqrt(value, lower, upper):
    value, lower, upper = map(exact, (value, lower, upper))
    if not (0 <= lower <= upper and lower*lower <= value <= upper*upper):
        raise ValueError('invalid nonnegative square-root enclosure')
    return True


def sqrt_bounds(value, bits=64):
    value = exact(value)
    if value < 0 or type(bits) is not int or not 4 <= bits <= 256:
        raise ValueError('require nonnegative rational and 4..256 precision bits')
    denominator = 1 << bits
    numerator = isqrt((value.numerator << (2*bits)) // value.denominator)
    lower = Fraction(numerator, denominator)
    upper = lower if lower*lower == value else Fraction(numerator+1, denominator)
    check_sqrt(value, lower, upper)
    return lower, upper


def norm_bounds(matrix, bits=64):
    if len(matrix) != 4:
        raise ValueError('require a real symmetric 2x2 matrix')
    x,y,z,w = map(exact, matrix)
    if y != z:
        raise ValueError('matrix is not symmetric')
    radicand = (x-w)**2 + 4*y*y
    lower, upper = sqrt_bounds(radicand, bits)
    # Eigenvalues=(trace +/- radius)/2. For radius>=0,
    # (|trace+radius|+|trace-radius|)/2=max(|trace|,radius).
    trace = abs(x+w)
    return (max(trace,lower), max(trace,upper)), (radicand,lower,upper)


def compare_leq(left, right):
    """Prove only by separated endpoint inequalities; overlap is inconclusive."""
    left, right = tuple(map(exact,left)), tuple(map(exact,right))
    if len(left) != 2 or len(right) != 2 or left[0] > left[1] or right[0] > right[1]:
        raise ValueError('invalid intervals')
    if left[1] <= right[0]:
        return 'proved'
    if left[0] > right[1]:
        return 'disproved'
    return 'inconclusive'


def _add(left, right):
    return tuple(x+y for x,y in zip(left,right))


def _scale(matrix, weight):
    return tuple(weight*x for x in matrix)


def _witness(bits):
    F = Fraction
    blocks = ((F(1,2),F(0),F(0),F(0)), (F(1,4),)*4)
    marginal = _add(*blocks)
    certificates = []
    def norm(matrix):
        interval, certificate = norm_bounds(matrix,bits)
        certificates.append(certificate)
        return interval
    distance = (F(0),F(0))
    for a,b in product(range(2),repeat=2):
        bins = [(F(0),)*4, (F(0),)*4]
        for v in range(2):
            z = (a*v)^b
            bins[z] = _add(bins[z],blocks[v])
        for block in bins:
            interval = norm(_add(block,_scale(marginal,-F(1,2))))
            distance = tuple(x+y/8 for x,y in zip(distance,interval))
    mass, eta = F(15,16), F(1,4)
    output = ((1-mass)/2,)*2
    restoration = tuple(x/2 for x in norm(_scale(marginal,1-mass)))
    own = tuple(mass*x for x in distance)
    guessing = tuple((1+x)/2 for x in norm(_add(blocks[0],_scale(blocks[1],-1))))
    radius_intervals = []
    for value in guessing:
        radicand = 2*mass*value
        lower,upper = sqrt_bounds(radicand,bits)
        certificates.append((radicand,lower,upper))
        radius_intervals.append((lower,upper))
    hashing = (radius_intervals[0][0]/2, radius_intervals[1][1]/2)
    triangle = tuple(x+y+z for x,y,z in zip(output,own,restoration))
    def multiply(a,b):
        return (a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3],
                a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3])
    commutator = _add(multiply(blocks[0],blocks[1]),_scale(multiply(blocks[1],blocks[0]),-1))
    return dict(input_cq_blocks=blocks, witness_trace=mass, purified_distance=eta,
                purified_distance_squared=1-mass, generalized_trace_distance=1-mass,
                output_smoothing_distance=output, marginal_restoration_distance=restoration,
                actual_fixed_marginal_distance=distance, witness_own_marginal_distance=own,
                three_term_bound=triangle, witness_hash_bound=hashing,
                commutator_squared_hilbert_schmidt_norm=sum((x*x for x in commutator),F(0)),
                renormalized=False, sqrt_certificates=certificates)


def cq_smoothing_enclosure(initial_bits=16, max_bits=128):
    if (type(initial_bits) is not int or type(max_bits) is not int or
            not 4 <= initial_bits <= max_bits <= 256):
        raise ValueError('require 4 <= initial_bits <= max_bits <= 256')
    bits, attempts = initial_bits, []
    while True:
        result = _witness(bits)
        comparisons = dict(fixed_to_triangle=compare_leq(result['actual_fixed_marginal_distance'],result['three_term_bound']),
                           own_to_hash=compare_leq(result['witness_own_marginal_distance'],result['witness_hash_bound']))
        attempts.append(dict(bits=bits, comparisons=comparisons))
        if all(x == 'proved' for x in comparisons.values()) or bits == max_bits:
            return dict(**result, precision_bits=bits, attempts=attempts,
                        status='proved' if all(x == 'proved' for x in comparisons.values()) else 'inconclusive',
                        scope='Only the supplied finite cq witness, not quantum soundness or entropy optimization.')
        bits = min(2*bits,max_bits)
