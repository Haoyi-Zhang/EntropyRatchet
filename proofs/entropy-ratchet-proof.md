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

The following definitions and argument use ordinary trace distance for game
hops and purified-distance smoothing over subnormalized witnesses. Formula (4)
below is the fixed-actual-marginal interface; it is not the optimized-distance
statement of Theorem 6 in arXiv:1002.2436. The proof is included in the article.

```latex
All registers are finite dimensional.  Actual executions are normalized,
including a classical abort flag; we never renormalize on a successful control
check.  Write $\mathcal S_{\leq}=\{\sigma\succeq0:\operatorname{tr}\sigma\leq1\}$,
$\Delta(\sigma,\omega)=\tfrac12\|\sigma-\omega\|_1$, and
\[
 \overline\Delta(\sigma,\omega)=\Delta(\sigma,\omega)
       +\tfrac12|\operatorname{tr}\sigma-\operatorname{tr}\omega|,
 \qquad P(\sigma,\omega)=\sqrt{1-\overline F(\sigma,\omega)^2},
\]
where
$\overline F(\sigma,\omega)=\|\sqrt\sigma\sqrt\omega\|_1+
\sqrt{(1-\operatorname{tr}\sigma)(1-\operatorname{tr}\omega)}$.
Thus $\Delta\leq\overline\Delta\leq P$; on normalized states $\Delta$
is the usual trace distance.  Let
\[
 \mathcal B_P^\eta(\rho)=\{\widetilde\rho\in\mathcal S_{\leq}:
          P(\widetilde\rho,\rho)\leq\eta\},\qquad 0\leq\eta<1.
\]
We use subnormalized purified-distance smoothing, not a normalized
trace-distance ball.  Conditional min-entropy and its smoothing are
\[
 \begin{split}
 H_{\min}(V\mid B)_\sigma
  &=\sup_{\omega_B\succeq0,\,\operatorname{tr}\omega_B=1}
    \sup\{k:\sigma_{VB}\preceq2^{-k}I_V\otimes\omega_B\},\\
 H_{\min}^\eta(V\mid B)_\rho
  &=\sup_{\widetilde\rho\in\mathcal B_P^\eta(\rho)}
                     H_{\min}(V\mid B)_{\widetilde\rho}.
 \end{split}
\]
For classical $V$, the first quantity equals $-\log p_{\rm guess}(V\mid B)$,
with subnormalized guessing mass when necessary
\cite{konig2009,tomamichel2016}.  Dephasing $V$ and any classical history in
$B$ preserves $\rho$, contracts $P$, and preserves each feasible operator
inequality above.  Hence the smoothing witness may be chosen cq without
changing the smooth-entropy supremum.  It need not have the actual marginal $\rho_B$ or
trace one.  The zero operator lies outside these balls for normalized $\rho$
and $\eta<1$.

Let $D$ be an independent uniform seed and $K=h_D(V)\in\bits^m$ for a
two-universal family.  Put $\rho_{KDB}=\mathcal H(\rho_{VB})$, where
$\mathcal H$ appends the seed and hashes.  The interface needed by the
compiler is
\begin{equation}\label{eq:quantum-lhl}
 \Delta\bigl(\rho_{KDB},\tau_K\otimes\tau_D\otimes\rho_B\bigr)
 \leq 2\eta+\frac12\sqrt{2^{m-H_{\min}^\eta(V\mid B)_\rho}},
\end{equation}
where $\tau$ denotes a normalized uniform state.  The ideal state keeps the
\emph{actual} $B$ marginal.  Definition~3 and Theorem~6 of
the arXiv text of Tomamichel et al.\ \cite{tomamichel2011} state distance to a uniform
output with an optimized side-information state.  Their theorem statement
alone does not identify these two distances.  The following argument retains
the fixed-marginal intermediate inequality in their Lemma~4 and proves the
precise interface used here.

\begin{proof}[Proof of Eq.~\eqref{eq:quantum-lhl}]
First take an arbitrary subnormalized cq state
$\sigma_{VB}=\sum_v|v\rangle\langle v|\otimes\sigma_v$ with
$H_{\min}(V\mid B)_\sigma\geq k$.  Choose a normalized $\omega_B$ satisfying
$\sigma_v\preceq2^{-k}\omega_B$; a limiting witness gives the same bound
if the supremum is not attained.  Inverses below are restricted to its support.
Set $M=2^m$, $A_v=\omega_B^{-1/4}\sigma_v\omega_B^{-1/4}$,
$A=\sum_vA_v$, and
$T_{d,z}=\sum_{v:h_d(v)=z}A_v-A/M$.
H\"older's inequality gives
\[
 \left\|\sum_{v:h_d(v)=z}\sigma_v-\sigma_B/M\right\|_1
 \leq \sqrt{\operatorname{tr}(T_{d,z}^2)},
\]
because $\operatorname{tr}\omega_B=1$.  Cauchy--Schwarz over output values
and the seed, followed by two-universality, yields
\[
 \begin{split}
 4\Delta\bigl(\mathcal H(\sigma),\tau_K\otimes\tau_D\otimes\sigma_B\bigr)^2
 &\leq M\,\mathbb E_d\sum_z\operatorname{tr}(T_{d,z}^2)\\
 &=M\sum_{v,w}\bigl(\Pr_d[h_d(v)=h_d(w)]-M^{-1}\bigr)
                         \operatorname{tr}(A_vA_w)\\
 &\leq M\sum_v\operatorname{tr}(A_v^2)
 \leq 2^{m-k}\operatorname{tr}\sigma
 \leq 2^{m-k}.
 \end{split}
\]
For the penultimate step use
$A_v\preceq2^{-k}\omega_B^{1/2}$ and
$\operatorname{tr}(A_v\omega_B^{1/2})=\operatorname{tr}\sigma_v$.
Cross terms have nonpositive coefficients and
$\operatorname{tr}(A_vA_w)\geq0$.
This proves the \emph{unsmoothed own-marginal} bound, including for
subnormalized states; it does not replace $\sigma_B$ by $\omega_B$.

Now choose a cq smoothing witness $\widetilde\rho$ with min-entropy $k$,
where $k$ approaches $H_{\min}^\eta(V\mid B)_\rho$.
Contractivity under hashing and partial trace gives
\[
 \Delta(\mathcal H(\rho),\mathcal H(\widetilde\rho))\leq\eta,
 \qquad \Delta(\rho_B,\widetilde\rho_B)\leq\eta.
\]
The three-term triangle inequality is therefore
\[
 \begin{split}
 \Delta(\rho_{KDB},\tau_K\otimes\tau_D\otimes\rho_B)
 &\leq\Delta(\mathcal H(\rho),\mathcal H(\widetilde\rho))\\
 &\quad+\Delta(\mathcal H(\widetilde\rho),
                  \tau_K\otimes\tau_D\otimes\widetilde\rho_B)\\
 &\quad+\Delta(\widetilde\rho_B,\rho_B)
 \leq 2\eta+\tfrac12\sqrt{2^{m-k}}.
 \end{split}
\]
Let $k$ approach the smooth entropy.  No smoothing witness is renormalized.
\end{proof}
The same argument gives a single $\eta$ if a witness with the asserted
entropy also satisfies $\widetilde\rho_B=\rho_B$.  Such a witness is necessarily
normalized and is an additional marginal-constrained premise, not implied by
ordinary smooth min-entropy.  We use the two-$\eta$ bound throughout.

Let $\mathsf I_j$ replace the first $j$ ratchet outputs by independent uniform
pairs inside the control-safe experiment.  Immediately before $D_j$ is sampled
in $\mathsf I_{j-1}$, $B_{j-1}$ includes the full classical history, identifier,
recovery information, ratchet observations, prover quantum register, and every
other surviving register needed to continue after the update.  Retired inputs
are not silently kept by this continuation.  The identifier is encoded at fixed
length and contributes no entropy.  Conditional on each classical identifier
block, the restricted hash family is two-universal; the preceding calculation
applies to these unnormalized blocks, whose cross terms vanish.  It does not
condition on a favorable history or require a per-history entropy bound.

\begin{definition}[Hybrid entropy ledger]\label{def:fresh}
Use the normalized pre-seed state of $\mathsf I_{j-1}$ (including abort flags),
with $V_j=C_{j-1}X_j$ and the smoothing convention above.  Update $j$ has
parameters $(k_j,\eta_j)$ when $0\leq\eta_j<1$ and
\begin{equation}\label{eq:entropy-ledger}
 H_{\min}^{\eta_j}(C_{j-1}X_j\mid B_{j-1})\geq k_j.
\end{equation}
The seed is independent of this entire state.  For $m_j=c_j+r_j$, set
\begin{equation}\label{eq:delta-j}
 \delta_j=2\eta_j+\frac12\sqrt{2^{m_j-k_j}}.
\end{equation}
\end{definition}
The entropy premise is evaluated in the predecessor hybrid; it is not assumed
to survive earlier game hops without proof.

\begin{lemma}[One update hop]\label{lem:extract-hop}
Under Definition~\ref{def:fresh},
$\Delta(\mathsf I_{j-1},\mathsf I_j)\leq\delta_j$.
\end{lemma}
\begin{proof}
Equation~\eqref{eq:quantum-lhl} compares the actual hashed pair and
$\tau_{C_jR_j}\otimes\tau_{D_j}\otimes\rho_{B_{j-1}}$,
not an optimized historical marginal.  Both branches then apply the same
trace-preserving continuation: split the pair, run $\mathsf{Key}$, and execute
later protocol, leakage, update, and abort operations.  All of its input
registers are present in the comparison.  Trace-distance contractivity proves
the hop.  Padding a stopped execution by an identical absorbing abort state is
trace preserving; no branch is postselected.
\end{proof}

\begin{corollary}[Ratchet semantic freshness]\label{cor:ratchet-freshness}
The control-safe real process $\mathsf I_0$ is within distance at most
$\sum_j\delta_j$ of the control-safe ideal process $\mathsf I_Q$, in which
every $(C_j,R_j)$ is independent uniform when created.
\end{corollary}
\begin{proof}
Apply Lemma~\ref{lem:extract-hop} successively and use the triangle inequality.
\end{proof}

```

