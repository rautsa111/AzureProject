# AzureProject

# Azure Data Factory - Incremental SQL to ADLS Data Pipeline

## Project Overview

This project implements an **incremental data ingestion pipeline** using **Azure Data Factory (ADF)**. The pipeline extracts only newly inserted or updated records from Azure SQL Database based on a Change Data Capture (CDC) column and stores the data as **Parquet files** in Azure Data Lake Storage Gen2 (ADLS).

The pipeline is designed to process multiple tables dynamically using a `ForEach` loop.

---

## Architecture

```
Azure SQL Database
        │
        ▼
Lookup Last CDC Value
        │
        ▼
ForEach (Each Table)
        │
        ├── Copy Incremental Data
        │
        ├── Check Records Copied
        │        │
        │        ├── No Records
        │        │      └── Delete Empty File
        │        │
        │        └── Records Found
        │               ├── Get MAX(CDC)
        │               └── Update CDC Metadata
        │
        ▼
Azure Data Lake Storage Gen2 (Bronze Layer)
        │
        ▼
Logic App Notification
```

---

# Technologies Used

- Azure Data Factory
- Azure SQL Database
- Azure Data Lake Storage Gen2
- Azure Blob Storage
- Parquet Format
- JSON Metadata
- Azure Logic Apps

---

# Features

- Incremental loading using CDC timestamp columns
- Dynamic table processing with ForEach activity
- Metadata-driven pipeline
- Automatic CDC value management
- Stores data in Parquet format
- Deletes empty output files
- Sends execution alerts through Logic App
- Easily scalable by adding tables to the parameter list

---

# Pipeline Parameters

The pipeline uses a single parameter named `file_loop`.

```json
[
  {
    "schema": "dbo",
    "table": "DimUser",
    "cdc_col": "updated_at",
    "from_date": ""
  },
  {
    "schema": "dbo",
    "table": "DimArtist",
    "cdc_col": "updated_at",
    "from_date": ""
  },
  {
    "schema": "dbo",
    "table": "DimTrack",
    "cdc_col": "updated_at",
    "from_date": ""
  },
  {
    "schema": "dbo",
    "table": "DimDate",
    "cdc_col": "date",
    "from_date": ""
  },
  {
    "schema": "dbo",
    "table": "FactStream",
    "cdc_col": "stream_timestamp",
    "from_date": ""
  }
]
```

Each object contains:

| Property | Description |
|----------|-------------|
| schema | SQL schema name |
| table | Source table |
| cdc_col | Incremental column |
| from_date | Optional override date |

---

# Pipeline Workflow

## Step 1

Loop through every table using a **ForEach** activity.

---

## Step 2

Read the latest processed CDC timestamp from:

```
bronze/
    <table>_cdc/
        cdc.json
```

---

## Step 3

Run an incremental SQL query.

Example:

```sql
SELECT *
FROM dbo.DimUser
WHERE updated_at >
'Last_CDC_Value'
```

---

## Step 4

Write the incremental records into ADLS Gen2 as Parquet.

```
bronze/
    DimUser/
        DimUser_2026-07-24T08:30:00.parquet
```

---

## Step 5

If no records are copied:

- Delete the empty Parquet file.

---

## Step 6

If records exist:

Run

```sql
SELECT MAX(updated_at)
FROM dbo.DimUser
```

---

## Step 7

Update

```
bronze/
    DimUser_cdc/
        cdc.json
```

Example

```json
{
    "cdc":"2026-07-24T12:45:19"
}
```

---

## Step 8

After the pipeline finishes, send a notification using Azure Logic Apps.

---

# Project Structure

```
ADF-Incremental-Load/
│
├── pipeline/
│   └── PL_Incremental_SQL_Load_Loop.json
│
├── datasets/
│   ├── AzureSqlTable.json
│   ├── Json.json
│   └── Parquet.json
│
├── linkedServices/
│   ├── AzureSqlDatabase.json
│   └── ADLS.json
│
├── triggers/
│
├── images/
│   ├── pipeline.png
│   └── architecture.png
│
└── README.md
```

---

# Output Folder Structure

```
bronze/

│
├── DimUser/
│      DimUser_2026-07-24.parquet
│
├── DimArtist/
│      DimArtist_2026-07-24.parquet
│
├── FactStream/
│      FactStream_2026-07-24.parquet
│
├── DimUser_cdc/
│      cdc.json
│
├── DimArtist_cdc/
│      cdc.json
│
└── FactStream_cdc/
       cdc.json
```

---

# Advantages

- Metadata-driven design
- Reusable for multiple tables
- Minimal code changes for new tables
- Faster incremental loads
- Reduced SQL load
- Lower storage costs
- Easy maintenance

---

# Future Improvements

- Parallel table execution
- Watermark table instead of JSON files
- Retry mechanism
- Logging to Azure Monitor
- Dynamic sink partitioning
- Data quality validation
- Integration with Azure Key Vault

---

# Author

**Sayali Raut**

Azure Data Engineer

---

