# MakerGit - Maker-First IoT Collaboration Hub

A maker-first platform for collaborating on IoT, edge computing, and homelab projects. Track devices, manage BOMs, share firmware, and build together.

## Features

✨ **Device Management** — Register and track devices (Arduino, ESP32, Raspberry Pi, etc.)
📋 **Bill of Materials** — Create and manage BOMs with real-time component search
🔌 **Device Library Autocomplete** — Search 2,800+ Arduino boards and components
🔐 **API Key Authentication** — Simple, fast auth for prototyping
📚 **Project Collaboration** — Share projects, revisions, and documentation
🏗️ **PostgreSQL Backend** — Reliable, scalable data storage

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Git

### 1. Setup Database

```bash
# Create database
createdb -U postgres makergit

# Apply schema
psql -U postgres -d makergit -f db/schema.sql
```

Or use the setup script:
```bash
# Windows
./setup.ps1

# macOS/Linux
./setup.sh
```

### 2. Load Device Library

The device library (2,800+ Arduino boards) loads from `docs/library_index.json`:

```bash
# Set environment variable (optional)
$env:DATABASE_URL = "postgresql://postgres:PASSWORD@localhost:5432/makergit"

# Load device library data
python db/load_device_library.py
```

When prompted, enter your PostgreSQL credentials.

### 3. Install Backend Dependencies

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# or source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 4. Start Backend

```bash
cd backend
uvicorn src.app:app --reload
# API available at http://localhost:8000
```

### 5. Start Frontend

```bash
cd frontend
python -m http.server 8080
# UI available at http://localhost:8080
```

## Project Structure

```
makergit/
├── backend/
│   ├── src/
│   │   ├── app.py                 # FastAPI app entry point
│   │   ├── database.py            # PostgreSQL connection
│   │   ├── models.py              # Pydantic models
│   │   ├── utils.py               # Helper functions
│   │   └── routers/
│   │       ├── auth.py            # Authentication endpoints
│   │       ├── projects.py        # Project CRUD
│   │       ├── devices.py         # Device management
│   │       ├── boms.py            # Bill of Materials
│   │       └── library.py         # Library search (NEW)
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── index.html                 # Main UI
│   ├── app.js                     # Frontend logic & autocomplete (UPDATED)
│   ├── styles.css                 # UI styling
│   └── README.md
├── db/
│   ├── schema.sql                 # Database schema (UPDATED)
│   ├── migration.sql              # Database migrations
│   ├── load_device_library.py     # Library loader (NEW)
│   └── bom-migration.sql
├── docs/
│   ├── library_index.json         # Arduino library data (2,800+ boards)
│   ├── architecture.md
│   └── data-model.md              # (UPDATED)
├── README.md                      # This file
├── QUICK_REFERENCE.md             # Fast setup guide (NEW)
├── LIBRARY_SETUP.md               # Detailed library docs (NEW)
├── IMPLEMENTATION_SUMMARY.md      # Feature overview (NEW)
└── setup_library.py               # Environment check tool (NEW)
```

## Core Features

### Device Registration with Autocomplete
- Register devices to projects
- **Device Type field has autocomplete** — Type "ESP32" to see matching boards
- Auto-populate device specs from Arduino library
- Supported: Arduino, ESP32, Raspberry Pi, and 2,800+ other boards

### Bill of Materials Manager
- Create project-specific BOMs
- Add components with **autocomplete search**:
  - Search by component name (e.g., "resistor")
  - Search by part number (e.g., "10k-1/4W")
  - Search by manufacturer (e.g., "Vishay")
- Track quantities, pricing, suppliers
- Export BOMs (future)

### Device Library (NEW)
- 2,800+ Arduino-compatible boards indexed
- Full-text search with category filtering
- Device specifications and architectures
- Component library for BOMs

### API Endpoints

#### Authentication
- `POST /auth/register` — Create user account
- `POST /auth/login` — Get API key
- `GET /auth/me` — Get authenticated user

#### Projects
- `GET /projects/` — List public projects
- `POST /projects/` — Create project
- `GET /projects/{project_id}` — Get project details
- `PUT /projects/{project_id}` — Update project
- `DELETE /projects/{project_id}` — Delete project

