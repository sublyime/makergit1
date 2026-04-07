# MakerGit Backend

A starter FastAPI backend scaffold for MakerGit.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
uvicorn src.app:app --reload
```

## Endpoints

- `GET /` — health check
- `POST /auth/register` — register a new user
- `POST /auth/login` — login and receive an API key
- `GET /auth/me` — get current authenticated user
- `GET /projects` — list public projects
- `POST /projects` — create a project (requires `Authorization: Bearer <api_key>`)
- `GET /projects/{project_id}` — get a project by ID
- `PUT /projects/{project_id}` — update a project (requires owner auth)
- `DELETE /projects/{project_id}` — delete a project (requires owner auth)

## Notes

- Authentication is currently API-key based for fast prototyping.
- The database schema uses `users`, `projects`, `tags`, and project tag relations.
- The backend is wired to PostgreSQL using `asyncpg` connection pooling.

## Next steps

- add production-grade auth and session handling
- wire more schema tables such as `project_metadata`, `components`, and `attachments`
- add pagination, search, and project revisions
