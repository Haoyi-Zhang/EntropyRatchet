# Reproducible artifact

This standalone repository accompanies **Entropy-Ratcheted Soundness for
Sequential Verification under State Exposure**.  It contains complete proof
notes, frozen finite domains, two differently structured exact calculations,
integrity and negative controls, 67 regression tests, an executable source audit,
source ledgers, and LaTeX
table generation.

The main result is a generic compiler.  It derives a fresh retained state and a
fresh complete base-verifier random tape from residual conditional entropy plus
a source sampled after the relevant exposure.  It is not an implementation of
Mahadev's protocol, an LWE experiment, a proof-assistant development, or an
in-place update of one lattice trapdoor under one fixed public key.

## Main theorem

For nonoverlapping sessions, control failure probability `rho`, extractor losses
`delta_j`, current classical-leakage causal factors `Gamma_j`, and matching
prefix-robust base errors `epsilon_j`, the paper proves

```text
Pr[first false acceptance]
  <= min(1, rho + sum_j delta_j + sum_j Gamma_j epsilon_j).
```

`Gamma_j` is not an after-the-fact support count.  It is the worst reciprocal
path probability of an efficient public online response sampler.  Fixed public
binary framing of at most `L_j` bits gives `Gamma_j <= 2^L_j`; a smaller
per-secret support does not by itself justify a smaller factor.  Retained-state
observation uses a separate joint-support parameter `J_j` in the next entropy
ledger.

The proof uses a control-safe coupling, predecessor-hybrid quantum conditional
min-entropy, strong seeded extraction, fixed-mode prefix lifting or an explicit
chosen-mode base theorem, causal leakage transport, and a first-bad-session
partition.  Completed base-verifier states may be released only after their
decisions are terminal.

The efficient prefix is simulated in an unmonitored ideal extension of the
declared interfaces. Positive path inclusion bounds the control-safe first-bad
event without running the proof-only failure monitor or conditioning on safety.

## Extractor distance contract

Actual histories and quantum side information are normalized, including abort
flags. Smoothing is over subnormalized states in a purified-distance ball.
No witness is renormalized. The compiler compares the hashed output to uniform
output tensor the **actual** side marginal. Its conservative error is

```text
delta_j = 2 eta_j + (1/2) sqrt(2^(m_j-k_j)).
```

`proofs/fixed-marginal-extraction.md` contains the same complete operator proof
as the manuscript. The source theorem's optimized-side definition is not
silently identified with this distance. `extractor_interface` records separate
budget arithmetic, a classical distance-definition example, and a noncommuting
cq witness with eta=1/4. These tests do not establish the general theorem.

## Reproduce

Requirements: Linux and Python 3.10 or later, standard library only.
The documented commands were checked on Linux with CPython 3.13.5.  Run from
the extracted repository root:

```sh
python3 reproduce.py --output results/recomputed
python3 verify.py results/recomputed/exact-results.json \
  --output results/recomputed/second-calculation.json
python3 -m unittest discover -s tests -v
python3 render_tables.py \
  --result results/recomputed/exact-results.json \
  --output results/tables
python3 audit_sources.py --output results/recomputed/source-audit.json
```

Do not use `python -O`; assertions are deliberate exact checks.  The principal
drivers use one worker, a 120 CPU-second limit, and a 3,072 MiB address-space
limit.  Runtime and peak-RSS observations vary by machine.  Counts, rational probabilities, CSV rows, and generated table bodies are deterministic.
The one small cq spectral diagnostic uses binary64 at absolute tolerance 1e-12.

When the repository is inside the complete project and the paper has been built,
the same audit can also compare the live manuscript and printed bibliography:

```sh
python3 artifact/audit_sources.py \
  --base artifact \
  --manuscript paper/main.tex \
  --bbl paper/main.bbl \
  --output results/recomputed/project-source-audit.json
```

`reproduce.py` enumerates the frozen cases directly.  `verify.py` does not
import the principal finite-game implementation; it uses separate recurrences,
probability-mass propagation, leaf-count identities, and explicit tuple
calculations.  The two implementations were produced in one research process,
so agreement is a second calculation, not independent peer review.

In the complete project, the additional structural check is:

```sh
python3 artifact/audit_interface.py --manuscript paper/main.tex \
  --output artifact/results/recomputed/interface-audit.json
```

This checks equation/ledger/proof-excerpt consistency, not the truth of a theorem.

## Evidence inventory

- `proofs/fixed-marginal-extraction.md` — full fixed-marginal extraction proof.
- `proofs/entropy-ratchet-proof.md` — complete compiler and instantiation proof.
- `proofs/model-and-proofs.md` — target, cq-support, causal-transport,
  fresh-secret, split-state, and rollback lemmas.
- `inputs/instances.json` and `inputs/README.md` — every finite domain and cap.
- `results/expected/` — frozen exact scientific outputs.
- `results/clean-reproduction/` — retained historical Linux commands, exits, measurements,
  output comparisons, and PDF inspection record.
- `claim_evidence_ledger.csv` — material claims mapped to proofs/checkers,
  results, paper objects, maturity, and boundaries.
