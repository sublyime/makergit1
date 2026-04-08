# Device Library Autocomplete Implementation Guide

This document describes the implementation of device library, component library, and autocomplete features for the MakerGit application.

## Overview

The implementation adds:
- **Device Library Database**: Stores Arduino and embedded device board information
- **Component Library Database**: Stores electronic components for Bill of Materials (BOM)
- **Autocomplete Search**: Real-time suggestions when typing in device type, component name, part number, and manufacturer fields
- **PostgreSQL Backend**: Efficient full-text search using GIN indexes

## Architecture

### Database Schema Changes

New tables added to `db/schema.sql`:

1. **device_library** - Device/board information
   - name, version, author, category
   - architectures[], types[]
   - description, repository, website
   - keywords[] for search

2. **component_library** - Electronic components
   - name, part_number (unique)
   - category, manufacturer
   - specifications (JSONB), package_type
   - keywords[] for search

3. **devices** - Project device instances
   - project_id, unique_id, name, device_type
   - status, firmware_version, config

4. **boms** - Bill of Materials
   - project_id, name, revision, total_cost

5. **bom_items** - Components in BOMs
   - bom_id, component_id
   - quantity, unit_cost, supplier info

### Backend API Endpoints

New endpoints in `/api/library/`:

#### Device Library Search
- `GET /api/library/library/devices/search?q=<query>&limit=10`
  - Search device boards by name, description
  - Returns: device name, version, category, description
  
- `GET /api/library/library/devices/category/{category}`
  - Get devices by category (e.g., "Arduino", "ESP32")
  
- `GET /api/library/library/devices/{device_id}`
  - Get detailed device information

#### Component Library Search
- `GET /api/library/library/components/search?q=<query>&limit=10`
  - Search components by name, part_number, manufacturer
  - Returns: component details
  
- `GET /api/library/library/components/category/{category}`
  - Get components by category
  
- `GET /api/library/library/components/{component_id}`
  - Get detailed component specs

#### Device & Project Autocomplete
- `GET /api/library/devices/search?project_id=<id>&q=<query>`
  - Search project devices
  
- `GET /api/library/projects/search?q=<query>`
  - Search user's projects

#### Library Statistics
- `GET /api/library/library/stats`
  - Get library statistics (total devices, components, categories)

### Frontend Implementation

#### HTML Changes
Modified `frontend/index.html`:
- Added `<datalist>` elements for autocomplete
- Device registration: `device-type` field with `device-types-list` datalist
- BOM component fields:
  - Component name → `component-names-list`
  - Part number → `part-numbers-list`
  - Manufacturer → `manufacturers-list`

#### JavaScript Functions
Added to `frontend/app.js`:

```javascript
// Device board autocomplete
searchDeviceTypes()              // Called on device-type input
onDeviceTypeSelected()           // Called on selection

// Component autocomplete
searchComponentByName()          // Search by component name
searchComponentByPartNumber()    // Search by part number
searchComponentByManufacturer()  // Search by manufacturer

// Initialize library on page load
initializeLibrarySearch()        // Called after user loads
```

#### CSS Styling
Added to `frontend/styles.css`:
- Datalist dropdown styling with hover effects
- Autocomplete box shadow and formatting
- Integration with existing design system

## Setup Instructions

### 1. Database Migration

Run the schema update:
```bash
psql -U postgres -d makergit -f db/schema.sql
```

### 2. Load Device Library Data

The library data from `docs/library_index.json` needs to be loaded into the database:

```bash
cd backend/
python3 ../db/load_device_library.py
```

This script will:
- Parse the Arduino library index JSON
- Extract device information (name, version, category, etc.)
- Insert into `device_library` table
- Create keywords from device properties for search

**Note**: The device library can be updated periodically by re-running this script. Duplicates are skipped based on (name, version) uniqueness.

### 3. Update Backend Dependencies

Ensure `requirements.txt` includes:
```
asyncpg>=0.29.0
fastapi>=0.104.0
pydantic>=2.0.0
```

### 4. Start Services

Backend:
```bash
cd backend/
python -m uvicorn src.app:app --reload --port 8000
```

