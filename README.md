# Snowflake + dbt Modern ELT Analytics Platform

Portfolio/reference implementation of a layered Snowflake ELT platform using dbt.

## Architecture
```text
Operational sources -> Snowflake RAW -> dbt staging -> intermediate -> dimensional marts -> BI / semantic layer
```

## Demonstrated patterns
- Layered transformation architecture
- Source declarations and quality checks
- Incremental fact processing
- Dimensional modeling
- Snowflake MERGE-oriented dbt incremental model
- Analytics-ready marts

The included order fact demonstrates how changed source records can be incrementally processed instead of rebuilding the full dataset.

This project uses generic/synthetic commerce structures and no proprietary data.
