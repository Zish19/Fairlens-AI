# 2. Treat ML Engine as a Python Package instead of an independent Microservice

Date: 2026-07-20

## Status
Accepted

## Context
Initially, the `ml-engine` was planned to run as an independent microservice over HTTP. However, managing two separate Python runtimes and orchestrating HTTP calls for data science tasks introduces significant networking and deployment complexity without immediate benefits.

## Decision
We will treat `services/ml-engine` as a logically isolated Python package that is imported directly by `apps/api`. It will run within the same container and execution environment as the FastAPI application (or its async workers).

## Alternatives Considered
- **Independent Microservice:** Allows independent scaling and remote execution (e.g., GPU nodes), but adds severe overhead for the MVP. We will pivot to this only if required later.

## Consequences
- Simpler `docker-compose.yml` (only `api` and `web` services).
- Easier local testing and debugging.
- We must ensure heavy ML tasks are offloaded to background threads (FastAPI `BackgroundTasks` or Celery) so they don't block the API event loop.
