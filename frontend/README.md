# MakerGit Frontend

A simple web frontend for MakerGit that connects to the FastAPI backend.

## Features

- User registration and login
- View public projects
- Create new projects (authenticated users only)
- Responsive design with clean UI

## Setup

1. Start the backend server (see `../backend/README.md`)
2. Open `index.html` in a web browser
3. Register a new account or login

## API Integration

The frontend connects to the backend API at `http://localhost:8000`:

- Authentication endpoints (`/auth/*`)
- Project CRUD endpoints (`/projects/*`)

## Files

- `index.html` — Main HTML structure with auth and project forms
- `app.js` — JavaScript for API calls and UI interactions
- `styles.css` — CSS styling for the interface

## Development

To run locally with a simple HTTP server:

```bash
python -m http.server 3000
```

Then visit `http://localhost:3000` in your browser.

## Next steps

- Add project detail pages
- Implement project editing and deletion
- Add search and filtering
- Add user profiles and project ownership display
