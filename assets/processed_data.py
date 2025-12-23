
import pandas as pd
from dagster import asset
from typing import Dict

START_YEAR = 2012
END_YEAR = 2023


def _worldbank_to_df(raw_json: Dict) -> pd.DataFrame:
    """Convert World Bank raw JSON to tidy DataFrame and filter 2012–2023."""
    records = raw_json[1]
    df = pd.DataFrame(records)

    c = pd.json_normalize(df["country"])
    df["country"] = c["value"]
    df["countryiso3code"] = c["id"]

    df["year"] = pd.to_numeric(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    df = df[(df["year"] >= START_YEAR) & (df["year"] <= END_YEAR)]

    return df[["country", "countryiso3code", "year", "value"]]


@asset(group_name="processed")
def gdp_df(gdp_raw_json) -> pd.DataFrame:
    df = _worldbank_to_df(gdp_raw_json)
    df = df.rename(columns={"value": "gdp_per_capita"})
    return df


@asset(group_name="processed")
def population_df(population_raw_json) -> pd.DataFrame:
    df = _worldbank_to_df(population_raw_json)
    df = df.rename(columns={"value": "population"})
    return df


@asset(group_name="processed")
def ewaste_europe_long(context, ewaste_raw_from_mongo: pd.DataFrame) -> pd.DataFrame:
    df = ewaste_raw_from_mongo.copy()

    context.log.info(f"Raw e-waste columns: {list(df.columns)}")
    possible_country_cols = ["country", "Geopolitical entity (reporting)", "country_name"]
    possible_year_cols = ["year", "Time"]
    possible_op_cols = ["management_operation", "Waste management operations"]
    possible_unit_cols = ["unit", "Unit of measure"]
    possible_val_cols = ["ewaste_value", "value", "kg_per_capita", "kg_per_cap"]

    def pick_column(possibles):
        for col in possibles:
            if col in df.columns:
                return col
        raise ValueError(f"None of {possibles} found in columns: {df.columns.tolist()}")

    col_country = pick_column(possible_country_cols)
    col_year = pick_column(possible_year_cols)
    col_operation = pick_column(possible_op_cols)
    col_unit = pick_column(possible_unit_cols)
    col_value = pick_column(possible_val_cols)

    # Rename standard names
    df = df.rename(columns={
        col_country: "country",
        col_year: "year",
        col_operation: "management_operation",
        col_unit: "unit",
        col_value: "ewaste_value"
    })

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["country", "year", "unit", "management_operation", "ewaste_value"])

    # Keep only kg per capita
    df = df[df["unit"].str.contains("per capita", case=False, na=False)]

    context.log.info(f"ewaste_europe_long shape: {df.shape}")

    return df[["country", "year", "management_operation", "unit", "ewaste_value"]]


@asset(group_name="processed", required_resource_keys={"mongo"})
def clean_ewaste_to_mongo(context, ewaste_europe_long):
    client = context.resources.mongo
    db = client["ewaste_db"]

    # convert rows to dict
    records = ewaste_europe_long.to_dict(orient="records")

    collection = db["clean_e_waste"]
    collection.delete_many({})        
    collection.insert_many(records)   
    context.log.info(f"Inserted {len(records)} documents into MongoDB.")

@asset(group_name="processed", required_resource_keys={"mongo"})
def clean_ewaste_from_mongo(context):
    client = context.resources.mongo
    db = client["ewaste_db"]
    collection = db["clean_e_waste"]

    data = list(collection.find({}, {"_id": 0}))
    df = pd.DataFrame(data)

    context.log.info(f"Loaded {df.shape[0]} rows from MongoDB.")
    return df