In the numbered notation of this note:

    delta <= 2 eta + (1/2) sqrt(2^{m-H_min^eta(V|B)}).             (4)
    H_min^{eta_j}(C_{j-1} X_j | B_{j-1}) >= k_j.                 (5)
    delta_j = 2 eta_j + (1/2) sqrt(2^{m_j-k_j}).                 (6)

Lemma 2 is the one-hop statement above; Corollary 3 is its triangle-inequality
sum. B includes every surviving continuation register. The entropy witness
is never normalized, and the actual B marginal is never replaced by an
optimizing auxiliary marginal. For per-hop target 2^{-tau}, the explicit split
eta<=2^{-tau-2} and k-m>=2 tau is sufficient.

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
`X_j` be uniform on `{0,1}^{c+r}`, sampled after the last exposure and jointly independent of the old secret and complete side information:
`rho_{X_j C_{j-1} B}=tau_{X_j} tensor rho_{C_{j-1} B}`.  For any public deterministic function `Phi`, set

    C_j || R_j = X_j XOR Phi(sid_j,C_{j-1}).                       (12)

Within each classical old-secret/identifier block, XOR permutes a uniform
source tensor the unchanged quantum block. Summing blocks gives independence
without conditioning on a quantum state. Thus `(C_j,R_j)` is independent uniform,
`delta_j=0`, and Theorem 4 gives

    Pr[Bad] <= min(1, rho + sum_j Gamma_j epsilon_j).              (13)

