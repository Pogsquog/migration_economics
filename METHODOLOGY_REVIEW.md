# Critical Methodology Review

**Paper:** Nam & Portes, "Migration and Productivity in the UK: An Analysis of Employee Payroll Data", IZA DP No. 16472 (2023)

---

## Overall Assessment

The paper is a useful descriptive contribution — it applies a standard panel regression framework to a genuinely novel dataset (HMRC PAYE RTI), and the finding of a positive association between non-EU employment share and productivity is plausible and interesting. However, several methodological weaknesses limit how much weight can be placed on the estimates, and the "association not causality" caveat in the conclusion is doing a lot of work. The core problems are: unresolved endogeneity, a very short panel, coarse nationality and industry groupings, and important omitted variables — particularly capital intensity.

---

## 1. Causal Identification: The Core Problem

### Endogeneity
The biggest weakness. The paper acknowledges it cannot establish causality, but the framing understates the problem. Migration is plausibly endogenous to productivity in *both* directions:

- **Positive feedback**: high-productivity, fast-growing firms and sectors attract more workers, including migrants — especially non-EU migrants on employer-sponsored visas, who by definition must have a job offer at or above a salary threshold. This mechanically correlates non-EU share with productivity *even with no causal effect*.
- **Negative feedback**: firms facing productivity pressures may recruit cheap labour (including EU migrants) as a substitute for capital investment — the so-called "easy labour" hypothesis, which would bias EU coefficients negative.

The fixed effects and first-differencing specifications help by removing time-invariant sector-region effects, but neither removes *within-cell time-varying* endogeneity (e.g., a productivity boom within a region-sector that simultaneously attracts more non-EU workers).

### The Instrument Attempt
The authors tried lagged migrant penetration as an IV and abandoned it as "questionable". This is correct: lagged penetration is a weak instrument for *changes* in penetration over a 6-year window, and it fails the exclusion restriction if past migration shares predict current productivity through persistence channels.

### Better Identification Strategies

**Brexit as a natural experiment.** The 2016 referendum and the subsequent fall in EU migration created a plausibly exogenous, regionally differentiated shock to the supply of EU-origin workers. A difference-in-differences design — comparing sectors and regions that were more vs. less exposed to EU migration pre-2016 — would give much cleaner identification of the EU migration effect. The HMRC data covers this period and could support this design.

**Bartik/shift-share instruments.** The standard approach in the migration-wages literature: instrument local migrant shares using national changes in immigration from each country of origin, interacted with the pre-existing local distribution of those nationalities. This has well-known validity problems (Goldsmith-Pinkham, Sorkin & Swift, 2020; Borusyak et al., 2022) but is at least transparent about its assumptions. The instrument is strong for non-EU workers (because national non-EU flows are driven by visa policy changes) and weaker for EU workers.

**Dynamic panel GMM (Arellano-Bond / Blundell-Bond).** The levels specification includes a lagged dependent variable. With a short panel (T=6), this induces Nickell bias in fixed-effects OLS. Dynamic GMM uses lagged levels as instruments for the differenced equation, addressing both the Nickell bias and, partially, the endogeneity of migration. The panel is almost too short to use this reliably, but it would still be an improvement.

---

## 2. Data and Panel Limitations

### Very Short Time Series
Six years (2014–2019) is a thin basis for a fixed-effects panel study. With region × industry FEs (192 dummies), the within-cell variation being exploited is small, and there is only one recession-free growth cycle to work with. The pre-GFC period, when both migration and productivity were growing, is entirely missing.

The ONS productivity series runs to 1998; the binding constraint is that the HMRC nationality data only starts in 2014. The paper does not consider whether earlier Annual Population Survey (APS) or LFS-based migration estimates — despite their acknowledged limitations — could be used to extend the panel back to the late 1990s and give more identifying variation.

### Nationality Groupings Are Too Coarse
The EU vs. non-EU distinction is a policy artefact, not an economically meaningful skill grouping:

- **"EU"** in 2014–2019 is dominated by EU8 (Polish, Czech, Slovak, etc.) and EU2 (Romanian, Bulgarian) workers — predominantly lower-wage, lower-skilled. But it also includes EU14 workers (German, French, Dutch), who are on average higher-skilled.
- **"Non-EU"** includes highly-paid tech workers on Tier 2 visas, refugees with no right to choose employer, international students working part-time, and dependants of students with work rights. These groups have very different productivity profiles.

