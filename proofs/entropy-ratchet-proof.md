# Entropy-ratcheted sequential verification: complete argument

This note restates the paper's key-evolution theorem in an implementation-audit
form.  It is a generic cryptographic compiler: residual retained-state entropy
and entropy sampled after the relevant exposure are converted into fresh
per-session verifier coins, after which a separately proved base-protocol
soundness theorem is invoked.  It does **not** update one Mahadev-style
trapdoor in place, preserve one fixed protocol public key, or assert that a
software erasure/counter interface realizes the control assumptions below.
All logarithms are base two and
`Delta(rho,sigma)=(1/2)||rho-sigma||_1`.

## 1. Base protocol and the exact prefix obligation

Fix public setup `pp` and a legal public mode `mu` containing the statement and
all current public parameters.  From a uniform complete random tape `R`, write

    (A,S) = Key(pp,mu;R),

where `A` is the current public interface and `S` is the complete secret
verifier state.  The remaining interaction and terminal decision may be
arbitrary.  `Bad(mu)` is false acceptance for the declared mode.

A *prefix-robust* theorem for a declared mode-selection rule permits a QPT
prefix generator, before `R` is sampled, to produce a classical history `H`, a
private quantum register `E`, and a legal current mode `mu` as allowed by that
rule.  A QPT continuation then receives `(H,E,A)` and runs the current session.
With no secret-dependent leakage from `S`, false acceptance must be at most the
declared `epsilon`.

**Lemma 1 (fixed-mode prefix lifting).** Fix `mu` before the prefix generator
runs.  If ordinary one-session soundness for that fixed mode quantifies over
every QPT prover and permits the prover to prepare any efficient private state
before seeing `A`, then every efficiently generated prefix for that same fixed
mode has the identical error `epsilon(mu)`.

**Proof.** Combine the prefix generator and continuation into one QPT prover.
Before receiving `A` it runs the generator and stores `(H,E)`; afterwards it
runs the continuation.  This is exactly the prefix experiment.  The
construction never copies, measures, conditions on, or rewinds `E`.  Ordinary
fixed-mode soundness applies.  QED.

The fixed-mode qualifier is material.  If the prefix generator may choose
`mu` correlated with `E`, pointwise soundness for externally fixed values of
`mu` need not provide an efficient sampler for the conditional state
`E | mu`.  Such an instantiation must prove the corresponding chosen-mode
two-stage game directly or restrict the mode schedule.  The main compiler below
therefore assumes the prefix-robust property matching the actual mode rule.  In
the Mahadev corollaries the BQP no-instance is fixed, while the outer session
identifier is public framing generated before the fresh key tape.

## 2. Two leakage ledgers with different mathematical roles

The ratchet retains a classical state `C_j`; the base verifier has a current
session state `S_j`.  The ordinary base protocol cannot read `C_j`.

* `W_j` is the complete classical transcript of observations of `C_j` after
  update `j` and before update `j+1`.  Its joint support is at most `J_j`.
  `J_j` is charged to the **next entropy ledger** by a conditional-min-entropy
  chain rule.
* `Z_j` is the complete classical read-only leakage transcript about current
  `S_j` before the decision in session `j`.  It must admit an efficient public
  **causal guesser** `q_j`.  For every complete legal response path `z`, let
  `q_j(z)` be the product of its public online conditional probabilities and set

      Gamma_j = max_{z legal} 1 / q_j(z),

  requiring `q_j(z)>0` for every legal real path.  `Gamma_j` is charged against
  **current one-session soundness**.

Public framing, response length, abort/timeout/status symbols, termination, and
secret-dependent call count are part of the response path.  Full release of
`S_j` after the current decision becomes terminal is allowed and is not current
leakage.  If `C_j` is readable through the current leakage interface, the same
observation may need to be charged both to `Gamma_j` and to the next `J_j`.

The distinction is essential.  A small actual support after fixing a secret is
not automatically an online distribution that a reduction can sample without
that secret.  Conversely, a causal guessing factor does not establish residual
entropy of the retained state.

### Causal leakage transport

