# Frozen 22-paper structural calibration

## Purpose and reading standard

This record compares the manuscript with twelve closest papers, five
field-defining or demonstrably influential papers, and five adjacent-model
papers.  The calibration is **structural**, not a claim of line-by-line proof
certification: for every selected work the accessible full text or primary
scholarly record was followed through its motivating problem, model and
quantifier order, principal theorem statements, proof architecture, assumptions,
and stated limitations or conclusion.  Bibliographic details and permanent
locators are stored in `literature_matrix.csv`; external paper bytes are not
redistributed.

The review asks the same questions of every paper:

1. What object and adversarial interface does the result define?
2. What is the strongest theorem actually proved, and under which assumptions?
3. What proof mechanism carries the central claim?
4. Which part is genuinely closest to the entropy-ratchet paper?
5. Which guarantee cannot be imported without a new proof?

This is an internal, single-process calibration.  It is not independent peer
review, a citation audit by the original authors, or a substitute for checking
every lemma before external publication.

## A. Twelve closest papers

| Key | Model and principal result | Proof architecture inspected | Delta retained in this manuscript |
|---|---|---|---|
| `mahadev2018` | A classical verifier forces standard/Hadamard measurements and verifies BQP under quantum-hard LWE; the published base protocol is a one-execution interactive verifier with protocol-specific trapdoor state. | Trapdoor claw-free functions, measurement protocol, reduction from accepted deviations to the measurement soundness statement, and the final verification wrapper. | Supplies the motivating base verifier and its one-session random tape. It does not provide arbitrary verifier-state leakage, terminal trapdoor release, crash recovery, or a fixed-key ratchet theorem. |
| `chia2020` | Parallel repetition reduces Mahadev-style soundness and later transformations target fewer rounds and an efficient verifier under additional models and assumptions. | Repetition analysis, Fiat--Shamir/QROM step, and succinct-verifier construction. | Establishes that amplification and efficiency are separate base-protocol obligations. The ratchet paper does not re-prove or silently assume its repetition theorem. |
| `alagic2020` | Moves a Mahadev-derived verifier toward non-interactive and zero-knowledge forms using offline setup, repetition, Fiat--Shamir in the QROM, NIZK, and FHE. | Instance-independent first message, repetition, random-oracle transform, and zero-knowledge compilation. | Changes interaction and privacy, not the exposure model of the verifier's evolving secret memory. Its setup/key distribution cannot be read as a generic state-exposure guarantee. |
| `bartusek2022` | Gives succinct classical verification with polylogarithmic verifier work/communication under post-quantum iO and LWE, including a modular re-analysis of Mahadev's protocol and compressed public keys. | Modular base proof, compressed-key abstraction, and succinct argument composition. | Demonstrates that public-key compression and succinctness are protocol-specific. It does not discharge retained-state entropy, rollback, or current-leakage support. |
| `bartusek2023` | Constructs obfuscation for pseudo-deterministic quantum circuits and upgrades a verification component to a reusable, publicly decodable oracle-style interface. | Publicly verifiable CVQC for partitioning circuits, reusable functional commitment, and obfuscation composition. | Prevents any claim that reusable verification itself is new. Its specified oracle interface is not arbitrary read access to hidden verifier implementation state. |
| `barhoush2026` | Proves a quantum black-box separation for non-interactive CVQC of QMA from falsifiable assumptions, conditional on an appropriate QMA--QCMA gap problem. | Meta-reduction/separation framework and oracle evidence for the gap premise. | Constrains claims about non-interactivity and black-box assumptions, but neither implies nor refutes a sequential state-ratchet theorem with fresh entropy. |
| `bartusek2026structure` | Defines tests of non-commutation and derives classical-communication key agreement, and with one-way functions oblivious transfer, for broad parameter ranges; also develops post-quantum amplification tools. | Reduction from verifier tests to cryptographic primitives, hard-core measure theorem, and interactive XOR lemma. | Shows that classical tests of qubit behavior can encode strong cryptographic structure. The paper's conclusion is not a leakage-resilient update theorem and does not justify evolving a trapdoor lineage after exposure. |
| `tomamichel2011` | Proves leftover hashing against quantum side information, including two-universal and almost-two-universal families. | Collision/conditional entropy analysis and conversion to trace-distance-from-uniform bounds. | Its fixed-marginal intermediate calculation motivates the article's self-contained hop; the optimized-side theorem is not used verbatim as an actual-marginal statement. The contribution is the entropy ledger and sequential composition, not a new extractor. |
| `dziembowski2008` | Develops leakage-resilient cryptographic constructions under explicit leakage models, separating bounded observation from standard black-box key secrecy. | Leakage game, entropy/hardness accounting, and construction-specific reductions. | Establishes that leakage security requires a mechanism-specific invariant. It does not yield verifier soundness merely from a changing state representation. |
| `davi2010` | Defines leakage-resilient storage as a randomized encoding secure against declared classes of leakage functions, including split-memory restrictions. | Encoding/decoding definition, leakage class, split-state constructions, and bounded leakage argument. | Closest storage abstraction for retained state. Storage privacy is not sequential false-acceptance soundness, and its split-state premises are not assumed by the general ratchet theorem. |
| `andrychowicz2012` | Gives a simpler linear-operation refresh protocol for leakage-resilient storage under the same split-state, bounded independent leakage, and leak-free-component assumptions as the prior construction it improves. | Inner-product extractor refresh algebra and preservation of the encoded secret. | Demonstrates a genuine correlated-state refresh theorem under narrower hardware/leakage interfaces. The paper's one-share theorem is intentionally separated from the entropy-injection compiler. |
| `cakan2024` | Protects encryption/signature secrets encoded as quantum states against unbounded rounds of LOCC-style leakage. | Quantum storage/LOCC security definitions and cryptographic constructions. | Shows that “unbounded leakage” is meaningful only relative to a restricted quantum leakage interface. It does not subsume the classical read-only state and post-exposure entropy model here. |

