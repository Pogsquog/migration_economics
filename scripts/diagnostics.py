"""Diagnostics for the functional-form / linear-model assumptions in Table 1.

Run with:  uv run python scripts/diagnostics.py

Focus: is the dependent variable better modelled in logs or in levels, and is
"normalising the normal way" (z-standardising) an alternative to logging?
We test:
  1. Standardising == levels for inference (only rescales coefficients).
  2. Distribution shape of productivity: levels vs log (skew, normality).
  3. Box-Cox: which power transform the data prefers (lambda ~0 => log).
  4. Residual diagnostics for the FE model under log vs levels:
       - heteroskedasticity (Breusch-Pagan)
       - residual normality (Jarque-Bera, skew, kurtosis)
       - functional form (Ramsey RESET)
  5. Does the substantive non-EU result survive in levels?
"""

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan, linear_reset
from statsmodels.stats.stattools import jarque_bera

from analyze import build_panel

LEV_RHS = "EU_emp_pct + nonEU_emp_pct + L1_log_prod + C(unit)"


def section(t):
    print("\n" + "=" * 80 + f"\n{t}\n" + "=" * 80)


def main():
    df = build_panel()
    d = df.dropna(subset=["L1_log_prod"]).copy()
    d["level_prod"] = np.exp(d["log_prod"])              # £ output per job
    d["z_prod"] = stats.zscore(d["level_prod"])          # standardised levels
    # A lagged regressor consistent with each Y scale.
    d["L1_level_prod"] = np.exp(d["L1_log_prod"])
    d["L1_z_prod"] = (d["L1_level_prod"] - d["level_prod"].mean()) / d["level_prod"].std(ddof=0)

    # ---- 1. Standardising only rescales: same R2 / t / p as levels ----------
    section("1. STANDARDISING vs LEVELS  (z-scoring is a linear rescale)")
    m_lvl = smf.ols("level_prod ~ EU_emp_pct + nonEU_emp_pct + L1_level_prod + C(unit)", d).fit()
    m_z = smf.ols("z_prod ~ EU_emp_pct + nonEU_emp_pct + L1_z_prod + C(unit)", d).fit()
    print(f"{'':22s}{'levels':>14s}{'standardised':>16s}")
    print(f"{'non-EU coef':22s}{m_lvl.params['nonEU_emp_pct']:>14.3f}"
          f"{m_z.params['nonEU_emp_pct']:>16.4f}")
    print(f"{'non-EU t-stat':22s}{m_lvl.tvalues['nonEU_emp_pct']:>14.3f}"
          f"{m_z.tvalues['nonEU_emp_pct']:>16.3f}")
    print(f"{'non-EU p-value':22s}{m_lvl.pvalues['nonEU_emp_pct']:>14.4f}"
          f"{m_z.pvalues['nonEU_emp_pct']:>16.4f}")
    print(f"{'R-squared':22s}{m_lvl.rsquared:>14.4f}{m_z.rsquared:>16.4f}")
    print("=> identical t / p / R2: standardising changes units, not the model,")
    print("   so it does NOT address what logging addresses.")

    # ---- 2. Distribution shape -----------------------------------------------
    section("2. DISTRIBUTION SHAPE OF PRODUCTIVITY  (levels vs log)")
    for name, x in [("output per job (levels)", d["level_prod"]),
                    ("log output per job", d["log_prod"])]:
        sk = stats.skew(x); ku = stats.kurtosis(x)  # excess kurtosis
        W, p = stats.shapiro(x)
        print(f"  {name:26s} skew={sk:6.2f}  excess_kurt={ku:6.2f}  "
              f"Shapiro W={W:.3f} (p={p:.1e})")
    print("  Right-skewed in levels; logging pulls it toward symmetry/normality.")

    # ---- 3. Box-Cox preferred transform --------------------------------------
    section("3. BOX-COX  (which power transform the data prefers)")
    lam = stats.boxcox_normmax(d["level_prod"], method="mle")
    print(f"  Box-Cox lambda (MLE) = {lam:.3f}")
    print("  lambda ~ 0 supports the log transform; lambda ~ 1 supports levels.")

    # ---- 4. Residual diagnostics: log vs levels FE model ---------------------
    section("4. RESIDUAL DIAGNOSTICS FOR THE FE MODEL  (log vs levels)")
    m_log = smf.ols(f"log_prod ~ {LEV_RHS}", d).fit()
    print(f"{'':26s}{'log model':>14s}{'levels model':>16s}")
    # Breusch-Pagan heteroskedasticity (LM p-value; low => heteroskedastic)
    bp_log = het_breuschpagan(m_log.resid, m_log.model.exog)[1]
    bp_lvl = het_breuschpagan(m_lvl.resid, m_lvl.model.exog)[1]
    print(f"{'Breusch-Pagan p':26s}{bp_log:>14.1e}{bp_lvl:>16.1e}")
    # Residual normality
    jb_log = jarque_bera(m_log.resid); jb_lvl = jarque_bera(m_lvl.resid)
    print(f"{'Jarque-Bera p':26s}{jb_log[1]:>14.1e}{jb_lvl[1]:>16.1e}")
    print(f"{'resid skew':26s}{jb_log[2]:>14.2f}{jb_lvl[2]:>16.2f}")
    print(f"{'resid excess kurtosis':26s}{jb_log[3]-3:>14.2f}{jb_lvl[3]-3:>16.2f}")
    # Ramsey RESET for functional-form misspecification (low p => misspecified)
    rs_log = linear_reset(m_log, power=2, use_f=True).pvalue
    rs_lvl = linear_reset(m_lvl, power=2, use_f=True).pvalue
    print(f"{'Ramsey RESET p':26s}{rs_log:>14.3f}{rs_lvl:>16.3f}")
    print("  Lower p = worse: more heteroskedastic / less normal / misspecified.")

    # ---- 5. Does the substantive result survive in levels? -------------------
    section("5. SUBSTANTIVE ROBUSTNESS  (non-EU coefficient, levels FE model)")
    c = m_lvl.params["nonEU_emp_pct"]; p = m_lvl.pvalues["nonEU_emp_pct"]
    print(f"  Levels: a full 0->1 shift in non-EU share assoc. with £{c:,.0f}/job "
          f"(p={p:.3f}).")
    print(f"  i.e. +1pp non-EU share ~ £{c*0.01:,.0f}/job; sample mean "
          f"= £{d['level_prod'].mean():,.0f}/job ({c*0.01/d['level_prod'].mean()*100:.1f}%).")
    print("  Sign and significance match the log model -> conclusion is robust to")
    print("  functional form; logs are preferred on the diagnostics above, not the sign.")

    # ---- 6. Normalising PER INDUSTRY -----------------------------------------
    section("6. NORMALISING PER INDUSTRY  (mean removal vs scale removal)")
    d["res_lvl"] = m_lvl.resid
    d["res_log"] = m_log.resid
    g = d.groupby("ons_ind")
    tab = pd.DataFrame({
        "mean_GBP_job": g["level_prod"].mean(),
        "resid_SD_levels": g["res_lvl"].std(),
        "resid_SD_log": g["res_log"].std(),
    }).sort_values("mean_GBP_job")
    print("  Region-industry FE removes each cell's MEAN but not its SCALE.")
    print("  Per-industry SD of the FE residuals vs that industry's mean level:\n")
    print(tab.round(3).to_string())
    r_lvl = np.corrcoef(tab["mean_GBP_job"], tab["resid_SD_levels"])[0, 1]
    r_log = np.corrcoef(tab["mean_GBP_job"], tab["resid_SD_log"])[0, 1]
    print(f"\n  corr(industry mean, residual SD): levels={r_lvl:.2f}  log={r_log:.2f}")
    print("  High corr in levels = scale heteroskedasticity the FE leaves behind;")
    print("  log flattens it. (Subtracting the industry mean does NOT fix scale.)")

    # Per-industry standardisation = subtract industry mean AND divide by SD.
    gi = d.groupby("ons_ind")
    mu, sd = gi["level_prod"].transform("mean"), gi["level_prod"].transform("std")
    d["z_ind_prod"] = (d["level_prod"] - mu) / sd
    d["z_ind_L1"] = (d["L1_level_prod"] - mu) / sd
    m_zind = smf.ols("z_ind_prod ~ EU_emp_pct + nonEU_emp_pct + z_ind_L1 + C(unit)",
                     d).fit()
    print("\n  Does per-industry standardising substitute for the log?")
    print(f"  {'spec':34s}{'Breusch-Pagan p':>18s}{'non-EU p':>12s}")
    for name, m in [("levels + FE", m_lvl),
                    ("per-industry standardised + FE", m_zind),
                    ("log + FE", m_log)]:
        bp = het_breuschpagan(m.resid, m.model.exog)[1]
        print(f"  {name:34s}{bp:>18.1e}{m.pvalues['nonEU_emp_pct']:>12.3f}")
    print("  => per-industry scaling fixes heteroskedasticity about as well as log,")
    print("     and the non-EU result survives all three. Log is still preferred:")
    print("     it reads as a % effect and needs no noisily-estimated per-industry SD.")


if __name__ == "__main__":
    main()