The new `c+r` uniform bits, not an algebraic refresh of a legacy trapdoor, supply
the post-exposure recovery.

Joint independence is essential. With c=r=1, independent uniform C,U,
X=(U,C), and Phi=(0,C), the output is (U,0) and its distance from uniform is
1/2. X is marginally uniform but correlated with C, so it violates the tensor
factorization above. With X a genuinely independent uniform two-bit source the
same transformation has distance zero. Both controls are computed, not constants.


The control and leakage transport coefficients are black-box sharp.
A system that falsely accepts exactly on `CtlFail` attains `rho`; a
maximizing event changes by exactly the actual hybrid distance `d`; a uniform
`m`-bit target with `L` revealed coordinates attains
`Gamma*epsilon=2^L*2^{-m}`; and independent bad events satisfy
`1-(1-p)^Q=Qp-O(Q^2p^2)`. The distance example establishes sharpness of generic
transport, not attainability of the leftover-hash/smoothing estimate `delta_j`
by an admissible extractor/source family. No simultaneous equality is claimed.

## 8. Necessity statements

**Entropy-support barrier.** For a fixed public seed, a deterministic map of a
flat source supported on at most `2^k` points to `m>k` bits has statistical
distance at least `1-2^{k-m}` from uniform.  Its output support has size at most
`2^k`, and uniform mass outside that support is the stated quantity.  Averaging
over an independent public seed preserves the lower bound.

**Erasure accounting (theoretical claim).** Because the extractor and seed are public, later
exposure of the complete retired input `(C_{j-1},X_j,D_j)` reconstructs
`(C_j,R_j)` exactly.  That exposure must be charged to all affected ledgers: current tape leakage
before the decision and retained-state observation for the next update. After
the decision only the retained-state charge remains. Any uncharged exposure is
a control failure.
The separate micro-check recomputes all 2,048 three-bit-input/two-bit-output
affine instances from their public seeds and disclosed complete retired inputs.
It corroborates deterministic reconstruction only, not secure physical erasure.

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