## B. Five influential foundations

| Key | Foundational role | Structural feature imported | Boundary preserved |
|---|---|---|---|
| `regev2009` | Introduces LWE with a worst-case lattice reduction and a public-key encryption application. | Exact assumption direction and distinction between the LWE problem and a protocol using it. | LWE hardness alone is not a state-update invariant; no fixed-trapdoor evolution claim is made here. |
| `gentry2008` | Constructs lattice trapdoors and associated preimage-sampling cryptographic tools from hard lattice problems. | Trapdoor-generation and sampling interface. | A trapdoor can be regenerated from fresh coins, but safe in-place refresh or exposure tolerance requires a separate proof. |
| `konig2009` | Gives the operational interpretation of cq conditional min-entropy as optimal guessing probability. | The `H_min=-log p_guess` interface used by the retained-state ledger. | Operational entropy does not assert that an implementation supplies fresh entropy or erasure. |
| `bellare1999` | Formalizes forward-secure signatures with a fixed public key and periodically updated signing key, protecting past signatures after later compromise. | Period-indexed game and update direction. | The protection direction is opposite to the paper's main concern: later verification after earlier exposure. The terminology is therefore compared, not transferred. |
| `herzberg1995` | Introduces proactive secret sharing against a mobile adversary by periodically refreshing distributed shares while preserving the secret. | Time-sliced compromise model, share refresh, and erasure/clean-period intuition. | Requires distributed components and threshold assumptions not present in the generic verifier compiler. |

## C. Five adjacent-model papers

| Key | Adjacent guarantee | Why it informs the paper | Why it does not subsume the theorem |
|---|---|---|---|
| `canetti2001` | Universal composability under an explicit environment and ideal functionality. | Forces adversarial history, interfaces, and composition claims to be stated rather than inferred. | The entropy-ratchet theorem proves a nonconcurrent sequential game, not UC realization. |
| `unruh2010` | Extends universal-composition reasoning to quantum adversaries and quantum protocol executions. | Confirms that retained quantum side information and no-cloning/rewinding constraints matter. | No ideal functionality or concurrent composition is proved in the current manuscript. |
| `hallgren2011` | Establishes classical secure-computation feasibility against quantum attackers under post-quantum assumptions and analyzes which classical proof techniques survive. | Motivates a straight-line reduction and explicit handling of quantum adversarial state. | General post-quantum protocol feasibility does not price verifier-state leakage or produce fresh key coins. |
| `dodis2002` | Key-insulated cryptography updates per-period user keys with help from a protected component while retaining a public-key identity. | Provides a clean example of separating online state from protected update material. | Its helper/device and exposure game are construction-specific; it is not a black-box verifier-soundness compiler. |
| `dodis2003` | Intrusion-resilient encryption jointly evolves user and base state to recover from repeated compromise. | Highlights the need to specify operation order, separability, and which component is authoritative after recovery. | Encryption indistinguishability and two-component update assumptions do not imply sequential verification soundness. |

