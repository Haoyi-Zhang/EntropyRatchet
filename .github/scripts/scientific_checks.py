"""Bounded offline scientific gates for the flat standalone artifact repository."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]


def compare(output: Path) -> dict:
    actual = json.loads((output/'exact-results.json').read_text(encoding='utf-8'))
    expected = json.loads((ROOT/'results/expected/exact-results.json').read_text(encoding='utf-8'))
    if actual != expected:
        raise ValueError('finite result differs from the frozen exact result')
    tables = sorted((ROOT/'results/expected/tables').glob('*.tex'))
    if len(tables) != 7:
        raise ValueError('expected seven frozen table bodies')
    for table in tables:
        if (output/'tables'/table.name).read_bytes() != table.read_bytes():
            raise ValueError('generated table differs: '+table.name)
    return {'exact_result_matches':True,'table_bodies_match':len(tables),
            'scope':'frozen finite equality, not a proof of the general theorem'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True,exist_ok=True)
    env = {**os.environ,'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'}
    schedule = [
        ('finite-calculation',['reproduce.py','--output',str(output)]),
        ('second-calculation',['verify.py',str(output/'exact-results.json'),
                               '--output',str(output/'second-calculation.json')]),
        ('regressions',['-m','unittest','discover','-s','tests','-v']),
        ('source-audit',['audit_sources.py','--output',str(output/'source-audit.json')]),
        ('table-generation',['render_tables.py','--result',str(output/'exact-results.json'),
                             '--output',str(output/'tables')]),
    ]
    records = []
    failed = False
    start = time.monotonic()
    for name, command in schedule:
        argv = [sys.executable,'-B',*command]
        remaining = 450 - (time.monotonic()-start)
        if remaining <= 0:
            records.append({'name':name,'exit_code':124,'reason':'whole-run wall budget exhausted'})
            failed = True
            break
        t = time.monotonic()
        with (output/(name+'.stdout.txt')).open('w',encoding='utf-8') as stdout, \
             (output/(name+'.stderr.txt')).open('w',encoding='utf-8') as stderr:
            try:
                proc = subprocess.run(argv,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,
                                      timeout=min(150,remaining),check=False)
                code = proc.returncode
            except subprocess.TimeoutExpired:
                code = 124
        records.append({'name':name,'command':argv,'exit_code':code,
                        'wall_seconds':time.monotonic()-t})
        failed |= code != 0
        (output/'commands.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    try:
        comparison = compare(output)
    except (OSError,ValueError) as exc:
        comparison = {'passed':False,'error':str(exc)}
        failed = True
    comparison.update(passed=not failed,wall_seconds=time.monotonic()-start)
    (output/'comparison.json').write_text(json.dumps(comparison,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(comparison,sort_keys=True))
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
