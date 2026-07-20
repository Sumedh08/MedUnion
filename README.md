# MedUnion 🏥

**Unified Healthcare Intelligence Platform**

A production-grade platform that ingests real data from public **FHIR** (HAPI R5) and **DHIS2** (Sierra Leone) servers into a canonical PostgreSQL database, powering hospital operations, community health dashboards, AI analytics, and a knowledge graph.

![Dashboard](docs/images/dashboard.png)

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐
│  HAPI FHIR  │───▶│   ETL        │───▶│  PostgreSQL    │
│  (R5)       │    │   Pipeline   │    │  (Canonical)   │
├─────────────┤    │              │    ├────────────────┤
│  DHIS2      │───▶│  Extract →   │───▶│  Hospital      │
│  (2.40)     │    │  Map →       │    │  + Community   │
├─────────────┤    │  Validate →  │    │  Tables        │
│  Seed SQL   │───▶│  Load        │    └────────────────┘
└─────────────┘    └──────────────┘           │
                                              ▼
                                      ┌────────────────┐
                                      │  FastAPI        │
                                      │  (REST + AI)    │
                                      ├────────────────┤
                                      │  React + Tailwind │
                                      └────────────────┘
```

## Features

- **Hospital Intelligence** — Beds, admissions, staff, equipment, medicine inventory from FHIR
- **Community Health** — Districts, facilities, indicators, vaccination programs from DHIS2
- **AI Health Copilot** — LLM-powered query interface via OpenRouter
- **Knowledge Graph** — Relationship map of all healthcare entities
- **Data Source Badge** — Dynamic 🟢/🟡/🔵 indicator per workspace based on import provenance

## Quick Start

### Prerequisites
- Docker (PostgreSQL), Node.js 18+, Python 3.10+

### Setup

```bash
# 1. Start PostgreSQL
docker compose up -d db

# 2. Backend
cd backend
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head

# 3. Import data from public FHIR + DHIS2 servers
python run_import.py

# 4. Start API
python -m uvicorn main:app --reload

# 5. Frontend (new terminal)
cd ..
npm install
npm run dev
```

### Seed Data (alternative to live import)
```bash
cd backend
python seed.py  # loads fixture SQL into canonical tables
```

## Data Sources

| Source | Type | Server | Records |
|--------|------|--------|---------|
| FHIR | Hospital | `hapi.fhir.org/baseR5` | 6,909 |
| DHIS2 | Community | `play.im.dhis2.org/stable-2-40-12` | 8,803 |

Connectors are **import-only** (one-time ETL, not runtime). After import, all queries read from PostgreSQL.

## Tech Stack
- **Frontend:** React, Vite, TailwindCSS, Leaflet Maps
- **Backend:** Python FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL 16
- **Connectors:** FHIR R5, DHIS2 2.40
- **AI:** OpenRouter / OpenAI-compatible API

## Project Structure
```
backend/
├── alembic/          # DB migrations (01 → 08)
├── connectors/       # FHIR + DHIS2 base & concrete connectors
├── core/             # Config, database, events, security
├── etl/              # Pipeline: mappers, loaders, contracts
├── fixtures/         # Seed data SQL
├── knowledge_graph/  # Entity relationship graph
├── models/           # SQLAlchemy ORM models
├── repositories/     # Data access layer
├── routers/          # FastAPI endpoints
├── schemas/          # Pydantic response models
├── services/         # Adapters, KPI engines, import manager
├── run_import.py     # One-shot FHIR + DHIS2 import
└── seed.py           # Static fixture loader
src/
├── components/       # Badge, charts, layout
├── pages/            # Hospital, community, copilot, simulation
└── services/         # API client
```

## Migrations
```bash
cd backend
alembic upgrade head     # Apply all
alembic downgrade -1     # Rollback one step
```
