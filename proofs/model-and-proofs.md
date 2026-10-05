> **Role in the final project.** This note is the companion library of generic
> target, transcript-support, fresh-secret, split-state, and rollback results.
> The final main construction and lifetime theorem are in
> `entropy-ratchet-proof.md`.  The fixed-key trapdoor problem is outside the
> claimed entropy-ratchet scope; it is not an omitted lemma of either note.
>
# Semantic freshness and leakage accounting for sequential verification

This document contains the complete mathematical arguments used by the finite
artifact. They cover the generic fresh-secret sequential compiler, support-sensitive
leakage transport, restricted refreshing, and counterexamples. They do not
instantiate a leakage-resilient evolving trapdoor for a concrete protocol.
All logarithms below are base two. All time bounds are polynomial in the
security parameter when an efficient adversary or decoder is asserted.

## 1. The sequential experiment

A verifier has a classical live state S_t, public descriptor p_t, and a public
epoch tag t. At an epoch it can interact with a prover, output a classical
transcript and decision, and update its state. The update may use fresh private
randomness. Between interactions, a leakage query names an eligible live state
and a classical circuit f with a publicly declared output length. The circuit
returns f(S_t). It does not change the state, its random tape, the acceptance
predicate, or the legal future schedule. The observer may adapt later queries
to the classical history. A quantum observer may retain a private quantum
register; its queries and the leakage answers are still classical.

A challenge after earlier exposures is a later interaction, after those
exposure epochs have finished. An exposure is obtained while the named state
is live, before its erasure. The observer retains only the leakage answer, not
the erased state. Thus the examples never retrieve an erased state from an
unavailable oracle. A restart is an explicit transition whose restored state,
mask, and accounting status must be specified.

Let Bad be a fixed event defined on the original game, such as acceptance of at
least one false statement during a fixed polynomial horizon. The leakage-free
game has the same ordinary protocol, state transitions, horizon, scheduling
interface, and event, but the prover receives no secret-dependent leakage
answers. For every admissible prover B, a soundness hypothesis can bound its
success probability by epsilon_0. This is a full sequential-game hypothesis;
it is not the soundness error of a single isolated interaction.

No claim here identifies recovery of a secret with Bad unless an explicit
procedure maps that secret to a winning interaction.

## 2. Predictable targets

**Definition.** A target Z in {0,1}^m is predictable at eligible epochs
 t_1,...,t_q if, at the time each query is chosen, there is an efficient known
classical circuit D_i such that D_i(p_i,S_{t_i})=Z. The decoder may depend on
that epoch. It may not depend on random coins or information that will become
available only after that query.

**Proposition P1 (distributed disclosure of one target).** Suppose Z is
predictable at these epochs, and b_i leakage bits are allowed at epoch t_i.
If sum_i b_i >= m, Z can be reconstructed by the last exposure with certainty.
If decoder i can fail, and its failure probability in the actual experiment is
at most delta_i, reconstruction succeeds with probability at least
max(0,1-sum_i delta_i). Uniform conditional failure bounds for every attainable
history are a sufficient way to obtain these actual-experiment bounds.

**Proof.** Partition the m coordinate positions into disjoint sets I_i with
|I_i| <= b_i, allowing empty sets, so that their union is all positions. At
eligible epoch i submit the circuit consisting of D_i followed by projection
onto I_i. This is an efficient legal whole-state circuit with the declared
output length. Store the returned coordinates in the appropriate positions.
If every queried decoder is correct, the assembled string is exactly Z. The
probability that any decoder fails is at most the sum of their failure
probabilities, regardless of dependence. Neither an encoding refresh nor
erasure changes the already returned coordinates. QED.

The proposition states a sufficient exposure amount for reconstruction, not a
universal lower bound on the amount necessary. The public descriptor might
already determine Z efficiently, and a nonuniform Z might be guessable with
much less information. Only the uniform-secret experiment in Proposition P3
has the matching exact success curve claimed below.

