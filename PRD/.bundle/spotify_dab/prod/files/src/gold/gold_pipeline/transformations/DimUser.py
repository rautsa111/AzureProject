from pyspark import pipelines as dp
from pyspark.sql.functions import *

expectations ={
     "rule1" : "user_id IS NOT NULL"
}

#CREATE STREAMING TABLE

@dp.table(
    name = "DimUser_stg_table"
)
@dp.expect_or_drop("rule1",  "user_id IS NOT NULL")
def DimUser_stg_table():
    df_user = spark.readStream.table("azure_project_spotify.silver.dimuser")
    return df_user

dp.create_streaming_table(
    name = "DimUser_gold",
    expect_all_or_drop = expectations
)

dp.create_auto_cdc_flow(
    source= "DimUser_stg_table",
    target = "DimUser_gold",
    keys= ["user_id"],
    sequence_by= col("updated_at"),
    stored_as_scd_type= 2
)


