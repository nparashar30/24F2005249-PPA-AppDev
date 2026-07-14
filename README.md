# Placement Portal Application (PPA) V2

A full-stack campus recruitment management system built for **Modern Application Development II (MAD-II)**.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend API | Flask |
| Frontend UI | Vue.js 3 (CDN) |
| Styling | Bootstrap 5 |
| Database | SQLite (programmatic creation) |
| Caching | Redis |
| Background Jobs | Celery + Redis |

## Roles

- **Admin** – Institute placement cell (pre-created, no registration)
- **Company** – Register, create drives after admin approval
- **Student** – Self-register, apply to drives, track applications

## Project Structure

```
├── app.py                  # Flask application entry point
├── config.py               # Configuration
├── celery_worker.py        # Celery worker entry
├── init_db.py              # Database initialization + admin seed
├── models/                 # SQLAlchemy models
├── routes/                 # API blueprints (auth, admin, company, student)
├── tasks/                  # Celery background tasks
├── utils/                  # Cache, validators, helpers
├── templates/index.html    # Jinja2 entry point (Vue mount)
├── static/js/              # Vue components & app
├── static/css/             # Custom styles
└── requirements.txt
```

## Setup (Local)

### 1. Prerequisites

- Python 3.10+
- Redis server running on `localhost:6379`

### 2. Install dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Environment variables

Copy `.env.example` to `.env` and adjust if needed.

### 4. Initialize database

```bash
python init_db.py
```

This creates all tables and seeds the default admin user.

### 5. Run the application

```bash
# Terminal 1 – Flask
python app.py

# Terminal 2 – Celery worker
celery -A celery_worker.celery worker --loglevel=info --pool=solo

# Terminal 3 – Celery Beat (scheduled jobs)
celery -A celery_worker.celery beat --loglevel=info
```

Open **http://localhost:5000** in your browser.

## Default Admin Credentials

| Field | Value |
|-------|-------|
| Email | admin@institute.edu |
| Password | admin123 |

## API Overview

| Prefix | Description |
|--------|-------------|
| `/api/auth` | Login, register (student/company) |
| `/api/admin` | Dashboard, approvals, search, blacklist |
| `/api/company` | Profile, drives, applications |
| `/api/student` | Profile, drives, apply, history, export |

## Background Jobs

1. **Daily Reminders** – Application deadline alerts (email/GChat webhook)
2. **Monthly Report** – HTML placement activity report to admin (1st of month)
3. **CSV Export** – Async export of student application history

## Milestones

- [x] Milestone 0 – GitHub setup
- [x] Database models & schema
- [x] Authentication & RBAC
- [x] Admin dashboard
- [x] Company dashboard
- [x] Student dashboard
- [x] Application history & status tracking
- [x] Celery backend jobs
- [x] Redis caching

## Issues & Resolutions

Log project issues in GitHub Issues as they arise during development.