#### Devices
- `GET /api/devices/devices` — List project devices
- `POST /api/devices/devices` — Register new device
- `GET /api/devices/devices/{device_id}` — Get device details

#### Bill of Materials
- `GET /api/boms/` — List project BOMs
- `POST /api/boms/` — Create BOM
- `GET /api/boms/{bom_id}` — Get BOM details
- `POST /api/boms/{bom_id}/items` — Add component to BOM

#### Library Search (NEW)
- `GET /api/library/library/devices/search?q=<query>` — Search device boards
- `GET /api/library/library/devices/category/{category}` — Get devices by category
- `GET /api/library/library/components/search?q=<query>` — Search components
- `GET /api/library/library/stats` — Get library statistics
- See [LIBRARY_SETUP.md](LIBRARY_SETUP.md) for full endpoint documentation

## Database Schema

Core tables:
- **users** — User accounts and authentication
- **projects** — Project metadata and ownership
- **project_metadata** — Device types, connectivity, firmware language
- **components** — Project components and parts
- **boms** — Bill of Materials
- **devices** — Registered IoT devices (NEW)
- **device_library** — Arduino board library (NEW)
- **component_library** — Electronic components (NEW)
- **project_revisions** — Version tracking
- **attachments** — Project files and documentation
- **build_log_entries** — Build progress and notes
- **discussion_threads** — Project collaboration
- **tags** — Project categorization

See [db/schema.sql](db/schema.sql) for full schema and [docs/data-model.md](docs/data-model.md) for details.

## Documentation

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** — 5-minute setup guide (START HERE)
- **[LIBRARY_SETUP.md](LIBRARY_SETUP.md)** — Device library architecture and API docs
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** — Feature overview
- **[docs/architecture.md](docs/architecture.md)** — System architecture
- **[docs/data-model.md](docs/data-model.md)** — Database design
- **[backend/README.md](backend/README.md)** — Backend setup and endpoints
- **[frontend/README.md](frontend/README.md)** — Frontend setup and features

## Configuration

### Environment Variables

```bash
# Database connection (optional, defaults to localhost)
DATABASE_URL=postgresql://user:password@host:5432/makergit

# CORS origins (for production)
ALLOWED_ORIGINS=https://example.com,https://app.example.com
```

### Database Settings

Default credentials (for local development):
- Database: `makergit`
- User: `postgres`
- Password: `NatEvan12!!` (change this in production!)
- Host: `localhost`
- Port: `5432`

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Run backend tests: `cd backend && pytest` (coming soon)
4. Commit with descriptive messages
5. Push and create a pull request

## Testing

```bash
# Backend tests (coming soon)
cd backend
pytest

# Frontend tests (coming soon)
cd frontend
npm test
```

## Performance Optimization

The device library uses:
- **GIN indexes** on full-text search fields (<100ms response)
- **B-tree indexes** on part numbers and categories
- **Connection pooling** with asyncpg (up to 20 concurrent connections)
- **Result limiting** on autocomplete (10-50 results max)

Device library search: ~30ms for 2,800+ boards

## Troubleshooting

### Database Connection Failed
```bash
# Test PostgreSQL connection
psql "postgresql://postgres:NatEvan12!!@localhost:5432/makergit"

# Ensure PostgreSQL is running
# Windows: Services → PostgreSQL
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

### Autocomplete Not Working
1. Check backend is running: `curl http://localhost:8000/api/library/library/stats`
2. Verify device_library has data: `psql -c "SELECT COUNT(*) FROM device_library"`
3. Check browser console (F12 → Console) for API errors

### Load Script Failed
```bash
# Run with verbose output
python -u db/load_device_library.py

# Check if library data exists
ls -la docs/library_index.json
```

## Contributing

Contributions welcome! Areas to help:
- Component library expansion (sensors, actuators, modules)
- UI/UX improvements for BOM management
- Advanced search filters and faceting
- Mobile-friendly responsive design
- Exporting BOMs to PDF/CSV
- Integration with supplier APIs (Mouser, Digi-Key)

## License

MIT License - See LICENSE file for details

## Support

- 📖 **Docs**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) to get started
- 🐛 **Issues**: Report bugs on GitHub Issues
- 💬 **Discussion**: Start a GitHub Discussion for questions

---

**Ready to get started?** Follow [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for a 5-minute setup! 🚀
