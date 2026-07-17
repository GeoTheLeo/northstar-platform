# ADR-0002: Repository Pattern

## Status

Accepted

## Context

Dashboard logic originally loaded CSV files directly.

This tightly coupled business logic to storage.

## Decision

Introduce a Repository abstraction.

Current implementation:

- CsvDashboardRepository

Future implementations:

- DuckDBDashboardRepository
- PostgreSQLDashboardRepository

## Consequences

Changing storage technology does not affect the application layer any longer - whew!.

Business logic remains independent from storage implementation.