- `literature-calibration.md` — 12 closest, 5 influential, and 5 adjacent
  full-paper structural calibration.
- `literature_matrix.csv` — all 84 cited references with reading depth, role,
  cohort, and redistribution boundary.
- `inputs/references.bib`, `inputs/manuscript-citations.txt`, and
  `inputs/bibliography_registry.csv` — the frozen bibliography, citation-key set,
  and one-row-per-reference registry used by the offline audit.
- `audit_sources.py` — rejects key-set drift, duplicate identifiers, generic DBLP
  searches, malformed persistent identifiers, non-DOI locator disagreement,
  incomplete type-specific publication fields, metadata mismatches, and missing
  external-resource coverage. It does not resolve the network or certify content.
- `external_resources.csv` and `source-boundaries.md` — scholarly/official
  source records and integration limits.

## Frozen exact coverage

| Family | Coverage |
|---|---:|
| Adaptive leakage trees | 4,439 |
| Public response-tree shapes / terminal paths | 677 / 6,813 |
| Trees where leaf sampling strictly improves local uniform guessing | 672 |
| Adaptive share policies | 1,368 |
| Prefix cases | 85 |
| XOR identities | 5,460 |
| Public update pairs / state paths | 65,536 / 262,144 |
| Fresh-target tuples | 99,404 |
| Flat sources / source-seed pairs | 14,760 / 471,200 |
| Exact XOR-ratchet points | 1,216 |
| Entropy budgets / barriers | 3 / 3 |
| Lifetime-loss vectors | 2 |
| Generic calculations / ratchet expected-value fixtures | 8 / 4 |
| Matched lifetime cases | 8, including zero leakage and saturation |
| Nonzero-smoothing cq witness | 1 (numerical diagnostic) |
| Public-seed/retired-input recomputations | 2,048 |
| Joint-independence XOR controls | 2 |
| Regression tests | 67 in current sources; 57 in the retained historical Linux log |

The ten additional regressions cover loss-budget domains, table projection, and control-safe
event inclusion. The latter exhausts 20,736 two-session monitor/acceptance
tables and checks non-renormalized event mass; it is not an efficiency proof or
a quantum computational experiment. Current local runs use CPython 3.12.14
on Windows through a private resource adapter, not the recorded Linux host.
The exact JSON and paper table bodies are unchanged. Frozen expected table
bodies now match the renderer and paper, including all eight matched-event
lifetime cases rather than the older four-case final-only projection.

Complete retained-state support includes recorded secret-dependent control and
abort symbols. The two-bit abort-flag regression raises guessing probability
from 1/4 to 1/2 despite zero payload leakage, requiring support J=2 rather than
J=1 in the normalized entropy ledger. The control-failure loss rho does not
erase this observation.

The standalone scientific workflow runs the finite driver, separate calculator,
regressions, offline source audit, and table/result equality gates on Ubuntu
24.04. Its raw command outputs are uploaded even on failure. A prepared
workflow is not evidence of a completed hosted run.

The public-tree domain enumerates every ordered pruned binary tree of depth at
most four.  A direct path sampler and a separate recurrence agree that sampling
children in proportion to terminal-descendant counts gives probability exactly
`1/N(root)` to every leaf.  The maximum ratio between the generic local-uniform
factor and the leaf-optimal factor is `16/5` in this frozen domain.

Both target modes permit one guess per session and public rejection feedback;
`persistent_target_success` is any-session success. The separately named
`persistent_final_only_no_feedback` is a different, one-final-guess baseline.
Full coordinate-policy search and a separately implemented prefix recursion
attain the counting optimum proved in P11. The policy-state count describes the
first solver only; it is not a separately reproduced scientific claim.

The XOR zero-loss case assumes joint independence from old C and complete B.
The correlated case X=(U,C), Phi=(0,C) has distance 1/2. Recomputing retired
inputs corroborates deterministic reconstruction, not a physical erasure control.

The ratchet-specific control rows are analytic expected-value fixtures. Their
separate comparison calculates the support-barrier row; the preloaded-source,
rollback, and unchecked-tag rows compare stated example values rather than
executing separate games. The dedicated rollback and XOR calculations remain
separate finite computations.

The calculations corroborate finite classical identities and accounting;
the labelled cq case checks a small distance calculation only.  They
are not evidence of quantum computational soundness, LWE hardness, deployed
erasure, hardware rollback resistance, performance, or scalability.

## Scientific boundary

The fresh-key Mahadev corollary regenerates the protocol key pair.  The
unamplified base error is mainly an interface check; a second corollary invokes
the published Chia--Chung--Yamakawa parallel-repetition theorem as the base
protocol and obtains negligible lifetime error when all session counts and
causal factors are polynomial and the remaining losses are negligible.  No
independent-repetition theorem is invented here.

Only classical read-only leakage with complete public framing is covered.
Coherent leakage, overlapping sessions, malicious state modification, UC
composition, physical-erasure guarantees, and fixed-public-key trapdoor
evolution are excluded.  External papers are cited but not redistributed or
relicensed.  No network, private cache, dataset, device, model API, or service is
required for the exact artifact.
