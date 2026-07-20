# FairLens AI

![FairLens AI Architecture](/architecture_diagram.png)

Production-ready AI Fairness & Explainability Platform.

## Features

- **Fairness Analysis**: Automatically compute disparate impact, demographic parity, equal opportunity, and more using Fairlearn.
- **Explainability**: Understand model predictions using global and local feature importance via SHAP.
- **AI Insights**: Generate human-readable insights and mitigation recommendations utilizing LLM providers.
- **Background Processing**: Heavy ML computations and model explanations are offloaded to Celery workers using Redis.
- **Production-Ready**: FastAPI backend, structured JSON logging, PostgreSQL, Redis cache, JWT Auth, and Prometheus metrics.

## Tech Stack

- **Frontend**: React, Tailwind CSS, Recharts
- **Backend**: FastAPI, SQLAlchemy, Alembic, Celery, Redis
- **ML Engine**: Scikit-Learn, Fairlearn, SHAP, Pandas
- **Infrastructure**: Docker, Docker Compose, PostgreSQL

## Installation

```bash
git clone https://github.com/Zish19/Fairlens-AI.git
cd Fairlens-AI

# Create your .env file based on .env.example
cp .env.example .env
```

## Docker Setup

To start the entire stack (PostgreSQL, Redis, FastAPI, Celery, React):

```bash
docker compose build
docker compose up -d
```

The API will be available at `http://localhost:8000` and the UI at `http://localhost:5173`.

## Environment Variables

Check `.env.example` for all configurable environment variables.
- `AI_PROVIDER`: Set to `stub`, `openai`, or `gemini`.

## License
MIT License
