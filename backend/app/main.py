"""Earthbucks FastAPI entrypoint.

Run locally:
    uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import auth, causes, initiatives, missions, organizations, posts

settings = get_settings()

app = FastAPI(
    title="Earthbucks API",
    version="0.1.0",
    description="Backend for the Earthbucks civic news + donation platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
def root():
    return {"name": "Earthbucks API", "version": "0.1.0", "status": "ok"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(causes.router)
app.include_router(organizations.router)
app.include_router(initiatives.router)
app.include_router(missions.router)
app.include_router(posts.router)
