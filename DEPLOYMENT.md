# Deployment Guide

## Using Docker Compose (Recommended)

1. Ensure Docker and Docker Compose are installed.
2. Configure `.env` with production secrets.
3. Run `docker compose up --build -d`

## Required Services
- PostgreSQL 15
- Redis 7
- Python 3.12 (for API and ML engine)
- Node.js 22 (for Frontend)
