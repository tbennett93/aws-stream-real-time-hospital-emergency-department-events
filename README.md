
# Incremental Streaming ED Pipeline  
### Firehose → Glue → Redshift + dbt (Airflow Orchesated)

---

## Overview

This project implements an incremental streaming Emergency Department (ED) pipeline using:

- Amazon Data Firehose    
- Amazon Glue  
- Amazon Redshift  
- dbt  
- Apache Airflow (Dockerised orchestration)

It processes high-concurrency A&E event data and produces a single, analytics-ready row per attendance, with full historical traceability

Key capabilities:

- Incremental ingestion  
- Idempotent merge logic  
- Event-time conflict resolution  
- dbt-based transformation layer  
- Containerised orchestration (Airflow)  

---

## Use Case

- High-concurrency A&E data  
- Events pushed to S3 via Firehose as JSON  
- 15–30 minute latency acceptable  
- Same attendance updated multiple times  
- Out-of-order events expected  

Outputs:
- Event-level dataset (full history)  
- Attendance-level dataset (latest state)  

---

## Architecture

### Ingestion → Processing → Modelling

Airflow → orchestration  

1. Firehose → S3 (raw JSON)  
2. Glue → Parquet conversion  
3. Glue → Redshift load 
4. dbt → transformation layer  

---

## Architectural Decisions

### Why Not Iceberg?

- Still requires downstream warehouse merge  
- Adds complexity without strong benefit  
- No requirement for time travel  

---

### Why Not Athena?

- Poor support for incremental upserts  
- Not suited for mutable fact rows  

---

### Why Redshift-Centric?

- Native `COPY` performance  
- Transactional `MERGE`  
- Strong OLAP performance  
- Supports mutable, late-arriving data  

---

## Pipeline Design

### 1. Ingestion

**Firehose → S3**

- JSON payloads  
- Test data simulates out-of-order events  
- Partitioned by ingestion date  
- At-least-once delivery  

---

### 2. JSON → Parquet Conversion (Glue)

- Schema enforcement  
- Snappy compression  
- Only new files processed (manifest tracking)  
- Python Shell used for cost efficiency  

---

### 3. Load into Redshift

- COPY into staging  
- Metadata tracks last processed S3 prefix  
- Redshift COPY JOB used for auto-detection  

Handles:
- Multiple files per batch  
- Duplicate ingestion safely  

---

### 4. Staging Clean-up

- Remove test data  
- Fix data types  
- Deduplicate  
- Apply quality checks  

---

### 5. Refresh Strategy 

- **1 row per attendance**
- Most recent `recorded_ts` wins  

Supports:

- Out-of-order events  
- Backdated corrections  
- Idempotent reprocessing  

Each field tracks its own modification timestamp.

---

## dbt Transformation Layer

dbt is used to structure the analytical layer on top of Redshift.

### Why Not dbt Snapshots?

Snapshots are **not used**.

**Reason:**
- Streaming batches can arrive late or out of order  
- Snapshots risk missing or incorrectly versioning changes  

**Instead:**
- Full history is stored in raw/event tables  
- SCD Type 2 logic is implemented explicitly in dbt  

---

### Model Layers

#### Staging

- Cleans raw data  
- Standardises formats  
- Deduplicates records  

---

#### `dim_patient`

- Implements **SCD Type 2**
- Tracks attribute changes over time  
- Uses:
  - `valid_from`
  - `valid_to`
  - current flag  

---

#### `fact_ed_events`

- Event-level dataset  
- Full historical record of all events  
- Used for reconstruction and auditing  

---

#### `fact_ed_attendances`

- Aggregated attendance-level dataset  
- Rolls up events into a single row  

Logic:
- Identifies key event types (arrival, discharge, etc.)  
- Selects the **most recent occurrence per event type**  
- Produces a single, analysis-ready record per attendance  

---

## Metadata & Traceability

Raw staging tables include:

- `processed_timestamp`  
- `source_file_name`  

This enables:

- Full traceability to source files  
- Debugging of ingestion issues  
- Reconciliation and auditability  

---

## Orchestration (Airflow)

Pipeline steps:

1. Convert JSON → Parquet (Glue)  
2. Load Parquet → Redshift (Glue)  
3. Run dbt transformations (DockerOperator)  

---

## Docker Setup

- Airflow runs in its own container  
- dbt runs in a **separate container**  
- Airflow triggers dbt via `DockerOperator`  

Benefits:

- Isolation of dependencies  
- Reproducibility  
- Flexibility for scaling  

---

## Error Handling

### Logged Errors

- Discharge before admission  
- Events for non-existent attendances  
- Missing attendance IDs  

---

### Quarantine Process

- Invalid rows stored separately  
- Allows processing of valid rows without breaking pipeline
Prevents:

- Pipeline failure  
- Data loss  
- Corruption  

---


## What I Would Do Next

### 1. Incremental dbt Models

Currently, dbt models are fully rebuilt.

Next step:
- Convert large models to incremental  
- Use ingestion timestamps / change detection  

Benefits:
- Faster runtime  
- Reduced compute cost  
- Better scalability  

---
### 2. Improved Orchestration

- Add alerting  
- Improve retry/backoff strategies  
- Parameterise DAG for environments  

---


## Summary

This pipeline demonstrates:

- Streaming-compatible data modelling  
- Robust handling of late-arriving data  
- Idempotent, event-time driven updates  
- SCD2 dimension modelling in dbt  
- Separation of ingestion, processing, and analytics layers  
- Containerised, production-style orchestration  