Consider a read-only classical leakage interface and a positive terminal event
`Bad`.  A leakage-free simulator forwards ordinary messages and answers each
leakage query by sampling the next public symbol from `q`.  Decompose the real
terminal cq state into positive subnormalized blocks indexed by complete
classical histories `h`; let `b_h` be the contribution of block `h` to `Bad` and
`z(h)` its leakage-response path.  While the guessed prefix matches `z(h)`, the
adversary asks the same query and performs the same quantum operation.  The
matched simulator block therefore contains `q(z(h)) b_h`, with
`q(z(h)) >= 1/Gamma(q)`.  Summing blocks yields

    Pr[G_0(B):Bad] >= sum_h q(z(h)) b_h
                    >= Pr[G_leak(A):Bad] / Gamma(q),              (1)

or equivalently the stated transport bound.  Unmatched blocks are positive and
can only add acceptance mass.  No guess is tested and no quantum register is
measured or rewound.

A universally available guesser samples locally uniformly from each finite
public conditional response alphabet, yielding

    Gamma(q) <= max_z product_i |Y_i(z_{<i})|.                    (2)

Fixed public binary framing of at most `L` bits gives `Gamma<=2^L`.  When the
entire response-framing tree is public, fixed independently of the secret and
of unexamined private branches, and terminal-descendant counts `N(v)` are
computable online, sampling child `vy` with probability `N(vy)/N(v)` makes every
leaf uniform and gives the optimal factor `Gamma=N(root)`.  This refinement is
not available for a future tree selected by a hidden private/quantum branch.

## 3. Control plane and update transaction

A legal update transaction has the following order.

1. Obtain a public identifier `sid_j` that has not previously committed in the
   lineage.
2. After the preceding exposure or recovery point, sample a classical source
   `X_j` that was absent from every restorable earlier snapshot.
3. Sample an independent public extractor seed `D_j`.
4. Compute

       Y_j = Ext_{D_j}(encode(sid_j) || C_{j-1} || X_j)
           = C_j || R_j,

   with output lengths `c_j` and `r_j`.
5. Compute `(A_j,S_j)=Key(pp,mu_j;R_j)` and bind the same checked identifier
   wherever cross-session substitution would otherwise be accepted.
6. Atomically commit `C_j` and the identifier, then erase `C_{j-1}`, `X_j`,
   `R_j`, and all temporary copies.  Only `C_j` remains in the ratchet
   compartment.

A pre-commit crash consumes the attempted identifier and source; recovery uses
a new identifier and newly sampled post-recovery source.  A post-commit crash
uses `C_j` as authoritative and rejects older snapshots.  These are mathematical
interface conditions, not claims about a particular operating system.

Let `CtlFail` include every undeclared violation: identifier reuse, treating
restorable bytes as fresh, making an old snapshot authoritative, or retaining
retired material outside `W_j`/`Z_j`.  Assume

    Pr[CtlFail] <= rho.

Define an instrumented experiment `G_safe` coupled to the real execution until
the first control failure and forced to reject thereafter.  Then

    Pr_G[Bad] <= rho + Pr_G_safe[Bad].                              (3)

All entropy statements below are made inside `G_safe`, not in a distribution
conditioned on `not CtlFail`; hence the proof hides no division by
`Pr[not CtlFail]`.

## 4. Quantum-proof entropy ledger

For a cq state `V B`, with classical `V`,

    H_min(V|B) = -log p_guess(V|B).

A strong quantum-proof seeded extractor satisfies

    Delta(D Ext_D(V) B, D U_m B) <= delta

for an independent uniform public seed `D`.  For two-universal hashing,

    delta <= eta + (1/2) sqrt(2^{m-H_min^eta(V|B)}).               (4)

The public identifier is fixed before hashing, contributes no entropy, and is
encoded canonically.  Restricting a two-universal family to inputs
`encode(sid)||V` preserves two-universality as a function of `V` for each fixed
identifier.

Inside `G_safe`, define hybrid `I_j` so that the first `j` outputs
`(C_i,R_i)` are replaced at creation by independent uniform strings, while later
updates remain real.  Immediately before `D_j` is sampled in predecessor hybrid
`I_{j-1}`, let `B_{j-1}` contain the complete classical history, recovery data,
all ratchet observations, and the adversary's unmeasured quantum register.  The
hybrid entropy ledger is

    H_min^{eta_j}(C_{j-1} X_j | B_{j-1}) >= k_j.                   (5)

It is intentionally stated in the predecessor hybrid; no entropy statement is
silently transported through earlier game hops.

**Lemma 2 (one update hop).** For `m_j=c_j+r_j`, (5) implies

    Delta(I_{j-1},I_j) <= delta_j,
    delta_j = eta_j + (1/2) sqrt(2^{m_j-k_j}).                     (6)

