# Scientific Protocol — Relative Grading Reproducibility Simulation

This protocol specifies the experimental design, constraints, and mathematical models for:
**“Robust Relative Grading in Engineering Education: Effects of Cohort Size, Score Distributions, Competency Constraints, and Score Perturbations.”**

## 1. Primary Factorial Experiment (Step 7D)

- **Total experimental cells:** 2,100
- **Replications per cell:** $R = 1,000$
- **Total cohort evaluations:** 2,100,000
- **Cohort sizes ($N$):** $10, 15, 20, 25, 30, 40, 50, 75, 100, 200$ (10 levels)
- **Marginal distributions:**
  1. Normal: $\text{clip}(60 + 15Z, 0, 100)$
  2. Compressed Normal: $\text{clip}(60 + 5Z, 0, 100)$
  3. Uniform: $U(0, 100)$
  4. Right-skewed: $100 \times \text{Beta}(2, 5)$
  5. Left-skewed: $100 \times \text{Beta}(5, 2)$
  6. Bimodal: 50/50 mixture of $100 \times \text{Beta}(2, 5)$ and $100 \times \text{Beta}(5, 2)$
- **Competency thresholds ($CE$):** $10\%, 15\%, 20\%, 25\%, 30\%$
- **Controlled score contamination ($\epsilon$):**
  - $\epsilon \in \{0\%, 1\%, 5\%, 10\%\}$
  - When $\epsilon > 0$: directions are Lower ($U(0, 5)$) and Upper ($U(95, 100)$).
  - Number of contaminated students: $m = \text{round}(\epsilon \times N)$.
- **Assessment score construction:**
  - $S, T \sim \text{target distribution}$ (independent)
  - $I = S$
  - $E = aS + (1-a)T$, $a = 3/7$ ($\rho \approx 0.60$)
  - $X = 0.40 I + 0.60 E$
- **External competency constraint:**
  - $E_i < CE \implies F$ (Grade 8).
  - Ineligible students ($E_i < CE$) are excluded from the relative-grading estimation pool.
- **Reference cohort:** $N_{\text{ref}} = 100,000$, evaluated on integer score grid $x = 0, 1, \dots, 100$.
- **Exact boundary convention:** Exact boundary receives the higher grade ($\ge$ rule).

## 2. Focused Rho Sensitivity Experiment (Step 8B)

- **Total cells:** 900
- **Replications per cell:** $R = 500$
- **Correlation parameter ($\rho$):** $0.0, 0.3, 0.6, 0.8, 0.9$
- **Competency threshold:** $CE = 20\%$
- **Contamination conditions:** Clean, 5% lower-tail, 5% upper-tail
- **Mixture parameter:** $a = \frac{\rho}{\rho + \sqrt{1 - \rho^2}}$

## 3. Five Grading Methods

1. **M1 — Mean–SD:** $B_j = \mu + k_j s$ ($ddof=1$), $k = [1.5, 1.0, 0.5, 0, -0.5, -1.0, -1.5]$, $B_7^* = \max(\mu - 1.5s, CE)$.
2. **M2 — Percentile:** Empirical Type-7 quantiles with $p = [0.933193, 0.841345, 0.691462, 0.500000, 0.308538, 0.158655, 0.066807]$, $B_7^* = \max(B_7, CE)$.
3. **M3 — Fixed Distribution / Max–Min:** $\Delta = (X_{\max} - X_{\min}) / 7$, $B_j = X_{\max} - j\Delta$, $B_7^* = \max(X_{\min}, CE)$.
4. **M4 — Q-Factor / Constrained:** $Q_a = CE$, $S_a = X_{\max}$, $B_j = Q_a + \frac{7-j}{7}(S_a - Q_a)$, $B_7^* = Q_a = CE$.
5. **M5 — Median–MAD:** $M = \text{median}(X)$, $MAD = \text{median}(|X - M|)$, $\sigma_R = 1.4826 \times MAD$, $B_j = M + k_j \sigma_R$, $B_7^* = \max(M - 1.5\sigma_R, CE)$.
