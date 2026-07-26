from pyspark import pipelines as dp
from pyspark.sql.functions import *

#CREATE STREAMING TABLE

@dp.table(
    name = "DimTrack_stg_table"
)
def DimTrack_stg_table():
    df_user = spark.readStream.table("azure_project_spotify.silver.DimTrack")
    return df_user

dp.create_streaming_table(
    name = "DimTrack_gold"
)

dp.create_auto_cdc_flow(
    source= "DimTrack_stg_table",
    target = "DimTrack_gold",
    keys= ["track_id"],
    sequence_by= col("updated_at"),
    stored_as_scd_type= 2
)


