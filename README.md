# Azure Data Factory - Metadata-Driven Incremental & Backdated SQL Data Pipeline

## Project Overview

This project demonstrates a **metadata-driven Azure Data Factory (ADF) pipeline** that performs **incremental data ingestion** from Azure SQL Database into Azure Data Lake Storage Gen2 (ADLS Gen2).

The pipeline dynamically processes multiple tables using a **ForEach** activity and supports both:

- **Incremental Loads** using Change Data Capture (CDC) columns
- **Backdated Refreshes** using a configurable `from_date` parameter

Data is stored in the **Bronze layer** in **Parquet** format, while the latest processed CDC value is maintained in JSON metadata files.

---

# Solution Architecture

```
                    Azure SQL Database
                            │
                            │
                    Metadata (file_loop)
                            │
                            ▼
                  ForEach (Dynamic Tables)
                            │
        ┌───────────────────┴────────────────────┐
        │                                        │
        ▼                                        ▼
Lookup Last CDC                        Use from_date (Optional)
        │                                        │
        └───────────────┬────────────────────────┘
                        ▼
              Determine Start Timestamp
                        │
                        ▼
             Copy Incremental Records
                        │
                        ▼
        Write Parquet Files to ADLS Gen2
                        │
         ┌──────────────┴──────────────┐
         │                             │
         ▼                             ▼
No Records Copied             Records Copied
Delete Empty File             Get MAX(CDC)
                                     │
                                     ▼
                           Update cdc.json
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
- Azure Logic Apps
- Parquet
- JSON Metadata

---

# Features

- Metadata-driven pipeline
- Dynamic processing of multiple SQL tables
- Incremental loading using CDC timestamp columns
- Backdated refresh using `from_date`
- Automatic CDC tracking
- Dynamic SQL query generation
- Parquet output format
- Empty file cleanup
- Logic App notifications
- Easily scalable by adding new table metadata

---

# Metadata Configuration

The pipeline uses a parameter named **file_loop**.

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
    "from_date": "2026-01-01 00:00:00"
  }
]
```

## Metadata Fields

| Field | Description |
|--------|-------------|
| schema | SQL schema name |
| table | Source table |
| cdc_col | Incremental timestamp column |
| from_date | Optional backdated refresh date |

---

# Loading Modes

## 1. Incremental Load

When `from_date` is empty, the pipeline reads the latest processed timestamp from:

```
bronze/
   <table>_cdc/
      cdc.json
```

Example:

```json
{
    "cdc":"2026-07-24T10:15:30"
}
```

The pipeline generates a query similar to:

```sql
SELECT *
FROM dbo.DimUser
WHERE updated_at > '2026-07-24T10:15:30'
```

Only newly inserted or updated records are copied.

---

## 2. Backdated Refresh

When a value is supplied in `from_date`, the pipeline ignores the stored CDC value.

Example:

```json
{
    "table":"FactStream",
    "from_date":"2026-01-01 00:00:00"
}
```

Generated SQL:

```sql
SELECT *
FROM dbo.FactStream
WHERE stream_timestamp > '2026-01-01 00:00:00'
```

This enables selective historical reprocessing without performing a full refresh.

### Backdated Refresh Use Cases

- Reload historical data
- Recover missed records
- Reprocess corrected source data
- Data quality fixes
- Partial historical backfills

---

# Pipeline Workflow

### Step 1

Loop through each table using the metadata parameter.

↓

### Step 2

Determine the extraction start timestamp.

```
IF from_date is provided
      Use from_date
ELSE
      Read latest CDC from cdc.json
```

↓

### Step 3

Execute incremental SQL query.

↓

### Step 4

Write records into ADLS Gen2 in Parquet format.

Example:

```
bronze/
   DimUser/
      DimUser_2026-07-24T11-20-00.parquet
```

↓

### Step 5

If no rows are copied

- Delete empty output file

↓

### Step 6

If records are copied

Execute:

```sql
SELECT MAX(updated_at)
FROM dbo.DimUser
```

↓

### Step 7

Update CDC metadata.

Example:

```
bronze/
   DimUser_cdc/
      cdc.json
```

```json
{
    "cdc":"2026-07-24T11:45:12"
}
```

↓

### Step 8

Trigger Azure Logic App notification after pipeline completion.

---

# Project Structure

```
ADF-Incremental-SQL-Load
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
│   └── AzureDataLakeStorage.json
│
├── images/
│   ├── architecture.png
│   ├── pipeline.png
│   └── workflow.png
│
└── README.md
```

---

# Output Structure

```
bronze/

├── DimUser/
│     DimUser_2026-07-24.parquet
│
├── DimArtist/
│     DimArtist_2026-07-24.parquet
│
├── DimTrack/
│     DimTrack_2026-07-24.parquet
│
├── FactStream/
│     FactStream_2026-07-24.parquet
│
├── DimUser_cdc/
│     cdc.json
│
├── DimArtist_cdc/
│     cdc.json
│
└── FactStream_cdc/
      cdc.json
```

---

# Advantages

- Metadata-driven design
- Supports multiple tables
- No hardcoded SQL queries
- Incremental loading for better performance
- Backdated refresh capability
- Reduced data movement
- Lower storage and compute costs
- Easily extensible
- Production-ready architecture

---



# Author

**Sayali Raut**

Azure Data Engineer | Azure Data Factory | Azure SQL | Azure Data Lake | ETL | Data Engineering

---

# License

This project is licensed under the MIT License.
