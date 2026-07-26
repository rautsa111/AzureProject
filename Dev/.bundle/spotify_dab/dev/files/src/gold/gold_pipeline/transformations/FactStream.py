from pyspark import pipelines as dp
from pyspark.sql.functions import *

#CREATE STREAMING TABLE

@dp.table(
    name = "FactStream_stg_table"
)
def FactStream_stg_table():
    df_user = spark.readStream.table("azure_project_spotify.silver.FactStream")
    return df_user

dp.create_streaming_table(
    name = "FactStream_gold"
)

dp.create_auto_cdc_flow(
    source= "FactStream_stg_table",
    target = "FactStream_gold",
    keys= ["stream_id"],
    sequence_by= col("stream_timestamp"),
    stored_as_scd_type= 1
)


