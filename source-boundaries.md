# Source boundaries and reading coverage

Scholarly papers are evidence for models, definitions, theorems, and closest-
work boundaries.  They are not executable instructions or redistributed
assets.  Stable locators, roles, reading depth, and calibration cohorts for all
84 cited works are in `literature_matrix.csv`; acquisition and integration
records are in `external_resources.csv`.  No external paper bytes are bundled,
and the repository license does not cover cited works.

## Inherited reading record and current focused verification

`literature-calibration.md` records a structural full-text calibration of 22
papers: twelve closest, five influential foundations, and five adjacent-model
works.  That inherited record describes following the motivating problem, adversarial
interface, principal theorem, proof architecture, assumptions, and stated
boundary.  This is stronger than title/abstract screening but is not line-by-
line proof certification, independent peer review, an exhaustive search, or an
external novelty opinion.  The remaining 62 references retain claim-level or
bibliographic depth labels. This continuation rechecked the actual definitions
and proof passages in arXiv:1002.2436, not every proof in all 84 references.
The executable audit remains an offline consistency check, not full-text
certification. The current fixed-marginal argument is self-contained.

## Verification lineage

Mahadev's classical-verification paper supplies the motivating key/trapdoor
state and published one-session soundness theorem.  The manuscript maps the
complete verifier random tape of a fresh session to the entropy ratchet, creates
fresh function keys and trapdoors, binds an outer session identifier, and
releases the old trapdoor state only after the decision is terminal.  It does
not re-prove Mahadev's theorem or claim that the published implementation offers
a safe leakage, erasure, or recovery interface.

Later efficient, noninteractive, succinct, and reusable verification results
prove different interfaces and prevent the broad novelty claim that repeated
verification is new.  Their setup, oracle, repetition, and compression
arguments cannot be silently converted into arbitrary access to hidden verifier
memory.  The current paper's delta is the entropy/control/leakage compiler
interface, not reusability by itself.

## Leakage, refresh, and temporal security

Bounded and continual leakage, leakage-resilient storage, proactive sharing,
forward security, key insulation, and intrusion resilience protect different
objects in different time directions.  Construction-specific continual-
leakage invariants do not follow from representation change alone.  Split-state
refresh requires its declared component and observation restrictions.  Forward
security usually protects past outputs after later compromise; this paper
protects later false-acceptance decisions after earlier exposure by regenerating
current key coins.

The two observation ledgers in the main theorem therefore remain separate:
retained-state transcript support `J` costs conditional min-entropy for the next
update, while current-base-state leakage must admit a public causal sampler with
factor `Gamma`.  A per-secret realized support is not an online simulator.

## Entropy and quantum side information

Operational cq min-entropy supplies `H_min=-log p_guess`.  Quantum-proof
leftover hashing supplies the one-hop trace-distance bound for a strong seeded
two-universal extractor.  The paper contributes the predecessor-hybrid ledger,
control-safe coupling, and sequential composition; it does not claim a new
leftover-hash lemma.  The public session identifier is canonically encoded and
fixed before extraction; restricting the hash family to that fixed prefix
preserves two-universality on the variable source.

## Composability and quantum attackers

Sequential/composable-security sources motivate complete-history interfaces
and explicit environments.  The actual theorem is nonconcurrent and not a UC
realization.  It preserves an adversary's polynomial-size quantum state through
straight-line simulation but permits only classical queries and answers at the
leakage interface.  No coherent leakage oracle is covered.

## Lattice foundations and the excluded fixed-key extension

LWE and lattice-trapdoor sources identify the assumptions and state objects in
the Mahadev family.  They justify neither safe in-place trapdoor refresh nor
hardness after old-trapdoor exposure.  A fixed-public-key extension would need
a new construction-specific residual-hardness invariant for every reachable
history, including rollback and recovery.  The absence of that extension does
not leave the claimed fresh-key compiler incomplete.

## Bibliographic integrity

The final bibliography has 84 unique keys, all cited, and the same key set is
frozen in `references.bib`, `manuscript-citations.txt`,
`bibliography_registry.csv`, and `literature_matrix.csv`.  The registry distinguishes 45 publisher/archive/institutional-record checks
from 39 bibliographic-screening records inherited with the project. They are not
84 new full-text readings. The source audit checks metadata, publication fields,
and identifier consistency. The fixed-marginal repair specifically rereads the
2010 arXiv text's smoothing definitions, Definition 3, Lemma 4 proof and
Theorem 6. The 2011 journal locator and preprint are one bibliography entry,
not counted twice. No source theorem is claimed to use the fixed actual
marginal solely on the basis of its optimized-distance statement.

## Executable boundary

No external implementation, benchmark, dataset, solver, or paper file is
required by the exact artifact.  The Python code uses only the standard library
and enumerates synthetic finite games declared in `inputs/instances.json`.
The main checks are classical; the separately labelled small cq witness is a
numerical distance diagnostic. Neither is a quantum verification experiment,
LWE attacks, hardware measurements, or deployment evidence.
