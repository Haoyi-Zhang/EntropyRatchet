#!/usr/bin/env python3
"""Check manuscript/ledger interface consistency, not mathematical validity."""
from __future__ import annotations
import argparse
import csv
import io
import json
from pathlib import Path
import re

LABEL_RE=r'(?:sec|fig|tab|thm|lem|cor|prop|eq|def):[A-Za-z0-9_-]+'

def audit_texts(tex: str, ledger: str, proof: str) -> dict:
    labels=re.findall(r'\\label\{([^}]+)\}',tex)
    if len(labels)!=len(set(labels)):
        raise ValueError('duplicate manuscript label')
    rows=list(csv.DictReader(io.StringIO(ledger)))
    references=set(re.findall(LABEL_RE,ledger))
    missing=references-set(labels)
    if missing:raise ValueError('unresolved evidence targets: '+', '.join(sorted(missing)))
    equations={}
    for label in ['eq:intro-extractor','eq:quantum-lhl','eq:delta-j']:
        match=re.search(r'\\begin\{equation\}\\label\{'+re.escape(label)+r'\}(.*?)\\end\{equation\}',tex,re.S)
        if not match or not re.search(r'2\s*\\eta',match.group(1)):
            raise ValueError('two-cost interface missing at '+label)
        equations[label]='2 eta present'
    start=tex.index('All registers are finite dimensional.')
    stop=tex.index('Let $\\mathsf I_j$ replace',start)
    if tex[start:stop] not in proof:
        raise ValueError('standalone extraction proof differs from manuscript')
    return {'passed':True,'claim_rows':len(rows),'resolved_targets':len(references),
            'equations':equations,'proof_excerpt_matches':True,
            'scope':'text/label consistency only; no automated certification of general proof'}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manuscript',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    base=Path(__file__).resolve().parent
    tex=args.manuscript.read_text()
    result=audit_texts(tex,(base/'claim_evidence_ledger.csv').read_text(),
                      (base/'proofs/fixed-marginal-extraction.md').read_text())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
    return 0
if __name__=='__main__':raise SystemExit(main())