The HMRC dataset *does* disaggregate into EU14, EU8, EU2, and Other EU. Using this finer breakdown would test whether the negative EU coefficient is driven by EU8/EU2 (as expected under the "batting average" hypothesis) while EU14 has a positive effect more similar to non-EU.

Similarly, a wage-band decomposition (HMRC data contains median earnings by nationality and sector in some releases) would let you separate skill effects from pure number effects.

### Industry Aggregation
The 16-sector breakdown is coarser than what the data could support. Within "Manufacturing" (SIC C), high-tech precision manufacturing and food processing have very different productivity profiles and very different migrant compositions. The ONS productivity dataset does provide some sub-sector granularity that the paper does not exploit.

---

## 3. Omitted Variables

### Capital Intensity
The most important omitted variable. Labour productivity (GVA per worker) is jointly determined by labour inputs *and* capital stock. If non-EU migrants are concentrated in capital-intensive sectors (e.g., information and communications, finance), the positive coefficient on non-EU share could simply reflect capital intensity rather than any labour quality or spillover effect. The ONS publishes regional capital stock estimates; including log(capital per worker) as a control is standard practice and its omission here is a significant gap.

### Technology Adoption and Automation
The 2014–2019 period saw rapid automation in some sectors. If automation raises GVA per worker while simultaneously displacing low-skill (predominantly EU) workers, this generates a spurious negative correlation between EU share and productivity. A proxy such as sector-level R&D expenditure (ONS BERD data) or investment in ICT capital (ONS capital services data) would help.

### Brexit Uncertainty
The referendum in June 2016 created abrupt, sector-differentiated investment uncertainty. Sectors most exposed to EU trade (e.g., manufacturing, financial services) saw sharper investment pullbacks, which depresses labour productivity. These same sectors had different migrant compositions. The paper includes time fixed effects but not sector-specific Brexit exposure controls, so this channel could confound results in either direction.

### National Living Wage (2016)
The introduction of the National Living Wage in April 2016 — a large mandatory wage floor increase — raised labour costs sharply in low-wage sectors (hospitality, retail, food processing). Firms responded with some combination of labour-saving investment and reduced hours. This is a sector-specific productivity shock coinciding precisely with the sample period and is not controlled for.

### Regional Public Sector Austerity
Austerity cuts post-2010 were geographically uneven, affecting Northern English regions and Wales more than London and the South East. ONS productivity in the public sector (SIC O, P, Q) is measured differently (largely input-based), and austerity differentially contracted measured output in these regions. This could create spurious regional correlations.

---

## 4. Statistical / Econometric Issues

### Standard Errors
The paper reports standard errors but does not state whether they are clustered. With a panel of region × industry cells observed over time, both cross-sectional and time-series correlation are likely: productivity shocks hit entire regions (macro conditions) and entire sectors (sectoral demand shocks) simultaneously. Standard errors should be clustered two-way (by region and by industry-year), or at minimum by region-industry cell. Failing to do this will understate standard errors and overstate significance.

### Weighting
Weighting by employment is reasonable, but the paper should check whether results are driven by London — which accounts for a disproportionate share of both migrants and productivity in a population-weighted regression. Results excluding London, or with region fixed effects interacted with a London dummy, would test robustness.

### Model Specification in Levels
The levels regression with lagged productivity as a control (columns 1–3) is essentially an AR(1) model in logs. The lagged coefficient is 0.99 in the unweighted OLS, which is extremely close to a unit root. This suggests the series may be better modelled in first differences throughout, and that the levels specification is questionable. A formal panel unit root test (e.g., Im-Pesaran-Shin) should precede the levels regression.

---

## 5. On Tree-Based and Boosting Methods

### Do They Help Here?

Random forests and gradient boosting are primarily **prediction tools**, not causal inference tools. Given the analysis has roughly 1,150 observations and 30–40 features (with fixed effects absorbed), ML models do not have a dramatic advantage in this regime and offer no solution to the core endogeneity problem.

However, there are legitimate uses:

