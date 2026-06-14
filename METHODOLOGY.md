# Methodology Summary

**Paper:** Nam, Hoseong and Portes, Jonathan. "Migration and Productivity in the UK: An Analysis of Employee Payroll Data." IZA DP No. 16472, September 2023.

---

## Research Question

Does immigration affect labour productivity in the UK, and do the effects differ between EU-origin and non-EU-origin workers?

---

## Data

### HMRC PAYE RTI / Migrant Worker Scan
- Source: HM Revenue & Customs payrolled employment data
- Coverage: July 2014 – June 2021 (monthly), by region and industry
- Population: All payrolled employee jobs, combined with the HMRC Migrant Worker Scan (MWS), which links PAYE records to National Insurance registration data to identify country of origin
- Groups: **UK-origin** (born in UK or arrived before age ~16), **EU-origin**, **non-EU-origin**

### ONS Labour Productivity by Industry and Region
- Source: Office for National Statistics
- Coverage: 1998–2019 (annual), by region and industry
- Measure: Output per job and output per hour worked

---

## Sample Construction

1. HMRC monthly data is converted to **annual averages** to match the yearly productivity series.
2. Datasets are merged on **region × industry × year**.
3. Both datasets use ITL1 (formerly NUTS1) regions and SIC 2007 industry codes.
4. The ONS data aggregates some SIC sections; the HMRC data is aggregated to match.
5. **Real estate (SIC L) is excluded**: ONS assigns imputed rent to this sector, causing a large upward distortion.
6. Years covered by the overlap: **2014–2019** (6 years).
7. Final dataset: **12 regions × 16 industries × 6 years = 1,152 observations** (192 unique region-industry pairs).

---

## Key Variables

| Variable | Definition |
|---|---|
| `log_productivity_per_job` | Log of real ONS output per job (dependent, levels) |
| `Δproductivity_per_job` | First difference of log productivity (dependent, FD) |
| `EU_emp_pct` | EU-origin employees as % of total payrolled employment |
| `nonEU_emp_pct` | Non-EU-origin employees as % of total payrolled employment |
| `L1.productivity` | Lagged level of log productivity (levels control) |
| `L1.Δproductivity` | Lagged first difference of log productivity (FD control) |
| `Δtotal_emp_pct` | Growth in total payrolled employment (FD control) |

---

## Regression Specifications

Two complementary approaches are used (following Nickell & Salaheen 2017 and Dustmann, Frattini & Preston 2013):

### Levels regression
```
log(productivity_it) = α·EU_pct_it + β·nonEU_pct_it
                     + γ·log(productivity_{i,t-1})
                     + [region-industry FEs] + ε_it
```
- Estimated with and without region-industry fixed effects (columns 1–3 of Table 1)
- Also estimated with observations weighted by total employment (column 3)

### First-differences regression
```
Δlog(productivity_it) = α·ΔEU_pct_it + β·ΔnonEU_pct_it
                      + γ·Δlog(productivity_{i,t-1})
                      + δ·Δtotal_emp_pct_it
                      + [region-industry FEs] + ε_it
```
- First-differencing removes time-invariant region-industry effects (columns 4–5)
- Also estimated weighted by total employment (column 5)

---

## Results (Table 1)

| | (1) Levels, no FE | (2) Levels + FE | (3) Levels + FE + wt | (4) FD + FE | (5) FD + FE + wt |
|---|---|---|---|---|---|
| EU Employment % | −0.033 | −0.371 | −0.040 | — | — |
| non-EU Employment % | +0.079 | **+2.961\*\*\*** | **+1.471\*\*\*** | — | — |
| ΔEU Employment % | — | — | — | −0.704 | −0.018 |
| Δnon-EU Employment % | — | — | — | **+3.092\*\*** | +1.370\* |
| R² | 0.979 | 0.558 | 0.838 | 0.029 | 0.035 |

**Key findings:**
- A 1 percentage point increase in non-EU employment share is associated with approximately **3% higher productivity** (unweighted) or **1.5% higher productivity** (weighted by employment).
- EU-origin migration coefficients are consistently **negative but not statistically significant** — consistent with either a small negative effect or a null effect.
- Results are robust across levels and first-differences specifications.

---

## Caveats

- The authors describe results as **associations**, not causal estimates; endogeneity cannot be fully ruled out.
- An IV approach using lagged migrant penetration was attempted but instrument validity is questionable over such a short panel.
- The period (2014–2019) predates the post-Brexit migration system, so extrapolation to the current system requires caution — especially given the recent surge in health/care visas and student dependants.
