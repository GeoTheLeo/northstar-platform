<p align="center">
  <img src="docs/images/northstar_banner.png" alt="NorthStar Banner" width="100%">
</p>

# NorthStar

## Enterprise Applied AI Decision Intelligence Platform

> **Predictive Analytics • Business Intelligence • Retrieval-Augmented Generation • Executive Decision Support • MLOps**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-Machine%20Learning-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![RAG](https://img.shields.io/badge/RAG-Knowledge%20Retrieval-5C2D91?style=for-the-badge)
![MLOps](https://img.shields.io/badge/MLOps-Production%20AI-0A7E8C?style=for-the-badge)

---

## Executive Summary

NorthStar is an **enterprise Applied AI Decision Intelligence Platform** that unifies predictive analytics, business intelligence, retrieval-augmented generation (RAG), executive decision support, and production-inspired MLOps into a single intelligent software platform.

Rather than treating analytics, machine learning, and generative AI as isolated capabilities, NorthStar integrates them into one operational workflow that enables educational organizations to identify learner risk, discover behavioral patterns, generate executive insights, and interact with institutional knowledge through natural language.

Built as the flagship project of an Applied AI engineering portfolio, NorthStar demonstrates modern software engineering practices including modular architecture, dependency injection, machine learning pipelines, repository abstraction, retrieval-augmented generation, and enterprise-oriented design.

---

## Why NorthStar?

Modern educational institutions generate vast amounts of operational and learner data, yet much of that information remains fragmented across reporting systems, spreadsheets, and institutional knowledge bases.

NorthStar consolidates these capabilities into a unified decision platform that empowers institutional leaders to move from reactive reporting to proactive, AI-assisted decision making.

The platform combines predictive machine learning, executive analytics, semantic search, and AI-powered recommendations into a cohesive experience designed around real organizational workflows rather than isolated technical demonstrations.

---

## Platform Highlights

| Capability | Business Outcome |
|------------|------------------|
| 🎯 Early Warning System | Predict learners at risk before performance declines |
| 👥 Learner Segmentation | Discover behavioral cohorts for targeted interventions |
| 📊 Executive BI Dashboard | Deliver institution-wide KPIs and strategic insights |
| 🤖 AI Knowledge Assistant | Enable semantic search across institutional knowledge |
| 🧠 Executive Copilot | Generate AI-powered executive briefings and recommendations |
| ⚙️ MLOps Foundation | Demonstrate production-inspired deployment and monitoring practices |

---

---

# Business Challenge

Educational institutions generate large volumes of learner, engagement, and operational data every day. Despite this abundance of information, many organizations continue to rely on fragmented reporting systems, manual analysis, and reactive intervention strategies.

As a result, institutional leaders often struggle to:

- Identify learners at risk before performance declines
- Understand behavioural patterns across diverse learner populations
- Transform operational data into executive decision intelligence
- Provide staff with fast, contextual access to institutional knowledge
- Operationalize machine learning models beyond experimentation
- Deliver consistent, data-driven intervention strategies across departments

NorthStar addresses these challenges through a unified Applied AI platform that combines predictive analytics, business intelligence, semantic knowledge retrieval, and executive decision support into a single operational ecosystem.

---

# Business Value

NorthStar was designed with a business-first philosophy. Every technical capability exists to improve a measurable organisational outcome rather than simply demonstrate an AI technique.

| Platform Capability | Business Outcome |
|---------------------|------------------|
| 🎯 Early Warning System | Detect learner risk early and support proactive intervention |
| 👥 Learner Segmentation | Personalise engagement strategies using behavioural analytics |
| 📊 Executive BI Dashboard | Provide leadership with institution-wide operational visibility |
| 🤖 AI Knowledge Assistant | Accelerate access to institutional knowledge through semantic search |
| 🧠 Executive Copilot | Generate executive briefings and strategic recommendations |
| ⚙️ MLOps Foundation | Demonstrate production-inspired model lifecycle management |

By integrating these capabilities into a single platform, NorthStar demonstrates how Applied AI can move beyond isolated machine learning models to become an operational decision intelligence system.

---

# Design Principles

NorthStar was engineered around a set of architectural principles commonly found in enterprise software systems.

- **Business-first architecture** where technical components serve measurable organisational objectives.
- **Modular service design** allowing individual capabilities to evolve independently.
- **Separation of concerns** through clearly defined domain boundaries.
- **Dependency injection** to reduce coupling and improve maintainability.
- **Unified analytics pipeline** that orchestrates predictive analytics, segmentation, business intelligence, and AI-driven recommendations.
- **Production-inspired engineering practices** including testing, type checking, repository abstraction, and MLOps concepts.

These principles guided every architectural decision throughout the project and helped create a platform that is both extensible and maintainable.

---

# Platform Capabilities

NorthStar combines six complementary capabilities into a unified Applied AI decision intelligence platform. Each capability contributes to a measurable organisational outcome while remaining modular and independently maintainable.

| Capability | Description | Business Outcome |
|------------|-------------|------------------|
| 🎯 Early Warning System | Predicts learners at risk using supervised machine learning. | Enables proactive intervention before performance declines. |
| 👥 Learner Segmentation | Groups learners into behavioural cohorts using clustering. | Supports targeted engagement strategies. |
| 📊 Executive BI Dashboard | Presents KPIs, trends, and executive analytics. | Improves institutional visibility and strategic planning. |
| 🤖 AI Knowledge Assistant | Uses Retrieval-Augmented Generation (RAG) for semantic search. | Accelerates access to institutional knowledge. |
| 🧠 Executive Copilot | Generates executive summaries and recommendations. | Supports faster executive decision making. |
| ⚙️ MLOps Foundation | Demonstrates production-inspired model lifecycle management. | Supports maintainable and scalable AI deployment. |

---
# Technology Stack

| Layer | Technologies |
|-------|--------------|
| Programming | Python 3.11, SQL |
| Data Engineering | Pandas, NumPy |
| Machine Learning | Scikit-learn, K-Means Clustering |
| Business Intelligence | Streamlit, Plotly |
| Generative AI | Sentence Transformers, Retrieval-Augmented Generation (RAG) |
| MLOps | Docker, GitHub Actions, Model Monitoring |
| Architecture | Dependency Injection, Repository Pattern, Modular Services |

---
# Platform Workflow

```text
Educational Data
        │
        ▼
Data Engineering
        │
        ├──────────────┐
        ▼              ▼
Early Warning    Learner Segmentation
        │              │
        └──────┬───────┘
               ▼
Business Intelligence
               │
               ▼
Executive Decision Layer
        ├───────────────┐
        ▼               ▼
Executive Copilot   Knowledge Assistant (RAG)
               │
               ▼
Institutional Decision Support
```

---
# Platform Architecture

NorthStar follows a layered architecture that separates presentation, orchestration, analytics, machine learning services, and infrastructure into clearly defined modules.

This modular approach enables each capability to evolve independently while maintaining a cohesive and maintainable enterprise application.

### Architectural Characteristics

- Business-first architecture
- Modular service design
- Dependency injection
- Repository abstraction
- Layered application architecture
- Production-inspired engineering practices

---
# Repository Tour

NorthStar is organised into modular packages that separate business capabilities, machine learning workflows, infrastructure, and user interface concerns.

| Package | Responsibility |
|----------|----------------|
| `advisor/` | Generates executive recommendations using business rules and AI-assisted reasoning. |
| `analysis/` | Coordinates the unified analytics pipeline that powers the platform. |
| `bi/` | Business Intelligence metrics, KPIs, dashboards, and reporting utilities. |
| `core/` | Shared interfaces, configuration, protocols, and common utilities. |
| `demo/` | Demonstration scenarios and presentation modes used throughout the platform. |
| `early_warning/` | Predictive machine learning pipeline for learner risk detection. |
| `executive/` | Executive workspace components and strategic overview functionality. |
| `feature_store/` | Centralised feature definitions and reusable feature engineering assets. |
| `insights/` | Executive insight generation and strategic analysis. |
| `logging/` | Centralised application logging infrastructure. |
| `mlops/` | Model registry, metadata, loading, and deployment support. |
| `models/` | Shared domain models used throughout the application. |
| `monitoring/` | Platform health monitoring and operational diagnostics. |
| `navigation/` | Workspace navigation and application routing. |
| `repositories/` | Repository abstraction supporting multiple data sources. |
| `segmentation/` | Behavioural clustering and learner segmentation services. |
| `services/` | Business services coordinating platform workflows. |
| `simulation/` | Scenario simulation and executive planning tools. |
| `status/` | Platform status components displayed throughout the UI. |
| `ui/` | Streamlit presentation layer and user interface components. |

---
# Engineering Decisions

NorthStar was intentionally engineered as a modular software platform rather than a collection of independent machine learning notebooks.

Several architectural decisions guided the implementation:

- Business capabilities are organised into independent packages with clearly defined responsibilities.
- Machine learning services remain isolated from presentation logic.
- Shared domain models minimise duplication across services.
- Repository abstraction allows future migration to alternative data sources without changing business logic.
- Dependency injection reduces coupling and improves maintainability.
- The platform emphasises readability, extensibility, and long-term maintainability over unnecessary complexity.

These principles reflect production-inspired engineering practices commonly found in enterprise AI systems.

---
# Quality Assurance

NorthStar follows a release-oriented development workflow designed to improve long-term maintainability and reliability.

Quality practices include:

- Static type checking with **mypy**
- Code quality enforcement with **ruff**
- Automated testing with **pytest**
- Modular architecture with dependency injection
- Repository abstraction
- Production-inspired MLOps concepts
- Release candidate stabilisation before publication

This engineering discipline mirrors the software delivery practices used by professional development teams.

---
# Repository Structure

```text
northstar-platform/
│
├── src/
│   └── northstar/
│       ├── advisor/
│       ├── analysis/
│       ├── bi/
│       ├── core/
│       ├── demo/
│       ├── early_warning/
│       ├── executive/
│       ├── feature_store/
│       ├── insights/
│       ├── logging/
│       ├── mlops/
│       ├── models/
│       ├── monitoring/
│       ├── navigation/
│       ├── repositories/
│       ├── segmentation/
│       ├── services/
│       ├── simulation/
│       ├── status/
│       └── ui/
│
├── docs/
├── tests/
└── README.md
```

---