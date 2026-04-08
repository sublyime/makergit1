# MakerGit Frontend

Modern, responsive web UI for MakerGit — the maker-first IoT collaboration platform.

## Features

🎨 **Clean Design** — Modern UI with intuitive navigation
🔐 **User Authentication** — Register, login, and manage sessions
📦 **Project Management** — Create, browse, and manage projects
🔌 **Device Management** — Register and track IoT devices with board autocomplete
📋 **Bill of Materials** — Create BOMs with component search and autocomplete
✨ **Real-time Search** — Autocomplete suggestions for devices, components, and projects
📱 **Responsive Design** — Works on desktop and tablet
🚀 **Zero Build Steps** — Plain HTML/CSS/JS, no bundler needed

## Quick Start

### 1. Ensure Backend is Running

```bash
cd backend
uvicorn src.app:app --reload
# Backend available at http://localhost:8000
```

### 2. Start Frontend Server

```bash
cd frontend
python -m http.server 8080
# Frontend available at http://localhost:8080
```

Or open `index.html` directly in browser (local file:// mode has limited functionality).

### 3. Create Account

1. Click "Register" to create new account
2. Enter username, email, password
3. Start creating projects!

## Core Features

### Authentication
- **Register** — Create new user account
- **Login** — Sign in with username/password
- **Sessions** — API key stored in browser localStorage
- **Logout** — Clear session and sign out

### Projects
- **View Projects** — Browse public projects
- **Create Project** — New projects (authenticated users)
- **Edit Project** — Update project info
- **Delete Project** — Remove projects

### Device Management (Tab)
- **Register Device** — Add IoT device to project
  - **Device Type autocomplete** — Start typing "ESP32" to see suggestions
  - Supports 2,800+ Arduino-compatible boards
  - Board specs auto-populated from device library
- **View Devices** — See all project devices
- **Upload Firmware** — Add firmware versions to devices
- **Firmware Management** — Track firmware releases

### Bill of Materials (Tab)
- **Create BOM** — New bill of materials
- **Add Components** — Add parts to BOM with autocomplete:
  - **Component Name autocomplete** — Search by name
  - **Part Number autocomplete** — Search by part number
  - **Manufacturer autocomplete** — Filter by manufacturer
- **Track Quantities** — Manage component quantities
- **Price Tracking** — Log unit costs and suppliers
- **BOM Statistics** — View total cost and item count

## File Structure

```
frontend/
├── index.html           # Main HTML page
├── app.js              # Frontend JavaScript logic
├── styles.css          # UI styling and theme
└── README.md           # This file
```

## HTML Structure

### index.html
- Header with auth section
- Tab navigation (Projects, Devices, BOMs)
- Project list section
- Device management section
- Bill of Materials section
- Datalist elements for autocomplete

### Built-in Components
- Authentication forms (login/register)
- Project cards with management actions
- Device registration form with autocomplete
- BOM editor with component search
- Real-time cost calculation

## JavaScript (app.js)

### Core Functions
- `apiCall()` — Fetch wrapper with auth headers
- `login()` — User login handler
- `register()` — User registration handler
- `logout()` — Sign out and clear session
- `loadUser()` — Load authenticated user info

### Project Functions
- `loadProjects()` — Fetch project list
- `displayProjects()` — Render project cards
- `createProject()` — Create new project
- `selectProject()` — Switch to project context

### Device Functions
- `registerDevice()` — Add device to project
- `loadDevices()` — Fetch project devices
- `displayDevices()` — Render device list
- `uploadFirmware()` — Add firmware version

### BOM Functions
- `createBOM()` — Create new bill of materials
- `loadBOMs()` — Fetch project BOMs
- `displayBOMs()` — Render BOM list
- `editBOM()` — Open BOM editor
- `addBOMItem()` — Add component to BOM
- `updateBOMItem()` — Modify component in BOM
- `deleteItem()` — Remove component from BOM

### Autocomplete Functions (NEW)
- `searchDeviceTypes()` — Search device library (boards)
- `onDeviceTypeSelected()` — Handle device type selection
- `searchComponentByName()` — Search components by name
- `searchComponentByPartNumber()` — Search by part number
- `searchComponentByManufacturer()` — Search by manufacturer
- `initializeLibrarySearch()` — Load library on startup

## CSS (styles.css)

### Design System
- **Color Palette** — Modern blues, greens, reds
- **Typography** — Inter font family, clear hierarchy
- **Spacing** — Consistent rem-based sizing
- **Shadows** — Subtle depth and elevation

### Components
- Buttons — Primary, secondary, danger states
- Forms — Input groups, text areas, selects
- Cards — Project, device, and component cards
- Status Banners — Info, success, error messages
- Tabs — Navigation between sections
- Modals — Overlay dialogs (future)

### Responsive Design
- Mobile-first approach
- Flexbox and CSS Grid layouts
- Touch-friendly button sizes
- Readable text sizes on all devices

### Autocomplete Styling (NEW)
- Datalist dropdown with smooth animations
- Hover effects on suggestions
- Integration with existing design system
- Accessible keyboard navigation

## API Integration

### Authentication Endpoints
```javascript
POST /auth/register
POST /auth/login
GET /auth/me
```

### Project Endpoints
```javascript
GET /projects/
POST /projects/
GET /projects/{project_id}
PUT /projects/{project_id}
DELETE /projects/{project_id}
```

### Device Endpoints
```javascript
GET /api/devices/devices?project_id=xxx
POST /api/devices/devices
GET /api/devices/devices/{device_id}
```

### BOM Endpoints
```javascript
GET /api/boms/?project_id=xxx
POST /api/boms/
POST /api/boms/{bom_id}/items
PUT /api/boms/bom-items/{item_id}
DELETE /api/boms/bom-items/{item_id}
```

### Library Search Endpoints (NEW)
```javascript
GET /api/library/library/devices/search?q=<query>
GET /api/library/library/components/search?q=<query>
GET /api/library/library/stats
GET /api/library/devices/search?project_id=<id>&q=<query>
GET /api/library/projects/search?q=<query>
```

## Development

### Add New Feature

1. **HTML** — Add form or element in `index.html`
2. **CSS** — Add styling to `styles.css`
3. **JavaScript** — Add handler function in `app.js`
4. **API** — Call backend endpoint via `apiCall()`
5. **UI** — Update page content with response data

### Testing in Browser
- Open `http://localhost:8080` in browser
- Open DevTools (F12)
- Check Console for errors
- Use Network tab to debug API calls

### Error Handling
- All API errors shown in toast messages
- Check browser console for detailed error info
- Verify backend is running: `curl http://localhost:8000/`

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- **No Bundler** — Plain HTML/CSS/JS loads instantly
- **Lazy Loading** — Data fetched on demand
- **Minimal Dependencies** — Only vanilla JavaScript
- **API Caching** — Results cached in memory
- **Responsive** — Debounced search, fast filters

## Accessibility

- **Semantic HTML** — Proper heading hierarchy
- **ARIA Labels** — Screen reader support
- **Keyboard Navigation** — Tab through form fields
- **Color Contrast** — WCAG AA compliant
- **Focus Indicators** — Visible focus states

## Troubleshooting

### API Connection Failed
```
Error: Failed to fetch / CORS error
```
**Solution**: 
- Ensure backend is running on port 8000
- Check CORS configuration in `backend/src/app.py`
- Verify network tab shows requests to `http://localhost:8000`

### Autocomplete Not Showing
```
No suggestions appear when typing
```
**Solution**:
- Verify backend `/api/library/library/stats` endpoint works
- Check device library is loaded: `psql -c "SELECT COUNT(*) FROM device_library"`
- Open browser console (F12) to see API errors
- Try typing more characters or different search term

### Lost Login Session
**Solution**:
- Reload page (data persisted in localStorage)
- Re-login if localStorage was cleared
- Check browser allows localStorage

### Frontend Not Loading
```
Blank page or 404 error
```
**Solution**:
- Verify `index.html` exists in frontend folder
- Ensure HTTP server is running: `python -m http.server 8080`
- Try opening in private/incognito mode to bypass cache
- Clear browser cache and hard refresh (Ctrl+Shift+R)

## Future Enhancements

- [ ] User profiles with project following
- [ ] Search and filter projects by category/tag
- [ ] Advanced BOM features (cost estimation, supplier integration)
- [ ] Revision history and collaborative editing
- [ ] Push notifications for project updates
- [ ] Mobile app or PWA
- [ ] Dark mode theme toggle
- [ ] CSV/PDF export for BOMs and projects

## Resources

- **MDN Web Docs** — https://developer.mozilla.org/
- **HTML Spec** — https://html.spec.whatwg.org/
- **CSS Tricks** — https://css-tricks.com/
- **JavaScript Info** — https://javascript.info/

See [../QUICK_REFERENCE.md](../QUICK_REFERENCE.md) for setup and [../backend/README.md](../backend/README.md) for API docs.