**Non-linearity and interactions.** The effect of migration on productivity may be non-linear — a modest migrant share may be complementary, while a very high share could saturate returns. It may also interact strongly with baseline sector productivity or urbanisation. Tree-based methods discover these interactions automatically. A gradient-boosted model with SHAP (SHapley Additive exPlanations) values could reveal whether the non-EU effect is driven by a small number of extreme cells (e.g., London × Information & Communication) or is broad-based.

**Feature selection / variable importance.** With many potential controls (capital, wages, automation proxies, Brexit exposure), a regularised model (LASSO, elastic net) or a random forest's variable importance scores can help identify which confounders are empirically important before entering them into a structural OLS specification.

**Double/Debiased Machine Learning (DML).** This is probably the most valuable ML contribution here. Chernozhukov et al. (2018) show that you can use any ML method to partial out nuisance functions (i.e., predict both the treatment — migration share — and the outcome — productivity — from all controls), and then regress the residuals on each other to recover an approximately unbiased causal estimate with valid standard errors. This would allow inclusion of a rich set of controls (capital, R&D, wages, Brexit exposure, region-year trends) without the degrees-of-freedom cost that kills a conventional OLS regression on this small a dataset.

### What They Cannot Fix

No amount of ML sophistication resolves the endogeneity problem without a valid instrument or quasi-experimental design. Gradient boosting with a high R² does not mean the migration coefficient is causal. If anything, overfitting on the non-EU/productivity correlation would make the estimate *less* credible, not more.

---

## 6. Additional Data Sources Worth Considering

| Source | What it adds |
|---|---|
| **ONS Annual Survey of Hours and Earnings (ASHE)** | Median wages by region, sector, and (in some releases) nationality — a skill-mix proxy and independent productivity check |
| **ONS Capital Services by industry** | Capital input data needed to compute TFP and control for capital intensity |
| **ONS BERD (Business Enterprise R&D)** | R&D expenditure by sector — innovation / technology adoption proxy |
| **ONS Business Register and Employment Survey (BRES)** | Granular employment counts at narrower sector × region cuts than LFS |
| **HMRC PAYE individual-level data (via secure access)** | Would allow controlling for the within-cell skill/wage composition of the workforce, including the earnings distribution of migrants vs. natives |
| **ONS experimental TFP estimates** | Total factor productivity rather than labour productivity — removes capital intensity confound |
| **ONS International Trade in Services / HMRC trade data** | Sectoral export intensity — Brexit-exposure proxy and trade-productivity link |
| **EU Settlement Scheme / Home Office visa data** | Post-2020 flows; would extend the series beyond 2022 with finer nationality detail |
| **Census 2011 & 2021** | Detailed migrant stock characteristics (education, age, length of residence) at local authority level — could be aggregated to NUTS1 for robustness checks |
| **Eurostat NUTS2-level productivity for EU countries** | Cross-country comparison to test whether UK results are distinctive |

---

## 7. Secular Trends to Account For

- **Globalisation and offshoring**: labour productivity in manufacturing rose partly because low-productivity tasks were offshored, leaving higher-productivity activities in the UK. If offshoring correlates with migrant hiring decisions, this confounds results.
- **Services sector financialisation**: rising GVA in finance (SIC K) reflects financial activity growth, not necessarily real productivity. The exclusion of real estate (L) is appropriate, but finance may have similar distortions.
- **Ageing workforce**: older workers are on average more experienced and better paid, raising measured labour productivity. Regional demographic differences could confound regional migration-productivity correlations.
- **Urbanisation and agglomeration**: the ongoing spatial concentration of high-productivity activity in London and major cities, independent of migration, generates a secular trend that region FEs alone may not fully capture if the trend is within-region across industries.

---

## Summary of Priority Improvements

1. **Use Brexit as a quasi-experiment** for EU migration identification — the most credible causal design available in this data.
2. **Add capital stock per worker** as a control — the most important omitted variable.
3. **Disaggregate nationality** to at least EU14 vs EU8/EU2 vs non-EU (the HMRC data supports this).
4. **Two-way clustered standard errors** (region and industry-year) — easy fix, may widen confidence intervals materially.
5. **Test for panel unit roots** before choosing levels vs. first differences.
6. **Apply Double ML** to partial out the growing list of confounders while preserving valid inference on the migration coefficient.
7. **Robustness check excluding London** — given London's extreme values on both migration and productivity.
8. **Extend the panel** using APS/LFS-based migration shares pre-2014 as supplementary years, acknowledging their measurement limitations.
