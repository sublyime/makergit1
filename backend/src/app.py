from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import projects, auth, devices, boms
from .database import connect_db, close_db

app = FastAPI(title="MakerGit API", version="0.1.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth, prefix="/auth", tags=["auth"])
app.include_router(projects, prefix="/projects", tags=["projects"])
app.include_router(devices, prefix="/api/devices", tags=["devices"])
app.include_router(boms, prefix="/api/boms", tags=["boms"])

@app.on_event("startup")
async def startup_event():
    await connect_db(app)

@app.on_event("shutdown")
async def shutdown_event():
    await close_db(app)

@app.get("/")
async def root():
    return {"service": "MakerGit API", "status": "ok"}