## Cross-paper narrative and design matrix

| Pattern | Closest papers | Influential papers | Adjacent papers | Manuscript organization |
|---|---|---|---|---|
| Motivating problem | A concrete verification primitive and its setup/interaction limits | A sharply oriented exposure goal | A composition or compromise-recovery model | Begin with the temporal question: which random variable still protects the next decision after a snapshot or release? |
| General principle | Protocol-specific soundness, leakage invariant, or extractor theorem | Operational entropy or period-indexed key evolution | Environment/history and separated state | Separate retained-state entropy (`J`), current causal leakage factor (`Gamma`), and control failure (`rho`). |
| Proof architecture | Reductions and hybrids around one declared interface | Reduction from a precise game or operational quantity | Simulation/straight-line composition | Safe-process coupling, predecessor-hybrid extraction, prefix lifting, first-bad-session partition. |
| Tightness/negative evidence | Barriers or interface-specific counterexamples | Directional compromise examples | Non-composability outside the model | Flat-source support barrier, reconstruction after erased-input exposure, rollback witness, unchecked-tag replay witness. |
| Practical connection | Explicit protocol random tape/setup assumptions | Key-update or entropy interpretation | Recovery and component separation | Fresh-key and amplified Mahadev corollaries plus an instantiation certificate; no fixed-key claim. |
| Evaluation/artifact | Mostly proof-driven; some papers have no executable artifact | Not generally applicable | Not generally applicable | Two exact small-domain implementations corroborate arithmetic and counterexamples but are never presented as quantum evidence. |
| Narrative sequence | Problem -> model -> theorem -> construction/limitations | Definition -> main theorem -> consequences | Model -> simulator/reduction -> scope | Problem -> closest-work separation -> state model -> failures -> transport -> compiler -> necessity -> finite checks -> instantiation. |
| Figures/tables | Sparse, role-specific | Mostly formal | Mostly formal | Two semantic TikZ diagrams and generated booktabs tables only where they carry a proof or audit role. |
| Bibliography use | Concentrated around the exact interface | Foundational theorem support | Boundary-setting | 84 cited references, with the 22-paper calibration distinguished from claim-level screening. |

## Novelty conclusion after calibration

The literature does **not** support any of the following broad claims: that
classical quantum verification was previously one-shot only; that reusable
verification is new; that a public epoch tag creates freshness; that leakage-
resilient storage automatically gives verifier soundness; or that LWE/trapdoor
hardness by itself permits safe in-place key evolution.

The defensible scoped delta is the following theorem interface and proof:

- a control-safe coupling prices undeclared rollback/erasure failure once, without
  conditioning on a rare event;
- a predecessor-hybrid cq min-entropy ledger converts a retained state plus
  genuinely post-exposure entropy into fresh base-verifier coins;
- observations of the retained state and leakage from the current base state are
  accounted for by different parameters (`J_j` and `Gamma_j`);
- ordinary one-session soundness is lifted automatically only for a mode fixed
  before the prefix; chosen-mode histories require the matching two-stage base
  theorem;
- the final lifetime loss is accompanied by componentwise tight examples and
  information-theoretic barriers for missing entropy, erasure, rollback, and
  unchecked domain binding.

This delta is complete for the stated entropy-ratchet compiler.  It is **not** a
claim of a new LWE trapdoor-refresh mechanism, a fixed-public-key Mahadev
lineage, coherent leakage security, concurrent composition, or universal
composability.
