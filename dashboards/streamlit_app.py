# dashboards/streamlit_app.py

import os
import json
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="E-waste Analytics", layout="wide")

# Styling
st.markdown("""
    <style>
    body {
        background-color: #f8f9fa;
        font-family: "Segoe UI", sans-serif;
    }
    .main-header {
        padding: 1rem 0;
        border-bottom: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
    }
    .metric-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #6c757d;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 600;
        color: #343a40;
    }
    </style>
""", unsafe_allow_html=True)

# Paths
AGG_PATH = "data/processed/ewaste_agg.csv"
OUTPUT_DIR = "data/output"

#Load Main Data
st.markdown('<div class="main-header"><h1>🌍 E-waste, GDP & Population Dashboard</h1></div>', unsafe_allow_html=True)

if not os.path.exists(AGG_PATH):
    st.error(f"Could not find {AGG_PATH}. Run the `ewaste_agg` asset in Dagster first.")
    st.stop()

@st.cache_data
def load_main():
    return pd.read_csv(AGG_PATH)

df = load_main()

# Set Top level metrics
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown('<div class="metric-card"><div class="metric-title">Rows</div>'
                f'<div class="metric-value">{df.shape[0]}</div></div>', unsafe_allow_html=True)
with col_b:
    st.markdown('<div class="metric-card"><div class="metric-title">Columns</div>'
                f'<div class="metric-value">{df.shape[1]}</div></div>', unsafe_allow_html=True)
with col_c:
    st.markdown('<div class="metric-card"><div class="metric-title">Countries</div>'
                f'<div class="metric-value">{df["country"].nunique()}</div></div>', unsafe_allow_html=True)

st.markdown("")

#Sidebar filters
st.sidebar.header("Filters")

countries = sorted(df["country"].unique())
selected_countries = st.sidebar.multiselect("Country", countries, default=countries)

years = sorted(df["year"].unique())
year_min, year_max = int(min(years)), int(max(years))
year_range = st.sidebar.slider("Year range", year_min, year_max, (year_min, year_max))

operation_map = {
    "Generated": "generated_kg_per_cap",
    "Collected": "collected_kg_per_cap",
    "Recycled": "recycled_kg_per_cap",
    "Treatment": "treatment_kg_per_cap",
    "Recovered": "recovered_kg_per_cap",
}
operation_label = st.sidebar.selectbox("E-waste operation", list(operation_map.keys()))
operation_col = operation_map[operation_label]

mask = (
    df["country"].isin(selected_countries) &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
)
fdf = df[mask].copy()

# Tabs
tab_overview, tab_trends, tab_models, tab_corr = st.tabs([
    "Overview", "Operations & Trends", "Model Insights", "Correlations"
])

