# E-Waste Management Analytics in Europe (2012–2023)
### End-to-End Data Engineering, Statistical Modelling & Dashboard Project
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Dagster](https://img.shields.io/badge/Dagster-Orchestration-6C5CE7?style=flat-square&logo=dagster)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit)
![MongoDB](https://img.shields.io/badge/MongoDB-NoSQL-green?logo=mongodb&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=flat-square&logo=postgresql)


## Why This Project Matters
Electronic waste is one of the fastest-growing waste streams globally. This project delivers a **longitudinal, policy-aware data analytics solution** that evaluates how effectively European countries manage e-waste  and what socio-economic factors drive performance.

Built as a **production-style analytics pipeline**, the project demonstrates skills across **data engineering, statistical modelling, automation, and visual analytics**.

---

## What I Built (At a Glance)
✔ Automated multi-source data ingestion (APIs)  
✔ Cleaned & integrated 11 years of panel data  
✔ Performed regression & correlation analysis    
✔ Built an automated **Dagster pipeline**  
✔ Deployed an interactive **Streamlit dashboard**

---

## Key Questions Answered
- Does **GDP per capita** influence how well countries manage e-waste?
- Does **population size** influence e-waste generation and recovery?
- Did the **2018 WEEE Open Scope Directive** improve e-waste management outcomes?

---

## Data Sources
- **E-waste management data:** :contentReference[oaicite:0]{index=0}  
- **Socio-economic indicators:** :contentReference[oaicite:1]{index=1}  

Data accessed programmatically via REST APIs for reproducibility.

---

## Architecture & Workflow
APIs → MongoDB (raw) → PostgreSQL (clean)
→ Dagster Assets → Statistical Models
→ Streamlit Dashboard

---

## Analytical Methods Used
- Exploratory Data Analysis (EDA)
- Time-series trend analysis
- Pearson correlation
- Multiple Linear Regression (OLS)
- Country-level normalisation and ranking

All modelling decisions were justified with statistical assumptions and diagnostics.

---

## Key Insights
- **GDP per capita** is a strong predictor of e-waste recovery and recycling efficiency
- **Population size** correlates more with *generation* than with *treatment quality*
- Ewaste management improved notably **post-2018**, following regulatory expansion
- Nordic countries consistently outperform despite shared EU policy — indicating governance and infrastructure effects beyond legislation

---

## Dashboard
The Streamlit dashboard allows users to:
- Explore trends by country and year
- Compare pre- and post-2018 performance
- Visualise correlations and regression outputs
- Interactively assess circular economy performance

---

## Tech Stack
**Languages & Libraries**
- Python (Pandas, NumPy, Statsmodels, Matplotlib, Seaborn)
**Data & Storage**
- MongoDB (raw ingestion)
- PostgreSQL (structured analytics)
**Orchestration & Apps**
- Dagster (asset-based pipelines)
- Streamlit (interactive dashboard)

---

## Author
**Miracle Deborah Oluwawole**  
📧 miracleoluwawole@gmail.com  
