
from dagster import Definitions, load_assets_from_modules

from assets import raw_data, processed_data, modelling_data, regression_models
from dashboards.dashboard_asset import dashboard_info
from resources.db_resources import mongo_resource, postgres_resource
from dotenv import load_dotenv
import os
load_dotenv()

defs = Definitions(
    assets=load_assets_from_modules([
        raw_data,
        processed_data,
        modelling_data,
        regression_models,
    ]) + [dashboard_info],
    
resources = {
    "mongo": mongo_resource.configured({
        "MONGO_URI": os.getenv("MONGO_URI")
    }),
    "postgres": postgres_resource.configured({
        "POSTGRES_URL": os.getenv("POSTGRES_URL")
    })
}
)


