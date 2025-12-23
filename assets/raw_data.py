
import os
import json
import requests
import pandas as pd
from dagster import asset, AssetExecutionContext

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)


@asset(group_name="raw")
def gdp_raw_json(context: AssetExecutionContext):
    url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.CD?format=json&per_page=20000"
    resp = requests.get(url)
    data = resp.json()

    out_path = os.path.join(RAW_DIR, "gdp_per_capita.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    context.log.info("Saved gdp_per_capita.json")
    return data


@asset(group_name="raw")
def population_raw_json(context: AssetExecutionContext):
    url = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=20000"
    resp = requests.get(url)
    data = resp.json()

    out_path = os.path.join(RAW_DIR, "population.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    context.log.info("Saved population.json")
    return data


@asset(group_name="raw", required_resource_keys={"mongo"})
def ewaste_raw_from_mongo(context):
    client = context.resources.mongo
    db = client["worldbank_ewaste"]
    collection = db["ewaste_2012_2023_flat"]

    docs = list(collection.find({}, {"_id": 0}))
    df = pd.DataFrame(docs)

    context.log.info(f"Loaded {df.shape[0]} rows from MongoDB (ewaste_2012_2023_flat).")
    context.log.info(f"Columns: {df.columns.tolist()}")

    return df

@asset(group_name="raw", required_resource_keys={"mongo"})
def gdp_json_to_mongo(context, gdp_raw_json):
    client = context.resources.mongo
    db = client["ewaste_db"]
    
    # Drop old records and load new ones
    db["gdp_per_capita"].delete_many({})
    db["gdp_per_capita"].insert_many(gdp_raw_json[1])

    context.log.info("GDP JSON data inserted into MongoDB.")
    return True


@asset(group_name="raw", required_resource_keys={"mongo"})
def population_json_to_mongo(context, population_raw_json):
    client = context.resources.mongo
    db = client["ewaste_db"]
    db["population"].delete_many({})
    db["population"].insert_many(population_raw_json[1])

    context.log.info("Population JSON data inserted into MongoDB.")
    return True