**Proof.** Apply (4) to `V_j=C_{j-1}X_j`, side information `B_{j-1}`, and
independent seed `D_j`.  Splitting the output, applying `Key`, running the
protocol, exposing declared leakage, and executing all later sessions are CPTP
maps; trace distance cannot increase.  QED.

**Corollary 3 (ratchet semantic freshness).** `I_0` is within distance
`sum_j delta_j` of `I_Q`, where every pair `(C_j,R_j)` is independent uniform at
creation.  This follows by successive application of Lemma 2 and the triangle
inequality.

## 5. Sequential soundness theorem

**Theorem 4 (entropy-ratcheted sequential soundness).** Consider at most `Q`
nonoverlapping sessions.  Assume:

1. `Pr[CtlFail] <= rho`;
2. the predecessor-hybrid ledger (5) holds with extraction errors `delta_j`;
3. the base protocol has prefix-robust error `epsilon_j` for the actual legal
   mode-selection rule in session `j`;
4. current leakage is classical, read-only, and admits an efficient public
   causal guesser with factor `Gamma_j`; and
5. a completed base state is released only after its decision is terminal.

Then

    Pr[Bad] <= min(1,
                   rho + sum_j delta_j + sum_j Gamma_j epsilon_j). (7)

The adversary may retain arbitrary polynomial-size quantum state and all
ordinary transcripts across sessions.

**Proof.** Equation (3) replaces the real process by `G_safe` at cost `rho`.
Corollary 3 replaces every ratchet output by an independent uniform pair at cost
`sum_j delta_j`.

In the final hybrid, let `Bad_j` be the event that the first false acceptance is
in session `j`.  These events are disjoint.  Fix `j`.  A one-session reduction
straight-line simulates sessions `1,...,j-1`, including ordinary feedback,
terminal old-state releases, retained-state observations, aborts, and the
adversary's resulting quantum register.  Current `R_j` is independent uniform
and unsampled, so the simulated history is a legal prefix under assumption 3.

The reduction embeds the current base session and runs the public causal guesser
`q_j` online.  Applying (1), every real current-leakage branch that leads to
`Bad_j` contributes at least a `1/Gamma_j` fraction to a leakage-free base-game
adversary.  Prefix-robust soundness therefore yields

    Pr[Bad_j] <= Gamma_j epsilon_j.

Sum the disjoint first-bad events and restore the two earlier losses.  The proof
is straight line and never tests the guessed path or rewinds the adversary.
QED.

For fixed public binary framing of `L_j` bits, `Gamma_j<=2^{L_j}`.  A smaller
factor is valid only when accompanied by an efficiently sampleable public causal
distribution; a per-secret support count is not enough.

## 6. Explicit retained-state exposure budget

In predecessor hybrid `I_{j-1}`, suppose `C_{j-1}` is uniform on `c` bits and
jointly independent of the prior side information and the simultaneously
created base tape `R_{j-1}`.  The ordinary base protocol may read `R_{j-1}` but
cannot read `C_{j-1}`.  Therefore any new correlation with `C_{j-1}` before the
next update must enter through declared classical observation `W_{j-1}`, or be
charged as a control failure.

If `W_{j-1}` has joint support at most `J`, the cq support chain rule gives

    H_min(C_{j-1} | B_{j-1}) >= c - log J.                         (8)

Let `X_j` be an independent uniform `h`-bit source sampled after that history.
Product additivity gives

    H_min(C_{j-1} X_j | B_{j-1}) >= c - log J + h.                 (9)

Extracting `c+r` bits then has

    delta <= (1/2) sqrt(J 2^{r-h}).                               (10)

To obtain `delta<=2^{-tau}`, it is sufficient that

    h >= r + log J + 2 tau - 2.                                  (11)

The ideal `C_{j-1}` in this calculation is independent uniform jointly with the
previous side information and `R_{j-1}`.  That independence is supplied by the
predecessor hybrid, not inferred from a marginal uniformity statement.  Full
retained-state exposure has `J=2^c`, so the fresh source must replace the entire
retained state in addition to producing the session tape and statistical slack.

## 7. Exact full-entropy ratchet and sharpness

