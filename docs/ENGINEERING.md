# FairLens AI – Engineering Standards & Architecture

## Technology Stack & Versions
- **Node.js:** 22 LTS | **React:** 19 | **Vite:** 7 | **TypeScript:** 5.8+ | **Tailwind CSS:** 4 | **shadcn/ui:** latest
- **Python:** 3.12 | **FastAPI:** latest stable | **Pydantic:** v2 | **SQLAlchemy:** 2.x | **Alembic:** latest
- **TanStack Query:** 5 | **React Hook Form:** 7 | **Zod:** 4 | **Docker Compose:** v2 | **pytest / Vitest:** latest

## State Management & Design System
- **State:** TanStack Query (Server), Zustand (Global UI), React Hook Form / Zod (Forms/Validation). *Never store server data in Zustand.*
- **Tokens:** Border Radius 12px, Spacing 4/8/12/16/24/32, Animation 200–300ms, Inter font, Lucide icons, Recharts, TanStack Table.

## API Standards
### Versioning & Contracts
- All endpoints must be versioned (e.g., `/api/v1/upload`).
- **Success:** `{ "success": true, "data": {}, "meta": {} }`
- **Error:** `{ "success": false, "error": { "code": "...", "message": "...", "details": [] } }`

### Asynchronous Processing & Object Storage
- Heavy operations (model training, SHAP, fairness) must use a background job workflow: 
  `POST /api/v1/analysis` -> `Return Job ID` -> `Background Worker` -> `Polling/WebSocket` -> `Completed Analysis`
- **Datasets:** Store only metadata in the DB. Use Local filesystem for dev, S3/MinIO for prod.

### Database Schema Expectations
Core Entities: `Users`, `Datasets`, `DatasetVersions`, `Analyses`, `Models`, `TrainingRuns`, `Reports`, `AuditLogs`.

## Observability & Security
- **Observability:** OpenTelemetry, Prometheus metrics, Grafana dashboards, Structured JSON logging.
- **Security:** OWASP Top 10, CSP, Secure cookies, CORS, File upload sanitization, Rate limiting, Envs for secrets, Vuln scanning.

## Performance Targets
- Dashboard Initial load: < 2s 
- Dataset upload (100MB): < 5s CSV parsing
- API latency: < 300ms 
- Bias calc: < 10s 
- Lighthouse: > 90
