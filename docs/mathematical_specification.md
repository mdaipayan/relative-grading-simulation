# Mathematical Specification

## 1. Score Generation and Marginals

Let $Z \sim \mathcal{N}(0, 1)$, $U \sim \mathcal{U}(0, 1)$, and $B_{\alpha, \beta} \sim \text{Beta}(\alpha, \beta)$.

1. **Normal:** $X = \min(\max(60 + 15Z, 0), 100)$
2. **Compressed Normal:** $X = \min(\max(60 + 5Z, 0), 100)$
3. **Uniform:** $X = 100 \times U$
4. **Right-skewed:** $X = 100 \times B_{2, 5}$
5. **Left-skewed:** $X = 100 \times B_{5, 2}$
6. **Bimodal:** $X = 100 \times [\mathbb{I}(U < 0.5) B_{2, 5} + \mathbb{I}(U \ge 0.5) B_{5, 2}]$

## 2. Assessment Dependence Model

Components:
$$I = S$$
$$E = \min(\max(a S + (1-a) T, 0), 100)$$
$$X = 0.40 I + 0.60 E$$
where $S, T$ are independent draws from the marginal distribution.

For target correlation $\rho \in [0, 1]$:
$$a = \frac{\rho}{\rho + \sqrt{1 - \rho^2}}$$
For primary experiment $\rho = 0.60$, $a = \frac{0.60}{0.60 + 0.80} = \frac{3}{7}$.

## 3. Metrics

### Stability on Integer Grid
For reference grid $x \in \{0, 1, \dots, 100\}$ across $R$ replications:
$$p_g(x) = \frac{1}{R} \sum_{r=1}^R \mathbb{I}(g_r(x) = g), \quad g \in \{1, \dots, 8\}$$
$$\text{stability}(x) = \max_{g \in \{1..8\}} p_g(x)$$
$$\text{mean\_grid\_stability} = \frac{1}{101} \sum_{x=0}^{100} \text{stability}(x)$$

### Boundary Displacement and RMSE
$$\text{Displacement} = \frac{1}{7 R} \sum_{r=1}^R \sum_{j=1}^7 |B_{r, j} - B_{\text{ref}, j}|$$
$$\text{RMSE} = \sqrt{\frac{1}{7 R} \sum_{r=1}^R \sum_{j=1}^7 (B_{r, j} - B_{\text{ref}, j})^2}$$
