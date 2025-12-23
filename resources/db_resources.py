
from dagster import resource
from pymongo import MongoClient
from sqlalchemy import create_engine


@resource
def mongo_resource(init_context):
    uri = init_context.resource_config["MONGO_URI"]
    client = MongoClient(uri)
    return client


@resource
def postgres_resource(init_context):
    url = init_context.resource_config["POSTGRES_URL"]
    engine = create_engine(url)
    return engine
