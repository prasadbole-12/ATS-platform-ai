# AI-Powered ATS Candidate Ranking Platform

A production-grade Applicant Tracking System with AI-powered resume parsing and candidate ranking.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Tailwind CSS, React Query |
| Backend | FastAPI, Python 3.11, SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL 15 |
| Deployment | Docker, Docker Compose |

---

## Option A — Run with Docker Compose (recommended)

```bash
# 1. Clone and enter project
cd ats-platform

# 2. Copy environment file
cp .env.example .env

# 3. Start all services (postgres + backend + frontend)
docker compose up --build

# 4. Apply database migrations (in a new terminal)
docker compose exec backend alembic upgrade head

# 5. Seed mock data
curl -X POST http://localhost:8000/api/v1/seed
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/api/docs |
| Health Check | http://localhost:8000/health |

---

## Option B — Run locally without Docker

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15 running locally

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp ../.env.example ../.env
# Edit DATABASE_URL in .env to match your local PostgreSQL

# Run database migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment
cp .env.local.example .env.local
# Edit VITE_API_BASE_URL if backend runs on different port

# Start frontend
npm run dev
```

---

## Database Migration Commands

```bash
# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base

# Generate new migration (after model changes)
alembic revision --autogenerate -m "describe your change"

# View migration history
alembic history
```

---

## Seed Mock Data

```bash
# Via curl
curl -X POST http://localhost:8000/api/v1/seed

# Via API docs
# Open http://localhost:8000/api/docs
# Find POST /api/v1/seed and click "Try it out"

# Via frontend
# Open Settings page → click "Seed Mock Data"
# Or on Dashboard → click "⚡ Seed Mock Data"
```

This seeds:
- 8 realistic candidates with skills
- 2 job descriptions
- 7 mock rankings with ATS scores

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/upload-resume | Upload PDF/DOCX resume |
| GET | /api/v1/candidates | List candidates (paginated, searchable) |
| GET | /api/v1/candidates/{id} | Get single candidate |
| PATCH | /api/v1/candidates/{id} | Update candidate |
| DELETE | /api/v1/candidates/{id} | Delete candidate |
| POST | /api/v1/job-description | Create job description |
| GET | /api/v1/job-descriptions | List all JDs |
| GET | /api/v1/job-descriptions/{id} | Get single JD |
| PATCH | /api/v1/job-descriptions/{id} | Update JD |
| DELETE | /api/v1/job-descriptions/{id} | Delete JD |
| GET | /api/v1/rankings | All rankings (enriched) |
| GET | /api/v1/rankings/job/{id} | Rankings for specific job |
| GET | /api/v1/dashboard/stats | Dashboard KPIs |
| POST | /api/v1/seed | Seed mock data (dev only) |
| GET | /health | Health check |
| GET | /api/docs | Swagger UI |

---

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://ats_user:ats_password@localhost:5432/ats_db
SECRET_KEY=your-secret-key
ENVIRONMENT=development
DEBUG=true
ALLOWED_ORIGINS=http://localhost:5173
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=10
```

### Frontend (.env.local)
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## Testing Instructions

### 1. Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","app":"ATS Platform",...}
```

### 2. Seed Data
```bash
curl -X POST http://localhost:8000/api/v1/seed
```

### 3. List Candidates
```bash
curl http://localhost:8000/api/v1/candidates
```

### 4. Upload a Resume
```bash
curl -X POST http://localhost:8000/api/v1/upload-resume \
  -F "file=@/path/to/resume.pdf"
```

### 5. Get Rankings
```bash
curl http://localhost:8000/api/v1/rankings
```

### 6. Dashboard Stats
```bash
curl http://localhost:8000/api/v1/dashboard/stats
```

---

## Project Structure

```
ats-platform/
├── docker-compose.yml
├── .env
├── .env.example
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 001_initial.py
│   └── app/
│       ├── main.py
│       ├── api/v1/
│       │   ├── router.py
│       │   └── endpoints/
│       │       ├── resumes.py
│       │       ├── candidates.py
│       │       ├── job_descriptions.py
│       │       └── rankings.py
│       ├── core/
│       │   ├── config.py
│       │   └── logging.py
│       ├── database/
│       │   └── session.py
│       ├── models/
│       │   ├── candidate.py
│       │   ├── job_description.py
│       │   └── ranking.py
│       ├── schemas/
│       │   ├── candidate.py
│       │   ├── job_description.py
│       │   └── ranking.py
│       └── services/
│           ├── candidate_service.py
│           ├── job_description_service.py
│           └── ranking_service.py
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.ts
    ├── tsconfig.json
    └── src/
        ├── App.tsx
        ├── main.tsx
        ├── index.css
        ├── types/index.ts
        ├── lib/utils.ts
        ├── services/
        │   ├── api.ts
        │   ├── candidateService.ts
        │   ├── jobDescriptionService.ts
        │   └── rankingService.ts
        ├── hooks/queries.ts
        ├── components/
        │   ├── layout/
        │   │   ├── Layout.tsx
        │   │   ├── Sidebar.tsx
        │   │   └── Navbar.tsx
        │   ├── ui/
        │   │   ├── button.tsx
        │   │   ├── card.tsx
        │   │   ├── badge.tsx
        │   │   ├── input.tsx
        │   │   ├── textarea.tsx
        │   │   ├── label.tsx
        │   │   ├── select.tsx
        │   │   ├── dialog.tsx
        │   │   ├── progress.tsx
        │   │   └── skeleton.tsx
        │   └── shared/
        │       ├── StatsCard.tsx
        │       ├── StatusBadge.tsx
        │       ├── ScoreRing.tsx
        │       ├── CandidateDrawer.tsx
        │       ├── EmptyState.tsx
        │       └── ErrorState.tsx
        └── pages/
            ├── DashboardPage.tsx
            ├── UploadResumePage.tsx
            ├── CandidatesPage.tsx
            ├── JobDescriptionsPage.tsx
            ├── RankingsPage.tsx
            └── SettingsPage.tsx
```

---

## Git Commit Message

```
feat: complete Day 1 full-stack foundation

- FastAPI backend with clean architecture (models/schemas/services/endpoints)
- PostgreSQL schema with Alembic migrations (candidates, job_descriptions, rankings)
- React 18 + TypeScript + Tailwind frontend with 6 pages
- React Query data fetching with full CRUD operations
- Resume upload with drag-and-drop UI
- Candidate management table with search, filter, and drawer
- Job description CRUD with modal form
- Rankings leaderboard with expandable score breakdown
- Dashboard with Recharts bar + pie charts and KPI cards
- Docker Compose for one-command local dev
- Mock data seeder for immediate testing
```
