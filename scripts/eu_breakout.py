"""Break the EU migration effect into accession cohorts (EU14 / EU8 / EU2 / Other EU).

Run with:  uv run python scripts/eu_breakout.py

IMPORTANT LIMITATION. The HMRC payroll data only publishes the EU sub-groups at
the UK-NATIONAL x industry level -- never by region. (The regional nationality
source has no sub-groups and no industry breakdown.) So this analysis necessarily
DROPS the region dimension and runs on a UK industry-level panel of ~15 industries
x 6 years (2014-2019). That is far smaller and lower-powered than the main
region x industry panel in analyze.py, and it discards the cross-region variation
that identifies the headline result. Treat these estimates as exploratory /
descriptive, not as a like-for-like extension of Table 1.

EU cohorts:
  EU14     pre-2004 members (older western EU; EU15 minus the UK)
  EU8      2004 accession (Poland, Czechia, Hungary, Slovakia, Slovenia, EE/LV/LT)
  EU2      2007 accession (Romania, Bulgaria)
  Other EU Cyprus, Malta, Croatia, etc.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from analyze import HMRC_TO_ONS, ONS_SECTIONS

PROC = "data/processed"
COHORTS = ["EU14", "EU8", "EU2", "Other EU"]
SHARE_COLS = {"EU14": "EU14_pct", "EU8": "EU8_pct", "EU2": "EU2_pct",
              "Other EU": "OtherEU_pct", "Non-EU": "nonEU_pct"}


def build_uk_panel():
    h = pd.read_csv(f"{PROC}/hmrc_payrolled_employments_2021.csv")
    h = h[(h["region_canonical"] == "United Kingdom")
          & h["industry_code"].isin(HMRC_TO_ONS)].copy()
    keep = COHORTS + ["Non-EU", "Total"]
    h = h[h["nationality_canonical"].isin(keep)].copy()
    h["ons_ind"] = h["industry_code"].map(HMRC_TO_ONS)
    h["date"] = pd.to_datetime(h["date"])
    h["year"] = h["date"].dt.year

    # Sum HMRC sub-sections into ONS groups per month (suppressed '<50' cells -> 0,
    # a small downward bias on the tiniest cohort shares; see module docstring).
    monthly = (h.groupby(["ons_ind", "date", "year", "nationality_canonical"],
                         observed=True)["payrolled_employments"].sum().reset_index())
    annual = (monthly.groupby(["ons_ind", "year", "nationality_canonical"],
                              observed=True)["payrolled_employments"].mean().reset_index())
    wide = annual.pivot_table(index=["ons_ind", "year"],
                              columns="nationality_canonical",
                              values="payrolled_employments").reset_index()
    for grp, col in SHARE_COLS.items():
        wide[col] = wide[grp] / wide["Total"]
    wide["total_emp"] = wide["Total"]

    # UK-level real productivity (output per job, CVM) by industry, excl. real estate.
    p = pd.read_csv(f"{PROC}/ons_labour_productivity_by_region_industry.csv")
    p = p[(p["measure"] == "OpJ (CVM)") & (p["region_canonical"] == "United Kingdom")
          & p["industry_code"].isin([s for s in ONS_SECTIONS if s != "L"])].copy()
    p = p.rename(columns={"industry_code": "ons_ind"})
    p["log_prod"] = np.log(p["value"])

    df = p[["ons_ind", "year", "log_prod"]].merge(wide, on=["ons_ind", "year"])
    df = df[(df["year"] >= 2014) & (df["year"] <= 2019)].sort_values(["ons_ind", "year"])
    df["L1_log_prod"] = df.groupby("ons_ind")["log_prod"].shift(1)
    return df


def main():
    df = build_uk_panel()
    print(f"UK industry-level panel: {len(df)} obs, "
          f"{df['ons_ind'].nunique()} industries, years {sorted(df.year.unique())}")

    print("\nMean cohort share of UK payrolled employment, 2014-2019:")
    for grp, col in SHARE_COLS.items():
        print(f"  {grp:9s} {df[col].mean()*100:5.2f}%")

    d = df.dropna(subset=["L1_log_prod"]).copy()
    rhs = "EU14_pct + EU8_pct + EU2_pct + OtherEU_pct + nonEU_pct + L1_log_prod"
    # Few industries -> classical OLS SEs (cluster-by-industry has too few clusters).
    models = {
        "Pooled + lag (no FE)": smf.ols(f"log_prod ~ {rhs}", d).fit(),
        "+ industry FE":        smf.ols(f"log_prod ~ {rhs} + C(ons_ind)", d).fit(),
    }

    def stars(p):
        return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""

    print("\n" + "=" * 70)
    print("EU COHORT BREAKOUT  (dep var: log real output per job; shares 0-1)")
    print("=" * 70)
    labels = [("EU14", "EU14_pct"), ("EU8", "EU8_pct"), ("EU2", "EU2_pct"),
              ("Other EU", "OtherEU_pct"), ("non-EU", "nonEU_pct"),
              ("lag log prod", "L1_log_prod")]
    print(f"{'':16s}" + "".join(f"{k:>22s}" for k in models))
    for lab, v in labels:
        line = f"{lab:16s}"
        for m in models.values():
            line += f"{m.params[v]:>14.3f} ({m.pvalues[v]:.2f}){stars(m.pvalues[v]):<2s}"
        print(line)
    print(f"{'N':16s}" + "".join(f"{int(m.nobs):>22d}" for m in models.values()))
    print(f"{'R2':16s}" + "".join(f"{m.rsquared:>22.3f}" for m in models.values()))
    print("=" * 70)
    print("Significance: *** p<0.01, ** p<0.05, * p<0.1   (classical OLS SEs)")
    print("EXPLORATORY: UK-only, ~15 industries, no region variation -> low power.")
    print("Coefficients are imprecise; read signs/relative magnitudes, not stars.")


if __name__ == "__main__":
    main()