**Corollary P2 (known deterministic evolution).** Fix a polynomial challenge
epoch T. Suppose the future update circuits U_t,...,U_{T-1}, with all inputs
needed to evaluate them, are known before the exposure at epoch t, and
S_{j+1}=U_j(S_j). Let Z=g(S_T) be an m-bit efficient function of the target
state. Then at epoch t the decoder

    D_{t,T}=g composed with U_{T-1} composed with ... composed with U_t

predicts Z. Consequently, the exposure schedule of P1 reconstructs a future
target even if the raw stored state changes at every update.

**Proof.** Applying the actual transition equations in order gives
D_{t,T}(S_t)=g(S_T). The composition has polynomial length and cost by the
hypotheses. Apply P1 to these epoch-dependent decoders. QED.

Future public randomness that is unknown when the leakage circuit is selected
can invalidate P2. Future secret randomness can also invalidate it. The
corollary does not say that deterministic functions are insecure in all games,
and does not contradict a forward-security definition that protects the past
from a compromise in the present.

**Corollary P2a (persistent semantics).** If all refreshed states decode to the
same m-bit value Z through one known decoder D, then P1 applies with D_i=D.
In particular, when S_t=(R_t,R_t XOR Z), even independently resampled masks do
not prevent a whole-state circuit from outputting coordinates of Z.

**Proof.** Substitute the invariant decoder in P1. In the example, the XOR of
the two shares is Z for every choice of R_t. QED.

**Proposition P3 (exact toy success curve).** Let Z be a uniform m-bit value,
independent of the initial public view. After learning L distinct coordinates,
with no additional information about Z, an optimal one-shot guess succeeds
with probability 2^{-max(m-L,0)}. This is also the maximum possible success
after at most L bits of adaptively chosen, deterministically framed classical
leakage of Z, with no other Z-dependent interface.

**Proof.** For the coordinate strategy each attainable answer fixes
min(m,L) independent coordinates. Exactly 2^{m-min(m,L)} equally likely
secrets remain, so a best guess has the asserted success. For the upper bound,
fix all observer coins. A depth-at-most-L binary decision tree has at most
2^L leaves. At a nonempty leaf, one guess can be correct for at most one of
the 2^m equally likely secrets. Thus success is at most min(1,2^L/2^m).
Randomization is a convex mixture of deterministic strategies and cannot
increase the maximum. If the observer initially has an independent quantum
register, its entire fixed-transcript behavior is still independent of which
secret reaches that transcript; the same one-guess-per-leaf bound holds.
The coordinate strategy attains the bound. QED.

## 3. A lifetime classical-leakage bound

**Proposition P4 (success-probability transport).** Consider the sequential
game of Section 1. Each query has its output length fixed publicly before the
answer, every execution returns at most L leakage bits, and no uncharged
secret-dependent information is conveyed by rejection, termination, length,
timing, or other framing. For every efficient observer A there is an efficient
leakage-free observer B such that

    Pr[G_leak(A): Bad] <= 2^L Pr[G_0(B): Bad].

The right-hand side may of course be truncated at one. The statement permits
quantum polynomial-time observers with classical query and answer channels.
It does not cover coherent queries to a quantum leakage oracle.

**Proof, classical form.** B runs A, forwards ordinary protocol messages, and
answers each length-l leakage request with l independent fair bits. The
scheduling operation itself is implemented through the common, secret-free
scheduling interface. B never computes the true answer and does not test
whether its guess was right.

Fix a real execution path, including the honest random tape, the observer's
random choices, and all ordinary messages. Until B gives an incorrect leakage
answer, its path and the real path coincide. If the real path has a total of
ell leakage bits, the probability that B guesses all answers on that path is
2^{-ell}. Matching paths have the same final acceptance predicate and the same
Bad value, because leakage was read-only and no hidden framing was added.
Summing the probabilities of matching winning paths gives

    Pr[G_0(B): Bad] >= sum_{winning real paths tau} 2^{-|tau|_leak} Pr[tau]
                    >= 2^{-L} Pr[G_leak(A): Bad].

