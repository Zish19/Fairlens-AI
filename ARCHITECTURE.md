# Architecture Overview

```mermaid
graph TD
    UI[Frontend Dashboard] --> API[FastAPI Backend]
    API --> DB[(PostgreSQL)]
    API --> Redis[(Redis Cache & Queue Broker)]
    Redis --> Celery[Celery Workers]
    Celery --> DB
    
    Prometheus[Prometheus Instrumentator] -.-> API
    Structlog[JSON Structured Logs] -.-> API
    Structlog -.-> Celery
```

## Layers
* **Presentation**: React (Vite, Tailwind).
* **API**: FastAPI orchestrating requests and authentication.
* **Business Logic**: Core services isolated from infrastructure.
* **Background Execution**: JobQueue abstraction utilizing Celery for execution and Redis as message broker.
* **ML Processing**: Fairlearn, SHAP, and AI abstractions isolated in `services/ml_engine`.
* **Infrastructure**: PostgreSQL, Redis, structured logging.
