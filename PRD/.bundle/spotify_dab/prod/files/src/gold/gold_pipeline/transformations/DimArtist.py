from pyspark import pipelines as dp
from pyspark.sql.functions import *

#CREATE STREAMING TABLE

@dp.table(
    name = "DimArtist_stg_table"
)
def DimArtist_stg_table():
    df_user = spark.readStream.table("azure_project_spotify.silver.DimArtist")
    return df_user

dp.create_streaming_table(
    name = "DimArtist_gold"
)

dp.create_auto_cdc_flow(
    source= "DimArtist_stg_table",
    target = "DimArtist_gold",
    keys= ["artist_id"],
    sequence_by= col("updated_at"),
    stored_as_scd_type= 2
)


