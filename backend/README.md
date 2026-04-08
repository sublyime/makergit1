# MakerGit Backend API

FastAPI backend for MakerGit IoT collaboration platform. Provides REST API for user authentication, project management, device registration, and bill of materials.

## Features

✨ **Authentication** — API key-based authentication for fast prototyping
🏗️ **Project Management** — Create, read, update, delete projects
🔌 **Device Registration** — Register and track IoT devices
📋 **Bill of Materials** — Create and manage component BOMs
🔍 **Library Search** — Search 2,800+ Arduino boards and components with autocomplete
🗄️ **PostgreSQL** — Reliable data storage with asyncpg connection pooling

## Setup

### 1. Create Virtual Environment

```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Requirements includes:**
- FastAPI — Modern web framework
- Uvicorn — ASGI server
- asyncpg — PostgreSQL async driver
- Pydantic — Data validation
- Passlib — Password hashing

### 3. Configure Database

Set environment variable (optional, defaults to localhost):

```powershell
$env:DATABASE_URL = "postgresql://postgres:PASSWORD@localhost:5432/makergit"
```

Or use default:
```
postgresql://postgres@localhost:5432/makergit
```

### 4. Run Development Server

```bash
uvicorn src.app:app --reload
```

Server starts at `http://localhost:8000`

API docs available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

```
POST /auth/register
  Input: {username, email, password, display_name}
  Returns: {id, username, email, display_name, api_key, ...}

POST /auth/login
  Input: {username, password}
  Returns: {api_key}

GET /auth/me
  Headers: Authorization: Bearer <api_key>
  Returns: {id, username, email, display_name, ...}
```

### Projects

```
GET /projects/
  Returns: [Project]

POST /projects/
  Headers: Authorization: Bearer <api_key>
  Input: {title, summary, description, visibility, status, tags}
  Returns: Project

GET /projects/{project_id}
  Returns: Project

PUT /projects/{project_id}
  Headers: Authorization: Bearer <api_key>
  Input: {title, summary, description, visibility, status, tags}
  Returns: Project

DELETE /projects/{project_id}
  Headers: Authorization: Bearer <api_key>
  Returns: {success}
```

### Devices

```
GET /api/devices/devices
  Query: project_id
  Returns: [Device]

POST /api/devices/devices
  Headers: Authorization: Bearer <api_key>
  Input: {project_id, name, device_type, unique_id, config, metadata}
  Returns: Device

GET /api/devices/devices/{device_id}
  Returns: Device

PUT /api/devices/devices/{device_id}
  Headers: Authorization: Bearer <api_key>
  Input: {name, status, firmware_version, config, ip_address}
  Returns: Device
```

### Bill of Materials

```
GET /api/boms/
  Query: project_id
  Returns: [BOM]

POST /api/boms/
  Headers: Authorization: Bearer <api_key>
  Input: {project_id, name, description, device_id, version}
  Returns: BOM

GET /api/boms/{bom_id}
  Returns: BOM

POST /api/boms/{bom_id}/items
  Headers: Authorization: Bearer <api_key>
  Input: {reference, description, quantity, part_number, manufacturer, unit_price, ...}
  Returns: BOMItem

PUT /api/boms/bom-items/{item_id}
  Headers: Authorization: Bearer <api_key>
  Input: {reference, description, quantity, unit_price, ...}
  Returns: BOMItem

DELETE /api/boms/bom-items/{item_id}
  Headers: Authorization: Bearer <api_key>
  Returns: {success}
```

### Library Search (NEW)

