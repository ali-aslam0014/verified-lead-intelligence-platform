# Verified Lead Intelligence Platform

Production-grade SaaS application designed to discover businesses for any niche and geography, resolve duplicate business records, verify business identity and contact data, classify website/social presence, audit websites & SEO, detect evidence-backed sales opportunities, score leads, send uncertain records to human review, and export outreach-ready leads.

## Core Principle
**TRUSTED, ACTIONABLE LEADS** — not maximum scraped volume.
The system never presents discovered information as verified without passing configured verification rules.

---

## Architecture Overview

**Modular Monolith Architecture**:
- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS, TanStack Query, React Hook Form, Zod
- **Backend API**: FastAPI (Python 3.11+), Pydantic v2, SQLAlchemy 2.0 (Async Engine), `asyncpg`
- **Database**: PostgreSQL 16
- **Cache / Task Broker**: Redis 7
- **Background Worker**: Celery
- **Containerization**: Docker & Docker Compose

---

## Infrastructure / System Components

1. **Backend API**: Serves RESTful endpoints, handles security, request ID propagation, and exposes structured health metrics.
2. **PostgreSQL Database**: Stores targets, business entities, source records, verifications, audits, opportunities, and lead scores.
3. **Redis & Celery Queue**: Asynchronous processing pipeline for discovery, entity resolution, website/social verification, auditing, and opportunity scoring.

---

## Getting Started

### Prerequisites
- Docker Engine & Docker Compose
- Node.js 18+ (for local frontend development outside Docker)
- Python 3.11+ (for local backend development outside Docker)

### Environment Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Running with Docker Compose
To launch all infrastructure components and services:
```bash
docker-compose up -d --build
```

Access services:
- **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
- **Backend Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Liveness**: [http://localhost:8000/healthz](http://localhost:8000/healthz)
- **System Components Health**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## Testing

### Backend Integration Tests
```bash
cd backend
pytest
```
Or inside Docker:
```bash
docker exec -it lead_intel_backend pytest
```
