"""Diagnostics for the fixed-actual-marginal extractor interface.

The general smooth quantum statement is proved in the manuscript and
proofs/fixed-marginal-extraction.md.  These routines do NOT prove it.  Rational
classical diagnostics and a two-dimensional noncommuting cq witness detect
convention drift; the latter's spectral norms use floating point, labelled as
such.  No entropy optimization over arbitrary quantum states is performed.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction
from itertools import product
from math import sqrt


def rational(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def tv(left: list[Fraction], right: list[Fraction]) -> Fraction:
    if len(left) != len(right):
        raise ValueError('distributions have different dimensions')
    return sum((abs(x-y) for x,y in zip(left,right)), Fraction(0))/2


def budget_case(output_bits: int, min_entropy_bits: int, smoothing: str) -> dict:
    eta = Fraction(smoothing)
    if not (0 <= eta < 1 and 0 <= output_bits <= min_entropy_bits):
        raise ValueError('invalid contract budget')
    slack = min_entropy_bits - output_bits
    if slack % 2:
        raise ValueError('rational diagnostic requires even entropy slack')
    hashing = Fraction(1, 2 ** (1 + slack//2))
    return {'output_bits':output_bits, 'min_entropy_bits':min_entropy_bits,
            'smoothing':rational(eta), 'hashing_term':rational(hashing),
            'output_smoothing_cost':rational(eta),
            'marginal_restoration_cost':rational(eta),
            'fixed_marginal_bound':rational(2*eta+hashing),
            'single_eta_with_same_marginal_witness':True}


def optimized_marginal_diagnostic() -> dict:
    # Rows index a binary side-information register; columns a four-value K.
    p = [Fraction(x,8) for x in (0,0,0,1,1,2,2,2)]
    b0=sum(p[:4]); b1=sum(p[4:])
    fixed=tv(p,[b0/4]*4+[b1/4]*4)
    # Convex piecewise-linear minimization: an optimum is at a breakpoint.
    points={Fraction(0),Fraction(1)}
    points.update(4*x for x in p[:4])
    points.update(1-4*x for x in p[4:])
    candidates=[(tv(p,[a/4]*4+[(1-a)/4]*4),a)
                for a in points if 0<=a<=1]
    optimized,alpha=min(candidates)
    assert optimized < fixed <= 2*optimized
    return {'joint_mass':[rational(x) for x in p],
            'actual_side_marginal':[rational(b0),rational(b1)],
            'optimizing_side_marginal':[rational(alpha),rational(1-alpha)],
            'fixed_distance':rational(fixed),'optimized_distance':rational(optimized),
            'same_distance_inference_rejected':fixed!=optimized,
            'scope':'classical distance-definition diagnostic, not a hash counterexample'}


def _add(a: tuple, b: tuple) -> tuple:
    return tuple(x+y for x,y in zip(a,b))


def _scale(a: tuple, x) -> tuple:
    return tuple(x*y for y in a)


def _norm(a: tuple) -> float:
    """Trace norm of a real symmetric 2x2 matrix, from its two eigenvalues."""
    x,y,z,w=a
    if y != z:
        raise ValueError('matrix is not symmetric')
    discriminant=(x-w)**2+4*y*y
    radius=sqrt(float(discriminant))
    trace=float(x+w)
    return (abs(trace+radius)+abs(trace-radius))/2


def cq_smoothing_diagnostic() -> dict:
    F=Fraction
    blocks=[(F(1,2),F(0),F(0),F(0)),(F(1,4),)*4]
    marginal=_add(*blocks)
    zero=(F(0),)*4
    distance=0.0
    for a,b in product(range(2),repeat=2):
        bins=[zero,zero]
        for v in range(2):
            z=(a*v)^b
            bins[z]=_add(bins[z],blocks[v])
        distance += sum(_norm(_add(z,_scale(marginal,-F(1,2)))) for z in bins)/8
    # This witness is subnormalized, not divided by its trace.
    mass=F(15,16)
    eta=F(1,4)
    left=float(1-mass)/2
    right=_norm(_scale(marginal,1-mass))/2
    smoothed_own=float(mass)*distance
    p_guess=(1+_norm(_add(blocks[0],_scale(blocks[1],-1))))/2
    remainder=sqrt(2*float(mass)*p_guess)/2
    triangle=left+smoothed_own+right
    assert eta*eta == 1-mass
    assert abs(left-right)<1e-14
    assert distance <= triangle+1e-13
    assert smoothed_own <= remainder+1e-13
    # Compute the commutator from the actual input blocks.
    def multiply(a, b):
        return (a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3],
                a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3])
    commutator=_add(multiply(blocks[0],blocks[1]),
                    _scale(multiply(blocks[1],blocks[0]),-1))
    commutator_squared=sum((x*x for x in commutator),F(0))
    return {'input_cq_blocks':[[rational(x) for x in row] for row in blocks],
            'arithmetic':'rational inputs; 2x2 spectral norms evaluated in binary64',
            'tolerance':1e-12,'witness_trace':rational(mass),
            'purified_distance':rational(eta),
            'purified_distance_squared':rational(1-mass),
            'generalized_trace_distance':rational(1-mass),
            'output_smoothing_distance':left,'marginal_restoration_distance':right,
            'actual_fixed_marginal_distance':distance,
            'witness_own_marginal_distance':smoothed_own,
            'three_term_bound':triangle,
            'witness_hash_bound':remainder,
            'commutator_squared_hilbert_schmidt_norm':rational(commutator_squared),
            'renormalized':False,
            'scope':'one explicit noncommuting cq witness with eta>0; not a general quantum proof'}


def xor_independence_controls() -> dict:
    correlated=Counter()
    independent=Counter()
    for c,u in product(range(2),repeat=2):
        x=2*u+c
        correlated[(c,x^c)]+=1
    for c,x in product(range(2),range(4)):
        independent[(c,x^c)]+=1
    def dist(table):
        n=sum(table.values())
        return sum((abs(Fraction(table[(c,y)],n)-Fraction(1,8))
                    for c in range(2) for y in range(4)),Fraction(0))/2
    return {'correlated_source_points':sum(correlated.values()),
            'correlated_source_joint_distance':rational(dist(correlated)),
            'independent_source_points':sum(independent.values()),
            'independent_source_joint_distance':rational(dist(independent)),
            'violated_condition':'rho_XCB = tau_X tensor rho_CB',
            'correlated_output_support':sorted({y for c,y in correlated})}


def retired_input_recomputation() -> dict:
    # Input = 1 old bit || 2 fresh bits; 2 output bits.
    points=mismatches=0
    image_sizes=Counter(); outputs=Counter()
    for row0,row1,offset in product(range(8),range(8),range(4)):
        image=set()
        for old,fresh in product(range(2),range(4)):
            inp=(old<<2)|fresh
            out=((row0&inp).bit_count()%2) | (((row1&inp).bit_count()%2)<<1)
            out ^= offset
            image.add(out); outputs[out]+=1
            # Reconstruct from the disclosed bytes and public seed.
            recovered_bits=[old,(fresh>>1)&1,fresh&1]
            recovered=0
            for bit,row in enumerate((row0,row1)):
                dot=sum(((row>>(2-i))&1)*v for i,v in enumerate(recovered_bits))%2
                recovered |= dot<<bit
            recovered ^= offset
            points += 1
            mismatches += out!=recovered
        image_sizes[len(image)]+=1
    assert mismatches==0
    return {'old_bits':1,'fresh_bits':2,'output_bits':2,
            'public_seeds':256,'inputs_per_seed':8,'recomputed_points':points,
            'mismatches':mismatches,
            'image_size_histogram':{str(k):v for k,v in sorted(image_sizes.items())},
            'output_histogram':{str(k):v for k,v in sorted(outputs.items())},
            'scope':'public recomputation from disclosed retired input; no physical-erasure measurement'}


def contract_checks(configs: list[dict]) -> dict:
    return {'contract':'subnormalized purified-distance smoothing; normalized actual states; fixed actual marginal; 2 eta',
            'budgets':[budget_case(**cfg) for cfg in configs],
            'optimized_marginal':optimized_marginal_diagnostic(),
            'nonzero_smoothing_cq':cq_smoothing_diagnostic(),
            'xor_controls':xor_independence_controls(),
            'retired_input':retired_input_recomputation()}