When a full uniform source is available, no extractor loss is needed.  Let
`X_j` be uniform on `{0,1}^{c+r}`, sampled after the last exposure and independent
of the history.  For any public deterministic function `Phi`, set

    C_j || R_j = X_j XOR Phi(sid_j,C_{j-1}).                       (12)

For every fixed history, identifier, and old retained state, XOR by the fixed
value of `Phi` is a permutation.  Thus `(C_j,R_j)` is independent uniform,
`delta_j=0`, and Theorem 4 gives

    Pr[Bad] <= min(1, rho + sum_j Gamma_j epsilon_j).              (13)

The new `c+r` uniform bits, not an algebraic refresh of a legacy trapdoor, supply
the post-exposure recovery.

The unit coefficients in (7) are componentwise sharp for the declared black-box
class.  A system that falsely accepts exactly on `CtlFail` attains `rho`; a
maximizing event changes by exactly a statistical distance `delta`; a uniform
`m`-bit target with `L` revealed coordinates attains
`Gamma*epsilon=2^L*2^{-m}`; and independent bad events satisfy
`1-(1-p)^Q=Qp-O(Q^2p^2)`.  This is componentwise/first-order sharpness, not a
claim that one construction simultaneously attains every term.

## 8. Necessity statements

**Entropy-support barrier.** For a fixed public seed, a deterministic map of a
flat source supported on at most `2^k` points to `m>k` bits has statistical
distance at least `1-2^{k-m}` from uniform.  Its output support has size at most
`2^k`, and uniform mass outside that support is the stated quantity.  Averaging
over an independent public seed preserves the lower bound.

**Erasure accounting.** Because the extractor and seed are public, later
exposure of the complete retired input `(C_{j-1},X_j,D_j)` reconstructs
`(C_j,R_j)` exactly.  That exposure must occur only after the relevant decision
and then be charged against future state, or be included in `CtlFail`.

**Rollback.** If recovery restores an exposed retained state together with every
input determining the next update, the next `(C,R)` pair is predictable with
probability one.  A monotone anchor is sufficient but not logically necessary:
adequate entropy generated only after recovery can also defeat restoration.

**Unchecked domain tags.** There is a verification protocol with isolated false
session error `2^{-m}` and sequential error one when a prior true session
releases the accepted token.  Merely displaying a session identifier changes
nothing unless the accepted relation binds it.  This is an existential boundary
for a generic compiler, not a claim about every untagged protocol.

**Per-secret support is not public guessability.** A deterministic response may
have support one after fixing the secret while ranging over an exponentially
large public space as the secret varies.  Hence replacing `Gamma` by the support
of the realized per-secret distribution is invalid.

## 9. Mahadev instantiation and amplified base error

For one fixed BQP no-instance, place the complete randomized verifier tape for
Mahadev's Protocol 7.5—including fresh function-key/trapdoor generation and all
decoder choices—inside `R_j`.  Prefix every outer message with a checked,
nonreused `sid_j`; retain the current trapdoor only until the decision is
terminal.  Mahadev's published fixed-instance theorem supplies
`epsilon_M(lambda)=3/4+negl(lambda)` under its extended trapdoor-claw-free/LWE
assumptions.  Fixed-mode Lemma 1 carries an efficiently generated history of old
sessions and released old trapdoors.  Theorem 4 gives

    Pr[Bad] <= min(1,
                   rho + sum_j delta_j
                       + sum_j Gamma_j epsilon_M(lambda)).        (14)

Because the unamplified error is close to `3/4`, (14) is principally an interface
check and is generally vacuous for many sessions.  Chia, Chung, and Yamakawa
prove a parallel-repetition variant with negligible fixed-no-instance soundness
under quantum-hard LWE for their declared repetition parameters.  Treating the
whole repeated verifier as one base session and deriving **all** repeated keys,
trapdoors, challenges, and decoder coins from `R_j` yields

    Pr[Bad] <= min(1,
                   rho + sum_j delta_j
                       + sum_j Gamma_j epsilon_rep(lambda,t)).    (15)

When `Q` and the `Gamma_j` are polynomially bounded and `rho`, the extractor
losses, and `epsilon_rep` are negligible, the lifetime error in (15) is
negligible.  No independent-repetition claim is inferred; the cited repetition
theorem is the base theorem.

These corollaries regenerate protocol key pairs.  They do not preserve one fixed
public verification key, update one correlated lattice trapdoor in place, or
assert that the published protocols expose a safe leakage API.  Those stronger
claims require new protocol-specific reductions.
