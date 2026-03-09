# Incremental Streaming ED Pipeline  
### Firehose → Glue → Redshift with Idempotent Merge & Event-Time Conflict Resolution

---

## Overview

This project implements an incremental streaming Emergency Department (ED) pipeline using:

- Amazon Data Firehose    
- Amazon Glue
- Amazon Redshift  
- Amazon DynamoDB

It processes high-concurrency A&E event data and produces a **single up-to-date row per attendance**, using:

- Incremental ingestion  
- Idempotent merge logic  
- Event-time conflict resolution  
- Change detection based on recorded timestamp
- Controlled reprocessing and quarantine handling  


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

- Efficient COPY ingestion  
- Transactional MERGE 
- Warehouse-native joins  
- Strong incremental update patterns  
- OLAP query performance

---

## Final Pipeline Design

### 1. Ingestion

**Firehose → S3 (Raw Landing Zone)**

- JSON event payloads 
    - Test data provided generated in python locally and pushed to firehose
    - Test data forces out of order attendance streams to test pipeline accuracy 
- Partitions outbound files by ingestion date  
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
- Processes only new files
- Processed files recorded in manifest. New files defined as such if not in the manifest during processinggit
- Use Glue Python Shell for improved affordability vs Spark as data fits into memory

Benefits:

- Faster Redshift COPY  
- Better compression  
- Lower cost  
- Want to land raw files in S3 then convert later so history is retained
- Firehose functionality allows conversion on inbound processing but using this would mean the raw data layer is lost

---

### 3. Incremental Load into Redshift

#### COPY into Staging

- COPY is the most efficient ingestion method  
- Only latest ingestion partitions are copied  
- Metadata table stores last processed S3 prefix  
- Uses native redshift COPY JOB to automatically detect and load new files in s3

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
- Updated incrementally via MERGE  
- Most recently entered record 'wins'
- Assumption that patient dimension already exists in the DW

---

#### Insert Logic

- Admissions inserted first (and before any updates are attempted)
- Prevents discharge processing before attendance exists  

---

#### Update Logic

- latest recorded_ts is authoritative  
- If inbound timestamp > stored timestamp → overwrite  
- Event statuses pertaining to leaving ED count as leaving ED (i.e. discharge method).
- If updating a record that doesn't exist - quarantine the file and attempt reprocessing for 1 business day
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

## Why not SCD

- Historical point-in-time analysis not required
- Attributes are classic 'dimensions'
- last_recorded_ts can be stored in FACT for each attribute
- Raw event history preserved in S3  
- ED reporting uses current truth  

If historical comparisons are required:
- Reconstruct from event-level data  

---

## Redshift Design

### Fact Table

- 1 row per attendance_id  
- Derived metrics (e.g. breach)  
- Current best-known timestamps for key markers (e.g. triage/discharge)
  - Narrows the number of columns update from all columns to only those required
- Designed to support mutable fields (late arrivals/corrections)

#### Sort Key
- On arrival_date. This is what will be queried the most by far and is the key date for the table



#### Why no Dimension/Support Tables
- A support table could abstract away the last_recorded_ts for a cleaner fact table
- This would be needlessly complicated to ingest for minimal gain
- No point-in-time history required


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