# Findings

Working log of the re-analysis of Nam & Portes (2023, IZA DP 16472),
*Migration and Productivity in the UK*. Methodology in `METHODOLOGY.md`;
reproducible scripts in `scripts/`.

- `scripts/analyze.py` — builds the panel and recreates Table 1.
- `scripts/diagnostics.py` — functional-form / linear-model assumption checks.

Run both with `uv run python scripts/<name>.py`. The merged panel is written to
`data/processed/analysis_panel.csv`.

---

## 1. Table 1 recreation

**Setup.** ONS real output per job (`OpJ (CVM)`, 2018 GBP) regressed on EU and
non-EU payrolled employment **shares** (HMRC PAYE/MWS), expressed as **fractions
of total employment (0–1)**, merged on region × industry × year. 12 ITL1 regions,
SIC sections (HMRC aggregated to ONS groupings), 2014–2019, real estate excluded.

**Result — the headline replicates.**

| coefficient | (1) Levels no FE | (2) Levels+FE | (3) Levels+FE+wt |
|---|---|---|---|
| non-EU share — paper | +0.079 | +2.961*** | +1.471*** |
| non-EU share — ours | +0.078 | +2.260*** | +2.188*** |
| EU share — paper | −0.033 | −0.371 | −0.040 |
| EU share — ours | −0.033 | −0.666** | +0.061 |

- Column (1) matches to 3 decimals (EU −0.033/−0.033, non-EU +0.079/+0.078,
  R² 0.979/0.978).
- The central finding holds: **+1pp non-EU employment share ≈ +2–3% productivity**,
  significant at p<0.01 in the FE levels specs.
- EU share is small and negative; not robustly significant (matches the paper's
  "small negative or null").
- First-difference specs (cols 4–5) are the weakest match — FD discards most of the
  signal over a 6-year panel, so the non-EU coefficient stays positive but loses
  significance.

**Things we had to infer / reconcile:**

- **Shares are fractions (0–1), not percentages.** The methodology table says "%",
  but the coefficient sizes (+2.96 → "~3% per +1pp") only parse as fractions. Using
  0–100 percentages made coefficients 100× too small.
- **Productivity measure = `OpJ (CVM)`** (real, 2018 GBP), not the nominal
  `OpJ (value)`.
- **R² gap in FE specs is a reporting convention.** Our R² (~0.99) includes the FE
  dummies; the paper reports within/demeaned R². Column 1 (no FE) matches exactly.

---

## 2. The "16th industry" / observation count

- Paper says "16 industries … 1152 observations"; line 245 also says "6 industries"
  (a typo — 12×6×6=432 ≠ 1152; 12×**16**×6 = 1152). Line 315 confirms 192
  region-sectors = 12×16.
- The ONS workbook has **exactly 16 individual SIC section-groups** (excluding the
  aggregates `TOTAL` and `G_J_L_T`). **Real estate (L) is the 16th.**
- So "16 industries / 1152 obs" is the **full grid including real estate**. The
  regressions exclude real estate (imputed-rent distortion, ~£470k/job), giving
  **15 industries / 1080 obs (180 region-industry pairs)** — our panel.
- Verified: including L reproduces 1152 obs / 192 pairs exactly.
- **Conclusion: no missing industry.** `METHODOLOGY.md` is internally inconsistent
  (states both "exclude real estate" and "1152 obs"); the 1152 is pre-exclusion.

---

## 3. Functional form — log vs levels vs normalising

Motivated by suspicion of the log transform. See `scripts/diagnostics.py`.

- **Standardising (z-score) is NOT an alternative to logging.** It's a linear
  rescale: identical t (2.92), p (0.0036), R² (0.985) as the raw-levels model — only
  the coefficient units change. It cannot fix anything a levels model gets wrong.
