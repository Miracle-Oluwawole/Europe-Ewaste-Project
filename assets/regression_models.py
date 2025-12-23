
from statsmodels.formula.api import ols
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dagster import asset

OUTPUT_DIR = "data/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _run_reg(df: pd.DataFrame, y_col: str, label: str):

    # check column exists
    if y_col not in df.columns:
        raise ValueError(f"{y_col} not found in dataframe")

    # ensure clean data
    data = df.dropna(subset=[y_col, "log_gdp", "log_population"]).copy()

    formula = f"{y_col} ~ log_gdp + log_population"
    model = ols(formula, data=data).fit()

    #Save coefficients
    coef_df = pd.DataFrame({
        "coef": model.params,
        "pvalue": model.pvalues
    })
    coef_path = f"{OUTPUT_DIR}/{label}_regression_summary.csv"
    coef_df.to_csv(coef_path)

    # Save coefficient plot
    plt.figure(figsize=(6, 4))
    coef_df["coef"].plot(kind="bar")
    plt.title(f"Coefficients — {label.capitalize()}")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/{label}_coefficients.png")
    plt.close()

    # Save ANOVA table
    import statsmodels.api as sm
    anova = sm.stats.anova_lm(model, typ=2)
    anova.to_csv(f"{OUTPUT_DIR}/{label}_anova.csv")

    # Save meta info
    meta = {
        "target": label,
        "y_col": y_col,
        "r2": float(model.rsquared),
        "adj_r2": float(model.rsquared_adj),
        "f_stat": float(model.fvalue),
        "f_pvalue": float(model.f_pvalue),
        "coefficients": model.params.to_dict(),
        "pvalues": model.pvalues.to_dict()
    }

    import json
    with open(f"{OUTPUT_DIR}/{label}_meta.json", "w") as f:
        json.dump(meta, f, indent=4)

    return meta


#Assets

@asset(group_name="models")
def reg_generated(ewaste_agg):
    return _run_reg(ewaste_agg, "generated_kg_per_cap", "generated")


@asset(group_name="models")
def reg_collected(ewaste_agg):
    return _run_reg(ewaste_agg, "collected_kg_per_cap", "collected")


@asset(group_name="models")
def reg_recycled(ewaste_agg):
    return _run_reg(ewaste_agg, "recycled_kg_per_cap", "recycled")


@asset(group_name="models")
def reg_treatment(ewaste_agg):
    return _run_reg(ewaste_agg, "treatment_kg_per_cap", "treatment")


@asset(group_name="models")
def reg_recovered(ewaste_agg):
    return _run_reg(ewaste_agg, "recovered_kg_per_cap", "recovered")
