# AapadaOps (ଆପଦାଅପ୍ସ) — Odisha Disaster-Response Platform

[![Architecture: C4 Verified](https://img.shields.io/badge/Architecture-C4%20Model-15803d.svg)](#)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-15803d.svg)](#)
[![FastAPI: 0.111+](https://img.shields.io/badge/FastAPI-0.111+-15803d.svg)](#)
[![React: 18.3+](https://img.shields.io/badge/React-18.3+-15803d.svg)](#)
[![Design: Gov Operations](https://img.shields.io/badge/Design-Government%20Operations-0f172a.svg)](#)

A complete AI-powered disaster-response coordination platform engineered for the **Odisha State Disaster Management Authority (OSDMA)** and **Special Relief Commissioner (SRC)**. AapadaOps coordinates multi-hazard disaster preparedness, real-time rescue dispatch, cyclone shelter tracking, and post-disaster recovery across all 30 districts of Odisha.

---

## Key Capabilities

1. **State & District Emergency Operations Center (EOC) Dashboard**: High-density operational cockpit for real-time situational awareness.
2. **Interactive PostGIS Disaster Map**: Real-time layers for Cyclone wind fields, Flood inundation zones (Mahanadi, Brahmani, Baitarani), and 800+ Multi-Purpose Cyclone Shelters (MCS).
3. **Citizen SOS & Incident Intake**: Multi-channel reporting with automated spatial deduplication and bilingual (Odia + English) severity classification.
4. **Relief Camp & Shelter Logistics**: Live occupancy, potable water supply, DG set fuel, rations, and vulnerable population tracking.
5. **Tactical Resource & Force Mobilization**: Pre-positioning and dispatch of ODRAF, NDRF 03 Battalion, and Fire & Emergency Services rescue boats, pumps, and chainsaws.
6. **AI/ML Predictive Risk Models**: Inundation depth forecasts, housing vulnerability indices, and relief demand projections.
7. **Common Alerting Protocol (CAP) Broadcast**: Multi-channel early warnings categorized into Green, Yellow, Orange, and Red tiers.

---

## Design Principles

- **Professional Government Operations**: Natural colors, warm neutral slate canvas, restrained governance green accents, clear typography, practical tables, subtle borders, and accessible layouts.
- **Zero Gimmicks**: Strictly NO purple gradients, NO neon effects, NO glowing cards, NO glassmorphism, and NO generic AI illustrations.
- **Genuine Functionality**: Every major interface connects to real backend APIs and persistent storage.

---

## Directory Structure

```
PROTOTYPE PROJECT/
├── .env.example              # Environment variables template
├── .gitignore                # Source control exclusions
├── README.md                 # Project root documentation
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/v1/           # Modular REST API endpoints
│   │   ├── core/             # Configuration, security, database engine
│   │   ├── models/           # SQLAlchemy / GeoAlchemy2 entities
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Business logic & geospatial services
│   │   ├── ml/               # AI risk modeling & triage logic
│   │   └── main.py           # FastAPI entrypoint
│   ├── tests/                # Automated pytest suite
│   ├── requirements.txt      # Production Python dependencies
│   └── requirements-dev.txt  # Development & testing dependencies
├── frontend/                 # React + TypeScript + Vite + Tailwind CSS
│   ├── public/               # Public assets
│   ├── src/
│   │   ├── components/       # Reusable government design components
│   │   ├── pages/            # Operational consoles & dashboards
│   │   ├── services/         # API client & query definitions
│   │   ├── types/            # TypeScript contracts
│   │   └── index.css         # Tailwind & base styling
│   ├── package.json          # Node dependencies
│   ├── tailwind.config.js    # Design system palette & tokens
│   ├── tsconfig.json         # TypeScript compiler config
│   └── vite.config.ts        # Vite bundler config
└── docs/                     # Comprehensive Architecture & Domain Docs
    ├── ARCHITECTURE.md       # Full C4 architecture & module breakdown
    ├── DESIGN_SYSTEM.md      # UI design tokens & accessibility criteria
    ├── DISASTER_MANAGEMENT_ODISHA_CONTEXT.md # OSDMA operational handbook
    └── API_SPECIFICATION.md  # REST API endpoint reference
```

---

## Quickstart

### Backend Setup
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# Copy environment configuration
cp .env.example .env

# Run FastAPI development server
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## Security & Compliance
- **Zero Hardcoded Secrets**: All credentials loaded strictly via environment variables.
- **Role-Based Access Control**: Strict access boundaries across SuperAdmin, State EOC, District Collector, Block Officer, and Field Responder roles.
- **Audit Logging**: Every operational dispatch, status change, and resource movement is recorded with immutable timestamps and operator identity.