All other paths contribute nonnegative winning probability. B uses one run of
A and L random bits, rather than trying 2^L executions. QED.

**Proof, quantum extension.** Keep the verifier state and the communication
history as classical registers, and the observer's private state as a quantum
register. Each publicly specified answer branch and each subsequent operation
acts linearly by a completely positive map on the unnormalized quantum state.
In the guessed experiment, retain for analysis only the branch whose guessed
answer equals the deterministic leakage answer on the current classical
verifier state. On a matched history, the observer sees the same answer and
therefore applies exactly the same next operation as in the real experiment.
A query of length l multiplies the unnormalized matched block by 2^{-l}.
This statement holds for each classical verifier-state block even when that
block is correlated with the quantum observer. Iterating gives weight
2^{-ell} on each matched terminal block. The Bad measurement is positive;
its probability on additional unmatched blocks is nonnegative. Summing the
matched terminal blocks and using ell <= L proves the same inequality.
No copying, rewinding, or measurement of the observer's private register is
performed by B. QED.

For randomized leakage, its coins may be included in an independent classical
oracle random tape; the same block argument applies. This extension requires
those coins to have no additional state-changing effect.

**Corollary P4a (account every inherited loss).** If the leakage-free theorem
bounds every such B by epsilon_0 <= Q epsilon + delta, then the proved bound
is min(1,2^L(Q epsilon + delta)). It is not automatically
Q 2^b epsilon + delta for a per-epoch allowance b.

**Proof.** Substitute the assumed full-game upper bound in P4 and truncate at
one. The proof provides no justification for removing delta from the
multiplicative factor or replacing a lifetime L by one epoch's allowance.
QED.

If epsilon_0 is only described as negligible, L=O(log lambda) preserves
negligibility by this bound. Larger leakage requires a sufficiently strong
concrete bound on epsilon_0. The guessing factor affects success probability,
not automatically a centered distinguishing or prediction advantage.

## 4. Failure of common substitutions

**Proposition P5 (one-shot soundness is insufficient).** There is an artificial
classical verification protocol with one-session soundness 2^{-m}, perfect
completeness, and two-session false acceptance probability one under a reused
secret. It uses no explicit leakage oracle and can have fresh public tags and
perfect erasure of old representations.

**Proof.** Take the language containing the single true statement 1, with 0 a
false statement. Choose Z uniformly from {0,1}^m. The statement is fixed at the
start of each session. On statement 1 the verifier accepts and returns Z as
part of its terminal transcript. On statement 0 the prover submits an m-bit
response a; the verifier accepts exactly when a=Z and sends no earlier
Z-dependent message. In an isolated false session a is independent of Z, so
success is 2^{-m}. Completeness on 1 is one. In two sequential sessions first
submit 1, retain the returned Z, then submit 0 with response Z. The second
session accepts with certainty. Tags may be unique and checked; no replay is
needed. The stored representation may be independently remasked and erased,
without changing its decoded Z. For m>=2, one exceeds 2*2^{-m}, refuting the
naive two-session union bound from isolated soundness. QED.

This is a deliberately weak generic protocol, not a model or implementation
of Mahadev's verification protocol.

**Proposition P5a (a sufficient conditional premise).** Let F_t be false
acceptance in session t. Suppose for every attainable history h before session
t with no previous false acceptance,

    Pr[F_t | h, no earlier false acceptance] <= epsilon_t.

Then the probability of any false acceptance in Q sessions is at most
sum_{t=1}^Q epsilon_t.

**Proof.** Partition the event of any false acceptance by its first index t.
For each t, average the conditional bound over histories with no previous
false acceptance, multiplying by their probabilities. This bounds the first-
false-acceptance probability by epsilon_t. The first-index events are disjoint;
summing proves the claim. QED.