```
GET /api/library/library/devices/search?q=<query>&limit=10
  Returns: [DeviceLibraryAutocomplete]

GET /api/library/library/devices/category/{category}
  Returns: [DeviceLibraryAutocomplete]

GET /api/library/library/devices/{device_id}
  Returns: DeviceLibraryRead (full details)

GET /api/library/library/components/search?q=<query>&limit=10
  Returns: [ComponentLibraryAutocomplete]

GET /api/library/library/components/category/{category}
  Returns: [ComponentLibraryAutocomplete]

GET /api/library/library/components/{component_id}
  Returns: ComponentLibraryAutocomplete

GET /api/library/library/stats
  Returns: {device_library: {total, top_categories}, component_library: {...}}

GET /api/library/devices/search?project_id=<id>&q=<query>
  Headers: Authorization: Bearer <api_key>
  Returns: [DeviceAutocomplete]

GET /api/library/projects/search?q=<query>
  Headers: Authorization: Bearer <api_key>
  Returns: [ProjectAutocomplete]
```

**See [../LIBRARY_SETUP.md](../LIBRARY_SETUP.md) for detailed library API documentation**

## Project Structure

```
src/
├── app.py              # FastAPI app, routers, CORS setup
├── database.py         # PostgreSQL connection pool
├── models.py           # Pydantic request/response models
├── utils.py            # Helpers (password hashing, JWT, auth)
└── routers/
    ├── auth.py         # Authentication endpoints
    ├── projects.py     # Project CRUD
    ├── devices.py      # Device management
    ├── boms.py         # Bill of Materials
    └── library.py      # Library search endpoints (NEW)

requirements.txt       # Python package dependencies
README.md             # This file
```

## Data Models

See [../docs/data-model.md](../docs/data-model.md) for complete database schema.

Key Pydantic models:
- **UserRead** — User account info
- **ProjectRead** — Project metadata
- **DeviceRead** — Device details
- **BOMRead** — Bill of Materials
- **BOMItemRead** — Component in BOM
- **DeviceLibraryRead** — Device library entry (2,800+ boards)
- **ComponentLibraryAutocomplete** — Component search result
- **DeviceLibraryAutocomplete** — Device search result

## Authentication

Current implementation uses **API Key authentication** for fast prototyping.

To authenticate:
1. Register: `POST /auth/register`
2. Get API key from response
3. Send key in requests: `Authorization: Bearer <api_key>`

Example:
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user@example.com","password":"pass123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123"}'

# Use API key
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Performance

- **Database**: Connection pooling (up to 20 concurrent connections)
- **Search**: Full-text indexes for <100ms device library queries
- **Caching**: Query result caching via HTTP headers
- **Pagination**: Limit autocomplete results (default 10, max 50)

## Development

### Add New Endpoint

1. Create router in `routers/` folder
2. Define Pydantic models in `models.py`
3. Import router in `app.py`
4. Include router: `app.include_router(router, prefix="/api/...", tags=["..."])`

### Database Queries

Use asyncpg directly in router functions:

```python
@router.get("/example/{id}")
async def get_example(id: str, request: Request):
    pool = get_pool(request.app)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM table WHERE id = $1", id)
        return row
```

### Add Database Migration

1. Create SQL file in `db/`
2. Test locally: `psql -d makergit -f new_migration.sql`
3. Document in migration.sql

## Testing

Tests coming soon. Will include:
- Unit tests for models and validation
- Integration tests for API endpoints
- Database transaction rollback for test isolation

## Troubleshooting

### Port Already in Use
```bash
# Change port
uvicorn src.app:app --port 8001 --reload
```

### Database Connection Error
```bash
# Test connection
psql "postgresql://postgres:PASSWORD@localhost:5432/makergit"

# Check PostgreSQL is running
# Windows: Services → PostgreSQL
# macOS: brew services start postgresql
```

### Module Not Found
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

## Next Steps

- [ ] Add production authentication (OAuth2, JWT tokens)
- [ ] Add pagination and advanced search
- [ ] Add data validation and error handling
- [ ] Add request logging and monitoring
- [ ] Add integration tests
- [ ] Add API rate limiting
- [ ] Add webhook support for device events
- [ ] Add component library management endpoints

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **asyncpg Docs**: https://magicstack.github.io/asyncpg/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

See [../QUICK_REFERENCE.md](../QUICK_REFERENCE.md) for quick setup guide.
