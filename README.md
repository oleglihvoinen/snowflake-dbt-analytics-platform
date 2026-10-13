# Modern Snowflake + dbt ELT Analytics Platform

A layered Snowflake/dbt analytics platform with explicit controls for **incremental correctness, late-arriving data, idempotent replay, reconciliation and operational auditability**.

## Architecture

```text
Operational sources
      ↓
Snowflake RAW
      ↓
dbt staging / reusable transformations
      ↓
incremental facts + dimensions
      ↓
dimensional marts
      ↓
BI / semantic / AI consumers

Control plane: watermark windows · replay · reconciliation · run audit · DQ exceptions
```

## Implemented engineering depth

- RAW → staging → marts separation
- incremental Snowflake MERGE fact processing
- bounded watermark lookback for late-arriving updates
- deterministic payload hashes for change comparison
- idempotent batch reprocessing
- last-write-wins state reducer with delete handling
- source/target reconciliation detecting missing, unexpected and hash-mismatched business keys
- pipeline-run audit table
- data-quality exception table
- automated tests covering watermarks, replay, late arrivals, deletes and reconciliation
- CI validation for the incremental control logic

The Python control module is a locally testable representation of the state-management rules that complement the dbt/Snowflake SQL.

## Why the lookback matters

A strict `updated_at > max(updated_at)` filter can permanently miss late-arriving records. The fact model intentionally re-reads a bounded overlap window; Snowflake MERGE and deterministic payload hashes make that replay safe.

**Technologies:** Snowflake · dbt · SQL · Python · incremental ELT · MERGE · watermarks · reconciliation · dimensional modeling · CI/CD
