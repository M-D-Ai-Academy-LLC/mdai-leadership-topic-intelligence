"""FastAPI application for the Leadership Topic Intelligence API."""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.routes import router
from storage.database import init_database

app = FastAPI(
    title="Leadership Topic Intelligence API",
    description="Search analytics and SEO intelligence for corporate leadership topics",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_database()


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "leadership-topic-intelligence", "version": "1.0.0"}
