# MakerGit Postgres Setup

This repository contains the PostgreSQL schema for the MakerGit MVP.

## Database settings

- Database: `makergit`
- User: `postgres`
- Password: `NatEvan12!!`
- Host: `localhost`
- Port: `5432`

## Local PostgreSQL setup

Install PostgreSQL locally and start the service on `localhost:5432`.

If you installed PostgreSQL using the Windows installer, make sure the `bin` folder with `psql` and `createdb` is on your `PATH`.

Create the database and apply the schema using `psql`:

```sh
createdb -U postgres makergit
psql -U postgres -d makergit -f db/schema.sql
```

Then connect with:

```sh
psql "postgresql://postgres:NatEvan12!!@localhost:5432/makergit"
```

If you already created the database, you can skip `createdb`.

## Automated setup scripts

You can also run the provided scripts to initialize the database and apply the schema:

- Windows PowerShell: `./setup.ps1`
- Unix/macOS shell: `./setup.sh`

These scripts will:
- Create the database if it doesn't exist and apply the full schema
- Apply migrations if the database already exists (adding new columns gracefully)

Make sure `psql` and `createdb` are installed and available on your `PATH`.

## Manual database migration

If you prefer to run migrations manually on an existing database:

```sh
psql "postgresql://postgres:NatEvan12!!@localhost:5432/makergit" -f db/migration.sql
```

This will add the new columns gracefully without affecting existing data.


## Repository structure

- `backend/` — API scaffold and backend startup files
- `frontend/` — static UI prototype for project discovery
- `db/` — PostgreSQL schema definition
- `docs/` — architecture and data-model documentation
- `setup.ps1` / `setup.sh` — local DB init helpers
- `.gitignore` — ignore patterns for Python and frontend artifacts

## Schema file

- `db/schema.sql` contains the core data model for users, projects, revisions, BOMs, attachments, build logs, tags, comments, and IoT metadata.
- `db/migration.sql` contains incremental database updates for existing installations.

## Next step

Use this schema as the foundation for your backend layer. If you want, I can also add:

- Node.js / TypeScript ORM models
- FastAPI / Django models
- project seed data or migrations