**Proposition P6 (framing matters).** Counting only the maximum payload length
can make the factor 2^L inapplicable.

**Proof.** Let Z be uniform on four values. A single oracle answer returns,
respectively, the framed strings empty, 0, 1, 1. No payload contains more than
one bit, yet there are three distinguishable answer symbols. After either of
the first two symbols the secret is known; after the last it is one of two
equally likely values. Optimal success is (1+1+1)/4=3/4, exceeding
2*(1/4)=1/2. The missing information was in the secret-dependent length. This
is excluded by publicly declaring an output length before each query. QED.

**Proposition P6a (advantage is not success).** A multiplicative bound on
success does not yield the same bound on prediction advantage.

**Proof.** Before a fair hidden bit is leaked, the best prediction success is
1/2 and its advantage above 1/2 is zero. After that bit is leaked, success is
one and advantage is 1/2. Multiplying the initial advantage by two gives zero,
which is false as an upper bound. Multiplying the initial success by two gives
one, which is valid. QED.

A public tag appended to an already known secret cannot make it unknown:
given (Z,t), the projection onto Z recovers it. This observation makes no
claim about cryptographic domain separation used to prevent cross-protocol
substitution; it only rejects treating a public label as secret entropy.

## 5. A restricted refreshing model

**Proposition P7 (one fresh share per epoch).** Let Z be a fixed m-bit secret,
uniform and initially independent of the observer. At each epoch t sample an
independent uniform R_t and form (R_t,R_t XOR Z). The observer chooses one of
the two shares before observing that epoch's contents; it may choose based on
all previous observations and its own coins. It sees the chosen whole share
and never the other share of that encoding. For any finite number of epochs,
the view is independent of Z, and an optimal final guess succeeds with
probability 2^{-m}.

**Proof.** Fix the observer's coins. Assume inductively that a given previous
view has the same probability for every Z=z. This holds for the empty view.
The choice of share is a deterministic function of that view. Conditional on
that view and any fixed z, R_t is uniform and independent. Either R_t or
R_t XOR z is therefore uniform. Every next observed value has probability
2^{-m}, independent of z. Multiplication establishes the induction. Averaging
over the initially independent coins preserves independence. The posterior
on Z remains uniform at every view, proving the guessing claim. QED.

There is a genuine restriction here: a whole-state leakage circuit can XOR
both shares and violates the permitted access model. This is not a theorem
for arbitrary bounded leakage from two memory parts, nor for leakage during
the refresh computation.

**Proposition P7a (restoration is not fresh sampling).** If the same mask R is
restored, an observer who receives R before a restart and R XOR Z afterward
recovers Z, even when it obtains at most one share in each labelled epoch.

**Proof.** XOR the two observations. A fresh epoch label has no effect on the
identity R XOR (R XOR Z)=Z. QED.

**Proposition P8 (full-compromise recovery needs an unobserved input).** If the
complete state S_t is known, and every subsequent transition is a deterministic
function of that state and inputs that the observer learns before the target
interaction, then the observer can compute the complete target state. Public
inputs may arrive after the compromise; it suffices that they are eventually
known in time to evaluate the transitions.

**Proof.** Induct on the transition index. The first transition is computable
from known S_t and its known input. Its output is therefore known. Repeat for
all transitions up to the target. QED.

The statement concerns full compromise. Under partial exposure, fresh public
randomness unknown at query time can invalidate the prospective decoder
hypothesis of P2. It would be incorrect to infer from P8 that every partially
exposed system requires fresh hidden entropy at every update.

In the independent full-rekey baseline, choose a new uniform m-bit Z' after
old exposure, independently of the complete prior view. Every conditional
posterior on Z' is uniform, so its optimal guessing probability is 2^{-m}.
That baseline changes the semantic secret; it is not a demonstration that a
fixed verification trapdoor can be safely reused.

