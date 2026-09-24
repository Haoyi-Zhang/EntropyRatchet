#!/usr/bin/env python3
"""Reproduce the frozen finite classical checks with one worker."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import resource
import time
from src.finite_games import (tree_case, public_framing_case, shares_case, prefix_cases,
                             mask_identity_count,negative_controls,fresh_rekey_case,future_target_case)
from src.sequential_bounds import sequential_cases, rollback_case, reduction_loss_cases
from src.entropy_ratchet import all_ratchet_cases, ratchet_negative_controls


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=Path('results/recomputed'))
    p.add_argument('--pilot',action='store_true')
    args=p.parse_args()
    base=Path(__file__).resolve().parent
    cfg=json.loads((base/'inputs/instances.json').read_text())
    resource.setrlimit(resource.RLIMIT_AS,(cfg['address_space_limit_mib']*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(cfg['time_limit_seconds'],)*2)
    start_wall=time.monotonic();start_cpu=time.process_time()
    if args.pilot:
        result={'scope':'classical finite pilot',
                'trees':[tree_case(2,2)],
                'shares':[shares_case(1,3,True),shares_case(1,3,False)],
                'negative_controls':negative_controls()}
    else:
        result={'scope':'finite classical checks, not general proof or quantum soundness evidence',
          'trees':[tree_case(c['bits'],c['depth']) for c in cfg['tree_cases']],
          'public_framing':public_framing_case(cfg['public_framing_max_depth']),
          'shares':[shares_case(c['bits'],c['epochs'],fresh)
                    for c in cfg['share_cases'] for fresh in (True,False)],
          'prefix':prefix_cases(cfg['prefix_bits_max']),
          'mask_identity_checks':mask_identity_count(cfg['mask_identity_bits_max']),
          'fresh_rekey':fresh_rekey_case(),
          'negative_controls':negative_controls(),
          'future_target':future_target_case(cfg['future_update_bits'],cfg['future_update_steps']),
          'sequential_semantic_freshness':sequential_cases(cfg['sequential_cases']),
          'rollback':rollback_case(cfg['rollback_bits']),
          'reduction_loss':reduction_loss_cases(cfg['reduction_loss_cases']),
          'entropy_ratchet':all_ratchet_cases(cfg),
          'ratchet_negative_controls':ratchet_negative_controls()}
    wall=time.monotonic()-start_wall;cpu=time.process_time()-start_cpu
    stats={'workers':1,'wall_seconds':wall,'cpu_seconds':cpu,
      'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'random_seed':None,'randomness':'none: complete enumeration of the frozen domains',
      'address_space_limit_mib':cfg['address_space_limit_mib'],
      'cpu_limit_seconds':cfg['time_limit_seconds']}
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'exact-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (args.output/'resource-use.json').write_text(json.dumps(stats,indent=2,sort_keys=True)+'\n')
    if not args.pilot:
        with (args.output/'tree-summary.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['bits','depth','trees','max_real_success','guessed_response_success','max_ratio'])
            w.writeheader()
            for row in result['trees']: w.writerow({k:row[k] for k in w.fieldnames})
        with (args.output/'public-framing-summary.csv').open('w',newline='') as f:
            names=['max_depth','public_tree_shapes','terminal_transcript_paths',
                   'leaf_uniform_probability_checks','leaf_uniform_failures',
                   'strict_improvement_trees','equal_factor_trees',
                   'maximum_local_uniform_factor','maximum_leaf_uniform_factor',
                   'maximum_local_over_leaf_ratio']
            w=csv.DictWriter(f,fieldnames=names);w.writeheader();w.writerow(result['public_framing'])
        with (args.output/'share-summary.csv').open('w',newline='') as f:
            names=['bits','epochs','fresh_masks','policies','points_per_policy','independent_policies','max_guess_success']
            w=csv.DictWriter(f,fieldnames=names);w.writeheader();w.writerows(result['shares'])
        with (args.output/'sequential-summary.csv').open('w',newline='') as f:
            names=['bits','leakage_bits_per_session','sessions','single_session_success',
                   'fresh_targets_lifetime_success','union_bound','persistent_target_success',
                   'fresh_target_tuples','persistent_targets']
            w=csv.DictWriter(f,fieldnames=names);w.writeheader();w.writerows(result['sequential_semantic_freshness'])
        with (args.output/'extractor-summary.csv').open('w',newline='') as f:
            names=['input_bits','entropy_bits','output_bits','flat_sources','affine_seeds',
                   'source_seed_pairs','maximum_distance','mean_distance',
                   'maximum_distance_squared','lhl_bound_squared']
            w=csv.DictWriter(f,fieldnames=names);w.writeheader()
            for row in result['entropy_ratchet']['extractor']:
                w.writerow({k:row[k] for k in names})
        with (args.output/'ratchet-budget-summary.csv').open('w',newline='') as f:
            names=['retained_bits','session_bits','observation_support','observation_bits',
                   'fresh_entropy_bits','extractor_input_min_entropy','extractor_output_bits',
                   'entropy_slack','distance_bound','required_fresh_entropy_at_this_slack']
            w=csv.DictWriter(f,fieldnames=names);w.writeheader()
            for row in result['entropy_ratchet']['entropy_budgets']:
                w.writerow({k:row[k] for k in names})
    print(json.dumps({'status':'finite checks passed','output':str(args.output),**stats},sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