Frontend (in another terminal):
```bash
python -m http.server 8080 -d frontend/
# or use any web server
```

## Usage Examples

### Device Registration with Autocomplete
1. Click on "My Devices" tab
2. In "Device Type" field, start typing: "ESP32"
3. Autocomplete dropdown appears with matching boards
4. Select "ESP32 (v1.0)" from suggestions
5. Device type is auto-filled

### BOM Creation with Component Search
1. Click on "Bill of Materials" tab
2. Create a new BOM
3. In the BOM editor, click "Add Component"
4. Type in "Component Name" field: "resistor"
5. Suggestions appear: "Resistor 10k", "Resistor 1k", etc.
6. Select a component to auto-fill part number and manufacturer
7. Enter quantity and unit price
8. Click "Add Item"

## Performance Optimization

The implementation uses several optimization techniques:

1. **GIN Indexes** on text fields for full-text search
   ```sql
   CREATE INDEX idx_device_library_name ON device_library 
   USING GIN(to_tsvector('english', name));
   ```

2. **B-tree Indexes** for exact match searches
   ```sql
   CREATE INDEX idx_component_library_part_number ON component_library(part_number);
   ```

3. **Limit clauses** on API responses (default 10, max 50 for devices, max 100 for categories)

4. **Lazy loading** - Libraries only search on user input

## File Modifications Summary

### New Files Created
- `backend/src/routers/library.py` - Library search API endpoints
- `db/load_device_library.py` - Migration script for device library data

### Modified Files
- `db/schema.sql` - Added 5 new tables and 7 indexes
- `backend/src/app.py` - Added library router to FastAPI app
- `backend/src/models.py` - Added 8 new Pydantic models
- `backend/src/routers/__init__.py` - Exported library router
- `frontend/index.html` - Added datalist elements and input attributes
- `frontend/app.js` - Added 6 autocomplete functions and library initialization
- `frontend/styles.css` - Added datalist styling (20 lines)

## Troubleshooting

### Issue: Autocomplete not showing suggestions
**Solution**: 
- Check browser console for API errors
- Verify backend is running: `curl http://localhost:8000/api/`
- Ensure database tables exist: `psql -c "\dt device_library"`

### Issue: Device library is empty after loading script
**Solution**:
- Run load script again with verbose output
- Check device_library table: `SELECT COUNT(*) FROM device_library;`
- Verify JSON file exists: `ls -la docs/library_index.json`

### Issue: Autocomplete is slow
**Solution**:
- Check if indexes were created: `SELECT * FROM pg_indexes WHERE tablename LIKE 'device%';`
- Run `VACUUM ANALYZE device_library;` to update statistics
- Monitor query performance with `EXPLAIN ANALYZE`

## Future Enhancements

1. **Offline Mode**: Cache library data in browser localStorage
2. **Library Sync**: Periodic updates from Arduino library registry
3. **Custom Components**: Allow users to add components to their own library
4. **Advanced Search**: Filter by architecture, category, price range
5. **Favorites**: Save frequently used components
6. **Cost Estimation**: Auto-calculate BOM costs from supplier APIs

## API Response Examples

### Device Library Search
```json
GET /api/library/library/devices/search?q=ESP32

[
  {
    "id": "uuid-1",
    "name": "ESP32",
    "version": "2.0.1",
    "category": "WiFi Microcontrollers",
    "description": "Dual-core 32-bit MCU with WiFi and Bluetooth"
  },
  {
    "id": "uuid-2",
    "name": "ESP32-C3",
    "version": "1.0.0",
    "category": "WiFi Microcontrollers",
    "description": "RISC-V based single-core MCU"
  }
]
```

### Component Library Search
```json
GET /api/library/library/components/search?q=resistor

[
  {
    "id": "uuid-101",
    "name": "Carbon Film Resistor",
    "part_number": "CF-10k-1/4W",
    "category": "Resistors",
    "manufacturer": "Vishay",
    "description": "Carbon film resistor 10K ohm 1/4W"
  }
]
```

## License & Attribution

Device library data sourced from Arduino Library Registry.
- Source: https://downloads.arduino.cc/libraries/library_index.json
- License: Respects individual library licenses
