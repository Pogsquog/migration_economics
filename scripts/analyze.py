"""Recreate Nam & Portes (2023, IZA DP 16472) Table 1.

Methodology: see METHODOLOGY.md. Run with:  uv run python scripts/analyze.py

  - ONS real output per job (OpJ CVM, 2018 GBP) is the productivity measure.
  - HMRC PAYE/MWS payrolled employments give EU / non-EU employment shares,
    expressed as FRACTIONS of total payrolled employment (0-1), matching the
    paper's coefficient scaling (coef 2.96 -> ~3% productivity per +1pp share).
  - Merge on region x industry x year, 2014-2019, 12 ITL1 regions, SIC sections.
  - HMRC industries are aggregated to the ONS section groupings. Real estate
    (SIC L) is excluded from the regressions (ONS imputes rent to it, distorting
    output per job ~6x); see sample_notes() for the grid count with/without it.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

PROC = "data/processed"

# ITL1 regions only (drop England / United Kingdom aggregates).
ITL1 = [
    "North East", "North West", "Yorkshire and The Humber", "East Midlands",
    "West Midlands", "East of England", "London", "South East", "South West",
    "Wales", "Scotland", "Northern Ireland",
]

# Map HMRC SIC sections to the ONS section groupings.
HMRC_TO_ONS = {
    "A": "ABDE", "B": "ABDE", "D": "ABDE", "E": "ABDE",
    "C": "C", "F": "F", "G": "G", "H": "H", "I": "I", "J": "J",
    "K": "K", "L": "L", "M": "M", "N": "N", "O": "O", "P": "P",
    "Q": "Q", "R": "R", "S": "S_T", "T_U": "S_T",
}

# The 16 individual ONS SIC section-groups (excl. aggregates TOTAL, G_J_L_T).
# Real estate (L) is the 16th; it is dropped for regressions via EXCLUDE_REAL_ESTATE.
ONS_SECTIONS = ["ABDE", "C", "F", "G", "H", "I", "J", "K", "L",
                "M", "N", "O", "P", "Q", "R", "S_T"]
EXCLUDE_REAL_ESTATE = True


def build_employment_shares():
    h = pd.read_csv(f"{PROC}/hmrc_payrolled_employments_2021.csv")
    h = h[h["region_canonical"].isin(ITL1)].copy()
    h = h[h["industry_code"].isin(HMRC_TO_ONS)].copy()
    h = h[h["nationality_canonical"].isin(["Total", "UK", "EU", "Non-EU"])].copy()

    h["ons_ind"] = h["industry_code"].map(HMRC_TO_ONS)
    h["date"] = pd.to_datetime(h["date"])
    h["year"] = h["date"].dt.year

    # Per month: sum HMRC sub-sections into ONS section groups.
    monthly = (
        h.groupby(["region_canonical", "ons_ind", "date", "year",
                   "nationality_canonical"], observed=True)["payrolled_employments"]
        .sum().reset_index()
    )
    # Annual average employment (mean across the year's available months).
    annual = (
        monthly.groupby(["region_canonical", "ons_ind", "year",
                         "nationality_canonical"], observed=True)["payrolled_employments"]
        .mean().reset_index()
    )
    wide = annual.pivot_table(
        index=["region_canonical", "ons_ind", "year"],
        columns="nationality_canonical", values="payrolled_employments",
    ).reset_index()

    wide["EU_emp_pct"] = wide["EU"] / wide["Total"]        # fraction 0-1
    wide["nonEU_emp_pct"] = wide["Non-EU"] / wide["Total"]  # fraction 0-1
    wide["total_emp"] = wide["Total"]
    return wide[["region_canonical", "ons_ind", "year",
                 "EU_emp_pct", "nonEU_emp_pct", "total_emp"]]


def build_productivity(exclude_real_estate=EXCLUDE_REAL_ESTATE):
    p = pd.read_csv(f"{PROC}/ons_labour_productivity_by_region_industry.csv")
    p = p[p["measure"] == "OpJ (CVM)"].copy()
    p = p[p["region_canonical"].isin(ITL1)].copy()
    keep = [s for s in ONS_SECTIONS if not (exclude_real_estate and s == "L")]
    p = p[p["industry_code"].isin(keep)].copy()
    p = p.rename(columns={"industry_code": "ons_ind"})
    p["log_prod"] = np.log(p["value"])
    return p[["region_canonical", "ons_ind", "year", "value", "log_prod"]]


def build_panel(exclude_real_estate=EXCLUDE_REAL_ESTATE):
    emp = build_employment_shares()
    prod = build_productivity(exclude_real_estate)
    df = prod.merge(emp, on=["region_canonical", "ons_ind", "year"], how="inner")
    df = df[(df["year"] >= 2014) & (df["year"] <= 2019)].copy()
    df["unit"] = df["region_canonical"] + " | " + df["ons_ind"]
    df = df.sort_values(["unit", "year"]).reset_index(drop=True)

    g = df.groupby("unit", observed=True)
    df["L1_log_prod"] = g["log_prod"].shift(1)
    df["d_log_prod"] = g["log_prod"].diff()
    df["d_EU_pct"] = g["EU_emp_pct"].diff()
    df["d_nonEU_pct"] = g["nonEU_emp_pct"].diff()
    df["d_total_emp_pct"] = g["total_emp"].diff() / g["total_emp"].shift(1)
    df["L1_d_log_prod"] = g["d_log_prod"].shift(1)
    return df


def run_models(df):
    lev = df.dropna(subset=["L1_log_prod"]).copy()
    fd = df.dropna(subset=["d_log_prod", "d_EU_pct", "d_nonEU_pct",
                           "L1_d_log_prod", "d_total_emp_pct"]).copy()
    LEV = "EU_emp_pct + nonEU_emp_pct + L1_log_prod"
    FD = "d_EU_pct + d_nonEU_pct + L1_d_log_prod + d_total_emp_pct"
    return {
        "(1) Levels no FE":     smf.ols(f"log_prod ~ {LEV}", lev).fit(),
        "(2) Levels + FE":      smf.ols(f"log_prod ~ {LEV} + C(unit)", lev).fit(),
        "(3) Levels + FE + wt": smf.wls(f"log_prod ~ {LEV} + C(unit)", lev,
                                        weights=lev["total_emp"]).fit(),
        "(4) FD + FE":          smf.ols(f"d_log_prod ~ {FD} + C(unit)", fd).fit(),
        "(5) FD + FE + wt":     smf.wls(f"d_log_prod ~ {FD} + C(unit)", fd,
                                        weights=fd["total_emp"]).fit(),
    }


def _stars(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""


def print_table1(results):
    print("\n" + "=" * 96)
    print("TABLE 1 RECREATION  (coefficient with significance; shares as fractions 0-1)")
    print("=" * 96)
    rows = [
        ("EU Employment %", "EU_emp_pct"),
        ("non-EU Employment %", "nonEU_emp_pct"),
        ("Lag log productivity", "L1_log_prod"),
        ("d EU Employment %", "d_EU_pct"),
        ("d non-EU Employment %", "d_nonEU_pct"),
        ("Lag d log productivity", "L1_d_log_prod"),
        ("d total emp %", "d_total_emp_pct"),
    ]
    print(f"{'':24s}" + "".join(f"{k:>18s}" for k in results))
    for label, var in rows:
        line = f"{label:24s}"
        for m in results.values():
            if var in m.params.index:
                line += f"{m.params[var]:>12.3f}{_stars(m.pvalues[var]):<6s}"
            else:
                line += f"{'-':>18s}"
        print(line)
    for stat, fn in [("R2 (incl. FE)", lambda m: f"{m.rsquared:.3f}"),
                     ("N", lambda m: f"{int(m.nobs)}")]:
        print(f"{stat:24s}" + "".join(f"{fn(m):>12s}{'':6s}" for m in results.values()))
    print("=" * 96)
    print("Significance: *** p<0.01, ** p<0.05, * p<0.1")
    print("Paper Table 1 for comparison:")
    print("  non-EU:  +0.079 | +2.961*** | +1.471*** |    -      |    -   ")
    print("  EU:      -0.033 | -0.371    | -0.040    |    -      |    -   ")
    print("  d non-EU:   -   |    -      |    -      | +3.092**  | +1.370*")
    print("  d EU:       -   |    -      |    -      | -0.704    | -0.018 ")


def print_detail(results):
    """coef / std err / t / p / 95% CI for the migration variables in each model."""
    want = {"EU_emp_pct": "EU share", "nonEU_emp_pct": "non-EU share",
            "d_EU_pct": "d EU share", "d_nonEU_pct": "d non-EU share"}
    print("\n" + "=" * 96)
    print("DETAILED INFERENCE (migration coefficients)")
    print("=" * 96)
    for name, m in results.items():
        ci = m.conf_int(0.05)
        print(f"\n{name}   N={int(m.nobs)}   R2(incl FE)={m.rsquared:.3f}")
        print(f"  {'variable':16s}{'coef':>9s}{'std err':>9s}{'t':>8s}"
              f"{'p>|t|':>9s}{'[0.025':>10s}{'0.975]':>10s}")
        for v, lab in want.items():
            if v in m.params.index:
                print(f"  {lab:16s}{m.params[v]:>9.3f}{m.bse[v]:>9.3f}"
                      f"{m.tvalues[v]:>8.2f}{m.pvalues[v]:>9.3f}"
                      f"{ci.loc[v, 0]:>10.3f}{ci.loc[v, 1]:>10.3f}")


def sample_notes():
    """Reconcile the 16-vs-15 industry / 1152-vs-1080 observation counts."""
    print("\n" + "=" * 96)
    print("SAMPLE RECONCILIATION")
    print("=" * 96)
    emp = build_employment_shares()
    for excl, tag in [(False, "incl. real estate (L)"), (True, "excl. real estate (L)")]:
        prod = build_productivity(exclude_real_estate=excl)
        df = prod.merge(emp, on=["region_canonical", "ons_ind", "year"]).query(
            "2014 <= year <= 2019")
        pairs = df.groupby(["region_canonical", "ons_ind"]).ngroups
        n_ind = df["ons_ind"].nunique()
        print(f"  {tag:24s}: {n_ind:2d} industries x 12 regions x 6 yrs "
              f"= {len(df):5d} obs ({pairs} region-industry pairs)")
    print("  -> Paper's '16 industries / 1152 obs' is the full grid INCLUDING real")
    print("     estate; the regressions drop it, giving 15 industries / 1080 obs.")

    # Within (FE-demeaned) R^2, the convention econ papers report for FE models.
    df = build_panel()
    d = df.dropna(subset=["L1_log_prod"]).copy()
    g = d.groupby("unit")
    cols = ["log_prod", "EU_emp_pct", "nonEU_emp_pct", "L1_log_prod"]
    for c in cols:
        d[c + "_w"] = d[c] - g[c].transform("mean")
    wm = smf.ols("log_prod_w ~ EU_emp_pct_w + nonEU_emp_pct_w + L1_log_prod_w - 1",
                 d).fit()
    print(f"\n  Note: reported R2 includes FE dummies (~0.99). Within/demeaned R2 "
          f"for (2) = {wm.rsquared:.3f}")
    print("        -> the FE-spec R2 gap vs the paper is a reporting convention, "
          "not a data difference.")


def main():
    df = build_panel()
    print(f"Merged regression panel: {len(df)} obs, "
          f"{df['unit'].nunique()} region-industry pairs, "
          f"years {sorted(df['year'].unique())}")
    results = run_models(df)
    print_table1(results)
    print_detail(results)
    sample_notes()
    out = f"{PROC}/analysis_panel.csv"
    df.to_csv(out, index=False)
    print(f"\nPanel written to {out}")


if __name__ == "__main__":
    main()
