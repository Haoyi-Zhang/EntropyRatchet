# Fixed-actual-marginal extraction

This self-contained proof is the manuscript's extraction interface. The source
is Tomamichel, Schaffner, Smith and Renner, *Leftover Hashing Against Quantum
Side Information*, arXiv:1002.2436, Sections II and III, Definition 3, Lemma 4 proof
and Theorem 6 (preprint numbering). The published record is IEEE Transactions
on Information Theory 57(8), 5524–5535 (2011), DOI 10.1109/TIT.2011.2158473.

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

```

## Executable evidence and its limits

`src/extractor_contract.py` computes rational budgets, a classical optimized
versus fixed marginal diagnostic, and a noncommuting qubit-side witness at
nonzero purified-distance smoothing. The second calculator uses an analytic
two-state formula for the cq example. These are diagnostics, not an entropy
optimizer, quantum-device experiment, or mechanized general proof. No check
at eta=0 establishes the smoothing step. The general proof is in the article.
