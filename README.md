# Incremental Streaming ED Pipeline  
### Firehose → Glue → Redshift with Idempotent Merge & Event-Time Conflict Resolution

---

## Overview

This project implements an incremental streaming Emergency Department (ED) pipeline using:

- Amazon Kinesis Data Firehose  
- AWS Glue  
- Amazon Redshift  

It processes high-concurrency A&E event data and produces a **single up-to-date row per attendance**, using:

- Incremental ingestion  
- Idempotent merge logic  
- Event-time conflict resolution  
- SCD1 overwrite semantics  
- Controlled reprocessing and quarantine handling  

The system favours warehouse-native incremental logic over unnecessary lakehouse complexity.

---

## Use Case

- High-concurrency A&E data  
- Events pushed to S3 via Firehose as JSON  
- 15–30 minute latency acceptable  
- Final output: **1 row per attendance with most up-to-date data**  
- Same attendance may be updated multiple times  
- Only latest inbound files processed  
- Historical partitions become increasingly stable over time  
- Data must live in a DW to support joins (e.g. IP data)  
- 99% of queries target last week’s data  

---

## Architectural Decisions

### Why Not Iceberg?

- Still requires loading and merging into Redshift  
- Adds unnecessary complexity  
- No strong need for time travel  
- Redshift already provides transactional MERGE  

### Why Not Athena?

- Relies heavily on drop/recreate patterns  
- Poor fit for incremental upserts  
- Not designed for mutable fact rows  

### Why Redshift-Centric?

Redshift provides:

- Efficient `COPY` ingestion  
- Transactional `MERGE`  
- Warehouse-native joins  
- Strong incremental update patterns  

---

## Final Pipeline Design

### 1. Ingestion

**Firehose → S3 (Raw Landing Zone)**

- JSON event payloads  
- Partitioned by ingestion date  
- Firehose provides:
  - Delivery reliability  
  - Automatic batching  
  - At-least-once semantics  
  - Buffering for ingestion spikes  

---

### 2. JSON → Parquet Conversion

Handled by Glue:

- Converts JSON to Parquet  
- Enforces schema  
- Compresses using Snappy  
- Processes only new ingestion partitions  

Benefits:

- Faster Redshift COPY  
- Column pruning efficiency  
- Better compression  
- Lower cost  

---

### 3. Incremental Load into Redshift

#### COPY into Staging

- COPY is the most efficient ingestion method  
- Only latest ingestion partitions are copied  
- Metadata table stores last processed S3 prefix  
- Idempotent design allows safe reprocessing  

If multiple Glue files exist since last load:
- They are copied together  
- Duplicates handled in staging  

---

### 4. Staging Clean-up

Inside Redshift:

- Remove test patients  
- Fix data types  
- Remove duplicates  
- Apply data quality checks  

---

### 5. Merge Strategy (Core Logic)

- 1 row per attendance  
- SCD1 overwrite semantics  
- Updated incrementally via MERGE  

---

#### Insert Logic

- Admissions inserted first (and before any updates are attempted)
- Prevents discharge processing before attendance exists  

---

#### Update Logic

- last_modified_ts is authoritative  
- If inbound timestamp > stored timestamp → overwrite  
- Supports:
  - Backdated corrections  
  - Out-of-sequence file loads  
  - Safe reprocessing  

Each tracked field stores its own modification timestamp.

This guarantees:

- Event-time conflict resolution  
- Idempotency  
- Protection against replay corruption  

---

## Why SCD1 (Not SCD2)

- Raw event history preserved in S3  
- ED reporting uses current truth  
- SCD2 adds unnecessary complexity  
- Fact table remains clean  

If historical comparisons are required:
- Reconstruct from event-level data  

---

## Redshift Design

### Fact Table

- 1 row per attendance_id  
- Derived metrics (e.g. breach)  
- Current best-known timestamps  
- Optimized for warehouse joins  

### Distribution Key


### Sort Key


---

## Error Handling

### Logged Errors

- Discharge before admission  
- Events for non-existent attendances  
- Missing attendance IDs  

### Quarantine Process

- Invalid rows stored separately  
- Reprocessing attempted for 1 day  
- Handles out-of-order arrival naturally  

Prevents:

- Hard failures  
- Pipeline corruption  
- Lost data  

---

## Why Historical Data Stays in Redshift

Considered splitting hot/cold storage but rejected because:

- A&E volumes do not justify complexity  
- Redshift storage cost acceptable  
- Simpler architecture preferred  

Future option if volumes increase significantly.

---

## Key Architectural Principles

- Decoupled ingestion and processing  
- Incremental processing only  
- No full table rebuilds  
- Idempotent merge design  
- Event-time > file-time precedence  
- Warehouse-native logic preferred  
- Raw data always preserved  

---

## Summary

This pipeline demonstrates:

- Incremental streaming ingestion  
- Reliable micro-batch processing  
- Warehouse-based conflict resolution  
- SCD1 state management  
- Idempotent merge design  
- Realistic healthcare event modelling  