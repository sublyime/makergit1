# MakerGit Architecture

MakerGit begins as a two-part application:

- `backend/` — API service for maker projects, users, and metadata
- `frontend/` — lightweight web UI for browsing and discovering projects
- `db/` — PostgreSQL schema for all project and collaboration data

Key components:

- `backend/src/app.py` — FastAPI application entrypoint
- `backend/src/routers/` — API route definitions
- `backend/src/models.py` — Pydantic schemas for API payloads
- `backend/src/database.py` — database connection helper
- `frontend/` — static HTML/CSS/JS project preview UI
- `db/schema.sql` — PostgreSQL schema for users, projects, revisions, attachments, tags, and comments