## 6. Exact finite corroboration

The decision-tree enumerator directly lists every predicate at every node.
For an independent count, fix N equally likely secrets and let H(k,d)[j] count
full depth-d trees with j nonempty reachable leaves when k secret values reach
the root. Then

    H(k,0)[j] = 1 if j = 1_{k>0}, and 0 otherwise;
    H(k,d)[j] = 2^{N-k} * sum_{a=0}^k binom(k,a)
                  * sum_{u+v=j} H(a,d-1)[u] H(k-a,d-1)[v].

To prove the recurrence, choose which a of the k reachable values go left.
The root predicate has N-k unrestricted values on unreachable inputs. The
left and right full subtrees are independent labelled choices, with u and v
nonempty leaves respectively. Multiplying and summing accounts for every
root predicate and every pair of subtrees exactly once, including k=0.
This proves the second calculation's histogram formula.

For the two-bit prospective-target example, there are 4^4 maps at each of two
updates. Hence there are 65,536 update sequences and 262,144 initial-state
paths. At the first exposure query the low bit of g(f(S_0)); at the second
query the high bit of g(S_1). Together they recover S_2 for every path. Among
all paths, exactly 196,608 have S_2 different from S_0: for a fixed S_0 and f,
the value g(f(S_0)) is uniform as g ranges over all maps, and three of four
values differ from S_0. Neither injectivity nor uniformity of a particular
map's output is assumed.

The remaining computations compare joint observation masses with the formulas
proved above. A passed finite computation means those enumerated classical
instances agree; it is not a machine-checked proof for unbounded parameters.

## 7. Classical–quantum support and causal leakage transport

Let `T` and `Z` be classical and `E` quantum.  If the joint transcript `Z` has
support at most `K`, then

    p_guess(T | E,Z) <= K p_guess(T | E),

or equivalently `H_min(T|E,Z) >= H_min(T|E)-log K`.

**Proof.**  For each transcript value `z`, let `{M_t^z}` be an optimal
conditional guessing measurement.  The averaged operators
`N_t=(1/K) sum_z M_t^z` form a measurement without `Z`.  In its success
probability retain only the positive diagonal terms whose measurement label
matches the actual `z`; this obtains at least `1/K` of the success with `Z`.
QED.

This statement is a joint-state entropy chain rule.  It is not by itself an
online simulator for an adaptive protocol.  For the latter, fix the public
ordinary transcript and leakage queries as they arise.  A **public causal
guesser** `q` samples each next response or termination symbol from a public,
efficient conditional distribution depending only on the already visible state
and guessed response prefix.  For a complete legal path `z`, define

    Gamma(q) = max_{z legal} 1/q(z),

with positive probability on every legal real path.

**Theorem P9a (causal leakage transport).**  For every efficient observer `A`
using a classical read-only leakage interface with public causal guesser `q`,
there is a leakage-free observer `B` such that

    Pr[G_leak(A):Bad] <= Gamma(q) Pr[G_0(B):Bad].

The result permits a quantum observer but only classical queries and answers.

**Proof.** `B` forwards ordinary messages and samples leakage replies from `q`.
Couple the real and simulated experiments on all verifier/prover randomness.  If
the guessed prefix equals a real path `z`, the same next query and quantum
operation occur.  The whole path matches with probability `q(z)`; on a matched
path the read-only interface leaves the verifier state and event unchanged.
Summing the matched positive subnormalized cq blocks gives at least a
`1/Gamma(q)` fraction of the real bad-event probability.  No private register is
measured or rewound.  QED.

Local uniform sampling from finite public conditional alphabets gives

    Gamma(q) <= max_z product_i |Y_i(z_{<i})|.

Fixed binary framing of total length `L` gives `Gamma<=2^L`.  If a complete
public framing tree is fixed independently of the secret and unexamined private
branches and its terminal-descendant counts are computable online, sampling a
child in proportion to its leaf count makes every leaf uniform and gives the
optimal factor equal to the number of leaves.  A per-secret or realized support
count is not a substitute: a deterministic response has support one after
fixing the secret but may range over the entire secret space publicly.

