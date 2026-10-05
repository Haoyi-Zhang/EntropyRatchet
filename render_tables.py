#!/usr/bin/env python3
"""Render manuscript tables from exact finite results; standard library only."""
from __future__ import annotations
import argparse
from fractions import Fraction
import json
from pathlib import Path


def frac(s: str) -> str:
    f=Fraction(s)
    if f.denominator==1:return str(f.numerator)
    return '$'+str(f.numerator)+'/'+str(f.denominator)+'$'


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result',type=Path,default=Path('results/expected/exact-results.json'))
    p.add_argument('--output',type=Path,default=Path('results/tables'))
    args=p.parse_args();data=json.loads(args.result.read_text())
    args.output.mkdir(parents=True,exist_ok=True)
    lines=[r'\begin{tabular}{rrrrr}',r'\toprule',r'$m$ & $d$ & Trees & Best real success & Guessing ratio \\',r'\midrule']
    for r in data['trees']:
        lines.append(f"{r['bits']} & {r['depth']} & {r['trees']:,} & {frac(r['max_real_success'])} & {frac(r['max_ratio'])}"+r' \\')
    lines += [r'\bottomrule',r'\end{tabular}']
    (args.output/'trees.tex').write_text('\n'.join(lines)+'\n')
    pairs={}
    for r in data['shares']:pairs.setdefault((r['bits'],r['epochs']),{})[r['fresh_masks']]=r
    lines=[r'\begin{tabular}{rrrrr}',r'\toprule',r'$m$ & Epochs & Policies per mode & Fresh masks & Restored mask \\',r'\midrule']
    for (m,t),pair in sorted(pairs.items()):
        lines.append(f"{m} & {t} & {pair[True]['policies']:,} & {frac(pair[True]['max_guess_success'])} & {frac(pair[False]['max_guess_success'])}"+r' \\')
    lines += [r'\bottomrule',r'\end{tabular}']
    (args.output/'shares.tex').write_text('\n'.join(lines)+'\n')
    names={
      'reset_budget_after_representation_refresh':'Reset the budget after refreshing',
      'restored_mask_is_not_fresh':'Treat restored randomness as fresh',
      'whole_state_query_is_not_one_share_query':'Allow a joint query in a one-share model',
      'secret_dependent_length_is_free':'Ignore secret-dependent framing',
      'multiply_distinguishing_advantage':'Multiply prediction advantage',
      'one_shot_soundness_implies_reuse':'Lift standalone soundness without a premise',
      'public_tags_restore_secret_entropy':'Treat public tags as secret entropy',
      'per_state_support_is_not_public_guessability':'Use per-state support as a public guessing factor'}
    lines=[r'\begin{tabular}{p{9.5cm}rr}',r'\toprule',r'Incorrect inference & Actual & False bound \\',r'\midrule']
    for r in data['negative_controls']:
        lines.append(names[r['name']]+' & '+frac(r['actual'])+' & '+frac(r['false_upper_bound'])+r' \\')
    lines += [r'\bottomrule',r'\end{tabular}']
    (args.output/'controls.tex').write_text('\n'.join(lines)+'\n')
    lines=[r'\begin{tabular}{rrrrrr}',r'\toprule',
      r'$m$ & $L$ & $Q$ & Fresh targets & Union bound & Persistent target \\',r'\midrule']
    for r in data['sequential_semantic_freshness']:
        lines.append(f"{r['bits']} & {r['leakage_bits_per_session']} & {r['sessions']} & "
          +frac(r['fresh_targets_lifetime_success'])+' & '+frac(r['union_bound'])+' & '
          +frac(r['persistent_target_success'])+r' \\')
    lines += [r'\bottomrule',r'\end{tabular}']
    (args.output/'semantic-freshness.tex').write_text('\n'.join(lines)+'\n')

    lines=[r'\begin{tabular}{rrrrrr}',r'\toprule',
      r'$n$ & $k$ & $m$ & Flat sources & Source--seed pairs & Max. distance \\',r'\midrule']
    for r in data['entropy_ratchet']['extractor']:
        lines.append(f"{r['input_bits']} & {r['entropy_bits']} & {r['output_bits']} & "
          +f"{r['flat_sources']:,} & {r['source_seed_pairs']:,} & {frac(r['maximum_distance'])}"+r' \\')
    lines += [r'\bottomrule',r'\end{tabular}']
    (args.output/'extractor.tex').write_text('\n'.join(lines)+'\n')

    lines=[r'\begin{tabular}{rrrrrr}',r'\toprule',
      r'$c$ & $r$ & Observation support & Fresh entropy & Slack & LHL distance \\',r'\midrule']
    for r in data['entropy_ratchet']['entropy_budgets']:
        lines.append(f"{r['retained_bits']} & {r['session_bits']} & {r['observation_support']} & "
          +f"{r['fresh_entropy_bits']} & {r['entropy_slack']} & {frac(r['distance_bound'])}"+r' \\')
    lines += [r'\bottomrule',r'\end{tabular}']
    (args.output/'ratchet-budget.tex').write_text('\n'.join(lines)+'\n')

    names2={
      'extract_more_uniform_bits_than_entropy':'Extract more uniform bits than source entropy',
      'preloaded_randomness_is_post_exposure_fresh':'Treat preloaded randomness as post-exposure fresh',
      'rollback_without_monotone_anchor':'Ignore restoration without a monotone anchor',
      'unchecked_domain_tag_blocks_replay':'Assume an unchecked public tag blocks replay'}
    lines=[r'\begin{tabular}{p{9.5cm}rr}',r'\toprule',r'Incorrect ratchet inference & Actual & False bound \\',r'\midrule']
    for r in data['ratchet_negative_controls']:
        lines.append(names2[r['name']]+' & '+frac(r['actual'])+' & '+frac(r['false_upper_bound'])+r' \\')
    lines += [r'\bottomrule',r'\end{tabular}']
    (args.output/'ratchet-controls.tex').write_text('\n'.join(lines)+'\n')
    print('Rendered seven manuscript tables from exact rational results.')
    return 0

if __name__=='__main__':raise SystemExit(main())
