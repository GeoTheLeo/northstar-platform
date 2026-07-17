# ADR-0003: DuckDB Analytical Warehouse

## Status

Accepted

## Context

NorthStar requires analytical querying across learner engagement, predictions, segmentation, and executive metrics.

CSV files are appropriate for prototypes but not for analytical workloads - go big or go home.

## Decision

Use DuckDB as the embedded analytical warehouse.

## Consequences

Advantages

- SQL-first analytics
- Fast local execution
- Embedded deployment
- Excellent Parquet support!
- Future scalability - so nice to be prepared!