## 8. Fresh-secret sequentialization

Let `Pi` be a protocol with public setup `pp`.  Immediately before session `j`,
the verifier samples fresh coins `r_j` and runs

    (a_j,S_j) <- KeyGen(pp,mu_j;r_j),

where `S_j` is the complete current secret state.  Sessions are nonoverlapping:
the decision of session `j` is terminal before the next secret state is
generated.  Completed-session state may be revealed in full but is never used
to verify a later session.  Current leakage has a public causal guesser with
factor `Gamma_j`.

**Definition (matching prefix-robust one-session soundness).**  Before `r_j` is
sampled, an efficient prefix generator may create the entire prior cq history
and a current mode only according to the declared mode-selection rule.  After
receiving `a_j`, a continuation interacts in the current session.  With no
current secret leakage, false acceptance is at most `epsilon_j`.

For an externally fixed mode, ordinary soundness against every QPT prover lifts
to such efficient prefixes by combining the generator and continuation into one
prover.  If the prefix chooses a mode correlated with its quantum register,
pointwise theorems for fixed modes do not automatically sample the conditional
register; the chosen-mode two-stage property must be proved directly.

**Definition (semantic-freshness error).** Compare the real key-source process
to an ideal process that samples each `r_j` independently after the pre-session
view is fixed.  The semantic-freshness error is at most `nu` if every admissible
sequential adversary induces terminal cq states at trace distance at most `nu`.
Exact independent key generation has `nu=0`; a coupling that disagrees only
with probability `nu` is sufficient.

**Theorem P10 (fresh-secret sequentialization).** If session `j` has matching
prefix-robust soundness `epsilon_j`, current causal factor `Gamma_j`, and the key
source has semantic-freshness error `nu`, then

    Pr[Bad] <= nu + sum_{j=1}^Q Gamma_j epsilon_j.

Full exposure of every completed-session state is allowed.

**Proof.** First use the ideal independent key source.  Let `F_j` be the event
that session `j` is the first false-accepting session.  The `F_j` are disjoint.
A one-session adversary straight-line simulates the earlier sessions and old
state releases, preserving the sequential adversary's quantum register.  The
current tape is independent and unsampled, so this is a legal prefix.  It
embeds the current base game and answers current leakage using the public causal
guesser.  Theorem P9a gives

    Pr_ideal[F_j] <= Gamma_j epsilon_j.

Sum the disjoint first-bad events.  Trace distance between the real and ideal
terminal states changes the probability of `Bad` by at most `nu`.  QED.

**Corollary P10a (fixed public modes).** If the mode of each session is fixed
before its prefix generator, ordinary fixed-mode soundness lifts by the
combination argument above and Theorem P10 applies.  For modes chosen from prior
history, use a base theorem that explicitly covers that selection rule; do not
condition a fixed-mode theorem on a potentially hard-to-sample quantum state.

**Corollary P10b (sequential source hybrids).** If replacing the current
key-source output by independent ideal output changes the cq state by at most
`delta_j` in every predecessor hybrid, then `nu<=sum_j delta_j`.

**Corollary P10c (direct correlated-lineage certificate).** Alternatively, if a
protocol-specific reduction proves for every reachable safe history `h`

    Pr[F_j | h] <= beta_j(h),

then `Pr[Bad] <= sum_j sup_h beta_j(h)`.  Such a certificate may avoid claiming
that correlated keys are close to an independent product source, but it must
simulate the actual history and leakage interface.

## 9. Tightness, persistent targets, and rollback

Define Target_m as the protocol that samples a uniform m-bit target and accepts
a false claim exactly when the adversary outputs that target. With no leakage,
success is 2^{-m}. Revealing L fixed target coordinates makes success
2^{-(m-L)} until saturation, attaining the factor 2^L in P10.

