# Backend Architecture

## Goal

Evolve the current single-file Flask application into a production-grade FastAPI backend with clear boundaries between:

- API delivery
- application orchestration
- data acquisition
- ML pipeline execution
- feature engineering
- shared configuration and error handling

The architecture below is the source of truth for the next implementation phases.

## Architectural Principles

1. Single responsibility per module
2. Explicit data contracts at every boundary
3. Dependency inversion for external services and ML components
4. Testable business logic outside the web layer
5. Configuration through environment variables
6. A `src` layout to avoid import ambiguity

## Target Directory Layout

```text
stockmlproject/
├── app/
│   └── api/
│       └── v1/
│           └── endpoints/
├── docs/
│   └── backend-architecture.md
├── src/
│   └── stockml/
│       ├── __init__.py
│       ├── main.py
│       ├── core/
│       │   ├── config.py
│       │   ├── exceptions.py
│       │   └── logging.py
│       ├── schemas/
│       │   ├── health.py
│       │   ├── prediction.py
│       │   └── stock.py
│       ├── services/
│       │   ├── health_service.py
│       │   ├── prediction_service.py
│       │   └── stock_data_service.py
│       ├── domain/
│       │   ├── models/
│       │   └── protocols/
│       ├── ml/
│       │   ├── pipeline.py
│       │   ├── trainer.py
│       │   └── feature_engineering.py
│       └── infrastructure/
│           └── market_data/
│               └── yfinance_client.py
└── tests/
    ├── unit/
    └── integration/
```

## Layer Responsibilities

### API Layer

Location: `app/api/v1/endpoints/`

Responsibilities:

- Define HTTP routes and response codes
- Validate request and response payloads with Pydantic
- Delegate all business work to services
- Never perform ML training, feature generation, or provider access directly

### Application Service Layer

Location: `src/stockml/services/`

Responsibilities:

- Coordinate use cases such as prediction requests and stock data retrieval
- Compose infrastructure dependencies with ML modules
- Translate domain and infrastructure failures into application-level exceptions

### Domain Layer

Location: `src/stockml/domain/`

Responsibilities:

- Hold core typed models and interfaces
- Define contracts for market data providers and prediction pipelines
- Stay independent from FastAPI, yfinance, and other framework details

### Infrastructure Layer

Location: `src/stockml/infrastructure/`

Responsibilities:

- Implement integrations with external systems
- Start with a `yfinance` provider behind a protocol so it can be replaced later
- Return normalized data structures for upstream services

### ML Layer

Location: `src/stockml/ml/`

Responsibilities:

- Manage feature engineering
- Split data into train and validation sets
- Train and score models
- Return structured prediction artifacts rather than HTML fragments

### Core Layer

Location: `src/stockml/core/`

Responsibilities:

- Centralize settings, logging, and shared exceptions
- Provide a single environment-driven configuration source
- Avoid framework-specific business logic

## Request Flow

Prediction request flow:

1. FastAPI endpoint receives a validated prediction request
2. `PredictionService` validates use-case rules and requests market data
3. `StockDataService` obtains normalized price history from a provider implementation
4. ML pipeline transforms raw history into model-ready features
5. Trainer fits the model and generates predictions
6. Service returns a typed response payload to the API layer

This keeps the web layer thin and allows the pipeline to be tested directly without HTTP.

## Data Contracts

The system will use typed models at each boundary:

- API payloads: Pydantic models in `schemas/`
- Domain records: dataclasses or immutable models in `domain/models/`
- Provider interfaces: `Protocol` definitions in `domain/protocols/`
- ML outputs: typed result objects, not loose tuples

Important rule:

- No layer should exchange anonymous tuples once scaffolding begins

## Error Handling Strategy

The backend will use explicit exception types for:

- invalid ticker or date range
- upstream market data failures
- insufficient training data
- model training failures
- internal server faults

FastAPI exception handlers will convert these into consistent JSON error responses.

## Type Safety Strategy

- Use Python type hints on all public functions
- Use Pydantic for request and response validation
- Use `Protocol` interfaces for replaceable dependencies
- Avoid returning `Any` from service and ML boundaries

## Scalability Decisions

- Use a package-based modular layout instead of a monolithic script
- Keep providers swappable so yfinance can later be replaced by a paid market-data source
- Separate feature engineering from model training so the pipeline can evolve independently
- Keep the API contract JSON-first; visualization rendering can be added as a separate concern later

## Testing Strategy

Unit tests will cover:

- feature engineering behavior
- service orchestration
- request validation
- exception mapping

Integration tests will cover:

- FastAPI health endpoint
- prediction endpoint with mocked provider dependencies

## Phase Boundaries

This document defines the implementation order:

1. Backend architecture
2. Project scaffolding
3. Dependency setup
4. Environment configuration
5. FastAPI server
6. ML pipeline foundation
7. Stock data service
8. Feature engineering module

Each subsequent phase must conform to the package layout and layer boundaries defined here.
