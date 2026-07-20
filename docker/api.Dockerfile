FROM python:3.12-slim AS builder

WORKDIR /build

COPY apps/api/requirements.txt ./api-requirements.txt
COPY services/ml_engine/requirements.txt ./ml-requirements.txt

RUN pip install --no-cache-dir --prefix=/install -r api-requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r ml-requirements.txt

FROM python:3.12-slim AS runner

WORKDIR /app

# Create non-root user
RUN addgroup --system fairlens && adduser --system --group fairlens

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY apps/api ./apps/api
COPY services/ml_engine ./services/ml_engine

# Change ownership
RUN chown -R fairlens:fairlens /app
RUN mkdir -p /app/data && chown -R fairlens:fairlens /app/data

USER fairlens

ENV PYTHONPATH=/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
