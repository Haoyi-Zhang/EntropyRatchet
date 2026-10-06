# Frozen finite input domain

`instances.json` declares every exact case, one-worker execution cap, CPU-time
limit, and address-space limit. Finite routines reject out-of-range game
parameters and invalid loss budgets; the second calculation rejects duplicate
tree, share, prefix, and lifetime evidence rows. No random seed is used because
every selected case is enumerated.

## Generic leakage cases

For an `m`-bit uniform target, a binary predicate is a truth table on `2^m`
inputs.  A full depth-`d` binary decision tree has `2^d-1` internal nodes; every
labelled tree in the declared cases is covered.  Share-selection cases enumerate
every adaptive policy that chooses one complete share after each observed
prefix, under both fresh-mask and restored-mask semantics.

The public-framing domain enumerates all 677 ordered pruned binary response-tree
shapes of maximum depth four and all 6,813 terminal paths.  For each tree, the
direct code samples a child in proportion to its number of terminal descendants;
the independent checker recomputes those counts by recurrence.  This domain
checks a public fixed-tree lemma only.  It does not justify leaf sampling when
the future tree depends on an unexamined private or quantum branch.

The prospective-target domain covers all pairs of public maps on a four-element
state space and all initial states: 65,536 update pairs and 262,144 paths.  It
checks predictability under known future updates, not one-wayness or
computational hardness.

Fresh/persistent lifetime cases enumerate 99,404 tuples.  Rollback compares
fresh regeneration with restoration of a fully exposed four-bit target.
Reduction-loss cases perform exact rational accounting for causal multipliers,
session sums, and additive freshness distance.

## Entropy-ratchet cases

The affine-hash audit enumerates every declared flat source and every seed of a
small two-universal affine family: 14,760 sources and 471,200 source-seed pairs.
It computes exact statistical distances and checks them against declared
leftover-hash bounds.  These toy cases test arithmetic and support logic, not
cryptographic parameters or quantum side information.

The exact XOR-ratchet cases enumerate 1,216 combinations of retained state,
post-exposure source, session identifier, and output split.  They verify that
XOR with a uniform post-exposure source yields an exactly uniform next retained
state/session-tape pair in the declared full-entropy construction.

Three entropy-budget cases check

```text
delta <= 1/2 sqrt(J * 2^(r-h)),
```

and three support-barrier cases check that a source of support `2^k` cannot be
mapped, for a fixed public seed, closer than `1-2^(k-m)` to uniform on `m>k`
bits.  Two lifetime vectors exercise
`rho + sum delta_j + sum Gamma_j epsilon_j`.

Four ratchet-specific controls detect extracting too many exact uniform bits,
treating snapshot bytes as post-exposure fresh, ignoring rollback without an anchor,
and displaying a domain tag without checking it.  Eight generic controls include
secret-dependent framing, isolated-to-sequential lifting, and the new error of
using per-secret support as a public causal factor.

## Fixed-marginal diagnostics

`contract_budget_cases` contains three rational instances of the two-cost
smoothing budget, one with eta=0 and two with eta>0. The general smooth quantum
bound is proved in the paper, not inferred from these cases. A fixed two-block
cq input (uniform V with conditional |0> and |+>) is scaled by 15/16 to a
subnormalized witness, without renormalization. Inputs and chosen witness are
explicit in code/results; 2x2 spectral norms are checked to 1e-12, not called
exact rational or hardware evidence. The classical eight-cell diagnostic
separates optimized and actual side marginals.

Lifetime success is any-session guessing with public rejection in both modes.
The standalone final-only formula is explicitly named. The full coordinate
policy search and the prefix-policy recursion are compared on the frozen cases;
tests also cover the complete 36-point grid 1<=m<=3, 0<=L<=m, 1<=Q<=4.

The joint-independence XOR controls enumerate correlated and independent sources.
The retired-input check enumerates 256 public affine seeds times eight complete
inputs, with separately written output and recomputation operations. It is not
physical-erasure or rollback-prevention evidence.

## Frozen bibliography inputs

`references.bib` is an exact snapshot of the manuscript bibliography,
`manuscript-citations.txt` is the sorted citation-key set extracted from the
manuscript, and `bibliography_registry.csv` is the normalized one-row-per-key
registry used by `audit_sources.py`.  The audit requires exact key-set equality
with `literature_matrix.csv`, checks normalized title/author/year/type fields,
validates persistent-identifier syntax and uniqueness, requires the same
non-DOI locator inside BibTeX, checks type-specific publication fields, rejects
generic DBLP search links, and requires every primary locator to appear in
`external_resources.csv`.  It is deliberately offline: a passing result proves
packet consistency, not that every remote record resolved on that run or that
every cited theorem was independently re-proved.

## Interpretation

The domains exercise adaptive framing, empty leaves, noninjective updates,
persistent versus independent semantics, fresh versus restored masks, leakage
saturation, entropy deficits, recovery order, and evidence-integrity failures.
They are synthetic exhaustive checks, not held-out data, a workload sample, a
scalability benchmark, a proof assistant, an LWE experiment, or a quantum
soundness test.
