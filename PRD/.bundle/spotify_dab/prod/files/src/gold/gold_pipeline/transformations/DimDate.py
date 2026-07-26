from pyspark import pipelines as dp
from pyspark.sql.functions import *

#CREATE STREAMING TABLE

@dp.table(
    name = "DimDate_stg_table"
)
def DimDate_stg_table():
    df_user = spark.readStream.table("azure_project_spotify.silver.DimDate")
    return df_user

dp.create_streaming_table(
    name = "DimDate_gold"
)

dp.create_auto_cdc_flow(
    source= "DimDate_stg_table",
    target = "DimDate_gold",
    keys= ["date_key"],
    sequence_by= col("date"),
    stored_as_scd_type= 2
)