- **The data prefer logs.** Productivity is right-skewed in levels (skew 1.37) and
  near-symmetric in logs (skew 0.22). Box-Cox λ = −0.21 (close to log's λ=0, far from
  levels' λ=1).
- **Residual diagnostics (FE model), log vs levels:**
  - Breusch-Pagan heteroskedasticity p: log 2.8e-12 vs levels 6.4e-30 — log **far**
    less heteroskedastic.
  - Residual excess kurtosis: log 5.4 vs levels 12.6 — log much less fat-tailed.
  - Ramsey RESET: levels 0.120 vs log 0.028 — the one check that mildly favours levels.
- **Caveat:** even in logs, residuals remain heteroskedastic and non-normal. OLS SEs
  (hence exact p-values/stars) are not fully trustworthy → **cluster-robust SEs are
  warranted** (not yet applied). Functional form ≠ inference.
- **Substantive result is robust to functional form.** In levels, non-EU is still
  positive & significant: +1pp ≈ +£1,272/job ≈ +2.5% of the £51,380 mean ≈ the log
  model's ~2.3%.

---

## 4. Normalising *per industry* (mean vs scale)

- The region-industry **fixed effects already remove each cell's mean** — so
  "normalise per industry by subtracting its mean" is effectively already done.
- But FE removes the **mean**, not the **scale**: residual SD in levels tracks
  industry level almost perfectly (corr 0.84 — finance residuals ~£4.4k, hospitality
  ~£0.9k). Logs flatten this (corr 0.35).
- **Per-industry standardisation** (subtract industry mean *and* divide by industry
  SD) *does* fix the scale problem — Breusch-Pagan improves from 6.4e-30 (levels) to
  7.5e-13, essentially matching log (2.8e-12). The non-EU result survives all three
  (p ≈ 0.002–0.004).
- **Still prefer log** because: (a) it reads directly as a % effect, comparable across
  the literature; (b) it needs no per-industry SD estimated from only 6 years × 12
  regions (noisy, and mechanically down-weights naturally volatile industries).

---

## 5. Cluster-robust standard errors

The diagnostics show residuals are heteroskedastic and serially correlated within
region-industry cells, so classical OLS SEs understate uncertainty. `analyze.py` now
fits all five specs with **cluster-robust SEs clustered by region-industry** (180
clusters); `run_models(cluster=False)` recovers classical SEs.

**Which non-EU stars survive clustering:**

| spec | coef | p (OLS) | p (clustered) |
|---|---|---|---|
| (1) Levels no FE | +0.078 | 0.197 | 0.100 * |
| (2) Levels + FE | +2.260 | 0.002 *** | 0.013 ** |
| (3) Levels + FE + wt | +2.188 | 0.000 *** | 0.001 *** |
| (4) FD + FE | +1.059 | 0.642 | 0.646 |
| (5) FD + FE + wt | +0.096 | 0.950 | 0.947 |

- **The headline survives:** non-EU is still significant in the FE levels specs (2)
  and (3) under clustering — the credible result.
- EU share in (2) weakens from ** to * (p=0.068) — reinforces "negative but not
  robustly significant".
- FD specs were never significant; clustering doesn't change that.

---

## 6. Breaking out EU accession cohorts (EU14 / EU8 / EU2 / Other EU)

See `scripts/eu_breakout.py`.

**Data constraint.** The EU sub-groups are published **only at UK-national ×
industry** level — never by region. (The NUTS1 nationality source has no sub-groups
and no industry; the regional payroll file stops at EU vs non-EU.) So breaking out
cohorts forces us to **drop the region dimension**, leaving a UK industry-level panel
of **15 industries × 6 years ≈ 90 obs (75 after the lag)** — far smaller and
lower-powered than the main region×industry panel, and without the cross-region
variation that identifies the headline result. **Exploratory only.**

Cohort shares of UK payrolled employment (2014–2019 mean): EU14 3.0%, EU8 3.4%,
EU2 1.2%, Other EU **0.06%**, non-EU 5.8%.

**Findings (read signs, not stars — coefficients are imprecise):**

- **non-EU stays positive and significant** even in this tiny panel (pooled p=0.03,
  +FE p<0.01) — consistent with the main result.
- **No EU cohort is robustly distinguishable from zero.** EU14 and EU8 both lean
  negative in the pooled spec; EU2 is ambiguous (sign flips across specs).
- **Other EU is too small to estimate** (0.06% share): its coefficients (−12 pooled,
  −156 with FE) are artefacts of a near-constant regressor and should be ignored,
  including its spurious FE "significance".
- With 15 industries and 90 obs, the FE spec is overfit (R²≈0.999) and unreliable;
  the pooled+lag column is the more trustworthy of the two.

**Takeaway:** a cohort breakout is *possible* but only at the UK level, where there's
too little data to separate the EU sub-groups. The data cannot support a regional
EU-cohort analysis. The slight overall negativity of the EU coefficient in the main
panel appears to come from EU14/EU8 rather than EU2, but this is suggestive at best.

**Caveat:** suppressed `<50` cells (0–15% of monthly values for the smaller cohorts)
are summed as 0 when aggregating HMRC sub-sections, mildly understating the smallest
cohort shares.

---

## Open / not yet done

- Dynamic-panel (Nickell) bias from lagged dependent + FE — acknowledged, not
  addressed (paper has the same issue).
- Real-estate-included robustness row (would match the paper's stated 1152 but
  reintroduce the imputed-rent distortion).
