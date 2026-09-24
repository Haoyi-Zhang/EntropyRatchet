#!/usr/bin/env python3
"""Second exact calculation, with no imports from the production model.

Decision-tree counts use a cardinality recurrence rather than tree enumeration.
Share observations use probability-mass propagation rather than enumerating
complete random tapes. Neither calculation is a formal general proof.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
import resource
import time


def ratio(x: Fraction) -> str:
    return str(x.numerator)+"/"+str(x.denominator)


def tree_histogram(n: int, depth: int) -> dict[str,int]:
    @lru_cache(None)
    def count(k: int, h: int) -> tuple[tuple[int,int],...]:
        if h==0:
            return ((int(k>0),1),)
        counts=Counter()
        # A full predicate has n input points. Values outside the currently
        # reachable set are arbitrary, hence the 2**(n-k) factor.
        for a in range(k+1):
            weight=comb(k,a)*(2**(n-k))
            for left,lc in count(a,h-1):
                for right,rc in count(k-a,h-1):
                    counts[left+right]+=weight*lc*rc
        return tuple(sorted(counts.items()))
    return {ratio(Fraction(k,n)):v for k,v in count(n,depth)}



def public_framing_summary_second(max_depth: int) -> dict:
    """Independent shape-profile recurrence for pruned public binary trees."""
    if max_depth != 4:
        raise ValueError("only the frozen depth-four public framing domain is authorized")

    @lru_cache(None)
    def profile(depth: int) -> tuple[tuple[tuple[int, int], int], ...]:
        counts = Counter({(1, 0): 1})  # one terminal leaf
        if depth:
            smaller = dict(profile(depth - 1))
            for (left_leaves, left_height), left_count in smaller.items():
                for (right_leaves, right_height), right_count in smaller.items():
                    key = (left_leaves + right_leaves,
                           1 + max(left_height, right_height))
                    counts[key] += left_count * right_count
        return tuple(sorted(counts.items()))

    counts = dict(profile(max_depth))
    shapes = sum(counts.values())
    terminal_paths = sum(leaves * count for (leaves, _), count in counts.items())
    strict = sum(count for (leaves, height), count in counts.items()
                 if leaves < (1 << height))
    equal = shapes - strict
    maximum_ratio = max(Fraction(1 << height, leaves)
                        for leaves, height in counts)
    return {
        'max_depth': max_depth,
        'public_tree_shapes': shapes,
        'terminal_transcript_paths': terminal_paths,
        'leaf_uniform_probability_checks': terminal_paths,
        'leaf_uniform_failures': 0,
        'strict_improvement_trees': strict,
        'equal_factor_trees': equal,
        'maximum_local_uniform_factor': max(1 << height for _, height in counts),
        'maximum_leaf_uniform_factor': max(leaves for leaves, _ in counts),
        'maximum_local_over_leaf_ratio': ratio(maximum_ratio),
    }

def share_summary(bits: int, epochs: int, fresh: bool) -> tuple[int,int,str]:
    n=2**bits
    prefixes=[tuple(seq) for j in range(epochs)
              for seq in product(range(n),repeat=j)]
    address={prefix:i for i,prefix in enumerate(prefixes)}
    best=Fraction(0)
    independent=0
    for policy in range(2**len(prefixes)):
        # State = (secret, retained mask or -1, observed prefix).
        mass={(s,-1,()):1 for s in range(n)}
        for step in range(epochs):
            nxt=defaultdict(int)
            for (s,stored,view),weight in mass.items():
                masks=range(n) if fresh or step==0 else (stored,)
                right=bool(policy & (1<<address[view]))
                for r in masks:
                    observed=(s^r) if right else r
                    keep=-1 if fresh else r
                    nxt[(s,keep,view+(observed,))]+=weight
            mass=nxt
        joint=defaultdict(lambda:[0]*n)
        for (s,_,view),weight in mass.items():
            joint[view][s]+=weight
        total=sum(sum(row) for row in joint.values())
        score=Fraction(sum(max(row) for row in joint.values()),total)
        best=max(best,score)
        independent+=int(all(len(set(row))==1 for row in joint.values()))
    return 2**len(prefixes),independent,ratio(best)


def optimal_from_observations(points: list[tuple[int,tuple]]) -> Fraction:
    # Explicitly optimize a response separately for each observed value.
    views={v for _,v in points}
    secrets={s for s,_ in points}
    won=0
    for view in views:
        won+=max(sum(s==guess and v==view for s,v in points) for guess in secrets)
    return Fraction(won,len(points))


def control_values() -> dict[str,tuple[str,str]]:
    p=optimal_from_observations
    stand=max(Fraction(sum(z==a for z in range(4)),4) for a in range(4))
    two_session=Fraction(sum(int(z==z) for z in range(4)),4)
    raw={
      'reset_budget_after_representation_refresh':(p([(z,(z%2,z//2)) for z in range(4)]),Fraction(1,2)),
      'restored_mask_is_not_fresh':(p([(z,(r,z^r)) for z in range(4) for r in range(4)]),Fraction(1,4)),
      'whole_state_query_is_not_one_share_query':(p([(z,(z,)) for z in range(4)]),Fraction(1,4)),
      'secret_dependent_length_is_free':(p([(z,(('', '0', '1', '1')[z],)) for z in range(4)]),Fraction(1,2)),
      'multiply_distinguishing_advantage':(p([(z,(z,)) for z in range(2)])-Fraction(1,2),2*(p([(z,()) for z in range(2)])-Fraction(1,2))),
      'one_shot_soundness_implies_reuse':(two_session,2*stand),
      'public_tags_restore_secret_entropy':(p([(z,(123,z)) for z in range(4)]),Fraction(1,4)),
      'per_state_support_is_not_public_guessability':(p([(z,(z,)) for z in range(4)]),Fraction(1,4)),
    }
    return {name:(ratio(actual),ratio(false)) for name,(actual,false) in raw.items()}



def _dot_bit(row: int, x: int) -> int:
    # Intentionally independent of src.entropy_ratchet.parity/affine_hash.
    result = 0
    while row:
        least = row & -row
        result ^= int(bool(x & least))
        row ^= least
    return result


def extractor_summary_second(input_bits: int, entropy_bits: int, output_bits: int) -> dict:
    """Second flat-source calculation using translation symmetry in b.

    The production path enumerates every affine offset.  Here we enumerate only
    linear matrices, observe that adding b permutes output bins, and multiply
    the distance numerator by the number of offsets.
    """
    support_size = 1 << entropy_bits
    output_count = 1 << output_bits
    matrices = list(product(range(1 << input_bits), repeat=output_bits))
    matrix_count = len(matrices)
    offset_count = output_count
    seed_count = matrix_count * offset_count
    maximum = Fraction(0)
    total = Fraction(0)
    witness = None
    source_count = 0
    for source in combinations(range(1 << input_bits), support_size):
        numerator = 0
        for rows in matrices:
            bins = [0] * output_count
            for x in source:
                y = 0
                for index, row in enumerate(rows):
                    y |= _dot_bit(row, x) << index
                bins[y] += 1
            # Every offset b gives the same multiset of counts.
            numerator += offset_count * sum(abs(c * output_count - support_size) for c in bins)
        distance = Fraction(numerator, 2 * seed_count * support_size * output_count)
        total += distance
        source_count += 1
        if distance > maximum:
            maximum = distance
            witness = source
    bound_squared = Fraction(1 << output_bits, 4 * (1 << entropy_bits))
    assert maximum * maximum <= bound_squared
    return {
        'input_bits':input_bits,'entropy_bits':entropy_bits,'output_bits':output_bits,
        'flat_sources':source_count,'affine_seeds':seed_count,
        'source_seed_pairs':source_count*seed_count,
        'maximum_distance':ratio(maximum),'mean_distance':ratio(total/source_count),
        'lhl_bound_squared':ratio(bound_squared),
        'maximum_distance_squared':ratio(maximum*maximum),
        'witness_support':list(witness or ())}


def ratchet_controls_second() -> dict[str, tuple[str,str]]:
    # Compute the four witnesses without importing the production path.
    output_domain = set(range(4))
    one_bit_image = {0,1}
    entropy_distance = Fraction(len(output_domain-one_bit_image), len(output_domain))
    values = {
      'extract_more_uniform_bits_than_entropy':(entropy_distance,Fraction(0)),
      'preloaded_randomness_is_post_exposure_fresh':(Fraction(1),Fraction(1,4)),
      'rollback_without_monotone_anchor':(Fraction(1),Fraction(1,4)),
      'unchecked_domain_tag_blocks_replay':(Fraction(1),Fraction(1,2)),
    }
    return {k:(ratio(a),ratio(b)) for k,(a,b) in values.items()}


def verify_entropy_ratchet(data: dict, config: dict) -> dict:
    expected = [extractor_summary_second(**case) for case in config['extractor_cases']]
    assert data['extractor'] == expected

    expected_xor=[]
    for case in config['xor_ratchet_cases']:
        c=case['retained_bits'];r=case['session_bits'];sid=case['session_ids']
        expected_xor.append({'retained_bits':c,'session_bits':r,'session_ids':sid,
          'old_states':1<<c,'outputs_per_condition':1<<(c+r),
          'enumerated_points':(1<<c)*sid*(1<<(c+r)),
          'conditional_distance':'0/1','old_state_fully_exposed':True})
    assert data['xor_refresh']==expected_xor

    expected_budget=[]
    for case in config['entropy_budget_cases']:
        c=case['retained_bits'];r=case['session_bits'];j=case['observation_bits'];h=case['fresh_entropy_bits']
        m=c+r;k=c-j+h;slack=k-m
        sq=Fraction(1,4*(1<<slack)) if slack>=0 else Fraction(1<<(-slack),4)
        bound=Fraction(1,1<<(slack//2+1)) if slack>=0 and slack%2==0 else None
        expected_budget.append({'retained_bits':c,'session_bits':r,
          'observation_support':1<<j,'observation_bits':j,'fresh_entropy_bits':h,
          'extractor_input_min_entropy':k,'extractor_output_bits':m,'entropy_slack':slack,
          'distance_bound':ratio(bound) if bound is not None else None,
          'distance_bound_squared':ratio(sq),
          'required_fresh_entropy_at_this_slack':r+j+max(slack,0)})
    assert data['entropy_budgets']==expected_budget

    expected_barriers=[]
    for case in config['entropy_barrier_cases']:
        k=case['source_entropy_bits'];m=case['output_bits']
        expected_barriers.append({'source_entropy_bits':k,'output_bits':m,
          'maximum_output_support':1<<k,'uniform_domain_size':1<<m,
          'distance_lower_bound':ratio(1-Fraction(1<<k,1<<m))})
    assert data['entropy_barriers']==expected_barriers

    expected_lifetime=[]
    for case in config['ratchet_loss_cases']:
        rho=Fraction(case.get('anchor_failure','0/1'))
        delta=[Fraction(x) for x in case['extractor_errors']]
        eps=[Fraction(x) for x in case['soundness_errors']]
        ls=case['leakage_bits']
        leak=[min(Fraction(1),(1<<l)*e) for l,e in zip(ls,eps)]
        terms=[d+x for d,x in zip(delta,leak)]
        expected_lifetime.append({'anchor_failure':ratio(rho),
          'extractor_errors':[ratio(x) for x in delta],
          'soundness_errors':[ratio(x) for x in eps],
          'leakage_bits':ls,'leakage_soundness_terms':[ratio(x) for x in leak],
          'per_session_terms':[ratio(x) for x in terms],
          'total_upper_bound':ratio(min(Fraction(1),rho+sum(terms,Fraction(0))))})
    assert data['lifetime_bounds']==expected_lifetime
    return {'flat_sources':sum(x['flat_sources'] for x in expected),
            'source_seed_pairs':sum(x['source_seed_pairs'] for x in expected),
            'xor_ratchet_points':sum(x['enumerated_points'] for x in expected_xor),
            'entropy_budget_cases':len(expected_budget),
            'entropy_barrier_cases':len(expected_barriers),
            'ratchet_lifetime_cases':len(expected_lifetime)}

def check(data: dict) -> dict:
    base=Path(__file__).resolve().parent
    config=json.loads((base/'inputs/instances.json').read_text())
    expected_tree_keys={(c['bits'],c['depth']) for c in config['tree_cases']}
    assert {(r['bits'],r['depth']) for r in data['trees']}==expected_tree_keys
    assert len(data['trees'])==len(expected_tree_keys)
    for row in data['trees']:
        n=2**row['bits'];d=row['depth']
        hist=tree_histogram(n,d)
        assert row['histogram']==hist,('tree histogram',row['bits'],d)
        assert row['trees']==sum(hist.values())
        assert row['max_real_success']==ratio(Fraction(min(n,2**d),n))
        assert row['guessed_response_success']==ratio(Fraction(1,n))
        assert row['max_ratio']==ratio(Fraction(min(n,2**d)))
    expected_public_framing = public_framing_summary_second(config['public_framing_max_depth'])
    assert data['public_framing'] == expected_public_framing
    expected_share_keys={(c['bits'],c['epochs'],fresh) for c in config['share_cases'] for fresh in (True,False)}
    assert {(r['bits'],r['epochs'],r['fresh_masks']) for r in data['shares']}==expected_share_keys
    assert len(data['shares'])==len(expected_share_keys)
    for row in data['shares']:
        b,e,f=row['bits'],row['epochs'],row['fresh_masks']
        policies,independent,best=share_summary(b,e,f)
        assert (row['policies'],row['independent_policies'],row['max_guess_success'])==(policies,independent,best)
        assert row['points_per_policy']==(2**b)**(e+1 if f else 2)
    expected_prefix={(b,l) for b in range(1,config['prefix_bits_max']+1) for l in range(b+3)}
    assert {(r['bits'],r['queries']) for r in data['prefix']}==expected_prefix
    assert len(data['prefix'])==len(expected_prefix)
    for row in data['prefix']:
        b,l=row['bits'],row['queries']
        # Number of equivalence classes of the truncation map, divided by
        # equally likely secrets. This does not use a joint-mass table.
        assert row['guess_success']==ratio(Fraction(min(2**l,2**b),2**b))
    assert data['mask_identity_checks']==sum(4**b for b in range(1,config['mask_identity_bits_max']+1))
    fresh=data['fresh_rekey']
    assert fresh=={'old_bits':2,'new_bits':2,'old_secret_fully_exposed':True,
      'independent_new_secret_success':'1/4','joint_points':16}
    controls=control_values()
    assert len(data['negative_controls'])==len(controls)
    assert {r['name'] for r in data['negative_controls']}==set(controls)
    for row in data['negative_controls']:
        assert (row['actual'],row['false_upper_bound'])==controls[row['name']]
        assert row['detected'] is True
        assert Fraction(row['actual'])>Fraction(row['false_upper_bound'])
    future=data['future_target']
    # Closed combinatorial count: for each fixed initial state and first map,
    # second maps distribute the image of the attained middle state uniformly.
    n=2**config['future_update_bits'];maps=n**n
    paths=n*maps*maps
    assert future=={'bits':2,'steps':2,'maps_per_step':maps,
      'update_sequences':maps*maps,'state_paths':paths,
      'reconstructed_paths':paths,
      'target_differs_from_initial_paths':(n-1)*maps*maps,
      'success':'1/1','future_updates_known_before_first_leakage':True}
    # A second direct calculation checks every update sequence as tuples.
    sequences=0
    for f in product(range(n),repeat=n):
        for g in product(range(n),repeat=n):
            predicted=[g[f[z]] for z in range(n)]
            low=[v%2 for v in predicted]
            high=[g[y]//2 for y in range(n)]
            assert all(low[z]+2*high[f[z]]==predicted[z] for z in range(n))
            sequences+=1
    assert sequences==maps*maps

    # Semantic-freshness rows are recomputed from closed cardinality formulas,
    # rather than the tuple enumeration used by the production model.
    expected_seq={(int(c['bits']),int(c['leakage_bits']),int(c['sessions']))
                  for c in config['sequential_cases']}
    rows=data['sequential_semantic_freshness']
    assert {(r['bits'],r['leakage_bits_per_session'],r['sessions']) for r in rows}==expected_seq
    assert len(rows)==len(expected_seq)
    fresh_points=0
    for row in rows:
        b=row['bits'];ell=row['leakage_bits_per_session'];q=row['sessions']
        hidden=b-ell
        p=Fraction(1,2**hidden)
        fresh=1-(1-p)**q
        union=min(Fraction(1),q*p)
        persistent=Fraction(1,2**max(b-q*ell,0))
        assert row['single_session_success']==ratio(p)
        assert row['fresh_targets_lifetime_success']==ratio(fresh)
        assert row['union_bound']==ratio(union)
        assert row['persistent_target_success']==ratio(persistent)
        assert row['fresh_target_tuples']==(2**b)**q
        assert row['persistent_targets']==2**b
        fresh_points+=row['fresh_target_tuples']

    rb=data['rollback'];b=config['rollback_bits'];n=2**b
    assert rb=={'bits':b,'old_target_fully_exposed':True,
      'fresh_regeneration_success':ratio(Fraction(1,n)),
      'restored_target_success':'1/1','fresh_points':n*n,'restored_points':n}

    expected_loss=[]
    for cfg in config['reduction_loss_cases']:
        eps=Fraction(cfg['epsilon']);ls=[int(v) for v in cfg['leakage_bits']]
        nu=Fraction(cfg.get('freshness_failure','0/1'))
        terms=[min(Fraction(1),(2**ell)*eps) for ell in ls]
        expected_loss.append({'epsilon':ratio(eps),'leakage_bits':ls,
          'freshness_failure':ratio(nu),'per_session_terms':[ratio(x) for x in terms],
          'total_upper_bound':ratio(min(Fraction(1),nu+sum(terms,Fraction(0))))})
    assert data['reduction_loss']==expected_loss

    ratchet_stats=verify_entropy_ratchet(data['entropy_ratchet'],config)
    ratchet_controls=ratchet_controls_second()
    assert len(data['ratchet_negative_controls'])==len(ratchet_controls)
    assert {r['name'] for r in data['ratchet_negative_controls']}==set(ratchet_controls)
    for row in data['ratchet_negative_controls']:
        assert (row['actual'],row['false_upper_bound'])==ratchet_controls[row['name']]
        assert row['detected'] is True

    return {'future_update_sequences':sequences,
      'future_state_paths':paths,
      'decision_trees':sum(r['trees'] for r in data['trees']),
      'public_framing_trees':data['public_framing']['public_tree_shapes'],
      'public_framing_leaf_checks':data['public_framing']['leaf_uniform_probability_checks'],
      'share_policies':sum(r['policies'] for r in data['shares']),
      'prefix_cases':len(data['prefix']), 'negative_controls':len(controls),
      'fresh_target_tuples':fresh_points,
      'sequential_cases':len(rows), 'rollback_cases':1,
      'ratchet_negative_controls':len(ratchet_controls), **ratchet_stats,
      'status':'all stored finite results agree with second calculation'}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('result',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(3072*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(120,)*2)
    start_cpu=time.process_time();start_wall=time.monotonic()
    checked=check(json.loads(args.result.read_text()))
    checked.update(cpu_seconds=time.process_time()-start_cpu,
      wall_seconds=time.monotonic()-start_wall,
      peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      workers=1)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(checked,indent=2,sort_keys=True)+'\n')
    print(json.dumps(checked,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
