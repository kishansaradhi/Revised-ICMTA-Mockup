
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api import members, admin, membership_applications, payments, events

app = FastAPI(
    title="ICMTA Backend API",
    version="1.0.0",
    description="FastAPI backend for the ICMTA website and faculty directory.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uploaded member/event/payment files are exposed through URLs stored in MySQL.
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(members.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(membership_applications.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(events.router, prefix="/api")


@app.get("/")
def root():
    return {"success": True, "message": "ICMTA FastAPI backend is running"}


@app.get("/api/health")
def health():
    return {"success": True, "status": "healthy"}