# Overview - Tab 1
with tab_overview:
    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader(f"GDP vs E-waste {operation_label} (per capita)")
    fig_scatter = px.scatter(
        fdf,
        x="gdp_per_capita",
        y=operation_col,
        color="country",
        size="population",
        hover_data=["year"],
        title=f"GDP per capita vs E-waste {operation_label} per capita",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# Operations and Trends - Tab 2
with tab_trends:
    st.subheader(f"Time Trend – {operation_label}")

    country_for_trend = st.selectbox("Select country for trend", countries)
    trend_df = df[df["country"] == country_for_trend].sort_values("year")

    fig_trend = px.line(
        trend_df,
        x="year",
        y=operation_col,
        markers=True,
        title=f"{operation_label} per capita over time – {country_for_trend}",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# Model Insight and Interpretation - Tab 3
with tab_models:
    st.subheader("Regression Insights & Interpretation")

    reg_targets = {
        "Generated": "generated",
        "Collected": "collected",
        "Recycled": "recycled",
        "Treatment": "treatment",
        "Recovered": "recovered",
    }

    model_choice = st.selectbox("Select Operation for model details", list(reg_targets.keys()))
    label = reg_targets[model_choice]

    # Paths
    coef_csv = os.path.join(OUTPUT_DIR, f"{label}_regression_summary.csv")
    coef_png = os.path.join(OUTPUT_DIR, f"{label}_coefficients.png")
    anova_csv = os.path.join(OUTPUT_DIR, f"{label}_anova.csv")
    meta_json = os.path.join(OUTPUT_DIR, f"{label}_meta.json")

    col1, col2 = st.columns(2)

    # Coeff table and plot 
    with col1:
        st.markdown("**Coefficients & p-values**")
        if os.path.exists(coef_csv):
            coef_df = pd.read_csv(coef_csv, index_col=0)
            st.dataframe(coef_df)
        else:
            st.warning("Coefficient summary not found. Re-run regression assets in Dagster.")

    with col2:
        st.markdown("**Coefficient Plot**")
        if os.path.exists(coef_png):
            st.image(coef_png, use_container_width=True)
        else:
            st.warning("Coefficient plot not found.")

    st.markdown("---")

    # ANOVA table 
    st.markdown("### ANOVA Table (Model-level significance)")
    if os.path.exists(anova_csv):
        anova_df = pd.read_csv(anova_csv, index_col=0)
        st.dataframe(anova_df)
    else:
        st.warning("ANOVA table not found.")

    # Interpretation from meta 
    st.markdown("### Model Interpretation")
    if os.path.exists(meta_json):
        with open(meta_json, "r", encoding="utf-8") as f:
            meta = json.load(f)

        r2 = meta.get("r2")
        adj_r2 = meta.get("adj_r2")
        f_pvalue = meta.get("f_pvalue")
        coefs = meta.get("coefficients", {})
        pvals = meta.get("pvalues", {})

        st.write(f"**R²:** {r2:.3f}  |  **Adjusted R²:** {adj_r2:.3f}")
        if f_pvalue is not None:
            st.write(f"**F-statistic p-value (overall model):** {f_pvalue:.4f}")

        # helper for significance text
        def explain_term(term_name, pretty_name):
            coef = coefs.get(term_name)
            p = pvals.get(term_name)
            if coef is None or p is None:
                return f"- {pretty_name}: not included in model."
            direction = "positive" if coef > 0 else "negative"
            sig = "statistically significant" if p < 0.05 else "not statistically significant"
            return f"- **{pretty_name}**: {direction} effect (coef = {coef:.3f}, p = {p:.4f}, {sig})."

        st.markdown("**Key points:**")
        st.markdown(explain_term("log_gdp", "Economic prosperity (log GDP per capita)"))
        st.markdown(explain_term("log_population", "Population size (log population)"))

        if f_pvalue is not None:
            if f_pvalue < 0.05:
                st.markdown(
                    "- **Overall model**: The F-test p-value is below 0.05, so the model is "
                    "statistically significant — GDP and population jointly explain a meaningful "
                    "share of variation in this e-waste outcome."
                )
            else:
                st.markdown(
                    "- **Overall model**: The F-test p-value is above 0.05, so the model is "
                    "not statistically significant — GDP and population do not jointly explain "
                    "a large, reliable share of variation in this outcome."
                )

        st.markdown(
            "_Interpretation guideline: a positive coefficient means that as the predictor "
            "increases, the e-waste metric tends to increase (holding the other variable constant). "
            "A negative coefficient implies the opposite._"
        )
    else:
        st.warning("Meta JSON not found. Re-run regression assets in Dagster.")

# Correlations- Tab 4
with tab_corr:
    st.subheader("Correlation Matrix & Heatmap")

    corr_csv = os.path.join(OUTPUT_DIR, "corr_matrix.csv")
    corr_png = os.path.join(OUTPUT_DIR, "corr_heatmap.png")

    c1, c2 = st.columns((1, 1.2))

    with c1:
        st.markdown("**Correlation Table**")
        if os.path.exists(corr_csv):
            corr_df = pd.read_csv(corr_csv, index_col=0)
            st.dataframe(corr_df.style.background_gradient(cmap="coolwarm"), use_container_width=True)
        else:
            st.warning("Correlation CSV not found. Materialise `ewaste_correlation` asset in Dagster.")

    with c2:
        st.markdown("**Heatmap**")
        if os.path.exists(corr_png):
            st.image(corr_png, use_container_width=True)
        else:
            st.warning("Correlation heatmap PNG not found.")
