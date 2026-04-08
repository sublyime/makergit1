# MakerGit Data Model

## Core Entities

### User Management
- **users** — User accounts and authentication
  - Authentication via API keys
  - Profile info (username, email, display name, bio, avatar)
  - Timestamps for account tracking

### Project Management
- **projects** — Maker project definitions
  - Owner, description, visibility settings
  - Status tracking (planning, active, completed, archived)
  - Cost tracking and difficulty levels
  - Timestamps and relationships

- **project_revisions** — Version control for projects
  - Published iterations or build versions
  - Changelog tracking
  - Metadata snapshots
  - Creation metadata (who, when)

- **project_metadata** — Structured hardware/IoT attributes
  - Platform (Arduino, ESP32, Raspberry Pi, custom)
  - Category (Smart Home, Industrial, Hobbyist, etc.)
  - Connectivity (WiFi, Bluetooth, Cellular, None)
  - Power source (Battery, USB, AC, Solar)
  - Firmware language (C/C++, Python, MicroPython, CircuitPython)
  - Hardware tags array
  - Custom fields (JSONB)

### Device & Library Management (NEW)
- **device_library** — Arduino board and device library
  - 2,800+ pre-indexed devices (Arduino, ESP32, Arduino MKR, etc.)
  - Name, version, author, category
  - Supported architectures and types
  - Repository and documentation links
  - Keywords for full-text search
  - Enables autocomplete in device registration

- **devices** — Project device instances
  - Project association
  - Unique device identifier (MAC, serial, custom)
  - Device type and name
  - Status tracking (online, offline, error)
  - Last seen timestamp
  - Network info (IP, MAC address)
  - Firmware version tracking
  - Configuration storage (JSONB)
  - Custom metadata (JSONB)

- **component_library** — Electronic component catalog
  - Part number (unique)
  - Name and manufacturing details
  - Category and package type
  - Datasheet and pinout diagrams
  - Specifications (JSONB)
  - Keywords for component search
  - Enables autocomplete in BOM

### Bill of Materials
- **boms** — Bill of Materials for projects
  - Project and revision association
  - Name and description
  - Revision tracking
  - Total cost calculation
  - Currency support
  - Creation metadata

- **bom_items** — Components within BOMs
  - Reference designator (R1, C2, U3, etc.)
  - Quantity tracking
  - Unit cost and total cost
  - Supplier and SKU information
  - Component library reference
  - Notes and specifications
  - Timestamps

### Documentation & Collaboration
- **components** — Legacy component/part tracking
  - Part number and supplier info
  - Categorization
  - URL and notes

- **attachments** — Project files and documentation
  - Files per project/revision
  - Type (schematic, firmware, photo, etc.)
  - Metadata (filename, MIME type, size)
  - Upload timestamps

- **build_log_entries** — Project progress tracking
  - Dated entries
  - Title and body content
  - Optional revision association
  - Author tracking
  - Timestamps

- **discussion_threads** — Project conversations
  - Project-level discussions
  - Title and description
  - Status tracking (open, resolved)
  - Author and timestamps

- **comments** — Threaded comments
  - Nested reply support (parent_comment_id)
  - Can be attached to builds or discussions
  - Author, content, timestamps
  - Resolution marking

### Organization & Discovery
- **tags** — Categorical labels
  - Tag name (unique)
  - Optional category

- **project_tags** — Project/tag relationships
  - Many-to-many project/tag association
  - Enables filtering and discovery

- **favorites** — User project bookmarks
  - User/project relationship
  - Timestamp of favorite action

- **follows** — User connections
  - Follower/followee relationships
  - For user network features

### Monitoring & Analytics
- **telemetry_snapshots** — IoT device metrics
  - Device status and health data
  - Flexible JSONB storage
  - Timestamps for time-series analysis

- **device_templates** — Preconfigured device profiles
  - Recommended components
  - Hardware profiles
  - Default configurations

## Key Design Decisions

### Separation of Concerns
- **Live vs. Historical**: Projects are live records; revisions capture history
- **Metadata Flexibility**: JSONB columns allow extensibility without schema changes
- **Audit Trail**: Timestamps and user association on critical tables

### Performance
- **Full-Text Search**: GIN indexes on device_library and component_library names
- **Categorical Indexes**: B-tree indexes on frequently-filtered columns
- **Connection Pooling**: asyncpg manages up to 20 concurrent connections

### Extensibility
- **Custom Fields**: JSONB columns store flexible project and device attributes
- **Component Specs**: JSONB in components and component_library for varying specifications
- **Metadata Snapshots**: Revisions capture complete state for reproducibility

### Security
- **Foreign Key Constraints**: Cascade deletes for data consistency
- **Ownership Tracking**: Owner IDs prevent unauthorized access
- **Timestamps**: Full audit trail of changes

## Relationships

```
users
  ├─ 1:M → projects (owner)
  ├─ 1:M → project_revisions (created_by)
  ├─ 1:M → build_log_entries (created_by)
  ├─ 1:M → discussion_threads (created_by)
  ├─ 1:M → comments (author)
  ├─ M:M → favorites (users ↔ projects)
  └─ M:M → follows (followers/followees)

projects
  ├─ 1:M → project_revisions
  ├─ 1:1 → project_metadata
  ├─ 1:M → components
  ├─ 1:M → boms
  ├─ 1:M → devices (NEW)
  ├─ 1:M → attachments
  ├─ 1:M → build_log_entries
  ├─ 1:M → discussion_threads
  └─ M:M → tags (via project_tags)

devices (NEW)
  └─ *:1 → projects

boms
  ├─ *:1 → projects
  └─ 1:M → bom_items

bom_items
  └─ *:1 → component_library (optional)

device_library (NEW)
  └─ 1:M → devices (via device_type reference)

component_library (NEW)
  └─ 1:M → bom_items
```

## Table Sizes (Estimated)

| Table | Rows | Notes |
|-------|------|-------|
| device_library | ~2,800 | Pre-loaded from Arduino registry |
| users | Variable | Added per registration |
| projects | Variable | Created per user |
| project_revisions | Variable | 1+ per project |
| devices | Variable | Registered per project |
| boms | Variable | Created per project |
| bom_items | Variable | Added per BOM |
| component_library | Variable | Can be expanded |
| tags | Variable | User-created |
| comments | Variable | Discussion activity |

## Query Patterns

### Common Searches
```sql
-- Device library autocomplete
SELECT id, name, version FROM device_library 
WHERE LOWER(name) LIKE ? LIMIT 10;

-- Component search
SELECT id, name, part_number FROM component_library
WHERE part_number = ? OR LOWER(name) LIKE ?;

-- User's projects
SELECT * FROM projects WHERE owner_id = $1;

-- Project devices
SELECT * FROM devices WHERE project_id = $1;

-- BOM with costs
SELECT bi.*, cl.name FROM bom_items bi
LEFT JOIN component_library cl ON cl.id = bi.component_id
WHERE bi.bom_id = $1;
```

## Future Enhancements

- Component library expansion (resistors, capacitors, ICs)
- User library creation (custom components per user/project)
- Supplier integration (pricing from Mouser, Digi-Key)
- Cost estimation and purchasing suggestions
- Advanced search with faceting
- Full-text project search
- Time-series analytics on telemetry data

---

See [../backend/README.md](../backend/README.md) for API documentation and [../LIBRARY_SETUP.md](../LIBRARY_SETUP.md) for library-specific information.
