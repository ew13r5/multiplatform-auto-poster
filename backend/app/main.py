import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, pages, posts, schedule, images


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: placeholder for MinIO bucket ensure + DB check
    yield
    # Shutdown: cleanup


app = FastAPI(
    title="Facebook Auto-Poster",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
cors_origins_str = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public routes (no auth)
app.include_router(health.router, prefix="/api")

# Protected routes (auth dependency added in section-03)
app.include_router(pages.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(schedule.router, prefix="/api")
app.include_router(images.router, prefix="/api")
