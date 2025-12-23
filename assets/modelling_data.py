
import os
import matplotlib
import pandas as pd
import numpy as np
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dagster import asset

@asset(group_name="model_ready")
def ewaste_agg(clean_ewaste_from_mongo, gdp_df, population_df):
    df = clean_ewaste_from_mongo.copy()

@asset(group_name="model_ready")
def ewaste_agg(ewaste_europe_long, gdp_df, population_df) -> pd.DataFrame:
    df = ewaste_europe_long.copy()

    # Pivot one column per management operation
    pivot = (
        df.pivot_table(
            index=["country", "year"],
            columns="management_operation",
            values="ewaste_value",
            aggfunc="sum",
        )
        .reset_index()
    )

    # Rename columns
    rename_map = {
        "Waste generated": "generated_kg_per_cap",
        "Waste collected": "collected_kg_per_cap",
        "Recycling": "recycled_kg_per_cap",
        "Waste treatment": "treatment_kg_per_cap",
        "Recovery": "recovered_kg_per_cap",
    }
    pivot = pivot.rename(columns=rename_map)

    # Merge with gdp and population data
    merged = (
        pivot
        .merge(gdp_df, on=["country", "year"], how="inner")
        .merge(population_df, on=["country", "year"], how="inner")
        .dropna(subset=["gdp_per_capita", "population"])
    )

    # Log transforms 
    merged["log_gdp"] = np.log(merged["gdp_per_capita"])
    merged["log_population"] = np.log(merged["population"])

    for col in [
        "generated_kg_per_cap",
        "collected_kg_per_cap",
        "recycled_kg_per_cap",
        "treatment_kg_per_cap",
        "recovered_kg_per_cap",
    ]:
        if col in merged.columns:
            merged[f"{col}_tonnes"] = (merged[col] * merged["population"]) / 1000.0
    # Save for Streamlit
    os.makedirs("data/processed", exist_ok=True)
    merged.to_csv("data/processed/ewaste_agg.csv", index=False)

    return merged

@asset(group_name="model_ready", required_resource_keys={"postgres"})
def ewaste_agg_to_postgres(context, ewaste_agg):
    engine = context.resources.postgres
    ewaste_agg.to_sql("ewaste_agg", engine, if_exists="replace", index=False)

    context.log.info("ewaste_agg table written to PostgreSQL.")


DIAG_OUTPUT_DIR = "data/output"
os.makedirs(DIAG_OUTPUT_DIR, exist_ok=True)


@asset(group_name="diagnostics")
def ewaste_correlation(ewaste_agg):
    #correlation matrix
    cols = [
        "gdp_per_capita",
        "population",
        "generated_kg_per_cap",
        "collected_kg_per_cap",
        "recycled_kg_per_cap",
        "treatment_kg_per_cap",
        "recovered_kg_per_cap",
    ]
    existing = [c for c in cols if c in ewaste_agg.columns]
    corr = ewaste_agg[existing].corr()

    csv_path = os.path.join(DIAG_OUTPUT_DIR, "corr_matrix.csv")
    corr.to_csv(csv_path)

    # Heatmap plot
    plt.figure(figsize=(7, 5))
    im = plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.xticks(range(len(existing)), existing, rotation=45, ha="right")
    plt.yticks(range(len(existing)), existing)
    plt.title("Correlation Heatmap")
    plt.tight_layout()

    png_path = os.path.join(DIAG_OUTPUT_DIR, "corr_heatmap.png")
    plt.savefig(png_path)
    plt.close()

    return {
        "csv_path": csv_path,
        "png_path": png_path,
    }