
from dagster import asset, AssetExecutionContext

@asset(group_name="dashboard")
def dashboard_info(context: AssetExecutionContext):
    context.log.info("Run dashboard using: streamlit run dashboards/streamlit_app.py")
    return {"dashboard": "streamlit_app.py"}
