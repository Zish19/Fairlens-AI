# FairLens AI – Architecture

## System Design
FairLens AI employs a strictly decoupled Client-Server architecture orchestrated within a Turborepo-based monorepo layout to foster code sharing on the frontend, while maintaining a robust, independent Python ML backend.

### Folder Structure
```
fairlens-ai/
├── apps/
│   ├── web/              # React (Vite, TS)
│   └── api/              # FastAPI
├── packages/
│   ├── ui/               # Shared shadcn/ui components
│   ├── config/           # Linting, formatting configs
│   ├── shared-types/     # TS Types & Zod Schemas
│   └── api-client/       # Axios/Fetch clients generated from OpenAPI
├── services/
│   └── ml-engine/        # Fairlearn, SHAP, training logic (consumed by API)
├── docs/                 # Documentation & ADRs
├── docker/
├── scripts/
├── .github/
└── docker-compose.yml
```

## Data Flow
1. **User Interaction:** The React client (Zustand + TanStack Query) sends a request.
2. **API Layer:** FastAPI validates incoming requests (Pydantic v2) and routes them to appropriate services.
3. **Async Jobs:** Heavy tasks (Training, SHAP) push a job to a background queue. The API immediately returns a Job ID.
4. **ML Engine:** The `ml-engine` is imported as a standard Python module by the API worker processes, simplifying deployment while maintaining logical separation.
5. **Data Persistence:** Relational data is stored in PostgreSQL (dev: SQLite) via SQLAlchemy 2.x. Files/Datasets are stored in an Object Storage bucket (dev: local FS, prod: S3/MinIO).
6. **Delivery:** Clients poll or use WebSockets for job completion, then render the Recharts visualization.

## Module Responsibilities
- `apps/web`: Pure UI rendering, global state, form validation.
- `apps/api`: Request routing, database I/O, authentication integration, background task delegation.
- `services/ml-engine`: Algorithmic execution (fairness metrics, model training, SHAP explanations). Fully decoupled logically, but executed within the same container runtime.