**Proposition P11 (matched any-session events).** Let m>=1, 0<=L<=m,
Q>=1. Each session allows at most L classical reads of target coordinates and
one full-target guess. Every wrong guess produces public rejection. Success is
at least one correct guess over all sessions. For independent uniform fresh
targets the optimum is

    p_fresh = 1 - (1 - 2^{L-m})^Q.

For one uniform persistent target the optimum is

    p_persistent = min(1, 2^{-m} sum_{j=1}^Q 2^{jL}).

**Proof.** On a surviving session-j path all previous guesses were rejected.
There are at most 2^{jL} binary-answer paths, and a full guess can newly win only
one target on each. Sum over sessions and truncate at the 2^m possible targets.
Randomization is a convex mixture, so it cannot improve this deterministic bound.

For L=0, use distinct guesses. For L>0 and QL>=m, read all coordinates by the
last session. For L>0 and QL<m, set a=2^L and read L successive coordinates per
session, yielding a full a-ary tree through depth Q. Assign distinct target
values to all guess nodes (depths 1..Q), upwards from depth Q. The subtree of a
depth-j node has sum_{i=0}^{Q-j} a^i < 2 a^{Q-j} nodes, whereas it contains
2^{m-jL} >= 2 a^{Q-j} target values. After descendants are assigned, an unused
target remains for this node. Guess its assigned value. The guesses are globally
distinct and all lie below their node, so their union attains sum_j 2^{jL} wins.
In the fresh case each new target is uniform independently of prior rejection;
its optimum is 2^{L-m}, giving the product failure formula. QED.

The **final-only no-feedback experiment**, which forbids earlier guesses, is a
different experiment: its persistent optimum is 2^{-max(m-QL,0)}. It is retained
as an explicitly named baseline in JSON/CSV, not as the lifetime curve.

**Bellman audit.** The exhaustive solver stores the remaining uniform candidate
set S, known-coordinate mask K, sessions q, and current reads l. A coordinate
read partitions S and sums the child optima; a guess x wins one candidate and
continues on S minus {x}, q-1, and a reset read budget. Empty sets have value
zero, and q>=|S| has value |S| using distinct guesses. Other values are maxima
over all legal actions. Induction on (q,l) proves optimality. A separate solver
restricts reads to a prefix schedule and optimizes guesses on tuple sets; its
lower bound attains the proven upper bound. It imports no production solver.

The ordinary union factor is asymptotically tight: for fixed Q and small
single-session epsilon, 1-(1-epsilon)^Q=Q epsilon-O(Q^2 epsilon^2).

**Proposition P12 (rollback makes the freshness term necessary).** Expose an
old uniform m-bit target. A genuinely regenerated independent target is guessed
with probability 2^{-m}. Restoring the exposed target is guessed with
probability one. If restoration occurs with probability nu and ideal fresh
sampling otherwise, success is nu+(1-nu)2^{-m}; the real and ideal key-source
processes admit a coupling that disagrees with probability nu.

**Proof.** The exposed old value is exactly the restored target on the rollback
branch. On the fresh branch it is independent of the new uniform target. The
mixture formula and coupling are immediate. QED.

These witnesses do not show that every construction reaches all loss terms at
once. They show that a black-box theorem cannot remove the support factor, the
session sum, or the additive freshness error without a premise that excludes
the corresponding witness.

## 10. Additional exact corroboration

Eight frozen cases enumerate 99,404 fresh-target tuples. Persistent any-session
values include 3/4 at (m,L,Q)=(3,1,2) and 7/16 at (5,1,3). Boundary cases include
L=0,Q=3; Q=1; full revelation; and saturation by repeated guesses alone. The
separate four-bit rollback example gives 1/16 after regeneration and 1 after
restoration. Numerical output and all tables are generated from these domains.
Finite agreement checks implementation, not the unbounded proof of P11.
