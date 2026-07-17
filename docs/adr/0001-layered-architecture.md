# ADR-0001: Layered Application Architecture

## Status

Accepted

## Context

NorthStar integrates predictive analytics, learner segmentation, executive BI, RAG, and MLOps.

As functionality expanded, placing business logic directly inside the Streamlit application reduced maintainability and made testing difficult.

## Decision

NorthStar adopts a layered architecture consisting of:

Presentation Layer

- Streamlit UI

Application Layer

- Controller

Service Layer

- Business Services

Repository Layer

- Data Access

Domain Layer

- Typed Models

## Consequences

Advantages

- Separation of concerns - yes!
- Easier testing!
- Improved maintainability
- Future web front-end support
- Cleaner dependency flow - so much nicer working this way