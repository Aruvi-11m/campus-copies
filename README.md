# Campus Copies ERP

Production-ready enterprise resource planning software designed for college printing businesses. Built with FastAPI, React 19, SQLite, and Docker.

## Features
- **Dashboard & Analytics:** Real-time metrics and KPI visualization for operations.
- **Order Management:** Track and process student print orders through a seamless pipeline.
- **Inventory System:** Manage stock thresholds and alerts for paper, ink, and binding materials.
- **Finance Module:** Full expense tracking, revenue forecasting, and reporting capabilities.
- **Settings & Audit:** Extensive configuration and full security audit logging.

## Tech Stack
- **Backend:** Python 3.9+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, TanStack Query/Table, Shadcn UI
- **Infrastructure:** Docker, Nginx, Prometheus

## Local Development Setup

### 1. Clone the repository
```bash
git clone <repo-url>
cd campus-copies-erp
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

## Production Deployment

The platform is designed to be easily deployed via Docker Compose.

### 1. Preparation
Ensure you have Docker and Docker Compose installed on your host server. Update the `.env` variables located in `backend/.env` with your secure production values (e.g., strong `SECRET_KEY`, specific `CORS_ORIGINS`).

### 2. Launch
Run the following from the repository root:
```bash
docker-compose up --build -d
```

### 3. Verification
- The Web App is served at `http://<your-server-ip>/`
- The API is served at `http://<your-server-ip>/api/`
- Prometheus metrics are available at `http://<your-server-ip>:9090`

## Architecture & Documentation
Comprehensive architectural documentation is available in the `/docs` directory.

- `docs/Frontend.md`: Details about UI structure, states, and hooks.
- `docs/Backend.md`: Detailed service layers, repositories, and ORM setups.
- `docs/Deployment.md`: Advanced infrastructure configuration (CI/CD, Monitoring).
