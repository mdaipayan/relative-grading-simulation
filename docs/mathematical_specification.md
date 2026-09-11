# Mathematical Specification

## 1. Score Generation and Marginals

Let $Z \sim \mathcal{N}(0, 1)$, $U \sim \mathcal{U}(0, 1)$, and $B_{\alpha, \beta} \sim \text{Beta}(\alpha, \beta)$.

1. **Normal:** $X = \min(\max(60 + 15Z, 0), 100)$
2. **Compressed Normal:** $X = \min(\max(60 + 5Z, 0), 100)$
3. **Uniform:** $X = 100 \times U$
4. **Right-skewed:** $X = 100 \times B_{2, 5}$
5. **Left-skewed:** $X = 100 \times B_{5, 2}$
6. **Bimodal:** $X = 100 \times [\mathbb{I}(U < 0.5) B_{2, 5} + \mathbb{I}(U \ge 0.5) B_{5, 2}]$

These are synthetic target marginals used for controlled simulation; they are not intended to represent an empirical institutional score distribution.

## 2. Assessment Dependence Model

Components:
$$I = S$$
$$E = \min(\max(a S + (1-a) T, 0), 100)$$
$$X = 0.40 I + 0.60 E$$
where $S, T$ are independent draws from the target marginal.

For target pre-clipping dependence parameter $\rho \in [0, 1)$:
$$a = \frac{\rho}{\rho + \sqrt{1 - \rho^2}}$$
For the primary experiment $\rho = 0.60$, $a = \frac{0.60}{0.60 + 0.80} = \frac{3}{7}$.

The parameter $\rho$ is defined through the analytical equal-variance, pre-clipping construction. Because $E$ is subsequently clipped to $[0,100]$, it should not be interpreted automatically as the realized post-clipping sample correlation.

## 3. Assessment and Eligibility

Internal and external components are combined as:
$$X_i = 0.40 I_i + 0.60 E_i.$$

The external competency threshold is applied to the external component:
$$E_i < CE \implies \text{Grade 8 (F)}.$$

Students failing the external competency requirement are excluded from the relative-grading estimation pool. Exact threshold equality is eligible.

## 4. Grading Methods

Let the seven grade boundaries be ordered from the highest boundary toward the pass/fail boundary.

### M1 — Mean–SD
$$B_j = \mu + k_j s,$$
where $s$ is the sample standard deviation ($ddof=1$) and
$$k=[1.5,1.0,0.5,0,-0.5,-1.0,-1.5].$$
The lower boundary is competency-constrained:
$$B_7^* = \max(\mu-1.5s,CE).$$

### M2 — Percentile
Empirical Type-7 quantiles are evaluated at the study-specific probabilities
$$p=[0.933193,0.841345,0.691462,0.500000,0.308538,0.158655,0.066807].$$
These probabilities are a computational operationalization calibrated to the M1 reference construction; they are not claimed as a universal percentile grading standard.

$$B_7^*=\max(B_7,CE).$$

### M3 — Fixed Distribution / Max–Min
$$\Delta=\frac{X_{\max}-X_{\min}}{7},$$
$$B_j=X_{\max}-j\Delta,$$
with the lower boundary constrained by
$$B_7^*=\max(X_{\min},CE).$$

### M4 — Q-Factor / Constrained
The study uses the following computational operationalization:
$$Q_a=CE, \qquad S_a=X_{\max},$$
$$B_j=Q_a+\frac{7-j}{7}(S_a-Q_a), \quad j=1,\ldots,6,$$
$$B_7=Q_a.$$

These equations are explicitly study-specific and should not be treated as a verbatim transcription of a published Q-Factor algorithm.

### M5 — Median–MAD
$$M=\operatorname{median}(X),$$
$$MAD=\operatorname{median}(|X_i-M|),$$
$$\sigma_R=1.4826\,MAD,$$
$$B_j=M+k_j\sigma_R,$$
$$B_7^*=\max(M-1.5\sigma_R,CE).$$

M5 is a proposed robust comparator for this study, not an established educational grading standard.

## 5. Grade Assignment Convention

Exact boundary equality receives the higher grade ($\ge$ convention). Competency failures are assigned Grade 8 (F) regardless of the relative-grade boundary construction.

## 6. Stability Metrics

For reference grid $x \in \{0,1,\dots,100\}$ across $R$ replications:
$$p_g(x)=\frac{1}{R}\sum_{r=1}^R\mathbb{I}(g_r(x)=g), \quad g\in\{1,\dots,8\},$$
$$\text{stability}(x)=\max_{g\in\{1,\dots,8\}}p_g(x),$$
$$\text{mean\_grid\_stability}=\frac{1}{101}\sum_{x=0}^{100}\text{stability}(x).$$

### Boundary Displacement and RMSE
$$\text{Displacement}=\frac{1}{7R}\sum_{r=1}^R\sum_{j=1}^7|B_{r,j}-B_{ref,j}|,$$
$$\text{RMSE}=\sqrt{\frac{1}{7R}\sum_{r=1}^R\sum_{j=1}^7(B_{r,j}-B_{ref,j})^2}.$$

Additional reported outcomes include reference disagreement, pass-rate variability, grade-count variability, contamination sensitivity, competency override rate, and infeasibility. Their operational definitions are implemented in `src/relative_grading/metrics.py` and documented in the manuscript methods section.
