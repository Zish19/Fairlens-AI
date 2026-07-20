# 1. Use FastAPI and Turborepo Monorepo

Date: 2026-07-20

## Status
Accepted

## Context
We need to build a complex, enterprise-grade web application (React frontend, Python machine learning backend). We want strict typing, shared configurations (ESLint/Prettier), and robust UI components on the frontend, while simultaneously needing powerful data science libraries (scikit-learn, Fairlearn) on the backend.

## Decision
We will use a **Turborepo Monorepo** structure for the project. The frontend and Node.js-based tooling will live in `apps/web` and `packages/` to take advantage of Turborepo's build caching and dependency management. 
The backend will use **FastAPI** and live in `apps/api`, while the heavy machine learning code will live in `services/ml-engine`. Python dependencies will be managed via `uv` or `Poetry`, completely independent of Turborepo's orchestration.

## Alternatives Considered
- **Two separate repositories:** Harder to keep API contracts in sync and increases CI/CD complexity.
- **Django/Flask:** FastAPI offers native async support, better typing with Pydantic v2, and automatic OpenAPI documentation, which is crucial for generating the `api-client` package.
- **Full Node.js Backend:** Node.js lacks the mature data science and ML ecosystem required for Bias Detection (scikit-learn, Fairlearn, SHAP).

## Consequences
- Better code sharing for frontend logic.
- Clear separation between the HTTP API (FastAPI) and the Core ML Logic (ml-engine).
- Requires developers to understand both NPM/Node tools (Turborepo) and Python tooling.
