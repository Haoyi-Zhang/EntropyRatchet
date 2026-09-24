"""Exact, small, entirely classical games. No cryptographic implementation.

The finite model consists only of integer secrets, Boolean predicates, XOR
shares and classical observations. General theorem proofs are separate.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import product
from typing import Iterable


def rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def posterior_success(joint: Counter[tuple[int, tuple[int, ...]]]) -> Fraction:
    """Optimal one-guess success from a joint *integer weight* table."""
    if not joint:
        raise ValueError("empty joint distribution")
    best: dict[tuple[int, ...], int] = defaultdict(int)
    for (secret, view), count in joint.items():
        if count <= 0:
            raise ValueError("weights must be strictly positive")
        best[view] = max(best[view], count)
    return Fraction(sum(best.values()), sum(joint.values()))


def tree_leaves(secret: int, tables: tuple[int, ...], depth: int) -> int:
    """Breadth-first, depth-complete binary tree of arbitrary predicates.

    Predicate t maps secret s to bit (t >> s) & 1. The observed leaf is the
    response bitstring, encoded as a depth-bit integer.
    """
    node = 0
    leaf = 0
    for _ in range(depth):
        bit = (tables[node] >> secret) & 1
        leaf = 2 * leaf + bit
        node = 2 * node + 1 + bit
    return leaf


def tree_case(bits: int, depth: int) -> dict:
    if (bits, depth) not in {(1,0),(1,1),(1,2),(2,0),(2,1),(2,2),(3,0),(3,1)}:
        raise ValueError("case exceeds the frozen finite enumeration domain")
    size = 1 << bits
    nodes = (1 << depth) - 1
    tables_range = range(1 << size)
    maximum = Fraction(0)
    ratio_maximum = Fraction(0)
    checks = 0
    histogram: Counter[str] = Counter()
    for tables in product(tables_range, repeat=nodes):
        cells: dict[int, list[int]] = defaultdict(list)
        for secret in range(size):
            cells[tree_leaves(secret, tables, depth)].append(secret)
        # The optimal real adversary picks one member of each nonempty cell.
        real = Fraction(len(cells), size)
        representatives = {leaf: min(cell) for leaf, cell in cells.items()}
        # Guessed-response experiment: every leaf, not only reachable leaves,
        # receives uniform weight. Empty leaves use a fixed valid response.
        successes = 0
        for secret in range(size):
            for guessed in range(1 << depth):
                response = representatives.get(guessed, 0)
                successes += int(response == secret)
        guessed_success = Fraction(successes, size * (1 << depth))
        assert guessed_success == Fraction(1, size)
        assert real <= min(Fraction(1), (1 << depth) * guessed_success)
        maximum = max(maximum, real)
        ratio_maximum = max(ratio_maximum, real / guessed_success)
        histogram[rational(real)] += 1
        checks += 1
    return {'bits':bits, 'depth':depth, 'trees':checks,
            'max_real_success':rational(maximum),
            'guessed_response_success':rational(Fraction(1,size)),
            'max_ratio':rational(ratio_maximum),
            'histogram':dict(sorted(histogram.items()))}



@lru_cache(maxsize=None)
def _public_framing_shapes(max_depth: int) -> tuple[object, ...]:
    """All ordered pruned binary response-tree shapes of depth at most max_depth.

    ``None`` is a terminal transcript and ``(left,right)`` is one publicly
    framed binary response followed by the indicated continuation.
    """
    if max_depth < 0:
        raise ValueError("max_depth must be nonnegative")
    if max_depth == 0:
        return (None,)
    smaller = _public_framing_shapes(max_depth - 1)
    return (None,) + tuple((left, right) for left in smaller for right in smaller)


def _public_leaf_paths(tree: object, prefix: tuple[int, ...] = ()) -> tuple[tuple[int, ...], ...]:
    if tree is None:
        return (prefix,)
    left, right = tree
    return (_public_leaf_paths(left, prefix + (0,))
            + _public_leaf_paths(right, prefix + (1,)))


def _public_leaf_count(tree: object) -> int:
    if tree is None:
        return 1
    left, right = tree
    return _public_leaf_count(left) + _public_leaf_count(right)


def _public_tree_height(tree: object) -> int:
    if tree is None:
        return 0
    left, right = tree
    return 1 + max(_public_tree_height(left), _public_tree_height(right))


def _leaf_uniform_probability(tree: object, path: tuple[int, ...]) -> Fraction:
    """Causal leaf-count sampler probability for one declared public path."""
    node = tree
    probability = Fraction(1)
    for bit in path:
        if node is None:
            raise ValueError("path continues past a terminal transcript")
        left, right = node
        left_count = _public_leaf_count(left)
        right_count = _public_leaf_count(right)
        parent_count = left_count + right_count
        child = left if bit == 0 else right
        child_count = left_count if bit == 0 else right_count
        probability *= Fraction(child_count, parent_count)
        node = child
    if node is not None:
        raise ValueError("path stops before a terminal transcript")
    return probability


def public_framing_case(max_depth: int) -> dict:
    """Exhaust public pruned binary framing trees and two causal samplers.

    The local-uniform sampler pays ``2**height`` on a deepest path.  When the
    complete public framing tree and continuation leaf counts are efficiently
    available, sampling a child proportionally to its number of leaves makes
    every terminal transcript have probability exactly ``1/N``.
    """
    if max_depth != 4:
        raise ValueError("only the frozen depth-four public framing domain is authorized")
    shapes = _public_framing_shapes(max_depth)
    total_leaf_paths = 0
    strict = 0
    equal = 0
    maximum_ratio = Fraction(0)
    maximum_local = 0
    maximum_leaf = 0
    checks = 0
    for tree in shapes:
        leaves = _public_leaf_paths(tree)
        leaf_count = len(leaves)
        assert leaf_count == _public_leaf_count(tree)
        height = _public_tree_height(tree)
        local_factor = 1 << height
        leaf_factor = leaf_count
        assert leaf_factor <= local_factor
        strict += int(leaf_factor < local_factor)
        equal += int(leaf_factor == local_factor)
        maximum_ratio = max(maximum_ratio, Fraction(local_factor, leaf_factor))
        maximum_local = max(maximum_local, local_factor)
        maximum_leaf = max(maximum_leaf, leaf_factor)
        for path in leaves:
            assert _leaf_uniform_probability(tree, path) == Fraction(1, leaf_count)
            checks += 1
        total_leaf_paths += leaf_count
    assert len(shapes) == 677
    assert strict + equal == len(shapes)
    return {
        'max_depth': max_depth,
        'public_tree_shapes': len(shapes),
        'terminal_transcript_paths': total_leaf_paths,
        'leaf_uniform_probability_checks': checks,
        'leaf_uniform_failures': 0,
        'strict_improvement_trees': strict,
        'equal_factor_trees': equal,
        'maximum_local_uniform_factor': maximum_local,
        'maximum_leaf_uniform_factor': maximum_leaf,
        'maximum_local_over_leaf_ratio': rational(maximum_ratio),
    }

def shares_case(bits: int, epochs: int, fresh: bool) -> dict:
    allowed={(1,1),(1,2),(1,3),(2,1),(2,2),(3,2)}
    if (bits, epochs) not in allowed:
        raise ValueError("case exceeds the frozen finite enumeration domain")
    size=1 << bits
    nodes=sum(size**j for j in range(epochs))
    policy_count=1 << nodes
    max_success=Fraction(0)
    independent=0
    points_per_policy=size**(epochs+1) if fresh else size**2
    for policy in range(policy_count):
        joint: Counter[tuple[int,tuple[int,...]]] = Counter()
        masks_iter=product(range(size), repeat=epochs if fresh else 1)
        # Materializing the masks is bounded by 8**2 here.
        masks_list=list(masks_iter)
        for secret in range(size):
            for mask_items in masks_list:
                masks=mask_items if fresh else mask_items*epochs
                view=[]
                offset=0
                prefix=0
                for t,mask in enumerate(masks):
                    choose_right=(policy >> (offset+prefix)) & 1
                    value=(secret ^ mask) if choose_right else mask
                    view.append(value)
                    offset+=size**t
                    prefix=prefix*size+value
                joint[(secret,tuple(view))]+=1
        assert sum(joint.values())==points_per_policy
        distributions=[{v:c for (s,v),c in joint.items() if s==secret}
                       for secret in range(size)]
        is_independent=all(d==distributions[0] for d in distributions[1:])
        independent+=int(is_independent)
        score=posterior_success(joint)
        if fresh:
            assert is_independent
            assert score==Fraction(1,size)
        max_success=max(max_success,score)
    return {'bits':bits,'epochs':epochs,'fresh_masks':fresh,
            'policies':policy_count,'points_per_policy':points_per_policy,
            'independent_policies':independent,
            'max_guess_success':rational(max_success)}


def prefix_cases(max_bits: int) -> list[dict]:
    if not 1 <= max_bits <= 10:
        raise ValueError("prefix cap must be between 1 and 10")
    out=[]
    for bits in range(1,max_bits+1):
        size=1<<bits
        for queries in range(bits+3):
            joint: Counter[tuple[int,tuple[int,...]]]=Counter()
            for secret in range(size):
                # Sequential coordinates of the persistent secret. Later queries
                # are redundant; they do not create new secret coordinates.
                view=tuple((secret>>j)&1 for j in range(min(queries,bits)))
                joint[(secret,view)]+=1
            score=posterior_success(joint)
            expected=Fraction(1,1<<max(bits-queries,0))
            assert score==expected
            out.append({'bits':bits,'queries':queries,'guess_success':rational(score)})
    return out


def mask_identity_count(max_bits: int) -> int:
    if not 1 <= max_bits <= 6:
        raise ValueError("mask identity cap must be between 1 and 6")
    count=0
    for bits in range(1,max_bits+1):
        for secret in range(1<<bits):
            for mask in range(1<<bits):
                assert mask ^ (mask ^ secret)==secret
                count+=1
    return count


def negative_controls() -> list[dict]:
    """Witnesses falsify *specified bad inferences*, not deployed protocols."""
    out=[]
    def add(name: str, actual: Fraction, false_upper: Fraction, explanation: str):
        assert actual>false_upper
        out.append({'name':name,'actual':rational(actual),
                    'false_upper_bound':rational(false_upper),
                    'detected':True,'explanation':explanation})
    # Same secret: two old epochs each disclose a different coordinate.
    joint=Counter((s,((s>>0)&1,(s>>1)&1)) for s in range(4))
    add('reset_budget_after_representation_refresh',posterior_success(joint),Fraction(1,2),
        'Two one-bit queries about the same two-bit secret reveal it; a one-bit per-lifetime calculation is invalid.')
    # One share before a restart, the other after restoring the same mask.
    joint=Counter((s,(r,r^s)) for s in range(4) for r in range(4))
    add('restored_mask_is_not_fresh',posterior_success(joint),Fraction(1,4),
        'Left and right shares from the same restored encoding reconstruct the secret.')
    add('whole_state_query_is_not_one_share_query',posterior_success(Counter((s,(r^(r^s),)) for s in range(4) for r in range(4))),Fraction(1,4),
        'A whole-state leakage circuit can combine both shares.')
    # At most one payload bit, but three distinguishable framed responses.
    labels=('', '0', '1', '1')
    joint=Counter((s,(labels[s],)) for s in range(4))
    add('secret_dependent_length_is_free',posterior_success(joint),Fraction(1,2),
        'Empty, zero and one are three framed symbols; payload-length accounting misses termination information.')
    hidden=Counter((s,()) for s in range(2))
    revealed=Counter((s,(s,)) for s in range(2))
    hidden_advantage=posterior_success(hidden)-Fraction(1,2)
    revealed_advantage=posterior_success(revealed)-Fraction(1,2)
    add('multiply_distinguishing_advantage',revealed_advantage,2*hidden_advantage,
        'A hidden fair bit has prediction advantage zero before leakage and one half after the bit itself is leaked.')
    standalone=max(Fraction(sum(a==s for s in range(4)),4) for a in range(4))
    # The first true statement returns s. The response in the next, false,
    # statement is that returned transcript value.
    reused=Fraction(sum((lambda true_transcript: true_transcript==s)(s)
                        for s in range(4)),4)
    add('one_shot_soundness_implies_reuse',reused,2*standalone,
        'A true-session transcript can disclose a two-bit verifier secret; the next false session succeeds, despite standalone error one quarter.')
    add('public_tags_restore_secret_entropy',posterior_success(Counter((s,(s,123)) for s in range(4))),Fraction(1,4),
        'Appending a public domain tag to a known secret does not make the secret unpredictable.')
    add('per_state_support_is_not_public_guessability',
        posterior_success(Counter((s,(s,)) for s in range(4))), Fraction(1,4),
        'Each fixed secret produces a singleton transcript, but the public range has four values; per-state support one is not a public causal guessing factor.')
    return out


def fresh_rekey_case() -> dict:
    joint=Counter((new,(old,)) for old in range(4) for new in range(4))
    probability=posterior_success(joint)
    assert probability==Fraction(1,4)
    return {'old_bits':2,'new_bits':2,'old_secret_fully_exposed':True,
            'independent_new_secret_success':rational(probability),
            'joint_points':sum(joint.values())}


def future_target_case(bits: int = 2, steps: int = 2) -> dict:
    """All two-step deterministic updates on a two-bit state, known before leakage.

    Each map is a packed table with two bits for each of its four inputs.
    At epoch zero leak target bit 0; at epoch one leak target bit 1.
    The target is the final state, not necessarily the initial state.
    """
    if (bits,steps)!=(2,2):
        raise ValueError("only the frozen two-bit two-update domain is authorized")
    n=1<<bits
    paths=0;recovered=0;changed=0
    for first in range(n**n):
        for second in range(n**n):
            for initial in range(n):
                middle=(first>>(bits*initial))&(n-1)
                target=(second>>(bits*middle))&(n-1)
                # The earlier leakage circuit composes both public updates.
                early_prediction=(second>>(bits*((first>>(bits*initial))&(n-1))))&(n-1)
                later_prediction=(second>>(bits*middle))&(n-1)
                early_bit=early_prediction&1
                later_bit=(later_prediction>>1)&1
                guess=early_bit|(later_bit<<1)
                paths+=1;recovered+=int(guess==target)
                changed+=int(target!=initial)
    assert recovered==paths
    return {'bits':bits,'steps':steps,'maps_per_step':n**n,
      'update_sequences':(n**n)**steps,'state_paths':paths,
      'reconstructed_paths':recovered,'target_differs_from_initial_paths':changed,
      'success':'1/1','future_updates_known_before_first_leakage':True}
